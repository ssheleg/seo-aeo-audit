# Deliverable templates

The files the audit produces. Copy these skeletons verbatim into the target
project; the first two are duplicated at `templates/*.template.md` in the repo for
non-agent use, and the validator keeps those copies identical.

Three files, not two — `experiments.md` was named in `experiments.md` as the place
to keep one row per test and had no skeleton anywhere, which is how a deliverable
becomes optional by accident:

1. `docs/seo/audit-<YYYY-MM-DD>.md` — the findings.
2. `docs/seo/plan-<YYYY-MM-DD>.md` — the change plan.
3. `docs/seo/experiments.md` — the running experiment record, appended to rather
   than dated, because it outlives any single audit.

Never overwrite an existing audit or plan silently — write a new dated file, or
ask before replacing.

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

- **Track:** {{A–J}}
- **Issue:** {{what is wrong}}
- **Impact:** {{1–5}} — {{traffic/revenue framing}}
- **Evidence:** {{observation, location, value, date}}
- **Evidence rung:** {{1 logs | 2 Search Console | 3 crawl | 4 field data | 5 third-party index | 6 manual fetch}} — the rung caps the tier (tooling.md)
- **Cause:** {{the mechanism, not the symptom}}
- **Fix:** {{the specific change}}
- **Effort:** {{1–5 engineering days, including release}}
- **Evidence tier:** {{CONFIRMED | STUDY | FIELD | HYPOTHESIS}}
- **Priority:** {{(impact × confidence) / effort}}
- **Verification:** {{the exact observable that proves it worked}}

## Not checked

| Area | Why not | What it would take |
|---|---|---|

## Track coverage

| Track | Status | Notes |
|---|---|---|
| A access & indexation | | |
| B canonicalization | | |
| C architecture & equity | | |
| D intent & SERP fit | | |
| E content value | | |
| F extractability / AEO | | |
| G entity & brand | | |
| H experience signals | | |
| I risk & threats | | |
| J measurement | | |
````

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
