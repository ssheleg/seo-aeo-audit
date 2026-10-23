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
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import residue  # noqa: E402

residue.open_case("url_inspection behaviour")
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

# ── CONFIRMED is a claim about data that arrived ─────────────────────────────
# The footer was appended after the loop, unconditionally, so a run where every
# inspection returned 403 still ended by declaring its output CONFIRMED. This is
# the one instrument that can legitimately produce that tier, which is exactly why
# it must not claim it when it produced nothing.
_all_failed = ui.render_markdown(
    [{"url": "https://e.com/a", "error": "403 — scope", "findings": []},
     {"url": "https://e.com/b", "error": "403 — scope", "findings": []}], dropped=0)
check("CONFIRMED" not in _all_failed,
      "a run where nothing was inspected must not describe its output as CONFIRMED")
check("no index answers" in _all_failed.lower() or "nothing was inspected" in _all_failed.lower(),
      "the empty run must say plainly that the index answered nothing")

_one_ok = ui.render_markdown(
    [{"url": "https://e.com/a", "error": "403", "findings": []},
     dict(ui.parse(result(verdict="PASS", coverageState="Submitted and indexed",
                          googleCanonical="https://e.com/b", userCanonical="https://e.com/b",
                          robotsTxtState="ALLOWED", pageFetchState="SUCCESSFUL",
                          lastCrawlTime="2026-08-01T10:00:00Z"), "https://e.com/b"),
          findings=[])], dropped=0)
check("CONFIRMED" in _one_ok,
      "a run that did get index answers must still tier them CONFIRMED")
check("1 of 2" in _one_ok or "1 URL" in _one_ok,
      "the footer must scope the tier to the rows that actually returned an answer")

# ── every excluded state is not indexed, not only the two that say so ────────
# The check was a substring test for "not indexed", which matches
# "Crawled - currently not indexed" and misses every other exclusion Google
# documents. The engine's own verdict field is the reliable signal.
for _state, _verdict in (("Duplicate without user-selected canonical", "NEUTRAL"),
                         ("Excluded by 'noindex' tag", "NEUTRAL"),
                         ("Alternative page with proper canonical tag", "NEUTRAL"),
                         ("Soft 404", "FAIL"),
                         ("URL is unknown to Google", "NEUTRAL")):
    _r = ui.parse(result(verdict=_verdict, coverageState=_state, robotsTxtState="ALLOWED",
                         pageFetchState="SUCCESSFUL", lastCrawlTime="2026-08-01T10:00:00Z"),
                  "https://e.com/x")
    check("not-indexed" in {f["code"] for f in ui.findings(_r)},
          f"{_state!r} (verdict {_verdict}) must be reported as not indexed")
# and PASS must stay silent, including the states that read alarming but are fine
for _state in ("Indexed, not submitted in sitemap", "Indexed, though blocked by robots.txt"):
    _r = ui.parse(result(verdict="PASS", coverageState=_state, robotsTxtState="ALLOWED",
                         pageFetchState="SUCCESSFUL", lastCrawlTime="2026-08-01T10:00:00Z",
                         googleCanonical="https://e.com/x", userCanonical="https://e.com/x"),
                  "https://e.com/x")
    check("not-indexed" not in {f["code"] for f in ui.findings(_r)},
          f"{_state!r} is an indexed state and must not be reported as a blocker")

# ── an unparseable response is not a page that was never crawled ─────────────
# With no indexStatusResult every field parsed to None, and the only finding
# emitted was "no last crawl time recorded for this URL" — a manufactured finding
# from a parse miss.
_empty = ui.parse({"inspectionResult": {}}, "https://e.com/z")
_ecodes = {f["code"] for f in ui.findings(_empty)}
check("never-crawled" not in _ecodes,
      "an empty inspectionResult must not be reported as a URL Google never crawled")
check("no-index-status" in _ecodes,
      "an empty inspectionResult must say the response carried no index status")

# ── issue #56: an ADC token lives about an hour; a long run must not outlive it ──
# Observed 2026-10-23: 1,682 URLs, rows 524 onward all answered HTTP 401. The token is
# re-minted when it is older than TOKEN_MAX_AGE, and a 401 re-mints once and retries once.
class _Clock:
    def __init__(self):
        self.t = 0.0
    def __call__(self):
        return self.t

_minted = []
def _mint():
    _minted.append(len(_minted) + 1)
    return "tok%d" % len(_minted)

_clock = _Clock()
_tokens = ui.Tokens(mint=_mint, clock=_clock)
check(_tokens.get() == "tok1" and _tokens.get() == "tok1", "a fresh token is reused")
_clock.t = ui.TOKEN_MAX_AGE + 1
check(_tokens.get() == "tok2", "a token older than TOKEN_MAX_AGE is re-minted before use")

_calls = []
def _inspect_401_once(site, url, token, qp):
    _calls.append(token)
    return {"_error": "HTTP 401: Request had invalid authentication credentials"} if len(_calls) == 1 else result(verdict="PASS")
_minted.clear(); _calls.clear()
_t = ui.Tokens(mint=_mint, clock=_Clock())
_raw = ui.inspect_fresh("sc-domain:e.com", "https://e.com/a", _t, None, inspect_fn=_inspect_401_once)
check("_error" not in _raw and _calls == ["tok1", "tok2"], f"a 401 re-mints once and retries with the new token: {_calls}")

def _inspect_always_401(site, url, token, qp):
    _calls.append(token)
    return {"_error": "HTTP 401: still invalid"}
_minted.clear(); _calls.clear()
_t = ui.Tokens(mint=_mint, clock=_Clock())
_raw = ui.inspect_fresh("sc-domain:e.com", "https://e.com/a", _t, None, inspect_fn=_inspect_always_401)
check(_raw.get("_error", "").startswith("HTTP 401") and len(_calls) == 2, f"a second 401 fails the row, no loop: {_calls}")

def _inspect_403(site, url, token, qp):
    _calls.append(token)
    return {"_error": "403 - scope missing"}
_minted.clear(); _calls.clear()
_t = ui.Tokens(mint=_mint, clock=_Clock())
ui.inspect_fresh("sc-domain:e.com", "https://e.com/a", _t, None, inspect_fn=_inspect_403)
check(_calls == ["tok1"] and _minted == [1], "a non-401 error does not re-mint")

def _mint_fails_after_first():
    if _minted:
        raise SystemExit("ADC token acquisition failed")
    _minted.append(1)
    return "tok1"
_minted.clear(); _calls.clear()
_t = ui.Tokens(mint=_mint_fails_after_first, clock=_Clock())
_raw = ui.inspect_fresh("sc-domain:e.com", "https://e.com/a", _t, None, inspect_fn=_inspect_always_401)
check(_raw.get("_error", "").startswith("HTTP 401") and _calls == ["tok1"], "a re-mint that fails keeps the row's 401, said as it was")

_c = _Clock(); _minted.clear(); _calls.clear()
_t = ui.Tokens(mint=_mint_fails_after_first, clock=_c)
ui.inspect_fresh("sc-domain:e.com", "https://e.com/a", _t, None, inspect_fn=_inspect_403)
_c.t = ui.TOKEN_MAX_AGE + 1
_raw = ui.inspect_fresh("sc-domain:e.com", "https://e.com/b", _t, None, inspect_fn=_inspect_403)
check("re-mint failed" in _raw.get("_error", "") and len(_calls) == 1, "an aged-out token whose re-mint fails fails the row, not the run")

_t = ui.Tokens(mint=_mint, clock=_Clock())
check(ui.inspect_fresh("sc-domain:e.com", "https://e.com/a", _t, None, inspect_fn=lambda *a: []) == [],
      "a malformed (non-object) payload passes through to the parser, not read as a 401")

if not failures:
    residue.close_case("url_inspection behaviour")
residue.report()

if failures:
    print("FAIL: url_inspection behavior")
    for f in failures:
        print(" - " + f)
    sys.exit(1)
print("PASS: url_inspection behavior (documented field names, canonical verdicts, "
      "blockers, error rows, visible cap, every excluded state, tier scoped to answers)")
