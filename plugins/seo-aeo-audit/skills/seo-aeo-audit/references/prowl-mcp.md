# Prowl MCP — bulk market data without a per-vendor login

One MCP endpoint (`https://prowl.chat/mcp`) fronts ~408 provider tools —
DataForSEO, Majestic, SpyFu, SearchAPI/SerpApi across 60+ engines, Firecrawl,
Exa, Perplexity — on a prepaid USD wallet billed per call. For an audit it
solves one specific problem: **getting competitive and demand data in bulk when
you have no seat on Ahrefs or Semrush**, and getting it in a shape an agent can
actually work with.

It does **not** solve the ground-truth problem. Read the ladder placement below
before you let anything from here into a `CONFIRMED` finding.

> Disclosure: Prowl is a commercial product. It is listed here as one option at
> rung 5, subject to the same "estimates, never ground truth" rule as every
> other third-party index in [tooling.md](tooling.md). Nothing in this skill
> requires it.

## Where it sits on the ladder

**Rung 5 — third-party indices.** Same rung as Ahrefs and Semrush, same
evidence cap: a Prowl figure cannot rise above `STUDY`. It never replaces
rungs 1–2 (server logs, Search Console).

One exception worth knowing: Prowl carries **two independent backlink indexes**
(DataForSEO and Majestic) and two independent volume datasets (DataForSEO Labs
Google volume and clickstream panel volume). Where both agree, confidence rises
materially — but the tier does not. Two third-party indexes agreeing is a
stronger `STUDY`, not a `CONFIRMED`.

Concretely: a domain that ranks for one keyword and holds 16 backlinks can be
established from Prowl alone. Whether Google *chose* a given canonical, or why a
page is "crawled – not indexed", cannot.

## When to reach for it

| Situation | Why Prowl helps |
|---|---|
| No Ahrefs/Semrush seat, or the API tier blocks the endpoint you need | One wallet, no per-vendor contract; you pay per call, typically $0.02–0.08 |
| You need to size 10–20 competitors at once | `dataforseo_bl_bulk_backlinks` takes up to 1000 targets in **one** call |
| You need to check whether a phrase has demand at all | Two independent volume datasets; disagreement is itself a finding |
| The audit is agent-driven | Every response carries a `billing` object, so cost is auditable per finding |
| You need SERP snapshots across engines/locales | SearchAPI's 60+ engines behind the same endpoint |
| AEO/GEO track needs AI-surface data at scale | `dataforseo_ai_llm_mentions` + per-engine response tools (see below) |

**When NOT to.** If you have Search Console, use Search Console. If you have
server logs, use server logs. Prowl is what you use for the market outside your
own property, and for demand validation — not for what Google did to your site.

## Discovery — start here, it is free

| Tool | Use |
|---|---|
| `prowl_search_tools` | Semantic search across all 408 tools. Ask in plain language: "anchor text distribution of backlinks for a domain". |
| `prowl_tool_info` | Exact input schema plus a `cost_hint` before you spend anything. |
| `prowl_get_stats` | Session token/cost totals. |

Both discovery tools are free. Use `prowl_tool_info` before every unfamiliar
call — it is cheaper than a malformed one, and it gives you the parameter names
the provider actually accepts.

## The tools that carry an audit

Grouped by which track they serve. Costs are real figures from a full
prowl.chat audit run on 2026-07-29 (whole run: **$0.50**).

### Baseline — what does this domain actually rank for

| Tool | Returns | Observed cost |
|---|---|---|
| `dataforseo_labs_ranked_keywords` | Every keyword a domain ranks for, with position, Google search volume, KD, traffic estimate, and the SERP snapshot Google served | $0.036 |
| `spyfu_get_most_valuable_keywords` | Organic keywords by SEO clicks — a second opinion on the same question | — |
| `spyfu_get_top_pages` | Top pages by organic traffic | — |

`ranked_keywords` also returns `backlinks_info` per ranking URL and the stored
SERP title/description, which is how you catch a **stale snapshot** — Google
still serving an old title months after a repositioning.

### Track D/E — demand validation, before anyone writes a page

| Tool | Returns | Observed cost |
|---|---|---|
| `dataforseo_labs_keyword_overview` | Google volume + **keyword difficulty** + CPC + search intent, for a keyword list | $0.039 / 13 keywords |
| `dataforseo_kw_clickstream_bulk_volume` | Clickstream-panel volume for up to 1000 keywords | $0.049 / 35 keywords |
| `dataforseo_labs_keyword_ideas` / `related_keywords` | Expansion from seeds | — |
| `dataforseo_kw_dataforseo_trends_*` | Trend and seasonality | — |

**Run both volume tools and compare.** This is the single highest-value habit
in this file. On the 2026-07-29 run, four programmatic pages were found to
target phrases the clickstream panel measured at **zero**; the Labs Google index
then returned **no keyword record at all** for the same six phrases. Two
independent datasets agreeing turned "these pages have an intent mismatch" into
"these pages target queries that do not exist" — a different fix entirely.

The same lookup surfaced what the panel had hidden: low-difficulty terms with
real volume and $9–16 CPCs, which is where the pages should have pointed.

### Track G + link work — competitive and backlink context

| Tool | Returns | Observed cost |
|---|---|---|
| `dataforseo_bl_bulk_backlinks` | Total backlinks for up to **1000 domains in one call** — the cheapest way to size a whole competitive set | $0.074 / 16 domains |
| `dataforseo_bl_anchors` | Anchor-text distribution with `referring_domains` **and `backlinks_spam_score` per anchor** | $0.075 |
| `dataforseo_bl_domain_pages` | Which pages on a domain attract the links (`page_summary.referring_domains`) | $0.074 |
| `dataforseo_bl_referring_domains` | Unique linking domains | — |
| `majestic_get_anchor_text` | The same question against a **second, independent index** | — |
| `majestic_get_top_pages` | TrustFlow/CitationFlow per URL; the only guaranteed "is this URL in the index" check | — |
| `majestic_get_ref_domains` | Referring domains, Majestic-side | — |

**Always read `backlinks_spam_score` before drawing conclusions from an anchor
profile.** On the 2026-07-29 run, the top anchors by referring domains for two
competitors were Telegram PBN spam at spam scores 60–89 — links pointed *at*
them, not built by them. Sorting by referring domains without filtering spam
would have produced an anchor strategy copied from someone else's negative-SEO
problem.

### Track F/AEO — AI-surface visibility at scale

This is where Prowl adds something the rest of [tooling.md](tooling.md) can only
do by hand, one prompt at a time:

| Tool | Returns |
|---|---|
| `dataforseo_ai_llm_mentions` | Brand/entity mentions across ChatGPT, Claude, Gemini and Perplexity |
| `dataforseo_ai_llm_mentions_aggregated` / `cross_aggregated` | Mention share over time and across engines |
| `dataforseo_ai_llm_mentions_top_domains` | Which domains AI cites most for a topic — the AEO equivalent of a SERP competitor set |
| `dataforseo_ai_llm_mentions_top_pages` | Which pages get cited |
| `ai_chatgpt_responses` / `ai_claude_responses` / `ai_gemini_responses` / `ai_perplexity_responses` | Raw answers per engine for a prompt set |

Use these to run the prompt set from [aeo-geo.md](aeo-geo.md) at volume instead
of by hand. The caveat from [measurement.md](measurement.md) J3 still stands:
these are sampled observations of a non-deterministic surface. Record the date
and the engine with every one, and never present a mention share as a rank.

### Tracks A/C/H — the site itself

| Tool | Returns |
|---|---|
| `seo_growth_audit` | Proprietary on-page + AI-readiness audit: semantic chunking, TL;DR extraction, AI content signals, hreflang, cannibalization |
| `seo_growth_check_technical` | Technical pass; **feed it real `sitemap_xml`**, or it reports "no sitemap" |
| `firecrawl_scrape_page_html` | Raw HTML for parity work |
| `firecrawl_map_domain` | URL discovery — does **not** replace a raw sitemap fetch |
| `dataforseo_op_*` (on-page family) | Crawl-style page data |

### SERP observation

| Tool | Returns |
|---|---|
| `google_rank_tracking` | Up to 100 organic results with position — for the market/device/date record every SERP observation needs |
| `google_search_light` | Fast organic results + related searches |
| SearchAPI's other 60+ engines | Bing, YouTube, Maps, app stores, Scholar, Patents |

## Operating notes — learned the hard way

- **`prowl_call_tool` nests its arguments.** The call takes `tool_name` and a
  `params` **object**; the underlying tool's arguments go inside `params`, not
  flat alongside `tool_name`. Getting this wrong returns
  `Missing required parameter(s): …`.
- **Failed calls are not billed.** The response carries `"debited": false`. Probe
  freely; a malformed call costs nothing.
- **Read the `billing` object.** Every response returns `estimated_cost_usd`,
  `actual_cost_usd`, `provider_cost_usd` and `debited`. Quote the real total in
  the audit — a reader who can see the spend can judge the depth.
- **Responses are large.** A 25-row anchor pull is ~50 KB of JSON; 15 domain
  pages ~70 KB. Route them to a file and parse with `jq`/Python rather than
  reading them into context. Ask for the smallest `limit` that answers the
  question.
- **Not every endpoint takes `order_by`.** `dataforseo_bl_domain_pages` rejects
  it (`40501: Invalid Field`). Check `prowl_tool_info` first, or sort client-side.
- **Nested payloads.** Backlink page data hides under `page_summary`, not at the
  item root. Probe the schema of the first item before writing a parser.
- **Set a stable `session_id`** across the audit so cost accounting and the
  circuit breaker stay scoped to one run.

## Cost discipline

A full competitive and demand pass for one domain — own rankings, 16 competitors
sized, three anchor profiles, one link-magnet pull, 35 keywords of clickstream
volume and a 13-keyword Google cross-check — cost **$0.50** on 2026-07-29.

Budget accordingly: this is a rounding error against an audit's value, so the
constraint is context window, not money. Pull what you will actually use, and
say in the report what you spent.
