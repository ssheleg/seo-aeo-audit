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

Exit codes: 0 = probes ran (even if some failed — that IS the report),
            1 = usage error.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

UA = "seo-aeo-audit/preflight (+https://github.com/ssheleg/seo-aeo-audit)"
GSC = "https://searchconsole.googleapis.com/v1"
PSI = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"


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


def check_gsc(token: str | None, site: str | None, quota_project: str | None) -> list[dict]:
    if not token:
        return [probe("Search Console", False, "no token to try with", "login",
                      "query data, position history, URL Inspection")]
    headers = {"Authorization": f"Bearer {token}"}
    if quota_project:
        headers["x-goog-user-project"] = quota_project
    req = urllib.request.Request(f"{GSC}/sites", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            entries = json.loads(r.read().decode()).get("siteEntry", [])
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")[:200]
        # The three gates fail independently and all say "403".
        gate = ("scope" if "insufficient" in body.lower() or "scope" in body.lower()
                else "api-not-enabled" if "disabled" in body.lower() or "has not been used" in body.lower()
                else "permission")
        return [probe("Search Console", False, f"HTTP {e.code}: {body}", gate,
                      "query data, position history, URL Inspection")]
    except Exception as exc:  # noqa: BLE001
        return [probe("Search Console", False, str(exc)[:160], "network",
                      "query data, position history, URL Inspection")]

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


def render(rows: list[dict]) -> str:
    ok = [r for r in rows if r["reachable"]]
    bad = [r for r in rows if not r["reachable"]]
    lines = ["# Preflight — what this audit can actually observe", "",
             f"**{len(ok)} of {len(rows)} sources reachable.**", ""]
    lines += ["| source | state | detail |", "|---|---|---|"]
    for r in rows:
        mark = "✅" if r["reachable"] else "❌"
        lines.append(f"| {r['source']} | {mark} | {r['detail']} |")
    if bad:
        lines += ["", "## What this costs the audit", ""]
        for r in bad:
            gate = f" (gate: **{r['gate']}**)" if r.get("gate") else ""
            what = r["blocks"] or "the checks that depend on this source"
            lines.append(f"- **{r['source']}** unreachable{gate} — blocks {what}")
        lines += ["", "Report these in the three-line status, and tier every finding "
                       "that rests on a missing source accordingly. An unreachable "
                       "source is a gap in the report, not a silent omission "
                       "(non-negotiable #6)."]
    else:
        lines += ["", "Every probed source answered. Findings can rest on the highest "
                       "rung each check allows (tooling.md, the evidence ladder)."]
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--site", help="GSC property: sc-domain:example.com or https://example.com/")
    ap.add_argument("--origin", help="site origin to probe publicly, e.g. https://example.com")
    ap.add_argument("--quota-project", help="GCP project that meters the API calls")
    ap.add_argument("--skip-psi", action="store_true", help="skip the PageSpeed probe (it is slow)")
    ap.add_argument("--format", choices=["markdown", "json"], default="markdown")
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
                          "total": len(rows)}, indent=2))
    else:
        print(render(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
