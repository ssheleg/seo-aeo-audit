#!/usr/bin/env python3
"""sitemap_audit — what the site declares, clustered into the templates it ships.

SKILL.md step 1 asks for indexed vs published URL counts **per template**. The
indexed half comes from Search Console; this is the published half, and until now
it needed a desktop crawler. Sitemaps are the site's own declaration of what it
wants indexed, which makes them the cheapest honest inventory available.

What it does: follows sitemap indexes, clusters URLs into path patterns (the
template families a site actually ships, derived from its URLs rather than
guessed from a list), and reports depth distribution and duplicate paths.

Per listed URL, on request (`--sample N`, bounded at 500): one GET each, redirects
not followed, reporting status, redirect target, `noindex` (meta robots or
`X-Robots-Tag`) and a canonical that names another URL. Google will attempt to crawl
sitemap URLs exactly as listed, so each of those contradicts the sitemap. A sampled
URL that could not be fetched is reported as unfetched and supports no finding. It
also flags an index listed by another index (Search Console: "Nested sitemap
indexes"), a batch-stamped `lastmod` (at least 10 entries with one, and one value on
at least 90% of them), and, with `--robots`, every `Sitemap:` line in robots.txt
that does not answer 200.

What it deliberately does NOT do: **orphan detection**. A sitemap contains no
link graph, so nothing in it can establish that a page has no inbound internal
links. Tools that report "orphan candidates" from a sitemap are inferring from
path shape; that is a guess wearing the clothes of a finding, and it fails
non-negotiable #1. Orphans need a crawl — architecture-and-equity.md says how.

stdlib only, no auth. Reads a URL or a local file.

Usage:
  sitemap_audit.py --url https://example.com/sitemap.xml
  sitemap_audit.py --file sitemap.xml --format json
  sitemap_audit.py --url https://example.com/sitemap_index.xml --max-maps 20
  sitemap_audit.py --robots https://example.com/robots.txt --sample 40

Every output carries a **producer block** — `skill` (this tool's version), `script`,
`observed_at` (UTC), `runtime`, `args` (credential values redacted), `scope` (the
resolved input set), and `actor` / `model` / `trace` from `SEO_AEO_AUDIT_ACTOR`,
`_MODEL`, `_TRACE`. It is present in the default output and under `--format json` as
`producer`. A field the harness did not supply reads `unavailable: <VAR> is not set by
this harness` — never guessed, and never dropped, because a field that vanishes when
unavailable is indistinguishable from one nobody checked. `observed_at` is the field
that decides whether a finding has expired; the report's own `## Provenance` block adds
the four invalidators (see references/preflight.md).

Exit codes: 0 = analyzed page URLs, 1 = fetch/parse error (a sitemap document, or
the robots.txt passed with --robots) or no page URLs, 2 = invalid arguments. A
sampled page URL that fails to fetch does not change the exit status; it is counted
in `sample_coverage`. Attempted collection emits a report even on exit 1.
"""
from __future__ import annotations

import argparse
import gzip
import io
import http.client
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import zlib
from collections import Counter, deque
from html.parser import HTMLParser
from urllib.parse import urlparse


# ── provenance: the execution that produced this payload ── shared block ──────
# Copied verbatim into all seven scripts and compared byte for byte by
# `test/validate.py`, for the same reason `_flat` is: these ship as standalone files
# with no shared module, and an import of one does not exist in the installed layout
# (`bin/seo-aeo-audit.js` copies `scripts/` alone into `~/.claude/skills/`). The
# doctrine behind the field set lives above this block in preflight.py. Never edit
# one copy — the guard fails all seven.
SKILL_VERSION = "0.28.0"

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


# BEGIN BOUNDED TRANSPORT
# Byte-identical in seven standalone collectors; transport_contract checks parity.
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

UA = "seo-aeo-audit/sitemap_audit (+https://github.com/ssheleg/seo-aeo-audit)"
# A sitemap file may hold 50,000 URLs and 50 MB uncompressed (sitemaps.org).
MAX_URLS_PER_MAP = 50000
MAX_BYTES_PER_MAP = 52_428_800

_NUM = re.compile(r"^\d+$")
_SLUGGY = re.compile(r"^[a-z0-9]+(?:[-_][a-z0-9]+){1,}$")


class IncompleteBody(ValueError):
    """Transport or decompression did not provide a complete document."""


def decode_body(raw: bytes, zipped: bool) -> str:
    if len(raw) > MAX_BYTES_PER_MAP:
        raise IncompleteBody("raw body exceeds the byte budget")
    if zipped:
        raw, complete, error = _bounded_gzip(raw, MAX_BYTES_PER_MAP)
        if not complete:
            raise IncompleteBody(error)
    return raw.decode("utf-8", "replace")


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA,
                                               "Accept-Encoding": "gzip"})
    with urllib.request.urlopen(req, timeout=45) as resp:
        raw, complete, error = _bounded_response(resp, MAX_BYTES_PER_MAP,
                                                force_gzip=urlparse(url).path.endswith(".gz"))
    if not complete:
        raise IncompleteBody(error)
    try:
        return raw.decode("utf-8")
    except UnicodeError as exc:
        raise IncompleteBody("invalid UTF-8 document") from exc


# ── per-URL checks: what the sitemap promises against what each URL serves ─────
# Google will attempt to crawl sitemap URLs exactly as listed, so a listed URL that
# redirects, errors, carries noindex or canonicalises elsewhere contradicts the
# sitemap (references/technical-checks.md, Sitemap protocol). A bounded sample is
# fetched, one GET each, redirects NOT followed: the redirect is the observation.
SAMPLE_MAX = 500
SAMPLE_BODY_BYTES = 1_048_576
# A batch stamp: at least this many entries carry lastmod, and one value covers at
# least this share of them. Below the floor nothing is claimed either way.
LASTMOD_BATCH_MIN = 10
LASTMOD_BATCH_SHARE = 0.9


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class _HeadSignals(HTMLParser):
    """Robots meta and canonical link, read from the served HTML only."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.robots: list[str] = []
        self.canonicals: list[str] = []

    def handle_starttag(self, tag, attrs):
        a = {k.lower(): (v or "") for k, v in attrs}
        if tag == "meta" and a.get("name", "").strip().lower() in ("robots", "googlebot"):
            self.robots.append(a.get("content", ""))
        elif tag == "link" and "canonical" in a.get("rel", "").lower().split() and a.get("href"):
            self.canonicals.append(a["href"].strip())


def _has_noindex(value: str) -> bool:
    # "googlebot: noindex" and "noindex, nofollow" both count; "none" means noindex too.
    tokens = re.split(r"[\s,:]+", value.lower())
    return "noindex" in tokens or "none" in tokens


def _canonical_from_link_header(values: list[str]) -> str | None:
    for value in values:
        for part in value.split(","):
            m = re.match(r"\s*<([^>]+)>\s*;(.*)$", part)
            if m and re.search(r"rel\s*=\s*\"?[^\";]*\bcanonical\b", m.group(2), re.I):
                return m.group(1).strip()
    return None


def _same_url(a: str, b: str) -> bool:
    """Equal after scheme/host case and default ports; path, query and slash count."""
    def norm(u):
        p = urlparse(u)
        host = (p.hostname or "").lower()
        port = p.port
        if port and not ((p.scheme == "http" and port == 80) or (p.scheme == "https" and port == 443)):
            host += f":{port}"
        return (p.scheme.lower(), host, p.path or "/", p.query)
    try:
        return norm(a) == norm(b)
    except ValueError:
        return False


def check_url(url: str, timeout: float = 20) -> dict:
    """One GET of a listed URL. A transport failure is an `error`, never a status."""
    obs = {"url": url, "status": None, "location": None, "noindex": None,
           "canonical": None, "foreign_canonical": None, "body_complete": None, "error": None}
    if urlparse(url).scheme not in ("http", "https"):
        obs["error"] = "not an http(s) URL"
        return obs
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "gzip"})
    opener = urllib.request.build_opener(_NoRedirect)
    try:
        resp = opener.open(req, timeout=timeout)
    except urllib.error.HTTPError as exc:
        resp = exc
    except (urllib.error.URLError, OSError, http.client.HTTPException, ValueError) as exc:
        obs["error"] = _flat(str(exc))
        return obs
    with resp:
        status = getattr(resp, "code", None)
        obs["status"] = status
        headers = resp.headers
        if status is not None and 300 <= status < 400:
            obs["location"] = urllib.parse.urljoin(url, headers.get("Location") or "") or None
            return obs
        if status != 200:
            return obs
        robots = list(_transport_values(headers, "X-Robots-Tag"))
        canonical = _canonical_from_link_header(list(_transport_values(headers, "Link")))
        if "html" in (headers.get("Content-Type") or "").lower():
            raw, complete, _ = _bounded_response(resp, SAMPLE_BODY_BYTES, salvage=True)
            obs["body_complete"] = complete
            parser = _HeadSignals()
            try:
                parser.feed(raw.decode("utf-8", "replace"))
            except (AssertionError, ValueError):
                pass
            robots += parser.robots
            canonical = canonical or (parser.canonicals[0] if parser.canonicals else None)
        obs["noindex"] = any(_has_noindex(v) for v in robots)
        if canonical:
            obs["canonical"] = urllib.parse.urljoin(url, canonical)
            obs["foreign_canonical"] = not _same_url(obs["canonical"], url)
        else:
            obs["foreign_canonical"] = False
    return obs


def pick_sample(urls: list[str], n: int) -> list[str]:
    """Up to n URLs, spread round-robin across template families, deterministic."""
    groups: dict[str, list[str]] = {}
    for u in dict.fromkeys(urls):
        groups.setdefault(path_pattern(u), []).append(u)
    queues = [deque(v) for v in groups.values()]
    out: list[str] = []
    while queues and len(out) < n:
        for q in list(queues):
            if len(out) >= n:
                break
            out.append(q.popleft())
            if not q:
                queues.remove(q)
    return out


def lastmod_profile(stamps: list[str]) -> dict:
    present = [s for s in stamps if s]
    top, top_n = (Counter(present).most_common(1)[0] if present else ("", 0))
    share = (top_n / len(present)) if present else None
    return {"entries": len(stamps), "with_lastmod": len(present),
            "distinct": len(set(present)), "most_common": top or None,
            "most_common_share": round(share, 4) if share is not None else None,
            "batch_stamped": bool(len(present) >= LASTMOD_BATCH_MIN
                                  and share is not None and share >= LASTMOD_BATCH_SHARE)}


def robots_sitemaps(text: str) -> list[str]:
    """The `Sitemap:` lines of a robots.txt, in order, deduplicated."""
    out = []
    for line in text.splitlines():
        m = re.match(r"\s*sitemap\s*:\s*(\S+)", line.split("#", 1)[0], re.I)
        if m:
            out.append(m.group(1))
    return list(dict.fromkeys(out))

def parse_sitemap(text: str, lastmods: list | None = None) -> tuple[list[str], list[str], int]:
    """Returns (page urls, nested sitemap urls, urls dropped by the cap).

    Pass a list as `lastmods` to collect each page entry's `<lastmod>` text in the
    same pass ("" where the entry carries none), capped like the pages.

    Namespace-agnostic. Walks the CONTAINERS (`<url>`, `<sitemap>`) and reads
    each one's own `<loc>` child, which is O(n). Locating each `<loc>`'s parent
    by rescanning the tree instead is O(n^2), and at the 50,000 URLs the sitemap
    spec permits that took minutes per file — a tool advertising a size it
    cannot serve.
    """
    pages: list[str] = []
    maps: list[str] = []
    try:
        root = ET.fromstring(text)
    except ET.ParseError as e:
        raise ValueError(f"not parseable XML: {e}") from e
    for container in root.iter():
        kind = container.tag.rsplit("}", 1)[-1]
        if kind not in ("url", "sitemap"):
            continue
        for child in container:
            if child.tag.rsplit("}", 1)[-1] != "loc":
                continue
            loc = (child.text or "").strip()
            if loc:
                (maps if kind == "sitemap" else pages).append(loc)
                if kind == "url" and lastmods is not None and len(pages) <= MAX_URLS_PER_MAP:
                    stamp = ""
                    for sibling in container:
                        if sibling.tag.rsplit("}", 1)[-1] == "lastmod":
                            stamp = (sibling.text or "").strip()
                            break
                    lastmods.append(stamp)
            break
    dropped = max(0, len(pages) - MAX_URLS_PER_MAP)
    return pages[:MAX_URLS_PER_MAP], maps, dropped


def path_pattern(url: str) -> str:
    """Collapse a URL path into the template family it belongs to.

    Numeric and slug-shaped segments become placeholders, so /blog/my-post/ and
    /blog/another-post/ land in one pattern while /blog/ and /pricing/ stay
    apart. The families come out of the site's own URLs — no taxonomy is assumed.
    """
    parts = [p for p in urlparse(url).path.split("/") if p]
    if not parts:
        return "/"
    out = []
    for i, seg in enumerate(parts):
        s = seg.lower()
        if _NUM.match(s):
            out.append("{n}")
        elif i > 0 and (_SLUGGY.match(s) or len(s) > 24):
            out.append("{slug}")
        else:
            out.append(s)
    return "/" + "/".join(out) + "/"


def depth(url: str) -> int:
    return len([p for p in urlparse(url).path.split("/") if p])


def analyze(urls: list[str]) -> dict:
    patterns = Counter(path_pattern(u) for u in urls)
    depths = Counter(depth(u) for u in urls)
    paths = Counter(urlparse(u).path for u in urls)
    dupes = {p: c for p, c in paths.items() if c > 1}
    hosts = Counter(urlparse(u).netloc for u in urls)
    return {
        "urls_total": len(urls),
        "hosts": dict(hosts),
        "templates": [{"pattern": p, "urls": c} for p, c in patterns.most_common()],
        "depth_distribution": {str(k): depths[k] for k in sorted(depths)},
        "duplicate_paths": dupes,
        "not_derivable_here": (
            "orphan pages, click depth from the homepage, and internal-link counts "
            "are NOT in a sitemap — it carries no link graph. Get them from a crawl "
            "(architecture-and-equity.md); do not infer them from path shape"
        ),
    }


def findings(a: dict) -> list[dict]:
    out: list[dict] = []

    def add(sev, code, msg):
        out.append({"severity": sev, "code": code, "message": msg})

    if a["duplicate_paths"]:
        first = list(a["duplicate_paths"])[:3]
        add("medium", "sitemap-duplicate-paths",
            f"{len(a['duplicate_paths'])} path(s) listed more than once, e.g. {first}")
    if len(a["hosts"]) > 1:
        add("high", "sitemap-mixed-hosts",
            f"URLs span several hosts {list(a['hosts'])} — a sitemap should list one "
            "host, and a mismatch usually means http/https or www variants are mixed")
    deep = sum(c for d, c in a["depth_distribution"].items() if int(d) >= 5)
    if deep and a["urls_total"]:
        share = deep / a["urls_total"]
        if share > 0.3:
            add("medium", "sitemap-deep-paths",
                f"{share:.0%} of declared URLs sit at path depth 5+ — check that the "
                "money templates are not among them (path depth is not click depth; "
                "confirm with a crawl)")
    for index_url in a.get("nested_indexes") or []:
        add("high", "sitemap-nested-index",
            f"{index_url} is a sitemap index listed by another index. A sitemap index file "
            "can't list other sitemap index files, only sitemap files (Search Console: "
            "\"Nested sitemap indexes\"); list its children in the top index instead")
    lm = a.get("lastmod") or {}
    if lm.get("batch_stamped"):
        add("medium", "sitemap-lastmod-batch",
            f"{lm['most_common_share']:.0%} of {lm['with_lastmod']} entries carrying lastmod share "
            f"one value ({lm['most_common']}), a deploy or build stamp, not a content date. "
            "Google uses lastmod only if it is consistently and verifiably accurate; open "
            "the generator before calling it a defect (it may be a decision)")
    for probe in a.get("robots_sitemaps") or []:
        if probe.get("status") is not None and probe["status"] != 200:
            where = f" -> {probe['location']}" if probe.get("location") else ""
            add("high", "sitemap-robots-unserved",
                f"robots.txt declares {probe['url']}, which answers HTTP {probe['status']}{where} "
                "instead of serving the sitemap")
    checks = [c for c in (a.get("url_checks") or []) if c.get("status") is not None]
    if checks:
        n = len(checks)
        def report(sev, code, rows, what):
            if rows:
                ex = "; ".join(rows[:3])
                add(sev, code, f"{len(rows)} of {n} sampled listed URL(s) {what}, e.g. {ex}. "
                    "A listed URL is a promise that it is canonical, indexable and serves 200")
        report("medium", "sitemap-url-redirects",
               [f"{c['url']} -> {c['location'] or '?'} ({c['status']})" for c in checks
                if 300 <= c["status"] < 400], "redirect")
        report("high", "sitemap-url-error-status",
               [f"{c['url']} ({c['status']})" for c in checks
                if c["status"] >= 400 or (c["status"] < 300 and c["status"] != 200)],
               "answer with an error or non-200 status")
        report("high", "sitemap-url-noindex",
               [c["url"] for c in checks if c.get("noindex")], "carry noindex")
        report("medium", "sitemap-url-foreign-canonical",
               [f"{c['url']} -> {c['canonical']}" for c in checks if c.get("foreign_canonical")],
               "declare a canonical other than themselves")
    return out


def render_markdown(a: dict, f: list[dict], sources: list[str]) -> str:
    lines = ["# Sitemap inventory — what the site declares", "",
             f"Sources: {', '.join(sources)}", "",
             f"**{a['urls_total']} URL(s)** across **{len(a['templates'])} template "
             f"pattern(s)**.", ""]
    # The caps belong beside the count they cap. They used to go to stderr only, so
    # any run that captured stdout — which is how this script is meant to be used —
    # lost them at the moment the number became evidence (non-negotiable #8).
    if a.get("urls_truncated") or a.get("sitemaps_skipped"):
        lines.append("> ⚠ **This is not the whole declaration.**")
        if a.get("urls_truncated"):
            lines.append(f"> {a['urls_truncated']} URL(s) beyond the "
                         f"{MAX_URLS_PER_MAP}-per-file sitemap limit were truncated and are "
                         f"not counted above.")
        if a.get("sitemaps_skipped"):
            lines.append(f"> {a['sitemaps_skipped']} nested sitemap(s) were not read "
                         f"(`--max-maps` reached after {a.get('sitemaps_read', '?')}). "
                         f"Raise `--max-maps` before treating the count as complete.")
        lines.append("")
    lines += ["## Template families", "",
              "| pattern | URLs |", "|---|---|"]
    for t in a["templates"][:40]:
        lines.append(f"| `{t['pattern']}` | {t['urls']} |")
    if len(a["templates"]) > 40:
        lines.append(f"| … {len(a['templates']) - 40} more pattern(s) | |")
    lines += ["", "## Path depth", "", "| depth | URLs |", "|---|---|"]
    for d, c in a["depth_distribution"].items():
        lines.append(f"| {d} | {c} |")
    if f:
        lines += ["", "## Findings", ""]
        for x in f:
            lines.append(f"- **{x['severity']}** [{x['code']}] {x['message']}")
    sample = a.get("url_checks")
    if sample is not None:
        answered = [c for c in sample if c.get("status") is not None]
        lines += ["", "## Listed URLs, sampled", "",
                  f"{len(answered)} of {len(sample)} sampled URL(s) answered; "
                  f"{len(sample) - len(answered)} could not be fetched and support no finding.", "",
                  "| URL | status | redirect | noindex | canonical |", "|---|---|---|---|---|"]
        for c in sample[:50]:
            status = c["status"] if c["status"] is not None else f"unfetched: {_flat(c.get('error') or '?', 60)}"
            noindex = "-" if c.get("noindex") is None else ("yes" if c["noindex"] else "no")
            canonical = "-" if not c.get("canonical") else ("foreign: " if c.get("foreign_canonical") else "self: ") + _flat(c["canonical"], 80)
            lines.append(f"| {_flat(c['url'], 80)} | {status} | {_flat(c.get('location') or '-', 80)} | {noindex} | {canonical} |")
        if len(sample) > 50:
            lines.append(f"| … {len(sample) - 50} more in --format json | | | | |")
    robots = a.get("robots_sitemaps")
    if robots is not None:
        lines += ["", "## Sitemaps declared in robots.txt", ""]
        if not robots:
            lines.append("- robots.txt declares no `Sitemap:` line")
        for r in robots:
            state = r["status"] if r.get("status") is not None else f"unfetched: {_flat(r.get('error') or '?', 80)}"
            lines.append(f"- {_flat(r['url'])}: {state}")
    lm = a.get("lastmod")
    if lm and lm.get("entries"):
        lines += ["", f"lastmod: {lm['with_lastmod']} of {lm['entries']} entries carry one, "
                  f"{lm['distinct']} distinct value(s)."]
    lines += ["", f"> {a['not_derivable_here']}", "",
              "Pair this with the GSC Pages report to get declared-vs-indexed per "
              "template, which is what SKILL.md step 1 asks for."]
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--url", help="sitemap or sitemap-index URL")
    ap.add_argument("--file", help="local sitemap file")
    ap.add_argument("--max-maps", type=int, default=50,
                    help="cap on nested sitemaps followed (default 50); the excess is reported")
    ap.add_argument("--robots", help="robots.txt URL: probe every Sitemap: line it declares; "
                    "with no --url/--file, the declared sitemaps that serve become the roots")
    ap.add_argument("--sample", type=int, default=0,
                    help=f"fetch up to N listed page URLs (max {SAMPLE_MAX}, default 0 = off) and "
                         "report status, redirect, noindex and foreign canonical per URL")
    ap.add_argument("--sample-delay", type=float, default=0.2,
                    help="seconds between sampled fetches (default 0.2)")
    ap.add_argument("--format", choices=["markdown", "json"], default="markdown")
    args = ap.parse_args(argv)
    if not 0 <= args.sample <= SAMPLE_MAX:
        ap.error(f"--sample must be between 0 and {SAMPLE_MAX}")
    if args.sample_delay < 0:
        ap.error("--sample-delay must not be negative")

    robots_probes = None
    robots_errors: list[dict] = []
    robots_roots: list[str] = []
    if args.robots:
        robots_probes = []
        try:
            declared = robots_sitemaps(fetch(args.robots))
        except (urllib.error.URLError, OSError, ValueError, http.client.HTTPException) as exc:
            declared = []
            robots_errors.append({"source": args.robots, "code": "robots_unavailable", "detail": _flat(str(exc))})
        for sm_url in declared:
            probe = check_url(sm_url)
            robots_probes.append({"url": sm_url, "status": probe["status"],
                                  "location": probe["location"], "error": probe["error"]})
            if probe["status"] == 200:
                robots_roots.append(sm_url)

    no_input = not args.url and not args.file and not robots_roots
    input_errors = [{"code": "no_input", "detail": "No sitemap input resolved; pass --url or --file."}] if no_input else []

    if args.max_maps <= 0:
        ap.error("--max-maps must be positive")

    sources: list[str] = []
    urls: list[str] = []
    errors: list[dict] = []
    page_errors: list[dict] = []
    reasons: list[dict] = list(input_errors)
    returned = 0
    skipped = 0
    truncated = 0
    unknown_frontier = False
    unfollowed = 0
    roots = [args.file] if args.file else ([args.url] if args.url else robots_roots)
    discovered = set() if no_input else set(roots)
    queue = deque(dict.fromkeys(roots) if not no_input else [])
    children: set[str] = set()
    nested_indexes: list[str] = []
    stamps: list[str] = []
    while queue:
        if not args.file and len(sources) >= args.max_maps:
            skipped = len(queue)
            unknown_frontier = True
            reasons.append({"code": "document_cap", "detail": f"{skipped} known documents were not attempted after --max-maps={args.max_maps}."})
            break
        source = queue.popleft()
        sources.append(source)
        try:
            if args.file:
                with open(source, "rb") as fh:
                    text = decode_body(fh.read(MAX_BYTES_PER_MAP + 1), source.endswith(".gz"))
            else:
                text = fetch(source)
            doc_stamps: list[str] = []
            pages, maps, capped = parse_sitemap(text, doc_stamps)
        except (urllib.error.URLError, OSError, ValueError, http.client.HTTPException) as exc:
            code = "incomplete_body" if isinstance(exc, IncompleteBody) else "input_failed"
            errors.append({"source": source, "code": code, "detail": str(exc)})
            unknown_frontier = True
            print(f"could not read sitemap: {exc}", file=sys.stderr)
            continue
        returned += 1
        stamps.extend(doc_stamps)
        if maps and source in children:
            nested_indexes.append(source)
        # XML completeness does not guarantee every loc can be analyzed as a URL.
        # Preserve valid observations instead of losing the entire report later.
        for page in pages:
            try:
                urlparse(page)
            except ValueError as exc:
                page_errors.append({"source": source, "url": page,
                                    "code": "invalid_page_url", "detail": str(exc)})
            else:
                urls.append(page)
        truncated += capped
        if args.file:
            unfollowed = len(set(maps))
            if unfollowed:
                unknown_frontier = True
                reasons.append({"code": "offline_index", "detail": f"{unfollowed} nested references are not followed in --file mode; they may hide descendants."})
        else:
            for nested in maps:
                if nested not in discovered:
                    discovered.add(nested)
                    children.add(nested)
                    queue.append(nested)
    for code in sorted({e["code"] for e in errors}):
        reasons.append({"code": code, "detail": f"{sum(e['code'] == code for e in errors)} attempted document(s) did not yield complete parseable XML; see errors."})
    if page_errors:
        reasons.append({"code": "invalid_page_url", "detail": f"{len(page_errors)} page URL entries could not be parsed and were excluded; see page_errors. Parsed document counts are unchanged."})
    if unknown_frontier:
        reasons.append({"code": "unknown_frontier", "detail": "Unresolved documents can hide additional descendants; requested is unknown, not the known-discovered count."})
    if truncated:
        reasons.append({"code": "page_url_cap", "detail": f"{truncated} page URL entries beyond the per-document limit were excluded from analysis; document counts are separate."})
        print(f"note: {truncated} URL(s) beyond the {MAX_URLS_PER_MAP}-per-file sitemap limit were not read", file=sys.stderr)
    if not urls:
        print("no sitemap input resolved" if no_input else "sitemap collection supplied no page URLs", file=sys.stderr)
    scope = ("One local file; returned means complete parseable XML. Nested references are not followed. "
             if args.file else "Exact unique discovered sitemap URLs, including the root; returned means complete parseable XML, including empty URL sets. ")
    scope += "Counts are documents, not page URLs, redirect hops or the site's URL universe."
    coverage = collector_coverage("local_file" if args.file else "unique_sitemap_document", scope,
                                  None if unknown_frontier else len(discovered), len(sources), returned, skipped, reasons)
    traversal = {"known_discovered": len(discovered), "unknown_frontier": unknown_frontier,
                 "offline_nested_references": unfollowed}

    a = analyze(urls)
    a["sitemaps_read"] = len(sources)
    a["sitemaps_skipped"] = skipped
    a["urls_truncated"] = truncated
    a["urls_invalid"] = len(page_errors)
    a["nested_indexes"] = nested_indexes
    a["lastmod"] = lastmod_profile(stamps)
    if robots_probes is not None:
        a["robots_sitemaps"] = robots_probes
    sample_coverage = None
    if args.sample:
        picked = pick_sample(urls, args.sample)
        checks = []
        for i, page in enumerate(picked):
            if i and args.sample_delay:
                time.sleep(args.sample_delay)
            checks.append(check_url(page))
        a["url_checks"] = checks
        failed = [c for c in checks if c["status"] is None]
        sample_reasons = []
        if failed:
            sample_reasons.append({"code": "input_failed", "detail": f"{len(failed)} sampled URL(s) could not be fetched; they support no finding."})
        if len(picked) < len(set(urls)):
            sample_reasons.append({"code": "sample_bound", "detail": f"{len(picked)} of {len(set(urls))} unique listed URLs sampled, spread across template families; the rest were not checked."})
        sample_coverage = collector_coverage(
            "listed_url_probe",
            "One GET per sampled listed page URL, redirects not followed; returned means an HTTP status was observed. Not the whole sitemap.",
            len(picked), len(picked), len(picked) - len(failed), 0, sample_reasons)
    f = [] if no_input else findings(a)
    if no_input and robots_probes is not None:
        f = findings({"duplicate_paths": {}, "hosts": {}, "depth_distribution": {}, "urls_total": 0,
                      "robots_sitemaps": robots_probes})
    prov = provenance("sitemap_audit.py", argv,
                      f"{len(urls)} URL(s) from {len(sources)} sitemap(s): "
                      + ", ".join(sources[:3])
                      + (f" (+{len(sources) - 3} more)" if len(sources) > 3 else ""))
    if args.format == "json":
        print(json.dumps({"producer": prov, "sources": sources,
                          "analysis": a, "findings": f, "coverage": coverage,
                          "traversal": traversal, "errors": errors, "page_errors": page_errors, "input_errors": input_errors,
                          "robots_errors": robots_errors, "sample_coverage": sample_coverage}, indent=2))
    else:
        print(render_markdown(a, f, sources))
        print("\n" + collector_coverage_md(coverage))
        if sample_coverage:
            print("\n" + collector_coverage_md(sample_coverage))
        if errors:
            print("\n## Collection errors\n")
            for error in errors:
                print(f"- {_flat(error['source'])}: {_flat(error['detail'])}")
        for error in robots_errors:
            print(f"\nrobots.txt unavailable: {_flat(error['source'])}: {_flat(error['detail'])}")
        if page_errors:
            print("\n## Excluded page URLs\n")
            for error in page_errors:
                print(f"- {_flat(error['url'])}: {_flat(error['detail'])}")
        print("\n" + provenance_md(prov))
    return 1 if errors or page_errors or robots_errors or not urls else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
