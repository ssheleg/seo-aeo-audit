# FW06 T2 — typed URL Inspection answers

Baseline: accepted implementation packet76818f2, production source6c3403d T1.
[Primary schema notes](../plans/2026-10-13-url-inspection-admission.md) were checked
before coding. The parent specifically required malformed crawl time to remain
unknown rather than become valid absence. All tests use fixtures/loopback/fake ADC.

## Behavior

Only recognized typed index observations feed `answered_rows`; scalar, unknown-only,
reserved/unspecified-only and empty-array-only payloads cannot count as answers.
Valid sibling fields survive with explicit payload limitations. Canonical and crawl
diagnostics distinguish malformed presence from absence. Rich-result values alone
do not prove index status. Google's reserved `PARTIAL` verdict is no longer described
as indexed. The confidence footer scopes evidence to admitted fields.

Result/object keys remain; additive `payload_errors` and `invalid_index_fields`
explain rejected fields without dumping their values. The single answer predicate
still controls both coverage and exit. `payload_fields_unavailable` makes partial
coverage visible even when a URL supplied another usable field. Parsed provider
error envelopes are redacted while the token is available in the transport adapter.

## Checks

- Initial57 controls FAIL on old source: scalar/numeric crashes, unknown-only
  false answers, malformed-field false negatives and missing diagnostics.
- Final75 focused controls PASS: documented valid observations; wrong types,
  reserved/unknown states; invalid crawl/canonical suppression; retained URL-list
  members; actual main JSON/default output; false-answer source mutant.
- The75 include copied standalone CLI subprocesses in both formats, fake local ADC
  and real loopback responses for three inputs. They retain all3 rows, admit1 URL,
  mark partial and make6 total requests across the two runs without a token echo.
- Existing `test/test_url_inspection.py`: PASS (field names, canonical/verdict,
  error/cap behavior, excluded states and scoped confidence).
- Structural validation and diff-check: PASS. Entry descriptions/version/workflows
  unchanged. Complete owner suite remains pending for the composed T1/T2/B1 wave.

Independent source review: pending. Bootstrap failures remain B1, provider/live
access remains NOT_RUN. This is not a closure of the whole B-9 backlog row.
