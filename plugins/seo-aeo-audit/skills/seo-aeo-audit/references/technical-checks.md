# Tracks A & B — access, indexation economics, canonicalization

Everything here is a check you run and record, not advice you repeat. Capture the
observed value and the date for each.

## A0. Blockers first

If any of these is true, stop and fix it before auditing anything else.

| Check | How | Blocker if |
|---|---|---|
| Manual action | GSC → Security & Manual actions | Any action present. It is a **binary multiplier** — nothing else you improve counts until it is lifted. Fix everything, *then* file reconsideration; premature requests get rejected and the improvements shipped meanwhile are not re-evaluated. |
| Sitewide `noindex` / auth wall | fetch the raw HTML (`view-source`, not the browser DOM) | `noindex` present in the **pre-render source** even if the rendered DOM is clean — Google honors the tag if it appears in *either* version, and GSC shows you neither the pre-render source nor the conflict. |
| Robots-blocked site or key section | `robots.txt` + GSC robots tester | Money paths disallowed. |
| Deindexation event | GSC Pages report + `site:` + log traffic | Sudden index loss → jump to [threats-and-defense.md](threats-and-defense.md) (hijack, DMCA, spam action). |
| DNS / property coverage | GSC properties list | Only the canonical variant is verified. Verify **all**: domain property, https www, https non-www, http, and key directories. A domain property aggregates protocols and subdomains — it is where a hijacked `www` shows up as an anomalous click spike. |
| **Every host variant actually resolves** | `curl -sI` each of `https://www.`, `https://`, `http://www.`, `http://` and read the status **and** the body title | Any variant returns 4xx/5xx instead of 200 or a 301 to the canonical host. A dead `www` silently kills every inbound link, citation and typed visit that used it — and it will not appear in any crawl that starts from the canonical host, so nothing else in this file catches it. |

**Look for spikes, not only drops.** A one-day burst of clicks on one URL for
off-topic queries is the classic signature of a subdomain takeover; deindexation
can precede the manual action by 24h+.

**Read the error body, not just the status, when a host variant fails.** A CDN
returns its own branded error page and the `<title>` names the cause, which is
usually not what the status code suggests:

- **Cloudflare Error 1000, "DNS points to prohibited IP"** — a proxied record
  pointing into the CDN's own address space. The classic shape is `www` as a
  **proxied CNAME to the apex** while the apex A records themselves already hold
  CDN addresses. The edge refuses to proxy to itself and answers 403 before the
  origin is ever contacted. Reading only the `403` sends you looking for a WAF
  rule or a missing redirect; neither exists.
- Before proposing the fix, check **whether the origin would even accept the
  host**. Platform-as-a-service origins (DigitalOcean App Platform, Heroku,
  Vercel and friends) route on the Host header and reject anything not registered
  as a domain on the app. If only the apex is registered, repointing DNS trades a
  403 for a 404 and fixes nothing.
- That leaves three real options, in cost order: a **redirect rule at the edge**
  (Cloudflare Single Redirects — note the API token permission is
  `Zone → Single Redirect → Edit`, *not* `Zone → Config → Edit`); a **tiny edge
  worker** on a `host/*` route, which needs only Workers Routes Edit and is the
  fallback when the redirect permission is unavailable; or **registering the host
  on the origin** and redirecting in the application, which is the heaviest
  because it usually means a deploy and a certificate.

Whichever is used, verify with path and query preserved on a real deep URL, not
just the root, and re-check a minute later — edge routes take a short while to
propagate and can return transient 5xx immediately after deployment.

## A1. Crawl access and rendering

- **Blocked resources break rendering.** Anything disallowed in `robots.txt` is
  never downloaded, therefore never rendered. Blocking a framework path (e.g.
  `/_next`) breaks layout and links for Googlebot; allowing `/_next/static/` and
  `/_next/image` restores indexing. Verify with GSC URL Inspection / Rich Results
  Test, DevTools request-blocking, or a robots-aware rendering proxy — **not**
  your browser.
- **Wildcards match substrings, not paths.** `Disallow: /*?` blocks every
  parameterized URL behind it (one store lost ~40% of product pages from the
  index; a retailer lost 45% of traffic and needed six weeks just to diagnose).
  `Disallow: /*print` also blocks `/blueprints/`, `/footprint/`, `/imprint/`;
  `Disallow: /account/` also catches `/account-settings/`.
  Validate by crawling twice (respecting vs ignoring robots.txt) and diffing the
  URL sets — every URL that disappears is a page the file hides from Google.
  Keep `robots.txt` in version control with a dated changelog; audit quarterly.
- **A clean `robots.txt` proves nothing if the edge blocks the bot.** CDN, WAF
  and bot-management rules answer crawlers with `403`, `429` or a JS challenge
  while a browser gets `200`. Fetch one URL per template with each bot user agent
  from an off-network IP and compare status code and byte size against the
  browser fetch (`CONFIRMED` — the status code is the observation). Reported as
  the first of three audit layers for AI reach, Jun 2026.
- **Never cloak with a Googlebot-specific `Disallow: /`.** It hides nothing and
  reads as deception.
- **`<meta name="robots" content="none">` ≡ `noindex, nofollow`.** Several SEO
  extensions parse it wrong — check the raw source, not a plugin.
- **Directives arrive in HTTP headers, not only in HTML.** `X-Robots-Tag` and
  `Link: <…>; rel="canonical"` never appear in `view-source`, and server,
  directory (`.htaccess`) or edge config applies them to whole folders and to
  non-HTML assets (PDF, images, feeds). Audit the response headers per template
  **and** per asset type: status, robots rules, canonical, content type, cache
  (SEJ *Ultimate Technical SEO Audit Workbook*, 2023). A near-empty PDF entered
  the index immediately once its directory was given an `index, follow`
  directive — the folder-level header, not the page content, was the blocker
  (`FIELD`, Jul 2026).
- **Blocked-but-indexed URLs are empty shells.** Google indexes the URL string
  without processing content, so they cannot trigger duplicate filters or dilute
  sitewide quality. Do **not** unblock `robots.txt` just to add `noindex` (that
  burns crawl budget); the GSC removal tool only hides results temporarily.
  Intervene only if those URLs actually steal impressions from canonical pages on
  commercial queries — which means the canonical page's quality is the real
  problem.
- **You cannot hide links from Google with JS, spans or JSON.** Google parses
  URL-like strings wherever it finds them (source HTML, rendered DOM, JSON
  blocks) and queues them. The only reliable controls are `robots.txt` (for
  compliant crawlers) and firewall/WAF rules.
- **Geo-redirects and content negotiation hide whole locales.** A site that
  redirects by IP, or serves a different language on `Accept-Language`, shows
  Googlebot one version and only one: Google crawls predominantly from US IPs
  with a US-English `Accept-Language`, so every other locale can be
  simultaneously live for users and **absent from the index**. It is invisible
  from inside the company, because staff browse from the country whose version
  works. Check: request a localized URL with a non-US egress and with varied
  `Accept-Language`, compare status codes and final URLs against a plain
  request; then confirm against the index rather than the response — the
  Google-selected canonical and coverage state per locale come from
  `scripts/url_inspection.py`, and a locale that resolves to another country's
  URL there is the finding. The fix is the standard one: let every locale live
  at its own crawlable URL, link them with reciprocal `hreflang`, and offer a
  *suggestion* banner instead of a redirect. Bing also treats hreflang
  differently from Google, so verify both when a property matters in each.
- **AI crawlers are separate user agents.** `OAI-SearchBot` (ChatGPT retrieval)
  is not `GPTBot` (training); unblocking one does nothing for the other. A
  robots-blocked page returns `viewing lines [0-0] of 0` to ChatGPT Deep Research
  and silently vanishes from the report. Verify from logs with
  forward-confirmed reverse DNS — a crawler hit only proves the URL was fetched,
  never that a model learned it. Whether the domain appears in **Common Crawl**
  is a separate check again. Bot identity today rests on a self-reported user
  agent plus IP; Google's experimental **Web Bot Auth** (announced May 2026) has
  agents sign requests cryptographically, which makes spoofed "trusted agents"
  detectable — until it is widely adopted, forward-confirmed reverse DNS stays
  the method.
- **You cannot block Google's AI use without blocking Google Search.** Googlebot
  is not split by purpose, and Cloudflare's Content Signals initiative (launched
  2025) had little uptake as of Jul 2026 — that part is documented (`CONFIRMED`).
  Sites that lost Google visibility were observed losing ChatGPT visibility
  roughly in proportion (`FIELD`, single case); a Bing-only counter-case points
  the other way, so the *index dependency* itself is `HYPOTHESIS` — aeo-geo.md F4
  owns both observations and the reading rule. Neither reading makes a Googlebot
  block safe: price the trade-off before it ships, not after.

### Rendering is a second budget, and it is not the crawl budget

Crawling and rendering are separate passes. Fetching HTML is cheap; executing
JavaScript is not, so JS-dependent pages queue for a later render that can arrive
hours or days behind the fetch. Crawl budget counts URLs fetched; the render
queue decides how many of them ever have their JavaScript run. On a JS template
this is the ordinary cause behind *Crawled – currently not indexed*: the page was
read, the content was not.

**The executable diagnostic.** URL Inspection reports **Last crawl**, and *View
crawled page* shows the HTML Google stored at that crawl. Compare that stored
copy against the raw source: content that exists only after JavaScript runs and
is missing from the stored copy is content Google has not rendered yet. Then run
*Test live URL*, which fetches and renders now — the gap between the stored copy
and the live render is the queue you are measuring. The tool exposes no
"last rendered" timestamp, so a diagnostic written around one cannot be run;
this is the form that can (`CONFIRMED` — both surfaces are documented, and the
comparison is an observation you can point at).

**What burns the render budget** is practitioner consensus, not measurement:
heavy bundles, third-party tags (analytics, session recording, chat widgets, a
tag manager carrying a dozen of them), lazy-loading that never fires for a bot,
and infinite scroll. Named thresholds — a megabyte of bundle, 200KB of
first-screen JavaScript — are places to measure, not targets to report
(`HYPOTHESIS`; no published study fixes them). One field account of a 700KB
bundle put the lever on third-party scripts plus server-side rendering rather
than bundle weight alone (`FIELD`, Jul 2026).

**Fix order that survives contact.** Server-render the content, headings and
metadata that define the page; then cut payload; never lazy-load the hero image,
the body copy, the headings or the navigation. Where SSR is impossible, serving
the crawler a cached HTML snapshot is allowed *provided the snapshot matches what
users get* — divergence is cloaking. Give every paginated batch a crawlable URL
carrying full content in the initial HTML response, and do not add
`rel=next`/`rel=prev` while doing it (A7: it is unsupported and must not be
"fixed" back in).

### Googlebot does not scroll — it stretches, once

To evaluate lazily-loaded content Googlebot renders with a viewport far taller
than a screen rather than scrolling down the page. That much is an engine
statement, and an old one — Google's advice for reproducing what it sees has been
a viewport around 9,000px tall in DevTools since **2017** (`CONFIRMED`; date it
to Mueller, not to whichever recent post reminded you of it). What practitioner
rendering research adds is the part that decides the audit: the expansion happens
**once per render**, and that single resize is what fires scroll listeners and
`IntersectionObserver` callbacks (`FIELD`, 2026-08 — no primary published, so
verify it on the template rather than asserting it). Two consequences worth
auditing:

- **Sequential infinite scroll never loads batch two.** An implementation that
  needs a second, third and n-th scroll event gets one, so everything after the
  first payload stays invisible to the indexer. Crawlable pagination URLs are the
  fix, not a taller viewport.
- **An unconstrained hero breaks the rendered layout.** A full-screen hero image
  with no CSS `max-height` scales with the stretch and pushes the main content
  thousands of pixels down the rendered page. Whether that depth costs ranking
  weight is unproven (`HYPOTHESIS`); that the rendered page no longer resembles
  the designed one is visible in the rendered screenshot, which is where to check
  it rather than in a browser.

### Mobile-first: the mobile response is the only one that counts

A URL can return 404 on desktop and 200 on mobile and stay indexed and ranking
for months — the desktop status is not the one being read. Two checks follow:

- **Request each template's status with a mobile user agent**, not only the
  desktop default. A 410 served to desktop alone changes nothing.
- **Kill the discovery path, not just the response.** A single internal link — one
  mention on a parent FAQ page — is enough to keep an obsolete URL in rotation,
  because the crawler keeps arriving and keeps re-confirming it. Removing that
  link destroys the path; `noindex` or an honest 404/410 removes the URL, with no
  meaningful speed difference between them; the GSC removal tool only buys time
  while one of those takes effect (John Mueller). `CONFIRMED` — the status code
  and the link are both observations.

## A2. Indexation economics

Treat the index as a scarce resource: Google raises the quality bar when it hits
capacity, so every new page competes for a finite slot (patent *Managing URLs*,
US7509315B1). Publishing more pages dilutes unless demand grows with them.

**Split the two GSC exclusion diagnoses — they need opposite fixes:**

| Status | Meaning | Fix path |
|---|---|---|
| Discovered – currently not indexed | Crawl budget/priority exhausted | Importance signals: contextual internal links from your most-crawled pages, a priority sitemap with fresh `lastmod`, one external dofollow link from an indexed page, clean server signals (TTFB <200ms, no 5XX, no redirect chains). 70–80% index within 72h in field reports. |
| Crawled – currently not indexed | Fetched and **not selected** — read here as a quality rejection, but the cause is disputed (see below) | Discovery signals will not help either way. Step back to page and sitewide quality: unique value, intent match, thin/duplicate clean-up. John Mueller: when systems doubt sitewide quality they crawl less and index less — that is not a technical bug to patch. |

**The cause of "Crawled – currently not indexed" is contested.** This file reads
it as a quality rejection (Mueller's statement above). A competing practitioner
account (FIELD, 2026-06-18) reads it as almost purely an **authority deficit**,
arguing from identical content indexing instantly on a strong domain and failing
on a weak one — the same case recorded in architecture-and-equity.md. Both are
credible and they prescribe different work (rewrite versus link), so the cause
drops to **HYPOTHESIS**: do not assert one in a report. The discriminating
experiment is in architecture-and-equity.md, "Crawl frequency is an architecture
output" — hold content constant, add links from strong nodes to one cohort,
leave a matched cohort alone, measure index rate (design it per experiments.md).
Whichever theory holds, discovery-side pushes are the wrong fix, so the fix path
above stands while the cause is open.

**Check the reporting before you diagnose the site.** A page-indexing freeze ran
for roughly 14 days alongside the June 2026 spam update and was logged by Google
as an internal delay, not a rollout effect. Confirm the Pages report is still
producing fresh data points — and cross-check GA4, server logs and an independent
rank tracker — before calling an index-count change real (see measurement.md).

**Indexing services can only force a crawl.** Link and page indexers queue a
fetch; nothing in them touches the quality gate, so "guaranteed indexing" is a
sales claim (`FIELD`, Jul 2026). The free lever that beats them is one internal
link from a page Googlebot already crawls daily.

**On a domain with no trust yet, none of the levers fire.** A new domain given
the full indexing toolkit — a paid indexer, links from aged footers, hub pages on
free platforms, syndicated posts on social publishing sites — recorded no
indexing progress at all, while the same target keywords placed inside an article
on an established ranking domain were indexed immediately (`FIELD`, Aug 2026,
single practitioner cohort). Read alongside the row above: those tools force a
crawl, and the gate that follows is applied before inclusion. The audit
consequence is an expectation, not a task — on a young domain, set the
indexing timeline against earned trust and say so in the report, rather than
selling a technical fix that the evidence says will not move it.

**Removing `noindex` is not a recovery lever.** A sports site that bulk-noindexed
pages on AI advice went from 4–5k daily impressions to about 10; stripping the
tag changed nothing on its own, because Googlebot stops visiting noindexed URLs.
Recovery is manual: filter the GSC Pages report for `Excluded by 'noindex' tag`,
resubmit and relink in batches, and budget 6–12 weeks (`FIELD`, Jul 2026).

**Index tiering** (a 50k-page store went from 8k indexed / 2.1k junk to 9.8k
valuable URLs indexed, −87% zero-traffic pages, +67% organic in 90 days):

- Tier 1 must index: live products, key service pages, conversion core, brand and
  commercial pages.
- Tier 2 should index: supporting content, clusters, category pages.
- Tier 3 block: filter combinations, pagination, internal search results,
  archives, facet parameter combinations — **not** tracking parameters, which are
  a different case ("Tracking parameters are not facets" below).
- Tier 4 hard block: admin, cart, thin duplicates.

Score each template on business value, search value and user value; if all three
are low, it should not be in the index. Then track the tiering as a running
metric rather than a one-off clean-up: index coverage per tier, time-to-index for
new URLs, and drop-out rate, reviewed monthly (`FIELD` — same case).

**Crawl-budget killers**, in the order they usually bite:

1. Faceted navigation and parameter explosion (one category × filters = thousands
   of crawlable URLs).
2. Pagination explosion (`?page=847`) — cap it, consolidate with View-All where
   sensible, canonicalize empty pages.
3. Duplicate variants: session IDs, print versions, HTTP/HTTPS, www/non-www —
   plus tracking parameters, the one entry here that is usually already solved by
   a canonical. Read "Tracking parameters are not facets" below before spending a
   `robots.txt` line on them.
4. Mass low-quality pages that are **crawlable** — audit for: zero organic in 12
   months, no inbound links, <200 words, bounce >80% → 410 / consolidate /
   noindex / improve. Crawlable is the operative word: their content is fetched
   and processed, so it counts against host quality and spends budget. This is
   the opposite case to robots-**blocked**-but-indexed URLs, whose content is
   never processed and therefore cannot dilute anything (see A1 above and
   myths.md). Do not treat the two as one bucket, and never unblock the second
   group in order to "clean it up".
5. Server performance: past ~600ms crawl efficiency measurably degrades, and 5XX
   responses force re-requests that spend the same allowance twice. Thresholds
   (TTFB, error rate) are in benchmarks.md, "Operational benchmarks". Audit
   response time **per template** — this is the profile to capture, and it is
   owned here, not repeated elsewhere (a real one: 1.8s home, 2.2s category,
   7.4s product, 5.9s checkout). A single sitewide average hides exactly the
   template that is burning the allowance.

A sixth cause is adversarial rather than architectural — bulk fabricated URLs
pointed at your domain so the allowance is spent on 404s. Detect it from the log
status-code mix against a per-day 404 baseline (see threats-and-defense.md).

Log-file evidence beats opinion: one e-commerce audit found 40% of crawl going to
filter URLs while products were recrawled every 90 days; after robots and
parameter fixes product crawl rate rose ~4× and new products indexed in 2 days
instead of 3 weeks.

**Soft 404s are the silent killer.** Pages returning `200 OK` with no useful
content (empty filter results, "no products found", auto-generated converter
pages) drag host-level quality down and make Google abandon the site as a crawl
target. In one publisher network, 120k soft 404s correlated with crawl requests
falling from 60–70k/day to 20–30k/day; the fix stack (real 404/410, remove or
noindex auto-generated pages, tighten parameters, rewrite canonicals) cut them
83% — and the biggest recovery landed in **Discover**, not classic search. The
same network carried 513k "Crawled – currently not indexed" URLs in one country
alone, down 57% within weeks of the fix.
Pause Core Web Vitals work while indexing is broken; it is the wrong bottleneck.

**Faceted navigation, done properly:**

- **Facets** carry independent search demand (brand, color, material, audience)
  → clean crawlable URLs with self-referencing canonicals.
- **Filters** are convenience (price range, sort order, availability) → no URL
  change, or parameter URLs that are canonicalized/noindexed.
- `robots.txt` blocks crawling, not indexing: a blocked filter URL with any
  external link gets indexed on anchor text alone and can then never see your
  `noindex`. Match the tool to the problem — non-linkable markup blocks
  discovery, `robots.txt` blocks crawling, `noindex, follow` blocks indexing
  while equity still flows, canonicals only consolidate signals (a hint, not a
  directive).
- Promote proven parameter combinations to clean paths (`/shoes/?color=red` →
  301 → `/shoes/red/`) only after demand shows up in internal search logs or GSC.

**Tracking parameters are not facets (mechanism owned here).** `utm_*`, `gclid`,
`fbclid` and their kin create a duplicate URL that carries no independent demand,
so the entire job is consolidation — the case canonicals were built for. The
healthy state for a tracking URL is *crawled and not indexed*: that is the tag
working, not a leak. Three consequences:

- **Do not `Disallow` them.** A block cuts off a crawl Google is performing
  legitimately and cannot improve consolidation — a blocked URL never sees the
  canonical either (A1 above, myths.md). It also removes the only fix for the
  failure case below.
- **Price the platform's own duplicates first.** On hosted commerce the platform
  out-produces every tracking parameter: Shopify serves each product under
  `/collections/{collection}/products/{handle}` as well as the canonical
  `/products/{handle}`, and appends `?variant=` per variant — one product in five
  collections with six variants is dozens of crawlable strings before a single UTM
  exists (`CONFIRMED`, visible in any store's crawl). Size that before touching
  tracking params.
- **Confirm the scale before calling it a problem.** Group the GSC Pages report by
  reason: *Alternative page with proper canonical tag* on tracking URLs means
  consolidation is working and the finding is closed; *Duplicate without
  user-selected canonical* means the tag is not being honored, and that is the
  finding. Logs settle the share of crawl where they exist — tooling.md carries
  the rung-2 fallback for platforms that expose none.

**The one case that breaks the default.** Canonical is a hint, so Google can
select a different URL; the trigger practitioners report is signal weight — a
parameterized URL that accumulates more links and traffic than the clean one can
be chosen despite the tag (`CONFIRMED` that Google may override the declaration;
the link-accumulation trigger is `FIELD`). `robots.txt` is useless against it,
because it changes no signal. The lever sits one step up, at the source:

- Strip tracking parameters from **internal** links and from affiliate or partner
  placements you control. Those are yours to fix, and internal UTM also breaks
  session attribution (demand-and-conversion.md).
- Leave genuine third-party tracking URLs alone: newsletter, social and partner
  links copied and reshared in the wild are real referrals carrying real equity.
  Suppressing them costs attribution and link value and returns no crawl budget.

**Out-of-stock trap (mechanism owned here):** applying `noindex`/301/canonical
while a product is out of stock leaves the crawl scheduler holding a negative
priority on that URL *after* the directive is removed — the current HTTP status
does not reset it. Sitemap resubmission and manual GSC submissions do not break
it; Atom/RSS feeds jump the fast-discovery queue, and dynamic internal links
from high-crawl-frequency nodes help. Rendering an out-of-stock page with no
directives can trigger a soft 404 and the same deprioritization. The observed
duration is in benchmarks.md, the recovery horizon in measurement.md §J5, and
the play in growth-plays.md L9.

**Sitemaps** are a discovery and diagnostic tool, not a ranking factor. Include
only indexable, valuable, canonical URLs plus anything published in the last 24h;
exclude pagination, filters, redirects, noindexed and duplicate URLs. Compare
sitemap count to GSC indexed count and to a full crawl — the three-way diff finds
orphans and phantom URLs.

## B. Canonicalization and duplication

- **Self-referencing canonicals are the documented recommendation** (written into
  Google's documentation Jul 2026). Every indexable page should declare itself.
- **Canonical can also arrive as an HTTP `Link` header** — the only option for
  PDFs, images and feeds, and a common CDN or framework default. Check the header
  and the in-page tag together: when they disagree, Google resolves the conflict
  for you and you find out from URL Inspection, not from the template.
- **Extra attributes silently kill the tag.** `<link rel="canonical">` carrying
  `media`, `type`, `hreflang` or `lang` makes Google discard the declaration —
  URL Inspection then reports user-declared canonical `None`. Framework `data-*`
  attributes (`data-react-helmet`, `data-n-head`, `data-rh`, `id`, `class`) are
  harmless. CMS and framework templates inject these silently and most crawlers
  do not flag them. Re-check after every CMS/framework migration.
- **Edge-rendered HTML must carry the same canonicals** as the client-rendered
  version; a mismatch creates a fresh duplicate conflict.
- **`noindex` beats `canonical`.** `noindex` is a directive, canonical is a hint.
  A `meta refresh` redirect combined with `noindex` has no defined precedence:
  the page drops out and the canonical never passes equity. Replace with a
  server-side 301.
- **GSC's duplicate-content grouping keys mainly on slug, title and H1** — not
  body text. It is a serving-layer filter preventing SERP cannibalization, not a
  crawl-time demotion.
- **Recovery is slow by design:** pages can stay in a duplicate group for up to
  two weeks after the fix, and they split faster only when the difference is
  obvious and substantial (Google canonicalization troubleshooting docs, Jul
  2026).
- Chains and loops: `A→B→C` where `B→C` breaks; canonicals pointing at noindexed
  pages; HTTP/HTTPS mismatches. Crawl and diff. The cost is not only Google's: a
  canonical mismatch between two fetches of the same URL is one of the conditions
  that makes Brave's Web Discovery Project discard the page outright, which zeroes
  the signal feeding Claude's results (see aeo-geo.md).

### B2. hreflang and international duplication

Multi-locale sites are the duplication case canonicals cannot solve on their own:
the pages are near-identical by design, and the job is to tell the engine *which
audience gets which URL* rather than to collapse them. Everything in this
subsection is documented by the engines (`CONFIRMED`); no case data is claimed
for it.

**Mechanics**

- **Annotations must be bidirectional.** If A declares B, B must declare A. A
  one-way annotation is ignored — the return tag is what authenticates the claim.
- **Every page self-references.** Each URL lists itself in its own set, with its
  own language/region value.
- **`x-default`** names the fallback for users no other annotation matches
  (language selector, global landing page). Optional, but its absence is what
  leaves unmatched users on an arbitrary locale.
- **Language vs country targeting.** The value is `language` or
  `language-region` (ISO 639-1 language, ISO 3166-1 alpha-2 region), never
  region alone. `en` targets English speakers everywhere; `en-GB` targets
  English speakers in the UK. Do not invent `en-UK` or `pt-BR-x`.
- **One delivery mechanism per set, applied consistently:** HTML `<link>` tags,
  HTTP `Link` headers (the only option for non-HTML files), or the XML sitemap.
  Mixing them across a set is where sets silently break.
- **hreflang is not a canonical and not a ranking signal.** It selects which
  variant is *shown* to whom. Each locale still needs its own self-referencing
  canonical; a canonical pointing across locales removes the page the annotation
  was pointing at. And a canonical `<link>` carrying an `hreflang` attribute is
  discarded outright (see section B above).

**Audit checks**

| Check | Fail looks like | Where |
|---|---|---|
| Return tags complete | A→B present, B→A missing | crawl (hreflang report) |
| Self-reference present in every set | sets listing siblings only | crawl |
| Codes valid | `en-UK`, `zh-CN` used as a language, region-only values | crawl |
| Annotated URLs are indexable and 200 | annotations pointing at redirects, 404s, noindexed or canonicalized-away URLs | crawl + status check |
| Absolute URLs, correct protocol and host | relative hrefs, http in an https set, staging hosts leaking in | crawl |
| One mechanism per set | tags on some templates, sitemap entries on others, both disagreeing | crawl + sitemap diff |
| `x-default` declared where a fallback exists | no fallback for unmatched users | crawl |
| GSC International Targeting / locale-split performance | one locale absorbing another's queries | GSC + query→country breakdown |

**Common failure modes**

1. **Broken return tags at scale** — usually a template that emits the set from a
   translation table only some locales are in.
2. **Annotations to non-canonical or redirecting URLs** — the set points at URLs
   the engine has already replaced, so the whole set is discarded.
3. **hreflang used to fix duplication.** Two English pages for two countries with
   identical content still compete; hreflang routes users, it does not create
   distinctiveness. Differentiate the pages (currency, stock, shipping, legal,
   local proof) or consolidate them.
4. **Locale collision in the SERP** — the wrong-country page ranks because the
   set is incomplete on the winning template only. Verify per country with a
   country-scoped rank check, not from your own location.
5. **Auto-translated locales.** Bulk machine translation is a documented
   demotion profile after the May/June 2026 updates (threats-and-defense.md I1)
   — an intact hreflang set does not protect it. Audit translation quality per
   locale before blaming the annotations.
6. **Migration drift.** Locale URLs move and the sets are not rewritten. Add an
   hreflang re-crawl to the migration checklist below.

## Migrations (the most expensive failure mode)

The eight-stage protocol below is owned by this file; growth-plays.md B11 is the
play that points at it, and the loss figures (average, disciplined, documented
failure) are in benchmarks.md, "Operational benchmarks". Quote them from there
with the date.

1. **Baseline**: export every URL, snapshot rankings for the top 500 keywords,
   12-month traffic baseline, full backup.
2. **Map 1:1** old → new; **301, never 302**; test on staging; no chains.
3. **Preserve technicals**: titles, descriptions, schema, internal links, alt
   text, and every hreflang set (re-crawl them after the move — see B2); keep URL
   structure as close as possible.
4. **Move all content**; never silently delete pages; keep heading hierarchy.
5. **Pre-launch**: crawl staging, confirm `robots.txt` allows crawling, validate
   the sitemap, check CWV, validate schema, mobile, 404 audit.
6. **Launch day**: redirects live, internal links updated to the new URLs, new
   sitemap submitted, analytics tracking updated, watch server logs.
7. **Week 1**: crawl errors, redirect coverage, 404s fixed immediately, daily
   organic.
8. **Weeks 2–8**: rank recovery tracking, re-index requests for key pages,
   documented timeline.

Verification technique: one sheet pulling status code, title, description and
heading hierarchy from old and new URLs side by side reveals redirect failures in
bulk.

**Watch the old host, not only the new one.** A leaky redirect map leaves Google
crawling both. In a documented news-network move (Jan 2022, country domain →
regional subdomain) crawl budget split across the two hosts and trust never
consolidated: daily clicks sat at 2–4k against a 15–25k baseline for over a year,
and recovery began only once the *old* domain's indexing problems were resolved
seven months later (`FIELD`). Week-1 evidence: Googlebot hits on the old host
decaying in the logs, and no old URL still answering `200`.

**Change of address covers every variant.** Google's updated guidance (Jun 2026):
submit a change-of-address request for every subdomain and for the www/non-www
variants of the old domain, even ones you no longer use — all verified in Search
Console. An unannounced subdomain move leaves Google treating the destination as
new URLs and spending crawl budget on them even where they carry `noindex`.
Enumerate forgotten subdomains before agreeing a migration plan.

**Bulk 301s to the homepage burn equity.** Redirect each removed URL to the
closest-intent live page (product → comparable product; otherwise the parent
category). Removing a large section (e.g. 200k URLs of a 2M-page site) costs the
whole domain equity, topical relevance and trust — brief stakeholders that
sitewide performance dips, not only the removed pages.

**Images**: image rankings attach to the image object. Changing an image URL can
drop a product from position 1–3 past 50. Prefer a stable backend-proxied URL
(`/product/{id}/image`) serving the current file; serving `.webp` bytes at a
`.png` URL confuses crawlers over time — a plain 301 is safer.

## Sitemap protocol — the details that make one silently ignored

A sitemap that parses in your editor and fails at the engine is a common,
invisible defect: Search Console reports "couldn't fetch" or quietly indexes
nothing new, and the file looks fine.

**The namespace is part of the contract.** A urlset without it, or with a typo
in it, is not a sitemap:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9
                            http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">
```

An index file uses `<sitemapindex>` with the same namespace and the
`siteindex.xsd` schema. Mixing the two — `<urlset>` holding `<sitemap>`
children — parses as XML and means nothing.

**Five characters must be escaped in every URL**, and the one that actually
bites is `&` inside a query string, because a CMS emits it unescaped and the
whole file becomes invalid at the first product URL with two parameters:

| Character | Escape |
|---|---|
| `&` | `&amp;` |
| `'` | `&apos;` |
| `"` | `&quot;` |
| `>` | `&gt;` |
| `<` | `&lt;` |

**`lastmod` must be W3C Datetime**, and it must be true. `2026-08-06` and
`2026-08-06T14:30:00+00:00` are both valid; a US-format date is not, and a
`lastmod` that updates on every build regardless of content is worse than none —
it is the signal that gets a sitemap discounted, and nothing reports that it
happened.

**Limits:** 50,000 URLs and 50MB uncompressed per file; split into an index past
either. Gzip is accepted and the 50MB limit applies to the *uncompressed* size.

**Submission:** reference it from `robots.txt` with an absolute URL
(`Sitemap: https://example.com/sitemap.xml`) — that is the discovery path that
works for every engine, including the ones with no console. Cross-domain
submission requires the sitemap be reachable and the domains verified together.

**Alternative formats** are legal and rarely worth it: a plain text file of one
URL per line, or an RSS/Atom feed. Both drop `lastmod` semantics and priority.
Use them only when generating XML is genuinely not an option.

**Check it mechanically, not by eye:**

```bash
curl -s https://example.com/sitemap.xml | xmllint --noout -    # well-formed?
curl -s https://example.com/sitemap.xml | grep -c '<loc>'      # count vs expectation
curl -s https://example.com/sitemap.xml | grep -oE '<loc>[^<]*&[^a][^m][^p]' | head
# ^ unescaped ampersands: any hit is a parse failure waiting at the engine
```

## A7. The mechanical sweep (completeness list)

Run this after the diagnostic work, as a completeness pass. It catches the
boring failures that quietly cost traffic. Group results by category, record the
URL list behind every failure, and only promote an item into the findings table
when it has an observable impact.

**Availability and access**
- Site and key pages respond (no timeouts); if a tool reports a timeout, verify
  in a browser before reporting — it may need allow-listing.
- Property verified in Search Console (all variants).
- Key templates are indexed (URL Inspection / crawl comparison).
- `robots.txt` does not block anything that must be crawled or rendered.
- Each template returns the status code it should. The mirror image of a soft 404
  is just as costly: a page that renders correctly for users while the header
  says `404`/`410`, which removes it from the index silently.

**Sitemaps**
- Submitted in Search Console and referenced from `robots.txt`.
- Contains only valid, canonical, indexable URLs that return 200.
- Does not contain URLs you deliberately keep out of the index.
- Under 50MB / 50,000 URLs per file.

**Crawl optimization**
- Meta directives set deliberately per template — and the header-level ones too
  (`X-Robots-Tag`, `Link: rel="canonical"`), including on PDFs and images.
- Pagination / load-more / infinite scroll implemented crawlably (`rel=next|prev`
  is no longer supported — do not "fix" it back in).
- Faceted URLs are noindexed or isolated (facets vs filters, see above).
- JavaScript renders for Googlebot; no console errors blocking content.
- Important content is not inside iframes or dead embeds.
- Same content served to all user agents (no cloaking); mobile URLs serve the
  right content regardless of device.
- Status codes verified with a **mobile** user agent, not only the desktop
  default — mobile-first means a desktop-only 404 or 410 is not the response
  being read (A1).
- hreflang sets complete and reciprocal on every localized template, pointing at
  indexable 200 URLs, one mechanism per set (see B2).
- Removed pages return 404/410 rather than soft 200s; valuable removed URLs are
  redirected to the closest intent.
- Internal links resolve 200; no redirect chains (keep any chain under a handful
  of hops); no JS or meta-refresh redirects standing in for server-side 301s.

**Performance**
- CWV (LCP, INP, CLS, FCP) green on field data, per template and per device.
- No mixed content; HTTP/2+; compression, caching and minification in place.
- External requests bounded and non-blocking; no timing-out third parties.
- Images: correct format, compressed, responsive, lazy-loaded below the fold,
  never lazy for the LCP element; no broken images.

**Accessibility** (users first; several items also affect crawlability)
- Content available without JavaScript; ARIA landmarks; skip-to-content link.
- Mobile-friendly, tap targets spaced, keyboard navigable.
- Captions and transcripts for audio/video, plus user-accessible controls.
- No strobing content; auto-scroll can be stopped; zoom works.
- `lang` declared; form errors describe what is wrong; contrast meets WCAG.

**Risk**
- No hack indicators; no cloaked content; no keyword stuffing.
- Backlink profile reviewed against the niche baseline
  (threats-and-defense.md I6).
- Structured data used honestly — markup matching visible content, no
  unsupported claims (technical-checks.md B, onpage-checks.md O1).

## Evidence to capture for tracks A/B

- `robots.txt` (full text + date), a diffed crawl (respecting vs ignoring it).
- GSC Pages report counts per status, per template, with dates.
- URL Inspection screenshots/output for one URL per template: indexed status,
  user-declared vs Google-selected canonical, crawl date, rendering.
- Raw source vs rendered DOM for one URL per template (robots meta, canonical,
  content parity).
- hreflang export for every localized template: URL, declared set, return-tag
  status, target status code (B2).
- Response headers for one URL per template and one per non-HTML asset type
  (`X-Robots-Tag`, `Link: rel="canonical"`, status, cache), captured with a bot
  user agent as well as a browser one.
- Server-log summary: bot, status code, path bucket, count, per day.
