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


## Unreleased — the documents were measured against the tree (conformance row SE-03)

**Not shipped.** No version bumped, no tag, no CHANGELOG section: the orchestrator
releases. **This heading becomes `## vX.Y.Z` in the release that ships it**, and
`validate.py` refuses a CHANGELOG release with no section here — which is the mechanism
the two sections below did not have, and why they were still saying "Not shipped" after
the tag.

The defect was one class in eleven places: **a number or a pointer stated in a document,
with nothing recomputing it.** The gate was green through all of them. Eight of the
eleven were a fact with two or more homes and no reconciler (standing instruction #4);
three were a command or an address quoted as runnable that does not resolve.

Every guard below was watched failing **on the real repository before its plant was
written** — the guard was added, the gate went red naming the defect, the document was
then corrected. That order matters: a guard written after the fix has only ever been
seen passing.

| REQ | What shipped | Confirmed | Evidence |
|---|---|---|---|
| The bundled-script count is measured in all four of its documents | the `I/O surface` guard now reads `README.md` and `CLAUDE.md` too, count **and** names | **planted** + **observed** | B-25 fixed `SECURITY.md` and `SKILL.md` and stopped there. The README said "Text plus **six** standard-library Python scripts" and divided six of the seven by role — `agent_surface.py` in neither list — and `CLAUDE.md:10` said six: the two files a reader opens first. The guard named both on its first run; three plants, one per claim |
| The gate's commands have a home list, and the documents that count it agree | `_GATE_HOMES` — six homes beside `check-docs.sh` — and DOCMAP's two home counts read out of the file | **planted** + **observed** | `CLAUDE.md` and `docs/DOCMAP.md` each published **five of the gate's seven** commands, missing `plant_guard_test.py` and `test_agent_surface.py`, and DOCMAP said "It runs exactly these and nothing else" over the shorter list. The count of homes had three values at once: that row said three, the propagation matrix said five, the checker read four. Four refusals on the first run; three plants |
| `_flat()`'s copies are counted, not described | DOCMAP row: "five of the seven scripts define one" | **planted** + **observed** | it read "one copy per script, five in all" — two claims in one breath against seven scripts, while `preflight.py:184-186` said the true version out loud in a comment. One plant |
| The ledger cannot fall behind a release | the newest `## v` in `CHANGELOG.md` must have a section here, and the releases that have none are a declared, counted list | **planted** + **observed** | two sections were headed `## Unreleased` and `## 2026-08-19` and opened "**Not shipped.**" for work that is in v0.23.0, tagged on HEAD — and there was no `v0.23.0` section at all. Sixteen of the twenty-one releases at or above the ledger's own floor have none; they are declared rather than backfilled, because backfilling from the changelog is what the closing paragraph refuses. Three plants |
| A section's tally is parsed out of its own Confirmed column | the tally guard, over every section with three or more classified rows | **planted** + **observed** | the v0.13.0 line said `5 observed · 6 test-only · 5 planted+observed · 6 never` — twenty-two against twenty-one rows, one planted+observed too many, one `never` too many, and R-13's `planted` row missing from the vocabulary; the prose under it then reasoned from the wrong number. v0.14.0 had twelve classified rows and no tally at all. Two plants |
| A board id the prose calls closed reads `done` on the board | the `board status` guard, over eight documents | **planted** + **observed** | `SECURITY.md:23` credited its own repair to **B-17** and dated that closure 2026-08-19. B-17 is **open** and is about comparing a third-party manifest's number against the site's; the row that closed it is B-25, which `CONTRIBUTING.md:109` cites correctly. Three of this repository's own guard comments carried the same wrong id. The guard also refuses a `B-nn` that resolves to no row; two plants |
| `SECURITY.md`'s `os.environ` line count is explained by what the code does | "one line per script", with the loop cited | **observed** | the row said "one read per producer field per script", which is 3 × 7 = 21 against the seven lines the grep prints. `preflight.py:161-163` is a single `for … in PRODUCER_ENV` loop per script. The totals were already guarded and were right; the sentence explaining them was not, and no guard reads an explanation |
| The run stamps are derived from tags and cannot fall behind | the `run stamps` guard: newest stamp ≥ `plugin.json`, live instructions counted from the headings | **planted** + **observed** | the stamps stopped at `v0.14.1`, **eighteen** releases behind HEAD, in the file every run is told to read first — so "no firing in five run stamps" was uncomputable. The prune log's arithmetic was wrong the other way: "all eleven checked" and "the list stands at **eleven** — one over the cap" against **ten** live instructions (twelve numbered, #5 and #6 struck through), and B-28 restated it. Two plants |
| `SKILL.md`'s body budget is measured in this repository | `len(body) / 3.9` vendored into `validate.py`; the gate prints it | **planted** + **observed** | three ledger rows and B-27 rested on `audit_skill.py --house`, which is `make-skill`'s script and is not in this tree — a reader handed that command gets `No such file or directory`, and the four numbers it produced were unreproducible here. The gate now prints `SKILL.md body ~4994/5000 tokens / 330/500 lines`, reproducing the figure B-27 was filed on. Over budget fails; past the 4750 house limit prints a note, because that state is filed. One plant |
| The README's freshness stamp and corpus size are computed | both compared to their sources by the gate | **planted** + **observed** | the Data-freshness bullet said "**Verified as of 2026-08-10**" while `algorithm-updates.md:3` — the single home of that fact — said the sources were last re-fetched 2026-08-16, so the staleness claim was itself six days stale. "Roughly 5,000 lines" against **6,977 total / 5,917 non-blank**; the README now states the rounded non-blank figure and says it is rounded, because the exact count was deleted once for moving on every edit. Two plants |
| `gsc_pull.py` can say it measured nothing | `measured_rows()`, one predicate for the report and the exit status | **planted** + **observed** | `main()` had three `return 0` paths and no `return 1`, and the docstring said only "0 = ran" — so a property that answered zero rows for every dimension printed a full report finding no cliff, no cannibalization and no CTR gap, and exited **success**. Every derivation below the position split is row-driven, so that document reads like a clean site. Run offline with `query` stubbed to `[]`: exit **1** in both formats and `NOTHING MEASURED` first in the report; with rows, exit 0 and no banner. The no-`--site` path returned 0 while printing a property list and now exits 1, which its docstring had always promised. Two plants |
| A run says what it left on disk | `test/residue.py`, **copied** from `make-skill` and the umbrella, with the prefix and the measurement changed | **planted** + **observed** | four suites built temp trees and removed none — `plant_guard_test.py:34` one per case across nine cases, plus `test_output_contracts.py:309`, `test_page_audit.py:240` and `test_collectors.py:128` — and no line of output said so, which is the half that let it run for months. Measured here: `find "$TMPDIR" -maxdepth 4 -type f -path '*/copy/sub/b.sh' \| wc -l` → **2560**, `find "$TMPDIR" -maxdepth 2 -type d -name 'tmp*' \| wc -l` → **28343**, `du -sh "$TMPDIR"` → **7.0G**. This repository was the **last of four** shipping the fixture byte-identical (md5 `623a086d10a04940573c31cbebb93e31`); `make-skill` closed its copy 2026-08-19, the umbrella on 2026-08-20. Every gate command now prints one line — `residue: this run left nothing — N temp tree(s) created, N removed` — on every path. Three plants |
| The pile that already exists is reported and left in place | B-34, `dropped (not ours to sweep)` | **observed** | the 2560 trees are plain `tmpXXXXXXXX`: nameless, and produced by a fixture four repositories ship identically, so none of them can prove the trees are its own. Sweeping state you cannot prove you own is what `manifesto.md:366` refuses, so the count is published and the directories are untouched. The `seo-aeo-audit-test-` prefix makes everything created after today attributable by name — the eighteen trees this session's own plant sweeps left were removed on that basis, and only on that basis |
| A failing case keeps its tree, and a planted run does not poison the shared box | `residue.open_case`/`close_case` per suite; `plant`, `plantq` and all 22 standalone negative steps run their copy with a `$TMPDIR` of its own | **planted** + **observed** | a plant is debugged by reading the tree it landed in, so cleanup on the pass path only deletes the evidence when somebody wants it. That collides with the ledger's last case, which reads the `$TMPDIR` the gate shares: **eighteen** ledger-prefixed trees were sitting there after one local plant sweep, every one of them kept exactly as designed. The negative steps now box their own residue, and the case was re-run after a full sweep — 63 plants, then `bash scripts/check-docs.sh` exit 0 and zero prefixed trees in the shared box |
| The manifesto citation resolves to the sentence it quotes | `manifesto.md:210` | **observed** | two documents cited `manifesto.md:206-208` for "the proof should identify the execution that produced it"; `:206-208` is the "Three gate types" paragraph and the sentence is at `:210`, confirmed by reading the file. CLAUDE.md rule 3: a pointer that resolves is not a pointer that answers |
| A plant that passes for the wrong reason is refused | `plantq` — the refusal must NAME the defect | **observed** | measured while writing this change: the anchor-liveness guard fires on *any* literal-anchored document plant, because the literal the workflow names is no longer in the file. So `plant`, which asks only "does the validator fail", cannot tell the intended guard from that one — and it reported `ok` for a run-stamp plant that lowered one stamp of several while the guard, which takes the newest, correctly did not fire. The nineteen new plants require the message; the 41 older calls are left as they are and the weakness is filed as B-33 |
| Every negative self-test behaves as designed | the whole set, extracted from `validate.yml` and re-run | **observed** | parsed with `yaml.safe_load` and run under bash from the repo root: **63 plants behaved as designed, 0 did not** — 44 `plant` and 19 `plantq` calls across 36 of the workflow's 38 runnable steps; the two skipped need `npm install -g` or `pip install`. Counted by parsing the workflow, not carried over: this file's own history is a release whose notes said 71 fixtures, whose record said 74, and whose count was 75 |
| The gate is green | `bash scripts/check-docs.sh` | **observed** | exit 0, and `PASS: seo-aeo-audit structure valid (1 cursor rule(s), 25 reference(s), SKILL.md body ~4994/5000 tokens / 330/500 lines)` |

**Counts, by parsing the table above: 18 rows — 6 observed · 12 planted+observed.**

**Not confirmed.** Nothing here was watched from the outside: every one of these guards
reads this repository's own documents, so the failure mode they cannot see is a document
that is internally consistent and wrong about the world. Three of them — the run stamps,
the ledger's release coverage and the declared unrecorded list — are satisfiable by
adding a line to a list, which is a weaker bar than recomputing a number, and it is the
strongest bar available without writing sixteen ledger sections from memory. And nothing
here was run on Linux: the residue ledger and the boxed negative steps are exercised on
macOS only, and `$TMPDIR` is a per-user directory there and `/tmp` on the CI runner —
which is the platform split that made eleven `sed -i` plants dead for two days. B-30,
B-31, B-32 and B-33 are what this run found and did not close; B-34 is what it found and
deliberately left alone.

## v0.25.0 — the plan is ordered on axes, not on a product (2026-08-24)

**Shipped in v0.25.0.** Written before the tag, the only order that works.

| REQ | What shipped | How it was confirmed | Confirmed |
|---|---|---|---|
| R-75 | `priority = (impact × confidence) / effort` removed from every live surface — `SKILL.md`, the command, `deliverable-templates.md`, `myths.md`, `README.md`, `CLAUDE.md`, `templates/audit-report.template.md` and `agent_surface.py`'s printed output | eight sites found by `grep -rn 'impact × confidence'`; after the change the same grep returns only CHANGELOG history, `docs/` records and the paragraph that names the removal. The count matters: the register row said four, and it said four because the earlier sweep grepped `plugins/` alone | **observed** |
| R-76 | Four axes declared machine-readably and swept by a gate — `check_the_plan_is_ordered_on_axes_and_not_a_product`, ported from `agent-stack` | watched failing against **two** plants: a composed priority put back into `SKILL.md`, and `irreversibility` swapped for `effort` in the declaration. Equality, not subset — an axis that is not one of the manifesto's four is as wrong as one missing | **planted** + **observed** |
| R-77 | The tier weights became an `Uncertainty rank` and stopped being restated in `SKILL.md` | the weights existed *as the confidence multiplier*; with the product gone, a check requiring the reference's table to also appear in `SKILL.md` was enforcing the two-homes defect this pack polices elsewhere. Single-home check kept, restatement dropped, reason recorded in the code | **observed** |
| R-78 | A negative self-test re-anchored from a literal to a shape | recounting `~5,900 non-blank lines` to `6,000` would have silently disarmed the plant pinned to the old literal — standing instruction #6, caught by this repository's own plant-integrity guard rather than by reading. `resub` on the number's shape | **planted** + **observed** |
| R-79 | `SKILL_VERSION` bumped in all seven collectors with the manifests | the gate refuses a producer block naming a version that never ran; 7 of 7 moved in this commit | **observed** |

**Counts at ship: 5 rows — 3 observed · 2 planted+observed.**


## v0.24.0 — eleven documented facts recomputed (2026-08-20)

**Shipped in v0.24.0.** This section exists because the guard added in the same release
demands it: the newest `## v` in `CHANGELOG.md` must have a section here, so a release can
no longer ship unrecorded. It was written before the tag, which is the only order that
works — the tag cannot exist before the commit that bumps to it.

| REQ | What shipped | How it was confirmed | Confirmed |
|---|---|---|---|
| R-70 | Eleven false statements in shipped documents, each replaced by a computed one | `bash scripts/check-docs.sh` → exit 0, `PASS: seo-aeo-audit structure valid (1 cursor rule(s), 25 reference(s), SKILL.md body ~4994/5000 tokens / 330/500 lines)`; the guards were added first and the first run named eleven defects at once | **planted** + **observed** |
| R-71 | 63 plants extracted from `validate.yml` and run under bash | 63 behaved as designed, 0 did not, across 36 of 38 runnable steps | **observed** |
| R-72 | `test/residue.py` copied from the umbrella; every gate command prints its residue | `PASS: residue — 8 cases`, `residue: this run left nothing — 5 temp tree(s) created, 5 removed`; the pre-existing pile (2560 trees, 28343 dirs, 7.0G) counted and left in place | **planted** + **observed** |
| R-74 | The plant proving "a release with no ledger section is refused" stopped pinning a version | it named `## v0.23.0 — the coverage vocabulary` and stopped landing the moment v0.24.0 shipped: the validator still failed, for other guards, and the plant read as one that had been watched. CI refused **after** the tag was public. `test/plant_newest_section.py` reads the newest release from `CHANGELOG.md`, the same fact the guard reads, and exits 1 saying `PLANT DID NOT LAND` when there is nothing to plant | **planted** + **observed** |
| R-73 | `gsc_pull.py` can say "measured nothing" | `measured_rows()` serves both the report and the exit status; a run with no `--site` exits 1 where it used to exit 0 | **planted** |

**Counts at ship: 5 rows — 1 observed · 1 planted · 3 planted+observed.**

## v0.23.0 — the coverage vocabulary (conformance row SE-01)

**Shipped in v0.23.0.** `git tag --points-at HEAD` prints `v0.23.0`, and the changelog's
v0.23.0 section carries this work under *"The report could not separate `pass` from
`never looked`"*. **Corrected 2026-08-20:** this section was headed `## Unreleased` and
opened *"Not shipped, and … not committed either"* — true of the working tree it was
written against, and left standing across the release that shipped it, which is exactly
the perishability the ledger exists to catch and had no check for. `test/validate.py`
now refuses a CHANGELOG release with no section here.

*As written 2026-08-19, and kept because the reasoning is why there was no changelog
section **at that time**:* "No version was bumped, no tag pushed, no CHANGELOG section
written: in this repository the changelog entry is a release artifact, and a section
under `v0.22.0` would claim this was in a package that is already on npm. The rows below
are what the gate and the plants confirmed on the working tree."

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
| `SKILL.md` carries no pointer, and that was measured | the pointer lives in `deliverable-templates.md` and `preflight.md` | **observed** | measured with `make-skill`'s `audit_skill.py --house`, which does **not** ship in this tree — its `len(body) / 3.9` estimator is vendored into `test/validate.py` since 2026-08-20, so the figure is reproducible here by `python3 test/validate.py`. The four-line Step 4 addition moved the body from 4994 to **5107** tokens against a 5000 budget, so it was reverted and the body is unchanged. Filed as B-27 — the remedy v0.22.0 named is a split, not a trim |
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

## v0.23.0 — provenance in every payload (conformance row SE-02)

**Shipped in v0.23.0**, the second half of the same release — the changelog carries it
under *"No output could say which run produced it"*. **Corrected 2026-08-20:** this
section was headed `## 2026-08-19` and opened *"Not shipped."*, for the same reason and
with the same defect as the section above: a state true in a working tree, restated as
fact after the tag.

*As written 2026-08-19:* "No version bumped, no tag, no CHANGELOG release section: the
changelog entry here is a release artifact, and a section under `v0.22.0` would claim
this was in a package already on npm. The rows below are what the gate and the plants
confirmed on the working tree, committed locally."

**A correction to the section above, appended rather than edited** (that is what
`docs/AGENT_SYNC.md` prescribes, and the ledger's own perishability is SE-03's row):
SE-01's block says it was "not committed either". It was — `265dfa5`. The umbrella
index cleared after that note was written.

The defect: **no output carried provenance.**
`grep -n "__version__\|observed_at\|timestamp" scripts/*.py` returned nothing across
all seven scripts, and the report skeleton had no producer block. So a deliverable
could not say when it was produced, by what version, or against what arguments — in
the family's **most perishable** evidence. A crawl result expires the moment the site
or the algorithm moves, and a three-month-old audit was indistinguishable from
today's. M-32 (`manifesto.md:210`, re-resolved 2026-08-20 — the citation read
`:206-208`, which is the "Three gate types" paragraph) asks the proof to identify the
execution behind it; M-08 asks every proof to be scoped, versioned and perishable.

| REQ | What shipped | Confirmed | Evidence |
|---|---|---|---|
| Every `--format json` payload carries a `producer` block | one per object payload; one per **array element** for `page_audit.py`, whose array shape is a documented contract (`page_audit.py:17`) that `jq '.[].url'` depends on | **observed** (offline) | all seven driven through both formats in `test_output_contracts.py` against stubbed probes and `.invalid` hosts — no network. `producer` is the first key of every object payload and present on every array element, and its keys equal `PRODUCER_FIELDS` in order |
| The field set is closed and has one home | `PRODUCER_FIELDS` in `preflight.py`; `validate_provenance()` is its only reader | **planted** | CI plant `observed_at dropped from the closed field set` edits all seven copies and the validator names the missing field. The same shape SE-01 gave `COVERAGE_STATUS`, deliberately — a second mechanism beside it would be two vocabularies for one report |
| Nothing is guessed to look complete | `actor` · `model` · `trace` read `SEO_AEO_AUDIT_ACTOR` / `_MODEL` / `_TRACE` and otherwise print `unavailable: <VAR> is not set by this harness` | **planted** + **observed** | run with all three unset (the normal case) and with `SEO_AEO_AUDIT_ACTOR=agent-42`, so the field is proven to report *and* to resolve. CI plant `a harness-owned field guessed instead of reported unavailable` replaces the sentence with a literal id and the contract test names each of the three. **`model` is never inferred** — the wrong vendor id sends an investigation to a model that never ran, which is worse than saying nothing |
| A field is never deleted when unavailable | every field in `PRODUCER_FIELDS` prints on every run | **planted** | a field that vanishes when unavailable is indistinguishable from one nobody checked. `validate_provenance` refuses a blank value cell and a missing row; both are planted |
| `observed_at` is a UTC timestamp, not free text | `time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())`, and the checker matches the shape | **planted** | two plants: the field removed, and rewritten as `"recently"`. This is the field the whole row turns on — without it nothing can say the report has expired |
| The audit is scoped to its RESOLVED inputs, not its flags | `scope`, computed per script: the URL set, the property and its windows, the sitemap sources, the local file | **observed** | `--urls-file urls.txt` names a file nobody can reconstruct later, so `scope` carries the URLs. Read on all seven: `2 URL(s) from 1 sitemap(s): /tmp/sm.xml`, `property sc-domain:e.com · recent 2026-05-19..2026-08-17 · history 2025-04-24..2026-08-17`, `local file test/fixtures/good-page.html as https://e.com/x` |
| A credential on the command line never reaches the block | `SECRET_FLAGS` + `redact()`; both `--key V` and `--key=V` | **planted** + **observed** | `psi_pull.py --key SUPERSECRET` was run in both formats and the string appears in neither. CI plant `a --key value echoed into the producer block` swaps `redact(argv)` for `list(argv)`. A producer block ends up in a deliverable somebody emails, and handling one spelling is the same as handling neither |
| The block reaches the DEFAULT format, not only JSON | `provenance_md()` in the shared block; every renderer prints it | **planted** + **observed** | **the guard was watched under-reporting first.** Asserting `provenance_md` *exists* left the suite green when the print was deleted from a renderer, because nothing ran a default-format `main()` and read its output. Now all seven are driven through their default format and the output is read; the plant deletes one `print` line and is named. `gsc_pull.py` is where this rule was learned — four of its analyses were JSON-only while `text` is the documented invocation |
| The emitter is one function, not seven | the shared block is copied verbatim into all seven scripts and compared **byte for byte** | **planted** | a copy rather than an import because `bin/seo-aeo-audit.js` installs `scripts/` alone into `~/.claude/skills/` — there is nothing to import from. Same reasoning as `_flat`'s five homes. CI plant `the shared block edited in one copy only` changes `SECRET_FLAGS` in `gsc_pull.py` and the diff is named against the reference copy |
| Every script calls it under its own name | `validate.py` requires `provenance("<its own file>", …)` in each | **planted** | two plants: the call removed, and `agent_surface.py` stamping `preflight.py`. A payload carrying another script's name is worse than an unstamped one, and a shared block nobody invokes passes every structural check |
| `SKILL_VERSION` cannot name a version that never ran | seven literals, each held equal to `plugin.json` | **planted** | a runtime manifest lookup is impossible in the installed layout, so the price is seven more homes for one semver and a guard that names each file that disagrees. CI plant drops all seven to `0.19.0`. `DOCMAP.md` and `CONTRIBUTING.md` both record that a release bumps them with the manifests |
| The report says what would expire it | `INVALIDATORS` — `site` · `index` · `instrument` · `policy` — in both skeletons and the seeded block | **planted** | `task-pipeline`'s verification-ledger shape (code / dependency / environment / policy) mapped onto this domain rather than redesigned; the mapping table is in `preflight.py` above `INVALIDATORS`. Invalidation is not deletion: an overtaken audit is true about the site it observed and stays. Plant drops the `policy` row from both skeletons |
| The block is seeded, never typed | `preflight.py --format provenance`, carried in both skeleton homes | **planted** + **observed** | run: exits 0 and probes nothing, because the block is about the execution and making a caller wait on a PageSpeed round trip is how a seeding step gets skipped. Plants: the command removed from both skeletons, and a field name dropped from the list they publish |
| Both skeleton homes carry it, byte for byte | `templates/audit-report.template.md` and `references/deliverable-templates.md` | **planted** | the three skeleton plants edit **both** homes on purpose, so the provenance guard fires rather than the pre-existing template-drift check |
| B-25: `SECURITY.md`'s counted claims are measured | script count in five sentences, one row per script, and the "prints **N** lines" claim | **planted** + **observed** | measured on the tree: **seven scripts and 26 grep lines** against a stated six and 22 — pre-existing and identical at HEAD, as filed. Now seven and **33**, because the published pattern also had to match `os.environ` (which the producer block reads) or the "whole surface" sentence would be true of a smaller pattern than it named. The regex is read **out of** `SECURITY.md` and run, so narrowing it breaks the count it claims — four plants |
| B-25's neighbour: `SKILL.md` named a script that has never existed | the inventory paragraph said `sitemap_pull.py`; the file is `sitemap_audit.py` | **planted** + **observed** | found while counting for B-25. The guard reads the inventory sentence both ways — a name that does not ship, and a script the paragraph omits. re-measured after the rename with the same estimator, now vendored (`python3 test/validate.py` prints it): body unchanged at **4994** tokens, so B-27's six tokens of headroom are intact and nothing was added to `SKILL.md` |
| The `sed -i` self-test measures a call in COMMAND POSITION | `_sed_call` widened to `do` / `then` / `else` / `{`; the plant anchors on the last line-initial call site | **observed** | found by running the whole extracted set: SE-02's new plants moved the last `plant_edit.py sub` inside a `for … ; do …; done`, the guard did not read that as a command position, and the step reported a **healthy guard as broken**. Both halves fixed — the guard genuinely missed a live shape, and the step's "last occurrence" assumption is now stated as what it needs |
| `plant_edit.py sub` accepts a count from a shell | `count = int(count)` | **observed** | a numeric count arrives as a string and `str.replace` refuses it, which this file reported as *"wrong number of arguments"* — sending the reader to the argv instead of the type. Two SE-02 plants need the count, and both were dead until this was fixed |
| Every negative self-test still behaves as designed | the whole set, extracted from `validate.yml` and re-run | **observed** | parsed with `yaml.safe_load` and run under bash: **64 behaved as designed, 0 did not** — 39 `plant()` calls (18 new) plus 25 standalone steps. Counted by parsing the workflow, not carried over: this file's own history is a release whose notes said 71 fixtures, whose record said 74, and whose count was 75 |
| The gate is green | `npm test` | **observed** | exit 0; `PASS: output contracts (… provenance in all 7 collectors — closed field set, nothing guessed, credentials redacted, default format included, checker refuses six ways to lie)` |

**Counts, by parsing the table above: 20 rows — 6 observed · 8 planted · 6 planted+observed.** Counted, not carried: the first draft of this line said 19 / 7 / 8 / 4 and every number was wrong, which is the defect `CLAUDE.md`'s Evidence section exists for.

**Not confirmed.** No provenance block has been read by a client on a live engagement,
so nothing says the four invalidators are the four an auditor actually reaches for.
`actor`, `model` and `trace` have never been exported by a real harness — the
resolve-from-environment path is exercised with a fabricated value in a test, and no
harness on this machine sets `SEO_AEO_AUDIT_*`. And `observed_at` is the moment the
payload was emitted, not the moment each URL was fetched: on a long `--url-list` crawl
those differ by the length of the run, which the docstring says out loud rather than
implying a precision it does not have.

## v0.22.0 — the Cloudflare row, and a body 18% over budget

This section predates the `Confirmed` vocabulary above: its third column holds the
command that was run, not one of the four values. The header is named for what the cells
are rather than left claiming a column this section never filled in — filed as B-30.

| REQ | What shipped | Evidence | When |
|---|---|---|---|
| The Cloudflare rows state the 2026-09-15 default and the multi-purpose rule | read inside the **published** tarball, not the working tree | `npm pack @ssheleg/seo-aeo-audit@0.21.0` → `grep -c 2026-09-15` returns 3 in `algorithm-updates.md`, 2 in `technical-checks.md` | 2026-08-16 |
| `OAI-AdsBot` is in the inventory and not in the retrieval bucket | same tarball | `grep -c oai-adsbot` → 2 in the shipped `agent_surface.py` | 2026-08-16 |
| The vendor facts were read, not restated | WebFetch of Meta's dedup page and OpenAI's bots page, and of the Cloudflare coverage | both `event_id` **and** `event_name`, 48-hour window; `OAI-AdsBot/1.0` with no stated robots.txt behaviour | 2026-08-16 |
| The body is inside the 5000 budget | `make-skill`'s `audit_skill.py --house` — not vendored at the time, so unreproducible from this repository until the estimator was brought into `test/validate.py` on 2026-08-20 | 5885 → **4996 tokens**; still 246 over the 4750 house limit, and the ledger says so rather than rounding | 2026-08-17 |
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

**Counts, by parsing the table above: 12 rows — 4 observed · 5 planted+observed · 1 planted · 2 never.** Added 2026-08-20; this section shipped with no tally at all, which is
the state that let the section below carry a wrong one for eight releases.

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

**Counts, by parsing the table above: 21 rows — 5 observed · 6 test-only · 4 planted+observed · 1 planted · 5 never.** Recounted 2026-08-20. The line said
`5 observed · 6 test-only · 5 planted+observed · 6 never` — twenty-two against
twenty-one rows, one planted+observed too many, one `never` too many, and R-13's
`planted` row missing from the vocabulary entirely. `validate.py` parses the Confirmed
column of every section here and compares it with the stated tally, so this cannot be a
number somebody carried over again.

Of the five `never` rows, four are prose (R-14, R-15, R-16, R-17) and R-19 is `never` by
construction — only a later run can confirm it. The honest reading stands: this release
fixed the machine-checkable half well and the prose half on inspection alone. B-4 on the
board is the item that would move R-15 and R-17.

## Earlier releases

Not reconstructed. Rows before v0.13.0 would be written from the changelog rather
than from evidence, and a ledger filled in from memory is the thing it exists to
replace. Releases from v0.13.0 forward get a row each.

## Releases at or above the floor with no section here

That policy was a sentence with nothing reading it, and the sentence lost.
**Sixteen** of the twenty-three releases at or above `v0.13.0` have no section
above — declared here and
counted by `test/validate.py` against `CHANGELOG.md`, rather than absent and invisible.
They are **not** backfilled: writing them now would be writing them from the changelog,
which is what the paragraph above refuses. What the guard does enforce is the half that
can be enforced going forward — the newest release in `CHANGELOG.md` must have a section
here, so a release can no longer ship unrecorded, and a release that leaves this list
must leave it by gaining a section.

<!-- unrecorded-releases:start -->
- `v0.21.0`
- `v0.20.2`
- `v0.20.1`
- `v0.20.0`
- `v0.19.1`
- `v0.19.0`
- `v0.18.0`
- `v0.17.1`
- `v0.17.0`
- `v0.16.3`
- `v0.16.2`
- `v0.16.1`
- `v0.16.0`
- `v0.15.2`
- `v0.15.1`
- `v0.15.0`
<!-- unrecorded-releases:end -->
