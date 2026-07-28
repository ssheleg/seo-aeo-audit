# Contributing

Thanks for taking the time. This skill is mostly **knowledge** — nineteen
reference contracts plus a small standard-library auditor. That shapes what a
good contribution looks like here.

## The one rule that matters

**Evidence or silence.** Every claim in this repo carries an evidence tier, and
the tier is a promise about what backs the claim:

| Tier | What it means |
|---|---|
| `CONFIRMED` | Documented by the search engine itself, or reproducible on demand |
| `STUDY` | A published study with a stated method and sample |
| `FIELD` | Repeated practitioner reports, named |
| `HYPOTHESIS` | Plausible, untested — routed to experiments, never to the plan |

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

No dependencies. Python 3.9+ is all you need.

```bash
git clone https://github.com/ssheleg/seo-aeo-audit && cd seo-aeo-audit
```

## Before you open a PR

Both must pass:

```bash
python3 test/validate.py
```

```bash
python3 test/test_page_audit.py
```

`validate.py` checks structure, the four-way version sync, that all nineteen
references exist and every relative link resolves, that the templates embedded in
`deliverable-templates.md` match the root copies, and that the auditor is
standard-library only. `test_page_audit.py` runs the auditor against offline
fixtures — including the URL-scheme guard, which exists because `urlopen` will
happily read `file:///etc/passwd` if you let it.

CI runs the same two plus negative self-tests that prove the validator can fail.

## Where things go

| Change | File |
|---|---|
| A check inside an audit track | that track's reference (`technical-checks.md`, `aeo-geo.md`, …) |
| A number, benchmark or dated figure | `benchmarks.md` — everything else links to it |
| A tactic worth trying | `growth-plays.md`, with a tier and an effort estimate |
| A tactic with counter-evidence | `myths.md`, with the counter-evidence |
| A Google update | `algorithm-updates.md`, with start and completion dates |
| Auditor behavior | `scripts/page_audit.py` **and** a fixture-backed test |

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
