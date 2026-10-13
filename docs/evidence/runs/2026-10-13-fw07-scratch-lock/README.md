# FW07 shared scratch-lock port — seo-aeo-audit

Frozen owner base `1e86edf178f0445ad2bace5fbbf79013de43f605`. The canonical
[TP source27b7e9e](https://github.com/ssheleg/task-pipeline/commit/27b7e9ef5722a79fd314216af183eb4db3a8ec5a)
was independently accepted with30 owned-namespace controls and42 existing runner
controls. Its packet proves different TMPDIR locks do not serialize fixed /tmp
plants and canonical owner scratch destinations overlap.

This owner port will copy `test/negative_lock.py` byte-identically, adapt the
runner's lock acquisition only, and replay fixtures under owned directories.
No public negative suite/list invocation, published payload, version or tag change.
The same helper supplies one physical-/tmp identity, exclusive create/no-follow
open, private regular current-user single-link admission and whole-suite flock.
It never truncates, chmods, unlinks or steals a lock. Old versions and directly
invoked plants remain outside the new mechanism.

Acceptance: owner actual runner refuses unsafe owned lock before plants and lists
under healthy owned lock; different TMPDIR/owner-labelled processes contend on
one inode, release/retry works; unsafe file kinds/modes/identity refuse unchanged.
Helper hash and excluded payload identity will be recorded after implementation.
Source-only plan at this commit; focused port and independent review next.

## Port implementation and focused results

[Helper identity](helper-identity.json) equals the canonical file byte-for-byte.
[Canonical independent review](canonical-independent-review.json) is source27b7e9
evidence, not independent acceptance of this owner adapter. Runtime package
version stays unchanged. [Dry-run payload readback](payload-parity.json) confirms
every included file's bytes match this owner's accepted base (46 SEO/68 dev files);
no package archive was published and temporary npm cache was removed.

`python3 -B test/audit_regressions/fw07_scratch_lock.py` passes
[30 controls](focused30.txt), exit0. `python3 -B test/validate.py` passes
[structural validation](structural.txt), exit0; the isolated checkout explicitly
discloses routed-trigger umbrella observation as unlooked. New regressions join
the existing `test:audit` glob, already part of the owner aggregate/CI.

The [first fixture run](first-fixture-failure.txt) failed because its positive
listing assertion was copied with TP's property-check suffix. These owners list
negative self-tests without that suffix. The common assertion now checks actual
negative-self-test listing and exit0; unsafe-lock refusal still requires exit1
and the admission diagnostic. No production guard was weakened.

SEO allocates its fixture through the existing residue ledger, without adding
a maker allowlist. Failed fixture35524 was retained, inspected through an owned-lock
listing, and removed after preserving its failure/output; corrected run reports
one created/one removed. No public scratch or lock was touched by this owner.

Next: independent owner-adapter review, required serialized aggregate, frozen
candidate promotion with genuine checks and normal merge. No full local suite
or hosted/release acceptance has run in this slice.

## Independent owner acceptance

[Independent frozen-source review](owner-independent-review.json) accepts SEO
d6c87c3 and dev366a2d3 adapters, exact helper identity and the dev dated-receipt
classification. It independently replayed30 controls per owner (SEO2.22seconds,
dev1.34seconds), exit0, using owned namespaces only. This is bounded source
acceptance; mandatory owner aggregate before PR remains queued behind the
coordinator's active release/full-suite slot. No public negative suite was run.


## Integration and version decision

[Author policy/readback](integration-plan.json) rechecks all 46 recorded npm
payload files against the accepted base and current source. No packaged byte
changed: retain 0.26.6, without a new tag or registry publication. This is an
author readback, not another independent review. The canonical helper has no
production environment override; path replacement is confined to owned fixtures.

`CONTRIBUTING.md:54` requires `bash scripts/check-docs.sh` before opening a PR and
provides no draft exception. The prepared PR text is saved in the integration plan;
no PR has been opened prematurely. Once the serial slot is available, run
`npm run test:all` so the changed negative runner and audit regressions are included.
Preserve exact source, output and any failure; then open the draft, freeze, promote
once for genuine required checks, and merge normally. Read back the accepted tree
and unchanged package payload before the parent's Git pin update. Old runner
versions and direct plant calls still lack the shared-lock protocol.

### New independent lifetime finding: acceptance held

The observer subsequently reproduced a gap with owned process barriers: killing
the runner parent releases its flock while a writing child survives; a contender
can enter before that child exits. The prior 30 controls do not establish
descendant-lifetime exclusion. Canonical helper/runner correction and independent
review are required before these ports' full gates and promotion. No public lock
or scratch path was used by the reproduction. The original review remains a
historical bounded result, not acceptance of this newly tested case.

## Child-lifetime correction port (TP 6b6d625)

Ported from task-pipeline [`6b6d625`](https://github.com/ssheleg/task-pipeline/commit/6b6d625)
(`compose/fw07-after-1941`; correction [`9c29ec3`](https://github.com/ssheleg/task-pipeline/commit/9c29ec3),
independently reviewed ACCEPT-WITH-FIXES and corrected; see TP packet
`docs/evidence/runs/2026-10-13-fw07-child-lock/README.md`, sections IO09 and
"Independent review of 25fb09d and correction"). Source diff `875c6e6..6b6d625`.

- `test/negative_lock.py`: copied byte for byte. `cmp` against TP 6b6d625 exits 0,
  sha256 `814951b89144c49e8bff9e575569518bc1cd3df06979929f2981945ebaa555d6`. The
  sheleg-dev copy is not yet ported, so the three-member identity is pending.
- `test/negatives.py`: `main` becomes `_main(argv, plants)`, wrapped in
  `ScratchProcesses`. Signal handlers are registered before any child. The lock is
  `plants.hold(...)`. Every plant Bash, including property checks, runs through
  `plants.run` (own process group, the lock fd passed through `pass_fds`).
  Workers check admission and cancel on any exception. `InterruptedError`/`OSError`/
  `RuntimeError` are reported as `FAIL: plant lifecycle refused (...)`, exit 1.
  No module-level constant was added, so `# diverges:` is unchanged.
- **Local divergence, snapshot:** TP removes its snapshot through `atexit`. Here the
  FW01 `residue` ledger already keeps and names an unfinished run's snapshot at
  exit, which `fw01_snapshot.py` asserts. So the port keeps that contract, and the
  snapshot control asserts the snapshot is kept *and named*, never an unreported orphan.
- `test/audit_regressions/fw07_child_lifetime.py`: TP's controls adapted to this
  runner (plants in a workflow file, `negatives.WORKFLOW` in BOOT). Fixture trees
  are `residue` cases, as `test/validate.py` requires
  ([first structural failure](child-structural-first-failure.txt)). Runner
  subprocesses get an owned TMPDIR. Every control is kept: parent/Bash SIGKILL
  (trailing `:`, writer's parent is not the runner), TERM/INT, normal, spawn,
  cancel-queue, startup signal, communicate fault, wait interruption, EPERM/ESRCH,
  cancel-fault drain, RuntimeError refusal and the snapshot.
- `test/audit_regressions/fw01_snapshot.py`: its driver called `negatives.main`
  with only TMPDIR redirected, which the helper ignores, so it took the **public**
  lock. It now patches `negative_lock.scratch_lock_path` to an owned file.
  This repository has no `runner_test.py`; no other test reaches the public lock.

Focused results on the ported tree, run while another owner's complete gate held
the public lock (public inode unchanged before and after; each run finished in
seconds, so none queued on it):

| Command | Exit | Count |
|---|---|---|
| `python3 -B test/audit_regressions/fw07_child_lifetime.py` | 0 | [62 controls](child-lifetime62.txt), 13 trees created/13 removed |
| `python3 -B test/audit_regressions/fw07_scratch_lock.py` | 0 | [30 controls](focused30-child-port.txt) |
| `python3 -B test/audit_regressions/fw01_snapshot.py` | 0 | [3/3](fw01-owned-lock.txt) |
| `python3 -B test/validate.py` | 0 | [structure valid](child-structural.txt) |

Red before, on a scratch clone with the new control file:
[old 78f2dd4 helper and runner](child-red-old-source.txt) and
[ported helper with old runner](child-red-old-runner.txt) both exit 1 at
`parent: actual writing Python inherits lock`. The
[ported runner with TP's pre-review 25fb09d helper](child-red-25fb09d-helper.txt)
passes the runner cases and exits 1 at the EPERM control (`PermissionError`).

**Operator-visible incident during this port.** One mistaken
`python3 -B test/negatives.py --help` started the full runner. This copy has no
argparse, so `--help` is not a refusal. It acquired the public lock and ran plants
for about two minutes. Then an independent complete gate (TP 6b6d625) began and
correctly waited on the flock. The run was stopped with SIGTERM. The ported
lifecycle drained its plant groups, and the gate took the lock next. Its kept
snapshot (this run's own process-group tag) was removed. Fixed `/tmp` plant paths
were left to the gate that then held the namespace. The unknown-flag defect is
open as backlog B-37, not fixed in this slice.

Not ported, not claimed: Linux, lock replacement while children hold it, a timeout
for a hung orphan plant, exit 130/143 on interruption (same limits as TP).
`test/negatives.py` in full, `npm test` and `npm run test:all` were **not** run.
**Owner full gate pending** on this source, then independent owner-adapter review,
PR and normal merge. Package payload unchanged (`test/` is not shipped): version
stays 0.26.6, no CHANGELOG entry (no unreleased section; CHANGELOG is shipped).

### Owner full gate on the child-lifetime port

`npm run test:all` on exact 087fa1a from a clean clone with an owned TMPDIR: exit0
in 281s, minimum free space 772MB — [result](owner-full-087fa1a.json),
[log](owner-full-087fa1a.log.gz). All 31 guards rejected their plant; the ported
`fw07_child_lifetime.py` (62 controls), `fw07_scratch_lock.py` (30), FW06 attribution
(93) and the owner-release controls (27) passed; residue: nothing left. This is the
owner gate, not hosted CI or a package release.
