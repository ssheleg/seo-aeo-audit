# Decision register

One entry per decision that is expensive to reverse. Newest last.

## 2026-08-04 — Seed the documentation registers

**Decision.** Create `docs/DOCMAP.md` (single-home table + propagation matrix)
and this register, and gate them with `scripts/check-docs.sh`.

**Why.** Two drifts had already shipped: `cursor/rules/*.mdc` carried five
non-negotiables where SKILL.md carried seven, and the reference count was stated
as nineteen in CONTRIBUTING while the validator enforced twenty-one. Both are the
same failure — a fact with more than one home and nothing reconciling them. This
is the register's first entry, which is also the record of its own seeding.

## 2026-08-04 — Instruments declare their own blind spots (non-negotiable #8)

**Decision.** Add an eighth non-negotiable, and enforce it with script checks
rather than prose: `page_audit.py` ships a JS-blindness caveat in every report,
`measurement.md` carries the GA4 consent-mode conditions, and `validate.py` fails
if either disappears.

**Why.** Non-negotiables #1 and #7 govern what the auditor writes. They cannot
see an instrument that blends or omits *before* the auditor looks. The class had
occurred twice — a static parser reporting JS-injected schema as absent, and GA4
returning modelled and observed behaviour inside one number — which is the bar
for promoting a rule from a doctrine line to a script check.

**Alternative rejected.** A ninth reference file about tool limitations. It would
have been read once and would not have failed anything.

## 2026-08-04 — Report absence as absence, never as zero or a substitute

**Decision.** Where CrUX has no data, `psi_pull.py` reports it as absent and
emits no verdict; `sitemap_audit.py` refuses orphan detection outright;
`gsc_pull.py` reports the branded split as unavailable without `--brand-terms`;
`url_inspection.py` produces no findings for a URL it could not inspect.

**Why.** Every one of these has a plausible-looking wrong version that a
competitor tool ships: a lab score standing in for field data, "orphan
candidates" inferred from path shape, a guessed brand classification. Each would
manufacture a finding out of missing data, which is the defect this skill exists
to prevent. The refusals are held by tests because the useful-looking wrong
feature is the one that gets added back later.

## 2026-08-05 — The evidence-tier vocabulary has one home

**Decision.** `references/evidence-tiers.md` is the single home of the four tier
definitions. `CONTRIBUTING.md` quotes them verbatim, and `test/validate.py` fails
when the copies diverge.

**Why.** They had already diverged on the one tier that decides most admissions:
`FIELD` read as "a single practitioner case, one site, no control" in the
reference and "repeated practitioner reports, named" in CONTRIBUTING. Same label,
two different admission bars, and nothing comparing them — the third instance of
the pattern the DOCMAP was seeded for. The reference wins because the corpus is
written against it: claims across the reference set are tagged `FIELD, single
case`.

**Alternative rejected.** Splitting into two tiers (`FIELD` for repeated reports,
a new `CASE` for single ones). More precise, and it would have required
re-tiering every claim in twenty-one files against a vocabulary the spec fixes as
closed. Recorded in the carry-over ledger instead.

## 2026-08-05 — A closed, paid source may be recorded, inside a stated boundary

**Decision.** Material from the closed `@MikeBlazerPRO` channel may enter the
skill under the same two gates as anything else, and the channel is named in
`docs/research/` with post ids. The boundary: facts and mechanics restated in
this repo's own words, attributed by channel and id; no quotation, no
reproduction of the source text, and nothing admitted that cannot be stated
without it.

**Why.** The alternative — admitting only what a public source also carries —
was considered and rejected: it would have dropped the service-area block, the
review-queue defense and three detection patterns, none of which are
manipulative and all of which are ordinary craft knowledge. Attribution without
reproduction is how the free channels were already handled; the paid status
changes who paid to read it, not whether a fact about Googlebot can be restated.

**What this does not license.** Bulk distillation of a paid feed into a public
repository. Each admitted item has to survive both gates on its own, and the
refusal list in PART G is part of the record precisely because it shows the gate
running.

## 2026-08-10 — Severity is not an evidence tier, and the scripts must emit both

**Decision.** Every finding a bundled script emits carries an evidence tier as
well as a severity. The mapping lives in `FINDING_TIERS` in
`scripts/page_audit.py`, and `test/validate.py` fails when a finding is added
without one.

**Why.** Non-negotiable #2 makes the tier the confidence multiplier in
`priority = (impact × confidence) / effort`. Until now every instrument emitted
`severity` alone and nothing mapped one to the other, so the agent had to invent
the number that orders the plan — per finding, with no rule, and consistently
enough to look deliberate. The two are not interchangeable: `read-budget` was
`high` severity resting on a `FIELD` single-engine median, while `noindex` was
`blocker` severity resting on a documented directive.

**Alternative rejected.** Documenting a severity→tier mapping in prose for the
agent to apply. It would have been read once and enforced nothing, which is the
same reason the eighth non-negotiable became a script check rather than a ninth
reference file.

## 2026-08-10 — Non-negotiable #8 applies to coverage, not only to JavaScript

**Decision.** An instrument must declare not just what it cannot see, but what it
did not read. Six behaviours change: `page_audit.py` reports a `--max-bytes`
truncation and drops every count-based finding; `sitemap_audit.py` prints its caps
in the report body rather than to stderr; `gsc_pull.py` prints the API row limit,
the rows removed as noise, and the cliff detector's sensitivity when it finds
nothing; `url_inspection.py` claims `CONFIRMED` only for rows the index answered;
`preflight.py` decides CrUX presence from the metrics block rather than a string
in a 4 KB prefix.

**Why.** #8 was written after two cases where a tool's *blindness* produced a
false finding, and it was implemented as one caveat string about JS-injected
JSON-LD. The 2026-08-10 audit found six cases of the adjacent failure: the tool
could see the thing and only read part of it, or read nothing and said something
anyway. Same defect — assumed data presented as measured — one step earlier.
`page_audit.py` produced 10,001 words for a page at the default cap and 475 for
the same page at `--max-bytes 3000`, with no warning either time.

**What this does not license.** Refusing to report on partial data. A truncated
read still prints every presence finding; what it stops doing is publishing counts
and absences taken from a fragment.

## 2026-08-10 — Section ids are unique across the reference set

**Decision.** `references/onpage-checks.md` renumbers its sections `O1`–`O5`, and
`test/validate.py` fails when any `[A-Z]\d+` id is defined in two references.

**Why.** `SKILL.md` routes track D to both `intent-and-content.md` and
`onpage-checks.md`, and both numbered their sections `D1`, `D2`, `E1`, `E2` with
different content. Four ids with two meanings each: a cross-reference had to name
the file to mean anything, and "run D1" had two answers. The sweep took the new
prefix because it is the file with fewer inbound pointers.

**Alternative rejected.** Leaving the collision and relying on every reference
naming its file. That is what was already happening, and it held right up to the
point where `page_audit.py` pointed the H1 findings at `intent-and-content.md`,
which carries no H1 guidance at all.

## 2026-08-10 — A per-run artefact does not live in the repository root

**Decision.** `pipeline.json` moves to `docs/superpowers/pipeline/<date>.json`,
with a README saying what those files are.

**Why.** A file called `pipeline.json` in the root reads as configuration. It
described a run that finished on 2026-08-05 and carried that run's decisions —
"No deploy this run by operator decision", a stage gate naming two of the four
test files — so the next agent to open it inherited a closed run's choices as
policy.

## 2026-08-10 — The repository carries its own instruction file

**Decision.** Add `CLAUDE.md`, plus the two pipeline ledgers
(`docs/superpowers/backlog.md`, `docs/superpowers/verification.md`).

**Why.** Every rule this repo depends on — DOCMAP as the propagation matrix, the
retro's standing instructions, the four-command gate, one channel per agent —
lived only in the operator's global files, which do not travel with a clone. An
agent invoked in a fresh checkout was told none of it. The two ledgers close the
same gap over time: every carry-over recorded on 2026-08-05 existed only in a
session that had ended.
