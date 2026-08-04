# Spec — seo-aeo-audit (2026-07-28)

## Problem

Existing SEO skills are checklists: they list "best practices" without evidence,
mix 2022-era advice with 2026 surfaces, and stop at findings. Meanwhile the
visibility problem has split in two — classic ranking and answer-engine
citation — with mechanics that are measurable but scattered across engine
documentation, published studies, patents, leaks and practitioner reports.

## Job

One job: **audit a real site and hand back a prioritized change plan** covering
search and answer engines, where every finding is backed by an observation on
that site and every recommendation carries an evidence tier.

Out of scope: writing content, building pages, link buying, running campaigns.

## Contracts

### Deliverable files (the target-project contract)

- `docs/seo/audit-<YYYY-MM-DD>.md` — findings. Per finding: Issue · Impact ·
  Evidence · Cause · Fix · Effort · Evidence tier · Priority · Verification.
- `docs/seo/plan-<YYYY-MM-DD>.md` — change plan grouped Blockers / Leaks / Gains
  / Experiments; per change: target, change, why (mechanism + tier), owner,
  effort, verification, horizon, rollback.
- `docs/seo/experiments.md` — optional experiment ledger.

Seeded from `templates/audit-report.template.md` and
`templates/action-plan.template.md`. Never overwrite an existing file silently.

### Audit tracks (fixed identifiers, used by findings and by references)

`A` access & indexation economics · `B` canonicalization & duplication ·
`C` architecture & link equity · `D` intent & SERP fit · `E` content value ·
`F` extractability & AEO/GEO · `G` entity & brand consensus · `H` experience
signals · `I` risk & threats · `J` measurement.

### Evidence tiers (fixed vocabulary, confidence weights)

`CONFIRMED` 1.0 · `STUDY` 0.7 · `FIELD` 0.4 · `HYPOTHESIS` 0.2.
Triage: `priority = (impact × confidence) / effort`, impact and effort 1–5.

### Script contract

`scripts/page_audit.py`, stdlib only, python ≥3.9 (`from __future__ import
annotations`), offline-capable via `--file`, output `markdown` (default) or
`json`. JSON shape per URL: flat metric keys plus
`read_budget: {window_chars, chars_used, content_pct, link_marker_pct,
links_before_first_text, exhausted}` and
`findings: [{severity, code, message, reference}]` with severity in
`blocker|high|medium|info`. Codes are stable identifiers (`noindex`,
`refresh-noindex`, `canonical-attrs`, `canonical-multiple`, `canonical-missing`,
`canonical-cross`, `nosnippet`, `h1-missing`, `h1-multiple`, `subheads-thin`,
`thin`, `title-missing`, `description-missing`, `jsonld-invalid`,
`jsonld-untyped`, `jsonld-incomplete`, `read-budget`, `nav-before-content`,
`link-count`, `alt-missing`, `price-not-in-text`).

Amended 2026-08-04. Every bundled script is stdlib-only, python ≥3.9, and
`validate.py` **discovers** them rather than listing them, so the contract binds
new scripts automatically.

Each one carries an obligation the others do not: it must state, in its own
output, what it cannot see. That is non-negotiable #8, and it is what these four
have in common rather than any shared schema.

| Script | Emits | Its declared blind spot |
|---|---|---|
| `page_audit.py` | per-URL metrics, `read_budget`, `findings[]`, `jsonld_missing_required[]`, `jsonld_caveat` | server-rendered HTML only — JS-injected JSON-LD is invisible, so an empty inventory is not evidence of absent markup |
| `url_inspection.py` | per-URL index verdict (`google_canonical`, `user_canonical`, `coverage_state`, `robots_txt_state`, `page_fetch_state`), `findings[]` | quota-capped at 2000/day and 600/min per property, so it samples; an un-inspected URL yields **no** findings |
| `sitemap_audit.py` | `templates[]` (path-pattern families), `depth_distribution`, `duplicate_paths`, `findings[]` | no link graph exists in a sitemap, so orphans and click depth are **not derivable** and are refused outright |
| `psi_pull.py` | `field_data` (CrUX p75 per metric with band), `origin_field_data`, `lab_performance_score`, `findings[]` | CrUX is absent for low-traffic URLs — reported as absent, never as zero, and the lab score never substitutes |
| `gsc_pull.py` | `monthly`, `cliff`, `position_split`, `ctr_curve`, `ctr_gaps`, `cannibalization`, `branded_split` | the CTR expectation is built from this property's own rows; a band with <5 rows yields no baseline, and the branded split is unavailable without `--brand-terms` rather than guessed |

Finding severities stay `blocker|high|medium|info` across every script, and every
`reference` value must resolve to a real heading anchor — `validate.py` checks
that for all of them.

### Distribution contract

Marketplace repo layout; contracts live **inside** the skill directory
(`skills/seo-aeo-audit/references/*.md`) so the skills CLI ships them to every
agent; four-way version sync (marketplace, plugin.json, package.json, CHANGELOG);
validator + CI with negative self-tests; Cursor rule with contracts inlined (no
relative links).

## Approach decisions

1. **Ten tracks, blockers first** rather than a flat checklist — a manual action
   or a pre-render `noindex` makes every other finding moot, and the ordering
   encodes that.
2. **Evidence tiers over confident prose.** The 2026 corpus contains directly
   contradictory findings (e.g. Markdown serving for AI crawlers). Rather than
   pick a winner, the skill downgrades conflicting claims to HYPOTHESIS and
   routes them to the experiment path.
3. **An explicit myth list.** The largest observed waste in this domain is
   spending on tactics with published negative evidence. The skill refuses them
   by name and offers the working alternative.
4. **Defense-only treatment of adversarial material.** Prompt injection,
   canonical hijacking, takedown abuse and behavioral poisoning are audited for,
   never recommended.
5. **One bundled script, not a tool suite.** The mechanical checks that are cheap
   to automate and easy to get wrong by eye (canonical attribute trap, `content`
   `="none"`, read budget, JS-gated prices) justify a stdlib script; anything
   requiring a full crawler defers to Screaming Frog/Sitebulb/logs.

## Rejected alternatives

- **Extending an existing seo-audit skill**: the shipped ones lack AEO mechanics,
  evidence discipline and a plan contract, and are keyed to 2024-era assumptions
  (FAQ rich results, AMP, schema-as-ranking-lever).
- **Splitting SEO and AEO into two skills**: retrieval eligibility for answer
  engines *is* classic indexation and ranking; splitting would duplicate tracks
  A–C and let each half give partial advice.
- **A scoring/grading product** (a single "SEO score"): scores hide the cause and
  invite optimization of the score. The deliverable is a plan, not a number.

## Definition of done

Validator green, auditor tests green (offline fixtures, both directions), CI
green, installers verified fresh/rerun/force, plugin installable, skills-CLI
discovery lists exactly one skill, and the umbrella repo (`sshlg-skills`) carries
the new submodule and registry entry.
