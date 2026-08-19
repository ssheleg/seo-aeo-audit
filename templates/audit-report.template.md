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
