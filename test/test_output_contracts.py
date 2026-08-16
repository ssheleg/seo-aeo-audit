#!/usr/bin/env python3
"""Cross-script output contracts — what every bundled collector owes its caller.

Two invariants. Each one had been settled *differently* by different scripts, and
that disagreement is the defect: an agent cannot learn a rule that only some of
the instruments follow.

1. **A run that measured nothing says so in its exit status**, not only in its
   prose. `page_audit.py` and `sitemap_audit.py` already exited 1 when every URL
   failed. `url_inspection.py` returned 0 after a run where every inspection came
   back 403, and `psi_pull.py` returned 0 after a run where every call was refused
   — both while their own docstrings promised 1. SKILL.md's documented invocation
   redirects stdout to a file, so an agent branching on `$?` read *success* from a
   file containing nothing but refusals. `preflight.py` is the deliberate
   exception and keeps returning 0: there, the failures **are** the report.

   The predicate has one home per script and the renderer and the exit status read
   the same one. Computing "did anything arrive" twice is how the prose and the
   status drift apart in the first place.

2. **Nothing reaches generated markdown unflattened.** Network errors arrive as
   HTML error pages and pretty-printed JSON. Interpolated verbatim into a table
   row, the row ends at the first newline and every row after it stops rendering:
   on a real preflight run against a 404 property, **5 of 7 rows survived**. The
   instrument whose entire job is evidence produced a report you cannot read the
   evidence from — and `validate.py` already rejects exactly this shape in the
   repository's own markdown, but a guard over checked-in files cannot see markdown
   the tool *generates*.

`_flat` is duplicated in each script rather than imported, because the scripts are
distributed as standalone files with no shared module. That makes it a fact with
five homes, so `validate.py` counts them (CLAUDE.md rule 1).
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import os
import sys

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


def silently(fn, *a, **kw):
    """Run something that prints a report; return its value, discard the report."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
        return fn(*a, **kw)


pre = load("preflight")
ui = load("url_inspection")
psi = load("psi_pull")
pa = load("page_audit")
ags = load("agent_surface")

# A Google error page: the thing that actually arrives, not a synthetic string.
HOSTILE = (
    'HTTP 404: <!DOCTYPE html>\n<html lang=en>\n  <meta charset=utf-8>\n'
    '  <title>Error 404 (Not Found)!!1</title>\n  <style>*{margin:0}</style>\n'
    'A pipe | in the middle, and a very long tail ' + "x" * 400
)

# ── 1. every renderer flattens before it interpolates ────────────────────────
for name, mod in (("preflight", pre), ("url_inspection", ui),
                  ("psi_pull", psi), ("page_audit", pa),
                  ("agent_surface", ags)):
    fn = getattr(mod, "_flat", None)
    if fn is None:
        failures.append(f"{name}.py must define _flat() — error text reaches its markdown raw")
        continue
    out = fn(HOSTILE)
    check("\n" not in out, f"{name}._flat must leave no newline (it ends a table row early)")
    check("|" not in out.replace("\\|", ""),
          f"{name}._flat must escape every pipe (an unescaped one splits the cell)")
    check(len(out) <= 220, f"{name}._flat must cap length; got {len(out)}")
    check("404" in out, f"{name}._flat must keep the diagnostic head of the message")

# ── 2. preflight's table survives a hostile detail ───────────────────────────
rows = [
    pre.probe("python", True, "3.14.6"),
    pre.probe("Search Console", False, HOSTILE, "permission", "query data"),
    pre.probe("homepage", True, "HTTP 200"),
]
md = pre.render(rows)
body = md.split("| source | state | detail |", 1)[-1].split("\n\n", 1)[0]
stray = [ln for ln in body.split("\n")[1:]
         if ln.strip() and not (ln.startswith("|") and ln.rstrip().endswith("|"))]
check(not stray, f"preflight.render must emit only well-formed table rows; stray: {stray[:2]}")
check(md.count("\n| ") >= 3, "all three probes must reach the table")

# ── 3. preflight's denominator does not shrink when a source fails ───────────
# check_gsc returned one probe on failure and two on success, so the headline
# "N of 7" silently became "N of 8" — and the probe that vanished is the one that
# decides the most: whether this account can see this property at all.
without = pre.check_gsc(None, "sc-domain:example.com", None)
check(len(without) == 2,
      f"check_gsc must still report the named property when it could not be reached; got {len(without)}")
if len(without) == 2:
    named = without[1]
    check("example.com" in named["source"], "the second probe must name the property")
    check(named["reachable"] is False, "an unattempted property is not reachable")

with_token_but_listed = pre.check_gsc(None, None, None)
check(len(with_token_but_listed) == 1,
      "with no --site there is no named property to report, so the count stays 1")

# ── 4. a run that answered nothing exits non-zero ────────────────────────────
answered = getattr(ui, "answered_rows", None)
if answered is None:
    failures.append("url_inspection.py must expose answered_rows() — the renderer and the "
                    "exit status must read one predicate, not two")
else:
    check(answered([{"url": "u", "error": "403"}]) == [],
          "a 403 row has not been answered by the index")
    check(len(answered([{"url": "u", "has_index_status": True}])) == 1,
          "a row carrying index status has been answered")

ui.access_token = lambda: "stub-token"
ui.inspect = lambda *a, **kw: {"_error": "403 — scope missing"}
rc = silently(ui.main, ["--site", "sc-domain:example.com", "--urls", "https://e.com/a"])
check(rc == 1, f"url_inspection must exit 1 when the index answered for no URL; got {rc}")

ui.inspect = lambda *a, **kw: {"inspectionResult": {"indexStatusResult": {
    "verdict": "PASS", "coverageState": "Submitted and indexed",
    "googleCanonical": "https://e.com/a", "userCanonical": "https://e.com/a"}}}
rc = silently(ui.main, ["--site", "sc-domain:example.com", "--urls", "https://e.com/a"])
check(rc == 0, f"url_inspection must exit 0 when the index answered; got {rc}")

# ── 5. psi: refusal is failure, absent CrUX is not ───────────────────────────
psi.fetch = lambda *a, **kw: {"_error": "429 — PSI rate limit"}
rc = silently(psi.main, ["--url", "https://e.com/a"])
check(rc == 1, f"psi_pull must exit 1 when every URL was refused; got {rc}")

# Absent field data is an honest result from a call that worked. Treating it as a
# failure would be the opposite defect — the lab run happened and is reportable.
psi.fetch = lambda *a, **kw: {
    "lighthouseResult": {"categories": {"performance": {"score": 0.9}},
                         "fetchTime": "2026-08-10T00:00:00Z"}}
rc = silently(psi.main, ["--url", "https://e.com/a"])
check(rc == 0, f"psi_pull must exit 0 when the call succeeded but CrUX has no data; got {rc}")


# ── 6. every severity a script emits can be ordered ──────────────────────────
#
# `page_audit.py` emitted `low` from `faq-schema-absent` and `SEVERITY_ORDER`
# held four keys without it, so `to_markdown` raised `KeyError: 'low'` on any
# page with no FAQ schema — which is most pages, and is the tool's default
# output mode. The JSON path was fine, so the crash only ever appeared to
# somebody running the documented invocation.
#
# Derived from the source rather than listed here, because a list in a test is a
# third place to forget the new severity.
import re as _re

for _name in ("page_audit", "sitemap_audit", "agent_surface", "url_inspection"):
    _path = os.path.join(SCRIPTS, _name + ".py")
    if not os.path.exists(_path):
        continue
    _src = open(_path, encoding="utf-8").read()
    _order = _re.search(r"^SEVERITY_ORDER\s*=\s*\{([^}]*)\}", _src, _re.M)
    if not _order:
        continue
    _known = set(_re.findall(r'"([a-z]+)"\s*:', _order.group(1)))
    _emitted = set(_re.findall(r'\badd\(\s*"([a-z]+)"', _src))
    _missing = sorted(_emitted - _known)
    check(not _missing,
          f"{_name}.py emits severity {_missing} that SEVERITY_ORDER cannot order — "
          f"to_markdown raises KeyError on the first finding at that level")

if failures:
    print("FAIL: output contracts")
    for f in failures:
        print("  -", f)
    raise SystemExit(1)
print("PASS: output contracts (flattening in 5 renderers, preflight table + stable "
      "denominator, exit status from the same predicate the report uses, every "
      "emitted severity orderable)")
