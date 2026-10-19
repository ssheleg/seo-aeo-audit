#!/usr/bin/env python3
"""Behaviour tests for scripts/ai_panel.py. Offline, stdlib only. Exit 0 = pass.

Fixture `test/fixtures/ai_panel/panel-3x4.json`: four prompts, three runs each on
three distinct days, one engine/mode/account/locale, every expected number worked
out by hand in the comments below. Plus one `api-proxy` record (its own cell) and
one record with no `source` label (rejected, never guessed).
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import residue  # noqa: E402

residue.open_case("ai_panel behaviour")
SCRIPT = os.path.join(ROOT, "plugins", "seo-aeo-audit", "skills", "seo-aeo-audit",
                      "scripts", "ai_panel.py")
FIX = os.path.join(ROOT, "test", "fixtures", "ai_panel")
sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location("ai_panel", SCRIPT)
ap = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ap)
failures: list[str] = []


def check(cond, msg):
    if not cond:
        failures.append(msg)


def run(fixture, *extra, fmt="json"):
    out = subprocess.run([sys.executable, SCRIPT, "--captures", os.path.join(FIX, fixture),
                          "--brand", "Acme", "--domain", "acme.com",
                          "--competitor", "Globex", "--competitor", "Initech",
                          "--competitor", "Umbrella", "--format", fmt, *extra],
                         capture_output=True, text=True, timeout=30)
    return out.returncode, (json.loads(out.stdout) if fmt == "json" else out.stdout)


rc, rep = run("panel-3x4.json")
check(rc == 0, f"a scored panel exits 0, got {rc}")
cells = {(c["prompt_id"], c["source"]): c for c in rep["cells"]}
check(len(rep["cells"]) == 5, f"4 ui-capture cells + 1 api-proxy cell, got {len(rep['cells'])}")
check(rep["valid_records"] == 13 and len(rep["rejected"]) == 1,
      f"13 valid records and 1 rejected, got {rep['valid_records']} / {rep['rejected']}")
check("source" in rep["rejected"][0], "the rejection names the missing source label")
check(rep["panel_verdict"] == "measured", "four cells meet 3 runs on 2+ days")

p1 = cells[("p1", "ui-capture")]
# p1 cited sets after normalisation: {pricing, g2}, {pricing, g2}, {pricing}
# pairwise Jaccard 1, 0.5, 0.5 -> mean 0.667. Case, trailing slash and fragment
# differences must not count as different URLs.
check(p1["cited_url_jaccard"] == 0.667, f"p1 Jaccard must be 0.667, got {p1['cited_url_jaccard']}")
check(p1["mention"]["k"] == 3 and p1["citation"]["k"] == 3, f"p1 mention/citation 3/3: {p1}")
check(p1["mention"]["interval_95"] == [0.439, 1.0],
      f"Wilson 95% for 3/3 is [0.439, 1.0], got {p1['mention'].get('interval_95')}")

p2 = cells[("p2", "ui-capture")]
# Acme is 4th by first appearance in run 1 (after Globex, Initech, Umbrella), 2nd in
# run 2, absent in run 3. Cited sets {a}, {b}, {} share nothing -> Jaccard 0.0.
check((p2["mention"]["k"], p2["top3_mention"]["k"]) == (2, 1),
      f"p2 mention 2/3 and top-3 1/3, got {p2['mention']} / {p2['top3_mention']}")
check(p2["cited_url_jaccard"] == 0.0 and p2["citation"]["k"] == 0, f"p2: {p2}")

p3 = cells[("p3", "ui-capture")]
check(p3["recommendation"] == {"k": 0, "n": 2, "rate": 0.0, "interval_95": ap.wilson(0, 2)}
      and p3["recommendation_unlabelled"] == 1,
      f"an unlabelled run is counted apart, never read as 'not recommended': {p3}")
check(p3["cited_url_jaccard"] == 1.0, "identical cited sets give Jaccard 1.0")

p4 = cells[("p4", "ui-capture")]
check(p4["citation"]["k"] == 1, "a subdomain of an owned domain is a citation (docs.acme.com)")
check(p4["recommendation"]["k"] == 3, "labelled recommendations are counted")

proxy = cells[("p1", "api-proxy")]
check(proxy["verdict"] == "insufficient-sample" and "rate" not in proxy["mention"],
      "a one-run proxy cell prints counts, never a rate")
check(rep["api_proxy_cells"] == 1 and "28.3%" in rep["api_proxy_caveat"],
      "api-proxy input is reported as under-covering, with the measured recovery figures")
check("Wilson" in rep["interval_method"] and "independent" in rep["interval_method"],
      "the interval method and its dependence caveat travel in the payload")

_, md = run("panel-3x4.json", fmt="markdown")
check("Wilson" in md and "under-cover" in md and "3/3 (100%, 95% 44% to 100%)" in md,
      "the markdown report carries counts, interval, method and the proxy caveat")
check("| script | `ai_panel.py` |" in md, "the default format carries the producer block")

# The refusal: one transcript is not a verdict.
rc, one = run("single-run.json")
check(rc == 0 and one["panel_verdict"] == "insufficient-sample",
      f"a single run must yield insufficient-sample, got {one['panel_verdict']}")
check(all("rate" not in one["cells"][0][k] for k in ("mention", "citation", "top3_mention")),
      "an insufficient cell must not print any rate")
_, one_md = run("single-run.json", fmt="markdown")
check("no rate is printed" in one_md and "not a visibility verdict" in one_md,
      "the markdown must say no verdict is possible from one run")

# Three runs on ONE day are still insufficient: the floor is days as well as runs.
same_day = [ap.score_record({"answer": "Acme", "date": "2026-10-19", "cited_urls": []},
                            ap._alias_re(["Acme"]), [], ["acme.com"]) for _ in range(3)]
check(ap.score_cell(("p", "e", "m", "a", "l", "ui-capture"), same_day)["verdict"]
      == "insufficient-sample", "three runs on one day must not be a verdict")

# Two runs on two days are insufficient too: the floor is runs as well as days.
two_days = [ap.score_record({"answer": "Acme", "date": d, "cited_urls": []},
                            ap._alias_re(["Acme"]), [], ["acme.com"])
            for d in ("2026-10-18", "2026-10-19")]
check(ap.score_cell(("p", "e", "m", "a", "l", "ui-capture"), two_days)["verdict"]
      == "insufficient-sample", "two runs on two days must not be a verdict")

# Input errors exit 1.
_r = subprocess.run([sys.executable, SCRIPT, "--captures", os.path.join(FIX, "absent.json"),
                     "--brand", "Acme", "--domain", "acme.com"], capture_output=True, text=True)
check(_r.returncode == 1 and "input_population_unknown" in _r.stdout,
      "an unreadable captures file exits 1 and says the population is unknown")
_r = subprocess.run([sys.executable, SCRIPT, "--captures", os.path.join(FIX, "single-run.json")],
                    capture_output=True, text=True)
check(_r.returncode == 2, "missing --brand/--domain is an argparse usage error")
check(ap.validate_record({**json.load(open(os.path.join(FIX, "single-run.json")))[0],
                          "source": "scraped"}, 0) is not None,
      "a source label outside ui-capture/api-proxy is rejected")

if not failures:
    residue.close_case("ai_panel behaviour")
residue.report()
if failures:
    print("FAIL: ai_panel behaviour")
    for f in failures:
        print(" - " + f)
    sys.exit(1)
print("PASS: ai_panel behaviour (3 runs x 4 prompts: mention, top-3, recommendation, "
      "citation, run-to-run Jaccard, Wilson intervals, api-proxy caveat, single-run refusal)")
