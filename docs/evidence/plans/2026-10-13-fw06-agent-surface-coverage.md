# FW06 next B-9 packet: agent-surface probe accounting

Status: implemented in candidate; [execution receipt](../runs/2026-10-13-fw06-agent-coverage.md) owns current checks/review.
Original planning snapshot: research/plan only; no collector implementation. Source observed at
`40c95d3c4d3267148e16e4767f28d28664ef3885`, stacked on the sitemap candidate.
Reconcile accepted sitemap main before implementation. The
[common contract](../../contracts/collector-coverage.md) remains the schema home.

## Measured defect

A local mock of `agent_surface.collect('https://example.invalid')`, returning a
200 HTML root and a 404 plain-text response for every other URL, observed **47**
`fetch` invocations and **47** unique `(URL, Accept, User-Agent)` variants. The
result had **23** `checks`, `_answered=23` and no common `coverage`. These are
counts from this finite fixture, not claims about a live site or every branch.
Reproduce from the checkout with
`python3 -B docs/evidence/plans/fw06-agent-surface-probe.py`; the tracked script
replaces the module transport and prints the five measured fields above.

The hidden calls are the entry-point alternatives and near-miss discovery loops.
`collect` may append a selected response later through `note`; deriving attempts
from displayed rows loses failed/unselected alternates. Reusing `_answered` as
network attempts or all usable responses would therefore fabricate a denominator.
`main` also fetches remote OpenAPI and API probes outside `collect`; a local
OpenAPI file can be combined with network options. All homes must be inventoried.

Other observed boundaries: `fetch` reads `MAX_BYTES` without a sentinel and
requests identity encoding. `Probe.answered` means a landing status exists, not a
complete usable body. HTTP errors can answer a status/header question; a complete
JSON/OpenAPI answer is a different predicate. URL parsing/Request construction
currently precedes its error-catching block. These are source findings, not
verified provider incidents.

## Implementation sequence and decisions to close first

1. Inventory every fetch and local-file read under `collect`, `main` and
   `collect_api_behaviour`. Classify the question each answers: landing status,
   headers, complete body, parseable JSON, or offline spec. Preserve actual
   redirect evidence; retries/hops are not extra logical probes.
2. Define a per-invocation attempt journal around one injected transport wrapper,
   retaining purpose, requested URL, Accept and User-Agent. Do not globally patch
   transport as the production mechanism, count selected `note` rows, or dedupe
   distinct header variants. Test repeated identical calls explicitly before
   deciding whether invocation or unique-probe identity is the unit.
3. Freeze the denominator before code: known scheduled probes, deliberately unused
   alternatives after selection, branch prerequisites that failed, and unknown
   discovered inputs must be distinct. A failed homepage can hide advertised
   links; absence of that branch is not proof that discovery was complete.
   Document finite scope and unknown frontiers instead of calling the whole site
   complete. For mixed local-file/network CLI runs, choose explicit per-unit
   records or a justified logical input unit; never silently add unlike units.
4. Bound body reads with completeness evidence while preserving observed statuses.
   A 404 answers a status probe; an unreadable/capped body does not answer markup
   or OpenAPI analysis. Add partial/unknown reasons at the layer whose question
   lost evidence; do not change all status probes to failed fetches.
5. Emit the existing JSON/text plus additive common coverage, preserve findings,
   keep the documented no-answer exit predicate explicit, and fixture every
   accepted input combination. Malformed URL, failed local read, failed parsing
   and failed later probes must not erase earlier observations.
6. Extend independent schema/copy parity and actual-source mutation controls in
   the existing output gate. Cover hidden alternatives, near misses, selected
   responses counted once, header variants, API-only/spec-only/mixed inputs,
   404/status success, body caps, partial failures, zero vs unknown, default
   Markdown/JSON agreement, unrelated-cwd standalone execution and bounded
   redirect evidence. No provider credentials or external traffic.
7. Update the single migration matrix, script reference, receipt, HANDOFF and B-9
   row. Run focused negatives, independent review, then one serialized owner gate
   and genuine frozen-candidate CI. Keep GSC, PSI and preflight open separately.

## Exact next task

Read accepted sitemap source and current owner policy/leases. Reproduce the
47/23 mock, inventory the two CLI-only network homes and mixed offline input,
then resolve step 3 in this packet before implementing the journal. Do not infer
provider, installed-host, whole-site or task-quality acceptance from schema pass.

Separately observed runner hygiene issue: `test/negatives.py --help` is not a help
path; unrecognized options currently start all groups. Use its documented
`--list`/`-k` interface. Any future CLI argument fix belongs to a separate bounded
runner packet with no-allocation negatives, not this collector migration.

## Carrier and denominator decisions after consumer inventory

The current three migrated collectors and their tests access `coverage` as one
record. `preflight.py` already emits a different track-vocabulary object under
that name. No existing carrier or schema is repurposed. Agent-surface will add
`coverage_by_unit`, a named map containing `network_probe` and, when an offline
spec was supplied, `local_file`. Each value is the unchanged strict
`collector-coverage/1` record. The independent reader will explicitly recognize
these supported carriers without interpreting preflight track coverage as a
collector record. Ambiguous competing collector carriers must refuse.

The network unit is one scheduled logical request invocation in this bounded
collector workflow, including hidden alternatives and distinct Accept/UA
variants. Repeated identical invocations remain separate: the count describes
what actually ran. Physical redirect hops/retries belong to transport evidence,
not extra logical attempts. A returned item means an observed landing status and
complete response body (including an empty body); it does not assert that every
analysis field answered or that a 200 document belongs to this product. A 404
can be a returned probe answering absence; status/headers remain observed even
when incomplete body excludes that request from complete returned responses.

Requested counts are scoped to this conditional workflow, not all site URLs.
A body/fetch failure that prevents a discovery-dependent branch from resolving
its input set requires unknown requested population and an explicit branch
reason. A failed fixed input remains a known attempted item without a returned
response. Alternatives deliberately unnecessary after successful selection are
outside the selected workflow's requested set, not failed probes. Instrument the
branch boundary, never infer this distinction from the number of rendered rows.
No cap currently exists over invocation count, so do not invent numeric drops for
unseen descendants; known omitted items alone can be dropped.

The local-file record is independent: one supplied OpenAPI file, one attempted
read, returned only when usable for the declared JSON-object analysis. Network
and local counts are never summed. An absent local-file input produces no local
record, not a fabricated failure. Existing findings/checks and producer keys stay
unchanged; JSON and Markdown carry all present per-unit records.

Before implementing, freeze tests for the 47/23 counterexample, header variants,
selected alternates, fixed versus blocked-discovery failures, mixed offline/network
runs and old singular-carrier compatibility. The whole-site unknown universe is
not a numeric requested denominator, and this packet does not certify provider
or native-host behavior.
