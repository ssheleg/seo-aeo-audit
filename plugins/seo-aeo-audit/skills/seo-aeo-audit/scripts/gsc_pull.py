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
  gsc_pull.py --list --format json        # explicit one-operation property listing

Freshness: it finds the last date that actually carries data. A tail of missing
days beyond the reporting lag, or a frozen tail repeating one value pair, prints
`report-stale` (JSON `freshness.status`), and a collapse falling inside that window
is withheld (`cliff_withheld`) rather than reported. A stale report does not change
the exit status: the rows it did return are still measured.

What it cannot give you: Manual Actions, Security Issues and the Index Coverage
report are web-UI only, at every scope. An unexplained cliff needs a human to
open that page.

Exit codes: 0 = the API answered rows for at least one dimension, 1 = usage/auth/API
error, or every dimension came back empty. "Ran" is not the useful question here: every
number this script prints below the position split is derived from rows, so a property
that answered nothing renders a full report in which no cliff, no cannibalization and no
CTR gap were found — a document that reads like a clean site and is a measurement of
nothing. Full-report exit status reads `measured_rows`. Explicit --list instead
exits 0 for a typed observed listing, including empty; missing both --site and
--list is usage before credentials or network.

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
import math
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, timedelta


# ── provenance: the execution that produced this payload ── shared block ──────
# Copied verbatim into all nine scripts and compared byte for byte by
# `test/validate.py`, for the same reason `_flat` is: these ship as standalone files
# with no shared module, and an import of one does not exist in the installed layout
# (`bin/seo-aeo-audit.js` copies `scripts/` alone into `~/.claude/skills/`). The
# doctrine behind the field set lives above this block in preflight.py. Never edit
# one copy — the guard fails all nine.
SKILL_VERSION = "0.32.4"

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
        # Flattened here rather than through `_flat`: this shared block must
        # render independently of the collector-specific helper.
        # test/validate.py counts the actual helper homes.
        cell = " ".join(str(v).split()).replace("|", "\\|")
        if len(cell) > 300:
            cell = cell[:299].rstrip() + "…"
        lines.append(f"| {f} | `{cell}` |")
    return "\n".join(lines)
# ── end provenance shared block ──────────────────────────────────────────────


MAX_RESPONSE_BYTES = 8_000_000  # raw and decoded JSON response bytes


# BEGIN BOUNDED TRANSPORT
# Byte-identical in eight standalone collectors; transport_contract checks parity.
# Interpretation (fragment, XML document, provider payload, status) stays local.
def _transport_values(headers, name):
    if hasattr(headers, "get_all"):
        return headers.get_all(name, [])
    return [value for key, value in headers.items() if key.lower() == name.lower()]


def _bounded_gzip(raw, max_bytes, salvage=False):
    import gzip
    import io
    import zlib
    if not raw.startswith(b"\x1f\x8b"):
        return b"", False, "gzip body has no valid member"
    try:
        with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
            decoded = stream.read(max_bytes + 1)
        return decoded[:max_bytes], len(decoded) <= max_bytes, "" if len(decoded) <= max_bytes else "decoded body exceeds byte budget"
    except (OSError, EOFError, zlib.error):
        decoded = b""
        if salvage:
            try:
                decoded = zlib.decompressobj(zlib.MAX_WBITS | 16).decompress(raw, max_bytes + 1)[:max_bytes]
            except zlib.error:
                pass
        return decoded, False, "incomplete or corrupt gzip body"


def _bounded_response(response, max_bytes, *, force_gzip=False, salvage=False):
    """Return bounded decoded bytes, completeness, and non-secret limitations.

    urllib removes supported chunk framing before this read. Length comparison
    is against raw content bytes, before content decompression, not decoded text.
    """
    import http.client
    import re
    raw, errors = b"", []
    try:
        raw = response.read(max_bytes + 1)
    except http.client.IncompleteRead as exc:
        raw = exc.partial[:max_bytes]
        errors.append("incomplete HTTP body")
    except (OSError, ValueError, http.client.HTTPException):
        errors.append("HTTP body read failed")
    headers = getattr(response, "headers", None) or {}
    lengths = [v.strip(" \t") for field in _transport_values(headers, "Content-Length") for v in field.split(",")]
    normalized = [v.lstrip("0") or "0" for v in lengths]
    transfers = [v.strip().lower() for field in _transport_values(headers, "Transfer-Encoding") for v in field.split(",")]
    if lengths and (any(not re.fullmatch(r"[0-9]+", v) for v in lengths) or len(set(normalized)) != 1 or transfers):
        errors.append("ambiguous or malformed HTTP length framing")
    elif normalized:
        observed = str(len(raw))
        if normalized[0] != observed:
            errors.append("incomplete or capped HTTP body")
    if transfers and transfers != ["chunked"]:
        errors.append("unsupported transfer encoding")
    if len(raw) > max_bytes:
        errors.append("raw body exceeds byte budget")
        raw = raw[:max_bytes]
    encodings = [v.strip().lower() for field in _transport_values(headers, "Content-Encoding") for v in field.split(",")]
    if encodings not in ([], ["identity"], ["gzip"]):
        raw = b""
        errors.append("unsupported content encoding")
    elif encodings == ["gzip"] or force_gzip:
        raw, complete, error = _bounded_gzip(raw, max_bytes, salvage)
        if not complete:
            errors.append(error)
    return raw, not errors, "; ".join(dict.fromkeys(errors))


def _transport_detail(value, secret=None, limit=300):
    from urllib.parse import quote, quote_plus
    text = str(value)
    if secret:
        for needle in (secret, quote(secret, safe=""), quote_plus(secret)):
            text = text.replace(needle, "<redacted>")
    return text[:limit]


def _transport_json(response, max_bytes):
    raw, complete, error = _bounded_response(response, max_bytes)
    if not complete:
        raise ValueError(error)
    try:
        return json.loads(raw.decode("utf-8"))
    except RecursionError as exc:
        raise ValueError("JSON nesting exceeds decoder capacity") from exc


def _transport_error(response, max_bytes, secret=None):
    raw, complete, error = _bounded_response(response, max_bytes)
    detail = _transport_detail(raw.decode("utf-8", "replace"), secret)
    return (error + (": " + detail if detail else "")) if not complete else detail
# END BOUNDED TRANSPORT


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


# ── collector coverage shared block ───────────────────────────────────────────
# Kept byte-identical in migrated standalone collectors; test_output_contracts
# compares the copies. docs/contracts/collector-coverage.md owns the semantics.
def collector_coverage(unit, scope, requested, attempted, returned, dropped, reasons):
    """Account one invocation's logical inputs, never redirect/retry attempts.

    A usable return is defined by each collector's scope. None is unknown, not
    zero. This record does not certify a whole site or provider dataset.
    """
    counts = (requested, attempted, returned, dropped)
    if not all(v is None or (type(v) is int and v >= 0) for v in counts):
        raise ValueError("coverage counts must be nonnegative integers or null")
    if not all(isinstance(v, str) and v.strip() for v in (unit, scope)) or not isinstance(reasons, list):
        raise ValueError("coverage needs a unit, scope and reason list")
    if any(not isinstance(r, dict) or not all(isinstance(r.get(k), str) and r[k].strip()
                                            for k in ("code", "detail")) for r in reasons):
        raise ValueError("coverage reasons need code and detail")
    if all(v is not None for v in (requested, attempted, dropped)) and attempted + dropped != requested:
        raise ValueError("coverage attempted + dropped must equal requested")
    if requested is not None and any(v is not None and v > requested for v in (attempted, returned, dropped)):
        raise ValueError("known coverage counts cannot exceed requested")
    if returned is not None and attempted is not None and returned > attempted:
        raise ValueError("coverage returned cannot exceed attempted")
    unknown = any(v is None for v in counts)
    gap = unknown or dropped or (returned != attempted)
    if gap and not reasons:
        raise ValueError("coverage gaps and unknown counts need reasons")
    state = "unknown" if unknown else "partial" if gap or reasons else "complete"
    return {"schema": "collector-coverage/1", "unit": unit, "scope": scope,
            "requested": requested, "attempted": attempted, "returned": returned,
            "dropped": dropped, "state": state, "reasons": reasons}


def collector_coverage_md(record):
    counts = " · ".join(f"{k}={record[k] if record[k] is not None else 'unknown'}"
                         for k in ("requested", "attempted", "returned", "dropped"))
    lines = ["## Collector coverage", "",
             f"State: **{record['state']}** · unit: `{_flat(record['unit'])}` · {counts}",
             "Scope: " + _flat(record["scope"], 500)]
    lines += [f"- `{_flat(r['code'])}`: {_flat(r['detail'])}" for r in record["reasons"]]
    return "\n".join(lines)
# ── end collector coverage shared block ───────────────────────────────────────


API = "https://searchconsole.googleapis.com/webmasters/v3"

# Search Console lags roughly two days. Asking for today returns a partial tail
# that reads as a drop — the easiest way to invent a collapse that is not there.
REPORTING_LAG_DAYS = 2
# The lag is not fixed. Days the window asked for beyond the last date that carries
# data are tolerated up to this many; more is a stale report, not a fall.
STALE_TOLERANCE_DAYS = 1
# A frozen tail repeats one (clicks, impressions) pair. Tiny properties repeat small
# numbers by chance, so only a pair at or above this many impressions, repeated on
# at least FROZEN_MIN_DAYS consecutive final days, counts as frozen.
FROZEN_MIN_IMPRESSIONS = 20
FROZEN_MIN_DAYS = 3


# ── auth ─────────────────────────────────────────────────────────────────────


def access_token() -> str:
    try:
        out = subprocess.run(
            ["gcloud", "auth", "application-default", "print-access-token"],
            capture_output=True, text=True, check=True, timeout=20,
        )
    except FileNotFoundError:
        raise SystemExit("gcloud not found; install the Google Cloud SDK and configure ADC.")
    except subprocess.CalledProcessError:
        raise SystemExit("ADC token acquisition failed; check the local gcloud login. Private stderr withheld.")
    except (subprocess.TimeoutExpired, OSError, UnicodeError):
        raise SystemExit("ADC token acquisition unavailable or timed out; no provider request was made.")
    token = out.stdout.strip()
    if not token:
        raise SystemExit("ADC returned no access token; no provider request was made.")
    return token


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
            return _transport_json(r, MAX_RESPONSE_BYTES)
    except urllib.error.HTTPError as e:
        with e:
            detail = _transport_error(e, MAX_RESPONSE_BYTES, token)
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
    return collection_rows(call(f"/sites/{enc}/searchAnalytics/query", token, quota_project, body), "rows")


ROW_LIMIT_NOTE = (
    "the API reached this request's row limit; whether further rows exist is "
    "unknown. This is one bounded page, not the provider's complete population. "
    "Narrow the window or assess a separate pagination request before extrapolating"
)


def collection_rows(payload, key):
    """A missing collection in a valid API envelope is genuinely empty."""
    if not isinstance(payload, dict) or "error" in payload:
        raise ValueError("unusable API collection envelope")
    rows = payload.get(key, [])
    if not isinstance(rows, list):
        raise ValueError("API collection is not a list: " + key)
    return rows


class CollectionJournal:
    def __init__(self, token, prerequisite_error=None):
        self.token, self.entries, self.errors = token, [], []
        self.prerequisite_error = prerequisite_error

    def request(self, name, operation):
        entry = {"operation": name, "usable_envelope": False, "attempted": not bool(self.prerequisite_error)}
        self.entries.append(entry)
        if self.prerequisite_error:
            self.errors.append({"operation": name, "code": "prerequisite_excluded", "detail": self.prerequisite_error})
            return None
        try:
            rows = operation()
            if not isinstance(rows, list):
                raise ValueError("API collection is not a list")
            entry["usable_envelope"] = True
            return rows
        except (SystemExit, OSError, ValueError, TypeError, KeyError) as exc:
            detail = str(exc)
            for secret in (self.token, urllib.parse.quote(self.token or "", safe="")):
                if secret:
                    detail = detail.replace(secret, "<redacted>")
            self.errors.append({"operation": name, "code": "input_failed", "detail": detail[:200]})
            return None

    def record(self, requested=6):
        reasons = [{"code": "input_failed", "detail": f"{len(self.errors)} collection diagnostics; see collection_errors."}] if self.errors else []
        dropped = sum(not entry["attempted"] for entry in self.entries)
        if dropped:
            reasons.append({"code": "prerequisite_excluded", "detail": f"{dropped} known operations excluded before attempt because ADC was unavailable."})
        scope = ("One explicit property-list operation" if requested == 1 else "Six full-report operations")
        scope += "; a usable typed collection envelope, including empty, is returned. Missing credentials exclude known operations before attempt. Retries and row populations are separate."
        return collector_coverage("api_request", scope, requested,
                                  sum(entry["attempted"] for entry in self.entries), sum(e["usable_envelope"] for e in self.entries), dropped, reasons)


def valid_analytics_row(row, dimensions):
    if not isinstance(row, dict):
        return False
    keys = row.get("keys")
    if not isinstance(keys, list) or len(keys) != len(dimensions) or any(not isinstance(k, str) or not k.strip() for k in keys):
        return False
    if dimensions == ["date"]:
        try:
            if date.fromisoformat(keys[0]).isoformat() != keys[0]:
                return False
        except ValueError:
            return False
    for name in ("clicks", "impressions", "ctr", "position"):
        value = row.get(name)
        if type(value) not in (int, float) or value < 0:
            return False
        try:
            if not math.isfinite(value):
                return False
        except OverflowError:
            return False
    return row["ctr"] <= 1


def observe_rows(name, rows, dimensions, cap, display_limit):
    reasons = [{"code": "provider_population_unknown", "detail": "One bounded Search Analytics page cannot enumerate the provider population, including below the configured cap."}]
    observation = {"received": None, "invalid": None, "noise": None,
                   "analyzed": None, "display_omitted_json": None,
                   "display_omitted_text": None, "row_limit": cap,
                   "envelope": "unavailable" if rows is None else "observed"}
    if rows is None:
        reasons.append({"code": "input_failed", "detail": "No usable row envelope; row counts are unknown."})
        return [], observation, collector_coverage(name + "_row", "Provider row population for this dimension/window; no cross-dimension sum.", None, None, None, None, reasons)
    accepted, invalid, noise = [], 0, 0
    for row in rows:
        if not valid_analytics_row(row, dimensions):
            invalid += 1
        elif "query" in dimensions and is_noise(row["keys"][0]):
            noise += 1
        else:
            accepted.append(row)
    observation.update(received=len(rows), invalid=invalid, noise=noise, analyzed=len(accepted),
                       display_omitted_json=max(0, len(accepted)-display_limit) if display_limit else 0,
                       display_omitted_text=max(0,len(accepted)-30) if name in ("query","page") else None)
    if len(rows) >= cap:
        reasons.append({"code":"row_cap_reached", "detail": ROW_LIMIT_NOTE})
    if invalid:
        reasons.append({"code":"invalid_rows", "detail":f"{invalid} received rows failed shape/finite-value validation and were not analyzed."})
    if noise:
        reasons.append({"code":"noise_filter", "detail":f"{noise} valid noise rows deliberately excluded before analysis attempts."})
    record = collector_coverage(name + "_row", "Single dimension/window provider population is unknown. Attempts are received rows after known noise exclusion; returned are individually usable rows admitted to analysis; derivation errors qualify aggregates separately. Display slices do not drop analysis inputs.", None, len(rows)-noise, len(accepted), noise, reasons)
    return accepted, observation, record


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


def finite_result(value):
    """Derived numeric leaves must be representable even if no operation raised."""
    if isinstance(value, dict):
        return all(finite_result(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return all(finite_result(item) for item in value)
    if type(value) in (int, float):
        try:
            return math.isfinite(value)
        except OverflowError:
            return False
    return True


def finite_sum(values):
    """Refuse unrepresentable aggregate arithmetic without inventing a ceiling."""
    total = sum(values)
    if not math.isfinite(total):
        raise OverflowError("aggregate is not finite")
    return total


def monthly_rollup(rows: list[dict]) -> list[dict]:
    """Group date-keyed rows by calendar month, ascending."""
    acc: dict[str, dict] = {}
    for r in rows:
        m = r["keys"][0][:7]
        a = acc.setdefault(m, {"month": m, "clicks": 0.0, "impressions": 0.0})
        a["clicks"] = finite_sum((a["clicks"], r["clicks"]))
        a["impressions"] = finite_sum((a["impressions"], r["impressions"]))
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
        total_impr = finite_sum(p["impressions"] for p in pages)
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
        acc[k]["clicks"] = finite_sum((acc[k]["clicks"], r.get("clicks", 0.0)))
        acc[k]["impressions"] = finite_sum((acc[k]["impressions"], r.get("impressions", 0.0)))
        acc[k]["queries"] += 1
    total_clicks = finite_sum((acc["branded"]["clicks"], acc["non_branded"]["clicks"]))
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
        imp = finite_sum(r["impressions"] for r in rs)
        clk = finite_sum(r["clicks"] for r in rs)
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
        baseline = finite_sum(r["impressions"] for r in daily[i - window:i]) / window
        if baseline < min_baseline:
            continue
        today = daily[i]["impressions"]
        drop = 1 - (today / baseline if baseline else 1)
        if drop < min_drop:
            continue
        hold = daily[i:i + hold_days]
        if (finite_sum(r["impressions"] for r in hold) / hold_days) > baseline * (1 - min_drop):
            continue
        return {"before": daily[i - 1]["keys"][0], "after": daily[i]["keys"][0],
                "before_impressions": round(daily[i - 1]["impressions"]),
                "after_impressions": round(today), "drop": round(drop, 4),
                # The sensitivity travels with the answer. Silence from a detector
                # whose threshold is never stated reads as "no collapse", and this
                # one only fires on a near-total one.
                "threshold": min_drop, "hold_days": hold_days, "window": window}
    return None


def freshness(rows: list[dict], window_end: str,
              tolerance: int = STALE_TOLERANCE_DAYS) -> dict:
    """Is the tail of the date series data, or a report that stopped moving?

    Two shapes read as a decline and are not one. A **missing tail**: the API omits
    dates it has no data for, so a report that stopped updating simply ends early.
    A **frozen tail**: the same clicks and impressions repeated day after day. Either
    prints `report-stale`, and a decline finding inside the stale window is withheld.
    The API cannot tell a stale report from a real fall to zero; GA4 and server logs
    can, which is the cross-check measurement.md J2 asks for.
    """
    end = date.fromisoformat(window_end)
    daily = sorted((r for r in rows if r.get("impressions", 0) > 0 or r.get("clicks", 0) > 0),
                   key=lambda r: r["keys"][0])
    out = {"status": "fresh", "window_end": window_end, "last_data_date": None,
           "missing_tail_days": None, "frozen_tail_days": 0, "stale_from": None,
           "tolerance_days": tolerance}
    if not daily:
        out.update(status="unavailable", why="no date rows carry data; freshness was not assessed")
        return out
    last = date.fromisoformat(daily[-1]["keys"][0])
    missing = max(0, (end - last).days)
    out.update(last_data_date=last.isoformat(), missing_tail_days=missing)
    pair = lambda r: (r.get("clicks"), r.get("impressions"))  # noqa: E731
    run = 1
    for prev, cur in zip(reversed(daily[:-1]), reversed(daily[1:])):
        if (pair(prev) == pair(cur) and cur.get("impressions", 0) >= FROZEN_MIN_IMPRESSIONS
                and (date.fromisoformat(cur["keys"][0]) - date.fromisoformat(prev["keys"][0])).days == 1):
            run += 1
        else:
            break
    frozen = run if run >= FROZEN_MIN_DAYS else 0
    out["frozen_tail_days"] = frozen
    if missing > tolerance:
        # The last day that carries data is inside the stale window too: a report
        # that stopped mid-day leaves a partial final point, which reads as a drop.
        out.update(status="report-stale", stale_from=last.isoformat(),
                   why=f"the last date carrying data is {last.isoformat()}, {missing} day(s) before "
                       f"the window end {window_end} (tolerance {tolerance})")
    elif frozen:
        first_frozen = date.fromisoformat(daily[-frozen]["keys"][0])
        out.update(status="report-stale", stale_from=first_frozen.isoformat(),
                   why=f"the last {frozen} dates repeat one value pair {pair(daily[-1])}: a frozen report")
    return out


def withhold_stale_decline(cliff: dict | None, fresh: dict) -> tuple[dict | None, dict | None]:
    """A decline whose fall lands in a stale tail is not a finding yet."""
    if not cliff or fresh.get("status") != "report-stale" or not fresh.get("stale_from"):
        return cliff, None
    if cliff["after"] >= fresh["stale_from"] or cliff["before"] >= fresh["stale_from"]:
        return None, cliff
    return cliff, None


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
                "NOTHING MEASURED — no usable rows were observed for any dimension "
                "(dates, queries, pages, query x page).",
                "  Every section below is empty because there was nothing to derive from, "
                "not because",
                "  this property has no cannibalization and no CTR gaps. Check the property "
                "spelling",
                "  (`sc-domain:example.com` and `https://example.com/` are different "
                "resources) and the",
                "  window: one that predates verification returns nothing. Exit status is 1."]

    failed_derivations = {entry["operation"] for entry in report.get("derivation_errors", [])}
    for entry in report.get("derivation_errors", []):
        out.append(f"UNAVAILABLE {entry['operation']}: {_flat(entry['detail'])}")
    observations = report.get("row_observations", {})
    unavailable = lambda name: name in observations and not observations[name].get("analyzed")
    for name, obs in observations.items():
        out.append(f"{name}: envelope={obs['envelope']}; received={obs['received']}; invalid={obs['invalid']}; noise={obs['noise']}; analyzed={obs['analyzed']}; display omitted JSON/text={obs['display_omitted_json']}/{obs['display_omitted_text']}")
    for error in report.get("collection_errors", []):
        out.append(f"UNAVAILABLE {error['operation']}: {_flat(error['detail'])}")
    ps = report["position_split"]
    out += ["", "position split (recent window) — rank the brief by THIS, not by impressions:"]
    for band, label in (("top20", "<= 20"), ("striking_21_30", "21-30"), ("beyond_30", "> 30")):
        if unavailable("query") or ps is None:
            out.append("  UNAVAILABLE — query inputs or aggregate computation unavailable; zero buckets are not measured negatives")
            break
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

    fresh = report.get("freshness") or {}
    if fresh.get("status") == "report-stale":
        out += ["", f"report-stale: {fresh.get('why')}.",
                f"  No decline finding is drawn for {fresh.get('stale_from')} -> {fresh.get('window_end')} "
                "until the report moves again;",
                "  the API cannot tell a stale report from a real fall to zero. Cross-check GA4 and "
                "server logs (measurement.md J2)."]
        withheld = report.get("cliff_withheld")
        if withheld:
            out.append(f"  WITHHELD: a collapse {withheld['before']} -> {withheld['after']} falls in that "
                       "window and is not reported as one.")
    elif fresh.get("status") == "fresh":
        out += ["", f"freshness: last date with data {fresh.get('last_data_date')}, window end "
                f"{fresh.get('window_end')}, fresh within {fresh.get('tolerance_days')} day(s)"]
    elif fresh:
        out += ["", f"freshness: UNAVAILABLE: {fresh.get('why')}"]
    cliff = report.get("cliff")
    out.append("")
    if cliff:
        out.append(f"COLLAPSE: {cliff['before']} ({n(cliff['before_impressions'])} imp) -> "
                   f"{cliff['after']} ({n(cliff['after_impressions'])} imp), "
                   f"{cliff['drop']*100:.1f}% and held.")
        out += ["  A cliff that holds is site-level, not an algorithmic update. Check which",
                "  URLs ranked before it and whether they still resolve. Manual Actions and",
                "  Index Coverage are web-UI only — the API cannot clear them."]
    elif report.get("cliff_withheld"):
        out.append("collapse NOT ASSESSED for the stale window: withheld while the report is stale (report-stale above)")
    elif unavailable("date") or "cliff" in failed_derivations:
        out.append("UNAVAILABLE — date inputs or aggregate computation unavailable; collapse was not assessed")
    else:
        out.append(f"no collapse detected — sensitivity: {CLIFF_SENSITIVITY}")

    out += ["", "month      clicks  impressions"]
    for m in report["monthly"] or []:
        out.append(f"  {m['month']}  {n(m['clicks']):>6}  {n(m['impressions']):>11}")

    # ── the four derivations that used to exist only in json ──────────────────
    bs = report.get("branded_split") or ({"why":"aggregate computation failed; see derivation_errors"} if "branded_split" in failed_derivations else {})
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
        if "branded_split" not in failed_derivations:
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
        out.append("  UNAVAILABLE — no usable query x page rows" if unavailable("query_page") or "cannibalization" in failed_derivations else "  none found in the query x page rows pulled for this window")
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
        out.append("  UNAVAILABLE — sitemap listing incomplete or failed" if report.get("sitemaps_observed") is False else "  none submitted")
    for sm in sitemaps:
        c = (sm.get("contents") or [{}])[0]
        out.append(f"  {sm['path']}  submitted={c.get('submitted','-')} "
                   f"errors={sm.get('errors',0)} lastDownloaded={(sm.get('lastDownloaded') or '-')[:19]}")
    out += ["", "Note: the sitemap 'indexed' field reads 0 for every sitemap — Google no longer",
            "populates it. It is not an indexation measurement.",
            "",
            "What this API cannot give you at any scope: Manual Actions, Security Issues and",
            "the Index Coverage report are web-UI only. An unexplained cliff needs a human."]
    for record in report.get("coverage_by_unit", {}).values():
        out += ["", collector_coverage_md(record)]
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

    try:
        if args.days <= 0 or args.history_days <= 0:
            raise ValueError("day windows must be positive")
        today = date.today()
        end = iso_days_before(REPORTING_LAG_DAYS, today)
        start_recent = iso_days_before(REPORTING_LAG_DAYS + args.days, today)
        start_hist = iso_days_before(REPORTING_LAG_DAYS + args.history_days, today)
    except (ValueError, OverflowError):
        ap.error("day windows must be positive and fit supported calendar dates")
    if not args.site and not args.list:
        print("Pass --site to pull a property, or explicit --list to list properties.", file=sys.stderr)
        return 1
    token, credential_error = None, None
    try:
        token = access_token()
        if not isinstance(token, str) or not token.strip():
            credential_error = "ADC returned no usable token; provider operations were not attempted."
    except (SystemExit, OSError, UnicodeError, subprocess.TimeoutExpired):
        credential_error = "ADC acquisition unavailable; provider operations were not attempted. Check local gcloud login."
    qp = args.quota_project
    journal = CollectionJournal(token, credential_error)
    if args.list:
        listed = journal.request("properties", lambda: collection_rows(call("/sites", token, qp), "siteEntry"))
        sites = [row for row in listed or [] if isinstance(row, dict) and isinstance(row.get("siteUrl"), str) and row["siteUrl"].strip() and (row.get("permissionLevel") is None or isinstance(row["permissionLevel"], str))]
        observed = listed is not None and len(sites) == len(listed)
        if listed is not None and not observed:
            journal.errors.append({"operation": "properties", "code": "invalid_rows", "detail": "Invalid property rows excluded; valid siblings retained. Membership is incomplete."})
        record = journal.record(1)
        prov = provenance("gsc_pull.py", argv, "Explicit property-list mode; no analytics or sitemap population requested.")
        if args.format == "json":
            print(json.dumps({"producer": prov, "mode": "list", "sites": sites, "properties_observed": observed,
                              "coverage_by_unit": {"api_request": record}, "collection_errors": journal.errors,
                              "api_operations": journal.entries}, indent=2))
        else:
            print("Visible properties" if observed else "Property listing incomplete or unavailable")
            for row in sites:
                print(f"  {_flat(row.get('permissionLevel') or '?'):<22} {_flat(row['siteUrl'])}")
            print("\n" + collector_coverage_md(record))
            print("\n" + provenance_md(prov))
        return 0 if observed or sites else 1

    site = args.site
    sites = journal.request("properties", lambda: collection_rows(call("/sites", token, qp), "siteEntry"))
    properties_observed = sites is not None and all(isinstance(s, dict) and isinstance(s.get("siteUrl"), str) for s in sites)
    if sites is not None and not properties_observed:
        journal.errors.append({"operation":"properties", "code":"invalid_rows", "detail":"Property list contains invalid entries; membership was not determined."})
    if properties_observed and not any(s["siteUrl"] == site for s in sites):
        print(f"warning: {site} is not in this account's returned property list.", file=sys.stderr)

    row_limits = {"date":25000, "query":5000, "page":5000, "query_page":25000}
    dimensions = {"date":["date"], "query":["query"], "page":["page"], "query_page":["query","page"]}
    coverage, observations, analyzed = {}, {}, {}
    for name, dims in dimensions.items():
        rows = journal.request(name, lambda dims=dims, name=name: query(site, token, qp, dims, start_hist if name=="date" else start_recent, end, row_limits[name]))
        accepted, observed, record = observe_rows(name, rows, dims, row_limits[name], {"query":100,"page":100,"query_page":5000}.get(name))
        record["scope"] += f" Property {site}; {start_hist if name=='date' else start_recent}..{end}; dimensions {','.join(dims)}."
        analyzed[name], observations[name], coverage[record["unit"]] = accepted, observed, record
    daily, queries, pages, pairs = (analyzed[name] for name in dimensions)
    noise_counts = [observations[name]["noise"] for name in ("query","query_page")]
    dropped_noise = sum(noise_counts) if all(n is not None for n in noise_counts) else None
    limit_reached = [name for name in dimensions if observations[name]["received"] is not None and observations[name]["received"] >= row_limits[name]]
    sitemaps = journal.request("sitemaps", lambda: collection_rows(call(f"/sites/{urllib.parse.quote(site, safe='')}/sitemaps", token, qp), "sitemap"))
    valid_sitemaps = []
    for item in sitemaps or []:
        contents = item.get("contents") if isinstance(item,dict) else None
        if not isinstance(item,dict) or not isinstance(item.get("path"),str) or (contents is not None and (not isinstance(contents,list) or any(not isinstance(c,dict) for c in contents))) or (item.get("lastDownloaded") is not None and not isinstance(item["lastDownloaded"],str)):
            journal.errors.append({"operation":"sitemaps", "code":"invalid_rows", "detail":"Sitemap entry failed shape validation; valid siblings retained."})
        else:
            valid_sitemaps.append(item)
    coverage["api_request"] = journal.record()

    derivation_errors = []
    def derive(name, dimension, operation):
        try:
            value = operation()
            if not finite_result(value):
                raise ValueError("derived result contains a nonfinite numeric value")
            return value
        except (ArithmeticError, ValueError):
            detail = "Aggregate could not be represented; individually usable rows remain observed."
            derivation_errors.append({"operation": name, "dimension": dimension, "code": "derivation_failed", "detail": detail})
            observations[dimension].setdefault("derivation_errors", []).append(name)
            coverage[dimension + "_row"]["reasons"].append({"code": "derivation_failed", "detail": name + ": " + detail})
            return None
    derived = {}
    for name, dimension, operation in (
        ("monthly", "date", lambda: monthly_rollup(daily)),
        ("cliff", "date", lambda: find_cliff(daily)),
        ("position_split", "query", lambda: position_split(queries)),
        ("ctr_curve", "query", lambda: ctr_curve(queries)),
        ("ctr_gaps", "query", lambda: derive_ctr_gaps(queries, derived["ctr_curve"] or {})),
        ("cannibalization", "query_page", lambda: derive_cannibalization(pairs)),
        ("branded_split", "query", lambda: derive_branded_split(queries, [t.strip() for t in (args.brand_terms or "").split(",") if t.strip()])),
    ):
        derived[name] = derive(name, dimension, operation)
    fresh = freshness(daily, end) if observations["date"].get("analyzed") is not None else {
        "status": "unavailable", "window_end": end, "why": "date rows unavailable; freshness was not assessed"}
    derived["cliff"], cliff_withheld = withhold_stale_decline(derived.get("cliff"), fresh)

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
        **derived,
        "freshness": fresh,
        "cliff_withheld": cliff_withheld,
        "derivation_errors": derivation_errors,
        "top_queries": sorted(queries, key=lambda r: -r["impressions"])[:100],
        "top_pages": sorted(pages, key=lambda r: -r["clicks"])[:100],
        "query_page_pairs": pairs[:5000],
        "sitemaps": valid_sitemaps,
        "sitemaps_observed": sitemaps is not None and len(valid_sitemaps) == len(sitemaps),
        "properties_observed": properties_observed,
        "coverage_by_unit": coverage,
        "row_observations": observations,
        "collection_errors": journal.errors,
        "api_operations": journal.entries,
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
