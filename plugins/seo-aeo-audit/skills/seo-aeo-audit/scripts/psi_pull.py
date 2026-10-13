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

Absent CrUX percentiles do not establish their cause: provider availability and
sample eligibility are possible causes. Absence is never zero or silently replaced
by the lab score (non-negotiable #8). Origin aggregates remain labelled context,
not a measurement of this page.

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

Exit codes: 0 = at least one supplied URL entry has a usable URL-field percentile
or lab performance score; 1 = usage/bootstrap error or no usable direct measurement.
Lab-only is a reportable synthetic measurement, never a field verdict. Empty and
origin-only responses retain their report but do not make a direct URL measurement.
The common coverage record counts input entries; component gaps remain explicit.
"""
from __future__ import annotations

import argparse
import json
import math
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
SKILL_VERSION = "0.26.5"

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
        # Flattened here rather than through `_flat`: this shared block must
        # render independently of the collector-specific helper.
        # test/validate.py counts the actual helper homes.
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


# ── collector coverage shared block ───────────────────────────────────────────
# Kept byte-identical in migrated standalone collectors; test_output_contracts
# compares the copies. docs/contracts/collector-coverage.md owns the semantics.
def collector_coverage(unit, scope, requested, attempted, returned, dropped, reasons):
    """Account one invocation's logical inputs, never redirect/retry attempts.

    A usable return is defined by each collector's scope. None is unknown, not
    zero. This record does not certify a whole site or provider dataset.
    """
    counts = (requested, attempted, returned, dropped)
    if not all(v is None or (type(v) is int and v >= 0) for v in counts):
        raise ValueError("coverage counts must be nonnegative integers or null")
    if not all(isinstance(v, str) and v.strip() for v in (unit, scope)) or not isinstance(reasons, list):
        raise ValueError("coverage needs a unit, scope and reason list")
    if any(not isinstance(r, dict) or not all(isinstance(r.get(k), str) and r[k].strip()
                                            for k in ("code", "detail")) for r in reasons):
        raise ValueError("coverage reasons need code and detail")
    if all(v is not None for v in (requested, attempted, dropped)) and attempted + dropped != requested:
        raise ValueError("coverage attempted + dropped must equal requested")
    if requested is not None and any(v is not None and v > requested for v in (attempted, returned, dropped)):
        raise ValueError("known coverage counts cannot exceed requested")
    if returned is not None and attempted is not None and returned > attempted:
        raise ValueError("coverage returned cannot exceed attempted")
    unknown = any(v is None for v in counts)
    gap = unknown or dropped or (returned != attempted)
    if gap and not reasons:
        raise ValueError("coverage gaps and unknown counts need reasons")
    state = "unknown" if unknown else "partial" if gap or reasons else "complete"
    return {"schema": "collector-coverage/1", "unit": unit, "scope": scope,
            "requested": requested, "attempted": attempted, "returned": returned,
            "dropped": dropped, "state": state, "reasons": reasons}


def collector_coverage_md(record):
    counts = " · ".join(f"{k}={record[k] if record[k] is not None else 'unknown'}"
                         for k in ("requested", "attempted", "returned", "dropped"))
    lines = ["## Collector coverage", "",
             f"State: **{record['state']}** · unit: `{_flat(record['unit'])}` · {counts}",
             "Scope: " + _flat(record["scope"], 500)]
    lines += [f"- `{_flat(r['code'])}`: {_flat(r['detail'])}" for r in record["reasons"]]
    return "\n".join(lines)
# ── end collector coverage shared block ───────────────────────────────────────


def band(metric_key: str, p75) -> str:
    spec = THRESHOLDS.get(metric_key)
    if not spec or p75 is None:
        return "unknown"
    _, good, poor, _u = spec
    value = p75 / 100 if metric_key == "CUMULATIVE_LAYOUT_SHIFT_SCORE" else p75
    if value <= good:
        return "good"
    return "needs-improvement" if value <= poor else "poor"


def safe_diagnostic(value, key=None):
    text = str(value)
    if key:
        for secret in (key, urllib.parse.quote(key, safe=""), urllib.parse.quote_plus(key)):
            text = text.replace(secret, "<redacted>")
    return text[:300]


def valid_number(value, maximum=None):
    if type(value) not in (int, float) or value < 0:
        return False
    try:
        return math.isfinite(value) and (maximum is None or value <= maximum)
    except OverflowError:
        return False


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
        try:
            detail = safe_diagnostic(e.read().decode("utf-8", "replace"), key)
        except Exception as exc:  # preserve status if even the error body cannot be read
            detail = "error body unavailable: " + safe_diagnostic(exc, key)
        hint = ("429 — PSI rate limit. Pass --key for automated runs"
                if e.code == 429 else f"HTTP {e.code}")
        return {"_error": f"{hint}: {detail}"}
    except Exception as exc:  # noqa: BLE001 - one bad URL must not end the run
        return {"_error": safe_diagnostic(exc, key)}


def _experience(block, errors=None, component="field"):
    """Keep recognized unknown metrics while refusing invalid measurements."""
    errors = errors if errors is not None else []
    if block is None:
        return {}
    if not isinstance(block, dict):
        errors.append(component + ": expected an object")
        return {}
    metrics = block.get("metrics")
    if metrics is None:
        return {}
    if not isinstance(metrics, dict):
        errors.append(component + ".metrics: expected an object")
        return {}
    out = {}
    for key, metric in metrics.items():
        if key not in THRESHOLDS:
            continue
        short, good, poor, unit = THRESHOLDS[key]
        value = metric.get("percentile") if isinstance(metric, dict) else None
        if value is not None and not valid_number(value):
            errors.append(component + "." + short + ": invalid percentile")
            value = None
        elif not isinstance(metric, dict):
            errors.append(component + "." + short + ": expected an object")
        out[short] = {"p75": value / 100 if value is not None and key == "CUMULATIVE_LAYOUT_SHIFT_SCORE" else value,
                      "unit": unit, "band": band(key, value),
                      "good_at_or_below": good, "poor_above": poor}
    return out


def component_status(metrics):
    observed = sum(metric.get("p75") is not None for metric in (metrics or {}).values())
    return "observed" if observed == len(THRESHOLDS) else "partial" if observed else "unavailable"


def useful_measurement(row):
    if "error" in row:
        return False
    return any(valid_number(metric.get("p75")) for metric in (row.get("field_data") or {}).values()) or valid_number(row.get("lab_performance_score"),100)


def parse(raw, url: str, key=None) -> dict:
    if not isinstance(raw, dict):
        return {"url": url, "error": "unusable PSI response: expected an object"}
    if "_error" in raw or "error" in raw:
        return {"url": url, "error": safe_diagnostic(raw.get("_error", raw.get("error")), key) or "unspecified PSI error"}
    errors = []
    field = _experience(raw.get("loadingExperience"), errors, "url_field")
    origin = _experience(raw.get("originLoadingExperience"), errors, "origin_field")
    lh = raw.get("lighthouseResult")
    if lh is not None and not isinstance(lh, dict):
        errors.append("lab: expected an object")
        lh = None
    lh = lh or {}
    categories = lh.get("categories")
    if categories is not None and not isinstance(categories, dict):
        errors.append("lab.categories: expected an object")
        categories = None
    performance = (categories or {}).get("performance")
    if performance is not None and not isinstance(performance, dict):
        errors.append("lab.performance: expected an object")
        performance = None
    score = (performance or {}).get("score")
    if score is not None and not valid_number(score, 1):
        errors.append("lab.score: expected a finite number in [0,1]")
        score = None
    stamp = lh.get("fetchTime") or raw.get("analysisUTCTimestamp")
    if stamp is not None and not isinstance(stamp, str):
        errors.append("measurement timestamp: expected a string")
        stamp = None
    field_status = component_status(field)
    return {
        "url": url, "fetched_at": stamp,
        "field_data": field or None,
        "field_note": (None if field_status == "observed" else
            "no CrUX field data for this URL, or some recognized percentiles are unavailable. "
            "The response does not establish why: provider availability and sample eligibility "
            "are possible causes. This is NOT a pass and NOT a failure; origin data is context "
            "only and lab scores never substitute for field measurements"),
        "origin_field_data": origin or None,
        "lab_performance_score": round(score * 100) if score is not None else None,
        "lab_note": "one synthetic load; it explains a field failure and cannot establish one — the field percentiles are the verdict",
        "component_status": {"url_field": field_status, "origin_field": component_status(origin),
                             "lab": "observed" if score is not None else "unavailable"},
        "payload_errors": errors,
    }


def findings(r: dict) -> list[dict]:
    out: list[dict] = []
    if "error" in r or not r.get("field_data"):
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
        if "error" in r:
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
        if r.get("field_note"):
            lines.append(f"- ⚠ {r['field_note']}")
        if not r.get("field_data") or r.get("component_status", {}).get("url_field") != "observed":
            if r.get("origin_field_data"):
                og = ", ".join(f"{k} {v['p75'] if v['p75'] is not None else '—'}{v['unit']} ({v['band']})"
                               for k, v in r["origin_field_data"].items())
                lines.append(f"- origin aggregate (the whole site, **not this page**): {og}")
        for error in r.get("payload_errors", []):
            lines.append("- incomplete response component: " + _flat(error))
        shown_lab = r.get("lab_performance_score")
        lines.append(f"- lab performance score: {shown_lab if shown_lab is not None else '—'} — "
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
        r = parse(fetch(u, args.strategy, args.key), u, args.key)
        r["findings"] = findings(r)
        rows.append(r)

    reasons = []
    failed = sum("error" in row for row in rows)
    missing_field = sum("error" not in row and row["component_status"]["url_field"] != "observed" for row in rows)
    missing_lab = sum("error" not in row and row["component_status"]["lab"] != "observed" for row in rows)
    malformed = sum(bool(row.get("payload_errors")) for row in rows)
    returned = sum(useful_measurement(row) for row in rows)
    if failed:
        reasons.append({"code":"input_failed", "detail":f"{failed} URL entries returned failed or unusable API envelopes."})
    if missing_field:
        reasons.append({"code":"url_field_unavailable", "detail":f"{missing_field} URL entries lack some or all recognized field percentiles; cause unestablished."})
    if missing_lab:
        reasons.append({"code":"lab_unavailable", "detail":f"{missing_lab} URL entries have no usable lab performance score."})
    if malformed:
        reasons.append({"code":"malformed_component", "detail":f"{malformed} responses contain invalid components; valid siblings remain observed."})
    coverage = collector_coverage("input_url_entry", "Supplied URL entries in order, duplicates retained, " + args.strategy + " strategy. Return requires a valid URL-field percentile or lab score; origin-only context is not a direct URL measurement. Complete does not certify provider/site population.", len(urls), len(rows), returned, 0, reasons)
    prov = provenance("psi_pull.py", argv,
                      f"{len(urls)} URL(s), {args.strategy} strategy: "
                      + ", ".join(urls[:5])
                      + (f" (+{len(urls) - 5} more)" if len(urls) > 5 else ""))
    if args.format == "json":
        print(json.dumps({"producer": prov, "strategy": args.strategy,
                          "results": rows, "coverage": coverage}, indent=2))
    else:
        print(render_markdown(rows))
        print("\n" + collector_coverage_md(coverage))
        print("\n" + provenance_md(prov))
    # Useful direct measurement and coverage share one predicate. Lab-only is
    # usable synthetic context; an empty envelope or origin-only answer is not
    # a URL measurement. Component absence remains explicit in either case.
    return 0 if returned else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
