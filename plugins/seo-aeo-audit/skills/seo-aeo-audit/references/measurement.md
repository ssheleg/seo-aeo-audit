# Track J — measurement and instrumentation

If nobody can tell whether the plan worked, the plan is a wish list.

## J1. The surfaces that exist in 2026

| Surface | What it gives you | Gotcha |
|---|---|---|
| Google Search Console | Clicks/impressions/position; Pages (index status) report; URL Inspection; Links; Manual actions | Sampling, freshness lag, data hiding on large properties; verify **all** property variants |
| GSC — Search Generative AI performance | Pages and impressions from AI surfaces (rolling out per market) | Partial metrics at first (no clicks/queries in early versions) |
| GSC — AI display control | Opt-out of AIO/AI Mode display; inherits from the nearest parent property, default from the TLD-level property | Check inheritance before assuming a setting applies |
| GSC — platform properties | YouTube, Instagram, TikTok and X performance in Search/Discover | Ties social distribution to search visibility |
| Bing Webmaster Tools — AI Performance | Intents, topics, citation counts and **citation share**, grounding query intents/topics | The most actionable AI reporting available; Bing also feeds ChatGPT |
| Microsoft Clarity | AI-visibility reporting from Copilot and Bing | AI referral traffic is only countable when the platform passes a referrer |
| Yandex Webmaster | Query monitoring (hours-level delay), vertical inclusion/exclusion, verification via YTM or GTM | Yandex now presents Direct as a useful signal for search — ads and organic are no longer described as independent |
| Server logs | Which bots fetch what, when, with which status | The only place AI-crawler behaviour is ground truth; use forward-confirmed reverse DNS to filter spoofed agents |
| Analytics (GA4 etc.) | Sessions, engagement, conversions by landing page and source | AI referrals appear only when the platform passes a referrer; assisted conversions arrive later via brand/direct |

Field-data sources worth wiring in: CrUX (`cruxvis.withgoogle.com`) for real
Chrome performance including form-factor split, and a rank tracker you control
for independent verification.

## J2. Cross-checking before you diagnose

GSC breaks, and it breaks disproportionately during algorithm rollouts — an audit
of 26 documented outages found 13 coinciding with active rollouts. Distinguish:

- **Reporting freeze**: clicks and impressions pin at one past date; GA4, server
  logs and third-party trackers keep moving. The UI usually shows an "internal
  issues" banner.
- **Real hit**: fresh data points keep arriving on a declining curve, and the
  other sources agree.

Never write "algorithmic penalty" in a report without that three-way
cross-check.

## J3. Measuring AI visibility honestly

- **No single number.** Only ~2.4% of URLs are cited by ChatGPT, Perplexity and
  Google AIO at once. Report per engine.
- **Mentions, not just citations.** An answer can name a brand four times while
  the citation points somewhere else entirely. Citation-only scorecards mark
  visible brands invisible and vice versa. Measure: mention rate, top-3 mention
  rate, recommendation rate, then citation rate.
- **Per persona and per funnel stage.** The same category, same engine, different
  buyer context produces different winners. Track a 25/50/25 TOFU/MOFU/BOFU
  prompt split and tag prompts by format (list vs open question) so you never
  compare across formats.
- **Expect volatility.** In one longitudinal study ~1 in 4 cited pages was cited
  once and never again; between first and last citation a page appeared roughly
  every third day; the longest unbroken streak was 52 days. Report ranges and
  medians over weeks, never a single-day snapshot.
- **Retrieval ≠ citation.** Perplexity left ~76% of retrieved pages uncited while
  ChatGPT cited 61%. If you can see retrieval (logs), report it separately.
- **Inbound truth beats vendor dashboards.** Which AI crawlers fetched which
  URLs, and which AI referrers produced sessions, are things you own. Vendor
  visibility scores are directional at best; several are demonstrably modelled,
  not observed.
- **A crawler hit is not a training receipt.** Crawled → archived → text
  extracted → filtered → deduplicated → mixed → trained → surfaced. Content drops
  out at any stage, and a deployed model's parametric memory is frozen until the
  next training cycle. Never correlate a GPTBot hit with a knowledge change.

## J4. The reporting cadence

Weekly (operational):
- Index status deltas per template; new crawl errors; 404/410 volume.
- Rankings for the priority set; clicks for the top revenue pages.
- Any manual action, security issue or unexpected traffic spike.

Monthly (strategic):
- Traffic and conversions by template and market vs baseline.
- The prompt set re-run per engine: mention/recommendation/citation rates.
- Ghost-citation rate; cited-source inventory changes for buyer attributes.
- Internal-link and index-coverage progress against the plan.
- Age-versus-SERP check on priority queries (which pages are now outside the
  freshness percentile).

Quarterly:
- Full `robots.txt` and sitemap audit; property and DNS inventory review.
- Competitive CWV and form-factor comparison.
- Third-party profile consistency re-check.

## J5. Setting expectations in the report

| Change | When to look | Typical horizon |
|---|---|---|
| Robots/rendering unblock | 24–72h for crawl, days for index | Fast |
| Canonical/duplicate consolidation | 2 weeks minimum (groups persist after fixes) | Weeks |
| Internal linking / "Discovered – not indexed" push | 24–72h to index, weeks to rank | Weeks |
| Quality clean-up after mass noindex or thin content | 6–12 weeks, staged in batches | Months |
| Migration recovery | 2–8 weeks with a clean protocol; months without | Months |
| Content/intent rework | One crawl+evaluation cycle, then a core update to fully settle | Quarter |
| Entity/brand consensus in models | Retrieval-level: days. Training-level: model releases | Months |
| Manual action | Fix everything, one reconsideration, days to weeks | Weeks |

State the horizon next to every recommendation. An audit that promises next-week
results for a quarter-long change is the reason clients stop trusting audits.

## J6. What not to measure

- A single "AI visibility score" from any vendor.
- Citations without mentions and recommendations.
- Rankings without the click and conversion context for the same query set.
- Industry-average CTR curves (build your own from GSC).
- Third-party toxicity percentages as a disavow trigger.
- Crawler hits as evidence of model knowledge.
- Vanity index counts: fewer, better-indexed pages routinely beat more.
