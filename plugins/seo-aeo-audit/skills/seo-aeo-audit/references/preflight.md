# Preflight — what it covers and what it cannot

`scripts/preflight.py` performs the automatable half of Step 0 rather than
describing it. This file is what it reaches and what it leaves to you; the
trap that makes it runnable at all (`$SKILL_DIR`) stays in `SKILL.md`, because
an agent cannot know to open a file about a trap it has not hit yet.

## Contents

- [What it probes](#what-it-probes)
- [Why a green preflight is not a covered step](#why-a-green-preflight-is-not-a-covered-step)

## What it probes

describing it, and reports which of the independent gates a failure hit — Search
Console, the GSC API and PageSpeed all answer `403` for entirely different reasons,
and their own messages do not distinguish them. An unreachable source comes back as
unreachable, never as absent data, because that difference decides whether a finding
is possible at all.

**What it probes:** the interpreter, `gcloud` ADC, the Search Console property list
and the named property, `robots.txt`, the sitemap, the homepage, and PageSpeed
(including whether CrUX has field data for the origin at all).
**What it cannot probe, so you still test by hand:** Bing and Yandex Webmaster,
analytics, server logs, a crawl export, and every MCP tool — Ahrefs, GSC-over-MCP,
Prowl, a crawler MCP. For those, make the one call each source is there for and
record what came back. A green preflight is not a covered step 2.

**Where the scripts live — resolve this once, before the first command.** You are
standing in the user's project; the scripts ship with the skill, somewhere else
entirely. Every invocation in this file is written against `$SKILL_DIR` for that
reason, and every one of them fails without it.

## Why a green preflight is not a covered step

Search Console, the GSC API and PageSpeed all answer `403` for entirely
different reasons and their own messages do not distinguish them, which is why
the script reports which independent gate a failure hit. An unreachable source
comes back as unreachable, never as absent data: that difference decides
whether a finding is possible at all.
