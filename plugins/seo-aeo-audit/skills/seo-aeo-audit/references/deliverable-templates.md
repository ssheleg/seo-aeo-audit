# Deliverable templates

The files the audit produces. Copy these skeletons verbatim into the target
project; the first two are duplicated at `templates/*.template.md` in the repo for
non-agent use, and the validator keeps those copies identical.

## Contents

- [docs/seo/audit-<YYYY-MM-DD>.md](#docsseoaudit-yyyy-mm-ddmd)
- [docs/seo/plan-<YYYY-MM-DD>.md](#docsseoplan-yyyy-mm-ddmd)
- [docs/seo/experiments.md](#docsseoexperimentsmd)


Three files, not two — `experiments.md` was named in `experiments.md` as the place
to keep one row per test and had no skeleton anywhere, which is how a deliverable
becomes optional by accident:

1. `docs/seo/audit-<YYYY-MM-DD>.md` — the findings.
2. `docs/seo/plan-<YYYY-MM-DD>.md` — the change plan.
3. `docs/seo/experiments.md` — the running experiment record, appended to rather
   than dated, because it outlives any single audit.

Never overwrite an existing audit or plan silently — write a new dated file, or
ask before replacing.

**The audit's Track coverage table is the one field you must not type.** Its
`Status` column is a closed vocabulary — `observed` · `partial` · `unlooked` ·
`blocked-by <gate>` · `out-of-scope` — carrying one row per track `SKILL.md` step 2
declares, and it is seeded from the instruments:

```bash
python3 "$SKILL_DIR/scripts/preflight.py" --origin https://example.com --format coverage
```

It used to be a free-text `Status` beside a free-text "Not checked" table, with
nothing reading either — so a track that silently returned nothing rendered exactly
like a track that came back clean, in the document the client reads. The seed cannot
write `observed`, which means a row nobody edits says *nobody looked*. The states,
the gate names and why the seed is a floor rather than a verdict:
[preflight.md](preflight.md).

**Its `## Provenance` block is the second field you must not type**, and for the
matching reason: an SEO audit is the most perishable evidence this skill makes, and
through v0.22.0 no script emitted a version, a timestamp or an input set at all — so a
three-month-old audit was indistinguishable from today's. Seed it:

```bash
python3 "$SKILL_DIR/scripts/preflight.py" --origin https://example.com --format provenance
```

It prints what produced the report (`skill`, `script`, `observed_at`, `runtime`,
`args`, `scope`) plus the three fields only the calling harness can supply (`actor`,
`model`, `trace`), each naming its variable when unset rather than vanishing. Under it
go the four invalidators — `site`, `index`, `instrument`, `policy` — because a proof
with no stated expiry reads as permanent. The field set, the redaction rule and the
checker: [preflight.md](preflight.md#seeding-the-reports-provenance-block).

## docs/seo/audit-<YYYY-MM-DD>.md

````markdown
# SEO / AEO audit — {{SITE}}

- **Date:** {{YYYY-MM-DD}}
- **Scope:** {{whole site | template | question}}
- **Markets / languages:** {{...}}
- **Inputs available:** {{GSC, Bing WMT, analytics, logs, crawl export, MCP tools}}
- **Inputs missing (and what that limits):** {{...}}
- **Previous audit:** {{link or "none"}}

## Executive summary

1. {{blocker one — one sentence, with the size of the effect}}
2. {{blocker two}}
3. {{biggest leak}}
4. {{biggest gain}}
5. **Do this first:** {{the single next action}}

## Baseline

| Metric | Value | Period | Source |
|---|---|---|---|
| Organic clicks | | | |
| Organic impressions | | | |
| Indexed vs published URLs | | | |
| Top revenue pages / positions | | | |
| AI mention rate (per engine) | | | |
| AI crawler fetches (per agent) | | | |

## Findings

Repeat this block per finding, most severe first.

### F-{{n}} — {{short title}}

- **Track:** {{A–K}}
- **Issue:** {{what is wrong}}
- **Impact:** {{1–5}} — {{traffic/revenue framing}}
- **Evidence:** {{observation, location, value, date}}
- **Evidence rung:** {{1 logs | 2 Search Console | 3 crawl | 4 field data | 5 third-party index | 6 manual fetch}} — the rung caps the tier (tooling.md)
- **Cause:** {{the mechanism, not the symptom}}
- **Fix:** {{the specific change}}
- **Effort:** {{1–5 engineering days, including release}}
- **Evidence tier:** {{CONFIRMED | STUDY | FIELD | HYPOTHESIS}}
- **Impact:** {{a revenue page · a template · one informational page}}
- **Irreversibility:** {{unrecoverable · recoverable with work · trivially reversible}}
- **Uncertainty:** {{the evidence tier above}}
- **Coordination:** {{how many systems and owners meet at the fix}}
- **Verification:** {{the exact observable that proves it worked}}

## Not checked

Anything **outside** the track list — a market, a template, a subdomain, a surface
nobody had access to. Every track's own gap belongs in Track coverage below, where
it carries a status from the closed vocabulary instead of a sentence.

| Area | Why not | What it would take |
|---|---|---|

## Track coverage

Status is a **closed vocabulary** — `observed` · `partial` · `unlooked` ·
`blocked-by <gate>` · `out-of-scope`. Any status but `observed` or `unlooked` owes
a reason in Notes. Nothing else is a status: a blank cell, a tick or a sentence
here is the defect this table exists to prevent, because a clean track and a track
that never ran then render identically.

Do not type this table — seed it from the instruments, which already know which
sources answered:

```bash
python3 "$SKILL_DIR/scripts/preflight.py" --origin https://example.com --format coverage
```

The seed never writes `observed`: preflight runs before any track does. So a row
left as seeded reads `unlooked`, and forgetting to edit this table produces
*nobody looked*, never a clean report.

| Track | Status | Notes |
|---|---|---|
| A access & indexation | unlooked | |
| B canonicalization | unlooked | |
| C architecture & equity | unlooked | |
| D intent & SERP fit | unlooked | |
| E content value | unlooked | |
| F extractability / AEO | unlooked | |
| G entity & brand | unlooked | |
| H experience signals | unlooked | |
| I risk & threats | unlooked | |
| J measurement | unlooked | |
| K agent surface | unlooked | |

## Provenance — what produced this, and what expires it

**Replace this whole section** with the output of the command below — do not type it.
A field a human fills in after the run is automation debt, and `observed_at` then
records when somebody remembered rather than when an instrument looked. The `Date`
bullet at the top is when this document was written; `observed_at` is when the site
was read, and that is the one that decides whether this report has expired.

```bash
python3 "$SKILL_DIR/scripts/preflight.py" --origin https://example.com \
  --format provenance
```

It prints one row per field — `skill` · `script` · `observed_at` · `runtime` ·
`args` · `scope` · `actor` · `model` · `trace` — and every field prints even when it
cannot be resolved, as `unavailable: <VAR> is not set by this harness`. A field that
vanishes when unavailable is indistinguishable from one nobody checked. `model` is
never inferred: naming the wrong id is worse than saying nothing, and what the
provenance is for is being *investigated*, not looking complete.

Every collector prints the same block under its own output and carries it in
`--format json` as `producer`, so a finding pasted into this report can be traced
back to the run that produced it.

**What invalidates this report.** An overtaken audit is not wrong — it is true about
the site it observed, and it stays. Re-auditing writes a new dated file and names
which row below applies.

| Invalidator | What moved |
|---|---|
| **site** | the audited pages, their markup, `robots.txt` or the sitemap changed |
| **index** | the engine re-crawled or re-ranked — its own state moved, not the site's |
| **instrument** | this skill, its probes or its access changed, so a later run looks elsewhere |
| **policy** | a core or AI-surface update changed the rules the evidence was read under |
````

## Priority — four axes, and no scalar

`priority = (impact × confidence) / effort` used to sit in `SKILL.md` and in the
command, beside a README that refuses "a score out of 100". A pack cannot say
*not a score* and then order its plan by one.

**And the number destroyed the inputs the argument needs.** `4 × 1.0 / 4` and
`1 × 1.0 / 1` both print **1**, so *a template-wide leak, CONFIRMED, four days*
and *one informational page, CONFIRMED, one day* arrive at the same priority and
nobody reading the plan can tell them apart. A product is a one-way function.

<!-- priority-axes: impact, irreversibility, uncertainty, coordination -->

The axes are the manifesto's four (`manifesto` -> *"How many agents,
repositories, services, and owners meet at the change?"*, under *"These axes are
not a fake numerical score"*). Two were absent from this pack entirely, and
`effort` -- a **cost**, not a risk axis -- had been substituted into their place.

| Axis | Question | High · Medium · Low |
|---|---|---|
| **Impact** | What is harmed if the finding is right? | a revenue page · a template · one informational page |
| **Irreversibility** | How hard is the harm to undo once it lands? | unrecoverable · recoverable with work · trivially reversible |
| **Uncertainty** | How much of the effect cannot be checked deterministically? | HYPOTHESIS · FIELD or STUDY · CONFIRMED |
| **Coordination** | How many systems and owners meet at the fix? | many · two · one |

**Irreversibility is the axis this domain most needed and did not have.** A
changed URL has already spread into links, indexes and citations by the time
anyone reconsiders it; a meta description has not. The old formula could not
express the difference, so a redirect plan and a title rewrite competed on one
number.

**Uncertainty is the evidence tier, renamed to its axis rather than multiplied
into a product.** `CONFIRMED` is measured, `HYPOTHESIS` is not, and the tier
already carried that meaning -- what it did not carry was a rank of its own.

**Effort keeps its job and loses its rank.** Recorded per finding in engineering
days including release, it sizes the work and never moves it up or down.

**Ordering rule: the first axis that separates two findings decides.** Impact,
then Irreversibility, then Uncertainty, then Coordination. A reader who
disagrees with the order of two findings can point at the axis that decided it
and argue about that axis alone.

## docs/seo/plan-<YYYY-MM-DD>.md

````markdown
# SEO / AEO change plan — {{SITE}}

- **Date:** {{YYYY-MM-DD}} · **From audit:** {{link}}
- **Owner(s):** {{engineering | content | brand/PR | ops}}
- **Review date:** {{when this plan gets re-checked}}

## 1. Blockers — nothing else counts until these ship

| # | Change | Target (file/template/URL pattern) | Why (mechanism + tier) | Owner | Effort | Verification | Horizon |
|---|---|---|---|---|---|---|---|
| B1 | | | | | | | |

## 2. Leaks — stop the bleeding

| # | Change | Target | Why (mechanism + tier) | Owner | Effort | Verification | Horizon |
|---|---|---|---|---|---|---|---|
| L1 | | | | | | | |

## 3. Gains — earn more visibility

| # | Change | Target | Why (mechanism + tier) | Owner | Effort | Verification | Horizon |
|---|---|---|---|---|---|---|---|
| G1 | | | | | | | |

## 4. Experiments — anything below CONFIRMED

| # | Hypothesis | Cohort (template, n) | Control (n) | Single variable | Duration | Success metric | Decision rule |
|---|---|---|---|---|---|---|---|
| E1 | | | | | | | |

## Sequencing

```
Week 1   {{...}}
Week 2   {{...}}
Week 3–4 {{...}}
Month 2  {{...}}
```

## Rollback

| Change | Rollback method | Blast radius if wrong |
|---|---|---|

## Explicitly out of scope

| Request | Why it is not in the plan | What we do instead |
|---|---|---|

## Human steps (only what genuinely needs a person)

- {{credentials, approvals, business decisions, third-party account access}}
````

## docs/seo/experiments.md

Not dated and not replaced: one row per test, appended, so a later audit can tell a
result from a repetition. The rules for designing what goes in it are in
`experiments.md`; this is only the record.

````markdown
# Experiment record — {{SITE}}

One row per test. Never delete a row: a reverted test is evidence too, and the
next audit needs to know it was tried.

| id | hypothesis | cohort (template, n) | control (n) | single variable | start | end | metric | control delta | test delta | significance | verdict | rolled out? |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E1 | {{...}} | {{...}} | {{...}} | {{...}} | {{YYYY-MM-DD}} | {{YYYY-MM-DD}} | {{...}} | {{...}} | {{...}} | {{...}} | {{win / no effect / loss / invalidated}} | {{yes / no + why}} |

**Verdict values:** `win → rolled out` · `win → not rolled out (why)` ·
`no effect` · `loss → reverted` ·
`invalidated (update / seasonality / instrumentation)`.

**Invalidation check before reading any row:** did the run overlap a core or spam
update? Date-align against `algorithm-updates.md` — a test through a rollout is
invalidated, not inconclusive.
````
