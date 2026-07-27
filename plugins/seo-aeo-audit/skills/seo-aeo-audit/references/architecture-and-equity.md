# Track C — architecture, internal links and equity distribution

## The default failure

On most sites the homepage holds ~80% of link equity and the money pages get
almost nothing: backlinks land on the entry point and never reach the revenue
generators. Equity flows through internal links by four properties — number of
links on the source page (dilution), position in the source order (higher =
stronger), contextual relevance, and the authority of the source page.

PageRank decays roughly 85% per hop, so anything more than three clicks from a
strong node keeps almost nothing. That is why large catalogues plateau around
partial index coverage regardless of content quality: authority is a
**prerequisite filter**, and identical content that will not index on a weak site
often indexes immediately on a strong one.

## The audit

1. **Equity map.** Crawl the site and pull internal link counts, inbound internal
   links per URL, click depth from the homepage, and (in Screaming Frog or
   equivalent) internal PageRank. Overlay backlink data. Answer: which pages
   receive the most internal authority, and are they the pages that make money?
2. **Targets.** Commercial keywords, revenue pages, and URLs sitting at positions
   11–30 — the cheapest opportunity band.
3. **Depth.** Key templates within 1–2 clicks of the homepage; nothing important
   deeper than 3.
4. **Orphans.** Diff a full crawl against the sitemap and against GSC's indexed
   URL list. Orphans rank badly and eventually deindex; deep pages need at least
   one click a week to hold their index slot.
5. **Leaks.** Links into pagination, tag archives, author bios, calendars,
   internal search results, and filter combinations; bloated footers; 50+ item
   menus; broken internal links; redirect chains; `nofollow` on important
   internal links.
6. **Anchors.** Descriptive, topically-consistent internal anchors between
   related pages beat "click here" and beat generic navigation text. Internal
   anchor text is a stronger topical-authority signal than most teams assume.
7. **Hub integrity.** Pillar → cluster → pillar loops closed? Every new article
   receiving 3–5 internal links from existing indexed pages?

## Read-budget: navigation now costs you twice

Classic crawl budget is not the only tax. ChatGPT **Deep Research** reads raw
HTML linearly, top to bottom (drops `<head>`, ignores JavaScript), with a first
read capped at ~5,700 characters (median; max ~8,000). Every link renders inline
as a marker that consumes the same budget:

| Links on page | Share of the first read that is your content |
|---|---|
| < 20 | ~78% |
| 20–59 | ~55% |
| 60+ | ~33% |

It never clicks (so "skip to main content" does nothing), and it uses only
`search` (Bing snippets), `open` and `find` (Ctrl+F). A successful `find`
triggers a re-read at the matched line ~95% of the time — **literal presence of
the term buys a second read**. `alt` attributes render as plain text and are the
only thing read from images (`alt=""` is skipped as decorative).

Consequence: **source order matters more than visual position**. A mega-menu that
CSS paints at the top but that sits at the end of the source costs nothing; an
answer buried below a large navigation block may never enter the first read.

Documented case: a site with ~1,000 sitewide links at the top of every page cut
~90% of them (sitewide nav = top categories only; subcategories appear on their
own category pages, visible to users and crawlers, nothing hidden) and rankings
improved in **both Google and ChatGPT**. Offset the added click depth with an
HTML sitemap and external links so discovery does not regress.

Two pages with identical link counts can extract very differently depending on
where the navigation sits in the DOM — measure survival inside the read budget
directly (`scripts/page_audit.py` estimates it) instead of inferring it from a
link count.

## The fixes, in the order that usually pays

1. **Link from the homepage to the money pages.** A strong page → a priority
   target is the highest-leverage single link on the site; a random DR-15 blog
   post → the pricing page is close to worthless.
2. **Hub-and-cluster.** One pillar page per topic linking to 10–15 cluster pages,
   each linking back; adjacent clusters linked to each other. Case: a new
   email-deliverability site reached 47 top rankings and 0 → 12k organic visits
   in six months on this structure alone.
3. **Contextual links from traffic-earning posts** into commercial URLs; body
   links and hub links transmit signal, footer/author-bio/comment links transmit
   far less.
4. **Comparison and solution hubs** that link to every product page — the SaaS
   case that lifted product pages an average of 12 positions and +$340K organic
   revenue in 90 days.
5. **Breadcrumbs** for hierarchical flow; footer links only for genuinely key
   categories.
6. **Chapter-style child pages** with self-contained H1s under a parent path —
   the pattern that earned sitelinks for a *category* page, which Google normally
   reserves for homepages. Clear structural paths beat clever architecture.
7. **HTML sitemaps as meaning bridges**: surround internal links with descriptive
   relevant text so the crawler reads topical association, not just a URL list.
8. **Re-link old posts** to new priority pages when you publish; continuous
   internal-link flow compounds.

## Internal-link anchor mix

Internal anchors should be descriptive and consistent, not artificially varied.
For **external** anchors, a natural-looking distribution as observed in field
work: branded 40–50%, naked URL 20–30%, generic 15–25%, partial match 10–15%,
exact match 5–10%, with a 30–50% nofollow share and a home-market-weighted geo
mix. Spiky, event-driven acquisition (launches, PR) reads as natural; flat linear
growth does not. 500 links in 30 days triggered penalties within 48h in one
report; 370 over 8 months ranked top-3.

## What to record

- Equity map export (URL, inbound internal links, depth, internal PageRank,
  referring domains, current position, revenue).
- The orphan list with the reason each page is orphaned.
- A per-template link count and read-budget estimate.
- Before/after link counts for any navigation change, plus the discovery
  compensation you added.
