# Track F — answer engines: retrieval, extraction, citation

AEO and GEO describe the same work: being retrievable, readable and quotable by
systems that answer instead of linking. Google's own position is that this is
still SEO; treat that as one interested party's opinion and verify per engine.

## F1. How the answer actually gets built

1. **Query fan-out.** One user query expands into several parallel queries
   (AI Overviews) or 5–20 internal sub-queries (agentic RAG: planning, tool use,
   multi-step iteration, reflection).
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
   obviously SEO-shaped content in favour of original publishers.

Implication: align with the consensus the model already holds, corroborate it
across several retrievable quality sources, and state claims declaratively.

## F2. What correlates with being cited (ranked evidence)

Meta-analysis of 54 published studies, factor weight out of 10:

| Factor | Weight |
|---|---|
| URL accessibility (can it be fetched at grounding time) | 9.5 |
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
  Wikipedia (DA 95) 59.2%. Pages are judged, not domains.
- Exact query–title match adds ~+19pp even after controlling for rank; strong
  H1–H4 match to the prompt: 41% cited vs 29% for weak matches.
- Focused beats exhaustive: pages covering 26–50% of the fan-out sub-topics
  outperform pages covering 100%.
- Length peaks at 500–2,000 words (34.3%); >5,000 words falls to 28.6%.
- Structure is a multiplier, not a source: 4–10 H2–H4 subheads (33.2% vs 28% for
  1–3), JSON-LD +6.5pp.
- Freshness: 30–89 days peaks at 32.8%; <30 days dips to 25.3% (incomplete
  indexing); >2 years 27.5%. The freshness bonus only applies to pages already
  well matched to the query.
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
- **Respect the read budget** (see architecture-and-equity.md): ~5,700 characters
  for the first read, navigation competes with content, source order beats visual
  order, `alt` text is the only thing read from images, and literal term presence
  triggers a second read.
- **Extraction cost is a selection factor.** Bloated HTML, JS-gated content and
  slow responses raise parsing cost, and engines prefer sources that yield data
  with less friction.
- **Preview controls gate everything.** `nosnippet`, `data-nosnippet`,
  `max-snippet` limits and paywalls decide what an engine may quote — audit them
  before concluding a page "is not cited".

## F4. Per-engine mechanics worth auditing separately

| Engine | Retrieval path | Audit implication |
|---|---|---|
| Google AIO / AI Mode | Google index + fan-out; sanctions synced with classic search | Classic ranking is the prerequisite; a Google penalty removes you from AI surfaces too |
| ChatGPT (search) | Bing partnership + own cache/index; `resultsource` values observed: `serp`, licensed publisher whitelist, third-party scrapers | Bing rankings are a first-class path: a site invisible in Google (past page 7) earned 90k+ ChatGPT citations purely from Bing |
| ChatGPT Deep Research | Bing snippets, three commands, no clicks, ~5,700-char read window, `OAI-SearchBot` | Optimise source order and literal terms; unblock the right user agent |
| Claude | ~86.7% overlap with Brave's organic results; Brave is a listed subprocessor | Brave's Web Discovery Project scores **behaviour** (query correlation, active time, copy events, scroll, internal-link clicks) and ignores backlinks, social signals, domain age and schema; pages failing its `validDoubleFetch` (missing title, noindex, canonical mismatch, big authenticated/anonymous HTML delta) emit zero signal |
| Perplexity | Own crawl + retrieval; leaves ~76% of retrieved pages uncited | Track retrieval separately from citation; localisation index is low (~9%) |
| Copilot / Bing | Bing index; publishes the most actionable guidance and AI analytics | Use Bing Webmaster AI Performance for citation share, intents and topics |
| Алиса AI (Yandex) | Yandex index; ~1 in 3 queries answered; ~10% product-related; Yandex Commerce Protocol places products inside answers with in-chat checkout | For RU commerce, YCP integration is a distribution decision, not an SEO one |

Personalisation is now a factor: Google's Personal Intelligence (Gmail, Photos,
Calendar) measurably shifts AI Mode recommendations — in a controlled test,
email-seeded brands went from 23.9% to 66.8% appearance on a connected account
(control unchanged). Personal context gets a brand into the pool; the open web
still validates it. So the honest question is not "what does AI Mode recommend"
but "what does it recommend *to this user, for this prompt, in this category*".

## F5. The prompt set (run it, record verbatim answers)

Per engine you can reach (ChatGPT, Gemini, Perplexity, Claude, Copilot, AI Mode,
Алиса AI), fresh session, no memory, and note whether web search was on:

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
open questions, and report per engine.

## F6. Experiment results that contradict the vendor pitch

Seven controlled GEO experiments across 100M sites:

- `llms.txt` attracted **0.1%** of AI-bot traffic and performed 3× worse than
  normal pages.
- **Markdown mirrors received 0% AI-crawler visits** vs 4.6% for the HTML
  versions. Do not duplicate pages as `.md`. (A single-site experiment reported
  AIO gains from serving structured Markdown — treat serving Markdown as an
  experiment to measure in your own logs, never as a default recommendation, and
  watch for duplicate-content ambiguity.)
- Schema lifted Google AIO visibility (reported 1500%) and AI Mode (377%) but
  *reduced* citations in ChatGPT, Gemini and Copilot. A 10-week controlled test
  of LocalBusiness schema on 29 domains found **no** ranking or visibility gain in
  Google, Bing or Yahoo (and Maps went the wrong way), while ChatGPT improved
  significantly (+3.33 recommendation positions, +10pp brand citation). Schema is
  a retrieval/entity aid on some surfaces, not a ranking lever.
- Press-release distribution produced citations within days; **YouTube is the #2
  cited social source** (cadence matters more than engagement); localisation
  varies wildly by platform (Copilot ~77% localisation index, ChatGPT ~58%,
  Perplexity ~9%) — localise *prompts*, not only pages.

Regression across 29,562 domains / 145 verticals / 105k ChatGPT prompts: classic
SEO signals correlate with LLM visibility but explain only **15–20% of the
variance** (SERP impressions ρ=+0.241, position ρ=+0.238, backlinks ρ=+0.204,
each R² ≈ 5–6%). The signal hierarchy flips by vertical — Wikidata dominates
established categories, Reddit dominates community categories, SERP outbound
links matter most in finance/SaaS. Visibility is also **per buyer persona**: the
top airline for a frequent flyer is not the top airline for a student.

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
