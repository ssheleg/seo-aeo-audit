# FW06 — collector completeness and redirect provenance

<sub>ssheleg skills — task-pipeline · agent-sync · evidence-docs</sub>

As of 2026-10-13. Baseline `fbb721b2d26b6cfe1a966b90b093d9ba6e452110`;
branch `fix/fw06-collector-provenance`. Source acceptance only, not a release,
installed update or live-provider result. Baseline board: 36 rows, 28 with literal
`open` status; these are board records, not independently reproduced defects.

## Requirement decisions

- **B-7:** existing gzip salvage code already distinguishes incomplete streams.
  Added the missing loopback integration scenarios: complete gzip at the exact cap,
  client-capped gzip, server-incomplete gzip, complete empty gzip and corrupt empty
  gzip. Successful salvage flows through analysis and human output with its partial
  flag and suppresses completeness-dependent findings. No decoder rewrite was needed.
- **B-22:** reproduced missing redirect codes, lost error-response landing URL,
  missing collection/rendering provenance and an invented 301 in root-bounce text.
  A per-request stdlib redirect handler records observed source/status/target hops
  during the existing GET chain. Success and HTTP-error responses retain their final
  URL. A later transport failure retains observed hops with null landing status/URL.
  Probe rows and the API response contract expose this in JSON and human output.
  Root-bounce text names a redirect without guessing its code.
- **B-9:** remains open. The single migration home is
  [collector-coverage.md](../../contracts/collector-coverage.md). It defines units,
  requested/attempted/returned/dropped and unknown quantities, with a migration order.
  Current collector outputs do not uniformly implement it. In particular displayed
  agent-surface checks omit some alternate probes; their count must not be sold as a
  total request count. Byte/body completeness and GSC pagination remain separate work.
- **B-33:** remains open. This change updates only the SECURITY I/O-count plant that
  it affects, using a format-tolerant regex and `plantq`'s intended-guard needle.
  Baseline has 44 plain `plant` calls and 19 `plantq` calls; not all plain calls use
  the same checker. A whole-run nonzero exit is still insufficient attribution for
  the remaining document plants. No blanket negative-runner closure is claimed.

## Checks and evidence

Initial provenance regression on baseline: 1/13 controls passed, 12 failed for the
named missing evidence. Final regression adds API human rendering, so its final
corpus has 14 controls. The red run first exposed an incorrect reviewer fixture key;
after correcting it to the existing `chars` schema, the 12 failures above were
observed against unchanged implementation.

Focused checks: `python3 -B test/audit_regressions/fw06_probe_provenance.py`,
`python3 -B test/test_agent_surface.py`, `python3 -B test/test_page_audit.py`,
`python3 -B test/validate.py`, and `git diff --check`. Full owner validation and
negative-plant results are recorded below after completion, with their exit status.

- `npm test`: exit 0. Structural/doctrine gate and all existing behavior suites,
  then seven audit regression scripts including FW01 snapshot and FW06 provenance.
  Installer 11 and residue 11 cases pass; FW06 is 14/14. The source listing still
  reports native routed-trigger checks as unlooked in this standalone worktree.
- `python3 -B test/negatives.py -k 'reconciliation guards'`: exit 0, one selected
  workflow step passes; its suite snapshot was created and removed through residue.
  The updated I/O plant requires the actual I/O-count diagnostic. Other legacy
  plants in that step retain their documented attribution limitation.
- After clarifying the landing-status column label and the `answered` docstring,
  FW06 14/14, structural validation and diff checks passed again. Those two wording
  edits introduce no further transport behavior.
- A test-author fixture-key error retained one attributable synthetic tree. It was
  inspected and removed after diagnosis; no foreign tree was removed.

The structural guard observed the SECURITY I/O regex count change from 33 to 34.
The updated table accounts for two opener constructions and two opener requests;
construction is not itself a network request. The two overlapping `opener.open`
matches explain why summing per-pattern counts produces 36 rather than 34.

Only loopback HTTP fixtures and synthetic responses were used. No paid API, provider
account, foreign repository/configuration or installed skill was modified. New
regression files create no temporary tree. Existing owner tests retain their residue
ledger. The lease is local/advisory, not enforced across machines.

## Next task and bounds

Independent reviewer checks the frozen diff and replays the provenance regression,
especially success/error/transport-failure distinctions and ordinary direct responses.
Parent owns integration, complete candidate CI, release and installed readback.
Then implement B-9 from its contract and convert remaining B-33 plants with guard-specific
negative controls. Partial-byte reads, unattempted alternate URLs and provider row
windows must remain visible uncertainty until those collectors are migrated.

---

**Made with [ssheleg skills](https://github.com/ssheleg/sshlg-skills)**

- [`task-pipeline`](https://github.com/ssheleg/task-pipeline) — bounded collector repair
- [`agent-sync`](https://github.com/ssheleg/agent-sync) — advisory ownership
- [`evidence-docs`](https://github.com/ssheleg/task-pipeline) — measured checks and remaining scope
