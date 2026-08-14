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
| B-9 | 1.5 | A shared `coverage` contract every collector emits — requested / returned / dropped | Six instruments were each taught honesty separately: `_flat` has four copies, the "did anything arrive" predicate two, the exit semantics four. Nothing states the contract, so a seventh script starts from zero and the copies are only held together by a count in `validate.py` | v0.13.0 plan root cause 4; v0.14.0 M1 | open |
| B-10 | 0.7 | Make the code graph's incremental mode usable in this repo | `detect_incremental` reports 72 of 72 files changed against either root, so `--update` cannot tell what moved; and re-extracting a file gives its entities new ids, which orphaned a hyperedge and pushed dangling endpoints from 6.3% to 10.3% between two builds one day apart. A graph that degrades each refresh is a false premise carrying a machine's authority | 2026-08-10 stage 9 | open |
| B-11 | 5.0 | `agent_traffic.py` — parse a server-log export, count AI/agent user agents, forward-confirm reverse DNS to drop spoofers | Track K tells the auditor to size agent demand before paying for agent surfaces, and hands them no instrument. Two live audits have now hit the same ceiling: every effect claim in K stays `HYPOTHESIS`, so the Experiments bucket cannot be ranked and the client is asked to buy files on faith. The highest-value missing tool in the skill | 2026-08-14 privateclawd §5, §8; 2026-08-14 gap doc A1 | open |
| B-12 | 2.0 | Extend the near-miss probe past root agent files | `agent-file-misnamed` catches `/llm.txt` standing in for `/llms.txt`. The same one-character class exists under `/.well-known/` and is unprobed, so a misnamed agent card still reports as plain absence — and absence sends the team to write a file they already have | 2026-08-14 privateclawd §7 | open |
| B-13 | 2.5 | `openapi_provenance` should ask whether the documented paths answer | It reads `servers[]` and template fingerprints, which catches the sample-spec case. A spec that genuinely describes this product's API but was never deployed passes every check, and the agent generating tools from it fails at call time rather than at read time | 2026-08-14 privateclawd §7 | open |
| B-14 | 3.0 | An instrument for a price restated in a flat agent file | `page_audit.py` has `jsonld-price-parity` for a page and now compares declared FAQ answers against the served body. A price restated in `llms.txt` has no instrument at all — the live case (a 30% annual discount the site's own tables put at 17%, in three places, on the surface built for machines) was found by reading, which does not scale | 2026-08-14 privateclawd §4.4 | open |
| B-15 | 2.0 | Detect a CDN-managed robots block that contradicts the origin for a **named** agent | `robots-contradictory` fires on duplicate `User-agent: *` records and disagreeing `Content-Signal` lines. The commoner shape — a managed block allowing what the origin disallows for one named crawler, or the reverse — is not detected, and it is the shape that silently reverses a decision somebody made on purpose | 2026-08-14 privateclawd §4.2 | open |

## How this file is used

Stage 0 of any run reads it and quotes the open count in the brief. Stage 10 gives
every unresolved ledger row a board id here, and re-derives the priorities. A row
that leaves without either a `done` or a stated reason is the thing this file exists
to prevent.
