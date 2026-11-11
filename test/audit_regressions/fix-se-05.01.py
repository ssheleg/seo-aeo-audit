#!/usr/bin/env python3
"""FIX-SE-05.01: a standing indexing route is the approval (audit 2026-11-11, SE1).

The finding: SKILL.md, tooling.md and PB4 asked for the operator's go in every
session before any indexing request, and put the Search Console UI before any
paid indexer. A host that records a standing indexing route (for example: an
indexer API first after a key and balance check, IndexNow and Search Console as
fallback, only URLs answering 200 and in the sitemap) was told to ask anyway.

The fix under test: one rule, with its home in tooling.md, says a route recorded
in the host's instructions counts as the approval and sets the provider order;
without one, the per-session rule holds. SKILL.md, SKILL-CARD.md and PB4 point
at it, and the SpeedyIndex provider sheet carries the check a route runs first.
Mutations that drop each point are refused, so the check is watched saying no.

Standard library only.
"""
import os
import re
import sys

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SKILL = os.path.join(ROOT, "plugins", "seo-aeo-audit", "skills", "seo-aeo-audit")

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


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def flat(text):
    return " ".join(text.split())


def route_section(text):
    return flat(text.split("## A standing indexing route", 1)[1].split("\n## ", 1)[0])


def route_contract(text):
    section = route_section(text)
    for needle in ("recorded in the host's instructions",
                   "counts as that approval and sets the provider order",
                   "Without a recorded route, the current rule holds",
                   "`GET /v2/account`", "answer 200", "listed in the sitemap",
                   "never buying more",
                   "playbooks.md#pb4-request-indexing-in-search-console"):
        assert needle in section, f"the route section no longer states {needle!r}"


def t_tooling_home():
    text = read(os.path.join(SKILL, "references", "tooling.md"))
    route_contract(text)
    assert "(#a-standing-indexing-route)" in text.split("## Contents", 1)[1].split("\n## ", 1)[0]


def t_pointers():
    skill = flat(read(os.path.join(SKILL, "SKILL.md")))
    assert "A standing indexing route recorded in the host's instructions is that approval" in skill
    assert "references/tooling.md#a-standing-indexing-route" in skill
    card = flat(read(os.path.join(ROOT, "SKILL-CARD.md")))
    assert "a standing route recorded in the host's instructions is that approval" in card
    pb = flat(read(os.path.join(SKILL, "references", "playbooks.md")).split("## PB4.", 1)[1].split("\n## ", 1)[0])
    assert "tooling.md#a-standing-indexing-route" in pb and "fallback" in pb


def t_provider_sheet_runs_the_check():
    text = read(os.path.join(SKILL, "references", "tooling.md"))
    sheet = text.split("**SpeedyIndex**, REST v2", 1)[1].split("**seoindex.link**", 1)[0]
    row = [l for l in sheet.splitlines() if l.startswith("| Before a run |")][0]
    assert "`GET /v2/account`" in row and "never to a purchase" in row


def t_dropped_points_are_refused():
    text = read(os.path.join(SKILL, "references", "tooling.md"))
    for token in ("counts as that approval and sets the provider order",
                  "Without a recorded route, the current rule holds",
                  "listed in the sitemap"):
        try:
            pattern = r"\s+".join(map(re.escape, token.split()))
            route_contract(re.sub(pattern, "REMOVED", text))
        except AssertionError:
            continue
        raise AssertionError(f"dropping {token!r} was not refused")


case("tooling.md is the rule's home and lists it", t_tooling_home)
case("SKILL.md, SKILL-CARD.md and PB4 point at it", t_pointers)
case("the SpeedyIndex sheet carries the key and balance check", t_provider_sheet_runs_the_check)
case("dropping any point is refused", t_dropped_points_are_refused)

if failures:
    print(f"\n{len(failures)} failure(s), {checks} passed")
    sys.exit(1)
print(f"\nall green ({checks} checks)")
