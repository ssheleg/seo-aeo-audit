# Tracks D & E — the on-page completeness sweep

The judgement calls live in intent-and-content.md. This file is the mechanical
sweep: run it per template (not per page), record the URL list behind every
failure, and feed the results into the findings table.

`scripts/page_audit.py` automates the starred (★) items for a sample URL.

Tiering: a failed check here is an observation on this site, so it enters the
report as `CONFIRMED` for *existence*. The claimed *impact* of fixing it keeps
whatever tier the underlying mechanism has (see evidence-tiers.md) — "the H1 is
missing" is confirmed; "fixing the H1 will add traffic" is not.

## D1. Can crawlers understand what the page is about

| Check | Fail looks like | Where |
|---|---|---|
| Canonical version of the site declared and consistent ★ | http/https and www/non-www both resolve 200; conflicting declarations | crawl + GSC |
| Title tag present, unique, descriptive ★ | missing, duplicated across templates, multiple `<title>` elements, truncated mid-word | crawl (Screaming Frog / Ahrefs / Semrush) |
| H1 present, single, matching the page's subject ★ | missing, duplicated sitewide, several H1s, H1 that repeats the nav | crawl + page_audit |
| H2–H4 structure reflects the content ★ | 0–3 subheads on a long page; headings used for styling; questions never mirrored | crawl + page_audit |
| One page per query cluster | several pages ranking for the same query (see cannibalization, intent-and-content.md D2) | GSC query→page breakdown |
| URL structure readable and stable | parameters where paths belong, dates in evergreen URLs, year suffixes | crawl |
| Image file names descriptive | `IMG_2043.jpg` on product pages | crawl |
| Image `alt` present and factual ★ | missing alt on informative images; keyword-stuffed alt; decorative images with text alt | crawl + page_audit |
| Structured data valid and matched to visible content ★ | validation errors; markup claiming ratings/prices the page does not show | Rich Results Test + page_audit |

On schema, hold the canonical stance from myths.md: mark up what is real and
required for the features you actually want (products, jobs, events,
breadcrumbs) — validity is hygiene, volume is not a lever.

## D2. Duplication and consolidation

| Check | Fail looks like | Where |
|---|---|---|
| Copy is original, not scraped or spun | large blocks matching supplier or competitor text | plagiarism check |
| HTTP → HTTPS enforced | mixed versions indexed | crawl |
| URL variants normalised (parameters, trailing slash, case, tracking) | the same page indexed under many strings | crawl + GSC |
| Canonicals used to consolidate near-duplicates ★ | duplicates with self-canonicals; canonical chains; canonical to a noindexed page | crawl + URL Inspection |
| Other domains/subdomains not duplicating the content | staging, print, regional mirrors in the index | `site:` + crawl |

## D3. Internal linking on the page

| Check | Fail looks like | Where |
|---|---|---|
| Important internal links are crawlable `<a href>` | JS-only navigation, `span`/`onclick` links | crawl + rendered DOM |
| No `nofollow` on internal links you want to pass equity | legacy sculpting attributes | crawl |
| Internal linking reflects priority | money pages linked once from a footer; nav links to everything equally | equity map |
| Key content within a few clicks of the homepage | depth 5+ on revenue pages | crawl |
| Link volume per page kept sane ★ | hundreds of links on every template; navigation ahead of content in source order | crawl + page_audit read budget |

## E1. Content substance (judgement, evidence required)

| Check | What good looks like | Reference |
|---|---|---|
| The page answers the query it targets in its opening | answer in the first ~100 words, one claim per sentence | aeo-geo.md F3 |
| The format matches what the SERP rewards | comparison for commercial intent, PDP for transactional, guide for informational | intent-and-content.md D1 |
| Unique data on the page | original measurements, internal analytics, tests; 15+ unique numbers correlates with the top of the information-gain scale | intent-and-content.md E2 |
| Questions the top-3 leave unanswered are answered here | in 90% of SERPs at least one is missing | intent-and-content.md E2 |
| Demonstrated first-hand experience | original photos, walkthroughs, named author with credentials, transparent method | ranking-model.md |
| The page completes the task | calculator, comparison, spec table, availability, booking | intent-and-content.md E1 |
| Decision-accelerator elements present where the intent is commercial | transparent pricing table in plain HTML, implementation timeline, integration guide, ROI calculator, industry case study | demand-and-conversion.md |
| No AI-slop signature | generic phrasing, no evidence, no author, templated structure across dozens of pages | intent-and-content.md E4 |

## E2. Metadata as a click and citation surface

- Titles and descriptions written for the searcher, not the crawler; test rather
  than assume (experiments.md documents year-in-title, capitalization and
  promo-copy results, all market-specific).
- Do not chase featured-snippet formatting for its own sake; check first whether
  the query even returns one, and whether owning it costs the click.
- Exact-match keyword phrasing appears in a small minority of AI Overviews —
  write in plain, accessible language and let the entity and topic coverage do
  the work.

## How to record it

For each failed check: the template, the number of affected URLs, a sample of
five URLs, the observed value, the fix, the effort, and the evidence tier. A
count without a URL list is not evidence.
