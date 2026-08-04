#!/usr/bin/env python3
"""Behaviour tests for url_inspection.py. No network: the API shape is fixed by
the Search Console reference, so the parser is tested against that shape.

The field name is the point. A widely copied third-party parser reads
`userDeclaredCanonical`; the documented field is `userCanonical`. With the wrong
name the declared canonical is always absent, so a page that declares one
perfectly gets reported as declaring none — a false finding in exactly the check
this tool exists for.
"""
from __future__ import annotations

import importlib.util
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "plugins", "seo-aeo-audit", "skills", "seo-aeo-audit",
                      "scripts", "url_inspection.py")
failures: list[str] = []

sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location("url_inspection", SCRIPT)
ui = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ui)


def check(cond: bool, msg: str) -> None:
    if not cond:
        failures.append(msg)


def result(**index_fields) -> dict:
    return {"inspectionResult": {"indexStatusResult": dict(index_fields)}}


# ── the documented field name ────────────────────────────────────────────────
r = ui.parse(result(googleCanonical="https://e.com/a",
                    userCanonical="https://e.com/b"), "https://e.com/a")
check(r["user_canonical"] == "https://e.com/b",
      "userCanonical must be read (userDeclaredCanonical is the wrong spelling)")
codes = {f["code"] for f in ui.findings(r)}
check("canonical-disagreement" in codes,
      "Google-selected canonical differing from the declared one is the headline finding")

# a page that declares nothing is a different finding, not the same one
r2 = ui.parse(result(googleCanonical="https://e.com/a"), "https://e.com/a")
c2 = {f["code"] for f in ui.findings(r2)}
check("canonical-undeclared" in c2, "no declared canonical must be its own finding")
check("canonical-disagreement" not in c2,
      "an undeclared canonical must not be reported as a disagreement")

# agreement must be silent — a guard that fires on healthy pages gets ignored
r3 = ui.parse(result(googleCanonical="https://e.com/a", userCanonical="https://e.com/a",
                     verdict="PASS", coverageState="Submitted and indexed",
                     robotsTxtState="ALLOWED", pageFetchState="SUCCESSFUL",
                     lastCrawlTime="2026-08-01T10:00:00Z"), "https://e.com/a")
check(ui.findings(r3) == [], f"a healthy URL must produce no findings: {ui.findings(r3)}")

# ── blockers ─────────────────────────────────────────────────────────────────
r4 = ui.parse(result(coverageState="Discovered - currently not indexed",
                     robotsTxtState="ALLOWED", pageFetchState="SUCCESSFUL",
                     lastCrawlTime="2026-08-01T10:00:00Z"), "https://e.com/c")
check("not-indexed" in {f["code"] for f in ui.findings(r4)},
      "a not-indexed coverage state must be a blocker")
r5 = ui.parse(result(robotsTxtState="DISALLOWED", pageFetchState="SUCCESSFUL",
                     lastCrawlTime="2026-08-01T10:00:00Z"), "https://e.com/d")
check("robots-disallowed" in {f["code"] for f in ui.findings(r5)},
      "a robots.txt disallow must be a blocker")

# ── failure handling: one bad URL must not end a run, and must not fake data ──
err = ui.parse({"_error": "403 — scope"}, "https://e.com/e")
check(err.get("error") and "403" in err["error"], "an API error must survive into the row")
check(ui.findings(err) == [],
      "an un-inspected URL must yield no findings — absence of data is not evidence")

# ── the cap must be visible, never silent ────────────────────────────────────
md = ui.render_markdown([{"url": "https://e.com/a", "error": "x"}], dropped=7)
check("7 URL(s) not inspected" in md, "a truncated run must say what it dropped")

if failures:
    print("FAIL: url_inspection behavior")
    for f in failures:
        print(" - " + f)
    sys.exit(1)
print("PASS: url_inspection behavior (documented field names, canonical verdicts, "
      "blockers, error rows, visible cap)")
