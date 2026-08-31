# Skill Card — seo-aeo-audit

## Identity

| Field | Value |
|---|---|
| Pack and skill | `seo-aeo-audit` |
| Version | `0.25.9` |
| License | MIT |
| Source | https://github.com/ssheleg/seo-aeo-audit |

## Job and boundary

Audit a public website for search and answer-engine visibility, prove findings
with observed evidence and produce a prioritized plan. The skill does not write
the content, implement fixes, buy links or mutate a live search property.

## Inputs and outputs

Inputs may include a live site, repository, crawl export, analytics, logs and
connected search tools. Missing access is reported. Outputs are dated audit,
plan and experiment documents; a link-building brief is optional.

## Runtime and trust

Access is read-only by default. Requesting indexing, disavowing links, submitting
forms or changing a live property requires explicit approval in the current
session. Bundled Python scripts use only the access the operator provides and
state their blind spots.

## Distribution

Install from npm/GitHub, through the Agent Skills CLI, or as the
`seo-aeo-audit` Claude Code plugin.

## Verification

- Repository validator: `python3 test/validate.py`
- Script fixtures and negative checks: repository test suite
- House audit: pinned `make-skill` auditor in `validate.yml`
- Behavioral data: `test/evals/`
- Evaluation status: schema-validated, with no recorded model run

## Known limits

A public-only audit cannot observe private indexation, conversion or server-log
facts. Recommendations inherit the evidence ceiling of the strongest available
instrument; unknown volume remains blank rather than becoming zero.
