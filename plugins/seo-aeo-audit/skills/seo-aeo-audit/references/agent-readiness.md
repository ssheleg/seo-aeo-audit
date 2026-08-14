# Track K — the agent surface: can a machine transact with this site?

Tracks A–J ask whether a **retrieval** system can fetch, read and quote the site.
This track asks a different question: whether an **agent acting for a user** can
discover the product, obtain a credential, call it, and recover when a call fails.
The two overlap in exactly one place — both want a fetchable, extractable page —
and diverge everywhere else. A site can be perfectly extractable and still be
unusable by an agent, and a site can pass every check here and be invisible in
search.

Run this track when the site sells something an agent could plausibly buy, call
or automate: an API, a SaaS product, a booking or purchasing flow, a data
service. Skip it for a content site with no programmable surface — publishing
`/.well-known/agent-card.json` for a recipe blog is how you teach an agent to
ignore the whole track.

## Contents

- [K1. The rule that keeps this track honest](#k1-the-rule-that-keeps-this-track-honest)
- [K2. Discovery — the well-known set, and what each spec actually says](#k2-discovery--the-well-known-set-and-what-each-spec-actually-says)
- [K2b. The entry points a machine tries, and the link that only exists after hydration](#k2b-the-entry-points-a-machine-tries-and-the-link-that-only-exists-after-hydration)
- [K3. Markdown representations — where the myth ends and the contract begins](#k3-markdown-representations--where-the-myth-ends-and-the-contract-begins)
- [K4. The API contract an LLM has to call through](#k4-the-api-contract-an-llm-has-to-call-through)
- [K5. Agent authentication — the discovery chain, not the login page](#k5-agent-authentication--the-discovery-chain-not-the-login-page)
- [K6. Runtime behaviour an agent depends on](#k6-runtime-behaviour-an-agent-depends-on)
- [K7. Third-party agent-readiness graders, and how to read one](#k7-third-party-agent-readiness-graders-and-how-to-read-one)
- [K8. The check table, with tiers](#k8-the-check-table-with-tiers)
- [K9. What to put in the plan](#k9-what-to-put-in-the-plan)

## K1. The rule that keeps this track honest

Every check in this track splits into two claims, and they carry different
evidence tiers:

| Claim | How it is verified | Tier it can reach |
|---|---|---|
| "This file / header / endpoint is absent" | one HTTP request, reproducible | `CONFIRMED` |
| "Publishing it will bring agent traffic or revenue" | needs a measurement nobody has here | `HYPOTHESIS` until logs say otherwise |

**Presence is measurable; effect mostly is not.** That asymmetry is the whole
discipline of this track. A missing `/.well-known/oauth-protected-resource` is a
fact. "Adding it will increase agent adoption" is a guess, and non-negotiable #2
forbids a guess from outranking a confirmed blocker in tracks A–C.

So the default routing is:

- **Cheap and specified** (a static file, a response header, an `operationId`) —
  ship it. Effort 1 keeps the priority score respectable even at `HYPOTHESIS`
  confidence, and a wrong guess costs a few hundred bytes.
- **Expensive and speculative** (build an MCP server, run an OAuth authorization
  server, publish and maintain SDKs in four languages) — this is an
  **Experiments-bucket** decision, not a Gains one, until the site can show
  agent demand. Size it against `references/experiments.md`.

**Measure the demand before sizing the prize.** Two sources answer it and both
are first-party:

1. **Server logs** — count requests by user agent for `GPTBot`, `OAI-SearchBot`,
   `ChatGPT-User`, `ClaudeBot`, `Claude-User`, `PerplexityBot`, `Google-Extended`,
   `Applebot-Extended`, `CCBot`, `Bytespider`, and any agent framework's default
   UA. Forward-confirm reverse DNS before believing a UA string
   (`references/threats-and-defense.md` covers the spoofing case).
2. **Requests to the agent surface itself** — once anything in K2 exists, the
   access log for those paths *is* the metric. Zero requests over a quarter is
   the answer to "should we build the MCP server", and it is a cheap answer to
   buy first.

An audit that recommends the whole of this track without either number has
skipped the diagnosis (non-negotiable #3).

## K2. Discovery — the well-known set, and what each spec actually says

These are the files an agent looks for before it asks a human anything. Status
column: **RFC** = published standard · **draft** = specification exists, not yet
an RFC · **vendor** = one vendor's convention that others copied · **grader** =
exists mainly because scanners score it.

| Path | What it declares | Status | Notes |
|---|---|---|---|
| `/robots.txt` | crawl policy per user agent | RFC 9309 | AI-crawler groups belong here explicitly; see K2a |
| `/llms.txt` | a curated map of the site for a model | vendor | Not a ranking or citation lever — `references/myths.md` row 1 holds the evidence. It is read by agentic browsers that were already sent here |
| `/.well-known/api-catalog` | linkset pointing at your API descriptions | RFC 9727 | `Content-Type: application/linkset+json;profile="https://www.rfc-editor.org/info/rfc9727"` |
| `/.well-known/oauth-protected-resource` | which authorization servers guard this API | RFC 9728 | Belongs on the host that **serves the API**, not the marketing apex |
| `/.well-known/oauth-authorization-server` | token, authorization and registration endpoints | RFC 8414 | Belongs on the authorization-server origin |
| `/.well-known/http-message-signatures-directory` | Ed25519 JWKs so bots can sign requests | draft (Web Bot Auth) | Pairs with RFC 9421 signatures; lets you tell a real agent from a spoofer |
| `/.well-known/agent-card.json` | an A2A agent's skills and endpoint | draft (A2A) | Only if you actually run an agent others can call |
| `/.well-known/mcp/server-card.json` | preview of an MCP server before opening a transport | draft | Also referenced from `llms.txt` in practice |
| `/.well-known/ai-catalog.json` | catalog of your agentic resources | draft (ARD) | agenticresourcediscovery.org |
| `/.well-known/agent-skills/index.json` | index of published Agent Skills | draft | Each entry needs `name` + `description` |
| `/auth.md` | prose walkthrough of how an agent gets a credential | draft (WorkOS) | See K5 |
| `/openapi.json` (or linked from the catalog) | the callable contract | RFC-adjacent | Quality matters more than presence — K4 |

**Do not publish a file you cannot keep true.** A stale `agent-card.json`
advertising a dead endpoint is worse than no card: the agent tries it, fails, and
has no fallback. Every URI advertised in these documents must resolve — an
`OPTIONS` preflight returning any status that is not `404` and not a DNS failure
is the cheap check, and it belongs in the verification column of the plan.

### K2a. Crawler policy is two decisions, not one

`robots.txt` groups AI user agents into three uses, and a single `Allow: /` for
everything answers only the first:

| Use | Agents (2026) | The decision |
|---|---|---|
| Answer-engine retrieval | `GPTBot`, `OAI-SearchBot`, `ChatGPT-User`, `ClaudeBot`, `Claude-User`, `PerplexityBot`, `Google-Extended` | Allow, if you want to be cited |
| Training-corpus collection | `CCBot`, `Bytespider` | A business decision, not a technical one — allowing it feeds models that may answer without linking |
| Everything else | unnamed agents | The `*` group already covers them |

Cloudflare's Content Signals policy (`Content-Signal: search=yes, ai-train=no`)
expresses the same split in one line and is machine-readable. **Neither choice is
a defect.** What is a defect is not having made the choice: an audit reports the
current state and names the trade-off, it does not smuggle in a business decision
about training data as a technical finding.

`Schemamap` / NLWeb schema feeds (`schemamap:` directive in `robots.txt`, pointing
at an XML map of JSONL/RSS structured-data feeds) sit in the same file and are
`HYPOTHESIS`-tier: the spec exists, adoption is thin.

### K2b. The entry points a machine tries, and the link that only exists after hydration

Before an agent reads any of the files above, it does what a person does: it opens
the root and looks for the obvious address. Two failures live here, and both are
invisible to anyone testing in a browser.

**Failure one — the hydration gap.** On a client-rendered site the header and
footer are assembled by JavaScript. The link to the API docs is in the navigation,
it works, every human sees it — and it is **not in the document the server sent**.
A crawler, an answer engine and an agent all read that document and stop. The
symptom is a page that is in the sitemap, returns 200, is linked from the site's
own menu, and is reachable from nothing.

Check it by reading the **server-rendered** root HTML and extracting same-origin
`<a href>` values, then asking which conventional entry points are missing from
that set. `scripts/agent_surface.py` does this and prints the table. Note two
mechanics that decide whether the result is trustworthy:

- **Normalize locale prefixes.** `/de/api` is a link to `/api` for this question.
  Without that, a nine-locale site reports the same gap nine times.
- **This is reachability, not equity.** How much authority flows through a link
  is track C ([architecture-and-equity.md](architecture-and-equity.md)). Whether
  the link exists in the delivered bytes at all is this check, and a page can pass
  one and fail the other.

**Failure two — the redirect that answers 200.** `/about-us` returns `301` to the
homepage. Any probe that follows redirects — `curl -L`, `urllib.urlopen`, most
scanners — then reports `200`, a title, and a healthy word count, all describing
the homepage. The About page does not exist and the check says it does.

> A redirect to the site root is how a site says "no such page" while answering
> 200. Compare the **final** URL against the requested path before believing any
> measurement taken from the body. This instrument had the bug and reported an
> About page with 1,564 characters that was never there.

The same rule covers `elsewhere` redirects: `/docs → /api` is fine and worth
recording, but the finding must name where it landed rather than silently
crediting the address that was asked for.

**The roles worth probing**, each with its conventional alternates — the role
matters, the spelling does not:

| Role | Tried | Why an agent wants it |
|---|---|---|
| developer docs | `/api`, `/docs`, `/developers`, `/api-docs` | the contract |
| sign-up | `/register`, `/signup`, `/join` | the credential |
| pricing | `/pricing`, `/plans` | can it afford the call |
| about · contact · privacy · terms | `/about`, `/about-us`; `/contact`, `/support`; `/privacy`; `/terms` | is this business real |

The last row is the **trust-anchor** set, and it carries a length check as well as
a status check: a page that exists and says forty words defines no entity
([entity-and-brand.md](entity-and-brand.md) G3 owns the mechanism). The
500-character bar third-party verifiers apply is a **convention, not a measured
threshold** — report it as one, and measure the text with HTML comments stripped.
Counting comments is not a hypothetical: it inflated a real trust-page measurement
by 60% and turned a page that fails the bar into one that passes it.

## K3. Markdown representations — where the myth ends and the contract begins

`references/myths.md` refutes "serve Markdown mirrors of your pages for LLMs" as
a **GEO tactic**, and that refutation stands: mirrors drew 0% of AI-crawler
visits against 4.6% for the HTML, and ChatGPT Deep Research does not follow `.md`
links. Nothing in this track overturns it.

The distinction that keeps both true:

> A Markdown mirror does not help you get **found**. It helps an agent that has
> already arrived **read you cheaply**. The first is a ranking claim and it is
> refuted. The second is a serving decision, and it is measured in tokens.

So the honest version of this recommendation is narrow:

- **One canonical Markdown document for the machine-readable facts** — pricing,
  the API contract, the capability list. Where a number has one home (facts,
  price list, spec), a Markdown twin of that home is cheap to keep true because
  it is generated from the same source as the HTML.
- **Content negotiation, if you serve Markdown at all.** `Accept: text/markdown`
  → `Content-Type: text/markdown`, **and `Vary: Accept`**. Without `Vary`, a CDN
  serves whichever variant it cached first to everyone — an HTML body to an agent
  that asked for Markdown, or worse, a Markdown body to a browser. The `Vary`
  header is not a nicety here; it is what makes the negotiation safe to enable.
- **Advertise it or do not serve it.** `<link rel="alternate" type="text/markdown"
  href="…">` in the head, or the equivalent `Link:` response header (RFC 8288).
  An advertisement pointing at HTML is worse than none — verify the target starts
  with a heading, not `<!doctype html>`.
- **A full `.md` twin of every content page is the refuted version.** It doubles
  the surface you must keep true, and the measured return is zero. If somebody
  wants it, it is an experiment on one section with a read metric, not a rollout.

Serving Markdown to a **bot user agent** that asked for HTML is a fourth thing
again, and it is the risky one: content that differs by user agent is the
mechanical definition of cloaking. It is defensible only when the Markdown is a
faithful representation of the same content — same facts, same prices, same
availability — and it is never worth the risk on a site with a manual-action
history. `references/threats-and-defense.md` owns that boundary.

## K4. The API contract an LLM has to call through

An OpenAPI document is not a document to an agent — it is the tool definition it
generates function schemas from. Four properties decide whether that generation
succeeds, and all four are checkable offline:

| Property | Why the agent needs it | Failure mode when absent |
|---|---|---|
| A unique `operationId` per operation | becomes the function name | The generator invents one from the path; two agents produce two different names for the same call, and neither matches your docs or your logs |
| A `description` (or `summary`) per operation | becomes the function description the model selects on | The model picks by path string, which is guesswork |
| Typed request and response schemas | validation, and knowing what came back | The agent parses prose or gives up |
| Declared error responses (`401`, `409`, `429`) with shapes | recovery | Every failure looks the same, so the retry is blind |

Two more that decide whether an agent can work at all:

- **Long-running work needs a followable pattern.** `202 Accepted` plus a status
  location and a job id in the body, documented in the spec. Without it, an agent
  either blocks on a request that will time out or polls a resource it invented.
- **Bulk work needs one call.** An agent acting on 200 items will make 200 calls
  if that is the only shape you offer, which is also how it hits your rate limit
  and looks like an attack.

**A versioning policy is a contract about change.** A version in the path or a
version header answers "which surface am I calling"; a documented `Sunset` /
`Deprecation` header (RFC 8594) answers "will it still be there next quarter".
Agents integrate against the second one. Versioning without a deprecation signal
is half the promise.

`scripts/agent_surface.py --openapi <url>` reports all of these per operation.

## K5. Agent authentication — the discovery chain, not the login page

The question is not "do you have OAuth". It is: **starting from one URL and no
human, can a program work out how to get a credential?** The chain has four
links, and a break anywhere ends the walk:

1. **The API returns `401` with a pointer.**
   `WWW-Authenticate: Bearer resource_metadata="https://api.example.com/.well-known/oauth-protected-resource"`.
   Without this an agent has to guess the well-known path, and a bare `401` with
   a JSON error body teaches it nothing.
2. **Protected-resource metadata (RFC 9728)** at that URL, on the host that serves
   the API — `resource`, `authorization_servers`, supported scopes, accepted
   bearer methods.
3. **Authorization-server metadata (RFC 8414)** at
   `/.well-known/oauth-authorization-server` on the AS origin, cross-linked back
   by being listed in the PRM's `authorization_servers`.
4. **A prose walkthrough at `/auth.md`** — `Content-Type: text/markdown`, leading
   with a top-level heading, with sections for Discover, Pick a method, Register,
   Claim, Use the credential, Errors and Revocation. The WorkOS draft
   (workos.com/auth-md) also defines an `agent_auth` block inside the AS metadata
   carrying `register_uri`, `identity_types_supported` (`anonymous`,
   `identity_assertion`) and a per-type sibling block. Whatever URIs that block
   or the prose advertises **must resolve** — see K2's stale-file rule.

**A self-serve API key is a valid answer to this track.** Not every product needs
an authorization server; what every product needs is a path from "agent arrives"
to "agent holds a credential" with no human in it. Key generation behind a login
the user can complete once, plus a documented `Authorization: Bearer` header, is
a lower-friction and lower-risk answer than a half-built OAuth deployment. Report
the friction honestly — "contact sales" is a wall an agent cannot climb, a signup
form is a speed bump, self-serve keys are open — and let the product decide.

A **sandbox or test mode** belongs in this section rather than in K6, because it
is what makes the first call safe. An agent's first call against production with
a live credential is the risk this removes.

## K6. Runtime behaviour an agent depends on

| Behaviour | Check | Why an agent needs it |
|---|---|---|
| Rate-limit headers | `RateLimit-Limit` / `RateLimit-Remaining` / `RateLimit-Reset` on 2xx, `Retry-After` on 429 | Self-throttling in real time. Without them the agent discovers the limit by hitting it |
| Honest 404s | a real `404` status, not `200` with the app shell | A SPA that answers `200` for every path teaches the agent that every path exists. A short Markdown body naming the sitemap and the docs index turns a dead end into a recovery |
| Stable error shapes | one JSON error envelope across the API | Branching on a shape that changes per endpoint is why agents retry blindly |
| `Link:` response headers (RFC 8288) | `rel="sitemap"`, `rel="alternate"` for Markdown, `rel="service-desc"` for the OpenAPI document | Discovery without parsing HTML, and the only discovery channel a `HEAD` request has |
| In-page tools (WebMCP) | `toolname` / `tooldescription` attributes on action forms; `document.modelContext.registerTool()` | A browser-resident agent can act on the page instead of reverse-engineering the DOM. W3C draft; `navigator.modelContext` is the deprecated pre-Chrome-150 alias |
| Natural-language endpoint (NLWeb) | `POST /ask` returning JSON with `_meta.response_type` and `_meta.version`; SSE streaming on `prefer.streaming: true` | Microsoft's protocol for asking a site a question in words. `HYPOTHESIS` tier — thin adoption |

The first two are worth doing on any site with an API. The last two are
Experiments-bucket by default: both are drafts, and neither has published
evidence of traffic.

## K7. Third-party agent-readiness graders, and how to read one

Scanners that score a domain out of 100 on "agent readiness" have appeared
alongside these specs. They are useful as a **check-list generator** and
dangerous as a **target**, for four reasons this skill has verified on a live
site:

1. **They score presence, not effect.** A perfect score means the files exist. It
   does not mean one agent used them. Non-negotiable #2 applies: the grade is not
   evidence for a plan, it is a list of things to verify.
2. **They sample narrowly.** A "no extended schema types found" verdict routinely
   means *the homepage* has none, while product templates carry `Product`,
   `Offer`, `FAQPage` and `HowTo`. Reproduce every finding against the URL the
   grader probed before accepting it — `scripts/agent_surface.py` prints the URL
   and status for each check so a false finding is visible.
3. **Some findings are unactionable inside the repository.** A Wikipedia article
   needs third-party notability; an npm SDK, a CLI and a public `AGENTS.md` need a
   public repository the company may deliberately not have; a ChatGPT app listing
   needs a submission and a review. Those belong in a business-decision section
   of the plan, not in an engineering ticket that will sit open forever.
4. **A grader's advice can contradict measured evidence.** Where it does — most
   often on `llms.txt` and Markdown mirrors — `references/myths.md` wins, and the
   plan says why. Buying a number is on the myth list for this reason.

The productive reading: take the grader's **absence findings** as a to-do list to
verify, its **score** as noise, and its **prescriptions** as claims to check
against the myth guard.

## K8. The check table, with tiers

Presence checks are `CONFIRMED` when reproduced with a request; the *effect*
column is the honest tier of "shipping this changes an outcome".

| # | Check | Presence | Effect tier | Effort |
|---|---|---|---|---|
| K-01 | Real `404` status for unknown paths | one request | `CONFIRMED` — an agent that believes every path exists is broken by it | 1 |
| K-02 | `operationId` + description on every operation | parse the spec | `CONFIRMED` — function generation fails without it | 1 |
| K-02a | Every conventional entry point linked from the **server-rendered** root | read the root HTML | `CONFIRMED` — a link added at hydration is absent for every non-browser consumer | 1 |
| K-02b | No entry point that answers 200 only by redirecting to the root | compare final vs requested URL | `CONFIRMED` — the page does not exist | 1 |
| K-02c | Trust anchors present, and their server-rendered text measured with comments stripped | one request each | `STUDY` for presence · `HYPOTHESIS` for the 500-char convention | 2 |
| K-03 | Rate-limit headers + `Retry-After` | one request | `STUDY` — documented client behaviour across API vendors | 2 |
| K-04 | `WWW-Authenticate` with `resource_metadata` on `401` | one request | `STUDY` — the discovery chain is specified | 1 |
| K-05 | RFC 9728 protected-resource metadata | one request | `STUDY` | 1 |
| K-06 | `/auth.md` walkthrough | one request | `HYPOTHESIS` | 1 |
| K-07 | `Link:` headers (sitemap, service-desc, markdown alternate) | one request | `HYPOTHESIS` | 1 |
| K-08 | Markdown twin of the canonical facts + `Vary: Accept` | one request | `HYPOTHESIS`, and `myths.md` caps it | 2 |
| K-09 | `llms.txt` with a "when to use this" section | one request | `HYPOTHESIS` — `myths.md` row 1 | 1 |
| K-10 | `.well-known` discovery set (api-catalog, ai-catalog, agent-card, mcp, agent-skills) | one request each | `HYPOTHESIS` — drafts, thin adoption | 1–2 |
| K-11 | Async (`202` + status location) and batch endpoints | parse the spec | `STUDY` for APIs an agent uses at volume | 3–5 |
| K-12 | Sandbox / test mode | docs + one request | `STUDY` | 3–5 |
| K-13 | MCP server over Streamable HTTP | connect | `FIELD` — real adoption, no published effect data for a site this size | 5 |
| K-14 | OAuth 2.0 authorization server | connect | `HYPOTHESIS` at most sites; a self-serve key is the cheaper answer (K5) | 5 |
| K-15 | Published SDK / CLI packages | registry lookup | `HYPOTHESIS`, and it is a maintenance commitment, not a file | 4 |
| K-16 | WebMCP in-page tools | scan the bundle | `HYPOTHESIS` — W3C draft | 3 |
| K-17 | NLWeb `/ask` + SSE | one request | `HYPOTHESIS` — thin adoption | 3 |

## K9. What to put in the plan

Three buckets, in this order, and the order is the argument:

1. **Gains — specified, cheap, and true regardless of agent traffic.** K-01 to
   K-05 (including K-02a/b/c) and K-07. These are correctness fixes wearing an agent-readiness label: a
   `200` for a missing page is a bug for search engines too, an operation with no
   `operationId` is a defect in your own documentation, and a `401` that says
   nothing is a support ticket waiting to happen. Ship them without waiting for a
   demand measurement.
2. **Experiments — cheap but unproven.** K-06, K-08, K-09, K-10. Each is one
   static file. Ship them together, then read the access log for those exact paths
   in 90 days. That log line is the evidence the next audit needs, and it is the
   only way the tier ever moves off `HYPOTHESIS`.
3. **Business decisions, not tickets.** K-13 to K-15, plus anything requiring a
   public repository, a package registry, a directory submission or third-party
   notability. Write them as a decision with a cost and a trigger — "build the MCP
   server when the agent-traffic log passes N requests/month" — not as work
   somebody is expected to start.

Never let this track outrank a track-A blocker. A site that is not indexable does
not need an agent card.
