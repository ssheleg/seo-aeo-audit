# Tooling — what to run for which check

The audit is an analysis exercise, not a tool run. Tools flag candidates; the
auditor decides what is real. Two rules before anything else:

1. **A flag is not a finding.** Many tool "issues" are irrelevant on a given
   site; confirm each one against behavior (index status, traffic, revenue).
2. **When two tools disagree, dig until you know why.** Do not average them and
   do not pick the one that supports the story.

## Ladder — use the highest rung available

| Rung | Source | Gives you |
|---|---|---|
| 1 | Server logs | Ground truth on what bots fetched, when, with which status. The only place AI-crawler behavior is observable. |
| 2 | Search Console / Bing Webmaster / Yandex Webmaster | First-party index status, queries, AI-surface reporting, manual actions |
| 3 | Full crawl (Screaming Frog, Sitebulb, Oncrawl, Botify) | Site-wide structure, directives, duplication, depth, internal links |
| 4 | Field performance (CrUX, `cruxvis.withgoogle.com`, RUM) | Real-user CWV by form factor, competitor comparison |
| 5 | Third-party indices (Ahrefs, Semrush, [Prowl MCP](prowl-mcp.md)) | Links, keyword estimates, competitor context — estimates, never ground truth |
| 6 | Manual fetch + browser DevTools | The specific page, the specific header, the specific render |

State in the report which rung each finding rests on. The rung caps the evidence
tier: a log line or a Search Console screenshot can support `CONFIRMED`; a
third-party index estimate cannot rise above `STUDY`, and an inference from
public data alone stays `HYPOTHESIS` until something first-party confirms it.

**Rung 1 does not exist on most hosted platforms.** Shopify, Wix, Squarespace and
comparable SaaS hosts expose no raw access logs, so a crawl-budget question there
starts at rung 2 and the finding is capped there. Say that in the report instead
of presenting a crawler's URL count as crawl data — a crawler tells you how many
URLs exist, never which ones Google spent its allowance on.

**Two third-party indexes agreeing is a stronger `STUDY`, not a `CONFIRMED`.**
It is still worth doing: cross-checking a volume figure or a backlink profile
against a second, independent index is the cheapest way to tell a real signal
from an artefact of one vendor's panel. [prowl-mcp.md](prowl-mcp.md) covers how
to run that cross-check when you have no second seat.

## Check → tool routing

| Check | Primary | Notes |
|---|---|---|
| Index status of a specific URL | GSC URL Inspection | Shows Google-selected canonical, crawl date, rendered HTML — but follows redirects and hides the pre-render source |
| Index coverage per template | GSC Pages report + crawl diff | Split "crawled – not indexed" from "discovered – not crawled" |
| Robots/directive conflicts | Crawl + raw source fetch | `view-source`, not the browser DOM; check `X-Robots-Tag` headers too |
| Rendering parity | GSC URL Inspection, Rich Results Test, DevTools request blocking, a robots-aware rendering proxy | Never judge rendering from your own browser |
| Crawl waste | Server logs by path bucket and status | Percentages of crawl per template beat any crawler estimate |
| Crawl waste with no server logs (hosted platform) | GSC Crawl Stats (Settings → Crawl stats: by response, file type, purpose, Googlebot type) + Pages report grouped by reason + a full crawl | The rung-2 substitute: host-level shares, totals and status mix, never per-URL truth. Enough to rank the causes, not to claim a percentage per template (technical-checks.md A2) |
| Site speed — field | CrUX / GSC CWV report / RUM | Lab numbers rank nothing |
| Site speed — diagnosis | DevTools Performance + Lighthouse | See the recipes below |
| Structured data | Rich Results Test + `scripts/page_audit.py` | Validation ≠ eligibility (technical-checks.md B) |
| Internal link equity | Crawl (internal PageRank) + backlink data | Overlay revenue to find the mismatch |
| Backlink risk | GSC Links report + one third-party index | Toxicity scores are not a disavow trigger (threats-and-defense.md I6) |
| Rank + SERP composition | An independent tracker; SERP screenshots per market/device | Record market, device, date with every observation |
| Does this phrase have demand at all | Two independent volume datasets — never one ([prowl-mcp.md](prowl-mcp.md): `dataforseo_labs_keyword_overview` + `dataforseo_kw_clickstream_bulk_volume`) | A page built on a zero-volume phrase is not an intent mismatch, it is a page with no query to rank for. One panel returning 0 is inconclusive; two indexes disagreeing with each other is itself the finding |
| Sizing a whole competitive set at once | `dataforseo_bl_bulk_backlinks` — up to 1000 domains in one call | Establishes which competitors are reachable benchmarks and which are five orders of magnitude away, before you copy anyone's playbook |
| Anchor profile of a competitor | `dataforseo_bl_anchors` + `majestic_get_anchor_text` for the second index | **Filter on `backlinks_spam_score` first.** Top anchors by referring domains are frequently PBN spam pointed *at* the domain; an unfiltered read copies someone else's negative-SEO problem |
| Which pages in a niche actually earn links | `dataforseo_bl_domain_pages` (`page_summary.referring_domains`) across the competitive set | Tells you whether links in this category accrue to deep content or to a directory homepage — that decides whether the answer is publishing or placement |
| AI visibility | The prompt set per engine + inbound logs + Bing AI Performance; at scale, `dataforseo_ai_llm_mentions*` and the per-engine `ai_*_responses` tools ([prowl-mcp.md](prowl-mcp.md)) | Vendor "visibility scores" are directional at best (measurement.md J3). Sampled observations of a non-deterministic surface — record engine and date, never present mention share as a rank |
| Conversion and call outcomes | Analytics + call tracking + CRM | See demand-and-conversion.md |
| What robots.txt actually breaks in the render | A robots-aware proxy (`VorticonCmdr/robotstxtProxy`, shipped with Docker images for the proxy and a Chromium instance) or DevTools request blocking | Anything disallowed is never downloaded, so it is never rendered; block the same resources locally and read the degraded page yourself |
| Forgotten hosts and subdomains | A subdomain enumerator (e.g. `guisublist3r`) before a migration, plus `site:` patterns against dev/staging host names | Run it on your own estate first — an indexed staging host is a common self-inflicted finding, not just a competitor-recon trick |
| Query class for a keyword set | `queryclassifier.com` | Predicts the class that maps to which SERP features appear and where the answer has to sit (intent-and-content.md) |
| CTR expectation for this site | GSC export + a custom CTR-curve notebook (Brittney Muller's Colab) | Generic CTR tables hide SERP-feature and brand effects; there is no universal benchmark (experience-signals.md) |
| Evidence capture for the report | DevTools full-page screenshot + the response headers, both dated | A finding needs an artefact someone else can re-open, not a description (evidence-tiers.md) |

## Chrome DevTools recipes worth memorising

- **Console drawer**: enable Coverage, Rendering and Network Conditions — the
  three panels that matter for SEO work.
- **Header response**: Network tab → select the document → Headers. Check request
  URL, method, status code, content encoding, last-modified, cache headers, and
  robots directives. This is where **soft 404s** are caught: page renders fine,
  header says 404 (or the reverse — an empty page returning 200).
- **JavaScript parity**: compare source HTML with the rendered DOM to find
  content, links or directives that exist in only one of them.
- **All links on a page with attributes**:
  `table($$('a'), ['text','href','rel'])` in the console — anchor text, target
  and `rel` in one table.
- **Images with dimensions**: `table($$('img'), ['src','width','height'])` —
  missing width/height are your layout-shift candidates.
- **JS errors**: Console filtered to errors; a code error can block content from
  rendering, an "SEO error" is invisible to users but breaks crawling.
- **Emulation**: device toolbar for mobile rendering, location override for
  geo-specific behavior, and network throttling for slow-connection reality.
- **Security panel**: certificate validity and mixed-content resources.
- **Copy selector / XPath** from the Elements panel straight into a crawler's
  custom extraction.
- **Beautify minified sources** with `{}` in the Sources panel before reading
  third-party scripts.
- **Parity diff, mechanically**: Elements panel → right-click → Copy → Copy
  element for the rendered DOM, `view-source` → select all for the delivered
  HTML, then diff the two. Ignore the injected script noise and read only for
  `meta robots`, canonical, hreflang, title, headings and the body copy — those
  are the differences that change indexing.
- **Switch user agent** in Network conditions to see what a page returns to a
  named crawler. Treat it as a smoke test for UA-conditional serving, not as a
  rendering verdict: it does not reproduce Google's rendering service, so confirm
  anything you find with URL Inspection.
- **Layout Shift Regions** and the **Core Web Vitals overlay**, both in the
  Rendering panel: the first highlights the areas that move during load, the
  second puts live metric values on screen while you interact — this is how you
  identify the element behind a CLS number instead of guessing from a score.
- **Performance Insights with throttling and the cache disabled** reproduces a
  first-time visitor and lists render-blocking resources with the moment each one
  bites — the panel to open before anyone proposes an image-format project.
- **Local Overrides** to hold an edit across reloads: prove the fix (remove a
  render-blocking file, change the title, drop the offending element) on the real
  page before writing the ticket. It costs minutes and turns "we think this is
  it" into a demonstrated cause.
- **Full-page screenshot** (Command menu → Capture full size screenshot) for the
  dated artefact that goes into the report next to the header dump.

## Where the automation stops

- Screaming Frog v24+ ships an MCP server — an agent can drive crawls and exports
  directly. Use it when available; it replaces the manual export step, not the
  judgement.
- The [Prowl MCP](prowl-mcp.md) puts ~408 provider tools behind one endpoint on a
  pay-per-call wallet, which is what makes bulk competitive and demand data
  reachable without a per-vendor seat. It moves the same rung-5 caveat with it:
  breadth, not ground truth. Discovery (`prowl_search_tools`, `prowl_tool_info`)
  is free, failed calls are not billed, and every response carries its own
  `billing` object — so quote the real spend in the report.
- `scripts/page_audit.py` in this skill covers per-page directives, canonical
  traps, headings, schema inventory, alt coverage, JS-gated prices and the
  answer-engine read budget. It does not crawl; pair it with a real crawler.
- **An agent handed raw rows will invent the arithmetic.** Ask a model for
  positions or click deltas and it answers fluently from rows it summed badly;
  most analytics MCPs make this worse by pushing thousands of rows into the
  context window. The pattern that holds: do the maths **before** the model sees
  it — run CTR curves, decay, cannibalization and position deltas in SQL/Python
  in the warehouse and hand back one compact result, so the model reads a
  finished table and does the interpreting (`FIELD`). The same server-side path
  is where URL Inspection API index-status checks and IndexNow submissions
  belong. Two caveats: deterministic is not the same as correct — GSC sampling,
  freshness lag and interpretation traps survive the rewrite — and the pattern
  does not port to analytics for free, because GA4 schemas vary per property
  while the GSC query shape is fixed.
- Spreadsheet work is still where multi-source data gets joined (crawl + GSC +
  analytics + revenue). Clean first (blank rows/columns, inconsistent labels),
  join on the URL, then pivot by template — that view is what makes a finding
  provable. Keep it survivable: named ranges instead of cell references, few
  formulas rather than chained ones, conditional formatting to make the outliers
  visible before anyone reads a number.
