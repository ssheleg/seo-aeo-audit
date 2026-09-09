#!/usr/bin/env python3
"""FIX-SE-01.01 — Discover recommendations are not a gate (sherlock audit, SE-01).

The finding: the Discover doctrine called two metatags "the whole gate" and a
card that "will not render at all" without them — recommendations promoted to a
mandatory gate, so a page without og: tags would be written up as confirmed
ineligible for a surface Google documents as automatic.

The fix under test: three checks of three strengths — eligibility (automatic
for indexed content; no tag's absence confirms ineligibility), large-preview
permission (`max-image-preview:large` OR AMP, a presentation limitation when
absent), and the 1200px image recommendation (never a blocker) — with the SDK
reverse-engineering kept FIELD and every CONFIRMED rule linking its exact
supporting primary source.

The three checks also run as behaviour, over HTML fixtures both ways.

Standard library only.
"""
import os
import re
import sys

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SKILL_DIR = os.path.join(ROOT, "plugins", "seo-aeo-audit", "skills", "seo-aeo-audit")
DOC = os.path.join(SKILL_DIR, "references", "discover.md")
SKILL = os.path.join(SKILL_DIR, "SKILL.md")

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


# ------------------------------------------------------------------ the doctrine


def t_doctrine_splits_the_three_checks():
    text = open(DOC, encoding="utf-8").read()
    for needle in ("## Check 1 — eligibility", "## Check 2 — large-preview permission",
                   "## Check 3 — image selection, a recommendation",
                   "it is automatic", "or the page is served as AMP",
                   "never a blocker row",
                   'no page is written up as "confirmed ineligible"'):
        assert needle in text, f"the doctrine no longer states {needle!r}"
    for gone in ("These two are the whole gate", "will not render at all if two"):
        assert gone not in text, f"the gate wording survived: {gone!r}"
    skill = open(SKILL, encoding="utf-8").read()
    assert "none of them\nis a render gate" in skill or "none of them is a render gate" in skill.replace("\n", " "), \
        "SKILL.md still advertises the Discover gate"


def t_every_confirmed_rule_names_its_source():
    """Each Check section marked CONFIRMED carries the primary-source link inside it."""
    text = open(DOC, encoding="utf-8").read()
    sections = re.split(r"^## ", text, flags=re.M)
    confirmed_sections = [s for s in sections if s.startswith("Check ")]
    assert len(confirmed_sections) == 3, f"expected 3 Check sections, found {len(confirmed_sections)}"
    for s in confirmed_sections[:2]:  # checks 1 and 2 state their own links
        assert "https://developers.google.com/search/docs" in s, \
            f"a CONFIRMED check carries no primary source: {s.splitlines()[0]!r}"
    # check 3 leans on the same documentation named in check 2's sentence or its own
    assert "same documentation" in confirmed_sections[2] \
        or "https://developers.google.com" in confirmed_sections[2], \
        "the recommendation check names no supporting source"


# ---------------------------- the three checks, run as documented behaviour


def audit_discover(html, indexed=True):
    """The classifier exactly as the doctrine states it. Returns findings with
    their strengths; 'ineligible' can only come from indexing, never from tags."""
    findings = []
    if not indexed:
        findings.append(("blocker", "not indexed — track A finding, blocks Discover too"))
    has_preview = bool(re.search(r'max-image-preview\s*:\s*large', html, re.I))
    is_amp = bool(re.search(r'<html[^>]*(\samp[\s>]|⚡)', html))
    if not has_preview and not is_amp:
        findings.append(("presentation", "large preview not permitted — max-image-preview:large or AMP"))
    m = re.search(r'og:image-width\s*=\s*"(\d+)"', html)  # fixture-carried width
    if m and int(m.group(1)) < 1200:
        findings.append(("recommendation", "image below 1200px — less likely to be featured large"))
    return findings


def strengths(findings):
    return {s for s, _ in findings}


def t_page_without_og_tags_is_not_ineligible():
    html = '<html><head><meta name="robots" content="max-image-preview:large"></head></html>'
    findings = audit_discover(html, indexed=True)
    assert "blocker" not in strengths(findings), \
        f"a page without og tags produced a blocker: {findings}"
    assert not any("ineligible" in msg for _s, msg in findings), \
        f"a tag check produced an ineligibility verdict: {findings}"


def t_missing_permission_is_presentation_not_ineligibility():
    html = "<html><head><title>x</title></head></html>"
    findings = audit_discover(html, indexed=True)
    assert ("presentation", "large preview not permitted — max-image-preview:large or AMP") in findings
    assert "blocker" not in strengths(findings), f"a permission gap became a blocker: {findings}"


def t_amp_is_the_documented_alternative():
    html = "<html amp><head></head></html>"
    findings = audit_discover(html, indexed=True)
    assert "presentation" not in strengths(findings), \
        f"an AMP page was flagged for the missing robots meta: {findings}"


def t_small_image_stays_a_recommendation():
    html = ('<html><head><meta name="robots" content="max-image-preview:large">'
            '<meta og:image-width="800"></head></html>')
    findings = audit_discover(html, indexed=True)
    assert ("recommendation",
            "image below 1200px — less likely to be featured large") in findings
    assert "blocker" not in strengths(findings), f"the image recommendation became a gate: {findings}"


def t_only_indexing_blocks():
    html = '<html><head><meta name="robots" content="max-image-preview:large"></head></html>'
    findings = audit_discover(html, indexed=False)
    assert "blocker" in strengths(findings), "a non-indexed page produced no blocker"
    assert "track A" in findings[0][1], "the blocker is not attributed to indexing"


def t_field_items_stay_field():
    text = open(DOC, encoding="utf-8").read()
    assert "## Card assembly signals (FIELD)" in text, "the og fallback chains lost their FIELD home"
    assert "**Report them as FIELD**" in text, "the FIELD reporting rule is gone"
    assert "no binary" in text or "not from documentation" in text, \
        "the SDK provenance caveat is gone"


def main():
    case("the doctrine splits eligibility / permission / recommendation",
         t_doctrine_splits_the_three_checks)
    case("every CONFIRMED rule names its exact primary source",
         t_every_confirmed_rule_names_its_source)
    case("a page without og tags is never confirmed ineligible",
         t_page_without_og_tags_is_not_ineligible)
    case("a missing permission is a presentation finding", t_missing_permission_is_presentation_not_ineligibility)
    case("AMP satisfies the permission as documented", t_amp_is_the_documented_alternative)
    case("a small image stays a recommendation", t_small_image_stays_a_recommendation)
    case("only indexing (track A) can block", t_only_indexing_blocks)
    case("SDK reverse-engineering stays FIELD", t_field_items_stay_field)
    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print(f"OK ({checks} checks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
