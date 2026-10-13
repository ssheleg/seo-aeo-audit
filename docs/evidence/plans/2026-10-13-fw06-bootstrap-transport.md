# FW06 transport and bootstrap completion packet

Status: proposed contract, before implementation. Stacked on independently accepted
preflight source `9d9b16690c7df4e058c9d237d1a18ad8a0784633`; current accepted
member main is `2de0d4042e1a312f4366ada325118b2a4413d760`. All sub-slices need
focused independent review, then one composed owner gate and normal PR admission
for the coherent next 0.26.6 correction. No tag or live provider calls in this packet.

## Actual baseline, not an inherited completion claim

`python3 -B docs/evidence/plans/fw06-transport-probe.py` makes only loopback calls
and uses fake ADC/token values. The tracked `2026-10-13-fw06-transport-baseline.json`
records 12 source-bound observations; the one owned fixture was removed:

| Home | Observed false/failed behavior | Existing consumer/return contract |
|---|---|---|
| page audit | Conflicting length headers return `truncated=false`; 5048 decoded gzip characters escape a 128-byte budget with `truncated=false`. | Array of page/error records; incomplete HTML retains fragment evidence but suppresses whole-page negatives/counts. |
| agent surface | Conflicting length headers return status200/body_complete=true. | Object plus per-unit coverage; returned network body requires observed status and complete body. |
| sitemap | Conflicting lengths admit one page from parseable XML. | Object; returned document requires complete parseable XML, incomplete traversal leaves requested universe unknown. |
| PSI | Conflicting lengths admit useful URL measurement. | Object with input-entry coverage and separate field/origin/lab semantics. |
| GSC | Conflicting lengths admit a typed empty row array; error-body IncompleteRead escapes actual main with no output. | Object with distinct API and unknown row-population records; one operation failure must preserve other dimensions. |
| URL Inspection | Conflicting lengths count answered1; scalar response and numeric verdict crash; unknown-only indexStatus counts returned1 and emits never-crawled; error-body IncompleteRead loses actual main output. | Object of per-URL results; an index answer must be observed before findings/returned count. |

These findings do not rewrite earlier bounded acceptance receipts. The prior
assertion that agent-surface already guarded duplicate framing was not true of the
accepted source inspected here. Preflight now has the independently reviewed guard;
other homes still need it. Its status-return semantics differ from complete-body
collectors and remain explicit.

## T1: common bounded transport, without changing public carriers

Inventory every home before editing: `page_audit.py:fetch/_gunzip`,
`agent_surface.py:_read_response`, `sitemap_audit.py:fetch/decode_body`,
`psi_pull.py:fetch`, `gsc_pull.py:call`, `url_inspection.py:inspect`, and the corrected
`preflight.py:_read_probe`. Preserve standalone shipping: no runtime sibling import.
A small byte-reading/framing block may be duplicated byte-identically and guarded
across seven homes, with caller-specific interpretation outside it.

- Read a raw cap plus one byte, and bound gzip decompression independently. Do not
  inflate an entire compressed body before checking the decoded cap. Preserve valid
  fragment observations only in collectors whose contract already supports them.
- Read all Content-Length occurrences/comma members using ASCII decimal admission;
  equal normalized values are allowed, contradictory/malformed values remain
  incomplete. A Transfer-Encoding plus Content-Length combination is incomplete.
  No unbounded integer conversion of header text. Unsupported transfer/content
  encoding is a limitation, never arbitrary bytes presented as a complete body.
- Handle HTTPError bodies through the same bounded reader, retaining observed
  status where the existing result carries it. Body read/decode errors must not
  escape to erase unrelated URLs/dimensions. Error diagnostics redact known token
  or key echoes before truncation; an error body cannot grow without a cap.
- Page audit keeps its `(text, headers, truncated)` API and array carrier. The raw
  and decoded caps both use its existing `max_bytes`; ambiguous framing or salvage
  marks truncation, preserving only eligible fragment findings. Agent/preflight
  retain their observed status plus body limitations. Sitemap refuses incomplete
  documents and keeps traversal/unknown-frontier evidence. Providers refuse an
  incomplete JSON document as a usable API envelope, preserve its per-input error,
  and continue independent inputs/operations. Do not invent parsed-zero rows.
- Add a documented byte budget for currently unbounded provider JSON reads (proposed
  8,000,000 raw and decoded bytes per response, matching preflight's existing JSON
  budget). This is transport scope, not a traffic/row ceiling or complete provider
  population. Capped bodies give explicit unavailable payload/unknown row state.

T1 acceptance: actual loopback duplicate equal/conflicting/malformed lengths,
TE+CL, chunked-only positive, identity/gzip, corrupt and incomplete gzip, raw and
inflated cap, empty valid bodies, error-body exceptions, mixed URL/operation
preservation and copied standalone calls. Compare all applicable JSON/default
counts/limitations; plant false completeness and an uncapped-inflate control. No
large-memory stress or real provider requests are needed.

## T2: typed URL Inspection admission

Do not certify an engine answer from nonempty `indexStatusResult` alone. Admit
recognized fields with their documented shape, refuse booleans/numeric/object
values where a string/URL/status is required, and preserve usable siblings with
explicit payload diagnostics. Empty/unknown-only/scalar envelopes establish no
index answer. Invalid canonical/verdict values cannot generate canonical mismatch,
not-indexed or never-crawled findings. A recognized valid field is an observation;
an absent field remains absent, and malformed data is not a valid absence.

Keep the existing object/result keys and `answered_rows` as the single predicate
for coverage and exit. Unknown-only results produce the existing no-index-status
report gap, not a verdict about a page. Validate all named field shapes against the
current official URL Inspection schema before freezing this slice. Existing indexed,
excluded and rich-result positives must remain valid. Add actual main mixed
malformed/valid controls and a false-answer mutation. No provider permission is
inferred from fixtures.

## B1: bootstrap carrier and input-resolution boundaries

A successfully parsed invocation that cannot resolve inputs or credentials must
emit honest diagnostics/coverage without changing successful output shapes.
Argument-parser usage errors and `--help` are explicit non-collection boundaries;
do not invent completed probes for them. Known empty input is zero; an unreadable
list's unknown population is null. Keep counted explicit URLs even if an optional
list fails, and do not deduplicate collectors that intentionally retain duplicates.

| CLI/carrier | Proposed bootstrap behavior |
|---|---|
| page audit array | Local-file failure emits a typed `record_type=input_error` array row with the existing error/findings keys and the supplied base URL or empty label. Unreadable/empty URL list emits one typed input-resolution error row with empty URL label, not an observed page; invocation coverage counts zero attempts and requested=null for unreadable population, zero for a genuinely empty file. Array length is not an input denominator. Successful page rows remain unchanged. |
| PSI object | Preserve producer/strategy/results; retain known explicit URL entries alongside failed-list diagnostics. Unknown list population gives requested=null/dropped=null with actual known attempts/returns. No-input emits zero-input partial/error record and exits1. Catch UTF-8 failures, not just OSError. |
| URL Inspection object | Preserve URL dedup/cap. Keep known explicit URLs when a list fails; requested population is unknown. Credential failure excludes known selected URLs before attempt, with a prerequisite reason, zero API attempts and explicit per-input unattempted state. Do not mint actual tokens in fixtures. |
| GSC object | Credential failure records known scheduled API operations as excluded-before-attempt; provider row populations remain unknown. Explicit `--list` is a one-operation mode with JSON/object versus text rendering and no row-population completeness claim. Missing site without `--list` is usage before credentials/network; stop implicit property-list traffic. Preserve full-report success keys/semantics. |
| sitemap object | No-input emits an honest zero-input error envelope; local-file failures already traverse the normal one-attempt path and must remain covered. No fabricated URL root. |
| preflight object | No site/origin emits no-probe error envelope; legacy track rows stay unlooked, common operation counts zero/partial, no fabricated Python/ADC/network attempt. Provenance remains a no-probe seed. |
| agent-surface object | Audit existing no-input/argparse boundary and local-file record; preserve already implemented local failure evidence and don't add a phantom network request. |

The new error-only page array row is explicitly typed as input resolution, not a
page, and exists only on paths that previously emitted no JSON. JSON/default
renderers must label it that way. Consumer tests must prove existing successful
arrays still support `.[].url`, mixed error records don't count as observed pages,
and repeated invocation coverage remains consistent. Do not switch to a wrapper
object under the existing JSON flag.

B1 acceptance: no-input, empty/missing/invalid-UTF8 lists, explicit+failed-list,
dedup/cap combinations, unavailable/empty/timed-out ADC, failed listings and valid
empty listings. Assert no provider request when prerequisites fail, no echoed raw
ADC stderr, null unknown population, no lost known results, intended exit codes,
legacy carrier compatibility and copied standalone execution. Record parser/help
boundaries explicitly; do not close B-9 by calling an absent record complete.

## Delivery and retained open work

Freeze each slice with its red/green evidence and peer source review. Compose only
reviewed deltas and run one `npm run test:all` after the serial slot clears. Preserve
reviewed preflight9d9b166 source acceptance and all preceding failed runs. Complete
normal PR checks/integration before packaging0.26.6; parent owns family pin updates.
Provider/live/model/native effectiveness remains NOT_RUN. Unrelated board rows,
GSC pagination, real credentials and new audit products are outside this packet.
