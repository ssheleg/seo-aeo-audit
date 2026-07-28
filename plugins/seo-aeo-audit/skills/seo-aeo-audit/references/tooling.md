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
| 5 | Third-party indices (Ahrefs, Semrush) | Links, keyword estimates, competitor context — estimates, never ground truth |
| 6 | Manual fetch + browser DevTools | The specific page, the specific header, the specific render |

State in the report which rung each finding rests on. The rung caps the evidence
tier: a log line or a Search Console screenshot can support `CONFIRMED`; a
third-party index estimate cannot rise above `STUDY`, and an inference from
public data alone stays `HYPOTHESIS` until something first-party confirms it.

## Check → tool routing

| Check | Primary | Notes |
|---|---|---|
| Index status of a specific URL | GSC URL Inspection | Shows Google-selected canonical, crawl date, rendered HTML — but follows redirects and hides the pre-render source |
| Index coverage per template | GSC Pages report + crawl diff | Split "crawled – not indexed" from "discovered – not crawled" |
| Robots/directive conflicts | Crawl + raw source fetch | `view-source`, not the browser DOM; check `X-Robots-Tag` headers too |
| Rendering parity | GSC URL Inspection, Rich Results Test, DevTools request blocking, a robots-aware rendering proxy | Never judge rendering from your own browser |
| Crawl waste | Server logs by path bucket and status | Percentages of crawl per template beat any crawler estimate |
| Site speed — field | CrUX / GSC CWV report / RUM | Lab numbers rank nothing |
| Site speed — diagnosis | DevTools Performance + Lighthouse | See the recipes below |
| Structured data | Rich Results Test + `scripts/page_audit.py` | Validation ≠ eligibility (technical-checks.md B) |
| Internal link equity | Crawl (internal PageRank) + backlink data | Overlay revenue to find the mismatch |
| Backlink risk | GSC Links report + one third-party index | Toxicity scores are not a disavow trigger (threats-and-defense.md I6) |
| Rank + SERP composition | An independent tracker; SERP screenshots per market/device | Record market, device, date with every observation |
| AI visibility | The prompt set per engine + inbound logs + Bing AI Performance | Vendor "visibility scores" are directional at best (measurement.md J3) |
| Conversion and call outcomes | Analytics + call tracking + CRM | See demand-and-conversion.md |

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

## Where the automation stops

- Screaming Frog v24+ ships an MCP server — an agent can drive crawls and exports
  directly. Use it when available; it replaces the manual export step, not the
  judgement.
- `scripts/page_audit.py` in this skill covers per-page directives, canonical
  traps, headings, schema inventory, alt coverage, JS-gated prices and the
  answer-engine read budget. It does not crawl; pair it with a real crawler.
- Spreadsheet work is still where multi-source data gets joined (crawl + GSC +
  analytics + revenue). Clean first (blank rows/columns, inconsistent labels),
  join on the URL, then pivot by template — that view is what makes a finding
  provable.
