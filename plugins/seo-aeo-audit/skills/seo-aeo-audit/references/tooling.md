# Tooling — what to run for which check

The audit is an analysis exercise, not a tool run. Tools flag candidates; the
auditor decides what is real. Two rules before anything else:

## Contents

- [Ladder — use the highest rung available](#ladder--use-the-highest-rung-available)
- [Check → tool routing](#check--tool-routing)
- [Browser engine — WebKit (Safari) first](#browser-engine--webkit-safari-first)
- [Chrome DevTools recipes worth memorising](#chrome-devtools-recipes-worth-memorising)
- [Where the automation stops](#where-the-automation-stops)
- [Property instrument registry](#property-instrument-registry)
- [The checkup by occasion](#the-checkup-by-occasion)
- [UI-only steps, and how an agent takes one](#ui-only-steps-and-how-an-agent-takes-one)
- [Paid indexers and index checkers](#paid-indexers-and-index-checkers)
- [Field notes from one property (October 2026)](#field-notes-from-one-property-october-2026)


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
| 6 | Manual fetch + browser devtools (Safari Web Inspector first — [engine order](#browser-engine--webkit-safari-first)) | The specific page, the specific header, the specific render |

State in the report which rung each finding rests on. **The rung caps the evidence
tier, and the cap is stated for all six** — an earlier version of this paragraph
mapped three of them and contradicted itself inside one sentence, capping a
third-party index at `STUDY` and "an inference from public data" at `HYPOTHESIS`
when a third-party index *is* public data. Between `STUDY` (0.7) and `HYPOTHESIS`
(0.2) sits a 3.5× difference in computed priority, so the gap changed the order of
the plan.

| Rung | Ceiling | Why |
|---|---|---|
| 1 · server logs | `CONFIRMED` | the fetch happened; the line is the observation |
| 2 · Search Console / Bing / Yandex Webmaster | `CONFIRMED` | the engine's own answer about your property |
| 3 · full crawl | `CONFIRMED` for what the crawler *saw* (a directive, a status code, a link) · `STUDY` for anything it *models* (internal PageRank, "orphan candidates") | a crawler observes markup and infers structure; the two are different claims |
| 4 · field performance (CrUX, RUM) | `CONFIRMED` for the distribution it reports · never for a cause | it measures users, not the reason |
| 5 · third-party indices | `STUDY` only when the method and sample are published, and no higher — two indices agreeing is a stronger `STUDY`, not a `CONFIRMED`; an estimate publishing neither is `HYPOTHESIS`, whoever sells it | a panel estimate about someone else's property |
| 6 · manual fetch + DevTools | `CONFIRMED` for what the response contains (header, source, rendered DOM) · `HYPOTHESIS` for what it implies about indexing | the lowest rung by *breadth*, not by reliability: one page seen exactly |

Rung 6 sitting at the bottom is about coverage, not truth. A `view-source` showing
`noindex` is `CONFIRMED` — `evidence-tiers.md` names an HTTP response and a
rendered DOM as CONFIRMED-grade observations — while "therefore the page is not
indexed" is an inference that rung 2 settles in one call.

**A public-only audit** (no property access at all) is capped at `STUDY` by rung 5,
which is what `SKILL.md` step 1 says. It cannot answer "why is this page not
indexed" at any tier, because no rung it can reach observes the index.

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
| Site speed — diagnosis | DevTools Performance + Lighthouse | The stated Chromium exception: both are Chrome tools. Check the same template in WebKit too (Safari Web Inspector's Timelines) before calling a speed problem universal. See the recipes below |
| Field + lab in one call, scriptable | PageSpeed Insights API (`pagespeedonline/v5/runPagespeed`, key optional) via `scripts/psi_pull.py` | Returns CrUX field data (`loadingExperience`, `originLoadingExperience`) **and** the Lighthouse lab run (`lighthouseResult`). Report the field percentiles; the lab score explains them, it does not replace them |
| Lighthouse categories other than performance | `chrome-devtools` MCP `lighthouse_audit` | The stated Chromium exception — Lighthouse runs only in Chrome. Covers SEO, accessibility, best practices **and agentic browsing** — the last is the surface where `llms.txt` is actually checked (myths.md). It **excludes performance**: for that, start a trace instead, or use the PSI row above |
| Independent rank verification, and what the SERP actually contains | `searchapi:google_rank_tracking` — up to 100 results per query with position, title, URL and snippet, localized via `gl` / `location` | One collector, subject to the poisoned-SERP guard ([measurement.md](measurement.md#the-poisoned-serp-guard)): from September 2026 on, a series counts only with its collection method recorded, a 3 to 5 query spot check against a logged-out WebKit capture, and agreement with GSC average position within a stated band, else it is `UNUSABLE`. A challenge page (HTTP 200, no organic block) is missing data, never rank 0. Once the guard passes, SERP **composition** is an observation for track D; an index's position estimate never is |
| Structured data | Rich Results Test + `scripts/page_audit.py` | Validation ≠ eligibility (technical-checks.md B) |
| Internal link equity | Crawl (internal PageRank) + backlink data | Overlay revenue to find the mismatch |
| Backlink risk | GSC Links report + one third-party index | Toxicity scores are not a disavow trigger (threats-and-defense.md I6) |
| Rank + SERP composition | An independent tracker, subject to the poisoned-SERP guard (measurement.md J2); SERP screenshots per market/device | Record market, device, date and collection method with every observation |
| Does this phrase have demand at all | Two independent volume datasets — never one ([prowl-mcp.md](prowl-mcp.md): `dataforseo_labs_keyword_overview` + `dataforseo_kw_clickstream_bulk_volume`) | A page built on a zero-volume phrase is not an intent mismatch, it is a page with no query to rank for. One panel returning 0 is inconclusive, and a 0 is written blank with `source=tool-zero`, never as zero (linkbuilding.md); demand evidence then comes from internal site search, GSC impressions and support questions; two indexes disagreeing with each other is itself the finding |
| Sizing a whole competitive set at once | `dataforseo_bl_bulk_backlinks` — up to 1000 domains in one call | Establishes which competitors are reachable benchmarks and which are five orders of magnitude away, before you copy anyone's playbook |
| Anchor profile of a competitor | `dataforseo_bl_anchors` + `majestic_get_anchor_text` for the second index | **Filter on `backlinks_spam_score` first.** Top anchors by referring domains are frequently PBN spam pointed *at* the domain; an unfiltered read copies someone else's negative-SEO problem |
| Which pages in a niche actually earn links | `dataforseo_bl_domain_pages` (`page_summary.referring_domains`) across the competitive set | Tells you whether links in this category accrue to deep content or to a directory homepage — that decides whether the answer is publishing or placement |
| Bing first-party queries and pages | `scripts/bwt_pull.py` (GetQueryStats, GetPageStats; key or OAuth token on stdin), after `preflight.py --bing-site` passes | Rung 2 for Bing. The AI Performance report has no documented API method: a dated manual export with its column headers recorded is the rung-2 evidence for it |
| Scoring repeated AI answers | `scripts/ai_panel.py` over saved capture records | Raw counts with a Wilson interval, run-to-run Jaccard of cited URLs, `insufficient-sample` below three runs on two days. API captures are labelled `api-proxy` and under-cover the UI (aeo-geo.md F5) |
| AI visibility | The prompt set per engine + inbound logs + Bing AI Performance; at scale, `dataforseo_ai_llm_mentions*` and the per-engine `ai_*_responses` tools ([prowl-mcp.md](prowl-mcp.md)) | Vendor "visibility scores" are directional at best (measurement.md J3). Sampled observations of a non-deterministic surface — record engine and date, never present mention share as a rank |
| Conversion and call outcomes | Analytics + call tracking + CRM | See demand-and-conversion.md |
| What robots.txt actually breaks in the render | A robots-aware proxy (`VorticonCmdr/robotstxtProxy`, shipped with Docker images for the proxy and a Chromium instance) or DevTools request blocking | Anything disallowed is never downloaded, so it is never rendered; block the same resources locally and read the degraded page yourself |
| Forgotten hosts and subdomains | A subdomain enumerator (e.g. `guisublist3r`) before a migration, plus `site:` patterns against dev/staging host names | Run it on your own estate first — an indexed staging host is a common self-inflicted finding, not just a competitor-recon trick |
| Entity gaps for a page or SERP | Any extractor, **then Google's own blocks for that query** as the referee | Between 46.6% and 65.1% of what four general-purpose extractors report has no trace in the engine's vocabulary or the competing top pages, and the budget-LLM option is not even deterministic (entity-and-brand.md G3, figures in benchmarks.md). The tool proposes; the AI Overview, People Also Ask and related searches decide |
| Recon with search operators (`inurl:`, `intitle:`, `site:`) | The operator, verified on a known-positive query first | Precision is degrading and reports conflict: practitioners report `inurl:` returning nothing, operator references say it still works with partial matching and regional inconsistency, and both agree Google now rate-limits and fingerprints automated querying (`HYPOTHESIS`, 2026-08 — both readings recorded, neither settled; `cache:` and `related:` are already gone). Prove the operator returns a URL you know matches before you build a recipe on it, and expect a browser session to be required where a raw request is not |
| Query class for a keyword set | `queryclassifier.com` | Predicts the class that maps to which SERP features appear and where the answer has to sit (intent-and-content.md) |
| CTR expectation for this site | GSC export + a custom CTR-curve notebook (Brittney Muller's Colab) | Generic CTR tables hide SERP-feature and brand effects; there is no universal benchmark (experience-signals.md) |
| Evidence capture for the report | A WebKit full-page screenshot (Playwright `webkit` with `fullPage: true`, or Safari) + the response headers, both dated, the engine named; Chrome DevTools' full-size capture when the finding is about Chrome | A finding needs an artefact someone else can re-open, not a description (evidence-tiers.md) |

## Browser engine — WebKit (Safari) first

When the audit opens a page in a browser — a manual look at a render, a parity
diff, a dated screenshot for the report — it opens it in **WebKit first**:
Safari through `safaridriver` (WebDriver; `sudo safaridriver --enable` once) for
a real browser, Playwright's `webkit` (the `webkit` project, `--browser webkit`,
installed with `npx playwright install webkit`) for automation, Safari Web
Inspector for debugging. On macOS open a page with `open -a Safari <url>`, not
the system default browser, which may be another engine. An automation library
(browser-use and the like) runs on its WebKit/Safari backend where it has one.
WebKit has the narrowest support envelope of the big three, so a page that
works there is the stricter claim — and iOS Safari is the audience CrUX cannot see.

**Chromium is a stated fallback, never the default.** Use it when the task needs
Chrome itself and say which and why: a Chrome-only API, a CDP trace, the
`chrome-devtools` MCP, and the measurement tools that are **Chromium by
definition** — Lighthouse, PageSpeed Insights (its lab run is Lighthouse) and
CrUX (field data from Chrome users only). Those stay in this skill as the
**stated Chromium exception**; they are not replaced and not re-labelled as
cross-browser. Prefer the Chrome Dev build for a Chrome run you start yourself;
give it a temporary profile (never the user's), record what you started, and
close every process you started before you finish.

A render checked only in Chromium is reported as exactly that — "checked only in
Chromium" — never as "tested in a browser". Neither engine is Google's renderer:
whether Googlebot saw the content is settled by URL Inspection and the Rich
Results Test, never by your own browser, Safari or Chrome.

## Chrome DevTools recipes worth memorising

These are Chromium DevTools panels — the stated Chromium exception above. Where a
recipe has a Safari Web Inspector equivalent (the Network tab's headers, the
Elements tree for a parity diff, the Console, user-agent override), run it there
first; Coverage, the Core Web Vitals overlay, Layout Shift Regions and
Performance Insights are Chrome tools and are reported as Chromium readings.

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
- The [Prowl MCP](prowl-mcp.md) puts ~448 provider tools behind one endpoint on a
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
  belong. The Indexing API is not a general one: on 2026-10-16 Google removed an
  outdated form from its quota documentation, and the API is still documented only
  for pages with JobPosting or BroadcastEvent embedded in a VideoObject
  (`CONFIRMED`, [documentation updates](https://developers.google.com/search/updates)). Two caveats: deterministic is not the same as correct — GSC sampling,
  freshness lag and interpretation traps survive the rewrite — and the pattern
  does not port to analytics for free, because GA4 schemas vary per property
  while the GSC query shape is fixed.
- Spreadsheet work is still where multi-source data gets joined (crawl + GSC +
  analytics + revenue). Clean first (blank rows/columns, inconsistent labels),
  join on the URL, then pivot by template — that view is what makes a finding
  provable. Keep it survivable: named ranges instead of cell references, few
  formulas rather than chained ones, conditional formatting to make the outliers
  visible before anyone reads a number.

## Property instrument registry

A checkup forgets what it does not list. Before the first audit of a property, write its
registry once, **in the property's own repository**, and make every later checkup walk it:
one row per instrument, with how it is reached and what it is there to answer. The audit
then reports each row as run, unreachable (and why), or not connected, never as silence.
Findings stay in the dated audit; the registry holds only access and purpose.

| Column | What goes in it |
|---|---|
| Instrument | the console, API, script or log, by its own name |
| Access | the route an agent takes: an API script, an MCP tool, a UI in a named browser session, a CLI |
| Credential | the vault **name** of the key or token, never its value; "operator session" for a UI |
| Rung | the ladder rung above, which caps the tier of anything it shows |
| Answers | the one question this instrument is there for |
| Evidence | the file and line, command or dated report that shows it was reached |

The rows to try on any property, so none is skipped for want of remembering it:

| Area | Rows |
|---|---|
| Google Search Console | Search Analytics API (`gsc_pull.py`); URL Inspection API (`url_inspection.py`); Sitemaps API (`sitemap_audit.py`); UI-only pages: Manual actions, Security issues, Live test, Request indexing; Pages report export |
| Bing Webmaster Tools | API (`bwt_pull.py` after `preflight.py --bing-site`); UI: AI Performance report, site verification or import from Search Console |
| Yandex Webmaster | UI; API behind an OAuth consent the property owner grants once |
| Verification | how each engine verified the property (DNS, file, meta tag, import), so a removed tag is not mistaken for lost access |
| Analytics | GA4 Data API and Admin API; GA4 Admin UI for key events and the Search Console link; Yandex Metrica goals; any first-party event sink |
| Server-side counts | one count per money step, recorded by the server, with no consent dependency |
| Answer engines | the prompt set per engine you can reach (`ai_panel.py` over saved captures; a SERP API for AI Mode) |
| Agent surface | `robots.txt`, `llms.txt`, Markdown variants via `Accept: text/markdown`, machine-readable pricing, `agent_surface.py` |
| Indexing push | IndexNow key file and the endpoints that accepted it; any paid indexer or index checker the operator holds an account with, by its vault name (below) |
| Performance | PSI and CrUX (`psi_pull.py`), Lighthouse, field RUM if any, the project's own byte budgets |
| Crawl and render | a full sitemap sweep with redirects not followed; WebKit render first; the project's own production readback scripts |
| Logs and errors | host access and router logs, a long-retention log drain, error tracking |

## The checkup by occasion

A registry answers *what exists*; the occasion decides *what runs now*. Each step names its
instrument; a step whose instrument is unreachable is reported as not done, with the reason.

**A new site, before launch.**

1. Search Console domain property by DNS; a quota project with the Search Console API enabled; `preflight.py` green.
2. Bing Webmaster by import from Search Console; its API key in the vault; `preflight.py --bing-site` green.
3. Yandex Webmaster and Metrica verified; Metrica goals created **before** the code calls `reachGoal`; the OAuth consent asked for on day one, because it is the step that waits on a person.
4. GA4 key events, the Search Console link, custom dimensions applied from a registry in code.
5. An IndexNow key file; a `robots.txt` that opens what should be crawled; `llms.txt` and Markdown variants only with content that is true.
6. A server-side count for every money step, so a consent banner cannot hide the funnel.
7. Production readback checks wired into the release script, so each release re-reads what earlier ones promised.

**Every release.** The project's gates and CI on the exact commit; the production readback;
a grep of the server-rendered HTML, per locale, for every string the release promised and every
string it removed; a render of the touched pages; host logs read for personal data and for the
request id.

**Weekly.** Search Analytics with brand and non-brand split; Bing traffic and crawl stats;
analytics channels; the server-side funnel; unresolved errors.

**Monthly, or after a content or catalog change.** The full sitemap sweep; URL Inspection on a
random sample and on every URL whose indexing was requested; the Pages report export; Yandex
duplicates; the answer-engine prompt set; Lighthouse on the heaviest templates; an IndexNow push
after a large URL change.

**An indexing push** (new pages, a new site, or pages Google discovered and left out) runs as an
experiment, never as a blast:

1. **Inspect** every candidate with `url_inspection.py`. Its per-property quota (benchmarks.md)
   covers a young site whole; on a large one, inspect the templates that earn money first.
2. **Plan**: keep only URLs reported absent and allowed (no `noindex`, not blocked by robots);
   an indexed URL is never paid for, and a row with no index status is missing data. Split the
   rest into a treatment and a held-out control by a seeded hash (10 to 50 percent), so a re-run
   never moves a URL between arms.
3. **Push** the treatment through the provider the operator chose (*Paid indexers and index
   checkers*, below), per engine, preferring per-indexed billing; record task ids and the
   provider's answers in a ledger beside the plan, never the key.
4. **Read** both arms with URL Inspection at day 7 and day 14 (Yandex: its own console at day 15).
   The effect is the treatment's indexed share minus the control's, with both counts; the
   provider's own report is not the verdict.

Free levers go first and are not part of the experiment's cost: one internal link from a page
crawled daily, the sitemap, IndexNow, Request indexing for a handful of URLs.

**Dated readings** (an experiment's read date, a re-inspection 14 days after a request) are not a
cadence: they live on the project's board with their date.

## UI-only steps, and how an agent takes one

Some first-party answers and actions have no API. URL Inspection's API reports only the
indexed version: *"Presently only the status of the version in the Google index is available;
you cannot test the indexability of a live URL"* (`CONFIRMED`,
[urlInspection.index.inspect](https://developers.google.com/webmaster-tools/v1/urlInspection.index/inspect),
read 2026-10-23), and it has no method that requests indexing. The Indexing API covers only
pages with JobPosting or BroadcastEvent embedded in a VideoObject (`CONFIRMED`, above). So
Request indexing, Live test, Manual actions and Security issues are Search Console UI, and so are
Bing's AI Performance report and, until its OAuth consent exists, everything in Yandex.

Requesting indexing changes the property's crawl queue, so it stays behind the access rule in
`SKILL.md`: only with the operator's go in this session. With the go, an agent can take the step
in the operator's signed-in browser without a person clicking, and one property did it for six
URLs in October 2026 (`FIELD`). The way that held:

1. **Open a window of your own** and act on it by its id, never by its index: another session
   driving the same browser moves the front window, and an action by index then lands in the
   wrong window (this happened once, on another organisation's tab; nothing was written there).
2. **Re-read the window's URL before every input**, and stop if it is not the console.
3. **Stop when someone else is using the screen**: a person at the keyboard or another session
   in the same browser. The step waits; it is never forced.
4. Submit the URL in the console's inspection field, wait for the panel, press Request indexing,
   and **read the confirmation back** ("URL was added to a priority crawl queue"). Inspection
   panels can stack in the page, so confirm that exactly one request button exists and that it
   belongs to the URL just inspected before reporting the request as made.
5. Close the window, record each URL with its status before the request (discovered, unknown,
   soft 404) and the date, and put a re-inspection 14 days later on the board.

## Paid indexers and index checkers

The doctrine stands as written: an indexer can only force a crawl, and the quality gate that
follows decides inclusion (technical-checks.md, myths.md). These services sell **two different
jobs**, and only one of them is an audit instrument.

**The checker is an instrument.** It answers "is this URL in the index" per URL, in bulk, and for
engines with no per-URL API an agent can call. It earns its place when the URLs to check exceed
the URL Inspection quota (benchmarks.md, *Operational benchmarks*): a sitemap of several thousand
URLs cannot be inspected through Google's API in a day. Its method is never published, so its
answer is `HYPOTHESIS` until it agrees with URL Inspection on a sample that holds both indexed and
unindexed URLs; record the agreement rate beside the result, and keep an answer of "unknown" as
missing data, never as "not indexed".

**The indexer is a paid push, and it acts on the property.** It spends money, so it runs only with
the operator's go, and only after the free levers: one internal link from a page crawled daily,
the sitemap, IndexNow, Request indexing (*UI-only steps*, above). **Never grant an indexer owner access to the property.** A service that asks for access to the
Search Console account or property (one of the three below has a flag for it) can act as the owner
and read the property's data, and how it uses that access is not published (`HYPOTHESIS` for the
use, `CONFIRMED` for the flag). If the operator grants it anyway, it goes into the property's
instrument registry as an access grant, with the date and who can revoke it.

Then:

1. Feed it only URLs verified **absent** from the index. A URL already indexed counts as a success
   and inflates the rate (myths.md).
2. Hold out a random share of the cohort as a control, and compare the indexed share of both at a
   fixed day (7 and 14), measured by URL Inspection, not by the vendor's report.
3. Prefer billing per indexed URL where it is offered, and still re-verify: the vendor's "indexed"
   is its own checker's verdict.
4. A service that does not disclose how it causes the crawl may use link networks, which the
   spam-network row of the field test in myths.md scored lowest; treat its effect on the property
   as unknown (`HYPOTHESIS`) and say so in the report.

Three services, as their API pages described them on 2026-10-23 (`CONFIRMED` for the API contract
only; nothing here measures their effect):

| Service | Jobs and engines | Billing | Status semantics | Access |
|---|---|---|---|---|
| SpeedyIndex | indexer for Google (also a drip-feed variant) and Yandex; checker for Google, Bing and Yandex; a backlink checker | tokens bought in packages; an indexer task can be billed per indexed URL (`pay_per_indexed`) | a task is complete when every URL was sent; with per-indexed billing the final count arrives later, so wait for the result flag, then read the full report (indexed and unindexed lists with titles) | REST v2, key in the `Authorization` header; base `https://api.speedyindex.com` |
| seoindex.link | indexer for Google; checker for Google | a fixed price per submitted link for indexing and a lower one per checked link, charged on acceptance; a batch the balance cannot cover is refused whole; unresolved checks are refunded | an indexing request ends at `submitted`, which means sent, not indexed; a check returns 1, 0 or null, and the vendor itself says null is not "not indexed" | REST v1, bearer key issued by a Telegram bot; mechanism not disclosed |
| 2index.ninja | indexer for Google, Yandex and Bing (an instant mode for Google), also from a watched sitemap; checker for Google only, per region | a plan with an expiry date plus tokens, charged when a link is queued; tokens come back only for links still in the queue; an automatic check after sending costs extra | a link's send status (`Sent`, `In the queue`, `Error sending` and others) is reported apart from `google_indexed`; a batch with one invalid link is refused whole | REST v1, bearer token from the account page; a `google_access_granted` flag on submissions, described only as Google account access granted |

### Provider sheets

What each API documented on 2026-10-23, so an agent can call it without reading the vendor's page
again. `CONFIRMED` for the contract as written by the vendor, nothing more: none of these numbers is a
measured indexing rate. Re-read the vendor page before a run that spends; prices and modes move.

**SpeedyIndex**, REST v2, base `https://api.speedyindex.com`.

| Item | Value |
|---|---|
| Auth | header `Authorization: <key>` (no `Bearer`); `Content-Type: application/json` on POST |
| Answer envelope | every response carries `code`: 0 success, 1 insufficient balance or not found, 2 validation error, 3 rate limit or server error; HTTP 401, 402, 413, 429 |
| Rate limit | 120 requests per minute per IP |
| Balance | `GET /v2/account` returns `balance.tokens`, `balance.indexer` (credits), `balance.checker` (credits); free to call |
| Create | `POST /v2/task/{google,yandex,bing}/{indexer,checker}/create` with `urls` (max 10,000) and an optional `title`; Bing is checker only |
| Google indexer | only `pay_per_indexed: true` is available: 100 tokens a URL charged at creation, refunded in full for URLs not indexed after 7 days |
| Yandex indexer | per-indexed always on: indexer credits first (1 a URL), then 20 tokens a URL, refunded in full for URLs not indexed after 15 days |
| Drip feed | Google indexer only: `drip_feed: true`, `drip_feed_days` 2 to 30, at least as many URLs as days, equal daily batches |
| Status | `POST .../status` with `task_id` or `task_ids` (max 1,000): `size`, `processed_count`, `indexed_count`, `is_completed`; per-indexed tasks add `status`, `tokens_charged`, `tokens_refunded`, `check_after` |
| Completion trap | `is_completed` means every URL was sent; on a per-indexed task the final `indexed_count` arrives after `check_after`, so read the report then |
| Reports | `POST .../report` (URL lists) and `.../fullreport` (indexed URLs with titles; unindexed with `error_code`) |
| List | `GET .../list/{page}`, 1,000 tasks a page, newest first; Google filters `standard`, `pay_per_indexed`, `drip_feed` |
| Single URL | `POST /v2/{google,yandex}/url` with `url` and optional `pay_per_indexed`; code 3 is a daily limit or a failed task, refunded |
| Backlink checker | `POST /v2/task/backlink/checker/create` with donor `urls` (max 10,000) and `target_domains` (max 50); report paginated (max 100) with HTTP status, Moz DA and spam score, target links |
| Packages | $5 = 5,000 tokens, $20 = 30,000, $50 = 120,000, $100 = 250,000, $250 = 700,000, $500 = 1,500,000; PayPal adds 10 percent |

**seoindex.link**, REST v1, base `https://seoindex.link/api/v1`.

| Item | Value |
|---|---|
| Auth | `Authorization: Bearer <key>` or `X-API-Key: <key>`; the key comes from a Telegram bot, and regenerating it kills the old one at once |
| Index | `POST /index` with `urls` (array or newline text, up to 200,000, duplicates merged); 202 with `id`, `charged_usd`, `balance_usd`; Google only |
| Status | `GET /status?id=`: `queued`, `processing`, `submitted` (sent, not indexed) or `failed` (refunded) |
| Check | `POST /check`, then `/check-status?id=` and `/check-results?id=` (cursor `after_id`, `limit` up to 10,000, filter `all`, `indexed`, `not_indexed`, `unknown`); `is_indexed` 1, 0 or null, and null is not "not indexed" |
| Billing | $0.01 a link to index, $0.002 a link to check, charged on acceptance; a batch the balance cannot cover is refused whole (402, nothing charged); unresolved checks refunded |
| Errors | 400 no valid URLs, 401 key, 402 balance, 404 unknown id, 405 method, 413 over 200,000 |
| Mechanism | not disclosed; no indexing-rate claim |

**2index.ninja**, REST v1, base `https://2index.ninja/api/v1/`.

| Item | Value |
|---|---|
| Auth | `Authorization: Bearer <token>` from the account page; send a `User-Agent`, some hosts answer 403 without one |
| Add | `POST link/add_simple` with `links` (array or newline text), optional `project_name` (default `default`), engine flags `google`, `yandex`, `bing` (booleans, at least one), `google_access_granted` (keep false) |
| Projects | `POST project` (`type` `indexing` or `indexing_check`, `website`, speed, `instant_indexing`, `check_links`, `geo_target_id`, default 2840, the US); `GET project/{id}` returns sent, queued, indexed and not-indexed counts with download URLs |
| Sitemap | `POST sitemap/add` with `watch` to keep sending new URLs from a sitemap |
| Resend | `POST link/resent_notindexed_links/{project_id}` with `max_attempts` 1 to 10 |
| Checker | Google only, per region |
| Billing | a plan with an expiry date plus tokens, charged when a link is queued; tokens return only for links still queued; an automatic check after sending costs extra; instant mode has its own rate |
| Traps | one invalid link refuses the whole batch; error shapes vary (array, object or string); a project id may come back as a number or a string |
| Mechanism | not disclosed; the `google_access_granted` flag asks for access to the Google account |

### The ledger

A push leaves one file per provider and engine beside its plan, and nothing in it is secret:

| Field | What it holds |
|---|---|
| plan | the path of the plan: label, property, seed, control share, counts by class, the treatment and control lists |
| provider, engine | which service and which engine received the treatment |
| sent_at | when |
| tasks | per request: the provider's task or project id (or none, when refused), the HTTP status, the provider's answer as returned, the URL count |
| snapshots | each status read: when, and what the provider answered per task |
| readings | each verdict: the day, URL Inspection counts for both arms, the difference, and the provider's tokens charged and refunded |

The verdict line of a run reads: treatment indexed `a` of `n`, control indexed `b` of `m`, difference in
percentage points, tokens charged and refunded, and the date. Below three properties or one cohort it is
`FIELD`.

## Field notes from one property (October 2026)

One multilingual storefront on a hosted platform behind a CDN. Every note is `FIELD`: one site,
no control. Each is worth checking for on the next property, not assuming.

- **A CDN served the old `robots.txt` for 24 hours** after the origin changed it. Read it again
  through the CDN the next day before calling the change live.
- **IndexNow's shared endpoint answered 403** to a key that Bing (200) and Yandex (202) accepted
  directly, the same day. Submit to the engines' own endpoints and record each status.
- **Bing's clicks ran about 15 times the analytics sessions** from Bing, and its click count
  includes bots it does not filter. Compare trends between the two, never totals.
- **Analytics behind a consent banner saw about one Google click in five.** Money steps were
  read from a server-side count instead, which needs no consent and stores no personal data.
- **PageSpeed Insights answered 429** (daily quota, no key) on three audit days. Field data was
  then a gap, written as such, never as a pass.
- **A banned-phrase grep over server HTML matched a quoted customer review.** Read the element a
  hit sits in before calling it a claim of the site.
- **A local build without its data source rendered no prices**, so every price check against it
  passed vacuously. A content check needs the data the page is built from.
- **A machine under load failed browser checks** for reasons outside the site: one cold
  `hydrated=false` in four runs at a load average of twice the core count. Re-run before it is a
  finding, and refuse lab measurements on an oversubscribed machine.
- **Router logs kept identifiers in URL paths** that the log drain's redactor did not mask,
  because it looked for the international `+` form only. Read a sample of the host's own router
  lines, not only the application's, when a check asks whether logs carry personal data.
- **A Metrica goal missing from the UI drops `reachGoal` without an error.** Create goals before
  the code that reaches them ships.
