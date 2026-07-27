# Benchmarks — dated numbers for sizing and expectation-setting

Use these to size an opportunity and to keep a report honest. **Always cite the
date**; this snapshot is April–July 2026 and search surfaces move fast. Re-check
anything older than ~18 months before it enters a plan.

## Surface reach

| Metric | Value | As of |
|---|---|---|
| Google AI Overviews | ~2.5B MAU | May 2026 |
| Google AI Mode | ~1B MAU | May 2026 |
| Google AI Mode share of sessions | <0.2% (growing) | Q1 2026 (panel data) |
| Bing | 1B MAU | May 2026 |
| Yandex "Алиса AI" | ~1 in 3 queries answered; 48.3M MAU on quick answers; ~10% of queries product-related | Q1–Q2 2026 |
| Bot vs human web traffic | Bots overtook humans for the first time | Jun 2026 |

## Click economics

| Metric | Value | As of |
|---|---|---|
| Zero-click Google searches (US, desktop+mobile) | 68% (was 60.45% in 2024); UK highest | Jan–Apr 2026 |
| Click-through on a link inside an AI summary | ~1% of sessions | 2025 study |
| First organic result when an AI Overview is present | −58% clicks | 2026 |
| Share of AI-answer links coming from the organic top-10 | 38% (was 76% mid-2025) | 2026 |
| Google AI citations sourced from the organic top-10 | 38% | 2026 |

## AI citation mechanics

| Metric | Value | Sample |
|---|---|---|
| Citation rate at retrieval position 0 vs 10 | 58% vs 14% | 16,851 queries / 353,799 pages |
| Never-cited pages | 58% of pages; 25% always cited | same |
| Median position: consistently cited vs never cited | 2.5 vs 13.0 | same |
| Exact query–title match uplift (rank-controlled) | +19pp | same |
| H1–H4 prompt match | 41% cited vs 29% | independent analysis |
| JSON-LD presence | +6.5pp | same dataset |
| Optimal length | 500–2,000 words (34.3%); >5,000 words 28.6% | same |
| Optimal subheads | 4–10 (33.2%) vs 1–3 (28%) | same |
| Optimal freshness | 30–89 days (32.8%); <30 days 25.3%; >2 years 27.5% | same |
| URLs cited by ChatGPT + Perplexity + AIO simultaneously | ~2.4% | cross-platform study |
| Classic SEO signals explaining ChatGPT recommendation variance | 15–20% (each factor R² ≈ 5–6%) | 29,562 domains / 105k prompts |
| Brand named in answer → cited | 53.1% vs 10.6% when not named | 541,213 answers / 20 brands / 6 platforms |
| Own "best [category]" page cited → brand excluded from the recommendation | 69% | 100 B2B prompts, 3 checkpoints |
| Retrieved-but-uncited rate | Perplexity ~76%; ChatGPT cites 61% | 9,886 answers |
| Citation persistence | ~1 in 4 pages cited once only; appearance ~every third day; longest streak 52 days | same |
| Reddit share of LLM citations | ~40% overall; ChatGPT's Reddit share fell ~60% → 10% in six weeks after a retrieval change | 2026 |

## Read budget (ChatGPT Deep Research)

| Metric | Value |
|---|---|
| First-read window | ~5,700 characters (median), max ~8,000 |
| Content share with <20 links | ~78% |
| Content share with 20–59 links | ~55% |
| Content share with 60+ links | ~33% |
| Re-read triggered by a successful `find` | ~95% of cases |

## Content and ranking correlations

| Metric | Value | Sample |
|---|---|---|
| Core-update growth correlation (Spearman) | offers product/service 0.391, task completion 0.381, proprietary assets 0.357, tight focus 0.250, strong brand 0.206 | 400+ sites |
| Win rate by feature count | 1 feature 13.5–15.4%; 4 features 68.1%; 5 features 69.7% | same |
| Information-gain median in the top-3 | 52/100 (identical across positions 1–3); 25% below 40 | 150 pages / 50 keywords / 10 verticals |
| Unique data points | 15+ → 62/100; 0–1 → 40/100; median top-3 page has 4 | same |
| SERPs with an unanswered common question in the entire top-3 | 90% | same |
| Median on-page optimisation score | 33/100 (46.8% below 25) against an ~80 practical threshold | 10,937 pages |
| Pages missing schema | 99% (45% none at all) | same |
| Four-year blog traffic outcome | median −85%; 12 of 100 to zero; 21 grew | 100 six-figure blogs, 2022→2026 |

## Operational benchmarks

| Metric | Target/observed |
|---|---|
| TTFB | <200ms optimal, <500ms acceptable |
| Server error rate | <0.5% |
| Duplicate-group persistence after a fix | up to 2 weeks |
| Out-of-stock crawl deprioritisation | 100+ days after the directive is removed |
| "Discovered – not indexed" push success | 70–80% indexed within 72h with the full protocol |
| Migration traffic loss | ~30% average; ~8% with a disciplined protocol; 67% in the documented failure |
| Recovery after mass accidental `noindex` | 6–12 weeks, staged |
| PageRank decay per hop | ~85% |
| Bounce/dwell thresholds for intent match | bounce <40% and >2 min = match; >70% = mismatch |

## Caveats

- Single-case figures (marked FIELD in growth-plays.md) are directional, not
  forecasts. Never present them as a promise.
- Vendor-published AI-visibility studies measure their own instrumentation; where
  two disagree, both drop to HYPOTHESIS.
- Regional variance is large: CWV outcomes, AI-surface availability, localisation
  depth and commerce protocols differ per market. State the market you measured.
