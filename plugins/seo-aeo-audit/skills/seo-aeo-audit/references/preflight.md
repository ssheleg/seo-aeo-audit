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
- [Seeding the report's provenance block](#seeding-the-reports-provenance-block)

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

## Seeding the report's provenance block

```bash
python3 "$SKILL_DIR/scripts/preflight.py" --origin https://example.com --format provenance
```

Prints the `## Provenance` section of `docs/seo/audit-<YYYY-MM-DD>.md`. It probes
nothing — the block is about the execution, not about the site — so seeding it never
waits on a PageSpeed round trip.

It exists because **no script emitted a version, a timestamp or an input set**, so a
deliverable could not say when it was produced, by what version, or against what
arguments. That matters more here than in most places: an SEO audit is the most
perishable evidence this skill makes — a crawl result expires the moment the site or
the algorithm moves — and a three-month-old audit was indistinguishable from today's.

| field | where it comes from |
|---|---|
| `skill` | `SKILL_VERSION` in the script, which `test/validate.py` holds equal to the manifests |
| `script` | the instrument that produced the payload |
| `observed_at` | UTC, `2026-08-19T12:34:56Z`. The field that decides whether the report has expired |
| `runtime` | the interpreter and platform that ran it |
| `args` | the argv, with every credential flag's value replaced by `<redacted>` |
| `scope` | the RESOLVED input set — the URLs, not `--urls-file urls.txt`, which names a file nobody can reconstruct six months later |
| `actor` · `model` · `trace` | `SEO_AEO_AUDIT_ACTOR` / `_MODEL` / `_TRACE`, exported by the calling harness |

**A field is never deleted and never guessed.** The last three are the harness's to
supply and unset is the normal case: each then reads `unavailable: <VAR> is not set by
this harness`, by name. A field that vanishes when unavailable is indistinguishable
from one nobody checked — the same defect the coverage vocabulary above removed from
the `Status` column. `model` least of all is inferred: the wrong vendor id sends an
investigation to a model that never ran, which is worse than saying nothing.

**Every collector carries the same block**, printed under its markdown or text output
and present in `--format json` under `producer` — one per array element for
`page_audit.py`, whose JSON is an array by contract. So a finding lifted out of one
payload and pasted into the report can still be traced back to the run that produced
it. `validate_provenance()` in the same script reads a rendered report and refuses a
blank value, a missing field, an `observed_at` that is not a timestamp, a missing
invalidator, or a block with no seeding command.

**What invalidates the report** is stated, not implied — four rows, the shape
`task-pipeline` ships for its verification ledger:

| invalidator | what moved |
|---|---|
| `site` | the audited pages, their markup, `robots.txt` or the sitemap |
| `index` | the engine re-crawled or re-ranked; its own state, not the site's |
| `instrument` | this skill, its probes or its access — a later version looks elsewhere |
| `policy` | a core or AI-surface update changed the rules the evidence was read under |

Invalidation is not deletion. An overtaken audit is not wrong — it is true about the
site it observed, and it stays; re-auditing writes a new dated file and names which
row applies.
