# Defect ledger — fresh-eyes audit of seo-aeo-audit, 2026-08-10

Working ledger for the audit run on branch `audit/2026-08-10-fresh-eyes`, against
`v0.11.2` (commit `743043a`). Every row carries the evidence that would let
someone else re-open it: a `file:line`, a command with its output, or a test name.
Severity is about what the defect does to an audit the skill produces, not about
how hard it is to fix.

`repro` rows were executed in this session; the command is quoted so the claim is
checkable rather than asserted.

## Severity key

| Level | Meaning |
|---|---|
| **critical** | The skill emits a false finding, or suppresses a true one, in ordinary use. An audit built on it misleads a paying client. |
| **high** | A documented claim about the skill is false, or doctrine and code disagree, so an agent must guess and will guess confidently. |
| **medium** | Navigation, provenance or coverage defect. Costs correctness on the margin or on a second reading. |
| **low** | Inconsistency with no path to a wrong finding. |

---

## Class 1 — the instrument manufactures findings (critical)

### D1 · `page_audit.py` reports `noindex` on a page that says `index, follow`

`plugins/seo-aeo-audit/skills/seo-aeo-audit/scripts/page_audit.py:346`

```python
noindex = bool(re.search(r"\bnoindex\b|\bnone\b", directives))
```

`directives` is the concatenation of every `robots` / `googlebot` / `google` meta
content string and the `X-Robots-Tag` header. `max-image-preview:none` and
`max-video-preview:none` are documented Google directives that contain the word
`none`, so the word-boundary match fires on them.

**repro** (this session):

```
$ page_audit.py --file t1.html --format json     # meta robots = "index, follow, max-image-preview:none, max-snippet:-1"
noindex        = True
blocker  noindex   page carries a noindex directive (...)
```

**Why this is the worst finding in the ledger.** `SKILL.md:159-162` makes a
track-A blocker a stop condition — "a track-A blocker (site not fetchable,
noindex in the pre-render source, manual action) makes every other finding
moot". So the agent does not merely add a wrong row; it terminates the audit and
reports a fabricated indexation blocker as the one thing that must happen first.
The false positive is silent on the very sites most likely to carry the directive
(news, paywalled, image-heavy).

The intended check — `content="none"` ≡ `noindex, nofollow`
(`technical-checks.md:74`) — is real, and the fix must keep it while rejecting
`none` as the *value of another key*.

### D2 · `page_audit.py` invents a JS-gated price out of jQuery, or out of correct markup

`page_audit.py:380`

```python
"currency_in_source_only": bool(CURRENCY_RE.search(html)) and not bool(CURRENCY_RE.search(text)),
```

`CURRENCY_RE` is `[$€£¥₽]|\b(usd|eur|gbp|rub)\b`, and it is searched against the
**raw HTML** — scripts, styles and JSON-LD included — while `text` correctly
excludes them (`_visible_text`, via `SKIP_TEXT_TAGS`). Two everyday triggers:

- any inline `<script>` using jQuery's `$`;
- a correct `Product` → `Offer` → `priceCurrency: "USD"` JSON-LD block.

**repro** (this session): both fixtures produced

```
high  price-not-in-text  a price appears in the source but not in extractable text
                         (JS-gated or image) — engines fall back to citing aggregators
                         for your pricing
```

The second case is the perverse one: marking the price up the way
`onpage-checks.md:35` asks for is what triggers the accusation that the price is
hidden. The finding also asserts a consequence ("engines fall back to citing
aggregators") that the script never observed.

### D3 · `page_audit.py` truncates silently and reports the truncated page as measured

`page_audit.py:571` reads `resp.read(max_bytes)` (default 5 MB) and neither the
payload nor the markdown carries a `truncated` flag.

**repro** (this session, local server serving one page twice):

```
$ page_audit.py --url http://127.0.0.1:8731/                  → words 10001
$ page_audit.py --url http://127.0.0.1:8731/ --max-bytes 3000 → words  470
```

Same URL, same run, no warning either time. Every downstream number — word
count, link totals, read budget, alt coverage, schema inventory — is computed on
a fragment and printed as a measurement. A page truncated just under the `thin`
threshold produces a fabricated thin-content finding. This is the exact failure
non-negotiable #8 exists to prevent, in the instrument that ships the #8 caveat.

### D4 · `preflight.py` decides "no CrUX field data" from a 4 KB prefix, and from the wrong signal

`preflight.py:47` — `return r.status, r.read(4096).decode(...)` — caps every probe
body at 4096 bytes. `preflight.py:154` then decides:

```python
has_field = '"loadingExperience"' in body or "loadingExperience" in body
```

Two independent defects in one line:

1. **Wrong signal.** PSI returns the `loadingExperience` key whether or not CrUX
   has data for the URL; the data lives in its `metrics` child. The repo's own
   parser knows this — `psi_pull.py:81` iterates `block.get("metrics") or {}`, and
   `psi_pull.py:109` treats an empty metrics map as absence. So preflight reports
   "CrUX field data present for this URL" from a key that is always present.
2. **Truncated read.** Even the string test is decided on the first 4 KB of a
   response that is hundreds of KB.

The negative branch is stated as a causal fact the script never established:
`"NO CrUX field data for this URL — too little traffic, so lab-only for this
page"`. Absence manufactured from a truncated read, with an explanation attached.

### D5 · `url_inspection.py` prints "Evidence tier: CONFIRMED" even when nothing was inspected

`url_inspection.py:186-187` appends the line after the loop, unconditionally:

```python
lines.append("Evidence tier: CONFIRMED — these are the index's own answers, "
             "not inferences from a fetch. Record the date beside them.")
```

A run where every row is `- **could not inspect**: 403 — either the OAuth scope
…` still ends by declaring its output CONFIRMED. The one instrument in the skill
that can legitimately produce CONFIRMED evidence is also the one that claims the
tier when it produced none.

### D6 · `gsc_pull.py` computes four analyses and prints none of them in the default format

`gsc_pull.py:358-374` builds `ctr_curve`, `ctr_gaps`, `cannibalization` and
`branded_split` into `report`. `gsc_pull.py:376-379` returns early for
`--format json`; the text renderer that follows (`:381-418`) prints
`position_split`, `cliff`, `monthly`, top queries, top pages and sitemaps — and
never touches the other four keys.

`--format text` is the **default** (`:324`). So:

- `SKILL.md:179-186` — "It also derives … cannibalization …, a CTR curve …, the
  pages falling materially below that curve, and the branded / non-branded split.
  The split needs `--brand-terms`; without them it reports itself unavailable
  rather than guessing" — is true only in JSON mode.
- `README.md:188-191` documents the default invocation with no `--format json`.
- `SKILL.md:190` shows the same.

The failure mode is precise: an agent runs the documented command, sees no
cannibalization section, and reports either "no cannibalization found" (false) or
writes the section from nothing. `derive_branded_split`'s careful refusal to
guess (`:233-236`) never reaches the operator on the documented path.

### D7 · `gsc_pull.py`'s cliff detector fires only on ≥90% collapses and never states its threshold

`find_cliff(rows, min_drop=0.9, min_baseline=50.0, window=7, hold_days=14)`
(`:272`). A 60% drop that held for a month is invisible, and the text output
prints nothing when the detector is silent (`:390`). Nothing in the report says
what sensitivity produced the silence, so "no collapse" reads as evidence of no
collapse. `SKILL.md:173-176` and `README.md:198-201` both describe the detector
without its threshold.

### D8 · `gsc_pull.py` truncates the query set with no note, then tells the operator to rank the brief by it

`query(...)` is called with `row_limit` 5000 for queries and pages and 25000 for
pairs (`:350-354`) and never paginates with `startRow`. GSC orders rows by clicks
descending, so truncation removes the long tail — which is where the
`beyond_30` band lives. `position_split` is then printed under the header
`"position split (recent window) — rank the brief by THIS, not by impressions:"`
(`:384`). `measurement.md:13` already names "Sampling, freshness lag, data hiding
on large properties" as the GSC caveat; the instrument does not carry it into its
own output.

`is_noise()` (`:304`) additionally drops every query containing a quote or the
substring `http`, before every derived number, and never reports how many rows it
removed.

### D9 · `sitemap_audit.py` puts its own truncation notice where a piped run cannot see it

`sitemap_audit.py:238-241` prints the URL-cap note to **stderr**, under the
comment "A silent cap reads as 'this is the whole site' and it is not" — and
`render_markdown` (`:164-184`) never prints `sitemaps_skipped` or
`urls_truncated`. The markdown headline stays `**N URL(s)** across **M template
pattern(s)**`. Any capture of stdout, which is how the skill's own examples use
these scripts (`SKILL.md:203`, `> audit.json`), loses the caveat exactly when the
number becomes evidence.

---

## Class 2 — doctrine and instrument contradict each other (high)

### D10 · The auditor emits the H1-count finding its own doctrine calls a non-finding

`onpage-checks.md:37-39`:

> **The H1 count is not one of these checks.** Google states that one H1 and
> several H1s both work, with no penalty for the count (myths.md) — so a "multiple
> H1s" line in an audit spends a finding on a non-finding.

`page_audit.py:449-450` emits exactly that line:

```python
elif r["h1_count"] > 1:
    add("info", "h1-multiple", f"{r['h1_count']} H1 elements", "intent-and-content.md")
```

The message carries no counter-guidance, and its reference points at
`intent-and-content.md`, which contains no H1 guidance at all — the guidance is in
`onpage-checks.md:37-45` and `myths.md:38`. `h1-missing` (`:448`) points at the
same wrong file. Nothing catches it: the validator only resolves anchors of the
form `file.md#anchor` (`validate.py:221`), and these references carry no anchor.

An agent reading `3 H1 elements` in a findings table writes "consolidate to one
H1" into the plan — a myth-list recommendation, produced by the skill's own tool.

### D11 · The `thin` finding cites a study that refutes its premise

`page_audit.py:456-460` fires at `word_count < 300` and points the reader at
`intent-and-content.md#e2-information-gain`. That section
(`intent-and-content.md:117-140`) says:

> Length barely matters (longest third 57.5 vs shortest third 50.5, and the
> middle third breaks the pattern entirely).

The threshold `300` appears nowhere else in the repository — no benchmark, no
reference, no tier, no source. `grep -rn '\b300\b' references/ scripts/` returns
only string-truncation slices. A bare word-count floor is also adjacent to the
myth list, which refuses "publish more pages" and "keyword-style manipulation" on
the same reasoning.

### D12 · `subheads-thin` drops the qualifier its own doctrine attaches

`onpage-checks.md:29` scopes the check to length: fail looks like "0–3 subheads
**on a long page**". `page_audit.py:451` fires at `subheads_h2_h4 < 4` on any
page, so a four-section pricing page collects a `medium` finding the doctrine
does not support.

### D13 · No script finding carries an evidence tier, and non-negotiable #2 requires one

`SKILL.md:23-27` requires every recommendation to carry `CONFIRMED` / `STUDY` /
`FIELD` / `HYPOTHESIS`, and `SKILL.md:251` turns the tier into the confidence
multiplier in `priority = (impact × confidence) / effort`. Every finding the
bundled scripts emit carries `severity` instead (`page_audit.py:412`,
`url_inspection.py:139`, `psi_pull.py:129`, `sitemap_audit.py:142`), and nothing
anywhere maps one to the other.

So the agent must assign the number that drives triage, per finding, with no
rule. The tiers are not interchangeable with severity either: `read-budget` is
`high` severity resting on a `FIELD`, single-engine measurement
(`aeo-geo.md:161`), while `noindex` is `blocker` severity resting on
`CONFIRMED`. Both arrive at the agent as bare severities.

### D14 · One sentence in `tooling.md` caps the same evidence at two different tiers

`tooling.md:22-25`:

> The rung caps the evidence tier: a log line or a Search Console screenshot can
> support `CONFIRMED`; a third-party index estimate cannot rise above `STUDY`,
> and an inference from public data alone stays `HYPOTHESIS` until something
> first-party confirms it.

A third-party index *is* public data, so the clause caps rung 5 at `STUDY` and at
`HYPOTHESIS` in the same breath. `SKILL.md:120` resolves it one way — "That
baseline is capped at `STUDY`" — and `prowl-mcp.md:21` agrees with SKILL.md.
Between `STUDY` (0.7) and `HYPOTHESIS` (0.2) sits a 3.5× difference in computed
priority, so the ambiguity changes the order of the plan.

The same sentence claims the rung caps the tier while mapping only rungs 1, 2 and
5. Rungs 3 (full crawl), 4 (field performance) and 6 (manual fetch + DevTools)
have no cap — and rung 6 is where `page_audit.py` and most `view-source`
observations sit. `evidence-tiers.md:14` independently allows a rung-6
observation to be `CONFIRMED` ("HTTP response, rendered DOM"), which a reader of
`tooling.md` would not expect from the bottom rung of a ladder "ordered by
evidence strength".

### D15 · `onpage-checks.md` overstates what `page_audit.py` automates

`onpage-checks.md:7` — "`scripts/page_audit.py` automates the starred (★) items".
Three of the eight starred items are not per-page mechanical checks and the script
does not perform them:

| Starred check | What the script actually does |
|---|---|
| `onpage-checks.md:26` canonical version of the **site** declared and consistent | reads one page's canonical; cannot compare http/https/www variants |
| `onpage-checks.md:27` title present, **unique**, descriptive | presence and length only; uniqueness is cross-page |
| `onpage-checks.md:35` structured data valid **and matched to visible content** | validates JSON and structural properties; never compares markup claims against visible text |

An agent that trusts the line marks the sweep covered.

---

## Class 3 — counts and claims about the skill that are false (high)

### D16 · The myth count is stated four times, three of them wrong

`myths.md` carries **32** claim rows (`awk` over the table, this session).

| Home | Says | Correct |
|---|---|---|
| `README.md:113` | 32 | ✅ — and it is the only one the validator reads |
| `README.md:336` | 29 | ❌ |
| `SKILL.md:297` | 30 | ❌ |
| `cursor/rules/seo-aeo-audit.mdc:115` | 29 | ❌ |

`validate.py:423` matches one fixed phrase — `myth guard\*\* that refuses (\d+)
popular tactics` — which appears only at `README.md:113`. The guard is green while
three of the four homes are wrong, which is retro standing instruction #4's own
lesson ("count the homes before writing the reconciler") recurring in the guard
written to enforce it.

The short lists also disagree: `SKILL.md:297` says "fourteen most-requested" and
lists 14; the Cursor rule says "thirteen" and lists 13, omitting the
tracking-parameter myth. Nothing compares them.

### D17 · The play count is wrong

`README.md:138` — "60 plays". `growth-plays.md` carries **61** rows: 11 `B*`,
13 `L*`, 29 `G*`, 8 `P*` (counted this session). `CHANGELOG.md:256` records an
earlier correction of the same number from 59 → 60; rows were added afterwards
without a third correction, and no check exists.

### D18 · The Prowl tool count contradicts itself across channels

`README.md:141` says "~408 provider tools". `tooling.md:124` and
`prowl-mcp.md:3` say "~448", and `prowl-mcp.md:53` says "all 448 tools". README
is the public-facing number and it is the wrong one.

### D19 · `CONTRIBUTING.md` names two of the four gate commands, and misdescribes CI

`CONTRIBUTING.md:52-60` — "Both must pass" — lists `validate.py` and
`test_page_audit.py`. `CONTRIBUTING.md:77` — "CI runs the same two plus negative
self-tests".

The real gate is four commands (`scripts/check-docs.sh:7-10`,
`docs/DOCMAP.md:48-49`), and CI runs all four
(`.github/workflows/validate.yml:20-30`). A contributor who follows CONTRIBUTING
runs half the suite and can land a change that breaks
`test_url_inspection.py` or `test_collectors.py` locally green.

`README.md:296-301` and `README.md:347` repeat the same two-command list.
`pipeline.json:100` repeats it a third time as a stage gate.

### D20 · `README.md` describes a two-script repository that ships six scripts

- `README.md:256` — "Text plus two stdlib Python scripts, and nothing else runs."
- `README.md:279` — "`scripts/` page_audit.py, gsc_pull.py (stdlib only)"
- `README.md:288` — the layout block names `test/test_page_audit.py` only

The skill ships six scripts (`page_audit.py`, `gsc_pull.py`, `url_inspection.py`,
`psi_pull.py`, `sitemap_audit.py`, `preflight.py`) and three test files. The
security posture paragraph therefore understates what runs, which is the one
section a reader consults precisely because they do not intend to read the code.
`preflight.py` additionally shells out to `gcloud` (`preflight.py:64`), which no
security statement mentions.

### D21 · `README.md` claims every benchmark is dated; 36 rows are not

`README.md:148` — "every benchmark carries its own date and sample size".

`benchmarks.md` holds 140 substantive rows. **36 of them carry no year at either
row or section level** (computed this session). The whole `## Operational
benchmarks` block (`benchmarks.md:138-153`, 12 rows) has a two-column shape —
`| Metric | Target/observed |` — with no source or date column at all, so no row
in it can be dated by construction. Those are the rows an audit uses to set
verification windows: "Duplicate-group persistence after a fix | up to 2 weeks",
"Recovery after mass accidental `noindex` | 6–12 weeks, staged", "PageRank decay
per hop | ~85%".

`benchmarks.md:3-4` asks the reader to "**Always cite the date**" and
`CONTRIBUTING.md:30-31` makes dates part of the claim. The file that owns dating
is the one violating it.

`PageRank decay per hop | ~85%` is separately suspect on direction: 0.85 is the
classic damping factor, i.e. the share that *passes*, so "decay per hop = ~85%"
reads as its inverse. Undated, unsourced, and used to argue about click depth.

### D22 · `evidence-tiers.md` says the validator compares two copies; it compares four homes

`evidence-tiers.md:7-8` — "`test/validate.py` compares the two copies and fails
when they diverge". `CONTRIBUTING.md:66` and `DOCMAP.md:19` both say four homes,
and `validate.py:460-499` implements four (verbatim for two, weights for SKILL.md,
the `single` token for the `.mdc`). A prose summary of a checker drifting from
the checker — the class standing instruction #3 promoted off the page.

---

## Class 4 — navigation and structure (medium)

### D23 · `technical-checks.md` numbering has holes and the sections are out of order

Heading order in the file: `A0`, `A1`, `A2`, `B`, `B2`, `Migrations`, `A7`,
`Evidence`. `A3`–`A6` do not exist, and `A7` sits after the B-track and the
migration protocol. `SKILL.md:154` sends the reader to "§A7 for tracks A/B", which
resolves, but a numbering scheme with four missing entries reads as content lost
in an edit, and an agent asked for "everything in track A" cannot tell.

`B2` is an `###` nested under `## B` while every other numbered subsection in the
reference set is a `##`.

### D24 · The slash command is a fourth partial copy of the doctrine, reconciled by nothing

`plugins/seo-aeo-audit/commands/seo-aeo-audit.md:18-22` restates the doctrine in
two sentences: evidence discipline plus the myth list. It omits non-negotiables
#2 (tier every recommendation), #5, #6, #7 and #8. `validate.py:165-179` checks
only that the command has a `description` and an `argument-hint`; nothing compares
its doctrine to `SKILL.md`, the way `_nn_count` compares the Cursor channel
(`validate.py:346-366`).

The command is also the only channel that never mentions `preflight.py`, and it
drops "never overwrite an existing audit silently" from step 5.

### D25 · `pipeline.json` is a stale artefact of the previous run, sitting in the repo root

`pipeline.json:8` names skills for a run that finished. `:106` — "No deploy this
run by operator decision: branch to main, release deferred to carry-over CO-2".
`:117` — "CONTRIBUTING.md and the spec lose the nineteen-references drift". Both
describe 2026-08-05. `:100` carries the two-command gate from D19.

A file named `pipeline.json` in the root reads as configuration. The next agent
that opens it inherits a finished run's decisions as policy.

### D26 · The repository has no `CLAUDE.md`

There is no project instruction file. Every routing rule the repo depends on —
DOCMAP as the propagation matrix, the retro's standing instructions binding the
next run, the four-command gate, the "one channel per agent" rule — lives in the
operator's global files (`~/.claude/CLAUDE.md`, `~/CLAUDE.md`), which do not
travel with a clone. An agent invoked in a fresh clone of this repository is told
none of it.

### D27 · Two pipeline ledgers the doctrine requires do not exist

`docs/superpowers/` holds `retro.md`, `plans/`, `specs/` and nothing else. The
board (`docs/superpowers/backlog.md`) and the verification ledger
(`docs/superpowers/verification.md`) are absent, so there is no place where an
unconfirmed shipped requirement or a deferred item survives between runs. Every
carry-over recorded on 2026-08-05 — corpus re-tiering, the `graphify` dependency,
auto-detection for knowledge REQs — exists only in a session that has ended.

---

## Class 5 — provenance and single-home violations (medium)

### D28 · Figures are restated outside `benchmarks.md` without date or source

`DOCMAP.md:17` — a dated number's one home is `benchmarks.md`; everywhere else
quotes it "**with its date and source**, never restate it". Restatements without
either:

| Restated at | Figure | Home |
|---|---|---|
| `technical-checks.md:217` | "70–80% index within 72h in field reports" | `benchmarks.md:146`, itself undated |
| `technical-checks.md:262` | the 50k-page store case, four figures | claimed by A2 itself; `growth-plays.md:32` defers to A2, not to benchmarks |
| `technical-checks.md:295` | "past ~600ms crawl efficiency measurably degrades" | no home; `benchmarks.md:142` carries 200/500ms instead |

DOCMAP names this row **review**, "a checker cannot tell a sourced claim from a
confident one". That is true of sourcing; it is not true of *date presence*, which
is a regex.

### D29 · A patent is used to assert live behaviour, against the tier rule

`technical-checks.md:209-211` opens A2 with "Treat the index as a scarce
resource: Google raises the quality bar when it hits capacity, so every new page
competes for a finite slot (patent *Managing URLs*, US7509315B1)" — stated as
fact, with no tier. `evidence-tiers.md:34-36`: "Leaks and patents describe
architecture, not confirmed live weights. They earn STUDY at best, and only when
the described mechanism matches something you can observe."

### D30 · The read budget is a `FIELD`, one-engine median presented as the window for all answer engines

`architecture-and-equity.md:122` states it correctly: "~5,700 characters
(median; max ~8,000)", measured on ChatGPT Deep Research
(`benchmarks.md:118`, `aeo-geo.md:161` — `FIELD`, ~June 2026, 10+ accounts).

Downstream the qualifiers drop:

- `page_audit.py:38` — `READ_BUDGET_CHARS = 5700`, a hard constant;
- `page_audit.py:480` — the finding reads "only X% of the ~5700-char
  **answer-engine** first read is content", generalizing one engine's median to
  the category, at `high` severity, with no tier;
- `README.md:179` — "a ~5,700-character first read".

Standing instruction #8 names this exact class: "a range stated without the word
*median* that made it".

---

## Class 6 — tier and date discipline is uneven, and the bare copy is the one that travels (high)

### D31 · The same figure carries a tier in one file and none in another

`CONTRIBUTING.md:9-10` — "Every claim in this repo carries an evidence tier". The
corpus applies three different conventions (a per-row `Tier` column in
`growth-plays.md`, a file-level tiering statement in `ranking-model.md:6-9`,
inline labels in `aeo-geo.md`) and in several places none of them. Where the same
claim appears twice, the untiered copy is the one an agent is likelier to lift,
because it reads as settled:

| Claim | Tiered / caveated home | Bare home |
|---|---|---|
| "~70% of the buying process happens before contact" | `growth-plays.md:68` — `STUDY`, with "undated 2025 vendor figures, B2B buyers only … never against the ~1% in-answer click rate" | `demand-and-conversion.md:41` — bare sentence, no tier, no caveat |
| "statistics hallucinate ~40% of the time" | `growth-plays.md:84` — `STUDY` | `intent-and-content.md:254` — bare |
| "82% of domains stayed blocked through the next core update" | `benchmarks.md` — "(82%, 2026)" | `threats-and-defense.md:18` — no date |
| anchor distribution bands, "500 links in 30 days triggered penalties within 48h" | `threats-and-defense.md:330-335` — `FIELD` | no date on either figure |
| the hacked-subdomain recovery timeline | `growth-plays.md:21` — `FIELD` | `threats-and-defense.md:10-11` — bare; `benchmarks.md:153` — undated |

### D32 · Four files carry numeric claims with no tiering convention at all

Every other reference either tiers per claim, per row or per file.
These do neither:

- `experience-signals.md:81-90` — "Measured across 47 pages over 90 days: bounce
  −31%, dwell +187%, average position +6.2, organic +218%, conversion +134%",
  then a five-row lever table in which only row 1 carries a tier. Rows 2–5
  (`mobile CVR ×2`, `CVR +127%`, `pages per session 1.4 → 3.2`, `CVR +89%`) have
  no tier, no date and no named source. The file has no file-level tiering
  statement either. It also states `~130,000 split tests → ~19% conversion cost`
  (`:97-99`) and `session benchmark 30–60s vs ~16s average view` (`:106-108`) the
  same way.
- `intent-and-content.md:15-19` — the intent-validation thresholds ("bounce <40%
  and time on page >2 min indicate a match; bounce >70% indicates a mismatch")
  plus a full before/after case, untiered and undated. These thresholds decide
  whether a page is reported as intent-mismatched, and `experience-signals.md:27`
  argues in the opposite direction for the neighbouring metric — "there is no
  universal CTR benchmark … build a site-specific curve". A universal bounce
  threshold sits badly beside that.
- `intent-and-content.md:77-92` — the five-feature correlation table and the
  additive win rates ("one feature → 13.5–15.4%; four → 68.1%; five → 69.7%"),
  untiered and undated, immediately followed by "Audit each key template against
  those five".
- `experiments.md:53-124` — the results list mixes tiered entries
  (`STUDY ×2, 2026-07` at `:104`, `STUDY, 2026-07` at `:112`) with eight untiered
  ones, including "+34.7% organic at 98.5% significance" and
  "50% of capitalization tests positive, zero negative".
- `entity-and-brand.md:141-143` — "improved answer accuracy ~29% in one presented
  analysis", unnamed and untiered; `:232-234` — the Gen Z / Google Lens figures;
  `:370` — "85 mid-market companies … top-3 in 63% of cases".
- `threats-and-defense.md:70-77` — the 32% prompt-injection rise and the Cornell
  13-word figure, both dated in prose but untiered; `:300-302` — leaked quality
  tags used without the tier `evidence-tiers.md:34-36` assigns to leaks.

### D33 · `algorithm-updates.md` is stamped older than its own newest row, and the repo carries two disagreeing freshness stamps

`references/algorithm-updates.md:3` — "**Verified as of: 2026-07-28.**"
The same file carries a row dated **2026-07-30** (`:52`, the Top Stories inside
AI Overviews entry). Its own refresh protocol requires the stamp to move
(`:134` — "Update the **Verified as of** line at the top").

`README.md:146` states a different stamp for the same corpus: "**Verified as of
2026-08-05.**" Two homes for one fact, no reconciler, and the one inside the
skill — the copy that travels to every agent — is the stale one.

### D34 · "PageRank decays ~85% per hop" — three homes, no source, no tier, and the direction is probably inverted

| Home | Wording |
|---|---|
| `architecture-and-equity.md:11` | "PageRank decays roughly 85% per hop, so anything more than three clicks from a strong node keeps almost nothing" |
| `benchmarks.md:149` | `PageRank decay per hop \| ~85%` |
| `growth-plays.md:87` (L7) | "PageRank decays ~85% per hop" |

0.85 is the classic damping factor — the share that *continues*, not the share
lost. Read as stated (85% lost per hop) three hops retain 0.34%; read the other
way they retain 61%. The two readings prescribe different architectures, and the
claim is used to justify the depth rule in all three files. No source, no date,
no tier anywhere.

The depth rule itself has independent field support
(`architecture-and-equity.md:72-83`, `FIELD`, 2026-06-11), so the rule survives
without this number.

---

## Class 7 — structure, pointers and deliverables (medium)

### D35 · Four section ids are defined twice with different content

`SKILL.md:139` routes track D to **both** `intent-and-content.md` and
`onpage-checks.md`. Both files number their sections in the same namespace:

| id | `intent-and-content.md` | `onpage-checks.md` |
|---|---|---|
| D1 | Intent match is a page-type decision | Can crawlers understand what the page is about |
| D2 | Cannibalization | Duplication and consolidation |
| E1 | What actually makes a page worth ranking | Content substance |
| E2 | Information gain | Metadata as a click and citation surface |

Cross-references that name the file resolve. "Run D1" does not, and
`onpage-checks.md:93` has to disambiguate its own neighbour by writing
"intent-and-content.md E2" inside a table cell that also says "E1".

### D36 · A misaligned table row silently deletes a play's evidence tier

`growth-plays.md:87` (play P5) carries **6 cells** under the 5-column header at
`:81`. Markdown drops the surplus cell, so the rendered table shows P5's
mechanism text in the *Observed* column and **no tier at all** — for the play
that governs decline attribution, in a file whose closing rule is "Never ship a
FIELD or HYPOTHESIS play sitewide" (`:50-51`).

`validate.py:390-404` checks tables for blank lines inside them and not for
column count, so the guard added after tables broke twice does not cover the
third way they break.

### D37 · An inserted block splits the "Evidence to capture" list in two

`experience-signals.md:153-179`: the section opens a bullet list, then at `:158`
a bolded paragraph plus a three-row table are inserted mid-list, and the list
resumes at `:173`. The CWV threshold table is good content in the wrong place —
it reads as part of the evidence list and renders as two unrelated lists.

Those thresholds are also a second home for `psi_pull.py:42-46`
(`2500/4000`, `200/500`, `0.10/0.25`) with nothing comparing them.

### D38 · Two `myths.md` pointers in `linkbuilding.md` point at rows that do not exist

- `linkbuilding.md:43-44` — "See `references/myths.md` on why a large impression
  count at position 50 is not an opportunity." `myths.md` has no such row; the
  claim lives at `SKILL.md:176` and `gsc_pull.py:254`.
- `linkbuilding.md:126-128` — "Never instruct paid link networks, PBNs or bulk
  directory placement. See `references/myths.md` and
  `references/threats-and-defense.md`." `myths.md` carries no PBN, paid-link-network
  or bulk-directory row; `threats-and-defense.md:298-353` (I6) does.

`validate.py:536-555` resolves markdown links, not backticked filenames in prose,
so a pointer to a file that exists but does not contain the claim resolves as
fine. An agent following it finds nothing and fills the gap from memory — which
is the whole mechanism this ledger is about.

### D39 · A third deliverable exists with no template and no mention in the deliverables step

`experiments.md:128` — "Keep one row per test in `docs/seo/experiments.md`", with
a row shape in a code fence. `SKILL.md:265-278` names only
`docs/seo/audit-<date>.md` and `docs/seo/plan-<date>.md`;
`deliverable-templates.md` carries no skeleton for the third file, and the
Cursor rule (`:126-131`) names two.

### D40 · The audit template has no slot for the evidence rung the skill requires

`SKILL.md:169-170` — "state in the report which rung a finding rests on". The
finding block in `deliverable-templates.md:45-56` has `Evidence tier` and no
rung field, and `templates/audit-report.template.md` matches it (the validator
keeps the two identical). A required report element with no slot in the template
is an element that does not get reported.

### D41 · The CSV contract defines a source label the bundled collector cannot produce

`linkbuilding.md:19` defines `gsc-historic-<window>` as a `source` value and
`:49-51` asks for "one earlier comparison window". `gsc_pull.py:344-354` pulls a
single recent window plus a daily history series; it never pulls a query×page set
for an earlier window. `validate.py:247-255` enforces that the label survives in
the reference, so the contract is guarded while the collection path for it does
not exist.

---

## Summary

| Class | Rows | Severity |
|---|---|---|
| 1 — the instrument manufactures findings | D1–D9 | critical |
| 2 — doctrine and instrument contradict | D10–D15 | high |
| 3 — false claims about the skill | D16–D22 | high |
| 4 — navigation and structure | D23–D27 | medium |
| 5 — provenance and single-home | D28–D30 | medium |
| 6 — tier and date discipline | D31–D34 | high |
| 7 — structure, pointers, deliverables | D35–D41 | medium |

**41 defects.** Nine of them make the skill emit or suppress findings in ordinary
use; the repository's four-command gate is green against all forty-one
(`bash scripts/check-docs.sh` → exit 0, this session).

### The four root causes underneath them

1. **A guard is written against the home that broke, not against the fact.** The
   myth-count check reads one sentence in one file while the same count lives in
   four (D16); the tier reconciler was written for two homes and the acceptance
   walk then found four (`retro.md:69-74`); the table guard covers blank lines and
   not column count (D36). Standing instruction #4 says count the homes; nothing
   *counts* them.
2. **Severity is not a tier, and the scripts only emit severity.** Non-negotiable
   #2 makes the tier the multiplier in the triage formula, and no bundled
   instrument produces one (D13). The agent must invent the number that orders the
   plan, per finding, with no documented mapping — and it will invent it
   consistently enough to look deliberate.
3. **A pointer that resolves is not a pointer that answers.** `file.md#anchor` is
   validated; `file.md A2` is validated by nothing; "see `myths.md` on why X" is
   validated by nothing and can be wrong while every link in the repo resolves
   (D38, D28). Progressive disclosure means the agent reads only what it is
   pointed at, so a pointer into empty space is a licence to improvise.
4. **An instrument's silence is not marked as silence.** Truncated reads (D3),
   4 KB probe bodies (D4), row-limit caps (D8), a 90%-only cliff detector (D7),
   stderr-only notices (D9) and an unconditional `CONFIRMED` footer (D5) all hand
   the agent a number or a blank where the honest answer is "not measured". This
   is non-negotiable #8 applied to the doctrine but not to the instruments'
   *coverage* — #8 was read as "declare what you cannot see" and implemented as one
   caveat string about JavaScript.

