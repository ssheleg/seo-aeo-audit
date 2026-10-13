# URL Inspection typed admission source notes

Companion to [the transport/bootstrap packet](2026-10-13-fw06-bootstrap-transport.md).
This is the policy used by the bounded T2 implementation; source acceptance is
recorded separately in [its receipt](../runs/2026-10-13-fw06-inspection-payload.md).
The bounded red controls are in
`test/inspection_payload_contract.py`; baseline57 controls failed on current source.

Primary source checked 2026-10-13: Google's
[UrlInspectionResult reference](https://developers.google.com/webmaster-tools/v1/urlInspection.index/UrlInspectionResult),
page update2025-01-21. The `IndexStatusInspectionResult` and `RichResultsInspectionResult`
sections declare the field names and JSON types; enum sections supply status domains.
The timestamp field specifies an RFC3339 UTC value with up to nine fractional digits.
The absence rule for crawl time applies to an actual index observation, not to an
arbitrary/malformed object that happened to contain `indexStatusResult`.

The collector's conservative admission policy is an implementation choice:

- Envelopes must be objects. Recognized enums must be declared values; an unknown
  future enum remains a payload limitation, never a fetch failure or indexing verdict.
- Nonempty `coverageState` is free text. Canonical/referring/sitemap fields must
  contain absolute HTTP(S) URLs with valid parseable authorities; malformed values
  are unavailable fields. List members are validated independently, preserving
  usable siblings. This URL admission is stricter than a JSON string type alone.
- Timestamp text must match the documented UTC form and a valid calendar time.
  Its malformed presence is distinct from valid absence, so it must suppress the
  missing-crawl finding. Malformed `userCanonical` similarly cannot establish that
  the page omitted its canonical declaration.
- A recognized meaningful index field admits one answer. Unknown-only fields,
  unspecified enums alone and empty arrays do not establish a usable answer.
  Rich-result observations alone do not establish index status.
- Record payload errors as field paths and type/domain failures, without dumping
  arbitrary provider values. Keep valid typed siblings and report a partial
  collection reason even if that URL supplied one usable answer. Findings only
  consult the admitted values; the report's confidence footer applies to those
  fields, not to rejected siblings.

Tests include actual `main` JSON/default rendering with malformed rows followed by
a valid row and a valid row with one malformed field. They must preserve the
result count, single answer predicate, provider/error distinction and diagnostics.
Provider access remains NOT_RUN.
