#!/usr/bin/env python3
"""Rendering checks run in WebKit (Safari) first; Chromium tools are a stated exception.

Family release 2026-10-16 (R13). The audit opens pages, captures evidence and
reads renders in a browser. The engine order is WebKit first; Lighthouse,
PageSpeed Insights, CrUX, the chrome-devtools MCP and CDP traces stay — they
are Chromium by definition — and are labelled as the stated Chromium
exception, never replaced. Mutations that drop each point are refused, so the
check is watched saying no. Text integrity only: no claim that a model follows it.

Standard library only.
"""
import os
import re
import sys

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SKILL = os.path.join(ROOT, "plugins", "seo-aeo-audit", "skills", "seo-aeo-audit")
HEADING = "## Browser engine — WebKit (Safari) first"

checks = 0
failures = []


def case(name, fn):
    global checks
    try:
        fn()
        checks += 1
        print(f"  ok  {name}")
    except (AssertionError, IndexError) as e:
        failures.append(f"{name}: {e}")
        print(f"FAIL  {name}: {e!r}")


def read(rel):
    with open(os.path.join(SKILL, rel), encoding="utf-8") as fh:
        return fh.read()


def flat(text):
    return " ".join(text.split())


def engine_contract(text):
    section = flat(text.split(HEADING, 1)[1].split("\n## ", 1)[0])
    needles = (
        "safaridriver", "Playwright", "`webkit`", "--browser webkit",
        "npx playwright install webkit", "Safari Web Inspector",
        "open -a Safari", "WebKit/Safari backend",
        "stated Chromium exception", "say which and why", "Chrome Dev",
        "temporary profile", "close every process", "checked only in Chromium",
        "Lighthouse", "PageSpeed Insights", "CrUX", "chrome-devtools",
        "CDP trace", "Chromium by definition",
        "URL Inspection",
    )
    for needle in needles:
        assert needle in section, f"engine section no longer states {needle!r}"


def t_tooling_has_engine_section():
    engine_contract(read("references/tooling.md"))


def t_contents_lists_engine_section():
    text = read("references/tooling.md")
    contents = text.split("## Contents", 1)[1].split("\n## ", 1)[0]
    assert "#browser-engine--webkit-safari-first" in contents


def t_ladder_rung_six_names_webkit():
    text = read("references/tooling.md")
    ladder = text.split("## Ladder", 1)[1].split("\n## ", 1)[0]
    row = [l for l in ladder.splitlines() if l.startswith("| 6 |")][0]
    assert "Safari Web Inspector" in row, "rung 6 still names only generic DevTools"


def t_routing_marks_chromium_rows():
    text = read("references/tooling.md")
    routing = text.split("## Check → tool routing", 1)[1].split("\n## ", 1)[0]
    rows = {l.split("|")[1].strip(): l for l in routing.splitlines()
            if l.startswith("| ") and not l.startswith("| Check")}
    for check in ("Site speed — diagnosis",
                  "Lighthouse categories other than performance"):
        assert "stated Chromium exception" in rows[check], f"{check} not marked"
    evidence = rows["Evidence capture for the report"]
    assert evidence.index("WebKit") < evidence.index("DevTools"), \
        "evidence capture does not put WebKit first"


def t_recipes_marked_as_chromium():
    text = read("references/tooling.md")
    recipes = text.split("## Chrome DevTools recipes worth memorising", 1)[1]
    head = flat(recipes.split("\n- ", 1)[0])
    assert "Safari Web Inspector" in head and "Chromium" in head


def t_crux_pages_name_the_webkit_gap():
    for rel in ("references/measurement.md", "references/experience-signals.md"):
        text = flat(read(rel))
        assert "Chromium by definition" in text, f"{rel}: CrUX not labelled"
        assert "WebKit" in text, f"{rel}: the Safari gap has no WebKit route"


def t_scripts_psi_labelled():
    text = flat(read("references/scripts.md").split("## psi_pull.py", 1)[1])
    assert "Chromium by definition" in text


def t_dropped_points_are_refused():
    text = read("references/tooling.md")
    engine_contract(text)
    for token in ("safaridriver", "open -a Safari", "stated Chromium exception",
                  "temporary profile", "close every process",
                  "checked only in Chromium", "Chrome Dev", "Chromium by definition"):
        try:
            pattern = r"\s+".join(map(re.escape, token.split()))
            engine_contract(re.sub(pattern, "REMOVED", text))
        except AssertionError:
            continue
        raise AssertionError(f"dropping {token!r} was not refused")
    try:
        engine_contract(text.replace(HEADING, "## Something else"))
    except IndexError:
        return
    raise AssertionError("a missing section was not refused")


case("tooling.md carries the WebKit-first engine section", t_tooling_has_engine_section)
case("the contents list names it", t_contents_lists_engine_section)
case("ladder rung 6 names Safari Web Inspector", t_ladder_rung_six_names_webkit)
case("Chromium-only routing rows are marked; evidence capture is WebKit first",
     t_routing_marks_chromium_rows)
case("the DevTools recipes say they are Chromium and name the Safari route",
     t_recipes_marked_as_chromium)
case("CrUX pages label Chromium and route the Safari gap to WebKit",
     t_crux_pages_name_the_webkit_gap)
case("psi_pull is labelled Chromium by definition", t_scripts_psi_labelled)
case("dropping any point is refused", t_dropped_points_are_refused)

if failures:
    print(f"\n{len(failures)} failure(s), {checks} passed")
    sys.exit(1)
print(f"\nall green ({checks} checks)")
