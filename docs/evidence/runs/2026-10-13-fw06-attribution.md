# FW06 B-33 intended diagnostic attribution — 2026-10-13

Current checkpoint: independent bounded PASS at
`22dc235a0d6d6b05db074c2518e6f46e0fd4d36a`; 93 focused controls and 19 independent
extras pass. Corrected real workflow replays passed all 53 structural and 10
behavioral helper calls. The earlier full owner gate at `4364c48` is retained below
with its exact scope. Normal frozen candidate CI and integration are next; this
receipt does not turn source tests into native/provider or release acceptance.

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

## Source checkpoint

Implementation `557ed7a505cb5a33e21ad30412407950ea63dcf5` preserves the exact
workflow/parser/helper source bound by the generated
[final call inventory](../plans/fw06-attribution-final-inventory.json), including
checker, expected diagnostic and mutation command per identity. Accepted B-9
source `3c3055a9a923f1281943ef54c5e27e9dc9089bb8` was merged normally into the
already published branch; the HANDOFF conflict preserved the newer task history
and accepted coverage receipt. No force/rebase or release version change.

## Owner full gate

`npm run test:all` completed with exit 0 at
`4364c4867d34b05e9e2d0f5e00da53a9b5889106`: the normal documentation/behavior
gate, all 31 workflow negative groups, then eight audit regression files. This
includes coverage 115/115, installer 11, residue 11, FW01 snapshot 3/3, attribution
52 controls and FW06 provenance 14/14. The real 53+10 attributed helper calls also
passed through the full negative run. No failed/broken/skipped negative group was
reported. Routed umbrella trigger comparison remains explicitly unlooked in this
isolated owner checkout. No provider or native observation was added.

## Independent findings corrected

Independent review of `4364c48` reproduced two bounded gaps. First, shlex-unquoted
fields concealed shell-active backticks; declaration validation now preserves quote
state, rejects command/variable expansion in active contexts and permits literal
Markdown backticks inside single quotes. Second, a prior `FAIL:` header left the
matcher armed across a traceback or progress note; only contiguous diagnostic
bullets now belong to that failure section. Both actual workflow shell helpers
refuse the reviewed prior-FAIL/traceback and prior-FAIL/progress counterexamples.

The baseline identity assertion now requires the original set as a subset of the
current unique identities, allowing an additional correctly attributed call while
still refusing omission and duplication. Focused regression replay passes 66
controls. The full gate at `4364c48` remains its historical result; the corrected
helper is undergoing affected group replays before final independent acceptance.
The workflow and all 63 current needle/mutation mappings remain byte-identical to
the source-bound inventory. No general shell interpretation or log authenticity
guarantee is claimed beyond the documented owner grammar.

The stricter matcher then exposed an old mutation's collateral syntax error: the
sitemap missing-producer plant replaced a positional call with a keyword-plus-
positional `dict` call. The compiling replacement now uses `dict(args=argv,
scope=...)`, preserving the intended missing-provenance-call defect. A dedicated
replay executes the exact workflow command, compiles the mutant, and requires the
semantic diagnostic. Focused controls now pass 69/69; the earlier full-suite pass
did not establish this corrected mutant. Affected workflow groups are replayed
again before acceptance. This changes one mutation command and requires the next
source-bound inventory snapshot; the prior inventory remains historical evidence.

Corrected core checkpoint: `b7eaf474f0e59937059a84d911c7d81f135683e7`. The
[reviewed mapping](../plans/fw06-attribution-reviewed-inventory.json) binds all
63 identities, needles, checkers and commands to this source. Corrected structural
group replay passed all 53 calls; corrected behavioral group replay also passed
all 10 calls (exit 0). The subsequent literal-token tightening changes declaration
validation only: its final 93-control suite and structure check pass. Matcher,
workflow commands and needles remain identical to those corrected group replays.


## Independent review — final helper source

Reviewer: `/root/fresh_research`, read-only implementation review at
`22dc235a0d6d6b05db074c2518e6f46e0fd4d36a`.

**Bounded PASS.** Reviewed the migration, parser, matcher, the actual workflow
helper chains and the compiling sitemap mutation. All 63 baseline identities
remain required; new attributed identities may be added, with duplicate identities
still refused. No production collector behavior was changed by this packet.

Independent counterexamples found during review were corrected before this verdict:
active backticks in declared fields, unquoted glob/process substitution and a
prior failure header leaking into later traceback/progress text. Single-quoted
Markdown backticks, escaped literal backticks and quoted punctuation remain valid.
These boundaries describe the documented declaration/output grammar, not arbitrary
shell execution or authenticated logs.

Verification on the final helper source:

- `python3 -B test/audit_regressions/fw06_attribution.py`: exit 0, **93** controls;
  the residue report confirms its one owned temporary tree was removed. This
  replays both actual shell helper chains and the source-level semantic/anchor
  counterexample, including the compiling producer mutation.
- **19** additional independent pure controls: eight dynamic declarations refused,
  five literal declarations accepted, four non-diagnostic section continuations
  refused, and two valid diagnostic formats accepted. The first review's actual
  failing examples are included in these controls.
- No duplicate full suite, live provider call, release or installed-host acceptance
  was performed by the reviewer. The author's earlier broad pass and later
  corrected 53/10 workflow replays retain their separate source bindings above.

The remaining B-33 breadth outside these two migrated groups is not certified by
this receipt. Integration must use the owner's normal CI and release policy.

Final declaration refinement: unquoted wildcard, brace, tilde, process-substitution
and operator characters are refused by a conservative bare-word grammar. Their
quoted/escaped literal forms remain accepted. This is the last parser-only
correction in `22dc235`; it is included in the independent 93+19 control results.
The final workflow retains the same trigger policy and same source-bound 63-call
map. No additional full local run was represented as occurring after the earlier
full pass; genuine candidate CI must run the final repository state.
