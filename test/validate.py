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

# every bundled script must exist, compile, and stay stdlib-only on python 3.9
for _script in ("page_audit.py", "gsc_pull.py"):
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

# the bundled auditor must exist and compile
script_rel = f"{SKILL_DIR}/scripts/page_audit.py"
script_path = os.path.join(ROOT, script_rel)
if not os.path.isfile(script_path):
    fail(f"missing script: {script_rel}")
else:
    with tempfile.TemporaryDirectory() as tmp:
        try:
            py_compile.compile(script_path, doraise=True, cfile=os.path.join(tmp, "page_audit.pyc"))
        except py_compile.PyCompileError as e:
            fail(f"{script_rel} does not compile: {e}")
    src = open(script_path, encoding="utf-8").read()
    # system python3 may be 3.9 — postponed annotations are required for `str | None`
    if "from __future__ import annotations" not in src:
        fail(f"{script_rel}: missing 'from __future__ import annotations' (python 3.9 support)")
    if re.search(r"\bimport requests\b|\bimport bs4\b", src):
        fail(f"{script_rel}: third-party import — the script must stay stdlib-only")
    # Every finding the auditor emits points a reader at a reference section. Those
    # pointers are plain strings, so nothing else catches a heading rename.
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
