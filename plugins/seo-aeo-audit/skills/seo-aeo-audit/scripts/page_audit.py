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

--format json always emits a JSON **array**, one object per page, even for a single
URL. Index it (`data[0]["findings"]`); `data["findings"]` raises AttributeError,
which is what an agent reading only the one-URL example above will write first.

Every output carries a **producer block** — `skill` (this tool's version), `script`,
`observed_at` (UTC), `runtime`, `args` (credential values redacted), `scope` (the
resolved input set), and `actor` / `model` / `trace` from `SEO_AEO_AUDIT_ACTOR`,
`_MODEL`, `_TRACE`. It is present in the default output and under `--format json` on EVERY
array element — an envelope would break the array contract above. A field the harness did not supply reads `unavailable: <VAR> is not set by
this harness` — never guessed, and never dropped, because a field that vanishes when
unavailable is indistinguishable from one nobody checked. `observed_at` is the field
that decides whether a finding has expired; the report's own `## Provenance` block adds
the four invalidators (see references/preflight.md).
On a multi-URL run `observed_at` is when the payload was emitted, which is the end
of the crawl rather than each fetch.

Network behavior: plain GETs to the URLs you pass, http(s) only, no cookies or
credentials, redirects off http(s) refused, non-HTML content types refused,
response capped by --max-bytes. It writes nothing and phones nothing home.

Every finding carries an evidence tier as well as a severity, because SKILL.md
non-negotiable #2 makes the tier the confidence multiplier in
`priority = (impact x confidence) / effort`. Severity says how loud a finding is;
the tier says what backs it, and the two are not interchangeable. The mapping is
declared once, in FINDING_TIERS below, so a reader can audit it:

  CONFIRMED  the check is an observation on this page (a directive is present, a
             count is what it is) or the mechanism is engine-documented. Per
             onpage-checks.md this covers *existence*; the claimed impact of
             fixing it keeps whatever tier its mechanism has.
  STUDY      the threshold comes from published multi-site data (subhead count).
  FIELD      the threshold comes from one engine measured by one practitioner
             group (everything resting on the answer-engine read budget).

Exit codes: 0 = at least one page was analyzed, 1 = usage error, or every URL
failed (a run that produced no analysis is not a success).
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import re
import sys
import time
import zlib
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener


# ── provenance: the execution that produced this payload ── shared block ──────
# Copied verbatim into all seven scripts and compared byte for byte by
# `test/validate.py`, for the same reason `_flat` is: these ship as standalone files
# with no shared module, and an import of one does not exist in the installed layout
# (`bin/seo-aeo-audit.js` copies `scripts/` alone into `~/.claude/skills/`). The
# doctrine behind the field set lives above this block in preflight.py. Never edit
# one copy — the guard fails all seven.
SKILL_VERSION = "0.25.3"

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


# --- constants -------------------------------------------------------------

# ChatGPT Deep Research first-read window: the MEDIAN of what one practitioner
# group measured across 10+ accounts, ~June 2026 (max ~8,000) — architecture-and-
# equity.md owns the numbers, aeo-geo.md F4 owns the tier. It is one engine's
# median, not a budget every answer engine enforces, and anything resting on it is
# FIELD. The window basis travels in the payload so a report cannot quote the
# number without it.
READ_BUDGET_CHARS = 5700
READ_BUDGET_BASIS = (
    "median first-read window measured on ChatGPT Deep Research (10+ accounts, "
    "~June 2026; max ~8,000 chars) — FIELD, one engine, not a universal budget"
)
# Directives whose value is a parameter, not another directive. `content="none"`
# really is `noindex, nofollow`, and `max-image-preview:none` really is not — a
# word-boundary match over the whole string cannot tell them apart, and it
# reported a track-A blocker on pages that say `index, follow`.
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


PARAMETER_DIRECTIVES = frozenset(
    {"max-snippet", "max-image-preview", "max-video-preview", "unavailable_after"}
)
NOINDEX_TOKENS = frozenset({"noindex", "none"})
# Content the browser never renders as text. The price check has to read the
# markup a crawler sees, not every byte in the file: searched against raw HTML it
# fired on jQuery's `$` and on a correct Offer.priceCurrency.
INERT_BLOCK_RE = re.compile(
    r"<(script|style|template|noscript)\b[^>]*>.*?</\1\s*>|<!--.*?-->", re.I | re.S
)
# A truncated read cannot support a finding that depends on having the whole page.
# Presence findings survive (a directive that is there is there); absence and
# count findings do not.
COMPLETENESS_DEPENDENT = frozenset({
    "low-extractable-text", "subheads-thin", "read-budget", "nav-before-content",
    "link-count", "alt-missing", "canonical-missing", "title-missing",
    "description-missing", "h1-missing", "jsonld-price-parity",
    # Both assert that no Q&A pairing was found, and a fragment cannot support an
    # absence. The two positive-count findings (faq-collapsed, faq-schema-absent)
    # survive truncation, because a count of three found is still three found.
    "faq-unpaired", "faq-schema-orphan", "faq-schema-partial", "faq-schema-unreadable",
})
# One home for the severity -> tier mapping, so the two never drift apart.
FINDING_TIERS = {
    "noindex": "CONFIRMED",
    "refresh-noindex": "CONFIRMED",
    "canonical-attrs": "CONFIRMED",
    "canonical-missing": "CONFIRMED",
    "canonical-multiple": "CONFIRMED",
    "canonical-cross": "CONFIRMED",
    "nosnippet": "CONFIRMED",
    "h1-missing": "CONFIRMED",
    "h1-multiple": "CONFIRMED",
    "subheads-thin": "STUDY",
    "low-extractable-text": "CONFIRMED",
    "title-missing": "CONFIRMED",
    "description-missing": "CONFIRMED",
    "jsonld-invalid": "CONFIRMED",
    "jsonld-incomplete": "CONFIRMED",
    "jsonld-untyped": "CONFIRMED",
    "jsonld-price-parity": "CONFIRMED",
    "read-budget": "FIELD",
    "nav-before-content": "FIELD",
    "link-count": "FIELD",
    "alt-missing": "CONFIRMED",
    "price-not-in-text": "CONFIRMED",
    "truncated-read": "CONFIRMED",
    # The Q&A block. All of these are DOM observations, not ranking claims.
    "faq-collapsed": "STUDY",
    "faq-unpaired": "CONFIRMED",
    "faq-schema-absent": "CONFIRMED",
    "faq-schema-orphan": "CONFIRMED",
    "faq-schema-partial": "CONFIRMED",
    # The one FAQ finding that is deliberately NOT confirmed: it fires where the
    # node could not be read, and "I could not read it" is the opposite of a
    # confirmed absence (non-negotiable #8).
    "faq-schema-unreadable": "HYPOTHESIS",
}
# Only rel and href are safe on a canonical link; anything that changes the
# semantics of the element makes Google discard the declaration.
CANONICAL_SAFE_ATTRS = {"rel", "href"}
CANONICAL_HARMLESS_PREFIXES = ("data-",)
CANONICAL_HARMLESS_ATTRS = {"id", "class"}
SKIP_TEXT_TAGS = {"script", "style", "template", "noscript", "svg"}
HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}
# A heading that announces a question-and-answer block. Matched against heading
# text only, so a page merely *mentioning* an FAQ in prose does not trip it.
FAQ_HEADING_RE = re.compile(
    r"\b(faq|faqs|frequently\s+asked|common\s+questions|questions\s+(and|&)\s+answers"
    r"|q\s*(and|&)\s*a)\b",
    re.I,
)
DEFAULT_UA = "seo-aeo-audit (+https://github.com/ssheleg/seo-aeo-audit)"
CURRENCY_RE = re.compile(r"[$€£¥₽]|\b(usd|eur|gbp|rub)\b", re.I)


class Doc:
    """Parsed view of one HTML document."""

    def __init__(self) -> None:
        self.title: str | None = None
        self.meta_description: str | None = None
        self.meta_robots: list[str] = []
        # The directive *contents*, kept apart from the display list above: the
        # display list is prefixed with the meta name, which a parser must not
        # mistake for a directive of its own.
        self.robots_contents: list[str] = []
        self.data_nosnippet = 0
        self.canonicals: list[dict] = []
        self.headings: list[tuple[str, str]] = []
        self.jsonld_raw: list[str] = []
        self.links: list[dict] = []
        self.images: list[dict] = []
        self.hreflang: list[str] = []
        self.meta_refresh: str | None = None
        self.stream: list[tuple[str, str]] = []  # ("text"|"link", payload)
        # Q&A shape. An answer engine can only quote an answer present in the
        # served markup, so these four counts are what separate "the page has an
        # FAQ" from "the page has an FAQ a machine can read".
        self.dt_count = 0        # <dt> — a question paired with its answer
        self.dd_count = 0        # <dd> — the answer, flat in the DOM
        self.details_count = 0   # <details> — an answer behind a click
        self.summary_count = 0   # <summary> — its label
        # The third pairing, and the one this parser used to read as no pairing at
        # all: the WAI-ARIA disclosure pattern. A button carrying aria-expanded +
        # aria-controls and a panel carrying aria-labelledby is the accessible
        # accordion every component library ships, its answer text is in the
        # served HTML, and counting only <dt>/<dd> and <details> reported those
        # answers as absent — a `high`/`CONFIRMED` finding about markup that was
        # right there. Reproduced on a live site on 2026-08-14.
        self.aria_disclosure = 0   # aria-expanded + aria-controls — the question
        self.aria_panel = 0        # aria-labelledby — the answer it points at


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
        # Element-level preview suppression, which the nosnippet finding has always
        # claimed to cover and never checked.
        if "data-nosnippet" in a:
            self.doc.data_nosnippet += 1
        # Counted on any element, not inside the tag dispatch below: the ARIA
        # disclosure pattern is attributes on whatever the component library
        # chose, and dispatching on tag name is exactly how this pairing went
        # unseen.
        if "aria-controls" in a and "aria-expanded" in a:
            self.doc.aria_disclosure += 1
        if "aria-labelledby" in a:
            self.doc.aria_panel += 1
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
                content = a.get("content", "").strip()
                self.doc.meta_robots.append(f"{name}:{content}")
                self.doc.robots_contents.append(content)
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
        elif tag == "dt":
            self.doc.dt_count += 1
        elif tag == "dd":
            self.doc.dd_count += 1
        elif tag == "details":
            self.doc.details_count += 1
        elif tag == "summary":
            self.doc.summary_count += 1
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
        "window_basis": READ_BUDGET_BASIS,
        "window_engine": "ChatGPT Deep Research",
        "window_tier": "FIELD",
        "chars_used": used,
        "content_pct": pct,
        "link_marker_pct": round(100.0 - pct, 1) if used else 0.0,
        "links_before_first_text": links_before_content,
        "exhausted": used >= budget,
    }


def parse_directives(values) -> set[str]:
    """Directive tokens from robots meta contents and X-Robots-Tag values.

    A directive is one comma-separated token. A token shaped `key:value` is a
    parameter when the key is one of PARAMETER_DIRECTIVES — its value is data, not
    a directive — and otherwise a user-agent prefix, where the value *is* the
    directive (`X-Robots-Tag: googlebot: noindex`).

    Matching the whole string with a word-boundary regex instead reads
    `max-image-preview:none` as `none`, i.e. as `noindex, nofollow`, and reports a
    fabricated indexation blocker on a page that declares `index, follow`.
    """
    out: set[str] = set()
    for raw in values:
        for token in (raw or "").split(","):
            token = token.strip().lower()
            if not token:
                continue
            if ":" in token:
                key, _, val = token.partition(":")
                key, val = key.strip(), val.strip()
                if key in PARAMETER_DIRECTIVES:
                    continue
                token = val or key
            if token:
                out.add(token)
    return out


def strip_inert(html: str) -> str:
    """HTML with script, style, template, noscript bodies and comments removed.

    The price check asks whether a currency symbol exists in the markup but not in
    the extractable text. Run against every byte of the file it answered yes for
    jQuery's `$` and for a correct `Offer.priceCurrency` — both of them markup a
    crawler reads as something other than page text.
    """
    return INERT_BLOCK_RE.sub(" ", html)


def _jsonld_price(doc: Doc) -> bool:
    """Does any JSON-LD node declare a price? (a different question from the text)"""
    keys = ("price", "priceCurrency", "lowPrice", "highPrice")
    found = False

    def walk(node):
        nonlocal found
        if found:
            return
        if isinstance(node, dict):
            if any(node.get(k) not in (None, "") for k in keys):
                found = True
                return
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    for raw in doc.jsonld_raw:
        try:
            walk(json.loads(raw))
        except Exception:  # noqa: BLE001 - malformed blocks are reported elsewhere
            continue
    return found


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


# Structural requirements only: a node of this @type without these properties is
# incomplete on its own terms, which is an observation about the page. It is NOT
# a rich-result eligibility verdict — Google's per-feature required-property
# tables are a separate contract, and claiming eligibility without checking them
# would be exactly the guessing non-negotiable #1 forbids. Route to the Rich
# Results Test for eligibility; report only what is observable here.
REQUIRED_PROPS = {
    "Article": ("headline",),
    "NewsArticle": ("headline",),
    "BlogPosting": ("headline",),
    "Product": ("name",),
    "Organization": ("name",),
    "LocalBusiness": ("name",),
    "BreadcrumbList": ("itemListElement",),
    "FAQPage": ("mainEntity",),
    "HowTo": ("name", "step"),
    "Event": ("name", "startDate"),
    "JobPosting": ("title", "datePosted"),
    "Recipe": ("name",),
}


def _jsonld_required(doc: Doc) -> list[str]:
    """`Type.property` for every documented-structural property that is absent."""
    missing: list[str] = []

    def walk(node):
        if isinstance(node, dict):
            raw_t = node.get("@type")
            names = [raw_t] if isinstance(raw_t, str) else [
                x for x in (raw_t or []) if isinstance(x, str)]
            for t in names:
                for prop in REQUIRED_PROPS.get(t, ()):
                    val = node.get(prop)
                    if val is None or (isinstance(val, (str, list, dict)) and len(val) == 0):
                        entry = f"{t}.{prop}"
                        if entry not in missing:
                            missing.append(entry)
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    for raw in doc.jsonld_raw:
        try:
            walk(json.loads(raw))
        except Exception:  # noqa: BLE001 - malformed blocks are reported by _jsonld_types
            continue
    return missing


def _faq_declared_vs_served(doc: Doc) -> dict:
    """Do the answers an FAQPage declares appear in the text that was served?

    The policy question is whether the markup describes content the page shows,
    and until 2026-08-14 this module answered a proxy for it — "did I see <dt>,
    <dd> or <details>" — then reported the proxy's silence as `high` /
    `CONFIRMED` "answers are absent". On an ARIA accordion, which renders the
    answer and hides it with CSS, that was a false finding about markup sitting in
    the response.

    Matching is on a normalized prefix rather than the whole string: an answer is
    routinely split across elements, and requiring the full text back would swap
    one false positive for another.
    """
    answers: list[str] = []

    def walk(node):
        if isinstance(node, dict):
            raw_t = node.get("@type")
            names = [raw_t] if isinstance(raw_t, str) else [
                x for x in (raw_t or []) if isinstance(x, str)]
            if "Question" in names:
                acc = node.get("acceptedAnswer") or {}
                text = acc.get("text") if isinstance(acc, dict) else None
                if isinstance(text, str) and text.strip():
                    answers.append(text)
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    for raw in doc.jsonld_raw:
        try:
            walk(json.loads(raw))
        except Exception:  # noqa: BLE001 - reported by _jsonld_types
            continue

    if not answers:
        return {"faq_declared": 0, "faq_declared_served": 0}
    served = " ".join(re.sub(r"<[^>]+>", " ", p) for kind, p in doc.stream if kind == "text")
    served = " ".join(served.split()).lower()
    found = 0
    for a in answers:
        probe = " ".join(re.sub(r"<[^>]+>", " ", a).split()).lower()[:60]
        if len(probe) >= 20 and probe in served:
            found += 1
    return {"faq_declared": len(answers), "faq_declared_served": found}


def analyze(html: str, url: str, headers: dict | None = None,
            truncated: bool = False) -> dict:
    parser = Parser()
    parser.feed(html)
    parser.close()
    doc = parser.doc
    headers = collapse_headers((headers or {}).items())

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

    # Parse the directives instead of pattern-matching the string they arrive in.
    directives = parse_directives(doc.robots_contents + [headers.get("x-robots-tag", "")])
    noindex = bool(NOINDEX_TOKENS & directives)
    nosnippet = "nosnippet" in directives or doc.data_nosnippet > 0

    canonical_href = doc.canonicals[0]["href"] if doc.canonicals else None
    canonical_abs = urljoin(url or "", canonical_href) if canonical_href else None
    self_ref = bool(url and canonical_abs and canonical_abs.split("#")[0] == url.split("#")[0])

    h1s = [t for tag, t in doc.headings if tag == "h1"]
    subheads = sum(1 for tag, _ in doc.headings if tag in ("h2", "h3", "h4"))
    imgs_no_alt = sum(1 for i in doc.images if i["alt"] is None)
    imgs_empty_alt = sum(1 for i in doc.images if i["alt"] == "")

    first_100 = " ".join(prose.split()[:100])
    markup = strip_inert(html)
    jsonld_price = _jsonld_price(doc)
    result = {
        "url": url,
        # Non-negotiable #8 again: a fragment is not a page. Everything below that
        # counts or fails to find something is unreliable when this is true, so it
        # travels with the numbers rather than in a log line nobody kept.
        "truncated": bool(truncated),
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
        # Markup a crawler reads as page structure, with script/style/JSON-LD
        # bodies removed — see strip_inert() for why the raw HTML is the wrong
        # haystack.
        "currency_in_source_only": (bool(CURRENCY_RE.search(markup))
                                    and not bool(CURRENCY_RE.search(text))),
        # A declared price is a separate observation with a separate fix: markup
        # that claims a price the page does not show is the parity check in
        # onpage-checks.md O1, not a JS-gated price.
        "jsonld_price_declared": jsonld_price,
        "data_nosnippet_elements": doc.data_nosnippet,
        "jsonld_blocks": len(doc.jsonld_raw),
        "jsonld_types": types,
        "jsonld_errors": jsonld_errors,
        "jsonld_missing_required": _jsonld_required(doc),
        # The Q&A shape, kept separate from the schema question it feeds. A page
        # can publish a readable FAQ with no FAQPage node (the common case) or an
        # FAQPage node over answers no crawler can reach (the worse one), and the
        # two want opposite fixes — so both halves are reported as observations.
        "qa_pairs_visible": min(doc.dt_count, doc.dd_count),
        "qa_pairs_collapsed": min(doc.details_count, doc.summary_count),
        "qa_pairs_aria": min(doc.aria_disclosure, doc.aria_panel),
        # The question the pairing counts were standing in for, asked directly:
        # of the answers an FAQPage node declares, how many are in the text this
        # response actually served? That is the structured-data policy question —
        # markup must describe content the page shows — and counting element
        # names only ever approximated it.
        **_faq_declared_vs_served(doc),
        "faq_heading": next(
            (t for _, t in doc.headings if FAQ_HEADING_RE.search(t or "")), None),
        # Non-negotiable #8: the instrument states its own blind spot, in the
        # payload, every run — not in documentation somebody may not have read.
        "jsonld_caveat": (
            "server-rendered HTML only: this parser does not execute JavaScript, "
            "so JSON-LD injected client-side (Yoast, RankMath, AIOSEO and most "
            "CMS SEO plugins) is invisible here. Zero blocks is NOT evidence of "
            "absent schema — confirm with a rendering check (GSC URL Inspection, "
            "Rich Results Test, or a JS-rendering crawl) before reporting it."
        ),
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
    """Deterministic checks. Each finding names the observation, not a guess.

    Two rules hold for everything below. Each finding carries its evidence tier
    from FINDING_TIERS, because the tier is what the triage formula multiplies by.
    And on a truncated read every finding in COMPLETENESS_DEPENDENT is dropped: a
    count taken from a fragment is not an observation about the page.
    """
    out: list[dict] = []

    def add(sev, code, msg, ref):
        out.append({"severity": sev, "code": code, "message": msg, "reference": ref,
                    "tier": FINDING_TIERS.get(code, "HYPOTHESIS")})

    if r.get("truncated"):
        add("high", "truncated-read",
            "the response was cut off by --max-bytes, so this page was analyzed as a "
            "fragment: every count below (words, links, subheads, images, read budget) "
            "is a lower bound and every absence is unverified. Re-run with a larger "
            "--max-bytes before reporting any of it",
            "technical-checks.md#a1-crawl-access-and-rendering")

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
        _where = []
        if "nosnippet" in " ".join(r["meta_robots"]).lower() or (
                "nosnippet" in (r["x_robots_tag"] or "").lower()):
            _where.append("a page-level nosnippet directive")
        if r.get("data_nosnippet_elements"):
            _where.append(f"{r['data_nosnippet_elements']} element(s) carrying data-nosnippet")
        add("high", "nosnippet",
            f"{' and '.join(_where) or 'nosnippet'} gates what answer engines may quote "
            "from this page; preview control is the highest-weighted citation factor the "
            "publisher fully controls",
            "aeo-geo.md#f3-extractability--the-part-most-audits-skip")
    if r["h1_count"] == 0:
        add("medium", "h1-missing", "no H1 on the page",
            "onpage-checks.md#o1-can-crawlers-understand-what-the-page-is-about")
    elif r["h1_count"] > 1:
        # onpage-checks.md O1 and myths.md are explicit that the count is not a
        # ranking issue. Reported as the accessibility note it is, with the reason
        # attached, so nobody turns it back into "consolidate to one H1".
        add("info", "h1-multiple",
            f"{r['h1_count']} H1 elements. Google states one and several both work, with no "
            "rank penalty for the count — this is a document-structure and screen-reader "
            "note, not an SEO finding. What is worth auditing is the meaning: check the "
            "mobile H1 still names the subject",
            "onpage-checks.md#o1-can-crawlers-understand-what-the-page-is-about")
    # The subhead optimum was measured on pages long enough to carry sections;
    # onpage-checks.md O1 scopes the failure to "0-3 subheads on a long page", so a
    # four-section pricing page is not the case the study describes.
    if r["subheads_h2_h4"] < 4 and r["word_count"] >= 600:
        add("medium", "subheads-thin",
            f"{r['subheads_h2_h4']} H2–H4 subheads on {r['word_count']} words of prose; "
            "4–10 is the observed citation optimum (33.2% vs 28% for 1–3)",
            "aeo-geo.md#f2-what-correlates-with-being-cited-ranked-evidence")
    # Not a length verdict. The reference this points at measured length and found
    # it barely matters; what a very short body does affect is how much there is to
    # extract and quote. Report the observation, name what it is not.
    if r["word_count"] < 300:
        add("medium", "low-extractable-text",
            f"only {r['word_count']} words of extractable prose (link labels excluded; "
            f"{r['link_text_words']} more words sit in link text). Length itself is not a "
            "ranking signal — the study behind this reference found it barely correlates — "
            "so treat this as 'little for an engine to quote', and judge the page on "
            "information gain and task completion instead",
            "intent-and-content.md#e2-information-gain")
    if r["title_len"] == 0:
        add("high", "title-missing", "no <title>", "technical-checks.md")
    if r["meta_description_len"] == 0:
        add("info", "description-missing", "no meta description", "technical-checks.md")
    if r["jsonld_errors"]:
        add("high", "jsonld-invalid",
            f"invalid JSON-LD ({r['jsonld_errors'][0]})", "entity-and-brand.md#g3-knowledge-graph-plumbing")
    if r["jsonld_missing_required"]:
        add("medium", "jsonld-incomplete",
            "JSON-LD node missing a structural property: "
            + ", ".join(r["jsonld_missing_required"][:4])
            + " (eligibility for any rich result still needs the Rich Results Test)",
            "entity-and-brand.md#g3-knowledge-graph-plumbing")
    if r["jsonld_blocks"] and not r["jsonld_types"] and not r["jsonld_errors"]:
        add("medium", "jsonld-untyped", "JSON-LD present with no @type",
            "entity-and-brand.md#g3-knowledge-graph-plumbing")

    # --- the Q&A block: is there one, can a machine read it, is it declared ---
    #
    # Three separate observations that people routinely collapse into "add FAQ
    # schema". They have different fixes and two of them are about the DOM, not
    # the markup: an answer behind <details> is a click away from a crawler, and
    # a page that hides its answers gains nothing from declaring them.
    qa_visible = r["qa_pairs_visible"]
    qa_collapsed = r["qa_pairs_collapsed"]
    qa_aria = r["qa_pairs_aria"]
    qa_any = qa_visible or qa_collapsed or qa_aria
    has_faq_schema = "FAQPage" in r["jsonld_types"]
    declared, declared_served = r["faq_declared"], r["faq_declared_served"]

    if qa_collapsed >= 3:
        add("medium", "faq-collapsed",
            f"{qa_collapsed} answers sit inside <details>/<summary>, so each one is a click "
            "away rather than text on the page. Browsers do expose <details> content to "
            "the accessibility tree and Google can index it, but an extracted answer is "
            "drawn from what renders — a definition list (<dl>/<dt>/<dd>) left open costs "
            "nothing and removes the question entirely",
            "aeo-geo.md#f8-the-qa-block-which-is-three-problems")
    if r["faq_heading"] and not qa_any and declared_served == 0:
        add("medium", "faq-unpaired",
            f"a heading announces a Q&A block ({_flat(r['faq_heading'], 60)!r}) but no "
            "<dt>/<dd>, <details>/<summary> or ARIA disclosure pairing was found and no "
            "declared answer text appears in the served body, so nothing marks which text "
            "is the question and which is the answer. Pair them structurally before "
            "declaring them in schema",
            "aeo-geo.md#f8-the-qa-block-which-is-three-problems")
    if qa_visible >= 3 and not has_faq_schema:
        add("low", "faq-schema-absent",
            f"{qa_visible} question/answer pairs are readable in the served markup and no "
            "FAQPage node declares them. The answers are already extractable, so this is a "
            "declaration gap, not a visibility one — and the payoff is small: Google "
            "restricted FAQ rich results in August 2023 and then discontinued them, so what "
            "remains is entity clarity and the non-Google engines that parse schema. Do not "
            "report this as a rich-result opportunity",
            "aeo-geo.md#f8-the-qa-block-which-is-three-problems")
    # An orphan is a node whose ANSWERS are missing from the response, and that is
    # now what gets checked. The pairing counts stay as the fallback for a node
    # this parser could not read answers out of; they are no longer allowed to
    # assert absence on their own, which is what made this fire at `high` /
    # `CONFIRMED` on an ARIA accordion whose answers were in the HTML.
    if has_faq_schema and declared and declared_served == 0:
        add("high", "faq-schema-orphan",
            f"an FAQPage node declares {declared} answer(s) and none of them appears in "
            "the served body text. Schema must describe content the page actually shows; "
            "a node whose answers are absent (or injected client-side) is a mismatch, and "
            "Google's structured-data policy treats invisible marked-up content as a "
            "violation",
            "aeo-geo.md#f8-the-qa-block-which-is-three-problems")
    elif has_faq_schema and declared and declared_served < declared:
        add("medium", "faq-schema-partial",
            f"{declared - declared_served} of {declared} declared answers are not in the "
            "served body text. The rest are — so this is a drift between the node and the "
            "page rather than a client-rendered block, and the usual cause is an answer "
            "edited in one of the two places",
            "aeo-geo.md#f8-the-qa-block-which-is-three-problems")
    elif has_faq_schema and not declared and not qa_any:
        add("medium", "faq-schema-unreadable",
            "an FAQPage node is declared, no acceptedAnswer text could be read out of it, "
            "and no Q&A pairing was found in the markup. Absence is not established here — "
            "the node may be malformed or assembled client-side; confirm with a rendering "
            "check before reporting it as a mismatch",
            "aeo-geo.md#f8-the-qa-block-which-is-three-problems")

    rb = r["read_budget"]
    if rb["content_pct"] < 55:
        add("high", "read-budget",
            f"only {rb['content_pct']}% of the first ~{rb['window_chars']} characters is content; "
            f"{rb['link_marker_pct']}% is link markers "
            f"({rb['links_before_first_text']} links before the first text). That window is the "
            "median measured on ChatGPT Deep Research, not a budget every answer engine "
            "enforces — treat the share as the finding and the window as one engine's median",
            "architecture-and-equity.md#read-budget-navigation-now-costs-you-twice")
    elif rb["links_before_first_text"] >= 20:
        add("medium", "nav-before-content",
            f"{rb['links_before_first_text']} links appear before the first text in source order, "
            "which spends the opening of the read on navigation (median window measured on "
            "ChatGPT Deep Research)",
            "architecture-and-equity.md#read-budget-navigation-now-costs-you-twice")
    if r["links_total"] >= 60:
        add("medium", "link-count",
            f"{r['links_total']} links on the page; in the same Deep Research measurement pages "
            "above 60 links spent ~33% of the first read on content",
            "architecture-and-equity.md#read-budget-navigation-now-costs-you-twice")
    if r["images_missing_alt"]:
        add("medium", "alt-missing",
            f"{r['images_missing_alt']} image(s) without an alt attribute; alt text is the only image "
            "content answer engines read",
            "aeo-geo.md#f3-extractability--the-part-most-audits-skip")
    if r["currency_in_source_only"]:
        add("high", "price-not-in-text",
            "a currency symbol appears in the page markup (an attribute, an image name) but "
            "not in extractable text — a JS-gated or image-only price. Engines that grep raw "
            "HTML for a number then cite an aggregator for your pricing instead",
            "aeo-geo.md#f3-extractability--the-part-most-audits-skip")
    if r.get("jsonld_price_declared") and not r["currency_in_text"]:
        add("medium", "jsonld-price-parity",
            "JSON-LD declares a price that does not appear in the page's extractable text. "
            "Markup has to match visible content: this is the parity check, not proof the "
            "price is JS-gated — confirm which by looking at the rendered page",
            "onpage-checks.md#o1-can-crawlers-understand-what-the-page-is-about")
    if r.get("truncated"):
        out = [f for f in out if f["code"] not in COMPLETENESS_DEPENDENT]
    return out


# --- io --------------------------------------------------------------------


ALLOWED_SCHEMES = ("http", "https")
# Analyzing a PDF or an image as HTML produces confident nonsense; refuse it
# instead. A response with no Content-Type at all is still parsed.
HTML_CONTENT_TYPES = ("text/html", "application/xhtml+xml", "application/xml", "text/xml")


class _SchemeGuardRedirectHandler(HTTPRedirectHandler):
    """Refuse redirects that leave http(s) — e.g. a 302 to file:// or ftp://."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if urlparse(newurl).scheme.lower() not in ALLOWED_SCHEMES:
            raise ValueError(f"refusing redirect to non-http(s) URL: {newurl}")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def collapse_headers(items) -> dict:
    """Lower-case header map that keeps repeated headers instead of dropping them.

    `X-Robots-Tag` is legitimately sent more than once (`noindex` on one line,
    `nosnippet` on the next); a plain dict() would keep only the last and hide a
    blocker.
    """
    out: dict[str, str] = {}
    for key, value in items:
        key = key.lower()
        out[key] = f"{out[key]}, {value}" if key in out else value
    return out


def _gunzip(raw: bytes) -> tuple[bytes, bool]:
    """Decompress a gzip body. Returns (bytes, salvaged_from_truncated_stream)."""
    try:
        return gzip.decompress(raw), False
    except Exception:  # noqa: BLE001 - truncated stream: salvage what decoded
        try:
            salvaged = zlib.decompressobj(zlib.MAX_WBITS | 16).decompress(raw)
        except zlib.error:
            salvaged = b""
        if not salvaged:
            raise ValueError(
                "gzip response could not be decompressed (raise --max-bytes if the page is larger)"
            ) from None
        return salvaged, True


def fetch(url: str, timeout: float, user_agent: str,
          max_bytes: int) -> tuple[str, dict, bool]:
    """Fetch one page over http(s). Returns (text, headers, truncated).

    The auditor only ever issues plain GETs to URLs the operator passed in: no
    credentials, no cookies, no redirects off http(s), and nothing is written
    anywhere. The scheme guard matters because `urlopen` would otherwise happily
    read `file:///etc/passwd` from a `--url-list`.

    `truncated` is the third return value and not a log line, because every number
    downstream is computed on what came back: a page cut off at --max-bytes
    produced word counts, link totals and a read-budget share that read as
    measurements of the whole page. One byte past the cap is read deliberately so
    the difference between "fits" and "was cut" is observable rather than inferred.
    """
    scheme = urlparse(url).scheme.lower()
    if scheme not in ALLOWED_SCHEMES:
        raise ValueError(f"unsupported URL scheme {scheme or '(none)'!r}: only http and https are fetched")

    opener = build_opener(_SchemeGuardRedirectHandler)
    req = Request(url, headers={"User-Agent": user_agent, "Accept-Encoding": "gzip"})
    with opener.open(req, timeout=timeout) as resp:
        declared = resp.headers.get("Content-Type")
        if declared and declared.split(";")[0].strip().lower() not in HTML_CONTENT_TYPES:
            raise ValueError(f"not an HTML document (Content-Type: {declared.strip()})")
        raw = resp.read(max_bytes + 1)
        truncated = len(raw) > max_bytes
        raw = raw[:max_bytes]
        headers = collapse_headers(resp.headers.items())
        if (headers.get("content-encoding") or "").lower() == "gzip":
            raw, salvaged = _gunzip(raw)
            truncated = truncated or salvaged
        charset = resp.headers.get_content_charset() or "utf-8"
    return raw.decode(charset, errors="replace"), headers, truncated


# `low` sat between `medium` and `info` in every message this file writes and
# in none of its ordering, so to_markdown raised KeyError on the first page
# without FAQ schema — the default output mode, on the common case.
SEVERITY_ORDER = {"blocker": 0, "high": 1, "medium": 2, "low": 3, "info": 4}


def to_markdown(results: list[dict]) -> str:
    lines: list[str] = []
    for r in results:
        lines.append(f"## {r['url'] or '(local file)'}")
        lines.append("")
        if "error" in r:
            lines.append(f"- **fetch failed**: {_flat(r['error'])}")
            lines.append("")
            continue
        rb = r["read_budget"]
        if r.get("truncated"):
            lines.append(
                "- ⚠ **truncated read**: the response was cut off by `--max-bytes`, so every "
                "count below is a lower bound and no absence below is verified. Re-run with a "
                "larger `--max-bytes` before quoting any of it."
            )
        lines.append(
            f"- title ({r['title_len']} chars): {r['title'] or '—'}\n"
            f"- H1: {r['h1'] or '—'} · subheads H2–H4: {r['subheads_h2_h4']} · prose words: "
            f"{r['word_count']} (+{r['link_text_words']} in link text)\n"
            f"- canonical: {r['canonical'] or '—'}"
            f"{' (extra attrs: ' + ', '.join(r['canonical_extra_attrs']) + ')' if r['canonical_extra_attrs'] else ''}\n"
            f"- robots: {', '.join(r['meta_robots']) or '—'}"
            f"{' · X-Robots-Tag: ' + r['x_robots_tag'] if r['x_robots_tag'] else ''}\n"
            f"- JSON-LD: {r['jsonld_blocks']} block(s), types: {', '.join(r['jsonld_types']) or '—'}"
            + (f"; missing: {', '.join(r['jsonld_missing_required'])}"
               if r["jsonld_missing_required"] else "") + "\n"
            f"  - ⚠ {r['jsonld_caveat']}\n"
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
            lines.append("| severity | tier | check | finding | reference |")
            lines.append("|---|---|---|---|---|")
            for f in sorted(r["findings"], key=lambda x: SEVERITY_ORDER[x["severity"]]):
                lines.append(
                    f"| {f['severity']} | `{f.get('tier', '?')}` | `{f['code']}` | "
                    f"{f['message']} | {f['reference']} |"
                )
        else:
            lines.append("No mechanical findings on this page.")
        lines.append("")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Per-page SEO/AEO mechanical audit (stdlib only).")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--url", help="single URL to fetch and analyze")
    src.add_argument("--url-list", help="file with one URL per line")
    src.add_argument("--file", help="local HTML file (offline mode)")
    ap.add_argument("--base-url", default="", help="URL the local file represents (offline mode)")
    ap.add_argument("--format", choices=("markdown", "json"), default="markdown")
    ap.add_argument("--timeout", type=float, default=20.0)
    ap.add_argument("--user-agent", default=DEFAULT_UA)
    ap.add_argument("--max-bytes", type=int, default=5_000_000)
    args = ap.parse_args(argv)

    if args.base_url and not args.file:
        print("warning: --base-url applies to --file only; ignoring it", file=sys.stderr)

    results: list[dict] = []
    if args.file:
        try:
            with open(args.file, encoding="utf-8", errors="replace") as fh:
                html = fh.read()
        except OSError as exc:
            print(f"error: cannot read {args.file}: {exc}", file=sys.stderr)
            return 1
        results.append(analyze(html, args.base_url))
    else:
        urls = [args.url] if args.url else []
        if args.url_list:
            try:
                with open(args.url_list, encoding="utf-8") as fh:
                    urls = [
                        line for line in (ln.strip() for ln in fh)
                        if line and not line.startswith("#")
                    ]
            except OSError as exc:
                print(f"error: cannot read {args.url_list}: {exc}", file=sys.stderr)
                return 1
        if not urls:
            print("error: no URLs to audit", file=sys.stderr)
            return 1
        for url in urls:
            try:
                html, headers, truncated = fetch(url, args.timeout, args.user_agent,
                                                 args.max_bytes)
                results.append(analyze(html, url, headers, truncated=truncated))
            except Exception as exc:  # noqa: BLE001 - one bad URL must not kill the run
                results.append({"url": url, "error": f"{type(exc).__name__}: {exc}", "findings": []})

    # The producer rides on EVERY element rather than wrapping the array, because
    # `--format json` emits an array by documented contract (line 17) and a caller
    # doing `jq '.[].url'` would break on an envelope. One block per element also
    # means a page pulled out of the array on its own still knows what produced it —
    # which is exactly how a finding reaches a ticket.
    #
    # `observed_at` is the moment the payload was emitted, not the moment each URL
    # was fetched. On a long `--url-list` run those differ by the length of the
    # crawl, and this says so rather than implying per-page precision it does not
    # have.
    scope = (f"local file {args.file}"
             + (f" as {args.base_url}" if args.base_url else "")
             if args.file else
             f"{len(results)} URL(s): " + ", ".join(r.get("url", "?") for r in results[:5])
             + (f" (+{len(results) - 5} more)" if len(results) > 5 else ""))
    prov = provenance("page_audit.py", argv, scope)
    if args.format == "json":
        for r in results:
            r["producer"] = prov
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print(to_markdown(results))
        print("\n" + provenance_md(prov))
    # A run that analyzed nothing is not a success, whatever the docstring used to
    # say. Partial failure keeps exit 0 — the error rows are the report — but a run
    # where every URL failed must not look like one where every URL was clean.
    if results and all("error" in r for r in results):
        print("error: every URL failed; no page was analyzed", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
