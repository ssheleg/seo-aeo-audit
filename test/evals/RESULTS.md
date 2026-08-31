# Evaluation results

**Status: executed 2026-08-31 against two models. The dated rows below are the
first behavioral run; before them this file said "authored, never executed".**

CI still proves only that the eval files are shaped correctly and that the
validator catches a planted invalid trigger class — schema validity is not
model quality, and nothing here is run by CI.

| Date | Version | Model | Trigger pass rate (train / validation) | Scenario lines passed | Installed alongside | Notes |
|---|---|---|---|---|---|---|
| 2026-08-31 | 0.25.8 (tree at release) | claude-haiku | 5/6 / 5/6 (positives 6/6, negatives 4/6) | s01 4/4 (one with caveat) · s02 4/4 · s03 3/4 | the ssheleg family, 28 skills (see Method) | q08 and q12 false-triggered: an implementation request ("исправь canonical tags…") and a definitional question both routed to the skill. s03 L2 failed: the surfaces were split but discovery-vs-cheaper-serving was never articulated |
| 2026-08-31 | 0.25.8 (tree at release) | claude-sonnet | 6/6 / 6/6 (positives 6/6, negatives 6/6) | s01 4/4 · s02 4/4 · s03 4/4 | the ssheleg family, 28 skills (see Method) | the s01 probe was severed from this run by a harness spend-limit pause, completed anyway, and its result arrived by relay — scored from that delivered result, not from a transcript this run read itself (preflight 3/8 sources with GSC 403 and PSI 429 named in the opening; indexation marked UNKNOWN after two Bing timeouts — "tool failure is not a clean result"; zero-schema confirmed against raw HTML before being reported; a next action, no score). s03 verbatim hit: a Markdown twin "can help an agent that has already arrived read you cheaply — a serving decision measured in tokens, not a citation lever" |

## Method — how this run was executed, and its limits

- **Trigger cases**: one FRESH general-purpose subagent per query per model
  (Claude Code Agent tool, `model` parameter). Each probe's whole task: the
  query verbatim, the instruction to read a file listing the 28 installed
  family skills (name + full frontmatter description, built from the family
  repositories' SKILL.md files), and "which ONE skill would you invoke, or
  none? answer with the name only". Hit for a positive = the answer names
  seo-aeo-audit; hit for a negative = it does not.
- **Scenarios**: one fresh subagent per scenario per model, told the skill was
  invoked, pointed at the real SKILL.md and references, allowed `curl` and the
  bundled scripts, and handed the scenario query verbatim. Each
  `expected_behavior` line scored from the final response.
- **Installed alongside** (the 28): agent-evals, agent-harness, agent-interop,
  agent-orchestrator, agent-sync, make-skill, seo-aeo-audit, sheleg-design,
  ad-tracking, crypto-payments, error-tracking, frontend-performance,
  google-auth, google-signin, stripe-billing, brand-voice, copywriting,
  ux-audit, ux-flows, ux-foundation, ux-scenarios, vision, evidence-docs,
  project-audit, task-pipeline, telegram-bots, telegram-miniapps,
  telegram-userbots.
- **Limits, stated rather than hidden**: (1) probes ran as subagents on the
  operator's machine, so the operator's global routing instructions were
  present in context — the same condition every real session on this machine
  runs under, but not a clean-room measurement; (2) each query was asked once
  per model, not the three times the README asks for — treat single-ask rates
  as coarse; (3) the probe answers with a name instead of actually loading a
  skill, so this measures routing choice, not the load mechanism; (4) one
  scenario probe (s01 sonnet) was severed by a harness pause and scored from
  its relayed result rather than a transcript this run read, and one scenario
  probe wrote into a real repository as a side effect — future runs should pin
  scenario probes to a scratch cwd.
  Per-probe verbatim answers and per-line scoring for this run are archived in
  the wave-3 job directory (`seo-eval-run-log.md`).

To repeat the measurement, follow `README.md` in this directory: each query in
a fresh session, three times, with the model, pack version and other installed
skills recorded — coexistence changes routing.
