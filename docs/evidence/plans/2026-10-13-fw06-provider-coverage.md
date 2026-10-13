# FW06 next B-9 packet: provider collectors and readiness probes

Status: research/planning only, stacked at agent-surface candidate
`54fe9d523e816e5868cdf68eb771cdf42c7c53a9`. Reconcile its accepted source before
implementation. No credentials/provider traffic, version or release change.

## Reproduced source boundaries

- A mocked GSC full report makes six API calls: property listing, four Search
  Analytics dimensions and sitemap listing. It returns JSON/exit 0 without common
  coverage. A mocked failure at the third call raises SystemExit and emits no
  stdout, losing the earlier successful dimension. `gsc_pull.py:call/query/main`
  own these seams. Credential minting was patched; no actual token was requested.
- `psi_pull.main` given a mocked empty object returns exit 0 while both URL field
  metrics and the lab score are null. A transport object without any measurement
  is currently treated as a successful measurement. No PSI request was made.
- GSC's displayed row limits omit the date dimension's inherited 25,000 cap.
  Query/page results are additionally sliced to 100 output rows and pairs to
  5,000 after analysis; noise filtering is another distinct known exclusion.
- Preflight already owns a different `coverage` track-vocabulary object. Preserve
  it. Inventory actual external/local readiness probes before introducing an
  additive `coverage_by_unit` record, using the compatibility reader established
  by the preceding packet.

## Primary-source check, 2026-10-13

The current [Search Analytics query reference](https://developers.google.com/webmaster-tools/v1/searchanalytics/query)
limits a response to at most 25,000 rows and does not guarantee all source rows;
its dataset is constrained by Search Console. The official
[pagination example](https://developers.google.com/webmaster-tools/v1/how-tos/search_analytics#getting-more-than-25000-rows)
shows that an exact-sized last page can be followed by an empty page. Therefore
this script's `ROW_LIMIT_NOTE` assertion that the tail **is** missing is stronger
than the evidence. A reached cap proves an unresolved boundary, not nonzero unseen
rows. Even paging until empty would not certify the provider's whole population.

The current [PSI getting-started guide](https://developers.google.com/speed/docs/insights/v5/get-started)
announces a plan to stop including CrUX field data and points to the separate
CrUX/CrUX History APIs. It supplies no removal date in that notice. Do not infer
that removal has already happened, or that absent field data proves low traffic.
Keep endpoint absence and insufficient samples as possible causes, with the
actual response as evidence. This packet does not authorize live API use or add
an automatic paid/keyed fallback.

## GSC bounded implementation packet

1. Capture existing full-report and `--list`/missing-site/credential-bootstrap
   behavior separately. Freeze which branch is migrated; do not silently claim
   early no-report branches complete. Validate positive day windows before
   credentials if changing their current unchecked values.
2. Use a separate `api_request` record for six planned full-report operations,
   with observed attempts/usable typed responses. Calls and data rows are different
   units. Continue independent requests after a per-call failure where possible;
   retain earlier data and explicit errors instead of throwing away the report.
   Credential bootstrap failure remains a distinct prerequisite, not zero rows.
3. Preserve per-dimension row observations and unknown provider populations.
   A possible representation is common per-dimension row records with unknown
   requested/attempted populations, known retained rows and known exclusions;
   freeze this carrier against actual consumers before code. Never count query
   invocations as attempted rows, sum different dimension populations, or invent
   a numerical unseen tail. Report date-dimension caps, noise/invalid-row exclusions
   and output display slices at their actual layer.
4. Replace the cap assertion with uncertainty supported by the primary sources.
   Bound/validate response shapes before derivation so malformed rows do not erase
   valid earlier dimensions. Do not turn missing/error dimensions into clean zero
   findings. Preserve text/JSON and no-measurement exit semantics explicitly.
5. Tests: mocked six-call success and failure in every position; zero rows versus
   no response; exact cap versus below-cap/provider limits; date cap; known noise
   and output slices; malformed row types; finite windows; bootstrap/list branches;
   both output formats and standalone script execution. Real provider acceptance
   and pagination performance remain separate unobserved rows.

## PSI bounded implementation packet

1. Unit is supplied URL entry with duplicates preserved, parameterized by strategy.
   Separate API-call success, any recognized measurement, URL-level field metrics,
   origin context and Lighthouse lab data. A missing metric is not numeric zero;
   origin/lab never substitute for URL field evidence.
2. Refuse empty/unusable response objects as successful measurement. Preserve any
   valid rows when another URL fails or carries malformed payload fields. Emit
   common coverage with explicit absent-field/failed-input reasons and retain the
   original structured result keys/default Markdown behavior.
3. Update the field-absence explanation using the dated source notice above;
   do not invent an effective date or automatically call a different API/key.
   Keep raw provider diagnostics from echoing supplied credential values in the
   report; verify with fake sentinels, never real keys.
4. Fixtures: field-only, lab-only, origin-only, empty object, missing/malformed
   result fields, HTTP/error envelopes, duplicates, mixed success/failure,
   redacted provenance/error diagnostics, JSON/Markdown state/count/exit parity,
   copied standalone invocation. Provider response availability stays unobserved.

## Preflight final migration packet

Inventory network calls, credential/list/readiness checks and output paths first.
Choose measured units for readiness probe invocations; do not reuse the count of
track rows or turn access refusal into absent underlying data. Preserve existing
track `coverage` and `--format coverage`/provenance behavior; add typed collector
records through the explicitly named carrier only where collection actually ran.
Fixture `observed/unlooked/blocked` boundaries and no-network seeding modes. The
existing convention that failures are the preflight report remains explicit.

## Integration order

Resolve each packet's remaining carrier/branch choices, implement one collector
at a time, preserve context and negative controls, obtain independent review and
use the serialized owner gate only after a slot is released. B-9 closes only when
all declared homes and boundaries are reconciled; no source/schema pass implies
provider, installed-host or end-to-end task-quality acceptance. Keep version
0.26.5 until a separately reviewed coherent patch package is ready.


## Reproducible baseline and proposed GSC accounting

Run `python3 -B docs/evidence/plans/fw06-provider-probe.py` from this checkout.
It patches credential minting and provider calls in-process. At baseline
`54fe9d523e816e5868cdf68eb771cdf42c7c53a9` it reports GSC six calls / exit 0 /
no common coverage; failing call three reports three attempts / zero stdout;
PSI empty object reports exit 0 with no field, origin or lab measurement.
No raw provider response or real token is captured.

Before implementation, review this bounded accounting proposal:

- Keep the existing report object and add `coverage_by_unit`. `api_request`
  requested/attempted are six logical full-report operations, each independently
  caught after credential bootstrap. A usable return means a correctly typed
  collection envelope, including a genuinely empty collection; invalid individual
  rows remain separately visible. Failure never invents an empty provider result.
- Add separate `date_row`, `query_row`, `page_row`, `query_page_row` records.
  Requested is null because the provider population is not enumerable through
  this single page, even below the configured cap. Attempted counts received rows
  admitted to local validation/analysis after deliberate noise exclusion; returned
  counts usable analyzed rows. Dropped counts known noise exclusions only. Invalid
  rows are failed attempts, not double-counted drops. An unavailable/malformed row
  envelope leaves row counts unknown, rather than zero. An actual empty typed row
  list permits attempted/returned/dropped zero while requested stays unknown.
- Preserve raw received row counts and local invalid/noise counts in separate
  `row_observations` entries. The report's top-query/page/pair display slices happen
  after analysis; they are `display_omitted` observations, never unattempted input
  drops or provider-tail estimates. Text's smaller display slice is also named.
- All four dimensions expose their requested row limit, including dates. A reached
  limit adds `row_cap_reached`; every provider-population record includes a bounded
  `provider_population_unknown` explanation. No automatic pagination or numerical
  missing-tail estimate. Sitemap/property listing remain API observations, not
  Search Analytics row populations.
- Per-dimension observation state qualifies derived values. Failed or unusable
  dimensions cannot produce an unqualified “no collapse”, “none submitted”, or
  “none found” statement. Preserve existing JSON keys, with explicit observation
  status beside them; absent-data derivations must be distinguishable from an
  actual measured negative. Existing `measured_rows` remains the exit predicate
  for a full report, so a valid empty provider result is observed but not a useful
  site measurement. Bootstrap/list-only branches remain explicit early boundaries.

The proposal is not implemented or accepted by fixtures yet. The next step is a
contract review, then frozen negatives for response envelopes, invalid row shapes,
cap boundaries and output qualification before editing the collector.
