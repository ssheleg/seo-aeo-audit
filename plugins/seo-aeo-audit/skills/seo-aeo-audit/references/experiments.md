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

## What cannot be split-tested

Domain-level trust, sitewide speed, migrations, algorithm updates. Use
before/after analysis against a control benchmark and say plainly that
attribution is weaker.

## Documented results worth reusing as hypotheses (not as facts)

- **Titles.** Adding the current year to titles: control +2.3%, test +34.7%
  organic at 98.5% significance, rolled to 1,500 pages for +28% sitewide. Test it
  — do not assume it.
- **Title capitalization.** Across five years of controlled tests, 50% of
  meta-title capitalization tests were positive and **zero** negative — the most
  consistently winning test type in that dataset. The mechanism appears to be
  indexing-side (capitalization as an emphasis/NER signal), not CTR: all-caps
  titles rarely even render in the SERP. Prefer targeted capitalization of key
  terms over full all-caps.
- **Meta-description promos.** "Save 30%" produced +21.2% organic sessions in one
  market and exactly nothing in another. Market-specific; always test locally.
- **Grid size.** Cutting a category grid from 48 to 36 products was positive at
  85% confidence (below the usual bar) via page weight and LCP, not content
  depth.
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
size. Use models to generate variants and to analyse results, not to replace the
test.
