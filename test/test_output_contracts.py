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
import json
import os
import re
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

# ── 8. every payload names the execution that produced it ─────────────────────
#
# M-32 asks the proof to identify the execution behind it; M-08 asks every proof to
# be scoped, versioned and perishable. Nothing here emitted any of it — no version,
# no timestamp, no run id — so a three-month-old audit was indistinguishable from
# today's, in the family's most perishable evidence.
#
# Six properties, and each is a way this could ship and still not work: the field set
# is closed, every field is present even when unavailable, nothing is guessed to look
# complete, a credential never reaches the block, the block is in the DEFAULT format
# too, and the checker refuses every way the block can lie.

_TMP = tempfile.mkdtemp(prefix="seo-aeo-contracts-")

sm = load("sitemap_audit")
gsc = load("gsc_pull")
COLLECTORS = (("preflight", pre), ("page_audit", pa), ("psi_pull", psi),
              ("sitemap_audit", sm), ("url_inspection", ui),
              ("agent_surface", ags), ("gsc_pull", gsc))

_manifest = json.load(open(os.path.join(ROOT, "package.json"), encoding="utf-8"))["version"]

for _name, _mod in COLLECTORS:
    _fn = getattr(_mod, "provenance", None)
    if _fn is None:
        failures.append(f"{_name}.py defines no provenance() — its payload cannot say which "
                        f"execution produced it, and a finding lifted out of it reaches a "
                        f"ticket with no way back to the run")
        continue
    _p = _fn(f"{_name}.py", ["--origin", "https://e.com"], "origin https://e.com")
    check(tuple(_p) == pre.PRODUCER_FIELDS,
          f"{_name}.provenance must emit exactly PRODUCER_FIELDS in order; got {tuple(_p)}")
    check(all(str(_p.get(f, "")).strip() for f in pre.PRODUCER_FIELDS),
          f"{_name}.provenance left a field empty — a blank reads the same whether the "
          f"value was unavailable or nobody looked")
    check(_p.get("skill") == f"seo-aeo-audit@{_manifest}",
          f"{_name}.provenance says {_p.get('skill')!r}; package.json says {_manifest} — a "
          f"producer block naming a version that never ran is worse than one naming none")
    check(_p.get("script") == f"{_name}.py",
          f"{_name}.provenance stamped {_p.get('script')!r} — a payload carrying another "
          f"script's name is worse than an unstamped one")
    check(re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$", str(_p.get("observed_at", ""))),
          f"{_name}.provenance observed_at is {_p.get('observed_at')!r}, not a UTC stamp — the "
          f"one field that decides whether the report has expired cannot be free text")
    # Nothing guessed to look complete. Unset is the normal case and says so BY NAME.
    for _f, _var, _ in pre.PRODUCER_ENV:
        check(str(_p.get(_f, "")).startswith("unavailable: ") and _var in str(_p.get(_f, "")),
              f"{_name}.provenance filled {_f!r} with {_p.get(_f)!r} while {_var} is unset — a "
              f"harness-owned field is reported unavailable and names the variable, never "
              f"inferred. `model` least of all: the wrong vendor id is worse than none")
    # ...and it is read from the environment when the harness DOES supply it.
    os.environ[pre.PRODUCER_ENV[0][1]] = "agent-42"
    try:
        check(_fn(f"{_name}.py", [])[pre.PRODUCER_ENV[0][0]] == "agent-42",
              f"{_name}.provenance ignores {pre.PRODUCER_ENV[0][1]} when it IS set — the "
              f"field would then read unavailable in the one case it is available")
    finally:
        del os.environ[pre.PRODUCER_ENV[0][1]]
    # A credential on the command line never reaches a block that gets emailed.
    _red = _fn(f"{_name}.py", ["--url", "u", "--key", "SEKRIT", "--key=SEKRIT2"])["args"]
    check("SEKRIT" not in " ".join(_red) and "SEKRIT2" not in " ".join(_red),
          f"{_name}.provenance echoed a --key value into args: {_red}")
    check(_red.count("<redacted>") + sum("<redacted>" in a for a in _red) >= 2,
          f"{_name}.provenance must redact BOTH --key spellings; got {_red}")
    # The block reaches the default format, not only --format json. This bundle has
    # shipped the other shape: four gsc_pull analyses were json-only while `text` was
    # the documented invocation.
    _md = getattr(_mod, "provenance_md", None)
    if _md is None:
        failures.append(f"{_name}.py defines no provenance_md() — the block would exist "
                        f"only in JSON, and the deliverable is markdown")
        continue
    _rendered = _md(_p)
    check(pre.PROVENANCE_HEADER in _rendered,
          f"{_name}.provenance_md must emit the declared table header")
    _stray = [l for l in _rendered.split("\n")[2:]
              if l.strip() and not (l.startswith("|") and l.rstrip().endswith("|"))]
    check(not _stray, f"{_name}.provenance_md must emit only well-formed rows; got {_stray[:2]}")

# ── 8b. the block reaches the DEFAULT format of every collector's main() ─────
#
# Asserting that `provenance_md` exists is not asserting that anything calls it, and
# the difference was measured: deleting `print(provenance_md(prov))` from a renderer
# left this file green. Every collector is driven through its own main() here, with
# its network stubbed, and its default-format output is read.
_stub_spec = os.path.join(_TMP, "spec.json")
with open(_stub_spec, "w", encoding="utf-8") as _fh:
    json.dump({"openapi": "3.1.0", "info": {"title": "x", "version": "1"},
               "paths": {"/a": {"get": {}}}}, _fh)
_stub_sitemap = os.path.join(_TMP, "sitemap.xml")
with open(_stub_sitemap, "w", encoding="utf-8") as _fh:
    _fh.write('<?xml version="1.0" encoding="UTF-8"?>\n'
              '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
              '<url><loc>https://e.com/a</loc></url>'
              '<url><loc>https://e.com/b</loc></url></urlset>\n')

psi.fetch = lambda *a, **kw: {"lighthouseResult": {
    "categories": {"performance": {"score": 0.9}}, "fetchTime": "2026-08-10T00:00:00Z"}}
ui.access_token = lambda: "stub-token"
ui.inspect = lambda *a, **kw: {"inspectionResult": {"indexStatusResult": {
    "verdict": "PASS", "coverageState": "Submitted and indexed",
    "googleCanonical": "https://e.com/a", "userCanonical": "https://e.com/a"}}}
gsc.access_token = lambda: "stub-token"
gsc.call = lambda path, *a, **kw: (
    {"siteEntry": [{"siteUrl": "sc-domain:e.com", "permissionLevel": "siteOwner"}]}
    if path == "/sites" else {"sitemap": []})
gsc.query = lambda *a, **kw: []

# `.invalid` is reserved and resolves nowhere, so preflight's probes fail at the
# resolver and no request leaves the machine — the same offline handle SE-01 used.
_DEFAULT_RUNS = (
    ("preflight", pre, ["--origin", "https://example.invalid", "--skip-psi"]),
    ("page_audit", pa, ["--file", os.path.join(ROOT, "test", "fixtures", "good-page.html"),
                        "--base-url", "https://e.com/x"]),
    ("psi_pull", psi, ["--url", "https://e.com/a"]),
    ("sitemap_audit", sm, ["--file", _stub_sitemap]),
    ("url_inspection", ui, ["--site", "sc-domain:e.com", "--urls", "https://e.com/a"]),
    ("agent_surface", ags, ["--openapi-file", _stub_spec]),
    ("gsc_pull", gsc, ["--site", "sc-domain:e.com"]),
)
check(len(_DEFAULT_RUNS) == len(COLLECTORS),
      f"every collector must be driven through its default format; {len(_DEFAULT_RUNS)} "
      f"runs against {len(COLLECTORS)} collectors")
for _name, _mod, _argv in _DEFAULT_RUNS:
    _buf = io.StringIO()
    with contextlib.redirect_stdout(_buf), contextlib.redirect_stderr(io.StringIO()):
        _mod.main(_argv)
    _out = _buf.getvalue()
    check(pre.PROVENANCE_HEADER in _out,
          f"{_name}.py prints no producer block in its DEFAULT format — the deliverable "
          f"is markdown, and a block that exists only under `--format json` is a block "
          f"the auditor pasting evidence never sees")
    check(f"| script | `{_name}.py` |" in _out,
          f"{_name}.py's default-format block does not name {_name}.py as its script")
    # And the JSON path carries it under the documented key.
    _buf = io.StringIO()
    with contextlib.redirect_stdout(_buf), contextlib.redirect_stderr(io.StringIO()):
        _mod.main(_argv + ["--format", "json"])
    _payload = json.loads(_buf.getvalue())
    # page_audit emits an ARRAY by documented contract, so the block rides on each
    # element rather than wrapping it — an envelope would break `jq '.[].url'`.
    _blocks = ([e.get("producer") for e in _payload] if isinstance(_payload, list)
               else [_payload.get("producer")])
    check(_blocks and all(isinstance(b, dict) for b in _blocks),
          f"{_name}.py --format json carries no `producer` block")
    check(all(tuple(b) == pre.PRODUCER_FIELDS for b in _blocks if isinstance(b, dict)),
          f"{_name}.py --format json emits a producer block whose fields are not "
          f"PRODUCER_FIELDS")

# A hostile value cannot break the table it is rendered into — the same defect the
# five _flat homes above exist for, in a block two of the seven scripts render
# without an _flat to call.
_hostile_md = pre.provenance_md(pre.provenance("preflight.py", [HOSTILE], HOSTILE))
check(all(l.startswith("|") and l.rstrip().endswith("|")
          for l in _hostile_md.split("\n")[2:] if l.strip()),
      "provenance_md must survive a value carrying newlines and pipes")
check(len(max(_hostile_md.split("\n"), key=len)) < 400,
      "provenance_md must cap a runaway value")

# The report block: seeded, and accepted by the checker a filled-in report faces.
_prov = pre.provenance("preflight.py", ["--origin", "https://e.com"],
                       pre.scope_of(None, "https://e.com"))
_block = pre.render_provenance(_prov)
check(pre.validate_provenance(_block) == [],
      f"the seeded provenance block must satisfy its own checker; got "
      f"{pre.validate_provenance(_block)}")
check("--format provenance" in _block,
      "the seeded block must carry the command that reproduces it — a block a human "
      "types after the run is automation debt, and observed_at then records when "
      "somebody remembered")
for _n, _ in pre.INVALIDATORS:
    check(_n in _block, f"the provenance block must name the {_n!r} invalidator — a proof "
                        f"with no stated expiry reads as permanent")

# `--format provenance` exits 0 and probes nothing, so seeding never waits on a
# PageSpeed round trip.
check(silently(pre.main, ["--origin", "https://example.invalid",
                          "--format", "provenance"]) == 0,
      "--format provenance must exit 0")

# Every way the block can lie is refused.
for _label, _bad, _needle in (
    ("no provenance section at all", "# an audit with findings and no producer\n", "Provenance"),
    ("a field dropped from the set",
     "\n".join(l for l in _block.split("\n") if not l.startswith("| observed_at ")),
     "observed_at"),
    ("a blank value cell",
     _block.replace(f"| skill | `{_prov['skill']}` |", "| skill |  |", 1), "blank"),
    ("observed_at as free text",
     # `.get`, because the plant one row up removes this very field and a KeyError
     # here would replace a named refusal with a traceback — the shape SE-01 named
     # when a plant emptied a file instead of editing it.
     _block.replace(_prov.get("observed_at", "1970-01-01T00:00:00Z"), "last quarter", 1),
     "observed_at"),
    ("an invalidator dropped",
     "\n".join(l for l in _block.split("\n") if not l.startswith("| **policy**")), "policy"),
    ("the seeding command removed",
     _block.replace("--format provenance", "by hand", 1), "automation debt"),
):
    _errs = pre.validate_provenance(_bad)
    check(_errs != [], f"validate_provenance must refuse {_label}")
    check(any(_needle in e for e in _errs),
          f"the refusal of {_label} must name {_needle!r}; got {_errs[:2]}")

# Both skeletons carry a block a reader can act on — the seeding command, every
# field name and every invalidator — without carrying values it cannot have yet.
for _rel in ("templates/audit-report.template.md",
             "plugins/seo-aeo-audit/skills/seo-aeo-audit/references/deliverable-templates.md"):
    _txt = open(os.path.join(ROOT, _rel), encoding="utf-8").read()
    check(pre.validate_provenance(_txt) == [],
          f"{_rel}: {pre.validate_provenance(_txt)}")


if failures:
    print("FAIL: output contracts")
    for f in failures:
        print("  -", f)
    raise SystemExit(1)
print("PASS: output contracts (flattening in 5 renderers, preflight table + stable "
      "denominator, exit status from the same predicate the report uses, every "
      "emitted severity orderable, coverage vocabulary closed and seeded, "
      f"provenance in all {len(COLLECTORS)} collectors — closed field set, nothing "
      "guessed, credentials redacted, default format included, checker refuses six "
      "ways to lie)")
