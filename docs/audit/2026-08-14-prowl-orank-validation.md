# prowl.chat — the third orank scan, and the eight checks this skill still cannot make

- **Date:** 2026-08-14
- **Site:** `prowl.chat` (FastAPI on DigitalOcean behind Cloudflare). An MCP server
  with a web app in front of it, selling metered tool calls to agents — so the
  product's buyer *is* the reader track K was written for.
- **Trigger:** an ora.ai / "orank" agent-readiness scan graded the domain
  **61/100 (C)** — Discovery 2/17, Access 49/63, Usability 42/58, Payments 0/0 —
  and returned **47 line items**.
- **Why this document exists:** this is the **third** orank scan the skill has
  reproduced ([agent-readiness-gap](2026-08-14-agent-readiness-gap.md) on
  `sms-activate.app`, [privateclawd](2026-08-14-privateclawd-orank-validation.md)
  on `privateclawd.com`). The first two produced track K and v0.19.0. This one is
  the first where **track K did most of the work by itself** — and that is what
  makes its residue interesting. Eight things the scan needed, the skill could not
  do.
- **The client-side output** lives in that project's own repository
  (`docs/audits/2026-08-14-orank-agent-readiness-validation.md`, 22 backlog rows
  T149–T170). Nothing here duplicates it; this file is only about the instrument.

## Contents

- [1. What track K found without being told](#1-what-track-k-found-without-being-told)
- [2. The arithmetic, a third time](#2-the-arithmetic-a-third-time)
- [3. Eight gaps, and where each is filed](#3-eight-gaps-and-where-each-is-filed)
- [4. Three refusals held, one confirmed out of scope](#4-three-refusals-held-one-confirmed-out-of-scope)
- [5. What this scan says about the design](#5-what-this-scan-says-about-the-design)

## 1. What track K found without being told

`agent_surface.py --origin https://prowl.chat --format json` — 14 findings, exit 0.
Against the grader's 47 line items, the skill independently reached **31**: the
whole `.well-known` set, markdown negotiation and the missing `Vary: Accept`, the
bot-UA byte comparison, the absent `Link` header, the robots AI-crawler taxonomy
(six retrieval agents unnamed, no `Content-Signal`, no `schemamap:`), the JSON-LD
inventory including the absent `sameAs`, the 404 shape, and the entry-point sweep.

The entry-point sweep is worth naming, because it produced the scan's most
important finding before the grader's narrative got there:

```
entry point: sign-up  — none of /register, /signup, /sign-up, /join answered 200
entry point: pricing  — none of /pricing, /plans, /plans-and-pricing answered 200
entry point: about    — none of /about, /about-us, /company, /about-company answered 200
```

The grader's report closes with a long narrative about an agent that reconstructed
the sign-up flow from documentation and never confirmed it live. That narrative and
these three lines are the same fact, and `K2b` reached it mechanically. Authentication
on that site is a JavaScript modal on `/`; there is no URL to link, quote or index.

**This is the first scan where the skill's coverage was not the story.** The two
earlier documents exist because 43 of 58 and then a comparable share of 53 checks had
no home. Here the residue is eight, and every one of them is a *class* of check
rather than a missing file.

## 2. The arithmetic, a third time

| Layer | Reported | Sum of the "lost N of M" figures in the same report |
|---|---|---|
| Discovery | 2/17 → 15 lost | **22 lost**, over a 17-point layer |
| Access | 49/63 → 14 lost | **34 lost** |
| Usability | 42/58 → 16 lost | **32 lost** |
| Payments | 0/0 → 0 lost | **2 lost**, over a **zero-point** layer |
| Total | 61/100 | layer maxima sum to **138**, not 100 |

Three for three. A layer worth zero points reports losing two of them, which is the
cleanest single exhibit yet: the item is not scored, is presented as a loss, and
would appear in any diff of "what to fix". `myths.md` row 33 and `agent-readiness.md`
K7 now have a third citation, and the pattern is no longer an anomaly worth
re-establishing per scan — **the arithmetic check belongs in the workflow, not in
each report's prose.**

## 3. Eight gaps, and where each is filed

Every row was needed by this scan and could not be met by the skill as shipped.
Priorities use the board formula — `(impact × confidence) / effort`.

| # | Gap | What it cost this scan | Filed |
|---|---|---|---|
| S1 | **`HEAD`/`GET` method asymmetry.** Every probe in `agent_surface.py` is a `GET` | `GET /.well-known/agent-skills/prowl/SKILL.md` → 200 `text/markdown`; `HEAD` on the same URL → **405**. The script reported the path as present. Crawlers and link-checkers `HEAD` first, so a path we would have called healthy is broken for its intended clients | **B-16**, new |
| S2 | **Cross-surface number agreement.** Nothing compares a number on a third-party manifest against the same number on the site | The MCP registry's current record (`chat.prowl/prowl-mcp` v1.4.0, `isLatest`) advertises "360+ tools"; the product ships **448**, and its own repo says so at the same version. Found by reading, not by an instrument | **B-17**, new |
| S3 | **Package-registry lookups** (npm / PyPI / Homebrew), checking `homepage` and `repository` point back at the domain | Two line items could not be settled without it — and settling them by hand **reversed** one: the grader said "CLI mentioned in `llms.txt`", but `llms.txt` mentions no CLI at all, while `@prowl-ai/cli@0.1.1` is published with `homepage: https://prowl.chat/`. The real gap was larger than the grader's | **B-18** — gap-doc **A4**, second exhibit |
| S4 | **"The product never mentions its own published package."** A consistency check between a registry and `llms.txt`/docs | Follows S3. A shipped, versioned CLI that the agent-facing manual never names is a discoverability defect no presence probe can see, because both halves are individually present | **B-19**, new |
| S5 | **skills.sh listing probe.** Currently routed to K9 bucket 3 as a business decision, with no measurement | `skills.sh/api/search?q=prowl` answered in one request and settled the item: only `prowler-cloud/prowler` skills, nothing from the vendor. A `DECISION` you can measure should be measured first | **B-20**, new |
| S6 | **`plugin.json` schema validation.** Presence is routed to a decision bucket | The manifests **exist** (`plugins/prowl/.claude-plugin/plugin.json` and a `.codex-plugin` twin) and are **non-conformant** — no `$schema`. Both available verdicts, "absent" and "present", would have been wrong | **B-21**, new |
| S7 | **Redirect reporting on every probe**, not just entry points | `/docs/llms.txt` returned **307**. The per-section check credited it as neither present nor absent, so a redirect that claims a resource moved read as noise | **B-22** — gap-doc **A8**, second exhibit |
| S8 | **Multi-template markup sweep by default** | The one-URL caveat is printed, but the ergonomics still push toward the homepage. Here the homepage carries **nine** schema types and `/docs/` and `/use-cases/` carry **three**, none descriptive. Running once on the root would have *flattered* the site — the inverse of the usual false finding, and the same defect | **B-23** — gap-doc **A7**, second exhibit |

Three of the eight are second exhibits for items already on the list. That is the
argument for promoting them rather than for re-recording them: an item that two
independent live audits have now needed is no longer deferred on evidence, only on
effort.

## 4. Three refusals held, one confirmed out of scope

The grader repeated three prescriptions the skill already refuses, and the refusals
survived contact with a third site:

1. **`?mode=agent`** — byte-identical to the homepage here (126,719 b both, `cmp`
   clean), so the finding reproduces and the fix is still declined. No spec exists;
   adopting it ships a surface whose only consumer is the scanner that asked for it.
   §4 **C1** now has its second exhibit and should stay closed.
2. **Bot-UA markdown serving** — `ClaudeBot` and the default UA both receive
   **121,176 bytes**. K3's rule is that this is reported as a fact in both
   directions and never as a win, because content that differs by user agent is the
   mechanical definition of cloaking. Identical bytes is the *correct* answer, and
   the grader scores it as a lost point.
3. **Blocking training-only crawlers** — K2a's position holds: whether to feed
   training corpora is a decision about the client's content, and a scanner awarding
   points for one answer is scoring a preference.

## 5. What this scan says about the design

The first two orank documents asked whether the skill had the checks. This one
answers a different question, because it mostly did: **what kind of check is left
when the file-presence layer is complete?**

All eight gaps in §3 share a shape. None of them is "probe another path". S1 is the
same path with a different method. S2 and S4 compare two surfaces that are each
individually fine. S6 is a file that exists and is wrong. S7 is a response that is
neither presence nor absence. S8 is one probe run against the wrong sample.

> A presence probe answers *is it there*. Everything above answers *does it agree
> with itself* — and a fixed list of paths cannot ask that question, no matter how
> long the list gets.

That is the direction track K grows next, and it is also why the track's own trap
statement still holds. `agent_surface.py` shipped 14 findings against this site
without a single measurement of whether one agent has ever fetched one of these
files. Server logs were unavailable again — the third audit in a row — so every
effect claim stayed `HYPOTHESIS` and **B-11** (`agent_traffic.py`) keeps its place
as the highest-value missing instrument in the skill. Eight new consistency checks
would still be eight checks nobody can rank.
