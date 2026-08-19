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


## Unreleased — the coverage vocabulary (conformance row SE-01)

**Not shipped, and — see the note at the end of this section — not committed either.** No version was bumped, no tag pushed, no CHANGELOG section written:
in this repository the changelog entry is a release artifact, and a section under
`v0.22.0` would claim this was in a package that is already on npm. The rows below
are what the gate and the plants confirmed on the working tree.

The defect was unusual in shape and worth recording as such: **the instruments could
already tell a clean result from a check that never looked, and the deliverable could
not.** `url_inspection.py:236-250` grants CONFIRMED only to the N of M URLs the index
answered for; `page_audit.py:94-110,924-925` drops every absence and count finding on
a truncated read; `gsc_pull.py:524-527` ships `row_limit_reached`; `preflight.py`'s
`_unattempted_property` keeps its own denominator fixed. The report skeleton then
offered a free-text `Status` column and a free-text "Not checked" table, with no
check reading either.

| REQ | What shipped | Confirmed | Evidence |
|---|---|---|---|
| The coverage `Status` column is a closed vocabulary with one home | `COVERAGE_STATUS` in `preflight.py`; `validate_coverage()` is its only reader | **planted** + **observed** | the guard fired on the real repository first — every one of the ten rows in both skeleton homes had a blank Status, and none of the five values was published anywhere. CI plant `a coverage status outside the closed vocabulary` was watched failing with `checked` in row E, naming the enum |
| A blank Status cell is an error, not an unread cell | `validate_coverage()` refuses it by name | **planted** | CI plant `a blank Status cell — the defect this vocabulary replaced`; the refusal names the row and lists the five legal values |
| The denominator is every track `SKILL.md` declares | the table is generated from `TRACKS`, reconciled against the step-2 table | **planted** + **observed** | `SKILL.md:151` declared track K and the skeleton stopped at J, in both homes — found by the guard on its first run, and the findings block offered `{{A–J}}` for the same reason. Two plants: the K row dropped, and `("K", "agent surface")` removed from `TRACKS` |
| The table is seeded by the instruments, not typed | `preflight.py --format coverage`, and `coverage` / `tracks` / `coverage_status` in the `--format json` payload | **observed** (offline) | run against stubbed probes — no network — with robots.txt 503 and no ADC: A and K read `blocked-by http`, D and J `blocked-by login` with the gate the preflight table names, the rest `unlooked`. Output read as a client would read it, which is how the note bug below was found |
| The seed can never write `observed` | `coverage_seed()` emits only `unlooked` and `blocked-by <gate>` | **test-only** | asserted in `test_output_contracts.py`. This is the property that makes forgetting safe: a row nobody edits says *nobody looked*, so the failure mode of omission is the honest state rather than the clean one |
| A `blocked-by` row may only name a gate this skill emits | `COVERAGE_GATES`, reconciled by reading every `probe(...)` argument **and** every assignment to a local `gate`, with `ast` | **planted** + **observed** | the first version read `probe()`'s arguments only and was watched **under-reporting on the real tree**: `check_gsc` classifies into a local `gate` before calling `probe`, so deleting `api-not-enabled` from the tuple left the validator green while the probe still emitted it — a coverage row naming that gate would have been refused as unknown. Two plants now, one per shape: a direct literal (`unattempted`) and one through the variable (`api-not-enabled`). Renaming `render()`'s `gate` local to `gate_note` was part of the fix — a rendering fragment was answering a question about the vocabulary |
| A track that can never be seeded `blocked-by` is refused | `validate.py` requires a `TRACK_SOURCES` entry for every track in `TRACKS` | **planted** | a missing key and an empty tuple behave identically at runtime and mean opposite things — the same "absence indistinguishable from a state" shape one level down. Track G declares `()` on purpose; the plant deletes track K's key and the refusal names it |
| A `blocked-by` note is true on every row that rests on the source | `coverage_seed` reads the probe's `detail`, not its `blocks` | **observed** | the first version put *"crawl-directive checks (track A)"* in track **K**'s row — a sentence about the wrong track in a client document. Found by reading the output, not by a test; standing instruction #9 |
| Both skeleton homes carry it, byte for byte | `templates/audit-report.template.md` and `references/deliverable-templates.md` | **planted** | the pre-existing template-drift guard; the three skeleton plants edit **both** homes on purpose, so it is the coverage guard that fires and not the drift check |
| Every negative self-test still fails as designed after the code changes | the whole set, re-run locally | **observed** | extracted from `validate.yml` with `yaml.safe_load` and run under bash: **44 behaved as designed, 0 did not** — 23 standalone steps plus 21 `plant()` calls, of which 7 are new. Counted by parsing the workflow, not carried over: this file's own history is a release whose notes said 71 fixtures, whose acceptance record said 74, and whose count was 75 |
| `SKILL.md` carries no pointer, and that was measured | the pointer lives in `deliverable-templates.md` and `preflight.md` | **observed** | `audit_skill.py --house`: the four-line Step 4 addition moved the body from 4994 to **5107** tokens against a 5000 budget, so it was reverted and the body is unchanged. Filed as B-19 — the remedy v0.22.0 named is a split, not a trim |
| The gate is green | `npm test` | **observed** | exit 0; `PASS: output contracts (… coverage vocabulary closed and seeded)` |

**Counts, by parsing the table above: 12 rows — 5 observed · 3 planted · 3 planted+observed · 1 test-only.**

**Uncommitted, and the reason is not this change.** The umbrella wires a `PreToolUse`
gate (`hooks/repo-gate.js`) that runs `npm test` before any `git commit`. It decides
whether a commit belongs to the umbrella by asking whether the umbrella has anything
staged — and on 2026-08-19 it did, from a concurrent row of the same conformance
program. So a commit inside this submodule was judged by the umbrella's suite, which
is red because five *sibling* submodules hold local-only commits, every one of them
under the same "commit locally, do not push" instruction. `seo-aeo-audit` holds none,
and its own gate — the one `docs/DOCMAP.md` names — exits 0. The hook's docstring
predicts this exact deadlock. Not routed around: the work is staged in this
submodule's index, green, and waiting for an umbrella index that is not this row's to
clear. The one
`test-only` row is the never-writes-`observed` property: it is asserted, and nobody has
yet watched an auditor fill this table in on a live engagement.

## v0.22.0 — the Cloudflare row, and a body 18% over budget

| REQ | What shipped | Confirmed | Evidence |
|---|---|---|---|
| The Cloudflare rows state the 2026-09-15 default and the multi-purpose rule | read inside the **published** tarball, not the working tree | `npm pack @ssheleg/seo-aeo-audit@0.21.0` → `grep -c 2026-09-15` returns 3 in `algorithm-updates.md`, 2 in `technical-checks.md` | 2026-08-16 |
| `OAI-AdsBot` is in the inventory and not in the retrieval bucket | same tarball | `grep -c oai-adsbot` → 2 in the shipped `agent_surface.py` | 2026-08-16 |
| The vendor facts were read, not restated | WebFetch of Meta's dedup page and OpenAI's bots page, and of the Cloudflare coverage | both `event_id` **and** `event_name`, 48-hour window; `OAI-AdsBot/1.0` with no stated robots.txt behaviour | 2026-08-16 |
| The body is inside the 5000 budget | `audit_skill.py --house` | 5885 → **4996 tokens**; still 246 over the 4750 house limit, and the ledger says so rather than rounding | 2026-08-17 |
| Every reference on disk is declared, both directions | planted an undeclared `references/*.md`; then a declared file with no counterpart | both refused | 2026-08-16 |
| The release shipped after three refusals | `npm view`; CI on the fourth tag | `0.22.0`; `release: completed success`. The first three were correct refusals — two stale plants and one guard looking where the invocations used to be | 2026-08-17 |

## v0.14.1 — 2026-08-10 acceptance walk

| REQ | What shipped | Confirmed | Evidence |
|---|---|---|---|
| R-34 | Every runnable invocation resolves, in all three homes | **observed** + **planted** | the walk found eight bare invocations in the README and one in the slash command after `v0.14.0` guarded `SKILL.md` alone; the CI self-test now plants the defect in each home and each was watched failing |

## v0.14.0 — 2026-08-10 agent-usage audit

The lens this time was the agent's path from invocation to report, not the
repository's internal consistency. Every row below names how it was confirmed, and
the two `never` rows say plainly that no check reads them.

| REQ | What shipped | Confirmed | Evidence |
|---|---|---|---|
| R-22 | Every `SKILL.md` invocation resolves through `$SKILL_DIR` | **observed** + **planted** | the documented command was run from a simulated project root and failed eleven times out of eleven before the change; the validator guard was watched failing with one path reverted |
| R-23 | `url_inspection.py` exits 1 when the index answered for no URL | **observed** + **planted** | live run against a property this account cannot see: exit was 0, now 1; CI self-test plants `return 0` |
| R-24 | `psi_pull.py` exits 1 when every call was refused | **observed** | live rate-limited run: exit was 0, now 1, with the report unchanged |
| R-25 | No renderer interpolates a network error into markdown unflattened | **observed** + **planted** | the live preflight that produced 11 stray lines and lost 2 of 7 rows now renders 8 well-formed rows; self-test plants the raw interpolation back |
| R-26 | `preflight.py`'s coverage denominator does not shrink on failure | **observed** | same live run: headline moved from "3 of 7" to "3 of 8" and the named property is reported `not attempted` |
| R-27 | `SECURITY.md` matches the bundle's measured I/O surface | **observed** | the per-script table was generated by measuring, not asserted; the doc's own grep prints 22 lines and six `open()` calls, all counted |
| R-28 | The gate's commands reconcile across five homes | **observed** + **planted** | the guard fired on the real repository the moment a fifth test file was added, naming CONTRIBUTING, README and CI; the PR template is now the fifth home |
| R-29 | `templates/` carries the third deliverable skeleton | **planted** | extracted from the reference so the drift check compares byte-for-byte; the template-drift self-test covers it |
| R-30 | The 2026-08-10 defect total reconciles against the ledger's rows | **observed** + **planted** | five of six homes were wrong on the real tree, including the ledger's own summary sentence; self-test plants `forty-one` back |
| R-31 | The Cursor channel names the six instruments and their blind spots | **never** | prose. The validator checks the channel carries the doctrine; nothing checks that a blind spot described there is the one the script actually has |
| R-32 | `page_audit.py --format json` documents its array shape | **never** | prose, in two homes. The shape itself is covered by the behaviour tests; the *documentation* of it is not |
| R-33 | All 17 negative self-tests still fail as designed after the code changes | **observed** | every one executed locally against its planted defect: 17 behaved as designed, 0 did not |

## v0.13.0 — 2026-08-10 fresh-eyes audit

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
| R-20 | Discover is reachable from the audit flow, not only from the reference list | **observed** | `SKILL.md` step 2 names it as an eleventh pass with an entry condition; the file was previously listed at line 359 and in no track |
| R-21 | The reference count is checked in all five prose homes | **planted** + **observed** | caught `v0.12.0`'s five stale counts on the merged tree; planted defect in CI |

**Counts at ship: 5 observed · 6 test-only · 5 planted+observed · 6 never.**

Six `never` rows are all prose, and the honest reading is that this release fixed
the machine-checkable half well and the prose half on inspection alone. B-4 on the
board is the item that would move R-15 and R-17.

## Earlier releases

Not reconstructed. Rows before v0.13.0 would be written from the changelog rather
than from evidence, and a ledger filled in from memory is the thing it exists to
replace. Releases from v0.13.0 forward get a row each.
