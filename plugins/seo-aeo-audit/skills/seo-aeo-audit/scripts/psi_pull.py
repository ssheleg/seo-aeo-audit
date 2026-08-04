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

Exit codes: 0 = ran, 1 = usage/API error.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

API = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

# developers.google.com/search/docs/appearance/core-web-vitals — the bands a
# 75th-percentile field value is judged against.
THRESHOLDS = {
    "LARGEST_CONTENTFUL_PAINT_MS": ("LCP", 2500, 4000, "ms"),
    "INTERACTION_TO_NEXT_PAINT": ("INP", 200, 500, "ms"),
    "CUMULATIVE_LAYOUT_SHIFT_SCORE": ("CLS", 0.10, 0.25, ""),
}


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
            lines.append(f"- **could not measure**: {r['error']}\n")
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

    if args.format == "json":
        print(json.dumps({"strategy": args.strategy, "results": rows}, indent=2))
    else:
        print(render_markdown(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
