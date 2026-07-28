# Tracks D & E — intent fit, cannibalization, content value

## D1. Intent match is a page-type decision, not a keyword decision

Read the current top-10 for the target query and classify what format the engine
rewards, then match it. Four dominant intents, each needing a different page:

| Intent | Example | What the SERP rewards |
|---|---|---|
| Informational | "how does X work" | Exhaustive, well-structured explanation, demonstrated expertise |
| Navigational | "ahrefs login" | Thin, fast, unambiguous; low competition |
| Commercial | "best SEO tools" | Comparisons, pros/cons, pricing breakdowns, selection criteria |
| Transactional | "buy ahrefs subscription" | Product detail above the fold, clear CTA, trust signals, frictionless checkout |

Validation is behavioral, not aesthetic: bounce <40% and time on page >2 min
indicate a match; bounce >70% indicates a mismatch. Documented case: transactional
PDPs targeting "best [product]" ranked 12–20 with 78% bounce and 0.4% CVR;
replacing them with comparison pages (commercial intent) interlinked to the PDPs
moved them to positions 3–7, bounce 34%, CVR 3.2% — an 8× conversion change.

Head terms often carry **mixed intent** ("project management software" =
what/which/where) and need composite pages that resolve all three, or a cluster
that does.

The same test applies to answer engines: pages that rank but are never cited
usually fail the *direct answer* expectation rather than the relevance one.

**One query, two surfaces.** The classic results and the AI answer on the same
query do not always reward the same page type. Documented example: [outdoor
lighting solutions] ranked ecommerce pages for purchase intent while the AI
Overview answered the category question — types, power options, brightness
levels, installation, maintenance (FIELD, one vendor-documented SERP, 2024-06;
dated, re-check it live). Classify both surfaces before choosing the page type,
and say which one a template is actually built for.

**Query class is measurable.** Google classifies queries into a small number of
classes, and the class predicts which SERP features appear and where the answer
must sit (a short-fact query wants the answer immediately, not after a build-up).
Free classifier: `queryclassifier.com` (DistilBERT trained on 4.8M query/category
pairs from the 2025 ranking-parameter leak) — treat its output as a hypothesis
generator for content structure, not as ground truth.

**Demand direction before investment**: check the 12-month search-volume trend
for the head terms (e.g. Ahrefs' GGR 12M column). Positive YoY = tailwind;
negative = you are optimizing a shrinking market and should say so in the report.

## D2. Cannibalization

Google does not "split equity" between competing URLs — it runs **rotational
testing**: it alternates the candidates in the SERP and measures which resolves
intent better. Both bounce in position and the combined click total falls.

Diagnose with two checks:

1. GSC → filter by query → break down by page. The same query surfacing several
   of your URLs is the first signal. On large properties (1M+ clicks) data hiding
   masks this — use layered filters.
2. SERP overlap: if two of your pages have >70% overlap in their top-10
   competitor sets, Google has clustered them into the same intent.

Rotation swaps every few days, so observe for at least a week before concluding.

**Merge protocol.** Pick the winner by: current best position, most clicks in 90
days, most backlinks, or cheapest internal-link rework. Then: move unique content
to the winner, draft or `noindex` the losers, **301** them (canonical is weaker
here), and update every internal link. Week 1 verify redirects; week 2 expect
volatility; the winner stabilizes first and combined clicks rise once the system
sees one source.

Two recurring self-inflicted causes: publishing new content before fixing an
existing overlap, and year-suffixed URLs ("best tools 2024" alongside "…2025")
that cannibalise each other and the evergreen page. Use one evergreen URL and
update it.

## E1. What actually makes a page worth ranking in 2026

Correlation analysis of 400+ winners and losers from a core update (Spearman vs
traffic growth):

| Feature | ρ |
|---|---|
| Offers a product/service | 0.391 |
| Allows task completion on-site | 0.381 |
| Proprietary assets (own data, inventory, UGC) | 0.357 |
| Tight topical focus | 0.250 |
| Strong brand (only when it reflects **navigational** demand) | 0.206 |

The effect is additive: one feature → 13.5–15.4% win rate; four → 68.1%; five →
69.7%. Examples: a recipe site that sells meal plans beats recipe publishers; an
education site where users solve interactive problems beats explainer
publishers; a comparison site loses because the task completes on someone else's
domain.

Audit each key template against those five, and be honest when the gap is
structural (a travel blog does not become a tour operator in a quarter) — the
plan then targets the reachable ones: task completion on-site, tighter focus,
proprietary data.

**Audit the modules, not only the prose.** Booking engines, aggregators and
comparison platforms carry their value in designed blocks, tables and
interactive modules rather than text, and the helpful-content system is
described as evaluating whether the page lets the user finish the task — so
layout and functionality are part of what gets read ("visual semantics",
practitioner framework, 2026-07-15; HYPOTHESIS, mechanism plausible, no measured
effect, but consistent with the ρ=0.381 task-completion correlation above). The
practical consequence is an audit error to avoid: a text-only read scores a
working comparison tool as a thin page. Inventory the modules per template and
check they exist for a crawler (onpage-checks.md E1).

**Trust does not travel with the template.** A dominant competitor's structure
is copyable; the decades of navigational demand underneath it are not (FIELD,
single observed case — a vendor blog holding #1 on head AI terms with
unremarkable prose, 2026-04-30). "Do what they do" is not a finding. The same
case carries the mirror warning for incumbents: topic expansion across every
adjacent category eventually collides with the tight-focus feature.

## E2. Information gain

Study of 150 top-3 pages across 50 keywords and 10 verticals:

- Originality does **not** correlate with position *inside* the top-3 (medians
  52 / 51.5 / 52 out of 100); a quarter of top-3 pages score below 40 — near-pure
  rehash.
- The one page-level lever that moves the score is **original quantitative
  data**: pages with 15+ unique data points average 62/100, pages with one or
  none average 40/100. The median top-3 page carries just **4** unique numbers.
- Length barely matters (longest third 57.5 vs shortest third 50.5, and the
  middle third breaks the pattern entirely).
- In **90% of SERPs**, at least one common user question is unanswered by the
  entire top-3; the spread between most and least original page in one top-3
  averages ~32 points.
- Vertical medians span 20 points (medicine 42 → legal 62); commercial and B2B
  SaaS sit near the bottom.

Editorial consequence: cover the consensus baseline briefly, then spend the
length on original measurements, internal analytics, and the questions everyone
skipped. This is also the AEO play — models synthesise consensus for free and
then look for what a single source can add on top.

Read the study for what it is (STUDY, published 2026-07-27): it describes the
state of the SERP, not the ranking function, and makes no claim that the score
drives position. Two further details hold up. Original quantitative data shows
no saturation ceiling in the data, unlike length, which plateaus. And the rehash
share climbs to 37–40% below the top-3 against 24% inside it — the further down
page one, the more filler, which is where a displacement opportunity usually is.

When you verify information gain, verify the numbers. Unique data points are
forgeable: a documented spam pattern extrapolates one national statistic down to
every town to manufacture "original" local data across thousands of
near-identical sites (detection material, threats-and-defense.md). A number
counts as information gain only if somebody measured it, and the audit note
should say who and when.

## E2b. What users expect to see on the page

Practitioner counterweight to keyword-first thinking (SEJ, *SEO Trends 2026*):
the ten-blue-links baseline died long before AI — featured snippets (2014),
Knowledge Graph (2012), video results (2007) — so "zero-click" understates a
longer shift and ignores Discover, video and multi-intent complex queries
entirely. What actually broke is **keyword-scaffolded content**: pages built on a
keyword list a tool produced, rather than on what a user came to do.

Two tests worth running on every key template:

1. **Expectation test.** Write down what a user expects to see on this page. On
   an e-commerce page: product images, specs, reviews, measurements, comparisons
   — not a five-paragraph essay above them. Then compare with what ships.
2. **Justification test.** If the reason for an element is "because Google wants
   to see it", it is the wrong decision. Remove it or justify it from user need.

Friction removal is the deliverable: list what stops a user from doing what they
came to do, and delete those obstacles. Depth where the user needs depth; brevity
where they do not.

## E3. Zero-click defensibility

Rank each content type by how much of its value AI can reproduce:

- **Strongest moat**: owned audience (email/SMS/in-app), transactional pages,
  original research, host-led video/podcast with branded demand, UGC communities.
- **Medium (labor moat)**: hands-on reviews with real testing, insider expert
  perspective, case studies with before/after metrics, original reporting,
  directories with first-party data and freshness.
- **Weak without differentiation**: guides and explainers, templates, brand pages
  (still critical for entity definition), support docs (canonical source still
  trusted), FAQ/glossary, listicles (survive only with real testing and
  transparent criteria).

The formula across all of them: **proprietary + task completion + niche focus**.

Selection rule from the 2026 practitioner panel: **find the queries AI does not
cannibalize**. Where Google surfaces no AI Overview and the answer still requires
a click, classic content converts — one agency reports strong MQLs directly from
those SERPs. Formats that resist replication: recorded opinion and interview
video, first-hand testing, and anything requiring a named person's judgment.
Depth over breadth: super-serve a niche audience instead of chasing scale.
Effort does not correlate with traffic; depth does.

Reality check from a four-year study of 100 six-figure blogs: the median lost
**85%** of search traffic; 12 went to zero; only 21 grew. Survivors clustered
around content requiring first-hand doing (a recipe actually cooked, a pattern
actually tested), not around a "safe" niche — by niche median: parenting +108%,
DIY +2%, food −44%, travel −74%, lifestyle −90%, health −93%, finance −99%.
There are no safe niches, only safe content: does the reader need *this author*
to get the result?

That collapse ran in two waves, which is why "we already survived the helpful
content update" is not reassurance: the September 2023 helpful-content update
and the March 2024 core update demoted templated, single-channel content, and
from 2025 the AI Overview became the default surface, so nothing has to be
demoted — the answer arrives before the click. One trait (summarizable, no
first-hand moat, one borrowed distribution channel) is fatal in both. The
distribution is bimodal, too: survivors were mostly small sites compounding from
a low base while established players in the same niches were gutted (one went
54,000 → 1,100 monthly visits). A niche peer's growth curve is not evidence that
your model still works.

## E4. Patterns that now hurt

Sites in decline typically run three or more of these AI-content templates (the
worst run all eight):

1. `/blog/[product-A]-vs-[product-B]` comparisons
2. `/glossary/[term]` definitions
3. Template rankings ("best X for Y")
4. Self-serving rankings where the author ranks itself #1
5. `/blog/[competitor]-alternatives`
6. Scaled geo/language duplication
7. One-question-per-page FAQ URLs
8. Mass off-topic publishing

Volume is the aggravating variable, not the template alone: the declining sites
carry hundreds to thousands of URLs on these patterns, and the largest losses
track the largest footprints (FIELD, pattern analysis across declining sites,
2026-05-13). Enforcement is also uneven — millions of machine-translated URLs
still rank on large platforms (FIELD, SERP observation, 2026-05-14) — so report
this as a risk profile with a cost attached, never as a predicted penalty date.

Self-promotional listicles are now actively negative in AI answers: when the
model used a brand's own "best [category]" article as a source, the brand was
excluded from the recommendation in **69%** of cases — the citation votes for
everyone on your list except you.

Scaled AI content is a documented penalty profile: 800+ auto-generated pages with
broken tables and phantom URLs preceded a 50k → 10k monthly-visit collapse in one
case; a "Scaled content abuse" manual action on one directory (850k AI articles)
removed it from Google **and** collapsed that directory's ChatGPT citations to
near zero, while the rest of the domain kept ranking. Penalties cascade
downstream into AI surfaces.

What does work: AI-assisted, human-edited content beat pure generation ~5× across
Google organic, ChatGPT, AIO and Gemini in a controlled experiment. Keep the
human share of the final text high and verify every fact — models hallucinate
sources ~40% of the time on statistics and generate plausible 404 URLs.

## E5. Freshness is relative, not calendar-based

Leaked ranking parameters score a document's age **against the rest of the result
pool** (`result_set_age_*_percentile_in_days`). A 2014 page can be "fresh" if the
competitors are older; a nine-day phone review is stale against two-day rivals.

Operational check: monthly, export last-modified dates for the top-10 on priority
queries and flag pages that fall outside the age percentile. That is the trigger
for a **substantial** update, and Google's own patent language is explicit about
what counts: a title change, a substantial new section, or link changes (anchor,
target, surrounding text — not navigation). Ignored: date and `lastmod` bumps,
JavaScript, ads, navigation and boilerplate. "Update the date" is not an update.

**Topic velocity sets the baseline**, so run the check per query, not sitewide:
an evergreen question tolerates content that is years old when the competitors
are equally old, while a fast-moving vertical prices a nine-day page as stale.
Field report from hardware reviews: a three-season-old deep review stayed the
freshest result while the products and the competing pages stood still (FIELD,
2026-06-02).

Tier the patent honestly: it is architecture, not a confirmed live weight, and
the filing is read as scoring updates on history, links, behavioral signals and
staleness markers beyond the fingerprint diff. Treat the three counted changes
as the minimum bar for "substantial", not as the whole model.

**Refreshing with a model erodes what already ranks.** Reported contamination
pattern: asked to improve a page, a model quietly deletes the specific,
hyper-relevant sentences it reads as redundant, and the page loses the passages
that earned its position. Cap the edit instead of commissioning a rewrite —
tighten title and H1 to the intent, rebuild the introduction, add the missing
entity or question blocks, refresh internal links, and leave ranking passages
alone (FIELD, practitioner method, 2026-05-13).

Then measure the refresh as a cohort. One directory reported +10% organic and
+80% AI Overview traffic after updating 500 high-converting pages — while also
redesigning the landing template and changing how content was served to AI
crawlers in the same window (FIELD, 2026-05-29). Three simultaneous changes
attribute to nothing. Ship refreshes as a batch against a held-back control and
size the result from that (experiments.md).

## Evidence to capture for D/E

- Per-target-keyword: the top-10 format inventory, your page type, the mismatch
  verdict, and current behavioral metrics.
- The cannibalization table: query, competing URLs, clicks each, SERP overlap %,
  chosen winner, action.
- Per key template: the five-feature scorecard, the count of unique data points
  (with the source of each — measured, or borrowed), the module inventory, and
  the unanswered-question list from People Also Ask / Reddit / support tickets.
- Per priority query: your last-modified date against the top-10 age
  distribution, and whether the page sits outside the percentile.
- For every refresh already shipped: what changed, on what date, what else
  shipped in the same window, and what was held back as a control.
