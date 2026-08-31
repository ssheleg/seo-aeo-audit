#!/usr/bin/env python3
"""Resolve every `$schema` this repository declares, and validate against what it serves.

    python3 test/check_schemas.py

Deliberately NOT part of `scripts/check-docs.sh`. That gate is stdlib-only and
offline by design, so its `$schema` guard can only PIN addresses — it asserts that
each manifest names the one schema right for its document type, at the document
root, and refuses the dead `claude-code-plugin.json` by name. Pinning is not proof:
an address that resolved when it was pinned can stop resolving, and a document that
validated can drift out of the schema it declares. This is the half that looks.

Both halves read `SCHEMA_FOR` from this module, so the address map has one home.
Two checks with two copies of a URL is how the copies disagree.

The import direction is the reverse of the sibling that first shipped this pair
(`telegram-dev`, where `check_schemas.py` imports the map out of `validate.py`).
There, `validate.py` collects `@check`-decorated functions and runs them from
`main()`, so importing it is free. Here it is a flat script that runs every guard
at import and calls `sys.exit(1)` on failure — importing it to borrow one constant
would run the whole validator and could kill this process before it looks at
anything. So the map lives in the module that is safe to import, and `validate.py`
imports it. One home either way; only the arrow moved.

Exits 1 on the first thing it can prove wrong, and 2 when it cannot look at all —
a check that could not run must never read as one that ran and passed.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAME = "seo-aeo-audit"

# The live Claude Code schemas on SchemaStore, one per document type. Both are
# 200 as of 2026-08-31, following a redirect to www.schemastore.org. An allowlist
# rather than a blocklist of the one dead name: the next wrong address will not be
# that one, and exactly two addresses are right here.
SCHEMA_HOST = "https://json.schemastore.org/"
SCHEMA_FOR = {
    ".claude-plugin/marketplace.json": SCHEMA_HOST + "claude-code-marketplace.json",
    f"plugins/{NAME}/.claude-plugin/plugin.json": SCHEMA_HOST + "claude-code-plugin-manifest.json",
}
# Named, because it is the address a plausible guess lands on. SchemaStore answers
# it with 404, and a `$schema` nobody can fetch reads as conformance while nothing
# checks the document — the state a sibling shipped for eleven releases.
DEAD_SCHEMAS = {SCHEMA_HOST + "claude-code-plugin.json": "404"}

TIMEOUT = 30
UA = f"{NAME}-schema-check (+https://github.com/ssheleg/{NAME})"


def fetch(url: str):
    """GET following redirects. Returns (final_url, parsed_json)."""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return resp.geturl(), json.loads(resp.read().decode("utf-8"))


def main() -> int:
    try:
        import jsonschema
    except ImportError:
        print("CANNOT LOOK: jsonschema is not installed — `pip install jsonschema`.")
        print("Refusing to exit 0: a check that did not run is not a check that passed.")
        return 2

    problems: list[str] = []
    for rel, want in SCHEMA_FOR.items():
        path = os.path.join(ROOT, rel)
        if not os.path.isfile(path):
            problems.append(f"{rel} is missing")
            continue
        with open(path, encoding="utf-8") as fh:
            doc = json.load(fh)
        declared = doc.get("$schema")
        if declared != want:
            # The offline guard owns this comparison; repeated here so this script
            # is honest when run alone against a tree that never met that guard.
            problems.append(f"{rel}: declares {declared!r}, pinned map says {want!r}")
            continue

        try:
            final, schema = fetch(declared)
        except urllib.error.HTTPError as exc:
            problems.append(f"{rel}: {declared} -> HTTP {exc.code} "
                            f"(final {exc.url}) — the declared schema does not resolve")
            continue
        except (urllib.error.URLError, OSError, json.JSONDecodeError) as exc:
            print(f"CANNOT LOOK: fetching {declared} failed — {exc}")
            return 2

        title = schema.get("title", "(untitled)")
        print(f"  {rel}")
        print(f"    $schema  {declared}")
        print(f"    resolves 200 -> {final}")
        print(f"    title    {title!r}")

        validator = jsonschema.validators.validator_for(schema)
        try:
            validator.check_schema(schema)
        except jsonschema.exceptions.SchemaError as exc:
            problems.append(f"{rel}: the served schema is itself invalid — {exc.message}")
            continue
        errors = sorted(validator(schema).iter_errors(doc), key=lambda e: list(e.path))
        if errors:
            for err in errors:
                loc = "/".join(str(p) for p in err.path) or "(root)"
                problems.append(f"{rel}: {loc}: {err.message}")
        else:
            print("    validates against it")

    if problems:
        print("\nFAIL: declared schemas")
        for p in problems:
            print(f" - {p}")
        return 1
    print(f"\nOK: {len(SCHEMA_FOR)} declared schema(s) resolve and validate what declares them")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
