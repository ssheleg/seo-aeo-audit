#!/usr/bin/env python3
"""Structural validator for the seo-aeo-audit plugin repo. Exit 0 = pass."""
from __future__ import annotations

import json
import os
import py_compile
import re
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAME = "seo-aeo-audit"
SKILL_DIR = f"plugins/{NAME}/skills/{NAME}"
REQUIRED_TEMPLATES = ("audit-report.template.md", "action-plan.template.md")
REQUIRED_REFERENCES = (
    "technical-checks.md",
    "architecture-and-equity.md",
    "intent-and-content.md",
    "aeo-geo.md",
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
)
errors = []


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
        if len(fm) > 1024:
            fail(f"SKILL.md: frontmatter is {len(fm)} chars, must be under 1024")

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

# Every finding the auditor emits points a reader at a reference section. Those
# pointers are plain strings, so nothing else catches a heading rename.
# (Compilation and the stdlib rule are covered for every script by the loop above.)
script_rel = f"{SKILL_DIR}/scripts/page_audit.py"
script_path = os.path.join(ROOT, script_rel)
if os.path.isfile(script_path):
    src = open(script_path, encoding="utf-8").read()
    ref_dir = os.path.join(ROOT, SKILL_DIR, "references")
    slug_cache: dict = {}
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

# CONTRIBUTING.md tells a contributor what this file enforces, and had fallen four
# guards behind — the same drift as every other prose summary of a moving thing.
# Each guard family added here names itself, and the name has to survive in that
# paragraph. It does not prove the description is *accurate*; it proves nobody can
# add a guard family and leave the summary untouched.
_GUARD_FAMILIES = (
    "four-way version sync",
    "standard-library only",
    "tier vocabulary",
    "myth count",
    "table integrity",
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

# A prose count about a list, sitting next to the list, is the drift this repo
# keeps re-discovering: CONTRIBUTING said nineteen references while the validator
# enforced twenty-one, and the README's myth count went stale the moment two rows
# were added. Second occurrence of the class, so it stops being a review item.
_myths = os.path.join(ROOT, SKILL_DIR, "references", "myths.md")
if os.path.isfile(_myths):
    _rows, _in_table = 0, False
    for _line in open(_myths, encoding="utf-8"):
        if _line.startswith("| Claim | Reality |"):
            _in_table = True
            continue
        if _in_table:
            if not _line.startswith("|"):
                break
            if not _line.startswith("|---"):
                _rows += 1
    _readme = open(os.path.join(ROOT, "README.md"), encoding="utf-8").read()
    _m = re.search(r"myth guard\*\* that refuses (\d+) popular tactics", _readme)
    if not _rows:
        fail("myths.md: could not find the claim table — the count check is blind")
    elif not _m:
        fail("README.md: the myth-guard sentence changed shape; the count check "
             "can no longer read it (expected 'refuses N popular tactics')")
    elif int(_m.group(1)) != _rows:
        fail(f"README.md says the myth guard refuses {_m.group(1)} tactics, "
             f"myths.md carries {_rows} rows")

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
        fail(f"evidence-tiers.md: {_t} no longer carries weight {_w} — SKILL.md's "
             f"triage math quotes it")
    if not re.search(rf"{_t}\s*{re.escape(_w)}", _skill_txt):
        fail(f"SKILL.md: no '{_t} {_w}' in the confidence line — the weights have "
             f"drifted from references/evidence-tiers.md")
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

if errors:
    print(f"FAIL: {NAME} structure invalid")
    for e in errors:
        print(" - " + e)
    sys.exit(1)
print(f"PASS: {NAME} structure valid ({len(mdcs)} cursor rule(s), "
      f"{len(REQUIRED_REFERENCES)} reference(s))")
