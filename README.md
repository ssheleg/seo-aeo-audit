# seo-aeo-audit

[![validate](https://github.com/ssheleg/seo-aeo-audit/actions/workflows/validate.yml/badge.svg)](https://github.com/ssheleg/seo-aeo-audit/actions/workflows/validate.yml)
[![npm](https://img.shields.io/npm/v/@ssheleg/seo-aeo-audit)](https://www.npmjs.com/package/@ssheleg/seo-aeo-audit)
[![license](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

**An agent skill that audits a website for search *and* answer-engine visibility,
proves every finding with evidence, and hands back a prioritized plan of
changes.** Part of the [sshlg-skills](https://github.com/ssheleg/sshlg-skills)
family.

Most SEO audits hand over a checklist and a health score. This one produces a
diagnosis: what is wrong, where you can see it, why it happens, what to change,
what it is worth, when to expect movement, and how you will know it worked —
across Google, Yandex and Bing, and across AI Overviews / AI Mode, ChatGPT,
Perplexity, Claude, Copilot, Gemini and Yandex Alice AI.

---

## Install

**Claude Code plugin** (recommended for Claude Code):

```
/plugin marketplace add ssheleg/seo-aeo-audit
/plugin install seo-aeo-audit@seo-aeo-audit
```

**Any other agent** (Cursor, Codex, OpenCode, Zed, Windsurf, Gemini CLI, 70+):

```bash
npx skills add ssheleg/seo-aeo-audit
```

**npx installer** (no clone; installs into `~/.claude`):

```bash
npx github:ssheleg/seo-aeo-audit
```

## Update

**Update the whole family — one package, every agent.** A bundle with one member current and the
rest stale is a combination nobody tested:

```bash
npx sshlg-skills update               # installed but behind — updates everything
npx sshlg-skills install              # nothing installed yet
npx --yes sshlg-skills@latest list    # what the current release of each member is
```

Restart your agent afterwards: skills and hooks load at session start, so the session that updates
is not the session that gets the new ones.

<details><summary>Updating this one member only</summary>

```
claude plugin marketplace update seo-aeo-audit && claude plugin update seo-aeo-audit@seo-aeo-audit
```

```bash
npx skills update seo-aeo-audit --global --yes
```

</details>

Keep **one channel per agent** — do not leave a plain `~/.claude/skills/` copy
next to the Claude Code plugin, or the stale copy shadows the fresh one. Restart
Claude Code after updating.

## Use

```
/seo-aeo-audit example.com
/seo-aeo-audit traffic dropped in May, /blog only
/seo-aeo-audit why doesn't ChatGPT cite us for "invoice reconciliation"
```

The skill detects the mode (first audit, re-audit, single-question diagnosis),
states which inputs it has and which it is missing, runs the tracks in scope, and
ends with exactly one recommended next action. Deliverables land in
`docs/seo/audit-<date>.md` and `docs/seo/plan-<date>.md`.

---

## The audit flow

| # | Track | The question it answers |
|---|---|---|
| A | Access & indexation economics | Can bots fetch, render and afford to index this? Where is crawl budget burned? |
| B | Canonicalization & duplication | Which URL is the one true URL — and does the engine agree? |
| C | Architecture & link equity | Do the money pages get authority, depth and crawl frequency? |
| D | Intent & SERP fit | Does each page match what the SERP rewards? Do pages fight each other? |
| E | Content value | Is there a reason to rank this that an AI cannot replicate? |
| F | Extractability & AEO/GEO | Can an answer engine retrieve, read and quote the answer? |
| G | Entity & brand consensus | Do the models know what this brand is — and name it? |
| H | Experience, conversion & attribution | Do users finish the task, does it convert, and is the conversion measured? |
| I | Risk & threats | Penalties, hijacks, prompt injection, takedown abuse, adversaries. |
| J | Measurement | Will anyone be able to tell whether the plan worked? |

Each track has two halves: the diagnosis (what is wrong and why) and a mechanical
sweep for completeness. Findings are triaged with
`priority = (impact × confidence) / effort` — where confidence is the evidence
tier — and grouped into **Blockers → Leaks → Gains → Experiments**.

### Rules the skill will not break

- **Evidence or silence.** Every finding names the observation, its location, the
  value and the date. No finding that was not verified on the site being audited.
- **Tiered claims.** Every recommendation carries `CONFIRMED` · `STUDY` · `FIELD`
  · `HYPOTHESIS`, and a hypothesis never outranks a confirmed blocker.
- **Diagnose before prescribing.** "Add schema" is not a diagnosis.
- **A myth guard** that refuses 30 popular tactics with published
  counter-evidence, and offers the working alternative instead.
- **Defense, not offense.** Adversarial techniques appear only as things to
  detect and withstand, never as recommendations.
- **Honest horizons.** Every change ships with a verification method and a
  realistic timeframe — including "we cannot promise a date".

---

## What knowledge is packed inside

Twenty-one reference contracts ship *inside* the skill, so they travel to every
agent, not just Claude Code. This is the substance:

| Area | What it holds | Why it is worth having |
|---|---|---|
| **Ranking model** | Systems vs signals vs "factors", the three that actually carry weight, what E-E-A-T really is, query-dependent weighting, personalization and locality | Stops audits built on documentation reshuffles and listicle "factor" claims |
| **Technical & indexation** | Crawl access, rendering traps, robots wildcard failures, index tiering, crawl-budget killers, tracking parameters versus facets, soft-404 collapse patterns, canonical traps, migration protocol, plus a full mechanical sweep | The failure modes that silently cost the most traffic, each with its exact observable |
| **Architecture & equity** | Equity distribution, hub-and-cluster, orphans, depth, anchor practice, and the answer-engine **read budget** | Explains why money pages starve while the homepage hoards authority — and why navigation now costs twice |
| **Intent & content value** | The four intents and the page types they reward, cannibalization mechanics, information-gain findings, the content types that survive zero-click, and the AI-content patterns that now hurt | Turns "write better content" into a specific, testable page-level decision |
| **AEO / GEO mechanics** | How an answer is actually built (fan-out → retrieval → grounding → arbitration), what correlates with citation, per-engine retrieval paths, extractability rules, and a ready prompt set for measuring brand presence | The part most audits either skip or fill with vendor folklore |
| **Entity & brand consensus** | Cross-profile consistency, the entity graph, ghost citations (cited but not recommended), and how review sentiment drives AI verdicts | Explains why a technically perfect site still gets no recommendation |
| **Experience & conversion** | CWV triage order, satisfaction-signal mechanics, CRO × SEO evidence, conversion elements per template, lead capture, the attribution gaps (calls, offline, AI referrals, cross-device), paid × organic alignment | The post-click half of the funnel that audits usually leave on the table |
| **Risk & defense** | Penalty behavior, subdomain and registrar risk, indirect prompt injection, takedown abuse, canonical hijacking, behavioral poisoning, proportionate link-risk handling | Turns "we got hit" into a specific, checkable hypothesis |
| **Google update timeline** | Every core, spam and Discover update with start and completion dates, the platform changes that retired old tactics, and an update-response protocol | Lets the skill date-align a traffic curve instead of guessing |
| **Growth plays** | 60 plays, each with the trigger that justifies it, the mechanism, the observed effect and its evidence tier | A plan built from things that measurably worked, not from best-practice lists |
| **Benchmarks** | Dated figures for surface reach, click economics, citation mechanics, read budget, content correlations, operational targets and industry context | Lets the report size an opportunity with numbers instead of adjectives |
| **Link building** | Target selection, both collection modes (Search Console reachable or not), anchor discipline, the exclusions a brief must name, and the CSV column contract | Turns the audit into a brief a contractor can execute without misreading an assumption as a measurement |
| **Bulk market data** | The Prowl MCP as a rung-5 source — ~408 provider tools behind one pay-per-call endpoint, routed by track, with measured per-call costs and the operating gotchas | Gives a no-seat audit a second independent index, which is what makes a demand finding hold up |
| **Method** | Evidence tiers, experiment design, the myth guard, check → tool routing with DevTools recipes, and the deliverable templates | Keeps two different runs of the audit comparable |

### Data freshness

- **Verified as of 2026-07-30.** Roughly 4,600 lines of distilled, dated
  reference material. The update timeline covers March 2025 → June
  2026; every benchmark carries its own date and sample size.
- The skill ships a **refresh routine**: re-fetch the update sources, append the
  new rows, re-check whether a shipped change retires a myth or invalidates a
  benchmark, and downgrade any claim older than ~18 months that nothing has
  confirmed since.
- Where credible evidence conflicts — and in AI-surface research it regularly
  does — the claim is demoted to a hypothesis and routed to the experiment path
  instead of being asserted.

---

## The bundled scripts

### `page_audit.py` — per-page evidence

`scripts/page_audit.py` — stdlib only, nothing to install, works offline:

```bash
python3 scripts/page_audit.py --url https://example.com/pricing
python3 scripts/page_audit.py --file saved.html --base-url https://example.com/pricing
python3 scripts/page_audit.py --url-list urls.txt --format json > audit.json
```

It catches what eyeballing misses: `content="none"` (≡ `noindex, nofollow`), a
`meta refresh` + `noindex` conflict, a canonical silently discarded because it
carries `media`/`type`/`hreflang`, invalid JSON-LD, missing `alt` text, a price
that exists in the source but not in extractable text (so engines cite an
aggregator for your pricing), and the **answer-engine read budget** — how much of
a ~5,700-character first read your navigation eats before the answer.

### `gsc_pull.py` — the half a crawl cannot see

Search Console evidence: which queries a property actually surfaces for, at what
position, and whether a drop is a **cliff that held** rather than a decline.
Stdlib only; auth is local Application Default Credentials, so no key file goes
near the repo.

```bash
python3 scripts/gsc_pull.py --list
python3 scripts/gsc_pull.py --site sc-domain:example.com --quota-project my-proj
```

It prints the **position split** first, deliberately. Ranking findings by
impressions is the mistake this script exists to prevent: a large impression
count beyond position 30 is usually the biggest number in the account and worth
the least, while a small cluster inside the top 20 carries most of the clicks.

The cliff detector only reports a drop that **stayed down** — a single bad day
is a reporting gap, and updates redistribute rather than zero a property for
weeks. When it fires, it says so plainly and points at what the API cannot
answer: Manual Actions and Index Coverage are web-UI only, at every scope.

Three auth gates fail independently with unhelpful errors — the OAuth scope, the
API being enabled on a project the account can *use*, and the quota-project
header that client libraries add and raw HTTP does not. The script names which
one you hit.

`scripts/url_inspection.py` — asks the index rather than inferring from a fetch.
The Google-selected canonical against the declared one, coverage state, robots
verdict, last crawl: the engine's own answers, so findings built on them are
`CONFIRMED` rather than inferences. Quota is 2000/day and 600/minute per
property, so it samples — a representative URL per template, plus the pages a
finding is about.

```bash
python3 scripts/url_inspection.py --site sc-domain:example.com --urls https://example.com/pricing
```

`scripts/sitemap_audit.py` — the published side of "indexed vs published per
template": declared URLs clustered into the template families the site actually
ships, derived from its own URLs rather than a guessed taxonomy. It does not
detect orphans; a sitemap carries no link graph, and inferring them from path
shape would be a guess wearing the clothes of a finding.

`scripts/psi_pull.py` — Core Web Vitals with field (CrUX) and lab (Lighthouse)
reported separately, judged at the 75th percentile. Where CrUX has no data for a
URL that is reported as absent, never as a pass, and the lab score never stands
in for it.

```bash
python3 scripts/sitemap_audit.py --url https://example.com/sitemap.xml
python3 scripts/psi_pull.py --url https://example.com/pricing
```

Every one of them states its own blind spot in its output. That is the eighth
non-negotiable: an instrument that cannot see something must not let its silence
read as a measurement.

## Link-building extraction

The audit also produces a deliverable for someone else to execute: a brief plus
a keyword CSV a contractor can work from. Two modes — with Search Console, every
row is measured; without it, candidates are derived from what the site sells.

The rule that makes it safe to hand over: **measured and assumed never share a
column.** A `source` column separates them, and the volume cells of an
unmeasured row stay **blank, not zero** — `0` reads as "measured, no demand",
blank reads as "nobody has checked". An auditor who overstates a finding wastes
their own time; a brief that overstates one spends a client's budget.

See `references/linkbuilding.md` for target selection, the exclusions a brief
must name, anchor discipline, and the CSV column contract.

## Security posture

Text plus two stdlib Python scripts, and nothing else runs. `page_audit.py` makes
plain http(s) GETs to the URLs you hand it — any other scheme is refused before a
request is made, redirects off http(s) are refused, non-HTML responses are
refused, no cookies or credentials are sent, responses are bounded by
`--timeout`/`--max-bytes`, and it writes nothing. No dependencies, no npm
lifecycle scripts, no telemetry. The installers (`install.sh`,
`bin/seo-aeo-audit.js`) only copy files into `~/.claude/` and only when you run
them. Full statement in [SECURITY.md](SECURITY.md).

Marketplace scanners rate skills that ship executable code above documentation-only
skills by default; that rating is about the *category*, not a finding — the audit
trail above is what it takes to check the claim yourself.

## Repo layout

```
.claude-plugin/marketplace.json      root manifest
plugins/seo-aeo-audit/
  ├── .claude-plugin/plugin.json
  ├── commands/seo-aeo-audit.md      slash command
  └── skills/seo-aeo-audit/
      ├── SKILL.md                   the procedure
      ├── references/*.md            21 contract files (shipped on every channel)
      └── scripts/                   page_audit.py, gsc_pull.py (stdlib only)
cursor/rules/seo-aeo-audit.mdc       Cursor rule (contracts inlined)
templates/*.template.md              deliverable skeletons for non-agent use
bin/seo-aeo-audit.js                 npx installer (zero dependencies)
install.sh                           POSIX installer for a local clone
package.json                         npm manifest for the installer CLI
CONTRIBUTING.md                      evidence discipline, checks, where things go
SECURITY.md                          what runs, what it touches, how to verify
test/validate.py                     structural validator
test/test_page_audit.py              functional tests (offline fixtures)
test/fixtures/*.html                 pages the auditor is tested against
.github/workflows/validate.yml       CI, including negative self-tests
docs/research/                       provenance behind every claim in the references
```

## Development

```bash
python3 test/validate.py        # structure, version sync, references, links, anchors, drift
python3 test/test_page_audit.py # auditor behavior against offline fixtures
node --check bin/seo-aeo-audit.js
bash -n install.sh
```

Version sync is a hard rule: `marketplace.json`, `plugin.json`, `package.json`
and the top `CHANGELOG.md` entry carry the same semver. Every finding the auditor
emits points at a reference section, and the validator resolves those anchors
against the real headings — a renamed heading fails the build. CI proves each
check can fail by corrupting a copy of the repo and requiring a non-zero exit.

## Part of a family

`seo-aeo-audit` is one of the
[ssheleg skills](https://github.com/ssheleg/sshlg-skills) — install or update
them all with a single command:

```bash
npx sshlg-skills install
npx sshlg-skills update
```

## What this gives you

Vibe-coded sites ship fast and land invisible: rendered entirely client-side, no
canonical story, a sitemap nobody ever submitted, and nothing an answer engine
can quote. Then the advice you get is a 200-row checklist that never says what
to do first.

- **Blockers first.** If the site cannot be crawled, rendered or indexed,
  nothing else matters — the audit says so and stops, instead of burying it on
  row 140.
- **Answer engines, not only Google.** What ChatGPT, Perplexity, Copilot and AI
  Overviews can actually extract from your pages, and why they cite a competitor
  instead of you.
- **Evidence or silence.** Every finding carries an observation, a location and
  a date; every recommendation carries an evidence tier, so you can tell proven
  from worth-testing at a glance.
- **A myth guard.** 29 popular tactics with published counter-evidence are
  refused outright — the ones an agent will otherwise recommend with total
  confidence.
- **The output is a prioritized change plan** with verification steps and honest
  horizons, not a score out of 100.

## Contributing

Issues and pull requests are welcome — see
[CONTRIBUTING.md](CONTRIBUTING.md). The short version: every claim carries an
evidence tier, `benchmarks.md` owns the numbers, dated facts stay dated, and
`python3 test/validate.py` plus `python3 test/test_page_audit.py` must pass.
Everyone taking part is expected to follow the
[Code of Conduct](CODE_OF_CONDUCT.md).

## Author

Built by ssheleg — [sshlg.me](https://sshlg.me)

- X / Twitter — [@fuck_this_year](https://x.com/fuck_this_year)
- Telegram — [@sshlg](https://t.me/sshlg)

Part of the [ssheleg skill family](https://github.com/ssheleg/sshlg-skills):
`super-ux`, `task-pipeline`, `agent-sync`, `make-skill`, `sheleg-design`, `seo-aeo-audit`.
**The family installs and updates as one package**, for every agent you use — a bundle with one
member current and the rest stale is a combination nobody tested:

```bash
npx sshlg-skills install              # nothing installed yet — the whole family, any agent
npx sshlg-skills update               # installed but behind — updates everything
npx --yes sshlg-skills@latest list    # what the current release of each member is
```

Restart your agent afterwards: skills and hooks load at session start, so the session that
updates is not the session that gets the new ones.

## License

MIT © 2026 ssheleg.
