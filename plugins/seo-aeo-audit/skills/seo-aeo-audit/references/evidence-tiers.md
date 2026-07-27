# Evidence tiers

Every finding and every recommendation carries a tier. The tier changes what you
are allowed to do with it.

| Tier | Definition | Allowed action | Confidence weight |
|---|---|---|---|
| **CONFIRMED** | Documented by the engine, or reproduced on this site with an observation you can point at (GSC output, log line, HTTP response, rendered DOM) | Ship it. Blockers of this tier come first. | 1.0 |
| **STUDY** | Published multi-site data with a stated method and sample size | Ship it where the site matches the study population; state the source and sample in the report | 0.7 |
| **FIELD** | A single practitioner case, one site, no control | Pilot on one template or a page cohort; measure before rollout | 0.4 |
| **HYPOTHESIS** | Mechanism plausible, evidence absent or contradictory | Experiment only, with a control group; never sitewide, never sold as a fix | 0.2 |

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
4. **Engine statements are evidence about intent, not always about behaviour.**
   Public guidance from a search company is a party with an interest; where a
   patent, a leak, or your own logs disagree, record both and mark the gap.
   Bing publishes more mechanical detail than Google does; use it, verify it.
5. **Leaks and patents describe architecture, not confirmed live weights.** They
   earn STUDY at best, and only when the described mechanism matches something
   you can observe.
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
