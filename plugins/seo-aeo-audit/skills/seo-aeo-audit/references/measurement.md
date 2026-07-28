# Track J — measurement and instrumentation

If nobody can tell whether the plan worked, the plan is a wish list.

Method only. Every dated number this file leans on — effect sizes, samples,
survey shares, contested figures — lives in benchmarks.md; quote it from there
with its date.

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
| Server logs | Which bots fetch what, when, with which status | The only place AI-crawler behavior is ground truth; use forward-confirmed reverse DNS to filter spoofed agents |
| Analytics (GA4 etc.) | Sessions, engagement, conversions by landing page and source | AI referrals appear only when the platform passes a referrer; assisted conversions arrive later via brand/direct |

Field-data sources worth wiring in: CrUX (`cruxvis.withgoogle.com`) for real
Chrome performance including form-factor split, and a rank tracker you control
for independent verification. CrUX is Chrome-only (~67.7% of the browser market,
no iOS Safari) — script it into the same dashboard as your analytics if you want
continuous competitor monitoring, and state the coverage gap in the report.
Google is testing a `google.com/goto` redirect that masks the destination URL in
the SERP (Jul 2026), so confirm how your rank tracker collects before you trust a
step change in its numbers.

**Rank tracking is a vendor-continuity risk, not just a data-quality one.**
Almost every tracker rests on SERP collection by a third party, and both the
technical basis and the legal basis of that collection are in motion: the
`google.com/goto` experiment above can break parsing, and Google's scraping suit
against SerpApi was dismissed (reported 2026-07, `FIELD`) — a single ruling that
settles nothing permanently and could go the other way next time. Consequences
for the report: record the collection method and the provider next to every
position series, keep at least one first-party series (GSC average position for
the same query set) that survives a provider outage, and never build a
long-horizon KPI on a number only one vendor can produce.

Three rules for the instrumentation itself:

- **Aggregate before the model sees it.** LLM- and MCP-driven GSC analysis that
  streams raw rows into a context window invents totals. Compute CTR curves,
  decay, cannibalization and position deltas in SQL/Python in the warehouse and
  hand the model the compact result (one reported build: a full report over a
  4GB dataset in 4.4s). Deterministic arithmetic is not the same as correct
  data — GSC sampling, freshness lag and interpretation traps survive the
  rewrite. FIELD.
- **Build the site's own CTR curve** from a GSC export rather than an industry
  curve; your curve is shaped by the SERP features and brand strength on your
  queries. No code needed — the published Colab takes the export as-is.
- **Treat the XML sitemap as an audit instrument**, not a ranking lever: diff
  sitemap counts against published pages and against GSC-indexed counts to
  expose phantom URLs (`/feed/` strings, parameter debris).

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

Four more artifacts that read as findings and are not:

- **A metric-definition change.** Google fixed an impressions-counting bug in
  the GSC performance report; the correction lowers impressions only from
  2026-04-27 onward and historical data was not restated. A step change dated to
  a fix is not a loss. CONFIRMED.
- **A documented data gap.** Google posts data anomalies per report (the
  Discover report was incomplete for 7–8 May 2026). Read the anomaly notice
  before diagnosing a dip that appears in one report and nowhere else.
  CONFIRMED.
- **"Indexed, though blocked by robots.txt" spikes.** Google's infrastructure
  runs boundary tests that inflate this count and then self-correct; the URLs
  are indexed as strings with no content processed, so they cannot dilute
  quality. Do not unblock `robots.txt` to insert `noindex`, and do not reach for
  the removal tool. Act only if a blocked URL takes impressions from a canonical
  page on a commercial query — and then the canonical page is the finding.
  CONFIRMED.
- **An inherited metric.** Pages cited by ChatGPT show ~96% less layout shift
  than Google's top pages, which reads as ChatGPT weighting page experience. It
  fetches raw HTML, loads no CSS/JS and has no CrUX access — the number is
  Google's index quality arriving second-hand. Before attributing a metric to an
  engine, check the engine can observe it at all. FIELD.

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
- **Format is the variable; wording mostly is not.** Ranking/list/comparison
  formats surface materially more brands than open questions, and prompt length
  and filler words do nothing (numbers in benchmarks.md). TOFU and branded BOFU
  prompts are stable under rewording; non-branded commercial MOFU prompts are
  where wording moves the result, so carry more MOFU variants. One hard rule:
  high similarity is not the same intent — when the qualifier changes (location,
  product, demographic, brand), it is a new prompt with its own baseline.
- **Personalization contaminates the sample.** AI Mode answers shift with the
  account's connected personal context; in a controlled test, seeding brands
  through Gmail lifted their appearance sharply on the connected account while
  the control account did not move (figures and sample size in benchmarks.md;
  mechanism in aeo-geo.md F4). Capture the prompt set from
  clean, logged-out sessions, record the account state next to every run, and
  never compare a signed-in capture with a control. STUDY (small sample — see
  benchmarks.md).
- **Popularity of a model is not its value as a channel.** In the RU market
  ChatGPT leads on awareness and use while Alisa AI sends roughly 5× more
  referred sessions. Rank engines by referred sessions and conversions in your
  market, never by headline MAU.
- **Mention volume without sentiment and stage is a trap.** One brand took a
  mention spike in under 60 days from a viral scandal (figures in benchmarks.md)
  and was dropped from transactional and recommendation prompts at the same
  time. Always cut mentions by sentiment and by prompt stage, keep volume and
  sentiment as **separate** metrics (§J3b), and report the commercial-prompt cut
  separately. FIELD.
- **Uncited influence is real.** Answers lean on forum threads that never appear
  as a link, so track brand mentions without links too — and per engine: Reddit
  is heavy in ChatGPT citations and near-absent in Perplexity.
- **Classic signals are leading indicators, not proxies.** SERP impressions and
  position are the strongest external correlates of ChatGPT recommendation, yet
  all external signals together explain only 15–20% of the variance — 80–85% is
  model-internal and unobservable from outside. Use them to forecast direction;
  never present them as AI visibility. Losing Google index health has been
  observed dragging AI visibility with it (figures in benchmarks.md), though a
  Bing-only counter-case makes the dependency itself HYPOTHESIS — record both
  and monitor each engine separately (aeo-geo.md F4).
- **Expect volatility.** In one longitudinal study ~1 in 4 cited pages was cited
  once and never again; between first and last citation a page appeared roughly
  every third day; the longest unbroken streak was 52 days. Report ranges and
  medians over weeks, never a single-day snapshot.
- **Retrieval ≠ citation.** Perplexity left ~76% of retrieved pages uncited while
  ChatGPT cited 61%. If you can see retrieval (logs), report it separately.
- **Inbound truth beats vendor dashboards.** Which AI crawlers fetched which
  URLs, and which AI referrers produced sessions, are things you own. Vendor
  visibility scores are directional at best; several are demonstrably modeled,
  not observed.
- **A crawler hit is not a training receipt.** Crawled → archived → text
  extracted → filtered → deduplicated → mixed → trained → surfaced. Content drops
  out at any stage, and a deployed model's parametric memory is frozen until the
  next training cycle. Never correlate a GPTBot hit with a knowledge change.

## J3b. The KPI set has moved

(The attribution gaps behind these metrics — calls, offline conversions, AI
referrals, cross-device — are audited in demand-and-conversion.md §H+3.)

Rankings, sessions, impressions and conversions still matter, but they no longer
describe how a brand is discovered. Add, and report alongside them:

| Metric | Where it comes from | Why |
|---|---|---|
| Branded search volume and trend | GSC branded queries, Ahrefs/Yandex volume | Whether people look for you at all — the clearest signal that discovery elsewhere is working |
| Brand presence in AI answers (mention → recommendation) | the prompt set, per engine | What the buyer actually hears |
| **Volume** of third-party UGC about the brand | social listening, Reddit/Quora/Trustpilot | Whether the category conversation includes you at all — a reach metric, nothing more |
| **Sentiment and semantic cluster** of that UGC, reported separately and cut by funnel stage | the same sources, plus the commercial-prompt cut of the prompt set | Volume and verdict move independently and can move in opposite directions: one brand took a mention spike from a viral scandal while being dropped from transactional and recommendation prompts in the same window (figures in benchmarks.md). Never report the two as one number |
| Direct and returning traffic | analytics | The owned-audience moat, immune to SERP composition |
| Newsletter/community signups | your own systems | The channel nobody can re-rank |
| Assisted and later-touch conversions | analytics, CRM | AI search has no attribution model; conversion often arrives weeks later via brand or direct |
| Index health per template | GSC Pages report | Coverage %, time to index, drop-out rate — and diagnose "Crawled – not indexed" (quality) apart from "Discovered – not crawled" (crawl budget) |
| Indexed URLs **with** traffic or conversions vs indexed with zero | GSC + analytics | The only index number tied to value; the raw indexed count moves the wrong way on purpose during consolidation |
| Local outcome signals (calls, direction requests, bookings) | GBP, call tracking | For a local business these replace citations entirely — a citation cannot be booked |

Two consequences for the report: stop treating last-click as the definition of
success, and stop treating any single channel's ranking as the definition of
visibility. A brand can be present at every step of the funnel and still show a
flat "position" chart.

One scorecard, not a wall of vendor dashboards: first-party data (Search
Console, analytics, internal systems) plus at most one AI-monitoring tool,
reported on five signals — presence, prominence, citation quality, authority
confirmation, business impact — cut weekly against a single strategic KPI
(reach, conversion or authority). FIELD: a practitioner framework, not measured
effect. It is compatible with this file only because the five signals stay
separate; the moment they are averaged into one number it becomes the vendor
score that myths.md refuses.

## J4. Cadence

Weekly (operational):
- Index status deltas per template; new crawl errors; 404/410 volume.
- Rankings for the priority set; clicks for the top revenue pages.
- Any manual action, security issue or unexpected traffic spike.
- AI-crawler fetches and AI-referred sessions per template, from logs and
  analytics — the two AI numbers you own outright.

Monthly (strategic):
- Traffic and conversions by template and market vs baseline.
- The prompt set re-run per engine, from clean sessions: mention/
  recommendation/citation rates, per persona and per funnel stage.
- Mention volume split by sentiment and by prompt stage, with the commercial
  prompts reported separately.
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
| Rich result restored after a markup or parity fix | 2–4 weeks after the fix | Weeks |
| Crawl priority on a URL that carried a negative directive (out of stock, temporary noindex) | 100+ days unless broken with feeds and links from high-crawl-rate pages | Months |
| Recovery after a spam filter | Do not promise the next core update: most domains pushed out of the top 100 stayed out through it | Open-ended |
| A new third-party mention reaching an AI answer | Retrieval-level, sometimes hours; treat single fast cases as anecdotes | Days |

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
- Raw AI mention volume with no sentiment and no funnel-stage cut.
- Third-party volume, DR or estimated-traffic numbers as evidence that a site or
  a link target is worth anything — fabricated-volume operations inflate exactly
  those fields; open the keywords tab and look for one brand name in 70
  variations and nothing else.
- Any figure an LLM produced by reading raw GSC rows. Aggregate first, then let
  it narrate.
- A period-over-period change in a vendor AI-visibility percentage as proof a
  change worked: the same prompt returns different answers by session, user,
  temperature, model version and day, so a single delta has no control in it.
  Use a control prompt set and report ranges (experiments.md).
