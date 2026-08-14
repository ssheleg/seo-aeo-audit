#!/usr/bin/env python3
"""Behaviour tests for agent_surface.py — track K's collector.

Offline. Every parser is exercised against the shape the spec fixes (robots.txt,
sitemaps.org, JSON-LD, OpenAPI 3.1) rather than against the network, so the suite
runs the same in CI as on a plane.

What is actually defended here is the failure this instrument exists to prevent —
a scanner that reports absence it never probed, and a checklist that presents a
draft specification's absence as a confirmed defect:

  * a probe that never answered must not read as "the thing is missing";
  * `<lastmod>` absent is absence, never a zero or a fabricated date;
  * markup absence on ONE url must carry the one-url caveat in the payload;
  * every finding the collector emits must carry a tier from FINDING_TIERS, and
    that tier is the tier of the EFFECT — the probe is always CONFIRMED, and
    conflating the two is how a draft spec becomes a blocker.
"""
from __future__ import annotations

import importlib.util
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "plugins", "seo-aeo-audit", "skills", "seo-aeo-audit", "scripts")
failures: list[str] = []
sys.dont_write_bytecode = True


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, os.path.join(SCRIPTS, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def check(cond: bool, msg: str) -> None:
    if not cond:
        failures.append(msg)


ag = load("agent_surface")

# ── robots.txt: three decisions, read separately ─────────────────────────────
ROBOTS = """User-agent: *
Allow: /

User-agent: GPTBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: CCBot
Allow: /

Sitemap: https://example.com/sitemap.xml
"""
rob = ag.parse_robots(ROBOTS)
check("gptbot" in rob["training_named"],
      "GPTBot is a TRAINING crawler on OpenAI's own words ('content that may be used in "
      "training our generative AI foundation models'). It sat in the retrieval bucket "
      "until 2026-08-14, which made blocking it read as a lost citation")
check("claudebot" in rob["training_named"],
      "ClaudeBot is a training crawler on Anthropic's own words; Claude-SearchBot and "
      "Claude-User are the retrieval pair")
check("perplexitybot" in rob["retrieval_missing"],
      "a retrieval crawler with no group must be reported as missing")
check("ccbot" in rob["training_named"],
      f"the training-crawler decision must be read separately; got {rob['training_named']}")
check(rob["retrieval_blocked"] == [], "nothing is disallowed in this fixture")
check(rob["has_schemamap"] is False, "no schemamap: directive here")
check(rob["sitemaps"] == ["https://example.com/sitemap.xml"], "sitemap line not read")

# An Allow for a training crawler is a DECISION, not a defect: the collector must
# report that the question was answered, whichever way. This is the check that
# stops the skill from smuggling a business decision in as a technical finding.
check(ag.parse_robots("User-agent: CCBot\nDisallow: /\n")["training_named"] == ["ccbot"],
      "Disallow must count as the training question being answered too")

# ── the verdict, not the roll call ───────────────────────────────────────────
# The defect this replaced: parse_robots read WHICH agents were named and never
# WHAT was decided about them, so a site that named every AI crawler and blocked
# all of them produced no finding at all. Silence, on the file that had shut the
# site out of Perplexity's answers.
BLOCKING = """User-agent: *
Allow: /
Disallow: /register

User-agent: PerplexityBot
Disallow: /

User-agent: GPTBot
Disallow: /

User-agent: Google-Extended
Disallow: /
"""
blk = ag.parse_robots(BLOCKING)
check(blk["retrieval_blocked"] == ["perplexitybot"],
      f"a blocked retrieval crawler must be named; got {blk['retrieval_blocked']}")
check(blk["training_blocked"] == ["gptbot"],
      f"a blocked training crawler is recorded apart; got {blk['training_blocked']}")
check(blk["grounding_blocked"] == ["google-extended"],
      "Google-Extended is grounding, not retrieval: blocking it does not touch Google "
      "Search, and filing it as a lost citation is a false finding")
check(blk["wildcard_disallow"] == ["/register"],
      f"the * record's disallow list must survive for the linked-page check; got "
      f"{blk['wildcard_disallow']}")
check(blk["wildcard_groups"] == 1, "one * record here")

# `Allow: /` inside the same record must beat `Disallow: /` — otherwise every site
# with a permissive root reads as blocked, which is the loudest false positive
# this check could possibly produce.
permissive = ag.parse_robots("User-agent: PerplexityBot\nAllow: /\nDisallow: /admin/\n")
check(permissive["retrieval_blocked"] == [],
      "a record that allows the root does not block the site")

# Two `User-agent: *` records with disagreeing Content-Signal — the shape a
# CDN-managed block prepended to the origin's own file produces.
CONTRADICTORY = """User-agent: *
Content-Signal: search=yes,ai-train=no
Allow: /

User-agent: *
Content-Signal: ai-train=yes, search=yes
Disallow: /cdn-cgi/
"""
con = ag.parse_robots(CONTRADICTORY)
check(con["wildcard_groups"] == 2, f"both * records must be seen; got {con['wildcard_groups']}")
check(len(con["content_signals"]) == 2,
      f"two disagreeing Content-Signal lines must not collapse into one; got "
      f"{con['content_signals']}")

# ── a link the crawler may see and may not follow ────────────────────────────
check(ag.robots_blocks_linked('<a href="/register">Sign up</a><a href="/pricing">P</a>',
                              ["/register", "/admin/"]) == ["/register"],
      "a homepage link into a disallowed path is a fact neither the robots check nor the "
      "page check could see alone")
check(ag.robots_blocks_linked('<a href="/pricing">P</a>', ["/admin/"]) == [],
      "a page that links nowhere disallowed must produce nothing")
check(ag.robots_blocks_linked('<a href="/admin/users">u</a>', ["/admin/"]) == ["/admin/users"],
      "a prefix disallow covers what sits under it")

# ── sitemap: absence is absence ──────────────────────────────────────────────
SM = """<?xml version="1.0"?><urlset>
<url><loc>https://e.com/a</loc><lastmod>2026-08-01</lastmod></url>
<url><loc>https://e.com/b</loc></url>
<url><loc>https://e.com/c</loc><lastmod>2026-07-01</lastmod></url>
<url><loc>https://e.com/d</loc></url>
</urlset>"""
st = ag.lastmod_stats(SM)
check(st["urls"] == 4 and st["with_lastmod"] == 2, f"lastmod count wrong: {st}")
check(st["pct"] == 50, f"coverage percentage wrong: {st}")
check(st["newest"] == "2026-08-01", f"newest lastmod wrong: {st}")

check(st["distinct_days"] == 2, f"distinct lastmod days wrong: {st}")

# Coverage answers "is the field there"; a crawler asks "which of these changed".
# A build that stamps one hard-coded date on every URL scores 100% on the first
# and says nothing to the second — observed on a live site whose 160 entries
# carried two dates, both five months old, while the site deployed daily.
frozen = ag.lastmod_stats("<urlset>" + "".join(
    f"<url><loc>https://e.com/{i}</loc><lastmod>2026-03-15</lastmod></url>"
    for i in range(25)) + "</urlset>")
check(frozen["pct"] == 100 and frozen["distinct_days"] == 1,
      f"a frozen sitemap must read as full coverage AND one date; got {frozen}")

empty = ag.lastmod_stats("<urlset></urlset>")
check(empty["pct"] is None,
      "a sitemap with no <url> entries has NO coverage percentage — 0 would read as "
      "'measured, none carry lastmod', which is a different claim from 'nothing to measure'")
check(empty["newest"] is None, "no dates means no newest date, not an epoch")

# ── JSON-LD: what a verifier looks for, and the one-url caveat ───────────────
HTML = """<html><head>
<script type="application/ld+json">{"@context":"https://schema.org","@graph":[
 {"@type":"Organization","name":"X","sameAs":["https://t.me/x"],
  "contactPoint":{"@type":"ContactPoint","email":"a@b.c"}},
 {"@type":"Product","name":"P"}]}</script>
</head><body><h1>hi</h1></body></html>"""
ld = ag.scan_jsonld(HTML)
check(ld["blocks"] == 1, f"block count wrong: {ld['blocks']}")
check("Product" in ld["extended_types"],
      f"Product must count as an extended type; got {ld['extended_types']}")
check("Organization" not in ld["extended_types"],
      "Organization is baseline, not an extended type")
check(ld["same_as"] == ["https://t.me/x"], f"sameAs not collected: {ld['same_as']}")
check(ld["has_contact_point"] is True, "contactPoint not detected")
check(ld["has_address"] is False, "there is no address in this fixture")
check(ld["has_speakable"] is False, "no speakable in this fixture")

broken = ag.scan_jsonld('<script type="application/ld+json">{not json}</script>')
check(broken["invalid_blocks"] == 1,
      "an unparseable block must be counted, not silently dropped — 'no schema found' "
      "and 'the schema does not parse' are different findings")
check(broken["types"] == [], "no types can be read out of a block that does not parse")

# ── OpenAPI: the four properties function calling needs ──────────────────────
SPEC = {
    "openapi": "3.1.0",
    "servers": [{"url": "https://api.e.com/v1"}],
    "paths": {
        "/a": {"get": {"operationId": "getA", "description": "d",
                       "responses": {"200": {"content": {"application/json": {}}}}}},
        "/b": {"get": {"summary": "s",
                       "responses": {"200": {"content": {"application/json": {}}},
                                     "401": {}}},
               "post": {"operationId": "getA",
                        "responses": {"201": {}, "429": {}}}},
    },
    "components": {"securitySchemes": {"bearerAuth": {"type": "http"}}},
}
sp = ag.analyze_openapi(SPEC)
check(sp["operations"] == 3, f"operation count wrong: {sp['operations']}")
check(sp["with_operation_id"] == 2, f"operationId count wrong: {sp['with_operation_id']}")
check(sp["duplicate_operation_ids"] == ["getA"],
      f"a duplicate operationId is as broken as a missing one; got "
      f"{sp['duplicate_operation_ids']}")
check(sp["with_description"] == 2, "summary counts as a description, absence does not")
check(sp["with_success_schema"] == 2,
      f"a 2xx with no content is not a typed response; got {sp['with_success_schema']}")
check(sp["declares_401"] and sp["declares_429"], "declared error codes not detected")
check(sp["has_async_202"] is False, "no 202 in this fixture")
check(sp["has_batch_path"] is False, "no batch path in this fixture")
check(sp["has_deprecation_policy"] is False, "no deprecation signal in this fixture")
check(sp["security_schemes"] == ["bearerAuth"], "security scheme not read")

batchy = ag.analyze_openapi({"paths": {"/v1/batch": {"post": {"responses": {"202": {}}}}}})
check(batchy["has_batch_path"] and batchy["has_async_202"],
      "a /batch path returning 202 must set both flags")

# ── whose API is this? ───────────────────────────────────────────────────────
# Every structural check above passes a documentation platform's starter file
# exactly as it passes a real spec. A live product shipped the Mintlify sample
# ("OpenAPI Plant Store", servers http://sandbox.mintlify.com) at its public
# api-reference URL, a third-party grader scored it as "schema found (3
# operations)", and nothing here had a word to say about it.
DEMO = {"openapi": "3.1.0", "info": {"title": "OpenAPI Plant Store"},
        "servers": [{"url": "http://sandbox.mintlify.com"}],
        "paths": {"/plants": {"get": {"responses": {"200": {}}}}}}
prov = ag.openapi_provenance(DEMO, "https://acme.com", "")
check(prov["template_fingerprints"],
      "a starter-template spec must be recognised before its structure is graded")
check(prov["foreign_servers"] == ["http://sandbox.mintlify.com"],
      f"a servers[] host unrelated to the site must be named; got {prov}")

own = ag.openapi_provenance({"servers": [{"url": "https://api.acme.com/v1"}]},
                            "https://acme.com", "https://api.acme.com")
check(own["foreign_servers"] == [] and own["template_fingerprints"] == [],
      f"a subdomain of the audited site is not a foreign host; got {own}")

# With no origin to compare against there is nothing to be foreign TO, and
# guessing would turn every offline --openapi-file run into a false blocker.
blind = ag.openapi_provenance({"servers": [{"url": "https://api.acme.com"}]}, "", "")
check(blind["foreign_servers"] == [],
      "with no origin passed, an unknown host is unknown — not wrong")

mixed = ag.openapi_provenance(
    {"servers": [{"url": "https://api.acme.com"}, {"url": "https://cdn.other.test"}]},
    "https://acme.com", "")
check(mixed["foreign_servers"] == [],
      "one foreign entry beside a matching one is a staging or CDN host, not a foreign "
      "spec — the finding requires ALL of them to point away")

# ── content negotiation: Vary is the load-bearing half ──────────────────────
md_ok = ag.negotiation_verdict(ag.Probe("u", 200, "text/markdown; charset=utf-8", "# x",
                                        {"Vary": "Accept, Accept-Encoding"}))
check(md_ok["served_markdown"] and md_ok["vary_has_accept"], "a correct negotiation must pass")
md_bad = ag.negotiation_verdict(ag.Probe("u", 200, "text/markdown", "# x",
                                         {"Vary": "Accept-Encoding"}))
check(md_bad["served_markdown"] and not md_bad["vary_has_accept"],
      "markdown served without `Vary: Accept` is the CDN-poisoning case and must be "
      "distinguishable from a clean one")
check(ag.negotiation_verdict(ag.Probe("u", 200, "text/html", "<!doctype html>",
                                      {}))["served_markdown"] is False,
      "html is not markdown")

check(ag.looks_like_markdown("# Title\n\ntext", "text/plain") is True,
      "a heading-led body is markdown even when the content type is vague")
check(ag.looks_like_markdown("<!doctype html><html>", "text/plain") is False,
      "an app shell is not a markdown twin, whatever the advertisement says")

# ── entry points: the link that only exists after hydration ─────────────────
ROOT = """<html><body>
<a href="/pricing">Pricing</a>
<a href="/de/api">API</a>
<a href="https://example.com/terms">Terms</a>
<a href="https://elsewhere.test/api">Their API</a>
<a href="#top">Top</a><a href="mailto:a@b.c">Mail</a>
<a href="relative/thing">Relative</a>
<a href="/blog/?utm=x#frag">Blog</a>
</body></html>"""
links = ag.same_origin_links(ROOT, "https://example.com")
check("/pricing" in links, "a plain absolute-path link must be collected")
check("/api" in links,
      "a locale-prefixed link must count as a link to the unprefixed path — otherwise a "
      "nine-locale site reports a false gap per locale")
check("/terms" in links, "a same-origin absolute URL must be collected")
check(not any("elsewhere" in x for x in links), "off-site links say nothing about reachability")
check("/blog" in links, "query and fragment must be stripped before comparison")
check("#top" not in links and not any("mailto" in x for x in links),
      "in-page and mailto links are not navigation")
check(not any(x.startswith("relative") for x in links),
      "a page-relative link cannot be resolved from the root document alone")

# The alternates list is a claim about how sites are named, and a missing plural
# is enough to invert a finding: on a live site (2026-08-14) the footer linked
# `/contacts`, the list carried only `/contact`, and `/support` — an in-product
# route that answers 200 — was reported as the contact page AND as unlinked from
# the homepage. Two wrong statements out of one missing letter.
_alts = {role: paths for role, paths, _ in ag.ENTRY_POINTS}
check("/contacts" in _alts["contact"],
      f"the plural spelling must be probed; got {_alts['contact']}")
check(_alts["contact"].index("/contacts") < _alts["contact"].index("/support"),
      "a public contact page must be tried before an in-product one — /support "
      "answers 200 on plenty of sites where it is not the contact page")
for _role, _paths in _alts.items():
    check(len(set(_paths)) == len(_paths), f"{_role} lists a path twice")

# ── visible text: the comment trap ──────────────────────────────────────────
# The measurement that produced a wrong number in a real audit: a page whose HTML
# comments carried 1,666 characters read as 772 characters of prose against a real
# 482. A trust-page length check that counts comments grades boilerplate.
# The `>` in the middle is the whole mechanism: a naive `<[^>]+>` sweep swallows a
# comment only while the comment contains no `>` of its own. One arrow in one build
# note is enough for the rest to leak into the word count as prose — which is what
# happened on the real page (three comments, 1,666 characters, 290 of them leaking).
commented = ("<html><body><!-- fetch as print media -> then promote it to all media "
             + ("boilerplate " * 40) + "--><p>Short.</p></body></html>")
check(ag.visible_text_length(commented) < 20,
      f"HTML comments must not count as visible text; got {ag.visible_text_length(commented)}. "
      f"A trust-page length check that counts build notes grades boilerplate")
check(ag.visible_text_length("<style>p{color:red}</style><script>var a=1</script><p>Hi there</p>") == 8,
      "script and style contents are not visible text")

# ── a 301 to the homepage is not a page ─────────────────────────────────────
# urlopen follows redirects, so a probe can report "200, 1,564 characters" while
# describing the homepage. /about-us did exactly that on a live site, and the
# instrument reported an About page that does not exist.
bounced = ag.Probe("https://example.com/about-us", 200, "text/html", "<html/>",
                   final_url="https://example.com/")
check(ag.landed_where(bounced, "https://example.com") == "root",
      "a redirect to the site root must be reported as root, never as the requested page")
straight = ag.Probe("https://example.com/api", 200, "text/html", "<html/>",
                    final_url="https://example.com/api")
check(ag.landed_where(straight, "https://example.com") == "same", "a direct 200 lands on itself")
moved = ag.Probe("https://example.com/docs", 200, "text/html", "<html/>",
                 final_url="https://example.com/api")
check(ag.landed_where(moved, "https://example.com") == "elsewhere",
      "a redirect to another path is neither the page asked for nor the root")
trailing = ag.Probe("https://example.com/api", 200, "text/html", "<html/>",
                    final_url="https://example.com/api/")
check(ag.landed_where(trailing, "https://example.com") == "same",
      "a trailing slash is not a redirect to somewhere else")
check(ag.Probe("u", 200).final_url == "u",
      "a probe with no recorded final url reports the url it asked for, never empty")

# ── a probe that never answered is not a measurement ─────────────────────────
dead = ag.Probe("https://nope.invalid/", None, error="dns failure")
check(dead.answered is False, "a probe with no status must not read as answered")
live404 = ag.Probe("https://e.com/x", 404)
check(live404.answered is True, "a 404 is an answer — the server spoke")

# ── every emitted finding carries a declared tier ────────────────────────────
src = open(os.path.join(SCRIPTS, "agent_surface.py"), encoding="utf-8").read()
emitted = set(__import__("re").findall(r'"code":\s*"([a-z0-9-]+)"', src))
undeclared = sorted(emitted - set(ag.FINDING_TIERS))
check(not undeclared,
      f"findings emitted with no FINDING_TIERS entry: {undeclared} — non-negotiable #2 "
      f"makes the tier the multiplier in the triage formula")
check(emitted, "no finding codes found in agent_surface.py — this check is blind")
bad_tiers = {c: t for c, t in ag.FINDING_TIERS.items()
             if t not in ("CONFIRMED", "STUDY", "FIELD", "HYPOTHESIS")}
check(not bad_tiers, f"tiers outside the vocabulary: {bad_tiers}")

# The specific confusion this track exists to prevent: a draft specification's
# absence dressed up as a confirmed defect. Everything in the .well-known set is
# draft or vendor convention, so its EFFECT tier may not be CONFIRMED.
for code in ("wellknown-absent", "llms-txt-absent", "markdown-no-negotiation",
             "robots-no-schemamap", "jsonld-no-speakable"):
    check(ag.FINDING_TIERS.get(code) == "HYPOTHESIS",
          f"{code} claims tier {ag.FINDING_TIERS.get(code)!r} — a draft spec's absence is "
          f"a fact about the site, not evidence that shipping it changes an outcome")
# ...and the converse: a soft 404 is broken for every consumer, agent or not.
check(ag.FINDING_TIERS["agent-404-soft"] == "CONFIRMED",
      "a 200 for a missing page is a defect, not a hypothesis")
for code in ("entry-point-unlinked", "entry-point-bounces-to-root"):
    check(ag.FINDING_TIERS[code] == "CONFIRMED",
          f"{code} is an observation about this site's own HTML, not a bet on agent "
          f"behaviour — it must not be discounted in the triage formula")
check(ag.FINDING_TIERS["trust-anchor-thin"] == "HYPOTHESIS",
      "the 500-character bar is a convention, not a measured threshold")
# The retrieval block is the one track-K finding whose EFFECT the blocked party
# documents itself, which is why it is CONFIRMED where most of K is not.
check(ag.FINDING_TIERS["robots-retrieval-blocked"] == "CONFIRMED",
      "Perplexity documents that allowing PerplexityBot is what makes a site appear in "
      "its results — the effect of the block is stated by the engine, not modelled here")
check(ag.FINDING_TIERS["robots-training-decided"] == "CONFIRMED",
      "recording an answered business decision is an observation; it is not discounted "
      "and it is not a defect")
check(ag.FINDING_TIERS["openapi-template-spec"] == "CONFIRMED",
      "a spec whose servers point at a vendor sandbox describes another product — a fact "
      "about the document, not a bet")

# The taxonomy is load-bearing enough to be asserted where a reader will see it
# fail: three buckets, no member in two of them.
overlap = (set(ag.RETRIEVAL_UAS) & set(ag.TRAINING_UAS)) | \
          (set(ag.RETRIEVAL_UAS) & set(ag.GROUNDING_UAS)) | \
          (set(ag.TRAINING_UAS) & set(ag.GROUNDING_UAS)) | \
          (set(ag.RETRIEVAL_UAS) & set(ag.OTHER_AI_UAS))
check(not overlap, f"a user agent in two buckets makes the finding ambiguous: {overlap}")
check(all(ag.RETRIEVAL_UAS[u] for u in ag.RETRIEVAL_UAS),
      "every retrieval agent carries the vendor sentence that put it in this bucket — "
      "without it the bucket is an opinion, and this module held a wrong one for a "
      "version and a half")
check("google-extended" not in ag.RETRIEVAL_UAS,
      "Google-Extended governs Gemini and Vertex grounding, not Google Search or AI "
      "Overviews — technical-checks.md says Googlebot cannot be split by purpose at all")

# ── the report must state its own blind spots ────────────────────────────────
rendered = ag.render({"origin": "https://e.com", "checks": [], "findings": []})
for needle in ("Presence is `CONFIRMED`", "ONE url", "server-rendered"):
    check(needle in rendered,
          f"render() dropped its blind-spot statement ({needle!r}) — non-negotiable #8 "
          f"requires the instrument to say what it could not see in the output")
check("read the probe table for checks that never answered" in rendered,
      "an empty findings list must not read as a clean surface")

# ── the whole pipeline, offline, through main() ──────────────────────────────
import tempfile  # noqa: E402 - deliberately after the module under test loads

with tempfile.TemporaryDirectory() as tmp:
    p = os.path.join(tmp, "spec.json")
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(SPEC, fh)
    import contextlib  # noqa: E402
    import io  # noqa: E402
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = ag.main(["--openapi-file", p, "--format", "json"])
    check(rc == 0, "an offline spec analysis measured something and must exit 0")
    payload = json.loads(buf.getvalue())
    check(payload["openapi"]["operations"] == 3, "main() lost the spec analysis")
    codes = {f["code"] for f in payload["findings"]}
    check("openapi-operationid" in codes, "the operationId findings did not reach main()")
    check(all(f.get("tier") for f in payload["findings"]),
          "a finding reached the payload with no tier")

if failures:
    print("FAIL: agent_surface")
    for f in failures:
        print(" - " + f)
    sys.exit(1)
print("PASS: agent_surface behaviour")
