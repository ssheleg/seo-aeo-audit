#!/usr/bin/env python3
"""psi_pull — Core Web Vitals as users experienced them, with the lab run beside it.

Two different things arrive in one PageSpeed Insights response and they answer
different questions. **Field** data (CrUX) is what real Chrome users met over the
trailing window: it is the number Search uses and the only one that can fail a
page. **Lab** data (Lighthouse) is one synthetic load on one machine: it explains
a field failure, it cannot establish one. This script keeps them apart on purpose
— a report that blends them is the measured-vs-assumed defect in another costume
(SKILL.md non-negotiable #7).

The pass mark is a distribution, not an average: a URL group is "good" when the
**75th percentile** of field data clears the threshold.

CrUX has no data for low-traffic URLs. That is reported as absent, never as zero
and never silently replaced by the lab score (non-negotiable #8) — and the origin
aggregate is offered instead, clearly labelled as the origin, not the page.

stdlib only. The API works without a key for occasional use; pass --key for
frequent or automated runs.

Usage:
  psi_pull.py --url https://example.com/pricing
  psi_pull.py --url https://example.com/ --strategy desktop --format json
  psi_pull.py --urls-file urls.txt --key "$PSI_KEY"

Every output carries a **producer block** — `skill` (this tool's version), `script`,
`observed_at` (UTC), `runtime`, `args` (credential values redacted), `scope` (the
resolved input set), and `actor` / `model` / `trace` from `SEO_AEO_AUDIT_ACTOR`,
`_MODEL`, `_TRACE`. It is present in the default output and under `--format json` as
`producer`. A field the harness did not supply reads `unavailable: <VAR> is not set by
this harness` — never guessed, and never dropped, because a field that vanishes when
unavailable is indistinguishable from one nobody checked. `observed_at` is the field
that decides whether a finding has expired; the report's own `## Provenance` block adds
the four invalidators (see references/preflight.md).

Exit codes: 0 = at least one URL was measured, 1 = usage error, or every call was
refused. A URL whose origin has no CrUX data still counts as measured — the call
worked and the lab half is reportable; absence is this script's honest result, not
its failure mode.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request


# ── provenance: the execution that produced this payload ── shared block ──────
# Copied verbatim into all seven scripts and compared byte for byte by
# `test/validate.py`, for the same reason `_flat` is: these ship as standalone files
# with no shared module, and an import of one does not exist in the installed layout
# (`bin/seo-aeo-audit.js` copies `scripts/` alone into `~/.claude/skills/`). The
# doctrine behind the field set lives above this block in preflight.py. Never edit
# one copy — the guard fails all seven.
SKILL_VERSION = "0.25.6"

# The fields no python process can establish, with the variable that would supply
# each. They print by NAME on every run, because a field that vanishes when
# unavailable is indistinguishable from one nobody checked.
PRODUCER_ENV = (
    ("actor", "SEO_AEO_AUDIT_ACTOR", "who or what invoked the run"),
    ("model", "SEO_AEO_AUDIT_MODEL", "the model behind the agent — never inferred"),
    ("trace", "SEO_AEO_AUDIT_TRACE", "the id linking these actions to a run"),
)

# The closed field set, in render order. A payload missing one of these is refused
# by `preflight.validate_provenance`.
PRODUCER_FIELDS = ("skill", "script", "observed_at", "runtime", "args", "scope",
                   "actor", "model", "trace")

# Flags whose VALUE is a credential. `psi_pull.py --key <secret>` is the live case:
# echoing argv verbatim would write an API key into a deliverable somebody emails.
SECRET_FLAGS = ("--key",)

# One home for the block's table shape, read by every renderer, by
# `preflight.validate_provenance`, and by `test/validate.py` when it looks for the
# block in both report skeletons.
PROVENANCE_HEADER = "| Field | Value |"


def redact(argv: list[str]) -> list[str]:
    """The argv as given, with every credential flag's value removed.

    Both spellings, because handling one is the same as handling neither: `--key V`
    hides the following token, `--key=V` hides the tail.
    """
    out: list[str] = []
    hide = False
    for a in argv:
        if hide:
            out.append("<redacted>")
            hide = False
            continue
        head, sep, _ = a.partition("=")
        if head in SECRET_FLAGS:
            out.append(f"{head}=<redacted>" if sep else head)
            hide = not sep
        else:
            out.append(a)
    return out


def provenance(script: str, argv: list[str], scope: str = "") -> dict:
    """Which execution produced this payload: what ran, when, on what, about what.

    Every field in `PRODUCER_FIELDS` is present on every run. A value this process
    cannot establish reads `unavailable: <VAR> is not set by this harness` — never a
    guess and never nothing. `model` in particular is not inferred: naming the wrong
    vendor id is worse than saying nothing.
    """
    v = sys.version_info
    out = {
        "skill": f"seo-aeo-audit@{SKILL_VERSION}",
        "script": script,
        "observed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "runtime": f"{sys.implementation.name} {v.major}.{v.minor}.{v.micro} "
                   f"on {sys.platform}",
        "args": redact(argv),
        "scope": scope or "unavailable: this run resolved no input set to record",
    }
    for _name, _var, _what in PRODUCER_ENV:
        _val = os.environ.get(_var, "").strip()
        out[_name] = _val or f"unavailable: {_var} is not set by this harness ({_what})"
    return out


def provenance_md(prov: dict) -> str:
    """The producer block as a markdown table — one row per field, always.

    Emitted in the DEFAULT output format too, not only under `--format json`. This
    bundle has already shipped the other shape: four `gsc_pull.py` analyses were
    computed into the payload and printed only in JSON while `text` was the
    documented invocation, so an agent running the documented command never saw
    them. A provenance block a human never reads is a provenance block that does
    not exist.
    """
    lines = ["## Provenance — the execution that produced this", "",
             PROVENANCE_HEADER, "|---|---|"]
    for f in PRODUCER_FIELDS:
        v = prov.get(f, "")
        if isinstance(v, list):
            v = " ".join(v)
        # Flattened here rather than through `_flat`: only five of the seven scripts
        # define one, and a shared block resting on a name two of its homes lack
        # would crash in exactly the two least-exercised renderers.
        cell = " ".join(str(v).split()).replace("|", "\\|")
        if len(cell) > 300:
            cell = cell[:299].rstrip() + "…"
        lines.append(f"| {f} | `{cell}` |")
    return "\n".join(lines)
# ── end provenance shared block ──────────────────────────────────────────────


API = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

# developers.google.com/search/docs/appearance/core-web-vitals — the bands a
# 75th-percentile field value is judged against.
THRESHOLDS = {
    "LARGEST_CONTENTFUL_PAINT_MS": ("LCP", 2500, 4000, "ms"),
    "INTERACTION_TO_NEXT_PAINT": ("INP", 200, 500, "ms"),
    "CUMULATIVE_LAYOUT_SHIFT_SCORE": ("CLS", 0.10, 0.25, ""),
}


def _flat(text: str, limit: int = 200) -> str:
    """One line, safe inside a table cell, capped.

    Network errors arrive as HTML error pages and pretty-printed JSON. Interpolated
    raw into a markdown row, the first newline ends the row and every row after it
    stops rendering — so the report becomes unreadable exactly where it is carrying
    the failure. Duplicated in each collector rather than imported: these ship as
    standalone files with no shared module, so `test/validate.py` counts the homes.
    """
    one = " ".join(str(text).split()).replace("|", "\\|")
    return one if len(one) <= limit else one[: limit - 1].rstrip() + "…"


def band(metric_key: str, p75) -> str:
    spec = THRESHOLDS.get(metric_key)
    if not spec or p75 is None:
        return "unknown"
    _, good, poor, _u = spec
    value = p75 / 100 if metric_key == "CUMULATIVE_LAYOUT_SHIFT_SCORE" else p75
    if value <= good:
        return "good"
    return "needs-improvement" if value <= poor else "poor"


def fetch(url: str, strategy: str, key: str | None) -> dict:
    params = {"url": url, "strategy": strategy}
    if key:
        params["key"] = key
    # category is repeatable; performance carries both the lab score and CrUX
    qs = urllib.parse.urlencode(params) + "&category=PERFORMANCE"
    try:
        with urllib.request.urlopen(f"{API}?{qs}", timeout=90) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:300]
        hint = ("429 — PSI rate limit. Pass --key for automated runs"
                if e.code == 429 else f"HTTP {e.code}")
        return {"_error": f"{hint}: {detail}"}
    except Exception as exc:  # noqa: BLE001 - one bad URL must not end the run
        return {"_error": str(exc)[:300]}


def _experience(block: dict) -> dict:
    """CrUX metrics from loadingExperience / originLoadingExperience."""
    out = {}
    for key, m in (block.get("metrics") or {}).items():
        if key not in THRESHOLDS:
            continue
        short, good, poor, unit = THRESHOLDS[key]
        p75 = m.get("percentile")
        display = p75 / 100 if key == "CUMULATIVE_LAYOUT_SHIFT_SCORE" else p75
        out[short] = {
            "p75": display,
            "unit": unit,
            "band": band(key, p75),
            "good_at_or_below": good,
            "poor_above": poor,
        }
    return out


def parse(raw: dict, url: str) -> dict:
    if "_error" in raw:
        return {"url": url, "error": raw["_error"]}
    page = raw.get("loadingExperience") or {}
    origin = raw.get("originLoadingExperience") or {}
    lh = raw.get("lighthouseResult") or {}
    perf = ((lh.get("categories") or {}).get("performance") or {}).get("score")
    field = _experience(page)
    return {
        "url": url,
        "fetched_at": (lh.get("fetchTime") or raw.get("analysisUTCTimestamp")),
        # CrUX needs enough traffic; absence is a fact about the data, not a zero.
        "field_data": field or None,
        "field_note": (
            None if field else
            "no CrUX field data for this URL — too little traffic in the window. "
            "This is NOT a pass and NOT a failure; use the origin aggregate below "
            "as context only, and never substitute the lab score for a field value"
        ),
        "origin_field_data": _experience(origin) or None,
        "lab_performance_score": round(perf * 100) if isinstance(perf, (int, float)) else None,
        "lab_note": ("one synthetic load; it explains a field failure and cannot "
                     "establish one — the field percentiles are the verdict"),
    }


def findings(r: dict) -> list[dict]:
    out: list[dict] = []
    if r.get("error") or not r.get("field_data"):
        return out
    for short, m in r["field_data"].items():
        if m["band"] == "poor":
            out.append({"severity": "high", "code": f"cwv-{short.lower()}-poor",
                        "message": f"{short} p75 = {m['p75']}{m['unit']} — poor "
                                   f"(good is ≤ {m['good_at_or_below']}{m['unit']})"})
        elif m["band"] == "needs-improvement":
            out.append({"severity": "medium", "code": f"cwv-{short.lower()}-ni",
                        "message": f"{short} p75 = {m['p75']}{m['unit']} — needs "
                                   f"improvement (good is ≤ {m['good_at_or_below']}{m['unit']})"})
    return out


def render_markdown(rows: list[dict]) -> str:
    lines = ["# Core Web Vitals — field first, lab beside it", ""]
    for r in rows:
        lines.append(f"## {r['url']}")
        if r.get("error"):
            lines.append(f"- **could not measure**: {_flat(r['error'])}\n")
            continue
        if r.get("field_data"):
            lines.append("| metric | p75 | band | good at or below |")
            lines.append("|---|---|---|---|")
            for short, m in r["field_data"].items():
                # A missing percentile must not render as "None ms", which reads
                # like a value. Absence gets a dash and an explicit band.
                shown = f"{m['p75']}{m['unit']}" if m["p75"] is not None else "—"
                lines.append(f"| {short} | {shown} | **{m['band']}** | "
                             f"{m['good_at_or_below']}{m['unit']} |")
        else:
            lines.append(f"- ⚠ {r['field_note']}")
            if r.get("origin_field_data"):
                og = ", ".join(f"{k} {v['p75']}{v['unit']} ({v['band']})"
                               for k, v in r["origin_field_data"].items())
                lines.append(f"- origin aggregate (the whole site, **not this page**): {og}")
        lines.append(f"- lab performance score: {r.get('lab_performance_score')} — "
                     f"{r['lab_note']}")
        for f in findings(r):
            lines.append(f"  - **{f['severity']}** [{f['code']}] {f['message']}")
        # Every finding carries its date (non-negotiable #1). If the API did not
        # give one, say so plainly rather than printing the word None.
        stamp = r.get("fetched_at") or "not reported by the API — stamp it yourself"
        lines.append(f"- measured: `{stamp}`\n")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--url", action="append", default=[], help="URL (repeatable)")
    ap.add_argument("--urls-file", help="file with one URL per line")
    ap.add_argument("--strategy", choices=["mobile", "desktop"], default="mobile",
                    help="form factor (default mobile — the one Search judges)")
    ap.add_argument("--key", help="PSI API key; optional, recommended for automated runs")
    ap.add_argument("--format", choices=["markdown", "json"], default="markdown")
    args = ap.parse_args(argv)

    urls = list(args.url)
    if args.urls_file:
        try:
            with open(args.urls_file, encoding="utf-8") as fh:
                urls += [ln.strip() for ln in fh if ln.strip() and not ln.startswith("#")]
        except OSError as e:
            print(f"cannot read --urls-file: {e}", file=sys.stderr)
            return 1
    if not urls:
        print("no URLs given: pass --url and/or --urls-file", file=sys.stderr)
        return 1

    rows = []
    for u in urls:
        r = parse(fetch(u, args.strategy, args.key), u)
        r["findings"] = findings(r)
        rows.append(r)

    prov = provenance("psi_pull.py", argv,
                      f"{len(urls)} URL(s), {args.strategy} strategy: "
                      + ", ".join(urls[:5])
                      + (f" (+{len(urls) - 5} more)" if len(urls) > 5 else ""))
    if args.format == "json":
        print(json.dumps({"producer": prov, "strategy": args.strategy,
                          "results": rows}, indent=2))
    else:
        print(render_markdown(rows))
        print("\n" + provenance_md(prov))
    # A refused call is a failure; CrUX having no data for a URL is not — that call
    # worked and the lab half of it is reportable. Only the first kind sets the
    # status, or the honest-absence path this script exists for would read as broken.
    return 0 if any(not r.get("error") for r in rows) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
