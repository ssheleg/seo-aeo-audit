# FW01/FW06 patch release candidate, 2026-10-13

Branch `release/fw06-0.26.5` prepares 0.26.5 from accepted main
`4f4b53026d556f405ec9dd6600ea5898f1e91786` (PR28), including FW01 PR27.
The [FW06 receipt](evidence/runs/2026-10-13-fw06-collectors.md) records
implementation, independent review and local source checks. Packaging changes
versions, changelog and evidence only; script SKILL_VERSION identifies output provenance.

Exact next task: validate the frozen release candidate, independent packaging review,
normal PR merge, then annotated v0.26.5 tag and genuine release/registry readback.
Publication, parent pin and installed update are pending. B-9 and remaining B-33
work retain their explicit scope; a patch release does not close the full board.

---

# FW06 collector provenance, 2026-10-13

Objective: distinguish observed redirects, landing responses and incomplete gzip
input. Baseline `fbb721b2d26b6cfe1a966b90b093d9ba6e452110`; branch
`fix/fw06-collector-provenance`. Read the
[FW06 receipt](evidence/runs/2026-10-13-fw06-collectors.md) for reproduced failures,
checks and residuals. B-7/B-22 have local implementation/fixture coverage; B-9's
[migration contract](contracts/collector-coverage.md) is defined but not uniformly
implemented. B-33 is still open beyond the one affected I/O plant.

Exact next task: independent frozen-source review, then parent-owned integration and
release. Follow with common coverage emission and guard-specific legacy plant
attribution, preserving unknown quantities. No provider credentials are needed for
the delivered slice; live/provider acceptance remains separate.

## Prior FW01 snapshot accounting, 2026-10-13

Objective: account for the negative-runner snapshot on success and failure.
Implementation and three bounded regression cases are complete on this branch.
Read the [receipt](evidence/runs/2026-10-13-fw01-snapshot.md) for the base revision,
checks, limitations, shared-runner seam and exact next task: independent review,
then coordinator-owned integration and aggregate validation. No release was made.
The make-skill guard half is a separate owner change. Other open work remains in
[evidence/backlog.md](evidence/backlog.md).
