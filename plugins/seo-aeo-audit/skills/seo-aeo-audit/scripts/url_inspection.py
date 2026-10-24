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
# Copied verbatim into all nine scripts and compared byte for byte by
# `test/validate.py`, for the same reason `_flat` is: these ship as standalone files
# with no shared module, and an import of one does not exist in the installed layout
# (`bin/seo-aeo-audit.js` copies `scripts/` alone into `~/.claude/skills/`). The
# doctrine behind the field set lives above this block in preflight.py. Never edit
# one copy — the guard fails all nine.
SKILL_VERSION = "0.32.2"

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
            raw = _transport_json(resp, MAX_RESPONSE_BYTES)
            if isinstance(raw, dict) and ("error" in raw or "_error" in raw):
                detail = _transport_detail(raw.get("error", raw.get("_error")), token)
                return {"_error": detail or "provider returned an error envelope"}
            return raw
    except urllib.error.HTTPError as e:
        with e:
            detail = _transport_error(e, MAX_RESPONSE_BYTES, token)
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
        return {"_error": _transport_detail(exc, token)}


MAX_RESPONSE_BYTES = 8_000_000  # raw and decoded JSON response bytes

# An ADC access token lives about an hour; one URL takes a few seconds, so a run of more
# than roughly 600 URLs outlived its token and every later row answered HTTP 401 (issue #56,
# 2026-10-23: rows 524 to 1,681 of 1,682). The token is re-minted before it gets this old,
# and a 401 re-mints once and retries that URL once.
TOKEN_MAX_AGE = 50 * 60


class Tokens:
    """The run's access token, re-minted when it is older than TOKEN_MAX_AGE or on demand."""

    def __init__(self, mint=None, clock=None):
        self._mint = mint or access_token
        self._clock = clock or time.monotonic
        self._token, self._at = None, None

    def get(self) -> str:
        if self._token is None or self._clock() - self._at > TOKEN_MAX_AGE:
            self.refresh()
        return self._token

    def refresh(self) -> str:
        self._token, self._at = self._mint(), self._clock()
        return self._token


def inspect_fresh(site: str, url: str, tokens: Tokens, quota_project: str | None,
                  inspect_fn=None) -> dict:
    """`inspect` with a token that is never stale: on HTTP 401, re-mint once and retry once.
    A re-mint that fails leaves the row's 401 as it was; a second 401 fails the row."""
    call = inspect_fn or inspect
    try:
        token = tokens.get()
    except (SystemExit, OSError, UnicodeError, subprocess.TimeoutExpired):
        return {"_error": "ADC token re-mint failed after it aged out; this URL was not inspected"}
    raw = call(site, url, token, quota_project)
    # A malformed provider payload (a list, a string) is the parser's to report, not a 401.
    if not isinstance(raw, dict) or not str(raw.get("_error", "")).startswith("HTTP 401"):
        return raw
    try:
        token = tokens.refresh()
    except (SystemExit, OSError, UnicodeError, subprocess.TimeoutExpired):
        return raw
    if not isinstance(token, str) or not token.strip():
        return raw
    return call(site, url, token, quota_project)


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


# Schema source and bounded admission policy:
# docs/evidence/plans/2026-10-13-url-inspection-admission.md.
INDEX_ENUMS = {
    "verdict": {"VERDICT_UNSPECIFIED", "PASS", "PARTIAL", "FAIL", "NEUTRAL"},
    "robotsTxtState": {"ROBOTS_TXT_STATE_UNSPECIFIED", "ALLOWED", "DISALLOWED"},
    "indexingState": {"INDEXING_STATE_UNSPECIFIED", "INDEXING_ALLOWED", "BLOCKED_BY_META_TAG", "BLOCKED_BY_HTTP_HEADER", "BLOCKED_BY_ROBOTS_TXT"},
    "pageFetchState": {"PAGE_FETCH_STATE_UNSPECIFIED", "SUCCESSFUL", "SOFT_404", "BLOCKED_ROBOTS_TXT", "NOT_FOUND", "ACCESS_DENIED", "SERVER_ERROR", "REDIRECT_ERROR", "ACCESS_FORBIDDEN", "BLOCKED_4XX", "INTERNAL_CRAWL_ERROR", "INVALID_URL"},
    "crawledAs": {"CRAWLING_USER_AGENT_UNSPECIFIED", "DESKTOP", "MOBILE"},
}
INDEX_FIELDS = {
    "verdict": "verdict", "coverageState": "coverage_state",
    "indexingState": "indexing_state", "robotsTxtState": "robots_txt_state",
    "pageFetchState": "page_fetch_state", "lastCrawlTime": "last_crawl_time",
    "crawledAs": "crawled_as", "googleCanonical": "google_canonical",
    "userCanonical": "user_canonical", "referringUrls": "referring_urls",
    "sitemap": "sitemaps",
}


def _inspection_url(value):
    if not isinstance(value, str) or not value or any(c.isspace() for c in value):
        return False
    try:
        parsed = urllib.parse.urlsplit(value)
        return parsed.scheme in ("http", "https") and bool(parsed.hostname) and (parsed.port is None or 0 < parsed.port < 65536)
    except ValueError:
        return False


def _inspection_timestamp(value):
    import re
    from datetime import datetime
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]{1,9})?Z", value):
        return False
    try:
        datetime.strptime(value[:19], "%Y-%m-%dT%H:%M:%S")
        return True
    except ValueError:
        return False


def parse(raw: dict, url: str) -> dict:
    """Admit typed observations; malformed presence is never valid absence."""
    errors, invalid = [], []
    def problem(path, detail):
        errors.append(path + ": " + detail)
    if isinstance(raw, dict) and "_error" in raw:
        return {"url": url, "error": str(raw["_error"]) or "provider returned an error envelope"}
    if not isinstance(raw, dict):
        problem("response", "expected an object")
        raw = {}
    inspection = raw.get("inspectionResult", {})
    if not isinstance(inspection, dict):
        problem("inspectionResult", "expected an object")
        inspection = {}
    idx = inspection.get("indexStatusResult", {})
    if not isinstance(idx, dict):
        problem("indexStatusResult", "expected an object")
        idx = {}
    result = {"url": url, "has_index_status": False}
    for field, output in INDEX_FIELDS.items():
        result[output] = [] if field in ("referringUrls", "sitemap") else None
        if field not in idx:
            continue
        value = idx[field]
        valid = False
        if field in ("referringUrls", "sitemap"):
            if isinstance(value, list):
                result[output] = [item for item in value if _inspection_url(item)]
                valid = len(result[output]) == len(value)
            if not valid:
                problem("indexStatusResult." + field, "expected an array of absolute HTTP(S) URLs; usable members retained")
        else:
            valid = isinstance(value, str) and bool(value.strip())
            if field in INDEX_ENUMS:
                valid = valid and value in INDEX_ENUMS[field] and not value.endswith("_UNSPECIFIED") and value not in ("PARTIAL", "BLOCKED_BY_ROBOTS_TXT")
            elif field in ("googleCanonical", "userCanonical"):
                valid = _inspection_url(value)
            elif field == "lastCrawlTime":
                valid = _inspection_timestamp(value)
            if valid:
                result[output] = value
            else:
                problem("indexStatusResult." + field, "unavailable: wrong type, invalid value or unspecified/unknown status")
        if not valid:
            invalid.append(field)
    result["has_index_status"] = any(bool(result[output]) for output in INDEX_FIELDS.values())
    rich = inspection.get("richResultsResult", {})
    if not isinstance(rich, dict):
        problem("richResultsResult", "expected an object")
        rich = {}
    verdict = rich.get("verdict")
    result["rich_results_verdict"] = verdict if isinstance(verdict, str) and verdict in INDEX_ENUMS["verdict"] and not verdict.endswith("_UNSPECIFIED") and verdict != "PARTIAL" else None
    if "verdict" in rich and result["rich_results_verdict"] is None:
        problem("richResultsResult.verdict", "unavailable: invalid or unknown status")
    items = rich.get("detectedItems", [])
    if not isinstance(items, list):
        problem("richResultsResult.detectedItems", "expected an array")
        items = []
    result["rich_result_types"] = []
    for item in items:
        name = item.get("richResultType") if isinstance(item, dict) else None
        if isinstance(name, str) and name.strip():
            result["rich_result_types"].append(name)
        else:
            problem("richResultsResult.detectedItems.richResultType", "expected a nonempty string")
    result["payload_errors"] = errors
    result["invalid_index_fields"] = invalid
    return result


# Google documents the coverage states; the verdict field is the engine's own
# summary of them. PASS is indexed; PARTIAL is reserved, not an indexed answer.
# FAIL and NEUTRAL are not indexed, and
# NEUTRAL is where every *exclusion* lands — duplicates, canonical alternates,
# `noindex`, unknown URLs. Substring-matching "not indexed" caught two of those
# and silently passed the rest.
INDEXED_VERDICTS = frozenset({"PASS"})
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
            "the API supplied no usable typed index status, so nothing about this URL's "
            "index state was returned. This is a gap in the report, not a verdict about "
            "the page — re-run it, and check the property and URL match")
        return out
    gc, uc = r.get("google_canonical"), r.get("user_canonical")
    if gc and uc and gc != uc:
        add("blocker", "canonical-disagreement",
            f"Google selected {gc} but the page declares {uc} — the declaration "
            "was not accepted, so signals consolidate somewhere you did not choose")
    invalid = set(r.get("invalid_index_fields", []))
    if uc in (None, "") and gc and "userCanonical" not in invalid:
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
    if not r.get("last_crawl_time") and "lastCrawlTime" not in invalid:
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
        for problem in r.get("payload_errors", []):
            lines.append(f"- **payload limitation**: {_flat(problem)}")
        for f in r.get("findings", []):
            lines.append(f"  - **{f['severity']}** [{f['code']}] {f['message']}")
        lines.append("")
    # The tier belongs to answers that arrived. Printed unconditionally, this line
    # declared a run of 403s to be CONFIRMED evidence — from the one instrument in
    # the skill whose whole justification is that it can legitimately claim the tier.
    answered = answered_rows(rows)
    if answered:
        lines.append(f"Evidence tier: CONFIRMED for the {len(answered)} of {len(rows)} URL(s) "
                     f"the index answered for — scoped to admitted typed fields; rejected sibling fields remain unknown. These are engine answers, not "
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
    if args.max_urls < 1:
        ap.error("--max-urls must be at least 1")

    urls = list(args.urls)
    input_errors = []
    unknown_input = False
    if args.urls_file:
        try:
            with open(args.urls_file, encoding="utf-8") as fh:
                urls += [line for line in (ln.strip() for ln in fh) if line and not line.startswith("#")]
        except (OSError, UnicodeError) as exc:
            unknown_input = True
            input_errors.append({"code": "input_population_unknown", "detail": "Cannot read --urls-file: " + type(exc).__name__})
    seen, deduped = set(), []
    for u in urls:
        if u not in seen:
            seen.add(u)
            deduped.append(u)
    if not deduped and not input_errors:
        input_errors.append({"code": "no_input", "detail": "No URLs resolved; pass --urls and/or --urls-file."})

    dropped = max(0, len(deduped) - args.max_urls)
    batch = deduped[: args.max_urls]
    if dropped:
        print(f"note: {dropped} URL(s) beyond --max-urls={args.max_urls} were not "
              f"inspected", file=sys.stderr)

    tokens, credential_error = Tokens(), None
    if batch:
        try:
            token = tokens.get()
            if not isinstance(token, str) or not token.strip():
                credential_error = "ADC returned no usable token; selected URLs were not attempted."
        except (SystemExit, OSError, UnicodeError, subprocess.TimeoutExpired):
            credential_error = "ADC acquisition unavailable; selected URLs were not attempted. Check local gcloud login."
    rows, attempted = [], 0
    for i, u in enumerate(batch):
        if credential_error:
            rows.append({"url": u, "attempted": False, "error": credential_error, "findings": []})
            continue
        if i:
            time.sleep(MIN_INTERVAL)
        attempted += 1
        row = parse(inspect_fresh(args.site, u, tokens, args.quota_project), u)
        row["findings"] = findings(row)
        rows.append(row)
    excluded = dropped + (len(batch) if credential_error else 0)

    prov = provenance("url_inspection.py", argv,
                      f"property {args.site}, {attempted} URL(s) attempted, {len(batch)} selected: "
                      + ", ".join(batch[:5])
                      + (f" (+{len(batch) - 5} more)" if len(batch) > 5 else ""))
    unanswered = attempted - len(answered_rows(rows))
    reasons = list(input_errors)
    if credential_error:
        reasons.append({"code": "prerequisite_excluded", "detail": credential_error})
    if dropped:
        reasons.append({"code": "input_cap", "detail": f"{dropped} unique URL(s) deliberately omitted by --max-urls."})
    payload_gaps = sum(bool(row.get("payload_errors")) for row in rows)
    if payload_gaps:
        reasons.append({"code": "payload_fields_unavailable", "detail": f"{payload_gaps} URL(s) included invalid/unknown fields; valid siblings were retained, rejected fields support no findings."})
    if unanswered:
        reasons.append({"code": "no_index_answer", "detail": f"{unanswered} attempted URL(s) failed or supplied no index status; see result rows."})
    coverage = collector_coverage(
        "unique_input_url",
        "This invocation's unique requested URLs; returned counts usable typed index-status observations, not completeness of every API field or the property's URL universe.",
        None if unknown_input else len(deduped), attempted, len(answered_rows(rows)), None if unknown_input else excluded, reasons)
    if args.format == "json":
        print(json.dumps({"producer": prov, "site": args.site, "inspected": attempted,
                          "not_inspected": excluded, "results": rows, "coverage": coverage, "input_errors": input_errors}, indent=2))
    else:
        print(render_markdown(rows, dropped))
        print("\n" + collector_coverage_md(coverage))
        print("\n" + provenance_md(prov))
    # The report already says the run supports nothing; the exit status has to say
    # it too. SKILL.md's own invocation redirects stdout to a file, so an agent that
    # branches on the status reads "success" from a page of refusals otherwise.
    return 0 if answered_rows(rows) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
