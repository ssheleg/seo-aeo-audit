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
Effort does not correlate with traffic; depth does.

Reality check from a four-year study of 100 six-figure blogs: the median lost
**85%** of search traffic; 12 went to zero; only 21 grew. Survivors clustered
around content requiring first-hand doing (a recipe actually cooked, a pattern
actually tested), not around a "safe" niche — by niche median: parenting +108%,
DIY +2%, food −44%, travel −74%, lifestyle −90%, health −93%, finance −99%.
There are no safe niches, only safe content: does the reader need *this author*
to get the result?

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

## Evidence to capture for D/E

- Per-target-keyword: the top-10 format inventory, your page type, the mismatch
  verdict, and current behavioral metrics.
- The cannibalization table: query, competing URLs, clicks each, SERP overlap %,
  chosen winner, action.
- Per key template: the five-feature scorecard, the count of unique data points,
  and the unanswered-question list from People Also Ask / Reddit / support
  tickets.
