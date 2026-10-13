# FW06 B-33 intended diagnostic attribution — 2026-10-13

The preserved [packet](../plans/2026-10-13-fw06-guard-attribution.md) and
[baseline inventory](../plans/fw06-attribution-inventory.json) identify 63 helper
calls: 33 anonymous structural calls, 20 existing named calls and 10 anonymous
behavioral calls. Historical board counts remain a dated observation, not the
current denominator. Implementation converts every identity to `plantq` with an
explicit diagnostic; behavior calls retain their checker. Workflow trigger policy,
shared `plant_guard.py`, residue implementation and `negatives.py` are unchanged.

## Failure reproduced and correction

The table-width selector's unescaped regex alternation matched an unrelated
heading once with no target row. The workflow now uses existing literal
`plant_edit.py sub`; an unrelated file exits nonzero with `PLANT DID NOT LAND`
and retains exact original bytes, while the real row changes.

The real source counterexample changes the SKILL myth count, then disables only
its semantic branch in a task-owned copy. The validator still exits nonzero via
anchor-liveness. The old helper would accept this; the new matcher refuses because
the intended semantic diagnostic is absent. Restoring that branch produces the
expected diagnostic. This is an executed source counterexample, not a toy model.

`test/plant_attribution.py` accepts only failure rows from the three actual owner
checker output formats. Success messages, progress notes, traceback echoes and
unrelated failure rows cannot satisfy the needle. The shell still requires nonzero
exit and `plant_guard.py` still requires a landed content/mode mutation.
The bounded call reader requires literal description/needle declarations in the
two existing helper groups, refuses anonymous/dynamic/empty/duplicate declarations,
and preserves the original identity set in the audit regression. The workflow is
the sole current home of mutation commands and needles. Standalone negative steps
outside these two groups are not certified by this migration.

## Checks actually observed

- `python3 -B test/audit_regressions/fw06_attribution.py`: PASS, 52 controls;
  owned fixture removed on success. An initial test harness attempt selected two
  identically worded semantic branches; it refused before execution. The selector
  was narrowed to the exact indentation and its sole occurrence, and the inspected
  failed fixture was removed explicitly.
- `python3 -B test/validate.py`: exit 0; 25 references, unchanged SKILL body
  4685 tokens and 325 lines. Routed trigger comparison is explicitly unlooked in
  this isolated owner checkout, which has no umbrella parent.
- `python3 -B test/negatives.py -k reconciliation`: exit 0, one workflow
  group with all 53 named structural calls completing; no failed/broken case.
- `python3 -B test/negatives.py -k 'provenance behaviour'`: exit 0, one workflow
  group with all 10 named behavioral calls completing; no failed/broken case.
  Each helper verifies a landed mutation, nonzero checker exit and intended
  diagnostic. The runner removes its owned snapshot on success.
- Both actual workflow shell helpers were extracted and executed over tiny
  controlled checker fixtures: intended nonzero failure passes; unrelated failure,
  success even with a diagnostic, and a no-op mutation refuse. These are part of
  the 52 focused controls, alongside the real semantic-guard-disabled source case.

Next: read every migrated refusal through the two real workflow groups, independent
review, complete owner gates, then deliberate frozen PR promotion and normal merge.
Keep package 0.26.5 until combined coverage/attribution corrections are accepted for
separate next patch packaging. No provider, browser, installed-host or native model
acceptance is claimed by source or mutation tests.
