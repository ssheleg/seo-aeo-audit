---
description: Audit a site for search + answer-engine visibility and produce a prioritized change plan
argument-hint: '[site URL or scope, e.g. "example.com" | "traffic dropped in May" | "/blog only"]'
---

Invoke the `seo-aeo-audit` skill for: $ARGUMENTS

Follow the skill exactly.

1. Detect mode first (new audit vs re-audit vs single-question diagnosis), report
   available inputs, missing inputs and scope in three lines, then start. Run
   `"$SKILL_DIR/scripts/preflight.py"` — resolve `SKILL_DIR` first, as SKILL.md
   shows, because a path relative to the project you are standing in will not find
   it — to test the access rather than assuming it — and remember
   it cannot probe Bing, Yandex, analytics, logs, a crawl export or any MCP tool, so
   make the one call each of those is there for by hand.
2. Establish the baseline with dates before forming any opinion.
3. Run the in-scope tracks (A access · B canonicalization · C architecture ·
   D intent · E content value · F extractability/AEO · G entity consensus ·
   H experience · I risk · J measurement), blockers first.
4. Triage with `priority = (impact × confidence) / effort`, where confidence is the
   evidence tier (CONFIRMED 1.0 · STUDY 0.7 · FIELD 0.4 · HYPOTHESIS 0.2), and group
   into Blockers / Leaks / Gains / Experiments.
5. Write `docs/seo/audit-<date>.md` and `docs/seo/plan-<date>.md`, plus
   `docs/seo/experiments.md` if the plan has an Experiments bucket. **Never overwrite
   an existing audit or plan silently** — write a new dated file, or ask first.
6. Finish with exactly one recommended next action.

## The eight non-negotiables apply in full

The skill's `SKILL.md` carries them and is the single home. They are named here
because a command that restates two of them reads as a complete list, and this one
did:

1. **Evidence or silence** — observation, location, value, date, or the finding does
   not go in.
2. **Label the evidence tier** of every recommendation, and never let a HYPOTHESIS
   outrank a CONFIRMED blocker. State the evidence *rung* too: it caps the tier.
3. **Diagnose before prescribing.** "Add schema" is not a diagnosis.
4. **Refuse the myth list.** Nothing from `references/myths.md` goes in the plan.
5. **Never recommend deceptive tactics.** The adversarial material exists only to
   detect and defend against.
6. **State what you could not check.** A missing login is a gap in the report.
7. **Never blend measured with assumed.** A `source` column separates them, and an
   unmeasured volume cell stays blank, never zero.
8. **Know each instrument's blind spot and say it in the output** — including this
   skill's own: a static fetch cannot see JS-injected JSON-LD, a truncated response
   is not a page, and a tool that returned nothing supports no finding at any tier.
