# FW06 B-9 PSI response and coverage packet

Status: proposed contract, no PSI implementation yet. Stacked on reviewed GSC
source de16b2baeb07b22a13af7662fa2ae56a1aa5db06; reconcile the combined accepted
GSC/R30 candidate before integration. No provider request, key or release action.

The earlier tracked `fw06-provider-probe.py` reproduces an empty object exiting 0
with no URL-field, origin or lab measurement. Source `psi_pull.py:parse/main`
accepts any object without `_error`, and nested wrong types may abort later URLs.
The existing behavior tests require an unknown metric with missing percentile to
remain representable, so retain that entry with null value/unknown band instead
of silently dropping its presence.

## Proposed input and usable-return contract

- Keep the existing JSON object (`producer`, `strategy`, `results`); add singular
  `coverage` under common schema. Unit is `input_url_entry`, preserving duplicates
  and order. Requested and attempted count supplied URL entries, not field metrics,
  origin aggregates or transport retries. No local cap/drop is introduced.
- A returned URL entry has at least one finite nonnegative recognized URL-field
  percentile or a finite Lighthouse performance score in [0,1]. A genuinely zero
  metric/score is usable; booleans, numeric strings, negatives and nonfinite values
  are not measurements. Lab scores remain a separate synthetic measurement, never
  a field verdict. No arbitrary upper traffic/latency ceiling is invented.
- Origin-only data stays in its existing context field but does not make this URL
  a usable direct measurement. Empty/unusable responses therefore return zero for
  that input; an all-empty/origin-only invocation exits 1 while retaining reports.
- Per-row component status names URL field, origin context and lab independently.
  Missing components/recognized percentiles remain explicit limitations. Coverage
  can be partial even when every input returns one useful component; returned is
  not a field-completeness claim. No metric count is added to URL counts.
- Wrong envelopes and malformed nested metric/lab fields produce bounded payload
  diagnostics. Preserve valid components in the same response and valid other URL
  entries. Keep unknown metric entries with null/unknown, and never render None as
  a numerical value. Findings read only valid URL-field measurements.
- The useful-response predicate drives both exit and common coverage. Existing
  early no-URL/unreadable URL-list-file branches remain explicit bootstrap
  boundaries for this packet, not complete collection. They need a later envelope
  decision before all B-9 boundaries can be called closed.

## Error and evidence boundaries

Redact the supplied key before rendering/truncating provider diagnostics, including
plain and URL-encoded echoes. No real key is used by fixtures. API error envelopes
and transport errors are observations, not a clean zero measurement. Preserve old
result keys, add diagnostics/status rather than infer why data is absent.

The dated official PSI notice and links live in
`2026-10-13-fw06-provider-coverage.md`: Google plans to stop carrying CrUX data in
PSI, without a date in that notice. The report must say absence has no established
cause here; it may reflect provider availability or sample eligibility. It must
not assert low traffic or that the announced removal already happened. This work
adds no CrUX API fallback, paid call or authorization flow.

## Frozen acceptance before implementation

Fixture field-only, lab-only, origin-only, empty, all components, missing
percentiles, partial malformed nested components, scalar/list envelopes, actual
HTTP error/echoes, finite/zero/bool/string/negative/nonfinite values, duplicate URL
entries and mixed success/failure. Compare default Markdown and JSON counts,
states and exit; execute a standalone copy against loopback, require secret
sentinels absent, and plant an intended false-return counterexample. Keep provider
and installed-host evidence NOT_RUN. Integrate one reviewed source packet at a
time; GSC/R30 gates continue independently.
