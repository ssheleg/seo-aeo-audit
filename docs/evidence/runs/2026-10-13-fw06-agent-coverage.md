# FW06 B-9 agent-surface probe coverage

Status: candidate implemented; focused checks below, independent review and owner
aggregate pending. Accepted sitemap base is
`dd5319a8935d60d0db7b3649b528d31d0b9ac45f`. Version remains 0.26.5. No provider
credentials/external requests, installed-host, task-quality or whole-site claims.

## Packet and measured problem

[The packet](../plans/2026-10-13-fw06-agent-surface-coverage.md) preserves source
inventory and a tracked reproducer. A finite mocked root/404 fixture made 47
fetch calls but displayed 23 checks; its selected-row `_answered` was also 23.
The new journal records each logical invocation including alternatives, header
variants and CLI-only OpenAPI/API probes. A separate near-miss fixture proved
that an unlisted landing response could still produce the false exit message
that every request failed. The final exit predicate now reads observed landing
statuses from the journal; a usable offline spec remains an answer too.

Consumer inventory found three singular collector carriers and preflight's
unrelated track-coverage object. The candidate therefore adds `coverage_by_unit`
without repurposing any existing `coverage`: network probes and optional local
files remain distinct common-schema records. The
[contract](../../contracts/collector-coverage.md) owns units, usable-return scope,
unknown discovery branches and the compatibility reader behavior.

## Implementation boundaries

`agent_surface.py` owns the invocation journal and response completeness flags.
Raw/gzip sentinel limits preserve status/header observations when body data is
incomplete. Malformed URLs become failed probes; local JSON/analyzer errors remain
explicit payload failures while earlier observations survive. A complete network
body is not proof every OpenAPI field answered, and a JSON object accepted by the
bounded analyzer is not full OpenAPI specification validation.

`test/collector_coverage_contract.py` supplies the independent carrier reader;
`test/agent_coverage_contract.py`, invoked from the existing output gate, supplies
mock/loopback/copied-CLI/mutation evidence and four-copy shared-block parity.
No workflow trigger, package version, skill entry or description changes here.

## Observed checks

The first dedicated fixture run exited 1 on absent accounting/journal and an
unhandled non-object local OpenAPI payload. After implementation,
`python3 -B test/agent_coverage_contract.py` passed **62 controls**, including
47/23 accounting, fixed versus blocked-discovery failures, separate/mixed local
inputs, legacy/new carrier acceptance and ambiguity rejection, physical-hop
separation, hidden-response exit behavior, loopback full/empty/404/redirect/gzip/
short/capped responses, actual standalone CLI calls and three executable mutants.
The mutant predicates name hidden request bypass, false complete-body return and
missing CLI-only attempt; they do not treat arbitrary checker errors as proof.

`python3 -B test/test_agent_surface.py` passed existing behavior.
`python3 -B test/audit_regressions/fw06_probe_provenance.py` passed **14/14**.
The combined `python3 -B test/test_output_contracts.py` exited 0 with 115 shared,
127 sitemap and 62 agent-coverage controls. `python3 -B test/validate.py` exited 0
with 25 references and unchanged SKILL body 4685 tokens / 325 lines; routed
trigger integration remains explicitly unlooked in this isolated checkout. Broad suite has not been run:
parent requested a disk/serial hold, so its absence is pending evidence, not a pass.
