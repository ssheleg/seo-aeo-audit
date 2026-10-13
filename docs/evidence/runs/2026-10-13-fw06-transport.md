# FW06 T1 — bounded transport across seven collectors

Source baseline: packet `76818f2dedeef0d1d5e9d2d47e451d46f534582e`, stacked on
preflight `9d9b16690c7df4e058c9d237d1a18ad8a0784633`. The parent accepted the
[contract packet](../plans/2026-10-13-fw06-bootstrap-transport.md) before production
implementation. This receipt covers T1 only; T2/B1 and composed acceptance remain open.

## Red evidence and correction

`python3 -B test/transport_contract.py` first exercised125 loopback controls and
exited1 with46 admission gaps. The original twelve observations remain in the
[immutable baseline snapshot](../plans/2026-10-13-fw06-transport-baseline.json).
Seven duplicated, parity-checked reader blocks now bound raw/gzip output, validate
all framing fields and contain body-read failure. Provider adapters bound JSON and
error responses at8,000,000 bytes and redact known credentials before truncation.
Page retains its tuple/array surface, agent/preflight status survives, sitemap
requires a complete document, and incomplete provider JSON cannot become zero rows.

The first existing page test replay failed2 assertions. One encoded the previous
raw-only gzip budget and was revised to require both raw and decoded fit, with a
new decoded-overflow negative. The other found a genuine regression: a corrupt
empty gzip became empty partial HTML. The adapter now fails that fetch while
preserving complete empty gzip and nonempty recovered prefixes. Its corrected
existing behavior suite passes. Neither failure is omitted from this receipt.

The expanded transport test first failed one environment-dependent expectation:
this Python decoder successfully parsed1500 nesting levels. The control now
injects a decoder capacity error and verifies its conversion to a reportable
payload error; it makes no universal claim that1500 levels must fail.

## Checks actually run

- Transport source acceptance:144 controls PASS, actual loopback framing, gzip
  bounds, caps, error-body redaction/read failure; copied standalone helper calls,
  ASCII/comma/zero length cases and two executable mutants.
- Existing `test/test_page_audit.py`: PASS after the documented correction; HTML
  fixtures, default/JSON, scheme/headers/gzip/list/error and partial finding behavior.
- Preflight82 controls PASS after adopting the common byte reader; its distinct
  observed-status semantics and prior duplicate-length correction remain covered.
- `python3 -B test/validate.py`: PASS; skill entry4685/5000 tokens,325/500 lines.
- Documentation structural replay initially caught the reference-line rounded count
  crossing6100→6200 (actual6155); README was reconciled from the measured count.
- `git diff --check`: PASS. No workflow, version, dependency or entry-description change.

Every scratch directory came through the owner residue ledger. Failed owned
fixtures were retained until their log/diffs were read, then removed explicitly;
passing checks reported automatic cleanup. Other sessions' data was not touched.
Logs are local convenience copies; commands, controls and this report are tracked.

Independent T1 review: pending. Aggregate full gate/eligible PR/merge: pending for
the coherent composed wave. Provider/live/native effectiveness: NOT_RUN.
