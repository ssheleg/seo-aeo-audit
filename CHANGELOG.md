# Changelog

## v0.14.0 — 2026-08-10

A second audit of the skill, run through the lens the first one did not use: **what
happens when an agent actually uses this**. Nine findings, one of them a blocker,
and the four-command gate was green against every one — again, because a guard
tests the invariant somebody thought to write, and nobody had thought to ask
whether the documented commands run at all.

Two output contracts change, so this is `0.14.0` and not `0.13.1`:
`url_inspection.py` and `psi_pull.py` now exit **1** when a run produced nothing
usable. Anything branching on their exit status needs to know.

### Fixed — the instruments were unreachable from where the agent stands

- **All eleven documented invocations failed in the only environment the skill is
  used in.** Every bash line read `python3 scripts/<name>.py`, which resolves
  against the agent's working directory — the user's project, where the scripts
  are not. Reproduced from a project root: `No such file or directory`, eleven
  times out of eleven. One sentence in the whole shipped skill admitted the paths
  were relative, and it did not say to what.

  The failure is quiet in the way that costs: an agent absorbs the error, does the
  check by hand, and the audit silently drops to the bottom rung of the evidence
  ladder — which caps every tier it is allowed to claim. Now `SKILL.md` resolves
  `$SKILL_DIR` once (`${CLAUDE_PLUGIN_ROOT}/skills/seo-aeo-audit` in a Claude Code
  plugin, the harness-named base directory elsewhere — the placeholder is
  documented to expand in *skill content*, which was verified before it was relied
  on), every invocation goes through it, and the validator rejects a bare
  `scripts/*.py` path.
- **The Cursor channel shipped non-negotiable #8 — "know each instrument's blind
  spot" — and named zero instruments.** It mentioned `scripts/` not once, so the
  rule governed nothing and every Cursor audit was capped at the manual-fetch rung
  without saying so. It now carries the six, each with what it settles and what it
  cannot see.
- **`page_audit.py --format json` emits an array even for one URL**, and said so
  nowhere; `data["findings"]` raises `AttributeError`, which is what the one-URL
  example in the docs leads you to write.

### Fixed — a run that measured nothing reported success

- **`url_inspection.py` and `psi_pull.py` returned 0 after total failure**, against
  their own docstrings, while `page_audit.py` and `sitemap_audit.py` returned 1 in
  the same situation. Four collectors, two answers. The prose was already honest —
  a run of 403s prints "supports **no findings at any tier**" — but SKILL.md's own
  documented invocation redirects stdout to a file, so an agent checking `$?` read
  success from a page of refusals. The predicate now has one home per script and
  the report and the status read the same one. An absent-CrUX result still exits 0
  and is pinned by a test: that call worked, and treating its honest absence as a
  failure would break the behaviour the script exists for.

### Fixed — the instruments emitted broken markdown

- **Four renderers interpolated raw network errors into generated markdown.** A
  Google error page arrives with newlines; the first one ends the table row and
  every row after it stops rendering. On a live preflight run against a 404
  property, **5 of 7 rows survived** — and `validate.py` already rejects exactly
  this shape in the repository's own files, but a guard over checked-in markdown
  cannot see markdown a tool generates. `_flat()` collapses whitespace, escapes
  pipes and caps length in all four.
- **`preflight.py`'s coverage denominator shrank when a source failed.** A failed
  property-list call returned one probe where a successful one returns two, so the
  headline said "3 of 7" where success says "of 8" — and the probe that silently
  left is the one that decides the most: whether this account can see this property
  at all. A reader could not tell a smaller world from an unasked question. The
  named-property row is now always reported, marked `not attempted`.

### Fixed — claims about the skill that were false

- **`SECURITY.md` described "documentation plus one small Python script"**, listed
  only `page_audit.py`, documented only its network behaviour, and closed with a
  verification recipe scoped to that one file under the sentence "No `subprocess`".
  Six scripts ship and **three execute `gcloud` as a subprocess** — the most
  security-relevant fact about the bundle, absent from the security document. It
  now carries a measured per-script table (outbound, subprocess, writes), explains
  what the `gcloud` token exchange does and does not do, and its grep covers all
  six: 22 lines, six `open()` calls, every one a file you named.
- **The PR template asked for two of the gate's commands.** It was never counted as
  a home, so it kept asking for two long after CONTRIBUTING and the README were
  corrected. The gate-parity guard now spans five homes.
- **The third deliverable had no root skeleton.** `deliverable-templates.md`
  embedded three; `templates/` shipped two, and the README calls that directory the
  skeletons for non-agent use — while step 4 makes `experiments.md` required as
  soon as anything sits below `CONFIRMED`.
- **The 2026-08-10 defect total was wrong in five of its six homes.** The ledger
  enumerates `D1`–`D43`; the changelog, the retro, the improvement plan and the
  ledger's *own summary sentence* said forty-one. It went stale in the release that
  appended `D42`–`D43` after the `v0.12.0` rebase.

### Added — guards, each watched failing on a planted defect

Script reachability, error flattening, the defect count against the rows the ledger
enumerates, and the PR template as the fifth gate home. `test/test_output_contracts.py`
holds what all six scripts owe their caller. All **17** negative self-tests were
re-run after the code changes — a changed line silently disables one, and a disabled
self-test looks exactly like a passing one.

The gate command count is no longer written down in any living document. It had four
homes and went stale in three of them the first time a file was added; a count that
does not exist cannot drift.

## v0.13.0 — 2026-08-10

**Version note.** This work was written against `v0.11.2` and released as `v0.11.3`
before `origin/main` was fetched — by which time `v0.12.0` had already shipped. The
number is corrected here rather than quietly reused: `0.13.0` and not `0.12.1`,
because two output contracts change. The `thin` finding code is now
`low-extractable-text`, and `onpage-checks.md`'s sections are `O1`–`O5` where they
were `D1`–`E2`, so anything parsing findings or citing those ids needs the new names.
The stray `v0.11.3` tag is deleted.

A fresh-eyes audit of the whole skill: every command, every bundled script, all
twenty-two references and the pipeline around them. **Forty-three defects**, nine of
which made the skill emit or suppress findings in ordinary use. The four-command
gate was green against all forty-three.

Full record: `docs/audit/2026-08-10-defect-ledger.md` (what was wrong, with the
repro for each) and `docs/audit/2026-08-10-improvement-plan.md` (what was done,
what was not, and what is next).

### Fixed — the auditor was manufacturing findings

- **`max-image-preview:none` was reported as `noindex`.** The directive string was
  matched with a word-boundary regex, and `none` is a real directive as well as the
  value of two documented parameters. A page declaring `index, follow` came back
  carrying a track-A indexation blocker — and SKILL.md makes a track-A blocker a
  stop condition, so the audit ended there on a fabrication. Directives are parsed
  as comma-separated tokens now, with `key:value` read as a parameter for the four
  parameter directives and as a user-agent prefix otherwise, so
  `X-Robots-Tag: googlebot: noindex` still counts.
- **jQuery's `$` produced a JS-gated-price finding.** `CURRENCY_RE` was searched
  against the raw HTML, so any inline script using `$` — or a correct
  `Product`/`Offer` `priceCurrency` — produced a `high` finding asserting the page
  hides its price from answer engines and hands it to aggregators. Doing the markup
  correctly was what triggered the accusation. The check reads markup with script,
  style, template, noscript and comments removed; a declared JSON-LD price absent
  from visible text is now its own `jsonld-price-parity` finding, which is the
  markup-versus-content parity check `onpage-checks.md` already asked for.
- **A truncated response was analyzed as if it were the page.** The same URL
  returned 10,001 words at the default `--max-bytes` and 475 at `--max-bytes 3000`,
  with no warning either time; a page truncated just under the threshold produced a
  fabricated thin-content finding. `fetch` reads one byte past the cap to tell
  "fits" from "was cut", the flag travels in the payload and the markdown, and every
  completeness-dependent finding is dropped. Presence findings survive.
- **`preflight.py` decided CrUX presence from a 4 KB prefix, and from the wrong
  key.** PSI returns `loadingExperience` whether or not it has data — the data is in
  its `metrics` child, which `psi_pull.py` has always read. So the probe reported
  field data that was not there, and reported absence with a cause it never
  established ("too little traffic"). Both instruments now answer the question the
  same way, and the tests pin them to each other.
- **`url_inspection.py` printed "Evidence tier: CONFIRMED" unconditionally.** A run
  where every inspection returned 403 ended by declaring its output CONFIRMED, from
  the one instrument in the skill whose justification is that it can legitimately
  claim that tier. The footer is scoped to the rows the index answered for and says
  plainly when there were none. Its not-indexed check was a substring test for
  "not indexed" — two documented coverage states out of the full set — and now reads
  the engine's own verdict, so duplicates, canonical alternates, `noindex` and
  unknown URLs are no longer passed silently. A response with no `indexStatusResult`
  produced exactly one finding, "no last crawl time recorded", manufactured from a
  parse miss.
- **`gsc_pull.py --format text` computed four analyses and printed none of them.**
  `ctr_curve`, `ctr_gaps`, `cannibalization` and `branded_split` existed only under
  `--format json`, while `text` is the default and the documented invocation. An
  agent running the documented command saw no cannibalization section and had
  nothing to distinguish "none found" from "never shown", and
  `derive_branded_split`'s refusal to guess never reached anybody. Two silences
  beside it: the cliff detector fires only on a ~90% drop held for two weeks and
  never said so, and the query set is capped at the API row limit with no
  pagination, dropping the long tail the beyond-30 band is made of — the band the
  report tells the operator to rank the brief by.
- **`sitemap_audit.py` printed its truncation notice to stderr**, under a comment
  saying a silent cap reads as "this is the whole site". Any run capturing stdout —
  which is how the skill's own examples use it — lost the caveat exactly when the
  count became evidence.

### Fixed — the instruments contradicted the doctrine

- **The auditor emitted the H1-count line `onpage-checks.md` calls a non-finding**,
  pointing at `intent-and-content.md`, which carries no H1 guidance at all. An agent
  reading "3 H1 elements" in a findings table writes "consolidate to one H1", which
  is on the myth list. Both H1 findings point at the owning section now, and the
  message carries the reason.
- **The `thin` finding cited a study that refutes its premise.** It fired at a bare
  300-word floor and pointed at the information-gain section, which says "length
  barely matters". The threshold appeared nowhere else in the repository. It is
  `low-extractable-text` now and states what it is not.
- **`subheads-thin` dropped the qualifier its own doctrine attaches** ("on a long
  page"), so a four-section pricing page collected a finding the doctrine does not
  support.
- **No script finding carried an evidence tier**, and non-negotiable #2 makes the
  tier the multiplier in `priority = (impact × confidence) / effort`. Severity alone
  reached the agent, so the number that orders the plan was invented per finding with
  no documented mapping. Declared in `FINDING_TIERS`, enforced by the validator.
- **`tooling.md` capped the same evidence at two tiers in one sentence** — a
  third-party index at `STUDY` and "an inference from public data" at `HYPOTHESIS`,
  when a third-party index *is* public data — and mapped three of six rungs, leaving
  the rung `page_audit` and every `view-source` observation sit on undefined. All six
  carry a stated ceiling, and the reason rung 6 is last (coverage, not reliability)
  is written down.
- **`onpage-checks.md` claimed `page_audit.py` automates the starred items.** Three
  of eight are cross-page or judgement calls it cannot make, so a sweep marked
  covered on that reading reported an absence as coverage.

### Fixed — claims about the skill that were false

- **The myth count was wrong in three of its four homes** (README's closing pitch
  29, SKILL.md 30, the Cursor rule 29, against 32 rows) while the guard read the one
  sentence that had drifted before. The two short lists disagreed too: fourteen items
  in SKILL.md and thirteen in the Cursor channel, with the tracking-parameter myth
  missing from the copy that ships to Cursor users.
- **The play count said 60 against 61 rows**, after an earlier correction from 59.
- **The Prowl tool count said ~408 in the README** where two references said ~448.
- **`CONTRIBUTING.md` named two of the four gate commands** and called CI "the same
  two"; CI runs four. A contributor following the docs ran half the suite. The README
  repeated the same pair.
- **The README described a two-script repository.** Six scripts ship, three of them
  shell out to `gcloud`, and the security posture — the section a reader consults
  precisely because they will not read the code — understated what runs.
- **"Every benchmark carries its own date and sample size" was false**: 36 of 140
  rows were undated at both row and section level, and the whole Operational block
  had a two-column shape with nowhere to put a source, in the file whose header says
  "Always cite the date". Those rows name their source or say **undated**.
- **`evidence-tiers.md` said the validator compares "the two copies"** of the tier
  vocabulary; it reconciles four homes, which CONTRIBUTING and DOCMAP already said.

### Fixed — provenance

- **"PageRank decays ~85% per hop" inverted the damping factor** in all three of its
  homes. 0.85 is the share modelled as *passing*: read as loss, three hops retain
  0.34%; read correctly, ~61%. The two prescribe different architectures, and the
  claim had no source, date or tier anywhere. The depth rule keeps its own field
  evidence and never needed it.
- **A patent asserted live behaviour untiered**, against the rule the same corpus
  applies correctly elsewhere (`evidence-tiers.md` rule 5).
- **The read budget was one engine's `FIELD` median presented as the answer-engine
  first read.** The window's basis travels in the payload and the finding text.
- **`algorithm-updates.md` was stamped older than its own newest row** (2026-07-28
  against a row dated 2026-07-30), and the README carried a different stamp for the
  same corpus. Two facts, stated separately, with the newest-row line checked.
- ~18 numeric claims across five references gained a tier and a date. The same
  figure was tiered in one file and bare in another, and the bare copy is the one an
  agent lifts.

### Fixed — structure

- **Four section ids were defined twice with different content.** `SKILL.md` routes
  track D to two files and both numbered their sections `D1`, `D2`, `E1`, `E2`, so
  "run D1" had two answers. The sweep owns `O1`–`O5`.
- **A misaligned table row silently deleted a play's evidence tier**:
  `growth-plays.md` P5 had six cells under a five-column header, in the file whose
  closing rule is "never ship a FIELD or HYPOTHESIS play sitewide".
- **`technical-checks.md` numbering had four holes and the sweep sat after the B
  track.** `A3`–`A6` never existed; the sweep is `A3` now and the scheme is stated.
- **Two `myths.md` pointers pointed at rows that do not exist**, so an agent
  following them found nothing and improvised the guardrail.
- **The experiment record was a third deliverable with no skeleton**, and the audit
  template had no slot for the evidence rung SKILL.md requires.
- **`experience-signals.md`'s CWV thresholds were inserted mid-list**, splitting the
  evidence list in two.

### Added — eleven reconciliation guards, each watched failing first

The myth count in all four homes plus both short-list sizes; the play count; the
Prowl count; the gate commands against CONTRIBUTING, README and CI; per-finding tier
coverage; the CWV bands against their documented home; the two freshness facts;
section-id uniqueness; table rows with more cells than their header; backticked
`references/*.md` pointers; and the slash command's non-negotiable count, since it
was the third doctrine channel and the only unguarded one. Every one has a
planted-defect step in CI, and all twelve pre-existing negative self-tests were
re-run after the code changes and still fail as designed.

### Added — the registers a fresh clone was missing

`CLAUDE.md`, `docs/superpowers/backlog.md` (eight rows, computed priorities) and
`docs/superpowers/verification.md` (nineteen rows: 4 observed, 6 test-only, 4
planted-and-observed, 6 never). Every rule the repository runs on lived only in the
operator's global instruction files, which do not travel with a clone, and there was
nowhere for a deferred item to survive between runs. `pipeline.json` moves out of the
root, where a finished run's decisions read as configuration. DOCMAP gains nine
single-home rows and eight propagation rows; DECISIONS gains five entries.

## v0.12.0 — 2026-08-06

### Added
- **`references/discover.md`** — Discover audited as its own surface. The skill
  mentioned Discover 42 times and mentioned `og:image` and `max-image-preview`
  **zero** times, so the one check whose failure is binary was the one it could
  not make. Carries the two tags without which no card renders, image
  requirements, the two metatags reported to halt the pipeline entirely, the
  freshness window, and a four-command audit.
- **Sitemap protocol** in `references/technical-checks.md` — the namespace and
  schema contract, the five characters that must be escaped (and why `&` in a
  query string is the one that actually breaks files), W3C Datetime for
  `lastmod` and why a build-stamped one is worse than none, the 50,000/50MB
  limits, `robots.txt` submission, and a mechanical check rather than an eyeball.

### Notes
- **The new reference states its own evidence tiers in its opening section**, and
  they are not uniform. Google's documentation carries the image and
  `max-image-preview` requirements (CONFIRMED, verified 2026-08-06 against *Get
  on Discover*); the parsing fallback chains, freshness buckets and
  pipeline-blocking metatags come from one practitioner's SDK reverse-engineering
  and ship as **FIELD**. Mixing the two silently would have been the exact
  failure `references/evidence-tiers.md` exists to prevent — a plan someone funds
  should not treat "Google says" and "one researcher observed" as the same claim.
- `discover.md` is in `REQUIRED_REFERENCES`, with its own negative self-test:
  deleting it must fail the validator.

## v0.11.2 — 2026-08-05

A self-audit of the two releases above, run on the same two gates the pass itself
used. Seven defects, five of them mine.

### Fixed
- **A 2017 engine statement was dated 2026.** Googlebot's ~9,000px render
  viewport is John Mueller's advice from November 2017, not a finding from this
  window — the recent report merely restated it. Both the benchmark row and the
  technical-checks passage now date the confirmed half to 2017 and mark the
  practitioner half (that the expansion fires listeners exactly once) as the
  unverified 2026 observation it is. Dating a claim to the post that reminded you
  of it is the exact rot `benchmarks.md` exists to prevent.
- **A second split table**, in `threats-and-defense.md`: two detection rows sat
  behind a blank line and rendered outside the table. Second occurrence of the
  class in one run, so `validate.py` now rejects a blank line inside any table in
  the skill — watched failing on a planted seam.
- `growth-plays.md` G29 was inserted before G28.
- Per-page entity counts are **medians** (15–172), which the study says and the
  reference did not.
- The B2B page-type counterweight in `ranking-model.md` quoted a sample size that
  no primary source supports; the observation stays, the number is gone.
- The S-CTS row now carries the paper's title, authors and its own wording for the
  platform — the figures were written from secondary coverage first and confirmed
  against the paper only during this audit, which is the wrong order.

## v0.11.1 — 2026-08-05

### Fixed
- Two myth-guard rows added in v0.11.0 were separated from the claim table by a
  blank line, so they rendered as loose text instead of table rows. Found by a
  new validator check rather than by eye.
- `validate.py` now compares the README's myth-guard count against the number of
  rows in `myths.md`. A prose count sitting next to the list it counts has now
  drifted twice in this repo — nineteen references against twenty-one enforced,
  and this one — which is the bar for moving a rule off the page into a check.

## v0.11.0 — 2026-08-05

A two-week window of practitioner sources, screened on two gates: does it
contradict what this skill already holds, and does the number survive its primary
source. Eleven items entered unchanged, nine after their claim was narrowed, five
as detection only. Nine were refused, three of them for contradicting evidence
already in the corpus — and the refusals are recorded, because a rejected claim
that leaves no trace returns next quarter wearing the same confidence.

The primary-source pass removed three figures, refuted one field name and
narrowed one claim **after** they had passed the first gate. That is the pass
earning its keep: every one of them reads as mechanical, and every one would have
shipped as fact.

### Added
- **Rendering as a second budget** (`technical-checks.md`). Crawl budget counts
  URLs; the render queue decides how many of them ever run their JavaScript,
  which is the ordinary cause behind *Crawled – currently not indexed* on a JS
  template. The diagnostic is written in the form that can be executed — Last
  crawl plus the stored render under *View crawled page*, against the raw source,
  then a live test. The field the source named for it does not exist in the tool.
- **Googlebot stretches its viewport once** to the page's full initial height
  instead of scrolling, so a sequential infinite scroll never loads its second
  batch and an unconstrained hero pushes the content thousands of pixels down the
  render.
- **Mobile-first status divergence** — a desktop-only 404 is not the response
  being read — and the single internal link that keeps a dead URL in rotation.
  Both are now in the mechanical sweep.
- **Entity extraction has an instrument problem** (`entity-and-brand.md` G3,
  `tooling.md`, `benchmarks.md`). Across 166 top-ranking pages, four
  general-purpose extractors put 46.6–65.1% of their output on material with no
  trace in Google's own vocabulary for the query, and the budget-LLM option
  rewrites two entity sets in five between identical runs. The rule: the tool
  proposes, the AI Overview / People Also Ask / related searches decide.
- **A loop that turns the GSC generative report into prompts you can test**
  (`measurement.md` J3), recording citation and mention as separate outcomes.
- **Service-area businesses** get the block they never had
  (`architecture-and-equity.md`): city-level areas, one real page per city,
  reviews as the geographic signal, citations without an address, and a geo-grid
  boundary measured rather than assumed.
- **Five detection patterns** (`threats-and-defense.md`): the paid-mention market
  selling itself as AEO, synthetic consensus with its documented case,
  retrieve-and-switch, canonical pulsing from expired domains, cluster-level
  detection of coordinated generation, and review-queue attacks.
- Layout split tests, editorial trend-onset timing, on-site UGC read honestly,
  map-pack call attribution, and a first-party reviews section with its gating
  guardrail.

### Fixed
- **The evidence-tier vocabulary had two homes and they disagreed.** `FIELD` read
  as "a single practitioner case" in `evidence-tiers.md` and "repeated
  practitioner reports" in `CONTRIBUTING.md` — one label, two admission bars.
  `evidence-tiers.md` is now the single home, CONTRIBUTING quotes it verbatim,
  and `validate.py` fails on drift. The guard was watched failing against both a
  drifted definition and a removed row before it was trusted.
- **`onpage-checks.md` reported a non-finding.** "Several H1s" sat in the
  crawler-understanding table while Google states the count carries no penalty.
  The check survives as document structure and accessibility; what replaces it is
  the meaning test on the mobile render, which is the loss that is real.
- Two myths retired: the five-second render limit (the rendering service pauses
  its own clock during fetches; the real ceiling is an event loop that never
  idles) and the multiple-H1 penalty.

### Changed
- Alice AI figures move to Yandex's Q2'26 release — 42% of queries, 49.5M monthly
  users — with the Q1 point kept beside it as a trend rather than replaced.
- The generative-features opt-out is priced: the reported cost is Top Stories
  shown inside an AI Overview, scoped and unconfirmed by Google.
- Search-operator recon is demoted to HYPOTHESIS with both readings named, and
  routed through "prove it on a known-positive query first".

## v0.10.0 — 2026-08-04

An eighth non-negotiable, four new scripts, and the literature that bounds the
one study this skill was leaning on.

The run started as an audit of every SEO/AEO skill installed on one machine —
twenty-six of them. None contributed knowledge: no mechanism, number or argument
turned up that these references did not already hold. What they did expose was
the opposite gap. This skill named evidence sources it had no way to collect, and
two of its own instruments were quietly reporting assumed data as measured.

### Added
- **Non-negotiable #8 — instruments declare their own blind spots.** Rules #1 and
  #7 govern what the auditor writes; neither can see a tool that blends or omits
  before the auditor looks. `validate.py` enforces it, and the Cursor channel is
  now count-checked against SKILL.md — it had shipped five non-negotiables where
  SKILL.md carried seven, so Cursor users ran without the measured-vs-assumed rule.
- `scripts/url_inspection.py` — the Google-selected canonical against the declared
  one, coverage state, robots verdict. The engine's own answers, so findings built
  on them are CONFIRMED. The skill cited URL Inspection in eight places and could
  not collect it.
- `scripts/sitemap_audit.py` — declared URLs clustered into the template families
  a site actually ships, derived from its own URLs. It refuses orphan detection: a
  sitemap holds no link graph.
- `scripts/psi_pull.py` — CrUX field and Lighthouse lab reported separately, judged
  at the 75th percentile. Absent field data is reported absent, never as a pass.
- `scripts/preflight.py` — step 0's "test the access, do not assume it", performed.
  Each failure names which independent gate it hit; three of them answer 403.
- `gsc_pull.py` derivations — cannibalization, and a **CTR curve built from the
  property's own rows**. Industry CTR tables are on measurement.md's do-not-measure
  list; a hardcoded "under 3%" threshold is the same error one step further from
  the data. Bands under five rows yield no baseline at all.
- `benchmarks.md` — **C-SEO Bench** (NeurIPS 2025, 1,921 queries): under competition
  the GEO methods are mostly ineffective, and in retail a traditional-SEO baseline
  was ~7.6x more effective. It bounds Aggarwal et al. (KDD '24), which this file
  quoted without it. Also PAWC named as the unit, the Similarweb recommendation
  data, llms.txt consumption (97% of files get zero AI requests), and title and
  description rewrite rates.
- The visibility ladder in `measurement.md` — retrieved / cited / mentioned /
  recommended, each governed by a different mechanism, so the gap between two rungs
  is itself the diagnosis. Plus the rule-out check in the prompt set.
- `technical-checks.md` — geo-redirects and content negotiation, a whole class of
  locale invisible to staff who browse from the country that works.
- `experience-signals.md` — the CWV thresholds this file spent its length fixing
  without ever stating.
- `docs/DOCMAP.md`, `docs/DECISIONS.md`, `scripts/check-docs.sh`,
  `docs/superpowers/retro.md`.

### Fixed
- `page_audit.py` reported JS-injected JSON-LD as absent schema. On any Yoast,
  RankMath or AIOSEO site that was a false finding — the exact defect this skill
  exists to prevent. Every report now carries the caveat and the way to confirm.
- `sitemap_audit.py` parsed in O(n^2): 10,000 URLs took 14.8s and a 60,000-URL
  file never finished. Now 0.16s and 0.52s for the full 50,000 the spec permits.
- Silent truncation in the sitemap cap, and `None` rendering as a value in
  psi_pull. Absence must read as absence.
- `measurement.md` — GA4 consent-mode modelling blends observed and estimated
  behaviour inside one number. The three activation conditions, the reporting
  identity, the visible indicator and the BigQuery escape hatch are recorded.
- Reference count in CONTRIBUTING (nineteen -> twenty-one) and the Prowl tool
  count (408 -> 448).

### Verification note
Three figures carried in from other skills failed verification against primary
sources and are NOT in this release: `userDeclaredCanonical` (the API returns
`userCanonical`), "+41% for Quotation Addition" (the paper groups three methods
and says over 40%), and "~9% of post-recommendation visits arrive as AI referrals"
(absent from the source). CI fails if the first ever reappears.

## v0.9.3 — 2026-07-30

### Added
- **`displayName`** ("SEO + AEO Audit") in both manifests — the picker shows
  `name` otherwise, and `name` is kebab-case because it namespaces components.

## v0.9.2 — 2026-07-30

### Fixed
- **`argument-hint` in `/seo-aeo-audit` parsed as a two-item list**, split on the
  comma inside it, because the value was unquoted — in YAML a bare `[...]` is a
  flow sequence. Quoted with single quotes, since the hint itself contains double
  quotes. Found by `claude plugin validate --strict`, which now runs in CI
  against both this plugin and its marketplace manifest.
- **`homepage` and `repository` sat at the top level of `marketplace.json`,
  where Claude Code does not recognize them.** They are plugin-entry fields;
  moved there, so the values reach the plugin listing instead of being ignored.

## v0.9.1 — 2026-07-30

### Changed
- `license: MIT` declared in the `marketplace.json` plugin entry and in the
  skill's front matter. The `LICENSE` file reaches neither the plugin listing
  nor an installed skill, so the terms were a repository visit away.

## v0.9.0 — 2026-07-30

Tracking parameters get their own mechanism, separate from facets and filters.
The trigger was a community thread («Site Growth», Jul 2026) about a large Shopify
store where a `robots.txt` `Disallow` on `utm_*` URLs was proposed as a
crawl-budget win — and the reference set could be read as endorsing exactly that,
because tracking parameters sat inside the facet-and-filter guidance with no case
of their own.

### Added
- `technical-checks.md` A2 — **"Tracking parameters are not facets"**, the new
  owner of the mechanism. UTM variants carry no independent demand, so the whole
  job is consolidation and *crawled, not indexed* is the canonical working rather
  than a leak. A `Disallow` cuts off a crawl Google performs legitimately, cannot
  improve consolidation (a blocked URL never sees the canonical) and cannot touch
  the one real failure case: a parameterized URL that out-signals its canonical
  is selected despite the tag, and `robots.txt` changes no signal. The lever is
  one step up, at the source — strip tracking parameters from internal links and
  from affiliate and partner placements you control, and leave genuine
  third-party tracking URLs crawlable, because they are real referrals carrying
  real equity. Split tiers: `CONFIRMED` for the engine-documented mechanics,
  `FIELD` for the link-accumulation trigger.
- `technical-checks.md` A2 — hosted-platform duplicates priced before tracking
  parameters: Shopify serves every product under
  `/collections/{collection}/products/{handle}` as well as the canonical
  `/products/{handle}` and appends `?variant=` per variant, so one product in
  five collections with six variants is dozens of crawlable strings before a
  single UTM exists (`CONFIRMED`, reproducible in any store's crawl). Plus the
  scale check that has to precede the finding: the GSC Pages report grouped by
  reason, where *Alternative page with proper canonical tag* closes the finding
  and *Duplicate without user-selected canonical* is the finding.
- `growth-plays.md` — play **L13**: tracking-parameter URLs named as the
  crawl-budget problem, or already sitting under a `Disallow`.
- `myths.md` — row: "`Disallow` the UTM URLs to protect crawl budget" (30 refuted
  tactics now).
- `tooling.md` — the rung-2 fallback for crawl-waste work with no server logs.
  Shopify, Wix, Squarespace and comparable SaaS hosts expose no raw access logs,
  so rung 1 does not exist there and the finding caps at rung 2: GSC Crawl Stats
  gives host-level shares, totals and status mix, never per-URL truth. Say that
  in the report instead of presenting a crawler's URL count as crawl data.

### Changed
- `technical-checks.md` A2 — the index-tiering Tier 3 line now reads "facet
  parameter combinations" and states explicitly that tracking parameters are
  **not** in that bucket; crawl-budget killer #3 no longer lists tracking params
  alongside session IDs without qualification, and routes to the new block before
  anyone spends a `robots.txt` line on them. This is the internal contradiction
  the thread exposed.
- `SKILL.md` — the myth guard's short list grows to fourteen of thirty and now
  carries the tracking-parameter block, so the correction is reachable without
  loading `myths.md`.
- `README.md` — myth count 29 → 30, plays 59 → 60, freshness date and line total
  refreshed, tracking-parameters case named in the technical row.
- `docs/research/2026-07-source-distillation.md` — PART F records the source and
  the per-claim tiers (repo-only; not shipped to agents or npm).

## v0.8.1 — 2026-07-30

### Changed
- **README** — `agent-sync` added to the family list, and the install block now
  carries all three family commands (`install`, `update`, `list`) plus the
  restart note. The registry copy of the README only moves on a release, so a
  doc fix that stays on `main` reaches nobody.
- `CONTRIBUTING.md` — how to run `test/validate.py` and what a PR is checked
  against.

## v0.8.0 — 2026-07-29

Bulk market data through one MCP endpoint, and the evidence discipline that has
to travel with it. Written from a full audit run against a live property, so
every cost and gotcha below is measured rather than assumed.

### Added
- `references/prowl-mcp.md` — the Prowl MCP as a rung-5 source: ~408 provider
  tools (DataForSEO, Majestic, SpyFu, SearchAPI's 60+ engines, Firecrawl) behind
  one pay-per-call endpoint, for when there is no Ahrefs or Semrush seat. Routed
  by track, with the tools that carry each one, observed per-call costs, and the
  operating notes that cost time to learn: `prowl_call_tool` nests its arguments
  under `params`, failed calls are not billed, responses run 50-70 KB so they
  belong in a file rather than the context window, and not every endpoint accepts
  `order_by`. Carries an explicit disclosure that Prowl is a commercial product
  and nothing in the skill requires it.

### Changed
- `tooling.md` — Prowl added to rung 5 under the same "estimates, never ground
  truth" cap as Ahrefs and Semrush, plus a new rule: **two third-party indexes
  agreeing is a stronger `STUDY`, not a `CONFIRMED`**. Four routing rows added:
  demand validation against two independent volume datasets, sizing a whole
  competitive set in one call, anchor profiling **filtered on spam score first**,
  and finding which pages in a niche actually earn links. The AI-visibility row
  now names the `dataforseo_ai_llm_mentions*` and per-engine `ai_*_responses`
  tools for running the AEO prompt set at volume.
- `SKILL.md` Step 0 — **test access, do not assume it**. A connected MCP server
  is not a working one: API tiers gate endpoints and tokens carry narrower scopes
  than the dashboard suggests. Probe the one call each source exists for before
  planning around it, and record the result — "connected but returns
  `Insufficient plan`" is a finding the next audit needs.
- `SKILL.md` Step 1 — an explicit fallback for **no first-party access at all**:
  what a third-party index can still establish (current rankings, link-profile
  size against a sized competitive set, whether the target phrases carry demand),
  capped at `STUDY`, and enough to tell a cold start from a decline — which need
  opposite plans.

### Also added — the host-variant blocker
`technical-checks.md` A0 gains a check that nothing else in the file caught: **every
host variant must actually resolve**. A dead `www` kills every inbound link,
citation and typed visit that used it, and it never shows up in a crawl that
starts from the canonical host.

With it, the diagnostic that goes with it — **read the error body, not just the
status**. Cloudflare Error 1000 ("DNS points to prohibited IP") presents as a bare
403: a proxied `www` CNAME pointing at an apex whose own A records already hold
CDN addresses, so the edge refuses to proxy to itself and never contacts the
origin. Reading only the status sends you hunting for a WAF rule or a missing
redirect, and neither exists. The entry also covers the trap that follows —
PaaS origins route on the Host header, so repointing DNS when only the apex is
registered trades a 403 for a 404 — and the three real fixes in cost order, with
the API-token permission that actually gates Cloudflare Single Redirects
(`Zone → Single Redirect → Edit`, not `Zone → Config → Edit`).

### Fixed — release hygiene
- **v0.7.0 shipped Python bytecode to users.** The npm tarball carried
  `plugins/…/scripts/__pycache__/gsc_pull.cpython-314.pyc`, left behind by a local
  run of the new script: `files` whitelists `plugins` wholesale and both
  installers copy that tree verbatim, so the artifact reached every install. Two
  layers now stop it — the validator **fails** when any `__pycache__` or `.pyc`
  exists under `plugins/` (with a CI negative test), and `files` excludes them so
  an unclean working tree cannot publish one either. This is the same defect class
  as the test-suite leak fixed in v0.6.1, arriving through a different script;
  the guard is placed at the shipped tree rather than at either script.
- **Two parallel v0.7.0 releases reconciled.** Link-building extraction and the
  Prowl work were developed from the same parent and both numbered 0.7.0. The
  published 0.7.0 keeps its entry unchanged; the Prowl and host-variant work is
  this release.
- **Validator de-duplicated.** Compilation, the `from __future__` requirement and
  the stdlib rule ran twice for `page_audit.py` — once in the per-script loop and
  once in an older block. The older block now carries only what is unique to it,
  the finding-anchor resolution.
- **README counts corrected**: nineteen/20 contract files → **21**, and the
  distilled-line figure re-measured (~4,300). Link building and bulk market data
  gained rows in the knowledge table.

### Why the two-index habit is now a rule
On the audit this release was written from, four programmatic pages were found to
target phrases one clickstream panel measured at zero. A second, independent
index then returned **no keyword record at all** for the same six phrases. That
turned "these pages have an intent mismatch" into "these pages target queries
that do not exist" — a different fix entirely, and one no single source would
have supported. The same run showed the inverse risk: the top anchors by
referring domains for two competitors were PBN spam at spam scores 60-89, links
pointed *at* them rather than built by them. Sorting without filtering would have
produced an anchor strategy copied from someone else's negative-SEO problem.

## v0.7.0 — 2026-07-29

Link-building extraction — the audit now produces a deliverable someone else
can execute, not only a diagnosis for the owner.

- **New `references/linkbuilding.md`.** Target selection, the two collection
  modes (Search Console reachable / not), anchor discipline, the exclusions a
  brief must name, and the CSV column contract.
- **New non-negotiable #7: never blend measured with assumed.** A link-building
  CSV always carries both, so a `source` column separates them and the volume
  cells of an unmeasured row stay **blank, not zero** — `0` reads as "measured,
  no demand", blank reads as "nobody has checked". This one matters because the
  reader spends a budget against it.
- **New `scripts/gsc_pull.py`** (stdlib only, local ADC auth). Pulls what no
  crawl can see: the query set with positions, and a cliff detector that only
  reports a drop which *held* — a decline and a cliff have different causes and
  only one of them is an algorithmic story. Names which of the three auth gates
  you hit (scope / API enabled / quota-project header) instead of returning a
  bare 403.
- **Position-split discipline.** Rank a brief by the position bands, never by
  impressions: a large impression count beyond position 30 is usually the
  biggest number in the account and worth the least.
- **Validator:** the new reference and script are required; the blank-not-zero
  rule, the `source` column and the CSV contract are asserted in the reference
  text; every bundled script is checked for compilation and stdlib-only imports.
  Four negative tests confirm each rule can fail.

## v0.6.1 — 2026-07-28

Open-source hygiene pass — the repo is public, so the files a first-time
contributor looks for now exist.

### Added
- `CONTRIBUTING.md` — the evidence-tier rule stated as the first thing a
  contributor reads: no claim without a tier, `benchmarks.md` owns the numbers,
  dated facts stay dated, conflicting sources are both named and the claim is
  demoted rather than decided, and manipulative tactics are declined.
- `CODE_OF_CONDUCT.md`, issue forms and a pull-request template.
- README gained a Contributing section and lists the new files in the repo map.

## v0.6.0 — 2026-07-28

Release-readiness pass: a full read of every file in the repo looking for claims
that contradict each other, claims that contradict the code, and half-finished
work. Everything found is fixed here.

### Fixed
- **Spelling standard applied to the last holdouts.** `honours`, `catalogue`,
  `Analyses`, `labelled`, `normalised`, `behaviour`, `fulfils` and `summarise`
  across the references, the changelog and the research notes; the auditor's
  `analyse()` renamed to `analyze()` with its call sites and test updated. The
  repo standard is US spelling — a mixed standard has already cost one broken
  anchor here.

### Fixed — contradictions

- **One tier for the ChatGPT-versus-Google-index claim.** `technical-checks.md`
  A1 carried it as `STUDY`, while `aeo-geo.md` F4, `myths.md` and
  `benchmarks.md` all record it as a single FIELD case whose *dependency* reading
  is HYPOTHESIS because a Bing-only counter-case points the other way. A1 now
  matches them and points at the file that owns the conflict; what stays
  `CONFIRMED` there is the part that is documented — Googlebot cannot be split by
  purpose.
- **Alice AI naming, actually swept.** v0.5.0 announced the rename and left
  `Alisa AI` / `Алиса AI` in six places (SKILL.md, `aeo-geo.md`,
  `benchmarks.md`, `algorithm-updates.md`, `measurement.md`, `growth-plays.md`)
  plus the research notes. English text now reads **Alice AI** everywhere, with
  `Алиса` kept as the native name in parentheses on first mention per file.
- **The myth guard says how much of itself it is showing.** SKILL.md and the
  Cursor rule each list thirteen refused tactics while the README advertises 29;
  both now say they are the short list and where the other sixteen live.
- **"No install script" removed from the README.** The repo ships two installers
  (`install.sh`, `bin/seo-aeo-audit.js`); what is actually true — and what the
  sentence was reaching for — is that there are no npm lifecycle scripts and
  nothing runs unless you run it.
- **Play list re-ordered.** `G15` sat after `G28` and `P4` after `P5`; the 59
  plays now read in order.
- **Research notes re-dated.** They were labeled "working notes behind v0.1.0"
  while carrying the v0.3.0 and v0.4.0 source passes.
- Every changelog entry carries its release date.

### Fixed — the bundled auditor

- **Repeated `X-Robots-Tag` headers no longer collapse.** `dict(headers)` kept
  only the last one, so a response sending `noindex` on one line and `nosnippet`
  on the next lost a blocker. Headers are now merged, and a regression test
  covers both directives surviving.
- **A gzip body truncated by `--max-bytes` is salvaged** instead of failing the
  whole URL with `EOFError`; if nothing decodes, the error says to raise the cap.
- **Non-HTML responses are refused.** Auditing a PDF or an image as HTML produced
  confident nonsense; the fetch now stops on the declared content type.
- `--url-list` skips indented comment lines and trims each URL.
- `--base-url` outside `--file` mode warns instead of being silently ignored.

### Fixed — rendering and structure

- The plan skeleton in `deliverable-templates.md` nested a fenced block inside a
  fenced block, which broke the rendering of everything after "Sequencing".
  Outer fences widened; the copies the validator compares are unchanged.
- README repo layout now lists the installers, the manifest, the fixtures and CI.

### Added — guardrails, so these classes of defect cannot come back

- The validator resolves **every reference anchor the auditor emits** against the
  real headings in the reference files. This is the defect class that produced
  the v0.1.1 broken cross-reference; nothing was checking it. CI proves the check
  can fail by renaming a heading.
- Relative markdown links are now checked **anchor and all**, not just the file.
- CI runs with `permissions: contents: read` and cancels superseded runs.
- `.gitignore` covers Python bytecode.

## v0.5.0 — 2026-07-28

### Changed
- Description restructured English-first — every Russian trigger paired with its
  English equivalent — and `"SEO change plan" / "план правок по SEO"` added as a
  missing pair.
- Yandex's assistant is now written **Alice AI** in English throughout, with
  `Алиса` kept once as the native name, across the references, the changelog and
  the research distillation.
- README is English-only, with a plain statement of what the audit gives you and
  an author/links block.

## v0.4.1 — 2026-07-28

Security hardening of the bundled auditor, plus an explicit statement of what the
skill does at runtime.

- **URL scheme guard.** `page_audit.py` passed operator-supplied URLs straight to
  `urlopen`, which happily resolves `file://` — so a crafted `--url-list` could
  have made the auditor read local files. It now refuses anything that is not
  http/https before issuing a request, and refuses redirects that leave http(s).
  Three regression tests cover it.
- The default User-Agent no longer carries a version string that drifts out of
  sync with the release.
- **`SECURITY.md`**: what each component does at runtime, the exact network
  behavior (plain GETs, no cookies or credentials, bounded by timeout and byte
  cap, writes nothing, no telemetry), the defensive-only stance on adversarial
  material, and a three-command recipe to verify the whole attack surface
  yourself. Shipped in the npm tarball and summarized in the README.

## v0.4.0 — 2026-07-28

Deep extraction pass over the full source corpus, section by section, followed by
a reconciliation pass over the whole set. +1,725 lines across all 19 contracts.

**Extraction** — one pass per audit track, each mining the same corpus for what
its own track was still missing:

- **A/B technical**: edge/WAF blocks that answer crawlers above `robots.txt`;
  header-delivered directives (`X-Robots-Tag`, `Link: rel="canonical"`) invisible
  in view-source; bot identity and Web Bot Auth; "removing `noindex` is not a
  recovery lever"; indexing services force crawling, never indexing; the
  leaky-redirect migration failure that kept both hosts crawled for a year.
- **C architecture**: crawl frequency as an architecture output (with the
  waste-40%→10% profile at a flat budget); the NavBoost floor below which links
  cannot lift a page; subfolder membership over visual navigation; local and
  multi-location architecture (PageRank is not used in Local Search); what to
  split-test rather than ship.
- **D/E content**: one query, two surfaces; auditing modules rather than prose;
  the two-wave mechanism behind the content collapse; volume as the aggravating
  variable; refresh contamination (models delete the sentences that earned the
  position) and cohort measurement of refreshes; the money-template sweep.
- **F AEO/GEO**: Google's own AIO chain description; the retrieval budget stack;
  per-engine rows rebuilt (Gemini arbitration, ChatGPT `resultsource` buckets,
  Deep Research re-read behavior, Brave/Claude gating, Perplexity localization,
  Alice AI / Алиса with RU figures); slots you do not control; the KDD benchmark with its
  omissions stated.
- **G entity/brand**: Wikidata quantified and bounded; the mention-manipulation
  guardrail; cross-platform rating divergence as an attack signature; mention
  volume versus semantic cluster; where the verdict is actually hosted; retrieval
  added as a fourth state next to mention/citation/recommendation.
- **H experience/conversion**: CTR curves as perishable; usefulness judged on
  function; the mobile-only failure inventory; the render-blocking inventory; the
  one legitimate exception to minimum form fields; self-reported attribution;
  the AI-impression → offline-conversion ladder; conversion data as bidding fuel.
- **I risk**: rich results withheld as a sanction; takedown abuse as a campaign
  rather than an incident; canonical-hijack loss signature; behavioral-poisoning
  timing; autocomplete and volume injection; entity records as an attack surface;
  link-risk scale thresholds — all detection-and-defense only.
- **J measurement**: aggregate before the model sees it; four reporting artifacts
  that read as findings; personalization contaminating capture; the restored
  cadence section; six horizon rows; five more things not to measure. Benchmarks
  gained samples and dates on every row, a user-self-report section and a
  contested-metrics section.
- **Plays and experiments**: 18 new plays (B8–B11, L9–L12, G22–G28, P6–P8) and
  four new experiment-design rules with five documented results.
- **Model, myths, updates, tooling**: how a ranking change actually ships; the
  retrieval/scoring/re-ranking stack with demotion and removal as separate
  machinery; five new myths; 14 new dated platform rows; six tool-routing rows
  and seven DevTools recipes.

**Reconciliation** — one pass over all 19 files:

- Sixteen contradictions resolved by naming both studies and demoting the
  contested direction to HYPOTHESIS rather than picking a winner (schema on
  ChatGPT, rank-1 versus Bing-only AI visibility, "crawled – not indexed" cause,
  zero-click direction, Wikipedia's weight by query class, literal phrasing
  versus title match).
- Click-economics rebuilt as four distinct measures with an explicit note that
  none refutes the others; vendor-sourced rows tagged undated.
- Duplication removed with a single owner per fact: link velocity →
  threats-and-defense, read budget → architecture-and-equity, index tiering,
  migration protocol and out-of-stock → technical-checks, every dated figure →
  benchmarks.
- Coverage gaps filled: **hreflang and international duplication** (new
  technical-checks §B2, engine-documented), fabricated information gain as a
  detection signature, publisher licensing posture, rank-tracker vendor
  continuity, EU DMA exposure.
- Spelling drift swept again; SKILL.md flow and the Cursor rule re-verified
  against the reference set.

## v0.3.1 — 2026-07-28

Consistency pass across the whole flow, plus a rewritten README.

- **One evidence ladder.** SKILL.md described the tooling order by convenience
  while `tooling.md` ordered it by evidence strength — the two now share a single
  ordering (logs → Search Console → crawl → field data → third-party → manual),
  and the rung a finding rests on caps its evidence tier.
- **One stance on structured data.** The schema position was stated three
  different ways across `myths.md`, `aeo-geo.md` and `onpage-checks.md`; the
  canonical stance now lives in `myths.md` (an eligibility and entity aid on
  specific surfaces, never a ranking or citation lever) and the others point at
  it.
- **Page-experience claim reconciled.** The speed case study in
  `experience-signals.md` and play `G8` are now labeled as bundling satisfaction
  signals, so they no longer read as a contradiction of the tiebreaker framing in
  `ranking-model.md`.
- **Keywords reconciled.** `ranking-model.md` now says explicitly that the
  failure mode is scaffolding a page on a keyword list, not using keywords —
  matching `intent-and-content.md` E2b.
- **Tier discipline in the four new contracts**: each states what it licenses
  (`ranking-model` = vocabulary and mechanism; `onpage-checks` = existence
  confirmed, impact tiered separately; `demand-and-conversion` = platform
  mechanics confirmed, vendor case numbers FIELD; `tooling` = the rung caps the
  tier).
- **Flow documented**: the mechanical sweeps are now named in Step 2 of the audit
  procedure, and the read-budget and attribution numbers have a single canonical
  home with cross-references instead of parallel copies.
- Spelling normalized again after the new files (one standard across references,
  Cursor rule and scripts).
- **README rewritten**: what the skill is, install and update commands up front,
  the audit flow, what knowledge ships inside and what each area is worth, data
  freshness and the refresh policy, and the link to the umbrella repo for the
  whole skill family.

## v0.3.0 — 2026-07-28

Completeness pass — every audit track now carries both the judgement work and the
mechanical sweep, and the post-click half of the funnel is in scope.

- **`ranking-model.md`** (new): systems vs signals vs factors and why the
  semantic argument is a trap; the "200 ranking factors" myth; the three that
  carry weight (content and relevance, page experience, links); helpful-content,
  RankBrain, BERT, MUM and query-dependent freshness; E-E-A-T's real status as a
  rater specification rather than a dial; personalisation and locality.
- **`onpage-checks.md`** (new): the per-template on-page sweep — crawler
  comprehension, duplication and consolidation, on-page internal linking, content
  substance, metadata as a click and citation surface — with the fail state and
  the tool for each row.
- **`tooling.md`** (new): the evidence ladder (logs → Search Console → crawl →
  field data → third-party indices → manual), check → tool routing, Chrome
  DevTools recipes (header/soft-404 forensics, JS parity, link and image tables,
  emulation), and an explicit statement of where automation stops.
- **`demand-and-conversion.md`** (new): conversion elements per money template,
  lead capture without value destruction, the attribution gap table (last-click,
  untracked calls, missed calls, offline conversions, AI referrals, cross-device,
  zero-click) and paid × organic alignment.
- **`technical-checks.md`** gains the mechanical completeness sweep: availability,
  sitemaps, crawl optimization, performance, accessibility and risk — the boring
  failures that quietly cost traffic.
- **`benchmarks.md`** gains practitioner-survey context (State of SEO 2026) and
  AI-surface coverage figures (AI Overview growth by vertical, exact-match
  phrasing in AIO, B2B click-through to cited sources, device split of AI
  referrals).
- **`myths.md`** gains four: the 200-factors list, "E-E-A-T is a ranking factor",
  "AI wrote it, just publish it", and "last-click tells us what organic did".
- **`growth-plays.md`** gains G19 (call and offline conversion tracking), G20
  (decision-accelerator content) and G21 (paid × organic alignment).
- Sources distilled: SEJ *Ultimate Technical SEO Audit Workbook* + its
  spreadsheet, *SEO In The Age Of AI*, *The Future of AI Search*, *State of SEO
  2026*, *Google Ranking Factors: The 3 That Really Matter*, *B2B Lead
  Generation*, *PPC Trends 2026*, *PPC Experts Tips*, and the CallRail × SEJ
  lead report.

## v0.2.0 — 2026-07-28

Update awareness — the skill now carries the Google update history and knows how
to refresh it.

- **New reference `algorithm-updates.md`**: dated timeline of every core, spam
  and Discover update from March 2025 through June 2026 (start date, completion
  date, type, audit implication), plus a table of platform and policy changes
  that retired old tactics (FAQ rich results, AMP cache, Preferred sources in AI
  surfaces, GSC AI reporting and opt-out, Bing AI Performance, the spam policy
  covering generative-AI manipulation, I/O 2026, commerce protocols).
- **Update-response protocol** — exact dates → before/after export by page,
  query, country, device → segment by template and intent → competitor set →
  classify winner/loser/unchanged → only then hypothesize. Wired into SKILL.md as
  a mandatory step before any decline diagnosis, and into the play list as `P5`.
- **Refresh routine** with named sources (SEJ algorithm history, Search Status
  Dashboard, Search Central and Bing blogs) so every release folds in what
  shipped since — including re-checking whether a change retires a myth or
  invalidates a benchmark.
- **Distilled SEJ's *SEO Trends 2026*** into the existing contracts: the
  user-expectation and "because Google wants it" tests (`intent-and-content.md`),
  discovery fragmentation and owned-vs-rented surfaces (`entity-and-brand.md`),
  the shifted KPI set — branded search volume, AI mention share, UGC tone,
  owned-audience growth, assisted conversions (`measurement.md`), three new
  growth plays (owned audience, UGC-platform presence, format diversification),
  two new myths, and four dated benchmarks (Google below 90% share, Gen Z Lens
  entry points, 80% still click to verify under an AI Overview).

## v0.1.1 — 2026-07-28

Review pass — defects found by re-auditing the skill against its own rules.

- **Deliverable skeletons now ship with the skill.** They lived only in
  `templates/` at the repo root, which the skills CLI does not copy, so every
  non-Claude agent got a SKILL.md pointing at files it could not read. They are
  embedded in `references/deliverable-templates.md`; the validator fails if the
  root copies drift from the shipped ones (CI proves it can fail).
- **Fixed a broken cross-reference**: the auditor pointed at
  `technical-checks.md#a0-blockers-first` while the heading generated a longer
  slug. Heading shortened, anchor resolves.
- **One spelling standard.** British/American forms were mixed across the
  references (canonicalisation/canonicalization, defence/defense,
  behavior/behavior, optimisation/optimization…), which also broke one anchor.
  Unified to American everywhere, including the anchors the script emits.
- **`page_audit.py` — prose vs link text.** `word_count` counted navigation
  labels, so a nav-heavy page looked substantial and `first_100_words` returned
  menu items instead of the opening answer. Prose and link text are now counted
  separately (`word_count`, `link_text_words`), and the thin-content finding says
  which is which.
- **`page_audit.py` — directive matching by word boundary.** `none` and
  `noindex` were matched as substrings, so body text like "nonexistent" could
  raise a false blocker. Added a third fixture (`edge-page.html`) that would have
  triggered it, plus coverage for `nosnippet` and for harmless `id`/`class`
  attributes on a canonical.
- Deduplicated a benchmark row that presented one 38% figure twice as if it were
  two findings, and attributed both sources.
- SKILL.md gained the **tooling ladder** (crawl export/MCP → GSC/Bing →
  logs → bundled script → manual) and an explicit rule for degraded,
  public-only audits: those findings are inferences and get tiered as such.
- `--base-url` documented as `--file`-only.

## v0.1.0 — 2026-07-28

First release.

- `seo-aeo-audit` skill: ten evidence-based audit tracks (A access & indexation
  economics, B canonicalization, C architecture & link equity, D intent & SERP
  fit, E content value, F extractability/AEO-GEO, G entity & brand consensus,
  H experience signals, I risk & threats, J measurement), a triage model
  (`priority = (impact × confidence) / effort` with evidence-tier weights), and a
  two-file deliverable contract (findings report + change plan).
- Thirteen reference files inside the skill directory, so every distribution
  channel ships the contracts: technical checks, architecture & equity, intent &
  content, AEO/GEO mechanics, entity & brand, experience signals, threats &
  defense, measurement, the ranked play list, experiment design, evidence tiers,
  the myth guard, and dated 2026 benchmarks.
- `scripts/page_audit.py` — stdlib-only page auditor: indexing directives, the
  canonical extra-attribute trap, heading/schema inventory, image alt coverage,
  JS-gated price detection, and an answer-engine **read-budget** estimate
  (~5,700-character first read, link markers versus content). Works offline via
  `--file`.
- `/seo-aeo-audit` slash command, Cursor rule with the contracts embedded inline,
  audit-report and action-plan templates.
- Structural validator (`test/validate.py`) with four-way version sync, reference
  and script checks, and a functional test suite for the auditor
  (`test/test_page_audit.py`) running against two offline fixtures.
- Distribution: Claude Code plugin, vercel skills CLI, npx installer, Cursor,
  POSIX `install.sh`.
