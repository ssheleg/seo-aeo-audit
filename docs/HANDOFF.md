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
