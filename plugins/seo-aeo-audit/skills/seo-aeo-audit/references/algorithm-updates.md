# Google update timeline — and how to keep it current

**Verified as of: 2026-07-28.** Primary source, re-fetch it on every refresh:
<https://www.searchenginejournal.com/google-algorithm-history/> (Search Engine
Journal, full history back to 2003; the page is organised by year, newest first).

Secondary sources for the same refresh:
- Google Search Status Dashboard — <https://status.search.google.com/> (official
  ranking-update feed with start/end timestamps and incident notices)
- Google Search Central blog — <https://developers.google.com/search/blog>
- Bing Webmaster blog — <https://blogs.bing.com/webmaster>
- Yandex Webmaster news (RU market)

An audit that names an algorithm update without dates is guesswork. Everything
below is dated so a traffic curve can be aligned against it.

## Ranking updates, last ~18 months

| Update | Rollout start | Complete | Type | What it means for an audit |
|---|---|---|---|---|
| June 2026 spam update | 2026-06-24 | 2026-06-26 | Spam | Fast, global. Spam actions and core-update recovery are **separate systems** — a domain hit here does not recover at the next core update (82% stayed blocked in the March-2026 study). |
| May 2026 core update | 2026-05-21 | 2026-06-02 | Core | ~12 days. Analyses read it as a re-tuning of *which site type* Google prefers per intent and market, not a quality purge. Sites leaning on self-promotional "best [category]" listicles accelerated downward here. |
| March 2026 core update | 2026-03-27 | 2026-04-08 | Core | Followed the spam update three days earlier — do not attribute movement to one without separating the windows. |
| March 2026 spam update | 2026-03-24 | 2026-03-25 | Spam | One-day rollout. SERP analysis over 100k queries: >24% of top-10 pages fell past position 100 (vs ~15% in December); domains older than 15 years took >57% of top-10 slots; sub-year-old domains ~0.7%. |
| Discover core update | 2026-02-05 | ~2 weeks, then global | Core (Discover) | Discover has its own ranking pass. Feed composition shifted toward social sources; publishers report CTR decline. Audit Discover separately from Search. |
| December 2025 core update | 2025-12-11 | 2025-12-29 | Core | 18 days. Baseline for "did we already lose this before the March event?" |
| August 2025 spam update | 2025-08-26 | 2025-09-21 | Spam | 26 days — long rollouts mean a "recovery" mid-window is noise. |
| June 2025 core update | 2025-06-30 | 2025-07-17 | Core | — |
| March 2025 core update | 2025-03-13 | 2025-03-27 | Core | — |

Older eras (2024 and back — HCU, site reputation abuse, product reviews, Panda,
Penguin, Florida…) are on the same SEJ page; pull them only when auditing a site
whose decline predates the window above.

## Platform and policy changes worth dating (not "algorithm updates", still audit-relevant)

| Change | When | Audit implication |
|---|---|---|
| FAQPage / Question / Answer rich results fully discontinued | 2026 (H1) | Remove FAQ markup from the plan as a SERP-feature play; keep the Q&A structure for extractability only. |
| AMP cache switched off; Search redirects to the publisher's AMP host | 2026-07 | AMP ranks like any page — no advantage, and maintenance work on AMP is not an SEO investment. |
| Preferred sources extended from Top stories to AI Overviews and AI Mode; "Highly cited" badge added | 2026-05 | Loyalty surfaces now feed AI answers. Publishers should promote the preferred-source link. |
| Publisher/creator Search profiles (US-first; thresholds 100k YouTube/Instagram/X, 300k TikTok) | 2026-06 | Entity surface tied to social scale; reachable from Discover and the Knowledge Graph. |
| GSC "Search Generative AI performance" report (UK/India first) | 2026-06 | First party AI-surface data — check availability before promising AI reporting. |
| GSC control to opt out of AIO/AI Mode display (inherits from the nearest parent property) | 2026-06/07 | Verify inheritance before assuming a property's setting. |
| GSC platform properties (YouTube, Instagram, TikTok, X) | 2026-07 | Ties social distribution to Search/Discover reporting. |
| Bing Webmaster Tools AI Performance: citation share, grounding query intents/topics, GEO recommendations | 2026-04 → 06 | The most actionable AI reporting available; Bing also grounds ChatGPT. |
| Spam policy updated to cover **manipulating generative AI answers**; sanctions synced between classic Search and AIO/AI Mode | 2026-05 | Mention-manipulation is now policy-equivalent to link buying (Gary Illyes). A Google penalty removes you from AI surfaces too. |
| Google I/O 2026: Intelligent Search box, Gemini 3.5 Flash in Search, Personal Intelligence (~200 countries, 98 languages), search agents for AI Pro/Ultra | 2026-05-19 | Personalisation is now a variable in AI answers — visibility is per user, not per query. |
| Web Guide (AI Labs experiment) | 2026 (testing) | Watch, do not optimise for it yet. |
| ChatGPT Atlas browser (macOS) | 2025-10 | Agentic browsing surface; relevant to WebMCP-style plays only. |
| Yandex Commerce Protocol out of beta; Google UCP appearing in regular SERP | 2026-05 | For commerce, feed/protocol integration is a distribution decision, not an SEO one. |
| Google documents `llms.txt` as ignored by Search, while Chrome Lighthouse adds an agentic-browsing check for it | 2026-06 | Two different surfaces; see myths.md. |
| Open Knowledge Format (OKF) proposal — markdown + YAML knowledge bundles for agents | 2026-06 | Emerging, no ranking claim. |

## How to use the timeline in an audit

1. **Date-align before diagnosing.** Plot clicks/impressions per template and
   market against the rollout windows above. If the decline starts outside every
   window, an update is not the cause — keep looking.
2. **The rollout window is not the effect window.** Practitioners report ranking
   shifts 7–10 days *before* the announcement (visible as a change in Googlebot
   crawl pattern in server logs), and volatility continuing after Google declares
   a rollout complete. Widen the comparison window accordingly.
3. **Separate the events.** March 2026 had a spam update and a core update three
   days apart; attributing movement to "the core update" without splitting the
   windows is a false diagnosis with an expensive plan attached.
4. **Cross-check the reporting.** Half of the documented GSC outages coincided
   with rollouts. A frozen report pins clicks at one date; a real hit keeps
   producing fresh declining points. Verify against GA4, logs and an independent
   tracker (see measurement.md).
5. **Discard overlapping experiments.** Any split test running through a rollout
   is invalidated (experiments.md).
6. **Set the right recovery expectation.** Core-update losses recover when the
   underlying quality assessment changes — often at a later core update, not by
   patching technicals. Spam-filter losses do **not** ride along with the next
   core update. Manual actions need fixes plus one reconsideration request.
7. **"A core update hit us" is not a finding.** The finding is *which* templates,
   intents and markets moved, and what the winners on those SERPs have that the
   losers do not (see intent-and-content.md E1).

## Protocol when a new update is announced

1. Record the exact start/end timestamps from the Search Status Dashboard.
2. Freeze a before/after export: GSC by page, query, country, device — 28 days
   either side, plus the same period last year for seasonality.
3. Segment by template and intent class, not sitewide.
4. Pull the same window for a competitor set, so a market-wide shift is not read
   as a site-specific hit.
5. Classify each template: winner / loser / unchanged, with the click delta.
6. Only then form a hypothesis, and tag its evidence tier. Google's stated target
   for the update is context, not proof.
7. Add the row to this file (below) with the audit implication you observed.

## Refresh protocol for this file (part of the skill's Definition of Done)

Do this quarterly, and immediately after any announced rollout:

1. Fetch the SEJ history page and the Search Status Dashboard.
2. Append every new update to the table with **start date, end date, type** and a
   one-line audit implication. Never delete old rows — decline analysis needs
   history.
3. Sweep the platform-change table for anything the engines shipped since the
   last refresh (Search Central blog, Bing blog).
4. Re-check `myths.md` and `benchmarks.md`: a shipped change can retire a myth
   (as the FAQ-rich-result removal did) or invalidate a benchmark.
5. Update the **Verified as of** line at the top and note the refresh in the
   repository CHANGELOG.
6. If a claim in any reference is now older than ~18 months and unconfirmed,
   downgrade its evidence tier or drop it.
