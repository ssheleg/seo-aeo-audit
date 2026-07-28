# Changelog

## v0.6.1 — 2026-07-28

Open-source hygiene pass — the repo is public, so the files a first-time
contributor looks for now exist.

### Added
- `CONTRIBUTING.md` — the evidence-tier rule stated as the first thing a
  contributor reads: no claim without a tier, `benchmarks.md` owns the numbers,
  dated facts stay dated, conflicting sources are both named and the claim is
  demoted rather than decided, and manipulative tactics are declined.
- `CODE_OF_CONDUCT.md`, issue forms and a pull-request template.
- README gained a Contributing section and lists the new files in the repo map.

## v0.6.0 — 2026-07-28

Release-readiness pass: a full read of every file in the repo looking for claims
that contradict each other, claims that contradict the code, and half-finished
work. Everything found is fixed here.

### Fixed
- **Spelling standard applied to the last holdouts.** `honours`, `catalogue`,
  `Analyses`, `labelled`, `normalised`, `behaviour`, `fulfils` and `summarise`
  across the references, the changelog and the research notes; the auditor's
  `analyse()` renamed to `analyze()` with its call sites and test updated. The
  repo standard is US spelling — a mixed standard has already cost one broken
  anchor here.

### Fixed — contradictions

- **One tier for the ChatGPT-versus-Google-index claim.** `technical-checks.md`
  A1 carried it as `STUDY`, while `aeo-geo.md` F4, `myths.md` and
  `benchmarks.md` all record it as a single FIELD case whose *dependency* reading
  is HYPOTHESIS because a Bing-only counter-case points the other way. A1 now
  matches them and points at the file that owns the conflict; what stays
  `CONFIRMED` there is the part that is documented — Googlebot cannot be split by
  purpose.
- **Alice AI naming, actually swept.** v0.5.0 announced the rename and left
  `Alisa AI` / `Алиса AI` in six places (SKILL.md, `aeo-geo.md`,
  `benchmarks.md`, `algorithm-updates.md`, `measurement.md`, `growth-plays.md`)
  plus the research notes. English text now reads **Alice AI** everywhere, with
  `Алиса` kept as the native name in parentheses on first mention per file.
- **The myth guard says how much of itself it is showing.** SKILL.md and the
  Cursor rule each list thirteen refused tactics while the README advertises 29;
  both now say they are the short list and where the other sixteen live.
- **"No install script" removed from the README.** The repo ships two installers
  (`install.sh`, `bin/seo-aeo-audit.js`); what is actually true — and what the
  sentence was reaching for — is that there are no npm lifecycle scripts and
  nothing runs unless you run it.
- **Play list re-ordered.** `G15` sat after `G28` and `P4` after `P5`; the 59
  plays now read in order.
- **Research notes re-dated.** They were labeled "working notes behind v0.1.0"
  while carrying the v0.3.0 and v0.4.0 source passes.
- Every changelog entry carries its release date.

### Fixed — the bundled auditor

- **Repeated `X-Robots-Tag` headers no longer collapse.** `dict(headers)` kept
  only the last one, so a response sending `noindex` on one line and `nosnippet`
  on the next lost a blocker. Headers are now merged, and a regression test
  covers both directives surviving.
- **A gzip body truncated by `--max-bytes` is salvaged** instead of failing the
  whole URL with `EOFError`; if nothing decodes, the error says to raise the cap.
- **Non-HTML responses are refused.** Auditing a PDF or an image as HTML produced
  confident nonsense; the fetch now stops on the declared content type.
- `--url-list` skips indented comment lines and trims each URL.
- `--base-url` outside `--file` mode warns instead of being silently ignored.

### Fixed — rendering and structure

- The plan skeleton in `deliverable-templates.md` nested a fenced block inside a
  fenced block, which broke the rendering of everything after "Sequencing".
  Outer fences widened; the copies the validator compares are unchanged.
- README repo layout now lists the installers, the manifest, the fixtures and CI.

### Added — guardrails, so these classes of defect cannot come back

- The validator resolves **every reference anchor the auditor emits** against the
  real headings in the reference files. This is the defect class that produced
  the v0.1.1 broken cross-reference; nothing was checking it. CI proves the check
  can fail by renaming a heading.
- Relative markdown links are now checked **anchor and all**, not just the file.
- CI runs with `permissions: contents: read` and cancels superseded runs.
- `.gitignore` covers Python bytecode.

## v0.5.0 — 2026-07-28

### Changed
- Description restructured English-first — every Russian trigger paired with its
  English equivalent — and `"SEO change plan" / "план правок по SEO"` added as a
  missing pair.
- Yandex's assistant is now written **Alice AI** in English throughout, with
  `Алиса` kept once as the native name, across the references, the changelog and
  the research distillation.
- README is English-only, with a plain statement of what the audit gives you and
  an author/links block.

## v0.4.1 — 2026-07-28

Security hardening of the bundled auditor, plus an explicit statement of what the
skill does at runtime.

- **URL scheme guard.** `page_audit.py` passed operator-supplied URLs straight to
  `urlopen`, which happily resolves `file://` — so a crafted `--url-list` could
  have made the auditor read local files. It now refuses anything that is not
  http/https before issuing a request, and refuses redirects that leave http(s).
  Three regression tests cover it.
- The default User-Agent no longer carries a version string that drifts out of
  sync with the release.
- **`SECURITY.md`**: what each component does at runtime, the exact network
  behavior (plain GETs, no cookies or credentials, bounded by timeout and byte
  cap, writes nothing, no telemetry), the defensive-only stance on adversarial
  material, and a three-command recipe to verify the whole attack surface
  yourself. Shipped in the npm tarball and summarized in the README.

## v0.4.0 — 2026-07-28

Deep extraction pass over the full source corpus, section by section, followed by
a reconciliation pass over the whole set. +1,725 lines across all 19 contracts.

**Extraction** — one pass per audit track, each mining the same corpus for what
its own track was still missing:

- **A/B technical**: edge/WAF blocks that answer crawlers above `robots.txt`;
  header-delivered directives (`X-Robots-Tag`, `Link: rel="canonical"`) invisible
  in view-source; bot identity and Web Bot Auth; "removing `noindex` is not a
  recovery lever"; indexing services force crawling, never indexing; the
  leaky-redirect migration failure that kept both hosts crawled for a year.
- **C architecture**: crawl frequency as an architecture output (with the
  waste-40%→10% profile at a flat budget); the NavBoost floor below which links
  cannot lift a page; subfolder membership over visual navigation; local and
  multi-location architecture (PageRank is not used in Local Search); what to
  split-test rather than ship.
- **D/E content**: one query, two surfaces; auditing modules rather than prose;
  the two-wave mechanism behind the content collapse; volume as the aggravating
  variable; refresh contamination (models delete the sentences that earned the
  position) and cohort measurement of refreshes; the money-template sweep.
- **F AEO/GEO**: Google's own AIO chain description; the retrieval budget stack;
  per-engine rows rebuilt (Gemini arbitration, ChatGPT `resultsource` buckets,
  Deep Research re-read behavior, Brave/Claude gating, Perplexity localization,
  Alice AI / Алиса with RU figures); slots you do not control; the KDD benchmark with its
  omissions stated.
- **G entity/brand**: Wikidata quantified and bounded; the mention-manipulation
  guardrail; cross-platform rating divergence as an attack signature; mention
  volume versus semantic cluster; where the verdict is actually hosted; retrieval
  added as a fourth state next to mention/citation/recommendation.
- **H experience/conversion**: CTR curves as perishable; usefulness judged on
  function; the mobile-only failure inventory; the render-blocking inventory; the
  one legitimate exception to minimum form fields; self-reported attribution;
  the AI-impression → offline-conversion ladder; conversion data as bidding fuel.
- **I risk**: rich results withheld as a sanction; takedown abuse as a campaign
  rather than an incident; canonical-hijack loss signature; behavioral-poisoning
  timing; autocomplete and volume injection; entity records as an attack surface;
  link-risk scale thresholds — all detection-and-defense only.
- **J measurement**: aggregate before the model sees it; four reporting artifacts
  that read as findings; personalization contaminating capture; the restored
  cadence section; six horizon rows; five more things not to measure. Benchmarks
  gained samples and dates on every row, a user-self-report section and a
  contested-metrics section.
- **Plays and experiments**: 18 new plays (B8–B11, L9–L12, G22–G28, P6–P8) and
  four new experiment-design rules with five documented results.
- **Model, myths, updates, tooling**: how a ranking change actually ships; the
  retrieval/scoring/re-ranking stack with demotion and removal as separate
  machinery; five new myths; 14 new dated platform rows; six tool-routing rows
  and seven DevTools recipes.

**Reconciliation** — one pass over all 19 files:

- Sixteen contradictions resolved by naming both studies and demoting the
  contested direction to HYPOTHESIS rather than picking a winner (schema on
  ChatGPT, rank-1 versus Bing-only AI visibility, "crawled – not indexed" cause,
  zero-click direction, Wikipedia's weight by query class, literal phrasing
  versus title match).
- Click-economics rebuilt as four distinct measures with an explicit note that
  none refutes the others; vendor-sourced rows tagged undated.
- Duplication removed with a single owner per fact: link velocity →
  threats-and-defense, read budget → architecture-and-equity, index tiering,
  migration protocol and out-of-stock → technical-checks, every dated figure →
  benchmarks.
- Coverage gaps filled: **hreflang and international duplication** (new
  technical-checks §B2, engine-documented), fabricated information gain as a
  detection signature, publisher licensing posture, rank-tracker vendor
  continuity, EU DMA exposure.
- Spelling drift swept again; SKILL.md flow and the Cursor rule re-verified
  against the reference set.

## v0.3.1 — 2026-07-28

Consistency pass across the whole flow, plus a rewritten README.

- **One evidence ladder.** SKILL.md described the tooling order by convenience
  while `tooling.md` ordered it by evidence strength — the two now share a single
  ordering (logs → Search Console → crawl → field data → third-party → manual),
  and the rung a finding rests on caps its evidence tier.
- **One stance on structured data.** The schema position was stated three
  different ways across `myths.md`, `aeo-geo.md` and `onpage-checks.md`; the
  canonical stance now lives in `myths.md` (an eligibility and entity aid on
  specific surfaces, never a ranking or citation lever) and the others point at
  it.
- **Page-experience claim reconciled.** The speed case study in
  `experience-signals.md` and play `G8` are now labeled as bundling satisfaction
  signals, so they no longer read as a contradiction of the tiebreaker framing in
  `ranking-model.md`.
- **Keywords reconciled.** `ranking-model.md` now says explicitly that the
  failure mode is scaffolding a page on a keyword list, not using keywords —
  matching `intent-and-content.md` E2b.
- **Tier discipline in the four new contracts**: each states what it licenses
  (`ranking-model` = vocabulary and mechanism; `onpage-checks` = existence
  confirmed, impact tiered separately; `demand-and-conversion` = platform
  mechanics confirmed, vendor case numbers FIELD; `tooling` = the rung caps the
  tier).
- **Flow documented**: the mechanical sweeps are now named in Step 2 of the audit
  procedure, and the read-budget and attribution numbers have a single canonical
  home with cross-references instead of parallel copies.
- Spelling normalized again after the new files (one standard across references,
  Cursor rule and scripts).
- **README rewritten**: what the skill is, install and update commands up front,
  the audit flow, what knowledge ships inside and what each area is worth, data
  freshness and the refresh policy, and the link to the umbrella repo for the
  whole skill family.

## v0.3.0 — 2026-07-28

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

## v0.2.0 — 2026-07-28

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

## v0.1.1 — 2026-07-28

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
  behavior/behavior, optimisation/optimization…), which also broke one anchor.
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

## v0.1.0 — 2026-07-28

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
