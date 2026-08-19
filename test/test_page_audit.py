#!/usr/bin/env python3
"""Functional tests for scripts/page_audit.py. Offline, stdlib only. Exit 0 = pass."""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import residue  # noqa: E402

residue.open_case("page_audit behaviour")
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
check("low-extractable-text" in codes,
      "bad-page: a body with almost no extractable prose must be recorded")
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
check("| severity | tier | check | finding | reference |" in md,
      "markdown output: findings table must carry the evidence tier column")
check("answer-engine first read" in md, "markdown output: read-budget line missing")

# non-http(s) schemes must be refused before any fetch happens.
# check=False: a run where every URL failed now exits 1 on purpose — the refusal
# is the point, and the exit code is asserted separately below.
for bad in ("file:///etc/passwd", "ftp://example.com/x", "gopher://example.com"):
    out = subprocess.run(
        [sys.executable, SCRIPT, "--url", bad, "--format", "json"],
        capture_output=True, text=True,
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
    capture_output=True, text=True,
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
        capture_output=True, text=True,
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
_salvaged, _was_cut = page_audit._gunzip(truncated)
check(len(_salvaged) > 0, "truncated gzip body must be salvaged, not dropped")
check(_was_cut is True, "a salvaged gzip stream must report itself as truncated")
_whole_body, _cut2 = page_audit._gunzip(_gzip.compress(blob))
check(_whole_body == blob, "intact gzip body must round-trip")
check(_cut2 is False, "an intact gzip body must not claim truncation")

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
_tmp = os.path.join(residue.workspace("incomplete-schema"), "incomplete.html")
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

# ── directive parsing: a parameter's value is not a directive ────────────────
# `max-image-preview:none` contains the word `none`, and `content="none"` really
# does mean `noindex, nofollow`. A word-boundary match over the whole directive
# string cannot tell them apart, so it reported a track-A blocker on a page that
# says `index, follow` — and SKILL.md makes a track-A blocker a stop condition,
# so the audit ended there. edge-page.html tests the neighbouring case
# (`nonexistent` in body copy) with `max-image-preview:large`, which is exactly
# why this one survived.


def analyze_html(html: str, url: str = "https://example.com/p", headers=None) -> dict:
    return page_audit.analyze(html, url, page_audit.collapse_headers((headers or {}).items()))


_PARAM_NONE = (
    "index, follow, max-image-preview:none, max-snippet:-1",
    "max-video-preview:none",
    "index,max-image-preview:none",
    "all, unavailable_after: 25 Jun 2026 15:00:00 PST",
)
for _content in _PARAM_NONE:
    _r = analyze_html(
        f'<html><head><title>t</title><meta name="robots" content="{_content}">'
        "</head><body><h1>h</h1><p>copy</p></body></html>"
    )
    check(_r["noindex"] is False,
          f"directive parsing: {_content!r} must NOT read as noindex")
    check("noindex" not in {f["code"] for f in _r["findings"]},
          f"directive parsing: {_content!r} must produce no noindex finding")

# the real thing must still be caught, in every documented spelling
for _content, _where in (("none", "meta"), ("noindex", "meta"), ("noindex, nofollow", "meta")):
    _r = analyze_html(
        f'<html><head><title>t</title><meta name="robots" content="{_content}">'
        "</head><body><h1>h</h1></body></html>"
    )
    check(_r["noindex"] is True, f"directive parsing: {_where} {_content!r} must read as noindex")

# X-Robots-Tag carries an optional user-agent prefix; the value after it is the
# directive, and the parameter rule must not swallow it.
_ua = analyze_html("<html><head><title>t</title></head><body><h1>h</h1></body></html>",
                   headers={"X-Robots-Tag": "googlebot: noindex"})
check(_ua["noindex"] is True, "X-Robots-Tag with a user-agent prefix must still be read")
_ua_param = analyze_html("<html><head><title>t</title></head><body><h1>h</h1></body></html>",
                         headers={"X-Robots-Tag": "googlebot: max-image-preview:none"})
check(_ua_param["noindex"] is False,
      "a parameter behind a user-agent prefix must not read as noindex")

# ── the price check must look at markup, not at bytes ────────────────────────
# CURRENCY_RE was searched against the raw HTML, so jQuery's `$` inside an inline
# script, or a correct Product/Offer priceCurrency, produced a `high` finding
# asserting the page hides its price from answer engines.
_jq = analyze_html(
    '<html><head><title>t</title></head><body><h1>h</h1><p>No prices here.</p>'
    '<script>var $ = window.jQuery; $(function(){});</script></body></html>'
)
check(_jq["currency_in_source_only"] is False,
      "jQuery's $ inside a script must not read as a hidden price")
check("price-not-in-text" not in {f["code"] for f in _jq["findings"]},
      "jQuery's $ must not produce a price finding")

_ld = analyze_html(
    '<html><head><title>t</title>'
    '<script type="application/ld+json">{"@context":"https://schema.org",'
    '"@type":"Product","name":"W","offers":{"@type":"Offer","price":"10",'
    '"priceCurrency":"USD"}}</script></head>'
    "<body><h1>h</h1><p>Widget, described without a number.</p></body></html>"
)
check(_ld["currency_in_source_only"] is False,
      "a priceCurrency inside JSON-LD is markup, not a price hidden in the source")
check("price-not-in-text" not in {f["code"] for f in _ld["findings"]},
      "correct Product/Offer markup must not be reported as a JS-gated price")
# it IS a markup-versus-visible-content parity observation, which is a different
# finding with a different fix (onpage-checks.md O1 starred item).
check("jsonld_price_declared" in _ld, "the payload must record a declared JSON-LD price")
check("jsonld-price-parity" in {f["code"] for f in _ld["findings"]},
      "a JSON-LD price absent from the visible text must surface as a parity finding")

# a price sitting in an attribute or in an image really is source-only
_attr = analyze_html(
    '<html><head><title>t</title></head><body><h1>h</h1>'
    '<div id="p" data-price="$49"></div><p>Plans for teams.</p></body></html>'
)
check(_attr["currency_in_source_only"] is True,
      "a price in an attribute is in the source and not in the text — still a finding")

# ── truncation is not a measurement (non-negotiable #8) ──────────────────────
# Every size-derived number (word count, links, read budget, alt coverage) was
# computed on whatever fitted inside --max-bytes and printed as if it were the
# page.
_long = ("<html><head><title>t</title><link rel=\"canonical\" href=\"https://example.com/p\">"
         "</head><body><h1>h</h1>" + "<p>word word word word word</p>" * 500 + "</body></html>")
_full = analyze_html(_long)
check(_full.get("truncated") is False, "an untruncated read must say so explicitly")

_cut = page_audit.analyze(_long[:2000], "https://example.com/p", {}, truncated=True)
check(_cut.get("truncated") is True, "analyze must carry the truncation flag into the payload")
_cut_codes = {f["code"] for f in _cut["findings"]}
check("truncated-read" in _cut_codes,
      "a truncated read must produce its own finding, not a silent number")
check("thin" not in _cut_codes and "low-extractable-text" not in _cut_codes,
      "size-derived findings must be suppressed on a truncated read, not reported")
check("read-budget" not in _cut_codes and "nav-before-content" not in _cut_codes,
      "the read budget cannot be estimated from a fragment")

_cut_md = page_audit.to_markdown([_cut])
check("truncated" in _cut_md.lower(),
      "the human-readable report must say the page was truncated")

# and the flag has to come from the fetch itself, not only from a keyword argument
import http.server  # noqa: E402 - local to this check
import socketserver  # noqa: E402
import threading  # noqa: E402

_body = ("<html><head><title>t</title></head><body><h1>h</h1>"
         + "<p>word word word word word</p>" * 400 + "</body></html>").encode()


class _Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802 - stdlib naming
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(_body)))
        self.end_headers()
        self.wfile.write(_body)

    def log_message(self, *a):  # noqa: D102 - silence the test log
        pass


socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("127.0.0.1", 0), _Handler) as _srv:
    _port = _srv.server_address[1]
    _t = threading.Thread(target=_srv.serve_forever, daemon=True)
    _t.start()
    try:
        _, _, _whole = page_audit.fetch(f"http://127.0.0.1:{_port}/", 10.0,
                                        page_audit.DEFAULT_UA, 5_000_000)
        check(_whole is False, "a body that fits inside --max-bytes is not truncated")
        _, _, _part = page_audit.fetch(f"http://127.0.0.1:{_port}/", 10.0,
                                       page_audit.DEFAULT_UA, 2000)
        check(_part is True, "a body cut off by --max-bytes must report itself truncated")
    finally:
        _srv.shutdown()

# ── every finding carries an evidence tier (non-negotiable #2) ───────────────
# The tier is the confidence multiplier in `priority = (impact × confidence) /
# effort`. Emitting severity alone leaves the agent to invent the number that
# orders the plan.
_TIERS = {"CONFIRMED", "STUDY", "FIELD", "HYPOTHESIS"}
for _name, _rec in (("bad-page", run("bad-page.html", "https://example.com/pricing")),
                    ("good-page", run("good-page.html", "https://example.com/pricing")),
                    ("edge-page", run("edge-page.html", "https://example.com/guide"))):
    for _f in _rec["findings"]:
        check(_f.get("tier") in _TIERS,
              f"{_name}: finding {_f['code']} carries tier {_f.get('tier')!r}, "
              f"which is not one of the four")

# ── the H1 count is not a finding, and the doctrine says so ──────────────────
# onpage-checks.md: "a 'multiple H1s' line in an audit spends a finding on a
# non-finding". The auditor emitted exactly that line, pointing at a file with no
# H1 guidance in it, and an agent reading it writes "consolidate to one H1" —
# which is on the myth list.
_h1 = analyze_html(
    "<html><head><title>t</title></head><body><h1>A</h1><h1>B</h1>"
    "<h2>x</h2><h2>y</h2><h2>z</h2><h2>w</h2><p>copy</p></body></html>"
)
_h1_findings = [f for f in _h1["findings"] if f["code"] == "h1-multiple"]
check(len(_h1_findings) == 1, "the H1 count is still worth reporting, as an accessibility note")
if _h1_findings:
    _m = _h1_findings[0]
    check("onpage-checks.md" in _m["reference"],
          f"h1-multiple must point at the file that owns H1 guidance, got {_m['reference']!r}")
    check("rank" in _m["message"].lower(),
          "h1-multiple must say in the message that the count is not a ranking issue")
    check(_m["severity"] == "info", "h1-multiple is not a defect and must not read as one")
_h1_missing = [f for f in run("bad-page.html", "https://example.com/pricing")["findings"]
               if f["code"] == "h1-missing"]
check(_h1_missing and "onpage-checks.md" in _h1_missing[0]["reference"],
      "h1-missing must point at onpage-checks.md O1, which owns the check")

# ── the thin-content threshold cited a study that refutes it ─────────────────
# intent-and-content.md E2: "Length barely matters". The finding fired at a bare
# 300-word floor and pointed the reader at that section.
_short = analyze_html(
    "<html><head><title>t</title></head><body><h1>h</h1><p>"
    + "word " * 120 + "</p><h2>a</h2><h2>b</h2><h2>c</h2><h2>d</h2></body></html>"
)
_short_findings = {f["code"]: f for f in _short["findings"]}
check("thin" not in _short_findings,
      "the bare word-count finding must be gone — its own reference says length barely matters")
check("low-extractable-text" in _short_findings,
      "a page with little extractable prose is still an observation worth recording")
if "low-extractable-text" in _short_findings:
    _msg = _short_findings["low-extractable-text"]["message"].lower()
    check("length" in _msg and "not" in _msg,
          "the finding must state that length itself is not the ranking signal")

# ── the subhead check keeps the qualifier its doctrine attaches ──────────────
# onpage-checks.md O1: the failure is "0–3 subheads **on a long page**".
_shortpage = analyze_html(
    "<html><head><title>t</title></head><body><h1>h</h1><h2>a</h2>"
    "<p>" + "word " * 90 + "</p></body></html>"
)
check("subheads-thin" not in {f["code"] for f in _shortpage["findings"]},
      "a short page with few subheads must not be flagged — the doctrine scopes it to long pages")
_longpage = analyze_html(
    "<html><head><title>t</title></head><body><h1>h</h1><h2>a</h2>"
    "<p>" + "word " * 900 + "</p></body></html>"
)
check("subheads-thin" in {f["code"] for f in _longpage["findings"]},
      "a long page with one subhead is the case the study actually measured")

# ── the read budget is one engine's median, and the finding must say so ──────
_navheavy = run("bad-page.html", "https://example.com/pricing")
_rb = [f for f in _navheavy["findings"] if f["code"] in ("read-budget", "nav-before-content")]
check(_rb, "bad-page must still produce a read-budget finding")
if _rb:
    _text = _rb[0]["message"].lower()
    check("median" in _text, "the read-budget finding must call ~5,700 chars a median")
    check("deep research" in _text or "chatgpt" in _text,
          "the read-budget finding must name the engine it was measured on")
check(_navheavy["read_budget"].get("window_basis"),
      "the read-budget payload must record what the window is (engine, median, tier)")

# ── data-nosnippet is in the message, so it has to be in the check ───────────
_dns = analyze_html(
    '<html><head><title>t</title></head><body><h1>h</h1>'
    '<p data-nosnippet>Not quotable.</p><p>Body copy here.</p></body></html>'
)
check(_dns.get("data_nosnippet_elements") == 1,
      "data-nosnippet must be counted — the nosnippet finding already claims it is")
check("nosnippet" in {f["code"] for f in _dns["findings"]},
      "an element-level data-nosnippet must surface, like the page-level directive")

# ── the Q&A block: shape, extractability, and schema parity ──────────────────
#
# Four observations people collapse into "add FAQ schema". Each fixture isolates
# one branch: a fixture that trips three findings at once cannot show which rule
# fired.
_FAQ_HEAD = "<h2>Frequently Asked Questions</h2>"


def _faq_dl(n: int) -> str:
    """n question/answer pairs as an always-open definition list."""
    rows = "".join(
        f"<div><dt>Question number {i}?</dt>"
        f'<dd><span aria-hidden="true">&#9492;</span><span>Answer number {i}.</span></dd></div>'
        for i in range(n)
    )
    return f"<dl>{rows}</dl>"


def _faq_details(n: int) -> str:
    """n pairs behind a disclosure widget — an answer one click from a crawler."""
    return "".join(
        f"<details><summary>Question number {i}?</summary><p>Answer number {i}.</p></details>"
        for i in range(n)
    )


_FAQ_LD = (
    '<script type="application/ld+json">'
    '{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question",'
    '"name":"Question number 0?","acceptedAnswer":{"@type":"Answer","text":"Answer number 0."}}]}'
    "</script>"
)

# 1. a readable <dl> FAQ with no FAQPage node — extractable, undeclared.
_qa_open = analyze_html(f"<html><body>{_FAQ_HEAD}{_faq_dl(5)}</body></html>")
_qa_open_codes = {f["code"] for f in _qa_open["findings"]}
check(_qa_open["qa_pairs_visible"] == 5,
      f"five <dt>/<dd> pairs must be counted, got {_qa_open['qa_pairs_visible']}")
check(_qa_open["qa_pairs_collapsed"] == 0,
      "a definition list must not be counted as collapsed")
check("faq-schema-absent" in _qa_open_codes,
      "a readable FAQ with no FAQPage node must be reported")
check("faq-collapsed" not in _qa_open_codes,
      "an always-open definition list must never be reported as collapsed")
check("faq-unpaired" not in _qa_open_codes,
      "a <dl>-paired FAQ must not also be reported as unpaired")
def _finding(result: dict, code: str) -> dict:
    """The named finding, or an empty dict — so a missing one fails a check with a
    message instead of raising StopIteration and hiding every check below it."""
    return next((f for f in result["findings"] if f["code"] == code), {})


# The payoff claim is the part most likely to be overstated, so it is pinned.
_absent = _finding(_qa_open, "faq-schema-absent")
check("2023" in _absent.get("message", ""),
      "faq-schema-absent must date Google's FAQ rich-result restriction, not promise stars")
check(_absent.get("severity") == "low",
      f"an already-extractable FAQ is a low-severity gap, got {_absent.get('severity')}")

# 2. the same FAQ behind <details> — a click away rather than text on the page.
_qa_shut = analyze_html(f"<html><body>{_FAQ_HEAD}{_faq_details(5)}</body></html>")
_qa_shut_codes = {f["code"] for f in _qa_shut["findings"]}
check(_qa_shut["qa_pairs_collapsed"] == 5,
      f"five <details>/<summary> pairs must be counted, got {_qa_shut['qa_pairs_collapsed']}")
check("faq-collapsed" in _qa_shut_codes, "answers behind <details> must be reported")
check("faq-unpaired" not in _qa_shut_codes,
      "<details>/<summary> is a pairing; it must not also be called unpaired")
_collapsed = _finding(_qa_shut, "faq-collapsed")
check("accessibility tree" in _collapsed.get("message", "")
      or "can index" in _collapsed.get("message", ""),
      "faq-collapsed must concede that <details> is indexable, not imply it is invisible")

# 3. an FAQ heading over unpaired prose — nothing marks question from answer.
_qa_bare = analyze_html(
    f"<html><body>{_FAQ_HEAD}<p>Is it fast?</p><p>Yes, very.</p></body></html>")
check("faq-unpaired" in {f["code"] for f in _qa_bare["findings"]},
      "an FAQ heading with no <dt>/<dd> or <details> pairing must be reported")

# 4. an FAQPage node over answers that are not in the served markup.
_qa_orphan = analyze_html(f"<html><body>{_FAQ_HEAD}{_FAQ_LD}<p>Nothing here.</p></body></html>")
_orphan_codes = {f["code"] for f in _qa_orphan["findings"]}
check("FAQPage" in _qa_orphan["jsonld_types"], "the FAQPage fixture must parse")
check("faq-schema-orphan" in _orphan_codes,
      "an FAQPage node with no visible pairing must be reported")
check("faq-schema-absent" not in _orphan_codes,
      "a page that declares FAQPage must not also be told its schema is absent")

# 5. THE FALSE POSITIVE THIS SECTION EXISTS TO PREVENT, reproduced on a live
# page on 2026-08-14. An ARIA disclosure accordion renders every answer into the
# HTML and hides it with CSS. Counting only <dt>/<dd> and <details> read that as
# "no pairing", and the module then reported `high` / `CONFIRMED` "the answers
# are absent" about text sitting in the response it had just parsed.
_ARIA_FAQ = "".join(
    f'<div><button aria-expanded="false" aria-controls="p{i}" id="b{i}">Is it fast?</button>'
    f'<div id="p{i}" role="region" aria-labelledby="b{i}">'
    f'<p>Yes. It answers in well under one second on the median request.</p></div></div>'
    for i in range(3))
_ARIA_LD = ('<script type="application/ld+json">{"@context":"https://schema.org",'
            '"@type":"FAQPage","mainEntity":[{"@type":"Question","name":"Is it fast?",'
            '"acceptedAnswer":{"@type":"Answer","text":"Yes. It answers in well under one '
            'second on the median request."}}]}</script>')
_aria = analyze_html(f"<html><body>{_FAQ_HEAD}{_ARIA_LD}{_ARIA_FAQ}</body></html>")
_aria_codes = {f["code"] for f in _aria["findings"]}
check(_aria["qa_pairs_aria"] == 3,
      f"the ARIA disclosure pattern must count as pairing; got {_aria['qa_pairs_aria']}")
check("faq-schema-orphan" not in _aria_codes,
      "answers that ARE in the served HTML must never be reported as absent — this is the "
      "false positive the whole check was rewritten for")
check("faq-unpaired" not in _aria_codes,
      "an accessible accordion is a pairing; only <dt>/<dd> and <details> were being counted")
check(_aria["faq_declared"] == 1 and _aria["faq_declared_served"] == 1,
      f"the declared answer must be found in the served body; got {_aria}")

# 6. and the partial case — some declared answers served, some not. The usual
# cause is an unsubstituted template in one of the two renderers, which is
# exactly what the live page turned out to be doing.
_DRIFT_LD = ('<script type="application/ld+json">{"@context":"https://schema.org",'
             '"@type":"FAQPage","mainEntity":[{"@type":"Question","name":"Is it fast?",'
             '"acceptedAnswer":{"@type":"Answer","text":"Yes. It answers in well under one '
             'second on the median request."}},{"@type":"Question","name":"Cost?",'
             '"acceptedAnswer":{"@type":"Answer","text":"Plans start at ${seat} per month '
             'with credits included."}}]}</script>')
_drift = analyze_html(f"<html><body>{_FAQ_HEAD}{_DRIFT_LD}{_ARIA_FAQ}</body></html>")
_drift_codes = {f["code"] for f in _drift["findings"]}
check(_drift["faq_declared"] == 2 and _drift["faq_declared_served"] == 1,
      f"one of two declared answers is on the page; got {_drift}")
check("faq-schema-partial" in _drift_codes,
      "an answer declared but not served is drift between the node and the page, and it "
      "is a different finding from an orphan node")
check("faq-schema-orphan" not in _drift_codes,
      "a node with SOME answers served is not an orphan")

# 7. a node whose answers cannot be read at all: absence is not established, so
# the tier drops. Asserting CONFIRMED here is the mistake this file is about.
_UNREADABLE = ('<script type="application/ld+json">{"@context":"https://schema.org",'
               '"@type":"FAQPage","mainEntity":[]}</script>')
_unread = analyze_html(f"<html><body>{_FAQ_HEAD}{_UNREADABLE}<p>Nothing.</p></body></html>")
check("faq-schema-unreadable" in {f["code"] for f in _unread["findings"]},
      "an FAQPage node with no readable answers and no pairing must say so rather than "
      "claim the answers are absent")
check(page_audit.FINDING_TIERS["faq-schema-unreadable"] == "HYPOTHESIS",
      "'I could not read it' is the opposite of a confirmed absence — non-negotiable #8")

# A heading is required: a page with a stray <dl> is a glossary, not an FAQ.
_gloss = analyze_html(
    "<html><body><h2>Glossary</h2><dl><dt>Term</dt><dd>Sense</dd></dl></body></html>")
check(_gloss["faq_heading"] is None,
      f"'Glossary' must not match as an FAQ heading, got {_gloss['faq_heading']!r}")
check("faq-unpaired" not in {f["code"] for f in _gloss["findings"]},
      "a non-FAQ heading must not trip the unpaired finding")

# Absence findings must not survive a fragment; positive counts must.
check("faq-unpaired" in page_audit.COMPLETENESS_DEPENDENT
      and "faq-schema-orphan" in page_audit.COMPLETENESS_DEPENDENT,
      "the two findings that assert 'no pairing found' must be completeness-dependent")
check("faq-collapsed" not in page_audit.COMPLETENESS_DEPENDENT
      and "faq-schema-absent" not in page_audit.COMPLETENESS_DEPENDENT,
      "a count of pairs found survives truncation and must not be dropped")
for _code in ("faq-collapsed", "faq-unpaired", "faq-schema-absent", "faq-schema-orphan"):
    check(_code in page_audit.FINDING_TIERS, f"{_code} must carry an evidence tier")

# ── exit code: a run where nothing could be fetched is not a success ─────────
_allfail = subprocess.run(
    [sys.executable, SCRIPT, "--url", "ftp://example.com/x", "--format", "json"],
    capture_output=True, text=True,
)
check(_allfail.returncode == 1,
      f"a run where every URL failed must exit non-zero, got {_allfail.returncode}")
check(json.loads(_allfail.stdout)[0].get("error"),
      "the failing run must still print the error row it collected")

if not failures:
    residue.close_case("page_audit behaviour")
residue.report()

if failures:
    print("FAIL: page_audit behavior")
    for f in failures:
        print(" - " + f)
    sys.exit(1)
print("PASS: page_audit behavior (3 fixtures, markdown + json + scheme guard + headers, "
      "gzip, url-list and error paths, blindness caveat, schema completeness, "
      "directive parsing, price provenance, truncation honesty, per-finding tiers)")
