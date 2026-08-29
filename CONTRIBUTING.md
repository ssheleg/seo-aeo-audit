# Contributing

Thanks for taking the time. This skill is mostly **knowledge** — twenty-five
reference contracts plus a small standard-library auditor. That shapes what a
good contribution looks like here.

## The one rule that matters

**Evidence or silence.** Every claim in this repo carries an evidence tier, and
the tier is a promise about what backs the claim:

These four definitions are quoted verbatim from
`plugins/seo-aeo-audit/skills/seo-aeo-audit/references/evidence-tiers.md`, which
is their single home. The vocabulary has **four** homes in all (that reference,
this file, `SKILL.md`'s inline weights and the Cursor gloss); `test/validate.py`
reconciles every one of them, and fails if the copies drift.

| Tier | What it means |
|---|---|
| `CONFIRMED` | Documented by the engine, or reproduced on this site with an observation you can point at (GSC output, log line, HTTP response, rendered DOM) |
| `STUDY` | Published multi-site data with a stated method and sample size |
| `FIELD` | A single practitioner case, one site, no control |
| `HYPOTHESIS` | Mechanism plausible, evidence absent or contradictory |

A PR that adds a claim without a tier, or with a tier the source does not
support, will be asked to fix that before anything else. Single-case numbers are
not forecasts. If two sources disagree, **both** get named and the claim is
demoted to `HYPOTHESIS` — we do not pick a winner quietly.

Corollaries worth stating:

- **Dates are part of the claim.** Anything about an algorithm, a surface or a
  benchmark carries the date it was true. Undated figures rot invisibly.
- **`benchmarks.md` owns the numbers.** One owner per fact; every other file
  cross-references it by filename. Restating a figure in a second place is how
  the two versions start to disagree.
- **The myth guard is load-bearing.** `myths.md` lists tactics with published
  counter-evidence. Adding one of them back needs stronger evidence than the
  counter-evidence it contradicts — not an anecdote.
- **Nothing manipulative.** Cloaking, review manipulation, click-signal spoofing
  and friends appear only in `threats-and-defense.md`, written as *detect and
  withstand*. Contributions that recommend them are declined.

## Setup

No dependencies. Python 3.9+ runs the skill and almost all of the gate; Node 16+
is needed only by `test/test_installer.py`, because the npm installer under test
is a Node CLI.

```bash
git clone https://github.com/ssheleg/seo-aeo-audit && cd seo-aeo-audit
```

## Before you open a PR

One command runs the gate, and it is the same one CI runs:

```bash
bash scripts/check-docs.sh
```

It runs exactly these, in this order, and nothing else — so the gate cannot
drift from what it claims to enforce:

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

`validate.py` checks structure, the four-way version sync, that all twenty-five
references exist and every relative link resolves, that the templates embedded in
`deliverable-templates.md` match the root copies, and that every bundled script is
standard-library only. It also reconciles the facts this repo keeps duplicating:
the tier vocabulary across its four homes, the myth count in **all four** of its
homes plus the size of the two short lists, the play count, the reference count in
five prose homes, the Prowl tool count,
the CWV thresholds against `psi_pull.py`, the gate commands against this file, the
README, the PR template and CI, per-finding tier coverage in `page_audit.py`,
section-id uniqueness across references, the two freshness facts in
`algorithm-updates.md`, the defect count against the rows the
2026-08-10 ledger actually enumerates, and
table integrity — both a blank line inside a table and a row with more cells than
its header, either of which stops rows rendering as part of the table.

Four guard families are about what the skill does at runtime rather than what the
repository says. **script reachability**: every invocation in `SKILL.md` must
resolve from the caller's working directory, which is the user's project and not
the skill directory — eleven bare `scripts/*.py` paths once failed in the only
environment the skill is ever used in. **error flattening**: no renderer may
interpolate a network error into generated markdown unflattened, because a Google
error page carries newlines and the first one ends the table row.
**coverage vocabulary**: the deliverable's Track coverage table must be present in
both skeleton homes, carry one row per track SKILL.md declares, and use only the
closed enum in `preflight.py:COVERAGE_STATUS` — a blank Status cell reads the same
whether a track came back clean or never ran, which was true of every row in the
shipped skeleton, and track K had no row to be blank in.
**provenance**: every script carries the byte-identical producer block, calls it
under its own name, declares a `SKILL_VERSION` that matches the manifests, and both
report skeletons publish every field in `preflight.py:PRODUCER_FIELDS`, all four
`INVALIDATORS` and the command that seeds the block — through v0.22.0 no script
emitted a version, a timestamp or an input set at all, so a deliverable could not say
when it was produced or by what. Bump `SKILL_VERSION` in all seven scripts in the same commit as
the manifests; the guard names each file that disagrees.
**I/O surface**: `SECURITY.md`'s script count and its "prints **N** lines" claim are
measured, and the regex is read out of that file and run rather than copied — it said
six scripts and 22 lines against seven and 26 for four releases (B-25). The same guard
reads `SKILL.md`'s script inventory, which named a `sitemap_pull.py` that has never
existed, in the one paragraph an agent consults to learn what it can run.

Eight more families are about this repository's own evidence documents — the ones that
say what shipped, what is owed and what proved it. They exist because on 2026-08-20 the
gate was green while eleven documented facts were false.
**gate homes**: every command in `check-docs.sh` is named in all six of its homes, and
the two documents that *explain* the gate — `CLAUDE.md` and `docs/DOCMAP.md` — were the
last two nobody read, each publishing five of the seven commands under the sentence "it
runs exactly these and nothing else"; the home count itself is read out of DOCMAP and
compared to the tuple, because that row said three, the matrix said five and the checker
read four.
**flat copies**: `_flat()` ships as a copy per script and DOCMAP said "one copy per
script, five in all" against seven scripts — the definitions are counted.
**corpus freshness**: the README's freshness stamp equals the one in
`algorithm-updates.md` that owns it, and the corpus line count is measured and rounded
rather than restated; the bullet said "Verified as of 2026-08-10" six days after the
re-fetch, and "Roughly 5,000 lines" against 5,917.
**body budget**: `SKILL.md`'s body is measured here — `len(body) / 3.9`, the estimator
vendored from `make-skill`'s `audit_skill.py --house`, which does not ship in this tree
and which three ledger rows quoted as runnable. Over the 5000-token or 500-line budget
fails; past the 4750 house limit prints a note, because that state is filed as B-27.
**board status**: a `B-nn` the prose calls closed must read `done` on the board, and
every board id cited must exist — `SECURITY.md` credited its own repair to B-17, which
is open and about something else.
**ledger coverage**: the newest release in `CHANGELOG.md` must have a section in
`docs/evidence/verification.md`, and the releases that have none are declared in a
counted list rather than silently absent; two sections said "**Not shipped**" about work
that had shipped in the release tagged on HEAD.
**confirmed tally**: every ledger section's stated tally is parsed out of its own
`Confirmed` column — the v0.13.0 line said twenty-two against twenty-one rows and left
a whole vocabulary value out, and the prose under it reasoned from the wrong number.
**run stamps**: `retro.md`'s newest run stamp cannot be older than `plugin.json`'s
version, and its live instruction count is read from the headings rather than from the
prune log's arithmetic — the stamps stopped eighteen releases back, which is the file
every run is told to read first.

Those names are not decoration: the validator asserts that this paragraph still
mentions each guard family it runs, because a prose summary of a checker is a fact
with two homes and this one had already fallen four checks behind, then four more.
Keep each family name on one line — the check uses fixed-string matching, and a
name wrapped across a line break reads as absent (it caught this very paragraph
being rewritten).

`test_page_audit.py` runs the auditor against offline fixtures — including the
URL-scheme guard, which exists because `urlopen` will happily read
`file:///etc/passwd` if you let it. `test_url_inspection.py` and
`test_collectors.py` do the same for the other four bundled scripts, and
`test_agent_surface.py` for the track-K collector.
`test_output_contracts.py` holds what all seven owe their caller: a run that
measured nothing exits non-zero, and no network error reaches generated markdown
with its newlines intact.

`test_installer.py` runs both installers as processes against throwaway HOMEs.
The case that earns it its place: an installer asked to write
`~/.claude/skills/seo-aeo-audit` while the same skill is installed as a Claude
Code plugin must **refuse with exit 3** and write nothing — a plain copy would
shadow the plugin and serve its frozen version forever — with the remedy naming
the real plugin spec from `installed_plugins.json`, `--force` as the deliberate
override, and a missing or corrupt JSON reading as "no plugin" (fail open,
never crash). It also holds the success path to its last lines: how the next
version arrives, and that a restart is needed before a session sees it.

`test/residue_test.py` is the ledger over what a run leaves on disk. Every temp tree in
this repository comes from `residue.workspace()`, a **failing** case keeps its own tree by
name so a plant can be read where it landed, and every gate command ends by printing one
line naming its residue — `nothing` included, because a clean run that stays silent is how
the next leak becomes invisible. It runs last, so its final case reads the `$TMPDIR` every
earlier suite shared.

CI runs the same set plus negative self-tests that prove each guard can fail.
**Add a guard and you add its negative self-test**: a guard nobody has watched
fail against a planted defect is indistinguishable from a guard that cannot. A plant
over a **document** uses `plantq`, which requires the refusal to name the defect: the
anchor-liveness guard fires on any literal-anchored document plant, so "the validator
failed" alone cannot tell the intended guard from that one (B-33).


### The family catalogue moves with the release

`sshlg-skills` — the launcher that installs and updates the whole ssheleg family — pins every
member's version in its own `skills.json`. **A release that does not bump that pin is invisible.**
`npx sshlg-skills list` keeps reporting the previous version, `update` keeps installing it, and
anyone comparing their install against `list` is told the wrong number with nothing to reveal it.

So a release is not finished at `npm publish`:

```bash
# in ssheleg/sshlg-skills
#   1. bump this member's "version" in skills.json
#   2. bump the launcher's own version, changelog, tag
npm publish --access public
npx --yes sshlg-skills@latest list   # the new number must appear here
```

## Where things go

| Change | File |
|---|---|
| A check inside an audit track | that track's reference (`technical-checks.md`, `aeo-geo.md`, …) |
| A number, benchmark or dated figure | `benchmarks.md` — everything else links to it |
| A tactic worth trying | `growth-plays.md`, with a tier and an effort estimate |
| A tactic with counter-evidence | `myths.md`, with the counter-evidence |
| A Google update | `algorithm-updates.md`, with start and completion dates |
| Auditor behavior | the script in `skills/*/scripts/` **and** a fixture-backed test (`test_page_audit.py` for the page auditor, `test_url_inspection.py` for the index checker, `test_collectors.py` for psi / sitemap / gsc / preflight, `test_agent_surface.py` for the agent surface) |

Adding a reference file means wiring it into `SKILL.md` and into
`REQUIRED_REFERENCES` in the validator. A reference nothing links to is never
loaded — progressive disclosure means the agent reads only what `SKILL.md` points
at.

## Style

- US spelling. A mixed standard has already cost one broken anchor here.
- Plain sentences over hedged ones. Say what is known and what is not.
- Cross-reference by filename, never by an invented anchor.
- Conventional commits (`feat:`, `fix:`, `docs:`), one concern per PR.
- Behavior changes update `README.md` and `CHANGELOG.md` in the same PR.

## Reporting problems

Bugs and ideas: [open an issue](https://github.com/ssheleg/seo-aeo-audit/issues).
For a wrong or outdated claim, please include what the correct claim is and what
backs it — that turns a report into a merge.

Security issues: see [SECURITY.md](SECURITY.md); please do not open a public
issue for those.

## License

By contributing you agree that your contributions are licensed under the
[MIT License](LICENSE).
