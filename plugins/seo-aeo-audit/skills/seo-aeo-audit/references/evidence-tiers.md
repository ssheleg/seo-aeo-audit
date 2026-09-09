# Evidence tiers

Every finding and every recommendation carries a tier. The tier changes what you
are allowed to do with it.

This table is the **single home** of the tier vocabulary, and it has **four**
homes to reconcile — the acceptance walk that added the first reconciler found two
more the same day, which is why the count is written down here:

1. this table (the home);
2. `CONTRIBUTING.md`, which quotes the four definitions verbatim for contributors;
3. `SKILL.md`, which carries the confidence weights inline for the triage formula;
4. `cursor/rules/*.mdc`, which carries a compressed gloss because an `.mdc` may not
   link out.

`test/validate.py` compares 1 against 2 string-for-string, pins the weights in 3,
and checks the one word 1 and 2 drifted on in 4. It diverged once — `FIELD` read as
"a single practitioner case" here and as "repeated practitioner reports" there,
which are different admission bars for the same label.

Every finding a bundled script emits carries a tier as well as a severity;
`scripts/page_audit.py` declares the mapping in `FINDING_TIERS` and the validator
fails if a finding is added without one. Severity is loudness, the tier is backing,
and only the tier enters the triage formula.

| Tier | Definition | Allowed action | Uncertainty rank |
|---|---|---|---|
| **CONFIRMED** | Documented by the engine, or reproduced on this site with an observation you can point at (GSC output, log line, HTTP response, rendered DOM) | Ship it. Blockers of this tier come first. | 1.0 |
| **STUDY** | Published multi-site data with a stated method and sample size | See the rollout policy below — population match AND action risk decide, not the label | 0.7 |
| **FIELD** | A single practitioner case, one site, no control | See the rollout policy below — pilot scope comes from the action's risk | 0.4 |
| **HYPOTHESIS** | Mechanism plausible, evidence absent or contradictory | Experiment only, with a control group; never sitewide, never sold as a fix | 0.2 |

## Five axes, one label — what the tier does NOT say

The tier is an ADMISSION label. A finding's record separates five things the
label used to compress into one word, because observation and transferability
are different claims (SE-04):

- **source** — who says it: the engine, your own observation, a published
  study, a vendor estimate, an anecdote;
- **directness** — observed directly, or modelled/inferred from observations;
- **population** — this page, this template, this site, or a multi-site
  population someone measured;
- **causal support** — effect measured against a control · association only ·
  mechanism plausible;
- **uncertainty** — the rank in the table, and nothing else.

A direct HTTP observation is CONFIRMED for what the response contains without
any console — GSC adds breadth, never permission. And no vendor rank raises a
claim past what its method supports.

## The rollout policy — one home, risk × evidence

What you may DO with a finding is decided by the ACTION's risk crossed with
the finding's causal support — never by the tier alone and never by who sold
the data:

| Action | With causal support (control or engine doc) | Without it |
|---|---|---|
| Reversible, scoped (one template, one tag) | ship, verify | pilot with a measurement |
| Reversible, sitewide | ship, verify | split test first |
| Hard to reverse (URL moves, removals, markup purges) | ship with a rollback plan | experiment only, whatever the tier |

STUDY ships only where the site matches the study population AND the action
row above allows it; `SKILL.md`'s Experiments bucket routes by this same
table.

## Rules

1. **Never let a lower tier outrank a higher-tier blocker.** An interesting
   HYPOTHESIS does not get engineering time while a CONFIRMED indexation blocker
   is open.
2. **Cite the observation, not the authority.** "Vendor X says schema helps" is
   not a tier. "URL Inspection shows the user-declared canonical as `None` on
   template Y, screenshot dated 2026-07-28" is CONFIRMED.
3. **Downgrade on conflict.** When two credible studies disagree (as they do on
   serving Markdown to AI crawlers), the claim drops to HYPOTHESIS and moves to
   the experiment list — you do not pick the flattering one.
4. **Engine statements are evidence about intent, not always about behavior.**
   Public guidance from a search company is a party with an interest; where a
   patent, a leak, or your own logs disagree, record both and mark the gap.
   Bing publishes more mechanical detail than Google does; use it, verify it.
5. **Leaks and patents describe architecture, not confirmed live weights.** They
   earn STUDY at best, and only when the described mechanism matches something
   you can observe.
5a. **STUDY is earned by a method, not by being third-party.** A vendor
   estimate with no published method and sample is a HYPOTHESIS about someone
   else's property, whoever sells it — an unknown vendor number never becomes
   STUDY by arriving in a spreadsheet.
6. **Re-tier on re-audit.** A FIELD play that worked here, measured against a
   control, becomes CONFIRMED **for this site**. Say so explicitly — that is how
   a site-specific playbook accumulates.
7. **Freshness matters.** Search surfaces changed materially between 2024 and
   2026 (FAQ rich results retired, AMP advantage removed, AI surfaces added, AI
   reporting added). Any claim older than about 18 months needs a re-check before
   it enters a plan; date every citation you make.

## What this looks like in the report

```
Finding: category templates emit a canonical with `media="all"`, so Google
         discards it.
Evidence: view-source of /shoes/ and /boots/ (2026-07-28); GSC URL Inspection
         reports user-declared canonical "None" for both.
Tier: CONFIRMED
Impact: 4 — 2,300 category URLs; duplicate grouping observed on 180 of them.
Effort: 1 — one template line.
Verification: URL Inspection shows the declared canonical accepted within a
         crawl cycle; duplicate-group count in the Pages report falls.
```
