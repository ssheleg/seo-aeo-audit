# Experiment design — for anything below CONFIRMED

Nothing at FIELD or HYPOTHESIS tier ships sitewide. It ships as a test.

## Rules

1. **One variable.** Change titles *or* descriptions, never both — otherwise the
   result is unattributable.
2. **Comparable cohorts.** URLs must match on template, traffic band and page
   type. 100 product pages on one template is a valid split; a mix of products,
   posts and categories is not.
3. **Size and duration.** ≥50 URLs per group (100+ preferred), ≥4 weeks, 95%
   confidence, seasonality accounted for.
4. **Discard tests that overlap a core or spam update.** Volatility swamps the
   effect. Watch for the rollout in server logs — a sharp change in Googlebot
   crawl pattern often precedes the public announcement by 7–10 days, and effects
   continue after Google declares a rollout complete.
5. **Control group always.** In a noisy environment the control is what separates
   your change from platform drift.
6. **Roll winners into templates**, not page by page, and record the result in
   the site's own playbook (it becomes CONFIRMED *for this site*).
7. **Stack tests sequentially** so gains compound; do not run overlapping tests
   on the same cohort.
8. **Sample AI citations repeatedly, never once.** Citation is intermittent: in a
   34-page / 5-domain / 9,886-answer run (Feb–May 2026) roughly one page in four
   was cited a single time and never again, a cited page reappeared about every
   third day between its first and last citation, and the longest unbroken streak
   was 52 days. Sample daily for ≥30 days, and score **retrieval** separately from
   **citation** — Perplexity left 76% of retrieved pages uncited while ChatGPT
   cited 61% of them.
9. **Hold the prompt format constant across rounds.** Format moves brand counts
   20–25% (rankings, lists and comparisons surface ~20% more brands;
   keyword-explicit prompts ~25% more) while wording barely matters above ~0.50–0.60
   cosine similarity (1,754 prompts / 37,804 answers). Changing the format between
   measurements changes the instrument, not the result. Report per engine and per
   persona.
10. **Allow for crawl-scheduler hysteresis.** A URL that once carried
    `noindex`/301/canonical stays deprioritized for 100+ days after the directive
    is removed, so any directive test needs a recovery window measured in months —
    and its control cohort must never have carried the directive.
11. **Give rotation time before scoring a merge.** Google rotates competing URLs
    every few days, so a cannibalization test needs ≥1 week of observation. Above
    roughly 1M clicks GSC data hiding masks the effect — use layered filters.

## What cannot be split-tested

Domain-level trust, sitewide speed, migrations, algorithm updates. Use
before/after analysis against a control benchmark and say plainly that
attribution is weaker.

## Documented results worth reusing as hypotheses (not as facts)

**Tiering for this list.** Each entry names its tier. A split test with a stated
significance level on a named client base is `STUDY`; a single before/after on one
site is `FIELD`; anything confounded is neither, and says so. The heading already
says "not as facts", and the list used to leave eight entries with no tier at all —
which is how "+34.7% organic" travels into a plan as a projection.

- **Titles.** Adding the current year to titles: control +2.3%, test +34.7%
  organic at 98.5% significance, rolled to 1,500 pages for +28% sitewide
  (`STUDY` — controlled split test, one client, significance stated). Test it —
  do not assume it, and note the effect is market- and query-specific.
- **Title capitalization.** Across five years of controlled tests, 50% of
  meta-title capitalization tests were positive and **zero** negative — the most
  consistently winning test type in that dataset (`STUDY`, multi-site controlled
  tests, reported 2026-04). The mechanism appears to be
  indexing-side (capitalization as an emphasis/NER signal), not CTR: all-caps
  titles rarely even render in the SERP. Prefer targeted capitalization of key
  terms over full all-caps.
- **Meta-description promos.** "Save 30%" produced +21.2% organic sessions in one
  market and exactly nothing in another (`STUDY`, split test; the null arm is the
  point). Market-specific; always test locally.
- **Grid size.** Cutting a category grid from 48 to 36 products was positive at
  85% confidence — below the 95% bar, so direction only (`FIELD`, 2026-06-23) —
  via page weight and LCP, not content depth.
- **Title capitalization — the case behind the pattern** (`FIELD`, one site). It
  moved every meta title to upper case and recorded +17.5% organic (mobile +20.4%),
  yet a live-SERP check found almost no all-caps titles rendering and its PDPs mostly
  surface inside product grids where the title text is not read. That is what
  points the mechanism at indexing, not CTR. Test targeted capitalization of key
  terms against full all-caps.
- **Schema, measured per surface.** Two named studies disagree on both Google's
  AI surfaces *and* ChatGPT (Study A / Study B, with samples and significance, in
  benchmarks.md "Contested metrics" and aeo-geo.md F6), so both directions are
  HYPOTHESIS and this is a live experiment candidate rather than a settled
  result. Any schema test that reports one blended "AI visibility" number will
  contradict itself; split the metric by engine, and hold the schema *type*
  constant — Study B tested one type on homepages only. The canonical stance
  (mark up what is real and required, then stop) stays in myths.md.
- **"Crawled – currently not indexed": quality rejection or authority deficit?**
  The two readings prescribe opposite work (rewrite versus link) and neither is
  settled (technical-checks.md, architecture-and-equity.md). The discriminating
  design is written up in architecture-and-equity.md: hold content constant, add
  links from strong nodes to one cohort, leave a matched cohort alone, measure
  index rate. Rule 2 (comparable cohorts) and rule 5 (control) do the heavy
  lifting here.
- **Promotional pages for an unknown entity.** 34 pages / 5 domains / 9,886
  answers, 7 Feb – 31 May 2026: a brand-new conference filled 72 previously empty
  answer slots (82% of the new mentions cited the published pages) while an
  established tool drew only 6% from its own pages. Caveats worth carrying into
  the design: 43% of answers linking the conference page never mentioned the
  event, and retrieval without citation was worse (74% ignored). Test on a
  category gap, not on an established brand.
- **Modules on category and store pages — direction replicated, cause not.** Two
  controlled split tests point the same way: adding a brand carousel below the
  content of store pages was estimated at **−2.8%** organic sessions, and
  removing a product carousel from category pages was **+29%**. The proposed
  mechanisms differ — commercial links diluting a local/navigational intent in
  the first, page weight and stale content in the second — so the direction is
  replicated while the cause stays open. Practical read: on any template whose
  ranking rests on a non-commercial intent, test module **removal** before you
  test module addition, and treat "add a carousel for discoverability" as a
  hypothesis with two negative precedents (STUDY ×2, 2026-07; sources in
  benchmarks.md).
- **Position of the substance, not its length.** Bringing product descriptions
  out of tabs and above the fold measured **+14%** on desktop, with the stated
  hypothesis being that tabbed content needed JavaScript to render. Two variables
  moved at once — position and render dependency — which is exactly why it is a
  hypothesis rather than a layout law, and why it is worth re-running as two
  tests on any template that hides substance behind an interaction (STUDY,
  2026-07).
- **Web-font weight** (`FIELD`, one estate, field data). 900KB of preloaded fonts
  widened the P90 TTFB→FCP gap from ~840ms on fast connections to ~1,488ms on slow
  ones and correlated with ~18% fewer pageviews per session. Subsetting is a clean one-template test with a
  field-data readout (CrUX, not lab).
- **Content refresh on a directory** (`FIELD`, 2026-05-29, and **confounded** —
  neither tier nor effect size transfers). 500 high-converting pages got a fresh FAQ
  block and retargeted keywords; AI Overviews traffic +80% and the property +10%
  period over period. Confounded — a Markdown pipeline and a template redesign
  shipped in the same window — so reuse it as a hypothesis about refresh scope,
  never as an effect size.
- **Markdown serving to AI crawlers.** Conflicting evidence (0% crawler visits in
  a 100M-site test vs a single-site AIO gain) — a textbook experiment candidate,
  measured in server logs and AI-surface reporting, on one section only.

## The experiment record

Keep one row per test in `docs/seo/experiments.md`:

```
| id | hypothesis | cohort (template, n) | control (n) | variable | start | end |
| metric | control delta | test delta | significance | verdict | rollout |
```

Verdict values: `win → rolled out`, `win → not rolled out (why)`, `no effect`,
`loss → reverted`, `invalidated (update/seasonality/instrumentation)`.

## Prediction hygiene

Do not ask a model to predict which variant will win: in a 48-test comparison the
best model guessed 62.5% and the worst 48%, inside the noise band for that sample
size (`STUDY`, 48 tests). Use models to generate variants and to analyze results, not to replace the
test.
