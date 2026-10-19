# Brief mode: build-time decisions for a site that does not exist yet

An audit reads a live site and proves what is wrong. A brief is written **before**
the pages exist, so it cannot prove anything about them: it records the decisions
the builders have to make, and names, for each one, the audit check that will
verify it once the site is live. Every row below is the inverse of an audit check
that already carries its evidence and tier. This file adds no doctrine of its own;
where a row and the section it links to disagree, the linked section wins and this
row is the defect.

The skill writes the brief and stops. It does not write the copy, the markup or the
components, and it does not choose the price or the positioning.

## Contents

- [When a brief, and what it produces](#when-a-brief-and-what-it-produces)
- [What a brief never contains](#what-a-brief-never-contains)
- [N1. Information architecture and the URL plan](#n1-information-architecture-and-the-url-plan)
- [N2. One question per page](#n2-one-question-per-page)
- [N3. Served HTML carries every answer](#n3-served-html-carries-every-answer)
- [N4. Schema plan for visible facts only](#n4-schema-plan-for-visible-facts-only)
- [N5. Entity home and one spelling](#n5-entity-home-and-one-spelling)
- [N6. Crawler policy as two decisions](#n6-crawler-policy-as-two-decisions)
- [N7. The llms.txt stance](#n7-the-llmstxt-stance)
- [N8. Explanatory internal links](#n8-explanatory-internal-links)
- [N9. A performance budget with field provenance](#n9-a-performance-budget-with-field-provenance)
- [N10. Preview controls set on purpose](#n10-preview-controls-set-on-purpose)
- [N11. Honest dates and lastmod](#n11-honest-dates-and-lastmod)
- [N12. Previews and staging behind authentication](#n12-previews-and-staging-behind-authentication)
- [N13. Measurement wired at launch](#n13-measurement-wired-at-launch)
- [N14. New-domain expectations](#n14-new-domain-expectations)
- [N15. HTML before PDF](#n15-html-before-pdf)
- [N16. Free-tool pages](#n16-free-tool-pages)
- [N17. Regional engines at launch](#n17-regional-engines-at-launch)
- [N18. Per-fact provenance and honest localization](#n18-per-fact-provenance-and-honest-localization)
- [N19. Native HTML and CSS before JavaScript](#n19-native-html-and-css-before-javascript)
- [Landing readiness](#landing-readiness)

## When a brief, and what it produces

Brief mode applies when there is no live page to fetch: a new site, a new section
of a live site, a landing page in design, or a migration target still on staging.
SKILL.md Step 0 makes the call. A live site with a planned section gets both runs:
an audit of what exists and a brief for what does not.

The output is one file, `docs/seo/brief-<YYYY-MM-DD>.md`, seeded from the brief
skeleton in [deliverable-templates.md](deliverable-templates.md). It holds one row
per section below, each with the decision taken, its owner, and the audit section
that verifies it. A row the project does not need is kept and marked `n/a` with a
reason, so a reader can tell a decision from an omission.

The first audit after launch is the brief's acceptance run: each row is checked
through the section it links to, and a row that fails becomes an ordinary finding
with its own evidence and tier.

## What a brief never contains

- **No finding and no tier on an unbuilt page.** There is nothing to observe yet;
  a brief row is a decision, and the audit section it links to supplies the tier
  when the page exists.
- **No item from the myth list.** Nothing in
  [myths.md](myths.md) enters a brief: no FAQPage markup for rich results, no
  publish-date bumps, no `llms.txt` as a ranking lever, no "write it for AI", no
  content volume as a strategy. A request for one is answered the way SKILL.md's
  myth guard answers it.
- **No copy, markup or design.** The brief says what the served HTML must carry;
  the copywriting, design and engineering owners decide how.
- **No number without its home.** A budget figure, a threshold or a benchmark is
  quoted from the section that owns it, with that section's date and source.

## N1. Information architecture and the URL plan

**Decide:** stable, descriptive URLs that will not change at the next redesign; money
pages reachable in few clicks through links from strong pages, not through a shallow
folder path. Folder depth and click depth are different things, and only the link
graph moves equity.

**Verified by:** [architecture-and-equity.md](architecture-and-equity.md#the-audit)
and [technical-checks.md](technical-checks.md#migrations-the-most-expensive-failure-mode)
(the URL plan is the migration you never have to run).

## N2. One question per page

**Decide:** a page-question table, one primary question and one intent per URL, with
the page type the SERP for that question already rewards. Two planned pages that
answer one question are merged in the plan, before anyone writes either.

**Verified by:** [intent-and-content.md](intent-and-content.md#d1-intent-match-is-a-page-type-decision-not-a-keyword-decision)
and [intent-and-content.md](intent-and-content.md#d2-cannibalization).

## N3. Served HTML carries every answer

**Decide:** every answer, price and FAQ answer is in the HTML the server sends, not
only in what JavaScript renders afterwards. Animation never holds the only copy of
content. A client-side modal or tab that carries content keeps a real URL that
renders the same content as a page on direct load.

**Verified by:** [aeo-geo.md](aeo-geo.md#f3-extractability--the-part-most-audits-skip)
and [technical-checks.md](technical-checks.md#a1-crawl-access-and-rendering).

## N4. Schema plan for visible facts only

**Decide:** structured data only for facts the page shows: `Organization` with real
`sameAs` profiles, `Product` or `SoftwareApplication` with an `Offer` whose price
matches the visible price. No FAQPage markup for rich results, and no schema for
content the page does not display.

**Verified by:** [technical-checks.md](technical-checks.md#b-canonicalization-and-duplication)
(validation is not eligibility),
[onpage-checks.md](onpage-checks.md#o1-can-crawlers-understand-what-the-page-is-about),
and `page_audit.py`'s `jsonld-*` findings, including `jsonld-price-parity`
([scripts.md](scripts.md#page_auditpy)).

## N5. Entity home and one spelling

**Decide:** one page that is the brand's home for who it is, and one spelling of the
brand and product names, used identically on the site, in profiles and in markup.

**Verified by:** [entity-and-brand.md](entity-and-brand.md#g1-cross-surface-consistency-the-cheapest-win-in-this-track)
and [entity-and-brand.md](entity-and-brand.md#g3-knowledge-graph-plumbing).

## N6. Crawler policy as two decisions

**Decide:** retrieval (may an answer engine fetch and cite the page) and training (may
a model learn from it) are decided separately, written into `robots.txt` per agent,
and recorded with their reason.

**Verified by:** [agent-readiness.md](agent-readiness.md#k2a-crawler-policy-is-two-decisions-not-one)
and `agent_surface.py` ([scripts.md](scripts.md#agent_surfacepy)).

## N7. The llms.txt stance

**Decide:** `llms.txt` is not a ranking or citation lever and the brief does not plan
it as one. It is an optional serving file, considered only where track K applies
(an agent that has already arrived needs to read the site cheaply).

**Verified by:** [agent-readiness.md](agent-readiness.md#k3-markdown-representations--where-the-myth-ends-and-the-contract-begins).

## N8. Explanatory internal links

**Decide:** internal links whose anchors say what the target page answers, placed in
the body where the reader needs the next step, and consistent across the site.

**Verified by:** [architecture-and-equity.md](architecture-and-equity.md#internal-link-anchor-mix)
and [onpage-checks.md](onpage-checks.md#o3-internal-linking-on-the-page).

## N9. A performance budget with field provenance

**Decide:** a performance budget for each template, owned by the engineering lead and
taken from the family's frontend-performance skill
([sheleg-dev frontend-performance](https://github.com/ssheleg/sheleg-dev/blob/main/plugins/sheleg-dev/skills/frontend-performance/SKILL.md)),
not restated here. Field data after launch is read at p75 with its cohort, period
and sample size.

**Verified by:** [experience-signals.md](experience-signals.md#h4-core-web-vitals--triage-order-that-actually-works)
and `psi_pull.py` ([scripts.md](scripts.md#psi_pullpy)).

## N10. Preview controls set on purpose

**Decide:** `nosnippet`, `data-nosnippet`, `max-snippet` and paywall markup are set
only where someone decided to limit quoting, never inherited from a template or a
plugin default.

**Verified by:** [aeo-geo.md](aeo-geo.md#f3-extractability--the-part-most-audits-skip)
(preview controls gate everything).

## N11. Honest dates and lastmod

**Decide:** a visible date changes only when the content changed, and sitemap
`lastmod` comes from the content's own modification time, never the deploy time.
A generator that cannot know the real date emits no date.

**Verified by:** [technical-checks.md](technical-checks.md#sitemap-protocol--the-details-that-make-one-silently-ignored),
[agent-readiness.md](agent-readiness.md#k2b-the-entry-points-a-machine-tries-and-the-link-that-only-exists-after-hydration),
and `sitemap_audit.py`'s batch-stamped `lastmod` finding
([scripts.md](scripts.md#sitemap_auditpy)).

## N12. Previews and staging behind authentication

**Decide:** preview deployments and staging hosts sit behind authentication. A
`noindex` tag alone still lets anyone, and any crawler that ignores it, fetch the
pages and follow their links.

**Verified by:** [tooling.md](tooling.md#check--tool-routing) (forgotten hosts and
subdomains) and [technical-checks.md](technical-checks.md#a3-the-mechanical-sweep-completeness-list).

## N13. Measurement wired at launch

**Decide:** on launch day, Search Console and Bing Webmaster Tools are verified for
every property variant, analytics records AI referrers, the direct / no-referrer
baseline starts, and the prompt-set baseline is run once and recorded verbatim.

**Verified by:** [measurement.md](measurement.md#j1-the-surfaces-that-exist-in-2026),
[measurement.md](measurement.md#j3b-the-kpi-set-has-moved),
[aeo-geo.md](aeo-geo.md#f5-the-prompt-set-run-it-record-verbatim-answers), and
`preflight.py` ([preflight.md](preflight.md)).

## N14. New-domain expectations

**Decide:** the plan states that indexing levers do not fire on a domain with no trust
yet, and sets the indexing timeline against earned trust instead of promising dates.

**Verified by:** [technical-checks.md](technical-checks.md#a2-indexation-economics).

## N15. HTML before PDF

**Decide:** content people read on screen is published as an HTML page. A PDF is
planned only where the PDF itself is the deliverable (a datasheet to download, a
form to print), and then with its own title and metadata.

**Verified by:** [growth-plays.md](growth-plays.md#gains--earn-more-visibility)
(the PDF play) and [onpage-checks.md](onpage-checks.md#o5-metadata-as-a-click-and-citation-surface).

## N16. Free-tool pages

**Decide:** one client-side utility per real task; the answer and the tool both work
from the served HTML; one path from the tool to the product; each locale rendered as
its own page. The brief also carries a "do not build" list: a tool that would expose
people or help someone evade a limit is not built.

**Verified by:** [growth-plays.md](growth-plays.md#gains--earn-more-visibility)
(task completion on site) and [aeo-geo.md](aeo-geo.md#f3-extractability--the-part-most-audits-skip).

## N17. Regional engines at launch

**Decide:** Bing Webmaster verification (meta tag or `BingSiteAuth.xml`) and an
IndexNow key exist from launch, plus verification with the locale's own engines
where the market uses them. Their absence is a data-access gap the first audit
reports, not a ranking factor.

**Verified by:** [measurement.md](measurement.md#j1-the-surfaces-that-exist-in-2026)
and [technical-checks.md](technical-checks.md#a3-the-mechanical-sweep-completeness-list).

## N18. Per-fact provenance and honest localization

**Decide:** every number on a data page names its source and date in the page itself,
and each fact has one home on the site. A localized page exists only where the offer,
price or conditions genuinely differ for that market, with a complete hreflang set.

**Verified by:** [entity-and-brand.md](entity-and-brand.md#g1-cross-surface-consistency-the-cheapest-win-in-this-track)
and [technical-checks.md](technical-checks.md#b2-hreflang-and-international-duplication).

## N19. Native HTML and CSS before JavaScript

**Decide:** anything that carries content or navigation is built from native HTML and
CSS first (links, details/summary, forms), with JavaScript as an enhancement that the
page does not need to show its content.

**Verified by:** [technical-checks.md](technical-checks.md#a1-crawl-access-and-rendering)
and [aeo-geo.md](aeo-geo.md#f3-extractability--the-part-most-audits-skip).

## Landing readiness

A landing page is checked by two command sets, each run against the **built** page,
never the draft.

**Copy and structure** belong to super-ux. Its readiness commands (LP-17 answers in
the markup, LP-13 one action one label, LP-18 the argument without JavaScript,
LP-11 one number one value, LP-20 the price stated) live in
[super-ux, landing pages, the readiness check](https://github.com/ssheleg/super-ux/blob/main/plugins/super-ux/skills/references/landing-pages.md#the-readiness-check).
They are linked here, not copied.

**Search and machine readability** belong to this skill:

```bash
python3 "$SKILL_DIR/scripts/page_audit.py" --url https://example.com/landing --format markdown
python3 "$SKILL_DIR/scripts/agent_surface.py" --origin https://example.com
python3 "$SKILL_DIR/scripts/psi_pull.py" --url https://example.com/landing --strategy mobile
```

Read from `page_audit.py`: the title and meta description findings
([onpage-checks.md](onpage-checks.md#o5-metadata-as-a-click-and-citation-surface)),
the JSON-LD inventory and its `jsonld-*` findings with the JavaScript-blindness
caveat beside them (N4), and the words present without JavaScript (N3). From
`agent_surface.py`: the crawler policy as served (N6). From `psi_pull.py`: field data
if the page has any traffic yet, and the lab run as diagnosis only (N9). A landing
page with no field data yet says so; the lab score does not stand in for it.
