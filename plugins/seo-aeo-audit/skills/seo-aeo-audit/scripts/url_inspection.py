#!/usr/bin/env python3
"""url_inspection — what Google itself says about a URL, not what a crawl infers.

Every other instrument in this skill observes the page. This one asks the index.
That difference is the whole point: the Google-selected canonical, the coverage
state and the robots verdict are the engine's own answer, so a finding built on
them sits at CONFIRMED rather than at whatever a fetch could support.

The check it exists for: `googleCanonical` != `userCanonical`. A site can declare
a canonical perfectly and still be grouped somewhere else, and no amount of
view-source shows that — only the index does.

stdlib only. Auth is the same local Application Default Credentials gsc_pull.py
uses, and the same scope already covers this API:

  gcloud auth application-default login --scopes="openid,email,\\
https://www.googleapis.com/auth/cloud-platform,\\
https://www.googleapis.com/auth/webmasters.readonly"

Quota is per PROPERTY and it is small: 2000 inspections/day and 600/minute
(developers.google.com/webmaster-tools/limits). This is not a crawler. Run it on
a representative URL per template and on the specific pages a finding is about,
the same way page_audit.py is meant to be run.

Usage:
  url_inspection.py --site sc-domain:example.com --urls https://example.com/a
  url_inspection.py --site https://example.com/ --urls-file urls.txt --format json
  url_inspection.py --site sc-domain:example.com --urls-file urls.txt --max-urls 50

Every output carries a **producer block** — `skill` (this tool's version), `script`,
`observed_at` (UTC), `runtime`, `args` (credential values redacted), `scope` (the
resolved input set), and `actor` / `model` / `trace` from `SEO_AEO_AUDIT_ACTOR`,
`_MODEL`, `_TRACE`. It is present in the default output and under `--format json` as
`producer`. A field the harness did not supply reads `unavailable: <VAR> is not set by
this harness` — never guessed, and never dropped, because a field that vanishes when
unavailable is indistinguishable from one nobody checked. `observed_at` is the field
that decides whether a finding has expired; the report's own `## Provenance` block adds
the four invalidators (see references/preflight.md).

Exit codes: 0 = the index answered for at least one URL, 1 = usage/auth/API error,
or no URL was answered. "Ran" is not the useful question: a run of 403s ran, and
supports nothing. The status and the report read the same predicate (answered_rows).
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request


# ── provenance: the execution that produced this payload ── shared block ──────
# Copied verbatim into all seven scripts and compared byte for byte by
# `test/validate.py`, for the same reason `_flat` is: these ship as standalone files
# with no shared module, and an import of one does not exist in the installed layout
# (`bin/seo-aeo-audit.js` copies `scripts/` alone into `~/.claude/skills/`). The
# doctrine behind the field set lives above this block in preflight.py. Never edit
# one copy — the guard fails all seven.
SKILL_VERSION = "0.25.3"

# The fields no python process can establish, with the variable that would supply
# each. They print by NAME on every run, because a field that vanishes when
# unavailable is indistinguishable from one nobody checked.
PRODUCER_ENV = (
    ("actor", "SEO_AEO_AUDIT_ACTOR", "who or what invoked the run"),
    ("model", "SEO_AEO_AUDIT_MODEL", "the model behind the agent — never inferred"),
    ("trace", "SEO_AEO_AUDIT_TRACE", "the id linking these actions to a run"),
)

# The closed field set, in render order. A payload missing one of these is refused
# by `preflight.validate_provenance`.
PRODUCER_FIELDS = ("skill", "script", "observed_at", "runtime", "args", "scope",
                   "actor", "model", "trace")

# Flags whose VALUE is a credential. `psi_pull.py --key <secret>` is the live case:
# echoing argv verbatim would write an API key into a deliverable somebody emails.
SECRET_FLAGS = ("--key",)

# One home for the block's table shape, read by every renderer, by
# `preflight.validate_provenance`, and by `test/validate.py` when it looks for the
# block in both report skeletons.
PROVENANCE_HEADER = "| Field | Value |"


def redact(argv: list[str]) -> list[str]:
    """The argv as given, with every credential flag's value removed.

    Both spellings, because handling one is the same as handling neither: `--key V`
    hides the following token, `--key=V` hides the tail.
    """
    out: list[str] = []
    hide = False
    for a in argv:
        if hide:
            out.append("<redacted>")
            hide = False
            continue
        head, sep, _ = a.partition("=")
        if head in SECRET_FLAGS:
            out.append(f"{head}=<redacted>" if sep else head)
            hide = not sep
        else:
            out.append(a)
    return out


def provenance(script: str, argv: list[str], scope: str = "") -> dict:
    """Which execution produced this payload: what ran, when, on what, about what.

    Every field in `PRODUCER_FIELDS` is present on every run. A value this process
    cannot establish reads `unavailable: <VAR> is not set by this harness` — never a
    guess and never nothing. `model` in particular is not inferred: naming the wrong
    vendor id is worse than saying nothing.
    """
    v = sys.version_info
    out = {
        "skill": f"seo-aeo-audit@{SKILL_VERSION}",
        "script": script,
        "observed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "runtime": f"{sys.implementation.name} {v.major}.{v.minor}.{v.micro} "
                   f"on {sys.platform}",
        "args": redact(argv),
        "scope": scope or "unavailable: this run resolved no input set to record",
    }
    for _name, _var, _what in PRODUCER_ENV:
        _val = os.environ.get(_var, "").strip()
        out[_name] = _val or f"unavailable: {_var} is not set by this harness ({_what})"
    return out


def provenance_md(prov: dict) -> str:
    """The producer block as a markdown table — one row per field, always.

    Emitted in the DEFAULT output format too, not only under `--format json`. This
    bundle has already shipped the other shape: four `gsc_pull.py` analyses were
    computed into the payload and printed only in JSON while `text` was the
    documented invocation, so an agent running the documented command never saw
    them. A provenance block a human never reads is a provenance block that does
    not exist.
    """
    lines = ["## Provenance — the execution that produced this", "",
             PROVENANCE_HEADER, "|---|---|"]
    for f in PRODUCER_FIELDS:
        v = prov.get(f, "")
        if isinstance(v, list):
            v = " ".join(v)
        # Flattened here rather than through `_flat`: only five of the seven scripts
        # define one, and a shared block resting on a name two of its homes lack
        # would crash in exactly the two least-exercised renderers.
        cell = " ".join(str(v).split()).replace("|", "\\|")
        if len(cell) > 300:
            cell = cell[:299].rstrip() + "…"
        lines.append(f"| {f} | `{cell}` |")
    return "\n".join(lines)
# ── end provenance shared block ──────────────────────────────────────────────


API = "https://searchconsole.googleapis.com/v1"

# 600 queries/minute per property is the documented ceiling. 0.12s between calls
# leaves headroom for the request itself and keeps a long run inside the limit
# without needing a token bucket.
MIN_INTERVAL = 0.12
DEFAULT_MAX_URLS = 25


def access_token() -> str:
    try:
        out = subprocess.run(
            ["gcloud", "auth", "application-default", "print-access-token"],
            capture_output=True, text=True, check=True,
        )
    except FileNotFoundError:
        raise SystemExit("gcloud not found. Install the Google Cloud SDK, then run the "
                         "application-default login shown in this script's header.")
    except subprocess.CalledProcessError as e:
        raise SystemExit(f"could not mint an access token: {e.stderr.strip()[:200]}")
    return out.stdout.strip()


def inspect(site: str, url: str, token: str, quota_project: str | None) -> dict:
    """One inspection. Returns the raw API result, or {'_error': ...} — never raises."""
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    if quota_project:
        headers["x-goog-user-project"] = quota_project
    body = json.dumps({"inspectionUrl": url, "siteUrl": site}).encode()
    req = urllib.request.Request(f"{API}/urlInspection/index:inspect",
                                 data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:300]
        # The three failure gates are independent and their messages are unhelpful
        # on their own; name which one was hit so the run is diagnosable.
        if e.code == 403:
            hint = ("403 — either the OAuth scope is missing webmasters.readonly, "
                    "or searchconsole.googleapis.com is not enabled on the quota "
                    "project, or this account cannot see this property")
        elif e.code == 429:
            hint = ("429 — quota exhausted. The per-property ceiling is 2000/day "
                    "and 600/minute; this is a sampling tool, not a crawler")
        else:
            hint = f"HTTP {e.code}"
        return {"_error": f"{hint}: {detail}"}
    except Exception as exc:  # noqa: BLE001 - one bad URL must not end the run
        return {"_error": str(exc)[:300]}


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


def answered_rows(rows: list[dict]) -> list[dict]:
    """The rows the index actually answered for.

    One home, because the report and the exit status must not decide this
    separately. Printed unconditionally, the CONFIRMED footer once declared a run
    of 403s to be confirmed evidence; returning 0 unconditionally made the exit
    status tell an agent the same lie one layer down.
    """
    return [r for r in rows if not r.get("error") and r.get("has_index_status")]


def _as_dict(v) -> dict:
    return v if isinstance(v, dict) else {}


def _as_list(v) -> list:
    return v if isinstance(v, list) else []


def parse(raw: dict, url: str) -> dict:
    """Field names per the Search Console API reference. `userCanonical` is the
    documented spelling — a widely copied third-party parser reads
    `userDeclaredCanonical`, which is always absent and so always reports the
    declared canonical as missing."""
    if "_error" in raw:
        return {"url": url, "error": raw["_error"]}
    inspection = _as_dict(raw.get("inspectionResult"))
    idx = _as_dict(inspection.get("indexStatusResult"))
    rich = _as_dict(inspection.get("richResultsResult"))
    rich_types = []
    for item in _as_list(rich.get("detectedItems")):
        name = _as_dict(item).get("richResultType")
        if name:
            rich_types.append(name)
    return {
        "url": url,
        # Whether the index answered at all, kept apart from what it answered: with
        # no indexStatusResult every field below parses to None, and "all fields
        # absent" used to come out as the finding "never crawled".
        "has_index_status": bool(idx),
        "verdict": idx.get("verdict"),
        "coverage_state": idx.get("coverageState"),
        "indexing_state": idx.get("indexingState"),
        "robots_txt_state": idx.get("robotsTxtState"),
        "page_fetch_state": idx.get("pageFetchState"),
        "last_crawl_time": idx.get("lastCrawlTime"),
        "crawled_as": idx.get("crawledAs"),
        "google_canonical": idx.get("googleCanonical"),
        "user_canonical": idx.get("userCanonical"),
        "referring_urls": _as_list(idx.get("referringUrls")),
        "sitemaps": _as_list(idx.get("sitemap")),
        "rich_results_verdict": rich.get("verdict"),
        "rich_result_types": rich_types,
    }


# Google documents the coverage states; the verdict field is the engine's own
# summary of them. PASS and PARTIAL are indexed; FAIL and NEUTRAL are not, and
# NEUTRAL is where every *exclusion* lands — duplicates, canonical alternates,
# `noindex`, unknown URLs. Substring-matching "not indexed" caught two of those
# and silently passed the rest.
INDEXED_VERDICTS = frozenset({"PASS", "PARTIAL"})
NOT_INDEXED_VERDICTS = frozenset({"FAIL", "NEUTRAL"})


def findings(r: dict) -> list[dict]:
    """Only what the index actually said. No inference, no eligibility claims."""
    out: list[dict] = []

    def add(sev, code, msg):
        out.append({"severity": sev, "code": code, "message": msg})

    if r.get("error"):
        return out
    if not r.get("has_index_status"):
        add("high", "no-index-status",
            "the API answered without an indexStatusResult, so nothing about this URL's "
            "index state was returned. This is a gap in the report, not a verdict about "
            "the page — re-run it, and check the property and URL match")
        return out
    gc, uc = r.get("google_canonical"), r.get("user_canonical")
    if gc and uc and gc != uc:
        add("blocker", "canonical-disagreement",
            f"Google selected {gc} but the page declares {uc} — the declaration "
            "was not accepted, so signals consolidate somewhere you did not choose")
    if uc in (None, "") and gc:
        add("high", "canonical-undeclared",
            f"no user-declared canonical; Google picked {gc} on its own")
    _verdict = (r.get("verdict") or "").upper()
    if _verdict in NOT_INDEXED_VERDICTS or (
            _verdict not in INDEXED_VERDICTS
            and r.get("coverage_state")
            and "not indexed" in str(r["coverage_state"]).lower()):
        add("blocker", "not-indexed",
            f"the index reports verdict {_verdict or '(none)'} with coverage state "
            f"{r.get('coverage_state')!r} — this URL is not in the index, and nothing else "
            "about the page matters until it is")
    if r.get("robots_txt_state") == "DISALLOWED":
        add("blocker", "robots-disallowed", "robots.txt disallows this URL")
    if r.get("page_fetch_state") not in (None, "SUCCESSFUL"):
        add("high", "fetch-failed", f"page fetch state: {r['page_fetch_state']}")
    if not r.get("last_crawl_time"):
        add("medium", "never-crawled", "no last crawl time recorded for this URL")
    return out


def render_markdown(rows: list[dict], dropped: int) -> str:
    lines = ["# URL Inspection — Google's own verdict", ""]
    if dropped:
        lines.append(f"> **{dropped} URL(s) not inspected** — capped by `--max-urls`. "
                     f"This tool samples; it does not crawl.\n")
    for r in rows:
        lines.append(f"## {r['url']}")
        if r.get("error"):
            lines.append(f"- **could not inspect**: {_flat(r['error'])}\n")
            continue
        lines.append(f"- verdict: `{r.get('verdict')}` · coverage: "
                     f"`{r.get('coverage_state')}`")
        lines.append(f"- canonical — Google: `{r.get('google_canonical')}` · "
                     f"declared: `{r.get('user_canonical')}`")
        lines.append(f"- robots: `{r.get('robots_txt_state')}` · fetch: "
                     f"`{r.get('page_fetch_state')}` · crawled as: `{r.get('crawled_as')}`")
        lines.append(f"- last crawl: `{r.get('last_crawl_time')}`")
        for f in r.get("findings", []):
            lines.append(f"  - **{f['severity']}** [{f['code']}] {f['message']}")
        lines.append("")
    # The tier belongs to answers that arrived. Printed unconditionally, this line
    # declared a run of 403s to be CONFIRMED evidence — from the one instrument in
    # the skill whose whole justification is that it can legitimately claim the tier.
    answered = answered_rows(rows)
    if answered:
        lines.append(f"Evidence tier: CONFIRMED for the {len(answered)} of {len(rows)} URL(s) "
                     f"the index answered for — those are the engine's own answers, not "
                     f"inferences from a fetch. Record the date beside them.")
        if len(answered) != len(rows):
            lines.append(f"The remaining {len(rows) - len(answered)} produced no index answer "
                         f"and support no finding at any tier (non-negotiable #6: that is a "
                         f"gap in the report, not a silent omission).")
    else:
        lines.append("No index answers were obtained: every URL failed or returned no index "
                     "status, so this run supports **no findings at any tier**. Fix the access "
                     "gate named above and re-run; report the gap meanwhile "
                     "(non-negotiable #6).")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--site", required=True,
                    help="GSC property: sc-domain:example.com or https://example.com/")
    ap.add_argument("--urls", nargs="*", default=[], help="one or more URLs to inspect")
    ap.add_argument("--urls-file", help="file with one URL per line")
    ap.add_argument("--max-urls", type=int, default=DEFAULT_MAX_URLS,
                    help=f"cap (default {DEFAULT_MAX_URLS}); the excess is reported, never dropped silently")
    ap.add_argument("--quota-project", help="GCP project that meters the API calls")
    ap.add_argument("--format", choices=["markdown", "json"], default="markdown")
    args = ap.parse_args(argv)

    urls = list(args.urls)
    if args.urls_file:
        try:
            with open(args.urls_file, encoding="utf-8") as fh:
                urls += [ln.strip() for ln in fh if ln.strip() and not ln.startswith("#")]
        except OSError as e:
            print(f"cannot read --urls-file: {e}", file=sys.stderr)
            return 1
    seen, deduped = set(), []
    for u in urls:
        if u not in seen:
            seen.add(u)
            deduped.append(u)
    if not deduped:
        print("no URLs given: pass --urls and/or --urls-file", file=sys.stderr)
        return 1

    dropped = max(0, len(deduped) - args.max_urls)
    batch = deduped[: args.max_urls]
    if dropped:
        print(f"note: {dropped} URL(s) beyond --max-urls={args.max_urls} were not "
              f"inspected", file=sys.stderr)

    token = access_token()
    rows = []
    for i, u in enumerate(batch):
        if i:
            time.sleep(MIN_INTERVAL)
        r = parse(inspect(args.site, u, token, args.quota_project), u)
        r["findings"] = findings(r)
        rows.append(r)

    prov = provenance("url_inspection.py", argv,
                      f"property {args.site}, {len(batch)} URL(s) inspected: "
                      + ", ".join(batch[:5])
                      + (f" (+{len(batch) - 5} more)" if len(batch) > 5 else ""))
    if args.format == "json":
        print(json.dumps({"producer": prov, "site": args.site, "inspected": len(rows),
                          "not_inspected": dropped, "results": rows}, indent=2))
    else:
        print(render_markdown(rows, dropped))
        print("\n" + provenance_md(prov))
    # The report already says the run supports nothing; the exit status has to say
    # it too. SKILL.md's own invocation redirects stdout to a file, so an agent that
    # branches on the status reads "success" from a page of refusals otherwise.
    return 0 if answered_rows(rows) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
