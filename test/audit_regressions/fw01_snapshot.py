#!/usr/bin/env python3
"""FW01: real negative-runner lifecycle against tiny workflow inputs, no repo copies."""
import os
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
TEST = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TEST))
import residue


def probe(mode):
    box = Path(residue.workspace("snapshot-" + mode))
    source = box / "source"
    source.mkdir()
    (source / "marker").write_text("snapshot evidence")
    script = "echo OK: tiny" if mode == "pass" else "echo FAIL: tiny; exit 1"
    workflow = source / "workflow.yml"
    workflow.write_text("- name: Negative self-test tiny\n  run: |\n    " + script + "\n")
    scratch = box / "scratch"
    scratch.mkdir()
    driver = f"""
import sys
sys.path.insert(0, {str(TEST)!r})
import negatives, negative_lock
# Owned lock: the helper ignores TMPDIR, so without this the fixture queues on the
# public family lock behind any running suite (FW07).
negative_lock.scratch_lock_path = lambda: {str(box / "owned-family.lock")!r}
negatives.ROOT = {str(source)!r}
negatives.WORKFLOW = {str(workflow)!r}
negatives.MIN_EXPECTED = 1
negatives.MIN_PROPS = 0
"""
    if mode == "exception":
        driver += "def broken_copy(*args, **kwargs): raise OSError('fixture copy failure')\nnegatives.shutil.copytree = broken_copy\n"
    driver += "sys.exit(negatives.main(['negatives.py']))\n"
    result = subprocess.run([sys.executable, "-B", "-c", driver], text=True,
                            capture_output=True, env=dict(os.environ, TMPDIR=str(scratch)))
    trees = [p for p in scratch.iterdir() if p.is_dir()]
    assert result.returncode == (0 if mode == "pass" else 1), result.stdout + result.stderr
    if mode == "pass":
        assert trees == [], trees
        assert "1 temp tree(s) created, 1 removed" in result.stdout, result.stdout
    else:
        assert len(trees) == 1, (trees, result.stdout, result.stderr)
        assert "1 of 1 temp tree(s) KEPT" in result.stdout, result.stdout
        assert str(trees[0]) in result.stdout, result.stdout
        assert trees[0].name.startswith(residue.PREFIX), trees
        if mode == "fail":
            assert (trees[0] / "repo" / "marker").read_text() == "snapshot evidence"


failures = []
for mode in ("pass", "fail", "exception"):
    residue.open_case(mode)
    try:
        probe(mode)
    except AssertionError as exc:
        failures.append(mode)
        print("FAIL:", mode, exc)
    else:
        residue.close_case(mode)
        print("OK:", mode)
residue.report()
print(f"FW01 snapshot: {3 - len(failures)}/3 passed")
sys.exit(bool(failures))
