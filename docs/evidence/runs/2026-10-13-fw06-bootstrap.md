# FW06 B1 — bootstrap reports and known versus unknown inputs

Baseline: typed-admission source `ce6d4df1e2f787683ed33c9752d6c185f5f0054e`.
The parent accepted the B1 [source-aware packet](../plans/2026-10-13-fw06-bootstrap-transport.md)
before implementation. T1/T2 source acceptance is recorded in their linked receipts.

## Completed mapping

- Page keeps its JSON array. Local open/decode failures and list-resolution errors
  have typed `input_error` rows, so neither a blank label nor array cardinality
  invents an observed page. Local file failure is one attempted file; unreadable
  list population is unknown with zero URL attempts. Successful rows stay unchanged.
- PSI preserves explicit duplicates; Inspection deduplicates/caps the known prefix.
  A failed optional list never erases those inputs. Unknown total requested/dropped
  stays null, even when known explicit inputs succeed or have known exclusions.
- Inspection/GSC ADC acquisition rejects empty tokens, has a 20-second timeout,
  withholds private stderr, and reports unavailable prerequisites. Known inputs/API
  operations are excluded before attempt. Inspection rows name unattempted URLs;
  GSC records six known operations while provider row populations stay unknown.
- GSC `--list` is explicit, with a one-operation JSON/text report. Typed empty
  listing succeeds; malformed-only listing does not, while valid siblings survive.
  Omitting both `--site` and `--list` is usage before ADC or network, not an implicit
  list. README, script usage and references describe this observable behavior.
- Parsed no-input sitemap/PSI/preflight paths emit zero partial records. Preflight
  runs no local or network prerequisites and leaves track statuses unlooked.
  Parser/help and GSC missing-site usage remain named non-collection boundaries.

## Red baseline and fixture isolation correction

Initial bootstrap controls exited1. That first fixture had an isolation defect:
its Inspection network method was mocked, but the first list loop did not mock ADC.
An indented-comment file was treated as a URL by old code, so local gcloud could be
invoked before the denied provider-collection method. Captured diagnostics/tokens
were never printed. This run **does not prove zero credential subprocesses or zero
credential-acquisition network activity**. It could not make an Inspection collection
call through the mocked method. The parent was notified immediately; the owned run
had already exited when inspected.

The loop was corrected with explicit fake ADC and rerun: 29 evaluated controls
failed as expected on old source. The final harness additionally denies subprocess
and provider transport at the **outer entry to every main invocation**, with explicit
fixture overrides only. Copied CLI subprocesses use an owned fake gcloud and a
`sitecustomize` guard denying every HTTP entry point before scripts import. These
final assertions establish zero collection HTTP calls; they do not rewrite the first run.

## Checks actually run

- `python3 -B test/bootstrap_contract.py`: 87 controls PASS, including default/JSON,
  missing/empty/invalid-UTF8 lists, explicit-prefix preservation, dedup/cap/ADC
  intersections, list-mode typing, process timeout/private diagnostics and one
  executable false-known-population mutant.
- The 87 include sixteen copied standalone CLI subprocesses across eight scenarios,
  guarded from HTTP, with exactly six expected fake ADC calls. Each emits the
  expected denominator and preserves the documented carrier.
- Updated GSC focused suite: 76 PASS. Its historical early-bootstrap/list assertions
  now check the accepted report contract and explicit-list success; API/row semantics
  and previous nonfinite controls remain.
- Structural validation initially caught the I/O grep count changing 33→37 due to
  additional timeout/bootstrap exception branches. The published breakdown was
  reconciled from the code, not waived. Structural and diff-check final results
  both passed at freeze (entry 4685/5000 tokens, 325/500 lines).

Temporary trees use the owner residue ledger. Failed fixture trees were retained
until logs were read, then only those named owned paths were removed. Final passes
report cleanup. No foreign state or credential configuration was modified.

Independent B1 source review: pending. One composed owner full gate and normal
eligible PR admission/merge remain next, before packaging 0.26.6. B-9 stays open
until final acceptance; live provider/native/model quality remains NOT_RUN.
