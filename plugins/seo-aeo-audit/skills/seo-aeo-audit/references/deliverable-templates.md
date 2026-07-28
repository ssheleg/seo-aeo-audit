# Deliverable templates

The two files the audit produces. Copy these skeletons verbatim into the target
project; they are duplicated at `templates/*.template.md` in the repo for
non-agent use, and the validator keeps the two copies identical.

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
