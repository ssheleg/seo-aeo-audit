---
description: Audit a site for search + answer-engine visibility and produce a prioritized change plan
argument-hint: [site URL or scope, e.g. "example.com" | "traffic dropped in May" | "/blog only"]
---

Invoke the `seo-aeo-audit` skill for: $ARGUMENTS

Follow the skill exactly:

1. Detect mode first (new audit vs re-audit vs single-question diagnosis), report
   available inputs, missing inputs and scope in three lines, then start.
2. Establish the baseline with dates before forming any opinion.
3. Run the in-scope tracks (A access · B canonicalization · C architecture ·
   D intent · E content value · F extractability/AEO · G entity consensus ·
   H experience · I risk · J measurement), blockers first.
4. Triage with `priority = (impact × confidence) / effort` and group into
   Blockers / Leaks / Gains / Experiments.
5. Write `docs/seo/audit-<date>.md` and `docs/seo/plan-<date>.md`.
6. Finish with exactly one recommended next action.

Evidence discipline is non-negotiable: every finding carries the observation, its
location, the value and the date, plus an evidence tier. Nothing from the myth
list goes into the plan.
