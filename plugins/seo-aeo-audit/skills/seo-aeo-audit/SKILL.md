---
name: seo-aeo-audit
description: Use when auditing a website for search and answer-engine visibility, diagnosing traffic or ranking loss, planning what to change, or extracting link-building targets and keywords - "SEO audit" / "сделай SEO-аудит", "technical SEO audit" / "технический аудит сайта", "AEO audit" / "аудит по SEO и AEO", "AI visibility audit", "why did my traffic drop" / "почему упал трафик", "why am I not ranking" / "почему нет позиций", "why doesn't ChatGPT cite us" / "почему нас не цитирует ChatGPT", "indexing issues" / "проверь индексацию", "SEO change plan" / "план правок по SEO", "google core update" / "апдейт гугла", "keywords for linkbuilding" / "ключи для линкбилдинга", "link building brief" / "бриф для линкбилдера". Runs ten evidence-based tracks (access, canonicalization, architecture, intent, content value, extractability/AEO, entity consensus, experience, risk, measurement) and outputs findings, a change plan, and a link-building brief with keyword CSV.
---

# seo-aeo-audit — audit search + answer-engine visibility, then ship a plan

One job: **look at a real site, prove what is wrong with evidence, and hand back
a prioritized plan of changes** that covers classic search (Google, Yandex, Bing)
and answer engines (AI Overviews / AI Mode, ChatGPT, Perplexity, Claude, Copilot,
Gemini, Alice AI).

Not this skill's job: writing the content, building the pages, buying links. It
ends at a verified diagnosis and an executable plan.

## Non-negotiables

1. **Evidence or silence.** Every finding carries: what you observed, where
   (`URL`, `file:line`, report name), the observed value, and the date. Never
   report a finding you did not verify on this site. "Best practice says" is not
   evidence.
2. **Label the evidence tier** of every recommendation (see
   [references/evidence-tiers.md](references/evidence-tiers.md)):
   `CONFIRMED` (documented by the engine or reproduced on this site) ·
   `STUDY` (published multi-site data) · `FIELD` (single-case report) ·
   `HYPOTHESIS`. Never let a HYPOTHESIS out-rank a CONFIRMED blocker.
3. **Diagnose before prescribing.** No fix goes in the plan until its cause is
   located. "Add schema" is not a diagnosis.
4. **Refuse the myth list.** See "Myth guard" below — recommending those wastes
   the client's budget and is a defect, not a nicety.
5. **Never recommend deceptive tactics.** Cloaking, fabricated consensus
   networks, review manipulation, competitor takedown abuse and click-signal
   spoofing stay out of the plan. They appear in this skill only in
   [references/threats-and-defense.md](references/threats-and-defense.md), as
   things to **detect and defend against**.
6. **State what you could not check.** A missing GSC login is a gap in the
   report, not a silent omission.
7. **Never blend measured with assumed.** When one deliverable carries both —
   a link-building CSV always does — a `source` column separates them and the
   volume cells of an unmeasured row stay **blank, not zero**. A `0` reads as
   "measured, no demand"; blank reads as "nobody has checked". The distinction
   matters most in work someone else executes on a budget.

## Step 0 — Detect mode, never ask twice

Inspect first, then act. In order:

1. Read `docs/seo/` (or the path the user names). If a previous audit exists,
   this run is a **re-audit**: diff against it and lead with what changed.
2. Establish what you can reach: the live site, a staging URL, `robots.txt`,
   `sitemap.xml`, Search Console / Bing Webmaster / analytics access, a crawl
   export (Screaming Frog, Sitebulb), server logs, any MCP tools connected
   (Ahrefs, GSC, analytics, a crawler MCP, or the
   [Prowl MCP](references/prowl-mcp.md) for bulk competitive and demand data
   without a per-vendor seat).
   **Test the access, do not assume it.** A connected server is not a working
   one: API tiers gate endpoints, and tokens carry narrower scopes than the
   dashboard suggests. Probe the one call each source is there for before you
   plan around it, and record what came back — "connected but returns
   `Insufficient plan`" is a finding the next audit needs.
3. Pick the scope with the user only if the answer changes the work: whole site,
   one template/section, one question ("why did traffic drop in May"), or a
   **link-building extraction** — targets, keywords and anchors for a contractor.
   That one is a deliverable rather than a diagnosis: read
   [references/linkbuilding.md](references/linkbuilding.md) when it is the ask.
   It works with or without Search Console.
4. Report status in three lines — inputs available, inputs missing, scope — then
   start. Suggest exactly one next action at the end of every run.

Access rules: read-only by default. Never submit forms, request indexing,
disavow links, or change a live property without explicit approval in this
session; those are outward-facing actions.

## Step 1 — Baseline before opinions

Record, with dates, so every later claim can be measured against it:

- organic clicks / impressions / avg position per country and device, 12 months
  (GSC + Bing), and the drop or plateau window if there is one;
- indexed vs published URL counts per template (`site:` is a smell test, GSC
  Pages report is the number);
- top-20 revenue or conversion pages and their current positions;
- AI-surface baseline: run the brand and category prompt set from
  [references/aeo-geo.md](references/aeo-geo.md) against each engine you can
  reach, and record answers verbatim;
- which AI crawlers actually fetch the site (server logs; forward-confirmed
  reverse DNS to filter spoofers) and which AI referrers appear in analytics;
- the **update timeline**: date-align every change in the curve against
  [references/algorithm-updates.md](references/algorithm-updates.md) before
  forming any hypothesis about a cause.

**When there is no first-party access at all**, say so in the three-line status
and fall back to what a third-party index can establish: what the domain ranks
for today, how large its link profile is against a sized competitive set, and
whether its target phrases carry measurable demand
([references/prowl-mcp.md](references/prowl-mcp.md)). That baseline is capped at
`STUDY` and cannot answer "why is this page not indexed" — but it is enough to
tell a cold start from a decline, and those need opposite plans.

If the site claims a traffic drop, **first separate reporting failure from
ranking failure**: a frozen GSC report pins clicks at one date while a real hit
keeps producing fresh declining points. Cross-check GA4 sessions, server logs and
an independent rank tracker before diagnosing an algorithmic cause.

## Step 2 — The ten tracks

Run every track that is in scope. Each has its own reference file with the
concrete checks, the 2026-current gotchas, and the evidence to capture.

| # | Track | Answers | Reference |
|---|---|---|---|
| A | Access & indexation economics | Can bots fetch, render and afford to index this? Where is crawl budget burned? | [technical-checks.md](references/technical-checks.md) |
| B | Canonicalization & duplication | Which URL is the one true URL, and does the engine agree — including across locales (hreflang)? | [technical-checks.md](references/technical-checks.md) |
| C | Architecture & link equity | Do the money pages get authority, depth and crawl frequency? | [architecture-and-equity.md](references/architecture-and-equity.md) |
| D | Intent & SERP fit | Does each page match what the SERP rewards, and do pages fight each other? | [intent-and-content.md](references/intent-and-content.md) + [onpage-checks.md](references/onpage-checks.md) |
| E | Content value | Is there a reason to rank this page that AI cannot replicate? | [intent-and-content.md](references/intent-and-content.md) + [ranking-model.md](references/ranking-model.md) |
| F | Extractability & AEO/GEO | Can an answer engine retrieve, read and quote the answer? | [aeo-geo.md](references/aeo-geo.md) |
| G | Entity & brand consensus | Do the models know what this brand is, consistently, and name it? | [entity-and-brand.md](references/entity-and-brand.md) |
| H | Experience, conversion & attribution | Do users complete the task here or bounce back to the SERP? Does it convert, and is the conversion measured? | [experience-signals.md](references/experience-signals.md) + [demand-and-conversion.md](references/demand-and-conversion.md) |
| I | Risk & threats | Penalties, hijacks, injections, adversaries, legal takedowns. | [threats-and-defense.md](references/threats-and-defense.md) |
| J | Measurement | Will anyone be able to tell whether the plan worked? | [measurement.md](references/measurement.md) |

**Before any decline diagnosis**, run the date-alignment and update-response
protocol in [references/algorithm-updates.md](references/algorithm-updates.md) —
"a core update hit us" is not a finding, and half the documented GSC outages
coincided with rollouts.

Each track has two halves: the **diagnostic** work (what is wrong and why) and a
**mechanical sweep** for completeness —
[technical-checks.md](references/technical-checks.md) §A7 for tracks A/B and
[onpage-checks.md](references/onpage-checks.md) for D/E. Run the diagnosis first;
the sweep afterwards catches the boring failures, and only sweep items with an
observable impact get promoted into the findings table.

**Order matters.** A track-A blocker (site not fetchable, noindex in the
pre-render source, manual action) makes every other finding moot — a manual
action is a binary multiplier: nothing you improve counts until it is lifted.
Work A → B → C before spending time on F/G.

**Evidence ladder** — the full routing lives in
[references/tooling.md](references/tooling.md); it is ordered by **evidence
strength**, not convenience: server logs → Search Console / Bing / Yandex →
full crawl → field performance data → third-party indices → manual fetch and
DevTools. Use the highest rung you can actually reach for each check, and state
in the report which rung a finding rests on. A public-only audit with no property
access is valid work, but its indexation and query findings are inferences, not
observations, and get tiered accordingly.

`scripts/gsc_pull.py` (stdlib-only, local ADC auth) pulls the half of the picture
no crawl can see: which queries a property actually surfaces for, at what position,
and whether a drop is a *cliff that held* rather than a decline. Run it before
rating any finding by impact — a large impression count at position 50 is not an
opportunity, and only the position split shows that.

```bash
python3 scripts/gsc_pull.py --list
python3 scripts/gsc_pull.py --site sc-domain:example.com --quota-project my-proj
```

`scripts/page_audit.py` (stdlib-only, no network required in `--file` mode)
collects the per-page mechanical evidence for tracks A, B, C and F — canonical
traps, robots directives, heading and schema inventory, and the answer-engine
**read-budget estimate**. Paths below are relative to this skill's own directory;
run it on a representative URL per template, not on a single page.

```bash
python3 scripts/page_audit.py --url https://example.com/pricing --format markdown
python3 scripts/page_audit.py --file ./saved.html --base-url https://example.com/pricing
python3 scripts/page_audit.py --url-list urls.txt --format json > audit.json
```

## Step 3 — Triage

Score every finding, then sort. Do not present an unranked list.

```
priority = (impact × confidence) / effort
```

- **impact** 1–5: revenue pages blocked = 5; a template-wide leak = 4; a single
  informational page = 1. Estimate in traffic or revenue terms where the baseline
  allows it.
- **confidence**: CONFIRMED 1.0 · STUDY 0.7 · FIELD 0.4 · HYPOTHESIS 0.2.
- **effort** 1–5 in engineering days, counting release process, not just the
  edit.

Group the output into four buckets, in this order:

1. **Blockers** — indexation, penalties, hijacks, revenue pages unreachable.
2. **Leaks** — crawl budget, equity, cannibalization, read-budget waste.
3. **Gains** — intent fit, information gain, extractability, entity consensus.
4. **Experiments** — anything below CONFIRMED that deserves a split test rather
   than a rollout. Design them per
   [references/experiments.md](references/experiments.md); never roll a
   HYPOTHESIS sitewide.

## Step 4 — Deliverables

Write two files, seeded from the skeletons in
[references/deliverable-templates.md](references/deliverable-templates.md).
Never overwrite an existing audit or plan silently — write a new dated file, or
ask first:

- `docs/seo/audit-<YYYY-MM-DD>.md` — findings. Per finding: **Issue · Impact ·
  Evidence · Cause · Fix · Effort · Evidence tier · Verification**.
- `docs/seo/plan-<YYYY-MM-DD>.md` — the change plan. Per change: exact target
  (`path/file:line`, template name, or URL pattern), the change itself, **why**
  (mechanism + evidence tier), the expected effect and by when, how to verify,
  and how to roll it back.

Executive summary rules: 5 bullets maximum, the top three blockers, the expected
size of the prize, and the one thing that must happen first. Write for a
technically literate non-specialist; expand jargon on first use.

## Step 5 — Verify, then follow up

- State the verification method per change *before* it ships (GSC Pages report
  moves from X to Y; the URL Inspection live test shows the canonical accepted;
  the log shows Googlebot fetching `/_next/static/`; the prompt set names the
  brand in N of 10 answers).
- Set the check-back window honestly: indexing 2–8 weeks, canonical group
  splits up to 2 weeks after the fix, core-update effects a quarter, AI training
  effects months. Say when you cannot promise a date.
- On re-audit, diff against the previous report and mark each earlier finding
  `fixed` / `partially fixed` / `unchanged` / `regressed`, with fresh evidence.

## Myth guard — do not put these in a plan

The fourteen most-requested of the **30** refuted claims. Each is refuted by 2026
evidence; the full list, with the counter-evidence and the working alternative
for each, is in [references/myths.md](references/myths.md) — read it before
answering a tactic question that is not on this short list.

- `llms.txt` as a ranking or citation lever · Markdown mirrors of HTML pages as
  a GEO tactic · "chunk your content for the retriever" · rewriting text
  specifically "for AI" · schema volume as an AI-citation lever · FAQPage markup
  for rich results (retired by Google) · AMP for ranking advantage · updating the
  publish date as a freshness signal · "just add more pages" · disavowing on a
  third-party toxicity score · buying an "AI visibility" number as a single KPI ·
  self-promotional "best [category]" listicles as an AEO play · scaled AI content
  as a growth strategy · `Disallow`-ing tracking-parameter URLs to protect crawl
  budget (technical-checks.md A2 owns the mechanism).

When the user asks for one of these, say plainly what the evidence shows, offer
the nearest thing that does work, and move on.

## References

- [references/ranking-model.md](references/ranking-model.md) — how ranking actually works: systems vs signals, the three that carry weight, E-E-A-T's real status, query-dependent weighting.
- [references/technical-checks.md](references/technical-checks.md) — tracks A/B: crawl, render, index, canonical, robots, sitemaps, hreflang/international duplication, migrations, plus the mechanical completeness sweep.
- [references/architecture-and-equity.md](references/architecture-and-equity.md) — track C: internal links, hubs, orphans, depth, read-budget-aware navigation.
- [references/intent-and-content.md](references/intent-and-content.md) — tracks D/E: intent match, cannibalization, information gain, defensible content types.
- [references/onpage-checks.md](references/onpage-checks.md) — the on-page completeness sweep per template.
- [references/aeo-geo.md](references/aeo-geo.md) — track F: how answer engines retrieve and cite, per-engine mechanics, the prompt set.
- [references/entity-and-brand.md](references/entity-and-brand.md) — track G: entity graph, cross-profile consistency, ghost citations, sentiment sources.
- [references/experience-signals.md](references/experience-signals.md) — track H: CWV/INP/LCP triage, satisfaction signals, CRO × SEO.
- [references/demand-and-conversion.md](references/demand-and-conversion.md) — track H+: conversion elements, lead capture, call/offline attribution, paid × organic alignment.
- [references/threats-and-defense.md](references/threats-and-defense.md) — track I: penalties, negative SEO, prompt injection, takedown abuse, hijacks.
- [references/measurement.md](references/measurement.md) — track J: GSC/Bing/AI reporting surfaces, per-engine metrics, what not to measure.
- [references/tooling.md](references/tooling.md) — check → tool routing, the evidence ladder, DevTools recipes, where automation stops.
- [references/prowl-mcp.md](references/prowl-mcp.md) — bulk competitive, demand and AI-surface data through one MCP endpoint: which tools serve which track, the two-index cross-check habit, spam-score filtering on anchors, and the operating gotchas.
- [references/growth-plays.md](references/growth-plays.md) — the ranked play list the plan draws from, with expected effect and evidence tier.
- [references/experiments.md](references/experiments.md) — split-test design rules for anything below CONFIRMED.
- [references/evidence-tiers.md](references/evidence-tiers.md) — the tier definitions and how they gate recommendations.
- [references/myths.md](references/myths.md) — the refuted list, with sources.
- [references/benchmarks.md](references/benchmarks.md) — dated 2026 numbers to size opportunities and set expectations.
- [references/algorithm-updates.md](references/algorithm-updates.md) — dated Google update timeline, platform changes, the update-response protocol, and how to keep the file current.
- [references/linkbuilding.md](references/linkbuilding.md) — extracting link-building targets, keywords and anchors for any site, with or without Search Console; the measured-vs-candidate rule and the CSV contract.
- [references/deliverable-templates.md](references/deliverable-templates.md) — the audit-report and change-plan skeletons.
