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


# ── 7. the report's coverage table is a closed vocabulary ─────────────────────
#
# The instruments could already tell a clean result from a check that never
# looked; the deliverable could not. `url_inspection` grants CONFIRMED only to
# the URLs the index answered for, `page_audit` drops absence findings on a
# truncated read, `gsc_pull` ships `row_limit_reached`, and `check_gsc` above
# keeps its own denominator fixed — and then the report's coverage table offered
# a `Status` column with no vocabulary and nothing that read it. A track that
# silently returned nothing rendered exactly like a track that came back clean.
#
# Three properties are asserted here, because each one is a way the fix could be
# shipped and still not work: the vocabulary is CLOSED (an out-of-enum value is an
# error, not an unread cell), the denominator is the whole declared track list, and
# the seed can never write the one value that reads as clean.

check(isinstance(getattr(pre, "TRACKS", None), tuple) and len(pre.TRACKS) >= 2,
      "preflight.py must declare TRACKS — the coverage table's denominator needs a home")
if isinstance(getattr(pre, "TRACKS", None), tuple) and pre.TRACKS:
    _ids = [t[0] for t in pre.TRACKS]
    check(len(set(_ids)) == len(_ids), f"TRACKS ids must be unique; got {_ids}")
    check(all(isinstance(t, tuple) and len(t) == 2 and t[1] for t in pre.TRACKS),
          "every TRACKS entry is (id, label) with a non-empty label")

check(isinstance(getattr(pre, "COVERAGE_STATUS", None), tuple) and len(pre.COVERAGE_STATUS) >= 4,
      "preflight.py must declare COVERAGE_STATUS — the closed vocabulary needs one home")
if isinstance(getattr(pre, "COVERAGE_STATUS", None), tuple):
    check("observed" in pre.COVERAGE_STATUS,
          "the vocabulary needs the value that means the track ran and answered")
    check(any(s.startswith("blocked-by") for s in pre.COVERAGE_STATUS),
          "the vocabulary needs a value that names the gate that stopped a track")
    check("unlooked" in pre.COVERAGE_STATUS,
          "the vocabulary needs the value that means nobody looked — that is the whole point")
    check(set(getattr(pre, "NO_REASON_NEEDED", ())) <=
          {s.split(" ", 1)[0] for s in pre.COVERAGE_STATUS},
          "NO_REASON_NEEDED names a status outside the vocabulary — the enum-drift defect")

# The seed: a floor, from probes, never a verdict.
_seed_rows = [
    pre.probe("python", True, "3.14.6"),
    pre.probe("robots.txt", False, "HTTP 503", "http", "crawl-directive checks (track A)"),
    pre.probe("sitemap", True, "HTTP 200"),
    pre.probe("homepage", True, "HTTP 200"),
    pre.probe("PageSpeed Insights", False, "HTTP 429", "rate-limit", "field CWV"),
]
_seed = pre.coverage_seed(_seed_rows)
check(len(_seed) == len(pre.TRACKS),
      f"coverage_seed must emit one row per declared track; got {len(_seed)} of {len(pre.TRACKS)}")
check([r["track"] for r in _seed] == [t[0] for t in pre.TRACKS],
      "coverage_seed must keep the declared track order — the denominator is the list, not a subset")
check(all(r["status"] != "observed" for r in _seed),
      "coverage_seed must never write `observed`: preflight runs before any track does, so "
      "the one value that reads as clean can only be written by somebody who looked")
_byid = {r["track"]: r for r in _seed}
check(_byid["A"]["status"] == "blocked-by http",
      f"track A rests on robots.txt, which was refused — got {_byid['A']['status']!r}")
check(_byid["A"]["notes"].strip() != "",
      "a blocked row must carry the reason it is blocked")
check(_byid["H"]["status"] == "blocked-by rate-limit",
      f"track H rests on PageSpeed, which was rate-limited — got {_byid['H']['status']!r}")
check(_byid["E"]["status"] == "unlooked",
      f"a track nothing refused starts at unlooked, not blank — got {_byid['E']['status']!r}")

# The seeded table is accepted by the checker that reads a real report.
_rendered = pre.render_coverage(_seed)
check(pre.COVERAGE_HEADER in _rendered, "render_coverage must emit the declared table header")
check(pre.validate_coverage(_rendered) == [],
      f"the seeded table must satisfy its own checker; got {pre.validate_coverage(_rendered)}")

# And the same seed reaches the JSON payload, so the table is generated from the
# instruments' own output rather than typed in afterwards.
_json_md = silently(pre.main, ["--origin", "https://example.invalid", "--skip-psi",
                              "--format", "coverage"])
check(_json_md == 0, f"--format coverage must exit 0; got {_json_md}")

# The checker refuses every way this table can lie.
_good = _rendered
for _label, _bad, _needle in (
    ("a status outside the vocabulary",
     _good.replace("| E content value | unlooked |", "| E content value | checked |", 1), "checked"),
    ("a blank status — the original defect",
     _good.replace("| E content value | unlooked |", "| E content value |  |", 1), "blank"),
    ("a track row dropped, shrinking the denominator",
     "\n".join(l for l in _good.split("\n") if not l.startswith(f"| {pre.TRACKS[-1][0]} ")),
     pre.TRACKS[-1][0]),
    ("blocked-by naming a gate nothing emits",
     _good.replace("blocked-by http", "blocked-by vibes", 1), "vibes"),
    ("partial with no reason given",
     _good.replace("| E content value | unlooked |", "| E content value | partial |", 1), "partial"),
    ("no coverage section at all", "# A report with findings and no coverage table\n", "Track coverage"),
):
    _errs = pre.validate_coverage(_bad)
    check(_errs != [], f"validate_coverage must refuse {_label}")
    check(any(_needle in e for e in _errs),
          f"the refusal of {_label} must name {_needle!r}; got {_errs[:2]}")

# A report that is honest about being partial, with reasons, is accepted — the
# checker must not push an auditor towards claiming `observed` to get past it.
_honest = _good.replace("| E content value | unlooked |  |",
                        "| E content value | partial | 3 of 40 templates sampled |", 1)
check(pre.validate_coverage(_honest) == [],
      f"an honest partial row must pass; got {pre.validate_coverage(_honest)}")

if failures:
    print("FAIL: output contracts")
    for f in failures:
        print("  -", f)
    raise SystemExit(1)
print("PASS: output contracts (flattening in 5 renderers, preflight table + stable "
      "denominator, exit status from the same predicate the report uses, every "
      "emitted severity orderable, coverage vocabulary closed and seeded)")
