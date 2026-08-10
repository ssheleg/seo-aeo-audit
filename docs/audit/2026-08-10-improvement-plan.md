# Improvement plan — seo-aeo-audit, after the 2026-08-10 fresh-eyes audit

Companion to `2026-08-10-defect-ledger.md`. The ledger says what was wrong; this
says what was done about it, what was deliberately not done, and what to build next
so the same classes stop recurring.

**Scope note.** The audit read `v0.11.2`. `v0.12.0` had shipped to `origin/main`
meanwhile, adding a 22nd reference (`discover.md`); it was rebased in and read with
the same lens, which produced two more rows (D42, D43) and one more guard. The
release number is `0.13.0`, not the `0.11.3` the audit was originally cut as — the
correction is recorded at the top of the changelog rather than quietly reused.

Every row names its verification. Where the verification is "prose, read once", the
row says so — that is the honest label, and it is what the board rows exist to
change.

---

## Part 1 — shipped in this pass (v0.13.0)

### Code, each with a failing test written first

| Fix | Defect | What changes for an audit | Verified by |
|---|---|---|---|
| Directives parsed as tokens, not pattern-matched | D1 | `max-image-preview:none` no longer reports a track-A indexation blocker on a page declaring `index, follow`. This was the worst defect in the ledger: SKILL.md makes a track-A blocker a stop condition, so the audit ended there on a fabrication | original repro fixture re-run; four parameter forms and three real-directive forms asserted; UA-prefixed `X-Robots-Tag` both ways |
| Price check reads markup, not bytes | D2 | jQuery's `$` and a correct `Offer.priceCurrency` no longer produce a `high` finding claiming the page hides its price. Correct markup used to trigger the accusation | both repro fixtures; the attribute-borne case still fires; new `jsonld-price-parity` finding for the real observation |
| Truncated reads declare themselves | D3 | The same page produced 10,001 words at the default cap and 475 at `--max-bytes 3000`, silently. Now the flag travels in the payload and the markdown, and every count-based finding is dropped | local server at two caps; `analyze(truncated=True)` asserts the suppression set |
| CrUX presence read from `metrics` | D4 | `preflight.py` decided from a string in a 4 KB prefix of a several-hundred-KB response, and PSI returns that key whether or not data exists. It reported field data that was not there, and explained absence with a cause it never established | pinned to `psi_pull.py`'s answer on the same shapes |
| `CONFIRMED` scoped to answers that arrived | D5 | A run of 403s used to end by declaring its output CONFIRMED — from the one instrument whose justification is that it can claim that tier | all-failed and mixed runs asserted |
| Every non-indexed verdict reported | D5 | The check was a substring test for "not indexed", catching two documented coverage states and silently passing duplicates, canonical alternates, `noindex` and unknown URLs | five exclusion states asserted, two indexed states asserted silent |
| Text format prints what JSON prints | D6 | Four analyses were computed and shown only under `--format json`, while `text` is the default and the documented invocation. The branded split's refusal to guess never reached anybody | `render_text` extracted as a pure function and asserted on all four sections |
| Cliff sensitivity printed | D7 | The detector fires only on a ≥90% drop held 14 days. Its silence read as "no collapse" | asserted in both branches |
| Row limits and noise filtering counted | D8 | The query set is capped with no pagination, dropping the long tail that the beyond-30 band is made of — under a header telling the operator to rank the brief by that band | asserted in the report text |
| Caps in the report body | D9 | The truncation notice went to stderr, under a comment saying a silent cap reads as "this is the whole site" | asserted for capped and uncapped |
| H1 findings re-aimed | D10 | The auditor emitted the "multiple H1s" line its own doctrine calls a non-finding, pointing at a file with no H1 guidance. An agent reading it writes a myth-list recommendation | reference, severity and message asserted |
| `thin` → `low-extractable-text` | D11 | A bare 300-word floor cited a study section that says length barely matters. The threshold had no provenance anywhere in the repo | old code asserted absent, new one asserted present with the disclaimer |
| Subhead check keeps its qualifier | D12 | The doctrine scopes the failure to long pages; the check fired on any page | short page silent, long page fires |
| Every finding carries a tier | D13 | Severity alone reached the agent, and the tier is the multiplier in the triage formula — so the number that orders the plan was invented per finding | three fixtures asserted; validator fails on a finding with no `FINDING_TIERS` entry |
| Read-budget window labelled | D30 | One engine's `FIELD` median presented as the answer-engine first read | finding text and payload asserted |
| Exit code honest | — | A run where every URL failed exited 0 while the docstring promised 1 | asserted |

### Reconciliation guards — eleven, each watched failing on the real repository

The pattern behind all of them: **a guard written against the one home a fact had
drifted in, while the fact lived in four.** Standing instruction #4 says count the
homes; nothing counted them.

| Guard | What it caught on the real tree |
|---|---|
| Myth count, all four homes + both short lists | README's closing pitch said 29, SKILL.md 30, the Cursor rule 29, against 32 rows; the short lists were 14 and 13 items, with the tracking-parameter myth missing from the channel that ships to Cursor |
| Play count | README said 60 against 61 rows, after an earlier correction from 59 |
| Prowl tool count | README ~408 where two references said ~448 |
| Gate commands in every home | CONTRIBUTING named two of four and called CI "the same two"; README the same |
| Per-finding tier coverage | (new invariant; proven by planting) |
| CWV thresholds vs their documented home | (new invariant; proven by planting) |
| Two freshness facts | `algorithm-updates.md` stamped 2026-07-28 while carrying a row dated 2026-07-30 |
| Section-id uniqueness | `D1`, `D2`, `E1`, `E2` each defined twice with different content |
| Table column count | `growth-plays.md` P5 had six cells under a five-column header, so the play governing decline attribution rendered with **no evidence tier** |
| Backticked `references/*.md` pointers | (new invariant; proven by planting) |
| Slash-command doctrine count | The command restated two non-negotiables and read as the list |

Each has a planted-defect step in CI. All twelve pre-existing negative self-tests
were re-run after the code changes and still fail as designed — a changed line
silently disables one, which is its own way of losing a guard.

### Doctrine and provenance

- `tooling.md` caps the tier for **all six** rungs; it used to map three and
  contradict itself inside one sentence, capping a third-party index at `STUDY` and
  "an inference from public data" at `HYPOTHESIS` — a 3.5× priority difference for
  the same evidence (D14).
- `onpage-checks.md` states per starred item what `page_audit.py` does and what is
  still manual; three of eight are cross-page or judgement calls (D15).
- `benchmarks.md` Operational rows name a source or say **undated**; the block had a
  two-column shape with nowhere to put one, in the file whose header says "Always
  cite the date" (D21).
- The PageRank claim is corrected in all three homes: 0.85 is the share modelled as
  *passing*, and read as loss-per-hop it changes three-hop retention from ~61% to
  0.34% (D34).
- A patent no longer asserts live behaviour untiered (D29); three restated figures
  name their source and undated status (D28); ~18 numeric claims across five
  references gain a tier and a date (D31, D32).
- `experience-signals.md` H3 gains a section-level tier statement, and its CWV
  thresholds get their own heading instead of being inserted mid-list (D32, D37).
- Two `myths.md` pointers that pointed at rows that do not exist now point at what
  owns the claim (D38).
- Third deliverable (`docs/seo/experiments.md`) gets a skeleton; the audit template
  gets the evidence-rung slot SKILL.md requires (D39, D40).

### Registers

`CLAUDE.md`, `docs/superpowers/backlog.md` and `docs/superpowers/verification.md`
did not exist; `pipeline.json` sat in the root describing a finished run (D25, D26,
D27). DOCMAP gains nine single-home rows and eight propagation rows; DECISIONS
gains five entries.

---

## Part 2 — the four root causes, and what closes each

The ledger's forty-one rows collapse into four mechanisms. Fixing instances without
fixing the mechanism is how this repository arrived at guards that were green while
the facts they guarded were wrong.

### 1. A guard is written against the home that broke, not against the fact

**Closed by:** the myth, play, Prowl, gate, threshold, freshness, section-id and
table-column guards, each enumerating its homes explicitly in `validate.py`; a
DOCMAP propagation row that says to count the homes first.

**Still open:** nothing enumerates the homes automatically. A new duplicated fact
still needs someone to notice it is duplicated. Board **B-4** is the general form —
a check that reads a diff for new figures and dates.

### 2. Severity is not a tier, and only the tier orders the plan

**Closed by:** `FINDING_TIERS`, the validator guard, the docstring that explains the
mapping, and a DECISIONS entry so the next person does not undo it.

**Still open:** the tier vocabulary itself is too coarse. `FIELD` covers an undated
anecdote and a named multi-account observation, and the formula weights both 0.4.
That is board **B-1**, and it was rejected once on cost — the audit found the cost
of *not* doing it.

### 3. A pointer that resolves is not a pointer that answers

**Closed by:** section-id uniqueness, backticked-filename resolution, the two
corrected `myths.md` pointers.

**Still open, and honestly:** a pointer can name the right file and the claim can be
absent. `validate.py` cannot read prose. DOCMAP marks this **review** with that
reason stated. The mitigation is a habit rather than a check — when you cite a claim
in another file, make the claim findable there.

### 4. An instrument's silence is not marked as silence

**Closed by:** truncation flags, printed caps, printed sensitivity, scoped
`CONFIRMED`, parsed CrUX presence — and a DECISIONS entry generalizing #8 from
*blindness* to *coverage*.

**Still open:** each instrument was fixed individually. There is no shared contract
saying "every collector reports what it did not read". The pattern to extract, if a
seventh script is ever added: a `coverage` block in every payload, with what was
requested, what came back, and what was dropped.

---

## Part 3 — what an agent using the skill will still get wrong

Found during the audit, not fixable by a check, and worth stating because these are
the places where a plausible wrong answer is cheapest.

1. **The evidence rung is now in the template and nothing populates it.** An agent
   will fill it from the tool it used, which is right, but a finding assembled from
   two sources has two rungs and the template has one field. Watch whether reports
   start naming the higher one.
2. **`preflight.py` reads as coverage.** It probes eight things and cannot probe
   Bing, Yandex, analytics, logs, a crawl export or any MCP tool. SKILL.md and the
   command now say so in the same breath as the invocation; the failure mode is an
   agent seeing "8 of 8 sources reachable" and treating step 2 as done.
3. **The prompt set is sampling a non-deterministic surface.** `measurement.md` says
   this well. The risk is a re-audit comparing one run against one run and calling
   the delta a result.
4. **`FIELD` figures read as forecasts in an executive summary.** The corpus is
   careful; the summary is five bullets, and five bullets is where a range becomes a
   number. No check reaches an output file the skill writes in someone else's repo.

---

## Part 4 — next passes, in the order that pays

Priorities are the board's computed values, not a wish order.

| Order | Board | Work | Why now |
|---|---|---|---|
| 1 | **B-4** (4.0) | A date/tier presence check per numeric claim | It is the general form of root cause 1, and it converts R-15 and R-17 in the verification ledger from `never` to `planted`. The sweep this run did by hand is the thing to automate |
| 2 | **B-1** (3.5) | Split `FIELD` into `FIELD` (repeated, named) and `CASE` (single, undated), re-tier the corpus | Root cause 2's remainder. Expensive — every claim in twenty-one files — which is exactly why it needs a decision rather than another deferral |
| 3 | **B-8** (3.0) | Re-read every claim admitted under the old `FIELD` bar | Pairs with B-1; DOCMAP already marks it **review** |
| 4 | **B-5** (2.5) | Decide `gsc_pull.py` pagination | The caveat is honest but the cap still truncates the band the brief is ranked by |
| 5 | **B-2** (2.3) | Wire `graphify` into the harvest | This audit read ~4,000 lines of references by hand to find cross-file contradictions. A graph makes them edges |
| 6 | **B-6** (2.0) | Second-window mode for `gsc_pull.py` | Closes the last gap between the CSV contract and the collector |
| 7 | **B-3** (1.8) | Auto-detect knowledge REQs from the diff | Would retire standing instruction #8 |
| 8 | **B-7** (1.5) | Truncated-gzip fixture | The one uncovered corner of the truncation work |

## Part 5 — what was deliberately not done

- **No new reference file.** The audit found gaps in what existing files claim, not
  missing subject areas. A twenty-second contract would have been read once, which
  is the reason DECISIONS 2026-08-04 rejected one for tool limitations.
- **No change to the tier vocabulary in this pass.** Splitting `FIELD` mid-audit
  would have re-tiered the corpus against a vocabulary the spec fixes as closed,
  inside a run already touching twenty files. It is B-1 with the cost of deferral
  now written down.
- **No reconstruction of the verification ledger for earlier releases.** Rows before
  v0.11.3 would be written from the changelog rather than from evidence, and a
  ledger filled in from memory is the thing it exists to replace.
- **No `.mdc` expansion.** The Cursor channel now carries the fourteenth myth and
  the corrected count. Its compressed glosses are deliberate — a `.mdc` may not link
  out — and the validator checks the two things that actually drifted.
