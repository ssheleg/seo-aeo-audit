# Preflight — what it covers and what it cannot

`scripts/preflight.py` performs the automatable half of Step 0 rather than
describing it. This file is what it reaches and what it leaves to you; the
trap that makes it runnable at all (`$SKILL_DIR`) stays in `SKILL.md`, because
an agent cannot know to open a file about a trap it has not hit yet.

## Contents

- [What it probes](#what-it-probes)
- [The gates, and which screen each one sends you to](#the-gates-and-which-screen-each-one-sends-you-to)
- [Why a green preflight is not a covered step](#why-a-green-preflight-is-not-a-covered-step)
- [Seeding the report's coverage table](#seeding-the-reports-coverage-table)

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

## Seeding the report's coverage table

```bash
python3 "$SKILL_DIR/scripts/preflight.py" --origin https://example.com --format coverage
```

Prints the `## Track coverage` section of `docs/seo/audit-<YYYY-MM-DD>.md`, already
filled in. It exists because the deliverable used to carry a `Status` column with
**no defined vocabulary** and a free-text "Not checked" table beside it, and nothing
read either — so a track that silently returned nothing rendered identically to a
track that came back clean. Two opposite states, one output, in the document
somebody pays for.

The vocabulary is closed. `validate_coverage()` in the same script refuses anything
else, including a blank cell:

| status | means |
|---|---|
| `observed` | the track ran and its checks answered |
| `partial` | the track ran on less than it wanted — say what was missing in Notes |
| `unlooked` | in scope, nobody ran it |
| `blocked-by <gate>` | an instrument was reached for and refused. `<gate>` comes from `COVERAGE_GATES` in the script, which is every gate a probe emits — the five the table above explains, plus `install`, `interpreter`, `network`, `unattempted`, `http`, `usage`, `rate-limit` — and two for blockers no probe can reach: `logs` (no server-log export) and `seat` (no seat on a third-party index) |
| `out-of-scope` | deliberately excluded — track K on a site with no programmable surface, a market nobody bought. Notes carries the decision |

**The seed is a floor, not a verdict, and it cannot write `observed`.** Preflight
runs at step 0, before any track has run: it fills `blocked-by <gate>` where a
source it probed refused, and `unlooked` everywhere else. Only somebody who looked
writes the one value that reads as clean — so the failure mode of forgetting this
table is *nobody looked*, never a clean report. Upgrading a row is the auditor's
job, and `partial` is there so an honest answer never has to be rounded up to
`observed`.

Where the gate is one of the five above, it is the same gate that decides which
screen you open next — which is why it is worth carrying into a client document:
*"we could not check indexation"* and *"this account is not on the property"* are
different asks. `validate_coverage()` refuses a gate outside `COVERAGE_GATES`, and
`test/validate.py` refuses a probe that emits one the tuple does not declare, so the
two cannot drift.
