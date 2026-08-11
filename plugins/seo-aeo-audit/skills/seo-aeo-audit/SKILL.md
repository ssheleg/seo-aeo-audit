---
name: seo-aeo-audit
description: Use when auditing a website for search and answer-engine visibility, diagnosing traffic or ranking loss, planning what to change, or extracting link-building targets and keywords - "SEO audit" / "сделай SEO-аудит", "technical SEO audit" / "технический аудит сайта", "AEO audit" / "аудит по SEO и AEO", "AI visibility audit", "why did my traffic drop" / "почему упал трафик", "why am I not ranking" / "почему нет позиций", "why doesn't ChatGPT cite us" / "почему нас не цитирует ChatGPT", "indexing issues" / "проверь индексацию", "SEO change plan" / "план правок по SEO", "google core update" / "апдейт гугла", "keywords for linkbuilding" / "ключи для линкбилдинга", "link building brief" / "бриф для линкбилдера". Runs ten evidence-based tracks (access, canonicalization, architecture, intent, content value, extractability/AEO, entity consensus, experience, risk, measurement) and outputs findings, a change plan, and a link-building brief with keyword CSV.
license: MIT
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
8. **Know each instrument's blind spot, and say it in the output.** Rules 1 and
   7 govern what *you* write; they do not see a tool that blends or omits before
   you ever look. Two arrive constantly. A static fetch cannot see JSON-LD that
   the CMS injects with JavaScript, so "no schema found" is a **false finding**
   on any Yoast/RankMath/AIOSEO site — `scripts/page_audit.py` prints the caveat
   next to every schema inventory, and absence is only reportable after a
   rendering check. GA4 with consent-mode modelling returns observed and
   estimated behaviour **inside one number** — see
   [references/measurement.md](references/measurement.md) J1 for the three
   activation conditions, the visible indicator, and the observed-only fallback.
   The rule generalizes: before an instrument's silence becomes a finding,
   establish that the instrument could have seen the thing at all.

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

`scripts/preflight.py` performs the automatable half of step 2 rather than
`scripts/preflight.py` runs the automatable half of this step and reports which
independent gate a failure hit — Search Console, the GSC API and PageSpeed all
answer `403` for different reasons. Read `references/preflight.md` for exactly
what it probes and what it leaves to you (Bing/Yandex, analytics, server logs,
crawl exports and every MCP tool). **A green preflight is not a covered step.**

```bash
# Claude Code plugin: ${CLAUDE_PLUGIN_ROOT} expands inside skill content.
SKILL_DIR="${CLAUDE_PLUGIN_ROOT}/skills/seo-aeo-audit"
# Any other channel: the base directory the harness names when it loads this
# skill — the directory this SKILL.md sits in. Confirm before relying on it:
ls "$SKILL_DIR/scripts/preflight.py"
```

`No such file or directory` here is not a missing feature and not a reason to
proceed quietly. It means the six instruments are unreachable, so every check they
would have made drops to the bottom rung of the evidence ladder — and a finding's
rung caps its tier. Say so in the three-line status; an audit that silently becomes
a manual one has changed what its conclusions are worth (non-negotiable #6).

```bash
python3 "$SKILL_DIR/scripts/preflight.py" --site sc-domain:example.com --origin https://example.com
```

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
| A | Access & indexation economics | Can bots fetch, render and afford this? Where is crawl budget burned? | [technical-checks.md](references/technical-checks.md) |
| B | Canonicalization & duplication | Which URL is canonical, and does the engine agree — hreflang included? | [technical-checks.md](references/technical-checks.md) |
| C | Architecture & link equity | Do money pages get authority, depth and crawl frequency? | [architecture-and-equity.md](references/architecture-and-equity.md) |
| D | Intent & SERP fit | Does each page match the SERP, and do pages cannibalise? | [intent-and-content.md](references/intent-and-content.md) + [onpage-checks.md](references/onpage-checks.md) |
| E | Content value | A reason to rank that AI cannot replicate? | [intent-and-content.md](references/intent-and-content.md) + [ranking-model.md](references/ranking-model.md) |
| F | Extractability & AEO/GEO | Can an answer engine retrieve, read and quote it? | [aeo-geo.md](references/aeo-geo.md) |
| G | Entity & brand consensus | Do models know the brand, consistently, and name it? | [entity-and-brand.md](references/entity-and-brand.md) |
| H | Experience, conversion & attribution | Task completed here or bounced back? Converted, and measured? | [experience-signals.md](references/experience-signals.md) + [demand-and-conversion.md](references/demand-and-conversion.md) |
| I | Risk & threats | Penalties, hijacks, injections, takedowns. | [threats-and-defense.md](references/threats-and-defense.md) |
| J | Measurement | Will anyone be able to tell if the plan worked? | [measurement.md](references/measurement.md) |

**Discover is not one of the ten tracks, and it is not part of track A.** It has
its own ranking pass, its own gate (two metatags, without which no card renders at
all) and its own freshness curve, so a site where Discover is a material traffic
source needs [references/discover.md](references/discover.md) run as an eleventh
pass — and a site where it is not can skip it entirely. Check the GSC Discover
report before deciding: the reference shipped reachable only from the list at the
bottom of this file, which meant an agent working the tracks in order never opened
it.

**Before any decline diagnosis**, run the date-alignment and update-response
protocol in [references/algorithm-updates.md](references/algorithm-updates.md) —
"a core update hit us" is not a finding, and half the documented GSC outages
coincided with rollouts.

Each track has two halves: the **diagnostic** work (what is wrong and why) and a
**mechanical sweep** for completeness —
[technical-checks.md](references/technical-checks.md) §A3 for tracks A/B and
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

**The six bundled scripts** — `preflight.py`, `gsc_pull.py`, `page_audit.py`,
`url_inspection.py`, `sitemap_audit.py`, `psi_pull.py` — collect the mechanical
half of every track. Read `references/scripts.md` for invocation, flags, quotas
and the per-script limits.

**Four traps that decide whether a finding is real:**

- `page_audit.py`'s schema inventory reads **server-rendered HTML only**. Where
  a CMS injects JSON-LD with JavaScript, an empty inventory is not evidence of
  absent markup (non-negotiable #8).
- `--format json` emits an **array**, one object per page, even for one URL:
  index `data[0]`.
- A response cut off by `--max-bytes` drops every count-based finding rather
  than publishing a fragment as a measurement.
- **Every emitted finding carries an evidence tier as well as a severity, and
  only the tier enters the triage formula.** Severity is how loud a finding is;
  the tier is what backs it. `url_inspection.py` asks the index rather than
  inferring from a fetch, which is the only way a finding reaches `CONFIRMED` —
  at a quota of 2000/day and 600/minute per property, so sample one URL per
  template plus the pages a finding is actually about.
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

Write these files, seeded from the skeletons in
[references/deliverable-templates.md](references/deliverable-templates.md).
Never overwrite an existing audit or plan silently — write a new dated file, or
ask first:

- `docs/seo/audit-<YYYY-MM-DD>.md` — findings. Per finding: **Issue · Impact ·
  Evidence · Evidence rung · Cause · Fix · Effort · Evidence tier · Verification**.
  The rung is which source the observation came from, and it caps the tier
  ([references/tooling.md](references/tooling.md)).
- `docs/seo/plan-<YYYY-MM-DD>.md` — the change plan. Per change: exact target
  (`path/file:line`, template name, or URL pattern), the change itself, **why**
  (mechanism + evidence tier), the expected effect and by when, how to verify,
  and how to roll it back.

- `docs/seo/experiments.md` — the running experiment record, one row per test,
  appended rather than dated because it outlives any single audit. Required as soon
  as the plan has an Experiments bucket, which anything below CONFIRMED puts there.

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

The ten most-requested of the **32** refuted claims. Each is refuted by 2026
evidence; the full list, with the counter-evidence and the working alternative
for each, is in [references/myths.md](references/myths.md) — read it before
answering a tactic question that is not on this short list.

- `llms.txt` as a ranking or citation lever · Markdown mirrors of HTML pages as
  a GEO tactic · "chunk your content for the retriever" · rewriting text
  specifically "for AI" · schema volume as an AI-citation lever · FAQPage markup
  for rich results (retired by Google) · AMP for ranking advantage · updating the
  publish date as a freshness signal · "just add more pages" · scaled AI content
  as a growth strategy

When the user asks for one of these, say plainly what the evidence shows, offer
the nearest thing that does work, and move on.

## References

- [ranking-model.md](references/ranking-model.md) — how ranking actually works.
- [technical-checks.md](references/technical-checks.md) — tracks A/B.
- [architecture-and-equity.md](references/architecture-and-equity.md) — track C.
- [intent-and-content.md](references/intent-and-content.md) — tracks D/E.
- [onpage-checks.md](references/onpage-checks.md) — the on-page completeness sweep per template.
- [aeo-geo.md](references/aeo-geo.md) — track F.
- [entity-and-brand.md](references/entity-and-brand.md) — track G.
- [experience-signals.md](references/experience-signals.md) — track H.
- [demand-and-conversion.md](references/demand-and-conversion.md) — track H+.
- [threats-and-defense.md](references/threats-and-defense.md) — track I.
- [measurement.md](references/measurement.md) — track J.
- [discover.md](references/discover.md) — Google Discover as its own surface.
- [tooling.md](references/tooling.md) — check → tool routing.
- [prowl-mcp.md](references/prowl-mcp.md) — bulk competitive, demand and AI-surface data through one MCP endpoint.
- [growth-plays.md](references/growth-plays.md) — the ranked play list the plan draws from.
- [experiments.md](references/experiments.md) — split-test design rules for anything below CONFIRMED.
- [evidence-tiers.md](references/evidence-tiers.md) — the tier definitions and how they gate recommendations.
- [myths.md](references/myths.md) — the refuted list.
- [benchmarks.md](references/benchmarks.md) — dated 2026 numbers to size opportunities and set expectations.
- [algorithm-updates.md](references/algorithm-updates.md) — dated Google update timeline.
- [linkbuilding.md](references/linkbuilding.md) — extracting link-building targets.
- [deliverable-templates.md](references/deliverable-templates.md) — the audit-report and change-plan skeletons.
