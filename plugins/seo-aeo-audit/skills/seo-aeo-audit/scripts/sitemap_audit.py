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

Exit codes: 0 = ran, 1 = usage/fetch/parse error.
"""
from __future__ import annotations

import argparse
import gzip
import json
import re
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter
from urllib.parse import urlparse

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
             f"pattern(s)**.", "", "## Template families", "",
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
    if args.format == "json":
        print(json.dumps({"sources": sources, "analysis": a, "findings": f}, indent=2))
    else:
        print(render_markdown(a, f, sources))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
