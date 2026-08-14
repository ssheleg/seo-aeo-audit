# CLAUDE.md — working in this repository

This repo had no project instruction file until 2026-08-10. Everything below was
true and lived only in the operator's global files, which do not travel with a
clone: an agent invoked in a fresh checkout was told none of it.

## What this is

`seo-aeo-audit` is an **agent skill**, not an application. The deliverable is
knowledge plus six standard-library scripts, shipped to several agent channels at
once. So the failure modes are documentation failure modes: a claim that is wrong, a
count that has drifted, a pointer into empty space, a tool whose silence reads as a
measurement.

The skill's own doctrine applies to the repository that contains it. If a change
here would fail non-negotiable #1 (`evidence or silence`) inside an audit, it fails
here too.

## The gate

```bash
bash scripts/check-docs.sh
```

That script is the whole gate — `test/validate.py`, `test/test_page_audit.py`,
`test/test_url_inspection.py`, `test/test_collectors.py` and
`test/test_output_contracts.py`. CI runs the same set plus a negative self-test
per guard. The count is deliberately not written down here: it had four homes and
went stale in three of them the first time a test file was added. `test/validate.py`
reconciles the counts and cross-file facts this repo keeps re-breaking; CONTRIBUTING
names each guard family and the validator asserts that paragraph keeps up.

**Run the gate as its own command from the repo root and read its exit status.** Not
behind a pipe: a shell pipeline exits with the status of its last command, so
`bash scripts/check-docs.sh 2>&1 | tail -2 && git commit` has already committed once
past a gate that never ran.

## Where the settled things live

| Question | File |
|---|---|
| What is the single home of a fact, and what does changing it oblige? | `docs/DOCMAP.md` |
| Why was something decided this way? | `docs/DECISIONS.md` |
| What binds the next run? | `docs/evidence/retro.md` — standing instructions, read in full |
| What is open? | `docs/evidence/backlog.md` |
| Which shipped requirement has never been confirmed? | `docs/evidence/verification.md` |
| What was wrong on 2026-08-10 and what was done about it? | `docs/audit/2026-08-10-defect-ledger.md` |
| Where does a contribution go? | `CONTRIBUTING.md` |
| How is coordination wired, and what does it NOT guarantee? | `docs/AGENT_SYNC.md` — **generated** from `.claude/agent-sync.json`; read it before editing a guarded file, and regenerate it in the same change that alters the config |

## Four rules this repository learned the expensive way

1. **Count the homes before writing the reconciler.** Every guard here was once
   written against the one place a fact had drifted, while the fact lived in four.
   The myth count was green in a repository where three of its four homes were
   wrong.
2. **Severity is not an evidence tier.** Only the tier enters
   `priority = (impact × confidence) / effort`. Any finding a script emits carries
   one, declared in `FINDING_TIERS`.
3. **A pointer that resolves is not a pointer that answers.** `file.md#anchor` is
   validated; "see `myths.md` on why X" is not, and one of those pointed at a row
   that did not exist. If you cite a claim in another file, make the claim findable
   there.
4. **An instrument's silence must be marked as silence.** A truncated read, a capped
   row set, a probe that got nothing — each one is a gap in the report, never a
   number and never a blank. This is non-negotiable #8 applied to *coverage*, not
   only to JavaScript.

## Version and release

Four manifests plus the CHANGELOG top entry carry one semver and the validator
enforces it: `.claude-plugin/marketplace.json`,
`plugins/seo-aeo-audit/.claude-plugin/plugin.json`, `package.json`, `CHANGELOG.md`.
A release is not finished at `npm publish` — the `sshlg-skills` launcher pins this
member's version in its own `skills.json`, and a release that does not bump that pin
is invisible to `npx sshlg-skills list`. CONTRIBUTING has the sequence.

## Not in scope here

Writing content, building pages, buying links. The skill ends at a verified
diagnosis and an executable plan, and so does the repository.
