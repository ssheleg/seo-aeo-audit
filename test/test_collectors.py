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

if failures:
    print("FAIL: collector behavior")
    for f in failures:
        print(" - " + f)
    sys.exit(1)
print("PASS: collector behavior (psi field/lab separation, CLS rescale, absent-CrUX "
      "honesty, sitemap template families, orphan refusal)")
