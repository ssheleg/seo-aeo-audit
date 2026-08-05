# Tracks D & E — the on-page completeness sweep

The judgement calls live in intent-and-content.md. This file is the mechanical
sweep: run it per template (not per page), record the URL list behind every
failure, and feed the results into the findings table.

`scripts/page_audit.py` automates the starred (★) items for a sample URL.

Tiering: a failed check here is an observation on this site, so it enters the
report as `CONFIRMED` for *existence*. The claimed *impact* of fixing it keeps
whatever tier the underlying mechanism has (see evidence-tiers.md) — "the H1 is
missing" is confirmed; "fixing the H1 will add traffic" is not.

**Sweep the money templates first.** Across 10,937 pages already being run
through on-page tooling, category and landing templates scored worst (median
33.6/100 on the vendor's rubric, whose stated practical threshold is ~80), with
the highest rate of an H1 that never names the subject (69.4%) and the highest
share of copy too thin for the SERP it competes in (68.6%) — the templates
closest to revenue are usually the least finished (STUDY, self-selected sample
of optimization-conscious sites, 2026-07-14). Everything else gets swept second.

## D1. Can crawlers understand what the page is about

| Check | Fail looks like | Where |
|---|---|---|
| Canonical version of the site declared and consistent ★ | http/https and www/non-www both resolve 200; conflicting declarations | crawl + GSC |
| Title tag present, unique, descriptive ★ | missing, duplicated across templates, multiple `<title>` elements, truncated mid-word | crawl (Screaming Frog / Ahrefs / Semrush) |
| H1 present and matching the page's subject ★ | missing, duplicated sitewide, H1 that repeats the nav | crawl + page_audit |
| H2–H4 structure reflects the content ★ | 0–3 subheads on a long page; headings used for styling; questions never mirrored | crawl + page_audit |
| One page per query cluster | several pages ranking for the same query (see cannibalization, intent-and-content.md D2) | GSC query→page breakdown |
| URL structure readable and stable | parameters where paths belong, dates in evergreen URLs, year suffixes | crawl |
| Image file names descriptive | `IMG_2043.jpg` on product pages | crawl |
| Image `alt` present and factual ★ | missing alt on informative images; keyword-stuffed alt; decorative images with text alt | crawl + page_audit |
| The subject is named in the structural elements, not only the prose | subheads that would fit any page ("Overview", "Conclusion"); internal anchors reading "read more"; captions and `alt` that never mention what the page is about | crawl + page_audit |
| Structured data valid and matched to visible content ★ | validation errors; markup claiming ratings/prices the page does not show | Rich Results Test + page_audit |

**The H1 count is not one of these checks.** Google states that one H1 and
several H1s both work, with no penalty for the count (myths.md) — so a "multiple
H1s" line in an audit spends a finding on a non-finding. Count belongs to
document structure and screen-reader navigation, and it is worth raising as an
accessibility note, never as a crawler-understanding failure. What does matter on
a responsive template is meaning: Google evaluates the mobile render, so a
desktop-only word carrying the subject is a real loss. Check that the mobile H1
still names the subject; prefer one H1 with the optional tail inside a span over
two H1s swapped by display classes.

On schema, hold the canonical stance from myths.md: mark up what is real and
required for the features you actually want (products, jobs, events,
breadcrumbs) — validity is hygiene, volume is not a lever. The same 10,937-page
sample found no markup at all on 45% of pages and none of the relevant type on
99%; report that as an eligibility gap on the surfaces you want, not as a
ranking finding.

On vocabulary, the failure is **absence, not density**: in that sample the
page's own topic terms were missing from subheads, anchors, file names and alt
text on 99.4% of pages (~20 terms per page) — the zones content teams never
revisit. Name the subject where the structure already exists; do not raise
density in the body, where keyword-style manipulation scored below baseline in
the one controlled benchmark (myths.md).

## D2. Duplication and consolidation

| Check | Fail looks like | Where |
|---|---|---|
| Copy is original, not scraped or spun | large blocks matching supplier or competitor text | plagiarism check |
| HTTP → HTTPS enforced | mixed versions indexed | crawl |
| URL variants normalized (parameters, trailing slash, case, tracking) | the same page indexed under many strings | crawl + GSC |
| Canonicals used to consolidate near-duplicates ★ | duplicates with self-canonicals; canonical chains; canonical to a noindexed page | crawl + URL Inspection |
| Other domains/subdomains not duplicating the content | staging, print, regional mirrors in the index | `site:` + crawl |
| Slug, title and H1 differ meaningfully between related pages | paginated, filtered, regional or near-duplicate variants sharing all three | crawl |

The last row matters more than it looks: the serving-layer duplicate grouping
keys mainly on slug, title and H1 rather than body text (technical-checks.md),
so two pages with genuinely different content can still be filtered out of the
SERP for sharing those three strings.

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
| The task module exists for a crawler, not only for the browser | the comparison table, calculator or spec grid renders in canvas, an image or JS-only markup, so a text-only read of the template scores it as thin | source vs rendered DOM, page_audit |
| Decision-accelerator elements present where the intent is commercial | transparent pricing table in plain HTML, implementation timeline, integration guide, ROI calculator, industry case study | demand-and-conversion.md |
| No AI-slop signature | generic phrasing, no evidence, no author, templated structure across dozens of pages | intent-and-content.md E4 |

## E2. Metadata as a click and citation surface

- Titles and descriptions written for the searcher, not the crawler; test rather
  than assume (experiments.md documents year-in-title, capitalization and
  promo-copy results, all market-specific).
- Do not chase featured-snippet formatting for its own sake; check first whether
  the query even returns one, and whether owning it costs the click.
- Exact-match keyword phrasing appears in a small minority of AI Overviews
  (benchmarks.md) — write the **body** in plain, accessible language and let the
  entity and topic coverage do the work.
- **That is not an argument against matching the query in the title and
  headings.** The two findings measure different objects and both hold: literal
  query strings are rare *inside the generated answer*, while an exact
  query–title match still adds materially to citation probability even after
  controlling for rank, and strong H1–H4 match to the prompt outperforms weak
  match (aeo-geo.md F2; play G4 in growth-plays.md). The rule that satisfies
  both: **match the question in the structural elements (title, H1–H4, the
  opening sentence), then answer it plainly in the prose.** Raising phrase
  density in the body is the failure mode — keyword-style manipulation scored
  below baseline in the one controlled benchmark (myths.md).

## How to record it

For each failed check: the template, the number of affected URLs, a sample of
five URLs, the observed value, the fix, the effort, and the evidence tier. A
count without a URL list is not evidence.
