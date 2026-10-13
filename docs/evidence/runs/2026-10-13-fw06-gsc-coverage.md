# FW06 B-9 GSC coverage candidate

Status: bounded implementation with focused acceptance; peer and owner aggregate
pending. Version remains 0.26.5. No provider credential, live API, quota/pagination
or native-host acceptance is claimed.

[The packet](../plans/2026-10-13-fw06-provider-coverage.md) records the baseline and
primary-source interpretation. Its tracked offline probe reproduced six requests
without common coverage and loss of all stdout after the third request failed.
The parent approved the separate request/unknown-row contract before code edits.

The candidate preserves typed envelopes independently, continues other operations,
and separates request counts from four provider row populations. The
[contract](../../contracts/collector-coverage.md) owns exact count semantics.
Malformed rows are failed attempts; known noise is excluded before attempts;
output slices occur after analysis. Failed dimensions stay unavailable beside
legacy derived keys, with qualified text conclusions. Invalid date windows fail
before credentials. List/bootstrap behavior remains explicitly separate.

The new fixture first exited 1 because emission was absent. After implementation,
`python3 -B test/gsc_coverage_contract.py` exited 0 with 54 controls: all six failure
positions, zero/malformed envelopes, invalid/zero/huge numeric rows, noise/display
arithmetic, cap uncertainty, early branches, credential redaction, real loopback
HTTP503 through the copied standalone CLI, and two executable accounting mutants.
Only a task-owned fake gcloud printed a fake sentinel; no user credentials were read.
`test/test_collectors.py` and structural validation passed. After merging accepted agent coverage e8aa59e, combined
`python3 -B test/test_output_contracts.py` passed 115 shared, 127 sitemap, 73 agent
and 54 GSC controls. Structural validation passed on that integrated source.

The fifth common coverage block needs GSC's seventh `_flat` home. DOCMAP and its
negative plant follow the measured count; the standalone provenance comment was
updated identically in all seven scripts, without changing that shared function.
One NOTHING MEASURED literal plant was updated to its changed honest wording.
Workflow events/jobs are unchanged. These affected negative groups still require
owner replay before integration.


## Aggregate-overflow review correction

Parent review of `53019f8618f23d1c48c730ee324d2374bbfc4f56` supplied two
individually finite query rows with clicks/impressions 1e308. Their sum overflowed
and erased both output formats despite six completed API operations. Extended
controls also showed nonfinite monthly/cannibalization JSON results and text
failure. The new tests first failed ten intended predicates after capturing these
actual main paths; an initial assertion assumed the not-yet-present error field
and was corrected to record its absence explicitly.

Finite-sum checks now refuse unrepresentable aggregates; isolated derivations
retain other dimensions and individually usable rows. Failed derived fields are
null with explicit operation/dimension errors and row-count qualification. No
arbitrary traffic ceiling or zero substitution was introduced. The final focused
GSC command passed **72 controls**, including query/date/query-page overflow in
both formats, brand/month/cliff/cannibalization paths and absence of nonfinite JSON
tokens. The two owned failed fixture trees were removed after replay. Independent
re-review and owner aggregate remain pending.


The parent then supplied a finite-over-finite quotient (clicks 1e308, impressions
1e-308) that became infinity without raising. Two new actual-main predicates
failed at 78fe9c9. Every derived result now has a recursive finite-numeric-leaf
check before admission, in addition to finite sums that guard internal control
flow. JSON/text preserve the report and explicitly refuse the affected position
aggregate. `python3 -B test/gsc_coverage_contract.py` passes **76 controls** after
this second correction; no new traffic ceiling or inferred metric consistency
rule was added.
