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
2. Establish what you can reach — live site, staging, `robots.txt`, `sitemap.xml`,
   Search Console / Bing / analytics, a crawl export, server logs, and any MCP
   connected ([Prowl](references/prowl-mcp.md) covers bulk competitive and demand
   data without a per-vendor seat).
   **Test the access, do not assume it.** A connected server is not a working one:
   tiers gate endpoints and tokens carry narrower scopes than the dashboard
   suggests. Probe the one call each source is there for, and record what came
   back — *"connected but returns `Insufficient plan`"* is a finding the next
   audit needs.
3. Pick the scope with the user **only if the answer changes the work**: whole
   site, one template, one question, or a **link-building extraction** — which is
   a deliverable rather than a diagnosis, works with or without Search Console,
   and has its own file ([linkbuilding.md](references/linkbuilding.md)).
4. Report status in three lines — inputs available, inputs missing, scope — then
   start. Suggest exactly one next action at the end of every run.

```bash
python3 "$SKILL_DIR/scripts/preflight.py" --site sc-domain:example.com --origin https://example.com
```

It names **which** gate a failure hit — `login`, `quota-project`,
`api-not-enabled`, `scope` and `permission` fail for different reasons and most of
them say `403`. What it probes, and the large half it leaves to you:
[preflight.md](references/preflight.md).
**A green preflight is not a covered step.**

Resolve `$SKILL_DIR` and confirm it before relying on it —
`${CLAUDE_PLUGIN_ROOT}/skills/seo-aeo-audit` under the Claude Code plugin, the
directory this file sits in anywhere else; [scripts.md](references/scripts.md)
has both forms and every invocation.

**`No such file or directory` is not a missing feature and not a reason to proceed
quietly.** It means the instruments are unreachable, so every check they would have
made drops to the bottom rung of the evidence ladder — and a rung caps a tier. Say
so in the three-line status: an audit that silently becomes a manual one has
changed what its conclusions are worth (non-negotiable #6).

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

**With no first-party access at all**, say so in the three-line status and fall
back to what a third-party index establishes — current rankings, link profile
against a sized competitive set, whether the target phrases carry demand
([prowl-mcp.md](references/prowl-mcp.md)). That baseline caps at `STUDY` and
cannot answer *"why is this page not indexed"*, but it tells a cold start from a
decline, and those need opposite plans.

If the site claims a traffic drop, **first separate reporting failure from
ranking failure**: a frozen GSC report pins clicks at one date while a real hit
keeps producing fresh declining points. Cross-check GA4 sessions, server logs and
an independent rank tracker before diagnosing an algorithmic cause.

## Step 2 — The ten tracks

Run every track in scope. Each has its own file with the concrete checks, the
2026-current gotchas, and the evidence to capture.

| # | Track | Answers | Reference |
|---|---|---|---|
| A | Access & indexation economics | Can bots fetch, render and afford this? Where is crawl budget burned? | [technical-checks.md](references/technical-checks.md) |
| B | Canonicalization & duplication | Which URL is canonical, and does the engine agree — hreflang included? | [technical-checks.md](references/technical-checks.md) |
| C | Architecture & link equity | Do money pages get authority, depth and crawl frequency? | [architecture-and-equity.md](references/architecture-and-equity.md) |
| D | Intent & SERP fit | Does each page match the SERP, and do pages cannibalise? | [intent-and-content.md](references/intent-and-content.md) + [onpage-checks.md](references/onpage-checks.md) |
| E | Content value | A reason to rank that AI cannot replicate, and does it read as written by one? | [intent-and-content.md](references/intent-and-content.md) + [ranking-model.md](references/ranking-model.md) |
| F | Extractability & AEO/GEO | Can an answer engine retrieve, read and quote it? | [aeo-geo.md](references/aeo-geo.md) |
| G | Entity & brand consensus | Do models know the brand, consistently, and name it? | [entity-and-brand.md](references/entity-and-brand.md) |
| H | Experience, conversion & attribution | Task completed here or bounced back? Converted, and measured? | [experience-signals.md](references/experience-signals.md) + [demand-and-conversion.md](references/demand-and-conversion.md) |
| I | Risk & threats | Penalties, hijacks, injections, takedowns. | [threats-and-defense.md](references/threats-and-defense.md) |
| J | Measurement | Will anyone be able to tell if the plan worked? | [measurement.md](references/measurement.md) |
| K | Agent surface | Can a machine discover, authenticate and transact here? | [agent-readiness.md](references/agent-readiness.md) |

**Track K is conditional.** Run it when the site sells something an agent could
plausibly buy, call or automate; skip it for a content site with no programmable
surface. It carries a rule the other ten do not need — **presence is `CONFIRMED`,
effect is mostly `HYPOTHESIS`** — so most of it belongs in Experiments until
first-party logs show agent traffic. When to run it, its cheapest check, and why a
third-party "agent-readiness score" is a checklist generator rather than a target:
[agent-readiness.md](references/agent-readiness.md).

**Discover is not one of the ten tracks, and it is not part of track A.** It has
its own ranking pass, its own gate (two metatags, without which no card renders at
all) and its own freshness curve, so a site where Discover is a material traffic
source needs [discover.md](references/discover.md) run as an eleventh pass — and a
site where it is not can skip it entirely. Check the GSC Discover report before
deciding.

**Before any decline diagnosis**, run the date-alignment and update-response
protocol in [references/algorithm-updates.md](references/algorithm-updates.md) —
"a core update hit us" is not a finding, and half the documented GSC outages
coincided with rollouts.

Each track has two halves: the **diagnostic** work and a **mechanical sweep** for
completeness — [technical-checks.md](references/technical-checks.md) §A3 for A/B,
[onpage-checks.md](references/onpage-checks.md) for D/E. Diagnose first; the sweep
catches the boring failures afterwards, and only sweep items with an observable
impact reach the findings table.

**Order matters.** A track-A blocker (site not fetchable, noindex in the
pre-render source, manual action) makes every other finding moot — a manual
action is a binary multiplier: nothing you improve counts until it is lifted.
Work A → B → C before spending time on F/G.

**Evidence ladder** — ordered by **evidence strength, not convenience**, from
server logs down to a manual fetch; the rungs and their routing are in
[tooling.md](references/tooling.md). Use the highest rung you can actually reach
and state which one a finding rests on. A public-only audit with no property
access is valid work, but its indexation and query findings are inferences rather
than observations, and get tiered accordingly.

**Seven scripts ship with the skill** — `preflight.py`, `gsc_pull.py`,
`page_audit.py`, `url_inspection.py`, `agent_surface.py`, `psi_pull.py` and
`sitemap_audit.py`. Their invocations, and the **four traps that decide whether a
finding is real** — rendered vs server HTML, the JSON array shape, truncation
dropping count-based findings, and the evidence tier that enters triage where
severity does not — are in [scripts.md](references/scripts.md).

## Step 3 — Triage

**First, check the tracks against each other.** Ten tracks produce ten sets of
findings that never saw one another, and the plan treats them as one answer — a
convergence that trusts its inputs because they arrived. Sorting an unranked list
is not the same as noticing that two of its rows cannot both be done.

Four things to look for, before any score is computed:

1. **Two recommendations that cannot both be executed.** D says two pages
   cannibalise and should merge; C says the deeper one is where the equity lands.
   Name the pair, decide which governs, and say why — a reader who meets both
   later cannot.
2. **One root cause wearing two track names.** A render-blocked template surfaces
   as an A, an F and an H finding: three rows, one fix, and the three inflate the
   plan and split its priority.
3. **A finding whose evidence rung contradicts a neighbour's.** Two rows about one
   URL at `CONFIRMED` and `HYPOTHESIS` is a fact about the instruments, not the
   site; the lower rung defers or the disagreement is stated.
4. **A track that returned nothing where a neighbour implies it should have.** F
   found no extractability problem on pages E called thin — one of the two did not
   look properly, and which is worth a minute now rather than a contradiction in
   the report.

Write the answer either way: `Cross-track: clean`, or the pairs with their
rulings. A check whose silence is indistinguishable from not having run is not
evidence — and this is the one most easily skipped, because every track
individually went green.

Then order every finding. Do not present an unranked list.

**Four axes, no scalar** — the first that separates two findings decides, in
this order: `impact` · `irreversibility` · `uncertainty` · `coordination`.
`effort` is recorded and never ranks. A product cannot be argued with on its
inputs; an axis can. Definitions:
[`deliverable-templates.md`](references/deliverable-templates.md).

<!-- priority-axes: impact, irreversibility, uncertainty, coordination -->

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

- `docs/seo/audit-<YYYY-MM-DD>.md` — findings, each carrying its **evidence rung**,
  which is the source the observation came from and caps its tier
  ([tooling.md](references/tooling.md)).
- `docs/seo/plan-<YYYY-MM-DD>.md` — the change plan: an exact target per change,
  the mechanism and tier behind it, the expected effect, and how to roll it back.
- `docs/seo/experiments.md` — appended rather than dated, because it outlives any
  single audit. Required as soon as the plan has an Experiments bucket, which
  anything below `CONFIRMED` puts there.

The field list for each is in the skeletons, which is the point of having them.

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

The fourteen most-requested of the **33** refuted claims. Each is refuted by
2026 evidence; the full list, with the counter-evidence and the working
alternative for each, is in [references/myths.md](references/myths.md) — read it before
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

**Two of them have a narrow non-myth use, and confusing the two is how the myth
gets re-sold.** `llms.txt` and Markdown twins do not help a page get **found**;
they can help an agent that has **already arrived** read the site cheaply, which
is a serving decision rather than a ranking one. The boundary and its conditions:
[agent-readiness.md](references/agent-readiness.md) K3. Anything sold as "publish
Markdown to rank in AI" is still the myth.

## Reference index

Load [REFERENCE_INDEX.md](REFERENCE_INDEX.md) to route a track, sweep,
instrument or deliverable to its detailed reference.
