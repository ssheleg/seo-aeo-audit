#!/usr/bin/env python3
"""Functional tests for scripts/page_audit.py. Offline, stdlib only. Exit 0 = pass."""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(
    ROOT, "plugins", "seo-aeo-audit", "skills", "seo-aeo-audit", "scripts", "page_audit.py"
)
FIXTURES = os.path.join(ROOT, "test", "fixtures")
failures: list[str] = []

# Import without leaving a __pycache__ behind: both installers copy the skill
# directory verbatim, so anything this test drops in there ships to users.
sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location("page_audit", SCRIPT)
page_audit = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(page_audit)


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

# --base-url outside --file mode must warn rather than be silently ignored
warned = subprocess.run(
    [sys.executable, SCRIPT, "--url", "ftp://example.com/x", "--base-url", "https://example.com",
     "--format", "json"],
    capture_output=True, text=True, check=True,
)
check("--base-url applies to --file only" in warned.stderr,
      f"--base-url outside --file must warn, stderr was {warned.stderr!r}")

# a URL list must tolerate indentation and commented lines
list_path = os.path.join(FIXTURES, "urls.txt")
with open(list_path, "w", encoding="utf-8") as fh:
    fh.write("  # a commented, indented line\n\n  ftp://example.com/one  \n")
try:
    listed = json.loads(subprocess.run(
        [sys.executable, SCRIPT, "--url-list", list_path, "--format", "json"],
        capture_output=True, text=True, check=True,
    ).stdout)
finally:
    os.remove(list_path)
check(len(listed) == 1, f"url-list: comment and blank lines must be skipped, got {len(listed)} record(s)")
check(listed[0]["url"] == "ftp://example.com/one", f"url-list: line not trimmed: {listed[0]['url']!r}")

# repeated X-Robots-Tag headers must both survive — a plain dict() would hide one
with open(os.path.join(FIXTURES, "good-page.html"), encoding="utf-8") as fh:
    good_html = fh.read()
multi = page_audit.analyze(
    good_html,
    "https://example.com/pricing",
    page_audit.collapse_headers([("X-Robots-Tag", "noindex"), ("x-robots-tag", "nosnippet")]),
)
check(multi["noindex"] is True, "repeated X-Robots-Tag: noindex on the first line must be read")
check(multi["nosnippet"] is True, "repeated X-Robots-Tag: nosnippet on the second line must be read")

# a gzip body truncated by --max-bytes must still yield the text it decoded
import gzip as _gzip  # noqa: E402 - local to this check

blob = ("<html><head><title>t</title></head><body><p>" + "word " * 4000 + "</p></body></html>").encode()
truncated = _gzip.compress(blob)[: len(_gzip.compress(blob)) // 2]
check(len(page_audit._gunzip(truncated)) > 0, "truncated gzip body must be salvaged, not dropped")
check(page_audit._gunzip(_gzip.compress(blob)) == blob, "intact gzip body must round-trip")

# ── non-negotiable #8: the instrument declares its own blind spot ────────────
# A static parser cannot see JSON-LD that a CMS injects with JavaScript, so an
# empty inventory is not evidence of absent schema. If the caveat ever falls out
# of the payload, "0 blocks" starts reading as a measurement and the tool becomes
# a false-finding generator on every Yoast/RankMath/AIOSEO site.
good = run("good-page.html", "https://example.com/pricing")
check("jsonld_caveat" in good, "report payload must always carry jsonld_caveat")
check("server-rendered HTML only" in good.get("jsonld_caveat", ""),
      "jsonld_caveat must name the blind spot, not just hint at it")
check("Rich Results Test" in good.get("jsonld_caveat", "")
      or "rendering check" in good.get("jsonld_caveat", ""),
      "jsonld_caveat must name the way to confirm, not only the limitation")

_md = subprocess.run(
    [sys.executable, SCRIPT, "--file", os.path.join(FIXTURES, "good-page.html"),
     "--base-url", "https://example.com/pricing", "--format", "markdown"],
    capture_output=True, text=True, check=True,
).stdout
check("server-rendered HTML only" in _md,
      "the caveat must reach the human-readable report too, not only JSON")

# a complete node must not be flagged — a guard that cries wolf gets ignored
check(good["jsonld_missing_required"] == [],
      f"good-page Product has name/offers; flagged anyway: {good['jsonld_missing_required']}")

# and an incomplete one must be caught, by structure, without claiming anything
# about rich-result eligibility (that needs Google's per-feature tables).
_tmp = os.path.join(tempfile.mkdtemp(), "incomplete.html")
with open(_tmp, "w", encoding="utf-8") as _fh:
    _fh.write(
        '<html><head><title>t</title>'
        '<script type="application/ld+json">'
        '{"@context":"https://schema.org","@type":"Article","author":"A"}'
        "</script></head><body><h1>h</h1><p>body</p></body></html>"
    )
_inc = json.loads(subprocess.run(
    [sys.executable, SCRIPT, "--file", _tmp, "--base-url", "https://example.com/a",
     "--format", "json"],
    capture_output=True, text=True, check=True,
).stdout)[0]
check("Article.headline" in _inc["jsonld_missing_required"],
      f"Article without headline must be reported: {_inc['jsonld_missing_required']}")
check("jsonld-incomplete" in {f["code"] for f in _inc["findings"]},
      "a missing structural property must surface as a finding")
check(any("Rich Results Test" in f["message"] for f in _inc["findings"]
          if f["code"] == "jsonld-incomplete"),
      "the incompleteness finding must route eligibility to the Rich Results Test")

if failures:
    print("FAIL: page_audit behavior")
    for f in failures:
        print(" - " + f)
    sys.exit(1)
print("PASS: page_audit behavior (3 fixtures, markdown + json + scheme guard + headers, "
      "gzip, url-list and error paths, blindness caveat, schema completeness)")
