#!/usr/bin/env python3
"""Read the committed workflow through the owner's parser; write one new snapshot."""
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / 'test'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    for path in ('.github/workflows/validate.yml', 'test/negatives.py', 'test/plant_attribution.py'):
        committed = subprocess.check_output(['git', 'show', sha + ':' + path], cwd=ROOT)
        if (ROOT / path).read_bytes() != committed:
            raise ValueError('snapshot refuses an uncommitted source: ' + path)
    spec = importlib.util.spec_from_file_location('owner_negatives', ROOT / 'test/negatives.py')
    owner = importlib.util.module_from_spec(spec); spec.loader.exec_module(owner)
    from plant_attribution import calls
    steps = owner.parse_steps(ROOT / '.github/workflows/validate.yml')
    rows, problems = calls(steps)
    if problems:
        raise ValueError(problems)
    bodies = dict(steps)
    for row in rows:
        row['kind'] = 'plantq'
        lines = bodies[row['step']].splitlines()
        i = row['line_in_step']
        command = []
        while i < len(lines):
            command.append(lines[i].strip())
            if not lines[i].rstrip().endswith('\\'):
                break
            i += 1
        row['mutation_command'] = '\n'.join(command)
    workflow = (ROOT / '.github/workflows/validate.yml').read_bytes()
    data = {'schema': 'plant-attribution-inventory/1', 'source_commit': sha,
            'source_path': '.github/workflows/validate.yml', 'source_sha256': hashlib.sha256(workflow).hexdigest(),
            'parser': 'test/negatives.py:parse_steps', 'scope': 'Shell plant/plantq calls only; individual standalone negative steps are not included.',
            'calls': rows, 'counts': {step: dict(Counter(r['kind'] for r in rows if r['step'] == step)) for step in sorted({r['step'] for r in rows})}}
    with args.output.open('x') as output:
        json.dump(data, output, indent=2); output.write('\n')
    print(json.dumps({'calls': len(rows), 'counts': data['counts']}))


if __name__ == '__main__':
    main()
