#!/usr/bin/env python3
"""FIX-SE-03.01 — compatible observations are not a contradiction (sherlock
audit, SE-03).

The finding: cross-track triage item 3 read any tier gap on one URL as a
disagreement, and item 4's "one of the two did not look properly" forced
different properties to agree — a thin page that extracts perfectly became a
conflict, and a confirmed HTTP status beside a hypothetical ranking cause
became a fact to reconcile. Real data was lost to artificial agreement.

The fix under test, run as the documented rule: claims are compared by key
(subject, predicate, scope, time, instrument); a contradiction exists only
for incompatible values of ONE predicate on one subject at one snapshot;
independent aspects are preserved; instrument disagreement is stated, not
merged.

Standard library only.
"""
import os
import sys

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SKILL = os.path.join(ROOT, "plugins", "seo-aeo-audit", "skills", "seo-aeo-audit",
                     "SKILL.md")

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


def t_doctrine_states_the_claim_key():
    flat = " ".join(open(SKILL, encoding="utf-8").read().split())
    for needle in ("`(subject, predicate, scope, time, instrument)`",
                   "incompatible values hit the SAME predicate",
                   "the tiers describe the instruments, not the site",
                   "stated as an instrument disagreement",
                   "check the predicates before calling it a miss",
                   "a short page can extract perfectly",
                   "forcing different properties to agree loses real data"):
        assert needle in flat, f"the doctrine no longer states {needle!r}"
    assert "one of the two did not " + "look properly, and which is worth a minute" \
        not in flat, "the forced-agreement rule survived unqualified"


# ---------------- the documented comparison, executed


def claim(subject, predicate, value, tier="CONFIRMED", scope="page",
          time="snap-1", instrument="page_audit"):
    return {"subject": subject, "predicate": predicate, "value": value,
            "tier": tier, "scope": scope, "time": time, "instrument": instrument}


def ruling(a, b):
    """Exactly the documented rule: same subject+predicate+scope+time with
    incompatible values opens a ruling; anything else coexists."""
    if (a["subject"], a["predicate"], a["scope"], a["time"]) != \
       (b["subject"], b["predicate"], b["scope"], b["time"]):
        return "coexist"
    if a["value"] == b["value"]:
        return "corroborate"
    if a["instrument"] != b["instrument"]:
        return "instrument-disagreement"
    return "contradiction"


def t_thin_plus_extractable_coexist():
    e = claim("/blog/post", "content-depth", "thin", tier="CONFIRMED",
              instrument="page_audit")
    f = claim("/blog/post", "extractability", "clean", tier="CONFIRMED",
              instrument="agent_surface")
    assert ruling(e, f) == "coexist", \
        "thin + extractable was declared a contradiction — the finding itself"


def t_different_predicates_and_tiers_on_one_url():
    a = claim("/checkout", "http-status", "200", tier="CONFIRMED",
              instrument="url_inspection")
    b = claim("/checkout", "ranking-cause", "cannibalisation", tier="HYPOTHESIS",
              instrument="gsc_pull")
    assert ruling(a, b) == "coexist", \
        "a tier gap across predicates was read as a disagreement"


def t_same_key_different_values_opens_a_ruling():
    a = claim("/pricing", "indexed", "yes", instrument="url_inspection")
    b = claim("/pricing", "indexed", "no", instrument="url_inspection")
    assert ruling(a, b) == "contradiction", \
        "one instrument against itself did not open a ruling"
    c = claim("/pricing", "indexed", "no", instrument="site-search-operator")
    assert ruling(a, c) == "instrument-disagreement", \
        "two instruments disagreeing was not attributed to the instruments"


def t_different_snapshots_are_change_not_conflict():
    a = claim("/docs", "indexed", "yes", time="snap-1")
    b = claim("/docs", "indexed", "no", time="snap-2")
    assert ruling(a, b) == "coexist", \
        "a change over time was flattened into a contradiction"


def t_nothing_is_silently_merged():
    a = claim("/pricing", "indexed", "yes")
    b = claim("/pricing", "indexed", "no")
    verdicts = {ruling(a, b), ruling(b, a)}
    assert verdicts == {"contradiction"}, "the ruling is order-dependent"
    assert "corroborate" not in verdicts, \
        "incompatible values were merged as agreement"


def main():
    case("the doctrine states the claim key and drops forced agreement",
         t_doctrine_states_the_claim_key)
    case("thin + extractable coexist", t_thin_plus_extractable_coexist)
    case("different predicates/tiers on one URL coexist",
         t_different_predicates_and_tiers_on_one_url)
    case("same key, different values opens a ruling; instruments named",
         t_same_key_different_values_opens_a_ruling)
    case("different snapshots are change, not conflict",
         t_different_snapshots_are_change_not_conflict)
    case("nothing incompatible is silently merged", t_nothing_is_silently_merged)
    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print(f"OK ({checks} checks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
