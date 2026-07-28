# Track F — answer engines: retrieval, extraction, citation

AEO and GEO describe the same work: being retrievable, readable and quotable by
systems that answer instead of linking. Google's own position is that this is
still SEO; treat that as one interested party's opinion and verify per engine.

## F1. How the answer actually gets built

1. **Query fan-out.** One user query expands into several parallel queries
   (AI Overviews) or 5–20 internal sub-queries (agentic RAG: planning, tool use,
   multi-step iteration, reflection). Google's own description of the AIO chain
   (Search Central, 2026-05) — fan-out → ordinary retrieval and ranking →
   **snippets, titles and page context from the selected results** → the model
   writes the summary. CONFIRMED (engine statement). Audit consequence: the
   title and the snippet-eligible text *are* the payload handed to the model,
   not just click bait.
2. **Retrieval.** Normal ranking machinery selects candidates. Scale reported by
   a Google engineer: ~30,000 candidate documents (~30M tokens) are compressed to
   about **117** that reach the generation stage. Being outside the classic
   top-100 means you are never considered.
3. **Grounding.** After candidate selection the pipeline adds evidence selection,
   answer construction, constrained generation, cross-checking and multimodal
   evaluation. **Citation ≠ visibility** — visibility is decided far earlier, at
   query understanding and retrieval.
4. **Arbitration.** Frontier models hold three layers — latent knowledge
   (training), active retrieval (web), and an arbitration policy deciding what to
   trust. Leaked system prompts show retrieval-first instructions ("use the web
   result as the source of truth even if it contradicts what you remember") and
   source-quality filters that demote affiliate roundups, aggregator listings and
   obviously SEO-shaped content in favor of original publishers.
5. **The retrieval stack under a budget.** Three layers do the work: tokenizers
   (English-biased — the same meaning costs ≈63% more tokens in Spanish and
   20–40% fewer in Mandarin), embeddings (the ticket into retrieval) and
   rerankers (the gatekeeper). Engines are minimizing entropy under hard token
   and energy limits, so watery text loses to dense focused passages
   (conference presentation, SEO Week 2026-04 — HYPOTHESIS, mechanism plausible,
   no controlled test).

Implication: align with the consensus the model already holds, corroborate it
across several retrievable quality sources, and state claims declaratively.

**Whose description of the pipeline to trust.** The two engines that publish
disagree in public (iPullRank comparison, 2026-06). Bing states chunking is
foundational and that specificity, entity weight, semantic coherence and
structural clarity feed retrieval scoring, and it ships citation analytics.
Google states chunking is unnecessary and "don't write for AI" — while its own
MUVERA multi-vector retrieval research, passage indexing and
pairwise-passage-selection patents describe passage-level machinery. Do not
resolve this by chunking your content: chunk length, overlap and boundaries are
the engine's parameters, not yours (myths.md). The residue that survives both
positions is editorial — a passage that makes one point extracts better than a
paragraph covering three. Treat Google's public guidance as one interested
party's account and verify per engine.

## F2. What correlates with being cited (ranked evidence)

Meta-analysis of 54 published studies, factor weight out of 10. These weights
describe the **retrieval and grounding stage** — what decides whether a live
fetch can be quoted into an answer now. They say nothing about the **training
stage**, where a crawler hit proves only that a URL was fetched (myths.md).
Fetchable is a precondition for a citation today; it is not evidence the model
knows you.

| Factor | Weight |
|---|---|
| URL accessibility (can it be fetched at grounding time — retrieval stage, not training) | 9.5 |
| Search rank (38% of Google AI citations come from the organic top-10) | 9.4 |
| Fan-out rank (coverage of the expanded sub-queries) | 9.3 |
| Preview control (`nosnippet` / `data-nosnippet` gate what can be shown) | 9.2 |
| Query–answer match | 9.2 |
| Topic-cluster ranking, answer positioning, AI-ready structure, factual accuracy, explicit statements | 8.0–8.9 |
| Trust signals, schema | 5.0–5.6 |
| `llms.txt` | 2.0 (no evidence) |

Controlled analysis of 16,851 queries / 353,799 pages on ChatGPT citations:

- Retrieval **position** dominates: position 0 is cited 58% of the time,
  position 10 → 14%. A mediocre page at position 0 (56%) beats a highly relevant
  page at position 6+ (26%).
- **Domain authority does not correlate** — consistently cited pages had a
  *lower* median DA (53) than never-cited ones (56). YouTube (DA 100) 2.4%;
  Wikipedia (DA 95) 59.2%. Pages are judged, not domains. Scope: this 59.2% is
  Wikipedia's citation rate across the dataset's **general/informational**
  queries. It does not carry into commercial evaluation prompts — once "review"
  enters the fan-out, Reddit and Trustpilot take over and Wikipedia's weight
  falls (entity-and-brand.md G4). Both hold; they describe different query
  classes.
- Exact query–title match adds ~+19pp even after controlling for rank; strong
  H1–H4 match to the prompt: 41% cited vs 29% for weak matches. But the match
  cannot rescue a bad position: pages with 0.80+ title–query similarity are
  cited 79.6% of the time at position 0 and 21.5% at position 11+. STUDY.
- Source-class bonus: `.gov` pages 49.1% cited vs 35.2% for the rest (+13.9pp).
  STUDY — an eligibility ceiling to price into expectations, not a lever.
- **Wikipedia is not a template.** 59.2% citation on general queries at median
  position 24 with the *weakest* query match in the dataset, on mass alone (avg
  4,383 words, 31 lists, 6.6 tables per page). The same dataset puts the length
  optimum at 500–2,000 words. Do not read Wikipedia's profile as permission to
  write longer. STUDY.
- Focused beats exhaustive: pages covering 26–50% of the fan-out sub-topics
  outperform pages covering 100%.
- Length peaks at 500–2,000 words (34.3%); >5,000 words falls to 28.6%.
- Structure is a multiplier, not a source: 4–10 H2–H4 subheads (33.2% vs 28% for
  1–3), JSON-LD +6.5pp.
- Freshness: 30–89 days peaks at 32.8%; <30 days dips to 25.3% (incomplete
  indexing); >2 years 27.5%. The freshness bonus only applies to pages already
  well matched to the query. Decay is vertical-specific — finance is the
  steepest (50.2% → 35.1%, a 15pp drop), so set the refresh cadence per vertical
  rather than sitewide. STUDY.
- **Reading level is contested.** The same 353,799-page analysis peaks citation
  at Flesch–Kincaid grade 16–17 (35.9%), while the one controlled academic GEO
  benchmark (F6) rewards *improving* readability and a 2025 vendor ebook advises
  "simple, accessible language". Two credible sources point opposite ways →
  HYPOTHESIS. Do not rewrite reading level sitewide in either direction; test it
  per template (experiments.md).
- Bimodal reality: 58% of pages are never cited for any query, 25% always are.
  Consistently cited pages sit at median position 2.5; never-cited at 13.0.

Cross-engine reality: only ~2.4% of URLs are cited by ChatGPT, Perplexity and
Google AIO simultaneously. **There is no single AI-visibility metric.**

## F3. Extractability — the part most audits skip

- **Front-load the substance.** Models weight the opening of a document heavily
  and extract content nearer the top; hidden text is demoted. Put the answer, the
  entity name and the key facts in the first ~100 words, in plain declarative
  sentences.
- **One claim per sentence.** Dense multi-claim sentences break entity and
  triple extraction — the system cannot bind entities to actions. Short factual
  sentences extract; marketing adjectives ("innovative", "world-class") read as
  promotional noise.
- **Keep facts in crawlable plain HTML.** ChatGPT's thinking model greps raw HTML
  for `$`/`€` to confirm pricing; when the number sits behind a JS toggle or
  inside an image it gives up and cites an aggregator (G2) instead. A JS pricing
  table does not just rank badly — it hands your own numbers to a comparison
  site.
- **Respect the read budget** (canonical numbers in architecture-and-equity.md): ~5,700 characters
  for the first read, navigation competes with content, source order beats visual
  order, `alt` text is the only thing read from images, and literal term presence
  triggers a second read.
- **Extraction cost is a selection factor.** Bloated HTML, JS-gated content and
  slow responses raise parsing cost, and engines prefer sources that yield data
  with less friction.
- **Non-English pages pay a token tax.** Tokenizers are English-biased; the same
  statement costs materially more tokens in most European languages (Spanish
  ≈63% more) and fewer in Mandarin. Under a fixed read budget that is fewer
  facts per fetch, so filler, boilerplate and repeated brand furniture cost more
  in a non-English market than in an English one. HYPOTHESIS (mechanism
  documented, effect on citation not measured) — audit it by comparing
  read-budget survival between language versions of the same template, not by
  assuming a penalty.
- **Preview controls gate everything.** `nosnippet`, `data-nosnippet`,
  `max-snippet` limits and paywalls decide what an engine may quote — audit them
  before concluding a page "is not cited".

## F4. Per-engine mechanics worth auditing separately

| Engine | Retrieval path | Audit implication |
|---|---|---|
| Google AIO / AI Mode | Google index + fan-out; sanctions synced with classic search | Classic ranking is the prerequisite; a Google penalty removes you from AI surfaces too |
| ChatGPT (search) | Bing partnership + own cache/index. Network-tab forensics (2026-07, FIELD) name the `resultsource` buckets: `serp`; `labrador` (licensed-publisher whitelist — Reuters/WSJ, ~1,080-char snippets you cannot enter by optimizing); `bright` (Bright Data scraper, dominant in shopping/finance/weather); `oxylabs`. A `turnusecase` bucket decides whether the web is consulted at all — some prompts answer from training with an empty network tab | Before diagnosing "not cited", establish which bucket the query even uses: a licensed-publisher or training-only answer is not a page problem. Bing rankings are a first-class path (see the index-dependency conflict below) — but a Bing path is **not** a reason to treat Googlebot as optional: the opposite observation, that an 85% Google traffic loss came with a ~75% ChatGPT loss and that blocking Googlebot cuts ChatGPT proportionally, is equally documented. Never let a plan conclude that blocking Googlebot is AI-neutral (myths.md, technical-checks.md A1) |
| ChatGPT Deep Research | Bing snippets, three commands, no clicks, ~5,700-char read window, `OAI-SearchBot`. Logged across 10+ accounts, ~June 2026 (FIELD): a successful `find` re-opens the page at the matched line in **95%** of sessions, so a literal term guarantees a second read — miss it and the agent tries another keyword and leaves. A robots-blocked page returns `viewing lines [0-0] of 0` and drops out of the report silently | Optimize source order and literal terms; unblock the right user agent (`OAI-SearchBot` ≠ `GPTBot` — unblocking one does nothing for the other). Treat `[0-0] of 0` as the evidence signature for a robots block, not "no interest" |
| Claude | ~86.7% overlap with Brave's organic results; Brave is a listed subprocessor. Field tests (2026-06) show Claude pulling Brave-top pages Google has not indexed yet, and ignoring Bing's top results that sit outside Brave's index | Brave's Web Discovery Project scores **behavior** (query correlation, active time, copy events, scroll, internal-link clicks) and ignores backlinks, social signals, domain age and schema; pages failing its `validDoubleFetch` emit zero signal. The full discard list: no title in **either** fetch; `noindex`; canonical mismatch between the two fetches; authenticated-vs-anonymous HTML length differing by <10% or >90%; a **password field present in the anonymous fetch only**; a **form present in the anonymous fetch only** — the last two are the login-wall signature, and they catch templates that show a sign-in prompt to logged-out visitors. Two mechanics worth auditing: structural data is collected at **5,000ms**, so a slow-rendering template ships a truncated payload; every event needs >1s of active time and is throttled to one increment per second, so click farming does not move it |
| Gemini | Google index + fan-out; distribution (bundled in Android and Chrome) drives share more than model capability. Leaked system prompts (FIELD) show the most aggressive arbitration of the three: check a **User Corrections History before any other source** and silently overwrite conflicting data, including retrieval. A 2026-06 feature connects a Google Business Profile directly — reviews, customer questions and performance data become assistant context | A per-user memory layer you cannot see or audit means Gemini answers are the least reproducible; record the account state with every observation. For local and service businesses, GBP data quality is now an assistant input, not only a Maps input |
| Perplexity | Own crawl + retrieval; leaves ~76% of retrieved pages uncited. Correlates weakly with both Brave and the Google top-10 | Track retrieval separately from citation; a Claude/Brave or Google fix does not transfer here. Localization index is low (~9%) — Italian-language prompts run in Italy unlocked 59 additional local citation slots (FIELD, 2026-06), so localize the *prompt set* before concluding absence |
| Copilot / Bing | Bing index; publishes the most actionable guidance and AI analytics | Use Bing Webmaster AI Performance for citation share, intents and topics |
| Alice AI / Алиса (Yandex) | Yandex index. ~1 in 3 Search queries now gets an Alisa AI answer, up from low single digits in two years, and Yandex reports 48.3M monthly users of the quick answers under the search box (Q1'26 report) and Search volume still growing >5% YoY; ~10% of Alisa AI queries are product-related. Yandex Commerce Protocol places products inside answers with in-chat checkout: 1,600+ merchants applied and 200+ integrating as of 2026-05; restaurant and salon booking inside the chat shipped 2026-06. Ads inside the AI answer are in live experiments and were confirmed as a future buyable format (Forbes interview, 2026-04) | For RU commerce, YCP integration is a distribution decision, not an SEO one. Do not model the surface as organic-only — part of the answer real estate is becoming paid. RU field survey (2026-05): ChatGPT leads on awareness and usage but Alisa AI drives roughly **5×** more clicks to sites, so RU prompt sets that skip it measure the wrong engine |

**Which index does ChatGPT actually depend on — unresolved.** Two field
observations point opposite ways. (a) Sites that lost 85% of their Google
traffic lost 75% of their ChatGPT traffic, and blocking Googlebot cuts ChatGPT
referrals proportionally — read as ChatGPT → Google index → page ranking
signals. (b) A YMYL site invisible in Google (past page 7) collected 90k+
ChatGPT citations purely from Bing, with 88k URLs in Bing's index versus 45k in
Google's — though the content was mass-generated with no authors or contact
details, and the analyst expects the position to collapse once Bing flags the
pattern Google already flagged. Both are FIELD, single-case, and they conflict →
the dependency claim is **HYPOTHESIS**. The only safe residue for a plan: rank
in at least one major engine, and never bet the plan on a single index path.
Test it on this site by comparing crawler logs and AI referrers per engine
(experiments.md, measurement.md).

**Slots you do not control.** Preferred sources now extends from Top stories
into AI Overviews and AI Mode, with a "Highly cited" badge on SERP article links
(2026-05, algorithm-updates.md). A share of the link slots is chosen by the
*user*, so a competitor whose audience has pinned them occupies space no
optimization reaches. When AI-surface visibility moves without a matching
ranking change, check for this before writing a cause.

**Licensing is becoming part of the crawler posture.** Two documented moves sit
on the same axis: ChatGPT's `labrador` bucket serves a licensed-publisher
whitelist you cannot enter by optimizing (above), and in the UK 31 sites added
**"search-only" license terms** — permitting search indexing while pricing
unlicensed AI use at £500/article (reported 2026-07, `FIELD`). For an audit that
means two questions, not one: *which agents are technically allowed* (robots,
WAF, CDN — technical-checks.md A1) and *what the site's own terms say those
agents may do with the content*. State both in the report; a terms change is a
commercial decision for the client, and this skill does not draft or advise on
license language. France's ~450 notified publishers being paid for content used
in AI answers is the same trend on the platform side (algorithm-updates.md).

Personalization is now a factor: Google's Personal Intelligence (Gmail, Photos,
Calendar) measurably shifts AI Mode recommendations. In the controlled test
(iPullRank, 1,922 AI Mode answers, 3 accounts, 30 Mar–15 Apr 2026 — FIELD, small
sample), email-seeded brands went from 23.9% to 66.8% appearance on a connected
account and 4.5% to 24.9% in the top three, while the control moved 21.9% →
18.9%. Email seeding beat Photos (53.6% vs 10.5%), and *invented* brands seeded
by email still surfaced in 35.7% of answers versus 55.8% for real ones. Personal
context gets a brand into the pool; the open web still validates it. So the
honest question is not "what does AI Mode recommend" but "what does it recommend
*to this user, for this prompt, in this category*".

## F5. The prompt set (run it, record verbatim answers)

Per engine you can reach (ChatGPT, Gemini, Perplexity, Claude, Copilot, AI Mode,
Alice AI), fresh session, no memory, and note whether web search was on:

**Entity/confidence block**
1. "What is [brand]?" 2. "Tell me about [brand]." 3. "What does [brand] do?"
4. "What is [brand] known for?" 5. "How does [brand] compare to [competitor]?"

**Commercial block** (the prompts buyers actually use)
6. "best [category] for [segment]" 7. "[category] alternatives to [competitor]"
8. "is [brand] any good / trustworthy?" 9. "[brand] pricing"
10. "[problem statement] — what should I use?"

Score every answer on three axes:

- **Accuracy** — positioning, products, geography, pricing correct, or stale and
  hallucinated?
- **Confidence** — assertive ("is the leading…") or hedged ("some users report
  that it may offer…")?
- **Consistency** — do the engines describe you the same way?

Two scoring traps. **Citation counts are not comparable across funnel stages** —
one strong TOFU explainer routinely collects hundreds of citations while a strong
BOFU page collects two, so compare a page only against pages at the same stage
(FIELD, practitioner consensus 2026-07). And **the prompt pool is unbounded**:
you cannot optimize per prompt variation, so track the head term inside the
prompt and the topical coverage behind it, not a list of phrasings.

Diagnosis: low accuracy → training data stale or mis-linked; hedged confidence →
thin parametric base; inconsistency → fragmented entity signals. A useful
separation test: ask the same question with **web search disabled** — hedged
phrasing indicates the retrieval layer is carrying you; assertive phrasing
indicates the claim is baked into training. Retrieval-level fixes land in days;
training-level changes wait for model releases.

**Prompt-format effects to control for** (1,754 prompts / 37,804 answers):
same-intent prompts return the same brands at the same rate — wording matters far
less than format. Rankings/lists/comparison/table formats surface ~20% more
brands than open questions; keyword-explicit prompts ~25% more; persona framing
fewer. Constraints reduce brand counts in ChatGPT/Perplexity but increase them in
Gemini/AIO. Prompt length and filler words: no effect. Track a 25/50/25
TOFU/MOFU/BOFU split, tag prompts by format so lists are not compared against
open questions, and report per engine. STUDY.

Two guards from the same dataset. **Similarity floor:** 88–92% of human prompt
pairs exceed 0.50 cosine similarity and brand visibility is stable above roughly
0.50–0.60 — below that, ChatGPT starts dropping the brand, and MOFU non-branded
commercial prompts are the band where wording genuinely changes the answer.
Rewriting a prompt inside the stable band and calling the delta a result is
noise. **Similarity is not intent:** "Charleston" and "Charlestown" are ~95%
similar and are different commercial markets, so never merge prompts on cosine
distance alone.

## F6. Experiment results that contradict the vendor pitch

Seven controlled GEO experiments across 100M sites:

- `llms.txt` attracted **0.1%** of AI-bot traffic and performed 3× worse than
  normal pages.
- **Markdown mirrors received 0% AI-crawler visits** vs 4.6% for the HTML
  versions. Do not duplicate pages as `.md`. (A single-site experiment reported
  AIO gains from serving structured Markdown — treat serving Markdown as an
  experiment to measure in your own logs, never as a default recommendation, and
  watch for duplicate-content ambiguity.)
- Schema is an eligibility and entity aid on specific surfaces, not a lever (the
  canonical stance in myths.md). **Two studies, and they contradict each other on
  both Google's AI surfaces and ChatGPT** — name them separately whenever you
  quote either:
  - **Study A — this 100M-site GEO run.** Schema lifted Google AIO visibility
    (reported 1500%) and AI Mode (377%) while *reducing* citations in ChatGPT,
    Gemini and Copilot.
  - **Study B — 10-week controlled LocalBusiness test, 29 domains** (geo-matched
    control and test groups, one-sided Welch t-test, 90% threshold, method
    reviewed before results). **No** ranking or visibility gain in Google, Bing
    or Yahoo, Maps went the wrong way, and AI Mode / AI Overviews / Gemini / Grok
    all landed at coin-flip significance (50–60%) — while **ChatGPT improved**
    (+3.33 recommendation positions at 92.91%, +10pp brand citation at 91.51%).
    Scope limits: one niche (service-area local businesses), one schema type,
    homepage only, no rich snippets; both arms sit under the conventional 95% bar.

  So "schema lifts AIO 1500%" and "schema does nothing in AIO" are both on the
  table, and so are "schema reduces ChatGPT citations" and "schema raises
  ChatGPT recommendation". **Both directions — AIO/AI Mode and ChatGPT — are
  HYPOTHESIS**, and both go to the experiment list (experiments.md), split by
  engine, not into the plan. Quoting Study B's Google/Bing/Yahoo null without its
  positive ChatGPT arm, or Study A's ChatGPT negative without Study B, misreports
  the evidence. Neither result licenses shipping schema volume (myths.md);
  samples and figures live in benchmarks.md.
- Press-release distribution produced citations within days; **YouTube is the #2
  cited social source** (cadence matters more than engagement); localization
  varies wildly by platform (Copilot ~77% localization index, ChatGPT ~58%,
  Perplexity ~9%) — localize *prompts*, not only pages.

The one controlled academic benchmark (Aggarwal et al., KDD 2024 — 10k-query
GEO-bench, 9 optimization methods) is still the only place where content changes
were tested against a held-out query set: gains came from **citing authoritative
sources, quoting named experts, adding statistics and improving readability**;
keyword-style manipulation scored *below* baseline. Read the omissions honestly —
schema, FAQ markup, heading hierarchy and machine-readable formats were never
tested, so "no evidence" there means untested, not disproven. STUDY.

**Penalties cascade into AI surfaces, at directory granularity.** A "Scaled
content abuse" manual action against one directory (850k AI-generated articles)
removed that directory from Google, and its ChatGPT citations collapsed to
roughly zero — with a residual trickle consistent with a Bing fallback — while
the rest of the same domain kept ranking and kept being cited (FIELD, 2026-06).
Two consequences: check for directory-scoped actions before concluding an AI
surface "just stopped citing us", and never plan an AI-visibility push on top of
an unresolved Google sanction.

**What is being sold as GEO and is not on this list.** A documented paid tactic
buys 30–100 listicle placements that manufacture entity consensus — target brand
locked into the first slot, competitors' outbound links and CTAs stripped from
their entries, competitors rotated between placements so the target is the only
stable variable, and Googlebot blocked on those subfolders while AI crawlers get
full access. Google's Gary Illyes publicly compared mention manipulation for
AIO/AI Mode to link buying (Search Central Live Sydney, 2026-05-29). This is
**detection material for threats-and-defense.md** — audit competitors' listicle
footprints and robots asymmetries for it; never recommend it. The same source's
claim that "classic LLM optimization yields 1% uplift" is a sales premise from an
interested party, not measured evidence — ignore it.

Regression across 29,562 domains / 145 verticals / 105k ChatGPT prompts: classic
SEO signals correlate with LLM visibility but explain only **15–20% of the
variance** (SERP impressions ρ=+0.241, position ρ=+0.238, backlinks ρ=+0.204,
each R² ≈ 5–6%). The signal hierarchy flips by vertical — Wikidata dominates
established categories, Reddit dominates community categories, SERP outbound
links matter most in finance/SaaS. Visibility is also **per buyer persona**: the
top airline for a frequent flyer is not the top airline for a student.

Say the corollary out loud in the report: if external signals explain 15–20% of
the variance, then **80–85% of why a model recommends a domain sits in factors no
external dataset observes**. Anyone selling a lever for that majority is
guessing. Plan against the 15–20% you can move, and price the rest as
uncertainty.

## F7. What to put in the plan

Ordered by evidence strength:

1. Fix retrieval eligibility first: indexable, fetchable by the right agents,
   ranking somewhere (Google **or** Bing), preview controls open.
2. Make the answer extractable: front-loaded, one claim per sentence, plain-HTML
   facts, 4–10 subheads, literal target terms present, alt text carrying facts,
   navigation out of the way in source order.
3. Match the prompt, not the keyword: headings that mirror the question, focused
   scope over exhaustive guides, freshness where the vertical demands it.
4. Earn third-party corroboration (see entity-and-brand.md) — that is what turns
   a citation into a recommendation.
5. Measure per engine, per persona, with the prompt set and inbound logs (see
   measurement.md). Never buy a single "AI visibility score" as truth.

Two guardrails on the ordering:

- **Never trade classic rankings for AI traffic.** Every documented recovery from
  a self-inflicted ranking loss runs 2–3 years, and the AI surfaces inherit the
  loss anyway (F4, F6). If a proposed GEO change risks Google or Yandex
  visibility, it is an experiment with a control, not a rollout.
- **Fix at the layer that can move.** Retrieval-layer changes (indexability,
  extractability, corroborated sources) land in days to weeks. Training-layer
  changes wait for model releases and take years to influence, so nothing in the
  plan should promise them. Say which layer each recommendation targets.
