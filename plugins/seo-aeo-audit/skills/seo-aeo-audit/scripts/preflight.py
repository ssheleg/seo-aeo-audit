#!/usr/bin/env python3
"""preflight — prove which inputs this audit actually has before planning around them.

SKILL.md step 0 says: *test the access, do not assume it. A connected server is
not a working one.* This is that test. It probes each source the audit can lean
on, reports what came back, and — the part that matters — says which of the three
independent gates a failure hit, because their own error messages do not.

It never guesses. A source it could not reach is reported as unreachable, not as
absent data, and the difference decides whether a finding is possible at all.

Read-only. It fetches, lists and reads; it submits nothing.

Usage:
  preflight.py --site sc-domain:example.com --origin https://example.com
  preflight.py --origin https://example.com          # public-only audit
  preflight.py --site sc-domain:example.com --format json
  preflight.py --origin https://example.com --format coverage   # seed the report's
                                                                # coverage table

`--format coverage` prints the `## Track coverage` section of
`docs/seo/audit-<date>.md` already filled in with what the probes found: every
track this run cannot reach reads `blocked-by <gate>`, and every other track reads
`unlooked`. It never writes `observed` — see the coverage block below.

Exit codes: 0 = probes ran (even if some failed — that IS the report),
            1 = usage error.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

UA = "seo-aeo-audit/preflight (+https://github.com/ssheleg/seo-aeo-audit)"
# The Search Console API is TWO surfaces on one host and they are not
# interchangeable. `/webmasters/v3` carries the property list (`sites`) and Search
# Analytics; `/v1` carries only URL Inspection. Probing `/v1/sites` returns a
# Google 404 HTML page, which this script then classified as gate "permission" —
# so a property the account can see was reported unreachable, in the one file
# whose whole job is to say what the audit can observe. Found 2026-08-14 by
# running it against a property the same credentials read fine through
# `gsc_pull.py`, which had the right base all along (D44).
GSC_SITES = "https://searchconsole.googleapis.com/webmasters/v3"
GSC = "https://searchconsole.googleapis.com/v1"
PSI = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"


def _flat(text: str, limit: int = 200) -> str:
    """One line, safe inside a table cell, capped.

    Network errors arrive as HTML error pages and pretty-printed JSON. Interpolated
    raw into a markdown row, the first newline ends the row and every row after it
    stops rendering — so the report becomes unreadable exactly where it is carrying
    the failure. Duplicated in each collector rather than imported: these ship as
    standalone files with no shared module, so `test/validate.py` counts the homes.
    """
    one = " ".join(str(text).split()).replace("|", "\\|")
    return one if len(one) <= limit else one[: limit - 1].rstrip() + "…"


def probe(name: str, ok: bool, detail: str, gate: str | None = None,
          blocks: str = "") -> dict:
    return {"source": name, "reachable": ok, "detail": detail,
            "gate": gate, "blocks": blocks}


def _get(url: str, timeout: int = 20, max_bytes: int = 4096) -> tuple[int, str]:
    """A probe reads only what it needs. `max_bytes` is explicit because a decision
    taken on a prefix of a large JSON body is a coin flip wearing a verdict."""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read(max_bytes).decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read(400).decode("utf-8", "replace")
    except Exception as exc:  # noqa: BLE001 - a failed probe is a result
        return 0, str(exc)[:200]


def has_crux_field_data(payload: dict) -> bool:
    """Does this PageSpeed response actually carry CrUX field data?

    PSI returns the `loadingExperience` block whether or not CrUX has data for the
    URL — with no `metrics` child when it does not. Testing for the *key* (or worse,
    for the string in a truncated body) reports field data that is not there, and
    the negative branch then explains the absence with a cause nobody established
    ("too little traffic"). psi_pull.py has always read `metrics`; this is the same
    rule, so the two instruments cannot disagree about what was measured.
    """
    block = payload.get("loadingExperience")
    if not isinstance(block, dict):
        return False
    metrics = block.get("metrics")
    return isinstance(metrics, dict) and bool(metrics)


def check_python() -> dict:
    v = sys.version_info
    ok = (v.major, v.minor) >= (3, 9)
    return probe("python", ok, f"{v.major}.{v.minor}.{v.micro}",
                 None if ok else "interpreter",
                 "" if ok else "the bundled scripts target python 3.9+")


def check_gcloud() -> tuple[dict, str | None]:
    try:
        out = subprocess.run(
            ["gcloud", "auth", "application-default", "print-access-token"],
            capture_output=True, text=True, check=True, timeout=60)
    except FileNotFoundError:
        return probe("gcloud ADC", False, "gcloud not on PATH", "install",
                     "Search Console: no queries, no URL Inspection"), None
    except subprocess.CalledProcessError as e:
        return probe("gcloud ADC", False, e.stderr.strip()[:160] or "token mint failed",
                     "login", "Search Console: no queries, no URL Inspection"), None
    except subprocess.TimeoutExpired:
        return probe("gcloud ADC", False, "timed out minting a token", "login",
                     "Search Console: no queries, no URL Inspection"), None
    return probe("gcloud ADC", True, "access token minted"), out.stdout.strip()


def _unattempted_property(site: str | None) -> list[dict]:
    """The named-property row for a run that never got far enough to try it.

    Emitted on every failure path so the coverage denominator stays fixed. It used
    to vanish instead: a failed property list produced "N of 7" where a successful
    one says "of 8", and the probe that silently left is the one that decides the
    most — whether this account can see this property at all. A reader cannot tell
    a smaller world from an unasked question, which is non-negotiable #8 applied to
    preflight's own headline.
    """
    if not site:
        return []
    return [probe(f"property {site}", False,
                  "not attempted — the property list call did not succeed, so this "
                  "check never ran", "unattempted",
                  "everything first-party for this site")]


def check_gsc(token: str | None, site: str | None, quota_project: str | None) -> list[dict]:
    if not token:
        return [probe("Search Console", False, "no token to try with", "login",
                      "query data, position history, URL Inspection")] + _unattempted_property(site)
    headers = {"Authorization": f"Bearer {token}"}
    if quota_project:
        headers["x-goog-user-project"] = quota_project
    req = urllib.request.Request(f"{GSC_SITES}/sites", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            entries = json.loads(r.read().decode()).get("siteEntry", [])
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")[:200]
        # The gates fail independently and most of them say "403". `quota-project`
        # is the one that has to be named separately: local Application Default
        # Credentials are refused by this API until a quota project is bound, and
        # the fix is `gcloud auth application-default set-quota-project <id>` or
        # `--quota-project`, not a permission grant on the property. Read as
        # "permission", it sends an auditor to the wrong screen entirely.
        low = body.lower()
        gate = ("quota-project" if "quota project" in low or "serviceusage" in low
                else "scope" if "insufficient" in low or "scope" in low
                else "api-not-enabled" if "disabled" in low or "has not been used" in low
                else "permission")
        return [probe("Search Console", False, f"HTTP {e.code}: {body}", gate,
                      "query data, position history, URL Inspection")] + _unattempted_property(site)
    except Exception as exc:  # noqa: BLE001
        return [probe("Search Console", False, str(exc)[:160], "network",
                      "query data, position history, URL Inspection")] + _unattempted_property(site)

    out = [probe("Search Console", True, f"{len(entries)} property/properties visible")]
    if site:
        match = next((e for e in entries if e.get("siteUrl") == site), None)
        if match:
            out.append(probe(f"property {site}", True,
                             f"permission: {match.get('permissionLevel','?')}"))
        else:
            out.append(probe(f"property {site}", False,
                             "not in this account's list — a property can be "
                             "DNS-verified and still invisible to an account never "
                             "added under Users and permissions", "permission",
                             "everything first-party for this site"))
    return out


def check_public(origin: str) -> list[dict]:
    origin = origin.rstrip("/")
    out = []
    status, body = _get(f"{origin}/robots.txt")
    out.append(probe("robots.txt", status == 200,
                     f"HTTP {status}" + ("" if status == 200 else f" — {body[:80]}"),
                     None if status == 200 else "http",
                     "" if status == 200 else "crawl-directive checks (track A)"))
    sitemaps = []
    if status == 200:
        for line in body.splitlines():
            if line.lower().startswith("sitemap:"):
                sitemaps.append(line.split(":", 1)[1].strip())
    guess = sitemaps[0] if sitemaps else f"{origin}/sitemap.xml"
    s_status, s_body = _get(guess)
    out.append(probe("sitemap", s_status == 200,
                     f"{guess} — HTTP {s_status}"
                     + ("" if s_status == 200 else f" — {s_body[:60]}"),
                     None if s_status == 200 else "http",
                     "" if s_status == 200 else "the published-URL inventory (sitemap_audit.py)"))
    h_status, _ = _get(origin + "/")
    out.append(probe("homepage", h_status == 200, f"HTTP {h_status}",
                     None if h_status == 200 else "http",
                     "" if h_status == 200 else "every page-level check"))
    return out


def check_psi(origin: str | None) -> dict:
    if not origin:
        return probe("PageSpeed Insights", False, "no --origin given", "usage",
                     "field CWV (psi_pull.py)")
    q = urllib.parse.urlencode({"url": origin, "strategy": "mobile"})
    # The whole body, parsed: the field-data question is answered by a nested key,
    # so a byte-capped read can only guess at it.
    status, body = _get(f"{PSI}?{q}&category=PERFORMANCE", timeout=90,
                        max_bytes=8_000_000)
    if status != 200:
        return probe("PageSpeed Insights", False, f"HTTP {status} — {body[:120]}",
                     "rate-limit" if status == 429 else "http",
                     "field CWV (psi_pull.py)")
    try:
        payload = json.loads(body)
    except ValueError:
        return probe("PageSpeed Insights", True,
                     "reachable, but the response did not parse as JSON — cannot say "
                     "whether CrUX field data exists for this URL")
    if has_crux_field_data(payload):
        return probe("PageSpeed Insights", True,
                     "reachable; CrUX field data present for this URL")
    return probe("PageSpeed Insights", True,
                 "reachable; no CrUX field data for this URL — the response carries no "
                 "field metrics, so this page is lab-only. That is absence, not a pass: "
                 "psi_pull.py will report it as absent and offer the origin aggregate")


# ── the report's coverage table ──────────────────────────────────────────────
# Every instrument in this bundle can already tell a clean result from a check
# that never looked. `url_inspection.py` grants CONFIRMED only to the N of M URLs
# the index answered for; `page_audit.py` drops every absence and count finding on
# a truncated read; `gsc_pull.py` ships `row_limit_reached` and
# `rows_dropped_as_noise`; `_unattempted_property` above keeps this script's own
# denominator fixed so an unasked question cannot look like a smaller world.
#
# None of it reached the markdown a client reads. The deliverable's coverage table
# offered a `Status` column with **no defined vocabulary** and a free-text
# "Not checked" table beside it, and nothing read either — so a track that
# silently returned nothing rendered identically to a track that came back clean.
# Two opposite states, one output, in the one document somebody pays for.
#
# Three properties fix that, and all three live here because a fact with two homes
# drifts:
#
# 1. **The vocabulary is closed.** A value outside `COVERAGE_STATUS` is an error,
#    not an unread cell. The family has already shipped the other shape — a
#    contract listing five statuses against a linter matching four, where an
#    out-of-enum value read as *no status at all*.
# 2. **The denominator is the whole declared track list.** SKILL.md step 2
#    declares eleven tracks; the skeleton shipped ten rows, so track K's coverage
#    was not merely unanswered, it was unstatable. `test/validate.py` reconciles
#    `TRACKS` against that table, in both directions.
# 3. **The seed cannot write `observed`.** Preflight runs at step 0, before any
#    track has run, so it fills the floor: `unlooked`, or `blocked-by <gate>`
#    where a source it probed refused. Only somebody who looked can write the one
#    value that reads as clean, which means the failure mode of forgetting is now
#    "nobody looked" instead of "clean".

# The eleven tracks of SKILL.md step 2, in its order. Second home of that list by
# necessity — a script cannot read a markdown table at runtime — so `validate.py`
# compares the two and fails on either a missing or a surplus track.
TRACKS = (
    ("A", "access & indexation"),
    ("B", "canonicalization"),
    ("C", "architecture & equity"),
    ("D", "intent & SERP fit"),
    ("E", "content value"),
    ("F", "extractability / AEO"),
    ("G", "entity & brand"),
    ("H", "experience signals"),
    ("I", "risk & threats"),
    ("J", "measurement"),
    ("K", "agent surface"),
)

# The closed vocabulary, written in the form a reader sees. `blocked-by <gate>`
# carries its gate because "we could not check" and "the account is not on the
# property" send a client to different rooms — that is the same reason this
# script names its gates at all.
COVERAGE_STATUS = (
    "observed",
    "partial",
    "unlooked",
    "blocked-by <gate>",
    "out-of-scope",
)

# Which statuses owe the reader a reason in Notes. `observed` needs none and
# `unlooked` explains itself; everything else is a claim about why. Kept as the
# short exemption list rather than the long obligation list, so a sixth status
# cannot arrive without a decision about its Notes cell.
NO_REASON_NEEDED = ("observed", "unlooked")

# Gates a `blocked-by` row may name. The first block is exactly what this
# script's own probes emit — `validate.py` parses every `probe(...)` call and
# refuses a gate that is not declared here, which is the enum drift this
# vocabulary exists to prevent. The second block is for blockers no probe can
# reach: the client never sent the log export (`logs`), or the audit has no seat
# for a third-party index (`seat`).
COVERAGE_GATES = (
    "install", "interpreter", "login", "quota-project", "scope",
    "api-not-enabled", "permission", "network", "unattempted", "http",
    "usage", "rate-limit",
    "logs", "seat",
)

# One home for the table's shape, read by the seeder, by the checker, and by
# `validate.py` when it looks for the table in the deliverable skeleton.
COVERAGE_HEADER = "| Track | Status | Notes |"

# The sources whose refusal genuinely stops a track, not every source it would
# like. A 404 sitemap costs track A its published-URL inventory and leaves the
# rest of A runnable, so that is a `partial` the auditor writes — not a
# `blocked-by` this script asserts. Matched by prefix, so `Search Console` also
# covers the `property <site>` row. A track with no entry has no probe that can
# speak for it and stays at the floor.
TRACK_SOURCES = {
    "A": ("robots.txt", "homepage"),
    "B": ("homepage",),
    "C": ("homepage",),
    "D": ("Search Console", "property"),
    "E": ("homepage",),
    "F": ("homepage",),
    "G": (),
    "H": ("PageSpeed Insights",),
    "I": ("homepage",),
    "J": ("Search Console", "property"),
    "K": ("robots.txt", "homepage"),
}


def _status_word(spec: str) -> str:
    """The keyword of a vocabulary entry: `blocked-by <gate>` matches on `blocked-by`."""
    return spec.split(" ", 1)[0]


def coverage_seed(rows: list[dict]) -> list[dict]:
    """The floor of the report's coverage table, computed from the probes that ran.

    Never `observed`: see property 3 above. A track whose blocking source was
    refused comes back `blocked-by <gate>` naming the same gate the preflight table
    named, with the probe's `detail` as its reason. Everything else is `unlooked`,
    which is the truth at step 0 and stays the truth for any row nobody edits.

    A track with no `TRACK_SOURCES` entry can never be reported blocked, so
    `test/validate.py` requires an entry for every track — an empty tuple where no
    probe can speak for it, as track G has, rather than a missing key that reads
    the same as a track nothing refused.
    """
    refused = [r for r in rows if not r.get("reachable")]
    out = []
    for tid, label in TRACKS:
        hit = None
        for req in TRACK_SOURCES.get(tid, ()):
            hit = next((r for r in refused if str(r.get("source", "")).startswith(req)), None)
            if hit:
                break
        if hit:
            gate = hit.get("gate") or "network"
            # `detail`, not `blocks`. A probe's `blocks` string is written for the
            # preflight table and names the track it was thought of for — reused
            # here it put "crawl-directive checks (track A)" in track K's row, a
            # sentence about the wrong track in the document a client reads. The
            # detail is a fact about the source, so it is true on every row that
            # rests on it.
            why = hit.get("detail") or hit.get("blocks") or "the probe was refused"
            out.append({"track": tid, "label": label,
                        "status": f"blocked-by {gate}",
                        "notes": _flat(f"{hit['source']} unreachable — {why}", 160)})
        else:
            out.append({"track": tid, "label": label, "status": "unlooked", "notes": ""})
    return out


def render_coverage(seed: list[dict]) -> str:
    """The coverage section, ready to paste into `docs/seo/audit-<date>.md`.

    Carries the vocabulary above the table rather than only in the skill's
    references, because the person who edits this table next may be reading the
    report and nothing else.
    """
    vocab = " · ".join(f"`{s}`" for s in COVERAGE_STATUS)
    lines = [
        "## Track coverage",
        "",
        f"Status is a closed vocabulary — {vocab}. Any status but `observed` or "
        f"`unlooked` owes a reason in Notes. A row left as seeded reads `unlooked`, "
        f"which is what a track nobody ran actually is.",
        "",
        COVERAGE_HEADER,
        "|---|---|---|",
    ]
    for r in seed:
        lines.append(f"| {r['track']} {r['label']} | {r['status']} | {_flat(r['notes'])} |")
    return "\n".join(lines)


def validate_coverage(text: str) -> list[str]:
    """Every complaint a coverage table can earn. Empty list = it says something.

    Reads a rendered report — the skeleton, a seeded table, or the filled-in
    deliverable — and answers whether a reader could tell a clean track from one
    that never ran. A blank cell is a finding here, which is the whole point: the
    defect this replaces was two opposite states sharing one output.
    """
    errs: list[str] = []
    lines = text.split("\n")
    start = next((i for i, ln in enumerate(lines)
                  if ln.strip().lower().startswith("## track coverage")), None)
    if start is None:
        return ["no `## Track coverage` section — a report with no coverage table cannot "
                "distinguish a track that came back clean from one that never looked"]

    hdr = None
    for i in range(start + 1, len(lines)):
        s = lines[i].strip()
        if s.startswith("## "):
            break
        if " ".join(s.split()) == COVERAGE_HEADER:
            hdr = i
            break
    if hdr is None:
        return [f"`## Track coverage` carries no table with the header {COVERAGE_HEADER!r}"]

    rows = []
    for i in range(hdr + 1, len(lines)):
        s = lines[i].strip()
        if not s.startswith("|"):
            break
        if re.match(r"^\|[\s:\-|]+\|$", s):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) != 3:
            errs.append(f"coverage row {s!r} has {len(cells)} cells, the header has 3")
            continue
        rows.append(cells)

    declared = [t[0] for t in TRACKS]
    seen = [c[0].split(" ", 1)[0] for c in rows]
    if seen != declared:
        errs.append(f"the coverage table lists tracks {seen} — SKILL.md declares {declared}. "
                    f"A track with no row cannot be reported as unchecked at all, which is "
                    f"the denominator shrinking silently")

    words = {_status_word(s) for s in COVERAGE_STATUS}
    for tid, status, notes in rows:
        where = f"coverage row {tid.split(' ', 1)[0]!r}"
        if not status:
            errs.append(f"{where}: blank Status — a blank cell reads the same whether the "
                        f"track was clean or never ran. Use one of: "
                        f"{', '.join(COVERAGE_STATUS)}")
            continue
        word = _status_word(status)
        if word not in words:
            errs.append(f"{where}: {status!r} is outside the closed vocabulary "
                        f"({', '.join(COVERAGE_STATUS)}) — an unrecognised status is read as "
                        f"no status, which is how the enum drifts")
            continue
        if word == "blocked-by":
            gate = status.split(" ", 1)[1].strip() if " " in status else ""
            if not gate:
                errs.append(f"{where}: `blocked-by` with no gate — the gate is what decides "
                            f"which screen the client opens next")
            elif gate not in COVERAGE_GATES:
                errs.append(f"{where}: gate {gate!r} is not one this skill emits "
                            f"({', '.join(COVERAGE_GATES)})")
        if word not in NO_REASON_NEEDED and not notes:
            errs.append(f"{where}: status {word!r} with an empty Notes cell — every status but "
                        f"{' and '.join(NO_REASON_NEEDED)} is a claim about why, and a claim "
                        f"with no reason is the thing this table replaced")
    return errs


def render(rows: list[dict]) -> str:
    ok = [r for r in rows if r["reachable"]]
    bad = [r for r in rows if not r["reachable"]]
    lines = ["# Preflight — what this audit can actually observe", "",
             f"**{len(ok)} of {len(rows)} sources reachable.**", ""]
    lines += ["| source | state | detail |", "|---|---|---|"]
    for r in rows:
        mark = "✅" if r["reachable"] else "❌"
        lines.append(f"| {r['source']} | {mark} | {_flat(r['detail'])} |")
    if bad:
        lines += ["", "## What this costs the audit", ""]
        for r in bad:
            # `gate_note`, not `gate`: this is a rendered fragment, and
            # `test/validate.py` reads assignments to a name `gate` to learn which
            # gates a probe can emit. Sharing the name made the guard report `''`
            # as an undeclared gate — a rendering local answering a question about
            # the vocabulary.
            gate_note = f" (gate: **{r['gate']}**)" if r.get("gate") else ""
            what = r["blocks"] or "the checks that depend on this source"
            lines.append(f"- **{r['source']}** unreachable{gate_note} — blocks {what}")
        lines += ["", "Report these in the three-line status, and tier every finding "
                       "that rests on a missing source accordingly. An unreachable "
                       "source is a gap in the report, not a silent omission "
                       "(non-negotiable #6)."]
    else:
        lines += ["", "Every probed source answered. Findings can rest on the highest "
                       "rung each check allows (tooling.md, the evidence ladder)."]
    # The coverage floor, in the deliverable's own vocabulary and its own table
    # shape, so step 4 pastes it instead of typing it. A field a human fills in
    # after the run is the debt this exists to retire.
    lines += ["", render_coverage(coverage_seed(rows))]
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--site", help="GSC property: sc-domain:example.com or https://example.com/")
    ap.add_argument("--origin", help="site origin to probe publicly, e.g. https://example.com")
    ap.add_argument("--quota-project", help="GCP project that meters the API calls")
    ap.add_argument("--skip-psi", action="store_true", help="skip the PageSpeed probe (it is slow)")
    ap.add_argument("--format", choices=["markdown", "json", "coverage"],
                    default="markdown",
                    help="markdown report, the JSON payload, or just the report's "
                         "seeded Track coverage section")
    args = ap.parse_args(argv)

    if not args.site and not args.origin:
        print("pass --site and/or --origin — there is nothing to probe otherwise",
              file=sys.stderr)
        return 1

    rows = [check_python()]
    if args.site:
        gcloud_row, token = check_gcloud()
        rows.append(gcloud_row)
        rows += check_gsc(token, args.site, args.quota_project)
    if args.origin:
        rows += check_public(args.origin)
        if not args.skip_psi:
            rows.append(check_psi(args.origin))

    if args.format == "json":
        print(json.dumps({"probes": rows,
                          "reachable": sum(1 for r in rows if r["reachable"]),
                          "total": len(rows),
                          "tracks": [{"track": t, "label": l} for t, l in TRACKS],
                          "coverage_status": list(COVERAGE_STATUS),
                          "coverage": coverage_seed(rows)}, indent=2))
    elif args.format == "coverage":
        print(render_coverage(coverage_seed(rows)))
    else:
        print(render(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
