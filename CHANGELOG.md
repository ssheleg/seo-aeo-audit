# Changelog

## v0.3.0

Completeness pass — every audit track now carries both the judgement work and the
mechanical sweep, and the post-click half of the funnel is in scope.

- **`ranking-model.md`** (new): systems vs signals vs factors and why the
  semantic argument is a trap; the "200 ranking factors" myth; the three that
  carry weight (content and relevance, page experience, links); helpful-content,
  RankBrain, BERT, MUM and query-dependent freshness; E-E-A-T's real status as a
  rater specification rather than a dial; personalisation and locality.
- **`onpage-checks.md`** (new): the per-template on-page sweep — crawler
  comprehension, duplication and consolidation, on-page internal linking, content
  substance, metadata as a click and citation surface — with the fail state and
  the tool for each row.
- **`tooling.md`** (new): the evidence ladder (logs → Search Console → crawl →
  field data → third-party indices → manual), check → tool routing, Chrome
  DevTools recipes (header/soft-404 forensics, JS parity, link and image tables,
  emulation), and an explicit statement of where automation stops.
- **`demand-and-conversion.md`** (new): conversion elements per money template,
  lead capture without value destruction, the attribution gap table (last-click,
  untracked calls, missed calls, offline conversions, AI referrals, cross-device,
  zero-click) and paid × organic alignment.
- **`technical-checks.md`** gains the mechanical completeness sweep: availability,
  sitemaps, crawl optimization, performance, accessibility and risk — the boring
  failures that quietly cost traffic.
- **`benchmarks.md`** gains practitioner-survey context (State of SEO 2026) and
  AI-surface coverage figures (AI Overview growth by vertical, exact-match
  phrasing in AIO, B2B click-through to cited sources, device split of AI
  referrals).
- **`myths.md`** gains four: the 200-factors list, "E-E-A-T is a ranking factor",
  "AI wrote it, just publish it", and "last-click tells us what organic did".
- **`growth-plays.md`** gains G19 (call and offline conversion tracking), G20
  (decision-accelerator content) and G21 (paid × organic alignment).
- Sources distilled: SEJ *Ultimate Technical SEO Audit Workbook* + its
  spreadsheet, *SEO In The Age Of AI*, *The Future of AI Search*, *State of SEO
  2026*, *Google Ranking Factors: The 3 That Really Matter*, *B2B Lead
  Generation*, *PPC Trends 2026*, *PPC Experts Tips*, and the CallRail × SEJ
  lead report.

## v0.2.0

Update awareness — the skill now carries the Google update history and knows how
to refresh it.

- **New reference `algorithm-updates.md`**: dated timeline of every core, spam
  and Discover update from March 2025 through June 2026 (start date, completion
  date, type, audit implication), plus a table of platform and policy changes
  that retired old tactics (FAQ rich results, AMP cache, Preferred sources in AI
  surfaces, GSC AI reporting and opt-out, Bing AI Performance, the spam policy
  covering generative-AI manipulation, I/O 2026, commerce protocols).
- **Update-response protocol** — exact dates → before/after export by page,
  query, country, device → segment by template and intent → competitor set →
  classify winner/loser/unchanged → only then hypothesize. Wired into SKILL.md as
  a mandatory step before any decline diagnosis, and into the play list as `P5`.
- **Refresh routine** with named sources (SEJ algorithm history, Search Status
  Dashboard, Search Central and Bing blogs) so every release folds in what
  shipped since — including re-checking whether a change retires a myth or
  invalidates a benchmark.
- **Distilled SEJ's *SEO Trends 2026*** into the existing contracts: the
  user-expectation and "because Google wants it" tests (`intent-and-content.md`),
  discovery fragmentation and owned-vs-rented surfaces (`entity-and-brand.md`),
  the shifted KPI set — branded search volume, AI mention share, UGC tone,
  owned-audience growth, assisted conversions (`measurement.md`), three new
  growth plays (owned audience, UGC-platform presence, format diversification),
  two new myths, and four dated benchmarks (Google below 90% share, Gen Z Lens
  entry points, 80% still click to verify under an AI Overview).

## v0.1.1

Review pass — defects found by re-auditing the skill against its own rules.

- **Deliverable skeletons now ship with the skill.** They lived only in
  `templates/` at the repo root, which the skills CLI does not copy, so every
  non-Claude agent got a SKILL.md pointing at files it could not read. They are
  embedded in `references/deliverable-templates.md`; the validator fails if the
  root copies drift from the shipped ones (CI proves it can fail).
- **Fixed a broken cross-reference**: the auditor pointed at
  `technical-checks.md#a0-blockers-first` while the heading generated a longer
  slug. Heading shortened, anchor resolves.
- **One spelling standard.** British/American forms were mixed across the
  references (canonicalisation/canonicalization, defence/defense,
  behaviour/behavior, optimisation/optimization…), which also broke one anchor.
  Unified to American everywhere, including the anchors the script emits.
- **`page_audit.py` — prose vs link text.** `word_count` counted navigation
  labels, so a nav-heavy page looked substantial and `first_100_words` returned
  menu items instead of the opening answer. Prose and link text are now counted
  separately (`word_count`, `link_text_words`), and the thin-content finding says
  which is which.
- **`page_audit.py` — directive matching by word boundary.** `none` and
  `noindex` were matched as substrings, so body text like "nonexistent" could
  raise a false blocker. Added a third fixture (`edge-page.html`) that would have
  triggered it, plus coverage for `nosnippet` and for harmless `id`/`class`
  attributes on a canonical.
- Deduplicated a benchmark row that presented one 38% figure twice as if it were
  two findings, and attributed both sources.
- SKILL.md gained the **tooling ladder** (crawl export/MCP → GSC/Bing →
  logs → bundled script → manual) and an explicit rule for degraded,
  public-only audits: those findings are inferences and get tiered as such.
- `--base-url` documented as `--file`-only.

## v0.1.0

First release.

- `seo-aeo-audit` skill: ten evidence-based audit tracks (A access & indexation
  economics, B canonicalization, C architecture & link equity, D intent & SERP
  fit, E content value, F extractability/AEO-GEO, G entity & brand consensus,
  H experience signals, I risk & threats, J measurement), a triage model
  (`priority = (impact × confidence) / effort` with evidence-tier weights), and a
  two-file deliverable contract (findings report + change plan).
- Thirteen reference files inside the skill directory, so every distribution
  channel ships the contracts: technical checks, architecture & equity, intent &
  content, AEO/GEO mechanics, entity & brand, experience signals, threats &
  defense, measurement, the ranked play list, experiment design, evidence tiers,
  the myth guard, and dated 2026 benchmarks.
- `scripts/page_audit.py` — stdlib-only page auditor: indexing directives, the
  canonical extra-attribute trap, heading/schema inventory, image alt coverage,
  JS-gated price detection, and an answer-engine **read-budget** estimate
  (~5,700-character first read, link markers versus content). Works offline via
  `--file`.
- `/seo-aeo-audit` slash command, Cursor rule with the contracts embedded inline,
  audit-report and action-plan templates.
- Structural validator (`test/validate.py`) with four-way version sync, reference
  and script checks, and a functional test suite for the auditor
  (`test/test_page_audit.py`) running against two offline fixtures.
- Distribution: Claude Code plugin, vercel skills CLI, npx installer, Cursor,
  POSIX `install.sh`.
