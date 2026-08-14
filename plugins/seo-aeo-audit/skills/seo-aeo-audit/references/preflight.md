# Preflight — what it covers and what it cannot

`scripts/preflight.py` performs the automatable half of Step 0 rather than
describing it. This file is what it reaches and what it leaves to you; the
trap that makes it runnable at all (`$SKILL_DIR`) stays in `SKILL.md`, because
an agent cannot know to open a file about a trap it has not hit yet.

## Contents

- [What it probes](#what-it-probes)
- [The gates, and which screen each one sends you to](#the-gates-and-which-screen-each-one-sends-you-to)
- [Why a green preflight is not a covered step](#why-a-green-preflight-is-not-a-covered-step)

## What it probes

It reports which of the independent gates a failure hit — Search Console, the GSC
API and PageSpeed all answer `403` for entirely different reasons, and their own
messages do not distinguish them. An unreachable source comes back as unreachable,
never as absent data, because that difference decides whether a finding is possible
at all.

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

## The gates, and which screen each one sends you to

The gate name is the point of the report: it decides which screen you open next,
and three of these five send you somewhere a permission grant would never help.

| gate | what actually failed | what fixes it |
|---|---|---|
| `login` | no ADC token could be minted | `gcloud auth application-default login` with the webmasters scope |
| `quota-project` | local ADC has no quota project bound, or the account cannot *use* the one it has | `gcloud auth application-default set-quota-project <id>`, or `--quota-project`, plus `roles/serviceusage.serviceUsageConsumer` on that project |
| `api-not-enabled` | `searchconsole.googleapis.com` is off for the project | enable it on the quota project |
| `scope` | the token was minted without `webmasters.readonly` | re-run the login with the scope |
| `permission` | the account is genuinely not on the property | Search Console → Users and permissions |

`quota-project` was added on 2026-08-14 with the endpoint fix below, because
without it that failure was reported as `permission` — an auditor sent to the
Users-and-permissions screen for a problem no grant there can solve.

**One endpoint defect, and how it hid.** The property list lives at
`https://searchconsole.googleapis.com/webmasters/v3/sites`; only URL Inspection
lives under `/v1`. The script probed `/v1/sites`, which answers with a Google 404
HTML page, and the classifier — written for the three ways this API says `403` —
read that 404 as `permission`. So the check reported *no Search Console access* on
a property the same credentials read perfectly through `gsc_pull.py`, which had
the right base all along. A previous audit worked around it by hand, blaming a
missing `x-goog-user-project` header, and the wrong cause survived in that report.
That is the shape to watch for: **an instrument that fails the same way for every
site looks like a fact about the site.**

## Why a green preflight is not a covered step

Search Console, the GSC API and PageSpeed all answer `403` for entirely
different reasons and their own messages do not distinguish them, which is why
the script reports which independent gate a failure hit. An unreachable source
comes back as unreachable, never as absent data: that difference decides
whether a finding is possible at all.
