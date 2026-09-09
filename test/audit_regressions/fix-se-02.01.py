#!/usr/bin/env python3
"""FIX-SE-02.01 — a manual action is a scoped multiplier (sherlock audit, SE-02).

The finding: the doctrine declared ANY manual action "a binary multiplier:
nothing you improve counts until it is lifted" — so a partial action on
/spam/* would have zeroed a proven auth fix on /checkout, a penalty Google
never issued.

The fix under test: an action is recorded with type, affected URL patterns,
surface, severity and scope; removal stays priority one; a SITEWIDE action
zeroes everything, a PARTIAL action zeroes only what its patterns cover, and
the two are reported differently.

Standard library only.
"""
import fnmatch
import os
import sys

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SKILL = os.path.join(ROOT, "plugins", "seo-aeo-audit", "skills", "seo-aeo-audit", "SKILL.md")

checks = 0
failures = []


def case(name, fn):
    global checks
    try:
        fn()
        checks += 1
        print(f"  ok  {name}")
    except AssertionError as e:
        failures.append(f"{name}: {e}")
        print(f"FAIL  {name}: {e}")


def t_doctrine_scopes_the_multiplier():
    flat = " ".join(open(SKILL, encoding="utf-8").read().split())
    for needle in ("A manual action is a scoped multiplier, never a binary one",
                   "type, the affected URL patterns, the surface, its severity and its scope",
                   "A SITEWIDE action zeroes every improvement",
                   "lifting it stays priority one",
                   "zeroes only what it covers",
                   "inventing a penalty Google did not issue"):
        assert needle in flat, f"the doctrine no longer states {needle!r}"
    assert "binary multiplier: nothing you improve counts" not in flat, \
        "the binary-multiplier claim survived"


# ------------------------- the scoping rule, run as documented behaviour


def action(scope, patterns=(), type_="pure spam", surface="Search", severity="high"):
    return {"type": type_, "patterns": list(patterns), "surface": surface,
            "severity": severity, "scope": scope}


def blocks(act, url):
    """Exactly the documented rule: sitewide covers everything; partial covers
    only its patterns."""
    if act["scope"] == "sitewide":
        return True
    return any(fnmatch.fnmatch(url, pat) for pat in act["patterns"])


def report_row(act):
    if act["scope"] == "sitewide":
        return f"MANUAL ACTION (sitewide, {act['type']}): every improvement is gated on removal"
    return (f"MANUAL ACTION (partial: {', '.join(act['patterns'])}, {act['type']}): "
            "findings inside these patterns are gated; everything else proceeds")


def t_partial_action_does_not_block_checkout():
    act = action("partial", ["/spam/*"])
    assert not blocks(act, "/checkout"), \
        "a partial action on /spam/* blocked a proven fix on /checkout"
    assert blocks(act, "/spam/casino-page"), "the partial action failed to cover its own scope"


def t_sitewide_blocks_everything_and_reads_differently():
    site = action("sitewide")
    part = action("partial", ["/spam/*"])
    for url in ("/checkout", "/spam/x", "/"):
        assert blocks(site, url), f"a sitewide action let {url} through"
    assert report_row(site) != report_row(part), "sitewide and partial render identically"
    assert "every improvement" in report_row(site)
    assert "everything else proceeds" in report_row(part)


def t_removal_stays_priority_one():
    findings = [
        {"id": "F-02", "title": "auth fix on /checkout", "priority": 2},
        {"id": "F-01", "title": "lift the manual action", "priority": 1},
    ]
    ordered = sorted(findings, key=lambda f: f["priority"])
    assert ordered[0]["title"] == "lift the manual action", \
        "the action's removal lost its priority"
    assert any(f["id"] == "F-02" for f in ordered), \
        "the unaffected fix was dropped from the plan instead of shipping beside the action"


def t_record_carries_the_five_fields():
    act = action("partial", ["/spam/*"], type_="thin content", surface="Discover",
                 severity="medium")
    for field in ("type", "patterns", "surface", "severity", "scope"):
        assert act.get(field) not in (None, ""), f"the record lost {field}"


def main():
    case("the doctrine scopes the multiplier", t_doctrine_scopes_the_multiplier)
    case("a partial /spam/* action does not block /checkout", t_partial_action_does_not_block_checkout)
    case("sitewide blocks everything and reads differently", t_sitewide_blocks_everything_and_reads_differently)
    case("removal stays priority one, the fix ships beside it", t_removal_stays_priority_one)
    case("the record carries type/patterns/surface/severity/scope", t_record_carries_the_five_fields)
    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print(f"OK ({checks} checks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
