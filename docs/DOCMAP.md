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
| The gate commands | `scripts/check-docs.sh` | six other homes — CONTRIBUTING, README, the PR template, CI, `CLAUDE.md` and this file — `validate.py` requires every command in the script to appear in all six of them. It read four for a while, and the two documents that EXPLAIN the gate were the two nobody read: both published five of the seven commands under the sentence *"it runs exactly these and nothing else"* |
| A finding's evidence tier | `FINDING_TIERS` in the script that emits it (`page_audit.py`, `agent_surface.py`) | the script's docstring explains the mapping; `validate.py` reads **every** script that declares the table, and both emitter shapes — `add(sev, code, …)` and an inline `"code":` key. Written against `page_audit.py` alone until a second emitter shipped |
| Whether a track-K check is a defect or a bet | `FINDING_TIERS` in `scripts/agent_surface.py`, and the K8 table in `references/agent-readiness.md` | the two must agree: K8 publishes the effect tier a reader plans against, the script multiplies by it. A draft specification's absence may never carry `CONFIRMED` — `test_agent_surface.py` names the five codes it checks |
| The CWV pass bands | `THRESHOLDS` in `scripts/psi_pull.py` | `references/experience-signals.md` publishes them as a table — compared numerically, in either unit |
| A reference's section ids | the reference that defines them | globally unique across `references/` — two files defined `D1`, `D2`, `E1`, `E2` with different content, so the sweep now owns `O1`–`O5` |
| When `algorithm-updates.md` was last refreshed | its `Sources last re-fetched` line | its `Newest row in this file` line is a **second, separate** fact; one used to stand in for both |
| A dated number | `references/benchmarks.md` | Other references quote it **with its date and source**, never restate it |
| Where a reference claim came from | `docs/research/` — one file per source pass | **review**. The code graph rates `2026-07-source-distillation.md` the ninth most connected node in the repository, and until 2026-08-10 nothing but the README's directory listing named it: an agent asking "where did this claim come from" had no pointer, while the answer was a 27-node hub. Cite the pass by filename when a reference's provenance is in question |
| A refuted claim | `references/myths.md` | SKILL.md carries the short list only |
| The evidence-tier vocabulary | `references/evidence-tiers.md` | `CONTRIBUTING.md` quotes the four definitions verbatim; `SKILL.md` carries the confidence weights inline and `cursor/rules/*.mdc` a compressed gloss, because a `.mdc` may not link out. `validate.py` compares all four homes — verbatim where it can, and on the weights plus the word `single` where it cannot |
| Tool → check routing | `references/tooling.md` | SKILL.md names a script; the routing table owns which rung it sits on |
| A script's contract | its own docstring | README and SKILL.md describe usage; neither is the contract |
| Version | `plugins/*/.claude-plugin/plugin.json` | marketplace.json, package.json, CHANGELOG — four-way sync enforced |
| A script's exit-code contract | its own docstring | asserted in `test_output_contracts.py`. Four scripts had settled it four ways, and two of them returned 0 after measuring nothing — the prose was honest, the machine-readable half was not. `gsc_pull.py` had no such path at all until 2026-08-20: three `return 0`s, no `return 1`, and a docstring saying only "0 = ran". Six of the seven now read one predicate for the report and the status; `preflight.py` is the deliberate exception, because there the failures **are** the report |
| How to reach the bundled scripts | the `$SKILL_DIR` block in `SKILL.md` | every invocation in that file uses it, and `validate.py` rejects a bare `scripts/*.py` path. The Cursor rule states the same thing in prose because a `.mdc` may not link out |
| Whether an error is safe to render | `_flat()` — five of the seven scripts define one | these ship as standalone files with no shared module, so the copies are counted rather than imported. The row said "one copy per script, five in all" — two claims in one breath, and the per-script half was false against seven scripts, while `preflight.py`'s shared provenance block said the true number out loud in a comment. `validate.py` counts the definitions now |
| The 2026-08-10 defect total | the `### D<n>` rows of `docs/audit/2026-08-10-defect-ledger.md` | six prose homes, each named with its phrase in `validate.py`. Five said forty-one against forty-three rows — including the ledger's own summary sentence, which said both |
| The audit's track list | the step-2 table in `SKILL.md` | `TRACKS` in `scripts/preflight.py` is the machine-readable second home, because a script cannot read a markdown table at runtime — `validate.py` compares ids, order and label, in both directions. The deliverable's coverage table is generated from `TRACKS`, so it can no longer ship one row short of the tracks the skill declares |
| The coverage-status vocabulary | `COVERAGE_STATUS` in `scripts/preflight.py` | both skeleton homes publish every value verbatim (`templates/audit-report.template.md` and `references/deliverable-templates.md`), and `references/preflight.md` defines each one — all checked. `validate_coverage()` is the only reader, so a value outside the enum is an error rather than an unread cell |
| Which gates a `blocked-by` row may name | `COVERAGE_GATES` in `scripts/preflight.py` | `validate.py` parses every `probe(...)` call with `ast` and refuses a gate the tuple does not declare. The five GSC gates also appear as a table in `references/preflight.md`, which explains what each one sends you to and is not the enum |
| The producer field set | `PRODUCER_FIELDS` in `scripts/preflight.py` | the shared block in all seven scripts declares it identically — `validate.py` compares the seven byte for byte, because these ship standalone and the installed layout has nothing to import from. Both skeleton homes must name every field, and `references/preflight.md` and `scripts.md` explain them |
| What a producer field says when unavailable | `PRODUCER_ENV` in `scripts/preflight.py` | `unavailable: <VAR> is not set by this harness`, generated — never a literal anywhere. `SECURITY.md` lists the three variables as the only environment this skill reads; `test_output_contracts.py` asserts a guessed value is refused |
| What invalidates an audit | `INVALIDATORS` in `scripts/preflight.py` | both skeleton homes and `references/preflight.md` publish the four rows; `validate_provenance()` refuses a block that names fewer. The shape is `task-pipeline`'s verification-ledger invalidators mapped onto this domain, not a second design |
| The skill version, at runtime | `SKILL_VERSION` in each script's shared block | seven literals rather than a lookup, because `bin/seo-aeo-audit.js` installs `scripts/` with no manifest beside it. `validate.py` holds all seven equal to `plugin.json` — a producer block naming a version that never ran is worse than one naming none |
| What a run leaves on disk | `test/residue.py` — every temp tree comes from `residue.workspace()` | no second implementation, deliberately: the module is **copied** from `make-skill` and the umbrella, which closed the same leak first, because two implementations of one ledger is the defect this family keeps finding. `test/residue_test.py` runs the real suites in a private `$TMPDIR` and requires the box to be empty |
| The bundled script inventory | the `scripts/` directory | `SECURITY.md` states the count in five sentences and one row per script; `SKILL.md` names them in its inventory paragraph — all measured against the directory since B-25, which had six/22 against seven/26 for four releases, and a `sitemap_pull.py` that has never existed |
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
| Document an invocation in `SKILL.md` | it resolves through `$SKILL_DIR`, never relative to the caller | `validate.py` script-reachability guard. The agent stands in the user's project; a relative path there is not a smaller feature, it is a silent drop to the bottom evidence rung |
| Render anything an API returned into markdown | `_flat()` around it | `validate.py` error-flattening guard rejects `r['error']`/`r['detail']` reaching a rendered line raw |
| Change what a script returns on total failure | its docstring, and the assertion in `test_output_contracts.py` | the test; the docstring is **review** — no check reads prose for intent, which is exactly how two contracts drifted from their own documentation |
| Add a test file to the gate | `check-docs.sh`, CONTRIBUTING, the README, the PR template, CI, `CLAUDE.md` and this file | `validate.py` gate parity across all six of them, and the count is read out of this row and out of the one above and compared to `_GATE_HOMES` — the row above said three homes, this one said five, and the checker read four. The PR template was the unguarded fifth home and kept asking for two commands long after that was fixed elsewhere |
| Add or rename an audit track | the step-2 table in `SKILL.md`, `TRACKS` in `preflight.py`, and therefore a row in both skeleton homes | `validate.py` coverage-vocabulary guard. This row exists because `SKILL.md` declared track K in v0.19.0 and the coverage table stopped at J for three releases: the track was not merely unanswered, its coverage was unstatable |
| Add a status to the coverage vocabulary | `COVERAGE_STATUS`, the decision about whether it owes a Notes reason (`NO_REASON_NEEDED`), both skeleton homes and the table in `references/preflight.md` | `validate.py` requires every value to be published in both skeletons and asserts the exemption list is a subset of the enum; the reference table is **review** |
| Add a gate name to a probe | `COVERAGE_GATES` | `validate.py` reads the `probe(...)` calls with `ast` — the enum-drift shape this family has already shipped is a contract listing five statuses against a linter matching four, where the fifth read as no status at all |
| Add a field to the producer block | `PRODUCER_FIELDS` and the shared block in **all seven** scripts, plus the field name in both skeleton homes | `validate.py` provenance guard: the seven copies are compared byte for byte and both skeletons must name every field. `references/preflight.md`'s field table is **review** |
| Release a version | also `SKILL_VERSION` in all seven scripts | `validate.py` compares each literal to `plugin.json` and names the files that disagree. Seven extra homes is the price of a version that survives `bin/seo-aeo-audit.js`, which copies `scripts/` alone |
| Add or remove a bundled script | `SECURITY.md`'s five count sentences and its per-script I/O row, and `SKILL.md`'s inventory paragraph | `validate.py` I/O-surface guard measures both against the directory and **runs** the regex `SECURITY.md` publishes, so narrowing the pattern breaks the count it claims |
| Add a way a payload can be produced | a producer block on it, stamped with that script's own name | `validate.py` requires every script to call `provenance("<its own file>", …)`; `test_output_contracts.py` drives all seven through both formats and reads the output |
| Add a validator guard | a planted-defect step in CI, and the family name in the CONTRIBUTING summary | `validate.py` asserts the name survives; CI proves the guard can fail. A guard nobody has watched fail is indistinguishable from one that cannot. A plant over a **document** uses `plantq`, which requires the refusal to name the defect — `plant` alone cannot tell the guard under test from the anchor-liveness guard, which fires on any literal-anchored document plant (B-33) |
| Make a temp directory in a test | `residue.workspace()`, never `tempfile.mkdtemp()` | `test/residue_test.py` runs the four suites that used to leak in a private `$TMPDIR` and requires it empty afterwards; every gate command prints one residue line, `nothing` included, because a clean run that says nothing is how the next leak becomes invisible. A negative self-test runs its copy with a `$TMPDIR` of its own: a planted run is designed to fail, a failing case keeps its tree, and the shared box would read that as a leak |

## What proves it

```bash
bash scripts/check-docs.sh
```

It runs exactly these and nothing else, so the gate cannot drift from the
tests — and `validate.py` requires every command in that script to be named in all six
homes the row above lists, this file included, because the docs had fallen two test
files behind the gate and then this list did it again:

```bash
python3 test/validate.py
python3 test/plant_guard_test.py
python3 test/test_page_audit.py
python3 test/test_url_inspection.py
python3 test/test_collectors.py
python3 test/test_agent_surface.py
python3 test/test_output_contracts.py
python3 test/test_installer.py
python3 test/residue_test.py
```

Read its exit status as its own command, not behind a pipe (standing instruction
#6).
