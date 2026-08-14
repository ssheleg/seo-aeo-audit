# privateclawd.com — every orank line item, reproduced by hand

- **Date:** 2026-08-14
- **Site:** `privateclawd.com` (Next.js on DigitalOcean behind Cloudflare), plus
  `docs.privateclawd.com` (Mintlify) and `api.privateclawd.com` (does not resolve).
- **Trigger:** an ora.ai / "orank" agent-readiness scan graded the domain
  **64/100 (C)** — Discovery 5/17, Access 52/63, Usability 57/85, Payments 0/0 —
  and returned **53 line items**.
- **Why this document exists:** the operator asked for the report to be validated
  rather than executed. This is the second orank scan this skill has reproduced
  ([2026-08-14-agent-readiness-gap.md](2026-08-14-agent-readiness-gap.md) is the
  first, on a different site), and the second time the exercise found defects in
  three places at once: the site, the grader, and this skill.
- **What shipped from it:** v0.19.0 — the crawler taxonomy corrected against
  vendor documentation, four new `agent_surface.py` checks, one `page_audit.py`
  false positive removed, myth row 33, and K2a/K3a/K4a/K7 rewritten.

## Contents

- [Status, in three lines](#status-in-three-lines)
- [1. Baseline, with dates](#1-baseline-with-dates)
- [2. The grader's arithmetic does not close](#2-the-graders-arithmetic-does-not-close)
- [3. All 53 line items, with verdicts](#3-all-53-line-items-with-verdicts)
- [4. What the grader structurally could not see](#4-what-the-grader-structurally-could-not-see)
- [5. Findings, triaged](#5-findings-triaged)
- [6. The change plan](#6-the-change-plan)
- [7. What this cost the skill](#7-what-this-cost-the-skill)
- [8. What could not be checked](#8-what-could-not-be-checked)

## Status, in three lines

- **Available:** production HTTP (all probes below), `robots.txt`, `sitemap.xml`,
  the codebase, Google Search Console for `sc-domain:privateclawd.com` (siteOwner;
  reached after enabling `searchconsole.googleapis.com` on the `sasai-agents`
  project — `preflight.py` had correctly classified the failure as
  `quota-project`), Google SERP via SearchAPI, and the vendor documentation for
  three crawler families.
- **Missing:** PageSpeed Insights (HTTP 429, daily quota — no field CWV), server
  logs (so **no measurement of agent traffic at all**, which caps every track-K
  effect claim at `HYPOTHESIS` — agent-readiness.md K1), Bing/Yandex webmaster,
  and any answer-engine citation baseline.
- **Scope:** whole site, tracks A/B/D/F/G/K, driven by the orank report; every
  item reproduced against production before being accepted or refused.

## 1. Baseline, with dates

Search Console, `sc-domain:privateclawd.com`, window 2026-05-14 → 2026-08-12
(history from 2025-04-19):

| Metric | Value |
|---|---|
| Queries at position ≤ 20 | 38 · 435 impressions · **1 click** |
| Queries at position 21–30 | 9 · 118 impressions · 0 clicks |
| Queries beyond position 30 | 89 · 728 impressions · 0 clicks |
| Branded | 3 queries · 187 impressions · 1 click |
| Non-branded | 133 queries · **1,094 impressions · 0 clicks** |
| Monthly clicks, Mar→Aug 2026 | 32 · 11 · 12 · 16 · 12 · 2 (Aug partial) |
| Monthly impressions | 585 · 842 · 830 · 1,409 · 796 · 461 |

**This is a cold start, not a decline** — the distinction decides the whole plan.
Every click the property has ever earned in this window is branded; 1,094
non-branded impressions produced zero. The largest single non-branded query,
`openclaw hosting` (241 impressions), sits at **position 49.2**. Nothing here is
losing ground; nothing has arrived yet.

Two canonicalization observations come free with that pull and belong to track B:

- `privateclawd` is served by **13 competing URLs**, including
  `https://privateclawd.com/?utm_source=earlyhunt&utm_medium=re` — a
  UTM-parameterized URL in the index.
- `privateclawd company` is served by **9 URLs**, four of them fragments of the
  homepage (`/#capabilities`, `/#how-it-works`, `/#showcase`, `/#team`).

Google's own autocorrect is a third, and it is a track-G reading: the query
`privateclawd api docs` returns `Did you mean: private cloud api docs`. The brand
string is not yet an entity Google is confident about.

## 2. The grader's arithmetic does not close

Before any finding: the report's own numbers do not reconcile, and this is
checkable from the report alone, without touching the site.

| Layer | Reported | Sum of the "lost N of M" figures in the same report |
|---|---|---|
| Discovery | 5/17 → 12 lost | **18 lost**, over a 17-point layer |
| Access | 52/63 → 11 lost | **31 lost** |
| Usability | 57/85 → 28 lost | **50 lost** |
| Total | 64/100 | layer subtotals sum to 114/165 = **69%** |

Discovery reports losing more points than the layer contains. The three layer
subtotals produce 69%, not the headline 64. A weighting scheme could explain some
of this, and the report publishes none. **Treat the number as noise** — which is
myths.md row 33 and agent-readiness.md K7, now written with this scan as the
second exhibit.

## 3. All 53 line items, with verdicts

Verdicts: **REPRODUCED** — checked against production and true · **REFUTED** —
checked and false · **PARTLY** — the consequence is right and the observable is
wrong · **N/A** — describes a surface this product does not have, so it is a
business decision, not a defect · **AGREED-DECISION** — true, and the site chose
it.

### Discovery (7 items)

| # | Grader check | Verdict | Evidence |
|---|---|---|---|
| D1 | Developer resources not discoverable by name | **PARTLY** | `privateclawd api docs` (SearchAPI, gl=us, 2026-08-14) returns `privateclawd.com` at **#1** and `docs.privateclawd.com` at **#4**. What is true is the rest of the page: positions 2, 3, 5–10 are generic OpenClaw docs and competitors. The docs *are* discoverable; the product has no API to document (see U-block) |
| D2 | No Wikipedia / Wikidata entity | **REPRODUCED** | Correct, and correctly ranked as high-impact by the grader — `entity-and-brand.md` sizes it. Notability comes first; this is not an engineering ticket |
| D3 | No `/.well-known/ai-catalog.json` | **REPRODUCED** | 404 |
| D4 | Not in the ChatGPT app directory | **N/A** | Needs a submission and an app to submit |
| D5 | No npm / PyPI SDK | **N/A** | No public API exists to wrap |
| D6 | No Agent Plugins `plugin.json` | **N/A** | Needs a public repository |
| D7 | Not on skills.sh | **N/A** | Same |

### Access (22 items)

| # | Grader check | Verdict | Evidence |
|---|---|---|---|
| A1 | No agent instruction / "when to use" file | **PARTLY — and this is the finding of the layer** | There is no `/llms.txt` (404). There **is** `/llm.txt` → HTTP 200, `text/plain`, 3,496 bytes, and `/llm-full.txt` → 200, 13,682 bytes. Written, maintained, linked from the footer (`src/components/footer.tsx:297`) and explicitly allowed in `src/middleware.ts:180` — at a filename one character off the convention every client probes. "Absent" is the wrong finding; the fix is a rename |
| A2 | No `/.well-known/agent-skills/index.json` | **REPRODUCED** | 404 |
| A3 | No `/.well-known/agent-card.json` | **REPRODUCED** | 404 |
| A4 | No `pricing.md` | **REPRODUCED** | 404 |
| A5 | `?mode=agent` returns the homepage | **REPRODUCED / out of scope** | True. No specification exists; K7 C1 keeps it out |
| A6 | No `/index.md` markdown fallback | **REPRODUCED** | 404 |
| A7 | skills.sh skill quality | **N/A** | Nothing published to grade |
| A8 | No `/.well-known/api-catalog` (RFC 9727) | **REPRODUCED** | 404 |
| A9 | "18,682 chars with H1 but flat heading structure" | **PARTLY — the second half is false** | Homepage server-renders **20,256 characters** of visible text with **one H1** and **37 H2–H4 subheads** (`page_audit.py`, 2026-08-14). "Flat" is not a description of 37 subheads |
| A10 | No `schemamap:` in robots.txt | **REPRODUCED** | Draft spec, thin adoption — `HYPOTHESIS` |
| A11 | Content efficiency 4.42% | **REPRODUCED (as a ratio), disputed as a metric** | Measured 20,256 / 443,079 = **4.57%**. The number is real; text-to-HTML ratio is a weak proxy. This skill measures the thing the proxy stands for: the answer-engine first read is **62.5% content / 37.5% link markers** |
| A12 | `Link:` header has no agent-relevant rel values | **REPRODUCED** | Two `Link` headers: eleven `rel="alternate" hreflang=…` and one font `preload`. No `sitemap`, `describedby` or `service-desc` |
| A13 | No per-section `llms.txt` | **REPRODUCED / myth-bounded** | Correct, and myths.md row 1 caps what it is worth |
| A14 | "Entity linking to linkedin.com — add more authority profiles" | **REFUTED** | The homepage `Organization` node carries **nine** `sameAs` targets: x.com, linkedin, t.me, producthunt, reddit, instagram, facebook, youtube, trustpilot. The consequence the grader draws (add Wikipedia/Wikidata/GitHub) is right; the observable it reports is wrong by a factor of nine |
| A15 | No speakable markup | **REPRODUCED** | `HYPOTHESIS` tier — thin adoption |
| A16 | "2/4 metadata signals — missing og:image, og:type" | **REPRODUCED, and located** | True **on the homepage only**. `src/app/[locale]/layout.tsx:87` declares a complete `openGraph` (type + 1200×630 image); `src/app/[locale]/page.tsx:24` overrides `openGraph` **without** `type` or `images`, and Next.js replaces the parent object rather than merging it. `/pricing` re-declares both (`pricing/page.tsx:27`), which is why it passes and the homepage does not |
| A17 | Organization schema missing `address` | **REPRODUCED** | `contactPoint` present, `address` absent. Whether to publish a postal address is a business decision |
| A18 | "Some extended types found: FAQPage, HowTo — add FAQPage, Service or AggregateRating" | **PARTLY, and internally contradictory** | The homepage carries `Organization`, `WebSite`, `SoftwareApplication`, `AggregateOffer`, `FAQPage`, `HowTo`; `/pricing` adds `BreadcrumbList`. The advice asks for `FAQPage`, which its own finding says it found |
| A19 | No `rel="alternate" type="text/markdown"` | **REPRODUCED** | Consistent with A1/A6 |
| A20 | No markdown content negotiation | **REPRODUCED** | `Accept: text/markdown` → `text/html; charset=utf-8` |
| A21 | `Vary` lacks `Accept` | **REPRODUCED / moot** | `vary: rsc, next-router-state-tree, next-router-prefetch, next-router-segment-prefetch, accept-encoding`. Only load-bearing once negotiation exists |
| A22 | No bot-UA markdown serving | **REPRODUCED / correctly declined** | Serving bots different content is the mechanical definition of cloaking (K3). Not a defect |

### Usability (24 items)

The whole layer rests on a premise worth stating once: **PrivateClawd has no
public API.** The only OpenAPI document on the domain is the Mintlify starter
template (see U2). Everything below about OAuth, scopes, SDKs, sandboxes, MCP and
async patterns describes a product surface that does not exist — those are
business decisions about whether to build one, not defects.

| # | Grader check | Verdict | Evidence |
|---|---|---|---|
| U1 | No MCP server / manifest | **N/A** | Nothing to expose |
| U2 | "REST: schema found (3 operations) but missing operationIds" · "Partial function-calling compatibility: 0/3 operationIds, 3/3 typed schemas" · "Documented as open with no authentication required" · "Permissions mentioned but granularity unclear" | **REFUTED, and this is the grader's most expensive error** | `https://docs.privateclawd.com/api-reference/openapi.json` is Mintlify's demo file: `"title": "OpenAPI Plant Store"`, `servers: [{"url": "http://sandbox.mintlify.com"}]`, operations `GET/POST /plants` and `DELETE /plants/{id}`. It is listed in the site's own `docs` `llms.txt` under "OpenAPI Specs". Four separate line items graded the quality of a documentation platform's sample petstore and reported an API as **present** |
| U3 | "API does not return JSON error responses (or no API detected)" — 4 of 4 points | **REFUTED** | `GET /api/bots` → **401** `{"error":"Unauthorized"}` (`application/json`); `GET /api/account/entitlement` → 401 JSON; `GET /api/health` → 200 JSON. The internal API returns JSON errors today. What is true is thinner: the body carries no `code` and no resolution hint, and **`/api/<unknown>` returns a 404 HTML app shell** instead of JSON — which is a real finding the grader did not make |
| U4 | No `WWW-Authenticate` on 401 | **REPRODUCED** | Confirmed: `HTTP/2 401` with no `WWW-Authenticate` header |
| U5 | No MCP Apps / A2UI / WebMCP | **N/A** | Drafts; no MCP surface to attach them to |
| U6 | No agent auth discovery (RFC 9728 / 8414) | **REPRODUCED** | Both 404 on the apex; `api.privateclawd.com` **does not resolve** (DNS failure, not 404) |
| U7 | No Web Bot Auth directory | **REPRODUCED** | 404 |
| U8 | No `/auth.md`, no `auth.md` structure, `agent_auth` endpoints unreachable | **REPRODUCED / N/A** | 404. With no API there is no credential to walk anyone through |
| U9 | No multi-language SDKs, no CLI | **N/A** | Same. "CLI tool mentioned in llms.txt" is **REFUTED** — the apex has no `llms.txt`, and neither `/llm.txt` nor the Mintlify `docs` `llms.txt` mentions a CLI |
| U10 | "You run an MCP server for your documentation, but not one for your product" | **REPRODUCED** | `docs.privateclawd.com/mcp` → **405** on GET (Mintlify's own MCP endpoint, POST-only). That surface is the platform's, not the product's |
| U11 | No sandbox / test environment | **N/A** | No API |
| U12 | No NLWeb `/ask`, no SSE streaming | **REPRODUCED** | Draft spec — `HYPOTHESIS`, Experiments bucket at best |
| U13 | "Nonexistent paths return a real HTTP 404" (passed, 1 of 2 lost for no markdown body) | **REPRODUCED** | 404 with a 6,836-byte HTML body. The markdown-recovery half is a convention, not a standard |
| U14 | "docs MCP returns error for invalid tool call but missing structured code or message" | **UNCHECKED** | Requires an MCP client; `agent_surface.py` is stdlib-only by design (K7 C2). Stated as a gap, not accepted as a finding |

## 4. What the grader structurally could not see

Six findings, none of which appears on any of the 53 lines, all reproduced on
2026-08-14. Five of them are `CONFIRMED`. This section is the argument for why a
scan is a to-do list and not an audit.

### 4.1 `PerplexityBot` is disallowed at the root — a retrieval crawler in a list named for training

`src/app/robots.ts:6–24` defines a constant `AI_TRAINING_BOTS` with seventeen
members. Sixteen of them are training or grounding crawlers, and blocking those
is a legitimate business decision with no retrieval cost. The seventeenth is
`PerplexityBot` (line 16), which Perplexity's own documentation describes as
"designed to surface and link websites in search results on Perplexity. **It is
not used to crawl content for AI foundation models**", and which Perplexity asks
site owners to allow "to ensure your site appears in search results".

The effect: **privateclawd.com cannot appear in Perplexity's answers.** Not as a
model of ranking — as the behaviour the engine documents.

The mechanism is the constant's name. Nobody reviewing "block the training bots"
reads the seventeen members; the name has already answered the question. And a
grader cannot find this, because a grader scores what a site *publishes*, never
what it *forbids*.

`GPTBot` and `ClaudeBot` are also on the list and are **correctly** there:
OpenAI documents `GPTBot` as training-only, Anthropic documents `ClaudeBot` as
training, and each vendor's retrieval agents (`OAI-SearchBot`, `ChatGPT-User`,
`Claude-SearchBot`, `Claude-User`) are separately controlled and **not blocked**.
`Google-Extended` is grounding and does not touch Google Search. This precision
matters in both directions: naming the whole list a citation loss would be as
wrong as missing `PerplexityBot`.

### 4.2 Two `User-agent: *` records with contradictory Content-Signal

Cloudflare's managed block is prepended to the origin's own `robots.txt`, so the
served file carries two wildcard records. On the apex they merely duplicate. On
`docs.privateclawd.com` they **disagree**:

```
# BEGIN Cloudflare Managed content
User-agent: *
Content-Signal: search=yes,ai-train=no,use=reference
…
# END Cloudflare Managed Content
User-agent: *
Content-Signal: ai-train=yes, search=yes, ai-input=yes
```

`Content-Signal` is drafted as an express reservation of rights under Article 4 of
EU Directive 2019/790 — the file's own header says so. Saying `ai-train=no` and
`ai-train=yes` two records apart is a legal statement that contradicts itself, and
RFC 9309 lets a crawler merge the records or take the first.

### 4.3 The FAQ answer an answer engine would quote is a template literal

`src/components/landing-v3-content.tsx:67–70` builds the items for the homepage's
`FAQPage` JSON-LD with `t(\`items.a${i+1}\`)` — **no values object**. The visible
accordion, `src/components/landing-v3-faq.tsx:22`, builds the same strings with
`t(\`items.a${i+1}\`, FAQ_PRICING_VALUES)`. So the machine-readable pricing
answer ships as:

> "Plans start at `${seat}`/month for a dedicated VM with your own API key, or
> `${seatTokens}`/month with `${included}`/mo in AI credits included…"

while the page shows real figures. 1 of 17 declared answers fails to appear in the
served body for this reason; the other 16 match.

The guard that exists for exactly this class,
`src/lib/__tests__/public-claims.test.ts:152–163` ("is passed by every surface
that renders a FAQ"), enumerates **four** files. `landing-v3-content.tsx` — the
fifth renderer, the one feeding the JSON-LD — is not among them.

### 4.4 The agent-facing manual states a price the team already corrected

`src/lib/pricing-tiers.ts:147` records that "Annual plans save 30%" **had never
been true** — the same tables give **17** — and that twenty translated sentences
were parameterized to fix it. `public/llm.txt:17` and `public/llm-full.txt:82,172`
still say **30%**, in three places.

The same root cause as 4.3, one layer out: the surface built for machines was not
in the list of surfaces the claims test protects.

### 4.5 `<lastmod>` is 100% covered and frozen five months back

`src/app/sitemap.ts:18–40` hard-codes `lastModified` per route. All **160**
sitemap URLs carry `<lastmod>`, with **two distinct values**: `2026-03-15` and
`2026-03-19`. The repository has shipped on most days since. A coverage check
scores this 100%; a crawler asking "which of these changed" is told "none, since
March". Present and uninformative is worse than absent — absent asks the crawler
to decide.

### 4.6 The homepage links to `/login` and `/register`, and `robots.txt` forbids both

**Retracted, same day, by this skill's own defect:** an earlier revision of this
section reported that the contact page "answers 200 at `/support` and appears in
no `href` of the served homepage". Both halves were wrong. The site's contact
page is `/contacts` — plural — it is linked from the footer, and it is in the
served HTML. `agent_surface.py`'s alternates list for the contact role carried
`/contact`, `/contact-us`, `/support` and stopped at the first path that answered
200; `/support` is an in-product route that answers 200, so the check named the
wrong page and then correctly observed that *that* page was unlinked. One missing
plural produced two confident false statements. Fixed in the same release: the
list carries `/contacts`, and the selection now prefers an alternate the homepage
actually links to over the first that merely answers. The `/about` half stands —
there is no about page at `/about`, `/about-us`, `/company` or `/about-company`.

What survives, and it is the part that matters: the homepage links to `/login`
and `/register`, both `Disallow`ed by the `*` record (`robots.ts:48–50`).

That last pair is the mechanism behind an earlier observation the operator
recorded: an agent asked to walk through account creation on privateclawd.com
produced its answer from ProductCool, Lenny's Newsletter and NextBigProduct
instead of from the site. Reproduced here: `/register` **does** server-render its
form ("Create an account · Name · Email · Password · Confirm password · Create
account"), but only **271 characters** of text in total, it carries no `H1`, and
`robots.txt` forbids fetching it. The site does not publish a crawlable answer to
"how do I sign up", so the answer gets written by whoever does. (The same note's
claim that `/pricing` was an empty shell is **refuted**: 5,990 characters of
server-rendered text, one `H1`, ten subheads.)

## 5. Findings, triaged

`priority = (impact × confidence) / effort`; confidence is the evidence tier.

### Blockers

| # | Finding | Impact | Tier | Effort | Priority |
|---|---|---|---|---|---|
| B1 | `PerplexityBot` disallowed at the root (§4.1) | 4 | CONFIRMED 1.0 | 1 | **4.0** |
| B2 | The public OpenAPI document is Mintlify's plant-store demo (§3 U2) | 4 | CONFIRMED 1.0 | 1 | **4.0** |

### Leaks

| # | Finding | Impact | Tier | Effort | Priority |
|---|---|---|---|---|---|
| L1 | Agent manual unreachable at `/llms.txt`; it lives at `/llm.txt` (§3 A1) | 3 | CONFIRMED 1.0 | 1 | **3.0** |
| L2 | FAQ JSON-LD emits `${seat}` placeholders (§4.3) | 3 | CONFIRMED 1.0 | 1 | **3.0** |
| L3 | `llm.txt` / `llm-full.txt` state a 30% annual discount that is 17% (§4.4) | 3 | CONFIRMED 1.0 | 1 | **3.0** |
| L4 | Homepage `openGraph` override drops `og:image` and `og:type` (§3 A16) | 2 | CONFIRMED 1.0 | 1 | **2.0** |
| L5 | `<lastmod>` frozen at two March dates across 160 URLs (§4.5) | 2 | CONFIRMED 1.0 | 1 | **2.0** |
| L6 | Contradictory `Content-Signal` on the docs host (§4.2) | 2 | CONFIRMED 1.0 | 1 | **2.0** |
| L7 | ~~`/support` unlinked in server-rendered HTML~~ — **retracted**, the contact page is `/contacts` and it is linked (§4.6). No `/about` page anywhere | 2 | CONFIRMED 1.0 | 2 | **1.0** |
| L8 | 13 URLs competing for `privateclawd`, incl. a UTM URL; 9 for `privateclawd company`, four of them fragments (§1) | 3 | CONFIRMED 1.0 | 3 | **1.0** |
| L9 | `/api/<unknown>` returns a 404 HTML app shell instead of JSON (§3 U3) | 2 | CONFIRMED 1.0 | 1 | **2.0** |

### Gains

| # | Finding | Impact | Tier | Effort | Priority |
|---|---|---|---|---|---|
| G1 | No non-branded traction: 1,094 impressions → 0 clicks, `openclaw hosting` at position 49 (§1) | 5 | CONFIRMED 1.0 | 5 | **1.0** |
| G2 | No `/about` page; `Organization` has no `address` (§3 A17) | 2 | STUDY 0.7 | 1 | **1.4** |
| G3 | `sameAs` has nine social profiles and no authority profile (Wikidata, GitHub) (§3 A14) | 2 | STUDY 0.7 | 2 | **0.7** |
| G4 | No Wikidata item with P856 (§3 D2) | 3 | STUDY 0.7 | 4 | **0.5** |

### Experiments

Everything below `CONFIRMED` that the grader asked for, and it is most of the
report: `ai-catalog.json`, `agent-card.json`, `agent-skills/index.json`,
`api-catalog`, `pricing.md`, `index.md`, markdown negotiation, `speakable`,
`schemamap:`, NLWeb `/ask`, WebMCP, per-section `llms.txt`. All are draft or
vendor conventions; **none has a measured effect on this site**, and with no
server logs there is no agent-traffic baseline to measure one against.

**The one experiment worth running first is not on the grader's list:** turn on
AI/agent user-agent counting in the logs. Track K tells an auditor to size agent
demand before paying for agent surfaces, and this site currently cannot answer
whether a single agent has ever fetched it. Every item in this bucket stays
`HYPOTHESIS` until it can.

## 6. The change plan

Ordered by priority. Each row names the exact target, the change, why, how to
verify, and how to undo it.

| # | Target | Change | Why (tier) | Verify | Rollback |
|---|---|---|---|---|---|
| 1 | `src/app/robots.ts:16` | Remove `PerplexityBot` from `AI_TRAINING_BOTS`; rename the constant to `AI_TRAINING_AND_GROUNDING_BOTS`; add a comment naming the retrieval agents that must stay allowed | Perplexity documents the bot as its search crawler and asks that it be allowed (CONFIRMED) | `curl https://privateclawd.com/robots.txt` shows no `PerplexityBot` `Disallow`; then a Perplexity query for the brand within ~4 weeks | Re-add the line |
| 2 | `docs.privateclawd.com/api-reference/` | Delete the plant-store spec and its nav entry, or replace it with a real spec. Until an API exists, deleting is correct | An agent reading it calls `sandbox.mintlify.com` (CONFIRMED) | `curl …/openapi.json` → 404, and the `docs` `llms.txt` no longer lists it under "OpenAPI Specs" | Restore the file |
| 3 | `public/llm.txt` → `public/llms.txt`, `public/llm-full.txt` → `public/llms-full.txt` | Rename; add 301s from the old names; update `src/middleware.ts:180` and `src/components/footer.tsx:297` | Every client probes the conventional name (CONFIRMED). **Not** a ranking lever — myths.md row 1 | `curl -I https://privateclawd.com/llms.txt` → 200 `text/plain`; old path → 301 | Rename back |
| 4 | `src/components/landing-v3-content.tsx:69` | Pass `FAQ_PRICING_VALUES` to `t()`, exactly as `landing-v3-faq.tsx:22` does | The JSON-LD ships `${seat}` to answer engines (CONFIRMED) | `page_audit.py --url https://privateclawd.com/` reports `faq_declared_served == faq_declared` | Revert |
| 5 | `src/lib/__tests__/public-claims.test.ts:153` | Add `src/components/landing-v3-content.tsx`, `public/llms.txt` and `public/llms-full.txt` to the enumerated surfaces | The guard's home list is what let #4 and #6 ship (CONFIRMED) | The test fails against the pre-#4 tree | Revert |
| 6 | `public/llms.txt:17`, `public/llms-full.txt:82,172` | Replace "30%" with 17%, or generate the block from `pricing-tiers.ts` | `pricing-tiers.ts:147` records 30% as never having been true (CONFIRMED) | #5's extended test passes | Revert |
| 7 | `src/app/[locale]/page.tsx:24` | Add `type: "website"` and the `images` array, or drop the `openGraph` override so the layout's survives | Next.js replaces the parent `openGraph` object (CONFIRMED) | `curl -s / \| grep og:image` returns a tag | Revert |
| 8 | `src/app/sitemap.ts:18–40` | Derive `lastModified` from the file's git mtime or the build timestamp | 160 URLs, two dates, five months stale (CONFIRMED) | `agent_surface.py` no longer reports `sitemap-lastmod-frozen` | Restore the map |
| 9 | Cloudflare dashboard | Decide `ai-train` once. Either drop the managed block on the docs host or align the origin's `Content-Signal` with it | The served file reserves rights in two directions (CONFIRMED) | `curl https://docs.privateclawd.com/robots.txt` shows one answer | Re-enable |
| 10 | `src/app/api/**` 404 handling | Return JSON with a `code` for unknown `/api/` paths, and add `WWW-Authenticate: Bearer` to the 401 | An agent parsing an HTML app shell from an API path cannot recover (CONFIRMED) | `curl -s /api/nope` → JSON | Revert |
| 11 | Navigation / `src/components/footer.tsx` | Put `/support` (and an `/about`) in the server-rendered HTML | A link that only exists after hydration is invisible to every document reader (CONFIRMED) | `agent_surface.py` no longer reports `entry-point-unlinked` | Revert |
| 12 | Canonicalization | Canonical the UTM variant; stop declaring homepage fragments as separate URLs | 13 URLs for one brand query (CONFIRMED) | GSC cannibalization list shrinks | Revert |
| 13 | Logging | Count AI/agent user agents with forward-confirmed reverse DNS | Nothing in track K can be sized without it (CONFIRMED as a gap) | The counter reports non-zero or zero, and either is an answer | — |

**Not in the plan, deliberately:** an MCP server, SDKs, a CLI, OAuth, sandboxes,
`auth.md`, agent cards and the rest of the Usability layer. They presuppose a
public API. Whether to build one is a product decision worth **$0 of SEO effort**
until it is taken, and no scanner's point total should make it.

## 7. What this cost the skill

Running the skill against a live site rather than reading it surfaced four defects
in the skill, all fixed in v0.19.0.

| # | Defect | How it hid |
|---|---|---|
| D48 | `page_audit.py` reported `faq-schema-orphan` at `high` / `CONFIRMED` — "no question/answer pairing was found in the served markup" — on a page whose answers **were** in the served markup. It counted `<dt>`/`<dd>` and `<details>`/`<summary>` and nothing else, so the WAI-ARIA disclosure pattern (`aria-expanded` + `aria-controls` → `aria-labelledby`) read as no pairing at all | The check was a **proxy** for the question. The question is "are the declared answers in the body"; it asked "did I see a definition list". A proxy fails silently in the direction nobody tests, and this one fired on both templates of a real site |
| D49 | `agent_surface.py`'s `parse_robots` collected which AI agents were **named** and never what was **decided** about them. A site naming seventeen AI crawlers and blocking all seventeen produced **no robots finding at all** | Silence read as a pass. The doctrine was already right — `growth-plays.md` B9 is this exact play, and `agent-readiness.md` K2a said to report the decision "whichever way it was answered" — so this is standing instruction #10 again: doctrine and instrument are two homes of one fact, and nothing compared them |
| D50 | The same module's `ANSWER_ENGINE_UAS` listed `GPTBot`, `ClaudeBot` and `Google-Extended` as answer-engine retrieval crawlers. All three are training or grounding crawlers on their vendors' own documentation, and the retrieval agents (`OAI-SearchBot`, `ChatGPT-User`, `Claude-SearchBot`, `Claude-User`) were absent or incomplete | The buckets were assembled from the **shape of the names**. `technical-checks.md` had carried the correct statement (`OAI-SearchBot` ≠ `GPTBot`) since before this module existed. Had the fix for D49 shipped without this one, the first site it ran on would have been told it had blocked its own citations in sixteen places, fourteen of them wrong |
| D51 | Nothing checked whether an OpenAPI document describes the product being audited. Every K4 property is structural, and a documentation platform's sample spec satisfies all of them | It needs one non-structural question, and the module was built entirely out of structural ones. The grader made the same error, which is the tell: this is a class, not an oversight |
| D52 | The entry-point check named the wrong contact page and then reported it unlinked. Its alternates list held `/contact`, `/contact-us`, `/support` — not `/contacts` — and it stopped at the first path that answered 200 | Two defects in one line. The list is a claim about how sites are named, and a missing plural is enough to invert a finding; the early break then guaranteed the wrong page won whenever an in-product route answered first. **Found by continuing to work after the report was written** — the finding was already in §4.6 and in the triage table before it was refuted, which is the argument for `git mv`-ing nothing and re-running everything after a fix |

Also fixed: `sitemap-lastmod` was measured as coverage only, so a hard-coded date
on every URL scored 100%.

**Shipped in v0.19.0**

- `agent_surface.py`: robots parsed as records with verdicts (`_robots_groups`,
  `_blocks_root`), four buckets with vendor sentences attached, and five new
  findings — `robots-retrieval-blocked`, `robots-training-decided`,
  `robots-contradictory`, `robots-blocks-linked-page`, `sitemap-lastmod-frozen`.
- `agent_surface.py`: `agent-file-misnamed` — probe the near-misses before
  reporting `/llms.txt` absent.
- `agent_surface.py`: `openapi_provenance()` → `openapi-template-spec` (blocker)
  and `openapi-foreign-servers`, run **before** the per-operation grading.
- `page_audit.py`: ARIA disclosure pairing counted; `_faq_declared_vs_served()`
  compares every declared `acceptedAnswer` against the served body;
  `faq-schema-orphan` re-scoped, `faq-schema-partial` and
  `faq-schema-unreadable` added (the latter `HYPOTHESIS` — "I could not read it"
  is not a confirmed absence).
- Doctrine: K2a rewritten with the verified taxonomy and the
  list-under-the-wrong-label failure mode; K3a added (publish at the name clients
  probe; a second surface for a fact needs the same guard); K4a added (whose API
  is this); K7 gains reasons 5 and 6; `aeo-geo.md` F8 gains the ARIA pairing and
  the drift case; `myths.md` row 33.
- Every new guard was watched failing against a deliberately broken tree before
  being trusted (standing instruction #2).

**Still open after v0.19.0** — carried to
[../evidence/backlog.md](../evidence/backlog.md):

| id | Item |
|---|---|
| K-A1 | `agent_traffic.py` — parse a log export and count AI user agents with forward-confirmed reverse DNS. Still the highest-value missing instrument: every track-K effect claim is `HYPOTHESIS` without it, and this audit hit that ceiling on item 13 of its own plan |
| K-A8 | The near-miss probe covers root agent files only. The same class exists for `/.well-known/` (`agent-card.json` vs `agentcard.json`) and is unprobed |
| K-A9 | `openapi_provenance` reads `servers[]` and fingerprints. It does not check whether the documented paths **answer** — a spec describing a real product's API that was never deployed passes |
| K-B4 | Nothing compares a JSON-LD `Offer`/`AggregateOffer` price against the page's own rendered price. `page_audit.py` has `jsonld-price-parity` for the page; the equivalent for a flat agent file (`llms.txt` restating a price) has no instrument at all — §4.4 was found by reading |
| K-B5 | The contradiction check finds two `User-agent: *` records. It does not detect the more common CDN case: a managed block whose rules contradict the origin's for a **named** agent |

### Coverage after v0.19.0 — what the skill still cannot answer mechanically

The operator's goal is that this skill can close a scan like this one on its own.
Of the 53 items, **41 are now produced by a bundled script**, 6 are answered by a
track's reasoning without a script (and should stay that way), and **6 need an
instrument the skill does not have**. The residue, with where each is tracked:

| Grader item(s) | Why no script answers it | Tracked as |
|---|---|---|
| D1 developer-resource discoverability | A SERP observation. `tooling.md` routes it to a SERP source (Prowl / SearchAPI); scripting it would mean shipping a search vendor | Not a gap — route, don't script |
| D2 Wikipedia / Wikidata | `entity-and-brand.md` owns it and it is not a fetch: notability is the constraint | Not a gap |
| D5, D6, D7, U9 npm / PyPI / plugin.json / skills.sh / SDKs | Three third-party registry APIs, each rate-limited, and the answer is a business decision either way. Worth a `--registries` opt-in flag rather than a default probe | gap doc §4 **A4** |
| U1, U10, U14 MCP server, product-vs-docs coverage, MCP error shapes | Needs a protocol client and a transport; the bundled scripts are stdlib-only single files by design. The server **card** is probed; the server is not | gap doc §4 **C2** (deliberate) |
| U5 WebMCP in-page tools | Needs same-origin bundle discovery, a size cap, and a regex over the bundles. Shipping it half-done returns "not found" on every code-split site | gap doc §4 **A2** |
| U12 NLWeb `/ask` and SSE | Two probes, cheap. Not written because the spec's adoption is thin enough that a false "absent" costs more than the check earns — revisit if adoption moves | **new, unassigned** |
| U8 `/auth.md` structure grading | Presence is probed; the seven-section structure is not. The draft is moving, and a structural check against a moving draft produces false findings on a compliant file | gap doc §4 **A5** |
| U6 Web Bot Auth key shapes | Presence is probed; whether the JWKs are `kty=OKP`, `crv=Ed25519` with `kid`/`nbf`/`exp` is not | gap doc §4 **A3** |
| — advertised-URI reachability | K2's stale-file rule ("do not publish a file you cannot keep true") is doctrine enforced by nothing | gap doc §4 **A6** |
| A5 `?mode=agent` | One scanner's convention with no specification. Adopting it would mean rewarding a site for guessing the same convention | gap doc §4 **C1** (deliberate) |

Plus the five this audit added: **B-11** (`agent_traffic.py` — the missing half of
K1, and the reason every Experiments row here is unrankable), **B-12** (near-miss
probing beyond root files), **B-13** (does the documented API answer, not just
exist), **B-14** (a price restated in a flat agent file), **B-15** (a managed
robots block contradicting the origin for a *named* agent).

**The honest summary: the skill can now produce every finding on this scan that is
worth producing, plus six the scan could not.** What it cannot yet do is *size*
any of them, because B-11 does not exist — and that, not the unprobed draft specs,
is the gap that matters.

## 8. What could not be checked

- **Agent and AI-crawler traffic.** No server-log access. This is the gap that
  caps the whole of track K at `HYPOTHESIS` (K1), and it is why the Experiments
  bucket is not a plan.
- **Field Core Web Vitals.** PageSpeed Insights returned HTTP 429 (daily quota).
- **Answer-engine citation baseline.** No before-state was captured for ChatGPT,
  Perplexity, Claude or AI Overviews, so the Perplexity fix (plan #1) will have
  no clean before/after. Capture the prompt set **before** shipping it.
- **The docs MCP endpoint's error shapes** (grader item U14) — needs an MCP
  client; out of scope for a stdlib-only collector by design (K7 C2).
- **Rendered DOM.** Every markup finding here is server-rendered HTML only. The
  JSON-LD findings are safe in that respect (the nodes are in the source), but
  "not in the served HTML" never means "not on the page" (non-negotiable #8).
- **Bing and Yandex.** No webmaster access; all index findings are Google's.
