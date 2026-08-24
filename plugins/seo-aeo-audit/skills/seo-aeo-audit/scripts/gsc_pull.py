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

Exit codes: 0 = the API answered rows for at least one dimension, 1 = usage/auth/API
error, or every dimension came back empty. "Ran" is not the useful question here: every
number this script prints below the position split is derived from rows, so a property
that answered nothing renders a full report in which no cliff, no cannibalization and no
CTR gap were found — a document that reads like a clean site and is a measurement of
nothing. The report and the exit status read one predicate, `measured_rows`.

Every output carries a **producer block** — `skill` (this tool's version), `script`,
`observed_at` (UTC), `runtime`, `args` (credential values redacted), `scope` (the
resolved input set), and `actor` / `model` / `trace` from `SEO_AEO_AUDIT_ACTOR`,
`_MODEL`, `_TRACE`. It is present in the default output and under `--format json` as
`producer`. A field the harness did not supply reads `unavailable: <VAR> is not set by
this harness` — never guessed, and never dropped, because a field that vanishes when
unavailable is indistinguishable from one nobody checked. `observed_at` is the field
that decides whether a finding has expired; the report's own `## Provenance` block adds
the four invalidators (see references/preflight.md).
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
from datetime import date, timedelta


# ── provenance: the execution that produced this payload ── shared block ──────
# Copied verbatim into all seven scripts and compared byte for byte by
# `test/validate.py`, for the same reason `_flat` is: these ship as standalone files
# with no shared module, and an import of one does not exist in the installed layout
# (`bin/seo-aeo-audit.js` copies `scripts/` alone into `~/.claude/skills/`). The
# doctrine behind the field set lives above this block in preflight.py. Never edit
# one copy — the guard fails all seven.
SKILL_VERSION = "0.25.0"

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
    """One searchAnalytics page. No pagination — see ROW_LIMIT_NOTE.

    The API orders rows by clicks descending, so a property with more rows than
    `row_limit` loses its long tail, which is exactly the band `position_split`
    exists to size. The caller reports when a limit was reached rather than
    presenting a truncated set as the query set (measurement.md J1 already names
    "data hiding on large properties" as the GSC caveat; this is the local form).
    """
    enc = urllib.parse.quote(site, safe="")
    body = {"startDate": start, "endDate": end,
            "dimensions": dimensions, "rowLimit": row_limit}
    return call(f"/sites/{enc}/searchAnalytics/query", token, quota_project, body).get("rows", [])


ROW_LIMIT_NOTE = (
    "the API returned exactly the row limit for this dimension, so the long tail is "
    "missing — and the tail is where the beyond-30 band lives. Treat the split as a "
    "lower bound on that band, or narrow the window and re-run"
)


# ── pure analysis (no network — unit-testable) ───────────────────────────────


def measured_rows(report: dict) -> int:
    """How many Search Console rows this report actually rests on.

    One predicate, read by `render_text` and by `main`'s exit status — the shape
    `url_inspection.answered_rows` settled, and the one this script did not have:
    `main()` had three `return 0` paths and no `return 1`, so a run that measured
    nothing exited success. Four dimensions are pulled and every derivation below
    the position split is computed from them, so zero rows across all four is the
    honest zero: not "no cannibalization on this property" but "nothing was
    measured". The commonest causes are a `sc-domain:` property spelled as its
    `https://` twin (different resources), and a window that predates verification.
    """
    return sum(len(report.get(k) or []) for k in
               ("monthly", "top_queries", "top_pages", "query_page_pairs"))


def monthly_rollup(rows: list[dict]) -> list[dict]:
    """Group date-keyed rows by calendar month, ascending."""
    acc: dict[str, dict] = {}
    for r in rows:
        m = r["keys"][0][:7]
        a = acc.setdefault(m, {"month": m, "clicks": 0.0, "impressions": 0.0})
        a["clicks"] += r["clicks"]
        a["impressions"] += r["impressions"]
    return sorted(acc.values(), key=lambda a: a["month"])


def ctr_curve(rows: list[dict], min_impressions: float = 30.0) -> dict:
    """This property's own CTR by position band — the only honest expectation.

    Industry CTR tables are in measurement.md J6's do-not-measure list, and for a
    reason: CTR is contextual. 5% at position 3 can be over- or under-performing
    depending on brand strength, SERP features and intent mix, none of which a
    generic table knows about this site. So the baseline is built here, from the
    property's own rows, and a page is judged against how *this* site performs at
    *that* position.

    Returns {band: {"median_ctr": float, "sample": int}}. Bands with too small a
    sample are omitted rather than reported thinly — a curve fitted to four rows
    is a guess with a decimal point.
    """
    buckets: dict[str, list[float]] = {}
    for r in rows:
        if r.get("impressions", 0) < min_impressions:
            continue
        p = r.get("position", 0)
        if p <= 0:
            continue
        band = ("1-3" if p <= 3.5 else "4-10" if p <= 10.5 else
                "11-20" if p <= 20.5 else "21-30" if p <= 30.5 else "31+")
        buckets.setdefault(band, []).append(r.get("ctr", 0.0))
    out = {}
    for band, vals in buckets.items():
        if len(vals) < 5:
            continue
        vals.sort()
        mid = len(vals) // 2
        median = vals[mid] if len(vals) % 2 else (vals[mid - 1] + vals[mid]) / 2
        out[band] = {"median_ctr": round(median, 4), "sample": len(vals)}
    return out


def _band_of(position: float) -> str:
    return ("1-3" if position <= 3.5 else "4-10" if position <= 10.5 else
            "11-20" if position <= 20.5 else "21-30" if position <= 30.5 else "31+")


def derive_ctr_gaps(rows: list[dict], curve: dict, min_impressions: float = 100.0,
                    ratio: float = 0.5, limit: int = 50) -> list[dict]:
    """Rows earning materially less than this property earns at that position.

    `ratio` is a fraction of the site's own median for the band, not an absolute
    CTR floor: a fixed "flag anything under 3%" threshold is the same mistake as
    a generic curve, one step further from the data.
    """
    out = []
    for r in rows:
        if r.get("impressions", 0) < min_impressions:
            continue
        band = _band_of(r.get("position", 0))
        ref = curve.get(band)
        if not ref or ref["median_ctr"] <= 0:
            continue  # no baseline for this band on this site — say nothing
        if r.get("ctr", 0.0) < ref["median_ctr"] * ratio:
            out.append({
                "key": r["keys"][0],
                "position": round(r.get("position", 0), 1),
                "band": band,
                "ctr": round(r.get("ctr", 0.0), 4),
                "site_median_ctr_for_band": ref["median_ctr"],
                "impressions": r.get("impressions", 0),
            })
    return sorted(out, key=lambda x: -x["impressions"])[:limit]


def derive_cannibalization(rows: list[dict], min_impressions: float = 100.0,
                           limit: int = 50) -> list[dict]:
    """Queries where several URLs of this site compete for the same demand.

    Needs query+page rows. Reports the incumbent (most clicks) and the rivals, so
    the plan can consolidate toward one URL instead of guessing which page Google
    prefers — intent-and-content.md owns what to do about it.
    """
    by_query: dict[str, list[dict]] = {}
    for r in rows:
        if len(r.get("keys", [])) < 2:
            continue
        by_query.setdefault(r["keys"][0], []).append(
            {"page": r["keys"][1], "clicks": r.get("clicks", 0.0),
             "impressions": r.get("impressions", 0.0),
             "position": round(r.get("position", 0), 1)})
    out = []
    for q, pages in by_query.items():
        if len(pages) < 2:
            continue
        total_impr = sum(p["impressions"] for p in pages)
        if total_impr < min_impressions:
            continue
        pages.sort(key=lambda p: (-p["clicks"], p["position"]))
        out.append({"query": q, "urls": len(pages), "impressions": total_impr,
                    "incumbent": pages[0], "rivals": pages[1:4]})
    return sorted(out, key=lambda x: -x["impressions"])[:limit]


def classify_branded(q: str, brand_terms: list[str]) -> bool:
    ql = q.lower()
    return any(t and t.lower() in ql for t in brand_terms)


def derive_branded_split(rows: list[dict], brand_terms: list[str]) -> dict:
    """Branded vs non-branded demand. Without brand terms this returns None —
    guessing which queries are brand queries would invent the number the split
    exists to measure."""
    if not brand_terms:
        return {"available": False,
                "why": "no --brand-terms given; the split is not inferable from "
                       "query text alone and a guess here would misstate the "
                       "single metric the AEO track leans on"}
    acc = {"branded": {"clicks": 0.0, "impressions": 0.0, "queries": 0},
           "non_branded": {"clicks": 0.0, "impressions": 0.0, "queries": 0}}
    for r in rows:
        k = "branded" if classify_branded(r["keys"][0], brand_terms) else "non_branded"
        acc[k]["clicks"] += r.get("clicks", 0.0)
        acc[k]["impressions"] += r.get("impressions", 0.0)
        acc[k]["queries"] += 1
    total_clicks = acc["branded"]["clicks"] + acc["non_branded"]["clicks"]
    acc["available"] = True
    acc["branded_click_share"] = (round(acc["branded"]["clicks"] / total_clicks, 4)
                                  if total_clicks else None)
    return acc


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
                "after_impressions": round(today), "drop": round(drop, 4),
                # The sensitivity travels with the answer. Silence from a detector
                # whose threshold is never stated reads as "no collapse", and this
                # one only fires on a near-total one.
                "threshold": min_drop, "hold_days": hold_days, "window": window}
    return None


CLIFF_SENSITIVITY = (
    "the detector reports only a drop of >=90% against the previous 7-day mean that "
    "then held for 14 days. A 60% drop that held is real and invisible here — read the "
    "monthly series below yourself before concluding the curve is intact"
)


def iso_days_before(days: int, today: date) -> str:
    return (today - timedelta(days=days)).isoformat()


def is_noise(q: str) -> bool:
    """Scraper and operator noise that should never reach a deliverable."""
    return q.startswith("-site:") or '"' in q or "http" in q


# ── rendering (pure — the text format must show what the json format shows) ───


def render_text(report: dict) -> str:
    """The default format. It used to print six of the ten things it computed.

    `ctr_curve`, `ctr_gaps`, `cannibalization` and `branded_split` were built into
    the report and returned only under `--format json`, while `text` is the default
    and the documented invocation. So an agent running the documented command saw
    no cannibalization section and either reported none or wrote one from nothing —
    and `derive_branded_split`'s refusal to guess never reached anybody.
    """
    n = lambda x: f"{round(x):,}"  # noqa: E731
    out: list[str] = [f"property: {report['site']}"]
    rw, hw = report.get("recent_window", {}), report.get("history_window", {})
    if rw:
        out.append(f"recent window: {rw.get('start')} -> {rw.get('end')}  ·  "
                   f"history: {hw.get('start')} -> {hw.get('end')}")

    if not measured_rows(report):
        out += ["",
                "NOTHING MEASURED — the API answered zero rows for every dimension "
                "(dates, queries, pages, query x page).",
                "  Every section below is empty because there was nothing to derive from, "
                "not because",
                "  this property has no cannibalization and no CTR gaps. Check the property "
                "spelling",
                "  (`sc-domain:example.com` and `https://example.com/` are different "
                "resources) and the",
                "  window: one that predates verification returns nothing. Exit status is 1."]

    ps = report["position_split"]
    out += ["", "position split (recent window) — rank the brief by THIS, not by impressions:"]
    for band, label in (("top20", "<= 20"), ("striking_21_30", "21-30"), ("beyond_30", "> 30")):
        b = ps[band]
        out.append(f"  pos {label:<6} queries={b['queries']:<5} impressions={n(b['impressions']):>9} "
                   f"clicks={b['clicks']:<5} ctr={b['ctr']*100:5.2f}%")

    # What the numbers above do NOT include, stated next to them.
    limits = report.get("row_limits") or {}
    reached = report.get("row_limit_reached") or []
    if reached:
        for dim in reached:
            out.append(f"  ! {dim}: row limit {limits.get(dim, '?')} reached — {ROW_LIMIT_NOTE}")
    dropped = report.get("rows_dropped_as_noise")
    if dropped:
        out.append(f"  ! {dropped} row(s) removed as scraper/operator noise "
                   f"(quoted strings, raw URLs, `-site:`) before every number above")

    cliff = report.get("cliff")
    out.append("")
    if cliff:
        out.append(f"COLLAPSE: {cliff['before']} ({n(cliff['before_impressions'])} imp) -> "
                   f"{cliff['after']} ({n(cliff['after_impressions'])} imp), "
                   f"{cliff['drop']*100:.1f}% and held.")
        out += ["  A cliff that holds is site-level, not an algorithmic update. Check which",
                "  URLs ranked before it and whether they still resolve. Manual Actions and",
                "  Index Coverage are web-UI only — the API cannot clear them."]
    else:
        out.append(f"no collapse detected — sensitivity: {CLIFF_SENSITIVITY}")

    out += ["", "month      clicks  impressions"]
    for m in report["monthly"]:
        out.append(f"  {m['month']}  {n(m['clicks']):>6}  {n(m['impressions']):>11}")

    # ── the four derivations that used to exist only in json ──────────────────
    bs = report.get("branded_split") or {}
    out += ["", "--- branded / non-branded ---"]
    if bs.get("available"):
        share = bs.get("branded_click_share")
        out.append(f"  branded      clicks={n(bs['branded']['clicks']):>7} "
                   f"impressions={n(bs['branded']['impressions']):>9} "
                   f"queries={bs['branded']['queries']}")
        out.append(f"  non-branded  clicks={n(bs['non_branded']['clicks']):>7} "
                   f"impressions={n(bs['non_branded']['impressions']):>9} "
                   f"queries={bs['non_branded']['queries']}")
        out.append(f"  branded share of clicks: "
                   f"{'—' if share is None else f'{share*100:.1f}%'}")
    else:
        out.append(f"  UNAVAILABLE — {bs.get('why', 'no brand terms given')}")
        out.append("  Pass --brand-terms \"brand,brand app\" to measure it. It is not "
                   "estimated here on purpose.")

    curve = report.get("ctr_curve") or {}
    out += ["", "--- this property's own CTR curve (never an industry table) ---"]
    if curve:
        for band in ("1-3", "4-10", "11-20", "21-30", "31+"):
            if band in curve:
                c = curve[band]
                out.append(f"  pos {band:<6} median ctr={c['median_ctr']*100:5.2f}%  "
                           f"(from {c['sample']} rows)")
    else:
        out.append("  no band had enough rows to build a baseline — a curve fitted to a "
                   "handful of rows is a guess with a decimal point, so none is offered")

    gaps = report.get("ctr_gaps") or []
    out += ["", f"--- below this property's own curve ({len(gaps)} row(s)) ---"]
    if not gaps:
        out.append("  none, or no baseline existed for the band (nothing is inferred)")
    for g in gaps[:20]:
        out.append(f"  {n(g['impressions']):>8} imp  pos {g['position']:5.1f}  "
                   f"ctr {g['ctr']*100:5.2f}% vs site median "
                   f"{g['site_median_ctr_for_band']*100:5.2f}%  {str(g['key'])[:60]}")

    cann = report.get("cannibalization") or []
    out += ["", f"--- cannibalization ({len(cann)} query/queries with several URLs) ---"]
    if not cann:
        out.append("  none found in the query x page rows pulled for this window")
    for c in cann[:20]:
        inc = c["incumbent"]
        out.append(f"  \"{str(c['query'])[:48]}\"  {c['urls']} URLs, "
                   f"{n(c['impressions'])} imp")
        out.append(f"      incumbent {inc['page'][:60]} "
                   f"(clicks {n(inc['clicks'])}, pos {inc['position']})")
        for riv in c["rivals"]:
            out.append(f"      rival     {riv['page'][:60]} "
                       f"(clicks {n(riv['clicks'])}, pos {riv['position']})")

    for label, rows_, k in (("top queries", report["top_queries"], 30),
                            ("top pages", report["top_pages"], 30)):
        out += ["", f"--- {label} ---"]
        for r in rows_[:k]:
            out.append(f"  {n(r['clicks']):>6} clicks {n(r['impressions']):>9} imp "
                       f"pos {r['position']:5.1f}  {r['keys'][0][:80]}")

    out += ["", "--- sitemaps ---"]
    sitemaps = report.get("sitemaps") or []
    if not sitemaps:
        out.append("  none submitted")
    for sm in sitemaps:
        c = (sm.get("contents") or [{}])[0]
        out.append(f"  {sm['path']}  submitted={c.get('submitted','-')} "
                   f"errors={sm.get('errors',0)} lastDownloaded={(sm.get('lastDownloaded') or '-')[:19]}")
    out += ["", "Note: the sitemap 'indexed' field reads 0 for every sitemap — Google no longer",
            "populates it. It is not an indexation measurement.",
            "",
            "What this API cannot give you at any scope: Manual Actions, Security Issues and",
            "the Index Coverage report are web-UI only. An unexplained cliff needs a human."]
    return "\n".join(out)


# ── CLI ──────────────────────────────────────────────────────────────────────


def main(argv: list[str]) -> int:
    # argv is a parameter rather than read from `sys.argv` inside, so the producer
    # block records the arguments THIS run was given and a test can hand it a set.
    # The other six scripts already had this shape; only this one read the global.
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--site", help="sc-domain:example.com or https://example.com/")
    ap.add_argument("--quota-project", help="GCP project that meters the API calls")
    ap.add_argument("--days", type=int, default=90, help="recent window (default 90)")
    ap.add_argument("--history-days", type=int, default=480,
                    help="long window for the trend and cliff detector (default 480)")
    ap.add_argument("--list", action="store_true", help="list visible properties and exit")
    ap.add_argument("--brand-terms", default="",
                    help="comma-separated brand terms; without them the branded/"
                         "non-branded split is reported as unavailable rather than guessed")
    ap.add_argument("--format", choices=["text", "json"], default="text")
    args = ap.parse_args(argv)

    token = access_token()
    qp = args.quota_project

    sites = call("/sites", token, qp).get("siteEntry", [])
    if args.list or not args.site:
        for s in sites:
            print(f"  {s.get('permissionLevel','?'):<22} {s['siteUrl']}")
        if not args.site:
            # A usage error, and the docstring has always said usage errors exit 1.
            # It returned 0, so an agent whose invocation lost `--site` read success
            # from output containing nothing but a property list.
            print("\nPass --site to pull a property.", file=sys.stderr)
            return 1
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

    QUERY_LIMIT = PAGE_LIMIT = 5000
    PAIR_LIMIT = 25000
    daily = query(site, token, qp, ["date"], start_hist, end)
    raw_queries = query(site, token, qp, ["query"], start_recent, end, QUERY_LIMIT)
    pages = query(site, token, qp, ["page"], start_recent, end, PAGE_LIMIT)
    raw_pairs = query(site, token, qp, ["query", "page"], start_recent, end, PAIR_LIMIT)
    # Both filters below remove rows before every derived number, so both are
    # counted: a silent filter and a silent cap read the same way in a report.
    queries = [r for r in raw_queries if not is_noise(r["keys"][0])]
    pairs = [r for r in raw_pairs if not is_noise(r["keys"][0])]
    dropped_noise = (len(raw_queries) - len(queries)) + (len(raw_pairs) - len(pairs))
    row_limits = {"query": QUERY_LIMIT, "page": PAGE_LIMIT, "query_page": PAIR_LIMIT}
    limit_reached = [name for name, rows, cap in
                     (("query", raw_queries, QUERY_LIMIT), ("page", pages, PAGE_LIMIT),
                      ("query_page", raw_pairs, PAIR_LIMIT))
                     if len(rows) >= cap]
    sitemaps = call(f"/sites/{urllib.parse.quote(site, safe='')}/sitemaps",
                    token, qp).get("sitemap", [])

    report = {
        "producer": provenance(
            "gsc_pull.py", argv,
            f"property {site} · recent {start_recent}..{end} · history {start_hist}..{end}"),
        "rows_dropped_as_noise": dropped_noise,
        "row_limits": row_limits,
        "row_limit_reached": limit_reached,
        "site": site,
        "recent_window": {"start": start_recent, "end": end},
        "history_window": {"start": start_hist, "end": end},
        "monthly": monthly_rollup(daily),
        "cliff": find_cliff(daily),
        "position_split": position_split(queries),
        "ctr_curve": ctr_curve(queries),
        "ctr_gaps": derive_ctr_gaps(queries, ctr_curve(queries)),
        "cannibalization": derive_cannibalization(pairs),
        "branded_split": derive_branded_split(
            queries, [t.strip() for t in (args.brand_terms or "").split(",") if t.strip()]),
        "top_queries": sorted(queries, key=lambda r: -r["impressions"])[:100],
        "top_pages": sorted(pages, key=lambda r: -r["clicks"])[:100],
        "query_page_pairs": pairs[:5000],
        "sitemaps": sitemaps,
    }

    # One predicate for both formats and for the report itself. Computed before the
    # branch so the two output paths cannot answer the question differently — which
    # is how this script came to have three `return 0`s and no `return 1`.
    rc = 0 if measured_rows(report) else 1

    if args.format == "json":
        json.dump(report, sys.stdout, indent=2)
        print()
        return rc

    print(render_text(report))
    # The producer block reaches the DEFAULT format too. This script is where that
    # rule was learned: four analyses were computed into `report` and printed only
    # under `--format json` while `text` is the documented invocation.
    print("\n" + provenance_md(report["producer"]))
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
