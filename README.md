# seo-aeo-audit

[![validate](https://github.com/ssheleg/seo-aeo-audit/actions/workflows/validate.yml/badge.svg)](https://github.com/ssheleg/seo-aeo-audit/actions/workflows/validate.yml)
[![npm](https://img.shields.io/npm/v/@ssheleg/seo-aeo-audit)](https://www.npmjs.com/package/@ssheleg/seo-aeo-audit)
[![license](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

**Evidence-first website audit for search *and* answer engines, ending in a
prioritized change plan.**

Most SEO audits produce a checklist. This one produces a diagnosis: what is
wrong, where you can see it, why it happens, what to change, how much it is
worth, and how you will know it worked — across Google, Yandex and Bing *and*
across AI Overviews / AI Mode, ChatGPT, Perplexity, Claude, Copilot, Gemini and
Алиса AI.

## What it does

Ten tracks, blockers first:

| Track | Question |
|---|---|
| A access & indexation economics | Can bots fetch, render and afford to index this? |
| B canonicalization | Which URL is the one true URL — and does the engine agree? |
| C architecture & link equity | Do the money pages get authority, depth and crawl frequency? |
| D intent & SERP fit | Does the page match what the SERP rewards? Do pages fight each other? |
| E content value | Is there a reason to rank this that AI cannot replicate? |
| F extractability & AEO/GEO | Can an answer engine retrieve, read and quote the answer? |
| G entity & brand consensus | Do the models know what this brand is — and name it? |
| H experience signals | Do users complete the task, or bounce back to the SERP? |
| I risk & threats | Penalties, hijacks, prompt injection, takedown abuse, adversaries. |
| J measurement | Will anyone be able to tell whether the plan worked? |

Then it triages (`priority = (impact × confidence) / effort`, where confidence is
the evidence tier) and writes two files: a findings report and a change plan with
verification steps, honest horizons and rollbacks.

### Opinionated on purpose

- **Evidence or silence.** Every finding names the observation, its location, the
  value and the date. Every recommendation carries a tier: CONFIRMED · STUDY ·
  FIELD · HYPOTHESIS — and a HYPOTHESIS never outranks a CONFIRMED blocker.
- **A myth guard.** `llms.txt` as a ranking lever, Markdown mirrors, "chunk your
  content", schema volume for AI citations, FAQPage rich results, date bumps as
  freshness, disavowing on a third-party toxicity score, self-promotional "best
  [category]" listicles, scaled AI content — all refused, with the evidence and
  the working alternative.
- **Update-aware.** Ships a dated Google update timeline (core, spam, Discover —
  through June 2026), the platform changes that retired old tactics, an
  update-response protocol, and a refresh routine so each skill release folds in
  what shipped since. Source of truth:
  [SEJ's algorithm history](https://www.searchenginejournal.com/google-algorithm-history/)
  plus the Search Status Dashboard.
- **Growth plays, tiered.** ~45 plays with trigger, mechanism, observed effect
  and evidence tier — not a checklist of best practices.
- **Defense, not offense.** Adversarial techniques (prompt injection, canonical
  hijacks, fake DMCA waves, behavioral poisoning, fabricated consensus) appear
  only as things to detect and withstand.

### The bundled auditor

`scripts/page_audit.py` (stdlib only, offline-capable) collects the mechanical
evidence per template:

```bash
python3 scripts/page_audit.py --url https://example.com/pricing
python3 scripts/page_audit.py --file saved.html --base-url https://example.com/pricing
python3 scripts/page_audit.py --url-list urls.txt --format json > audit.json
```

It flags the traps that eyeballing misses: `content="none"` (≡ `noindex,
nofollow`), a `meta refresh` + `noindex` conflict, a canonical silently discarded
because it carries `media`/`type`/`hreflang`, invalid JSON-LD, missing `alt`
text, a price that exists in the source but not in extractable text (so engines
cite an aggregator for your pricing instead), and the **answer-engine read
budget** — how much of ChatGPT Deep Research's ~5,700-character first read your
navigation eats before it reaches your answer.

## Install

**Claude Code plugin** (recommended for Claude Code):

```
/plugin marketplace add ssheleg/seo-aeo-audit
/plugin install seo-aeo-audit@seo-aeo-audit
```

**Any agent (Cursor, Codex, OpenCode, Zed, 70+)** via the skills CLI:

```
npx skills add ssheleg/seo-aeo-audit
```

**npx installer** (no clone, installs into `~/.claude`):

```
npx github:ssheleg/seo-aeo-audit
```

After publish, the short form works too: `npx @ssheleg/seo-aeo-audit`.

**POSIX fallback**: `git clone` then `./install.sh` (macOS/Linux only — on
Windows use npx, the plugin, or the skills CLI).

Keep **one channel per agent**: do not add a plain `~/.claude/skills/` copy next
to the Claude Code plugin, or the stale copy will shadow the fresh one.

## Use

```
/seo-aeo-audit example.com
/seo-aeo-audit traffic dropped in May, /blog only
/seo-aeo-audit why doesn't ChatGPT cite us for "invoice reconciliation"
```

The skill detects the mode (new audit, re-audit, single-question diagnosis),
reports available and missing inputs, runs the in-scope tracks, and finishes with
exactly one recommended next action.

## Repo layout

```
.claude-plugin/marketplace.json      root manifest
plugins/seo-aeo-audit/
  ├── .claude-plugin/plugin.json
  ├── commands/seo-aeo-audit.md      slash command
  └── skills/seo-aeo-audit/
      ├── SKILL.md                   the procedure
      ├── references/*.md            15 contract files (shipped on every channel,
      │                                incl. the deliverable skeletons)
      └── scripts/page_audit.py      stdlib page auditor
cursor/rules/seo-aeo-audit.mdc       Cursor rule (contracts inlined)
templates/*.template.md              same skeletons for non-agent use (validator
                                     checks they match the embedded copy)
test/validate.py                     structural validator
test/test_page_audit.py              functional tests (offline fixtures)
```

## Development

```bash
python3 test/validate.py        # structure, version sync, references, links
python3 test/test_page_audit.py # auditor behavior against offline fixtures
node --check bin/seo-aeo-audit.js
bash -n install.sh
```

Version sync is a hard rule: `marketplace.json`, `plugin.json`, `package.json`
and the top `CHANGELOG.md` entry carry the same semver, and the validator
enforces it.

## Sources

The audit tracks are distilled from primary engine documentation, published
multi-site studies, patent and leak analysis, and practitioner field reports from
2026 — every number in `references/benchmarks.md` carries its date and sample.
Search surfaces move fast: re-check anything older than about 18 months before it
enters a plan.

---

## По-русски

`seo-aeo-audit` — скил для **аудита сайта под поиск и AI-ответы**, который
заканчивается не чек-листом, а планом правок: что менять, где именно, почему
(механизм + уровень доказательности), сколько это стоит и как проверить
результат.

Десять треков: доступность и экономика индексации · каноникализация ·
архитектура и распределение веса · интент и каннибализация · ценность контента ·
извлекаемость и AEO/GEO · сущности и консенсус о бренде · поведенческие сигналы ·
риски и угрозы · измеримость.

Правила жёсткие: **каждый вывод с доказательством** (что наблюдали, где, когда) и
с уровнем доказательности (CONFIRMED / STUDY / FIELD / HYPOTHESIS). Мифы
(`llms.txt`, markdown-зеркала, «нарежьте контент на чанки», разметка ради
AI-цитирований, обновление даты вместо апдейта, массовый ИИ-контент, самопиарные
подборки «лучший X») в план не попадают — вместо них даётся то, что реально
работает.

Установка: `/plugin marketplace add ssheleg/seo-aeo-audit` +
`/plugin install seo-aeo-audit@seo-aeo-audit`, либо
`npx skills add ssheleg/seo-aeo-audit` для остальных агентов.
Запуск: `/seo-aeo-audit example.com`.
