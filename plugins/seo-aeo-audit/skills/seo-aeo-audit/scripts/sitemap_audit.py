#!/usr/bin/env python3
"""sitemap_audit — what the site declares, clustered into the templates it ships.

SKILL.md step 1 asks for indexed vs published URL counts **per template**. The
indexed half comes from Search Console; this is the published half, and until now
it needed a desktop crawler. Sitemaps are the site's own declaration of what it
wants indexed, which makes them the cheapest honest inventory available.

What it does: follows sitemap indexes, clusters URLs into path patterns (the
template families a site actually ships, derived from its URLs rather than
guessed from a list), and reports depth distribution and duplicate paths.

What it deliberately does NOT do: **orphan detection**. A sitemap contains no
link graph, so nothing in it can establish that a page has no inbound internal
links. Tools that report "orphan candidates" from a sitemap are inferring from
path shape; that is a guess wearing the clothes of a finding, and it fails
non-negotiable #1. Orphans need a crawl — architecture-and-equity.md says how.

stdlib only, no auth. Reads a URL, a local file, or stdin.

Usage:
  sitemap_audit.py --url https://example.com/sitemap.xml
  sitemap_audit.py --file sitemap.xml --format json
  sitemap_audit.py --url https://example.com/sitemap_index.xml --max-maps 20

Every output carries a **producer block** — `skill` (this tool's version), `script`,
`observed_at` (UTC), `runtime`, `args` (credential values redacted), `scope` (the
resolved input set), and `actor` / `model` / `trace` from `SEO_AEO_AUDIT_ACTOR`,
`_MODEL`, `_TRACE`. It is present in the default output and under `--format json` as
`producer`. A field the harness did not supply reads `unavailable: <VAR> is not set by
this harness` — never guessed, and never dropped, because a field that vanishes when
unavailable is indistinguishable from one nobody checked. `observed_at` is the field
that decides whether a finding has expired; the report's own `## Provenance` block adds
the four invalidators (see references/preflight.md).

Exit codes: 0 = ran, 1 = usage/fetch/parse error.
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter
from urllib.parse import urlparse


# ── provenance: the execution that produced this payload ── shared block ──────
# Copied verbatim into all seven scripts and compared byte for byte by
# `test/validate.py`, for the same reason `_flat` is: these ship as standalone files
# with no shared module, and an import of one does not exist in the installed layout
# (`bin/seo-aeo-audit.js` copies `scripts/` alone into `~/.claude/skills/`). The
# doctrine behind the field set lives above this block in preflight.py. Never edit
# one copy — the guard fails all seven.
SKILL_VERSION = "0.25.10"

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


UA = "seo-aeo-audit/sitemap_audit (+https://github.com/ssheleg/seo-aeo-audit)"
# A sitemap file may hold 50,000 URLs and 50 MB uncompressed (sitemaps.org).
MAX_URLS_PER_MAP = 50000
MAX_BYTES_PER_MAP = 52_428_800

_NUM = re.compile(r"^\d+$")
_SLUGGY = re.compile(r"^[a-z0-9]+(?:[-_][a-z0-9]+){1,}$")


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA,
                                               "Accept-Encoding": "gzip"})
    with urllib.request.urlopen(req, timeout=45) as resp:
        raw = resp.read(MAX_BYTES_PER_MAP)
        if resp.headers.get("Content-Encoding") == "gzip" or url.endswith(".gz"):
            try:
                raw = gzip.decompress(raw)
            except OSError:
                pass  # not actually gzipped, or truncated — parse what we have
    return raw.decode("utf-8", "replace")


def parse_sitemap(text: str) -> tuple[list[str], list[str], int]:
    """Returns (page urls, nested sitemap urls, urls dropped by the cap).

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
    ap.add_argument("--format", choices=["markdown", "json"], default="markdown")
    args = ap.parse_args(argv)

    if not args.url and not args.file:
        print("pass --url or --file", file=sys.stderr)
        return 1

    sources: list[str] = []
    urls: list[str] = []
    skipped = 0
    truncated = 0
    try:
        if args.file:
            with open(args.file, encoding="utf-8") as fh:
                text = fh.read()
            sources.append(args.file)
            pages, maps, capped = parse_sitemap(text)
            urls += pages
            truncated += capped
            if maps:
                print(f"note: {len(maps)} nested sitemap(s) referenced; pass --url to "
                      f"follow them", file=sys.stderr)
        else:
            queue = [args.url]
            seen = set()
            while queue:
                if len(sources) >= args.max_maps:
                    skipped = len(queue)
                    break
                m = queue.pop(0)
                if m in seen:
                    continue
                seen.add(m)
                sources.append(m)
                pages, maps, capped = parse_sitemap(fetch(m))
                urls += pages
                truncated += capped
                queue += [x for x in maps if x not in seen]
    except (urllib.error.URLError, OSError, ValueError) as e:
        print(f"could not read sitemap: {e}", file=sys.stderr)
        return 1

    if skipped:
        print(f"note: {skipped} nested sitemap(s) beyond --max-maps={args.max_maps} "
              f"were not read", file=sys.stderr)
    if truncated:
        # A silent cap reads as "this is the whole site" and it is not.
        print(f"note: {truncated} URL(s) beyond the {MAX_URLS_PER_MAP}-per-file "
              f"sitemap limit were not read", file=sys.stderr)
    if not urls:
        print("sitemap parsed but declared no page URLs", file=sys.stderr)
        return 1

    a = analyze(urls)
    a["sitemaps_read"] = len(sources)
    a["sitemaps_skipped"] = skipped
    a["urls_truncated"] = truncated
    f = findings(a)
    prov = provenance("sitemap_audit.py", argv,
                      f"{len(urls)} URL(s) from {len(sources)} sitemap(s): "
                      + ", ".join(sources[:3])
                      + (f" (+{len(sources) - 3} more)" if len(sources) > 3 else ""))
    if args.format == "json":
        print(json.dumps({"producer": prov, "sources": sources,
                          "analysis": a, "findings": f}, indent=2))
    else:
        print(render_markdown(a, f, sources))
        print("\n" + provenance_md(prov))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
