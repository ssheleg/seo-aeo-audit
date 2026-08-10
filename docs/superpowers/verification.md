# Verification ledger

One row per shipped requirement, and the honest answer to "has anyone watched this
work?" Seeded 2026-08-10, because the repository had no place to record the
difference between *tested* and *confirmed against reality*, and that difference is
what the whole skill is about.

`Confirmed` values:

- **`observed`** — someone ran it against real input and read the result.
- **`planted`** — a guard was watched failing against a deliberately broken tree, so
  it is known to be able to fail.
- **`test-only`** — a test passes; nobody has seen the failure mode it defends
  against, or seen it work on real data.
- **`never`** — shipped, unconfirmed. Not a bug, but not evidence either.

A green check nobody has watched fail is `test-only` at best. That is the rule
standing instruction #2 encodes, written down as a column.

## v0.11.3 — 2026-08-10 fresh-eyes audit

| REQ | What shipped | Confirmed | Evidence |
|---|---|---|---|
| R-1 | `page_audit.py` no longer reads `max-image-preview:none` as `noindex` | **observed** | the original repro fixture re-run: `noindex = False` where it was `True`, and the fabricated track-A blocker is gone |
| R-2 | jQuery `$` and `Offer.priceCurrency` no longer produce `price-not-in-text` | **observed** | both repro fixtures re-run: `currency_in_source_only = False`; the JSON-LD case now emits `jsonld-price-parity` instead |
| R-3 | A truncated read reports itself and suppresses count-based findings | **observed** | same page over a local server at `--max-bytes 5000000` and `3000`: `truncated` False/True, findings `[canonical-missing, subheads-thin, description-missing]` vs `[truncated-read]` |
| R-4 | `preflight.py` decides CrUX presence from `metrics`, agreeing with `psi_pull.py` | **test-only** | unit-tested on both response shapes and pinned to psi_pull's answer; not yet run against a live PSI response for a no-CrUX URL |
| R-5 | `url_inspection.py` claims CONFIRMED only for rows the index answered | **test-only** | asserted for an all-failed run and a mixed run; no live 403 run since the change |
| R-6 | `url_inspection.py` reports every non-indexed verdict, not two coverage strings | **test-only** | five documented exclusion states asserted, plus two indexed states asserted silent; API shape not re-verified live |
| R-7 | `gsc_pull.py --format text` prints the four derivations JSON had | **test-only** | `render_text` asserted on a fixture report; no live property run since the change |
| R-8 | The cliff detector states its sensitivity when it finds nothing | **test-only** | asserted in `render_text`; the detector's positive path is asserted on a synthetic 99% drop |
| R-9 | `sitemap_audit.py` puts the cap in the markdown body | **test-only** | asserted for a capped and an uncapped analysis |
| R-10 | Every script finding carries an evidence tier | **planted** + **observed** | three fixtures asserted; validator guard watched failing with a tier entry deleted |
| R-11 | The myth count reconciles across all four homes | **planted** + **observed** | watched failing on the real repository (three homes wrong), then per-home planted defects in CI |
| R-12 | Play count, Prowl count, gate commands, CWV thresholds, freshness, section ids, table columns, backticked pointers | **planted** + **observed** | each watched failing on the real repository before the fact was corrected; each has a planted-defect step in CI |
| R-13 | The slash command carries all eight non-negotiables and is count-checked | **planted** | guard watched failing with non-negotiable #8 removed from the command |
| R-14 | `tooling.md` caps the tier for all six rungs with no self-contradiction | **never** | prose; no check can read it. Re-read on the next audit that assigns a tier to a rung-3 or rung-6 finding |
| R-15 | `benchmarks.md` Operational rows name a source or say **undated** | **never** | prose and judgement; DOCMAP already marks sourcing as **review** |
| R-16 | The corrected PageRank statement in three homes | **never** | prose. The claim is now stated as the damping factor with the inversion named; nothing checks that it stays stated that way |
| R-17 | Tier and date added to ~18 numeric claims across five references | **never** | prose. B-4 on the board is the check that would make this `planted` |
| R-18 | `CLAUDE.md`, the board and this ledger exist | **observed** | the files are in the tree; their value is only proven by the next run reading them, which is R-19 |
| R-19 | The next run's stage 0 quotes this ledger's `never` count | **never** | by construction — it can only be confirmed by a later run |

**Counts at ship: 4 observed · 6 test-only · 4 planted+observed · 6 never.**

Six `never` rows are all prose, and the honest reading is that this release fixed
the machine-checkable half well and the prose half on inspection alone. B-4 on the
board is the item that would move R-15 and R-17.

## Earlier releases

Not reconstructed. Rows before v0.11.3 would be written from the changelog rather
than from evidence, and a ledger filled in from memory is the thing it exists to
replace. Releases from v0.11.3 forward get a row each.
