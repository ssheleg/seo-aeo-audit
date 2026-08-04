# Documentation map

Where settled things live, what each fact's single home is, what a change of type
X obliges, and what proves it. Seeded 2026-08-04 during the audit-findings run,
after two drifts shipped that a matrix would have caught.

## The decision home

`docs/DECISIONS.md` is the register. There is exactly one, and it is not
duplicated into commit messages or the changelog — those reference it.

## Single home per fact

| Fact | Its one home | Everywhere else |
|---|---|---|
| The audit doctrine (non-negotiables) | `plugins/seo-aeo-audit/skills/seo-aeo-audit/SKILL.md` | `cursor/rules/*.mdc` carries a full copy for a different agent — count-checked by `validate.py`, never summarized |
| A dated number | `references/benchmarks.md` | Other references quote it **with its date and source**, never restate it |
| A refuted claim | `references/myths.md` | SKILL.md carries the short list only |
| Tool → check routing | `references/tooling.md` | SKILL.md names a script; the routing table owns which rung it sits on |
| A script's contract | its own docstring | README and SKILL.md describe usage; neither is the contract |
| Version | `plugins/*/.claude-plugin/plugin.json` | marketplace.json, package.json, CHANGELOG — four-way sync enforced |
| Reference count | `test/validate.py:REQUIRED_REFERENCES` | README and CONTRIBUTING quote it in prose — the source of truth is the tuple |

## Propagation matrix

A change of the type on the left obliges everything on the right, in the same
change. The right-hand column names what enforces it, or the word **review** with
the reason no check can.

| Change | Obliges | Enforced by |
|---|---|---|
| Add or edit a non-negotiable in SKILL.md | the same rule in `cursor/rules/seo-aeo-audit.mdc` | `validate.py` compares the counts between channels |
| Add a bundled script | compile + stdlib checks; a behaviour test; a CI step; README and SKILL.md usage | `validate.py` discovers `scripts/*.py`, so the first two are automatic; the CI step and the prose are **review** — no check can tell a documented script from an undocumented one without parsing prose |
| Add a reference file | `REQUIRED_REFERENCES`, the SKILL.md reference list, the counts in README and CONTRIBUTING | `validate.py` fails on a missing reference; the counts are **review** — they are prose numbers about a tuple |
| Add a finding code that points at a reference anchor | the anchor must exist | `validate.py` resolves every `file.md#anchor` in the scripts |
| Add a dated claim to any reference | a row in `benchmarks.md` with source and date | **review** — a checker cannot tell a sourced claim from a confident one |
| Change a deliverable skeleton | `templates/` and `references/deliverable-templates.md` together | `validate.py` fails on drift between the two copies |
| Release a version | four manifests plus the CHANGELOG top entry | `validate.py` four-way sync |
| Change what an instrument can see | its caveat string, and the guard that pins it | `validate.py` doctrine guards; CI negative self-tests |

## What proves it

```bash
python3 test/validate.py && python3 test/test_page_audit.py \
  && python3 test/test_url_inspection.py && python3 test/test_collectors.py
```

`scripts/check-docs.sh` runs exactly that and nothing else, so the gate cannot
drift from the tests.
