# FW01 remaining SEO source guard — bounded candidate

Base: [00601e620f7d273893b6a97566a26abd9e9b520e](https://github.com/ssheleg/seo-aeo-audit/commit/00601e620f7d273893b6a97566a26abd9e9b520e).
This is the missing source-guard half of agent-stack B-159. The earlier
[snapshot receipt](../2026-10-13-fw01-snapshot.md) remains valid and separate.
Status: focused source checks passed; independent review, coordinated owner full
gate and normal PR integration pending. No source/publication closure is claimed yet.

## Recovered gap and contract

The referral asked for both snapshot accounting and a whole-repository maker
scanner. The first was fixed; the second still admitted a script outside test/
with an aliased directory-maker call. The [baseline receipt](baseline.json) runs
the actual public validator on an owned archive of the exact base. Healthy,
outside-test alias, renamed from-import and changed ledger prefix all exited 0.
The last three are the watched missing refusals, not successful negative tests.

`test/validate.py` now uses the reviewed family lexical mechanism from
[make-skill c6b0470](https://github.com/ssheleg/make-skill/blob/c6b047057559f8dd2fe12dec59e4a4bee374fac2/test/validate.py),
which ports agent-stack AG-06a. Python sources are discovered recursively across
the repository, including shipped scripts and evidence helpers. Direct makers,
a one-component receiver alias, and renamed from-import forms are detected.

`TEMP_TREE_ALLOWED` admits exact paths, counts and call shapes, with no whole-file
skip. The observed source had four existing sites:

| Site | Exact admitted contract |
|---|---|
| test/residue.py | One attributed allocator with PREFIX + RUN_TAG and tag suffix |
| test/validate.py | One existing context-managed compiled-bytecode scratch call |
| test/test_agent_surface.py | One existing context-managed offline spec fixture |
| docs/evidence/runs/2026-10-13-shared-header-truth/reproduce.py | One historical context-managed header proof with its fixed prefix |

The three context managers retain their existing Python cleanup semantics; their
scratch directories are not counted as ledger allocations or retained failed cases.
Changing their call form, adding another maker to that file, or moving a maker to
an unregistered path is refused. Removing an exception's source file is also refused.
Historical evidence source was not rewritten. CONTRIBUTING and DOCMAP now state
this boundary instead of claiming every temporary tree goes through the ledger.
The new guard family is registered in the existing contributor-doc reconciliation.

## Checks and limits

The [focused receipt](focused.json) binds source hashes and command outputs. The
new audit regression has nine tiny source-fixture groups and one public-entry group.
The latter runs healthy plus alias/from-import/exemption-drift plants against the
actual complete validator, requiring the intended path and temp-tree diagnostic.
All ten groups pass; the public cases now produce 0/1/1/1. The actual final structural
validator also exits 0. The tests use residue-owned fixture trees; successful runs
remove their own trees. No extractor, provider or model call was made.

The existing audit glob discovers this regression. Full `npm run test:all` remains
queued after the parent's TP gate; it was not repeated concurrently. All 46 file
hashes in the accepted 0.26.6 publication receipt still match. Version, skill bodies,
collector scripts and workflows are unchanged; this source-only change needs no
new package tag if integration preserves that full payload equality.

The matcher is intentionally the reviewed bounded family mechanism, not a Python
semantic analyzer. Dependency/cache/build/fixture directories are excluded; JS and
shell allocations are not scanned. Chained receivers, stored references, getattr,
multiline renamed imports and embedded triple-quote markers can escape the lexical
matcher. A green source check does not prove every allocation is accounted for,
observe arbitrary TMPDIR contents, or establish runtime cleanup after SIGKILL or
power loss. Those limits are preserved in code and contributor docs.

## Handoff

Task FW01-SEO-SOURCE-GUARD owns an isolated branch and the validator lease. Lease
exclusion is local/advisory across machines, not distributed enforcement. Parent
owns the agent-stack referral board; B-159 remains partial until this slice is
independently accepted and integrated. Next: bounded peer review, one serialized
owner full gate, exact frozen draft promotion, genuine required checks and normal
merge, then full-tree/payload readback. No installed-machine update is authorized
or performed by this task.
