# Source distillation — where the audit tracks come from

Working notes behind the reference set (started at v0.1.0, extended through the
v0.3.0 completeness pass and the v0.4.0 deep-extraction pass): the 2026 industry
corpus distilled into the claims the reference files make. Kept in the repo (not
shipped to agents or npm) so that every recommendation can be traced back to its
source and re-checked when the surfaces move.


The file keeps its July name because things link to it; the corpus it records now
runs to 2026-08-05 (PART G).

Sources:
- Telegram channels `@notjohnmu` ("noindex, nofollow", 175 posts) and
  `@MikeBlazerX` ("Mike Blazer", 217 posts), 27.04.2026–27.07.2026.
- The same two channels for 27.07.2026–05.08.2026, plus `@MikeBlazerPRO`
  (23.07.2026–05.08.2026), distilled in PART G. The PRO channel is closed and
  paid; the boundary on using it is recorded in `docs/DECISIONS.md`.
- Search Engine Journal, *Google Algorithm Updates & Changes: A Complete History*
  — <https://www.searchenginejournal.com/google-algorithm-history/> (fetched
  2026-07-28; feeds `references/algorithm-updates.md`).
- Search Engine Journal ebooks and reports (2023–2026), distilled in PART E:
  *The Ultimate Technical SEO Audit Workbook* (2023) + its companion spreadsheet,
  *SEO In The Age Of AI* (2024), *The Future of AI Search* (2025, CallRail),
  *State of SEO 2026*, *Google Ranking Factors: The 3 That Really Matter*,
  *B2B Lead Generation: Create Content That Converts*, *PPC Trends 2026*,
  *PPC Experts Tips*, *CallRail × SEJ: Better Leads, More Sales* (2025).
- Telegram channel «Site Growth» — community thread on `robots.txt` versus
  canonical for tracking parameters (Jul 2026), distilled in PART F into
  `technical-checks.md` A2, `tooling.md`, `growth-plays.md` (L13) and `myths.md`.
- Search Engine Journal, *SEO Trends 2026* ebook (Nov 2025 / 2026 edition, 34pp;
  Katie Morton ed., contributors Shelley Walsh, Matt Southern, Roger Montti, Dan
  Taylor, Patrick Reinhart, Grzegorz Czapik, Sam Page) — distilled into
  `intent-and-content.md` (E2b), `entity-and-brand.md` (G3b), `measurement.md`
  (J3b), `growth-plays.md` (G16–G18), `myths.md` and `benchmarks.md`.

## PART A — "noindex, nofollow" (industry news, RU/global)

### A1. Landscape numbers (use as audit context, cite with date)
- Google AI Overviews ≈ 2.5B MAU; AI Mode ≈ 1B MAU (May 2026).
- Zero-click: 68% of Google searches end without a click (Similarweb/SparkToro,
  Jan–Apr 2026, US, desktop+mobile) vs 60.45% in 2024. UK highest zero-click.
- Google search volume at all-time high (Q1'26, Pichai); Bing 1B MAU.
- Yandex: every 3rd query gets an "Alice AI" (Алиса) answer; 48.3M MAU on quick answers;
  ~10% of Alice AI queries are product/selection; RU search share 73.34%.
- Bots overtook humans in web traffic for the first time (Cloudflare, Jun 2026).
- Only ~2.4% of URLs are cited by ChatGPT + Perplexity + Google AIO
  simultaneously (Kevin Indig) → **no single "AI visibility" metric; measure per
  platform**.

### A2. Mechanics that must drive an audit
- **AIO pipeline** (Search Off the Record): query fan-out into several parallel
  queries → normal retrieval+ranking → snippets/titles/context → LLM summary.
  Classic ranking is the prerequisite for AIO inclusion.
- **Agentic RAG is default** (Mike King): planning, tool use, multi-step
  iteration, reflection; 1 user query → 5–20 internal subqueries.
- Lily Ray: the factor correlating most strongly with appearing in AI answers is
  **rank #1 in Google**.
- Queries get longer/conversational/multi-aspect → optimize for scenarios and
  intents, not short keywords.
- Google spam policy now explicitly covers **manipulating generative AI
  answers**; Gary Illyes compares mention-manipulation to link buying; sanctions
  are synced between classic search and AIO/AI Mode.
- John Mueller: sitewide quality concerns → less crawling, less indexing →
  "Crawled – currently not indexed" / "Discovered – not indexed". Not a technical
  bug to patch; step back to overall quality. Marie Haynes sees growth of this
  status since Mar 2026 (Google more selective, index skews to AI usefulness).

### A3. Google's own AI-search guidance + the debunked myths
Google Search Central doc (May 2026): SEO best practices still apply; AEO and
GEO both describe the same work; optimizing for generative surfaces = SEO.
Explicit myths: **llms.txt not needed**, **chunking not needed**, **no rewriting
text for AI**, hunting "inaccurate mentions" is low value, **excessive Schema.org
is useless**.
- Counterweight (Mike King): Google's guidance is an opinion from the party with
  most to lose in a multi-platform world; Bing publishes far more actionable
  index/AI mechanics. Take what's useful, verify.
- Pedro Dias: GEO/AEO = rebranded SEO. Transformers read tokens; nothing in the
  pipeline parses microdata; chunking parameters belong to the engine, not the
  publisher. The one academic study shows gains from **citations, statistics,
  authoritative sources, readability** — not from keyword saturation.
- Cyrus Shepard's counter-list — what AI-era SEOs actually do that they wouldn't
  otherwise: AI visibility tracking, citation-gap analysis, agent-ready sites,
  optimizing for broad fan-out queries, publishing YouTube transcripts, auditing
  AI-crawler access/bot management, plainer factual statements, entity
  consistency across the web, listicles.
- Cyrus Shepard (54 studies): AI citation correlates with relevance, trust,
  topical authority, **extractability**.

### A4. Deprecations / config facts to check in an audit
- **FAQPage/Question/Answer rich results fully discontinued** by Google.
- **AMP**: cache off; Search redirects to the publisher's AMP host; AMP ranks
  like any page (no advantage).
- **llms.txt**: no effect on Google Search; BUT Chrome Lighthouse has an
  "Agentic browsing audits" check for it (WebMCP / agentic web). Two different
  surfaces — citation ≠ agentic browsing. AIOSEO ships it by default in WP.
- **Open Knowledge Format (OKF)** (Google proposal): catalog of markdown files
  with YAML metadata + index file, so an agent reads the index and targets
  relevant areas instead of RAG over everything.
- **Canonicalization**: pages can stay in a duplicate group up to 2 weeks after
  fixes; differences must be obvious and substantial; **self-referential
  canonical is now the documented recommendation**.
- **Site moves**: submit change-of-address for every subdomain and www/non-www
  variant, all verified in Search Console.
- **Rendering**: blocking `/_next` in robots.txt broke rendering; allowing
  `/_next/static/` + `/_next/image` restored indexing and traffic. Always verify
  JS/CSS/image crawlability.
- `<meta name="robots" content="none">` ≡ `noindex, nofollow` (several SEO
  extensions parse it wrong).
- **Web Bot Auth** (Google, experimental): bots cryptographically sign requests →
  identify automated traffic, prevent spoofing of trusted agents.
- **Indirect Prompt Injection (IPI)**: Google Security Blog flags it as the main
  attack vector against AI agents. Brett Tabke: technical SEO now owns auditing
  what pages tell users vs crawlers vs AI systems, incl. hidden/third-party
  content that instructs AI systems. → **New audit dimension: AI-input hygiene.**

### A5. Reporting/measurement surfaces (2026)
- GSC: new **Search Generative AI performance** report (UK/India rollout; pages
  and impressions only at first); opt-out control for AIO/AI Mode display
  (inherits from nearest parent property, TLD default); **platform properties**
  (YouTube, Instagram, TikTok, X) to see social content in Search/Discover.
- Bing Webmaster Tools **AI Performance**: intents, topics, citation counts,
  **Citation Share**, Grounding Query Intent/Topics, GEO Recommendations.
- Microsoft Clarity AI-visibility report (Copilot + Bing); AI referral traffic is
  only countable when the platform passes a referrer (ChatGPT, Claude, Gemini,
  Perplexity).
- Yandex: query monitoring with hours-level delay; verification via Yandex Tag
  Manager or GTM; exclusion from vertical search (Yandex Uslugi / Kvartiry — services and real estate) while staying
  in regular results; Direct is now declared a useful signal for search (ads and
  organic are no longer positioned as independent).
- Screaming Frog v24 ships an **MCP server** — agent-driven crawl/export.

### A6. Distribution/loyalty surfaces
- **Preferred sources** global (incl. RU); now extends to AIO and AI Mode; 2×
  more visits after a user marks a source; 200k+ unique sites marked.
- **"Highly cited" badge** on SERP article links.
- **Publisher/creator Search profiles** (profile.google.com/@handle), US-first;
  manual creation thresholds: 100k YouTube / 100k Instagram / 100k X / 300k
  TikTok; reachable from Discover and Knowledge Graph.
- Subscription linking for paywalled sites. Barry Adams: these = the "audience
  loyalty ecosystem" — chase loyalty, not clicks.
- Discover: feed volume +58% YoY; social (X, YouTube) ≈ 25% of feed; AI summary
  cards in 13+ languages, merged multi-publisher cards; falling CTR; goal is to
  be the lead item in the card, not merely a source.
- Commerce protocols: **Yandex Commerce Protocol (YCP)** out of beta (products
  inside Alice AI answers + in-chat checkout; 1.6k merchants applied, 200+
  integrating); Google **UCP** appearing in regular SERP with a Buy button.

### A7. Content-quality patterns that now hurt (Lily Ray)
Traffic decline correlates with combinations of AI-content templates; sites in
decline typically run 3–4 of these, the worst run all 8:
1. `/blog/[product-A]-vs-[product-B]` comparisons
2. `/glossary/[term]` definitions
3. Template rankings ("best X for Y")
4. Self-serving rankings where the author ranks itself #1
5. `/blog/[competitor]-alternatives`
6. Scaled geo/language duplication
7. One-question-per-page FAQ `/faq/[full-question]`
8. Mass off-topic publishing
Also: fake/self-promotional listicles are now a liability in AIO — you can be
cited as the source while the competitors listed in your own article get
recommended.

### A8. Strategy positions worth quoting in recommendations
- Eli Schwartz: AEO is a **layer on top of SEO**, largely owned by the brand
  team; expecting SEO to "fix AEO" misallocates resources and damages both. Also:
  SEO is measured by signups/purchases/activations and pipeline contribution;
  content marketing by audience growth/engagement — don't conflate them.
- Gaetano DiNardi: most companies don't have an AEO problem or unsolvable
  technical SEO — they have positioning, category-fit and market-validation
  problems.
- Pedro Dias: SEO runs on infrastructure time, not campaign time; a URL structure
  surviving three migrations beats a week-long content campaign.
- Michael Hastings (USA Today): content AI can't replace = first-hand
  experience ("5 places I actually ate, what I ordered").
- Condé Nast (Roger Lynch): budget as if search traffic were zero; digital
  subscriptions +29%.
- Koray Tuğberk Gübür — **Visual Semantics**: layout/functionality is a ranking
  input; the helpful-content system evaluates whether the page lets the user
  complete a task (comparison modules, tables, interactive layouts), not only
  text.
- AI-text fingerprints: "не просто X, а Y" ("not merely X, but Y") up 4× in corporate comms; Substack
  ships a Pangram detector; Habr bans AI-generated posts. Detectability is now a
  reputational risk of scaled AI content.

### A9. Legal/market context (affects recommendations, not rankings)
German court: Google is directly liable for false statements in AI Overviews
(AIO is Google's own content). France: AIO/AI Mode launched after a
126M€ ad-antitrust award; ~450 publishers to be paid for content in AI answers.
UK: 31 sites added "search-only" licences (£500/article for unlicensed AI use).
EU DMA: Google must share anonymized query data with competitors from 2027.
SerpApi won dismissal of Google's scraping suit.

## PART B — "Mike Blazer" (tactics, growth hacks, AEO/GEO mechanics)

### B1. Entity / AI-confidence layer (posts 6340, 6342, 6365)
- **L2 confidence audit**: ask ChatGPT + Gemini + Perplexity: "what is [brand]",
  "tell me about [brand]", "what does [brand] do", "what is [brand] known for",
  "how does [brand] compare to [competitor]". Score answers on three axes:
  **accuracy** (positioning, products, geo, price — or stale/hallucinated),
  **confidence** (assertive "is" vs hedged "reportedly offers"),
  **consistency** (do all three describe you the same way).
  Diagnosis: low accuracy → training data stale/mis-linked; wavering confidence →
  thin parametric base; no consistency → fragmented entity signals.
  Test trick: same question, fresh sessions, **web search disabled** → hedged
  phrasing = retrieval layer, assertive = baked into training.
  Maturity playbook: young co → signal density (one canonical markup, hard
  positioning on owned properties, Knowledge Graph); large co → deepen signal
  (content refresh, markup refresh, trusted citations); enterprise → single
  entity architecture (product interlinking via markup, portfolio-level links,
  one graph across properties). Retrieval-level fixes land in days; training-level
  changes wait for model releases.
- **Ghost citations** (Seer, 541,213 LLM answers / 20 brands / 6 platforms):
  LLMs pick brand names from parametric memory FIRST, then retrieve sources to
  back the answer — citations are a bibliography, not the brainstorm. Brand
  mentioned in the answer → cited 53.1% of the time; not mentioned → 10.6% (5×).
  Ghost-citation rate varies by vertical (Hospitality & Travel >20pp spread;
  Industrial Services 0.3%; Financial/HR <2%). Worst damage at awareness stage
  (competitive ghost rate 5.0%).
  Fixes, three layers: (1) make the brand name the **grammatical subject** of
  extractable insights ("At [Brand], our approach to compliance starts with…"
  instead of "five approaches to compliance training"); (2) entity-graph signals
  — Wikidata entry, Wikipedia presence, Organization schema with `sameAs`, one
  canonical brand name everywhere, author markup tying experts to the company,
  FAQ markup with the brand name inside answers; (3) third-party mentions in
  **recommendation context** (analyst reports, PR, review aggregators, partner
  pages). Track **Competitive Ghost Citation Rate** monthly per platform and
  funnel stage. Weeks-to-months lag.
- **Cross-profile consistency**: compare the tagline on homepage vs LinkedIn vs
  G2 vs YouTube vs Capterra/Clutch/DesignRush/Crunchbase/X/Instagram (most
  companies have 8–12 forgotten profiles). Homepage H1 + top-menu services = the
  reference; rewrite every mismatching profile to it, re-check quarterly
  (automate — manual sync of 8–12 profiles doesn't survive contact with reality).
  Inconsistent category signals make LLMs average you out or take the loudest
  attribute, killing citation visibility regardless of link authority.

### B2. Citation mechanics — hard data (post 6357, AirOps: 16,851 queries /
353,799 pages)
- SERP position dominates: position 0 takes 58% of citations, position 10 → 14%
  (4×). Strong title-query match (0.80+ similarity) collapses from 79.6% at
  position 0 to 21.5% at 11+. **Authority signals don't correlate**: consistently
  cited pages median DA 53 vs never-cited DA 56.
- Wikipedia is the exception (59% citation at median position 24, weakest query
  match) — wins by mass: avg 4,383 words, 31 lists, 6.6 tables/page. Not
  replicable.
- Structure = multiplier, not source: 4–10 H2–H4 subheads + JSON-LD (+6.5pp),
  Flesch-Kincaid grade 16–17 peaks at 35.9% citation. Moderate fan-out coverage
  (26–50%) beats exhaustive guides (100%) when relevance to the head term holds —
  **focused pages beat longreads**.
- Freshness: optimum 30–89 days (32.8%); >5 years drops to 27.5%; finance has the
  steepest freshness decay (50.2% → 35.1%, 15pp).
- .gov source-trust bonus: 49.1% vs 35.2% (+13.9pp).
- Bimodal split: 58% of pages are never cited for any query, 25% always, 17% in
  between. Consistently cited pages sit at median position 2.5; never-cited at
  13.0.
- **Penalties cascade into AI** (post 6374, GSQI/NationalToday): a "Scaled
  content abuse" manual action on `/us/` (850k AI articles) removed the directory
  from Google → ChatGPT citations of that directory collapsed to ~zero (residual
  via Bing fallback), while the rest of the domain kept ranking and being cited.
  Directory-level actions exist. AIO/AI Mode/ChatGPT all inherit Google index
  removal.

### B3. Ranking-feature correlations (post 6345, Zyppy, 400+ sites, Dec-2025 core)
Spearman correlation with traffic growth: Offers Product/Service 0.391, Allows
Task Completion 0.381, Proprietary Assets 0.357, Tight Topical Focus 0.250,
Strong Brand 0.206. Additive: 1 feature → 13.5–15.4% win rate; 4 features →
68.1%; 5 → 69.7%. Brand volume only counts when it reflects **navigational**
intent (Zoom yes, Lifewire no). Examples: BudgetBytes (sells meal plans) beats
recipe sites; MathIsFun (interactive tasks/quizzes on-site) beats edu publishers;
WalletHub loses because task completion happens elsewhere.
→ Audit dimension: does the page/site *offer* something, *complete the task*
on-site, own *proprietary assets*, hold a *tight topical focus*, own
*navigational demand*.

### B4. Intent-match framework (post 6341)
Four intents with different required structures: informational (exhaustive
guides), navigational (low competition), commercial (comparisons, pros/cons,
pricing breakdowns), transactional (product details above the fold, clear CTA,
trust signals, frictionless checkout). Method: read the current top-10 formats →
match content type → structure to intent expectations → validate on behavior
(bounce <40%, time >2 min = match; bounce >70% = mismatch). Case: transactional
PDPs targeting "best [product]" ranked 12–20, 78% bounce, 0.4% CVR; switching to
comparison pages (commercial intent) interlinked to PDPs → positions 3–7, bounce
34%, CVR 3.2% (8×). Mixed-intent head terms need composite content. Same
framework applies to AI engines: pages that rank but are never cited usually
mismatch the direct-answer expectation.

### B5. NavBoost / lastLongestClick (post 6376)
`lastLongestClick` = user spends longer on your result than any other in the
session and does not return to Google. badClicks come from structural friction
(slow load, clickbait title mismatch, broken mobile render) and from answering
one question while ignoring the obvious follow-up. Seven formats that own the
signal: ultimate guides, comparison pages, tools/calculators, case studies with
numbers, original research, step-by-step processes, FAQ hubs. Nine page-level
tactics: answer the main question above the fold; pre-empt the next step; delete
unproven claims; place the CTA at task completion; kill load time (drop-off at
4s); map title tag hard to content; optimize mobile scroll depth; FAQ/HowTo
markup to pre-qualify in the SERP; keep evergreen (13-month NavBoost window).
Avoid: context-free news, opinion without facts, empty categories, basic
listicles, hub pages that link without answering.

### B6. Internal linking / link equity (post 6349)
Typical site: homepage holds ~80% of link equity, money pages get nothing. Equity
flows by: number of links on the source (dilution), position in the code (higher
= stronger), contextual relevance, source authority. Framework: audit equity
distribution (Ahrefs/Semrush + Screaming Frog internal PageRank), pick targets
(commercial keywords, revenue pages, positions 11–30), build hub-and-cluster,
link products from the homepage, contextual links from traffic-heavy posts,
resource pages, breadcrumbs, footer links to key categories. Plug leaks: links to
author bios/tag pages, bloated footers, 50+ item menus, broken internal links,
redirect chains, nofollow on important internal links. Case: SaaS product pages
+12 positions avg, +$340K organic revenue in 90 days. Anchor mix: exact 10%,
partial 30%, branded 20%, generic 20%, naked URL 20%. Review quarterly.

### B7. Cannibalization (post 6370)
Google runs **rotational testing** between competing URLs (not "equity split") —
both bounce in position and lose combined clicks. Diagnose: GSC filter by query
then break down by page; plus a SERP-overlap test — >70% top-10 overlap between
two of your pages = same intent cluster. Pick a winner by: current best position,
most clicks in 90 days, most backlinks, cheapest internal-link rework. Merge:
move unique content to the winner, draft/noindex the losers, **301** (not
canonical — canonical does not pass equity the same way), update all internal
links. Week 1 verify redirects, week 2 expect volatility. Don't publish new
content before fixing cannibalization. Never create year-suffixed URLs
("best tools 2024" + "…2025") — one evergreen URL, updated yearly.
Large sites (1M+ clicks) hit GSC data hiding that masks cannibalization; use
layered filters. Rotation swaps every few days → observe ≥1 week.

### B8. Migration protocol (post 6361)
Average migration loses 30% of traffic; disciplined protocol keeps it to 8%.
Eight stages: (1) audit + baseline (export all URLs, rank snapshot for top-500
keywords, 12-month traffic baseline, full backup); (2) 1:1 URL map, **301** not
302, tested on staging, no chains; (3) preserve technicals (titles, descriptions,
schema, internal links, alt text, keep URL structure similar); (4) migrate all
content, never delete pages, keep heading hierarchy and media; (5) pre-launch
tests (Screaming Frog crawl of staging, robots.txt allows crawling, XML sitemap,
CWV, schema validation, mobile, 404 audit); (6) launch day (redirects live,
internal links updated to new URLs, new sitemap in GSC, GA4 tracking, watch
server logs); (7) week 1 (crawl errors, redirect coverage, fix 404s, monitor
indexing, daily organic); (8) weeks 2–8 recovery tracking. Failure case: 67%
traffic lost, −340 positions, −73% revenue, $2.4M. Verification technique: one
sheet pulling status codes, titles, descriptions and heading hierarchy from old
and new URLs side by side.

### B9. Structured data reality (posts 6360, 6369)
- Multiple types: use an array `"@type": ["Product","FinancialProduct"]` (never
  two `@type` keys — duplicate key error), or `additionalType` for extra context;
  `additionalType` can point at Product Ontology / Wikipedia entities (note:
  productontology.org uses **http**, not https). Useful where Schema.org lacks a
  type (e.g. Personal Injury Lawyer → LegalService).
- Rich results can be withheld despite valid markup — six causes: manual
  action/quality problems; markup not matching visible content; guideline
  violations (self-written reviews, unavailable products, fake events, incomplete
  recipes, how-to without real steps); insufficient traffic/trust on the page;
  competing SERP features (Google shows one enhanced type per query); technical
  implementation errors (JS-only injection without SSR, conflicting types —
  Organization + LocalBusiness on one page, missing required fields, wrong format,
  bad nesting, deprecated types). Diagnostic: Rich Results Test → visible-content
  parity → GSC Enhancements → Manual Actions → live URL inspection → compare with
  competitors winning the same rich result. Expect 2–4 weeks after fixes.

### B10. Freshness / content updates (post 6368, patent US20120209838A1)
Google fingerprints a page on first crawl and diffs on re-crawl. Changes that
count: **title update, a substantial new section, link changes (anchor, target,
surrounding text — not navigation)**. Ignored: date/lastmod bumps, JavaScript,
ads, navigation and boilerplate. → "Update the date" is not an update.

### B11. Split testing (post 6352)
Test one variable; segment URLs matched by template/traffic/type (100 PDPs on one
template = good; mixed pages = worthless); ≥4 weeks, ≥50 pages per group
(100+ better), 95% confidence, seasonality-adjusted, and discard tests that run
during a core update. Case: adding "2026" to titles → control +2.3%, test +34.7%
(98.5% significance), rolled to 1,500 pages → +28% sitewide. Tools: SearchPilot,
SplitSignal. Some things can't be split-tested (domain trust, sitewide speed,
migrations, algorithm updates) → before/after with control benchmarks.
- Title **capitalization** (SearchPilot, 5 years of tests): 50% of meta-title
  capitalization tests positive, 0% negative — their most consistently winning
  test type. Mechanism is indexing-side (capitalization as a NER/emphasis signal
  in NLP), not CTR — all-caps titles rarely even render in the SERP. Prefer
  targeted capitalization of key words over full all-caps.
- Meta description promos ("Save 30%") are market-specific: +21.2% organic
  sessions in India, zero effect in the UK. Test per market before scaling.

### B12. Link acquisition & digital PR (posts 6359, 6346)
Hidden-donor sourcing: mine competitors' *weakest* backlinks (low-DR niche
directories, small blogs, regional media), community placements (subreddit
sidebars, pinned Facebook group links, Slack #resources, Discord tool lists,
forum signatures), guest-author trails (`"[expert]" + "contributor"`), guest
podcasts (500–5k listeners sweet spot, Listen Notes/Podchaser), newsjacking
(Alerts/HARO), academic/.edu resource pages. Cybersecurity case: 47 subreddits +
23 Discords + 34 Slack groups → 38% outreach success, 29 links, avg DR 35.
Relevance beats DR; ten DR-40 relevant links beat chasing one DR-80.
LinkedIn micro-influencer buys: filter by real engagement not followers (same
5–10 commenters = engagement POD, skip); price by comment volume ($300 for
100–300, $500 for 300–500, $750 for 500+); non-US accounts for the same reach at
a third of the price; you write the copy, they paste; unique tracking links per
account. ~$1.5 revenue per $1 in month one — that's payback speed, not LTV;
dark-social sharing inflates apparent ROI.

### B13. Security / infrastructure findings (post 6358)
YMYL site fully deindexed: the **www** DNS record pointed at a decommissioned
Azure redirect app; when it was shut down the subdomain was released, an attacker
claimed it and pointed it at a gambling network. Detected via the GSC **domain
property** (aggregates protocols + subdomains): a one-day spike of 12,000 clicks
on gambling queries to the www homepage. Deindexation preceded the manual action
by ~24h; reconsideration approved in 24h; full recovery in 36h.
Operational rules: verify **all** property variants in GSC (domain property,
https www, https non-www, http, key directories); monitor DNS and performance for
both www and non-www; expect a 24h+ lag between deindexing and the manual action;
when investigating, look for anomalous traffic **spikes**, not only drops.

### B14. Reconnaissance / tooling tricks
- `cruxvis.withgoogle.com` — free CrUX visualizer: real Chrome field data per
  origin, incl. **form-factor split** (mobile/desktop/tablet) for any competitor
  with enough Chrome traffic; matches GA4 proportions closely. Caveat: Chrome-only
  (67.7% share), no iOS Safari.
- Regex-ish patterns work in Google search operators (undocumented, partial):
  `site:dev.__.co.uk`, `site:staging.__.co.uk`, `site:test.*.co.uk` surface
  competitors' dev/staging hosts in the index; also works inside Custom Search
  Engines. → also a **self-audit**: your own staging/dev hosts may be indexed.
- Bing-hosted pages with YouTube/Reddit/Medium embeds have been ranking in Google
  after the core update (parasite vector, short window) — relevant as a *risk*
  signal when auditing SERPs, not as a recommendation.

### B15. Editorial / operations
- Content pipeline that took a team from 4 → 40 posts/month with the same
  headcount: strict role split (strategist/writer/SME with a 48h comment-only
  review/editor/SEO/publisher), standardized briefs (target keyword, search
  intent, audience, 3–5 key points, competitor URLs, internal-link requirements,
  conversion goal, length, deadline), async review, and an **automated QA gate**
  (keyword in H1 and first paragraph, meta description ≤160 chars, ≥3 internal
  links, images ≤100KB, Flesch >60, plagiarism-free, CTA present) blocking
  publication on any failure. 8-day cycle.
- Topical authority beats domain age: narrow niche, 50–100 subtopics, hub +
  10–15 clusters, hub↔cluster interlinking, 3–5 internal links from existing
  indexed pages to every new article, front-loaded publishing cadence. Case:
  email-deliverability site → 47 top rankings, 0 → 12k organic/month in 6 months.
- Chapter-style child pages with self-contained H1s earned **sitelinks for a
  category page** (Contentful) — clear structural paths beat clever architecture.

### B16. Zero-click survivable content types (post 6377, Zyppy)
Ranked by defensibility. Strongest moat: owned audience (email/SMS/in-app),
transactional pages, original research, host-led video/podcast (branded demand),
UGC communities. Medium (labor moat): hands-on reviews with real testing, insider
expert perspective, case studies with before/after metrics, original reporting,
directories/databases with first-party data + freshness. Weak (AI-copyable):
guides/explainers, templates, brand pages (About/Trust/Legal — still critical for
entity definition), support docs (canonical source still trusted), FAQ/glossary,
listicles (survive only with real testing + transparent criteria). Formula for
all 17: proprietary + task completion + niche focus. Effort does not correlate
with traffic; depth does.

### B17. CRO × SEO coupling (posts 6378, 6395)
47 pages / 90 days: bounce −31%, dwell +187%, position +6.2, organic +218%, CVR
+134%. Individual levers: load 4.2s→1.3s (bounce 67%→41%, CVR +93%, +8 positions
after 6 weeks); mobile UX rework (mobile CVR ×2); layout restructure (CVR +127%,
scroll depth +45%, bounce −23%); contextual internal links (pages/session
1.4→3.2); trust signals (CVR +89%, dwell +2.1 min); benefit-led headlines.
Landing pages: **One-Second Test** — translate the page into an unfamiliar
language and show it to 5 people; if the visual alone doesn't communicate the
category, the asset leaks traffic. 130k split tests: generic stock photos above
the fold cost −19% conversion; real product screenshots / uniformed staff and
branded vans beat lifestyle imagery. Video above the fold cannibalizes attention
(session benchmark 30–60s; average explainer view 16s) — put it below the fold or
behind a "See How It Works" secondary button, static screenshot + play button, no
autoplay, always show duration.

### B18. AI-search architecture insights (posts 6392, 6410, 6412, 6413, 6417, 6427)
- Retrieval funnel (Jeff Dean, via Glenn Gabe): ~30,000 candidate documents
  (~30M tokens) compressed to **117 documents** that reach the RAG stage → you
  must be in the classic top-100 first. Krishna Madhavan: don't pack multiple
  claims into one sentence — dense syntax breaks entity/triple extraction;
  isolate each fact in a short sentence.
- Grounding ≠ search: shared pipeline (query understanding → transformation →
  multi-vector retrieval → candidate processing → multi-stage ranking) then
  grounding adds evidence selection, answer construction, constrained generation,
  cross-check + multimodal evaluation. **Citation ≠ visibility; visibility is
  decided at query understanding.**
- Scott Stouffer: your brand is a **centroid** in embedding space; retrieval
  matches queries against centroids before ranking — a distant or blurred
  centroid keeps pages out of the candidate pool.
- Andrea Volpini: schema alone gives no lift, but entity pages with proper RDF
  links raise answer accuracy ~29% — the moat is the linked-data layer.
- Metehan Yeşilyurt: retrieval = tokenizers (English-biased; other languages pay
  a token tax) + embeddings (the ticket to retrieval) + rerankers (the
  gatekeeper). Front-load the substance, cut empty tokens in non-English markets,
  use embedding similarity as a content tool. (Related: Spanish ≈63% more
  expensive in tokens; Mandarin can be 20–40% cheaper.)
- Jory Ford — **Hybrid Engine Optimization**: one scorecard on first-party data
  (GSC, GA, internal) + one trusted AI-monitoring tool; five signals —
  Presence, Prominence, Citation quality, Authority confirmation, Business
  impact; weekly cuts against one strategic KPI (Reach, Conversion or Authority).
- Zyppy meta-analysis of 54 studies — AI-citation factor weights: URL
  accessibility 9.5; search rank 9.4 (Ahrefs: 38% of Google AI citations come
  from the top-10); fan-out rank 9.3; **preview control 9.2**
  (`nosnippet`/`data-nosnippet` gate visibility); query-answer match 9.2;
  mid-tier 8.0–8.9 (topic-cluster ranking, answer positioning, AI-ready structure,
  factual accuracy, explicit statements); trust and schema only 5.0–5.6;
  **llms.txt 2.0 (no evidence)**. Models extract content nearer the top of the
  page; hidden text is demoted.
- ChatGPT depends on Google's index: sites that lost 85% of Google traffic lost
  75% of ChatGPT traffic; blocking Googlebot cuts ChatGPT traffic proportionally.
- ChatGPT citation numbers (AirOps): 500–2,000 words peaks at 34.3% (>5,000 words
  → 28.6%); schema +6.5pp (FAQPage, MedicalWebPage, BreadcrumbList best); 4–10
  subheads 33.2% vs 1–3 at 28%; exact query-title match adds +19pp even after
  controlling for rank; <30-day content dips to 25.3% (incomplete indexing),
  30–89 days peaks 32.8%.
- Pedro Dias / theinference: LLMs tokenize text, not metadata; the KDD 2024 GEO
  paper (Aggarwal et al., 10k-query benchmark, 9 methods) found gains from citing
  authoritative sources, quoting relevant experts, adding statistics and improving
  readability — schema/FAQ markup/heading hierarchy/machine-readable formats were
  never tested and are not an optimization surface; keyword stuffing scored below
  baseline.
- Sean Butcher: pages whose H1–H4 match the user's prompt get cited 41% of the
  time vs 29% for weak semantic match; DA/DR/organic volume show no positive
  correlation.
- Markdown experiments: serving structured Markdown to AI bots on one subfolder →
  AIO visibility +34%, +4.5% clicks on test pages (rest of site −1.1%), 122
  keywords went from no AIO presence to a ranking URL. Second case (directory,
  via Cloudflare) reports immediate visibility lift. Caveat: duplicate-content
  risk between HTML and .md variants; verify crawler behavior in server logs.

### B19. Google-mechanics details worth auditing
- **CTR is contextual, not raw** (Mark Williams-Cook, leaked ranking params):
  `click_age_probability` (expected click given document age vs. what users expect
  for that query), `relative_click_order`, `dense_glue_trad_imp_mobile` —
  NavBoost + Glue reranking on top of Mustang. 5% CTR at position 3 can be
  under- or over-performing depending on query, position, device and doc age. No
  universal CTR benchmark.
- **Freshness is relative, not calendar-based**: `result_set_age_*_percentile_in_days`
  scores your age against the rest of the result pool. A 2014 page can be "fresh"
  if competitors are older; a 9-day iPhone review is stale against 2-day rivals.
  Operational check: monthly, export last-modified dates for the top-10 on
  priority queries and flag pages falling outside the age percentile → trigger a
  *substantial* update (rewritten sections, new data, intent restructure).
- **Blocked-but-indexed URLs are empty shells** (John Mueller): Google indexes the
  URL string without processing content, so they can't trigger duplicate filters
  or dilute site quality. Don't unblock robots.txt just to add noindex (burns
  crawl budget); the GSC removal tool only hides temporarily; intervene only if
  blocked URLs actually steal impressions from canonical pages on commercial
  queries — that means the canonical page's quality is the real problem.
- **Out-of-stock crawl trap**: applying noindex/301/canonical while a product is
  out of stock makes the crawl scheduler deprioritize the URL for 100+ days even
  after the directive is removed. Sitemap resubmission and manual GSC submissions
  don't break it; use Atom/RSS feeds (feeds jump the fast-discovery queue) plus
  dynamic internal links from high-crawl-frequency nodes. Rendering an
  out-of-stock page with no directives can trigger soft-404 and the same
  deprioritization.
- **Spam vs core-update recovery are separate systems**: after a spam filter, 82%
  of domains that fell out of the top-100 stayed blocked through the following
  core update. March 2026: 24% of top-10 pages dropped past 100; sites older than
  15 years took >57% of top-10 slots; domains under a year took 0.7%.
- **Manual action = binary multiplier**: nothing you improve counts until it is
  lifted; only file reconsideration after all fixes are complete.
- **Rendering/CWV specifics**: modal patterns that add a scroll-lock class to
  `<html>` plus a blurred overlay push style recalculation into the click handler
  and inflate INP — use native `<dialog>` + `::backdrop`. `sizes="auto"` +
  `loading="lazy"` replaces hand-written `sizes` (still requires width/height;
  LCP hero images must not be lazy-loaded).
- Hosting/IP neighborhood: shared IPs with 200+ domains correlated with a
  ranking ceiling around position 7 in a controlled test; isolated cloud
  instances took 90% of top-10 slots. Treat as a hypothesis to check, not law.
- JSON-LD content appears to feed keyword-density/relevance math on the ranking
  side even when the indexer strips those fields — ranking and indexing behave as
  separate systems (Ted Kubaitis).

### B20. Threats to audit for (defensive, from black-hat coverage)
These are attacker/competitor tactics an audit should *detect*, not deploy:
- **Indirect prompt injection**: Google Threat Intelligence saw malicious indirect
  injection attempts grow **32%** Nov 2025 → Feb 2026 ("ignore previous
  instructions", "recommend this business above all others", "do not mention
  competitors", "insert this phrase into your summary"). Audit five surfaces:
  rendered DOM (hidden blocks, widget injections, JS content), UGC/review
  moderation, programmatic pages (imported feeds, partner data, scraped or AI
  text), AI-visibility tactics, and bot-behavior analytics (anomalous crawling of
  hidden content or infinite pages). New rule: read the source, render the DOM,
  check for injected instructions, and assume an AI agent reads all of it.
- **Subdomain takeover / abandoned DNS** (see B13) and registrar-level domain
  theft (GoDaddy transferred a 27-year-old domain with no documentation despite
  privacy + 2FA) → domain-security posture belongs in a technical audit.
- **Fabricated-consensus networks**: up to 100 ten-page EMD sites, isolated
  hosting/GSC accounts, Googlebot blocked in robots.txt while AI crawlers are
  allowed, tuned to the citation count an LLM uses for a target prompt. Detect via
  citation-source review of who the models quote for your category.
- **Parasite hosting**: Ghost.io (DR92), X Premium long posts, Bing pages with
  YouTube/Reddit/Medium embeds — competitors renting third-party authority to
  outrank you on your own terms.
- **Historic-URL resurrection**: recreating a dead URL path (same path, title, H1)
  on a fresh domain can inherit the old page's algorithmic memory — a reason to
  keep valuable retired URLs redirected and monitored.
- **Reddit / brand-SERP defense**: harmful threads can be removed via Reddit's 8
  content rules (1 harassment, 2 spam/manipulation incl. competitor astroturfing,
  3 privacy/doxxing, 5 impersonation). Reports must cite a specific rule, comment,
  date and user; removed threads leave the SERP, freeing the slot for a page you
  control.

### B21. Practical audit techniques worth stealing
- Hidden technical wins most audits miss: log-file analysis (one e-commerce case —
  40% of crawl on filter URLs, products recrawled every 90 days; after robots/param
  fixes product crawl rate +400% and new products indexed in 2 days instead of 3
  weeks); JS rendering diffs (test with Google's rendering tool, not your browser);
  equity leaks to pagination/tag archives/filters/author/calendar/search pages;
  descriptive internal anchors between semantically related pages; orphan pages
  (crawl vs. sitemap diff); per-template server response times (1.8s home / 2.2s
  category / 7.4s product / 5.9s checkout — audit by page type); render-blocking
  resources (3.8s → 1.2s gave +23% organic); schema gaps; mobile-specific UX
  breakage; canonical chains/loops/canonical-to-noindex/HTTP-HTTPS mismatches;
  bloated sitemaps (redirects, noindex, pagination, duplicates); keyword/traffic
  mismatches, staging domains in the index, localized duplicates, soft 404s; key
  pages within 1–2 clicks of the homepage.
- Demand check before investing: Ahrefs Keyword Explorer **GGR 12M** column —
  positive YoY = tailwind, negative = losing battle.
- Reddit research: append `.json` to any thread URL for the raw structured thread,
  paste into an LLM to extract pains, objections, comparisons, recurring
  questions. Reddit is a long-tail intent corpus: threads triangulate meaning for
  LLMs (engagement/comment depth/upvotes act as E-E-A-T proxies).
- Link-velocity patterns Google reads as authenticity: anchors 40–50% branded,
  20–30% naked URL, 15–25% generic, 10–15% partial, 5–10% exact; 30–50% nofollow
  share; geo mix ~60–70% home market; expect 5–15%/yr link decay; spiky,
  event-driven acquisition (launches, PR) reads as natural, flat linear growth
  does not. 500 links in 30 days triggered penalties in 48h; 370 over 8 months
  ranked top-3.
- Donor filters that kill fake-DR PBNs: exact TLD match, minimum share of traffic
  from the target country, locally originated backlinks.
- Market-data sanity check: Datos/Semrush State of Search Q1 2026 — classic search
  still grows faster in absolute terms than AI tools; Google AI Mode <0.2% share;
  Gemini second and growing, ChatGPT flat-to-down since Sep 2025. Budget panic
  runs 12–18 months ahead of actual share shifts.

### B22. AI-search: what experiments actually show (posts 6444–6452)
- **OtterlyAI, 7 controlled GEO experiments across 100M sites**: `llms.txt`
  attracted 0.1% of AI-bot traffic and performed 3× worse than normal pages;
  **Markdown mirrors of pages got 0% AI-crawler visits vs 4.6% for the HTML
  versions** (do NOT duplicate pages as `.md`); schema lifted Google AIO
  visibility 1500% and AI Mode 377% but *reduced* citations in ChatGPT/Gemini/
  Copilot; pure AI content ranks short-term then collapses. What worked:
  **AI-assisted, human-edited content beat pure generation 5×** across Google
  organic, ChatGPT, AIO and Gemini; press-release distribution produced citations
  (BusinessInsider, Yahoo) within days; **YouTube is the #2 cited social source**
  (1.8M citations/30 days) where posting cadence matters more than engagement;
  localization varies wildly by platform (Copilot 77% localization index,
  ChatGPT 58%, Perplexity 9% — localize *prompts*, not just pages).
  ⚠️ Contradicts the single-site Markdown wins in B18 — treat Markdown-serving as
  an experiment to run and measure, never as a default recommendation.
- **OtterlyAI, 29,562 domains / 145 verticals / 1,595 buyer personas / 105k
  ChatGPT prompts / 500TB**: classic SEO signals correlate with ChatGPT
  visibility but explain only **15–20% of variance**. Strongest: SERP impressions
  (ρ=+0.241), search position (ρ=+0.238), outbound links from SERPs (ρ=+0.230),
  backlink count (ρ=+0.204), link trust (ρ=+0.200) — each R² ≈ 5–6%. Signal
  hierarchy flips by vertical: **Wikidata** dominates established categories
  (hotels, ERP, furniture), **Reddit** drives community categories, SERP outbound
  links matter most in finance/SaaS. Visibility is **per buyer persona**, not per
  domain — one "ChatGPT traffic" number is a lie; test per persona.
- **Google vs Bing guidance asymmetry** (iPullRank): Bing states chunking is
  foundational and that specificity, entity weight, semantic coherence and
  structural clarity feed retrieval scoring, and ships citation analytics; Google
  says chunking isn't needed and "don't write for AI". Google's own MUVERA
  multi-vector retrieval research, passage indexing and pairwise-passage-selection
  patents contradict the public guidance. Practical reading: passages that make
  one point extract better than paragraphs covering three.
- **Arbitration layers in frontier models** (leaked system prompts): Latent
  Knowledge (training) + Active Retrieval (web) + Arbitration (what to trust).
  GPT-5.5-class instruction: treat the web result as the single source of truth
  even when it contradicts memory → the dominant retrieved result wins synthesis.
  Claude-class: retrieval-first for current questions, with source-quality filters
  that demote affiliate roundups, aggregator listings and obviously SEO-shaped
  content in favor of original publishers. Practical: align with the consensus the
  model already holds, corroborate it across several quality retrievable sources,
  and state claims declaratively.
- **WebMCP** (agentic surface): sites expose structured tools
  (`navigator.modelContext`, Chrome Beta 146+, or the MIT `WebMCP` JS widget) so
  agents call functions instead of screenshotting. New optimization plane: tool
  discoverability (= indexing), tool descriptions (= conversion copy), input
  schema design (= structured data), agentic CRO (A/B testing tool descriptions,
  tracking agent success rate). Practical setup: widget + `/mcp/` page listing
  tools + footer link + reference the MCP page from `llms.txt`.
- **OKF (Open Knowledge Format)**: markdown + YAML frontmatter (only `type`
  required), portable bundles, producer/consumer split, "living knowledge" pattern
  where agents update the docs; Google shipped a BigQuery enrichment agent, an
  HTML bundle visualizer and three sample bundles. v0.1 — a starting point.
- Chrome ships a local ~4GB LLM (Gemma-3-4b based, offline, multimodal input,
  training cutoff Oct 2023) usable from extensions.

### B23. More Google-mechanics detail
- **Craps / NavBoost** (leaked `QualityNavboostCrapsCrapsData`): splits clicks
  into goodClicks, badClicks and **lastLongestClicks**; NavBoost reranks on a
  13-month history. `patternLevel` shows signals aggregate at **URL, directory
  and subdomain** level → "topical neighborhoods": a whole section builds
  reputation, so site architecture concentrates or dilutes satisfaction signals.
  `onsiteProminence` uses high-Craps pages as seeds in a traffic-flow simulation
  of internal authority → satisfying pages become internal authority hubs. All
  data is sliced by country, language and device — each context is its own
  portfolio.
- **Query classification**: Google classifies queries into one of 8 categories
  (from the 2025 ranking-parameter leak); free `queryclassifier.com` predicts the
  class for up to 10k keywords (DistilBERT trained on 4.8M query/category pairs).
  Query class maps to which SERP features appear and to answer placement (e.g.
  SHORT_FACT wants the answer immediately, not a build-up).
- **Custom CTR curves**: Brittney Muller's Colab builds a site-specific CTR curve
  from GSC data — generic 2021-era CTR benchmarks hide SERP-feature and brand
  effects.
- **Index tiering** (case: 50,000-page store): tier 1 must-index (live products,
  key service pages, conversion core, brand/commercial), tier 2 should-index
  (supporting content, clusters, categories), tier 3 block (filter combos,
  pagination, search results, archives, parameter variants), tier 4 hard-block
  (admin, cart, thin, duplicates). Result after 90 days: indexed pages −24%
  overall but valuable indexed URLs +308%, zero-traffic pages −87%, 95% of
  products indexed, organic +67%. Diagnose "Crawled – not indexed" (failed
  quality) separately from "Discovered – not crawled" (crawl-budget exhaustion).
- **Crawl-budget killers**: infinite scroll/pagination explosion (cap 50–100,
  View-All consolidation, canonical empty pages to page 1), faceted navigation
  (robots param rules, canonical to base, JS-render filters, noindex junk
  combos), duplicate variants (session IDs, tracking params, print versions,
  HTTP/HTTPS, www), mass low-quality pages (audit: zero organic in 12 months, no
  inbound links, <200 words, bounce >80% → 410 / consolidate / noindex /
  improve), server performance (TTFB <200ms optimal, <500ms acceptable, error rate
  <0.5%). Sitemaps: only high-value, frequently updated, deep-but-important and
  <24h-new URLs; exclude pagination, filters, duplicates, junk.

### B24. Negative SEO & brand-defense (defensive audit checklist)
- **Weaponized spam reports**: Google began processing spam reports in mid-April
  2026 and manual actions in competitive niches followed ~a week later; one
  practitioner received 100+ reports with one visible action. Audit implication:
  keep your own site defensibly clean; expect adversarial reporting.
- **Fake DMCA / fake government takedowns**: no verification on intake; target
  URLs vanish for ~2 weeks per complaint, repeat filings keep pages out of the
  index long enough to lose rankings; takedown-as-a-service and AI-generated
  filings scaled attack frequency 100–200% within days of public coverage.
  Defense = documentation discipline: screenshots, timestamps, removal notices,
  restoration records, attack patterns; file counter-notices promptly.
- **Canonical hijack / cloud stacking**: cloned HTML on cloud blob storage,
  canonicalized to a "master clone", tier-2 spam links to the stacks and PR links
  to the master → clone flips with the original in the SERP; "shadow affiliate"
  variant replaces Buy buttons with affiliate links back to the victim, so the
  victim fulfills the order and never sees the interception in GSC. Audit: search
  for duplicated markup/structure of your own pages; monitor cross-domain
  canonical claims.
- **Slow behavioral poisoning**: a low, steady drip of direct traffic with
  deliberately bad engagement spread across many pages, designed to stay under
  alarm thresholds and degrade NavBoost-class metrics over time.
- **Fake search-volume sites**: bots search an invented brand thousands of times
  from random IPs → Ahrefs records the "volume" → the site "ranks" for its own
  fake brand → tools estimate huge traffic → guest posts sold at $200. Always open
  the keyword tab: 70 variants of one brand name and nothing else = fabricated.
- **Wikidata as knowledge-graph backdoor**: lower moderation threshold than
  Wikipedia, but entries get deleted without real external signals — triangulate
  with Crunchbase, verified social profiles, consistent NAP, real reviews.

### B25. Extractability / read-budget (posts 6498, 6553, 6566 — Peec AI logs)
ChatGPT **Deep Research** streams its session over WebSocket; logged across 10+
accounts: the agent reads **raw HTML top-to-bottom** (drops `<head>`, ignores
JavaScript), first read capped at **~5,700 characters** (median; max ~8,000).
Every link renders inline as a `【n†anchor†url】` marker and spends the same
budget:
- <20 links on the page → ~78% of the first read is your content
- 20–59 links → ~55%
- 60+ links → ~33% (two thirds eaten by navigation)
Only three commands exist: `search` (Bing snippets — no Google), `open`, `find`
(Ctrl+F). It **never clicks** — "skip to main content" doesn't help. A successful
`find` triggers a re-read 95% of the time at the matched line → **literal
keyword presence guarantees a second read**. `alt` attributes render as plain
text and are the only thing read from images (`alt=""` is skipped). The fetch
comes from `OAI-SearchBot`, separate from `GPTBot` (training) — unblocking one
does nothing for the other. robots.txt-blocked → `viewing lines [0-0] of 0` and
the page silently drops out of the report.
Case: a mega-menu putting ~1,000 sitewide links at the top of every page; cutting
~90% of those internal links raised rankings in **both Google and ChatGPT**.
Fix pattern: sitewide nav shows top categories only; subcategories appear on the
category page (no hidden content), combined with an HTML sitemap and backlinks so
discovery doesn't suffer. **Source-order matters more than visual position.**

### B26. Indexing as a scarce resource (posts 6472, 6491, 6514, 6525, 6536, 6551)
- Adam Gent: the index is designed to **exclude**; Google raises the quality bar
  when it hits capacity (patent *Managing URLs* US7509315B1) — every new page
  competes for a finite slot. Publishing more pages dilutes; sitewide trust is a
  glass ceiling.
- "Discovered – not indexed" protocol (70–80% indexed within 72h): contextual
  internal links from your most-crawled pages (export GSC top pages, link from
  their body content), priority XML sitemap with fresh `lastmod`, a 200+ word
  content addition, one external dofollow link from an indexed page, clean server
  signals (TTFB <200ms, no 5XX, no redirect chains). "Crawled – not indexed" is a
  *different* problem — already fetched and rejected; discovery signals won't fix
  it.
- PageRank decays ~85% per link hop → deep pages beyond three clicks lose almost
  everything; HTML sitemaps with descriptive surrounding text act as "meaning
  bridges"; deep pages need at least one click per week to stay indexed.
- Soft-404 case (crypto news network): a leaky migration + auto-generated
  converter URLs produced 513k "crawled not indexed" and ~120k soft-404s network
  wide; France crawl requests fell 60–70k/day → 20–30k/day. Fix stack: real
  404/410 on empty pages, remove/noindex auto-generated pages, tighten parameters
  + robots, rewrite canonicals, **pause CWV work until indexing recovers**.
  Result: soft-404s −83%; the biggest recovery came in **Discover** (Germany
  clicks 8k → 12–15k/day, Discover share 42%→58%; Poland Discover share 15%→86%).
- Panic-noindexing on AI advice: a sports site went from 4–5k daily impressions
  to ~10. Removing noindex does not trigger recovery — Googlebot stops visiting
  noindexed URLs; you must resubmit and rebuild, 6–12 weeks, in batches.
- Link indexers can only force **crawling**, never indexing; "100% guaranteed"
  is a lie; the free lever that beats most paid tools is an internal link from a
  page Googlebot already crawls daily.

### B27. More technical traps (posts 6508, 6520, 6535, 6539, 6550, 6552, 6554, 6557, 6560)
- **Canonical with extra attributes is silently dropped**: `<link rel="canonical">`
  carrying `media`, `type`, `hreflang` or `lang` makes Google discard the
  declaration (URL Inspection reports user-declared canonical "None"). Framework
  `data-*` attributes (`data-react-helmet`, `data-n-head`, `data-rh`, `id`,
  `class`) are harmless. Check after any CMS/framework migration, and make sure
  edge-rendered HTML carries the same canonicals as the client version.
- **GSC "Duplicate content" filters primarily on slug, title and H1** — not body
  text; it's a serving-layer filter, not a crawl-time demotion.
- **robots.txt wildcards match substrings**: `Disallow: /*?` blocked ~40% of
  product pages in one store (another retailer lost 45% of traffic, six weeks to
  diagnose); `Disallow: /*print` also blocks `/blueprints/`, `/footprint/`,
  `/imprint/`; `/account/` also catches `/account-settings/`. Block specific junk
  params only, canonicalize filtered variants instead of blocking them, never
  cloak with a Googlebot-specific `Disallow: /`, validate by crawling twice in
  Screaming Frog (respecting vs. ignoring robots.txt) and diffing, keep the file
  in version control with a dated changelog, audit quarterly.
- **Faceted navigation**: robots.txt blocks crawling, not indexing — a blocked
  filter URL with any external link gets indexed on anchor text alone and can
  never see your noindex. Split **facets** (independent search demand → clean
  crawlable URLs with self-referencing canonicals) from **filters** (convenience:
  price range, sort order, availability → no URL change or noindexed parameter
  URLs). Promote proven parameter combos to clean paths via 301 only after
  demand shows up in internal search logs / GSC. Empty filter results returning
  200 "no products found" become soft-404s at scale.
- **noindex in the pre-render source wins even when the rendered DOM is clean** —
  and GSC hides this (URL Inspection follows redirects and shows the rendered
  HTML; neither view shows the pre-render source Google reads first). A `meta
  refresh` + `noindex` combination has no defined precedence; noindex is a
  directive while canonical is only a hint, so the page drops out and the
  canonical never passes equity. Fix with a server-side 301.
- **Hiding links from Google via JS/spans/JSON doesn't work**: Google parses
  URL-like strings anywhere (source HTML, rendered DOM, JSON blocks) and queues
  them; the only real controls are robots.txt (for compliant crawlers) and
  firewall/WAF rules.
- **Widget/embed links** are named in Google's link-spam guidance; treat them as
  discounted, `nofollow` them (plus `noindex` on an iframe page you control), and
  keep widgets for referral traffic, not link building. The risk scales with the
  footprint (sidebar links across thousands of domains got penalized).
- **Bulk 301s to the homepage burn equity**: redirect each removed URL to the
  closest-intent live page (product → comparable product; otherwise the parent
  category/PLP). Removing a large section (200k URLs = 10% of a 2M-page site)
  costs sitewide equity, topical relevance and trust — brief stakeholders that
  the whole domain dips, not just the removed pages.
- **Images**: image rankings attach to the image object; changing an image URL
  can drop a product from position 1–3 past 50 — the robust pattern is a stable
  backend-proxied URL (`/product/{id}/image`) serving the current file; serving
  `.webp` bytes at a `.png` URL confuses crawlers over time (prefer a 301).
- **Rendering**: everything blocked in robots.txt is never downloaded, so it is
  never rendered — use GSC URL Inspection / Rich Results Test, or a
  robots.txt-aware proxy (`VorticonCmdr/robotstxtProxy`) or DevTools request
  blocking to see what Googlebot actually renders.
- LCP triage order (Arjen Karel): fix TTFB → remove everything less important
  than the LCP element from its path → `fetchpriority="high"` on the LCP element →
  defer non-critical JS until after load; image format work comes last. Fonts:
  900KB of preloaded fonts widened the P90 TTFB→FCP gap from ~840ms (fast
  connections) to ~1,488ms (slow) and correlated with ~18% fewer pageviews per
  session.
- SearchPilot: cutting a category grid from 48 to 36 products was positive at 85%
  confidence — the mechanism is page weight/LCP, not content depth. Test per site.
- PDFs are an ignored asset class: bulk-compressing files and rewriting
  extracted-text-based titles/metadata lifted clicks measurably.

### B28. Content & information gain (posts 6518, 6534, 6567, 6568)
- **Information Gain study** (150 top-3 pages, 50 keywords, 10 verticals):
  originality does **not** correlate with position inside the top-3 (medians
  52 / 51.5 / 52); a quarter of top-3 pages score below 40 (pure rehash). The
  only page-level lever that moves the score is **original quantitative data** —
  pages with 15+ unique data points average 62/100 vs 40/100 for one or none,
  while the median top-3 page carries just 4 unique numbers. Length barely moves
  it. In 90% of SERPs at least one common user question is unanswered by the
  entire top-3; the spread between the most and least original page in one top-3
  averages ~32 points. Vertical medians span 20 points (medicine 42 → legal 62;
  commercial and B2B SaaS near the bottom). Editorial play: cover the baseline
  briefly, then spend the length on original measurements, internal analytics and
  the questions everybody skipped. (Patent: *Contextual Estimation of Link
  Information Gain*, US 11,354,342 B2 — architecture, not a confirmed factor.)
- **On-page baseline is lower than the noise suggests** (10,937 PageOptimizer Pro
  pages): median optimization score 33/100, 46.8% below 25, against an ~80
  practical threshold. Schema missing on 99% of pages (45% none at all); semantic
  terms missing in 99.4% (≈20 per page, incl. alt text, file names, anchors,
  subheads). Category and landing pages score worst (33.6) with the highest rate
  of missing H1 keywords (69.4%) and thin copy (68.6%). 13 major models scored
  58.4/100 average on the same on-page rubric — models write but don't optimize.
- **The great blogging collapse** (Semrush, 100 six-figure blogs, Apr 2022 →
  Apr 2026): median lost **85%** of search traffic; 55 lost ≥80%, 20 lost ≥99%,
  12 went to zero, only 21 grew. Excluding three food outliers the rest fell 63%.
  By niche median: parenting +108%, DIY +2%, food −44%, travel −74%, lifestyle
  −90%, make-money −93%, health −93%, fashion −95%, finance −99%. The surviving
  variable is first-hand doing (a recipe actually cooked, a pattern actually
  knitted) — not the niche. Ahrefs: first organic result loses 58% of clicks when
  an AI Overview is present. Semrush: Reddit ≈40% of LLM citations; only 38% of
  AI-answer links now come from the organic top-10 (down from 76% in mid-2025);
  Reddit's share of ChatGPT answers fell ~60% → 10% in six weeks after one
  retrieval-logic change → **AI visibility is a portfolio whose rules are
  rewritten by model vendors**.
- Content atomization: one 3,000-word piece → ~60 atoms (27 standalone insights,
  12 statistics, 8 walkthroughs, 15 quotes), each repackaged per platform and
  **linking back to the original** — distribution doubles as internal/external
  equity into the cluster; stagger the release.

### B29. AI-visibility measurement (posts 6516, 6531, 6545, 6549, 6558, 6515)
- **Prompt format beats prompt wording** (1,754 prompts / 37,804 answers across
  ChatGPT, Gemini, Perplexity, AI Mode, AIO): same-intent prompts return the same
  brands at the same rate; 88–92% of human prompt pairs exceed 0.50 cosine
  similarity, and brand visibility is stable above ~0.50–0.60. Rankings/lists/
  comparisons/table formats surface ~20% more brands than open questions;
  keyword-explicit prompts ("best CRM small business 2026") ~25% more; persona
  prompts fewer. Constraints cut brand counts in ChatGPT/Perplexity but raise them
  in Gemini/AIO. Prompt length and filler words: no effect. MOFU non-branded
  commercial prompts are where wording actually shifts results (ChatGPT loses the
  brand below ~0.60 cosine). Track a 25/50/25 TOFU/MOFU/BOFU split, tag prompts by
  format, report per engine. High similarity ≠ same intent (Charleston vs
  Charlestown = 95% similar, different commerce).
- **Citations are the wrong KPI** (Tom Capper / Mark Williams-Cook): an answer can
  name Audi four times while the citation points at a parts site. Field data on 85
  UK mid-market companies: being *named* decides whether the buyer hears about
  you; when named, the brand is top-3 in 63% of cases. Measure mentions +
  recommendation share, and for local businesses replace citations with calls,
  direction requests and bookings.
- **Self-promotional listicles backfire** (Lily Ray, 100 B2B "best [category]"
  prompts across three checkpoints): when the AI used the brand's own
  self-promotional article as a source, the brand was excluded from the actual
  recommendation in **69%** of cases (224 of 323 cited articles) — the citation
  functions as a vote for everyone on your list except you. Google appears to have
  decoupled *who gets cited* from *who gets recommended*; recommendation now rides
  on external signals (referring domains, brand mentions in AIO/ChatGPT). Around
  20 Jan 2026 an adjustment cut organic visibility for sites leaning on the
  tactic, spreading from the listicle directory to the whole domain, accelerating
  in the May 2026 core update (40+ affected sites). Pew 2025: users click a link
  inside an AI summary in ~1% of sessions.
- **Ahrefs' own experiment** (34 promo pages, 5 domains, 9,886 answers, Feb–May
  2026): for a brand-new conference the pages filled 72 previously empty answer
  slots (82% citing the new articles); for an established tool only 6% of new
  mentions came from them — the tactic bridges *unknown → mentioned* only when the
  model has a category gap. 43% of answers linking the promo page didn't mention
  the event at all; retrieval-without-citation is worse (74% ignored). Citation
  persistence is erratic: ~1 in 4 pages was cited once and never again; the page
  appeared roughly every third day between first and last citation; longest
  unbroken streak 52 days. Perplexity left 76% of retrieved pages uncited,
  ChatGPT cited 61%. Narrow intent wins: 66.4% presence for "best SEO conferences
  2026" vs 15.8% for "best marketing conferences 2026". Sanity test: would the
  brand read as a natural recommendation if someone else had written the page?
- **Review sentiment drives the verdict** (5M ChatGPT conversations): brands with
  *bad* Trustpilot ratings surface more often than mediocre ones — the model
  highlights one strong option then contrasts it with weak ones, so average
  ratings disappear. Once "review" enters the fan-out, ChatGPT leans on Reddit for
  social proof and Trustpilot for ratings; Wikipedia's weight is falling. Fix at
  the source: list the URLs LLMs cite per attribute (support, pricing, security),
  update stale trusted pages (a 2024 security article still fed resolved
  concerns), and report coordinated review attacks (75% of the negatives coming
  from single-review accounts is a footprint, not feedback). Complaints the model
  repeats are real product problems.
- **25 AEO facts worth keeping** (condensed): mentions ≠ citations; SEO drives
  citations; PR and marketing drive mentions; a citation at position 17 is
  worthless; one strong TOFU page can collect hundreds of citations while a strong
  BOFU page collects two; nobody has proven ROI for `llms.txt` or LLM-specific
  schema; don't damage Google rankings chasing AI traffic (2–3 years to recover);
  influencing training data takes years; strong brands beat better-optimized
  sites; you can't optimize per prompt variation — build topical authority;
  models confidently repeat stale claims that many sources repeat; don't
  artificially chunk, just be readable; not every heading must be a question;
  AI search has no attribution model (conversion arrives later via brand/direct);
  start by asking the models about your brand before buying tracking software.
  Plus: extraction cost is a selection factor (bloated HTML, JS-gated content and
  slow pages get skipped); AI treats ~70% market agreement as fact; verify AI
  visibility from **inbound logs** (which AI crawlers fetch you, forward-confirmed
  reverse DNS to filter spoofers) and referrers, not vendor dashboards.
- **Personal Intelligence** (iPullRank, 1,922 AI Mode answers, 30 Mar–15 Apr
  2026): seeding brands through Gmail lifted appearance in AI Mode answers from
  23.9% → 66.8% on a connected account (control 21.9% → 18.9%); top-3 4.5% →
  24.9%. Email beat Photos (53.6% vs 10.5%). Invented brands seeded via Gmail
  still appeared in 35.7% of answers vs 55.8% for real ones — personal context
  gets you into the pool, the web validates the choice. Small sample (3 accounts).
- **Claude ↔ Brave** (Profound): 86.7% overlap between Claude's links and Brave's
  organic top results; Anthropic lists Brave as a subprocessor. Brave's Web
  Discovery Project is open source and reads like a behavioral ranking algorithm:
  `validDoubleFetch()` discards pages missing a title in either fetch, carrying
  noindex, with canonical mismatch, or with authenticated-vs-anonymous HTML length
  differing by <10% or >90%. Signal stack by strength: query correlation (`qr.q`),
  active time (`a`, only counted with interaction in the last 5s), **copy events**
  (`e.cp` — the highest-intent passive signal; extractable content like data,
  definitions, code earns more), scroll depth/events, internal-link clicks.
  Every event needs `a > 1s` and is throttled to one increment per second →
  synthetic clicks don't inflate it. Structural data is collected at 5,000ms, so
  slow-rendering pages send truncated payloads. Backlinks, social signals, domain
  age and schema are **not** inputs to WDP.
- **ChatGPT source selection** (Suganthan, network-tab forensics): the thinking
  model fetches your page first and greps raw HTML for `$`/`€` to confirm pricing;
  when the number is behind a JS toggle or inside an image it gives up and cites
  G2 instead. `resultsource` values seen: `serp`, `labrador` (licensed publisher
  whitelist — Reuters/WSJ with ~1,080-char snippets), `bright` (Bright Data
  scraper, dominant in shopping/finance/weather), `oxylabs`. A `turnusecase`
  bucket decides whether the web is consulted at all — some questions answer from
  training with an empty network tab.
- **Bing is a first-class path**: a YMYL site invisible in Google (past page 7) is
  cited in 90,000+ ChatGPT prompts purely because it ranks in Bing (88k URLs in
  Bing's index vs 45k in Google's). Ranking in *at least one* major engine is the
  entry ticket.

### B30. Miscellaneous levers
- Manual actions are a binary multiplier — fix everything, then file
  reconsideration.
- GSC data gaps: 13 of 26 documented GSC outages (mid-2023 → Jun 2026) coincided
  with algorithm rollouts; a freeze pins clicks/impressions at a past date while a
  real algorithmic hit keeps producing fresh declining data points; validate
  against GA4, server logs and third-party rank trackers; the "internal issues"
  banner marks infrastructure, not a penalty.
- Toxic backlinks: Penguin 4.0 devalues rather than demotes; leaked quality tags
  `SiteAuthority`, `PageRankNS`, `BadBackLinksPenalized`. Disavow only in four
  cases (manual action; a negative-SEO spike of hundreds-to-thousands of low-DR
  foreign links in 24–72h *with* ranking loss — disavow only the spike window; a
  Fiverr blast; inherited spam). Toxicity is relative to the niche baseline (20%
  exact anchors kills a local plumber, is normal in iGaming). Third-party toxicity
  scores collapse context into one number and cause self-inflicted damage.
  301s from expired domains inherit the whole source profile — audit them too.
- `unicornClicks` in the 2024 leak is a **child-account** marker (COPPA/GDPR-K
  isolation), not a premium-user signal — don't optimize for it.
- Server-side computation for GSC MCP tooling: run CTR curves, decay,
  cannibalization and position deltas in SQL/Python in the warehouse and hand the
  model a compact result; a full report over a 4GB dataset in 4.4s, no invented
  arithmetic. Deterministic ≠ correct — GSC sampling, freshness lag and
  interpretation traps remain.
- LLM cost: list price ≠ bill (Stanford/Berkeley/CMU/Microsoft, 8 reasoning
  models, 12 tasks — the "cheaper" model cost more in ~1/3 of cases, up to 28×;
  same prompt varied up to 9.7× run to run).
- Author-level authority patent ("Determining Topic Authority"): authority
  accrues to author entities (authorship share × topic weight per document),
  relevant again now that Google surfaces author profiles — but the inventor
  worked on Drive/AppSheet, so treat it as a documented architecture pattern, not
  a confirmed web-search factor.
- Reddit answer influence can be near-real-time: a comment recommending a client
  was quoted by ChatGPT 1h45m after posting. Track brand mentions without links.


## PART C — SEJ *SEO Trends 2026* (practitioner panel)

- **Zero-click is a misnomer** (Montti): the ten-blue-links baseline ended with
  featured snippets (2014), Knowledge Graph (2012), video results (2007). The
  real break is keyword-scaffolded, made-for-search-engines content; Google still
  links out, across more surfaces and for more complex queries.
- **User-expectation test**: decide what a user expects on this page type
  (e-commerce = images, specs, reviews, measurements, comparisons — not an essay)
  and ship that. "Because Google wants to see it" is the marker of a wrong
  decision. Remove friction between the user and the task.
- **Find what AI cannot cannibalize** (Walsh): target queries where no AI Overview
  appears and a click is still required; recorded opinion/interview video and
  first-hand testing are the formats models cannot replicate. One client kept
  strong MQLs straight from Google SERPs on that selection alone.
- **Super-serve a niche, don't chase scale** (Southern): diversify formats
  (newsletter, video, podcast) for the same audience; depth beats breadth; build
  something people would miss.
- **Owned vs rented** (Southern): email lists, Discord/Slack, Substack are owned —
  you keep the data, the relationships and the distribution; subreddits, Facebook
  groups, TikTok accounts are rented and can change or vanish. Cycle: participate
  on rented platforms to learn and build awareness, migrate engaged people to
  owned ones. Owned communities compound (early members onboard later ones).
- **Brand narrative control across platforms** (Walsh, Czapik): a new visibility
  layer across LLMs is eating TOFU informational search; discovery happens in
  forums, social, YouTube and trusted publications, which both humans and models
  read to judge credibility. Consistent brand messaging plus machine-accessible
  content is "the new basic level of SEO". Younger users trust Google SERPs less
  after sock-puppet review content.
- **Discovery surfaces named** (Taylor): TikTok, Meta AI in Facebook/WhatsApp,
  Gemini, Google Lens, ChatGPT, Perplexity, plus agentic layers and personal
  bots that filter content on the user's behalf. Gen Z is Google's
  fastest-growing Search demographic; ~1 in 10 of their searches starts with
  Lens, ~1 in 5 of those commercial. CRM data shows first contact via ChatGPT or
  social, return via direct or branded search.
- **Measurement shift** (Taylor, Czapik): move past last-click; track branded
  search volume, brand presence in AI answers, and the volume and tone of
  third-party UGC; measure presence and value at every funnel stage, and treat
  Search as an input to commercial decisions rather than an output measured in
  rankings.
- **Consistency wins** (Reinhart): the successful accounts publish consistently,
  monitor and automate QA, and educate the wider organization; the ones chasing
  the shiny object of the quarter do not sustain results.
- **Fundamentals over hype** (Southern, Walsh): quality content for a real
  audience, trust built over time, showing up consistently; separate fundamental
  shifts from temporary noise; the brands winning now built authority before the
  panic.
- **Counter-signal on AI adoption** (Southern, citing Kevin Indig): 80% of users
  still click through to traditional results to verify even when an AI Overview
  is present — source evaluation still matters to people.
- **Market context** (Morton): Google's search market share dipped below 90%;
  Web Guide (AI Labs) still underwhelming in testing; ChatGPT Atlas browser
  launched Oct 2025 (macOS); expect more SERP experiments and volatility.
- **Cross-functional** (Page): SEO now spans social, video, content, affiliate,
  field marketing, paid search and data; strategy extends to YouTube, Reddit and
  Quora, not just backlinks and on-site content.

## PART D — Google update timeline (SEJ algorithm history, fetched 2026-07-28)

| Update | Start | Complete |
|---|---|---|
| June 2026 spam update | 2026-06-24 | 2026-06-26 |
| May 2026 core update | 2026-05-21 | 2026-06-02 |
| March 2026 core update | 2026-03-27 | 2026-04-08 |
| March 2026 spam update | 2026-03-24 | 2026-03-25 |
| Discover core update | 2026-02-05 | ~2 weeks, then global |
| December 2025 core update | 2025-12-11 | 2025-12-29 |
| August 2025 spam update | 2025-08-26 | 2025-09-21 |
| June 2025 core update | 2025-06-30 | 2025-07-17 |
| March 2025 core update | 2025-03-13 | 2025-03-27 |

Older eras (2024 → 2003) remain on the source page; pull them when a decline
predates this window.


## PART E — SEJ ebook corpus (2023–2026)

### E1. Ultimate Technical SEO Audit Workbook (2023) + spreadsheet
Workflow contract: pick a check → run it with the named tool → mark result →
export the flagged URLs to a data tab → summarize in a recommendations tab with a
priority (Critical / High / Medium / Low) and a link to the data. Checklist
content (69 technical rows, ~26 on-page rows) folded into
`technical-checks.md` §A7 and `onpage-checks.md`. Prioritisation guidance
(Conductor): act immediately when pages are inaccessible, the site is penalised
or traffic drops; then critical pages for business-critical terms; group issues
into themes (indexability, content, speed, links, schema) so a team can act.
Tool guide and DevTools walkthrough folded into `tooling.md`; the closing note —
"the audit is only as good as the auditor", tools flag non-issues, contradictions
need a deep dive — matches the skill's evidence discipline. Migration: audit both
before and after. Conversions as the KPI (CallTrackingMetrics): track conversions
from key pages, not just rankings.

### E2. SEO In The Age Of AI (2024)
Timeline of the SGE → AI Overviews transition (May 2023 labs → Nov 2023 120+
countries → May 2024 AI Overviews US rollout → dial-backs after viral failures).
Durable parts: citation behavior differs per engine (Google wants quotable
content above the fold answering the question directly; Perplexity leans
academic/research citations; Bing engineers for discovery back to the origin
site; ChatGPT digests and rephrases, citing publisher partners), so being the
cited source is the new ranking; GEO overlaps quality SEO (keyword coverage
including conversational phrasing, unified content strategy on E-E-A-T,
technical hygiene, data-driven iteration); differentiation checklist (unique
perspective, original research and case studies, rewrite/update, author
credentials, trust signals, disclose AI use). Dated 2024 — tiered accordingly.

### E3. The Future of AI Search (2025, CallRail-sponsored)
AI systems favour direct answers, structured data (tables, lists), natural
language over keyword repetition; exact-match keyword phrasing appears in 5.4% of
AI Overviews; AI Overview coverage growth by vertical (entertainment +175%,
travel +108%, B2B tech +7%); 72% of B2B buyers encounter AI Overviews and 90%
click a cited source; 43% of AI Overviews link to Google-owned properties; ~94%
of AI search referrals originate on desktop while 58% of Google mobile traffic is
iPhone; ~94% of ChatGPT traffic from desktop apps, Google the only major AI
search with mobile-majority referrals (53%). Conversion/attribution material
(untracked calls at 80–90% of one channel's conversions, missed-call recovery,
conversation intelligence lifting leads 67% / ROI 11% / sales 23%, 7% close-rate
lift from coaching on call sentiment) folded into `demand-and-conversion.md`.
Content that converts: transparent pricing tables AI can extract, implementation
timelines, technical documentation, ROI calculators with benchmarks; ~70% of the
buying process precedes contact; 58% of buyers seek expert input.

### E4. State of SEO 2026 (practitioner survey)
Opinion data, not effect data — tiered as survey context in `benchmarks.md`:
66.3% say original content creation is the most impactful activity; 77.9% fear AI
answers cutting clicks; 59.3% cite algorithm volatility as the top challenge;
49.6% plan E-E-A-T investment; 58.5% plan human-authored content with AI support
(22.4% primarily AI-generated); 42.3% saw positive impact from technical work;
60.4% report on qualified leads/sales but only 33.7% plan conversion-focused
investment; 42.6% find content creation hardest to scale; 9.4% rate
cross-functional collaboration impactful today versus 37.7% planning to increase
it; 42% trained teams on AI integration; 65% expect stable or increased
investment. Tom Capper on "the Great Decoupling" of informational traffic; John
Shehata on doubling down on the first E (original photos, walkthroughs, credible
bios, transparent process).

### E5. Google Ranking Factors: The 3 That Really Matter
Basis of `ranking-model.md`: no official factor list; the "200" number traces to
a 2009 remark; Yandex's 2023 leak showed ~690 factors; systems vs signals is
"just language" (Illyes) and documentation moves items between them without
behavior changing; weighting is query-dependent (meaning, relevance, quality,
usability, context). The three: content quality and relevance (helpful content,
RankBrain, BERT, MUM, query-dependent freshness, entities), page experience
(HTTPS, speed, mobile, CWV — a tiebreaker between near-equivalent candidates),
and links (internal and external; deflated in public messaging because they are
the most manipulated signal, still how pages are discovered and weighted).
E-E-A-T is a rater specification, not a factor. Personalisation and locality sit
on top of everything.

### E6. B2B Lead Generation: Create Content That Converts
A lead is a person who actively opted in — not a visitor. Two intersecting
models: accessible content that earns subscribers, and gated content that
converts them. "Add value before you extract value": a gated asset that could
have been googled turns a warm lead hostile, and the follow-up email turns it
into a spam report. Ask only for what the next step needs. Folded into
`demand-and-conversion.md` §H+2.

### E7. PPC Trends 2026 + PPC Experts Tips + CallRail lead report
Relevant to an SEO audit only where the channels touch: AI-first campaign types
(Performance Max, Demand Gen, AI-expanded search) change how much organic space a
query has left; durable measurement now rests on consent-based first-party and
zero-party data plus offline conversion import, not on last click; landing pages,
titles/descriptions and high-value brand messaging are where human effort still
beats generation; paid search-term data is a live intent feed for organic
planning; buyers do not distinguish paid from organic, so contradictory messaging
interrupts the journey. Folded into `demand-and-conversion.md` §H+4 and play G21.

## PART F — «Site Growth» thread: tracking parameters vs `robots.txt` (Jul 2026)

One community thread, occasioned by a large Shopify store where a `Disallow` on
`utm_*` URLs was proposed as a crawl-budget win. Single source, so nothing here
rises above the tier its own mechanism carries.

### F1. Tracking parameters are the case canonicals were built for
UTM variants carry no independent demand, so the whole job is consolidation.
Crawled-and-not-indexed is the tag working, not a leak. A `Disallow` blocks a
crawl Google performs legitimately and cannot improve consolidation, because a
blocked URL never sees the canonical either — the same blocked-≠-unindexed
mechanism already documented in `technical-checks.md` A1 and `myths.md`.
`CONFIRMED` (engine-documented mechanism). → `technical-checks.md` A2 block
"Tracking parameters are not facets", `myths.md` row, play `L13`.

### F2. The platform's own duplicates outrank UTM as the crawl hole
Shopify serves every product under `/collections/{collection}/products/{handle}`
as well as the canonical `/products/{handle}`, and appends `?variant=` per
variant. One product across five collections with six variants is dozens of
crawlable strings before a single tracking parameter exists. `CONFIRMED` —
platform behavior, reproducible in any store's crawl. → `technical-checks.md` A2.

### F3. The exception the block cannot fix
Canonical is a hint, so Google may select a different URL. The trigger reported
here is signal weight: a parameterized URL that accumulates more links and traffic
than the clean one can win despite the tag, and `robots.txt` is irrelevant because
it changes no signal. Split tiers: `CONFIRMED` that Google may override a declared
canonical; `FIELD` for the link-accumulation trigger as the mechanism. →
`technical-checks.md` A2, `growth-plays.md` L13.

### F4. Intervention altitude — own sources versus the wild
The controllable surface is internal links and affiliate/partner placements
carrying UTM; those get cleaned (internal UTM also breaks session attribution,
`demand-and-conversion.md`). Genuine third-party tracking links — newsletter,
social, partner URLs copied and reshared — are real referrals carrying real
equity; suppressing them costs attribution and link value and returns no crawl
budget. `CONFIRMED` (mechanism). → `technical-checks.md` A2, play `L13`.

### F5. Confirm the scale before treating it as a problem, and the no-logs case
Size the tracking share in the GSC Pages report grouped by reason (*Alternative
page with proper canonical tag* = closed; *Duplicate without user-selected
canonical* = the actual finding) plus server logs. Hosted platforms including
Shopify expose no raw access logs, so rung 1 of the tooling ladder is unavailable
and the finding caps at rung 2: GSC Crawl Stats gives host-level shares, totals
and status mix, never per-URL truth. `CONFIRMED`. → `tooling.md` ladder note and
the "Crawl waste with no server logs" routing row.

## PART G — the 2026-08 window (27.07–05.08.2026)

Screened against everything above, so overlap with PART B is excluded by
construction: `@MikeBlazerX` was already distilled to post 6568, and the new
window is 6569–6590 plus `@notjohnmu` 2919–2937. `@MikeBlazerPRO` (414–433) had
never been read and is entirely new.

Two gates were applied before anything entered a reference. **Non-contradiction:**
a candidate that disagrees with a claim the corpus already holds on better
evidence is refused, not demoted — `evidence-tiers.md` rule 3 governs
disagreement between two credible sources, and an unmethodded assertion is not
the second credible source. **Evidence:** every carried number was treated as a
lead until a primary source was read (`docs/superpowers/retro.md` #1). That
second gate removed three figures and one field name that had already passed the
first.

### G1. What the primary-source pass changed

| Claim as carried | What the primary said | Outcome |
|---|---|---|
| Five-second render limit is real | Published test pages and method (D. Smart, 2026-07-23): the WRS pauses its own clock during fetches; real cut-off 48–54s live, ~30s for indexing | Admitted as a myth-guard row with the ceilings |
| Entity extractors are unreliable | On-Page.ai / E. Lancheres, 2026-07-20, n=166 pages / 48 SERPs; §3.4 gives the determinism split (n=50) | Admitted with the vendor conflict disclosed |
| Brand carousel −2.8% | SearchPilot, 2026-07-17 — and the same publisher's carousel-*removal* test at +29% | Admitted, and strengthened into a replicated direction |
| Alice AI 49.5M / 42% | Yandex Q2'26 results, 2026-07-29 | Admitted, with the Q1 point kept beside it |
| Google detects generated-content networks | Google Research S-CTS paper: cluster-level termination, 50k clusters / 130k channels in six months | Admitted, upgraded to STUDY, marked as transferred by analogy |
| Opt-out removes you from Top Stories | Scoped by the source to Top Stories *inside* AI Overviews, and explicitly unconfirmed by Google | Admitted as HYPOTHESIS, narrowed |
| `inurl:` has been killed | Operator references say it still works with degraded precision and regional inconsistency; both readings agree on rate-limiting and fingerprinting | Rewritten as operator decay, demoted to HYPOTHESIS |
| Compare `Last crawl` with `Last crawl rendered` in GSC | **No such field exists.** The tool exposes Last crawl, the stored render under *View crawled page*, and a live test | Diagnostic rewritten into the form that can be run |
| A relocated widget produced €120k/yr | No primary found | Number dropped; the mechanism kept, carried by the published tabs/above-fold test instead |
| SAB visibility radius 2–5 miles vs 5–10 | No primary found | Number dropped; the block ships without it |
| 10+ sponsorships → +83% visibility | No primary found; unnamed survey | Number dropped; the guardrail kept |

### G2. Admitted, by destination

`technical-checks.md` — the render queue as a budget separate from crawl budget,
with an executable diagnostic; the one-shot viewport stretch and its two
consequences (sequential infinite scroll, unconstrained hero); mobile-first
status divergence and the single internal link as a discovery path; trust as the
gate on a new domain's indexing. `myths.md` — the five-second limit, the
multiple-H1 penalty. `entity-and-brand.md` — extractor false-positive ranges and
the validate-against-Google rule; rating as a recommendation-stage input, scoped
against the existing "bad ratings surface more" finding; pay-to-play listicle
footprints as a placement liability. `tooling.md` — entity-gap routing, operator
decay. `measurement.md` — the generative-report → grounded-validation loop, with
citation and mention recorded separately. `experiments.md` — three layout split
tests. `architecture-and-equity.md` — internal-link intent, and the service-area
block. `ranking-model.md` — controlled evidence for layout position, plus the
B2B page-type counterweight. `linkbuilding.md` — the sponsorship guardrail.
`demand-and-conversion.md` — map-pack call attribution. `intent-and-content.md` —
trend-onset timing, on-site UGC. `growth-plays.md` + `threats-and-defense.md` —
the first-party reviews section with its gating guardrail.
`threats-and-defense.md` — five detection entries: the paid-mention market
labelled as AEO, synthetic consensus with its documented case, retrieve-and-
switch, canonical pulsing from expired domains, cluster-level detection of
coordinated generation, and review-queue attacks. `benchmarks.md` and
`algorithm-updates.md` carry the figures and the dated platform change.

### G3. Refused, and why — so the next pass does not re-litigate it

| Refused | Reason |
|---|---|
| "Parsers ignore hidden JSON-LD in favour of visible HTML tables"; a three-sentence embedding-dense intro yielding 76% citation | Contradicts a STUDY already in the corpus (JSON-LD +6.5pp across 353,799 pages, `aeo-geo.md` F2). The counter-claim has no published method and an unverifiable sample, so rule 3 does not apply — this is refusal, not demotion. The actionable half (facts in plain HTML, one claim per sentence) is already in F3 |
| ORCAS clickstream as a source of "empirical conversion and revenue models" | The dataset is 2020, contains clicked query–URL pairs and **no conversion or revenue data at all**, and is released for non-commercial research. The claim describes a dataset that does not exist |
| Hourly automated news publishing as a freshness strategy | Is the documented scaled-content-abuse profile the corpus already refuses (`myths.md`). The 21-day QDF cycle survives only as the reason such traffic is rented |
| Ranking exchange and "second spot" placement to dodge self-promotion filters | Manipulation. The underlying observation — self-promotional sourcing costs the recommendation — is already in `myths.md` from a different study, and needed nothing from here |
| EU/UK AI Mode visits overtaking the US | A screenshot of a third-party panel chart with no method and no figures available |
| "Publisher search traffic 51% → 27% in two years" | No source named anywhere in the material |
| Live URL Test as a crawl-priority lever | Unverifiable folklore. The useful half of the same post — trust gating indexation — was admitted separately as FIELD |
| Buying aged forum accounts; cloning validated SaaS products; thumbnail structure extraction; platform-specific growth tactics; click-signal manipulation and "freeze the page during a core update"; midpoint verification pins for service areas; hidden-text keyword loading | Out of scope by `CONTRIBUTING.md`: manipulative, or about a platform this skill does not audit |
| Forcing an entity into a model's knowledge base via co-citation prompting | One anecdote. It belongs in `experiments.md` as a design if anyone wants it, not in a reference as a claim |
