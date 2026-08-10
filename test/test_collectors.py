#!/usr/bin/env python3
"""Behaviour tests for the two collectors: psi_pull.py and sitemap_audit.py.

Both are tested offline. The PSI response shape is fixed by the API reference and
the sitemap shape by sitemaps.org, so the parsers are exercised against those
shapes rather than against the network.

What is actually being defended here is non-negotiable #8: an instrument must not
let its own blind spot read as a measurement. For PSI that is missing CrUX data
(absence, not zero, and never the lab score standing in for it); for the sitemap
it is orphan detection, which a sitemap cannot support at all.
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "plugins", "seo-aeo-audit", "skills", "seo-aeo-audit", "scripts")
failures: list[str] = []
sys.dont_write_bytecode = True


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, os.path.join(SCRIPTS, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def check(cond: bool, msg: str) -> None:
    if not cond:
        failures.append(msg)


psi = load("psi_pull")
sm = load("sitemap_audit")

# ── psi_pull: field and lab must never merge ─────────────────────────────────
raw = {
    "loadingExperience": {"metrics": {
        "LARGEST_CONTENTFUL_PAINT_MS": {"percentile": 4200},
        "INTERACTION_TO_NEXT_PAINT": {"percentile": 150},
        "CUMULATIVE_LAYOUT_SHIFT_SCORE": {"percentile": 30},
    }},
    "lighthouseResult": {"categories": {"performance": {"score": 0.92}},
                         "fetchTime": "2026-08-04T12:00:00Z"},
}
r = psi.parse(raw, "https://e.com/a")
check(r["field_data"]["LCP"]["band"] == "poor", "LCP 4200ms must land in the poor band")
check(r["field_data"]["INP"]["band"] == "good", "INP 150ms must be good")
# CrUX reports CLS x100; a raw 30 is 0.30, which is poor — not 30, which would be
# poor for the wrong reason and would print an absurd number in the report.
check(r["field_data"]["CLS"]["p75"] == 0.30, f"CLS must be rescaled: {r['field_data']['CLS']['p75']}")
check(r["field_data"]["CLS"]["band"] == "poor", "CLS 0.30 must be poor")
check(r["lab_performance_score"] == 92, "lab score must survive as 0-100")

codes = {f["code"] for f in psi.findings(r)}
check("cwv-lcp-poor" in codes and "cwv-cls-poor" in codes, f"poor metrics must be findings: {codes}")
check("cwv-inp-poor" not in codes and "cwv-inp-ni" not in codes,
      "a good metric must not produce a finding")

# a strong lab score must never mask absent field data
raw_nofield = {"lighthouseResult": {"categories": {"performance": {"score": 0.99}}}}
r2 = psi.parse(raw_nofield, "https://e.com/b")
check(r2["field_data"] is None, "absent CrUX must be None, not an empty pass")
check(r2["field_note"] and "NOT a pass" in r2["field_note"],
      "absent field data must say it is neither a pass nor a failure")
check(psi.findings(r2) == [],
      "no field data means no CWV verdict — a 99 lab score is not evidence about users")
md = psi.render_markdown([r2])
check("no CrUX field data" in md, "the human report must state the gap, not skip the section")

# a metric block that arrives with no percentile must not render as "None ms",
# which reads like a measurement
r3 = psi.parse({"loadingExperience": {"metrics": {"LARGEST_CONTENTFUL_PAINT_MS": {}}},
                "lighthouseResult": {"categories": {"performance": {"score": 0.5}}}}, "u")
check(r3["field_data"]["LCP"]["band"] == "unknown", "a metric with no percentile is unknown")
check(psi.findings(r3) == [], "an unknown band must not become a verdict")
md3 = psi.render_markdown([r3])
check("None" not in md3, f"absence must render as a dash, not the word None:\n{md3}")

# sitemap: the per-file cap must be returned so the caller can report it —
# a silent truncation reads as "this is the whole site"
_pages, _maps, _dropped = sm.parse_sitemap(
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    + "".join(f"<url><loc>https://e.com/{i}/</loc></url>" for i in range(50010))
    + "</urlset>")
check(_dropped == 10, f"the cap must report what it dropped, got {_dropped}")
check(len(_pages) == 50000, "the cap itself must still hold")

# a sitemap index must yield maps, not pages
_p, _m, _d = sm.parse_sitemap(
    '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    '<sitemap><loc>https://e.com/s1.xml</loc></sitemap></sitemapindex>')
check(_p == [] and _m == ["https://e.com/s1.xml"],
      f"an index must be read as nested sitemaps, not pages: {_p} {_m}")

# ── sitemap_audit: template families come from the site's own URLs ───────────
urls = ["https://e.com/blog/first-post/", "https://e.com/blog/second-post/",
        "https://e.com/product/123/", "https://e.com/product/456/",
        "https://e.com/pricing/", "https://e.com/pricing/"]
a = sm.analyze(urls)
pats = {t["pattern"]: t["urls"] for t in a["templates"]}
check(pats.get("/blog/{slug}/") == 2, f"slug segments must collapse into one family: {pats}")
check(pats.get("/product/{n}/") == 2, f"numeric ids must collapse into one family: {pats}")
check(pats.get("/pricing/") == 2, f"a real path must stay itself: {pats}")
check(a["duplicate_paths"] == {"/pricing/": 2}, f"duplicates must be reported: {a['duplicate_paths']}")

# the refusal is load-bearing: a sitemap has no link graph, so orphans are not
# derivable from it and must never be claimed
check("orphan" in a["not_derivable_here"].lower(),
      "the analysis must state that orphans are not derivable from a sitemap")
blob = json.dumps(a).lower()
check("orphan_candidates" not in blob and "orphans" not in json.dumps(list(a.keys())).lower(),
      "no key may offer orphan detection from sitemap data")

# mixed hosts is a real defect and must surface
mixed = sm.analyze(["https://e.com/a/", "http://www.e.com/b/"])
check("sitemap-mixed-hosts" in {f["code"] for f in sm.findings(mixed)},
      "URLs spanning host variants must be flagged")

# end-to-end through the CLI, so the argument surface is covered too
tmp = os.path.join(tempfile.mkdtemp(), "sitemap.xml")
with open(tmp, "w", encoding="utf-8") as fh:
    fh.write('<?xml version="1.0" encoding="UTF-8"?>\n'
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
             + "".join(f"<url><loc>{u}</loc></url>" for u in urls) + "</urlset>")
out = subprocess.run([sys.executable, os.path.join(SCRIPTS, "sitemap_audit.py"),
                      "--file", tmp, "--format", "json"],
                     capture_output=True, text=True, check=True)
parsed = json.loads(out.stdout)
check(parsed["analysis"]["urls_total"] == 6, "CLI must parse every declared URL")

# ── gsc_pull derivations: the expectation comes from the property, not a table ──
# measurement.md J6 puts industry-average CTR curves on the do-not-measure list.
# A hardcoded "flag anything under 3%" threshold is the same error one step
# further from the data, so the baseline is built from the site's own rows.
gsc = load("gsc_pull")

own = [{"keys": [f"q{i}"], "impressions": 500, "ctr": 0.10, "position": 6.0}
       for i in range(10)]
own.append({"keys": ["weak"], "impressions": 900, "ctr": 0.02, "position": 6.0})
own.append({"keys": ["fine"], "impressions": 900, "ctr": 0.09, "position": 6.0})
curve = gsc.ctr_curve(own)
check(curve.get("4-10", {}).get("median_ctr") == 0.10,
      f"the curve must come from this property's rows: {curve}")
gaps = [g["key"] for g in gsc.derive_ctr_gaps(own, curve)]
check(gaps == ["weak"], f"only rows far below the site's own median are gaps: {gaps}")

# a band with too few rows must be omitted, not fitted — a curve from four rows
# is a guess with a decimal point
check(gsc.ctr_curve([{"keys": ["a"], "impressions": 100, "ctr": 0.5, "position": 1.0}]) == {},
      "a thin band must produce no baseline rather than a confident one")
check(gsc.derive_ctr_gaps([{"keys": ["x"], "impressions": 999, "ctr": 0.001, "position": 2.0}],
                          {}) == [],
      "with no baseline for the band, nothing may be reported as a gap")

pairs = [{"keys": ["shoes", "/a"], "clicks": 10, "impressions": 200, "position": 4.0},
         {"keys": ["shoes", "/b"], "clicks": 2, "impressions": 150, "position": 9.0}]
cn = gsc.derive_cannibalization(pairs)
check(cn and cn[0]["incumbent"]["page"] == "/a",
      "the incumbent is the URL with the clicks, and the rivals are named")
check(gsc.derive_cannibalization(
    [{"keys": ["solo", "/a"], "clicks": 9, "impressions": 900, "position": 3.0}]) == [],
    "one URL for a query is not cannibalization")

# the branded split must refuse to guess rather than invent the metric
nb = gsc.derive_branded_split(own, [])
check(nb["available"] is False and "guess" in nb["why"],
      "without brand terms the split must be reported unavailable, not estimated")
bs = gsc.derive_branded_split([{"keys": ["acme login"], "clicks": 5, "impressions": 10},
                               {"keys": ["running shoes"], "clicks": 1, "impressions": 40}],
                              ["acme"])
check(bs["branded"]["queries"] == 1 and bs["non_branded"]["queries"] == 1,
      f"brand terms must partition the query set: {bs}")

# ── preflight: an unreachable source is a gap in the report, not silence ─────
pf = load("preflight")

rows = [pf.probe("python", True, "3.13.0"),
        pf.probe("Search Console", False, "HTTP 403: insufficient scope", "scope",
                 "query data, URL Inspection")]
out = pf.render(rows)
check("1 of 2 sources reachable" in out, "the header must count what was actually reached")
check("gate: **scope**" in out,
      "a failure must name WHICH gate it hit — all three say 403 on their own")
check("blocks query data" in out, "a failure must say what it costs the audit")
check("non-negotiable #6" in out, "the report must point at the rule it is serving")

clean = pf.render([pf.probe("python", True, "3.13.0")])
check("What this costs" not in clean, "a clean preflight must not invent a problems section")
check("evidence ladder" in clean, "a clean preflight must say findings can climb the ladder")

# the three GSC gates are told apart from the body, because their status codes
# are identical and their messages are not
check(pf.check_gsc(None, None, None)[0]["gate"] == "login",
      "no token must be reported as a login gate, not a permission one")

# ── preflight: CrUX presence is decided by the metrics, not by a key name ────
# The probe read at most 4096 bytes of a several-hundred-KB PSI response and then
# decided on the presence of the *string* `loadingExperience`, which PSI returns
# whether or not CrUX has data for the URL. psi_pull.py has always known better:
# the data lives in that block's `metrics` child. So the probe could report
# "CrUX field data present for this URL" from a key that is always there, and
# "NO CrUX field data — too little traffic" from a read that never reached it.
check(pf.has_crux_field_data({"loadingExperience": {"metrics": {
          "LARGEST_CONTENTFUL_PAINT_MS": {"percentile": 2000}}}}) is True,
      "a block carrying metrics is field data")
check(pf.has_crux_field_data({"loadingExperience": {"id": "https://e.com/",
                                                    "initial_url": "https://e.com/"}}) is False,
      "the key without metrics is PSI's way of saying there is no CrUX data")
check(pf.has_crux_field_data({"loadingExperience": {"metrics": {}}}) is False,
      "an empty metrics map is absence, not presence")
check(pf.has_crux_field_data({}) is False, "no block at all is absence")
# and the same rule as psi_pull, on the same shape, so the two cannot drift
_psi_says = psi.parse({"loadingExperience": {"id": "u"},
                       "lighthouseResult": {"categories": {"performance": {"score": 0.9}}}},
                      "u")["field_data"] is not None
check(pf.has_crux_field_data({"loadingExperience": {"id": "u"}}) == _psi_says,
      "preflight and psi_pull must agree about what counts as CrUX field data")

# ── sitemap_audit: the cap has to appear where the number is read ────────────
# The notice went to stderr under a comment saying a silent cap reads as "this is
# the whole site". Any run that captures stdout — which is how the skill's own
# examples use these scripts — loses it exactly when the count becomes evidence.
_capped = sm.analyze(["https://e.com/a/"])
_capped["urls_truncated"] = 12
_capped["sitemaps_skipped"] = 3
_capped["sitemaps_read"] = 50
_md_cap = sm.render_markdown(_capped, sm.findings(_capped), ["https://e.com/sitemap.xml"])
check("12" in _md_cap and "truncat" in _md_cap.lower(),
      "the markdown report must name the URLs the per-file cap dropped")
check("3" in _md_cap and "not read" in _md_cap.lower(),
      "the markdown report must name the nested sitemaps it never opened")
_clean = sm.analyze(["https://e.com/a/"])
_clean.update({"urls_truncated": 0, "sitemaps_skipped": 0, "sitemaps_read": 1})
_md_clean = sm.render_markdown(_clean, sm.findings(_clean), ["s.xml"])
check("truncat" not in _md_clean.lower(),
      "a complete read must not invent a truncation caveat")

# ── gsc_pull: the default format must not silently drop four analyses ────────
# ctr_curve, ctr_gaps, cannibalization and branded_split were computed into the
# report and printed only under --format json, while `text` is the default and the
# documented invocation. An agent that runs the documented command sees no
# cannibalization section and reports either "none found" or writes one from
# nothing — and derive_branded_split's careful refusal to guess never arrives.
_report = {
    "site": "sc-domain:e.com",
    "recent_window": {"start": "2026-05-01", "end": "2026-07-30"},
    "history_window": {"start": "2025-04-01", "end": "2026-07-30"},
    "monthly": [{"month": "2026-07", "clicks": 100.0, "impressions": 5000.0}],
    "cliff": None,
    "position_split": {"top20": {"queries": 2, "impressions": 300, "clicks": 30, "ctr": 0.1},
                       "striking_21_30": {"queries": 1, "impressions": 100, "clicks": 1, "ctr": 0.01},
                       "beyond_30": {"queries": 5, "impressions": 9000, "clicks": 2, "ctr": 0.0002}},
    "ctr_curve": {"4-10": {"median_ctr": 0.1, "sample": 12}},
    "ctr_gaps": [{"key": "weak", "position": 6.0, "band": "4-10", "ctr": 0.02,
                  "site_median_ctr_for_band": 0.1, "impressions": 900}],
    "cannibalization": [{"query": "shoes", "urls": 2, "impressions": 350,
                         "incumbent": {"page": "/a", "clicks": 10, "impressions": 200,
                                       "position": 4.0},
                         "rivals": [{"page": "/b", "clicks": 2, "impressions": 150,
                                     "position": 9.0}]}],
    "branded_split": {"available": False, "why": "no --brand-terms given; the split is not "
                                                "inferable from query text alone and a guess "
                                                "here would misstate the single metric the AEO "
                                                "track leans on"},
    "top_queries": [{"keys": ["q"], "clicks": 5.0, "impressions": 50.0, "position": 4.0}],
    "top_pages": [{"keys": ["/p"], "clicks": 5.0, "impressions": 50.0, "position": 4.0}],
    "query_page_pairs": [],
    "sitemaps": [],
    "rows_dropped_as_noise": 4,
    "row_limits": {"query": 5000, "page": 5000, "query_page": 25000},
    "row_limit_reached": ["query"],
}
_text = gsc.render_text(_report)
check("cannibaliz" in _text.lower(), "the text report must show cannibalization")
check("/a" in _text and "/b" in _text, "cannibalization must name the incumbent and the rival")
check("ctr" in _text.lower() and "4-10" in _text, "the text report must show the site's own CTR curve")
check("weak" in _text, "pages below the site's own curve must be listed")
check("brand" in _text.lower() and "--brand-terms" in _text,
      "the branded split must report itself unavailable in the DEFAULT format, not only in JSON")

# the cliff detector fires only on a >=90% collapse held for 14 days. Silence from
# a detector whose sensitivity is never printed reads as "no collapse".
check("90%" in _text or "min_drop" in _text or "90 %" in _text,
      "when no cliff is found the report must state the threshold that found nothing")
_days = [{"keys": [f"2026-01-{d:02d}"], "clicks": 5.0, "impressions": 500.0} for d in range(1, 8)]
_days += [{"keys": [f"2026-01-{d:02d}"], "clicks": 0.0, "impressions": 5.0} for d in range(8, 25)]
check(gsc.find_cliff(_days) is not None, "a 99% drop that held must still be detected")
check(gsc.find_cliff(_days)["threshold"] >= 0.9,
      "the detected cliff must carry the threshold it was measured against")

# row limits are not pagination: a property with more queries than the limit gets
# its long tail dropped, which is precisely the band position_split is used to rank.
check("5000" in _text and "row" in _text.lower(),
      "the report must say the query set hit the API row limit")
check("4" in _text and "noise" in _text.lower(),
      "the rows dropped as scraper noise must be counted, not silently removed")

if failures:
    print("FAIL: collector behavior")
    for f in failures:
        print(" - " + f)
    sys.exit(1)
print("PASS: collector behavior (psi field/lab separation, CLS rescale, absent-CrUX "
      "honesty, sitemap template families, orphan refusal, sitemap cap in the report, "
      "preflight/psi CrUX agreement, gsc text parity with json)")
