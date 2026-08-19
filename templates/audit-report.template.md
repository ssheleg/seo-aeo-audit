# SEO / AEO audit — {{SITE}}

- **Date:** {{YYYY-MM-DD}}
- **Scope:** {{whole site | template | question}}
- **Markets / languages:** {{...}}
- **Inputs available:** {{GSC, Bing WMT, analytics, logs, crawl export, MCP tools}}
- **Inputs missing (and what that limits):** {{...}}
- **Previous audit:** {{link or "none"}}

## Executive summary

1. {{blocker one — one sentence, with the size of the effect}}
2. {{blocker two}}
3. {{biggest leak}}
4. {{biggest gain}}
5. **Do this first:** {{the single next action}}

## Baseline

| Metric | Value | Period | Source |
|---|---|---|---|
| Organic clicks | | | |
| Organic impressions | | | |
| Indexed vs published URLs | | | |
| Top revenue pages / positions | | | |
| AI mention rate (per engine) | | | |
| AI crawler fetches (per agent) | | | |

## Findings

Repeat this block per finding, most severe first.

### F-{{n}} — {{short title}}

- **Track:** {{A–K}}
- **Issue:** {{what is wrong}}
- **Impact:** {{1–5}} — {{traffic/revenue framing}}
- **Evidence:** {{observation, location, value, date}}
- **Evidence rung:** {{1 logs | 2 Search Console | 3 crawl | 4 field data | 5 third-party index | 6 manual fetch}} — the rung caps the tier (tooling.md)
- **Cause:** {{the mechanism, not the symptom}}
- **Fix:** {{the specific change}}
- **Effort:** {{1–5 engineering days, including release}}
- **Evidence tier:** {{CONFIRMED | STUDY | FIELD | HYPOTHESIS}}
- **Priority:** {{(impact × confidence) / effort}}
- **Verification:** {{the exact observable that proves it worked}}

## Not checked

Anything **outside** the track list — a market, a template, a subdomain, a surface
nobody had access to. Every track's own gap belongs in Track coverage below, where
it carries a status from the closed vocabulary instead of a sentence.

| Area | Why not | What it would take |
|---|---|---|

## Track coverage

Status is a **closed vocabulary** — `observed` · `partial` · `unlooked` ·
`blocked-by <gate>` · `out-of-scope`. Any status but `observed` or `unlooked` owes
a reason in Notes. Nothing else is a status: a blank cell, a tick or a sentence
here is the defect this table exists to prevent, because a clean track and a track
that never ran then render identically.

Do not type this table — seed it from the instruments, which already know which
sources answered:

```bash
python3 "$SKILL_DIR/scripts/preflight.py" --origin https://example.com --format coverage
```

The seed never writes `observed`: preflight runs before any track does. So a row
left as seeded reads `unlooked`, and forgetting to edit this table produces
*nobody looked*, never a clean report.

| Track | Status | Notes |
|---|---|---|
| A access & indexation | unlooked | |
| B canonicalization | unlooked | |
| C architecture & equity | unlooked | |
| D intent & SERP fit | unlooked | |
| E content value | unlooked | |
| F extractability / AEO | unlooked | |
| G entity & brand | unlooked | |
| H experience signals | unlooked | |
| I risk & threats | unlooked | |
| J measurement | unlooked | |
| K agent surface | unlooked | |

## Provenance — what produced this, and what expires it

**Replace this whole section** with the output of the command below — do not type it.
A field a human fills in after the run is automation debt, and `observed_at` then
records when somebody remembered rather than when an instrument looked. The `Date`
bullet at the top is when this document was written; `observed_at` is when the site
was read, and that is the one that decides whether this report has expired.

```bash
python3 "$SKILL_DIR/scripts/preflight.py" --origin https://example.com \
  --format provenance
```

It prints one row per field — `skill` · `script` · `observed_at` · `runtime` ·
`args` · `scope` · `actor` · `model` · `trace` — and every field prints even when it
cannot be resolved, as `unavailable: <VAR> is not set by this harness`. A field that
vanishes when unavailable is indistinguishable from one nobody checked. `model` is
never inferred: naming the wrong id is worse than saying nothing, and what the
provenance is for is being *investigated*, not looking complete.

Every collector prints the same block under its own output and carries it in
`--format json` as `producer`, so a finding pasted into this report can be traced
back to the run that produced it.

**What invalidates this report.** An overtaken audit is not wrong — it is true about
the site it observed, and it stays. Re-auditing writes a new dated file and names
which row below applies.

| Invalidator | What moved |
|---|---|
| **site** | the audited pages, their markup, `robots.txt` or the sitemap changed |
| **index** | the engine re-crawled or re-ranked — its own state moved, not the site's |
| **instrument** | this skill, its probes or its access changed, so a later run looks elsewhere |
| **policy** | a core or AI-surface update changed the rules the evidence was read under |
