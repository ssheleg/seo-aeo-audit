# The play list — what to put in the plan, ranked

Each play: the trigger that justifies it, the change, the mechanism, the observed
effect, the evidence tier, and how to verify. Only recommend a play when its
trigger is present in **this** audit. Nothing here relies on deception; the
adversarial material lives in threats-and-defense.md as defense only.

Tiers: `CONFIRMED` (documented by the engine or reproduced here) · `STUDY`
(published multi-site data) · `FIELD` (single-case report) · `HYPOTHESIS`.

## Blockers — do these before anything else

| # | Trigger | Play | Mechanism | Observed | Tier |
|---|---|---|---|---|---|
| B1 | Manual action present | Fix every cited cause, document, then one reconsideration request | The action is a binary multiplier on ranking | Recovery within 24h–weeks once accepted | CONFIRMED |
| B2 | `noindex` in pre-render source, or `meta refresh` + `noindex` | Replace with a server-side 301; strip the directive | `noindex` is a directive and wins over canonical; it counts if present in either source or DOM | Page returns to index within a crawl cycle | CONFIRMED |
| B3 | Rendering resources blocked (`/_next`, `/assets`, CSS/JS) | Allow the render-critical paths | Blocked resources are never downloaded, so never rendered | Reindexing and partial traffic recovery within weeks | FIELD |
| B4 | Canonical carries `media`/`type`/`hreflang`/`lang` | Emit `rel` + `href` only | Extra attributes make Google discard the declaration | URL Inspection shows the user-declared canonical accepted | CONFIRMED |
| B5 | Broad `robots.txt` wildcard (`/*?`, `/*print`) | Replace with parameter-specific rules; canonicalize filtered variants | Wildcards match substrings, not paths | One store recovered ~40% of product pages; a retailer's 45% traffic loss traced to one line | FIELD |
| B6 | Soft 404s at scale / auto-generated empty pages | Return real 404/410, remove or noindex the generators, tighten parameters | Soft 404s degrade host quality and make Google abandon crawling | −83% soft 404s; crawl requests and Discover share recovered first | FIELD |
| B7 | Hijacked or dangling subdomain | Reclaim DNS, verify every property variant in GSC, monitor both www/non-www | Abandoned CNAMEs get claimed and redirected | Full recovery in 36h in the documented case | FIELD |

## Leaks — stop the bleeding

| # | Trigger | Play | Mechanism | Observed | Tier |
|---|---|---|---|---|---|
| L1 | Crawl budget on filters/params (log evidence) | Facet/filter split, parameter rules, canonical to base, cap pagination | Budget follows structure and quality signals | Product crawl rate ×4; new products indexed in 2 days vs 3 weeks | FIELD |
| L2 | Large index with low-value pages | Index tiering (must/should/block/hard-block) by business, search and user value | Fewer, better pages concentrate budget and quality | Valuable indexed URLs +308%, zero-traffic pages −87%, organic +67% in 90 days | FIELD |
| L3 | Homepage hoards equity, money pages starve | Link products/services from the homepage; comparison and solution hubs; contextual links from traffic pages | Equity flows by count, position, relevance and source authority | Product pages +12 positions average, +$340K organic revenue in 90 days | FIELD |
| L4 | Same query on multiple URLs, >70% SERP overlap | Merge: content to the winner, 301 the losers, update internal links | Rotational testing splits clicks between candidates | Combined clicks rise once one source is established | STUDY |
| L5 | 60+ links before the content in source order | Trim sitewide navigation to top categories; subcategories on their own pages; add an HTML sitemap | Read budget ~5,700 chars; each link consumes it | ~90% link cut improved rankings in Google **and** ChatGPT | FIELD |
| L6 | Equity into tag archives, calendars, author bios, internal search | Noindex/nofollow/remove those receivers; redirect where they have value | Dilution across low-value receivers | Standard technical-audit finding | STUDY |
| L7 | Orphans (crawl ∖ sitemap diff) | Link them from relevant hubs or retire them deliberately | PageRank decays ~85% per hop; zero-click pages get deprioritized | Deep pages need ≥1 click/week to hold their index slot | FIELD |
| L8 | Bulk 301s pointing at the homepage | Redirect each URL to the closest-intent live page; parent category as fallback | 301 passes ranking only on close intent match | Prevents the sitewide dip that follows mass removal | STUDY |

## Gains — earn more visibility

| # | Trigger | Play | Mechanism | Observed | Tier |
|---|---|---|---|---|---|
| G1 | Page type mismatches the SERP | Rebuild to the dominant format; interlink commercial → transactional | Intent match drives satisfaction signals | Positions 12–20 → 3–7, bounce 78% → 34%, CVR 0.4% → 3.2% | FIELD |
| G2 | Thin information gain (few unique numbers) | Add original measurements/analytics; answer the questions the top-3 skip | Consensus is free; only single-source data adds value | 15+ unique data points ≈ 62/100 vs 40/100 | STUDY |
| G3 | No task completion on-site | Add the calculator/comparison/tool that finishes the job | Task completion correlates ρ=0.381 with growth; four features → 68% win rate | Multi-site core-update analysis | STUDY |
| G4 | Answer buried, multi-claim sentences, JS-gated facts | Front-load the answer, one claim per sentence, facts in plain HTML, 4–10 subheads, factual `alt` text | Lead bias, entity/triple extraction, raw-HTML parsing | Title–query match +19pp citation probability; JSON-LD +6.5pp | STUDY |
| G5 | Brand described differently across profiles | Normalize 8–12 third-party profiles to the homepage reference; re-check quarterly | Conflicting category signals blur the brand centroid | Prerequisite for consistent AI answers | STUDY |
| G6 | Cited but not recommended (ghost citations) | Brand as grammatical subject of insights; entity graph (`sameAs`, Wikidata, author markup); third-party mentions in recommendation context | Models select names from memory, then retrieve support | Named brands cited 53.1% vs 10.6% unnamed | STUDY |
| G7 | Stale relative to the SERP age percentile | Substantial update: new sections, new data, restructure to intent — never a date bump | Freshness is scored against the result pool | Title/section/link changes count; `lastmod` does not | CONFIRMED |
| G8 | Slow or heavy money pages | LCP triage order (TTFB → clear the path → `fetchpriority` → defer JS), native `<dialog>` for modals | CWV plus satisfaction signals | 4.2s → 1.3s: bounce 67%→41%, CVR +93%, +8 positions in 6 weeks | FIELD |
| G9 | Weak reviews/sentiment in the sources models cite | Fix the product complaints models repeat; refresh the stale cited pages; report coordinated attacks | Reviews feed the model's verdict once "review" enters the fan-out | Mediocre ratings are the worst position — they give the model nothing to say | STUDY |
| G10 | Ranking in Google only, invisible in Bing | Fix Bing-side indexation and rankings deliberately | ChatGPT grounds heavily on Bing | A site past page 7 in Google earned 90k+ ChatGPT citations via Bing | FIELD |
| G11 | Long-form asset with no distribution | Atomize into ~60 platform-native pieces, each linking back, released over weeks | Distribution doubles as equity and independent entry points | Reported ~14× reach at zero content cost | FIELD |
| G12 | Local/service business with generic targeting | Neighborhood, landmark, urgency and "near me + qualifier" keyword layers built from Maps, PAA, autocomplete, GBP insights, support tickets | Specific intent beats broad location terms | Aggregate 1,840/mo at low competition, positions 2–5, 3× conversion vs the head term | FIELD |
| G13 | Programmatic pages planned | Three layers: template, data, **differentiation** (city-specific context generated from data fields, rotated structures); pre-publish gate (no empty variables, ≥800 words, valid schema, internal links, no near-duplicates); stagger publishing | Thin duplication triggers filters; specificity plus locality survives | 387 of 500 pages in the top-10 in 6 months in the cited case — with a closing window and rising risk | FIELD |
| G14 | PDFs ignored (manuals, datasheets, specs) | Bulk-compress and rewrite titles/metadata from extracted text | PDFs rank and are extractable | Measurable click lift per file | FIELD |
| G16 | Traffic concentrated in one channel; publisher or lead-gen model exposed to zero-click | Build an **owned** surface (email list, community, Discord/Slack, Substack) and move engaged people onto it from rented platforms | Owned audiences are immune to SERP composition and platform algorithm changes; rented ones can vanish overnight | The one asset the 2026 practitioner panel agrees compounds; publishers with direct audiences kept revenue while click volume fell | STUDY |
| G17 | Buyers research the category on UGC platforms where the brand is absent | Presence on the platforms this audience actually uses (Reddit, YouTube, TikTok, Quora, Substack): study the conversations first, then contribute where engagement already exists | Those spaces are read by buyers **and** by models forming the category verdict; a Reddit comment was quoted by ChatGPT within 1h45m in one case | Reddit ≈40% of LLM citations; review/UGC sources drive the sentiment verdict | STUDY |
| G18 | One content format only | Diversify formats for the same niche — newsletter, video, podcast, first-hand testing — rather than more articles | Depth for a niche audience beats breadth; video and recorded opinion are the formats AI cannot replicate | Panel consensus 2026; survivors of the four-year blog collapse clustered on first-hand formats | STUDY |
| G15 | Agentic surfaces unaddressed | Expose WebMCP tools (`/mcp/` page listing them, footer link; `llms.txt` may point at that page — as agent plumbing only, never sold as a ranking or citation lever, see myths.md) | Agents call structured tools instead of guessing from screenshots | Early-mover positioning; no ranking or citation claim | HYPOTHESIS |

## Editorial and process plays

| # | Trigger | Play | Observed | Tier |
|---|---|---|---|---|
| P1 | Content ships slowly and inconsistently | Role split (strategist / writer / SME 48h comment-only review / editor / SEO / publisher), standard brief, async review, automated pre-publish QA gate (keyword in H1 and first paragraph, meta ≤160 chars, ≥3 internal links, images ≤100KB, readability floor, CTA present) | 4 → 40 posts/month at constant headcount, 8-day cycle | FIELD |
| P2 | AI-assisted writing | Human-edited AI (not pure generation); source-grounded prompting; inline citation required for every external claim; automated fact-check pass; hallucinated-URL sweep | AI-assisted beat pure generation ~5× across Google, ChatGPT, AIO, Gemini; statistics hallucinate ~40% of the time unsupervised | STUDY |
| P3 | New site or new topic | Narrow niche → 50–100 subtopics → hub + 10–15 clusters → 3–5 internal links from indexed pages to every new article → front-loaded publishing cadence | 47 top rankings and 0 → 12k organic/month in 6 months | FIELD |
| P5 | An update rolled out, or a decline needs attribution | Run the update-response protocol from algorithm-updates.md: exact dates → before/after export by page, query, country, device → segment by template and intent → competitor set for the same window → classify winner/loser/unchanged → only then hypothesize | Rollout ≠ effect window; spam and core recovery paths differ; GSC outages cluster on rollouts | Prevents the most expensive audit error — a confident plan built on a misattributed cause | CONFIRMED |
| P4 | Link acquisition needed | Mine competitors' weakest donors, community placements, guest-author trails, podcasts (500–5k listeners), newsjacking, academic resource pages; relevance over DR; natural, event-driven velocity | 38% outreach success, 29 links at avg DR 35 in one campaign | FIELD |

## Rules that override the table

- A play whose trigger is absent is noise — leave it out of the report.
- Never ship a FIELD or HYPOTHESIS play sitewide; run it as an experiment
  (experiments.md).
- Every play in the plan needs a verification step and an honest horizon
  (measurement.md, §J5).
- If a play conflicts with the myth list (myths.md), the myth list wins.
