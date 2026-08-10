# Board

The work-list between runs. Seeded 2026-08-10 during the fresh-eyes audit, which
found that every carry-over recorded on 2026-08-05 existed only in a session that
had ended — there was nowhere for a deferred item to survive.

Priority is computed, not asserted: **`(impact × confidence) / effort`**, the same
formula the skill uses on a client site. `impact` 1–5 on what it costs an audit to
be wrong here; `confidence` 1.0 confirmed defect · 0.7 measured but scoped · 0.4
single observation · 0.2 hypothesis; `effort` 1–5 in engineering days including the
release.

Status: `open` · `in progress` · `done` · `dropped (why)`.

| id | Priority | Item | Why it matters | Source | Status |
|---|---|---|---|---|---|
| B-1 | 3.5 | Re-tier the corpus against a split `FIELD` / `CASE` vocabulary | `DECISIONS.md` 2026-08-05 rejected the split because it meant re-tiering every claim in twenty-one files against a closed vocabulary. The 2026-08-10 audit found the cost of *not* splitting: `FIELD` now covers a single undated anecdote and a named multi-account observation, and the triage formula weights both 0.4 | carry-over 2026-08-05; ledger D31 | open |
| B-2 | 2.3 | Wire `graphify` into the harvest so the next run queries a graph rather than grepping | The pipeline's own doctrine names the code graph as the first thing a harvest queries; this repo has none, so every run re-reads the corpus by hand — this one read ~4,000 lines of references to find contradictions a graph would surface as edges | carry-over 2026-08-05 | open |
| B-3 | 1.8 | Auto-detect knowledge REQs from a diff instead of listing them | Standing instruction #8 exists because the source-admission gate attached to the requirement list and not to the diff. A check that reads the diff for new figures and dates would retire the instruction | carry-over 2026-08-05; retro #8 | open |
| B-4 | 4.0 | A guard that a claim's date is present, per numeric claim | The tier/date sweep in this run was manual across five references. `benchmarks.md` has a source column now; prose claims elsewhere do not, and 36 undated rows were found by a script that could be kept | ledger D31, D32 | open |
| B-5 | 2.5 | Decide whether `gsc_pull.py` should paginate | It caps at the API row limit and now says so. Pagination would remove the caveat but multiplies quota use on large properties, and the beyond-30 band is the one the cap truncates | ledger D8 | open |
| B-6 | 2.0 | A second-window mode for `gsc_pull.py`, for `gsc-historic-<window>` rows | The CSV contract defines the label and the script pulls one window; the workaround (two runs with different `--days`) is documented but manual | ledger D41 | open |
| B-7 | 1.5 | Fixture for a truncated **gzip** response | The truncation flag is proven end-to-end for an uncompressed body and unit-tested for the salvage path; the two are not covered together | ledger D3 | open |
| B-8 | 3.0 | Re-read every claim admitted under the old `FIELD` bar | `DECISIONS.md` 2026-08-05 marks this **review** — no check knows which claims were admitted under which definition of the tier that gates the most admissions | DOCMAP propagation matrix | open |

## How this file is used

Stage 0 of any run reads it and quotes the open count in the brief. Stage 10 gives
every unresolved ledger row a board id here, and re-derives the priorities. A row
that leaves without either a `done` or a stated reason is the thing this file exists
to prevent.
