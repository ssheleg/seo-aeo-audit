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
REQUIRED_TEMPLATES = ("audit-report.template.md", "action-plan.template.md",
                      "experiments.template.md")
REQUIRED_REFERENCES = (
    "technical-checks.md",
    "discover.md",
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
    "standard-library only",
    "tier vocabulary",
    "myth count",
    "table integrity",
    "script reachability",
    "error flattening",
    "defect count",
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
_WORDNUM = {19: "nineteen", 20: "twenty", 21: "twenty-one", 22: "twenty-two",
            23: "twenty-three", 24: "twenty-four", 25: "twenty-five"}
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

# The gate is one fact with five homes: scripts/check-docs.sh runs it, CI repeats
# it, CONTRIBUTING and README tell a contributor what to run, and the PR template
# asks them to paste the output. CONTRIBUTING named two of the four commands and
# called CI "the same two"; the PR template was not counted as a home at all, so it
# kept asking for two of five long after that was corrected everywhere else.
_gate_path = os.path.join(ROOT, "scripts", "check-docs.sh")
if not os.path.isfile(_gate_path):
    fail("missing scripts/check-docs.sh — the documentation gate")
else:
    _gate_cmds = re.findall(r"^python3 (test/\S+\.py)\s*$", open(_gate_path, encoding="utf-8").read(),
                            re.M)
    if len(_gate_cmds) < 2:
        fail("scripts/check-docs.sh: no `python3 test/*.py` lines found — the gate-parity "
             "check cannot read it")
    for _rel in ("CONTRIBUTING.md", "README.md",
                 os.path.join(".github", "PULL_REQUEST_TEMPLATE.md")):
        _txt = open(os.path.join(ROOT, _rel), encoding="utf-8").read()
        for _cmd in _gate_cmds:
            if _cmd not in _txt:
                fail(f"{_rel} does not mention `{_cmd}`, which scripts/check-docs.sh runs — "
                     f"a contributor following the docs runs a subset of the gate")
    _ci = open(os.path.join(ROOT, ".github", "workflows", "validate.yml"),
               encoding="utf-8").read()
    for _cmd in _gate_cmds:
        if _cmd not in _ci:
            fail(f"CI does not run `{_cmd}`, which scripts/check-docs.sh runs")

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
_INVOCATION_HOMES = (
    os.path.join(SKILL_DIR, "SKILL.md"),
    "README.md",
    os.path.join("plugins", "seo-aeo-audit", "commands", "seo-aeo-audit.md"),
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
_RENDERERS = ("preflight.py", "url_inspection.py", "psi_pull.py", "page_audit.py")
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
    (os.path.join("docs", "superpowers", "retro.md"), r"exited 0 against (\S+) defects"),
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

# Every finding page_audit emits must have a tier in FINDING_TIERS. The behaviour
# test proves the fixtures carry one; this proves the next finding somebody adds
# cannot ship without one, which is the case a fixture cannot cover.
_pa = os.path.join(ROOT, SKILL_DIR, "scripts", "page_audit.py")
if os.path.isfile(_pa):
    _pasrc = open(_pa, encoding="utf-8").read()
    _declared = set(re.findall(r'^\s+"([a-z0-9-]+)": "(?:CONFIRMED|STUDY|FIELD|HYPOTHESIS)",',
                               _pasrc, re.M))
    _emitted = set(re.findall(r'add\(\s*"[a-z]+",\s*"([a-z0-9-]+)"', _pasrc))
    for _code in sorted(_emitted - _declared):
        fail(f"page_audit.py emits finding {_code!r} with no entry in FINDING_TIERS — "
             f"non-negotiable #2 makes the tier the multiplier in the triage formula")
    if not _emitted:
        fail("page_audit.py: no finding codes found — the tier-coverage check is blind")

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
