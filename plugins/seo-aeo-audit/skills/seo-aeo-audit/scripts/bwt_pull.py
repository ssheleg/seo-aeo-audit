#!/usr/bin/env python3
"""bwt_pull: Bing Webmaster Tools query and page statistics, as Bing reports them.

Bing is a separate engine with its own index, its own first-party data and its own
verification. An audit that reads only Search Console has no first-party view of
it, which is the gap this script closes for the two reports the Bing Webmaster API
documents for search traffic:

  GetQueryStats   "Get detailed traffic statistics for top queries"
  GetPageStats    "Get detailed traffic statistics for top pages"

Both return rows of Query (the page URL, for GetPageStats), Impressions, Clicks,
AvgImpressionPosition, AvgClickPosition and Date, and Microsoft's reference says of
both: "The data will be updated every week." Rows arrive per date; this script sums
impressions and clicks per key, computes CTR from the sums, and averages position
weighted by impressions, and says so beside every table. Source: the IWebmasterApi
reference on learn.microsoft.com, read 2026-10-19.

**What is not here.** The documented API method list has no method for the AI
Performance report. Export it from the Bing Webmaster Tools interface, keep the
file, record the export date and the column headers exactly as exported, and cite
it as rung-2 evidence (references/tooling.md, the evidence ladder). This script
does not scrape the interface.

**Credentials never touch the command line.** Pipe the API key in on stdin with
`--key-stdin` (sent as the documented `apikey` query parameter, and redacted from
every error this script prints), or an OAuth access token with `--token-stdin`
(sent as `Authorization: Bearer`, the method Microsoft recommends). Exactly one.
A key typed as an argument would land in shell history and in the producer block.

Usage (the first command is whatever prints the secret from your secret manager):
  <print-secret> | bwt_pull.py --site https://example.com/ --key-stdin
  <print-token> | bwt_pull.py --site https://example.com/ --token-stdin \
      --report query --top 50 --format json

Every output carries a **producer block**: `skill` (this tool's version), `script`,
`observed_at` (UTC), `runtime`, `args` (credential values redacted), `scope` (the
resolved input set), and `actor` / `model` / `trace` from `SEO_AEO_AUDIT_ACTOR`,
`_MODEL`, `_TRACE`. It is present in the default output and under `--format json` as
`producer`. A field the harness did not supply reads `unavailable: <VAR> is not set by
this harness`, never guessed, and never dropped, because a field that vanishes when
unavailable is indistinguishable from one nobody checked. `observed_at` is the field
that decides whether a finding has expired; the report's own `## Provenance` block adds
the four invalidators (see references/preflight.md).

Each failed call names its gate, in the vocabulary preflight.py uses: `login` (no
credential, an invalid key, HTTP 401), `scope` (HTTP 403: the credential is valid
and cannot read this site), `network` (no HTTP status), `http` (anything else).

Exit codes: 0 = at least one report returned at least one usable row; 1 = no
credential on stdin, or no report returned a usable row (a run that measured
nothing is not a success); 2 = argparse usage error.
"""
from __future__ import annotations

import argparse
import json
import os
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
SKILL_VERSION = "0.29.0"

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

# Microsoft documents the key form on ssl.bing.com and the OAuth form on www.bing.com
# (Getting Started and OAuth 2.0 pages, read 2026-10-19). Kept apart so a key is
# never sent to a host the documentation does not show it going to.
API_KEY_BASE = "https://ssl.bing.com/webmaster/api.svc/json"
API_TOKEN_BASE = "https://www.bing.com/webmaster/api.svc/json"
REPORTS = {"query": "GetQueryStats", "page": "GetPageStats"}
MAX_RESPONSE_BYTES = 16_000_000

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


def classify(status, body: str) -> str:
    """The gate a failed call hit, in preflight.py's COVERAGE_GATES vocabulary."""
    low = (body or "").lower()
    if not status:
        return "network"
    if status == 401 or "invalidapikey" in low or '"errorcode":3' in low.replace(" ", ""):
        return "login"
    if status == 403:
        return "scope"
    return "http"


def call(method: str, params: dict, auth: tuple[str, str]) -> dict:
    """One documented JSON call. Returns {"rows": [...]} or {"error", "gate", "status"}."""
    kind, secret = auth
    query = dict(params)
    headers = {"Accept": "application/json", "User-Agent": "seo-aeo-audit"}
    if kind == "key":
        query["apikey"] = secret
        url = f"{API_KEY_BASE}/{method}?{urllib.parse.urlencode(query)}"
    else:
        headers["Authorization"] = f"Bearer {secret}"
        url = f"{API_TOKEN_BASE}/{method}?{urllib.parse.urlencode(query)}"
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers),
                                    timeout=60) as resp:
            payload = _transport_json(resp, MAX_RESPONSE_BYTES)
    except urllib.error.HTTPError as exc:
        with exc:
            detail = _transport_error(exc, MAX_RESPONSE_BYTES, secret)
        return {"error": f"HTTP {exc.code}: {_flat(detail, 160)}",
                "gate": classify(exc.code, detail), "status": exc.code}
    except Exception as exc:  # noqa: BLE001 - one failed report must not end the run
        detail = _transport_detail(f"{type(exc).__name__}: {exc}", secret)
        return {"error": _flat(detail, 160), "gate": "network", "status": None}
    rows = payload.get("d") if isinstance(payload, dict) else None
    if not isinstance(rows, list):
        return {"error": "response has no `d` list", "gate": "http", "status": 200}
    return {"rows": rows, "status": 200}


def _date(value) -> str | None:
    """`/Date(1316156400000-0700)/` -> `2011-09-16` (UTC), or None when unreadable."""
    import re
    m = re.match(r"^/Date\((-?\d+)([+-]\d{4})?\)/$", str(value or ""))
    if not m:
        return None
    return time.strftime("%Y-%m-%d", time.gmtime(int(m.group(1)) / 1000))


def _num(value):
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) \
        and value >= 0 else None


def aggregate(rows: list) -> tuple[list[dict], int]:
    """Sum per key across dates. Returns (aggregated rows, malformed row count)."""
    agg: dict[str, dict] = {}
    malformed = 0
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("Query"), str):
            malformed += 1
            continue
        imp, clk = _num(row.get("Impressions")), _num(row.get("Clicks"))
        pos = _num(row.get("AvgImpressionPosition"))
        day = _date(row.get("Date"))
        if imp is None or clk is None:
            malformed += 1
            continue
        a = agg.setdefault(row["Query"], {"key": row["Query"], "impressions": 0, "clicks": 0,
                                          "_pos_weight": 0.0, "_pos_imps": 0, "dates": set()})
        a["impressions"] += imp
        a["clicks"] += clk
        if pos is not None and imp:
            a["_pos_weight"] += pos * imp
            a["_pos_imps"] += imp
        if day:
            a["dates"].add(day)
    out = []
    for a in agg.values():
        dates = sorted(a.pop("dates"))
        w, n = a.pop("_pos_weight"), a.pop("_pos_imps")
        a["ctr"] = round(a["clicks"] / a["impressions"], 4) if a["impressions"] else None
        a["avg_impression_position"] = round(w / n, 1) if n else None
        a["first_date"], a["last_date"] = (dates[0], dates[-1]) if dates else (None, None)
        out.append(a)
    out.sort(key=lambda r: (-r["impressions"], r["key"]))
    return out, malformed


def read_secret(stream) -> str:
    """First line of stdin. A terminal is never waited on: no pipe means no credential."""
    try:
        if stream is None or stream.isatty():
            return ""
    except (AttributeError, ValueError):
        pass
    return (stream.readline() or "").strip()


def render_markdown(site: str, reports: dict, top: int) -> str:
    lines = [f"# Bing Webmaster Tools: {_flat(site, 120)}", "",
             "Impressions and clicks are summed per key across the dates Bing returned; "
             "CTR is computed from the sums; position is impression-weighted. Bing updates "
             "these reports weekly, so the newest week may be missing.", ""]
    for name, rep in reports.items():
        lines.append(f"## {name} ({REPORTS[name]})")
        if "error" in rep:
            lines += [f"- **could not read** (gate: **{rep['gate']}**): {_flat(rep['error'])}", ""]
            continue
        rows = rep["rows"]
        span = [d for r in rows for d in (r["first_date"], r["last_date"]) if d]
        lines.append(f"- {len(rows)} key(s); dates {min(span) if span else 'n/a'} to "
                     f"{max(span) if span else 'n/a'}; {rep['malformed']} malformed row(s) dropped")
        if not rows:
            lines += ["- **NOTHING MEASURED**: the API answered with no usable row.", ""]
            continue
        lines += ["", "| key | impressions | clicks | CTR | avg position |", "|---|---|---|---|---|"]
        for r in rows[:top]:
            ctr = "n/a" if r["ctr"] is None else f"{r['ctr']:.2%}"
            pos = "n/a" if r["avg_impression_position"] is None else r["avg_impression_position"]
            lines.append(f"| {_flat(r['key'], 100)} | {r['impressions']} | {r['clicks']} | {ctr} | {pos} |")
        if len(rows) > top:
            lines.append(f"\n{len(rows) - top} more key(s) not shown; --top or --format json.")
        lines.append("")
    return "\n".join(lines)


def main(argv: list[str], stdin=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--site", required=True, help="site URL as verified in Bing Webmaster Tools")
    cred = ap.add_mutually_exclusive_group(required=True)
    cred.add_argument("--key-stdin", action="store_true", help="read the API key from stdin")
    cred.add_argument("--token-stdin", action="store_true",
                      help="read an OAuth access token from stdin (recommended by Microsoft)")
    ap.add_argument("--report", choices=["query", "page", "both"], default="both")
    ap.add_argument("--top", type=int, default=25, help="rows per table in markdown (default 25)")
    ap.add_argument("--format", choices=["markdown", "json"], default="markdown")
    args = ap.parse_args(argv)

    secret = read_secret(stdin if stdin is not None else sys.stdin)
    names = ["query", "page"] if args.report == "both" else [args.report]
    prov = provenance("bwt_pull.py", argv,
                      f"Bing site {args.site}; report(s) {', '.join(names)}")
    reports: dict[str, dict] = {}
    if not secret:
        for name in names:
            reports[name] = {"error": "no credential on stdin", "gate": "login", "status": None}
    else:
        auth = ("key" if args.key_stdin else "token", secret)
        for name in names:
            res = call(REPORTS[name], {"siteUrl": args.site}, auth)
            if "error" in res:
                reports[name] = res
            else:
                rows, malformed = aggregate(res["rows"])
                reports[name] = {"rows": rows, "malformed": malformed, "raw_rows": len(res["rows"])}
    returned = sum(1 for r in reports.values() if r.get("rows"))
    reasons = []
    failed = [n for n, r in reports.items() if "error" in r]
    empty = [n for n, r in reports.items() if "rows" in r and not r["rows"]]
    if failed:
        reasons.append({"code": "call_failed", "detail": "; ".join(
            f"{n}: gate {reports[n]['gate']}" for n in failed)})
    if empty:
        reasons.append({"code": "empty_report", "detail": ", ".join(empty) + " answered with no usable row"})
    if any(r.get("malformed") for r in reports.values()):
        reasons.append({"code": "malformed_rows",
                        "detail": "some rows lacked numeric impressions or clicks and were dropped"})
    attempted = len(names) if secret else 0
    coverage = collector_coverage(
        "api_report", "Documented Bing Webmaster API reports requested for one site. "
        "Returned means at least one usable row; it does not cover the AI Performance "
        "report (no documented API method) or any engine but Bing.",
        len(names), attempted, returned, len(names) - attempted, reasons)
    if args.format == "json":
        print(json.dumps({"producer": prov, "site": args.site, "reports": reports,
                          "coverage": coverage}, indent=2))
    else:
        print(render_markdown(args.site, reports, max(1, args.top)))
        print("\n" + collector_coverage_md(coverage))
        print("\n" + provenance_md(prov))
    return 0 if returned else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
