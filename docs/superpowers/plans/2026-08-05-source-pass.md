# Plan — the 2026-08 source pass

Spec: `docs/superpowers/specs/2026-08-05-source-pass-design.md`.
Branch: `feat/2026-08-source-pass`. Gate after every module:
`bash scripts/check-docs.sh`.

## M1 — doctrine (do first: it changes what a tier means)

1. `references/evidence-tiers.md` — state that this table is the single home of
   the tier vocabulary and that `CONTRIBUTING.md` quotes it under a validator
   check. No definition text changes.
2. `CONTRIBUTING.md` — replace the paraphrased tier table with the four
   definitions verbatim from `evidence-tiers.md`.
3. `test/validate.py` — extract the four `| **TIER** | definition |` rows from
   both files, normalize whitespace and markdown emphasis, fail naming both files
   and the diverging tier.
4. Prove it fails: edit a copy of `CONTRIBUTING.md` in a scratch tree, run the
   validator, confirm the failure message, restore.
5. `docs/DOCMAP.md` — single-home row for the tier vocabulary, propagation row
   for "edit a tier definition".
6. `references/onpage-checks.md` D1 — the H1 row stops reporting "several H1s" as
   a crawler-understanding failure; the check survives as document structure and
   accessibility, with the engine statement named. (R26)

Commit: `fix(doctrine): one home for the tier vocabulary, and the H1 row stops
reporting a non-finding`.

## M2 — rendering and indexation (`technical-checks.md`, `myths.md`)

7. A1 — rendering block: two-pass model; the render queue as a separate budget;
   the one-shot viewport stretch and its two consequences (sequential infinite
   scroll, unconstrained hero); the executable diagnostic (Last crawl date +
   `View crawled page` rendered HTML vs source, live test for the current state);
   thresholds explicitly `HYPOTHESIS`. Strike nothing that already exists; do not
   write `rel=next`/`rel=prev`. (R1, R12, R27)
8. A1 — mobile-first status divergence: desktop 404 with mobile 200, and the
   single internal link as the surviving discovery path. (R5)
9. A7 sweep — add the mobile-UA status check row. (R5)
10. A2 — trust gates indexing on a new domain, pointing at the existing
    `myths.md` row rather than restating it. (R6)
11. `myths.md` — two rows: the five-second render limit, and multiple H1s. (R2, R14)

Commit: `feat(technical-checks): the render budget, the one-shot viewport, and
two myths that cost audit findings`.

## M3 — answer engines (`entity-and-brand.md`, `tooling.md`, `measurement.md`)

12. G3 — extractor reliability: false-positive and precision ranges, the
    determinism split, the validation rule against Google's own blocks, vendor
    disclosure. (R3)
13. G4 — rating as a recommendation-stage input, explicitly scoped against the
    existing "bad ratings surface more" finding; pay-to-play listicle footprint
    as a placement risk. (R10, R11)
14. `tooling.md` — operator decay and anti-automation friction, both readings
    named. (R9)
15. `measurement.md` J3 — the GSC generative report → grounding validation loop,
    with the candidate-prompts-are-hypotheses caveat. (R19)

Commit: `feat(aeo): extractor reliability, rating as a recommendation input, and
a validation loop for AI-surface prompts`.

## M4 — content, local, links, risk

16. `experiments.md` — the two carousel results and the tabs/above-fold result,
    as hypotheses with sources. (R4, R13)
17. `architecture-and-equity.md` — internal-link intent (commercial links on a
    local page), and the service-area block. (R4, R15)
18. `ranking-model.md` — layout section gains the controlled evidence, and the
    B2B page-type counterweight; no chunking instruction. (R13)
19. `linkbuilding.md` — sponsorship guardrail. (R17)
20. `demand-and-conversion.md` — paid-pin call attribution. (R18)
21. `intent-and-content.md` — trend timing and on-site UGC. (R20)
22. `growth-plays.md` + `threats-and-defense.md` I5 — first-party reviews
    subfolder with the gating guardrail. (R16)
23. `threats-and-defense.md` I4/I6 — five detection entries. (R21–R25)

Commit: `feat(references): local service areas, link guardrails, and five
detection patterns`.

## M5 — numbers (`benchmarks.md`, `algorithm-updates.md`)

24. Every figure introduced by M2–M4 gets its row with source and date; the
    Alice AI rows move to Q2'26 with the Q1 figure retained as the prior point.
25. `algorithm-updates.md` — the opt-out ↔ Top Stories-in-AIO row. (R7, R8)

Commit: `docs(benchmarks): the Q2 figures this pass verified`.

## M6 — record

26. `docs/research/2026-07-source-distillation.md` — PART G: the new window, the
    channels, the post ids, **and the rejected list with its reason per item**.
27. `docs/DECISIONS.md` — two entries: the tier home, and the closed-source
    boundary.
28. `README.md` / `CHANGELOG.md` — behaviour-visible changes.

Commit: `docs(research): the 2026-08 window, including what was refused`.

## M7 — release

29. Four-way version bump to 0.11.0, CHANGELOG section, tag, push; CI publishes.
30. `sshlg-skills`: bump this member's pin and the launcher's own version, tag,
    push; verify with `npx --yes sshlg-skills@latest list`.
31. Refresh local installs; confirm no shadow copies.
