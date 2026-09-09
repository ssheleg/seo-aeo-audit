#!/usr/bin/env python3
"""FIX-EV-01.15 — the outcome corpus for seo-aeo-audit (sherlock audit, parent
FIX-EV-01; depends on the family harness of FIX-EV-01.01).

The corpus (evals/cases/seo-aeo-audit.json) holds a positive, a negative
(routing), a no-op and a live-host case, judged on ARTIFACTS through the
family's outcome-case contract — so seo-aeo-audit can no longer pass an eval
by its name being picked.

Checked here, stdlib only:

* every case is structurally valid against the contract (version, frozen
  prompt, case digest, non-empty outcome checks reading artifacts);
* the manifest records the oracle-and-raw-result rule and the with/without
  arms; nothing in it touches production integration;
* the live-host case is gated by a probe, so an unreachable host is NOT_RUN;
* where the family harness is present on this machine it validates each case
  for real; where it is absent that check is reported NOT_RUN — never PASS.
"""
import json
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CASES = os.path.join(ROOT, "evals", "cases", "seo-aeo-audit.json")
HARNESS = os.path.expanduser("~/DATA/sshlg-skills/test/outcome_harness.py")

failures = []
not_run = []


def case(name, fn):
    try:
        fn()
        print(f"  ok  {name}")
    except AssertionError as e:
        failures.append(f"{name}: {e}")
        print(f"FAIL  {name}: {e}")


def manifest():
    with open(CASES, encoding="utf-8") as fh:
        return json.load(fh)


def t_cases_are_structurally_valid():
    m = manifest()
    ids = [c["id"] for c in m["cases"]]
    assert len(ids) == len(set(ids)) and len(ids) >= 3, f"corpus too small or duplicated: {ids}"
    kinds = set()
    for c in m["cases"]:
        assert re.match(r"^outcome-case/1$", c["schema_version"])
        assert c["skill"] == "seo-aeo-audit"
        assert c["prompt"]["text"].strip(), f"{c['id']}: empty frozen prompt"
        assert re.match(r"^[0-9a-f]{64}$", c["environment"]["case_digest"])
        assert c["checks"]["outcome"], f"{c['id']}: no outcome checks — the name-picking eval again"
        for o in c["checks"]["outcome"]:
            assert o["kind"] in ("artifact-exists", "artifact-digest",
                                 "artifact-contains", "command-exit-0")
        kinds.add(c["id"].split("-")[-1])
    assert {"positive", "routing", "page", "host"} <= {i.split("-")[-1] for i in ids} or len(ids) >= 4


def t_negative_and_noop_present():
    m = manifest()
    by_id = {c["id"]: c for c in m["cases"]}
    neg = by_id["SEO-OUT-002-negative-routing"]
    assert "seo-aeo-audit" in neg["checks"]["load_trace"]["expect_not_loaded"], \
        "the negative case does not forbid the skill from loading"
    noop = by_id["SEO-OUT-003-noop-clean-page"]
    assert any("none" in (o.get("expect") or "") for o in noop["checks"]["outcome"]), \
        "the no-op case does not pin the empty-blockers artifact"


def t_live_host_is_probe_gated():
    m = manifest()
    live = next(c for c in m["cases"] if c["id"] == "SEO-OUT-004-live-host")
    assert live["checks"]["tool"], "the live case has no reachability probe — it cannot NOT_RUN"
    assert "curl" in live["checks"]["tool"][0]["command"]


def t_manifest_records_the_rules():
    m = manifest()
    flat = " ".join(json.dumps(m).split())
    for needle in ("actual output oracle", "raw result", "with/without-skill",
                   "NOT_RUN", "grader convenience"):
        assert needle in flat, f"the manifest no longer records {needle!r}"
    assert "baseline" in m["arms"] and "current" in m["arms"]


def t_family_harness_validates_each_case_where_present():
    if not os.path.isfile(HARNESS):
        not_run.append("family harness absent at ~/DATA/sshlg-skills — case-level "
                       "validation NOT_RUN on this machine (never a PASS)")
        return
    for c in manifest()["cases"]:
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            json.dump(c, fh)
            path = fh.name
        try:
            r = subprocess.run([sys.executable, HARNESS, path],
                               capture_output=True, text=True, timeout=60)
            assert r.returncode == 0, f"{c['id']} rejected by the family harness:\n{r.stdout}"
        finally:
            os.unlink(path)


def main():
    case("every case is structurally valid, none is name-picking", t_cases_are_structurally_valid)
    case("the negative and no-op cases hold their shape", t_negative_and_noop_present)
    case("the live-host case is probe-gated (NOT_RUN offline)", t_live_host_is_probe_gated)
    case("the manifest records oracle/raw/arms/grader rules", t_manifest_records_the_rules)
    case("the family harness validates each case (where present)",
         t_family_harness_validates_each_case_where_present)
    for n in not_run:
        print(f"  NOT_RUN  {n}")
    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print("\nall green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
