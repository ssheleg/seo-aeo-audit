# Coverage gap — what an agent-readiness grader asked that this skill could not answer

- **Date:** 2026-08-14
- **Trigger:** an external agent-readiness scanner (ora.ai / "orank") graded
  `sms-activate.app` **50/100 (C)** across four layers — Discovery 1/17, Access
  41/60, Usability 39/67, Payments 0/0 — and returned 58 line items.
- **Why this document exists:** the site had already been audited by this skill
  twice (`docs/seo/audit-2026-07-28.md`, `audit-2026-08-07.md` in that project).
  Roughly half the grader's findings named things **none of the ten tracks looks
  at**. That is a coverage gap, not a disagreement, and a coverage gap that a
  third party found first is worth writing down in full.
- **What shipped from it:** **v0.19.0** — track K, `references/agent-readiness.md`,
  `scripts/agent_surface.py`, a myth-guard boundary, one confirmed `preflight.py`
  defect and two generalized guards.
- **Status of the backlog below:** open. Items are ordered by whether the skill
  can close them at all.
- **Version note.** The work below was written under a `v0.18.0` CHANGELOG
  heading and **released as v0.19.0**; `v0.18.0` was never tagged and is not on
  npm. Where this document said "v0.18.0 ships X", it now says the release does.
  Corrected 2026-08-15 during a re-audit of this work.

## Contents

- [1. The mapping — all 58 grader checks against the skill](#1-the-mapping--all-58-grader-checks-against-the-skill)
- [2. What the grader got wrong, and what that taught the design](#2-what-the-grader-got-wrong-and-what-that-taught-the-design)
- [3. Defects in this repository found by running it](#3-defects-in-this-repository-found-by-running-it)
- [4. Backlog — what this release does not close](#4-backlog--what-this-release-does-not-close)
- [5. The design rule this whole episode produced](#5-the-design-rule-this-whole-episode-produced)

## 1. The mapping — all 58 grader checks against the skill

Legend for **Before**: `covered` — a track already owned it · `partial` — a track
owned the neighbouring question but not this one · `absent` — nothing in the skill
looked at it.

Legend for **Now**: `K<n>` — the section of `references/agent-readiness.md` that
owns it · `script` — `scripts/agent_surface.py` probes it mechanically · `out` —
deliberately not covered, with the reason in §4.

### Discovery (grader: 1/17)

| # | Grader check | Before | Now |
|---|---|---|---|
| D1 | Developer resource discoverability (name-based search finds your API docs) | partial — tracks D/G own query coverage and brand, not the developer subset | K2 + track D. Not scriptable: it is a SERP observation |
| D2 | Wikipedia / Wikidata entity, P856 → the domain | **covered** — `entity-and-brand.md` sizes both, including Wikidata at ~half a Wikipedia article's pull at a far lower bar | unchanged |
| D3 | ARD catalog at `/.well-known/ai-catalog.json` | absent | K2 · script |
| D4 | Brand-name search returns the domain | **covered** — `entity-and-brand.md` | **G1b** — the two-query collision test, added because the covered version had no procedure |
| D5 | Listed in the ChatGPT app / connector directory | absent | K9 bucket 3 — a submission, not a ticket |
| D6 | `robots.txt` AI-crawler policy | partial — `technical-checks.md` owns robots syntax; the three-way AI split was missing | K2a · script |
| D7 | npm / PyPI SDK package | absent | K8 `K-15` — a maintenance commitment |
| D8 | `AGENTS.md` / agent configs in a public repo | absent | K9 bucket 3 — needs a public repo |
| D9 | Agent Plugins `plugin.json` manifest | absent | K9 bucket 3 |
| D10 | Listed on skills.sh | absent | K9 bucket 3 |

### Access (grader: 41/60)

| # | Grader check | Before | Now |
|---|---|---|---|
| A1 | Developer portal at `/developers` | partial — `architecture-and-equity.md` owns hubs, not this one | K5 + **K2b · script** (probes `/developers`, `/docs`, `/api`, `/api-docs`) |
| A2 | Agent instruction / "when to use this" in `llms.txt` | absent | K2 · script (it greps for the section, not just the file) |
| A3 | Agent Skills index `/.well-known/agent-skills/index.json` | absent | K2 · script |
| A4 | A2A agent card `/.well-known/agent-card.json` | absent | K2 · script |
| A5 | MCP well-known discovery | absent | K2 · script |
| A6 | `?mode=agent` view | absent | **out** — §4 |
| A7 | Markdown URL fallback (`/index.md`) | **refuted** — `myths.md` row 2 | K3, bounded: the myth stands for *being found*, the twin is for *being read* |
| A8 | API docs linked from the homepage | partial — internal linking is track C, but not "does the SSR HTML carry the link" | **K2b · script** — generalized to every conventional entry point, read from the server-rendered root |
| A9 | skills.sh skill quality | absent | K9 bucket 3 |
| A10 | JSON-LD `sameAs` entity linking | **covered** — `entity-and-brand.md` | unchanged + script probes it |
| A11 | Schema type breadth | **covered** — `aeo-geo.md`, `onpage-checks.md` | unchanged + script probes it, **with the one-url caveat** |
| A12 | API catalog (RFC 9727) | absent | K2 · script |
| A13 | NLWeb schema feeds (`schemamap:`) | absent | K2a · script |
| A14 | HTTP `Link` headers (RFC 8288) | absent | K6 · script |
| A15 | Per-section `llms.txt` | absent | K2, myth-bounded |
| A16 | Sitemap `lastmod` freshness | **covered** — `technical-checks.md` | unchanged + script reports the percentage |
| A17 | Speakable markup | partial — `aeo-geo.md` mentions it | script probes it; tier stays `HYPOTHESIS` |
| A18 | Organization schema completeness (address, contactPoint) | **covered** — `entity-and-brand.md` | unchanged + script probes it |
| A19 | Trust anchor pages (`/about`, `/contact`, `/privacy`) | **covered** — `entity-and-brand.md`, `demand-and-conversion.md` | unchanged + **K2b · script** measures each one's server-rendered length with comments stripped |
| A20 | `rel="alternate" type="text/markdown"` advertisement | absent | K3 · script — including whether the advertised URL *actually* serves markdown |
| A21 | Markdown agent docs at a root path | **refuted** as a GEO tactic | K3, bounded |
| A22 | Markdown content negotiation + `Vary: Accept` | absent | K3 · script. The `Vary` half is `CONFIRMED`: without it a CDN serves the wrong variant |
| A23 | Bot-UA markdown serving | absent | K3 — reported as a **fact in both directions**, never as a win: content that differs by user agent is the mechanical definition of cloaking |

### Usability (grader: 39/67)

| # | Grader check | Before | Now |
|---|---|---|---|
| U1 | MCP server / manifest | absent | K8 `K-13` — business decision with a trigger |
| U2 | OAuth 2.0 support | absent | K5 — and K5 says plainly that a self-serve API key is a valid answer |
| U3 | Agent auth discovery metadata (RFC 9728 + RFC 8414 + `agent_auth`) | absent | K5 · script (PRM on the API host) |
| U4 | CLI tool | absent | K8 `K-15` |
| U5 | Multi-language SDKs | absent | K8 `K-15` |
| U6 | Web Bot Auth directory | absent | K2 · script |
| U7 | RFC 9728 protected-resource metadata | absent | K5 · script |
| U8 | `/auth.md` exists | absent | K2/K5 · script |
| U9 | `/auth.md` structure (Discover / Pick / Register / Claim / Use / Errors / Revocation) | absent | K5 |
| U10 | `agent_auth` endpoints reachable | absent | K2 stale-file rule — every advertised URI must resolve |
| U11 | WebMCP in-page tools | absent | K6 — `HYPOTHESIS`, Experiments bucket |
| U12 | Rate-limit response headers | absent | K6 · script |
| U13 | REST async-job pattern (`202` + status location) | absent | K4 · script (reads the spec) |
| U14 | MCP `server-card.json` | absent | K2 · script |
| U15 | Product + docs MCP coverage | absent | K8 `K-13` |
| U16 | Sandbox / test environment | absent | K5 |
| U17 | REST batch / bulk endpoint | absent | K4 · script |
| U18 | Agent onboarding friction | absent | K5 — named on a three-step scale: wall / speed bump / open |
| U19 | `WWW-Authenticate` hint on 401 | absent | K5 · script |
| U20 | REST versioning + deprecation policy | absent | K4 · script (`Sunset` / `Deprecation` / `deprecated`) |
| U21 | NLWeb `/ask` endpoint | absent | K6 — `HYPOTHESIS` |
| U22 | NLWeb SSE streaming | absent | K6 — `HYPOTHESIS` |
| U23 | Agent-friendly 404s | partial — `technical-checks.md` owns soft-404 collapse; the markdown recovery body was new | K6 · script |
| U24 | API schema complexity (operationIds, descriptions, typed responses) | absent | K4 · script |
| U25 | Function-calling compatibility | absent | K4 · script |

### Payments (grader: 0/0)

The grader defines a payments layer and scored **nothing** in it. Neither does
this skill. That is a shared blind spot rather than a pass — see §4, item B1.

**Totals**, counted off the rows above rather than stated beside them: **58**
grader checks — **7 already covered** by tracks A, D, F and G · **6 partial** ·
**2 already refuted** by `myths.md` · **43 absent**. Of the 43, this release gives
**32** a home in track K, routes **10** to business decisions (a public repo, a
package registry, a directory submission, an MCP deployment), and leaves **1**
deliberately out — `?mode=agent`, §4 C1.

## 2. What the grader got wrong, and what that taught the design

Every finding was reproduced by hand against production on 2026-08-14 before
being accepted. Four did not survive, and each failure mode is now a rule in K7.

| Grader said | Reproduced result | What it means for the skill |
|---|---|---|
| "No `sameAs` entity linking in JSON-LD — agents cannot disambiguate your brand" | `sameAs` **is present**, with exactly one target (`https://t.me/PrivatePhoneBot`) | The finding was right about the *consequence* and wrong about the *fact*. A report that misstates the observable loses the argument with the engineer who checks it. `agent_surface.py` reports the count and the targets, so "thin" and "absent" are different findings |
| "No extended schema types found — AI can only answer basic questions" | The **homepage** carries `Organization`/`WebSite`/`WebApplication`/`AggregateOffer`. `/numbers/whatsapp/canada` carries `Product`, `Brand`, `Offer`, `FAQPage`, `HowTo`, `BreadcrumbList`; `/pricing` carries `Service` + `OfferCatalog` | **One url is not a site.** This is the single most common false finding a grader produces, and it is now a blind-spot line printed in every `agent_surface.py` report plus a `--page` flag |
| "`?mode=agent` returns the same content as the homepage" | True in substance — but a naive byte comparison says they *differ*, because the CSP nonce is per-request | A diff is not a comparison. The script compares body length with a tolerance and says what it compared |
| "Consider blocking training-only crawlers (CCBot, ByteSpider) to earn full credit" | `robots.txt` explicitly **allows** CCBot | Not a defect. Whether to feed training corpora is a business decision about the company's content, and a scanner that awards points for one answer is scoring a preference. K2a states it as a decision with a trade-off, and the script reports the question as *answered* whichever way it was answered |

A fifth, subtler one: the grader awards points for `llms.txt` and Markdown twins,
which `myths.md` rows 1–2 refute with published numbers. The resolution is not to
soften the myth guard. It is that **the two claims are about different jobs** —
being found (refuted) versus being read cheaply once already here (a serving
decision). K3 and the new boundary section in `myths.md` hold that line, and K7
says outright that a grader's prescriptions are claims to check, not instructions.

## 3. Defects in this repository found by running it

Running the skill on a live site — rather than reading it — surfaced four defects
in the skill itself. All four are fixed in v0.19.0.

| # | Defect | How it hid |
|---|---|---|
| D44 | `preflight.py` probed `searchconsole.googleapis.com/v1/sites`. The property list lives under `/webmasters/v3`; only URL Inspection lives under `/v1`. The API answered with a Google 404 HTML page, which the gate classifier — written for the three ways this API says `403` — read as `permission` | It failed identically for **every** site, so it looked like a fact about the site. A previous audit worked around it by hand and wrote down the wrong cause (a missing `x-goog-user-project` header), which is now the second wrong explanation on record for the same bug |
| D45 | The gate classifier had no `quota-project` state. Local ADC is refused by this API until a quota project is bound, and that failure was reported as `permission` | The remedy for `permission` is a screen in Search Console. No grant on that screen can fix an unbound quota project, so the report sent the auditor to the wrong place with confidence |
| D46 | `SKILL.md` step 0 and `references/preflight.md` each carried a duplicated, half-overwritten sentence from a merge — `preflight.md`'s first section opened mid-sentence with the word "describing it," | Prose defects survive every structural guard in `validate.py`. Nothing checks that a paragraph is a paragraph |
| D47 | The reference-anchor guard and the `FINDING_TIERS` coverage guard were both written against `page_audit.py` by path | The moment a second script emitted findings, both guards exempted it silently — the exact class the 2026-08-10 audit named as "a guard written against one home of a fact that lives in several". Both now iterate `_bundled`, and the tier guard reads both emitter shapes |

## 4. Backlog — what this release does not close

Ordered by whether the skill can close it at all.

### A. Can close — deferred with a reason

| id | Item | Why it is not in this release |
|---|---|---|
| A1 | **`agent_traffic.py`** — parse a server-log export and count AI/agent user agents, forward-confirming reverse DNS to drop spoofers | This is the missing half of K1. Track K tells the auditor to measure agent demand before sizing the prize, and then hands them no instrument. Everything else in K stays `HYPOTHESIS` until this exists, which makes it the highest-value item on this list |
| A2 | **WebMCP bundle scan** — fetch same-origin script bundles and look for `document.modelContext.registerTool` and `toolname` / `tooldescription` form attributes | Feasible in stdlib (fetch + regex over the bundle), but it needs a bundle-discovery step and a size cap, and shipping it half-done would produce "not found" on every code-split site |
| A3 | **Web Bot Auth key-shape validation** — parse `/.well-known/http-message-signatures-directory` and check the JWKs are `kty=OKP`, `crv=Ed25519`, with `kid`, `nbf`, `exp` | Presence is probed today; validity is not. A directory serving malformed keys passes the current check |
| A4 | **Registry lookups** — npm / PyPI / Homebrew for an official SDK or CLI, checking `repository` and `homepage` point back at the domain | Three third-party APIs, each with its own rate limit, and the finding is a business decision anyway. Worth a `--registries` opt-in flag rather than a default probe |
| A5 | **`/auth.md` structure grading** — check the seven WorkOS sections and the spec anchor keywords are present, not just that the file exists | Cheap, but the draft is moving; a structural check against a moving draft produces false findings on a compliant file |
| A6 | **Reachability sweep for advertised URIs** — `OPTIONS` every URI found in `agent_auth`, an agent card or an MCP server card, and fail the ones that 404 | K2's stale-file rule is stated as doctrine and enforced by nothing. This is the check that makes "do not publish a file you cannot keep true" real |
| A7 | **A `--page` sweep** — accept a URL list so the markup checks run per template in one invocation | Today the one-url caveat is stated; the ergonomics still push toward running it once on the homepage, which is exactly the mistake the caveat warns about |
| A9 | **A guard that every CHANGELOG section has a tag** — `validate.py` enforces the four-way sync between the manifests and the CHANGELOG *top* entry, and nothing asks whether the sections below it were ever released | Found by re-auditing this work: the `v0.18.0` section reads as a release and no `v0.18.0` exists in git or on npm. One `git tag -l` per section, in the same file that already reconciles six other prose counts |
| A8 | **Redirect-chain reporting for every probe, not just entry points** — the `.well-known` and markdown checks still credit a followed redirect | The entry-point probe now compares final vs requested URL; the other probes do not. Same defect class, narrower blast radius, so it is listed rather than rushed |

### B. Should cover, and nothing does yet

| id | Item | Note |
|---|---|---|
| B1 | **Agentic payments.** The grader defines a payments layer and scores nothing in it; neither does this skill. The rails exist — agent-initiated payment protocols, delegated-authority mandates, per-call settlement — and a site that sells to agents will need a position on them | This is a candidate **track L**, not a section of K. Before writing it: establish what is actually deployed rather than announced, and keep every claim dated. `benchmarks.md` owns the numbers |
| B2 | **The `agent-readiness score` as a myth row.** "Buying an AI-visibility number as a single KPI" is already row 11; an agent-readiness grade is the same shape and is not named | Add a row, or extend row 11 explicitly to agent-readiness grades. K7 currently carries the argument without the myth table carrying the claim |
| B3 | **A prose-integrity guard.** D46 was two duplicated sentences that every structural check passed | A cheap version: flag a paragraph where the same 40-character opening appears twice within N lines, and flag a section whose first sentence begins with a lowercase continuation word. Both patterns are exactly what a bad merge leaves |

### C. Deliberately out of scope

| id | Item | Why |
|---|---|---|
| C1 | **`?mode=agent`** | There is no specification. It is one scanner's convention, and adopting it would mean shipping a check that rewards a site for guessing the same convention. If it converges on a spec, it becomes a K2 row |
| C2 | **Connecting to an MCP server to enumerate its tools** | Needs a protocol client and a transport; the bundled scripts are stdlib-only single files by design. The server card is the documented preview, and that is what K2 probes |
| C3 | **A composite "agent readiness score"** | The whole of K7 argues that a number is the wrong output. Emitting one here would contradict the reference that ships beside it |

## 5. The design rule this whole episode produced

A third-party grader found 43 checks this skill did not have. It also produced
four findings that did not survive reproduction, and two prescriptions this
skill's own evidence refutes. Both halves of that are the lesson:

> **Take a grader's absence findings as a to-do list to verify. Take its score as
> noise. Take its prescriptions as claims to check.**

The reason a grader can find a gap this skill cannot is structural — it probes a
fixed list, so it notices everything on that list and nothing off it. The reason
this skill can refuse a grader's prescription is also structural — it carries
evidence tiers, so "a scanner awards points for this" is visibly not the same kind
of claim as "a 100M-site experiment measured this". Track K is built to keep both
properties: the fixed list, and the refusal.

The trap it is built to avoid has a name now, and it is written into K1 rather
than left to judgement: **presence is `CONFIRMED`, effect is mostly
`HYPOTHESIS`.** A track whose findings are all one HTTP request away is the
easiest place in this skill to accumulate a checklist nobody can defend.
