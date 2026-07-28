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

Two boundaries on this track. PageRank is **not used in Local Search at all**
(reported in SEJ, *Google Ranking Factors: The 3 That Really Matter* — FIELD), so
equity engineering does not move the map pack; see "Local and multi-location
architecture" below. And answer engines do not rebuild a deep link graph at
retrieval time — running PageRank over one is too expensive per query, so they
lean on document volume and corroboration instead (practitioner analysis reported
2026-05-20 — HYPOTHESIS). The fabricated-consensus tactic built on that
observation is detection material in threats-and-defense.md, never a
recommendation. Internal equity is a Google and Bing lever; the architecture
lever that reaches answer engines is read budget, below.

The track is underpriced by the people who own it: in SEJ's State of SEO 2026,
internal linking was named a top-three highest-impact activity by **22.9%** of
respondents against 66.3% for original content and 42.3% for technical work
(STUDY — self-reported, "select up to 3", opinion rather than measured effect).
It is the cheapest lever in this file and the one least likely to already be
taken.

## The audit

1. **Equity map.** Crawl the site and pull internal link counts, inbound internal
   links per URL, click depth from the homepage, and (in Screaming Frog or
   equivalent) internal PageRank. Overlay backlink data. Answer: which pages
   receive the most internal authority, and are they the pages that make money?
2. **Targets.** Commercial keywords, revenue pages, and URLs sitting at positions
   11–30 — the cheapest opportunity band. Check the floor as well: click systems
   only engage once a URL is in play, and a page parked past roughly position 70
   collects no click signal and no navigational bonus, so links alone will not
   lift it (leak reading, 2026-05-18 — FIELD). Below that line the page is the
   problem, not the plumbing.
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
8. **Crawl frequency.** Group log fetches per URL per week by template and
   compare priority pages against filters, pagination and archives. A money page
   refetched every third day while a filter path is hit hourly is an architecture
   finding, not a server finding — see the next section.
9. **Hub link budget.** Count actual out-links per hub and back-links per cluster
   page against the targets in fix 9. A page that links to 60 others is a menu,
   not a hub.

## Crawl frequency is an architecture output

Crawl priority follows internal structure; it is not a setting you can request.
The rules that hold up in field work (FIELD, 2026-06-11):

- Priority pages within 3 clicks of the homepage, with **more than one** inbound
  link from a strong page.
- New content linked from URLs the bot fetched recently, not from the archive.
- Deep pages need a path from a hub that is itself crawled often.
- Orphans are skipped entirely — the bot never arrives, so nothing else about
  the page matters.

Documented profile from one crawl-waste cleanup: total budget unchanged at
~10,000 fetches/day, waste 40% → 10%, priority pages moved from a refetch every
2–3 days to daily, and priority-page rankings roughly 4× (FIELD, 2026-06-11).
Note what did not change: the budget. The whole gain came from where the links
pointed.

The fastest single lever on a URL stuck in "Discovered – currently not indexed"
is a contextual **body** link from your most-crawled pages: export GSC Top Pages,
link from inside their content, and indexing often lands in **24–48 hours**
(FIELD, 2026-07-09). Placement decides — body and hub links transmit, footer,
author-bio and comment links transmit far less. The full 72-hour protocol and the
opposite diagnosis ("Crawled – currently not indexed") live in
technical-checks.md; the two statuses need opposite fixes, so never treat them as
one bucket.

One live disagreement, to be tested rather than believed: the engine-side reading
of "Crawled – currently not indexed" is a **quality rejection**
(technical-checks.md, quoting Mueller), while a competing practitioner account
calls it almost purely an **authority deficit** (FIELD, 2026-06-18), arguing from
the fact that identical content indexes instantly on a strong domain. Both files
record both readings and neither picks a winner — the cause is **HYPOTHESIS**.
**Discriminating experiment** (referenced from technical-checks.md, owned here):
hold content constant, add links from strong nodes to one cohort, leave a matched
cohort alone, measure index rate. Run it per experiments.md — do not rewrite 500
pages on either theory. Note what does *not* depend on the outcome: discovery-side
pushes are the wrong fix under either reading.

Two structural details from the same account (FIELD, 2026-06-18):

- Googlebot leans on **subfolder membership and directory nesting** to read
  hierarchy, not on the visual navigation menu. The URL path is structure, not
  cosmetics — which matches the leaked `patternLevel` finding that signals
  aggregate at URL, directory and subdomain level (experience-signals.md). Put a
  page in the directory whose reputation you want it to inherit.
- Index coverage around **42%** is normal even at Amazon/eBay scale. On a large
  catalogue, full coverage is not the target; coverage of the URLs that earn is.

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

On this surface navigation buys nothing back. Because no link graph is
recomputed at retrieval time, the internal links an answer engine reads are pure
cost: they spend budget and return no equity (HYPOTHESIS). In Google the same
mega-menu at least distributes PageRank; in ChatGPT it only crowds out your
answer. Deep Research also never opens `.md` links even when they are internally
linked (FIELD, 2026-06-29), so an internal link to a Markdown mirror is budget
spent on a page that will never be read — see myths.md.

Corroborating, weakly, on the Google side: a controlled SEO A/B test cut a
category template from 48 listed products to 36 with everything else held
constant — design, navigation, filters, schema and internal linking unchanged —
and measured a positive shift at **85%** confidence (FIELD, 2026-06-23). That is
below the 95% bar, so it is direction, not proof. Fewer links per listing page is
worth testing on your own template; it is not worth shipping sitewide on this
evidence.

## The fixes, in the order that usually pays

1. **Link from the homepage to the money pages.** A strong page → a priority
   target is the highest-leverage single link on the site; a random DR-15 blog
   post → the pricing page is close to worthless.
2. **Hub-and-cluster.** One pillar page per topic, a cluster of **10–15 pages**
   under it, each linking back to the pillar; adjacent clusters linked to each
   other. Case: a new email-deliverability site reached 47 top rankings and
   0 → 12k organic visits in six months on this structure alone. **Cluster size
   is not the hub's link budget** — see fix 9 for how many of those links the
   hub body carries at once.
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
   internal-link flow compounds. Those edits also register as a real content
   update — the page diff counts anchor, target and surrounding-text changes —
   but only inside content: navigation and boilerplate link changes are filtered
   out (myths.md).
9. **Give every hub a link budget.** The two numbers in this file measure
   different objects and both stand: **a cluster holds 10–15 pages** (fix 2 — a
   content-planning unit), while **the hub's body carries 5–10 contextual links
   out at a time** (FIELD, 2026-06-11 — a per-page budget). The reconciliation,
   and the recommendation to give: build the cluster to 10–15 pages, but do not
   put all of them in the hub's body. Reason — each additional link both dilutes
   the equity the hub passes and consumes the answer-engine read budget in the
   same move (see "Read-budget" above), so past ~10 the marginal link costs more
   than it returns. Route the surplus through **sub-hubs** (split a 15-page
   cluster into two sub-topics with their own hubs) or through **sibling links
   between cluster pages**, and if every page must be reachable from the hub,
   put the remainder in a listing block *after* the body copy in source order,
   never before it. Around it: 3–5 links back from each cluster page, nothing
   important deeper than 3 clicks (FIELD, 2026-06-11), and 3–5 links to priority
   pages inside every new article (FIELD, 2026-04-30).
10. **Front-load the cluster release.** Ship the hub plus ~5 clusters first, the
    supporting articles after (FIELD, 2026-05-07), so early pages have somewhere
    to receive links from. Publishing the long tail before its hub orphans it by
    default.

## Local and multi-location architecture

PageRank is not used in Local Search, so none of the equity work above moves the
map pack. Internal structure still earns its keep locally in two ways:

- **Mesh the pages.** Geo mesh — each city page links to its neighbors; topic
  mesh — each city page links up to the state or region page and across to the
  service category. On programmatic location pages make this a **pre-publish
  gate**, alongside no unfilled template variables, a hard word-count floor (800
  in the documented gate), valid markup, and a duplicate check against existing
  pages (FIELD, 2026-07-09).
- **Go deep, not wide.** Fresh sites carrying ~40 district-and-service pages have
  displaced DR 70+ aggregators in local packs, because breadth-first aggregators
  hold no local depth (FIELD, 2026-05-07). 500 substantive pages beat 5,000 thin
  ones — and 5,000 thin ones are what trips the filter the architecture exists to
  avoid.

## Internal-link anchor mix

Internal anchors should be descriptive and consistent, not artificially varied.

**External** anchor distribution and link velocity are a link-risk question, not
an architecture one: the distribution bands, the velocity thresholds and the
niche-relative reading of "toxic" live in threats-and-defense.md I6, and the
acquisition play is growth-plays.md P8. Do not restate them here — the only
architectural point is that internal and external anchors follow opposite rules,
because internal anchors are not a spam-risk surface.

A competing framework prescribes a distribution for **internal** anchors as well
— exact 10%, partial 30%, branded 20%, generic 20%, naked URL 20% (2026-04-30).
It contradicts the descriptive-and-consistent rule above, so by the conflict rule
in evidence-tiers.md the claim drops to **HYPOTHESIS** and belongs on the
experiment list, not in a plan. The mechanism gap to state when asked: internal
anchors are not a spam-risk surface the way external ones are, and 40% of them
spent on "check this out" and bare URLs buys no topical signal at all.

## What to test rather than ship

Architecture is one of the few tracks where a clean SEO split test is available,
because the change is template-level and the control is a matched page cohort.
From one sequential test program (FIELD, 2026-05-01): a change of internal-linking
scheme returned **+18%** in its month, inside a run where title work returned
+34% and content restructuring +22%. Variables that tested cleanly there include
internal links per page (3 vs 7) and, separately, listing size per category page
(48 vs 36, above).

Test hygiene this track keeps failing: cohorts under 30 pages, runs under 3
weeks, more than one variable at a time, no significance check, and the one that
voids everything — a run overlapping an update rollout. Date-align against
algorithm-updates.md before believing a result, and design per experiments.md.

## What to record

- Equity map export (URL, inbound internal links, depth, internal PageRank,
  referring domains, current position, revenue).
- The orphan list with the reason each page is orphaned.
- A per-template link count and read-budget estimate.
- Before/after link counts for any navigation change, plus the discovery
  compensation you added.
- Crawl frequency per template from the logs: fetches per URL per week, and the
  share of total fetches landing on priority pages versus filters, pagination and
  archives.
- Per-hub link budget: out-links, back-links per cluster page, click depth.
- The quarterly re-measure — internal PageRank distribution, authority
  concentration versus spread, target-page positions, organic by index tier, and
  a fresh orphan diff. Internal linking rots as a site ships; treat the equity map
  as a recurring measurement, not a one-off deliverable.
