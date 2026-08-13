# Spec — the 2026-08 source pass (2026-08-05)

Amends `2026-07-28-seo-aeo-audit-design.md`. That spec defines the skill; this one
defines a single change to it: what a two-week window of practitioner sources is
allowed to add, and the three doctrine defects the pass exposed.

## Problem

The reference corpus was distilled from two Telegram channels up to 2026-07-27.
Three things happened after that date:

1. A new two-week window (`@notjohnmu` 2919–2937, `@MikeBlazerX` 6569–6590) went
   unread, and a third channel (`@MikeBlazerPRO` 414–433) had never been read at
   all.
2. Screening that window against the existing corpus surfaced material that is
   genuinely missing (rendering economics, extractor reliability, an executable
   local-SAB block) alongside material that **contradicts claims the corpus
   already holds with better evidence**.
3. The screening also exposed defects in the skill itself — a check that reports a
   non-finding, a diagnostic naming a field that does not exist, and a tier
   defined twice with two different meanings.

The failure mode this spec exists to prevent: a practitioner retelling entering a
reference as fact because it sounded mechanical and arrived with a number.

## Job

Admit only what survives two gates, fix the three defects, and record the rejected
material so the next pass does not re-litigate it.

**Gate 1 — non-contradiction.** A candidate is checked against every claim the
corpus already makes on that surface. Contradicting a `STUDY` with an
unmethodded practitioner claim is a rejection, not a demotion: `evidence-tiers.md`
rule 3 governs disagreement between two *credible* sources, and an unverifiable
assertion is not the second credible source.

**Gate 2 — evidence.** Every carried number is a lead until a primary source is
read (`docs/superpowers/retro.md`, standing instruction #1). Verified numbers go
to `benchmarks.md` with source and date. Unverified numbers are dropped and the
surrounding mechanism enters without them, or the item goes to carry-over. No
number enters a reference with a hedge attached.

Out of scope: re-tiering the existing corpus; adding a reference file; anything
the rejected list names.

## Decisions this spec locks

### D1. `evidence-tiers.md` is the single home of the tier vocabulary

`CONTRIBUTING.md` defined `FIELD` as "repeated practitioner reports, named" while
`evidence-tiers.md` defined it as "a single practitioner case, one site, no
control". The corpus is written against the second. CONTRIBUTING now quotes the
definitions verbatim and `validate.py` fails when the two copies diverge
(`docs/DOCMAP.md`, propagation matrix; standing instructions #3 and #4).

### D2. Two evidence claims about one mechanism are recorded as two observations

Where the pass produced a second controlled result pointing the same way as an
existing one (carousels on category and store pages), both are recorded with
their own source, and the *direction* is reported as replicated while the
*mechanism* stays `HYPOTHESIS` — the two studies propose different causes.

### D3. A closed, paid channel may be a recorded source, under a stated boundary

Recorded in `docs/DECISIONS.md`. The boundary: facts and mechanics, restated in
this repo's own words, attributed by channel and post id; no quotation, no
reproduction of the source text, and no claim that cannot be stated without it.

## Contracts

### Where each admitted item lands

| REQ | Lands in | Tier after stage 1 |
|---|---|---|
| R1 viewport stretch, one-shot | `technical-checks.md` A1 | **split by the self-audit**: the tall viewport is CONFIRMED and dates to a 2017 engine statement; the once-per-render firing is FIELD, 2026-08 |
| R2 five-second render myth | `myths.md`, `technical-checks.md` A1 | STUDY |
| R3 entity-extractor reliability | `entity-and-brand.md` G3, `tooling.md`, `benchmarks.md` | STUDY (vendor-run, disclosed) |
| R4 carousel tests | `experiments.md`, `architecture-and-equity.md`, `benchmarks.md` | STUDY ×2 |
| R5 desktop 404 / mobile 200 | `technical-checks.md` A1 + A7 sweep | CONFIRMED |
| R6 trust gates indexing | `technical-checks.md` A2 | FIELD |
| R7 generative opt-out ↔ Top Stories in AIO | `algorithm-updates.md` | HYPOTHESIS |
| R8 Alice AI Q2'26 | `benchmarks.md`, quoted by `aeo-geo.md` F4 | CONFIRMED (company report) |
| R9 operator decay | `tooling.md` | HYPOTHESIS |
| R10 review rating vetoes recommendation | `entity-and-brand.md` G4 | HYPOTHESIS |
| R11 pay-to-play listicle footprint | `entity-and-brand.md` G4 | HYPOTHESIS |
| R12 render budget | `technical-checks.md` A1 | mechanism CONFIRMED / thresholds HYPOTHESIS |
| R13 layout position | `experiments.md`, `ranking-model.md` | STUDY (replacement source) |
| R14 multiple H1 | `myths.md` | CONFIRMED |
| R15 service-area local block | `architecture-and-equity.md` | FIELD, no radius figure |
| R16 first-party reviews subfolder | `threats-and-defense.md` I5, `growth-plays.md` | FIELD + guardrail |
| R17 sponsorship links | `linkbuilding.md` | guardrail only, no figures |
| R18 paid-pin call attribution | `demand-and-conversion.md` | FIELD |
| R19 GSC → grounding validation loop | `measurement.md` J3 | FIELD (method) |
| R20 trend timing, on-site UGC | `intent-and-content.md` | FIELD |
| R21–R25 detection rows | `threats-and-defense.md` I4/I6 | detect-only |

### Invariants the build must not break

1. **No recommendation may contradict `myths.md`.** Specifically: nothing in R13
   may instruct the reader to structure a page *for the retriever's chunking* —
   `myths.md` holds that chunk boundaries are the engine's choice.
2. **R10 must separate mention from recommendation.** `entity-and-brand.md` G4
   already records that badly-rated brands surface *more* than mediocre ones. A
   rating claim that does not name which of the three outcomes it affects
   contradicts it.
3. **R1 and R12 must agree on one rendering model.** The source for R12 asserts
   Googlebot renders the initial viewport and stops; R1's primary shows a
   one-shot stretch to full initial height. R1 wins; R12's sentence is struck.
4. **R12 must not reintroduce `rel=next`/`rel=prev`.** `technical-checks.md`
   already records that it is unsupported and must not be "fixed" back in.
5. **Every dated number carries source and date, and lives in `benchmarks.md`**;
   other files quote it (`docs/DOCMAP.md`).
6. **Detection material never appears as a recommendation** (`CONTRIBUTING.md`).

### The reconciler contract (D1)

`validate.py` gains one check: the four tier definitions in
`references/evidence-tiers.md` and the four in `CONTRIBUTING.md` must match
string-for-string after normalization. Failure message names both files and the
diverging tier. The check must be observed failing against a deliberately
edited copy before it is trusted (standing instruction #2).

## Module cut

This is a change, not a platform, so the modules are commit boundaries rather
than independently shippable bricks. No two modules write the same file.

| Module | Files | REQs |
|---|---|---|
| M1 doctrine | `evidence-tiers.md`, `CONTRIBUTING.md`, `test/validate.py`, `docs/DOCMAP.md`, `onpage-checks.md` | R26, R28 |
| M2 rendering | `technical-checks.md`, `myths.md` | R1, R2, R5, R6, R12, R14, R27 |
| M3 answer engines | `entity-and-brand.md`, `tooling.md`, `measurement.md` | R3, R9, R10, R11, R19 |
| M4 content and risk | `experiments.md`, `architecture-and-equity.md`, `ranking-model.md`, `linkbuilding.md`, `demand-and-conversion.md`, `intent-and-content.md`, `growth-plays.md`, `threats-and-defense.md` | R4, R13, R15, R16, R17, R18, R20, R21–R25 |
| M5 numbers | `benchmarks.md`, `algorithm-updates.md` | R7, R8, and every figure from M2–M4 |
| M6 record | `docs/research/`, `docs/DECISIONS.md`, `README.md`, `CHANGELOG.md` | R29, R30 |
| M7 release | four manifests, tag, `sshlg-skills` pin | R32 |

M1 first: it changes what a tier *means*, and every other module writes tiers.
M5 after M2–M4, because it collects their figures.

## Definition of done

`scripts/check-docs.sh` green; the new reconciler observed failing on a broken
tree and passing on the real one; every REQ row above present in its file with a
tier; no figure without a source and date; the rejected list recorded; v0.11.0
published and the family catalogue pin moved.
