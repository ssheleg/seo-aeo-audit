#!/usr/bin/env python3
"""page_audit — per-page mechanical evidence for an SEO/AEO audit.

Collects the checks that are cheap to automate and expensive to eyeball:
indexing directives, the canonical-attribute trap, heading and schema
inventory, link/read-budget economics for answer engines, and image alt
coverage.

stdlib only. Works offline with --file so it can be tested without network.

Usage:
  page_audit.py --url https://example.com/pricing [--format markdown|json]
  page_audit.py --file saved.html --base-url https://example.com/pricing
  (--base-url applies to --file only; with --url the fetched URL is used)
  page_audit.py --url-list urls.txt --format json > audit.json

Exit codes: 0 = ran (findings may exist), 1 = usage/fetch error.
"""
from __future__ import annotations

import argparse
import gzip
import json
import re
import sys
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

# --- constants -------------------------------------------------------------

# ChatGPT Deep Research first-read window, measured from WebSocket logs (2026).
READ_BUDGET_CHARS = 5700
# Only rel and href are safe on a canonical link; anything that changes the
# semantics of the element makes Google discard the declaration.
CANONICAL_SAFE_ATTRS = {"rel", "href"}
CANONICAL_HARMLESS_PREFIXES = ("data-",)
CANONICAL_HARMLESS_ATTRS = {"id", "class"}
SKIP_TEXT_TAGS = {"script", "style", "template", "noscript", "svg"}
HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}
DEFAULT_UA = "seo-aeo-audit/0.1 (+https://github.com/ssheleg/seo-aeo-audit)"
CURRENCY_RE = re.compile(r"[$€£¥₽]|\b(usd|eur|gbp|rub)\b", re.I)


class Doc:
    """Parsed view of one HTML document."""

    def __init__(self) -> None:
        self.title: str | None = None
        self.meta_description: str | None = None
        self.meta_robots: list[str] = []
        self.canonicals: list[dict] = []
        self.headings: list[tuple[str, str]] = []
        self.jsonld_raw: list[str] = []
        self.links: list[dict] = []
        self.images: list[dict] = []
        self.hreflang: list[str] = []
        self.meta_refresh: str | None = None
        self.stream: list[tuple[str, str]] = []  # ("text"|"link", payload)


class Parser(HTMLParser):
    """Single pass: metadata, structure and a source-order text/link stream."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.doc = Doc()
        self._skip_depth = 0
        self._in_head = False
        self._in_title = False
        self._heading: str | None = None
        self._heading_buf: list[str] = []
        self._in_jsonld = False
        self._jsonld_buf: list[str] = []
        self._anchor: dict | None = None
        self._anchor_buf: list[str] = []

    # -- helpers
    @staticmethod
    def _attrs(attrs: list[tuple[str, str | None]]) -> dict:
        return {k.lower(): (v if v is not None else "") for k, v in attrs}

    def handle_starttag(self, tag, attrs):  # noqa: C901 - flat dispatch is clearer
        tag = tag.lower()
        a = self._attrs(attrs)
        if tag in SKIP_TEXT_TAGS:
            if tag == "script" and a.get("type", "").lower() == "application/ld+json":
                self._in_jsonld = True
                self._jsonld_buf = []
            self._skip_depth += 1
            return
        if tag == "head":
            self._in_head = True
        elif tag == "body":
            self._in_head = False
        elif tag == "title":
            self._in_title = True
        elif tag == "meta":
            name = a.get("name", "").lower()
            if name == "description":
                self.doc.meta_description = a.get("content", "").strip()
            elif name in ("robots", "googlebot", "google"):
                self.doc.meta_robots.append(f"{name}:{a.get('content', '').strip()}")
            if a.get("http-equiv", "").lower() == "refresh":
                self.doc.meta_refresh = a.get("content", "").strip()
        elif tag == "link":
            rels = a.get("rel", "").lower().split()
            if "canonical" in rels:
                extra = sorted(
                    k
                    for k in a
                    if k not in CANONICAL_SAFE_ATTRS
                    and k not in CANONICAL_HARMLESS_ATTRS
                    and not k.startswith(CANONICAL_HARMLESS_PREFIXES)
                )
                self.doc.canonicals.append({"href": a.get("href", "").strip(), "extra_attrs": extra})
            if "alternate" in rels and a.get("hreflang"):
                self.doc.hreflang.append(a["hreflang"])
        elif tag in HEADING_TAGS:
            self._heading = tag
            self._heading_buf = []
        elif tag == "a":
            self._anchor = {
                "href": a.get("href", "").strip(),
                "rel": a.get("rel", "").lower(),
                "nofollow": "nofollow" in a.get("rel", "").lower(),
            }
            self._anchor_buf = []
        elif tag == "img":
            self.doc.images.append(
                {
                    "src": a.get("src", "").strip(),
                    "alt": a.get("alt"),
                    "loading": a.get("loading", ""),
                    "has_dims": bool(a.get("width") and a.get("height")),
                }
            )

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in SKIP_TEXT_TAGS:
            if tag == "script" and self._in_jsonld:
                self.doc.jsonld_raw.append("".join(self._jsonld_buf))
                self._in_jsonld = False
            self._skip_depth = max(0, self._skip_depth - 1)
            return
        if tag == "head":
            self._in_head = False
        elif tag == "title":
            self._in_title = False
        elif tag in HEADING_TAGS and self._heading == tag:
            text = " ".join("".join(self._heading_buf).split())
            self.doc.headings.append((tag, text))
            self._heading = None
        elif tag == "a" and self._anchor is not None:
            anchor_text = " ".join("".join(self._anchor_buf).split())
            self._anchor["text"] = anchor_text
            self.doc.links.append(self._anchor)
            # Deep Research renders every link inline as a marker that eats the
            # same read budget as content.
            self.doc.stream.append(("link", f"【{anchor_text}†{self._anchor['href']}】"))
            self._anchor = None

    def handle_data(self, data):
        if self._in_jsonld:
            self._jsonld_buf.append(data)
            return
        if self._skip_depth:
            return
        if self._in_title:
            self.doc.title = ((self.doc.title or "") + data).strip()
        if self._heading is not None:
            self._heading_buf.append(data)
        if self._anchor is not None:
            self._anchor_buf.append(data)
            return
        # <head> never reaches the answer-engine read window, and its text would
        # otherwise count as content in the read-budget model.
        if data.strip() and not self._in_head:
            self.doc.stream.append(("text", data))


# --- analysis --------------------------------------------------------------


def _visible_text(doc: Doc, include_links: bool = True) -> str:
    """Extractable text in source order.

    include_links=False gives prose only, so navigation labels do not inflate the
    word count or hide whether the page answers in its opening words.
    """
    parts = []
    for kind, payload in doc.stream:
        if kind == "text":
            parts.append(payload)
        elif include_links:
            parts.append(payload.split("†")[0].lstrip("【"))
    return " ".join(" ".join(parts).split())


def _read_budget(doc: Doc, budget: int = READ_BUDGET_CHARS) -> dict:
    """Share of the answer-engine first read spent on content vs link markers."""
    used = content = links = 0
    links_before_content = 0
    seen_content = False
    for kind, payload in doc.stream:
        chunk = " ".join(payload.split())
        if not chunk:
            continue
        remaining = budget - used
        if remaining <= 0:
            break
        take = min(len(chunk) + 1, remaining)
        used += take
        if kind == "text":
            content += take
            seen_content = True
        else:
            links += take
            if not seen_content:
                links_before_content += 1
    pct = round(100.0 * content / used, 1) if used else 0.0
    return {
        "window_chars": budget,
        "chars_used": used,
        "content_pct": pct,
        "link_marker_pct": round(100.0 - pct, 1) if used else 0.0,
        "links_before_first_text": links_before_content,
        "exhausted": used >= budget,
    }


def _jsonld_types(doc: Doc) -> tuple[list[str], list[str]]:
    types: list[str] = []
    errors: list[str] = []

    def walk(node):
        if isinstance(node, dict):
            t = node.get("@type")
            if isinstance(t, str):
                types.append(t)
            elif isinstance(t, list):
                types.extend([x for x in t if isinstance(x, str)])
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    for raw in doc.jsonld_raw:
        try:
            walk(json.loads(raw))
        except Exception as exc:  # noqa: BLE001 - report, never crash the audit
            errors.append(str(exc))
    return sorted(set(types)), errors


def analyse(html: str, url: str, headers: dict | None = None) -> dict:
    parser = Parser()
    parser.feed(html)
    parser.close()
    doc = parser.doc
    headers = {k.lower(): v for k, v in (headers or {}).items()}

    text = _visible_text(doc)
    prose = _visible_text(doc, include_links=False)
    words = len(prose.split())
    link_words = len(text.split()) - words
    types, jsonld_errors = _jsonld_types(doc)

    host = urlparse(url).netloc.lower() if url else ""
    internal = external = nofollow = 0
    for link in doc.links:
        href = link.get("href", "")
        if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue
        netloc = urlparse(urljoin(url or "", href)).netloc.lower()
        if not netloc or netloc == host:
            internal += 1
        else:
            external += 1
        if link.get("nofollow"):
            nofollow += 1

    robots_values = " ".join(doc.meta_robots).lower()
    x_robots = headers.get("x-robots-tag", "").lower()
    directives = robots_values + " " + x_robots
    # word boundaries: `none` is a directive, `nonexistent` is not
    noindex = bool(re.search(r"\bnoindex\b|\bnone\b", directives))
    nosnippet = bool(re.search(r"\bnosnippet\b", directives))

    canonical_href = doc.canonicals[0]["href"] if doc.canonicals else None
    canonical_abs = urljoin(url or "", canonical_href) if canonical_href else None
    self_ref = bool(url and canonical_abs and canonical_abs.split("#")[0] == url.split("#")[0])

    h1s = [t for tag, t in doc.headings if tag == "h1"]
    subheads = sum(1 for tag, _ in doc.headings if tag in ("h2", "h3", "h4"))
    imgs_no_alt = sum(1 for i in doc.images if i["alt"] is None)
    imgs_empty_alt = sum(1 for i in doc.images if i["alt"] == "")

    first_100 = " ".join(prose.split()[:100])
    result = {
        "url": url,
        "title": doc.title,
        "title_len": len(doc.title or ""),
        "meta_description_len": len(doc.meta_description or ""),
        "meta_robots": doc.meta_robots,
        "x_robots_tag": headers.get("x-robots-tag"),
        "meta_refresh": doc.meta_refresh,
        "noindex": noindex,
        "nosnippet": nosnippet,
        "canonical": canonical_href,
        "canonical_count": len(doc.canonicals),
        "canonical_extra_attrs": doc.canonicals[0]["extra_attrs"] if doc.canonicals else [],
        "canonical_self_referential": self_ref,
        "h1_count": len(h1s),
        "h1": h1s[0] if h1s else None,
        "subheads_h2_h4": subheads,
        "word_count": words,
        "link_text_words": link_words,
        "first_100_words": first_100,
        "currency_in_text": bool(CURRENCY_RE.search(text)),
        "currency_in_source_only": bool(CURRENCY_RE.search(html)) and not bool(CURRENCY_RE.search(text)),
        "jsonld_blocks": len(doc.jsonld_raw),
        "jsonld_types": types,
        "jsonld_errors": jsonld_errors,
        "hreflang_count": len(doc.hreflang),
        "links_total": internal + external,
        "links_internal": internal,
        "links_external": external,
        "links_nofollow": nofollow,
        "images_total": len(doc.images),
        "images_missing_alt": imgs_no_alt,
        "images_empty_alt": imgs_empty_alt,
        "read_budget": _read_budget(doc),
    }
    result["findings"] = findings(result)
    return result


def findings(r: dict) -> list[dict]:
    """Deterministic checks. Each finding names the observation, not a guess."""
    out: list[dict] = []

    def add(sev, code, msg, ref):
        out.append({"severity": sev, "code": code, "message": msg, "reference": ref})

    if r["noindex"]:
        add("blocker", "noindex",
            f"page carries a noindex directive ({r['meta_robots'] or r['x_robots_tag']}); "
            "note that content=\"none\" is equivalent to noindex, nofollow",
            "technical-checks.md#a0-blockers-first")
    if r["meta_refresh"] and r["noindex"]:
        add("blocker", "refresh-noindex",
            "meta refresh combined with noindex has no defined precedence: the page drops out "
            "and the canonical never passes equity — replace with a server-side 301",
            "technical-checks.md#b-canonicalization-and-duplication")
    if r["canonical_extra_attrs"]:
        add("high", "canonical-attrs",
            "canonical link carries extra attributes "
            f"({', '.join(r['canonical_extra_attrs'])}); Google discards the declaration — "
            "emit rel and href only",
            "technical-checks.md#b-canonicalization-and-duplication")
    if r["canonical_count"] == 0:
        add("medium", "canonical-missing",
            "no rel=canonical; a self-referencing canonical is the documented recommendation",
            "technical-checks.md#b-canonicalization-and-duplication")
    elif r["canonical_count"] > 1:
        add("high", "canonical-multiple",
            f"{r['canonical_count']} canonical declarations on one page — the engine may ignore all of them",
            "technical-checks.md#b-canonicalization-and-duplication")
    elif not r["canonical_self_referential"]:
        add("info", "canonical-cross",
            f"canonical points elsewhere ({r['canonical']}) — confirm that is intended",
            "technical-checks.md#b-canonicalization-and-duplication")
    if r["nosnippet"]:
        add("high", "nosnippet",
            "nosnippet / data-nosnippet gates what answer engines may quote from this page",
            "aeo-geo.md#f3-extractability--the-part-most-audits-skip")
    if r["h1_count"] == 0:
        add("medium", "h1-missing", "no H1 on the page", "intent-and-content.md")
    elif r["h1_count"] > 1:
        add("info", "h1-multiple", f"{r['h1_count']} H1 elements", "intent-and-content.md")
    if r["subheads_h2_h4"] < 4:
        add("medium", "subheads-thin",
            f"{r['subheads_h2_h4']} H2–H4 subheads; 4–10 is the observed citation optimum "
            "(33.2% vs 28% for 1–3)",
            "aeo-geo.md#f2-what-correlates-with-being-cited-ranked-evidence")
    if r["word_count"] < 300:
        add("medium", "thin",
            f"{r['word_count']} words of prose (link labels excluded; "
            f"{r['link_text_words']} more words sit in link text)",
            "intent-and-content.md#e2-information-gain")
    if r["title_len"] == 0:
        add("high", "title-missing", "no <title>", "technical-checks.md")
    if r["meta_description_len"] == 0:
        add("info", "description-missing", "no meta description", "technical-checks.md")
    if r["jsonld_errors"]:
        add("high", "jsonld-invalid",
            f"invalid JSON-LD ({r['jsonld_errors'][0]})", "entity-and-brand.md#g3-knowledge-graph-plumbing")
    if r["jsonld_blocks"] and not r["jsonld_types"] and not r["jsonld_errors"]:
        add("medium", "jsonld-untyped", "JSON-LD present with no @type",
            "entity-and-brand.md#g3-knowledge-graph-plumbing")
    rb = r["read_budget"]
    if rb["content_pct"] < 55:
        add("high", "read-budget",
            f"only {rb['content_pct']}% of the ~{rb['window_chars']}-char answer-engine first read is "
            f"content; {rb['link_marker_pct']}% is link markers "
            f"({rb['links_before_first_text']} links before the first text)",
            "architecture-and-equity.md#read-budget-navigation-now-costs-you-twice")
    elif rb["links_before_first_text"] >= 20:
        add("medium", "nav-before-content",
            f"{rb['links_before_first_text']} links appear before the first text in source order",
            "architecture-and-equity.md#read-budget-navigation-now-costs-you-twice")
    if r["links_total"] >= 60:
        add("medium", "link-count",
            f"{r['links_total']} links on the page; above 60 the first read is ~33% content",
            "architecture-and-equity.md#read-budget-navigation-now-costs-you-twice")
    if r["images_missing_alt"]:
        add("medium", "alt-missing",
            f"{r['images_missing_alt']} image(s) without an alt attribute; alt text is the only image "
            "content answer engines read",
            "aeo-geo.md#f3-extractability--the-part-most-audits-skip")
    if r["currency_in_source_only"]:
        add("high", "price-not-in-text",
            "a price appears in the source but not in extractable text (JS-gated or image) — "
            "engines fall back to citing aggregators for your pricing",
            "aeo-geo.md#f3-extractability--the-part-most-audits-skip")
    return out


# --- io --------------------------------------------------------------------


def fetch(url: str, timeout: float, user_agent: str, max_bytes: int) -> tuple[str, dict]:
    from urllib.request import Request, urlopen

    req = Request(url, headers={"User-Agent": user_agent, "Accept-Encoding": "gzip"})
    with urlopen(req, timeout=timeout) as resp:  # noqa: S310 - explicit user-provided URL
        raw = resp.read(max_bytes)
        headers = dict(resp.headers.items())
        if (headers.get("Content-Encoding") or "").lower() == "gzip":
            raw = gzip.decompress(raw)
        charset = resp.headers.get_content_charset() or "utf-8"
    return raw.decode(charset, errors="replace"), headers


SEVERITY_ORDER = {"blocker": 0, "high": 1, "medium": 2, "info": 3}


def to_markdown(results: list[dict]) -> str:
    lines: list[str] = []
    for r in results:
        lines.append(f"## {r['url'] or '(local file)'}")
        lines.append("")
        if "error" in r:
            lines.append(f"- **fetch failed**: {r['error']}")
            lines.append("")
            continue
        rb = r["read_budget"]
        lines.append(
            f"- title ({r['title_len']} chars): {r['title'] or '—'}\n"
            f"- H1: {r['h1'] or '—'} · subheads H2–H4: {r['subheads_h2_h4']} · prose words: "
            f"{r['word_count']} (+{r['link_text_words']} in link text)\n"
            f"- canonical: {r['canonical'] or '—'}"
            f"{' (extra attrs: ' + ', '.join(r['canonical_extra_attrs']) + ')' if r['canonical_extra_attrs'] else ''}\n"
            f"- robots: {', '.join(r['meta_robots']) or '—'}"
            f"{' · X-Robots-Tag: ' + r['x_robots_tag'] if r['x_robots_tag'] else ''}\n"
            f"- JSON-LD: {r['jsonld_blocks']} block(s), types: {', '.join(r['jsonld_types']) or '—'}\n"
            f"- links: {r['links_total']} ({r['links_internal']} internal / {r['links_external']} external, "
            f"{r['links_nofollow']} nofollow)\n"
            f"- images: {r['images_total']} ({r['images_missing_alt']} without alt, "
            f"{r['images_empty_alt']} decorative)\n"
            f"- answer-engine first read: {rb['content_pct']}% content / {rb['link_marker_pct']}% link markers"
        )
        lines.append("")
        lines.append(f"> first 100 prose words: {r['first_100_words'][:400] or '—'}")
        lines.append("")
        if r["findings"]:
            lines.append("| severity | check | finding | reference |")
            lines.append("|---|---|---|---|")
            for f in sorted(r["findings"], key=lambda x: SEVERITY_ORDER[x["severity"]]):
                lines.append(
                    f"| {f['severity']} | `{f['code']}` | {f['message']} | {f['reference']} |"
                )
        else:
            lines.append("No mechanical findings on this page.")
        lines.append("")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Per-page SEO/AEO mechanical audit (stdlib only).")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--url", help="single URL to fetch and analyse")
    src.add_argument("--url-list", help="file with one URL per line")
    src.add_argument("--file", help="local HTML file (offline mode)")
    ap.add_argument("--base-url", default="", help="URL the local file represents (offline mode)")
    ap.add_argument("--format", choices=("markdown", "json"), default="markdown")
    ap.add_argument("--timeout", type=float, default=20.0)
    ap.add_argument("--user-agent", default=DEFAULT_UA)
    ap.add_argument("--max-bytes", type=int, default=5_000_000)
    args = ap.parse_args(argv)

    results: list[dict] = []
    if args.file:
        try:
            with open(args.file, encoding="utf-8", errors="replace") as fh:
                html = fh.read()
        except OSError as exc:
            print(f"error: cannot read {args.file}: {exc}", file=sys.stderr)
            return 1
        results.append(analyse(html, args.base_url))
    else:
        urls = [args.url] if args.url else []
        if args.url_list:
            try:
                with open(args.url_list, encoding="utf-8") as fh:
                    urls = [ln.strip() for ln in fh if ln.strip() and not ln.startswith("#")]
            except OSError as exc:
                print(f"error: cannot read {args.url_list}: {exc}", file=sys.stderr)
                return 1
        if not urls:
            print("error: no URLs to audit", file=sys.stderr)
            return 1
        for url in urls:
            try:
                html, headers = fetch(url, args.timeout, args.user_agent, args.max_bytes)
                results.append(analyse(html, url, headers))
            except Exception as exc:  # noqa: BLE001 - one bad URL must not kill the run
                results.append({"url": url, "error": f"{type(exc).__name__}: {exc}", "findings": []})

    if args.format == "json":
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print(to_markdown(results))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
