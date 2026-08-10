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
| The audit doctrine (non-negotiables) | `plugins/seo-aeo-audit/skills/seo-aeo-audit/SKILL.md` | `cursor/rules/*.mdc` **and** `plugins/*/commands/*.md` each carry a full copy for a different consumer — both count-checked by `validate.py`, neither summarized. The command was the unguarded third channel: it restated two and read as the list |
| The myth count | the rows of `references/myths.md` | four prose homes — README twice, SKILL.md, the Cursor rule — plus the size of the two short lists. `validate.py` reads every one; it used to read one, and was green while three were wrong |
| The play count | the rows of `references/growth-plays.md` | README's knowledge table — checked |
| The Prowl provider-tool count | `references/prowl-mcp.md` | `tooling.md` and README quote it — all three compared |
| The gate commands | `scripts/check-docs.sh` | CONTRIBUTING, README and CI — `validate.py` requires every command in the script to appear in all three |
| A finding's evidence tier | `FINDING_TIERS` in `scripts/page_audit.py` | the script's docstring explains the mapping; `validate.py` fails on a finding with no entry |
| The CWV pass bands | `THRESHOLDS` in `scripts/psi_pull.py` | `references/experience-signals.md` publishes them as a table — compared numerically, in either unit |
| A reference's section ids | the reference that defines them | globally unique across `references/` — two files defined `D1`, `D2`, `E1`, `E2` with different content, so the sweep now owns `O1`–`O5` |
| When `algorithm-updates.md` was last refreshed | its `Sources last re-fetched` line | its `Newest row in this file` line is a **second, separate** fact; one used to stand in for both |
| A dated number | `references/benchmarks.md` | Other references quote it **with its date and source**, never restate it |
| A refuted claim | `references/myths.md` | SKILL.md carries the short list only |
| The evidence-tier vocabulary | `references/evidence-tiers.md` | `CONTRIBUTING.md` quotes the four definitions verbatim; `SKILL.md` carries the confidence weights inline and `cursor/rules/*.mdc` a compressed gloss, because a `.mdc` may not link out. `validate.py` compares all four homes — verbatim where it can, and on the weights plus the word `single` where it cannot |
| Tool → check routing | `references/tooling.md` | SKILL.md names a script; the routing table owns which rung it sits on |
| A script's contract | its own docstring | README and SKILL.md describe usage; neither is the contract |
| Version | `plugins/*/.claude-plugin/plugin.json` | marketplace.json, package.json, CHANGELOG — four-way sync enforced |
| Reference count | `test/validate.py:REQUIRED_REFERENCES` | README (three places) and CONTRIBUTING (two) quote it in prose, in words or digits — **checked** since 2026-08-10. It was marked *review* on the grounds that it is "a prose number about a tuple", and went stale again the moment a twenty-second reference shipped |

## Propagation matrix

A change of the type on the left obliges everything on the right, in the same
change. The right-hand column names what enforces it, or the word **review** with
the reason no check can.

| Change | Obliges | Enforced by |
|---|---|---|
| Add or edit a non-negotiable in SKILL.md | the same rule in `cursor/rules/seo-aeo-audit.mdc` | `validate.py` compares the counts between channels |
| Add a bundled script | compile + stdlib checks; a behaviour test; a CI step; README and SKILL.md usage | `validate.py` discovers `scripts/*.py`, so the first two are automatic; the CI step and the prose are **review** — no check can tell a documented script from an undocumented one without parsing prose |
| Add a reference file | `REQUIRED_REFERENCES`, the SKILL.md reference list, the counts in README and CONTRIBUTING | `validate.py` fails on a missing reference **and** on any of the five prose counts disagreeing with the tuple, in words or digits. `v0.12.0` added a reference and left all five stale, which is what promoted this from *review* |
| Add a finding code that points at a reference anchor | the anchor must exist | `validate.py` resolves every `file.md#anchor` in the scripts |
| Add a dated claim to any reference | a row in `benchmarks.md` with source and date | **review** — a checker cannot tell a sourced claim from a confident one |
| Change a deliverable skeleton | `templates/` and `references/deliverable-templates.md` together | `validate.py` fails on drift between the two copies |
| Release a version | four manifests plus the CHANGELOG top entry | `validate.py` four-way sync |
| Change what an instrument can see | its caveat string, and the guard that pins it | `validate.py` doctrine guards; CI negative self-tests |
| Add a guard family to `validate.py` | its name in the CONTRIBUTING summary of what the validator enforces | `validate.py` asserts each family name survives in that paragraph — the summary had fallen four guards behind |
| Add a row to a claim table (myths, plays, detection patterns) | the prose count that names its size, and the table's own integrity | `validate.py` compares the README's myth count against `myths.md`, and rejects a blank line inside any table in the skill — both added after the class drifted twice |
| Edit a tier definition | the quoted copy in `CONTRIBUTING.md`, and a re-read of every claim carrying that tier | `validate.py` compares the two copies string-for-string; the re-read is **review** — no check knows which claims were admitted under the old bar |
| Add a finding to a bundled script | an entry in `FINDING_TIERS`, and a fixture assertion | `validate.py` fails on a finding code with no tier; the behaviour test asserts every fixture finding carries one |
| Change a threshold a script judges against | the reference that publishes it | `validate.py` compares the CWV bands numerically. Every other threshold is **review** — this is the pattern to extend, not the finished set |
| Add a prose count about a table | the check that reads it, in **every** home the count has | `validate.py`. The rule this row exists for: count the homes first. Three separate guards here were written against the one home that had drifted |
| Append a row to `algorithm-updates.md` | the `Newest row in this file` line | `validate.py` compares it to the newest date in the file |
| Number a new section in a reference | a prefix no other reference uses | `validate.py` fails on a section id defined twice |
| Cite a claim that lives in another file | the claim must be findable there | **review** — `validate.py` resolves markdown links, anchors and backticked filenames, so a pointer to a file that exists and does not contain the claim still passes. Two of those shipped |
| Add a validator guard | a planted-defect step in CI, and the family name in the CONTRIBUTING summary | `validate.py` asserts the name survives; CI proves the guard can fail. A guard nobody has watched fail is indistinguishable from one that cannot |

## What proves it

```bash
bash scripts/check-docs.sh
```

It runs exactly these four and nothing else, so the gate cannot drift from the
tests — and `validate.py` now requires every command in that script to be named in
CONTRIBUTING, in the README and in CI, because the docs had fallen two test files
behind the gate:

```bash
python3 test/validate.py
python3 test/test_page_audit.py
python3 test/test_url_inspection.py
python3 test/test_collectors.py
```

Read its exit status as its own command, not behind a pipe (standing instruction
#6).
