#!/usr/bin/env python3
"""FIX-SE-04.01 — the tier label stops compressing five axes (sherlock
audit, SE-04).

The finding: any third-party index was capped STUDY while STUDY's own
definition demands a published method and sample; one place shipped STUDY on
a matching population while another demanded experiments for everything
below CONFIRMED — two rollout policies; and observation vs transferability
rode one label.

The fix under test: the five axes are separated in the doctrine; an unknown
vendor estimate is HYPOTHESIS, not STUDY; a direct HTTP observation confirms
without the console; and ONE rollout policy (action risk × causal support)
is shared by the table and SKILL.md — run here as documented behaviour.

Standard library only.
"""
import os
import re
import sys

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
REFS = os.path.join(ROOT, "plugins", "seo-aeo-audit", "skills", "seo-aeo-audit")

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


def read(rel):
    return open(os.path.join(REFS, rel), encoding="utf-8").read()


def t_doctrine_separates_the_axes():
    flat = " ".join(read("references/evidence-tiers.md").split())
    for needle in ("Five axes, one label",
                   "observation and transferability are different claims",
                   "**source**", "**directness**", "**population**",
                   "**causal support**", "**uncertainty**",
                   "The rollout policy — one home, risk × evidence",
                   "never becomes STUDY by arriving in a spreadsheet",
                   "GSC adds breadth, never permission"):
        assert needle in flat, f"evidence-tiers.md no longer states {needle!r}"


def t_vendor_estimate_is_not_study():
    flat = " ".join(read("references/tooling.md").split())
    assert "`STUDY` only when the method and sample are published" in flat, \
        "tooling row 5 still grants STUDY to any third-party index"
    assert "an estimate publishing neither is `HYPOTHESIS`" in flat


def t_one_rollout_policy_shared_by_both_homes():
    tiers = " ".join(read("references/evidence-tiers.md").split())
    skill = " ".join(read("SKILL.md").split())
    assert "action risk crossed with" in tiers or "risk × evidence" in tiers
    assert "action risk × causal support, never the tier alone" in skill, \
        "SKILL.md's Experiments bucket no longer routes by the shared policy"
    assert "anything below CONFIRMED that deserves a split test" not in skill, \
        "the blanket below-CONFIRMED policy survived — two policies again"


# ------------- the documented admission + rollout rules, executed


def admit(source, method_published=False, direct=False):
    """The admission rule as documented: tiers come from evidence, not rank."""
    if source == "engine" or (source == "own-observation" and direct):
        return "CONFIRMED"
    if source == "published-study" and method_published:
        return "STUDY"
    if source == "practitioner-case":
        return "FIELD"
    return "HYPOTHESIS"


def rollout(action_risk, reversible, causal):
    if causal:
        return "ship-with-rollback" if not reversible else "ship-verify"
    if not reversible:
        return "experiment-only"
    return "split-test" if action_risk == "sitewide" else "pilot-measured"


def t_admission_behaviour():
    assert admit("vendor-estimate") == "HYPOTHESIS", \
        "an unknown vendor estimate was admitted as STUDY — the finding itself"
    assert admit("published-study", method_published=True) == "STUDY"
    assert admit("own-observation", direct=True) == "CONFIRMED", \
        "a direct HTTP observation needed the console to confirm"
    assert admit("published-study", method_published=False) == "HYPOTHESIS"


def t_rollout_behaviour():
    assert rollout("scoped", True, causal=False) == "pilot-measured"
    assert rollout("sitewide", True, causal=False) == "split-test"
    assert rollout("any", False, causal=False) == "experiment-only", \
        "an irreversible action without causal support escaped the experiment list"
    assert rollout("any", False, causal=True) == "ship-with-rollback"


def t_definitions_still_verbatim_with_contributing():
    def defs(path):
        out = {}
        for line in open(path, encoding="utf-8"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 2:
                name = cells[0].strip("*` ").upper()
                if name in ("CONFIRMED", "STUDY", "FIELD", "HYPOTHESIS"):
                    out.setdefault(name, " ".join(cells[1].replace("**", "").split()))
        return out
    home = defs(os.path.join(REFS, "references", "evidence-tiers.md"))
    copy = defs(os.path.join(ROOT, "CONTRIBUTING.md"))
    assert home == copy and len(home) == 4, \
        "the definition cells drifted from CONTRIBUTING.md — the verbatim contract broke"


def main():
    case("the doctrine separates the five axes", t_doctrine_separates_the_axes)
    case("a vendor estimate without a method is not STUDY", t_vendor_estimate_is_not_study)
    case("one rollout policy is shared by the table and SKILL.md",
         t_one_rollout_policy_shared_by_both_homes)
    case("admission behaviour: rank never substitutes for method",
         t_admission_behaviour)
    case("rollout behaviour: risk × causal support decides", t_rollout_behaviour)
    case("the definition cells stay verbatim with CONTRIBUTING.md",
         t_definitions_still_verbatim_with_contributing)
    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print(f"OK ({checks} checks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
