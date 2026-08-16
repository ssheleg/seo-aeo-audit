# Changelog

## v0.20.1 — 2026-08-16

**The default output mode crashed on the common case, and only there.** `page_audit.py`
emitted the severity `low` from `faq-schema-absent` while `SEVERITY_ORDER` held four
keys without it. `to_markdown` sorts findings on that map, so any page lacking FAQ
schema — which is most pages — died with `KeyError: 'low'` before printing a single
finding. The `--json` path builds no such ordering and was fine, so the crash was
invisible to every caller except the one running the invocation `SKILL.md` documents.
Found by pointing v0.20.0 at a real site: it failed on the first URL.

**The guard is the general form, not the incident.** `test_output_contracts.py` now
parses `SEVERITY_ORDER` out of each script's source and compares it against every
severity string that script actually emits, so the next severity added anywhere fails
the suite instead of the first real page. Watched failing against the reinstated defect
before this release: *page_audit.py emits severity ['low'] that SEVERITY_ORDER cannot
order*.

**Released as its own version because the fix was already on `main` and untagged.** The
umbrella pinned 0.20.0 — a version that crashes — while the branch carried the repair,
so the two channels the family installs through disagreed about what this skill does.

## v0.20.0 — 2026-08-16

### Added

- **The ten tracks are checked against each other before they become one plan.** Each track
  runs independently and produces findings that never saw the others; step 3 then sorts them
  into a single prioritised list, which treats them as one answer. That is a convergence, and
  a convergence trusts its inputs because they arrived — sorting an unranked list is not the
  same as noticing that two of its rows cannot both be executed.

  Four things to look for before any score is computed: two recommendations that cannot both
  be done (D says merge the cannibalising pair, C says the deeper page is where the equity
  lands); one root cause wearing three track names and splitting its own priority; two rows
  about one URL at CONFIRMED and HYPOTHESIS, which is a fact about the instruments; and a
  track that found nothing where a neighbour implies it should have.

  `Cross-track: clean` is the answer most audits will write, and writing it is the point — a
  check whose silence is indistinguishable from not having run is not evidence, and this is
  the one most easily skipped because every track individually went green.

  The model is one home away, in `agent-stack`'s
  `agent-orchestrator/references/graph-engineering.md`; this is its application to an audit
  whose shape is a fan-out.

## v0.19.1 — 2026-08-15

Two false findings and one false claim, all found by running v0.19.0 against a
site that had just acted on its own report — which is the only way any of them
would have surfaced.

**A `medium` / `CONFIRMED` false positive told a site its own link was
forbidden.** The record was `Allow: /` · `Allow: /api$` · `Disallow: /api/` ·
`Disallow: /admin/`. `/api` is permitted by an anchored Allow and forbidden by
nothing — `Disallow: /api/` requires the trailing slash. Two causes in one
function: `href == pattern.rstrip("/")` let a trailing-slash Disallow cover the
slashless path, and `parse_robots` never collected `Allow` lines at all, so the
more specific rule could not win **because it was not in the room**. Acting on
that finding means deleting a good link or loosening a good `robots.txt`.
Replaced with the documented rule — most specific pattern wins, `Allow` breaks
the tie — with `*` and `$` handled, the live record pinned as a fixture, and a CI
plant that flips the comparison and must fail.

**A false negative in the same run** reported "no markdown recovery" against a
site that had shipped exactly the recommended implementation the day before. The
recommendation is a markdown body served to a client that *asked* for markdown;
the probe fetched with the default `Accept`. It now asks the way the fix is meant
to be reached, and checks `Vary: Accept` when it finds one. An instrument that
does not request the fix the way the fix is reached cannot see it.

**`v0.18.0` never existed.** The CHANGELOG carried a section that reads like a
release; there is no tag and no npm publish — the registry goes `0.17.1` →
`0.19.0`. The gap document said six times that track K shipped in a version
nobody can install. Corrected to name the release that carries it, with the
substitution stated rather than applied silently.

**K2b gained the rule underneath all of it:** an artifact cannot say whether its
shape is a defect or a decision. Two live cases pointing opposite ways —
`/register` unlinked (an auth route, `noindex` by design) and 47% `<lastmod>`
coverage (a deploy-date stamp that had been measured restamping 3,582 of 3,582
URLs, then deliberately deleted) — and neither reason was visible in the
artifact. Both took one read of the generator. `sitemap-lastmod-thin` now says so
at the point of use.

Gates, each run alone: `validate.py`, `plant_guard_test.py`, `test_page_audit.py`,
`test_url_inspection.py`, `test_collectors.py`, `test_agent_surface.py`,
`test_output_contracts.py`.

## v0.19.0 — 2026-08-14

A second agent-readiness scan, on a second live site, was reproduced line by line.
It returned 53 items and missed the one finding that was costing the product
answers on a live engine — and reproducing it found four defects in this skill,
one of them a `high` / `CONFIRMED` false positive.

**The taxonomy was wrong, and the instrument was silent.** `agent_surface.py`
listed `GPTBot`, `ClaudeBot` and `Google-Extended` as answer-engine retrieval
crawlers. All three are training or grounding crawlers on their vendors' own
documentation, read on 2026-08-14; the retrieval agents are `OAI-SearchBot`,
`ChatGPT-User`, `Claude-SearchBot`, `Claude-User`, `PerplexityBot` and
`Perplexity-User`, and each is controlled independently. Separately, `parse_robots`
collected which agents a file **named** and never what it **decided** about them,
so a site naming seventeen AI crawlers and disallowing all seventeen produced no
robots finding at all. On the audited site those two defects compounded into
silence about a `Disallow: /` for `PerplexityBot` — a search crawler sitting in a
constant named `AI_TRAINING_BOTS`, where nobody reviewing the name reads the
members. Fixing only the second defect would have produced sixteen confident false
findings on the first site it ran against.

- **robots.txt is now parsed as records with verdicts** (`_robots_groups`,
  `_blocks_root`) across four buckets, each retrieval entry carrying the vendor
  sentence that put it there. New findings: `robots-retrieval-blocked` (high,
  `CONFIRMED` — the effect is documented by the engine doing the excluding),
  `robots-training-decided` (an answered business decision, recorded and not
  counted against the site), `robots-contradictory` (two `User-agent: *` records,
  or two disagreeing `Content-Signal` lines — the shape a CDN-managed block
  prepended to an origin file produces), `robots-blocks-linked-page` (the homepage
  links where the `*` record forbids).
- **`agent-file-misnamed`** — before reporting `/llms.txt` absent, probe
  `/llm.txt`, `/llms-full.txt`, `/llm-full.txt`, `/ai.txt` and
  `/.well-known/llms.txt`. The audited site had written, linked and maintained its
  agent manual at `/llm.txt`; every client that follows the convention got a 404,
  and "absent" would have sent the team to write a file they already had.
- **`openapi_provenance()`** — ask whose API a spec describes **before** grading
  its structure. `openapi-template-spec` (blocker) and `openapi-foreign-servers`.
  The audited site published Mintlify's sample — `"OpenAPI Plant Store"`,
  `servers: http://sandbox.mintlify.com` — at its public api-reference URL, listed
  it in its own `llms.txt`, and the scanner scored it as "schema found (3
  operations)" while docking a point for the sample's missing `operationId`s.
- **`sitemap-lastmod-frozen`** — coverage answers "is the field there"; a crawler
  asks "which of these changed". 160 URLs, 100% coverage, two distinct dates five
  months old passed the old check exactly.

**`page_audit.py` stops reporting an absence it never established.**
`faq-schema-orphan` fired at `high` / `CONFIRMED` — "no question/answer pairing
was found in the served markup" — on a page whose answers were in the served
markup, because the check counted `<dt>`/`<dd>` and `<details>`/`<summary>` and
the page used the WAI-ARIA disclosure pattern every component library ships. The
proxy was never the question: the question is whether the declared answers are in
what was served, and it is now asked directly.

- ARIA disclosure pairing (`aria-expanded` + `aria-controls` → `aria-labelledby`)
  counted as pairing; `_faq_declared_vs_served()` compares every declared
  `acceptedAnswer` against the body text.
- `faq-schema-orphan` re-scoped to a node whose answers are genuinely absent.
  `faq-schema-partial` added for drift between the node and the page — which found
  a real one on the first page it ran on: a homepage whose visible accordion
  passed a values object to the translator while the JSON-LD emitter, a different
  component reading the same key, did not, so the machine-readable pricing answer
  shipped as `"Plans start at ${seat}/month …"`. `faq-schema-unreadable` added at
  `HYPOTHESIS`, because "I could not read it" is the opposite of a confirmed
  absence.

**Doctrine.** K2a rewritten with the verified taxonomy, the list-under-the-wrong-
label failure mode, the two-`User-agent: *` case and the linked-but-disallowed
case. **K3a** added — publish an agent file at the name clients probe, and put any
fact it restates under the same guard that protects the page. **K4a** added —
a document at a conventional path is evidence that something is published there,
never that it describes this product. K7 gains reasons 5 and 6: a grader scores
what a site publishes and never what it forbids, and cannot ask whose API a spec
describes. `aeo-geo.md` F8 gains the ARIA pairing and the drift case.
`myths.md` **row 33** — "raise our agent-readiness score", which is row 11 in
agent-readiness costume and more expensive, because its remediation list is
specific enough to read as engineering.

Full validation, all 53 items with verdicts and the change plan:
[docs/audit/2026-08-14-privateclawd-orank-validation.md](docs/audit/2026-08-14-privateclawd-orank-validation.md).
Five items carried to the backlog as B-11…B-15; B-11 (`agent_traffic.py`) is now
the highest-priority open item in the repository, because two consecutive audits
have hit the same ceiling: nothing in track K can be sized without it.

## v0.18.0 — 2026-08-14

> **Never released on its own.** There is no `v0.18.0` tag and no `0.18.0` on
> npm: the registry goes `0.17.1` → `0.19.0`. This section describes work that
> shipped **inside v0.19.0**, which was cut two commits later on the same day.
> The note is here because the section reads as a release, and `npm install
> @ssheleg/seo-aeo-audit@0.18.0` fails. Install `0.19.0` or later to get track K.
>
> Nothing checks this. `validate.py` enforces the four-way version sync between
> the manifests and the CHANGELOG top entry; it does not ask whether every
> CHANGELOG section corresponds to a tag that exists. That guard is in the
> backlog (`docs/audit/2026-08-14-agent-readiness-gap.md`, §4 A9).

An external agent-readiness scanner graded a site this skill had already audited
twice and returned 58 findings across four layers. Roughly half of them named
things none of the ten tracks looks at: `.well-known` discovery documents, OAuth
metadata an agent reads before it ever sees a login screen, `WWW-Authenticate`
pointing at RFC 9728, rate-limit headers, whether an OpenAPI operation carries the
`operationId` an LLM turns into a function name. The skill was not wrong about
those; it had nothing to say.

**Track K — the agent surface — is the answer, and it arrives with the rule that
keeps it from becoming a checklist.** Tracks A–J ask whether a retrieval system
can fetch, read and quote a site. K asks whether an agent acting for a user can
discover it, get a credential, call it, and recover when a call fails. It is
**conditional**: run it only when the site sells something an agent could
plausibly buy, call or automate.

The rule, in `references/agent-readiness.md` K1: **presence is `CONFIRMED`, effect
is mostly `HYPOTHESIS`.** One request proves a file is absent. Nothing here proves
that publishing it brings anyone. So the cheap, specified fixes ship as Gains —
a real 404 status, `operationId`s, rate-limit headers, a `401` that says where to
look — while the draft-spec set ships as one Experiments batch whose success
metric is *requests to those exact paths in 90 days*, and MCP servers, OAuth
deployments and SDK fleets are written as business decisions with a trigger rather
than as tickets. `test_agent_surface.py` enforces the split by name: five codes are
required to be `HYPOTHESIS`, and a plant that promotes one to `CONFIRMED` fails CI.

**Where a grader contradicts `myths.md`, the myth guard wins.** Scanners award
points for `llms.txt` and Markdown mirrors, which rows 1–2 refute with the numbers.
Both rows keep their entries, and both now carry a boundary that names the one
non-myth use precisely: they do not help a page get **found**; they can let an
agent that **already arrived** read the canonical facts for fewer tokens. That is
a serving decision, honest only when the Markdown is generated from the same
source as the HTML, `Vary: Accept` is set wherever negotiation is on, and an
advertised `rel="alternate"` actually resolves to Markdown. A full `.md` twin of
every page is still the refuted version. K7 adds the reading protocol for such a
score: absence findings are a to-do list to verify, the number is noise, and the
prescriptions are claims to check.

`scripts/agent_surface.py` collects the mechanical half in one pass — the
`.well-known` set, `robots.txt` read as three separate decisions, Markdown
negotiation and its `Vary`, RFC 8288 `Link` headers, the 404 shape, `<lastmod>`
coverage, JSON-LD `sameAs` / address / extended types / `speakable`, the four
OpenAPI properties function calling needs, and the auth-discovery chain on the
host that actually serves the API. It prints the URL and status behind every
check, because the failure it exists to prevent is a scanner reporting absence it
never probed. Two blind spots travel in every report: **one url is not a site**
(the "no extended schema types" verdict that means *on the homepage* while the
product templates carry `Product`, `Offer`, `FAQPage` and `HowTo` — reproduced
live), and server-rendered HTML only, the same blindness `page_audit.py` carries.

**The check that turned out to matter most is also the cheapest, and it is the
one no scanner had run: read the SERVER-RENDERED root and list which conventional
entry points it links to.** On a client-rendered site the API docs, the sign-up
and the contact page sit in the navigation, work in every browser, and are absent
from the document a crawler, an answer engine or an agent actually reads. On the
site that triggered this release the developer surface — an OpenAPI spec, a
copy-paste agent skill, a full documentation page — was reachable from the root by
nothing that does not execute JavaScript. K2b owns the reasoning, `agent_surface.py`
prints the table, and locale prefixes are normalized so a nine-locale site does not
report the same gap nine times.

**And the instrument produced a false finding on its first live run, which is now
its own guard.** `urlopen` follows redirects, so probing `/about-us` returned
`200` with a title and 1,564 characters — all of it the homepage, because the path
is a `301` to `/`. The About page does not exist and the check said it did. Every
entry-point probe now compares the final URL against the requested path: a
redirect to the site root reads as *the page does not exist*, which is what it
means, and `entry-point-bounces-to-root` is `CONFIRMED` rather than a guess. The
same run found the trust-page length check counting HTML comments as prose —
1,666 comment characters inflated one page's 482 real characters to 772, turning a
page that fails the 500-character convention into one that passes it.

**`entity-and-brand.md` G1b — the two-query brand-collision test**, added because
the largest finding on that site was not in the agent surface at all. A clean
search for the brand name returned four other operators and not the domain; the
exact-domain query returned it first. Those two facts together are a *name
collision*, not an indexation problem, and they need opposite plans — the table in
G1b routes all four outcomes, and says plainly when the unqualified brand query is
not winnable and the honest recommendation is to stop paying for it.

**One confirmed defect, found by running the skill rather than by reading it.**
`preflight.py` probed `https://searchconsole.googleapis.com/v1/sites` for the
property list. That path does not exist — `sites` lives under `/webmasters/v3`,
and only URL Inspection lives under `/v1` — so the API answered with a Google 404
HTML page, and the gate classifier, written for the three ways this API says
`403`, read it as `permission`. The check reported *no Search Console access* on a
property the same credentials read perfectly through `gsc_pull.py`, which had the
right base all along. It had been failing that way for every site, and a previous
audit had already worked around it by hand with the wrong cause written down.
Fixed, with a fifth gate — `quota-project` — because local ADC is refused by this
API until a quota project is bound, and reading that as `permission` sends an
auditor to a screen where no grant can help.

Two guards were generalized in the same pass, both instances of the class the
2026-08-10 audit named: a guard written against one home of a fact that lives in
several. The reference-anchor check and the `FINDING_TIERS` coverage check now
read every bundled script instead of `page_audit.py` alone, and the second one
learned the inline-dict emitter shape as well as `add(sev, code, …)`.

Also in this release: SKILL.md's step-0 paragraph lost a duplicated line that had
survived a merge, and `references/preflight.md` lost the same botched split plus
the orphaned sentence fragment its first section opened with.

Gates, each run alone: `validate.py`, `plant_guard_test.py`, `test_page_audit.py`,
`test_url_inspection.py`, `test_collectors.py`, `test_agent_surface.py`,
`test_output_contracts.py`.

## v0.17.1 — eleven plants that could only ever run in CI now run anywhere

`plant()` takes its command as an argv, and every substituting plant reached for
`sed -i`. BSD sed needs an **argument** to `-i`, so all eleven were no-ops on macOS: the
guard they were meant to disarm stayed armed, the validator honestly passed, and the step
would report a healthy guard as broken. Elsewhere in this family that exact shape hid a
broken plant for two days.

### Added

- **`test/plant_edit.py`** — three verbs (`sub`, `delline`, `truncate`), anchors
  **literal** rather than regular expressions, and each one **refuses by name** when its
  anchor is absent. Half the sed calls it replaces spent their length escaping `**` and
  `/`, and an escape wrong in one direction silently matches nothing. `plant_guard.py`
  would still catch a plant that did nothing; this says *which* anchor moved, which is
  the difference between a five-minute fix and a hunt.
- **A guard against the return of `sed -i`**, because the failure it causes is silent on
  one platform and invisible on the other. Watched failing on a plant that turns one
  `plant_edit` call back into a sed.
- **`truncate` keeps the trailing newline.** Found by the fixture, not by reading:
  `sed '/x/,$d'` leaves one, and a plant that also strips it damages the file in a second
  way its own description never claimed.

All fourteen plants in this workflow now run on the machine they were written on, and
were watched doing so.

## v0.17.0 — 2026-08-14

The pack had no guidance on how a sentence reads. `E4` priced machine-drafted
content by volume and template, which catches a thousand generated glossary
pages and says nothing about the one honest page written in the generated
register.

**`E4b` adds it, and opens with the limit rather than burying it.** There is
no measured ranking penalty for an em dash, nothing in `benchmarks.md` prices
punctuation, and a style note sitting in the same table as a crawl finding is
broken tier discipline. Register carries no tier and is reported separately.

Three mechanisms justify auditing it anyway:

- A "Scaled content abuse" manual action is applied by a person reading
  pages, so a useful page written in the generated register is being asked to
  survive that read having volunteered the surface signal. A risk argument,
  worth what a risk argument is worth.
- Extraction is priced by track F. A sentence whose two halves are joined
  only by a dash loses the relationship when an engine lifts it out of its
  paragraph; a comma, a colon and a full stop each survive the lift because
  each names the relationship.
- A `<title>` ending in a full stop spends a character in a field measured in
  characters. That one is mechanical and now sits in `onpage-checks.md`
  beside `O1`.

**The markers are not forked here.** They stay in super-ux's `ai-tells.md` as
`AT-01`..`AT-15` with their grades, density threshold and change-rate guard;
three are deterministic there as `B060`, `B062` and `B063`. A second copy of
a marker list drifts from the first inside one release, which is the failure
the family's propagation rules exist to prevent.

The non-English case is called out explicitly, because getting it wrong
discredits the rest of the report: the rule bans the **rhetorical** dash and
keeps the **grammatical** one, and in Russian the dash between subject and
predicate is orthography rather than style.

Gates, each run alone: `validate.py`, `plant_guard_test.py`,
`test_page_audit.py`, `test_url_inspection.py`, `test_collectors.py`,
`test_output_contracts.py`. All pass.
## v0.16.3 — 2026-08-14

A red `validate` could not stop a publish anywhere in this family, and one member
proved it: on 2026-08-12 `sheleg-dev` tagged v0.4.1 while its own validate run for that
exact tag **failed**, and npm served 0.4.1 four minutes later.

### Fixed

- **The release now runs the whole validate suite before anything is published.**
  `validate.yml` gained a `workflow_call` trigger and `release.yml` calls it with
  `needs: validate` — the release runs *after* the real suite rather than beside a copy
  of it. **Not one plant is duplicated:** each still has exactly one home.
- **A guard keeps the connection there.** It fails when the trigger, the call, or the
  `needs` goes missing — calling the suite without depending on it lets the jobs run in
  parallel, which looks gated and is not. Watched failing against the planted removal.

Proven end to end on `sheleg-dev` v0.4.3 before it reached here: the release run shows
`validate / validate` completing first, then `release`, then `publish`.

## v0.16.2 — 2026-08-13

Twelve plants could not run on a developer's machine, and none of the nine that edit a
file could say whether it had. The first attempt to fix that broke a step three times,
which is why the check is now a script rather than a careful copy.

### Added

- **`test/plant_guard.py`** — one implementation of *did the plant actually land*, called
  by `plant()` for every row it runs and by the standalone steps around their edits. It
  compares **content and mode**, ignores `.git` churn, and refuses when handed no tree or
  no snapshot. `test/plant_guard_test.py` covers nine cases and now runs in
  `scripts/check-docs.sh`, so a contributor following the docs runs the whole gate —
  which this repository's own validator insisted on, by name, three surfaces at a time.

### Fixed

- **Twelve `sed -i` plants converted to Python.** BSD sed requires an argument to `-i`,
  so every one errored and changed nothing on macOS; they could only ever be exercised in
  CI. That is how a broken plant in a sibling repo kept its `main` red for two days while
  blaming a guard that worked.
- **Every plant now proves it landed** — `PLANT DID NOT LAND: <desc>`, naming the row.

### Known residue

Eleven `sed -i` calls remain **inside `plant()`**, where the command is passed as an argv
and a heredoc cannot go: converting them needs `python3 -c` one-liners, and three
attempts at that broke the step (a delimiter collision, lost sed escaping, and a heredoc
read at the wrong indentation — `IndentationError` in CI). They are guarded by
`plant()`'s call to the helper, which is what B-27 asked for; they are still not runnable
on macOS, which is portability and is carried as its own row.


## v0.16.1 — 2026-08-13

This project's own pipeline paperwork moved from `docs/superpowers/` to
`docs/evidence/`, following `task-pipeline` v1.53.0, which renamed the default and made
the root resolvable. **A patch, deliberately: nothing a consumer of this skill can see
changed.** The directory, this repository's own validator paths and its CI plants moved
together; the records inside the directory were NOT rewritten — a brief describes where
things were when it was written.

## v0.16.0 — 2026-08-12

Four new page-auditor findings for the Q&A block, and a reference section that
stops "add FAQ schema" from being one recommendation.

### Added

- **`page_audit.py` reads the Q&A shape.** The parser counts `<dt>`/`<dd>` and
  `<details>`/`<summary>` pairs and matches an FAQ-announcing heading, and the
  payload carries `qa_pairs_visible`, `qa_pairs_collapsed` and `faq_heading`.
  Four findings report the four states apart, because they want different fixes:
  - `faq-collapsed` (STUDY) — answers behind a disclosure widget. The message
    **concedes** that `<details>` is in the DOM, is exposed to the accessibility
    tree and is indexed by Google: the argument is that an open definition list
    costs nothing, not that the accordion is invisible. An audit that claims
    otherwise is repeating folklore.
  - `faq-unpaired` (CONFIRMED) — a heading announces a Q&A block and nothing
    marks which text is the question.
  - `faq-schema-absent` (CONFIRMED, **low**) — readable pairs with no `FAQPage`
    node. Deliberately low: the FAQ rich result was restricted in August 2023 and
    then discontinued, so the payoff is entity clarity, and the finding says so
    rather than selling a SERP feature that no longer exists.
  - `faq-schema-orphan` (CONFIRMED, **high**) — an `FAQPage` node over answers
    absent from the served markup. Higher than the absent case because marking up
    content users cannot see is a structured-data policy violation, not a missed
    opportunity.
- **`references/aeo-geo.md` F8 — "The Q&A block, which is three problems."**
  Structure, then extractability, then declaration, in that order, because
  declaring answers a crawler cannot reach fixes nothing. Carries the measured
  pattern worth copying (`zernio.com`, read 2026-08-12: an FAQ as a `<dl>` with
  zero `<details>`, its decorative glyph in a separate grid column so it never
  lands in an extracted answer) and the same page's coverage failure — the
  homepage mirrors its visible steps into `HowTo` while `/pricing` and
  `/phone-numbers` ship no structured data at all. **Audit schema per page, never
  per site.**
- **A parity warning with a live example.** On that homepage the `HowToStep`
  names read `Connect accounts` and `Start posting` while the visible steps read
  `Connect channels` and `Launch`. Nothing breaks and no tool flags it — which is
  how a schema block becomes stale documentation of a page since rewritten.
- **`references/onpage-checks.md`: the visible section label *is* the heading.**
  A new O1 row and a design-time note: the common failure is not a missing `<h2>`
  but a layout with no place for one — a styled kicker as a `<span>` over a
  section with no heading. Wrapping the chip itself in the `<h2>` makes the
  visible label and the semantic outline the same object, so they cannot drift.
  The coverage table records honestly that the script **cannot** check this one,
  because the distinction is visual.

### Changed

- `references/onpage-checks.md`'s "What `page_audit.py` actually covers" table
  gains rows for the Q&A findings and for the heading check the script cannot do
  — an absence reported as coverage is the thing that table exists to prevent.

### Fixed

- Two self-inflicted defects, both caught by the repo's own gates during this
  change and both worth recording:
  - The four findings first pointed at reference anchors that did not exist
    (`aeo-geo.md#q1-answer-extractability`). `validate.py`'s anchor check caught
    it — the gate works.
  - The new tests used bare `next(...)`, so a regression raised `StopIteration`
    and hid every check below it instead of reporting. Found by planting a defect
    and watching the failure mode, not the failure. Now a missing finding fails
    with a message.


## v0.15.2 — 2026-08-12

### Changed

- `references/growth-plays.md` crossed 100 lines and gains the `## Contents` list the
  canon requires past that mark — generated from its own five headings, so the list
  cannot disagree with them on the day it was written. It was the last reference here
  without one.

## v0.15.1 — 2026-08-11

### Fixed

- **The myth short list goes back to fourteen.** Shortening it to ten in
  v0.15.0 disarmed a negative self-test without touching a line of the check:
  the plant creates a disagreement by rewriting the literal
  `The fourteen asked for most often`, and against `ten` the `sed` became a
  no-op, the validator passed, and CI reported `BROKEN GUARD`. Re-aiming the
  plant needs a change under `.github/workflows/`, so the list is restored
  instead — it costs ~60 tokens against a body at 4648 with headroom to 4750,
  and shortening it was never the point.

  v0.15.0 shipped from a commit whose `validate` was red for this reason. This
  release is cut from a green one, which is what the pin should point at.

## v0.15.0 — 2026-08-11

### Changed

- **The body went 396 lines / 6103 tokens to 313 / 4582** — the cap is 5000
  tokens and it was 22% over. Measured with `cl100k`, not with
  `claude plugin details`, which over-reports by roughly 40%.

  Two blocks moved out, neither deleted:

  - Step 2's tail was a **manual for the six bundled scripts** — invocation,
    flags, quotas, per-script limits — now `references/scripts.md`, with a
    heading per script so the contents list resolves.
  - Step 0's "what preflight probes and what it cannot" is now
    `references/preflight.md`.

  The body keeps the four traps that decide whether a finding is real: the
  schema inventory reads server-rendered HTML only, `--format json` emits an
  array even for one URL, a `--max-bytes` truncation drops count-based findings
  rather than publishing a fragment, and **only the evidence tier enters the
  triage formula** while severity is merely how loud a finding is. A trap an
  agent has not hit yet is a trap it cannot know to go read about.

  The myth short list drops from fourteen to ten in both channels — the
  validator requires `SKILL.md` and the Cursor rule to offer the same list, and
  caught the attempt to change one of them alone.

- **Every reference over 100 lines now opens with `## Contents`** (19 files).
  A partial read is what agents actually do with a long reference; without the
  list it returns an arbitrary slice.

## v0.14.1 — 2026-08-10

**The acceptance walk found what the requirement table could not**, which is what
it is for: a comparison needs two sides, and an absence has one.

`v0.14.0` fixed the eleven unreachable invocations in `SKILL.md` and guarded that
file. The **README carried eight more**, and the slash command a ninth. The guard
had been written against the one home the defect was noticed in — the exact
mechanism this repository has now recorded four times, committed **inside the
release that exists to fix it**.

Worse in the README's case: those paths did not resolve for a contributor in a
clone either. `scripts/` at the repository root is the documentation gate, so
`python3 scripts/page_audit.py` finds `check-docs.sh`'s neighbour or nothing —
a third way to be wrong, in the file a first-time reader opens.

- Both homes now use `$SKILL_DIR`, and the README explains the two contexts it
  resolves in: a clone, and an installed plugin.
- The reachability guard reads **three** homes, and only flags runnable forms — a
  backticked `scripts/page_audit.py` used as a name is fine and reads better.
  Its CI self-test plants the defect in each home rather than one.

## v0.14.0 — 2026-08-10

A second audit of the skill, run through the lens the first one did not use: **what
happens when an agent actually uses this**. Nine findings, one of them a blocker,
and the four-command gate was green against every one — again, because a guard
tests the invariant somebody thought to write, and nobody had thought to ask
whether the documented commands run at all.

Two output contracts change, so this is `0.14.0` and not `0.13.1`:
`url_inspection.py` and `psi_pull.py` now exit **1** when a run produced nothing
usable. Anything branching on their exit status needs to know.

### Fixed — the instruments were unreachable from where the agent stands

- **All eleven documented invocations failed in the only environment the skill is
  used in.** Every bash line read `python3 scripts/<name>.py`, which resolves
  against the agent's working directory — the user's project, where the scripts
  are not. Reproduced from a project root: `No such file or directory`, eleven
  times out of eleven. One sentence in the whole shipped skill admitted the paths
  were relative, and it did not say to what.

  The failure is quiet in the way that costs: an agent absorbs the error, does the
  check by hand, and the audit silently drops to the bottom rung of the evidence
  ladder — which caps every tier it is allowed to claim. Now `SKILL.md` resolves
  `$SKILL_DIR` once (`${CLAUDE_PLUGIN_ROOT}/skills/seo-aeo-audit` in a Claude Code
  plugin, the harness-named base directory elsewhere — the placeholder is
  documented to expand in *skill content*, which was verified before it was relied
  on), every invocation goes through it, and the validator rejects a bare
  `scripts/*.py` path.
- **The Cursor channel shipped non-negotiable #8 — "know each instrument's blind
  spot" — and named zero instruments.** It mentioned `scripts/` not once, so the
  rule governed nothing and every Cursor audit was capped at the manual-fetch rung
  without saying so. It now carries the six, each with what it settles and what it
  cannot see.
- **`page_audit.py --format json` emits an array even for one URL**, and said so
  nowhere; `data["findings"]` raises `AttributeError`, which is what the one-URL
  example in the docs leads you to write.

### Fixed — a run that measured nothing reported success

- **`url_inspection.py` and `psi_pull.py` returned 0 after total failure**, against
  their own docstrings, while `page_audit.py` and `sitemap_audit.py` returned 1 in
  the same situation. Four collectors, two answers. The prose was already honest —
  a run of 403s prints "supports **no findings at any tier**" — but SKILL.md's own
  documented invocation redirects stdout to a file, so an agent checking `$?` read
  success from a page of refusals. The predicate now has one home per script and
  the report and the status read the same one. An absent-CrUX result still exits 0
  and is pinned by a test: that call worked, and treating its honest absence as a
  failure would break the behaviour the script exists for.

### Fixed — the instruments emitted broken markdown

- **Four renderers interpolated raw network errors into generated markdown.** A
  Google error page arrives with newlines; the first one ends the table row and
  every row after it stops rendering. On a live preflight run against a 404
  property, **5 of 7 rows survived** — and `validate.py` already rejects exactly
  this shape in the repository's own files, but a guard over checked-in markdown
  cannot see markdown a tool generates. `_flat()` collapses whitespace, escapes
  pipes and caps length in all four.
- **`preflight.py`'s coverage denominator shrank when a source failed.** A failed
  property-list call returned one probe where a successful one returns two, so the
  headline said "3 of 7" where success says "of 8" — and the probe that silently
  left is the one that decides the most: whether this account can see this property
  at all. A reader could not tell a smaller world from an unasked question. The
  named-property row is now always reported, marked `not attempted`.

### Fixed — claims about the skill that were false

- **`SECURITY.md` described "documentation plus one small Python script"**, listed
  only `page_audit.py`, documented only its network behaviour, and closed with a
  verification recipe scoped to that one file under the sentence "No `subprocess`".
  Six scripts ship and **three execute `gcloud` as a subprocess** — the most
  security-relevant fact about the bundle, absent from the security document. It
  now carries a measured per-script table (outbound, subprocess, writes), explains
  what the `gcloud` token exchange does and does not do, and its grep covers all
  six: 22 lines, six `open()` calls, every one a file you named.
- **The PR template asked for two of the gate's commands.** It was never counted as
  a home, so it kept asking for two long after CONTRIBUTING and the README were
  corrected. The gate-parity guard now spans five homes.
- **The third deliverable had no root skeleton.** `deliverable-templates.md`
  embedded three; `templates/` shipped two, and the README calls that directory the
  skeletons for non-agent use — while step 4 makes `experiments.md` required as
  soon as anything sits below `CONFIRMED`.
- **The 2026-08-10 defect total was wrong in five of its six homes.** The ledger
  enumerates `D1`–`D43`; the changelog, the retro, the improvement plan and the
  ledger's *own summary sentence* said forty-one. It went stale in the release that
  appended `D42`–`D43` after the `v0.12.0` rebase.

### Added — guards, each watched failing on a planted defect

Script reachability, error flattening, the defect count against the rows the ledger
enumerates, and the PR template as the fifth gate home. `test/test_output_contracts.py`
holds what all six scripts owe their caller. All **17** negative self-tests were
re-run after the code changes — a changed line silently disables one, and a disabled
self-test looks exactly like a passing one.

The gate command count is no longer written down in any living document. It had four
homes and went stale in three of them the first time a file was added; a count that
does not exist cannot drift.

## v0.13.0 — 2026-08-10

**Version note.** This work was written against `v0.11.2` and released as `v0.11.3`
before `origin/main` was fetched — by which time `v0.12.0` had already shipped. The
number is corrected here rather than quietly reused: `0.13.0` and not `0.12.1`,
because two output contracts change. The `thin` finding code is now
`low-extractable-text`, and `onpage-checks.md`'s sections are `O1`–`O5` where they
were `D1`–`E2`, so anything parsing findings or citing those ids needs the new names.
The stray `v0.11.3` tag is deleted.

A fresh-eyes audit of the whole skill: every command, every bundled script, all
twenty-two references and the pipeline around them. **Forty-three defects**, nine of
which made the skill emit or suppress findings in ordinary use. The four-command
gate was green against all forty-three.

Full record: `docs/audit/2026-08-10-defect-ledger.md` (what was wrong, with the
repro for each) and `docs/audit/2026-08-10-improvement-plan.md` (what was done,
what was not, and what is next).

### Fixed — the auditor was manufacturing findings

- **`max-image-preview:none` was reported as `noindex`.** The directive string was
  matched with a word-boundary regex, and `none` is a real directive as well as the
  value of two documented parameters. A page declaring `index, follow` came back
  carrying a track-A indexation blocker — and SKILL.md makes a track-A blocker a
  stop condition, so the audit ended there on a fabrication. Directives are parsed
  as comma-separated tokens now, with `key:value` read as a parameter for the four
  parameter directives and as a user-agent prefix otherwise, so
  `X-Robots-Tag: googlebot: noindex` still counts.
- **jQuery's `$` produced a JS-gated-price finding.** `CURRENCY_RE` was searched
  against the raw HTML, so any inline script using `$` — or a correct
  `Product`/`Offer` `priceCurrency` — produced a `high` finding asserting the page
  hides its price from answer engines and hands it to aggregators. Doing the markup
  correctly was what triggered the accusation. The check reads markup with script,
  style, template, noscript and comments removed; a declared JSON-LD price absent
  from visible text is now its own `jsonld-price-parity` finding, which is the
  markup-versus-content parity check `onpage-checks.md` already asked for.
- **A truncated response was analyzed as if it were the page.** The same URL
  returned 10,001 words at the default `--max-bytes` and 475 at `--max-bytes 3000`,
  with no warning either time; a page truncated just under the threshold produced a
  fabricated thin-content finding. `fetch` reads one byte past the cap to tell
  "fits" from "was cut", the flag travels in the payload and the markdown, and every
  completeness-dependent finding is dropped. Presence findings survive.
- **`preflight.py` decided CrUX presence from a 4 KB prefix, and from the wrong
  key.** PSI returns `loadingExperience` whether or not it has data — the data is in
  its `metrics` child, which `psi_pull.py` has always read. So the probe reported
  field data that was not there, and reported absence with a cause it never
  established ("too little traffic"). Both instruments now answer the question the
  same way, and the tests pin them to each other.
- **`url_inspection.py` printed "Evidence tier: CONFIRMED" unconditionally.** A run
  where every inspection returned 403 ended by declaring its output CONFIRMED, from
  the one instrument in the skill whose justification is that it can legitimately
  claim that tier. The footer is scoped to the rows the index answered for and says
  plainly when there were none. Its not-indexed check was a substring test for
  "not indexed" — two documented coverage states out of the full set — and now reads
  the engine's own verdict, so duplicates, canonical alternates, `noindex` and
  unknown URLs are no longer passed silently. A response with no `indexStatusResult`
  produced exactly one finding, "no last crawl time recorded", manufactured from a
  parse miss.
- **`gsc_pull.py --format text` computed four analyses and printed none of them.**
  `ctr_curve`, `ctr_gaps`, `cannibalization` and `branded_split` existed only under
  `--format json`, while `text` is the default and the documented invocation. An
  agent running the documented command saw no cannibalization section and had
  nothing to distinguish "none found" from "never shown", and
  `derive_branded_split`'s refusal to guess never reached anybody. Two silences
  beside it: the cliff detector fires only on a ~90% drop held for two weeks and
  never said so, and the query set is capped at the API row limit with no
  pagination, dropping the long tail the beyond-30 band is made of — the band the
  report tells the operator to rank the brief by.
- **`sitemap_audit.py` printed its truncation notice to stderr**, under a comment
  saying a silent cap reads as "this is the whole site". Any run capturing stdout —
  which is how the skill's own examples use it — lost the caveat exactly when the
  count became evidence.

### Fixed — the instruments contradicted the doctrine

- **The auditor emitted the H1-count line `onpage-checks.md` calls a non-finding**,
  pointing at `intent-and-content.md`, which carries no H1 guidance at all. An agent
  reading "3 H1 elements" in a findings table writes "consolidate to one H1", which
  is on the myth list. Both H1 findings point at the owning section now, and the
  message carries the reason.
- **The `thin` finding cited a study that refutes its premise.** It fired at a bare
  300-word floor and pointed at the information-gain section, which says "length
  barely matters". The threshold appeared nowhere else in the repository. It is
  `low-extractable-text` now and states what it is not.
- **`subheads-thin` dropped the qualifier its own doctrine attaches** ("on a long
  page"), so a four-section pricing page collected a finding the doctrine does not
  support.
- **No script finding carried an evidence tier**, and non-negotiable #2 makes the
  tier the multiplier in `priority = (impact × confidence) / effort`. Severity alone
  reached the agent, so the number that orders the plan was invented per finding with
  no documented mapping. Declared in `FINDING_TIERS`, enforced by the validator.
- **`tooling.md` capped the same evidence at two tiers in one sentence** — a
  third-party index at `STUDY` and "an inference from public data" at `HYPOTHESIS`,
  when a third-party index *is* public data — and mapped three of six rungs, leaving
  the rung `page_audit` and every `view-source` observation sit on undefined. All six
  carry a stated ceiling, and the reason rung 6 is last (coverage, not reliability)
  is written down.
- **`onpage-checks.md` claimed `page_audit.py` automates the starred items.** Three
  of eight are cross-page or judgement calls it cannot make, so a sweep marked
  covered on that reading reported an absence as coverage.

### Fixed — claims about the skill that were false

- **The myth count was wrong in three of its four homes** (README's closing pitch
  29, SKILL.md 30, the Cursor rule 29, against 32 rows) while the guard read the one
  sentence that had drifted before. The two short lists disagreed too: fourteen items
  in SKILL.md and thirteen in the Cursor channel, with the tracking-parameter myth
  missing from the copy that ships to Cursor users.
- **The play count said 60 against 61 rows**, after an earlier correction from 59.
- **The Prowl tool count said ~408 in the README** where two references said ~448.
- **`CONTRIBUTING.md` named two of the four gate commands** and called CI "the same
  two"; CI runs four. A contributor following the docs ran half the suite. The README
  repeated the same pair.
- **The README described a two-script repository.** Six scripts ship, three of them
  shell out to `gcloud`, and the security posture — the section a reader consults
  precisely because they will not read the code — understated what runs.
- **"Every benchmark carries its own date and sample size" was false**: 36 of 140
  rows were undated at both row and section level, and the whole Operational block
  had a two-column shape with nowhere to put a source, in the file whose header says
  "Always cite the date". Those rows name their source or say **undated**.
- **`evidence-tiers.md` said the validator compares "the two copies"** of the tier
  vocabulary; it reconciles four homes, which CONTRIBUTING and DOCMAP already said.

### Fixed — provenance

- **"PageRank decays ~85% per hop" inverted the damping factor** in all three of its
  homes. 0.85 is the share modelled as *passing*: read as loss, three hops retain
  0.34%; read correctly, ~61%. The two prescribe different architectures, and the
  claim had no source, date or tier anywhere. The depth rule keeps its own field
  evidence and never needed it.
- **A patent asserted live behaviour untiered**, against the rule the same corpus
  applies correctly elsewhere (`evidence-tiers.md` rule 5).
- **The read budget was one engine's `FIELD` median presented as the answer-engine
  first read.** The window's basis travels in the payload and the finding text.
- **`algorithm-updates.md` was stamped older than its own newest row** (2026-07-28
  against a row dated 2026-07-30), and the README carried a different stamp for the
  same corpus. Two facts, stated separately, with the newest-row line checked.
- ~18 numeric claims across five references gained a tier and a date. The same
  figure was tiered in one file and bare in another, and the bare copy is the one an
  agent lifts.

### Fixed — structure

- **Four section ids were defined twice with different content.** `SKILL.md` routes
  track D to two files and both numbered their sections `D1`, `D2`, `E1`, `E2`, so
  "run D1" had two answers. The sweep owns `O1`–`O5`.
- **A misaligned table row silently deleted a play's evidence tier**:
  `growth-plays.md` P5 had six cells under a five-column header, in the file whose
  closing rule is "never ship a FIELD or HYPOTHESIS play sitewide".
- **`technical-checks.md` numbering had four holes and the sweep sat after the B
  track.** `A3`–`A6` never existed; the sweep is `A3` now and the scheme is stated.
- **Two `myths.md` pointers pointed at rows that do not exist**, so an agent
  following them found nothing and improvised the guardrail.
- **The experiment record was a third deliverable with no skeleton**, and the audit
  template had no slot for the evidence rung SKILL.md requires.
- **`experience-signals.md`'s CWV thresholds were inserted mid-list**, splitting the
  evidence list in two.

### Added — eleven reconciliation guards, each watched failing first

The myth count in all four homes plus both short-list sizes; the play count; the
Prowl count; the gate commands against CONTRIBUTING, README and CI; per-finding tier
coverage; the CWV bands against their documented home; the two freshness facts;
section-id uniqueness; table rows with more cells than their header; backticked
`references/*.md` pointers; and the slash command's non-negotiable count, since it
was the third doctrine channel and the only unguarded one. Every one has a
planted-defect step in CI, and all twelve pre-existing negative self-tests were
re-run after the code changes and still fail as designed.

### Added — the registers a fresh clone was missing

`CLAUDE.md`, `docs/superpowers/backlog.md` (eight rows, computed priorities) and
`docs/superpowers/verification.md` (nineteen rows: 4 observed, 6 test-only, 4
planted-and-observed, 6 never). Every rule the repository runs on lived only in the
operator's global instruction files, which do not travel with a clone, and there was
nowhere for a deferred item to survive between runs. `pipeline.json` moves out of the
root, where a finished run's decisions read as configuration. DOCMAP gains nine
single-home rows and eight propagation rows; DECISIONS gains five entries.

## v0.12.0 — 2026-08-06

### Added
- **`references/discover.md`** — Discover audited as its own surface. The skill
  mentioned Discover 42 times and mentioned `og:image` and `max-image-preview`
  **zero** times, so the one check whose failure is binary was the one it could
  not make. Carries the two tags without which no card renders, image
  requirements, the two metatags reported to halt the pipeline entirely, the
  freshness window, and a four-command audit.
- **Sitemap protocol** in `references/technical-checks.md` — the namespace and
  schema contract, the five characters that must be escaped (and why `&` in a
  query string is the one that actually breaks files), W3C Datetime for
  `lastmod` and why a build-stamped one is worse than none, the 50,000/50MB
  limits, `robots.txt` submission, and a mechanical check rather than an eyeball.

### Notes
- **The new reference states its own evidence tiers in its opening section**, and
  they are not uniform. Google's documentation carries the image and
  `max-image-preview` requirements (CONFIRMED, verified 2026-08-06 against *Get
  on Discover*); the parsing fallback chains, freshness buckets and
  pipeline-blocking metatags come from one practitioner's SDK reverse-engineering
  and ship as **FIELD**. Mixing the two silently would have been the exact
  failure `references/evidence-tiers.md` exists to prevent — a plan someone funds
  should not treat "Google says" and "one researcher observed" as the same claim.
- `discover.md` is in `REQUIRED_REFERENCES`, with its own negative self-test:
  deleting it must fail the validator.

## v0.11.2 — 2026-08-05

A self-audit of the two releases above, run on the same two gates the pass itself
used. Seven defects, five of them mine.

### Fixed
- **A 2017 engine statement was dated 2026.** Googlebot's ~9,000px render
  viewport is John Mueller's advice from November 2017, not a finding from this
  window — the recent report merely restated it. Both the benchmark row and the
  technical-checks passage now date the confirmed half to 2017 and mark the
  practitioner half (that the expansion fires listeners exactly once) as the
  unverified 2026 observation it is. Dating a claim to the post that reminded you
  of it is the exact rot `benchmarks.md` exists to prevent.
- **A second split table**, in `threats-and-defense.md`: two detection rows sat
  behind a blank line and rendered outside the table. Second occurrence of the
  class in one run, so `validate.py` now rejects a blank line inside any table in
  the skill — watched failing on a planted seam.
- `growth-plays.md` G29 was inserted before G28.
- Per-page entity counts are **medians** (15–172), which the study says and the
  reference did not.
- The B2B page-type counterweight in `ranking-model.md` quoted a sample size that
  no primary source supports; the observation stays, the number is gone.
- The S-CTS row now carries the paper's title, authors and its own wording for the
  platform — the figures were written from secondary coverage first and confirmed
  against the paper only during this audit, which is the wrong order.

## v0.11.1 — 2026-08-05

### Fixed
- Two myth-guard rows added in v0.11.0 were separated from the claim table by a
  blank line, so they rendered as loose text instead of table rows. Found by a
  new validator check rather than by eye.
- `validate.py` now compares the README's myth-guard count against the number of
  rows in `myths.md`. A prose count sitting next to the list it counts has now
  drifted twice in this repo — nineteen references against twenty-one enforced,
  and this one — which is the bar for moving a rule off the page into a check.

## v0.11.0 — 2026-08-05

A two-week window of practitioner sources, screened on two gates: does it
contradict what this skill already holds, and does the number survive its primary
source. Eleven items entered unchanged, nine after their claim was narrowed, five
as detection only. Nine were refused, three of them for contradicting evidence
already in the corpus — and the refusals are recorded, because a rejected claim
that leaves no trace returns next quarter wearing the same confidence.

The primary-source pass removed three figures, refuted one field name and
narrowed one claim **after** they had passed the first gate. That is the pass
earning its keep: every one of them reads as mechanical, and every one would have
shipped as fact.

### Added
- **Rendering as a second budget** (`technical-checks.md`). Crawl budget counts
  URLs; the render queue decides how many of them ever run their JavaScript,
  which is the ordinary cause behind *Crawled – currently not indexed* on a JS
  template. The diagnostic is written in the form that can be executed — Last
  crawl plus the stored render under *View crawled page*, against the raw source,
  then a live test. The field the source named for it does not exist in the tool.
- **Googlebot stretches its viewport once** to the page's full initial height
  instead of scrolling, so a sequential infinite scroll never loads its second
  batch and an unconstrained hero pushes the content thousands of pixels down the
  render.
- **Mobile-first status divergence** — a desktop-only 404 is not the response
  being read — and the single internal link that keeps a dead URL in rotation.
  Both are now in the mechanical sweep.
- **Entity extraction has an instrument problem** (`entity-and-brand.md` G3,
  `tooling.md`, `benchmarks.md`). Across 166 top-ranking pages, four
  general-purpose extractors put 46.6–65.1% of their output on material with no
  trace in Google's own vocabulary for the query, and the budget-LLM option
  rewrites two entity sets in five between identical runs. The rule: the tool
  proposes, the AI Overview / People Also Ask / related searches decide.
- **A loop that turns the GSC generative report into prompts you can test**
  (`measurement.md` J3), recording citation and mention as separate outcomes.
- **Service-area businesses** get the block they never had
  (`architecture-and-equity.md`): city-level areas, one real page per city,
  reviews as the geographic signal, citations without an address, and a geo-grid
  boundary measured rather than assumed.
- **Five detection patterns** (`threats-and-defense.md`): the paid-mention market
  selling itself as AEO, synthetic consensus with its documented case,
  retrieve-and-switch, canonical pulsing from expired domains, cluster-level
  detection of coordinated generation, and review-queue attacks.
- Layout split tests, editorial trend-onset timing, on-site UGC read honestly,
  map-pack call attribution, and a first-party reviews section with its gating
  guardrail.

### Fixed
- **The evidence-tier vocabulary had two homes and they disagreed.** `FIELD` read
  as "a single practitioner case" in `evidence-tiers.md` and "repeated
  practitioner reports" in `CONTRIBUTING.md` — one label, two admission bars.
  `evidence-tiers.md` is now the single home, CONTRIBUTING quotes it verbatim,
  and `validate.py` fails on drift. The guard was watched failing against both a
  drifted definition and a removed row before it was trusted.
- **`onpage-checks.md` reported a non-finding.** "Several H1s" sat in the
  crawler-understanding table while Google states the count carries no penalty.
  The check survives as document structure and accessibility; what replaces it is
  the meaning test on the mobile render, which is the loss that is real.
- Two myths retired: the five-second render limit (the rendering service pauses
  its own clock during fetches; the real ceiling is an event loop that never
  idles) and the multiple-H1 penalty.

### Changed
- Alice AI figures move to Yandex's Q2'26 release — 42% of queries, 49.5M monthly
  users — with the Q1 point kept beside it as a trend rather than replaced.
- The generative-features opt-out is priced: the reported cost is Top Stories
  shown inside an AI Overview, scoped and unconfirmed by Google.
- Search-operator recon is demoted to HYPOTHESIS with both readings named, and
  routed through "prove it on a known-positive query first".

## v0.10.0 — 2026-08-04

An eighth non-negotiable, four new scripts, and the literature that bounds the
one study this skill was leaning on.

The run started as an audit of every SEO/AEO skill installed on one machine —
twenty-six of them. None contributed knowledge: no mechanism, number or argument
turned up that these references did not already hold. What they did expose was
the opposite gap. This skill named evidence sources it had no way to collect, and
two of its own instruments were quietly reporting assumed data as measured.

### Added
- **Non-negotiable #8 — instruments declare their own blind spots.** Rules #1 and
  #7 govern what the auditor writes; neither can see a tool that blends or omits
  before the auditor looks. `validate.py` enforces it, and the Cursor channel is
  now count-checked against SKILL.md — it had shipped five non-negotiables where
  SKILL.md carried seven, so Cursor users ran without the measured-vs-assumed rule.
- `scripts/url_inspection.py` — the Google-selected canonical against the declared
  one, coverage state, robots verdict. The engine's own answers, so findings built
  on them are CONFIRMED. The skill cited URL Inspection in eight places and could
  not collect it.
- `scripts/sitemap_audit.py` — declared URLs clustered into the template families
  a site actually ships, derived from its own URLs. It refuses orphan detection: a
  sitemap holds no link graph.
- `scripts/psi_pull.py` — CrUX field and Lighthouse lab reported separately, judged
  at the 75th percentile. Absent field data is reported absent, never as a pass.
- `scripts/preflight.py` — step 0's "test the access, do not assume it", performed.
  Each failure names which independent gate it hit; three of them answer 403.
- `gsc_pull.py` derivations — cannibalization, and a **CTR curve built from the
  property's own rows**. Industry CTR tables are on measurement.md's do-not-measure
  list; a hardcoded "under 3%" threshold is the same error one step further from
  the data. Bands under five rows yield no baseline at all.
- `benchmarks.md` — **C-SEO Bench** (NeurIPS 2025, 1,921 queries): under competition
  the GEO methods are mostly ineffective, and in retail a traditional-SEO baseline
  was ~7.6x more effective. It bounds Aggarwal et al. (KDD '24), which this file
  quoted without it. Also PAWC named as the unit, the Similarweb recommendation
  data, llms.txt consumption (97% of files get zero AI requests), and title and
  description rewrite rates.
- The visibility ladder in `measurement.md` — retrieved / cited / mentioned /
  recommended, each governed by a different mechanism, so the gap between two rungs
  is itself the diagnosis. Plus the rule-out check in the prompt set.
- `technical-checks.md` — geo-redirects and content negotiation, a whole class of
  locale invisible to staff who browse from the country that works.
- `experience-signals.md` — the CWV thresholds this file spent its length fixing
  without ever stating.
- `docs/DOCMAP.md`, `docs/DECISIONS.md`, `scripts/check-docs.sh`,
  `docs/superpowers/retro.md`.

### Fixed
- `page_audit.py` reported JS-injected JSON-LD as absent schema. On any Yoast,
  RankMath or AIOSEO site that was a false finding — the exact defect this skill
  exists to prevent. Every report now carries the caveat and the way to confirm.
- `sitemap_audit.py` parsed in O(n^2): 10,000 URLs took 14.8s and a 60,000-URL
  file never finished. Now 0.16s and 0.52s for the full 50,000 the spec permits.
- Silent truncation in the sitemap cap, and `None` rendering as a value in
  psi_pull. Absence must read as absence.
- `measurement.md` — GA4 consent-mode modelling blends observed and estimated
  behaviour inside one number. The three activation conditions, the reporting
  identity, the visible indicator and the BigQuery escape hatch are recorded.
- Reference count in CONTRIBUTING (nineteen -> twenty-one) and the Prowl tool
  count (408 -> 448).

### Verification note
Three figures carried in from other skills failed verification against primary
sources and are NOT in this release: `userDeclaredCanonical` (the API returns
`userCanonical`), "+41% for Quotation Addition" (the paper groups three methods
and says over 40%), and "~9% of post-recommendation visits arrive as AI referrals"
(absent from the source). CI fails if the first ever reappears.

## v0.9.3 — 2026-07-30

### Added
- **`displayName`** ("SEO + AEO Audit") in both manifests — the picker shows
  `name` otherwise, and `name` is kebab-case because it namespaces components.

## v0.9.2 — 2026-07-30

### Fixed
- **`argument-hint` in `/seo-aeo-audit` parsed as a two-item list**, split on the
  comma inside it, because the value was unquoted — in YAML a bare `[...]` is a
  flow sequence. Quoted with single quotes, since the hint itself contains double
  quotes. Found by `claude plugin validate --strict`, which now runs in CI
  against both this plugin and its marketplace manifest.
- **`homepage` and `repository` sat at the top level of `marketplace.json`,
  where Claude Code does not recognize them.** They are plugin-entry fields;
  moved there, so the values reach the plugin listing instead of being ignored.

## v0.9.1 — 2026-07-30

### Changed
- `license: MIT` declared in the `marketplace.json` plugin entry and in the
  skill's front matter. The `LICENSE` file reaches neither the plugin listing
  nor an installed skill, so the terms were a repository visit away.

## v0.9.0 — 2026-07-30

Tracking parameters get their own mechanism, separate from facets and filters.
The trigger was a community thread («Site Growth», Jul 2026) about a large Shopify
store where a `robots.txt` `Disallow` on `utm_*` URLs was proposed as a
crawl-budget win — and the reference set could be read as endorsing exactly that,
because tracking parameters sat inside the facet-and-filter guidance with no case
of their own.

### Added
- `technical-checks.md` A2 — **"Tracking parameters are not facets"**, the new
  owner of the mechanism. UTM variants carry no independent demand, so the whole
  job is consolidation and *crawled, not indexed* is the canonical working rather
  than a leak. A `Disallow` cuts off a crawl Google performs legitimately, cannot
  improve consolidation (a blocked URL never sees the canonical) and cannot touch
  the one real failure case: a parameterized URL that out-signals its canonical
  is selected despite the tag, and `robots.txt` changes no signal. The lever is
  one step up, at the source — strip tracking parameters from internal links and
  from affiliate and partner placements you control, and leave genuine
  third-party tracking URLs crawlable, because they are real referrals carrying
  real equity. Split tiers: `CONFIRMED` for the engine-documented mechanics,
  `FIELD` for the link-accumulation trigger.
- `technical-checks.md` A2 — hosted-platform duplicates priced before tracking
  parameters: Shopify serves every product under
  `/collections/{collection}/products/{handle}` as well as the canonical
  `/products/{handle}` and appends `?variant=` per variant, so one product in
  five collections with six variants is dozens of crawlable strings before a
  single UTM exists (`CONFIRMED`, reproducible in any store's crawl). Plus the
  scale check that has to precede the finding: the GSC Pages report grouped by
  reason, where *Alternative page with proper canonical tag* closes the finding
  and *Duplicate without user-selected canonical* is the finding.
- `growth-plays.md` — play **L13**: tracking-parameter URLs named as the
  crawl-budget problem, or already sitting under a `Disallow`.
- `myths.md` — row: "`Disallow` the UTM URLs to protect crawl budget" (30 refuted
  tactics now).
- `tooling.md` — the rung-2 fallback for crawl-waste work with no server logs.
  Shopify, Wix, Squarespace and comparable SaaS hosts expose no raw access logs,
  so rung 1 does not exist there and the finding caps at rung 2: GSC Crawl Stats
  gives host-level shares, totals and status mix, never per-URL truth. Say that
  in the report instead of presenting a crawler's URL count as crawl data.

### Changed
- `technical-checks.md` A2 — the index-tiering Tier 3 line now reads "facet
  parameter combinations" and states explicitly that tracking parameters are
  **not** in that bucket; crawl-budget killer #3 no longer lists tracking params
  alongside session IDs without qualification, and routes to the new block before
  anyone spends a `robots.txt` line on them. This is the internal contradiction
  the thread exposed.
- `SKILL.md` — the myth guard's short list grows to fourteen of thirty and now
  carries the tracking-parameter block, so the correction is reachable without
  loading `myths.md`.
- `README.md` — myth count 29 → 30, plays 59 → 60, freshness date and line total
  refreshed, tracking-parameters case named in the technical row.
- `docs/research/2026-07-source-distillation.md` — PART F records the source and
  the per-claim tiers (repo-only; not shipped to agents or npm).

## v0.8.1 — 2026-07-30

### Changed
- **README** — `agent-sync` added to the family list, and the install block now
  carries all three family commands (`install`, `update`, `list`) plus the
  restart note. The registry copy of the README only moves on a release, so a
  doc fix that stays on `main` reaches nobody.
- `CONTRIBUTING.md` — how to run `test/validate.py` and what a PR is checked
  against.

## v0.8.0 — 2026-07-29

Bulk market data through one MCP endpoint, and the evidence discipline that has
to travel with it. Written from a full audit run against a live property, so
every cost and gotcha below is measured rather than assumed.

### Added
- `references/prowl-mcp.md` — the Prowl MCP as a rung-5 source: ~408 provider
  tools (DataForSEO, Majestic, SpyFu, SearchAPI's 60+ engines, Firecrawl) behind
  one pay-per-call endpoint, for when there is no Ahrefs or Semrush seat. Routed
  by track, with the tools that carry each one, observed per-call costs, and the
  operating notes that cost time to learn: `prowl_call_tool` nests its arguments
  under `params`, failed calls are not billed, responses run 50-70 KB so they
  belong in a file rather than the context window, and not every endpoint accepts
  `order_by`. Carries an explicit disclosure that Prowl is a commercial product
  and nothing in the skill requires it.

### Changed
- `tooling.md` — Prowl added to rung 5 under the same "estimates, never ground
  truth" cap as Ahrefs and Semrush, plus a new rule: **two third-party indexes
  agreeing is a stronger `STUDY`, not a `CONFIRMED`**. Four routing rows added:
  demand validation against two independent volume datasets, sizing a whole
  competitive set in one call, anchor profiling **filtered on spam score first**,
  and finding which pages in a niche actually earn links. The AI-visibility row
  now names the `dataforseo_ai_llm_mentions*` and per-engine `ai_*_responses`
  tools for running the AEO prompt set at volume.
- `SKILL.md` Step 0 — **test access, do not assume it**. A connected MCP server
  is not a working one: API tiers gate endpoints and tokens carry narrower scopes
  than the dashboard suggests. Probe the one call each source exists for before
  planning around it, and record the result — "connected but returns
  `Insufficient plan`" is a finding the next audit needs.
- `SKILL.md` Step 1 — an explicit fallback for **no first-party access at all**:
  what a third-party index can still establish (current rankings, link-profile
  size against a sized competitive set, whether the target phrases carry demand),
  capped at `STUDY`, and enough to tell a cold start from a decline — which need
  opposite plans.

### Also added — the host-variant blocker
`technical-checks.md` A0 gains a check that nothing else in the file caught: **every
host variant must actually resolve**. A dead `www` kills every inbound link,
citation and typed visit that used it, and it never shows up in a crawl that
starts from the canonical host.

With it, the diagnostic that goes with it — **read the error body, not just the
status**. Cloudflare Error 1000 ("DNS points to prohibited IP") presents as a bare
403: a proxied `www` CNAME pointing at an apex whose own A records already hold
CDN addresses, so the edge refuses to proxy to itself and never contacts the
origin. Reading only the status sends you hunting for a WAF rule or a missing
redirect, and neither exists. The entry also covers the trap that follows —
PaaS origins route on the Host header, so repointing DNS when only the apex is
registered trades a 403 for a 404 — and the three real fixes in cost order, with
the API-token permission that actually gates Cloudflare Single Redirects
(`Zone → Single Redirect → Edit`, not `Zone → Config → Edit`).

### Fixed — release hygiene
- **v0.7.0 shipped Python bytecode to users.** The npm tarball carried
  `plugins/…/scripts/__pycache__/gsc_pull.cpython-314.pyc`, left behind by a local
  run of the new script: `files` whitelists `plugins` wholesale and both
  installers copy that tree verbatim, so the artifact reached every install. Two
  layers now stop it — the validator **fails** when any `__pycache__` or `.pyc`
  exists under `plugins/` (with a CI negative test), and `files` excludes them so
  an unclean working tree cannot publish one either. This is the same defect class
  as the test-suite leak fixed in v0.6.1, arriving through a different script;
  the guard is placed at the shipped tree rather than at either script.
- **Two parallel v0.7.0 releases reconciled.** Link-building extraction and the
  Prowl work were developed from the same parent and both numbered 0.7.0. The
  published 0.7.0 keeps its entry unchanged; the Prowl and host-variant work is
  this release.
- **Validator de-duplicated.** Compilation, the `from __future__` requirement and
  the stdlib rule ran twice for `page_audit.py` — once in the per-script loop and
  once in an older block. The older block now carries only what is unique to it,
  the finding-anchor resolution.
- **README counts corrected**: nineteen/20 contract files → **21**, and the
  distilled-line figure re-measured (~4,300). Link building and bulk market data
  gained rows in the knowledge table.

### Why the two-index habit is now a rule
On the audit this release was written from, four programmatic pages were found to
target phrases one clickstream panel measured at zero. A second, independent
index then returned **no keyword record at all** for the same six phrases. That
turned "these pages have an intent mismatch" into "these pages target queries
that do not exist" — a different fix entirely, and one no single source would
have supported. The same run showed the inverse risk: the top anchors by
referring domains for two competitors were PBN spam at spam scores 60-89, links
pointed *at* them rather than built by them. Sorting without filtering would have
produced an anchor strategy copied from someone else's negative-SEO problem.

## v0.7.0 — 2026-07-29

Link-building extraction — the audit now produces a deliverable someone else
can execute, not only a diagnosis for the owner.

- **New `references/linkbuilding.md`.** Target selection, the two collection
  modes (Search Console reachable / not), anchor discipline, the exclusions a
  brief must name, and the CSV column contract.
- **New non-negotiable #7: never blend measured with assumed.** A link-building
  CSV always carries both, so a `source` column separates them and the volume
  cells of an unmeasured row stay **blank, not zero** — `0` reads as "measured,
  no demand", blank reads as "nobody has checked". This one matters because the
  reader spends a budget against it.
- **New `scripts/gsc_pull.py`** (stdlib only, local ADC auth). Pulls what no
  crawl can see: the query set with positions, and a cliff detector that only
  reports a drop which *held* — a decline and a cliff have different causes and
  only one of them is an algorithmic story. Names which of the three auth gates
  you hit (scope / API enabled / quota-project header) instead of returning a
  bare 403.
- **Position-split discipline.** Rank a brief by the position bands, never by
  impressions: a large impression count beyond position 30 is usually the
  biggest number in the account and worth the least.
- **Validator:** the new reference and script are required; the blank-not-zero
  rule, the `source` column and the CSV contract are asserted in the reference
  text; every bundled script is checked for compilation and stdlib-only imports.
  Four negative tests confirm each rule can fail.

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
