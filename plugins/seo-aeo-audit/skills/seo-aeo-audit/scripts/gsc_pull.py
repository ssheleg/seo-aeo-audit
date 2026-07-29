#!/usr/bin/env python3
"""gsc_pull — Search Console evidence for an audit or a link-building brief.

Pulls what an audit cannot observe from the outside: which queries a property
actually surfaces for, at what position, and which pages carry them. Also
detects a *collapse* — a drop that holds — because a cliff and a decline have
different causes and only one of them is an algorithmic story.

stdlib only. Auth is local Application Default Credentials, so no key file and
no secret lives near this script:

  gcloud auth application-default login --scopes="openid,email,\\
https://www.googleapis.com/auth/cloud-platform,\\
https://www.googleapis.com/auth/webmasters.readonly"

Three gates fail independently, each with an unhelpful error; this script names
which one you hit:
  1. the OAuth scope above
  2. searchconsole.googleapis.com enabled on a project the account can USE
  3. the quota project, sent as x-goog-user-project (client libraries add it
     from the ADC file, raw HTTP does not)

The quota project only decides where calls are metered. It does NOT select the
property and grants no access to any site — that comes from the signed-in
account and the siteUrl.

Usage:
  gsc_pull.py --site sc-domain:example.com [--quota-project my-proj]
  gsc_pull.py --site https://example.com/ --days 90 --format json
  gsc_pull.py --list                      # properties this account can see

What it cannot give you: Manual Actions, Security Issues and the Index Coverage
report are web-UI only, at every scope. An unexplained cliff needs a human to
open that page.

Exit codes: 0 = ran, 1 = usage/auth/API error.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, timedelta

API = "https://searchconsole.googleapis.com/webmasters/v3"

# Search Console lags roughly two days. Asking for today returns a partial tail
# that reads as a drop — the easiest way to invent a collapse that is not there.
REPORTING_LAG_DAYS = 2


# ── auth ─────────────────────────────────────────────────────────────────────


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


def call(path: str, token: str, quota_project: str | None,
         body: dict | None = None) -> dict:
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    if quota_project:
        headers["x-goog-user-project"] = quota_project
    req = urllib.request.Request(
        f"{API}{path}",
        data=json.dumps(body).encode() if body is not None else None,
        headers=headers,
        method="POST" if body is not None else "GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")
        if e.code == 403 and "quota project" in detail:
            raise SystemExit(
                "403: no quota project. Pass --quota-project <gcp-project> where "
                "searchconsole.googleapis.com is enabled and the signed-in account "
                "can use it. It only meters calls; it grants no site access."
            )
        if e.code == 403 and "scope" in detail.lower():
            raise SystemExit(
                "403: the credential lacks webmasters.readonly. Re-run the "
                "application-default login shown in this script's header, listing "
                "every scope you already had — the login replaces them."
            )
        raise SystemExit(f"HTTP {e.code} on {path}: {detail[:300]}")


def query(site: str, token: str, quota_project: str | None, dimensions: list[str],
          start: str, end: str, row_limit: int = 25000) -> list[dict]:
    enc = urllib.parse.quote(site, safe="")
    body = {"startDate": start, "endDate": end,
            "dimensions": dimensions, "rowLimit": row_limit}
    return call(f"/sites/{enc}/searchAnalytics/query", token, quota_project, body).get("rows", [])


# ── pure analysis (no network — unit-testable) ───────────────────────────────


def monthly_rollup(rows: list[dict]) -> list[dict]:
    """Group date-keyed rows by calendar month, ascending."""
    acc: dict[str, dict] = {}
    for r in rows:
        m = r["keys"][0][:7]
        a = acc.setdefault(m, {"month": m, "clicks": 0.0, "impressions": 0.0})
        a["clicks"] += r["clicks"]
        a["impressions"] += r["impressions"]
    return sorted(acc.values(), key=lambda a: a["month"])


def position_split(rows: list[dict]) -> dict:
    """Split a query set by position band. This is the number that decides a brief.

    A large impression count beyond position 30 is not an opportunity; the band
    at or inside 20 usually carries a fraction of the impressions and most of
    the clicks.
    """
    bands = {"top20": [], "striking_21_30": [], "beyond_30": []}
    for r in rows:
        p = r.get("position", 999)
        key = "top20" if p <= 20 else ("striking_21_30" if p <= 30 else "beyond_30")
        bands[key].append(r)
    out = {}
    for k, rs in bands.items():
        imp = sum(r["impressions"] for r in rs)
        clk = sum(r["clicks"] for r in rs)
        out[k] = {"queries": len(rs), "impressions": round(imp),
                  "clicks": round(clk), "ctr": (clk / imp) if imp else 0.0}
    return out


def find_cliff(rows: list[dict], min_drop: float = 0.9, min_baseline: float = 50.0,
               window: int = 7, hold_days: int = 14) -> dict | None:
    """A drop that HOLDS. The hold requirement is the whole point.

    A single bad day is noise, and reporting gaps produce exactly that. What
    separates a site-level event from an algorithmic one is that the floor
    persists — updates redistribute, they do not zero a property for weeks.
    """
    daily = sorted(rows, key=lambda r: r["keys"][0])
    if len(daily) < window + hold_days + 1:
        return None
    for i in range(window, len(daily) - hold_days):
        baseline = sum(r["impressions"] for r in daily[i - window:i]) / window
        if baseline < min_baseline:
            continue
        today = daily[i]["impressions"]
        drop = 1 - (today / baseline if baseline else 1)
        if drop < min_drop:
            continue
        hold = daily[i:i + hold_days]
        if (sum(r["impressions"] for r in hold) / hold_days) > baseline * (1 - min_drop):
            continue
        return {"before": daily[i - 1]["keys"][0], "after": daily[i]["keys"][0],
                "before_impressions": round(daily[i - 1]["impressions"]),
                "after_impressions": round(today), "drop": round(drop, 4)}
    return None


def iso_days_before(days: int, today: date) -> str:
    return (today - timedelta(days=days)).isoformat()


def is_noise(q: str) -> bool:
    """Scraper and operator noise that should never reach a deliverable."""
    return q.startswith("-site:") or '"' in q or "http" in q


# ── CLI ──────────────────────────────────────────────────────────────────────


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--site", help="sc-domain:example.com or https://example.com/")
    ap.add_argument("--quota-project", help="GCP project that meters the API calls")
    ap.add_argument("--days", type=int, default=90, help="recent window (default 90)")
    ap.add_argument("--history-days", type=int, default=480,
                    help="long window for the trend and cliff detector (default 480)")
    ap.add_argument("--list", action="store_true", help="list visible properties and exit")
    ap.add_argument("--format", choices=["text", "json"], default="text")
    args = ap.parse_args()

    token = access_token()
    qp = args.quota_project

    sites = call("/sites", token, qp).get("siteEntry", [])
    if args.list or not args.site:
        for s in sites:
            print(f"  {s.get('permissionLevel','?'):<22} {s['siteUrl']}")
        if not args.site:
            print("\nPass --site to pull a property.", file=sys.stderr)
        return 0

    site = args.site
    if not any(s["siteUrl"] == site for s in sites):
        print(f"warning: {site} is not in this account's property list. "
              f"A property can be DNS-verified and still invisible to an account "
              f"that was never added under Users and permissions.", file=sys.stderr)

    today = date.today()
    end = iso_days_before(REPORTING_LAG_DAYS, today)
    start_recent = iso_days_before(REPORTING_LAG_DAYS + args.days, today)
    start_hist = iso_days_before(REPORTING_LAG_DAYS + args.history_days, today)

    daily = query(site, token, qp, ["date"], start_hist, end)
    queries = [r for r in query(site, token, qp, ["query"], start_recent, end, 5000)
               if not is_noise(r["keys"][0])]
    pages = query(site, token, qp, ["page"], start_recent, end, 5000)
    pairs = [r for r in query(site, token, qp, ["query", "page"], start_recent, end, 25000)
             if not is_noise(r["keys"][0])]
    sitemaps = call(f"/sites/{urllib.parse.quote(site, safe='')}/sitemaps",
                    token, qp).get("sitemap", [])

    report = {
        "site": site,
        "recent_window": {"start": start_recent, "end": end},
        "history_window": {"start": start_hist, "end": end},
        "monthly": monthly_rollup(daily),
        "cliff": find_cliff(daily),
        "position_split": position_split(queries),
        "top_queries": sorted(queries, key=lambda r: -r["impressions"])[:100],
        "top_pages": sorted(pages, key=lambda r: -r["clicks"])[:100],
        "query_page_pairs": pairs[:5000],
        "sitemaps": sitemaps,
    }

    if args.format == "json":
        json.dump(report, sys.stdout, indent=2)
        print()
        return 0

    n = lambda x: f"{round(x):,}"  # noqa: E731
    print(f"property: {site}")
    ps = report["position_split"]
    print("\nposition split (recent window) — rank the brief by THIS, not by impressions:")
    for band, label in (("top20", "<= 20"), ("striking_21_30", "21-30"), ("beyond_30", "> 30")):
        b = ps[band]
        print(f"  pos {label:<6} queries={b['queries']:<5} impressions={n(b['impressions']):>9} "
              f"clicks={b['clicks']:<5} ctr={b['ctr']*100:5.2f}%")

    if report["cliff"]:
        c = report["cliff"]
        print(f"\nCOLLAPSE: {c['before']} ({n(c['before_impressions'])} imp) -> "
              f"{c['after']} ({n(c['after_impressions'])} imp), {c['drop']*100:.1f}% and held.")
        print("  A cliff that holds is site-level, not an algorithmic update. Check which")
        print("  URLs ranked before it and whether they still resolve. Manual Actions and")
        print("  Index Coverage are web-UI only — the API cannot clear them.")

    print("\nmonth      clicks  impressions")
    for m in report["monthly"]:
        print(f"  {m['month']}  {n(m['clicks']):>6}  {n(m['impressions']):>11}")

    for label, rows_, k in (("top queries", report["top_queries"], 30),
                            ("top pages", report["top_pages"], 30)):
        print(f"\n--- {label} ---")
        for r in rows_[:k]:
            print(f"  {n(r['clicks']):>6} clicks {n(r['impressions']):>9} imp "
                  f"pos {r['position']:5.1f}  {r['keys'][0][:80]}")

    print("\n--- sitemaps ---")
    if not sitemaps:
        print("  none submitted")
    for sm in sitemaps:
        c = (sm.get("contents") or [{}])[0]
        print(f"  {sm['path']}  submitted={c.get('submitted','-')} "
              f"errors={sm.get('errors',0)} lastDownloaded={(sm.get('lastDownloaded') or '-')[:19]}")
    print("\nNote: the sitemap 'indexed' field reads 0 for every sitemap — Google no longer")
    print("populates it. It is not an indexation measurement.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
