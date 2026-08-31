#!/usr/bin/env python3
"""Structural validator for the seo-aeo-audit plugin repo. Exit 0 = pass."""
from __future__ import annotations

import ast
import importlib.util
import json
import subprocess
import os
import py_compile
import re
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import residue  # noqa: E402
# The pinned `$schema` map, imported rather than copied. Its home is the module that
# also FETCHES those addresses, because this file is a flat script that runs every
# guard at import — the reverse arrow would run the whole validator inside the fetch
# check. See test/check_schemas.py for why the direction is what it is.
from check_schemas import DEAD_SCHEMAS, SCHEMA_FOR  # noqa: E402

residue.open_case("structural validator")
NAME = "seo-aeo-audit"
SKILL_DIR = f"plugins/{NAME}/skills/{NAME}"
REQUIRED_TEMPLATES = ("audit-report.template.md", "action-plan.template.md",
                      "experiments.template.md")
REQUIRED_REFERENCES = (
    "technical-checks.md",
    "discover.md",
    "architecture-and-equity.md",
    "intent-and-content.md",
    "aeo-geo.md",
    "agent-readiness.md",
    "entity-and-brand.md",
    "experience-signals.md",
    "threats-and-defense.md",
    "measurement.md",
    "growth-plays.md",
    "experiments.md",
    "evidence-tiers.md",
    "myths.md",
    "benchmarks.md",
    "deliverable-templates.md",
    "algorithm-updates.md",
    "ranking-model.md",
    "onpage-checks.md",
    "tooling.md",
    "demand-and-conversion.md",
    "linkbuilding.md",
    "prowl-mcp.md",
    "preflight.md",
    "scripts.md",
)
errors = []

# One home for the number-words. Three separate guards below carried their own map
# over overlapping ranges, which is the defect class this file exists to reconcile,
# one level down: a prose count written in words could be read by one map and not by
# another, and the guard that could not read it passed.
NUMWORDS = {
    0: "zero", 1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six",
    7: "seven", 8: "eight", 9: "nine", 10: "ten", 11: "eleven", 12: "twelve",
    13: "thirteen", 14: "fourteen", 15: "fifteen", 16: "sixteen", 17: "seventeen",
    18: "eighteen", 19: "nineteen", 20: "twenty", 21: "twenty-one",
    22: "twenty-two", 23: "twenty-three", 24: "twenty-four", 25: "twenty-five",
    26: "twenty-six", 27: "twenty-seven", 28: "twenty-eight", 29: "twenty-nine",
    30: "thirty", 31: "thirty-one", 32: "thirty-two", 33: "thirty-three",
    34: "thirty-four", 35: "thirty-five", 36: "thirty-six", 37: "thirty-seven",
    38: "thirty-eight", 39: "thirty-nine", 40: "forty",
}
_WORD_TO_N = {w: n for n, w in NUMWORDS.items()}


def numword(text):
    """A prose number as an int, in digits or in words. None when it is neither."""
    t = str(text).strip().strip(".,;:*`()").lower().replace(",", "")
    if t.isdigit():
        return int(t)
    return _WORD_TO_N.get(t)


def semver(v):
    """`0.13.0` -> (0, 13, 0), so releases sort by version and not by string."""
    return tuple(int(x) for x in str(v).split("."))


def fail(m):
    errors.append(m)


def slugify(heading: str) -> str:
    """GitHub's heading-anchor rule: strip code ticks and punctuation, space -> '-'."""
    text = heading.replace("`", "").strip().lower()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    return text.replace(" ", "-")


def heading_slugs(path: str) -> set:
    """Anchors a markdown file actually offers, ignoring headings inside code fences."""
    slugs = set()
    fence = 0
    for line in open(path, encoding="utf-8"):
        m = re.match(r"^\s*(`{3,}|~{3,})", line)
        if m:
            marker = len(m.group(1))
            if fence and marker >= fence:
                fence = 0
            elif not fence:
                fence = marker
            continue
        if fence:
            continue
        h = re.match(r"^#{1,6}\s+(.*?)\s*$", line)
        if h:
            slugs.add(slugify(h.group(1)))
    return slugs


def load_json(rel):
    p = os.path.join(ROOT, rel)
    if not os.path.isfile(p):
        fail(f"missing file: {rel}")
        return None
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        fail(f"invalid JSON in {rel}: {e}")
        return None


mkt = load_json(".claude-plugin/marketplace.json")
plg = load_json(f"plugins/{NAME}/.claude-plugin/plugin.json")
pkg = load_json("package.json")

mkt_name = mkt_ver = None
if mkt:
    plugins = mkt.get("plugins") or []
    if not plugins:
        fail("marketplace.json: plugins[] empty")
    else:
        p0 = plugins[0]
        mkt_name = p0.get("name")
        mkt_ver = p0.get("version")
        src = p0.get("source", "")
        srcdir = os.path.normpath(os.path.join(ROOT, src))
        if not os.path.isfile(os.path.join(srcdir, ".claude-plugin", "plugin.json")):
            fail(f"marketplace source {src!r} has no .claude-plugin/plugin.json")

plg_name = plg.get("name") if plg else None
plg_ver = plg.get("version") if plg else None

# SKILL.md frontmatter
skill_path = os.path.join(ROOT, SKILL_DIR, "SKILL.md")
fm_name = None
if not os.path.isfile(skill_path):
    fail("missing SKILL.md")
else:
    txt = open(skill_path, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n", txt, re.S)
    if not m:
        fail("SKILL.md: no frontmatter")
    else:
        fm = m.group(1)
        nm = re.search(r"^name:\s*(.+)$", fm, re.M)
        dm = re.search(r"^description:\s*(.+)$", fm, re.M)
        fm_name = nm.group(1).strip().strip('"').strip("'") if nm else None
        if not fm_name:
            fail("SKILL.md: empty/missing name")
        if not dm or not dm.group(1).strip():
            fail("SKILL.md: empty/missing description")
        else:
            desc = dm.group(1).strip().strip('"').strip("'")
            if not desc.lower().startswith("use when"):
                fail("SKILL.md: description must start with 'Use when …' (canon)")
            if not re.search(r"[а-яё]", desc, re.I):
                fail("SKILL.md: description must include Russian trigger phrases too (canon)")
        # Spec caps, per field — not one cap over the whole block. The old check
        # capped len(fm) at 1024, which was the DESCRIPTION limit misapplied to the
        # block: the moment `compatibility` arrived (spec-required here, because the
        # skill needs the network and optionally GSC/PSI credentials) the block
        # legitimately outgrew it while every field stayed inside its own cap.
        cmp_m = re.search(r"^compatibility:\s*(.+)$", fm, re.M)
        if cmp_m is None or not cmp_m.group(1).strip():
            fail("SKILL.md: empty/missing compatibility — this skill audits over the "
                 "network with optional GSC/PSI credentials, and the field that "
                 "declares that must not drift back out")
        for _label, _m, _cap in (("description", dm, 1024),
                                 ("compatibility", cmp_m, 500)):
            if _m is None or not _m.group(1).strip():
                continue  # absence already failed above, with its own message
            _val = _m.group(1).strip()
            if len(_val) > _cap:
                fail(f"SKILL.md: {_label} is {len(_val)} chars, the spec cap is {_cap}")
            # A plain YAML scalar that contains ': ' fails yaml.safe_load — the
            # umbrella's pin gate parses this front matter, and the family shipped
            # exactly this defect twice (sheleg-design v1.37.4 and v1.58.0).
            # Quoted scalars may carry it; unquoted ones may not.
            if _val[:1] not in ('"', "'") and ": " in _val:
                fail(f"SKILL.md: {_label} is an unquoted scalar containing ': ' — "
                     f"that is not valid YAML in a plain scalar (write ' - ' instead; "
                     f"the family shipped this twice, see sheleg-design v1.58.1)")

# name sync across the three sources of truth
for label, val in {"marketplace": mkt_name, "plugin.json": plg_name, "frontmatter": fm_name}.items():
    if val != NAME:
        fail(f"name mismatch: {label}={val!r} expected {NAME!r}")

# four-way version sync: marketplace entry, plugin.json, package.json, CHANGELOG top
pkg_ver = pkg.get("version") if pkg else None
if not plg_ver:
    fail("plugin.json: missing version")
if not mkt_ver:
    fail("marketplace.json: plugin entry missing version")
if not pkg_ver:
    fail("package.json: missing version")
vers = {"marketplace": mkt_ver, "plugin.json": plg_ver, "package.json": pkg_ver}
distinct = {v for v in vers.values() if v}

def check_release_gates_on_validate():
    """A release must not publish over a red `validate`.

    On 2026-08-12 `sheleg-dev` tagged v0.4.1 while its own `validate` run for that exact
    tag FAILED, and npm served 0.4.1 four minutes later. The two are separate workflows,
    so nothing connected them: the release ran the structural validator and never the
    negative self-tests, which are steps in `validate.yml`. Six of the family's nine
    repositories were in that state.

    The fix is a `workflow_call` — the release calls the real suite rather than a copy of
    it — and this guard keeps the call there. A dependency nobody checks is a dependency
    somebody removes.
    """
    _wf = os.path.join(ROOT, ".github/workflows")
    _rel, _val = os.path.join(_wf, "release.yml"), os.path.join(_wf, "validate.yml")
    if not (os.path.isfile(_rel) and os.path.isfile(_val)):
        return
    _v = open(_val, encoding="utf-8").read()
    _r = open(_rel, encoding="utf-8").read()
    if not re.search(r"^\s*workflow_call:\s*$", _v, re.M):
        fail(".github/workflows/validate.yml: no `workflow_call:` trigger — the release "
               "workflow cannot run this suite, so a publish goes out over whatever subset "
               "it runs itself")
    if not re.search(r"^\s*uses:\s*\./\.github/workflows/validate\.yml\s*$", _r, re.M):
        fail(".github/workflows/release.yml: does not call ./.github/workflows/validate.yml "
               "— a red validate would not stop a publish, which is how v0.4.1 of a sibling "
               "reached npm with its own suite failing")
    if not re.search(r"^\s*needs:\s*(?:\[[^\]]*\bvalidate\b[^\]]*\]|validate)\s*$", _r, re.M):
        fail(".github/workflows/release.yml: no job declares `needs: validate` — calling "
               "the suite without depending on it lets the release run beside it rather than "
               "after it, which looks gated and is not")


check_release_gates_on_validate()


def check_schema_addresses_are_pinned_and_at_the_document_root():
    """A `$schema` that resolves to nothing is worse than no `$schema` at all — and
    for twenty-five releases both of this repository's manifests declared none at all.

    Nothing failed. `claude plugin validate --strict` was green throughout: it does
    not follow `$schema`, and an absent one is not a manifest error. So the tree read
    as conformant while no editor, no CI validator and no reviewer had anything to
    fetch — the same shape a sibling shipped for eleven releases with a `$schema`
    pointing at `claude-code-plugin.json`, an address SchemaStore answers with 404.

    Three branches rather than one, because that sibling's marketplace was wrong three
    ways at once and fixing the address alone would have left two standing: a dead
    address, the PLUGIN document type declared on a MARKETPLACE document, and a
    declaration nested inside the plugin entry, where `$schema` is inert — only the
    root one is ever read. The fourth branch below is the state this repository was
    actually in: no declaration anywhere.

    This half is offline on purpose — the gate must run without a network — so it can
    only pin. `test/check_schemas.py` is the half that fetches the addresses and
    validates each document against what they serve; CI runs it. Both read
    `SCHEMA_FOR` from that module so the map has one home.
    """
    docs = {".claude-plugin/marketplace.json": mkt,
            f"plugins/{NAME}/.claude-plugin/plugin.json": plg}
    for rel, want in SCHEMA_FOR.items():
        doc = docs.get(rel)
        if doc is None:                      # already reported by load_json
            continue
        got = doc.get("$schema")
        if got is None:
            fail(f"{rel}: declares no $schema — every editor and validator that would "
                 f"check this document has nothing to fetch; declare {want}")
        elif got in DEAD_SCHEMAS:
            fail(f"{rel}: $schema is {got!r}, which SchemaStore answers with "
                 f"{DEAD_SCHEMAS[got]} — a dead address reads as conformance while "
                 f"nothing checks the document; use {want}")
        elif got != want:
            fail(f"{rel}: $schema is {got!r}, not the schema for this document type — "
                 f"a marketplace is not a plugin manifest and the two shapes differ "
                 f"(a marketplace entry requires `source`, a manifest has no such key); "
                 f"use {want}")
    for entry in (mkt or {}).get("plugins", []):
        if "$schema" in entry:
            fail(f".claude-plugin/marketplace.json: plugin entry {entry.get('name')!r} "
                 "carries its own $schema, which is inert — below the document root "
                 "nothing reads it, so a declaration there is decoration that hides the "
                 "absence of the root one")


check_schema_addresses_are_pinned_and_at_the_document_root()

if len(distinct) > 1:
    fail(f"version mismatch across manifests: {vers}")

chg_path = os.path.join(ROOT, "CHANGELOG.md")
if not os.path.isfile(chg_path):
    fail("missing root file: CHANGELOG.md")
else:
    chg = open(chg_path, encoding="utf-8").read()
    vm = re.search(r"^##\s*v(\d+\.\d+\.\d+)", chg, re.M)
    if not vm:
        fail("CHANGELOG.md: no '## vX.Y.Z' entry found")
    elif plg_ver and vm.group(1) != plg_ver:
        fail(f"version mismatch: CHANGELOG top entry=v{vm.group(1)} plugin.json={plg_ver!r}")

# The fifth version home, and the one nobody was reading: `SKILL-CARD.md` published
# `0.25.5` while the tree shipped `0.25.8`. The four-way sync above covers the
# manifests and the CHANGELOG, and the seven `SKILL_VERSION` literals are compared
# further down — the card was outside both, so it drifted three releases and stayed
# green. A public card stating a version that never shipped is the same defect class
# as a prose count, one document over.
_card_path = os.path.join(ROOT, "SKILL-CARD.md")
if not os.path.isfile(_card_path):
    fail("missing root file: SKILL-CARD.md")
else:
    _cm = re.search(r"\|\s*Version\s*\|\s*`([^`]+)`\s*\|", open(_card_path, encoding="utf-8").read())
    if not _cm:
        fail("SKILL-CARD.md: no `| Version | `X.Y.Z` |` row to compare")
    elif plg_ver and _cm.group(1) != plg_ver:
        fail(f"version mismatch: SKILL-CARD.md says v{_cm.group(1)}, "
             f"plugin.json says v{plg_ver} — the card is the public identity of the pack")

# slash command with proper frontmatter
cmd_path = os.path.join(ROOT, f"plugins/{NAME}/commands/{NAME}.md")
if not os.path.isfile(cmd_path):
    fail(f"missing command: plugins/{NAME}/commands/{NAME}.md")
else:
    ctxt = open(cmd_path, encoding="utf-8").read()
    cm = re.match(r"^---\n(.*?)\n---\n", ctxt, re.S)
    if not cm:
        fail("command: no frontmatter")
    else:
        cfm = cm.group(1)
        if not re.search(r"^description:\s*\S", cfm, re.M):
            fail("command: empty/missing description in frontmatter")
        if not re.search(r"^argument-hint:\s*\S", cfm, re.M):
            fail("command: empty/missing argument-hint in frontmatter")

# the contract files must live INSIDE the skill dir — the skills CLI ships only
# the skill's own directory to non-Claude agents.
for ref in REQUIRED_REFERENCES:
    if not os.path.isfile(os.path.join(ROOT, SKILL_DIR, "references", ref)):
        fail(f"missing reference: {SKILL_DIR}/references/{ref}")

# Every bundled script must exist, compile, and stay stdlib-only on python 3.9.
# Discovered, not listed: a hardcoded tuple silently exempts the next script
# somebody adds, and the exemption looks identical to coverage.
_scripts_dir = os.path.join(ROOT, SKILL_DIR, "scripts")
_bundled = sorted(f for f in os.listdir(_scripts_dir)
                  if f.endswith(".py")) if os.path.isdir(_scripts_dir) else []
if not _bundled:
    fail(f"{SKILL_DIR}/scripts/: no bundled scripts found")
for _script in _bundled:
    _rel = f"{SKILL_DIR}/scripts/{_script}"
    _path = os.path.join(ROOT, _rel)
    if not os.path.isfile(_path):
        fail(f"missing script: {_rel}")
        continue
    with tempfile.TemporaryDirectory() as _tmp:
        try:
            py_compile.compile(_path, doraise=True, cfile=os.path.join(_tmp, _script + "c"))
        except py_compile.PyCompileError as _e:
            fail(f"{_rel} does not compile: {_e}")
    _src = open(_path, encoding="utf-8").read()
    if "from __future__ import annotations" not in _src:
        fail(f"{_rel}: missing 'from __future__ import annotations' (python 3.9 support)")
    if re.search(r"\bimport requests\b|\bimport bs4\b|\bfrom google\.", _src):
        fail(f"{_rel}: third-party import — bundled scripts must stay stdlib-only")

# Every finding a script emits points a reader at a reference section. Those
# pointers are plain strings, so nothing else catches a heading rename.
# (Compilation and the stdlib rule are covered for every script by the loop above.)
#
# Written for page_audit.py alone until 2026-08-14, when a second script started
# emitting findings with anchors — the same "guard written against one home of a
# fact that lives in several" shape the 2026-08-10 audit named. Discovered rather
# than listed, for the same reason the compile loop is.
ref_dir = os.path.join(ROOT, SKILL_DIR, "references")
slug_cache: dict = {}
for _script in _bundled:
    script_rel = f"{SKILL_DIR}/scripts/{_script}"
    script_path = os.path.join(ROOT, script_rel)
    if not os.path.isfile(script_path):
        continue
    src = open(script_path, encoding="utf-8").read()
    for ref_file, anchor in sorted(set(re.findall(r"\b([a-z0-9-]+\.md)#([\w-]+)", src))):
        ref_path = os.path.join(ref_dir, ref_file)
        if not os.path.isfile(ref_path):
            fail(f"{script_rel}: finding points at missing reference {ref_file}")
            continue
        if ref_file not in slug_cache:
            slug_cache[ref_file] = heading_slugs(ref_path)
        if anchor not in slug_cache[ref_file]:
            fail(f"{script_rel}: finding anchor {ref_file}#{anchor} matches no heading in {ref_file}")

# Nothing but sources may live under plugins/: both installers copy that tree
# verbatim and `files` ships it to npm, so a stray __pycache__ from running a
# bundled script locally is installed onto every user's machine. v0.7.0 shipped
# exactly that.
for dirpath, dirnames, filenames in os.walk(os.path.join(ROOT, "plugins")):
    for junk in [d for d in dirnames if d == "__pycache__"] + [f for f in filenames if f.endswith(".pyc")]:
        fail(f"build artifact inside the shipped tree: "
             f"{os.path.relpath(os.path.join(dirpath, junk), ROOT)} — delete it before releasing")


# The link-building contract is the one place a deliverable mixes measured and
# assumed data. If the "blank, not zero" rule ever drops out of the reference,
# a contractor gets a CSV whose zeros look like measurements.
_lb = os.path.join(ROOT, SKILL_DIR, "references", "linkbuilding.md")
if os.path.isfile(_lb):
    _lbsrc = open(_lb, encoding="utf-8").read()
    for _needle, _why in (
        ("product-candidate", "the candidate source label"),
        ("blank", "the blank-not-zero rule for unmeasured volume"),
        ("source", "the source column that separates measured from assumed"),
    ):
        if _needle not in _lbsrc:
            fail(f"references/linkbuilding.md: lost {_why} ('{_needle}')")
    if "priority,target_url,keyword" not in _lbsrc:
        fail("references/linkbuilding.md: the CSV column contract is missing")

# ── doctrine guards ──────────────────────────────────────────────────────────
# Rung 3 (a script check) is earned when a failure CLASS has occurred twice.
# This one has: a tool that cannot see something reports its absence as a
# finding (page_audit and JS-injected JSON-LD), and a source that models data
# hands back one number with observed and estimated blended into it (GA4
# consent mode). Both are the same defect — assumed data presented as measured
# — and both arrive through OUR OWN instruments, where non-negotiables #1 and
# #7 cannot see them. A doctrine line alone was not enough: #7 already existed
# and neither case was caught.


def _needles(rel_path: str, needles, label: str):
    """Require each needle in a shipped file, naming what the loss would cost."""
    p = os.path.join(ROOT, rel_path)
    if not os.path.isfile(p):
        fail(f"missing file for {label}: {rel_path}")
        return
    src = open(p, encoding="utf-8").read()
    for needle, why in needles:
        if needle not in src:
            fail(f"{rel_path}: lost {why} ('{needle}')")


# The instrument must declare its own blind spot in the output it prints.
# Reporting "no schema found" from a static fetch is a false finding on every
# site whose CMS injects JSON-LD client-side (Yoast, RankMath, AIOSEO).
_needles(
    f"{SKILL_DIR}/scripts/page_audit.py",
    (("server-rendered HTML only", "the JS-blind caveat on the schema inventory"),
     ("jsonld_caveat", "the machine-readable caveat field in the report payload")),
    "the page_audit blindness caveat",
)

# agent_surface.py carries a third blind spot of its own, and it is the one a
# checklist-shaped instrument loses first: it measures PRESENCE, and presence is
# not effect. Without that sentence in the report, a draft specification's absence
# reads as a confirmed defect and the triage formula multiplies by the wrong
# number. The one-url caveat is the same class as page_audit's JS blindness —
# absence on the page you probed is not absence on the site.
_needles(
    f"{SKILL_DIR}/scripts/agent_surface.py",
    (("Presence is not effect", "the presence-vs-effect blind spot in the docstring"),
     ("Presence is `CONFIRMED`", "the same statement in the rendered report"),
     ("ONE url", "the one-url caveat, which is the false finding graders produce most"),
     ("server-rendered HTML only", "the JS-blind caveat inherited from page_audit")),
    "the agent_surface blindness caveats",
)

# GA4 blends modelled with observed behind one number. An audit that sizes a
# prize from that number breaks #7 by proxy, so measurement.md must carry the
# observable check, not a vague warning.
_needles(
    f"{SKILL_DIR}/references/measurement.md",
    (("Blended", "the reporting-identity setting that turns blending on"),
     ("Including estimated user data", "the visible GA4 indicator an auditor can check"),
     ("BigQuery", "the observed-only escape hatch")),
    "the GA4 modelled-data guard",
)

# The doctrine that generalises both cases. If it drops out of SKILL.md the
# guards above degrade into two unexplained string checks.
_needles(
    f"{SKILL_DIR}/SKILL.md",
    (("blind spot", "the instrument-blindness non-negotiable"),),
    "the instrument-blindness doctrine",
)

# npm package: bin resolves, files whitelist ships the sources
if pkg:
    bin_map = pkg.get("bin") or {}
    if not bin_map:
        fail("package.json: missing bin entry")
    for bin_name, bin_rel in bin_map.items():
        if not os.path.isfile(os.path.join(ROOT, bin_rel)):
            fail(f"package.json bin {bin_name!r} -> missing file {bin_rel!r}")
    files = pkg.get("files") or []
    for req in ("bin", "plugins"):
        if req not in files:
            fail(f"package.json: files[] must whitelist {req!r}")

# Cursor channel: every cursor/rules/*.mdc must carry description + alwaysApply
cursor_dir = os.path.join(ROOT, "cursor", "rules")
mdcs = [f for f in os.listdir(cursor_dir) if f.endswith(".mdc")] if os.path.isdir(cursor_dir) else []
if not mdcs:
    fail("cursor/rules: no .mdc rules found")
for f in mdcs:
    mtxt = open(os.path.join(cursor_dir, f), encoding="utf-8").read()
    mm = re.match(r"^---\n(.*?)\n---\n", mtxt, re.S)
    if not mm:
        fail(f"cursor/rules/{f}: no frontmatter")
        continue
    mfm = mm.group(1)
    if not re.search(r"^description:\s*\S", mfm, re.M):
        fail(f"cursor/rules/{f}: empty/missing description")
    if not re.search(r"^alwaysApply:\s*(true|false)\s*$", mfm, re.M):
        fail(f"cursor/rules/{f}: alwaysApply must be true or false")
    # .mdc files get copied into foreign projects — any relative link dangles there.
    for target in re.findall(r"\[[^\]]*\]\(([^)\s]+)\)", mtxt):
        if not target.startswith(("http://", "https://", "mailto:", "#")):
            fail(f"cursor/rules/{f}: relative link {target!r} — .mdc must embed contracts inline")

# The Cursor channel is a full copy of the doctrine for a different agent, and it
# has already drifted: it shipped six non-negotiables while SKILL.md had seven,
# so Cursor users ran without the measured-vs-assumed rule and nothing said so.
_nn_re = re.compile(r"^\s*\d+\.\s+\*\*", re.M)


def _nn_count(path: str) -> int:
    """How many numbered non-negotiables a doctrine file carries. -1 = no section."""
    if not os.path.isfile(path):
        return -1
    txt = open(path, encoding="utf-8").read()
    m = re.search(r"^#{2,3}\s+Non-negotiables\s*$(.*?)(?=^#{2,3}\s|\Z)", txt, re.M | re.S)
    return len(_nn_re.findall(m.group(1))) if m else -1


_skill_nn = _nn_count(os.path.join(ROOT, SKILL_DIR, "SKILL.md"))
if _skill_nn < 1:
    fail("SKILL.md: no '## Non-negotiables' section with a numbered list")
else:
    for f in mdcs:
        _cn = _nn_count(os.path.join(cursor_dir, f))
        if _cn != _skill_nn:
            fail(f"cursor/rules/{f}: carries {_cn} non-negotiable(s), SKILL.md has "
                 f"{_skill_nn} — the Cursor channel must ship the whole doctrine")
    # The slash command is the third channel, and it was the unguarded one: it
    # restated two non-negotiables and read as a complete list. The Cursor rule was
    # count-checked from the day it drifted; the command never was.
    _cmd_nn_re = re.compile(r"^\s*\d+\.\s+\*\*", re.M)
    _cmd_txt = open(cmd_path, encoding="utf-8").read() if os.path.isfile(cmd_path) else ""
    _cmd_sec = re.search(r"^##\s+The eight non-negotiables[^\n]*$(.*)", _cmd_txt, re.M | re.S)
    if not _cmd_sec:
        fail("the slash command has no non-negotiables section — a command that names "
             "two of them reads as the whole doctrine, which is how it shipped")
    else:
        _cmd_nn = len(_cmd_nn_re.findall(_cmd_sec.group(1)))
        if _cmd_nn != _skill_nn:
            fail(f"the slash command carries {_cmd_nn} non-negotiable(s), SKILL.md has "
                 f"{_skill_nn} — every channel ships the whole doctrine")

# CONTRIBUTING.md tells a contributor what this file enforces, and had fallen four
# guards behind — the same drift as every other prose summary of a moving thing.
# Each guard family added here names itself, and the name has to survive in that
# paragraph. It does not prove the description is *accurate*; it proves nobody can
# add a guard family and leave the summary untouched.
_GUARD_FAMILIES = (
    "four-way version sync",
    "card version",
    "standard-library only",
    "tier vocabulary",
    "myth count",
    "table integrity",
    "script reachability",
    "error flattening",
    "defect count",
    "coverage vocabulary",
    "provenance",
    "I/O surface",
    "gate homes",
    "flat copies",
    "corpus freshness",
    "body budget",
    "board status",
    "ledger coverage",
    "confirmed tally",
    "run stamps",
    "declared schemas",
)
_contrib = open(os.path.join(ROOT, "CONTRIBUTING.md"), encoding="utf-8").read()
for _g in _GUARD_FAMILIES:
    if _g not in _contrib:
        fail(f"CONTRIBUTING.md does not mention the {_g!r} guard family — the "
             f"summary of validate.py has drifted from what it runs")

# A blank line inside a markdown table ends the table: the rows after it render as
# loose text, and the content still reads fine in the source, so nobody sees it.
# It happened twice in one run — appending rows by inserting before the following
# heading leaves the original blank line in the middle.
for _dirpath, _dirnames, _filenames in os.walk(os.path.join(ROOT, SKILL_DIR)):
    for _fn in sorted(f for f in _filenames if f.endswith(".md")):
        _fp = os.path.join(_dirpath, _fn)
        _rel = os.path.relpath(_fp, ROOT)
        _prev_row, _saw_blank = False, False
        for _n, _line in enumerate(open(_fp, encoding="utf-8"), 1):
            _stripped = _line.rstrip("\n")
            if _prev_row and _stripped == "":
                _saw_blank = True
                continue
            if _saw_blank and _stripped.startswith("|"):
                fail(f"{_rel}:{_n}: table row separated from its table by a blank "
                     f"line — the rows above it stop being a table here")
            _saw_blank = False
            _prev_row = _stripped.startswith("|")

# The third way a table breaks: a row with more cells than its header. Markdown
# drops the surplus, so the row renders shifted and its last column disappears —
# in growth-plays.md that silently deleted play P5's evidence tier, in the file
# whose closing rule is "never ship a FIELD or HYPOTHESIS play sitewide". The
# blank-line guard above could not see it. Code fences are skipped: a fenced
# two-line row template is deliberate, not a broken table.
for _dirpath, _dirnames, _filenames in os.walk(os.path.join(ROOT, SKILL_DIR)):
    for _fn in sorted(f for f in _filenames if f.endswith(".md")):
        _fp = os.path.join(_dirpath, _fn)
        _rel = os.path.relpath(_fp, ROOT)
        _fence, _hdr_cells, _hdr_line = 0, None, 0
        for _n, _line in enumerate(open(_fp, encoding="utf-8"), 1):
            _s = _line.rstrip("\n").strip()
            _m = re.match(r"^(`{3,}|~{3,})", _s)
            if _m:
                _marker = len(_m.group(1))
                if _fence and _marker >= _fence:
                    _fence = 0
                elif not _fence:
                    _fence = _marker
                _hdr_cells = None
                continue
            if _fence or not _s.startswith("|"):
                if not _fence:
                    _hdr_cells = None
                continue
            _cells = len(_s.strip("|").split("|"))
            if re.match(r"^\|[\s:\-|]+\|$", _s):
                continue          # the separator row confirms the header above it
            if _hdr_cells is None:
                _hdr_cells, _hdr_line = _cells, _n
            elif _cells != _hdr_cells:
                fail(f"{_rel}:{_n}: table row has {_cells} cells, the header at line "
                     f"{_hdr_line} has {_hdr_cells} — markdown drops the surplus, so the "
                     f"last column of this row does not render")

# A prose count about a list, sitting next to the list, is the drift this repo
# keeps re-discovering: CONTRIBUTING said nineteen references while the validator
# enforced twenty-one, and the README's myth count went stale the moment two rows
# were added. Second occurrence of the class, so it stops being a review item.
#
# The 2026-08-10 audit found the third form of it: this check was written against
# the ONE sentence that had drifted, while the same count lived in four places. It
# was green while README said 29 in its second mention, SKILL.md said 30 and the
# Cursor rule said 29, against 32 rows. Standing instruction #4 says count the
# homes; so the homes are enumerated here and every one of them is read.


def _table_rows(path: str, header_prefix: str) -> int:
    """Rows in the first markdown table whose header line starts with the prefix."""
    if not os.path.isfile(path):
        return 0
    rows, in_table = 0, False
    for line in open(path, encoding="utf-8"):
        if line.startswith(header_prefix):
            in_table = True
            continue
        if in_table:
            if not line.startswith("|"):
                break
            if not line.startswith("|---"):
                rows += 1
    return rows


_myths = os.path.join(ROOT, SKILL_DIR, "references", "myths.md")
_myth_rows = _table_rows(_myths, "| Claim | Reality |")
if not _myth_rows:
    fail("myths.md: could not find the claim table — the count check is blind")
else:
    # (file, regex with one numeric group, what the sentence is for)
    _MYTH_COUNT_HOMES = (
        ("README.md",
         r"myth guard\*\* that refuses (\d+) popular tactics",
         "the feature list"),
        ("README.md",
         r"myth guard\.\*\* (\d+) popular tactics with published",
         "the closing pitch"),
        (f"{SKILL_DIR}/SKILL.md",
         r"most-requested of the \*\*(\d+)\*\* refuted claims",
         "the myth-guard section"),
        ("cursor/rules/seo-aeo-audit.mdc",
         r"out of (\d+) refuted claims",
         "the Cursor channel"),
    )
    for _rel, _pat, _what in _MYTH_COUNT_HOMES:
        _p = os.path.join(ROOT, _rel)
        if not os.path.isfile(_p):
            fail(f"missing file for the myth-count check: {_rel}")
            continue
        _txt = open(_p, encoding="utf-8").read()
        _m = re.search(_pat, _txt)
        if not _m:
            fail(f"{_rel}: the myth count in {_what} changed shape, so the check can no "
                 f"longer read it (expected /{_pat}/) — a count nothing reads is the "
                 f"drift this guard exists for")
        elif int(_m.group(1)) != _myth_rows:
            fail(f"{_rel}: {_what} says {_m.group(1)} myths, myths.md carries {_myth_rows}")

    # The fifth home, and the one that only announces itself in CI: the negative
    # self-tests plant a WRONG myth count over the right one, so both numbers are
    # written into the workflow. Add a myth row without touching them and the
    # plants stop landing — `plant_guard` then refuses, correctly, and the first
    # anyone hears of it is a red pipeline on a green local gate. That happened on
    # v0.19.0. The `from` side of each plant is the current count, so it is
    # checkable here, where it costs one run of the gate instead of one of CI.
    _wf = os.path.join(ROOT, ".github", "workflows", "validate.yml")
    if not os.path.isfile(_wf):
        fail("missing .github/workflows/validate.yml for the myth-plant check")
    else:
        _wft = open(_wf, encoding="utf-8").read()
        for _pat, _what in (
            (r'"most-requested of the \*\*(\d+)\*\*"', "the SKILL.md myth plant"),
            (r'"out of (\d+) refuted claims"', "the Cursor-rule myth plant"),
        ):
            _m = re.search(_pat, _wft)
            if not _m:
                fail(f"validate.yml: {_what} changed shape, so nothing checks that it "
                     f"still matches the tree (expected /{_pat}/)")
            elif int(_m.group(1)) != _myth_rows:
                fail(f"validate.yml: {_what} plants over {_m.group(1)}, myths.md carries "
                     f"{_myth_rows} — the plant will not land and CI will refuse it")

    # The two short lists must also agree on their own size, and with each other's
    # claim about it: SKILL.md said "fourteen" and listed 14, the Cursor rule said
    # "thirteen" and listed 13, and nothing compared the two channels.
    _WORDS = {"ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
              "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
              "nineteen": 19, "twenty": 20}
    _skill_src = open(os.path.join(ROOT, SKILL_DIR, "SKILL.md"), encoding="utf-8").read()
    _mdc_src = open(os.path.join(ROOT, "cursor", "rules", "seo-aeo-audit.mdc"),
                    encoding="utf-8").read()

    def _shortlist_claim(txt: str, pat: str) -> int | None:
        m = re.search(pat, txt, re.I)
        return _WORDS.get(m.group(1).lower()) if m else None

    def _shortlist_items(txt: str, start: str, stop: str) -> int:
        """Count ` · `-separated entries in the short list between two markers."""
        try:
            body = txt.split(start, 1)[1].split(stop, 1)[0]
        except IndexError:
            return -1
        return len([p for p in body.split("·") if p.strip()])

    _skill_claim = _shortlist_claim(_skill_src, r"The (\w+) most-requested of")
    _skill_items = _shortlist_items(_skill_src, "read it before\nanswering a tactic question",
                                    "When the user asks for one of these")
    if _skill_claim is None:
        fail("SKILL.md: the myth short-list size is no longer stated in words the check "
             "can read (expected 'The <word> most-requested of')")
    elif _skill_items < 0:
        fail("SKILL.md: the myth short list moved; the item count cannot be read")
    elif _skill_claim != _skill_items:
        fail(f"SKILL.md says {_skill_claim} most-requested myths and lists {_skill_items}")
    _mdc_claim = _shortlist_claim(_mdc_src, r"The (\w+) asked for most often")
    _mdc_items = _shortlist_items(_mdc_src, "install it for the counter-evidence and the working "
                                            "alternative to\neach):", "## Deliverables")
    if _mdc_claim is None:
        fail("cursor/rules: the myth short-list size is no longer stated in readable words")
    elif _mdc_items < 0:
        fail("cursor/rules: the myth short list moved; the item count cannot be read")
    elif _mdc_claim != _mdc_items:
        fail(f"cursor/rules says {_mdc_claim} most-asked myths and lists {_mdc_items}")
    elif _skill_claim is not None and _skill_claim != _mdc_claim:
        fail(f"the myth short list is {_skill_claim} items in SKILL.md and {_mdc_claim} in the "
             f"Cursor rule — the two channels must offer the same shortlist")

# The play count is the same class of fact as the myth count, and it had drifted
# the same way: README said 60 against 61 rows, after an earlier correction from
# 59 to 60. A prose number about a table gets a check, not a review item.
_plays = os.path.join(ROOT, SKILL_DIR, "references", "growth-plays.md")
if os.path.isfile(_plays):
    _play_rows = len(re.findall(r"^\| *`?[A-Z]+\d+ *\|", open(_plays, encoding="utf-8").read(),
                                re.M))
    _readme_src = open(os.path.join(ROOT, "README.md"), encoding="utf-8").read()
    _pm = re.search(r"\*\*Growth plays\*\* \| (\d+) plays", _readme_src)
    if not _play_rows:
        fail("growth-plays.md: no play rows found — the count check is blind")
    elif not _pm:
        fail("README.md: the growth-plays row changed shape; the play-count check can no "
             "longer read it (expected '**Growth plays** | N plays')")
    elif int(_pm.group(1)) != _play_rows:
        fail(f"README.md says {_pm.group(1)} plays, growth-plays.md carries {_play_rows}")

# The reference count is the oldest instance of this class — CONTRIBUTING said
# nineteen while the validator enforced twenty-one, in 2026-08-04 — and DOCMAP still
# marked it **review** on the grounds that it is "a prose number about a tuple".
# It went stale again the moment a twenty-second reference shipped, in the same tree
# as the guards written for exactly this. Third occurrence of the class in one file,
# so it stops being a review item (standing instruction #3).
# The tuple is the declaration; the directory is the fact. Compared both ways since
# 2026-08-16, when `preflight.md` and `scripts.md` had been shipping in every tarball
# and on every channel while the tuple said 23 and three documents repeated it. The
# prose reconciler below reads `len(REQUIRED_REFERENCES)`, so without this the number
# could drift as far as the tuple did and stay green the whole way.
_ref_dir = os.path.join(ROOT, SKILL_DIR, "references")
if os.path.isdir(_ref_dir):
    _on_disk = {f for f in os.listdir(_ref_dir) if f.endswith(".md")}
    _declared = set(REQUIRED_REFERENCES)
    for _extra in sorted(_on_disk - _declared):
        fail(f"references/{_extra} ships but is not in REQUIRED_REFERENCES — every "
             "reference is declared, or the count that three documents restate is "
             "measured against a number nobody keeps")
    for _missing in sorted(_declared - _on_disk):
        fail(f"REQUIRED_REFERENCES names references/{_missing}, which is not on disk")

_WORDNUM = {n: NUMWORDS[n] for n in range(19, 31)}
_ref_n = len(REQUIRED_REFERENCES)
_ref_word = _WORDNUM.get(_ref_n)
for _rel, _pats in (("README.md", (r"(\w+(?:-\w+)?) reference contracts ship",
                                   r"across the (\w+(?:-\w+)?) contracts",
                                   r"references/\*\.md\s+(\d+) contract files")),
                    ("CONTRIBUTING.md", (r"mostly \*\*knowledge\*\* — (\w+(?:-\w+)?)",
                                         r"that all (\w+(?:-\w+)?)\n?references exist",
                                         r"that all (\w+(?:-\w+)?)"))):
    _txt = open(os.path.join(ROOT, _rel), encoding="utf-8").read()
    for _pat in _pats:
        _m = re.search(_pat, _txt)
        if not _m:
            continue          # that sentence may not exist in this file
        _found = _m.group(1).lower()
        _ok = (_found == str(_ref_n)) or (_ref_word and _found == _ref_word)
        if not _ok:
            fail(f"{_rel}: says {_found!r} references, REQUIRED_REFERENCES has {_ref_n} "
                 f"({_ref_word}) — /{_pat}/")

# Prowl's tool count is a third prose number with several homes: README said ~408
# while tooling.md and prowl-mcp.md said ~448.
_prowl_counts = {}
for _rel in ("README.md", f"{SKILL_DIR}/references/tooling.md",
             f"{SKILL_DIR}/references/prowl-mcp.md"):
    _p = os.path.join(ROOT, _rel)
    if os.path.isfile(_p):
        _prowl_counts[_rel] = set(re.findall(r"~?(\d{3}) (?:provider )?tools",
                                            open(_p, encoding="utf-8").read()))
_seen_prowl = set().union(*_prowl_counts.values()) if _prowl_counts else set()
if len(_seen_prowl) > 1:
    fail(f"the Prowl provider-tool count disagrees across its homes: "
         f"{ {k: sorted(v) for k, v in _prowl_counts.items() if v} }")

# The gate is one fact with several homes: scripts/check-docs.sh runs it, CI repeats
# it, CONTRIBUTING and README tell a contributor what to run, the PR template asks
# them to paste the output, and CLAUDE.md and docs/DOCMAP.md are the two documents an
# agent reads to learn what the gate IS. CONTRIBUTING named two of the four commands
# and called CI "the same two"; the PR template was not counted as a home at all, so
# it kept asking for two of five long after that was corrected everywhere else.
#
# The two documents that EXPLAIN the gate were the last two nobody read: on 2026-08-20
# `CLAUDE.md` and `docs/DOCMAP.md` each published five of the gate's seven commands —
# `plant_guard_test.py` and `test_agent_surface.py` missing from both — while DOCMAP's
# own sentence said "It runs exactly these and nothing else". So the home list is a
# tuple, the loop reads it, and the prose that COUNTS the homes is compared to `len()`:
# the row at DOCMAP said three homes, its propagation matrix said five, and the checker
# read four. Three numbers for one tuple is the shape this file exists to refuse.
_GATE_HOMES = (
    "CONTRIBUTING.md",
    "README.md",
    os.path.join(".github", "PULL_REQUEST_TEMPLATE.md"),
    os.path.join(".github", "workflows", "validate.yml"),
    "CLAUDE.md",
    os.path.join("docs", "DOCMAP.md"),
)
_gate_path = os.path.join(ROOT, "scripts", "check-docs.sh")
_gate_cmds = []
if not os.path.isfile(_gate_path):
    fail("missing scripts/check-docs.sh — the documentation gate")
else:
    _gate_cmds = re.findall(r"^python3 (test/\S+\.py)\s*$", open(_gate_path, encoding="utf-8").read(),
                            re.M)
    if len(_gate_cmds) < 2:
        fail("scripts/check-docs.sh: no `python3 test/*.py` lines found — the gate-parity "
             "check cannot read it")
    for _rel in _GATE_HOMES:
        _p = os.path.join(ROOT, _rel)
        if not os.path.isfile(_p):
            fail(f"{_rel} is named as a home of the gate commands and does not exist")
            continue
        _txt = open(_p, encoding="utf-8").read()
        for _cmd in _gate_cmds:
            if _cmd not in _txt:
                fail(f"{_rel} does not mention `{_cmd}`, which scripts/check-docs.sh runs — "
                     f"a reader following that document runs a subset of the gate")

    # The home COUNT is itself a prose fact, and it had three values. DOCMAP states it
    # twice — once in the single-home table, once in the propagation matrix — and both
    # are read out of the document and compared to this tuple.
    _dm_path = os.path.join(ROOT, "docs", "DOCMAP.md")
    if os.path.isfile(_dm_path):
        _dm = open(_dm_path, encoding="utf-8").read()
        for _pat, _what in ((r"appear in all (\w+(?:-\w+)?) of them", "the single-home row"),
                            (r"gate parity across all (\w+(?:-\w+)?) of them",
                             "the propagation-matrix row")):
            _m = re.search(_pat, _dm)
            if not _m:
                fail(f"docs/DOCMAP.md: {_what} no longer counts the gate's homes in a form "
                     f"this check can read (expected /{_pat}/) — a home list nothing reads "
                     f"is how one document said three, another five, and the checker four")
            elif numword(_m.group(1)) != len(_GATE_HOMES):
                fail(f"docs/DOCMAP.md: {_what} says the gate commands have "
                     f"{_m.group(1)!r} homes beside the script; `_GATE_HOMES` holds "
                     f"{len(_GATE_HOMES)} ({NUMWORDS[len(_GATE_HOMES)]}): "
                     f"{', '.join(_GATE_HOMES)}")

# Every documented invocation must resolve from where the agent is standing, which
# is the user's project — not the skill directory. Eleven bash lines read
# `python3 scripts/<name>.py`, and all eleven failed with "No such file or
# directory" in the only environment the skill is ever used in. The failure is
# quiet in the way that matters: the agent falls back to checking by hand, the
# whole audit drops to the bottom rung of the evidence ladder, and nothing says so.
#
# Three homes, because the acceptance walk found the guard had been written against
# one: after SKILL.md was fixed, the README still carried eight bare invocations and
# the slash command a ninth — and the README's did not resolve for a developer in a
# clone either, since `scripts/` at the repository root is the documentation gate.
#
# A fourth home appeared on 2026-08-16 without anyone adding it: the body split for
# the token budget moved every invocation into `references/scripts.md`, and this
# list did not follow. The guard kept passing because it was looking where the
# invocations used to be — the exact shape the comment above describes, one move
# later. So the reference set is DISCOVERED rather than listed: a new reference
# joins this check by existing.
_INVOCATION_HOMES = (
    os.path.join(SKILL_DIR, "SKILL.md"),
    "README.md",
    os.path.join("plugins", "seo-aeo-audit", "commands", "seo-aeo-audit.md"),
) + tuple(
    os.path.join(SKILL_DIR, "references", _f)
    for _f in sorted(os.listdir(os.path.join(ROOT, SKILL_DIR, "references")))
    if _f.endswith(".md")
)
for _rel in _INVOCATION_HOMES:
    _txt = open(os.path.join(ROOT, _rel), encoding="utf-8").read()
    # Runnable forms only. A backticked `scripts/page_audit.py` used as a *name*
    # is fine and reads better; what breaks is a line somebody copies and runs.
    _bare = re.findall(r"python3\s+\"?(?:\./)?scripts/(\w+\.py)", _txt)
    if _bare:
        fail(f"{_rel} names {sorted(set(_bare))} by a path relative to the caller's "
             f"working directory — write it as \"$SKILL_DIR/scripts/<name>.py\". "
             f"Nobody stands where that path resolves: an agent stands in the user's "
             f"project, a contributor in a clone whose root `scripts/` is the gate")

_skill_md = open(os.path.join(ROOT, SKILL_DIR, "SKILL.md"), encoding="utf-8").read()
if "SKILL_DIR" not in _skill_md:
    fail("SKILL.md documents no way to resolve the skill directory, so every script "
         "invocation in it is unreachable from a project root")
if "${CLAUDE_PLUGIN_ROOT}" not in _skill_md:
    fail("SKILL.md must name ${CLAUDE_PLUGIN_ROOT} — it is the documented expansion "
         "for skill content in a Claude Code plugin, and the only channel-native way "
         "to resolve the scripts")

# `_flat` has one home per script because these ship as standalone files with no
# shared module. Four renderers interpolated a network error straight into markdown:
# a Google error page carries newlines, the first one ends the table row, and every
# row after it stops rendering. Five of preflight's seven rows were being lost.
_RENDERERS = ("preflight.py", "url_inspection.py", "psi_pull.py", "page_audit.py",
              "agent_surface.py")
for _r in _RENDERERS:
    _src = open(os.path.join(ROOT, SKILL_DIR, "scripts", _r), encoding="utf-8").read()
    if "def _flat(" not in _src:
        fail(f"{_r} renders network errors into markdown without _flat() — one "
             f"newline in an API error ends the row and hides every row after it")
    for _m in re.finditer(r"lines\.append\(f\"[^\"]*\{r\['(error|detail)'\]\}", _src):
        fail(f"{_r}: r['{_m.group(1)}'] reaches markdown unflattened at offset "
             f"{_m.start()} — wrap it in _flat()")

# The 2026-08-10 defect total, stated in six places. It went stale in the release
# that appended D42-D43 after the v0.12.0 rebase: the ledger's own summary said
# "43 defects" and "green against all forty-one" in one sentence. Homes are listed
# as data, with the phrase each one uses, so a reworded home fails loudly rather
# than dropping out of the check (CLAUDE.md rule 1: count the homes first).
_LEDGER = os.path.join("docs", "audit", "2026-08-10-defect-ledger.md")
_DEFECT_COUNT_HOMES = (
    (_LEDGER, r"\*\*(\S+) defects\.\*\*"),
    (_LEDGER, r"gate is green against all (\S+)\s"),
    (os.path.join("docs", "audit", "2026-08-10-improvement-plan.md"), r"ledger's (\S+) rows"),
    (os.path.join("docs", "evidence", "retro.md"), r"exited 0 against (\S+) defects"),
    ("CHANGELOG.md", r"\*\*(\S+) defects\*\*"),
    ("CHANGELOG.md", r"gate was green against all (\S+)\."),
)
_WORD = {41: "forty-one", 42: "forty-two", 43: "forty-three", 44: "forty-four",
         45: "forty-five"}
_defect_n = len(re.findall(r"^### D\d+", open(os.path.join(ROOT, _LEDGER),
                                              encoding="utf-8").read(), re.M))
_ok_forms = {str(_defect_n), _WORD.get(_defect_n, ""), _WORD.get(_defect_n, "").capitalize()}
for _rel, _pat in _DEFECT_COUNT_HOMES:
    _txt = open(os.path.join(ROOT, _rel), encoding="utf-8").read()
    _m = re.search(_pat, _txt)
    if not _m:
        fail(f"{_rel}: the defect-count phrase {_pat!r} is gone — a home that is "
             f"reworded silently leaves the reconciler, which is how this count "
             f"drifted in the first place")
    elif _m.group(1) not in _ok_forms:
        fail(f"{_rel} states the defect total as {_m.group(1)!r}; the ledger "
             f"enumerates {_defect_n} `### D<n>` rows")

# Every finding a script emits must have a tier in FINDING_TIERS. The behaviour
# tests prove the fixtures carry one; this proves the next finding somebody adds
# cannot ship without one, which is the case a fixture cannot cover.
#
# Every script that declares FINDING_TIERS is checked, not page_audit.py alone: the
# emitters have two shapes now — `add("high", "code", …)` and an inline dict with a
# `"code":` key — and a check that knows one shape exempts the other silently.
for _script in _bundled:
    _sp = os.path.join(ROOT, SKILL_DIR, "scripts", _script)
    _ssrc = open(_sp, encoding="utf-8").read()
    if "FINDING_TIERS" not in _ssrc:
        continue
    _declared = set(re.findall(r'^\s+"([a-z0-9-]+)": "(?:CONFIRMED|STUDY|FIELD|HYPOTHESIS)",',
                               _ssrc, re.M))
    _emitted = set(re.findall(r'add\(\s*"[a-z]+",\s*"([a-z0-9-]+)"', _ssrc))
    _emitted |= set(re.findall(r'"code":\s*"([a-z0-9-]+)"', _ssrc))
    for _code in sorted(_emitted - _declared):
        fail(f"{_script} emits finding {_code!r} with no entry in FINDING_TIERS — "
             f"non-negotiable #2 makes the tier the multiplier in the triage formula")
    if not _emitted:
        fail(f"{_script}: declares FINDING_TIERS but no finding codes were found — the "
             f"tier-coverage check is blind")

# The CWV thresholds live in psi_pull.py and in experience-signals.md. Two homes,
# and the numbers decide whether a page passes.
_psi = os.path.join(ROOT, SKILL_DIR, "scripts", "psi_pull.py")
_exp = os.path.join(ROOT, SKILL_DIR, "references", "experience-signals.md")
if os.path.isfile(_psi) and os.path.isfile(_exp):
    _psisrc = open(_psi, encoding="utf-8").read()
    _expsrc = open(_exp, encoding="utf-8").read()
    for _key, _short, _good, _poor in (
            ("LARGEST_CONTENTFUL_PAINT_MS", "LCP", "2500", "4000"),
            ("INTERACTION_TO_NEXT_PAINT", "INP", "200", "500"),
            ("CUMULATIVE_LAYOUT_SHIFT_SCORE", "CLS", "0.10", "0.25")):
        if not re.search(rf'"{_key}":\s*\("{_short}",\s*{_good},\s*{_poor}', _psisrc):
            fail(f"psi_pull.py: {_short} thresholds are no longer ({_good}, {_poor}) — "
                 f"experience-signals.md publishes those numbers as the pass bands")
        _row = re.search(rf"\*\*{_short}\*\*[^|]*\|([^|]*)\|([^|]*)\|([^|]*)\|", _expsrc)
        if not _row:
            fail(f"experience-signals.md: no threshold row for {_short} — psi_pull.py's "
                 f"bands have no documented home")
        else:
            # The doc states LCP in seconds and the code in milliseconds, so compare
            # the numbers the row actually contains against the value in either unit
            # rather than string-matching one spelling of it.
            _nums = {float(x) for x in re.findall(r"\d+(?:\.\d+)?", " ".join(_row.groups()))}
            for _label, _raw in (("good", _good), ("poor", _poor)):
                _v = float(_raw)
                _forms = {_v, round(_v / 1000, 3)} if _v >= 100 else {_v}
                if not (_forms & _nums):
                    fail(f"experience-signals.md: the {_short} row carries {sorted(_nums)} and "
                         f"none of them is psi_pull.py's {_label} threshold {_raw} "
                         f"(in ms or s)")

# algorithm-updates.md carries a "Verified as of" stamp and its own refresh
# protocol says to move it. It said 2026-07-28 while the file already held a row
# dated 2026-07-30, so the copy that travels to every agent was stamped older than
# its own newest claim.
_au = os.path.join(ROOT, SKILL_DIR, "references", "algorithm-updates.md")
if os.path.isfile(_au):
    _ausrc = open(_au, encoding="utf-8").read()
    _refetch = re.search(r"\*\*Sources last re-fetched:\s*(\d{4}-\d{2}-\d{2})", _ausrc)
    _newest = re.search(r"\*\*Newest row in this file:\s*(\d{4}-\d{2}-\d{2})", _ausrc)
    # Every date in the file except the two header claims themselves.
    _body = _ausrc.split("Primary source", 1)[-1]
    _dates = sorted(re.findall(r"\b(20\d{2}-\d{2}-\d{2})\b", _body))
    if not _refetch:
        fail("algorithm-updates.md: no '**Sources last re-fetched: YYYY-MM-DD**' line")
    if not _newest:
        fail("algorithm-updates.md: no '**Newest row in this file: YYYY-MM-DD**' line — the "
             "two freshness facts must be stated separately, because one of them used to "
             "stand in for the other")
    elif _dates and _dates[-1] != _newest.group(1):
        fail(f"algorithm-updates.md says its newest row is {_newest.group(1)} but the newest "
             f"date in the file is {_dates[-1]} — a row was appended without moving the line")

# Every plant in the workflow must still land — checked HERE, before the tag.
#
# A negative self-test is a string substitution into a real file, so it rots the
# moment the fact it guards is reworded. v0.21.0 hit this twice: the freshness
# plant was pinned to the literal `2026-07-30` and the reference-count plant to
# `twenty-three`, and both facts were exactly what the release changed. CI refused,
# correctly — a plant that does not land leaves its check unproven — but it refused
# AFTER the tag was public, which is the one moment the release workflow cannot
# recover from on its own.
#
# So the local gate reads the workflow and asserts each needle is still present.
# It is a cheap parse, not an execution: nothing is planted, nothing is written.
_wf = os.path.join(ROOT, ".github", "workflows", "validate.yml")
if os.path.isfile(_wf):
    _wfsrc = open(_wf, encoding="utf-8").read()
    # `plant_edit.py` is not the only way a step plants: a `perl -0pi -e 's{A}{B}'`
    # over a named file is the same thing with the needle inside a substitution.
    # That form is how a plant reached CI on 2026-08-16 after the needle it depended
    # on was moved into another file — this guard was looking only at the first form.
    _pats = [r'plant_edit\.py sub ("?[^"\s]+"?) (".*?"|\'.*?\')',
             r'plant_edit\.py delline ("?[^"\s]+"?) (".*?"|\'.*?\')',
             r'plant_edit\.py truncate ("?[^"\s]+"?) (".*?"|\'.*?\')']
    for _m in re.finditer(r"perl -0pi -e 's\{(.+?)\}\{.*?\}' \"?([^\"\s]+)\"?", _wfsrc):
        _needle = _m.group(1).replace("\\$", "$").replace("\\\\", "\\")
        _raw = _m.group(2)
        if "$home" in _raw:
            # The file comes from a `for home in A \ B \ C` list above this line.
            # Read that list rather than skipping — skipping is how this exact plant
            # reached CI, and a guard that silently declines to look is the thing
            # every other guard here exists to prevent.
            _before = _wfsrc[:_m.start()]
            _loop = re.search(r"for home in \\\n((?:\s+\S+ \\\n)*\s+\S+)\n\s*do",
                              _before[_before.rfind("for home in"):] if "for home in" in _before else "")
            _homes = ([h.strip().rstrip(" \\") for h in _loop.group(1).split("\n")]
                      if _loop else [])
        else:
            _homes = [_raw]
        for _f in _homes:
            _f = _f.strip('"').strip()
            if not _f or "$" in _f:
                continue
            _full = os.path.join(ROOT, _f)
            if os.path.isfile(_full) and _needle not in open(_full, encoding="utf-8").read():
                fail(f"validate.yml: a `perl` negative self-test plants into {_f} by "
                     f"substituting {_needle!r}, which is no longer in that file — the "
                     "plant will not land and its guard is unproven.")
    for _pat in _pats:
        for _m in re.finditer(_pat, _wfsrc):
            _f = _m.group(1).strip('"').replace("$S", SKILL_DIR)
            _needle = _m.group(2)[1:-1]
            _full = os.path.join(ROOT, _f)
            if not os.path.isfile(_full):
                continue          # the tool's own usage example, not a plant
            if _needle not in open(_full, encoding="utf-8").read():
                fail(f"validate.yml: a negative self-test plants into {_f} by substituting "
                     f"{_needle!r}, which is no longer in that file — the plant will not "
                     "land, its check is unproven, and CI refuses AFTER the tag is public. "
                     "Match the fact with a regex rather than pinning it to a literal.")

# Section ids must be unique across the reference set. Two files defined D1, D2,
# E1 and E2 with different content, so "run D1" had two answers.
_sec_home: dict = {}
for _ref in sorted(REQUIRED_REFERENCES):
    _p = os.path.join(ROOT, SKILL_DIR, "references", _ref)
    if not os.path.isfile(_p):
        continue
    for _line in open(_p, encoding="utf-8"):
        _m = re.match(r"^#{2,4}\s+([A-Z]\d+[a-z]?)[.\s]", _line)
        if _m:
            _sec_home.setdefault(_m.group(1), set()).add(_ref)
for _sec, _homes in sorted(_sec_home.items()):
    if len(_homes) > 1:
        fail(f"section id {_sec} is defined in {sorted(_homes)} — a cross-reference that "
             f"names only the id resolves to two different sections")

# A backticked `references/<file>.md` in prose is a pointer the markdown link
# checker never sees, and one of them pointed at a file that exists and does not
# contain the claim. The file must at least resolve.
for _dirpath, _dirnames, _filenames in os.walk(os.path.join(ROOT, SKILL_DIR)):
    for _fn in sorted(f for f in _filenames if f.endswith(".md")):
        _fp = os.path.join(_dirpath, _fn)
        _rel = os.path.relpath(_fp, ROOT)
        for _target in set(re.findall(r"`(references/[a-z0-9-]+\.md)`",
                                      open(_fp, encoding="utf-8").read())):
            if not os.path.isfile(os.path.join(ROOT, SKILL_DIR, _target)):
                fail(f"{_rel}: backticked pointer `{_target}` resolves to no file")

# The tier vocabulary is a second fact with two homes: references/evidence-tiers.md
# defines it for the auditor, CONTRIBUTING.md repeats it for contributors. They had
# already drifted — FIELD read as "a single practitioner case" in one and "repeated
# practitioner reports" in the other, which are different admission bars wearing the
# same label. Compare the copies rather than trusting whoever edits next.
_TIERS = ("CONFIRMED", "STUDY", "FIELD", "HYPOTHESIS")


def _tier_definitions(path: str) -> dict:
    """Map tier name -> its definition cell, from a markdown table in `path`."""
    out = {}
    if not os.path.isfile(path):
        return out
    for line in open(path, encoding="utf-8"):
        if not line.lstrip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        name = cells[0].strip("*` ").upper()
        if name in _TIERS and cells[1]:
            # First occurrence wins: the definition table precedes any later
            # table that merely mentions a tier name in its first column.
            out.setdefault(name, " ".join(cells[1].replace("**", "").split()))
    return out


_tier_home = os.path.join(ROOT, SKILL_DIR, "references", "evidence-tiers.md")
_tier_copy = os.path.join(ROOT, "CONTRIBUTING.md")
_home_defs = _tier_definitions(_tier_home)
_copy_defs = _tier_definitions(_tier_copy)
for _t in _TIERS:
    if _t not in _home_defs:
        fail(f"evidence-tiers.md: no definition row for {_t} — it is the single home")
    elif _t not in _copy_defs:
        fail(f"CONTRIBUTING.md: no definition row for {_t}")
    elif _home_defs[_t] != _copy_defs[_t]:
        fail(f"tier {_t} differs between references/evidence-tiers.md and "
             f"CONTRIBUTING.md — one home, quoted verbatim "
             f"(home: {_home_defs[_t]!r}; copy: {_copy_defs[_t]!r})")

# The vocabulary has two further homes that cannot be verbatim copies: SKILL.md
# carries the confidence weights inline, and the Cursor rule carries a compressed
# gloss because a .mdc may not link out. Those cannot be string-compared, so check
# the two things that actually broke: the weights (exact) and the one word that
# separated the two FIELD definitions when they drifted (`single`). This is a
# narrow check by design — it does not prove the glosses are otherwise faithful.
_weights = {"CONFIRMED": "1.0", "STUDY": "0.7", "FIELD": "0.4", "HYPOTHESIS": "0.2"}
_skill_txt = open(os.path.join(ROOT, SKILL_DIR, "SKILL.md"), encoding="utf-8").read()
_home_txt = open(_tier_home, encoding="utf-8").read()
for _t, _w in _weights.items():
    if not re.search(rf"\|\s*\*\*{_t}\*\*\s*\|.*\|\s*{re.escape(_w)}\s*\|", _home_txt):
        fail(f"evidence-tiers.md: {_t} no longer carries rank {_w} — it is the "
             f"single home of the `uncertainty` axis's ordering")
    # SKILL.md no longer restates them, and that is the point. The weights existed
    # as the confidence MULTIPLIER of `priority = (impact × confidence) / effort`;
    # that product was removed on 2026-08-24 (four axes, no scalar) because it
    # destroyed the inputs its own argument needed. With `uncertainty` ranked
    # rather than multiplied, the numbers are an ORDERING and have one home. A
    # check requiring the reference's table to also appear in SKILL.md was
    # enforcing the two-homes defect this pack polices everywhere else.
for _f in mdcs:
    _mdc_txt = open(os.path.join(cursor_dir, _f), encoding="utf-8").read()
    _gloss = re.search(r"FIELD\s*\(([^)]*)\)", _mdc_txt)
    if not _gloss:
        fail(f"cursor/rules/{_f}: no FIELD gloss — the Cursor channel must carry "
             f"the tier vocabulary inline")
    elif "single" not in _gloss.group(1).lower():
        fail(f"cursor/rules/{_f}: FIELD glossed as {_gloss.group(1)!r} — the home "
             f"definition is a *single* practitioner case, and that is the exact "
             f"word these two copies drifted on before")

# templates/: skeletons must NOT be named SKILL.md (the skills CLI would ship them)
tpl_dir = os.path.join(ROOT, "templates")
if not os.path.isdir(tpl_dir):
    fail("missing templates/ directory")
else:
    # The skills CLI ships only the skill's own directory, so the deliverable
    # skeletons must also live inside it — and the two copies must not drift.
    embed_path = os.path.join(ROOT, SKILL_DIR, "references", "deliverable-templates.md")
    embedded = open(embed_path, encoding="utf-8").read() if os.path.isfile(embed_path) else ""
    for t in REQUIRED_TEMPLATES:
        tp = os.path.join(tpl_dir, t)
        if not os.path.isfile(tp):
            fail(f"missing template: templates/{t}")
            continue
        body = open(tp, encoding="utf-8").read().rstrip("\n")
        if embedded and body not in embedded:
            fail(f"templates/{t} has drifted from references/deliverable-templates.md "
                 f"(the copy the skills CLI ships) — regenerate the embedded copy")

# ── the report's coverage vocabulary ─────────────────────────────────────────
# M-40: *a report that says nothing about what was skipped cannot distinguish a
# clean result from a check that never looked.* Every instrument in this bundle
# could already tell those apart — `url_inspection.py` grants CONFIRMED only to
# the URLs the index answered for, `page_audit.py` drops absence findings on a
# truncated read, `gsc_pull.py` ships `row_limit_reached`, `preflight.py` keeps
# its own denominator fixed — and none of it reached the markdown a client reads.
# The skeleton offered a `Status` column with no vocabulary and a free-text
# "Not checked" table, and nothing read either.
#
# Four things are checked here, and each one is a way the fix could ship and still
# not work:
#
#   1. the enum is CLOSED and lives in one place (`preflight.COVERAGE_STATUS`),
#      and the skeleton publishes exactly those values. The family has shipped the
#      other shape: a contract listing five statuses against a linter matching
#      four, where an out-of-enum value read as *no status at all*;
#   2. the denominator is the track list SKILL.md step 2 declares — it declared
#      eleven and the skeleton carried ten rows, so track K's coverage was
#      unstatable;
#   3. the skeleton satisfies the same checker a filled-in report does, so the
#      document an auditor starts from is a valid document;
#   4. every gate `preflight.py` actually emits is a gate a `blocked-by` row may
#      name. Parsed out of the `probe(...)` calls with `ast`, not grepped, because
#      the drift this prevents is a gate string added in one place and not the
#      other.
_pre_path = os.path.join(ROOT, SKILL_DIR, "scripts", "preflight.py")
_pre = None
if os.path.isfile(_pre_path):
    try:
        # Imported rather than parsed, so the enum and the track list have exactly one
        # home and this guard cannot fall behind them. `dont_write_bytecode` is not
        # hygiene: without it the first run of this guard left a `__pycache__` inside
        # `plugins/`, which both installers copy verbatim and npm ships — the artifact
        # guard forty lines up caught it on the spot.
        _no_pyc = sys.dont_write_bytecode
        sys.dont_write_bytecode = True
        try:
            _spec = importlib.util.spec_from_file_location("_preflight_for_validate", _pre_path)
            _pre = importlib.util.module_from_spec(_spec)
            _spec.loader.exec_module(_pre)
        finally:
            # `finally`, because the plant that breaks this import is exactly the run
            # where the flag would otherwise stay set for the rest of the validator.
            sys.dont_write_bytecode = _no_pyc
    except Exception as _e:  # noqa: BLE001 - a module that will not load is a failure
        fail(f"{SKILL_DIR}/scripts/preflight.py does not import: {_e}")
        _pre = None
if _pre is not None and not callable(getattr(_pre, "validate_coverage", None)):
    fail("preflight.py exposes no validate_coverage() — the coverage table would have "
         "no reader, which is the state this guard exists to leave behind")
    _pre = None

if _pre is not None:
    _tracks = getattr(_pre, "TRACKS", None)
    _status = getattr(_pre, "COVERAGE_STATUS", None)
    if not isinstance(_tracks, tuple) or not _tracks:
        fail("preflight.py declares no TRACKS — the coverage table's denominator has no home")
    elif not isinstance(_status, tuple) or not _status:
        fail("preflight.py declares no COVERAGE_STATUS — the coverage vocabulary has no home")
    else:
        # 2. the denominator, against SKILL.md step 2
        _skill_txt = open(os.path.join(ROOT, SKILL_DIR, "SKILL.md"), encoding="utf-8").read()
        _step2 = re.search(r"^\| # \| Track \| Answers \| Reference \|\n(.*?)(?=\n\n)",
                           _skill_txt, re.M | re.S)
        if not _step2:
            fail("SKILL.md: no step-2 track table with the header "
                 "'| # | Track | Answers | Reference |' — the coverage denominator is "
                 "read from it")
        else:
            _skill_tracks = re.findall(r"^\| ([A-Z]) \| ([^|]+?) *\|", _step2.group(1), re.M)
            _declared = [t[0] for t in _tracks]
            if [t[0] for t in _skill_tracks] != _declared:
                fail(f"SKILL.md step 2 declares tracks {[t[0] for t in _skill_tracks]} and "
                     f"preflight.py TRACKS declares {_declared} — the coverage table's "
                     f"denominator is read from TRACKS, so the two must agree")
            else:
                _srcs = getattr(_pre, "TRACK_SOURCES", {})
                _no_entry = [t for t, _ in _tracks if t not in _srcs]
                if _no_entry:
                    fail(f"preflight.py: track(s) {_no_entry} have no TRACK_SOURCES entry, so "
                         f"they can never be seeded `blocked-by` — a missing key reads exactly "
                         f"like a track nothing refused. Declare an empty tuple where no probe "
                         f"can speak for it, as track G does")
                for (_tid, _sk_label), (_, _pf_label) in zip(_skill_tracks, _tracks):
                    _first = re.sub(r"[^\w]", "", _sk_label.split()[0]).lower()
                    if _first and _first not in _pf_label.lower():
                        fail(f"track {_tid}: SKILL.md calls it {_sk_label.strip()!r} and "
                             f"preflight.py calls it {_pf_label!r} — a reader matching the "
                             f"coverage row to the track cannot")

        # 1 + 3. both homes of the skeleton, against the checker itself
        _cov_homes = ("templates/audit-report.template.md",
                      f"{SKILL_DIR}/references/deliverable-templates.md")
        _range = f"{{{{{_tracks[0][0]}–{_tracks[-1][0]}}}}}"
        for _rel in _cov_homes:
            _p = os.path.join(ROOT, _rel)
            if not os.path.isfile(_p):
                continue
            _txt = open(_p, encoding="utf-8").read()
            for _err in _pre.validate_coverage(_txt):
                fail(f"{_rel}: {_err}")
            for _s in _status:
                if f"`{_s}`" not in _txt:
                    fail(f"{_rel}: the coverage vocabulary does not publish `{_s}` — the enum "
                         f"lives in preflight.py:COVERAGE_STATUS and every value has to be "
                         f"readable where the table is edited")
            # A findings block that cannot name the last track is the same
            # denominator bug one section up: it said {{A–J}} while step 2
            # declared K.
            if _range not in _txt:
                fail(f"{_rel}: the findings block does not offer the track range {_range} — "
                     f"a finding on the last declared track cannot be labelled")

    # 4. every gate a probe emits is a gate a coverage row may name


    def _gate_literals(_node):
        """The strings an expression can EVALUATE to, ignoring the tests along the way.

        A conditional's test strings are not gates: `check_gsc` classifies on
        "quota project", "serviceusage", "insufficient" and "disabled" and evaluates
        to `quota-project`, `scope`, `api-not-enabled` or `permission`. Collecting
        every constant in the expression would demand the test strings be declared
        too; collecting only the top level would miss all four, because that gate is
        assigned to a variable before it reaches `probe()`.

        Watched under-reporting before this existed: removing `api-not-enabled` from
        COVERAGE_GATES left the validator green while the probe still emitted it, so
        a `blocked-by api-not-enabled` row would have been refused as an unknown
        gate. That is the same guard-written-against-one-home shape the 2026-08-10
        audit named, one call indirection later.
        """
        if isinstance(_node, ast.Constant):
            return {_node.value} if isinstance(_node.value, str) else set()
        if isinstance(_node, ast.IfExp):
            return _gate_literals(_node.body) | _gate_literals(_node.orelse)
        return set()

    _gates_declared = set(getattr(_pre, "COVERAGE_GATES", ()))
    _emitted = set()
    for _node in ast.walk(ast.parse(open(_pre_path, encoding="utf-8").read())):
        if isinstance(_node, ast.Call) and isinstance(_node.func, ast.Name) \
                and _node.func.id == "probe":
            _g = _node.args[3] if len(_node.args) > 3 else None
            for _kw in _node.keywords:
                if _kw.arg == "gate":
                    _g = _kw.value
            _emitted |= _gate_literals(_g)
        # The indirect form: `gate = <conditional>` then `probe(..., gate, ...)`.
        elif isinstance(_node, ast.Assign) and any(
                isinstance(_t, ast.Name) and _t.id == "gate" for _t in _node.targets):
            _emitted |= _gate_literals(_node.value)
    # An empty string is never a gate: `validate_coverage` already refuses a bare
    # `blocked-by`, and a rendering local that evaluates to "" is not a claim about
    # the vocabulary.
    _undeclared = sorted(_emitted - _gates_declared - {""})
    if _undeclared:
        fail(f"preflight.py emits gate(s) {_undeclared} that COVERAGE_GATES does not declare — "
             f"a `blocked-by <gate>` row naming one would be refused by validate_coverage, "
             f"which is the enum drift the closed vocabulary exists to prevent")
    if not set(getattr(_pre, "NO_REASON_NEEDED", ())) <= {s.split(" ", 1)[0] for s in (_status or ())}:
        fail("preflight.py: NO_REASON_NEEDED names a status outside COVERAGE_STATUS")

# ── every payload names the execution that produced it ───────────────────────
# M-32: *when an agent produces the change, the proof should identify the execution
# that produced it.* M-08: every proof is **scoped, versioned and perishable**.
#
# Nothing here emitted any of it — `grep -n "__version__\|observed_at\|timestamp"
# scripts/*.py` returned nothing — so a deliverable could not say when it was
# produced, by what version, or against what arguments. An SEO audit is the most
# perishable evidence this family makes, and a three-month-old one was
# indistinguishable from today's.
#
# Five things are checked, and each is a way the fix could ship and not work:
#
#   1. the field set is CLOSED and lives in one place (`preflight.PRODUCER_FIELDS`),
#      the same shape SE-01 gave the coverage vocabulary;
#   2. the emitter is byte-identical in all seven scripts. It is a copy rather than
#      an import because these ship standalone — `bin/seo-aeo-audit.js` copies
#      `scripts/` alone into `~/.claude/skills/`, so there is nothing to import from
#      — and a copy nobody compares is seven versions of one function;
#   3. every script CALLS it, naming itself. A shared block nobody invokes is dead
#      code that passes every structural check;
#   4. `SKILL_VERSION` agrees with the manifests. It is the one field that says which
#      doctrine produced a finding, and a stale literal is worse than none: it names
#      a version that never ran;
#   5. both report skeletons publish every field, every invalidator and the command
#      that seeds the block. A field a human types after the run is the automation
#      debt the manifesto names at :283.
_SCRIPTS_DIR = os.path.join(ROOT, SKILL_DIR, "scripts")
_ALL_SCRIPTS = sorted(f for f in os.listdir(_SCRIPTS_DIR) if f.endswith(".py")) \
    if os.path.isdir(_SCRIPTS_DIR) else []
_PROV_RE = re.compile(
    r"# ── provenance: the execution that produced this payload ── shared block ─+\n"
    r".*?# ── end provenance shared block ─+\n", re.S)

_prov_blocks = {}
for _s in _ALL_SCRIPTS:
    _src = open(os.path.join(_SCRIPTS_DIR, _s), encoding="utf-8").read()
    _m = _PROV_RE.search(_src)
    if not _m:
        fail(f"{_s} carries no provenance shared block — its `--format json` payload "
             f"cannot say which execution produced it, and a finding taken from it "
             f"reaches a ticket with no way back to the run (M-32)")
        continue
    _prov_blocks[_s] = _m.group(0)
    # 3. the block is called, and it names this script rather than a sibling's file.
    if not re.search(rf'provenance\(\s*"{re.escape(_s)}"', _src):
        fail(f"{_s} never calls provenance(\"{_s}\", …) — either the block is dead code "
             f"or the payload is stamped with another script's name, which is worse than "
             f"an unstamped one")

if len(set(_prov_blocks.values())) > 1:
    # Named as a diff against the alphabetically-first copy, because "seven copies
    # disagree" sends nobody anywhere.
    _ref = _prov_blocks[sorted(_prov_blocks)[0]]
    _drifted = sorted(k for k, v in _prov_blocks.items() if v != _ref)
    fail(f"the provenance shared block differs in {_drifted} from {sorted(_prov_blocks)[0]} "
         f"— it is copied rather than imported because these ship standalone, so the only "
         f"thing holding the seven together is this comparison")

if _pre is not None:
    _fields = getattr(_pre, "PRODUCER_FIELDS", None)
    _penv = getattr(_pre, "PRODUCER_ENV", None)
    _inval = getattr(_pre, "INVALIDATORS", None)
    if not isinstance(_fields, tuple) or not _fields:
        fail("preflight.py declares no PRODUCER_FIELDS — the producer block's field set "
             "has no home, so nothing can say a payload is missing one")
    elif not callable(getattr(_pre, "validate_provenance", None)):
        fail("preflight.py exposes no validate_provenance() — the provenance block would "
             "have no reader, which is the state SE-01 left the coverage table's checker "
             "behind to avoid")
    elif not isinstance(_inval, tuple) or len(_inval) < 2:
        fail("preflight.py declares no INVALIDATORS — a proof with no stated expiry reads "
             "as permanent, and that is the half of M-08 that matters most for a crawl "
             "result")
    else:
        # 1. `observed_at` is the field the whole thing turns on: it is what makes the
        #    proof perishable rather than merely stamped.
        for _need in ("skill", "script", "observed_at", "args", "scope"):
            if _need not in _fields:
                fail(f"preflight.py: PRODUCER_FIELDS has no {_need!r} — without it a payload "
                     f"cannot answer "
                     f"{'when it was taken' if _need == 'observed_at' else 'what it is about'}")
        # 2b. every harness-owned field is IN the field set and reports itself by name.
        for _n, _var, _ in (_penv or ()):
            if _n not in _fields:
                fail(f"preflight.py: PRODUCER_ENV names {_n!r}, which is not in "
                     f"PRODUCER_FIELDS — a field the renderer never prints")
            if not _var.startswith("SEO_AEO_AUDIT_"):
                fail(f"preflight.py: PRODUCER_ENV reads {_var!r} — a producer field is fed "
                     f"from this skill's own namespace, never from a variable another tool "
                     f"may set to something about itself")

        # 4. the version literal against the manifests. Seven more homes for one
        #    semver, and they are literals rather than a runtime lookup because the
        #    installed layout carries no manifest to look in.
        for _s, _blk in _prov_blocks.items():
            _vm = re.search(r'^SKILL_VERSION = "([^"]+)"$', _blk, re.M)
            if not _vm:
                fail(f"{_s}: the provenance block declares no SKILL_VERSION")
            elif plg_ver and _vm.group(1) != plg_ver:
                fail(f"{_s}: SKILL_VERSION is {_vm.group(1)!r}, the manifests say "
                     f"{plg_ver!r} — a producer block naming a version that never ran is "
                     f"worse than one naming none. Bump all {len(_ALL_SCRIPTS)} scripts in "
                     f"the same commit as the manifests")

        # 5. both skeletons, against the checker a filled-in report faces
        for _rel in ("templates/audit-report.template.md",
                     f"{SKILL_DIR}/references/deliverable-templates.md"):
            _p = os.path.join(ROOT, _rel)
            if not os.path.isfile(_p):
                continue
            _txt = open(_p, encoding="utf-8").read()
            for _err in _pre.validate_provenance(_txt):
                fail(f"{_rel}: {_err}")

# ── the I/O surface this file publishes is counted, not restated ──────────────
# B-25 (this comment said B-17 until 2026-08-20, which is an open row about something
# else): `SECURITY.md` said **six** scripts and that its I/O grep "prints **22** lines
# and that is all of it", against a measured seven and 26, for four releases. Those
# numbers are the whole point of that section — a reader consults it *because* they
# will not read the code — and it is the same prose-count class already reconciled
# above for the myth, play, Prowl and reference counts.
#
# The regex is read OUT OF the document and run, rather than copied here: a guard
# with its own copy of the pattern proves that its copy agrees with its own count.
_sec_path = os.path.join(ROOT, "SECURITY.md")
if os.path.isfile(_sec_path) and _ALL_SCRIPTS:
    _sec = open(_sec_path, encoding="utf-8").read()
    _WORDS_UP = {n: NUMWORDS[n] for n in range(6, 13)}
    _n_scripts = len(_ALL_SCRIPTS)
    _word = _WORDS_UP.get(_n_scripts, str(_n_scripts))
    for _pat, _what in (
        (r"documentation plus \*\*(\S+?)\*\* small Python scripts", "the headline"),
        (r"`scripts/\*\.py` — (\S+) of them", "the component table"),
        (r"reproduces this\ntable for all (\S+)", "the measurement note"),
        (r"anywhere in the (\S+) —", "the no-eval sentence"),
        (r"I/O surface of all (\S+) scripts", "the verification command"),
    ):
        _m = re.search(_pat, _sec)
        if not _m:
            fail(f"SECURITY.md: {_what} no longer states the script count in a form this "
                 f"check can read (expected /{_pat}/) — the number goes stale silently the "
                 f"moment nothing reads it, which is exactly how B-25 happened")
        elif _m.group(1).strip(".,") not in (_word, str(_n_scripts)):
            fail(f"SECURITY.md: {_what} says {_m.group(1)!r} scripts, the directory holds "
                 f"{_n_scripts} ({_word})")
    # every script has a row in the per-script I/O table
    for _s in _ALL_SCRIPTS:
        if f"| `{_s}` |" not in _sec:
            fail(f"SECURITY.md: no row for `{_s}` in the per-script I/O table — a script "
                 f"absent from the table a reader trusts is an undisclosed surface")
    # the documented grep, run
    # The same class one document over: SKILL.md enumerates the bundled scripts by
    # name, and named `sitemap_pull.py` — a file that has never existed — in the one
    # paragraph an agent reads to learn what it can run. A count word beside a list of
    # names is two claims, so both are measured.
    _skill_txt2 = open(os.path.join(ROOT, SKILL_DIR, "SKILL.md"), encoding="utf-8").read()
    _inv = re.search(r"\*\*(\w+) scripts ship with the skill\*\*(.*?)\. ", _skill_txt2, re.S)
    if not _inv:
        fail("SKILL.md: no '**<N> scripts ship with the skill**' sentence — the script "
             "inventory an agent reads to learn what it can run is unchecked")
    else:
        _claim = {"six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}.get(
            _inv.group(1).lower())
        if _claim != _n_scripts:
            fail(f"SKILL.md says {_inv.group(1)!r} scripts ship, the directory holds "
                 f"{_n_scripts}")
        _named = set(re.findall(r"`([a-z_0-9]+\.py)`", _inv.group(2)))
        for _bad in sorted(_named - set(_ALL_SCRIPTS)):
            fail(f"SKILL.md names `{_bad}` among the bundled scripts and no such file "
                 f"ships — an agent told to run it gets a missing-file error, which is "
                 f"CLAUDE.md rule 3: a pointer that resolves is not the same as one that "
                 f"answers")
        for _missing in sorted(set(_ALL_SCRIPTS) - _named):
            fail(f"SKILL.md's script inventory does not name `{_missing}`, which ships — "
                 f"an instrument nobody is told about is an instrument nobody uses")

    _gm = re.search(r'grep -rnE "([^"]+)"', _sec)
    if not _gm:
        fail("SECURITY.md: the I/O verification command no longer carries a "
             "`grep -rnE \"…\"` pattern this check can run")
    else:
        try:
            _io_re = re.compile(_gm.group(1))
        except re.error as _e:
            _io_re = None
            fail(f"SECURITY.md: the published I/O regex does not compile in python "
                 f"({_e}) — a reader is being handed a command that cannot run")
        if _io_re is not None:
            _io_lines = sum(
                1 for _s in _ALL_SCRIPTS
                for _l in open(os.path.join(_SCRIPTS_DIR, _s), encoding="utf-8")
                if _io_re.search(_l))
            _cm = re.search(r"prints \*\*(\d+) lines and that is all of it\*\*", _sec)
            if not _cm:
                fail("SECURITY.md: the I/O line count is no longer stated as "
                     "'prints **N** lines and that is all of it' — nothing can compare it")
            elif int(_cm.group(1)) != _io_lines:
                fail(f"SECURITY.md says the I/O grep prints {_cm.group(1)} lines; running "
                     f"the pattern it publishes over scripts/ gives {_io_lines}. That "
                     f"sentence claims to be the WHOLE surface, so a low number reads as "
                     f"an audited bundle and is not one")


# ── the script count in the two documents a reader meets FIRST ───────────────
# B-25 measured `SECURITY.md` and `SKILL.md` and stopped there. On 2026-08-20 the
# README's security posture (`Text plus **six** …`) and `CLAUDE.md`'s opening
# sentence (`knowledge plus six standard-library scripts`) still said six, and the
# README's own enumeration accounted for six of the seven by role — `agent_surface.py`,
# the track-K collector, was in neither. Two more homes of the fact B-25 was filed
# against, in the two files a reader opens before either of the documents it fixed.
#
# The README also NAMES them, and a count word beside a list of names is two claims,
# so both are measured — the same shape the SKILL.md inventory check above uses.
if _ALL_SCRIPTS:
    _n_all = len(_ALL_SCRIPTS)
    for _rel, _pat, _what in (
        ("README.md", r"Text plus \*\*(\w+)\*\* standard-library Python scripts",
         "the security-posture sentence"),
        ("CLAUDE.md", r"knowledge plus (\w+) standard-library scripts",
         "the opening description"),
    ):
        _p = os.path.join(ROOT, _rel)
        if not os.path.isfile(_p):
            fail(f"{_rel} is named as a home of the script count and does not exist")
            continue
        _txt = open(_p, encoding="utf-8").read()
        _m = re.search(_pat, _txt)
        if not _m:
            fail(f"{_rel}: {_what} no longer states the bundled-script count in a form "
                 f"this check can read (expected /{_pat}/) — the number goes stale "
                 f"silently the moment nothing reads it, which is how B-25 happened")
        elif numword(_m.group(1)) != _n_all:
            fail(f"{_rel}: {_what} says {_m.group(1)!r} scripts, the directory holds "
                 f"{_n_all} ({NUMWORDS[_n_all]}) — {', '.join(_ALL_SCRIPTS)}")
    # The README's enumeration by role, read to the end of its paragraph.
    _rm = open(os.path.join(ROOT, "README.md"), encoding="utf-8").read()
    _para = re.search(r"Text plus \*\*\w+\*\* standard-library Python scripts.*?\n\n",
                      _rm, re.S)
    if not _para:
        fail("README.md: the security-posture paragraph that enumerates the scripts by "
             "role is unreadable — it is the only place a reader learns which script "
             "does what before opening SECURITY.md")
    else:
        _named = set(re.findall(r"`([a-z_0-9]+\.py)`", _para.group(0)))
        for _bad in sorted(_named - set(_ALL_SCRIPTS)):
            fail(f"README.md's security posture names `{_bad}` among the bundled scripts "
                 f"and no such file ships")
        for _missing in sorted(set(_ALL_SCRIPTS) - _named):
            fail(f"README.md's security posture does not name `{_missing}`, which ships — "
                 f"a script absent from the paragraph that divides them by role is an "
                 f"undisclosed surface in the document a reader meets first")


# HARD RULE: a SKILL.md may exist ONLY inside plugins/<plugin>/skills/<skill>/.
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules")]
    if "SKILL.md" not in filenames:
        continue
    rel = os.path.relpath(os.path.join(dirpath, "SKILL.md"), ROOT)
    if not re.match(r"^plugins/[^/]+/skills/[^/]+/SKILL\.md$", rel):
        fail(f"stray SKILL.md at {rel} — the skills CLI would ship it as a skill; "
             f"rename it (e.g. SKILL.template.md) or move it under plugins/<p>/skills/<s>/")

# required root files
for r in ("README.md", "LICENSE", "install.sh"):
    if not os.path.isfile(os.path.join(ROOT, r)):
        fail(f"missing root file: {r}")

# every relative markdown link in repo docs must resolve — file *and* anchor
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules")]
    for fn in filenames:
        if not fn.endswith(".md"):
            continue
        fp = os.path.join(dirpath, fn)
        rel = os.path.relpath(fp, ROOT)
        for target in LINK_RE.findall(open(fp, encoding="utf-8").read()):
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            if "{{" in target:  # template placeholder
                continue
            path_part, _, anchor = target.partition("#")
            tpath = fp if not path_part else os.path.normpath(os.path.join(dirpath, path_part))
            if not os.path.exists(tpath):
                fail(f"broken relative link in {rel}: {target}")
                continue
            if anchor and tpath.endswith(".md") and anchor not in heading_slugs(tpath):
                fail(f"broken anchor in {rel}: {target} — no heading with that slug")


# --------------------------------------------------------------------------- evidence guards
# Everything below reconciles a number or a pointer that one of this repository's own
# evidence documents STATES against the thing it is about. Each family was measured
# wrong on this tree on 2026-08-20 before its guard existed; each has a planted-defect
# step in CI. The pattern is the one CLAUDE.md rule 1 names: count the homes first.

# ── `_flat()` is copied, so the copies are counted ────────────────────────────
# DOCMAP called it "one copy per script, five in all" — two claims in one breath,
# and the per-script half was false: seven scripts ship and five define one.
# `preflight.py` says the true version out loud in a comment above the shared
# provenance block ("only five of the seven scripts define one"), which is a fact with
# two homes and no reconciler, so the document drifted and the code did not.
_flat_homes = [_s for _s in _ALL_SCRIPTS
               if "def _flat(" in open(os.path.join(_SCRIPTS_DIR, _s), encoding="utf-8").read()]
_DOCMAP = os.path.join(ROOT, "docs", "DOCMAP.md")
if _ALL_SCRIPTS and os.path.isfile(_DOCMAP):
    _dm_txt = open(_DOCMAP, encoding="utf-8").read()
    _m = re.search(r"`_flat\(\)` — (\w+) of the (\w+) scripts define one", _dm_txt)
    if not _m:
        fail("docs/DOCMAP.md: the `_flat()` row no longer states its copy count as "
             "'<N> of the <M> scripts define one' — it used to say 'one copy per script, "
             "five in all' against seven scripts, and nothing could read either number")
    else:
        _claim = (numword(_m.group(1)), numword(_m.group(2)))
        if _claim != (len(_flat_homes), len(_ALL_SCRIPTS)):
            fail(f"docs/DOCMAP.md: the `_flat()` row says {_m.group(1)!r} of "
                 f"{_m.group(2)!r} scripts define one; measured "
                 f"{len(_flat_homes)} of {len(_ALL_SCRIPTS)} — "
                 f"{', '.join(_flat_homes)}")

# ── the reference corpus: its freshness stamp and its size, both measured ────
# README's "Data freshness" bullet said **Verified as of 2026-08-10** while
# `algorithm-updates.md` — the single home of that fact per the row above — said the
# sources were last re-fetched 2026-08-16. A staleness claim that is itself stale is
# the one number in this repository a reader uses to decide whether to trust the rest.
#
# The size is rounded ON PURPOSE, to the nearest hundred, and the rounding is what the
# README states. An exact line count sat there once and was wrong four edits later;
# a figure nothing recomputes is the defect, and a figure that moves on every comma
# is the reason the last one was deleted instead of fixed.
_ALG = os.path.join(ROOT, SKILL_DIR, "references", "algorithm-updates.md")
_README = os.path.join(ROOT, "README.md")
if os.path.isfile(_ALG) and os.path.isfile(_README):
    _alg_txt = open(_ALG, encoding="utf-8").read()
    _rm_txt = open(_README, encoding="utf-8").read()
    _am = re.search(r"\*\*Sources last re-fetched:\s*(\d{4}-\d{2}-\d{2})", _alg_txt)
    _rmm = re.search(r"\*\*Sources last re-fetched (\d{4}-\d{2}-\d{2})\*\*", _rm_txt)
    if not _am:
        fail("references/algorithm-updates.md: no `**Sources last re-fetched: YYYY-MM-DD`"
             " line — it is the single home of the corpus freshness date")
    elif not _rmm:
        fail("README.md: the Data-freshness bullet no longer carries "
             "`**Sources last re-fetched YYYY-MM-DD**` — it used to say "
             "'Verified as of 2026-08-10' with nothing comparing it to the reference "
             "that owns the date, and it was six days stale")
    elif _am.group(1) != _rmm.group(1):
        fail(f"README.md says the sources were last re-fetched {_rmm.group(1)}; "
             f"references/algorithm-updates.md — the single home of that fact — says "
             f"{_am.group(1)}. A freshness claim that is itself stale is the number a "
             f"reader uses to decide whether to trust the corpus")
    if os.path.isdir(_ref_dir):
        _corpus_nonblank = sum(
            1 for _f in sorted(os.listdir(_ref_dir)) if _f.endswith(".md")
            for _l in open(os.path.join(_ref_dir, _f), encoding="utf-8") if _l.strip())
        _rounded = round(_corpus_nonblank / 100) * 100
        _sm = re.search(r"\*\*~([\d,]+) non-blank lines\*\*", _rm_txt)
        if not _sm:
            fail("README.md: the Data-freshness bullet no longer states the corpus size "
                 "as `**~N non-blank lines**` — it said 'Roughly 5,000 lines' against a "
                 f"measured {_corpus_nonblank}")
        elif numword(_sm.group(1)) != _rounded:
            fail(f"README.md says ~{_sm.group(1)} non-blank lines of reference material; "
                 f"`references/*.md` holds {_corpus_nonblank}, which rounds to "
                 f"{_rounded}. The README states the rounding, so this is the figure "
                 f"it claims and not an approximation of a different one")

# ── SKILL.md's body budget is measured HERE, not in another repository ────────
# Three evidence rows and a board row rested on `audit_skill.py --house`, which is
# `make-skill`'s script and does not exist in this tree: a reader handed that command
# gets `No such file or directory`, and the four numbers it produced were unreproducible
# from this repository. The estimator is `len(body) / 3.9` — the same one that script
# uses — so it is vendored rather than cited, and the gate prints the measurement on
# every run.
#
# The HARD limits fail; the house limit only reports. The body is over the house limit
# today (that is board row B-27) and a gate that goes red on a known, filed, deliberate
# state teaches everyone to ignore it.
_BODY_MAX_TOKENS, _BODY_HOUSE_TOKENS, _BODY_MAX_LINES, _CHARS_PER_TOKEN = 5000, 4750, 500, 3.9
_body_tokens = _body_lines = None
if os.path.isfile(skill_path):
    _sm_txt = open(skill_path, encoding="utf-8").read()
    _fmm = re.match(r"^---\n.*?\n---\n", _sm_txt, re.S)
    if _fmm:
        _body = _sm_txt[_fmm.end():]
        _body_tokens = int(len(_body) / _CHARS_PER_TOKEN)
        _body_lines = _body.count("\n") + 1
        if _body_tokens >= _BODY_MAX_TOKENS:
            fail(f"SKILL.md body is ~{_body_tokens} tokens ({len(_body)} chars / "
                 f"{_CHARS_PER_TOKEN}), the budget is < {_BODY_MAX_TOKENS} — move detail "
                 f"into references/. The answer at this ceiling is a split, not a trim "
                 f"(B-27)")
        if _body_lines >= _BODY_MAX_LINES:
            fail(f"SKILL.md body is {_body_lines} lines, the budget is < {_BODY_MAX_LINES}")

# ── a `B-nn` the prose calls closed must read closed on the board ─────────────
# `SECURITY.md` credited its own repair to "(B-17, closed 2026-08-19)". B-17 is open
# and is about comparing a number on a third-party manifest against the same number on
# the site; the row that closed the I/O count is B-25, which `CONTRIBUTING.md:109`
# cites correctly. Three of this repository's own guard comments carried the same wrong
# id. A pointer that resolves is not a pointer that answers (CLAUDE.md rule 3), and a
# closed-row credit is the citation a reader follows to learn what was actually fixed.
_BOARD = os.path.join(ROOT, "docs", "evidence", "backlog.md")
_board_status = {}
if os.path.isfile(_BOARD):
    for _line in open(_BOARD, encoding="utf-8"):
        _bm = re.match(r"\|\s*(B-\d+)\s*\|", _line)
        if _bm:
            _cells = [_c.strip() for _c in _line.strip().strip("|").split("|")]
            _board_status[_bm.group(1)] = _cells[-1].lower()
    if not _board_status:
        fail("docs/evidence/backlog.md: no `| B-nn |` rows found — the board is the "
             "single home of every row's status and nothing else can be checked against it")
    # A quotation is not an exemption: a document that reproduces "(B-17, closed …)"
    # reads as that claim to every checker and most readers, so a correction records
    # the wrong id WITHOUT reassembling the sentence — the same rule this family
    # applies to a dead command, which may be named and never quoted as runnable.
    _CLOSED_CLAIMS = (r"(B-\d+),\s*closed\b", r"\bclosed by (B-\d+)\b", r"(B-\d+)\s*\(closed")
    for _rel in ("README.md", "SECURITY.md", "CONTRIBUTING.md", "CLAUDE.md",
                 os.path.join("docs", "DOCMAP.md"),
                 os.path.join("docs", "evidence", "verification.md"),
                 os.path.join("docs", "evidence", "retro.md"),
                 os.path.join("docs", "evidence", "backlog.md")):
        _p = os.path.join(ROOT, _rel)
        if not os.path.isfile(_p):
            continue
        _txt = open(_p, encoding="utf-8").read()
        for _bid in sorted(set(re.findall(r"\b(B-\d+)\b", _txt))):
            if _bid not in _board_status:
                fail(f"{_rel} cites {_bid} and the board has no such row — a board id is "
                     f"the pointer a reader follows to learn why something was done")
        for _pat in _CLOSED_CLAIMS:
            for _bid in sorted(set(re.findall(_pat, _txt))):
                _st = _board_status.get(_bid)
                if _st is not None and "done" not in _st:
                    fail(f"{_rel} calls {_bid} closed; the board reads {_st!r}. The row "
                         f"that closed the work is a different one, and crediting the "
                         f"wrong id sends a reader to an open item for the explanation")

# ── the verification ledger covers every release it says it covers ────────────
# Two sections headed `## Unreleased` and `## 2026-08-19` opened "**Not shipped.**" for
# work that is in v0.23.0, tagged on HEAD, and there was no `v0.23.0` section at all:
# the ledger was frozen in the working-tree state it was written in and the release went
# past it. Its own closing policy — read out of the file rather than copied here — says
# every release from a stated floor forward gets a row.
#
# The newest release must have a section, full stop; the historical gap is DECLARED and
# counted instead of silent, because backfilling sixteen sections from the changelog is
# exactly what that closing paragraph refuses ("a ledger filled in from memory is the
# thing it exists to replace").
_LEDGER = os.path.join(ROOT, "docs", "evidence", "verification.md")
_CHANGELOG = os.path.join(ROOT, "CHANGELOG.md")
if os.path.isfile(_LEDGER) and os.path.isfile(_CHANGELOG):
    _led = open(_LEDGER, encoding="utf-8").read()
    _chg = open(_CHANGELOG, encoding="utf-8").read()
    _fm = re.search(r"Releases from v(\d+\.\d+\.\d+) forward get a row each", _led)
    if not _fm:
        fail("docs/evidence/verification.md: no 'Releases from vX.Y.Z forward get a row "
             "each' sentence — that sentence is the floor this check reads, and without "
             "it the ledger's coverage is whatever it happens to be")
    else:
        _floor = semver(_fm.group(1))
        _releases = [_v for _v in re.findall(r"^## v(\d+\.\d+\.\d+)\b", _chg, re.M)
                     if semver(_v) >= _floor]
        _recorded = set(re.findall(r"^## v(\d+\.\d+\.\d+)\b", _led, re.M))
        if not _releases:
            fail(f"CHANGELOG.md has no `## vX.Y.Z` heading at or above v{_fm.group(1)}")
        else:
            _newest = max(_releases, key=semver)
            if _newest not in _recorded:
                fail(f"docs/evidence/verification.md has no `## v{_newest}` section, and "
                     f"that is CHANGELOG.md's newest release — a release with no ledger "
                     f"section is a release nobody has said was confirmed. Two sections "
                     f"headed `## Unreleased` and a date said '**Not shipped**' about "
                     f"work that had shipped, for exactly this reason")
            _gap = sorted((_v for _v in _releases if _v not in _recorded), key=semver)
            _dec = re.search(r"<!-- unrecorded-releases:start -->(.*?)"
                             r"<!-- unrecorded-releases:end -->", _led, re.S)
            if not _dec:
                fail("docs/evidence/verification.md: no `<!-- unrecorded-releases:start -->"
                     "` block — the releases with no section here are declared and counted, "
                     "or they are silently absent, which is the state this guard was "
                     "written against")
            else:
                _declared = sorted(set(re.findall(r"^- `?v(\d+\.\d+\.\d+)`?", _dec.group(1),
                                                  re.M)), key=semver)
                if _declared != _gap:
                    _extra = sorted(set(_declared) - set(_gap), key=semver)
                    _short = sorted(set(_gap) - set(_declared), key=semver)
                    fail(f"docs/evidence/verification.md: the declared unrecorded-release "
                         f"list disagrees with CHANGELOG.md — not declared: "
                         f"{['v' + _v for _v in _short]}; declared but recorded above: "
                         f"{['v' + _v for _v in _extra]}")
                _cm = re.search(r"\*\*(\w+(?:-\w+)?)\*\* of the (\w+(?:-\w+)?) releases "
                                r"at or above", _led)
                if not _cm:
                    fail("docs/evidence/verification.md: the unrecorded-release block no "
                         "longer states its size as '**N** of the M releases at or above' "
                         "— a list nothing counts is a list that grows quietly")
                elif (numword(_cm.group(1)), numword(_cm.group(2))) != (len(_gap),
                                                                       len(_releases)):
                    fail(f"docs/evidence/verification.md says {_cm.group(1)!r} of "
                         f"{_cm.group(2)!r} releases are unrecorded; measured "
                         f"{len(_gap)} of {len(_releases)}")

    # ── each section's stated tally is parsed out of its own rows ─────────────
    # The v0.13.0 section said "5 observed · 6 test-only · 5 planted+observed · 6 never"
    # — twenty-two against twenty-one rows, four planted+observed, five never, and one
    # `planted` row omitted from the vocabulary altogether. The prose under it then
    # reasoned from the wrong number ("Six `never` rows are all prose"). This is the
    # `Confirmed` column's own count, in the file whose entire subject is the difference
    # between tested and confirmed.
    _CONF_ORDER = (
        ("planted+observed", (r"\*\*planted\*\*\s*\+\s*\*\*observed\*\*",
                              r"\*\*observed\*\*\s*\+\s*\*\*planted\*\*")),
        ("planted", (r"\*\*planted\*\*",)),
        ("observed", (r"\*\*observed\*\*",)),
        ("test-only", (r"\*\*test-only\*\*",)),
        ("never", (r"\*\*never\*\*",)),
    )

    def _classify_confirmed(cell):
        for _label, _pats in _CONF_ORDER:
            for _pat in _pats:
                if re.search(_pat, cell):
                    return _label
        return None

    _sections, _cur = [], None
    for _line in _led.split("\n"):
        if _line.startswith("## "):
            _cur = (_line[3:].strip(), [])
            _sections.append(_cur)
        elif _cur is not None:
            _cur[1].append(_line)
    for _head, _lines in _sections:
        _conf_col, _tally = None, {}
        for _line in _lines:
            if not _line.startswith("|"):
                _conf_col = None
                continue
            _cells = [_c.strip() for _c in _line.strip().strip("|").split("|")]
            if "Confirmed" in _cells:
                _conf_col = _cells.index("Confirmed")
                continue
            if _conf_col is None or set("".join(_cells)) <= set("-: "):
                continue
            if _conf_col < len(_cells):
                _lab = _classify_confirmed(_cells[_conf_col])
                if _lab:
                    _tally[_lab] = _tally.get(_lab, 0) + 1
        _total = sum(_tally.values())
        _stated = re.search(r"^\*\*Counts[^*]*?:\s*(.+?)\*\*", "\n".join(_lines), re.M)
        if _total >= 3 and not _stated:
            fail(f"docs/evidence/verification.md: section {_head!r} has {_total} rows with "
                 f"a Confirmed value and no '**Counts …**' line — a table this size with "
                 f"no tally is a tally nobody can check, and the one that existed was wrong")
        elif _stated:
            _cap = _stated.group(1)
            _said = {}
            for _n, _lab in re.findall(
                    r"(\d+)\s+(planted\+observed|planted|observed|test-only|never)", _cap):
                _said[_lab] = _said.get(_lab, 0) + int(_n)
            if _said != _tally:
                fail(f"docs/evidence/verification.md: section {_head!r} states "
                     f"{ {k: _said[k] for k in sorted(_said)} } and its rows give "
                     f"{ {k: _tally[k] for k in sorted(_tally)} }")
            _rm2 = re.search(r"(\d+)\s+rows", _cap)
            if _rm2 and int(_rm2.group(1)) != _total:
                fail(f"docs/evidence/verification.md: section {_head!r} says "
                     f"{_rm2.group(1)} rows, its Confirmed column has {_total}")


# ── the plan is ordered on axes, never on a product ──────────────────────────
# Ported from `agent-stack` on 2026-08-24, where the same defect was found and
# closed first. `priority = (impact × confidence) / effort` sat in SKILL.md, the
# command, two references, the README, CLAUDE.md, a shipped template and a
# script's own output — eight live surfaces — beside a README that refuses "a
# score out of 100". A pack cannot say *not a score* and order its plan by one.
#
# Two design decisions, both learned from agent-stack's version:
#  * the name is an alternation, not the literal `priority`, because renaming the
#    variable would walk this check straight past the defect;
#  * the whole line must BE the formula. A formula inside a sentence explaining
#    why it was dropped is a citation, and refusing that would delete the record.
PRIORITY_SCALAR = re.compile(
    r"(?m)^\s*[-*]?\s*`?\s*(?:P|score|priority|rank|weight)\s*=\s*[^`\n]*[×*/][^`\n]*`?\s*$")
PRIORITY_AXES_REQUIRED = ("impact", "irreversibility", "uncertainty", "coordination")
PRIORITY_AXES_DECL = re.compile(r"<!--\s*priority-axes:\s*([^>]+?)\s*-->")


def check_the_plan_is_ordered_on_axes_and_not_a_product():
    """No live surface may prescribe a composed priority, and the axes are declared.

    The declaration is a machine-readable marker rather than prose: the axis list WAS
    prose here, and prose is what let two of the manifesto's four axes be absent from
    the entire pack while `effort` -- a cost, not a risk axis -- stood in their place.
    """
    # Live prescriptions only. `CHANGELOG.md` and `docs/` record what past releases
    # said and rewriting them is a thing this repository refuses; `docs/evidence/`
    # holds frozen records of runs.
    live = []
    for base in (SKILL_DIR, "templates", "cursor/rules"):
        for root_dir, _dirs, files in os.walk(os.path.join(ROOT, base)):
            if "__pycache__" in root_dir:
                continue
            for f in files:
                if f.endswith((".md", ".mdc", ".py")):
                    live.append(os.path.join(root_dir, f))
    for f in ("README.md", "CLAUDE.md", "CONTRIBUTING.md"):
        fp = os.path.join(ROOT, f)
        if os.path.isfile(fp):
            live.append(fp)
    cmd = os.path.join(ROOT, "plugins", "seo-aeo-audit", "commands")
    if os.path.isdir(cmd):
        live += [os.path.join(cmd, f) for f in os.listdir(cmd) if f.endswith(".md")]

    looked = 0
    for path in sorted(set(live)):
        try:
            text = open(path, encoding="utf-8").read()
        except OSError:
            continue
        looked += 1
        rel = os.path.relpath(path, ROOT)
        for m in PRIORITY_SCALAR.finditer(text):
            fail(f"{rel}: prescribes a composed priority -- {m.group(0).strip()!r}. "
                 f"Multiplication destroys the inputs the ranking argument needs: "
                 f"`4 × 1.0 / 4` and `1 × 1.0 / 1` both print 1. Order on the four "
                 f"axes and let the first that separates two findings decide")
    if looked < 5:
        _skips.append(f"priority-scalar sweep looked at only {looked} file(s) -- "
                      f"the corpus walk found almost nothing, which is a fact about "
                      f"the walk")

    home = os.path.join(ROOT, SKILL_DIR, "references", "deliverable-templates.md")
    if not os.path.isfile(home):
        fail("references/deliverable-templates.md missing -- it is the single home of "
             "the priority axes")
        return
    body = open(home, encoding="utf-8").read()
    m = PRIORITY_AXES_DECL.search(body)
    if not m:
        fail("references/deliverable-templates.md: no `<!-- priority-axes: ... -->` "
             "declaration, so the axis list is prose again")
        return
    axes = tuple(x.strip().lower() for x in m.group(1).split(",") if x.strip())
    if axes != PRIORITY_AXES_REQUIRED:
        fail(f"references/deliverable-templates.md declares axes {axes} -- the "
             f"manifesto names exactly {PRIORITY_AXES_REQUIRED}, and this is equality "
             f"rather than a subset: an axis that is not one of them is as wrong as "
             f"one that is missing (`effort` is the specific wrong one)")


check_the_plan_is_ordered_on_axes_and_not_a_product()


# ── the standing instructions: their run stamps and their cap ─────────────────
# `retro.md` says the run stamps are "what makes the cold-retirement trigger
# computable" and its newest was `v0.14.1`, eighteen releases behind HEAD — so no run
# could tell which instruction had gone cold, in the file every run is told to read
# first. And the prune log's arithmetic was wrong in the other direction: it said the
# list stood at eleven, one over the cap, while ten live instructions ship.
_RETRO = os.path.join(ROOT, "docs", "evidence", "retro.md")
if os.path.isfile(_RETRO) and plg_ver:
    _rt = open(_RETRO, encoding="utf-8").read()
    # Up to the prune log, not to the first blank line: the stamp series is a
    # paragraph of its own under the heading sentence, and a regex that stopped at
    # the first blank line read the heading and reported "no version".
    _sb = re.search(r"\*\*Run stamps[^*]*\*\*(.*?)\*\*Prune log", _rt, re.S)
    if not _sb:
        fail("docs/evidence/retro.md: no `**Run stamps…**` block — it is what makes the "
             "cold-retirement trigger computable, and the file says so itself")
    else:
        _stamps = re.findall(r"v(\d+\.\d+\.\d+)", _sb.group(1))
        if not _stamps:
            fail("docs/evidence/retro.md: the run-stamp block names no version")
        else:
            _newest_stamp = max(_stamps, key=semver)
            if semver(_newest_stamp) < semver(plg_ver):
                fail(f"docs/evidence/retro.md's newest run stamp is v{_newest_stamp} and "
                     f"the shipped version is v{plg_ver} — the stamps stopped eighteen "
                     f"releases behind HEAD once, which made the 'no firing in five run "
                     f"stamps' retirement trigger uncomputable. Stamp the release in the "
                     f"same change that bumps the manifests")
    _numbered = re.findall(r"^## (\d+)\.\s+(.*)$", _rt, re.M)
    _live = [_n for _n, _title in _numbered if not _title.strip().startswith("~~")]
    _CAP = 10
    if len(_live) > _CAP:
        fail(f"docs/evidence/retro.md carries {len(_live)} live standing instructions "
             f"against a cap of {_CAP} — the cap is the whole mechanism: an instruction "
             f"that cannot be added without retiring one is an instruction somebody has "
             f"to justify")
    _stands = re.findall(r"the list stands at \*\*(\w+)", _rt)
    if not _stands:
        fail("docs/evidence/retro.md: no 'the list stands at **N**' figure in the prune "
             "log — the count that decides whether the cap has been breached was wrong "
             "by one, in both directions, and nothing read it")
    elif numword(_stands[-1]) != len(_live):
        fail(f"docs/evidence/retro.md's last prune entry says the list stands at "
             f"{_stands[-1]!r}; counting live `## N.` headings gives {len(_live)} "
             f"({NUMWORDS.get(len(_live), len(_live))}) — struck-through headings are "
             f"retired and do not bind a run")
    _checked = re.findall(r"all (\w+) checked", _rt)
    if _checked and numword(_checked[-1]) != len(_live):
        fail(f"docs/evidence/retro.md's last prune entry says 'all {_checked[-1]} "
             f"checked'; {len(_live)} instructions are live")


# --------------------------------------------------------------------------- portability
# A plant that cannot run on the machine where it is written is a plant nobody watches
# fail. BSD sed needs an ARGUMENT to `-i`, so `sed -i "s/a/b/" f` is a no-op on macOS —
# and every one of this workflow's eleven sed plants was dead there until 2026-08-14,
# exercisable only in CI. Elsewhere in this family that is exactly how a broken plant hid
# for two days: the step reported a healthy guard as broken because the damage it was
# meant to do never happened.
#
# The replacement is `test/plant_edit.py`, whose verbs refuse BY NAME when their anchor is
# absent. This guard keeps sed from coming back, because the failure it causes is silent
# on one platform and invisible on the other.
_wf = os.path.join(ROOT, ".github", "workflows", "validate.yml")
if os.path.isfile(_wf):
    with open(_wf, encoding="utf-8") as fh:
        _wf_text = fh.read()
    # A CALL, not a mention. The first draft matched `\bsed -i\b` anywhere on the line and
    # flagged four lines the moment it shipped: a step name, a code comment, an `echo`, and
    # the payload string of the plant that deliberately writes one. That is standing
    # instruction #7 — a mechanical sweep cannot tell a path used from a path discussed —
    # so the pattern anchors on command position instead.
    # `do`, `then` and `else` are command positions too, and the first version of this
    # pattern missed them: `for f in …; do sed -i …; done` is a live call and read as
    # prose. Found on 2026-08-19, when a new plant's call site moved inside such a loop
    # and the sed self-test reported a healthy guard as broken. Still anchored — a
    # bare `\bsed -i\b` flagged a step name, a comment, an `echo` and a payload string
    # the moment it shipped.
    _sed_call = re.compile(
        r"(?:^|&&|\|\||;|\bdo\b|\bthen\b|\belse\b|\{)\s*sed\s+-i\b")
    _seds = [i + 1 for i, l in enumerate(_wf_text.split("\n")) if _sed_call.search(l)]
    if _seds:
        errors.append(
            f".github/workflows/validate.yml: `sed -i` at line(s) {_seds} — BSD sed needs an "
            f"argument to -i, so this is a no-op on macOS and the plant can only ever run in "
            f"CI. Use `python3 test/plant_edit.py`, which refuses by name when its anchor moved")
    if not os.path.isfile(os.path.join(ROOT, "test", "plant_edit.py")):
        errors.append("test/plant_edit.py is missing — the workflow's plants name it, so "
                      "every plant in this repository would fail to run at all")


def _disclose_routing(msg):
    """A check that could not run, said out loud rather than counted as a pass."""
    print(f"  unlooked: {msg}")


def check_routed_triggers_still_advertised():
    """The family's routing hook fires on words this description has to keep.

    B-54, 2026-08-16: `sheleg-design` 1.37.0 shipped green on its own gate having dropped
    a phrase from its description that was a live trigger in the umbrella's
    `lib/triggers.js`. This repository has no way to know that table exists, and it
    releases BEFORE the umbrella re-pins, so the umbrella found out minutes after the tag.
    A hook firing on a promise nobody made is the defect; a patch release was the cost.

    **The table is not copied here.** The umbrella's own checker is asked, reading the
    module the hook itself calls, so there is no duplicate to drift. When no umbrella sits
    above this checkout — the ordinary state of a standalone clone, and of CI — this
    discloses instead of passing, because a check that cannot look must never read as one
    that looked.
    """
    script = os.path.join(str(ROOT), "..", "..", "test", "advertised_check.js")
    if not os.path.isfile(script):
        _disclose_routing("routed triggers — no sshlg-skills umbrella above this checkout")
        return
    try:
        proc = subprocess.run(["node", script, "--member", "seo-aeo-audit", "--root", str(ROOT)],
                              capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError) as exc:
        _disclose_routing(f"routed triggers — could not run the umbrella's checker ({exc})")
        return
    if proc.returncode == 1:
        fail((proc.stdout + proc.stderr).strip())
    elif proc.returncode != 0:
        _disclose_routing(f"routed triggers — {(proc.stderr or 'the checker could not look').strip()}")


check_routed_triggers_still_advertised()


if not errors:
    residue.close_case("structural validator")
residue.report()

if errors:
    print(f"FAIL: {NAME} structure invalid")
    for e in errors:
        print(" - " + e)
    sys.exit(1)
_budget_note = ""
if _body_tokens is not None:
    _budget_note = (f", SKILL.md body ~{_body_tokens}/{_BODY_MAX_TOKENS} tokens "
                    f"/ {_body_lines}/{_BODY_MAX_LINES} lines")
    if _body_tokens >= _BODY_HOUSE_TOKENS:
        # Reported, not failed: the body is knowingly past the house limit and B-27
        # holds the remedy. A gate that goes red on a filed, deliberate state is a
        # gate everyone learns to run with `|| true`.
        print(f"note: SKILL.md body is ~{_body_tokens} tokens — inside the "
              f"{_BODY_MAX_TOKENS} budget, past the {_BODY_HOUSE_TOKENS} house limit "
              f"(B-27; the answer at this ceiling is a split, not a trim)")
print(f"PASS: {NAME} structure valid ({len(mdcs)} cursor rule(s), "
      f"{len(REQUIRED_REFERENCES)} reference(s){_budget_note})")
