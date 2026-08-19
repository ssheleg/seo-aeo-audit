#!/usr/bin/env python3
"""The edit half of a plant, portable — and asserting that it landed.

`plant()` takes its command as an **argv**, so a heredoc cannot be substituted at the
call site: three attempts produced a `\\n`-mangled one-liner or an `IndentationError` in
CI. And `sed -i` is not the answer either — BSD sed needs an argument to `-i`, so all
eleven `sed` plants in this workflow were no-ops on macOS and could only ever be
exercised in CI. That is how a broken plant went unnoticed for two days elsewhere in this
family.

So the edit becomes a command with an argv of its own:

    plant "what this is supposed to break" \\
      python3 test/plant_edit.py sub README.md "61 plays" "60 plays"

Every verb **refuses when its anchor is absent**, by name. `plant_guard.py` already
compares the tree before and after and would catch a plant that did nothing — this says
*which* anchor moved, which is the difference between a five-minute fix and a hunt.
Standing instruction #6 and its corollary, in one file instead of eleven shell quotings.

Anchors are LITERAL, never regular expressions. Half the sed calls this replaces spent
their length escaping `**` and `/`, and an escape that is wrong in one direction silently
matches nothing.
"""
import re
import sys


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def write(path, text):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def sub(path, needle, replacement, count=1):
    # `count` arrives from a shell as a string and `str.replace` refuses one, which
    # this file then reported as "wrong number of arguments" — sending the reader to
    # the argv instead of to the type. Coerced here so a plant that legitimately
    # needs to hit the Nth copy of a duplicated block can say so.
    count = int(count)
    s = read(path)
    if needle not in s:
        raise SystemExit(f"PLANT DID NOT LAND: {path} does not contain {needle!r}")
    out = s.replace(needle, replacement, count)
    if out == s:
        raise SystemExit(f"PLANT DID NOT LAND: replacing {needle!r} in {path} changed nothing")
    write(path, out)


def resub(path, pattern, replacement, count=1):
    """Substitute by REGEX, so a plant does not pin the number it is about.

    Two plants in this workflow named a literal — `**Sixteen** of the twenty-one releases`
    and a run-stamp line — and both stopped landing the moment the fact they measure
    changed, which is on every release. A plant that does not land is a check nobody ran,
    reported green, and the guard that noticed says so out loud: *the plant will not land,
    its check is unproven, and CI refuses AFTER the tag is public.* A regex tracks the
    shape instead of the value, which is what the plant was always about.
    """
    count = int(count)
    s = read(path)
    # MULTILINE, because every file this plants into is a document: an anchored pattern
    # like `…\)\*\*\s*$` is meant to say "end of that LINE", and without the flag it says
    # "end of the file" and lands nowhere. Cost one red release to learn — the plant
    # printed `PLANT DID NOT LAND`, honestly, after the tag was already public.
    out, n = re.subn(pattern, replacement, s, count=count, flags=re.M)
    if not n:
        raise SystemExit(f"PLANT DID NOT LAND: {path} matches no {pattern!r}")
    if out == s:
        raise SystemExit(f"PLANT DID NOT LAND: substituting {pattern!r} in {path} changed nothing")
    write(path, out)


def delline(path, exact):
    """Drop every line equal to `exact` (stripped of its newline)."""
    lines = read(path).split("\n")
    keep = [l for l in lines if l.rstrip("\r") != exact]
    if len(keep) == len(lines):
        raise SystemExit(f"PLANT DID NOT LAND: {path} has no line equal to {exact!r}")
    write(path, "\n".join(keep))


def truncate(path, prefix):
    """Drop the first line starting with `prefix` and everything after it."""
    lines = read(path).split("\n")
    for i, l in enumerate(lines):
        if l.startswith(prefix):
            kept = "\n".join(lines[:i])
            # A truncated text file still ends with a newline. `sed '/x/,$d'` leaves one
            # too, and a plant that also strips it damages the file in a second way the
            # description never claimed — which is how a guard gets blamed for the wrong
            # thing.
            write(path, kept + "\n" if kept else "")
            return
    raise SystemExit(f"PLANT DID NOT LAND: {path} has no line starting {prefix!r}")


VERBS = {"sub": sub,
    "resub": resub, "delline": delline, "truncate": truncate}


def main(argv):
    if not argv or argv[0] not in VERBS:
        print(f"usage: plant_edit.py {{{'|'.join(VERBS)}}} <file> <args...>", file=sys.stderr)
        return 2
    verb, rest = argv[0], argv[1:]
    try:
        VERBS[verb](*rest)
    except TypeError:
        print(f"plant_edit.py {verb}: wrong number of arguments: {rest}", file=sys.stderr)
        return 2
    except FileNotFoundError:
        print(f"PLANT DID NOT LAND: {rest[0] if rest else '?'} does not exist", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
