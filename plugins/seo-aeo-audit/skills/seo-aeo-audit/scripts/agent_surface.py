#!/usr/bin/env python3
"""agent_surface — track K evidence: what a machine finds when it arrives alone.

Tracks A-J ask whether a retrieval system can fetch, read and quote the site.
This collects the other question: whether an agent acting for a user can discover
the product, get a credential, call it, and recover when a call fails.
`references/agent-readiness.md` owns the reasoning; this owns the requests.

stdlib only. Every check is one HTTP request or one parse, and each one prints the
URL and status it rests on, because the finding this instrument exists to prevent
is a scanner reporting absence it never probed.

Usage:
  agent_surface.py --origin https://example.com
  agent_surface.py --origin https://example.com --api-origin https://api.example.com
  agent_surface.py --openapi https://example.com/openapi.json
  agent_surface.py --openapi-file spec.json          # offline
  agent_surface.py --origin https://example.com --format json > agent.json

--format json emits ONE object (not an array): the surface is a property of a
site, not of a list of pages. `data["findings"]` is the list.

WHAT THIS INSTRUMENT CANNOT SEE (non-negotiable #8 — state the blind spot in the
output, not only in the docs):

  * **Presence is not effect.** Every check here answers "is it there", which is
    `CONFIRMED`. Whether shipping it changes an outcome is a separate claim and
    mostly `HYPOTHESIS` — agent-readiness.md K1 carries the split, and the tier
    that reaches the triage formula is the one on the *effect*, not the probe.
  * **One URL is not a site.** The JSON-LD and markup checks run against the URL
    you name (the origin root by default). "No FAQPage found" means *on that
    page*; product templates routinely carry markup the homepage does not. Pass
    --page for each template before writing a sitewide finding.
  * **Server-rendered HTML only**, like page_audit.py: markup a CMS injects with
    JavaScript is invisible here, so an empty inventory is not evidence of absent
    markup.
  * **A draft spec's absence is not a defect.** Most of the .well-known set is
    draft or vendor convention. This reports what is missing; agent-readiness.md
    K8/K9 decides what is worth shipping, and a business decision (a public repo,
    an npm package, a directory listing) is never inferable from a fetch.

Exit codes: 0 = at least one probe answered, 1 = usage error, or nothing answered
(a run where every request failed is not a measurement of an absent surface).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

UA = "seo-aeo-audit/agent_surface (+https://github.com/ssheleg/seo-aeo-audit)"
TIMEOUT = 20
MAX_BYTES = 2_000_000

# Every finding carries an evidence tier as well as a severity: SKILL.md
# non-negotiable #2 makes the tier the confidence multiplier in
# `priority = (impact x confidence) / effort`. These are the tiers of the EFFECT,
# not of the probe — the probe is always CONFIRMED, which is exactly the
# confusion agent-readiness.md K1 exists to prevent. Declared once so a reader can
# audit them against K8's table.
FINDING_TIERS = {
    "agent-404-soft": "CONFIRMED",
    "agent-404-no-recovery": "HYPOTHESIS",
    "openapi-operationid": "CONFIRMED",
    "openapi-description": "CONFIRMED",
    "openapi-response-schema": "CONFIRMED",
    "openapi-error-shapes": "STUDY",
    "openapi-async": "STUDY",
    "openapi-batch": "STUDY",
    "openapi-deprecation": "STUDY",
    "api-401-no-hint": "STUDY",
    "api-no-ratelimit-headers": "STUDY",
    "auth-discovery-broken": "STUDY",
    "no-link-headers": "HYPOTHESIS",
    "markdown-no-negotiation": "HYPOTHESIS",
    "markdown-no-vary": "CONFIRMED",
    "markdown-alternate-unadvertised": "HYPOTHESIS",
    "markdown-alternate-lies": "CONFIRMED",
    "bot-ua-divergence": "CONFIRMED",
    "robots-ai-undeclared": "HYPOTHESIS",
    "robots-training-undecided": "HYPOTHESIS",
    "robots-no-schemamap": "HYPOTHESIS",
    "llms-txt-absent": "HYPOTHESIS",
    "llms-txt-no-when-to-use": "HYPOTHESIS",
    "wellknown-absent": "HYPOTHESIS",
    "sitemap-lastmod-thin": "STUDY",
    "jsonld-no-sameas": "STUDY",
    "jsonld-sameas-thin": "STUDY",
    "jsonld-no-address": "STUDY",
    "jsonld-narrow-types": "STUDY",
    "jsonld-no-speakable": "HYPOTHESIS",
    "entry-point-unlinked": "CONFIRMED",
    "entry-point-missing": "STUDY",
    "trust-anchor-missing": "STUDY",
    "trust-anchor-thin": "HYPOTHESIS",
    "entry-point-bounces-to-root": "CONFIRMED",
}

# The three uses a robots.txt has to tell apart (agent-readiness.md K2a).
ANSWER_ENGINE_UAS = ("gptbot", "oai-searchbot", "chatgpt-user", "claudebot",
                     "claude-user", "perplexitybot", "google-extended")
TRAINING_ONLY_UAS = ("ccbot", "bytespider")

# Draft/vendor discovery documents. `required` is never True: none of these is a
# standard a site is obliged to serve, and a checklist that says otherwise is the
# cargo cult K7 warns about.
WELL_KNOWN = (
    ("/.well-known/api-catalog", "RFC 9727 API catalog"),
    ("/.well-known/oauth-protected-resource", "RFC 9728 protected-resource metadata"),
    ("/.well-known/oauth-authorization-server", "RFC 8414 authorization-server metadata"),
    ("/.well-known/http-message-signatures-directory", "Web Bot Auth key directory"),
    ("/.well-known/agent-card.json", "A2A agent card"),
    ("/.well-known/mcp/server-card.json", "MCP server card"),
    ("/.well-known/ai-catalog.json", "ARD agentic-resource catalog"),
    ("/.well-known/agent-skills/index.json", "Agent Skills index"),
    ("/auth.md", "agent credential walkthrough"),
)

# Types beyond the two every site emits. Their absence on ONE page is not a
# sitewide finding — see the blind-spot block above.
BASELINE_TYPES = {"organization", "website", "webpage", "imageobject", "breadcrumblist",
                  "listitem", "contactpoint", "country"}

# The addresses a machine tries before it asks anyone (agent-readiness.md K2b).
# Alternates per role, most conventional first — the role is what matters, not the
# spelling. A role is PRESENT if any alternate answers 200; probing stops there.
#
# `anchor` marks the roles a verifier reads to decide the business is real, which
# is why they carry a length check as well as a status check.
ENTRY_POINTS = (
    ("developer docs", ("/api", "/docs", "/developers", "/api-docs", "/developer"), False),
    ("sign-up", ("/register", "/signup", "/sign-up", "/join"), False),
    ("pricing", ("/pricing", "/plans", "/plans-and-pricing"), False),
    ("about", ("/about", "/about-us", "/company"), True),
    ("contact", ("/contact", "/contact-us", "/support"), True),
    ("privacy", ("/privacy", "/privacy-policy"), True),
    ("terms", ("/terms", "/terms-of-service", "/tos"), True),
)

# The conventional bar third-party verifiers apply to a trust page. It is a
# CONVENTION, not a measured threshold — the finding says so, and its tier is set
# accordingly. The mechanism underneath it is real (entity-and-brand.md G3: brand
# pages are the minimum viable entity definition); the number is not.
TRUST_ANCHOR_MIN_CHARS = 500


def _flat(text: str, limit: int = 200) -> str:
    """One line, safe inside a table cell, capped.

    Network errors arrive as HTML error pages and pretty-printed JSON. Interpolated
    raw into a markdown row, the first newline ends the row and every row after it
    stops rendering — so the report becomes unreadable exactly where it is carrying
    the failure. Duplicated in each collector rather than imported: these ship as
    standalone files with no shared module, so `test/validate.py` counts the homes.
    """
    one = " ".join(str(text).split())
    one = one.replace("|", "\\|")
    return one[:limit] + ("…" if len(one) > limit else "")


# --- transport ---------------------------------------------------------------


class Probe:
    """One request and what came back. A probe that never ran is not evidence."""

    def __init__(self, url: str, status, ctype: str = "", body: str = "",
                 headers=None, error: str = "", final_url: str = ""):
        self.url = url
        self.status = status
        self.ctype = ctype
        self.body = body
        self.headers = {k.lower(): v for k, v in (headers or {}).items()}
        self.error = error
        # Where the request ACTUALLY landed. urlopen follows redirects, so a probe
        # that reports 200 may be describing a completely different page — and it
        # will describe it convincingly, with a title and a word count. Found by
        # running this script against a live site: /about-us answered "200, 1564
        # characters" and was a 301 to the homepage. An instrument that credits a
        # redirect as the page you asked for manufactures the finding it exists to
        # measure (non-negotiable #8).
        self.final_url = final_url or url

    @property
    def answered(self) -> bool:
        """Did the server speak at all? A 404 answered; a DNS failure did not."""
        return self.status is not None


def fetch(url: str, accept: str = "", user_agent: str = UA) -> Probe:
    if urlparse(url).scheme not in ("http", "https"):
        return Probe(url, None, error="refused: not an http(s) URL")
    headers = {"User-Agent": user_agent, "Accept-Encoding": "identity"}
    if accept:
        headers["Accept"] = accept
    req = Request(url, headers=headers)
    try:
        with urlopen(req, timeout=TIMEOUT) as r:
            raw = r.read(MAX_BYTES)
            return Probe(url, r.status, r.headers.get("Content-Type", ""),
                         raw.decode("utf-8", "replace"), dict(r.headers),
                         final_url=getattr(r, "url", "") or url)
    except HTTPError as e:
        raw = b""
        try:
            raw = e.read(MAX_BYTES)
        except Exception:  # noqa: BLE001 - a body we cannot read is still a status
            pass
        return Probe(url, e.code, e.headers.get("Content-Type", "") if e.headers else "",
                     raw.decode("utf-8", "replace"), dict(e.headers or {}))
    except (URLError, OSError, ValueError) as exc:
        return Probe(url, None, error=str(exc)[:160])


# --- pure analysis (tested offline) ------------------------------------------


def parse_robots(text: str) -> dict:
    """Which AI groups a robots.txt names, and whether it decided about training."""
    named = set()
    for m in re.finditer(r"^\s*user-agent:\s*(\S+)", text, re.I | re.M):
        named.add(m.group(1).strip().lower())
    return {
        "answer_engines_named": sorted(u for u in ANSWER_ENGINE_UAS if u in named),
        "answer_engines_missing": sorted(u for u in ANSWER_ENGINE_UAS if u not in named),
        "training_named": sorted(u for u in TRAINING_ONLY_UAS if u in named),
        "has_content_signal": bool(re.search(r"^\s*content-signal:", text, re.I | re.M)),
        "has_schemamap": bool(re.search(r"^\s*schemamap:", text, re.I | re.M)),
        "sitemaps": re.findall(r"^\s*sitemap:\s*(\S+)", text, re.I | re.M),
    }


def lastmod_stats(sitemap_xml: str) -> dict:
    """<lastmod> coverage. Absence is a fact; it is not a zero date."""
    urls = re.findall(r"<url>(.*?)</url>", sitemap_xml, re.S)
    if not urls:
        return {"urls": 0, "with_lastmod": 0, "pct": None, "newest": None}
    with_lm = sum(1 for u in urls if "<lastmod>" in u)
    dates = sorted(re.findall(r"<lastmod>\s*([0-9T:+\-]{10,})", sitemap_xml))
    return {"urls": len(urls), "with_lastmod": with_lm,
            "pct": round(with_lm * 100 / len(urls)),
            "newest": dates[-1][:10] if dates else None}


def scan_jsonld(html: str) -> dict:
    """Types, sameAs targets and the two properties a verifier looks for.

    Server-rendered HTML only. An empty inventory on a JS-injecting CMS is a false
    finding, which is why the caller prints the caveat with the numbers.
    """
    blocks = re.findall(
        r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html, re.S | re.I)
    types: list = []
    same_as: list = []
    invalid = 0
    has_address = False
    has_contact = False

    def walk(node):
        nonlocal has_address, has_contact
        if isinstance(node, dict):
            t = node.get("@type")
            if isinstance(t, str):
                types.append(t)
            elif isinstance(t, list):
                types.extend(x for x in t if isinstance(x, str))
            if "address" in node or t == "PostalAddress":
                has_address = True
            if "contactPoint" in node or t == "ContactPoint":
                has_contact = True
            sa = node.get("sameAs")
            if isinstance(sa, str):
                same_as.append(sa)
            elif isinstance(sa, list):
                same_as.extend(x for x in sa if isinstance(x, str))
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    for b in blocks:
        try:
            walk(json.loads(b))
        except (ValueError, TypeError):
            invalid += 1
    lowered = {t.lower() for t in types}
    return {
        "blocks": len(blocks),
        "invalid_blocks": invalid,
        "types": sorted(set(types)),
        "extended_types": sorted(t for t in set(types) if t.lower() not in BASELINE_TYPES),
        "same_as": same_as,
        "has_address": has_address,
        "has_contact_point": has_contact,
        "has_speakable": "speakable" in html.lower(),
        "markdown_alternate": re.findall(
            r'<link[^>]+type=["\']text/markdown["\'][^>]*>', html, re.I),
        "_baseline_only": not (lowered - BASELINE_TYPES),
    }


def analyze_openapi(spec: dict) -> dict:
    """Per-operation function-calling readiness. Offline; no network."""
    methods = ("get", "post", "put", "patch", "delete", "options", "head")
    ops = []
    for path, item in (spec.get("paths") or {}).items():
        if not isinstance(item, dict):
            continue
        for method, op in item.items():
            if method.lower() not in methods or not isinstance(op, dict):
                continue
            responses = op.get("responses") or {}
            ok = {c: r for c, r in responses.items() if str(c).startswith("2")}
            ops.append({
                "method": method.upper(),
                "path": path,
                "operation_id": op.get("operationId"),
                "described": bool(op.get("description") or op.get("summary")),
                "success_schema": any(isinstance(r, dict) and r.get("content")
                                      for r in ok.values()),
                "codes": sorted(str(c) for c in responses),
                "deprecated": bool(op.get("deprecated")),
            })
    blob = json.dumps(spec).lower()
    all_codes = {c for o in ops for c in o["codes"]}
    return {
        "operations": len(ops),
        "with_operation_id": sum(1 for o in ops if o["operation_id"]),
        "duplicate_operation_ids": sorted(
            {o["operation_id"] for o in ops
             if o["operation_id"] and
             [x["operation_id"] for x in ops].count(o["operation_id"]) > 1}),
        "with_description": sum(1 for o in ops if o["described"]),
        "with_success_schema": sum(1 for o in ops if o["success_schema"]),
        "declares_401": "401" in all_codes,
        "declares_429": "429" in all_codes,
        "has_async_202": "202" in all_codes,
        "has_batch_path": any(re.search(r"/(batch|bulk)\b", o["path"], re.I) for o in ops),
        "has_deprecation_policy": ("sunset" in blob or "deprecation" in blob
                                   or any(o["deprecated"] for o in ops)),
        "security_schemes": sorted((spec.get("components") or {})
                                   .get("securitySchemes", {}) or {}),
        "servers": [s.get("url") for s in (spec.get("servers") or []) if isinstance(s, dict)],
        "ops": ops,
    }


def negotiation_verdict(probe: Probe) -> dict:
    """Did `Accept: text/markdown` get markdown, and is the Vary header honest?"""
    ctype = (probe.ctype or "").lower()
    vary = (probe.headers.get("vary") or "")
    return {
        "content_type": probe.ctype or "",
        "served_markdown": "text/markdown" in ctype,
        "vary": vary,
        "vary_has_accept": bool(re.search(r"(^|,)\s*accept\s*(,|$)", vary, re.I)),
    }


def same_origin_links(html: str, origin: str) -> set:
    """Every same-origin path the SERVER-RENDERED html links to, normalized.

    This is the whole point of the check it feeds: a link a framework adds during
    hydration is not in this set, and a crawler, an answer engine and an agent all
    read the document before that happens. Locale prefixes are stripped so
    `/de/api` counts as a link to `/api` — otherwise a nine-locale site reports
    seven false gaps.
    """
    origin = (origin or "").rstrip("/")
    out = set()
    for href in re.findall(r'<a\b[^>]*?href=["\']([^"\']+)["\']', html, re.I):
        href = href.strip()
        if href.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue
        if href.startswith("http"):
            if not origin or not href.startswith(origin):
                continue          # off-site links say nothing about reachability
            href = href[len(origin):] or "/"
        elif not href.startswith("/"):
            continue              # relative-to-page links: not resolvable here
        path = href.split("?")[0].split("#")[0].rstrip("/") or "/"
        # /de/api and /api are the same destination for this question.
        m = re.match(r"^/([a-z]{2}(?:-[a-z]{2})?)(/.*)$", path)
        if m:
            out.add(m.group(2).rstrip("/") or "/")
        out.add(path)
    return out


def landed_where(probe: Probe, origin: str) -> str:
    """Did the probe land on the page it asked for? Returns a verdict string.

    `same` — the final URL is the requested path.
    `root` — it redirected to the site root. The page does NOT exist: a 301 to the
             homepage is how a site says "no such page" while answering 200, and
             every content measurement taken after that describes the homepage.
    `elsewhere` — it redirected to some other path; a human decides whether that
             still serves the role.
    """
    origin = (origin or "").rstrip("/")
    req = urlparse(probe.url).path.rstrip("/") or "/"
    fin = urlparse(probe.final_url or probe.url).path.rstrip("/") or "/"
    if req == fin:
        return "same"
    return "root" if fin == "/" else "elsewhere"


def visible_text_length(html: str) -> int:
    """Characters a reader sees, script/style stripped. Server-rendered only."""
    body = re.sub(r"<script\b.*?</script>", " ", html, flags=re.S | re.I)
    body = re.sub(r"<style\b.*?</style>", " ", body, flags=re.S | re.I)
    body = re.sub(r"<!--.*?-->", " ", body, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", body)
    return len(re.sub(r"\s+", " ", text).strip())


def looks_like_markdown(body: str, ctype: str) -> bool:
    """A markdown body leads with a heading; an app shell leads with a doctype."""
    if "text/markdown" in (ctype or "").lower():
        return True
    head = body.lstrip()[:400].lower()
    if head.startswith(("<!doctype", "<html")):
        return False
    return body.lstrip().startswith("#") or body.lstrip().startswith("---")


# --- collection --------------------------------------------------------------


def collect(origin: str, api_origin: str = "", page: str = "",
            spec_url: str = "", spec_obj: dict | None = None,
            expect: tuple = ()) -> dict:
    """`expect` adds project-specific entry points as (role, (paths,), is_anchor)."""
    origin = origin.rstrip("/") if origin else ""
    checks: list = []
    findings: list = []
    answered = 0

    def note(name, probe: Probe, detail: str = ""):
        nonlocal answered
        if probe.answered:
            answered += 1
        checks.append({"check": name, "url": probe.url,
                       "status": probe.status if probe.answered else "no answer",
                       "content_type": probe.ctype,
                       "detail": detail or probe.error})
        return probe

    def add(sev, code, msg, ref):
        findings.append({"severity": sev, "code": code, "message": msg,
                         "reference": ref,
                         "tier": FINDING_TIERS.get(code, "HYPOTHESIS")})

    out: dict = {"origin": origin, "api_origin": api_origin or None}

    if origin:
        # --- 1. does a missing path say so ----------------------------------
        p = note("404 shape", fetch(f"{origin}/agent-surface-probe-404-check"))
        if p.answered:
            if p.status == 200:
                add("blocker", "agent-404-soft",
                    "an unknown path answers HTTP 200 — every path looks real to an agent",
                    "agent-readiness.md#k6-runtime-behaviour-an-agent-depends-on")
            elif not looks_like_markdown(p.body, p.ctype):
                add("low", "agent-404-no-recovery",
                    f"HTTP {p.status} for unknown paths (correct) but the body is not a "
                    "short markdown recovery pointing at the sitemap or docs index",
                    "agent-readiness.md#k6-runtime-behaviour-an-agent-depends-on")

        # --- 2. the homepage, three ways ------------------------------------
        home = note("homepage (default UA)", fetch(origin + "/"))
        md_probe = note("homepage (Accept: text/markdown)",
                        fetch(origin + "/", accept="text/markdown"))
        neg = negotiation_verdict(md_probe)
        out["markdown_negotiation"] = neg
        if md_probe.answered and not neg["served_markdown"]:
            add("low", "markdown-no-negotiation",
                f"Accept: text/markdown returned {_flat(neg['content_type'])} — no markdown "
                "representation for an agent that arrived without reading llms.txt",
                "agent-readiness.md#k3-markdown-representations--where-the-myth-ends-and-the-contract-begins")
        elif neg["served_markdown"] and not neg["vary_has_accept"]:
            add("high", "markdown-no-vary",
                f"markdown is served by negotiation but Vary is {_flat(neg['vary'] or 'absent')} "
                "— a CDN will hand the cached HTML to an agent asking for markdown",
                "agent-readiness.md#k3-markdown-representations--where-the-myth-ends-and-the-contract-begins")

        bot = note("homepage (ClaudeBot UA)", fetch(origin + "/", user_agent="ClaudeBot/1.0"))
        if home.answered and bot.answered and home.body and bot.body:
            # Reported as a fact in BOTH directions: serving bots something else is
            # the mechanical definition of cloaking (threats-and-defense.md), and
            # serving them the same thing is not a defect.
            if len(bot.body) != len(home.body) and abs(len(bot.body) - len(home.body)) > 512:
                add("info", "bot-ua-divergence",
                    f"a bot UA receives a different body ({len(bot.body)} vs {len(home.body)} "
                    "bytes) — verify it is a faithful representation, not divergent content",
                    "agent-readiness.md#k3-markdown-representations--where-the-myth-ends-and-the-contract-begins")
        out["bot_ua_bytes"] = {"default": len(home.body) if home.answered else None,
                               "claudebot": len(bot.body) if bot.answered else None}

        # --- 2b. entry points, and the link that only exists after hydration --
        # The highest-value check in this script and the cheapest to get wrong:
        # a link the framework adds during hydration is invisible to everything
        # that reads the document, and it looks present to every human who opens
        # the page in a browser. Reachability, not equity — track C owns equity.
        if home.answered and home.body:
            linked = same_origin_links(home.body, origin)
            out["root_links"] = sorted(linked)
            roles = []
            for role, alternates, is_anchor in ENTRY_POINTS + tuple(expect):
                found_path, found_probe, last = "", None, None
                bounced = []          # alternates that 200'd by redirecting to the root
                for alt in alternates:
                    last = fetch(origin + alt)
                    if not (last.answered and last.status == 200):
                        continue
                    where = landed_where(last, origin)
                    if where == "root":
                        # A 301 to the homepage is not a page. Counting it is how a
                        # checklist reports an About page that does not exist.
                        bounced.append(alt)
                        continue
                    found_path, found_probe = alt, last
                    note(f"entry point: {role}", last,
                         "" if where == "same" else f"redirected to {_flat(last.final_url, 80)}")
                    break
                if not found_path:
                    detail = (f"{', '.join(bounced)} → 301 to the site root, which is not a page"
                              if bounced else
                              f"none of {', '.join(alternates) or '(no paths given)'} answered 200")
                    note(f"entry point: {role}",
                         last or Probe(origin + (alternates[0] if alternates else "/"), None),
                         detail)
                rec = {"role": role, "path": found_path or None,
                       "redirects_to_root": bounced or None,
                       "linked_from_root": found_path in linked if found_path else None,
                       "chars": visible_text_length(found_probe.body) if found_probe else None}
                roles.append(rec)

                if bounced and not found_path:
                    add("medium", "entry-point-bounces-to-root",
                        f"{role}: {_flat(', '.join(bounced))} answers 200 only by redirecting "
                        "to the site root. The page does not exist, and any scanner that "
                        "follows redirects will report that it does",
                        "agent-readiness.md#k2b-the-entry-points-a-machine-tries-and-the-link-that-only-exists-after-hydration")

                if not found_path:
                    if is_anchor:
                        add("medium", "trust-anchor-missing",
                            f"no {role} page — tried {_flat(', '.join(alternates))}. A verifier "
                            "deciding whether this business is real has nothing to read",
                            "entity-and-brand.md")
                    else:
                        add("low", "entry-point-missing",
                            f"no {role} page at any conventional address "
                            f"({_flat(', '.join(alternates))}) — an agent guessing has nowhere "
                            "to guess",
                            "agent-readiness.md#k2b-the-entry-points-a-machine-tries-and-the-link-that-only-exists-after-hydration")
                    continue

                if not rec["linked_from_root"]:
                    add("high", "entry-point-unlinked",
                        f"{role} lives at {found_path} and answers 200, but the "
                        "SERVER-RENDERED homepage links to it nowhere. If it is in the "
                        "navigation, that navigation is client-rendered — a crawler, an "
                        "answer engine and an agent all read the document before hydration",
                        "agent-readiness.md#k2b-the-entry-points-a-machine-tries-and-the-link-that-only-exists-after-hydration")
                if is_anchor and rec["chars"] is not None and rec["chars"] < TRUST_ANCHOR_MIN_CHARS:
                    add("low", "trust-anchor-thin",
                        f"{found_path} carries {rec['chars']} characters of server-rendered "
                        f"text, under the {TRUST_ANCHOR_MIN_CHARS}-character bar verifiers "
                        "conventionally apply. The bar is a convention, not a measured "
                        "threshold; the mechanism under it is entity resolution",
                        "entity-and-brand.md")
            out["entry_points"] = roles

        # --- 3. RFC 8288 Link headers ---------------------------------------
        link = home.headers.get("link", "") if home.answered else ""
        out["link_header"] = link
        if home.answered and not link:
            add("low", "no-link-headers",
                "no RFC 8288 Link: response headers (sitemap, service-desc, markdown "
                "alternate) — the only discovery channel a HEAD request has",
                "agent-readiness.md#k6-runtime-behaviour-an-agent-depends-on")

        # --- 4. markup on the named page ------------------------------------
        page_url = page or (origin + "/")
        page_probe = home if page_url == origin + "/" else note("page markup", fetch(page_url))
        if page_probe.answered and page_probe.body:
            ld = scan_jsonld(page_probe.body)
            ld["_caveat"] = ("server-rendered HTML only, and ONE url — markup injected by "
                             "JavaScript or carried by other templates is invisible here")
            ld["_url"] = page_url
            out["jsonld"] = ld
            if not ld["same_as"]:
                add("medium", "jsonld-no-sameas",
                    f"no sameAs in the JSON-LD on {page_url} — nothing disambiguates the "
                    "brand from same-named entities",
                    "entity-and-brand.md")
            elif len(ld["same_as"]) < 3:
                add("low", "jsonld-sameas-thin",
                    f"sameAs carries {len(ld['same_as'])} target(s) "
                    f"({_flat(', '.join(ld['same_as']))}) — too few to corroborate an entity",
                    "entity-and-brand.md")
            if ld["blocks"] and not ld["has_address"]:
                add("low", "jsonld-no-address",
                    "Organization schema has no address (PostalAddress) — a verifier "
                    "checking business legitimacy finds nothing",
                    "entity-and-brand.md")
            if ld["blocks"] and ld["_baseline_only"]:
                add("low", "jsonld-narrow-types",
                    f"only baseline types on {page_url} ({_flat(', '.join(ld['types']))}) — "
                    "check the product templates before calling this sitewide",
                    "aeo-geo.md")
            if ld["blocks"] and not ld["has_speakable"]:
                add("info", "jsonld-no-speakable",
                    "no speakable markup — an assistant reading aloud picks its own excerpt",
                    "aeo-geo.md")
            if not ld["markdown_alternate"]:
                add("info", "markdown-alternate-unadvertised",
                    "no <link rel=\"alternate\" type=\"text/markdown\"> and no Link header "
                    "advertising one",
                    "agent-readiness.md#k3-markdown-representations--where-the-myth-ends-and-the-contract-begins")
            else:
                href = re.search(r'href=["\']([^"\']+)["\']', ld["markdown_alternate"][0])
                if href:
                    tgt = href.group(1)
                    tgt = tgt if tgt.startswith("http") else origin + tgt
                    twin = note("advertised markdown twin", fetch(tgt))
                    if twin.answered and not looks_like_markdown(twin.body, twin.ctype):
                        add("high", "markdown-alternate-lies",
                            f"the advertised markdown alternate {tgt} serves "
                            f"{_flat(twin.ctype)} — an advertisement pointing at HTML is "
                            "worse than none",
                            "agent-readiness.md#k3-markdown-representations--where-the-myth-ends-and-the-contract-begins")

        # --- 5. robots.txt as three decisions -------------------------------
        rp = note("robots.txt", fetch(f"{origin}/robots.txt"))
        if rp.answered and rp.status == 200:
            rob = parse_robots(rp.body)
            out["robots"] = rob
            if rob["answer_engines_missing"] and not rob["has_content_signal"]:
                add("info", "robots-ai-undeclared",
                    "answer-engine crawlers with no explicit group: "
                    f"{_flat(', '.join(rob['answer_engines_missing']))} — they fall to the "
                    "* group, which is a default rather than a decision",
                    "agent-readiness.md#k2a-crawler-policy-is-two-decisions-not-one")
            if not rob["training_named"] and not rob["has_content_signal"]:
                add("info", "robots-training-undecided",
                    "no group for training-only crawlers (CCBot, Bytespider) and no "
                    "Content-Signal — the training-corpus question has not been answered "
                    "either way. This is a business decision, not a defect",
                    "agent-readiness.md#k2a-crawler-policy-is-two-decisions-not-one")
            if not rob["has_schemamap"]:
                add("info", "robots-no-schemamap",
                    "no schemamap: directive (NLWeb schema feeds)",
                    "agent-readiness.md#k2-discovery--the-well-known-set-and-what-each-spec-actually-says")
            for sm in rob["sitemaps"][:1]:
                sp = note("sitemap (lastmod coverage)", fetch(sm))
                if sp.answered and sp.status == 200:
                    stats = lastmod_stats(sp.body)
                    if stats["urls"] == 0 and "<sitemapindex" in sp.body:
                        first = re.search(r"<loc>\s*([^<]+)</loc>", sp.body)
                        if first:
                            sp = note("sitemap child (lastmod coverage)",
                                      fetch(first.group(1).strip()))
                            stats = lastmod_stats(sp.body) if sp.answered else stats
                    out["sitemap"] = stats
                    if stats["pct"] is not None and stats["pct"] < 50:
                        add("low", "sitemap-lastmod-thin",
                            f"{stats['pct']}% of {stats['urls']} sitemap entries carry "
                            "<lastmod> — a crawler cannot prioritize what changed",
                            "technical-checks.md")

        # --- 6. llms.txt and the well-known set -----------------------------
        lp = note("llms.txt", fetch(f"{origin}/llms.txt"))
        if not (lp.answered and lp.status == 200):
            add("info", "llms-txt-absent",
                "no /llms.txt. Not a ranking or citation lever (myths.md) — publish it "
                "only if agentic browsers are a target",
                "agent-readiness.md#k2-discovery--the-well-known-set-and-what-each-spec-actually-says")
        elif not re.search(r"when to use|use this (when|if)|best for", lp.body, re.I):
            add("info", "llms-txt-no-when-to-use",
                "llms.txt lists pages but never says when an agent should reach for this "
                "product — a link map is not guidance",
                "agent-readiness.md#k2-discovery--the-well-known-set-and-what-each-spec-actually-says")

        missing = []
        for path, label in WELL_KNOWN:
            wp = note(label, fetch(origin + path))
            if not (wp.answered and wp.status == 200):
                missing.append(path)
        out["well_known_missing"] = missing
        if missing:
            add("info", "wellknown-absent",
                f"{len(missing)} of {len(WELL_KNOWN)} agent-discovery documents absent: "
                f"{_flat(', '.join(missing))}. Drafts and vendor conventions — K8 ranks "
                "which are worth the bytes",
                "agent-readiness.md#k8-the-check-table-with-tiers")

    # --- 7. the auth discovery chain on the host that serves the API --------
    if api_origin:
        api_origin = api_origin.rstrip("/")
        prm = note("api /.well-known/oauth-protected-resource",
                   fetch(f"{api_origin}/.well-known/oauth-protected-resource"))
        if not (prm.answered and prm.status == 200):
            add("medium", "auth-discovery-broken",
                "no RFC 9728 protected-resource metadata on the API host — an agent "
                "cannot learn which authorization server guards this API",
                "agent-readiness.md#k5-agent-authentication--the-discovery-chain-not-the-login-page")

    return {**out, "checks": checks, "findings": findings, "_answered": answered}


def collect_api_behaviour(url: str) -> dict:
    """Rate-limit headers and the 401 hint, from one authenticated-shaped call."""
    p = fetch(url)
    hdrs = p.headers
    rate = {k: v for k, v in hdrs.items()
            if k.startswith(("ratelimit", "x-ratelimit")) or k == "retry-after"}
    return {
        "url": url,
        "status": p.status if p.answered else "no answer",
        "error": p.error,
        "rate_limit_headers": rate,
        "www_authenticate": hdrs.get("www-authenticate", ""),
        "has_resource_metadata_hint": "resource_metadata=" in hdrs.get("www-authenticate", ""),
    }


# --- rendering ---------------------------------------------------------------


def render(data: dict) -> str:
    lines = ["# Agent surface — track K", ""]
    lines.append(f"- Origin: `{_flat(data.get('origin') or '(none)')}`")
    if data.get("api_origin"):
        lines.append(f"- API origin: `{_flat(data['api_origin'])}`")
    lines.append("")
    lines.append("> **Blind spots this run inherits.** Presence is `CONFIRMED`; effect is "
                 "mostly `HYPOTHESIS` (agent-readiness.md K1). Markup was read from "
                 "server-rendered HTML on ONE url, so absence here is not a sitewide "
                 "finding. A draft spec's absence is not a defect.")
    lines.append("")

    checks = data.get("checks") or []
    if checks:
        lines += ["## Probes", "", "| check | url | status | content-type |",
                  "|---|---|---|---|"]
        for c in checks:
            lines.append(f"| {_flat(c['check'], 60)} | `{_flat(c['url'], 90)}` | "
                         f"{_flat(c['status'], 20)} | {_flat(c.get('content_type') or '-', 40)} |")
        lines.append("")

    eps = data.get("entry_points")
    if eps:
        lines += ["## Entry points, read from the server-rendered root", "",
                  "| role | path | answers 200 | linked from the root | visible chars |",
                  "|---|---|---|---|---|"]
        for e in eps:
            linked = ("—" if e["linked_from_root"] is None
                      else ("yes" if e["linked_from_root"] else "**NO**"))
            path = e["path"] or (f"{', '.join(e['redirects_to_root'])} → 301 to /"
                                 if e.get("redirects_to_root") else "(none found)")
            lines.append(f"| {_flat(e['role'], 24)} | {_flat(path, 46)} | "
                         f"{'yes' if e['path'] else 'no'} | {linked} | "
                         f"{e['chars'] if e['chars'] is not None else '—'} |")
        lines += ["", "\"Linked from the root\" reads the HTML as delivered. A link a "
                      "framework adds during hydration is **not** in that document, and "
                      "every non-browser consumer stops there.", ""]

    api = data.get("api_behaviour")
    if api:
        lines += ["## API response contract", "",
                  f"- Probed: `{_flat(api['url'], 90)}` → {_flat(api['status'], 20)}",
                  f"- Rate-limit headers: "
                  f"{_flat(', '.join(api['rate_limit_headers']) or 'none')}",
                  f"- `WWW-Authenticate`: {_flat(api['www_authenticate'] or 'absent')}", ""]

    spec = data.get("openapi")
    if spec:
        lines += ["## OpenAPI — function-calling readiness", "",
                  f"- Operations: **{spec['operations']}**",
                  f"- With `operationId`: **{spec['with_operation_id']}/{spec['operations']}**",
                  f"- With a description or summary: "
                  f"**{spec['with_description']}/{spec['operations']}**",
                  f"- With a typed success schema: "
                  f"**{spec['with_success_schema']}/{spec['operations']}**",
                  f"- Declares 401: {spec['declares_401']} · 429: {spec['declares_429']} · "
                  f"async 202: {spec['has_async_202']} · batch path: {spec['has_batch_path']}",
                  f"- Deprecation policy signal: {spec['has_deprecation_policy']}", ""]
        if spec["duplicate_operation_ids"]:
            lines.append(f"- **Duplicate operationIds:** "
                         f"{_flat(', '.join(spec['duplicate_operation_ids']))}")
            lines.append("")

    findings = data.get("findings") or []
    lines += ["## Findings", ""]
    if not findings:
        lines.append("No findings from the probes that answered. That is not the same as a "
                     "clean surface: read the probe table for checks that never answered.")
    else:
        lines += ["| severity | tier | finding | reference |", "|---|---|---|---|"]
        order = {"blocker": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
        for f in sorted(findings, key=lambda x: order.get(x["severity"], 9)):
            # The reference is a pointer an agent has to be able to open, so it is
            # capped generously: a truncated anchor resolves to nothing.
            lines.append(f"| {f['severity']} | `{f['tier']}` | {_flat(f['message'], 240)} | "
                         f"{_flat(f['reference'], 140)} |")
    lines.append("")
    lines.append("Tier is the confidence multiplier in `priority = (impact × confidence) / "
                 "effort`; severity is not. A `HYPOTHESIS` here belongs in the Experiments "
                 "bucket, never in a sitewide rollout.")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description="Track K: the agent surface of a site (stdlib only).")
    ap.add_argument("--origin", help="site origin, e.g. https://example.com")
    ap.add_argument("--api-origin", default="", help="host that serves the API")
    ap.add_argument("--page", default="", help="url to read markup from (default: origin root)")
    ap.add_argument("--expect", default="",
                    help="comma-separated extra paths that must be reachable from the "
                         "server-rendered root, e.g. /status,/changelog")
    ap.add_argument("--openapi", default="", help="url of an OpenAPI document")
    ap.add_argument("--openapi-file", default="", help="local OpenAPI document (offline)")
    ap.add_argument("--api-probe", default="",
                    help="url of an API endpoint to read rate-limit and 401 headers from")
    ap.add_argument("--format", choices=["markdown", "json"], default="markdown")
    args = ap.parse_args(argv)

    if not (args.origin or args.openapi or args.openapi_file):
        ap.error("nothing to probe: pass --origin, --openapi or --openapi-file")

    expect = tuple((p.strip(), (p.strip(),), False)
                   for p in args.expect.split(",") if p.strip().startswith("/"))
    data = collect(args.origin or "", args.api_origin, args.page, expect=expect)

    spec_obj = None
    if args.openapi_file:
        try:
            with open(args.openapi_file, encoding="utf-8") as fh:
                spec_obj = json.load(fh)
        except (OSError, ValueError) as exc:
            print(f"could not read {args.openapi_file}: {_flat(exc)}", file=sys.stderr)
    elif args.openapi:
        p = fetch(args.openapi)
        data["checks"].append({"check": "openapi document", "url": p.url,
                               "status": p.status if p.answered else "no answer",
                               "content_type": p.ctype, "detail": p.error})
        if p.answered:
            data["_answered"] += 1
            try:
                spec_obj = json.loads(p.body)
            except ValueError as exc:
                print(f"openapi document is not JSON: {_flat(exc)}", file=sys.stderr)

    if spec_obj is not None:
        spec = analyze_openapi(spec_obj)
        data["openapi"] = spec
        n = spec["operations"]
        if n:
            missing_id = n - spec["with_operation_id"]
            if missing_id:
                data["findings"].append({
                    "severity": "high", "code": "openapi-operationid",
                    "message": f"{missing_id}/{n} operations have no operationId — the "
                               "function name an agent generates is then invented from the "
                               "path and matches neither your docs nor your logs",
                    "reference": "agent-readiness.md#k4-the-api-contract-an-llm-has-to-call-through",
                    "tier": FINDING_TIERS["openapi-operationid"]})
            if spec["duplicate_operation_ids"]:
                data["findings"].append({
                    "severity": "high", "code": "openapi-operationid",
                    "message": "duplicate operationIds: "
                               f"{_flat(', '.join(spec['duplicate_operation_ids']))}",
                    "reference": "agent-readiness.md#k4-the-api-contract-an-llm-has-to-call-through",
                    "tier": FINDING_TIERS["openapi-operationid"]})
            if spec["with_description"] < n:
                data["findings"].append({
                    "severity": "medium", "code": "openapi-description",
                    "message": f"{n - spec['with_description']}/{n} operations carry no "
                               "description or summary — the model selects the tool on that "
                               "string",
                    "reference": "agent-readiness.md#k4-the-api-contract-an-llm-has-to-call-through",
                    "tier": FINDING_TIERS["openapi-description"]})
            if spec["with_success_schema"] < n:
                data["findings"].append({
                    "severity": "medium", "code": "openapi-response-schema",
                    "message": f"{n - spec['with_success_schema']}/{n} operations declare no "
                               "typed success response",
                    "reference": "agent-readiness.md#k4-the-api-contract-an-llm-has-to-call-through",
                    "tier": FINDING_TIERS["openapi-response-schema"]})
            if not spec["declares_429"]:
                data["findings"].append({
                    "severity": "low", "code": "openapi-error-shapes",
                    "message": "no 429 response documented — an agent cannot tell rate "
                               "limiting from failure",
                    "reference": "agent-readiness.md#k6-runtime-behaviour-an-agent-depends-on",
                    "tier": FINDING_TIERS["openapi-error-shapes"]})
            if not spec["has_async_202"]:
                data["findings"].append({
                    "severity": "info", "code": "openapi-async",
                    "message": "no 202 Accepted anywhere — long-running work has no "
                               "followable pattern (only a defect if such work exists)",
                    "reference": "agent-readiness.md#k4-the-api-contract-an-llm-has-to-call-through",
                    "tier": FINDING_TIERS["openapi-async"]})
            if not spec["has_batch_path"]:
                data["findings"].append({
                    "severity": "info", "code": "openapi-batch",
                    "message": "no batch or bulk path — an agent acting on N items makes N "
                               "calls, which is also how it trips your rate limit",
                    "reference": "agent-readiness.md#k4-the-api-contract-an-llm-has-to-call-through",
                    "tier": FINDING_TIERS["openapi-batch"]})
            if not spec["has_deprecation_policy"]:
                data["findings"].append({
                    "severity": "low", "code": "openapi-deprecation",
                    "message": "versioned but with no Sunset/Deprecation signal — versioning "
                               "without a deprecation promise is half a contract",
                    "reference": "agent-readiness.md#k4-the-api-contract-an-llm-has-to-call-through",
                    "tier": FINDING_TIERS["openapi-deprecation"]})

    if args.api_probe:
        api = collect_api_behaviour(args.api_probe)
        data["api_behaviour"] = api
        if api["status"] != "no answer":
            data["_answered"] += 1
            if not api["rate_limit_headers"]:
                data["findings"].append({
                    "severity": "medium", "code": "api-no-ratelimit-headers",
                    "message": f"no rate-limit headers on {_flat(api['url'], 80)} — an agent "
                               "discovers the limit by hitting it",
                    "reference": "agent-readiness.md#k6-runtime-behaviour-an-agent-depends-on",
                    "tier": FINDING_TIERS["api-no-ratelimit-headers"]})
            if api["status"] == 401 and not api["has_resource_metadata_hint"]:
                data["findings"].append({
                    "severity": "medium", "code": "api-401-no-hint",
                    "message": "401 with no `WWW-Authenticate: Bearer resource_metadata=…` — "
                               "the agent learns nothing from the refusal",
                    "reference": "agent-readiness.md#k5-agent-authentication--the-discovery-chain-not-the-login-page",
                    "tier": FINDING_TIERS["api-401-no-hint"]})

    answered = data.pop("_answered", 0)
    if args.format == "json":
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(render(data))

    # Contract #1: a run where nothing answered is not a measurement of an absent
    # surface. Offline spec analysis counts as an answer — it measured something.
    if not answered and spec_obj is None:
        print("\nNothing answered: every probe failed at the network layer. This report "
              "measures the connection, not the site.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
