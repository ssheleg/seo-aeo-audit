#!/usr/bin/env python3
"""B-33: inspect owner-parsed shell calls and match reported failure diagnostics.

This is not a shell interpreter. Calls in the two named workflow steps declare
literal description/diagnostic arguments on their opening line; continuation
lines hold the command. Whitespace/comments are allowed, dynamic identities are
refused. The workflow remains the single home of mutations and needles.
"""
import re
import shlex
import sys

STEPS = (
    'Negative self-tests for the reconciliation guards',
    'Negative self-tests for the provenance behaviour contracts',
)


def calls(steps):
    rows, errors = [], []
    found = set()
    for step, body in steps:
        if step not in STEPS:
            continue
        found.add(step)
        for line, text in enumerate(body.splitlines(), 1):
            if not re.match(r'^\s*plantq?(?:\s|$)', text):
                continue
            try:
                words = shlex.split(text.rstrip().removesuffix('\\'), comments=True)
            except ValueError as exc:
                errors.append(f'{step}:{line}: unparsed plant declaration: {exc}')
                continue
            if not words or words[0] != 'plantq':
                errors.append(f'{step}:{line}: anonymous plant has no intended diagnostic')
                continue
            if len(words) < 3 or any(not w.strip() or '$' in w or '\n' in w for w in words[1:3]):
                errors.append(f'{step}:{line}: literal nonempty description and diagnostic required')
                continue
            if step == STEPS[1] and (len(words) < 4 or words[3] not in ('$C', '$R')):
                errors.append(f'{step}:{line}: behavioral checker must be explicitly named')
                continue
            rows.append({'step': step, 'line_in_step': line, 'description': words[1],
                         'needle': words[2], 'checker': words[3] if step == STEPS[1] else 'test/validate.py'})
    for missing in set(STEPS) - found:
        errors.append('missing attributed workflow step: ' + missing)
    seen = set()
    for row in rows:
        key = (row['step'], row['description'])
        if key in seen:
            errors.append('duplicate plant identity: ' + row['description'])
        seen.add(key)
    for step in found:
        if not any(row['step'] == step for row in rows):
            errors.append('no attributed calls in ' + step)
    return rows, errors


def matches(output, needle):
    """Accept only a diagnostic row from the three owner checker output formats.

    A traceback/source echo, progress note or success text containing the needle
    cannot qualify. The shell additionally requires a nonzero checker exit.
    """
    if not needle.strip():
        return False
    in_failures = False
    for line in output.splitlines():
        if line.startswith('FAIL: '):
            in_failures = True
        elif line.startswith(('PASS:', 'OK:')):
            in_failures = False
        if re.match(r'^\s+FAIL\s{2}', line) and needle in line:
            return True
        if in_failures and re.match(r'^\s+- ', line) and needle in line:
            return True
    return False


if __name__ == '__main__':
    if len(sys.argv) != 3 or sys.argv[1] != 'match':
        raise SystemExit('usage: plant_attribution.py match <diagnostic> (output on stdin)')
    raise SystemExit(0 if matches(sys.stdin.read(), sys.argv[2]) else 1)
