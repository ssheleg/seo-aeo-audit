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
check("gptbot" in rob["answer_engines_named"], "GPTBot group not detected")
check("claudebot" in rob["answer_engines_named"], "ClaudeBot group not detected")
check("perplexitybot" in rob["answer_engines_missing"],
      "an answer engine with no group must be reported as missing")
check(rob["training_named"] == ["ccbot"],
      f"the training-crawler decision must be read separately; got {rob['training_named']}")
check(rob["has_schemamap"] is False, "no schemamap: directive here")
check(rob["sitemaps"] == ["https://example.com/sitemap.xml"], "sitemap line not read")

# An Allow for a training crawler is a DECISION, not a defect: the collector must
# report that the question was answered, whichever way. This is the check that
# stops the skill from smuggling a business decision in as a technical finding.
check(ag.parse_robots("User-agent: CCBot\nDisallow: /\n")["training_named"] == ["ccbot"],
      "Disallow must count as the training question being answered too")

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
