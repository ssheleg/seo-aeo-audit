# Benchmarks — dated numbers for sizing and expectation-setting

Use these to size an opportunity and to keep a report honest. **Always cite the
date**; this snapshot is April–July 2026 and search surfaces move fast. Re-check
anything older than ~18 months before it enters a plan.

## Surface reach

| Metric | Value | As of |
|---|---|---|
| Google AI Overviews | ~2.5B MAU | May 2026 |
| Google AI Mode | ~1B MAU | May 2026 |
| Google AI Mode share of sessions | <0.2% (growing) | Q1 2026 (Datos/Semrush panel, tens of millions of devices) |
| AI-tool share trend | Classic search still grows faster than AI tools in absolute terms; Gemini second and growing; ChatGPT flat-to-down since its Sep 2025 peak | Q1 2026 (same panel) |
| Yandex share of the RU search market | 73.34%; classic-search growth effectively stalled | Jun 2026 (impulse.guru: 72.4M AI-service referral clicks analyzed) |
| Google global traffic YoY | −0.89% — first recorded decline | Jun 2026 (same study) |
| RU referral value by model | Alice AI sends ~5× more site referrals than ChatGPT, which leads on awareness and usage | Jun 2026 (same study) |
| Bing | 1B MAU | May 2026 |
| Yandex "Alice AI" (Алиса) | **42%** of Search queries answered (+7pp QoQ) and **49.5M** monthly users of the quick answers under the search box; ~10% of queries product-related. Yandex attributes the coverage jump to a new generation of compact Alice AI Search models | Q2 2026 (Yandex quarterly results, 2026-07-29). Prior point: ~1 in 3 queries and 48.3M MAU (Q1 2026) — the metric wording is the company's own and unchanged, so the pair is a trend, not two measures |
| Bot vs human web traffic | Bots overtook humans for the first time | Jun 2026 |
| Google share of the search market | dipped below 90% | 2026 (SEJ) |
| Gen Z searches starting with Google Lens | ~1 in 10; ~1 in 5 of those commercial | 2026 (SEJ) |

## Click economics

**Four different things get called "the click".** They measure different
populations and different actions, so none of them refutes the others — quoting
one against another is the most common misreading of this section. Keep the
label attached to the number in the report.

| What is actually measured | Value | As of |
|---|---|---|
| Sessions ending with **no click on anything** (zero-click) | 68% (was 60.45% in 2024); UK highest | Jan–Apr 2026, US, desktop+mobile panel (Similarweb/SparkToro) |
| Clicks on a link **inside** the AI summary | ~1% of sessions | 2025 study |
| Users who, with an AI Overview present, still click **a traditional organic result** to verify | 80% | 2025 study (Kevin Indig, cited by SEJ) |
| Click loss of the **first organic result** when an AI Overview is present (same position, relative) | −58% | 2026 (Ahrefs) |
| Share of AI-answer links coming from the organic top-10 | 38%, down from 76% in mid-2025 (Semrush); Ahrefs reports the same 38% for Google AI citations specifically | 2026 |

Read them together: on the sessions that do produce a click, the traditional
result still takes most of it (80%) while the in-answer link takes almost none
(~1%) — and position 1 keeps a much smaller share of that traffic than it used
to (−58%). "Nobody clicks any more" and "80% still click" are both wrong as
summaries.

**Zero-click is not a one-directional trend.** The 68% is one panel's US
desktop+mobile aggregate across a single four-month window. A later desktop cut
(reported 2026-05) has zero-click *falling* from March 2026 with organic clicks
rising. Two credible cuts point opposite ways, so per evidence-tiers.md rule 3
the *direction* is **HYPOTHESIS**: quote the level with its segment, window and
panel, and never extrapolate the line. See also the "Contested metrics" table
below and the B2B AI-Overview figures under "AI-surface coverage and device
context", which are vendor-sourced and undated inside their report.

## User self-report (opinion data, not behavior)

Stated behavior from a consumer survey. Use it to frame a plan, never as
evidence that traffic will or will not move.

| Finding | Share | Sample / date |
|---|---|---|
| Use AI tools at all / regularly | 90.2% / 67.5% | 3,000 RU users surveyed, Jun 2026 |
| Say they do not double-check AI answers | 50.9% | same (contested — see below) |
| Say they start a complex research task with an AI | 42.8% | same |
| Say they already use AI when choosing goods or services | >50% | same |

## AI citation mechanics

| Metric | Value | Sample |
|---|---|---|
| Citation rate at retrieval position 0 vs 10 | 58% vs 14% | 16,851 queries / 353,799 pages |
| Never-cited pages | 58% of pages; 25% always cited | same |
| Median position: consistently cited vs never cited | 2.5 vs 13.0 | same |
| Exact query–title match uplift (rank-controlled) | +19pp | same |
| H1–H4 prompt match | 41% cited vs 29% | independent analysis |
| JSON-LD presence | +6.5pp | same dataset — a correlation on one engine's citation rate, **not** a license to add schema; the canonical stance and the contradicting experiments are in myths.md, and the AIO/AI Mode direction is contested (see "Contested metrics" below) |
| Optimal length | 500–2,000 words (34.3%); >5,000 words 28.6% | same |
| Optimal subheads | 4–10 (33.2%) vs 1–3 (28%) | same |
| Optimal freshness | 30–89 days (32.8%); <30 days 25.3%; >2 years 27.5% | same |
| URLs cited by ChatGPT + Perplexity + AIO simultaneously | ~2.4% | cross-platform study |
| Classic SEO signals explaining ChatGPT recommendation variance | 15–20% (each factor R² ≈ 5–6%) | 29,562 domains / 105k prompts |
| Brand named in answer → cited | 53.1% vs 10.6% when not named | 541,213 answers / 20 brands / 6 platforms |
| Own "best [category]" page cited → brand excluded from the recommendation | 69% | 100 B2B prompts, 3 checkpoints |
| Retrieved-but-uncited rate | Perplexity ~76%; ChatGPT cites 61% | 9,886 answers |
| Citation persistence | ~1 in 4 pages cited once only; appearance ~every third day; longest streak 52 days | same |
| Reddit share of LLM citations | ~40% overall (Semrush, 2026) — **volatile by construction**: ChatGPT's Reddit share fell ~60% → 10% in six weeks after one retrieval-logic change, and bulk auto-translated Reddit content was demoted after the May/June 2026 updates (algorithm-updates.md, threats-and-defense.md I1). Re-measure before quoting; never size a plan on the 40% | 2026 (Semrush); volatility observed 2026, demotion reported 2026-07 |
| UGC weight in deep-research agents | UGC sources cited in ~half of searches; ~25% of all citations point at UGC platforms | Cornell UGC-poisoning study, 2026 |
| Brand named in the answer → placed top-3 | 63% | field data, 85 UK mid-market companies across ChatGPT/Claude/Gemini, 2026 |
| Strongest external correlates of ChatGPT recommendation (Spearman ρ) | SERP impressions +0.241, position +0.238, SERP outbound links +0.230, backlinks +0.204, link trust +0.200; all external signals together <20% of variance, so 80–85% is model-internal | 29,562 domains / 145 verticals / 1,595 personas / 105k prompts (OtterlyAI) |
| Prompt **format** effect on brands surfaced (intent held constant) | ranking/list/comparison/table formats ~+20% vs open questions; keyword-explicit prompts ~+25%; persona prompts fewer; constraints cut brands in ChatGPT/Perplexity but raise them in Gemini/AIO; prompt length and filler words: no effect | 1,754 prompts / 37,804 answers across ChatGPT, Gemini, Perplexity, AI Mode, AIO — Jul 2026 |
| Prompt-wording stability | 88–92% of human prompt pairs exceed 0.50 cosine similarity, ~95% exceed 0.40; brand visibility stable above ~0.50–0.60; only the 0.35–0.39 bucket breaks down (−2.40pp on a 4.9% base, ~50% relative) | same |
| AI Mode personalization effect (Gmail seeding, connected Personal Intelligence account) | appearance 23.9% → 66.8% (control account 21.9% → 18.9%); top-3 4.5% → 24.9%; top-10 17.7% → 54.6%; email-seeded 53.6% vs photo-seeded 10.5%; invented brands 35.7% vs real 55.8% | 1,922 AI Mode answers, **3 accounts**, 30 Mar–15 Apr 2026 — small sample, no decay data |
| Google index dependence | sites that lost 85% of Google traffic lost ~75% of ChatGPT traffic; blocking Googlebot cuts ChatGPT proportionally. A single Bing-only counter-case points the other way, so the *dependency* claim is HYPOTHESIS — both observations and the reading rule are in aeo-geo.md F4 | field observation, 2026 |
| Mention volume vs commercial visibility | a viral scandal produced +2800% ChatGPT brand mentions in <60 days while the brand was dropped from transactional/recommendation prompts | single case, Jul 2026 |

## What a recommendation is worth, and where the traffic shows up

Being *recommended* is a different outcome from being *cited* (aeo-geo.md F7,
measurement.md J3b). Similarweb tracked users who asked ChatGPT an
industry-relevant question, got a brand recommendation, and then visited that
brand or a competitor within seven days (US desktop; finance, travel, beauty).

| Metric | AI-influenced | Comparison |
|---|---|---|
| Likelihood of visiting the recommended brand | **~2.5×** vs a competitor left off the list | — |
| Visits arriving via **search** | **55.9%** | 40.4% of non-AI-influenced visits |
| Visits arriving via **direct** | 19.9% | 38.8% of non-AI-influenced visits |
| Pages per visit | 12 | 6.5 |
| Time on site | 11.8 min | 5.6 min |

**Read the first two rows together.** The majority of AI-influenced visits arrive
as *search* traffic, so the AI touch is largely invisible to last-click
attribution — which is the measured version of the blind spot
demand-and-conversion.md describes. What this does **not** license is a single
"X% of visits are AI referrals" figure: the study reports channel composition,
not a referrer share, and the residual is bounded by the two rows above rather
than measured directly.

## Read budget (ChatGPT Deep Research)

The first-read window, the link-count bands and the re-read rate live with the
mechanism that explains them — **architecture-and-equity.md**, "Read-budget:
navigation now costs you twice". Do not restate them here; quote them from there
with the FIELD tier attached (logged across 10+ accounts, ~June 2026).

## Content and ranking correlations

| Metric | Value | Sample |
|---|---|---|
| Core-update growth correlation (Spearman) | offers product/service 0.391, task completion 0.381, proprietary assets 0.357, tight focus 0.250, strong brand 0.206 | 400+ sites |
| Win rate by feature count | 1 feature 13.5–15.4%; 4 features 68.1%; 5 features 69.7% | same |
| Information-gain median in the top-3 | 52/100 (identical across positions 1–3); 25% below 40 | 150 pages / 50 keywords / 10 verticals |
| Unique data points | 15+ → 62/100; 0–1 → 40/100; median top-3 page has 4 | same |
| SERPs with an unanswered common question in the entire top-3 | 90% | same |
| Median on-page optimization score | 33/100 (46.8% below 25) against an ~80 practical threshold | 10,937 pages |
| Pages missing schema | 99% (45% none at all) | same |
| Four-year blog traffic outcome | median −85%; 12 of 100 to zero; 21 grew | 100 six-figure blogs, 2022→2026 |

## Operational benchmarks

| Metric | Target/observed |
|---|---|
| TTFB | <200ms optimal, <500ms acceptable |
| Server error rate | <0.5% |
| Duplicate-group persistence after a fix | up to 2 weeks |
| Out-of-stock crawl deprioritization | 100+ days after the directive is removed |
| "Discovered – not indexed" push success | 70–80% indexed within 72h with the full protocol |
| Migration traffic loss | ~30% average; ~8% with a disciplined protocol; 67% in the documented failure |
| Recovery after mass accidental `noindex` | 6–12 weeks, staged |
| PageRank decay per hop | ~85% |
| Bounce/dwell thresholds for intent match | bounce <40% and >2 min = match; >70% = mismatch |
| Rich result restored after a markup or content-parity fix | 2–4 weeks |
| Spam-filter recovery | most domains pushed out of the top 100 stayed out through the following core update (82%, 2026) — do not date a recovery to the next update |
| Manual-action lag after a hijack | deindexation preceded the manual action by ~24h in the documented case; reconsideration approved in 24h, full recovery 36h |

## Rendering ceilings (not the five-second myth)

| Metric | Value | Source |
|---|---|---|
| Render cut-off, live testing tools | 16–18 chained fetches ≈ 48–54s before the render was truncated | Published render tests, 2026-07-23 (myths.md) |
| Render cut-off, actual indexing | ~10 chained fetches ≈ 30s, with the exact point drifting between runs | Same |
| Reported duration of an awaited fetch inside the render | 0.02s for calls that took 3–6s of wall clock — the service pauses its own clock while a request is in flight | Same |
| Googlebot render viewport | Very tall rather than screen-sized; ~9,000px in DevTools is Google's own suggestion for reproducing what it sees | John Mueller, **2017-11** — long-standing behaviour, re-observed in practice since. Do not date this to the report that reminded you of it |
| Viewport expansion fires listeners **once** | A single resize at render time, so `scroll` and `IntersectionObserver` callbacks run one time only | Practitioner rendering research, 2026-08 (`FIELD` — no primary read; the tall viewport above is the confirmed half, this consequence is not) |

Read these as ceilings for pathological pages, not as a budget to optimize
against: rendering ends when the event loop goes idle (technical-checks.md A1).

## Entity extraction — how much of a tool's output is noise

166 top-ranking pages across 48 SERPs, five extractors, judged against Google's
own language for the query (AI Overview text, all People Also Ask questions,
related searches, captured with the ranking pages). Published 2026-07-20 by
On-Page.ai (Eric Lancheres) — a vendor whose own model wins the comparison, which
is why its row is labelled as theirs; the referee data is external and the method
is reproducible.

| Extractor | False-positive rate | Precision, top-30 |
|---|---|---|
| On-Page.ai (the study's own model) | 13.4% | 48.6% |
| Google Cloud Natural Language | 46.6% | 33.7% |
| TextRazor | 54.3% | 21.2% |
| gpt-5-mini (naive prompting) | 59.9% | 17.8% |
| spaCy `en_core_web_sm` | 65.1% | 16.4% |

Run-to-run stability, three identical runs over identical text (n=50 pages, mean
pairwise Jaccard): gpt-5-mini **61%**, the other four **100%**. Per-page entity
counts across the five ranged from 15 to 172 on the same pages. Audit rules in
entity-and-brand.md G3.

## Layout and module split tests

| Test | Result | Source |
|---|---|---|
| Brand carousel added below content on store pages | −2.8% organic sessions (estimated) | SearchPilot, 2026-07-17 |
| Product carousel removed from category pages | +29% | SearchPilot, reported 2026 |
| Product description moved out of tabs, above the fold | +14% desktop | SearchPilot, reported 2026 |

Direction over the first two replicates; the proposed causes differ (intent
dilution vs page weight and staleness), so the mechanism stays open
(experiments.md).

## Coordinated-generation enforcement

| Metric | Value | Source |
|---|---|---|
| Generation clusters terminated | 50K clusters comprising 130K channels, over a six-month operational period, on "a major Online Video Platform" the paper does not name | Google Research, *Scalable Detection of Adversarial Synthetic Slop and Coordinated Media Abuse* (Mathur, Orten, Liu, Tan, Liu), 2026 |

A video-platform system. It is here because the unit of enforcement is the
cluster — shared infrastructure plus templated output — not the individual page
(threats-and-defense.md I4).

## Industry context (practitioner survey, State of SEO 2026)

Survey of **371 SEO professionals across 52 countries** (78.5% with 4+ years'
experience, 77% in leadership roles), published in the 2026 edition — this is
what the industry *believes and plans*, not effect data. Useful for framing a
plan to stakeholders, never as evidence that a tactic works.

| Finding | Share |
|---|---|
| Original content creation is the most impactful activity | 66.3% |
| Fear AI-generated answers will reduce website clicks | 77.9% |
| Cite algorithm volatility / SERP disruption as the biggest challenge | 59.3% |
| Plan E-E-A-T investment as the strategic response | 49.6% |
| Plan human-authored content supported by AI (vs 22.4% primarily AI-generated) | 58.5% |
| Saw positive impact from technical SEO work | 42.3% |
| Report on qualified leads / sales conversions | 60.4% |
| Plan to invest in conversion-focused SEO | 33.7% |
| Struggle with ROI measurement | 28.6% |
| Content creation is the hardest thing to scale | 42.6% |
| Cross-functional collaboration rated as impactful today / planned increase | 9.4% / 37.7% |
| Trained teams on AI integration in the last year | 42.0% |
| Expect stable or increased SEO investment | 65.0% |

What those teams actually measure and with what (same survey, 371 respondents,
2026 edition — opinion data):

| Reported priority / tool / outcome | Share |
|---|---|
| Top measurement priorities: organic traffic | 74.9% |
| — qualified leads / sales conversions | 60.4% |
| — keyword visibility / rankings | 56.9% |
| — return on investment | 21.8% |
| — on-page engagement | 20.8% |
| — site performance | 17.5% |
| — **brand searches** | 15.9% |
| — social sharing / off-site | 5.1% |
| Most critical tool category: analytics & performance reporting | 56.3% |
| — cross-functional platforms | 51.2% |
| — technical health & auditing | 47.2% |
| — AI writing assistants | 42.3% |
| — rank tracking & SERP analysis | 27.0% |
| — SEO automation & AI agents | 14.8% |
| — backlink research & outreach | 7.8% |
| Most improved outcome: organic traffic growth | 60.6% |
| — keyword rankings | 57.7% |
| — brand visibility | 34.8% |
| — lead generation / conversions | 34.0% |
| — **no measurable improvement at all** | 9.2% |

Four gaps worth quoting in a report: conversion measured (60.4%) versus
conversion invested in (33.7%); zero-click fear (77.9%) versus E-E-A-T
investment (49.6%); branded search — the clearest surviving discovery signal —
prioritized by 15.9% while rankings still get 56.9%; and 9.2% who measured
nothing that moved, which is an attribution finding more often than a
performance one.

## AI-surface coverage and device context

Every row below comes from the same **vendor-sponsored 2025 report** (*The Future
of AI Search*, CallRail-sponsored, reported via SEJ; the BrightEdge figures are
quoted inside it). The report does not date its individual measurements, so
treat each as **2025, undated-vendor** — usable to frame a plan, never as a
current figure or a forecast. Re-check anything you intend to put in front of a
client.

| Metric | Value | Source/date |
|---|---|---|
| AI Overview coverage growth by vertical | entertainment +175%, travel +108%, B2B technology +7% | 2025, vendor (SEJ/CallRail) |
| Exact-match keyword phrasing present in AI Overviews | 5.4% | 2025, vendor — the body-phrasing finding behind onpage-checks.md O5; it is about literal query strings in the *answer*, not about title/heading match (aeo-geo.md F2) |
| B2B buyers encountering AI Overviews / clicking a cited source | 72% / 90% | 2025, undated-vendor (Google data quoted via SEJ), B2B buyers only — **not comparable** to the ~1% in-answer click rate or the 68% zero-click share in "Click economics", which measure all sessions and a different action |
| AI Overviews linking to Google-owned properties | 43% | 2025, undated-vendor (BrightEdge, quoted in the same report) |
| AI search referrals originating on desktop | ~94% | 2025, undated-vendor (BrightEdge, same) |
| Share of Google mobile traffic from iPhone | 58% | 2025, undated-vendor (BrightEdge, same) |
| ChatGPT traffic originating from desktop apps | ~94%; Google is the only major AI search with a mobile majority (53%) | 2025, undated-vendor (same) |

## Contested metrics — record both figures, pick neither

Two credible sources disagree on each of these. Per evidence-tiers.md rule 3 the
claim drops to HYPOTHESIS: quote both with their samples, or leave the number
out of the report.

| Metric | Figure A | Figure B | Status |
|---|---|---|---|
| Do users verify AI answers? | 80% still click through to a traditional result when an AI Overview is present (2025 study, US, cited by SEJ) | 50.9% say they do **not** double-check AI answers (3,000 RU users self-reported, Jun 2026) | Contested — different populations, different questions (observed click-through vs stated habit), and one is self-report |
| Does schema move ChatGPT citations? | **Study A — OtterlyAI GEO experiment, 100M sites:** schema **reduced** citations in ChatGPT, Gemini and Copilot while lifting Google AIO (~1500%) and AI Mode (~377%) | **Study B — LocalBusiness schema, 29 domains, 10 weeks, geo-matched control, one-sided Welch t-test, method reviewed before results, 90% threshold:** ChatGPT recommendation position **+3.33** (92.91% significance) and brand citation frequency **+10pp** (91.51%); **no** gain in Google/Bing/Yahoo, Maps got worse, AI Mode/AIO/Gemini/Grok at coin-flip 50–60%. Scope limits: one niche (service-area local businesses), one schema type, homepage only | Two named studies point **opposite ways on ChatGPT** and opposite ways on AIO/AI Mode; Study B also sits below the conventional 95% bar. Both directions are therefore **HYPOTHESIS** → experiments.md, split by engine. Quoting "no gain in Google/Bing/Yahoo" without Study B's positive ChatGPT arm (or vice versa) misreports it. Schema stays an eligibility and entity aid (myths.md), never a citation lever |
| Does serving Markdown to AI crawlers help? | 0% AI-crawler visits to `.md` mirrors vs 4.6% to the HTML (100M-site experiment) | One subfolder test reported +34% AIO visibility and +4.5% clicks | Contested — experiment only, per myths.md |
| Is zero-click still rising? | 68% and up from 60.45% in 2024 (US desktop+mobile panel, Jan–Apr 2026) | A desktop cut reported 2026-05 has zero-click falling from March 2026 with organic clicks rising | Contested — different device segments and windows. The **level** is quotable with its segment; the **direction** is HYPOTHESIS. See "Click economics" |
| Does ChatGPT depend on Google's index? | An 85% Google traffic loss came with a ~75% ChatGPT loss, and blocking Googlebot cuts ChatGPT referrals proportionally (FIELD, 2026) | A YMYL site past Google page 7 collected 90k+ ChatGPT citations from Bing alone, 88k URLs indexed in Bing vs 45k in Google (FIELD, 2026) | Contested, both single cases → HYPOTHESIS. Full reading and the safe residue in aeo-geo.md F4. Neither figure licenses "blocking Googlebot is AI-neutral" |

## Academic benchmarks — the only controlled numbers here

Everything else on this page is vendor or field data. These two are peer-reviewed,
and the second one bounds the first.

| Finding | Figure | Source |
|---|---|---|
| Content changes that raise visibility in generative answers | Adding **citations, quotations from relevant sources and statistics** raised visibility by **over 40%** across queries; keyword-style manipulation scored at or below baseline | Aggarwal, Murahari, Rajpurohit, Kalyan, Narasimhan, Deshpande — *GEO: Generative Engine Optimization*, KDD '24 (arXiv:2311.09735), GEO-bench: **10,000 queries**, 9 methods |
| The same methods on a real engine | **up to 37%** on Perplexity.ai | same paper |
| The metric all of the above is measured in | **Position-Adjusted Word Count (PAWC)** — a source's words in the answer, weighted by where they appear. Not clicks, not citation counts as an engine reports them | same paper |
| **What happens when everyone does it** | Across 9 C-SEO methods, 6 domains and **1,921 queries**, the methods are **mostly ineffective under competition**; in the retail domain a traditional-SEO baseline was about **7.6× more effective** than the best C-SEO method | Puerto, Gubri, Green, Oh, Yun — *C-SEO Bench*, NeurIPS 2025 Datasets & Benchmarks |

**How to quote these together.** The KDD figures come from optimizing one source
against a fixed set; C-SEO Bench measures what survives when rivals optimize too,
which is the situation every client is actually in. Quoting the first without the
second sells a lift that the follow-up study could not reproduce competitively.
Treat the direction (evidence-dense, quotable, well-sourced content) as `STUDY`
and the **magnitude** as unproven in a contested market. Secondary write-ups
attribute the peak to a single named method (some say Quotation Addition, some
Statistics Addition); the paper's own framing groups the three, so do not quote a
per-method percentage.

## Machine-readable files — adoption and consumption

| Metric | Figure | Note |
|---|---|---|
| `llms.txt` files receiving **zero AI requests** | **97%** | The load-bearing number: adoption and consumption are different questions, and this one answers the second |
| Adoption, top 1,000 sites | 8.7% (15.8% of the 549 that serve a page at the root) | Jun 2026 |
| Adoption, top 10,000 sites | ~5.6% | Jun 2026 |
| Adoption, Fortune 500 | 7.4% (37 of 500) | Mar 2026 |
| Growth | ~36,120 sites by May 2026, **8.8×** in twelve months | Rising fast and still not read |

Always state the denominator: as a share of the whole web the same count is
~0.01%, and quoting that against a top-1,000 figure compares two different things.

## Title and description rewriting

Google routinely replaces what you wrote, which caps what any title/description
work can be promised to deliver.

| Element | Rewrite rate | Source |
|---|---|---|
| Title tags | **61%** (2023, Zyppy) → **76%** (Q1 2025); when rewritten, ~2.71 words removed and ~35% of the original retained | Two studies, different years — the direction is up |
| Meta descriptions | **71%** mobile / **68%** desktop (Portent); ~63% across 192,000 pages (Ahrefs, 2022) | Figures differ by method and sample; quote one with its source |

Use this to set expectations, not to skip the work: the tag is still the input
Google rewrites *from*, and onpage-checks.md keeps the observable failure modes
(truncated mid-word, duplicated across templates) rather than a character count.

## Caveats

- Single-case figures (marked FIELD in growth-plays.md) are directional, not
  forecasts. Never present them as a promise.
- Vendor-published AI-visibility studies measure their own instrumentation; where
  two disagree, both drop to HYPOTHESIS.
- Regional variance is large: CWV outcomes, AI-surface availability, localization
  depth and commerce protocols differ per market. State the market you measured.
