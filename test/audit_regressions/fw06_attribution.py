#!/usr/bin/env python3
"""B-33 parser, intended-diagnostic and real anchor-liveness counterexamples."""
import os
from pathlib import Path
import re
import shutil
import shlex
import subprocess
import sys
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'test'))
import residue
from negatives import parse_steps
from plant_attribution import STEPS, calls, matches
from plant_edit import sub

checks = 0

def check(ok, why):
    global checks
    checks += 1
    assert ok, why

residue.open_case('FW06 intended guard attribution')
steps = parse_steps(ROOT / '.github/workflows/validate.yml')
rows, errors = calls(steps)
check(not errors, errors)
check(len(rows) == len({(r['step'], r['description']) for r in rows}), 'unique identities')
# Frozen pre-migration source identities must all survive the conversion, not just
# a fixed numerical floor. The snapshot is historical evidence, not new needles.
import json
baseline = json.loads((ROOT / 'docs/evidence/plans/fw06-attribution-inventory.json').read_text())
check({(r['step'], r['description']) for r in rows} ==
      {(r['step'], r['description']) for r in baseline['calls']}, 'all original identities retained')
for step in STEPS:
    body = dict(steps)[step]
    first = next(l for l in body.splitlines() if re.match(r'^\s*plantq\s', l))
    # No-op/omitted needle and anonymous calls cannot be admitted by structure.
    for broken in (first.replace('plantq ', 'plant ', 1), 'plantq "description" \\',
                   'plantq "description" "" \\', 'plantq "description" "$EXPECTED" \\'):
        _, problems = calls([(s, b.replace(first, broken, 1) if s == step else b) for s,b in steps])
        check(bool(problems), 'refuse missing/dynamic needle: ' + broken)
    _, problems = calls([(s, b.replace(first, first+'\n'+first, 1) if s == step else b) for s,b in steps])
    check(any('duplicate' in p for p in problems), 'duplicate identity')
    _, problems = calls([(s, '# plant "comment only"\nplant() {\n true\n}\n'+b if s == step else b) for s,b in steps])
    check(not problems, 'comments and function definitions are not calls')
_, problems = calls([(s,b) for s,b in steps if s != STEPS[0]])
check(any('missing attributed' in p for p in problems), 'missing group')
needle = 'expected semantic refusal'
for output in ('FAIL: structure invalid\n - '+needle, 'FAIL: output contracts\n  - '+needle,
               '  FAIL  case: '+needle):
    check(matches(output, needle), 'accept named checker failure')
for output in ('', 'PASS: '+needle, 'Traceback\n    '+needle+'\nSyntaxError',
               'note: '+needle+'\nFAIL: unrelated\n - anchor is missing',
               'FAIL: unrelated\n - another failure',
               'FAIL: old\nPASS: done\n - '+needle):
    check(not matches(output, needle), 'reject unrelated/echo/success')
check(not matches('FAIL: invalid\n - any', ''), 'empty needle')

box = Path(residue.workspace('fw06-attribution'))
# Execute the exact workflow selector command. It must refuse an unrelated file;
# the previous regex matched its empty alternation even without the target row.
body = dict(steps)[STEPS[0]]
lines = body.splitlines()
idx = next(i for i,l in enumerate(lines) if 'plantq "a table row with more cells' in l)
command = lines[idx+1].strip()
check('test/plant_edit.py sub' in command, 'workflow uses literal source-owned selector')
fixture = box/'selector'; (fixture/'test').mkdir(parents=True)
shutil.copy2(ROOT/'test/plant_edit.py', fixture/'test/plant_edit.py')
skill = fixture/'plugins/seo-aeo-audit/skills/seo-aeo-audit'
(skill/'references').mkdir(parents=True)
target = skill/'references/growth-plays.md'
for text, expected in [('# unrelated heading\n',False), ('| B1 | Manual action present | data |\n',True)]:
    target.write_text(text)
    proc = subprocess.run(['bash','-c','S=plugins/seo-aeo-audit/skills/seo-aeo-audit\n'+command], cwd=fixture,capture_output=True,text=True)
    check((proc.returncode == 0) == expected, 'literal selector result')
    check((target.read_text() != text) == expected, 'only intended target changes')
    if not expected:
        check('PLANT DID NOT LAND' in proc.stderr, 'missing target names refusal')
check(re.subn('^| B1 | Manual action present |','extra','# unrelated heading\n',count=1,flags=re.M)[1] == 1,
      'baseline regex falsely matched unrelated input')

# Execute BOTH actual workflow helper functions against controlled checker exits.
# Tiny fixture trees avoid full-suite repetition while preserving the complete
# copy/snapshot/mutation/verify/matcher chain and shell exit behavior.
for group_index, step in enumerate(STEPS):
    body = dict(steps)[step]
    function = body[body.index('plantq() {'):]
    function = function[:function.index('\n}')+2]
    root_literal = '/tmp/neg' if group_index == 0 else '/tmp/negb'
    harness = box / ('shell-' + str(group_index))
    (harness/'test').mkdir(parents=True)
    for name in ('plant_guard.py', 'plant_attribution.py'):
        shutil.copy2(ROOT/'test'/name, harness/'test'/name)
    # Prefix replacement also relocates the corresponding -residue sibling.
    isolated = box / ('helper-copy-' + str(group_index))
    function = function.replace(root_literal, shlex.quote(str(isolated)))
    for label, output, code, mutate, expected in (
        ('named failure', 'FAIL: fixture\n - expected semantic refusal', 1, True, 0),
        ('unrelated failure', 'FAIL: fixture\n - unrelated', 1, True, 1),
        ('success with needle', 'FAIL: fixture\n - expected semantic refusal', 0, True, 1),
        ('no mutation', 'FAIL: fixture\n - expected semantic refusal', 1, False, 1),
    ):
        (harness/'test/validate.py').write_text('print('+repr(output)+')\nraise SystemExit('+str(code)+')\n')
        command = "python3 -c \"open('changed', 'w').write('x')\"" if mutate else 'true'
        invocation = 'plantq "controlled" "expected semantic refusal" '
        if group_index:
            invocation += 'test/validate.py '
        run = subprocess.run(['bash', '-c', 'set -eu\n'+function+'\n'+invocation+command],
                             cwd=harness, capture_output=True, text=True)
        check((run.returncode == 0) == (expected == 0), 'actual helper: '+step+': '+label)
        if label == 'no mutation':
            check('PLANT DID NOT LAND' in run.stdout+run.stderr, 'real no-op refusal')
        elif expected:
            check('BROKEN GUARD:' in run.stdout, 'named helper refusal class')

# Actual source counterexample, not a toy validator: the same mutation remains
# landed while only its semantic branch is disabled. Anchor liveness still fails.
repo = box/'repo'
shutil.copytree(ROOT, repo, ignore=shutil.ignore_patterns('.git','__pycache__','node_modules'))
skillfile = repo/'plugins/seo-aeo-audit/skills/seo-aeo-audit/SKILL.md'
sub(str(skillfile), 'most-requested of the **33**', 'most-requested of the **30**')
validator = repo/'test/validate.py'
source = validator.read_text()
anchor = '\n        elif int(_m.group(1)) != _myth_rows:'
check(source.count(anchor) == 1, 'exact semantic branch')
validator.write_text(source.replace(anchor, '\n        elif False: # only intended semantic guard disabled',1))
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', TMPDIR=str(box))
proc = subprocess.run([sys.executable,'-B','test/validate.py'],cwd=repo,env=env,capture_output=True,text=True)
check(proc.returncode != 0, 'old exit-only helper would report pass')
check('plant will not land' in proc.stdout, 'anchor liveness remains active')
needle = 'the myth-guard section says 30 myths'
check(not matches(proc.stdout+proc.stderr, needle), 'new helper refuses unrelated liveness failure')
validator.write_text(source)
proc = subprocess.run([sys.executable,'-B','test/validate.py'],cwd=repo,env=env,capture_output=True,text=True)
check(proc.returncode != 0 and matches(proc.stdout+proc.stderr, needle), 'restored semantic guard named')
residue.close_case('FW06 intended guard attribution')
print(f'PASS: FW06 attribution {checks} controls')
