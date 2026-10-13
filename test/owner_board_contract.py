"""Bounded board grammar plus real structural validator mutation controls."""
from pathlib import Path
import shutil
import subprocess
import sys
from owner_board import board_errors


def run(check,root,workspace):
    count=0
    def ok(cond,label):
        nonlocal count
        count+=1;check(cond,'R30 SEO board: '+label)
    base='| ID | Item | Status |\n|---|---|---|\n| B-1 | one | open |\n'
    for text in (base,base.replace('one',r'one\|two'),base+'\nA prose reference to B-1.\n',base+'\n```\n| B-1 | example | done |\n```\n',base+'\n| Metric | Value |\n|---|---|\n| count | 1 |\n',base.replace('B-1','**B-1**'),base.replace('B-1','[B-1](#item)')):
        ok(not board_errors(text),'valid declaration, escapes or non-declaration content')
    for text,needle in [
        (base+'| B-1 | duplicate | open |\n','duplicate ID'),
        (base+'\n'+base,'duplicate ID'),
        (base.replace('one |','one | extra |'),'row width'),
        (base.replace('one | open','open'),'row width'),
        (base.replace('one',r'one\\|two'),'row width'),
        (base.replace('|---|---|---|\n',''),'immediate matching separator'),
        (base.replace('|---|---|---|','|---|---|'),'immediate matching separator'),
        (base+'\n| B-2 | orphan | open |\n','without ID header'),
        (base.replace('| B-1 |','| bogus |'),'invalid ID'),
        (base.replace('| ID |','| Row |'),'Row header unsupported'),
        (base.replace('| B-1 | one | open |','| B-1 | one | open'),'row width'),
        ('','no declared rows'),
    ]:ok(any(needle in err for err in board_errors(text)),'reject '+needle)
    # Clone shares only the immutable object store, then overlay the exact tested
    # worktree sources. Only this owned clone is mutated, and only one at a time.
    target=Path(workspace)/'repo'
    result=subprocess.run(['git','clone','--shared','--quiet',str(root),str(target)],capture_output=True,text=True)
    if result.returncode:raise RuntimeError(result.stderr)
    for relative in ('test/validate.py','test/owner_board.py','test/owner_release.py','docs/evidence/backlog.md'):
        shutil.copyfile(Path(root)/relative,target/relative)
    board=target/'docs/evidence/backlog.md';original=board.read_text()
    lines=original.splitlines(keepends=True);index=next(i for i,line in enumerate(lines) if line.startswith('| B-35 |'));row=lines[index]
    def validate():
        return subprocess.run([sys.executable,'-B','test/validate.py'],cwd=target,capture_output=True,text=True)
    result=validate();ok(result.returncode==0,'actual validator repaired baseline')
    for label,replacement,needle in [
        ('duplicate',''.join(lines[:index+1]+[row]+lines[index+1:]),'board duplicate ID B-35'),
        ('width',''.join(lines[:index]+[row.replace('| B-35 |','| B-35 | extra |',1)]+lines[index+1:]),'board row width: B-35'),
        ('escaped',''.join(lines[:index]+[row.replace('| B-35 |','| B-35 |',1).replace('| 5.0 |',r'| 5.0\|fixture |',1)]+lines[index+1:]),None),
    ]:
        board.write_text(replacement);result=validate()
        ok(result.returncode!=0 and needle in result.stdout if needle else result.returncode==0,'actual validator '+label+' control')
    board.write_text(original+'\n```\n| B-1 | example | done |\n```\n')
    readme=target/'README.md';saved=readme.read_text();readme.write_text(saved+'\nB-1, closed by this unsupported fixture.\n')
    result=validate();ok(result.returncode!=0 and 'board reads' in result.stdout,'fenced example cannot replace live row status')
    readme.write_text(saved);board.write_bytes(b'\xff')
    result=validate();ok(result.returncode!=0 and 'board unreadable: invalid UTF-8' in result.stdout,'unreadable board named refusal')
    board.unlink();result=validate();ok(result.returncode!=0 and 'board missing or unreadable' in result.stdout,'missing board named refusal')
    board.write_text(original)
    release=target/'.github/workflows/release.yml';workflow=release.read_text()
    for before,after,needle in [('git merge-base --is-ancestor','git merge-base-removed --is-ancestor','guard missing'),('fetch-depth: 0','fetch-depth: 1','full-history')]:
        release.write_text(workflow.replace(before,after,1));result=validate()
        ok(result.returncode!=0 and needle in result.stdout,'actual validator release '+needle+' refusal')
    release.write_text(workflow)
    print(f'R30 SEO board: {count} controls')


if __name__=='__main__':
    import residue
    failures=[];residue.open_case('r30-board');workspace=residue.workspace('r30-board')
    run(lambda cond,label:failures.append(label) if not cond else None,Path(__file__).resolve().parents[1],workspace)
    if not failures:residue.close_case('r30-board')
    residue.report()
    if failures:
        print('FAIL: R30 board');print('\n'.join('  - '+x for x in failures));raise SystemExit(1)
    print('PASS: R30 board')
