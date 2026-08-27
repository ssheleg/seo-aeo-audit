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

Every output carries a **producer block** — `skill` (this tool's version), `script`,
`observed_at` (UTC), `runtime`, `args` (credential values redacted), `scope` (the
resolved input set), and `actor` / `model` / `trace` from `SEO_AEO_AUDIT_ACTOR`,
`_MODEL`, `_TRACE`. It is present in the default output and under `--format json` as
`producer`. A field the harness did not supply reads `unavailable: <VAR> is not set by
this harness` — never guessed, and never dropped, because a field that vanishes when
unavailable is indistinguishable from one nobody checked. `observed_at` is the field
that decides whether a finding has expired; the report's own `## Provenance` block adds
the four invalidators (see references/preflight.md).

Exit codes: 0 = at least one probe answered, 1 = usage error, or nothing answered
(a run where every request failed is not a measurement of an absent surface).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


# ── provenance: the execution that produced this payload ── shared block ──────
# Copied verbatim into all seven scripts and compared byte for byte by
# `test/validate.py`, for the same reason `_flat` is: these ship as standalone files
# with no shared module, and an import of one does not exist in the installed layout
# (`bin/seo-aeo-audit.js` copies `scripts/` alone into `~/.claude/skills/`). The
# doctrine behind the field set lives above this block in preflight.py. Never edit
# one copy — the guard fails all seven.
SKILL_VERSION = "0.25.6"

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
    # CONFIRMED on the vendors' own documentation, not on a model of ranking:
    # Perplexity says allowing PerplexityBot is what makes a site "appear in
    # search results", and OpenAI says each of its three agents is controlled
    # independently. The effect of the block is documented by the party doing the
    # blocking-out, which is the strongest evidence this skill admits.
    "robots-retrieval-blocked": "CONFIRMED",
    "robots-training-decided": "CONFIRMED",
    "robots-contradictory": "CONFIRMED",
    "robots-blocks-linked-page": "CONFIRMED",
    "robots-no-schemamap": "HYPOTHESIS",
    "sitemap-lastmod-frozen": "STUDY",
    # The claim is reachability, not ranking: a manual at a non-conventional name
    # 404s for every client that follows the convention. Publishing llms.txt at
    # all remains what myths.md says it is.
    "agent-file-misnamed": "CONFIRMED",
    "openapi-foreign-servers": "CONFIRMED",
    "openapi-template-spec": "CONFIRMED",
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

# The uses a robots.txt has to tell apart (agent-readiness.md K2a).
#
# The buckets carry different consequences, which is the whole reason to keep them
# apart: blocking a RETRIEVAL agent removes the site from that engine's answers,
# and blocking a TRAINING agent costs no retrieval at all. One list that mixes
# them — especially one named for the training half — is how a site blocks its own
# citations while believing it opted out of a training corpus. Every retrieval
# entry carries the vendor's own sentence, read from the vendor's documentation on
# 2026-08-14; nothing here is bucketed from the shape of the name.
RETRIEVAL_UAS = {
    "oai-searchbot": "OpenAI: 'used to surface websites in search results in "
                     "ChatGPT's search features'",
    "chatgpt-user": "OpenAI: used 'for certain user actions in ChatGPT and Custom GPTs'",
    "claude-searchbot": "Anthropic: 'navigates the web to improve search result "
                        "quality for users'",
    "claude-user": "Anthropic: 'When individuals ask questions to Claude, it may "
                   "access websites using a Claude-User agent'",
    "perplexitybot": "Perplexity: 'designed to surface and link websites in search "
                     "results on Perplexity. It is not used to crawl content for AI "
                     "foundation models'",
    "perplexity-user": "Perplexity: visits a page 'when users ask Perplexity a question'",
}
# Training-corpus collection. GPTBot and ClaudeBot sit here on their vendors' own
# words: OpenAI documents GPTBot as crawling 'content that may be used in training
# our generative AI foundation models', and Anthropic documents ClaudeBot as
# 'collecting web content that could potentially contribute to their training'.
# Both were in this script's retrieval list until 2026-08-14, which made a site
# that blocked them read as having blocked its own citations.
TRAINING_UAS = ("gptbot", "claudebot", "ccbot", "bytespider")
# Model grounding, which is neither. Blocking Google-Extended removes the site
# from Gemini and Vertex AI grounding; it does not touch Google Search or AI
# Overviews, which are Googlebot's and cannot be separated from Search at all —
# technical-checks.md.
GROUNDING_UAS = ("google-extended", "applebot-extended")
# Named in real robots.txt files (Cloudflare's managed block ships several) with
# no vendor purpose statement read here. Reported as blocked, never as a retrieval
# loss: an unverified purpose cannot support that claim.
# `oai-adsbot` is here and NOT in RETRIEVAL_UAS deliberately. OpenAI documents it
# ("used to validate the safety of web pages submitted as ads on ChatGPT",
# developers.openai.com/api/docs/bots, read 2026-08-16) but states no robots.txt
# behaviour for it, where it states one for OAI-SearchBot and GPTBot. An
# unverified purpose cannot support a retrieval-loss claim — the rule two comments
# up — so a block is reported as a block. It matters anyway: a site running ChatGPT
# ads behind a blanket `OAI-*` or managed-bot block gets a clean report here while
# its ad landing pages fail validation.
OTHER_AI_UAS = ("meta-externalagent", "facebookbot", "amazonbot", "ai2bot",
                "diffbot", "omgilibot", "omgili", "imagesiftbot", "anthropic-ai",
                "cohere-ai", "oai-adsbot")

# Root paths a client probes for an agent manual, and the near-misses a presence
# check reads as absence. A file served one character off the convention is
# invisible to every client that follows it, and "absent" is the wrong finding for
# it — agent-readiness.md K2.
AGENT_FILE_NEAR_MISSES = ("/llm.txt", "/llms-full.txt", "/llm-full.txt",
                          "/ai.txt", "/.well-known/llms.txt")

# Fingerprints of the starter specs documentation platforms ship. Every structural
# check passes them, which is how a demo spec survives into production and gets
# scored as an API — agent-readiness.md K4.
OPENAPI_TEMPLATE_FINGERPRINTS = (
    "sandbox.mintlify.com", "petstore.swagger.io", "openapi plant store",
    "swagger petstore", "api.example.com", "your-api.example",
)

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
    ("about", ("/about", "/about-us", "/company", "/about-company"), True),
    # `/contacts` is here because leaving it out produced a false finding on a
    # live site: the footer linked `/contacts`, the list did not carry it, and
    # `/support` — an in-product route that answers 200 — was reported as the
    # contact page and as unlinked. An alternates list is a claim about how sites
    # are named, and a missing plural is enough to invert a finding.
    ("contact", ("/contact", "/contacts", "/contact-us", "/support", "/help"), True),
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


def _robots_groups(text: str) -> list[dict]:
    """robots.txt as records, per RFC 9309: agent lines, then their rules.

    Consecutive `User-agent` lines share one rule set; the next `User-agent` after
    a rule opens a new record. Reading the file as a flat list of names — which is
    what this module did until 2026-08-14 — answers *whether an agent is named*
    and never *what the site decided about it*, so a site that named every AI
    crawler and blocked all of them read as fully declared.
    """
    groups: list[dict] = []
    cur: dict | None = None
    open_for_agents = False
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        field, _, value = line.partition(":")
        field, value = field.strip().lower(), value.strip()
        if field == "user-agent":
            if cur is None or not open_for_agents:
                cur = {"agents": [], "allow": [], "disallow": [], "signals": []}
                groups.append(cur)
                open_for_agents = True
            cur["agents"].append(value.lower())
        elif field in ("allow", "disallow", "content-signal") and cur is not None:
            open_for_agents = False
            key = {"allow": "allow", "disallow": "disallow",
                   "content-signal": "signals"}[field]
            cur[key].append(value)
    return groups


def _blocks_root(group: dict) -> bool:
    """Does this record shut the whole site? `Disallow: /` with no `Allow: /`."""
    return any(d == "/" for d in group["disallow"]) and not any(
        a == "/" for a in group["allow"])


def parse_robots(text: str) -> dict:
    """What a robots.txt DECIDED about each class of AI crawler, not who it names.

    The three classes have different consequences (RETRIEVAL_UAS / TRAINING_UAS /
    GROUNDING_UAS above), so they are returned apart. Blocking is reported for all
    of them and called a loss for none: which blocks cost citations is a claim the
    caller makes with the vendor sentence in hand.
    """
    groups = _robots_groups(text)
    named: set[str] = {a for g in groups for a in g["agents"]}
    blocked: set[str] = {a for g in groups if _blocks_root(g) for a in g["agents"]}
    wildcard = [g for g in groups if "*" in g["agents"]]
    signals = []
    for g in groups:
        for s in g["signals"]:
            norm = " ".join(s.lower().replace(" ", "").split(","))
            if norm not in signals:
                signals.append(norm)
    return {
        "retrieval_named": sorted(u for u in RETRIEVAL_UAS if u in named),
        "retrieval_missing": sorted(u for u in RETRIEVAL_UAS if u not in named),
        "retrieval_blocked": sorted(u for u in RETRIEVAL_UAS if u in blocked),
        "training_named": sorted(u for u in TRAINING_UAS if u in named),
        "training_blocked": sorted(u for u in TRAINING_UAS if u in blocked),
        "grounding_blocked": sorted(u for u in GROUNDING_UAS if u in blocked),
        "other_ai_blocked": sorted(u for u in OTHER_AI_UAS if u in blocked),
        "wildcard_groups": len(wildcard),
        "wildcard_disallow": [d for g in wildcard for d in g["disallow"] if d],
        "wildcard_allow": [a for g in wildcard for a in g["allow"] if a],
        "content_signals": signals,
        "has_content_signal": bool(signals),
        "has_schemamap": bool(re.search(r"^\s*schemamap:", text, re.I | re.M)),
        "sitemaps": re.findall(r"^\s*sitemap:\s*(\S+)", text, re.I | re.M),
    }


def _registrable(host: str) -> str:
    """Last two labels of a host — enough to tell `api.acme.com` from `acme.io`.

    Deliberately not a public-suffix implementation: this decides whether to ask a
    human, and asking about a `co.uk` pair costs one glance. Getting it wrong the
    other way — silently calling a foreign host familiar — is what this exists to
    prevent.
    """
    labels = [p for p in (host or "").lower().split(".") if p]
    return ".".join(labels[-2:]) if len(labels) >= 2 else (labels[0] if labels else "")


def openapi_provenance(spec: dict, origin: str = "", api_origin: str = "") -> dict:
    """Does this spec describe the site being audited, or the platform's sample?

    Every structural check in K4 — operationIds, descriptions, typed responses —
    passes a documentation platform's starter file exactly as it passes a real
    spec, so a demo petstore left at `/api-reference/openapi.json` is scored as an
    API. Observed on a live product on 2026-08-14, where a third-party grader
    awarded points for it and this script had nothing to say.
    """
    servers = [s.get("url", "") for s in (spec.get("servers") or [])
               if isinstance(s, dict) and s.get("url")]
    own = {_registrable(urlparse(u).hostname or "") for u in (origin, api_origin) if u}
    own.discard("")
    foreign = [u for u in servers
               if (urlparse(u).hostname or "") and _registrable(urlparse(u).hostname) not in own]
    haystack = " ".join(servers + [str(spec.get("info", {}).get("title", "")),
                                   " ".join(list(spec.get("paths", {}) or {})[:20])]).lower()
    prints = sorted({f for f in OPENAPI_TEMPLATE_FINGERPRINTS if f in haystack})
    return {
        "servers": servers,
        # Only claim "foreign" when there was something to compare against: with
        # no origin passed, every host is unknown rather than wrong.
        "foreign_servers": foreign if (own and servers and len(foreign) == len(servers)) else [],
        "template_fingerprints": prints,
    }


def _robots_pattern_matches(pattern: str, path: str) -> bool:
    """RFC 9309 path matching: `*` is any run of characters, `$` anchors the end."""
    if not pattern.startswith("/"):
        return False
    anchored = pattern.endswith("$")
    body = pattern[:-1] if anchored else pattern
    rx = "".join(".*" if ch == "*" else re.escape(ch) for ch in body)
    return re.match(rx + ("$" if anchored else ""), path) is not None


def robots_path_verdict(path: str, allow: list[str], disallow: list[str]) -> str:
    """`allow` or `disallow` for one path, by the documented precedence rule.

    **The most specific rule wins, and Allow beats Disallow on a tie** — that is
    the rule Google and RFC 9309 both publish, and skipping it is how this module
    produced a `medium` / `CONFIRMED` false positive on a live site (2026-08-15).

    The record was:

        Allow: /            Allow: /api$        Disallow: /api/     Disallow: /admin/

    `/api` is matched by `Allow: /api$` (5 characters of pattern) and by nothing
    that forbids it: `Disallow: /api/` requires the trailing slash. The check that
    was here compared `href == p.rstrip("/")`, so a `Disallow: /api/` silently
    covered `/api` as well, and `Allow` lines were never collected at all — the
    more specific rule could not win because it was not in the room.

    The finding it produced said the homepage linked to a path the site forbids,
    against a path the site had gone out of its way to permit with an anchored
    rule. Acting on it means deleting a good link or loosening a good robots.txt.
    """
    best_len, verdict = -1, "allow"
    for rules, name in ((allow, "allow"), (disallow, "disallow")):
        for pattern in rules:
            if not _robots_pattern_matches(pattern, path):
                continue
            n = len(pattern)
            # Strictly longer wins; on an exact tie Allow wins, and Allow is
            # evaluated first, so `>` rather than `>=` implements both.
            if n > best_len:
                best_len, verdict = n, name
    return verdict


def robots_blocks_linked(html: str, disallowed: list[str],
                         allowed: list[str] | None = None) -> list[str]:
    """Same-origin paths the page links to that the `*` record actually forbids.

    A link a crawler can see pointing at a page it may not fetch. Harmless on a
    login form and a real finding on anything the site wants read — either way it
    is a fact about the site nobody was reading, because it needs the page and the
    robots file in the same hand and no single check held both.

    `allowed` is not optional in spirit: without the Allow rules this cannot apply
    the precedence rule and will over-report. It defaults to empty only so an old
    caller keeps working, and passing the group's `allow` list is the correct use.
    """
    if not [p for p in disallowed if p.startswith("/")]:
        return []
    hrefs = {h.split("#")[0].split("?")[0]
             for h in re.findall(r'href=["\'](/[^"\']*)["\']', html)}
    return sorted(h for h in hrefs
                  if robots_path_verdict(h, allowed or [], disallowed) == "disallow")


def lastmod_stats(sitemap_xml: str) -> dict:
    """<lastmod> coverage. Absence is a fact; it is not a zero date."""
    urls = re.findall(r"<url>(.*?)</url>", sitemap_xml, re.S)
    if not urls:
        return {"urls": 0, "with_lastmod": 0, "pct": None, "newest": None}
    with_lm = sum(1 for u in urls if "<lastmod>" in u)
    dates = sorted(re.findall(r"<lastmod>\s*([0-9T:+\-]{10,})", sitemap_xml))
    days = sorted({d[:10] for d in dates})
    return {"urls": len(urls), "with_lastmod": with_lm,
            "pct": round(with_lm * 100 / len(urls)),
            "newest": dates[-1][:10] if dates else None,
            # Coverage answers "is the field there". This answers the question a
            # crawler actually asks — "which of these changed" — and a build that
            # stamps one hard-coded date on every URL answers 100% to the first
            # and nothing to the second.
            "distinct_days": len(days),
            "oldest": days[0] if days else None}


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
        missing = f"{origin}/agent-surface-probe-404-check"
        p = note("404 shape", fetch(missing))
        if p.answered:
            if p.status == 200:
                add("blocker", "agent-404-soft",
                    "an unknown path answers HTTP 200 — every path looks real to an agent",
                    "agent-readiness.md#k6-runtime-behaviour-an-agent-depends-on")
            elif not looks_like_markdown(p.body, p.ctype):
                # Ask the way the fix is meant to be reached before reporting it
                # missing. The recommendation is a markdown body served to a client
                # that ASKED for markdown — serving it to everyone would hand a
                # browser a text file. Probing only with the default Accept
                # therefore reports the recommended implementation as absent, which
                # is what this check did to a site that had just shipped it
                # (2026-08-15).
                md404 = note("404 shape (Accept: text/markdown)",
                             fetch(missing, accept="text/markdown"))
                if not (md404.answered and looks_like_markdown(md404.body, md404.ctype)):
                    add("low", "agent-404-no-recovery",
                        f"HTTP {p.status} for unknown paths (correct) but no short markdown "
                        "recovery, with or without Accept: text/markdown — an agent that "
                        "mistyped a path gets no route back",
                        "agent-readiness.md#k6-runtime-behaviour-an-agent-depends-on")
                elif not re.search(r"(^|,)\s*accept\s*(,|$)", md404.headers.get("vary", ""), re.I):
                    add("high", "markdown-no-vary",
                        "the 404 serves markdown by negotiation but its Vary header does "
                        f"not list Accept ({_flat(md404.headers.get('vary') or 'absent')}) "
                        "— a CDN will hand one variant to everyone",
                        "agent-readiness.md#k3-markdown-representations--where-the-myth-ends-and-the-contract-begins")

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
                    # Prefer an alternate the served homepage actually links to,
                    # and only fall back to the first that merely answers.
                    # Stopping at the first 200 reported a live site's contact
                    # page as unlinked (2026-08-14): `/support` answered — it is
                    # an in-product route — and `/contacts`, which the footer
                    # links, was never reached because the loop had already
                    # broken. A wrong path makes the *finding* wrong, not just
                    # the label.
                    if not found_path:
                        found_path, found_probe = alt, last
                    if alt in linked:
                        found_path, found_probe = alt, last
                        break
                if found_probe is not None:
                    note(f"entry point: {role}", found_probe,
                         "" if landed_where(found_probe, origin) == "same"
                         else f"redirected to {_flat(found_probe.final_url, 80)}")
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
            # The decided-against case, which this script reported for a version
            # and a half by saying nothing at all. Silence where a site has shut
            # out its own citations reads exactly like a pass.
            if rob["retrieval_blocked"]:
                add("high", "robots-retrieval-blocked",
                    "retrieval crawlers disallowed at the root: "
                    f"{_flat(', '.join(rob['retrieval_blocked']))}. These are the agents "
                    "that put a page in an answer with a link, not the ones that build a "
                    "training corpus — "
                    + _flat(RETRIEVAL_UAS[rob["retrieval_blocked"][0]], 160)
                    + ". Blocking them removes the site from those answers; confirm the "
                      "block was the intention and not a training decision that swept "
                      "them up",
                    "agent-readiness.md#k2a-crawler-policy-is-two-decisions-not-one")
            # The other blocks are recorded as answered decisions, never as
            # defects: which corpora a company feeds is its call, and a scanner
            # that scores one answer is scoring a preference (K7).
            decided = (rob["training_blocked"] + rob["grounding_blocked"]
                       + rob["other_ai_blocked"])
            if decided:
                add("info", "robots-training-decided",
                    f"{len(decided)} non-retrieval AI crawler(s) disallowed at the root: "
                    f"{_flat(', '.join(decided))}. Recorded, not counted against the site — "
                    "training and grounding access is a business decision with no retrieval "
                    "cost, and Google-Extended in particular does not touch Google Search",
                    "agent-readiness.md#k2a-crawler-policy-is-two-decisions-not-one")
            if rob["retrieval_missing"] and not rob["has_content_signal"]:
                add("info", "robots-ai-undeclared",
                    "retrieval crawlers with no explicit group: "
                    f"{_flat(', '.join(rob['retrieval_missing']))} — they fall to the "
                    "* group, which is a default rather than a decision",
                    "agent-readiness.md#k2a-crawler-policy-is-two-decisions-not-one")
            if not rob["training_named"] and not rob["has_content_signal"]:
                add("info", "robots-training-undecided",
                    "no group for training crawlers and no Content-Signal — the "
                    "training-corpus question has not been answered either way. This is a "
                    "business decision, not a defect",
                    "agent-readiness.md#k2a-crawler-policy-is-two-decisions-not-one")
            # Two records for the same agent, or two Content-Signal lines that
            # disagree. The usual cause is a CDN-managed block prepended to the
            # origin's own file, and the result is a machine-readable reservation
            # of rights that says both yes and no.
            if rob["wildcard_groups"] > 1 or len(rob["content_signals"]) > 1:
                add("medium", "robots-contradictory",
                    f"{rob['wildcard_groups']} separate `User-agent: *` record(s) and "
                    f"{len(rob['content_signals'])} distinct Content-Signal line(s) "
                    f"({_flat('; '.join(rob['content_signals']) or 'none')}). RFC 9309 "
                    "leaves a crawler free to merge or to take the first, so the file "
                    "states a policy it cannot be held to — and Content-Signal is written "
                    "as a reservation of rights, which makes a contradiction a legal "
                    "statement rather than a formatting slip",
                    "agent-readiness.md#k2a-crawler-policy-is-two-decisions-not-one")
            if home.answered and home.body and rob["wildcard_disallow"]:
                shut = robots_blocks_linked(home.body, rob["wildcard_disallow"],
                                          rob.get("wildcard_allow", []))
                out["linked_but_disallowed"] = shut
                if shut:
                    add("medium", "robots-blocks-linked-page",
                        f"the homepage links to {len(shut)} path(s) the * record disallows: "
                        f"{_flat(', '.join(shut))}. A crawler sees the invitation and may "
                        "not accept it, so an agent asked how to do the thing behind that "
                        "link answers from someone else's page. Intended for a private "
                        "area; a finding for anything the site wants read",
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
                            "<lastmod>. Read the generator before calling this a defect: "
                            "a date the site cannot compute truthfully is better omitted "
                            "than faked, and a deploy date restamping every URL is the "
                            "more expensive failure",
                            "technical-checks.md")
                    # 100% coverage and two dates is the shape a hard-coded map
                    # produces, and it passes a coverage check exactly. The field
                    # is then present and uninformative, which is worse than
                    # absent: absent asks the crawler to decide, a frozen date
                    # tells it nothing has changed.
                    elif (stats["urls"] >= 20 and stats["distinct_days"]
                          and stats["distinct_days"] <= 2):
                        add("medium", "sitemap-lastmod-frozen",
                            f"{stats['urls']} sitemap entries carry <lastmod> and only "
                            f"{stats['distinct_days']} distinct date(s) "
                            f"({_flat(stats['oldest'])}–{_flat(stats['newest'])}). Coverage "
                            "is 100% and the information content is zero — check whether "
                            "the value is written by the build or by hand, and compare the "
                            "newest date against the last deploy before believing it",
                            "technical-checks.md")

        # --- 6. llms.txt and the well-known set -----------------------------
        lp = note("llms.txt", fetch(f"{origin}/llms.txt"))
        if not (lp.answered and lp.status == 200):
            # Before reporting absence, look one character away. A manual served
            # at /llm.txt is written, linked and maintained — and invisible to
            # every client that probes the conventional name, which is all of
            # them. "Absent" sends the team to write a file they already have.
            near = []
            for path in AGENT_FILE_NEAR_MISSES:
                np_ = fetch(origin + path)
                if np_.answered and np_.status == 200 and np_.body.strip() \
                        and "html" not in (np_.ctype or "").lower():
                    note(f"near-miss agent file {path}", np_)
                    near.append(path)
            out["agent_file_near_misses"] = near
            if near:
                add("medium", "agent-file-misnamed",
                    f"no /llms.txt, but {_flat(', '.join(near))} answers 200 with a "
                    "non-HTML body. The file exists and is one character off the name "
                    "every client probes, so the work is done and none of it is reachable. "
                    "This is a rename plus a redirect, not a writing task",
                    "agent-readiness.md#k2-discovery--the-well-known-set-and-what-each-spec-actually-says")
            else:
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
    lines.append("Tier is the `uncertainty` axis, one of the four the plan is ordered "
                 "on — ranked, never multiplied into a product; severity is not an "
                 "axis at all. A `HYPOTHESIS` here belongs in the Experiments bucket, "
                 "never in a sitewide rollout.")
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
        # Before grading the spec, ask whether it describes THIS product. Every
        # structural check below passes a documentation platform's starter file,
        # and a scanner that reports "schema found (3 operations)" for a demo
        # petstore has awarded points for an API that does not exist. Cheap to
        # check, and nothing else in this script would ever notice.
        prov = openapi_provenance(spec_obj, args.origin, args.api_origin)
        data["openapi"]["provenance"] = prov
        if prov["template_fingerprints"]:
            data["findings"].append({
                "severity": "blocker", "code": "openapi-template-spec",
                "message": "the OpenAPI document carries a starter-template fingerprint "
                           f"({_flat(', '.join(prov['template_fingerprints']))}) — this is "
                           "the sample spec a documentation platform ships, not this "
                           "product's API. An agent that reads it will call somebody "
                           "else's host, and every structural check on it is measuring "
                           "the template",
                "reference": "agent-readiness.md#k4-the-api-contract-an-llm-has-to-call-through",
                "tier": FINDING_TIERS["openapi-template-spec"]})
        elif prov["foreign_servers"]:
            data["findings"].append({
                "severity": "high", "code": "openapi-foreign-servers",
                "message": "every servers[] entry points at a host unrelated to the site: "
                           f"{_flat(', '.join(prov['foreign_servers']))}. Either the spec "
                           "belongs to another product or the base URL was never changed "
                           "from the example",
                "reference": "agent-readiness.md#k4-the-api-contract-an-llm-has-to-call-through",
                "tier": FINDING_TIERS["openapi-foreign-servers"]})
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
    prov = provenance("agent_surface.py", argv,
                      " · ".join(p for p in (
                          f"origin {args.origin}" if args.origin else "",
                          f"api {args.api_origin}" if args.api_origin else "",
                          f"page {args.page}" if args.page else "",
                          f"spec {args.openapi}" if args.openapi else "",
                          f"spec file {args.openapi_file}" if args.openapi_file else "",
                      ) if p))
    if args.format == "json":
        # Prepended, not appended: `data` is one object per the contract at line 20,
        # and the block that says which execution produced it belongs above the
        # findings a reader will act on.
        print(json.dumps({"producer": prov, **data}, indent=2, ensure_ascii=False))
    else:
        print(render(data))
        print("\n" + provenance_md(prov))

    # Contract #1: a run where nothing answered is not a measurement of an absent
    # surface. Offline spec analysis counts as an answer — it measured something.
    if not answered and spec_obj is None:
        print("\nNothing answered: every probe failed at the network layer. This report "
              "measures the connection, not the site.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
