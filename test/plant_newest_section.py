#!/usr/bin/env python3
"""Plant: rename the verification ledger's section for the NEWEST release.

Version-agnostic on purpose, and the reason is a plant that stopped landing. The step
that proves *"the newest release with no ledger section is refused"* used to substitute
the literal `## v0.23.0 — the coverage vocabulary`. The moment v0.24.0 became the newest
release, removing v0.23.0's heading no longer triggered that guard at all: the validator
still failed — for the declared-list and count guards — and the plant read as a guard that
had been watched. CI caught it after the tag was public, which is the shape the family's
`plant_guard` exists to make impossible.

So the version is discovered from `CHANGELOG.md` at plant time, which is the same fact the
guard itself reads.

Usage:  python3 test/plant_newest_section.py
Exit:   0 = the heading was renamed
        1 = the plant did not land, and says why
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def main() -> int:
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    m = re.search(r"^## v?([0-9]+\.[0-9]+\.[0-9]+)", changelog, re.M)
    if not m:
        print("PLANT DID NOT LAND: CHANGELOG.md has no `## vX.Y.Z` heading")
        return 1
    ver = m.group(1)

    path = ROOT / "docs" / "evidence" / "verification.md"
    text = path.read_text(encoding="utf-8")
    pat = re.compile(r"^## v?" + re.escape(ver) + r"\b", re.M)
    if not pat.search(text):
        print(f"PLANT DID NOT LAND: no ledger section for the newest release v{ver}")
        return 1
    path.write_text(pat.sub("## Unreleased", text, count=1), encoding="utf-8")
    print(f"planted: the ledger section for v{ver} is now headed `## Unreleased`")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
