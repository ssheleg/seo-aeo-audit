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

Exit codes: 0 = ran, 1 = usage/auth/API error.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

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
    idx = _as_dict(_as_dict(raw.get("inspectionResult")).get("indexStatusResult"))
    rich = _as_dict(_as_dict(raw.get("inspectionResult")).get("richResultsResult"))
    rich_types = []
    for item in _as_list(rich.get("detectedItems")):
        name = _as_dict(item).get("richResultType")
        if name:
            rich_types.append(name)
    return {
        "url": url,
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


def findings(r: dict) -> list[dict]:
    """Only what the index actually said. No inference, no eligibility claims."""
    out: list[dict] = []

    def add(sev, code, msg):
        out.append({"severity": sev, "code": code, "message": msg})

    if r.get("error"):
        return out
    gc, uc = r.get("google_canonical"), r.get("user_canonical")
    if gc and uc and gc != uc:
        add("blocker", "canonical-disagreement",
            f"Google selected {gc} but the page declares {uc} — the declaration "
            "was not accepted, so signals consolidate somewhere you did not choose")
    if uc in (None, "") and gc:
        add("high", "canonical-undeclared",
            f"no user-declared canonical; Google picked {gc} on its own")
    if r.get("verdict") == "FAIL" or (
            r.get("coverage_state") and "not indexed" in str(r["coverage_state"]).lower()):
        add("blocker", "not-indexed",
            f"coverage state: {r.get('coverage_state')!r} — nothing else about this "
            "page matters until it is in the index")
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
            lines.append(f"- **could not inspect**: {r['error']}\n")
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
    lines.append("Evidence tier: CONFIRMED — these are the index's own answers, "
                 "not inferences from a fetch. Record the date beside them.")
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

    if args.format == "json":
        print(json.dumps({"site": args.site, "inspected": len(rows),
                          "not_inspected": dropped, "results": rows}, indent=2))
    else:
        print(render_markdown(rows, dropped))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
