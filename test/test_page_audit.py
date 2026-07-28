#!/usr/bin/env python3
"""Functional tests for scripts/page_audit.py. Offline, stdlib only. Exit 0 = pass."""
from __future__ import annotations

import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(
    ROOT, "plugins", "seo-aeo-audit", "skills", "seo-aeo-audit", "scripts", "page_audit.py"
)
FIXTURES = os.path.join(ROOT, "test", "fixtures")
failures: list[str] = []


def check(cond: bool, msg: str) -> None:
    if not cond:
        failures.append(msg)


def run(fixture: str, base_url: str) -> dict:
    out = subprocess.run(
        [
            sys.executable,
            SCRIPT,
            "--file",
            os.path.join(FIXTURES, fixture),
            "--base-url",
            base_url,
            "--format",
            "json",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(out.stdout)[0]


bad = run("bad-page.html", "https://example.com/pricing")
codes = {f["code"] for f in bad["findings"]}

check(bad["noindex"] is True, "bad-page: content=\"none\" must be read as noindex")
check("noindex" in codes, "bad-page: missing noindex finding")
check("refresh-noindex" in codes, "bad-page: missing meta refresh + noindex conflict finding")
check("canonical-attrs" in codes, "bad-page: missing canonical extra-attribute finding")
check(bad["canonical_extra_attrs"] == ["media"], f"bad-page: extra attrs wrong: {bad['canonical_extra_attrs']}")
check("canonical-multiple" in codes, "bad-page: two canonicals must be flagged")
check("jsonld-invalid" in codes, "bad-page: invalid JSON-LD must be flagged")
check("alt-missing" in codes, "bad-page: image without alt must be flagged")
check("price-not-in-text" in codes, "bad-page: JS-gated price must be flagged")
check("h1-missing" in codes, "bad-page: missing H1 must be flagged")
check("thin" in codes, "bad-page: thin content must be flagged")
check(
    bad["read_budget"]["links_before_first_text"] >= 20,
    f"bad-page: nav links before content miscounted: {bad['read_budget']['links_before_first_text']}",
)
check(
    "read-budget" in codes or "nav-before-content" in codes,
    "bad-page: navigation-heavy source order must produce a read-budget finding",
)
check(bad["links_total"] == 24, f"bad-page: expected 24 links, got {bad['links_total']}")
check(bad["word_count"] == 6, f"bad-page: prose words must exclude nav labels, got {bad['word_count']}")
check(bad["link_text_words"] == 28, f"bad-page: link-text words wrong: {bad['link_text_words']}")
check(
    "Twenty" not in bad["first_100_words"],
    "bad-page: first_100_words must be prose only, not navigation labels",
)
check(
    any(f["severity"] == "blocker" for f in bad["findings"]),
    "bad-page: must produce at least one blocker",
)

good = run("good-page.html", "https://example.com/pricing")
gcodes = {f["code"] for f in good["findings"]}

check(good["noindex"] is False, "good-page: must not be flagged noindex")
check(good["canonical_self_referential"] is True, "good-page: canonical must be self-referential")
check(
    good["canonical_extra_attrs"] == [],
    f"good-page: data-* attributes are harmless, got {good['canonical_extra_attrs']}",
)
check("canonical-attrs" not in gcodes, "good-page: data-react-helmet must not be flagged")
check(good["h1_count"] == 1, f"good-page: expected one H1, got {good['h1_count']}")
check(good["subheads_h2_h4"] == 4, f"good-page: expected 4 subheads, got {good['subheads_h2_h4']}")
check(
    sorted(good["jsonld_types"]) == ["Offer", "Product"],
    f"good-page: JSON-LD types wrong: {good['jsonld_types']}",
)
check(good["currency_in_text"] is True, "good-page: price must be present in extractable text")
check("price-not-in-text" not in gcodes, "good-page: price is in text, must not be flagged")
check(good["images_missing_alt"] == 0, "good-page: image has alt text")
check(
    good["read_budget"]["content_pct"] >= 55,
    f"good-page: content share too low: {good['read_budget']['content_pct']}%",
)
check(
    not any(f["severity"] == "blocker" for f in good["findings"]),
    f"good-page: unexpected blocker: {[f['code'] for f in good['findings']]}",
)

edge = run("edge-page.html", "https://example.com/guide")
ecodes = {f["code"] for f in edge["findings"]}

check(
    edge["noindex"] is False,
    "edge-page: 'nonexistent'/'noneffective' in body must not be read as a noindex directive",
)
check("noindex" not in ecodes, "edge-page: no noindex finding expected")
check(edge["nosnippet"] is True, "edge-page: nosnippet directive must be detected")
check("nosnippet" in ecodes, "edge-page: nosnippet must be reported — it gates AI quoting")
check(
    edge["canonical_extra_attrs"] == [],
    f"edge-page: id/class on a canonical are harmless, got {edge['canonical_extra_attrs']}",
)
check(edge["jsonld_types"] == ["Article"], f"edge-page: JSON-LD types wrong: {edge['jsonld_types']}")
check(
    not any(f["severity"] == "blocker" for f in edge["findings"]),
    f"edge-page: unexpected blocker: {[f['code'] for f in edge['findings']]}",
)

# markdown mode must render without crashing and carry the findings table
md = subprocess.run(
    [sys.executable, SCRIPT, "--file", os.path.join(FIXTURES, "bad-page.html"),
     "--base-url", "https://example.com/pricing"],
    capture_output=True, text=True, check=True,
).stdout
check("| severity | check | finding | reference |" in md, "markdown output: findings table missing")
check("answer-engine first read" in md, "markdown output: read-budget line missing")

# non-http(s) schemes must be refused before any fetch happens
for bad in ("file:///etc/passwd", "ftp://example.com/x", "gopher://example.com"):
    out = subprocess.run(
        [sys.executable, SCRIPT, "--url", bad, "--format", "json"],
        capture_output=True, text=True, check=True,
    )
    rec = json.loads(out.stdout)[0]
    check(
        "unsupported URL scheme" in rec.get("error", ""),
        f"scheme guard: {bad} must be refused, got {rec.get('error')!r}",
    )
    check("Traceback" not in out.stderr, f"scheme guard: {bad} must not traceback")

# a missing file must fail cleanly, not traceback
missing = subprocess.run(
    [sys.executable, SCRIPT, "--file", os.path.join(FIXTURES, "nope.html")],
    capture_output=True, text=True,
)
check(missing.returncode == 1, "missing file must exit 1")
check("Traceback" not in missing.stderr, "missing file must not traceback")

if failures:
    print("FAIL: page_audit behavior")
    for f in failures:
        print(" - " + f)
    sys.exit(1)
print("PASS: page_audit behavior (3 fixtures, markdown + json + scheme guard + error path)")
