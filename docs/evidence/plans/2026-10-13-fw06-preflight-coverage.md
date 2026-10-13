# FW06 B-9 preflight and bootstrap follow-up packet

Status: proposed bounded contract; no preflight implementation yet. Base is
reviewed PSI `50e7c3e898602ab221b53cccb66620354fce5aec`. Reconcile accepted GSC/R30
and PSI before integration; local isolated branch owns only this packet/probe.

## Source and consumer inventory

`preflight.py:main` emits JSON with `producer`, `probes`, `reachable`, `total`,
`tracks`, `coverage_status` and **`coverage` as an audit-track list**. Existing
`test/test_output_contracts.py` and `references/preflight.md` plus
`references/deliverable-templates.md` consume that vocabulary/seeded table.
`--format coverage` runs probes then prints the track seed; only
`--format provenance` returns before probes. Do not silently change either mode.
The independent `test/collector_coverage_contract.py:coverage_records` already
accepts additive `coverage_by_unit` beside a track list, and refuses competing
common singular/per-unit records. Preserve all existing keys and list meaning.

`check_gsc` emits two visible rows (API and requested-property access) from one
logical API operation. `check_public` makes three logical requests: robots, the
first declared sitemap or fallback `/sitemap.xml`, and homepage. `check_psi` adds
one mobile PSI request unless skipped. Python and ADC are local probes. A display
row is therefore not a network-request denominator. Redirects/internal transport
attempts are not additional logical probes. No full sitemap traversal is requested.

## Reproduced defects

`python3 -B docs/evidence/plans/fw06-preflight-probe.py` at the base uses only mocks
and one ledger-owned invalid-UTF8 file. Its source-bound JSON snapshot is
`2026-10-13-fw06-preflight-baseline.json`:

1. A valid JSON PSI array makes preflight main raise `AttributeError` with empty
   stdout, losing previously collected public checks.
2. PSI `{}` is labelled lab-only although no lab score was observed.
3. GSC `siteEntry: [null]` raises `AttributeError` while evaluating property access.
4. PSI's invalid-UTF8 URL-list file raises `UnicodeDecodeError` before any report.
5. Preflight currently has only the track-list carrier, not common collector
   records. Its success exit is report completion, not all sources reachable.

Source inspection also shows `_get` reads prefixes without a sentinel/completeness
record, builds Request before its failure handler, and may throw while reading
HTTPError bodies. This is source inspection, not an executed transport finding.
`check_gsc` raw diagnostic text knows the token and must redact before truncation.
No provider permission or live service state was tested.

## First bounded implementation: preflight only

Add `coverage_by_unit` with separate `local_probe` and `network_probe` records.
Keep the existing report/track semantics and exit policy; a preflight report may
honestly contain blockers while exiting 0. Common coverage is not a replacement
for readiness, reachability or audit-track status.

- Local scope: Python inspection always, ADC acquisition only when `--site` is
  supplied. Requested/attempted count these scheduled local operations, not output
  rows. Returned means a determined local prerequisite outcome; missing executable,
  refused login and timeout remain explicit unsuccessful outcomes/limitations,
  not evidence that credentials exist. Never expose token/stdout in the journal.
- Network scope is known from flags: one property-list operation for `--site`,
  three public probes for `--origin`, and one PSI probe unless `--skip-psi`. With
  no ADC token the property-list operation is a known excluded input (`dropped=1`,
  attempted=0), with a prerequisite reason. A returned logical network probe means
  an observed landing HTTP status. Failed transport has no returned status. Any
  non-success status, incomplete body or unusable required JSON adds a limitation
  and keeps common state partial even when HTTP status itself was observed.
- Journal attempts/observations explicitly rather than infer them from visible
  `reachable` flags. GSC property-match output is derived from its one API response
  and does not count twice. A typed empty property list is observed; malformed
  envelope/row does not establish that the property is absent. Preserve independent
  public/PSI probes after GSC failure.
- Preserve landing status when body read fails. Bound reads with explicit cap/EOF
  evidence; a parsed prefix is never treated as a complete PSI/property document.
  Robots selection uses only the first declared sitemap or fallback as before;
  incomplete robots adds a scope limitation without inventing an unbounded crawl.
- PSI observations distinguish recognized valid URL-field percentiles, origin
  context and a valid lab score with the already reviewed numeric predicate. Missing
  field does not establish cause or lab presence. Wrong JSON types and nested
  components become diagnostics, preserving prior rows and later probes.
- Redact the known ADC token and its standard URL-encoded form before diagnostic
  truncation. Do not print raw token-mint stdout. Keep no-network provenance mode
  intact; exclude it from probe coverage rather than invent completed probes.

Acceptance: flags/site/origin/skip combinations, missing/empty ADC, typed empty and
malformed property lists, partial field/lab/origin PSI, scalar/deep JSON, capped
or failed bodies, 200/4xx/no landing status, first-sitemap selection, exact
local/network count arithmetic, legacy track-list identity, default/JSON parity,
coverage-mode behavior, pure provenance no-network control, copied standalone CLI
with local fake ADC/loopback, token echoes absent, and intended omission/false-return
mutants. Common block becomes seven byte-identical standalone copies. Peer review
before one serialized owner gate; live provider/model/host evidence stays NOT_RUN.

## Separate bootstrap envelope decision

Do not fold all seven CLIs into the first patch. `psi_pull.py` and
`url_inspection.py` catch OSError but not UnicodeDecodeError for URL lists;
`page_audit.py` has early file/list/no-input paths; GSC has credential/list/bootstrap
paths; sitemap has a no-input early branch; preflight requires site/origin.
Agent-surface local-file errors already have an independent record but must be
checked against the final carrier inventory. Argument-parser usage errors are
another boundary, not automatically a collector invocation.

Next bootstrap packet must decide each collector's preserved top-level shape,
known versus unreadable input denominator, and whether valid explicit inputs are
retained alongside a failed list file. For page-audit's array carrier, do not invent
an error-only object under the same public shape. Unknown list population is not
zero and cannot be added to counted explicit entries as though known. Keep this
work open until a source-aware per-CLI matrix and reader fixtures agree on the
shape; B-9 remains open after preflight alone. No new version/release in this plan.
