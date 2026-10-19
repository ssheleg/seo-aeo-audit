# SEO / AEO build-time brief: {{SITE OR SECTION}}

- **Date:** {{YYYY-MM-DD}}
- **What is being built:** {{new site | new section | landing page | migration target}}
- **Markets / languages:** {{...}}
- **Live today:** {{nothing | the URLs already live, which get an audit instead}}
- **Owners:** {{copy · design · engineering · analytics}}

This brief records decisions, not findings. Nothing here is observed yet; each row
names the audit section that will verify it after launch. A row the project does
not need stays, marked `n/a` with a reason.

## Page-question table

| URL | Primary question | Intent | Page type the SERP rewards | Owner |
|---|---|---|---|---|

## Build-time decisions

| Row | Decision taken | Owner | Verified after launch by |
|---|---|---|---|
| N1 URL plan | | | build-time.md N1 · architecture-and-equity.md, the audit |
| N2 one question per page | | | build-time.md N2 · intent-and-content.md D1, D2 |
| N3 served HTML carries every answer | | | build-time.md N3 · aeo-geo.md F3 |
| N4 schema for visible facts only | | | build-time.md N4 · page_audit.py jsonld-* findings |
| N5 entity home and one spelling | | | build-time.md N5 · entity-and-brand.md G1, G3 |
| N6 crawler policy, two decisions | | | build-time.md N6 · agent-readiness.md K2a |
| N7 llms.txt stance | | | build-time.md N7 · agent-readiness.md K3 |
| N8 explanatory internal links | | | build-time.md N8 · architecture-and-equity.md anchor mix |
| N9 performance budget | | | build-time.md N9 · experience-signals.md H4, psi_pull.py |
| N10 preview controls | | | build-time.md N10 · aeo-geo.md F3 |
| N11 honest dates and lastmod | | | build-time.md N11 · sitemap_audit.py lastmod finding |
| N12 staging behind authentication | | | build-time.md N12 · technical-checks.md A3 |
| N13 measurement at launch | | | build-time.md N13 · measurement.md J1, J3b, preflight.py |
| N14 new-domain expectations | | | build-time.md N14 · technical-checks.md A2 |
| N15 HTML before PDF | | | build-time.md N15 · onpage-checks.md O5 |
| N16 free-tool pages | | | build-time.md N16 · aeo-geo.md F3 |
| N17 regional engines | | | build-time.md N17 · measurement.md J1 |
| N18 per-fact provenance, honest localization | | | build-time.md N18 · technical-checks.md B2 |
| N19 native HTML and CSS first | | | build-time.md N19 · technical-checks.md A1 |

## Do not build

| Idea | Why not |
|---|---|

## Landing readiness (landing pages only)

Run both command sets against the built page, never the draft: super-ux's
readiness check for copy and structure, and this skill's `page_audit.py`,
`agent_surface.py` and `psi_pull.py` for search and machine readability
(build-time.md, Landing readiness).

| Check | Command | Result | Date |
|---|---|---|---|

## Acceptance

The first audit after launch checks every row above through the section it names,
and writes the result into that audit, not into this file.
