# Tracks A & B — access, indexation economics, canonicalization

Everything here is a check you run and record, not advice you repeat. Capture the
observed value and the date for each.

## A0. Blockers first (stop the audit if any is true)

| Check | How | Blocker if |
|---|---|---|
| Manual action | GSC → Security & Manual actions | Any action present. It is a **binary multiplier** — nothing else you improve counts until it is lifted. Fix everything, *then* file reconsideration; premature requests get rejected and the improvements shipped meanwhile are not re-evaluated. |
| Sitewide `noindex` / auth wall | fetch the raw HTML (`view-source`, not the browser DOM) | `noindex` present in the **pre-render source** even if the rendered DOM is clean — Google honours the tag if it appears in *either* version, and GSC shows you neither the pre-render source nor the conflict. |
| Robots-blocked site or key section | `robots.txt` + GSC robots tester | Money paths disallowed. |
| Deindexation event | GSC Pages report + `site:` + log traffic | Sudden index loss → jump to [threats-and-defense.md](threats-and-defense.md) (hijack, DMCA, spam action). |
| DNS / property coverage | GSC properties list | Only the canonical variant is verified. Verify **all**: domain property, https www, https non-www, http, and key directories. A domain property aggregates protocols and subdomains — it is where a hijacked `www` shows up as an anomalous click spike. |

**Look for spikes, not only drops.** A one-day burst of clicks on one URL for
off-topic queries is the classic signature of a subdomain takeover; deindexation
can precede the manual action by 24h+.

## A1. Crawl access and rendering

- **Blocked resources break rendering.** Anything disallowed in `robots.txt` is
  never downloaded, therefore never rendered. Blocking a framework path (e.g.
  `/_next`) breaks layout and links for Googlebot; allowing `/_next/static/` and
  `/_next/image` restores indexing. Verify with GSC URL Inspection / Rich Results
  Test, DevTools request-blocking, or a robots-aware rendering proxy — **not**
  your browser.
- **Wildcards match substrings, not paths.** `Disallow: /*?` blocks every
  parameterised URL behind it (one store lost ~40% of product pages from the
  index; a retailer lost 45% of traffic and needed six weeks just to diagnose).
  `Disallow: /*print` also blocks `/blueprints/`, `/footprint/`, `/imprint/`;
  `Disallow: /account/` also catches `/account-settings/`.
  Validate by crawling twice (respecting vs ignoring robots.txt) and diffing the
  URL sets — every URL that disappears is a page the file hides from Google.
  Keep `robots.txt` in version control with a dated changelog; audit quarterly.
- **Never cloak with a Googlebot-specific `Disallow: /`.** It hides nothing and
  reads as deception.
- **`<meta name="robots" content="none">` ≡ `noindex, nofollow`.** Several SEO
  extensions parse it wrong — check the raw source, not a plugin.
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
- **AI crawlers are separate user agents.** `OAI-SearchBot` (ChatGPT retrieval)
  is not `GPTBot` (training); unblocking one does nothing for the other. A
  robots-blocked page returns `viewing lines [0-0] of 0` to ChatGPT Deep Research
  and silently vanishes from the report. Verify from logs with
  forward-confirmed reverse DNS — a crawler hit only proves the URL was fetched,
  never that a model learned it.

## A2. Indexation economics

Treat the index as a scarce resource: Google raises the quality bar when it hits
capacity, so every new page competes for a finite slot (patent *Managing URLs*,
US7509315B1). Publishing more pages dilutes unless demand grows with them.

**Split the two GSC exclusion diagnoses — they need opposite fixes:**

| Status | Meaning | Fix path |
|---|---|---|
| Discovered – currently not indexed | Crawl budget/priority exhausted | Importance signals: contextual internal links from your most-crawled pages, a priority sitemap with fresh `lastmod`, one external dofollow link from an indexed page, clean server signals (TTFB <200ms, no 5XX, no redirect chains). 70–80% index within 72h in field reports. |
| Crawled – currently not indexed | Fetched and **rejected** on quality | Discovery signals will not help. Step back to page and sitewide quality: unique value, intent match, thin/duplicate clean-up. John Mueller: when systems doubt sitewide quality they crawl less and index less — that is not a technical bug to patch. |

**Index tiering** (a 50k-page store went from 8k indexed / 2.1k junk to 9.8k
valuable URLs indexed, −87% zero-traffic pages, +67% organic in 90 days):

- Tier 1 must index: live products, key service pages, conversion core, brand and
  commercial pages.
- Tier 2 should index: supporting content, clusters, category pages.
- Tier 3 block: filter combinations, pagination, internal search results,
  archives, parameter variants.
- Tier 4 hard block: admin, cart, thin duplicates.

Score each template on business value, search value and user value; if all three
are low, it should not be in the index.

**Crawl-budget killers**, in the order they usually bite:

1. Faceted navigation and parameter explosion (one category × filters = thousands
   of crawlable URLs).
2. Pagination explosion (`?page=847`) — cap it, consolidate with View-All where
   sensible, canonicalise empty pages.
3. Duplicate variants: session IDs, tracking params, print versions, HTTP/HTTPS,
   www/non-www.
4. Mass low-quality pages — audit for: zero organic in 12 months, no inbound
   links, <200 words, bounce >80% → 410 / consolidate / noindex / improve.
5. Server performance: TTFB <200ms optimal, <500ms acceptable; error rate <0.5%.
   Audit response time **per template** (a real profile: 1.8s home, 2.2s
   category, 7.4s product, 5.9s checkout).

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
83% — and the biggest recovery landed in **Discover**, not classic search.
Pause Core Web Vitals work while indexing is broken; it is the wrong bottleneck.

**Faceted navigation, done properly:**

- **Facets** carry independent search demand (brand, colour, material, audience)
  → clean crawlable URLs with self-referencing canonicals.
- **Filters** are convenience (price range, sort order, availability) → no URL
  change, or parameter URLs that are canonicalised/noindexed.
- `robots.txt` blocks crawling, not indexing: a blocked filter URL with any
  external link gets indexed on anchor text alone and can then never see your
  `noindex`. Match the tool to the problem — non-linkable markup blocks
  discovery, `robots.txt` blocks crawling, `noindex, follow` blocks indexing
  while equity still flows, canonicals only consolidate signals (a hint, not a
  directive).
- Promote proven parameter combinations to clean paths (`/shoes/?color=red` →
  301 → `/shoes/red/`) only after demand shows up in internal search logs or GSC.

**Out-of-stock trap:** applying `noindex`/301/canonical while a product is out of
stock makes the crawl scheduler deprioritise that URL for 100+ days *after* the
directive is removed. Sitemap resubmission and manual GSC submissions do not
break it; Atom/RSS feeds jump the fast-discovery queue, and dynamic internal
links from high-crawl-frequency nodes help. Rendering an out-of-stock page with
no directives can trigger a soft 404 and the same deprioritisation.

**Sitemaps** are a discovery and diagnostic tool, not a ranking factor. Include
only indexable, valuable, canonical URLs plus anything published in the last 24h;
exclude pagination, filters, redirects, noindexed and duplicate URLs. Compare
sitemap count to GSC indexed count and to a full crawl — the three-way diff finds
orphans and phantom URLs.

## B. Canonicalisation and duplication

- **Self-referencing canonicals are the documented recommendation.** Every
  indexable page should declare itself.
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
  body text. It is a serving-layer filter preventing SERP cannibalisation, not a
  crawl-time demotion.
- **Recovery is slow by design:** pages can stay in a duplicate group for up to
  two weeks after the fix, and they split faster only when the difference is
  obvious and substantial.
- Chains and loops: `A→B→C` where `B→C` breaks; canonicals pointing at noindexed
  pages; HTTP/HTTPS mismatches. Crawl and diff.

## Migrations (the most expensive failure mode)

Average migration loses ~30% of traffic; a disciplined protocol keeps it near 8%.
Documented failure: 67% traffic lost, −340 positions, −73% revenue, six months to
partial recovery.

1. **Baseline**: export every URL, snapshot rankings for the top 500 keywords,
   12-month traffic baseline, full backup.
2. **Map 1:1** old → new; **301, never 302**; test on staging; no chains.
3. **Preserve technicals**: titles, descriptions, schema, internal links, alt
   text; keep URL structure as close as possible.
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

**Change of address covers every variant.** Google's updated guidance: submit a
change-of-address request for every subdomain and for the www/non-www variants of
the old domain, even ones you no longer use — all verified in Search Console.
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

## Evidence to capture for tracks A/B

- `robots.txt` (full text + date), a diffed crawl (respecting vs ignoring it).
- GSC Pages report counts per status, per template, with dates.
- URL Inspection screenshots/output for one URL per template: indexed status,
  user-declared vs Google-selected canonical, crawl date, rendering.
- Raw source vs rendered DOM for one URL per template (robots meta, canonical,
  content parity).
- Server-log summary: bot, status code, path bucket, count, per day.
