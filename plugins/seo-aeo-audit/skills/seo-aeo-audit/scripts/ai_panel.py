#!/usr/bin/env python3
"""ai_panel: score captured answer-engine responses against a fixed prompt panel.

The script only SCORES. Capturing stays manual (a person in a browser, ideally
WebKit first per references/tooling.md) or tool-driven; every capture is one record
in a JSON or JSONL file, and this script reads nothing else.

One record is one answer to one prompt:

  {"prompt_id": "p1", "prompt": "best invoicing tool for freelancers",
   "engine": "chatgpt", "mode": "search", "account_state": "logged-out",
   "locale": "en-US", "date": "2026-10-19", "run": 1,
   "source": "ui-capture",            # or "api-proxy"; required, never inferred
   "answer": "full answer text",
   "cited_urls": ["https://example.com/pricing", "..."],
   "recommended": true}               # optional, a human label; absent = unlabelled

For each cell (prompt x engine x mode x account state x locale x source) it reports:

  mention         the brand (any --brand alias) appears in the answer text
  top-3 mention   the brand is among the first three of brand + --competitor names
                  by first appearance in the answer (with no competitors given, a
                  mention is rank 1)
  recommendation  the record's own `recommended` label; unlabelled runs are counted
                  apart and never read as "not recommended"
  citation        a cited URL's host is a --domain or one of its subdomains
  run-to-run Jaccard  mean pairwise Jaccard similarity of the cited-URL sets across
                  the cell's runs (URLs normalised: scheme, host case, trailing
                  slash, fragment)

Every proportion is printed as raw counts (k/n) with a Wilson score 95% interval.
The interval treats runs as independent draws; they are not (same model, same day,
same account), so the true uncertainty is wider than printed. That caveat travels
in every report.

**A single run is not a verdict.** A cell with fewer than MIN_RUNS runs, or runs on
fewer than MIN_DAYS distinct dates, is `insufficient-sample`: its raw counts print,
its rates and intervals do not. Answers vary run to run, and one transcript says
what one answer said.

**`api-proxy` input under-covers.** Records labelled `api-proxy` are scored in
their own cells and every report says so: a preprint (arXiv 2610.15382, `STUDY`)
found that Google Search plus the OpenAI Responses API recovered only 28.3% and
26.2% of the URLs ChatGPT cited (two model versions). A record with no `source`
label, or any other value, is rejected rather than guessed.

Usage:
  ai_panel.py --captures panel.json --brand "Acme" --brand "Acme Inc" --domain acme.com
  ai_panel.py --captures panel.jsonl --brand Acme --domain acme.com \
      --competitor Globex --competitor Initech --format json

Every output carries a **producer block**: `skill` (this tool's version), `script`,
`observed_at` (UTC), `runtime`, `args` (credential values redacted), `scope` (the
resolved input set), and `actor` / `model` / `trace` from `SEO_AEO_AUDIT_ACTOR`,
`_MODEL`, `_TRACE`. It is present in the default output and under `--format json` as
`producer`. A field the harness did not supply reads `unavailable: <VAR> is not set by
this harness`, never guessed, and never dropped, because a field that vanishes when
unavailable is indistinguishable from one nobody checked. `observed_at` is the field
that decides whether a finding has expired; the report's own `## Provenance` block adds
the four invalidators (see references/preflight.md). Here `observed_at` is when the
captures were scored; each record's own `date` is when it was captured.

Exit codes: 0 = at least one capture record was valid and scored (an all
insufficient-sample panel still exits 0: its counts are the report, and the
report says no verdict is possible); 1 = an unreadable captures file or no valid
record; 2 = argparse usage error (no --brand or --domain).
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import os
import re
import sys
import time
from urllib.parse import urlsplit, urlunsplit


# ── provenance: the execution that produced this payload ── shared block ──────
# Copied verbatim into all nine scripts and compared byte for byte by
# `test/validate.py`, for the same reason `_flat` is: these ship as standalone files
# with no shared module, and an import of one does not exist in the installed layout
# (`bin/seo-aeo-audit.js` copies `scripts/` alone into `~/.claude/skills/`). The
# doctrine behind the field set lives above this block in preflight.py. Never edit
# one copy — the guard fails all nine.
SKILL_VERSION = "0.32.0"

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
        # Flattened here rather than through `_flat`: this shared block must
        # render independently of the collector-specific helper.
        # test/validate.py counts the actual helper homes.
        cell = " ".join(str(v).split()).replace("|", "\\|")
        if len(cell) > 300:
            cell = cell[:299].rstrip() + "…"
        lines.append(f"| {f} | `{cell}` |")
    return "\n".join(lines)
# ── end provenance shared block ──────────────────────────────────────────────


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


# ── collector coverage shared block ───────────────────────────────────────────
# Kept byte-identical in migrated standalone collectors; test_output_contracts
# compares the copies. docs/contracts/collector-coverage.md owns the semantics.
def collector_coverage(unit, scope, requested, attempted, returned, dropped, reasons):
    """Account one invocation's logical inputs, never redirect/retry attempts.

    A usable return is defined by each collector's scope. None is unknown, not
    zero. This record does not certify a whole site or provider dataset.
    """
    counts = (requested, attempted, returned, dropped)
    if not all(v is None or (type(v) is int and v >= 0) for v in counts):
        raise ValueError("coverage counts must be nonnegative integers or null")
    if not all(isinstance(v, str) and v.strip() for v in (unit, scope)) or not isinstance(reasons, list):
        raise ValueError("coverage needs a unit, scope and reason list")
    if any(not isinstance(r, dict) or not all(isinstance(r.get(k), str) and r[k].strip()
                                            for k in ("code", "detail")) for r in reasons):
        raise ValueError("coverage reasons need code and detail")
    if all(v is not None for v in (requested, attempted, dropped)) and attempted + dropped != requested:
        raise ValueError("coverage attempted + dropped must equal requested")
    if requested is not None and any(v is not None and v > requested for v in (attempted, returned, dropped)):
        raise ValueError("known coverage counts cannot exceed requested")
    if returned is not None and attempted is not None and returned > attempted:
        raise ValueError("coverage returned cannot exceed attempted")
    unknown = any(v is None for v in counts)
    gap = unknown or dropped or (returned != attempted)
    if gap and not reasons:
        raise ValueError("coverage gaps and unknown counts need reasons")
    state = "unknown" if unknown else "partial" if gap or reasons else "complete"
    return {"schema": "collector-coverage/1", "unit": unit, "scope": scope,
            "requested": requested, "attempted": attempted, "returned": returned,
            "dropped": dropped, "state": state, "reasons": reasons}


def collector_coverage_md(record):
    counts = " · ".join(f"{k}={record[k] if record[k] is not None else 'unknown'}"
                         for k in ("requested", "attempted", "returned", "dropped"))
    lines = ["## Collector coverage", "",
             f"State: **{record['state']}** · unit: `{_flat(record['unit'])}` · {counts}",
             "Scope: " + _flat(record["scope"], 500)]
    lines += [f"- `{_flat(r['code'])}`: {_flat(r['detail'])}" for r in record["reasons"]]
    return "\n".join(lines)
# ── end collector coverage shared block ───────────────────────────────────────


# A cell needs this many runs, on this many distinct capture dates, before a rate is
# printed. Three runs over two days is a floor, not a recommendation:
# references/aeo-geo.md F5 asks for more where the decision is expensive.
MIN_RUNS = 3
MIN_DAYS = 2
SOURCES = ("ui-capture", "api-proxy")
CELL_KEYS = ("prompt_id", "engine", "mode", "account_state", "locale", "source")
REQUIRED = CELL_KEYS + ("date", "answer")
Z95 = 1.959963984540054
INTERVAL_METHOD = ("Wilson score interval, 95%, treating runs as independent draws; "
                   "runs of one prompt share a model, a day and an account, so the true "
                   "uncertainty is wider than printed")
PROXY_CAVEAT = ("api-proxy cells under-cover UI citations: a preprint (arXiv 2610.15382, "
                "STUDY) found Google Search plus the OpenAI Responses API recovered only "
                "28.3% and 26.2% of the URLs ChatGPT cited (two model versions). Never read an "
                "api-proxy citation rate as a measurement of the UI")


def wilson(k: int, n: int) -> list[float] | None:
    """Wilson score interval for k successes in n trials, rounded to 3 places."""
    if n <= 0:
        return None
    p = k / n
    denom = 1 + Z95 ** 2 / n
    centre = (p + Z95 ** 2 / (2 * n)) / denom
    half = Z95 * math.sqrt(p * (1 - p) / n + Z95 ** 2 / (4 * n * n)) / denom
    return [round(max(0.0, centre - half), 3), round(min(1.0, centre + half), 3)]


def norm_url(url: str) -> str:
    parts = urlsplit(str(url).strip())
    path = parts.path.rstrip("/") or "/"
    return urlunsplit(((parts.scheme or "https").lower(), parts.netloc.lower(), path,
                       parts.query, ""))


def jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b)


def mean_pairwise_jaccard(sets: list[set]) -> float | None:
    pairs = list(itertools.combinations(sets, 2))
    if not pairs:
        return None
    return round(sum(jaccard(a, b) for a, b in pairs) / len(pairs), 3)


def _alias_re(names: list[str]):
    names = [n for n in (x.strip() for x in names) if n]
    if not names:
        return None
    return re.compile(r"(?<!\w)(" + "|".join(re.escape(n) for n in
                                           sorted(names, key=len, reverse=True)) + r")(?!\w)",
                      re.I)


def _first_pos(rx, text: str) -> int | None:
    if rx is None:
        return None
    m = rx.search(text)
    return m.start() if m else None


def host_matches(url: str, domains: list[str]) -> bool:
    host = (urlsplit(str(url)).hostname or "").lower()
    return any(host == d or host.endswith("." + d) for d in domains)


def validate_record(rec, index: int) -> str | None:
    """Why this record cannot be scored, or None."""
    if not isinstance(rec, dict):
        return f"record {index}: not an object"
    missing = [k for k in REQUIRED if not isinstance(rec.get(k), str) or not rec[k].strip()]
    if missing:
        return f"record {index}: missing or empty {', '.join(missing)}"
    if rec["source"] not in SOURCES:
        return (f"record {index}: source {_flat(rec['source'], 40)!r} is not one of "
                f"{', '.join(SOURCES)}; the label is required, never inferred")
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", rec["date"]):
        return f"record {index}: date {_flat(rec['date'], 40)!r} is not YYYY-MM-DD"
    cited = rec.get("cited_urls", [])
    if not isinstance(cited, list) or not all(isinstance(u, str) for u in cited):
        return f"record {index}: cited_urls must be a list of strings"
    if "recommended" in rec and not isinstance(rec["recommended"], bool):
        return f"record {index}: recommended must be true or false when present"
    return None


def score_record(rec: dict, brand_rx, competitor_rxs, domains: list[str]) -> dict:
    text = rec["answer"]
    pos = _first_pos(brand_rx, text)
    mention = pos is not None
    rank = None
    if mention:
        others = [p for p in (_first_pos(rx, text) for rx in competitor_rxs) if p is not None]
        rank = 1 + sum(1 for p in others if p < pos)
    cited = {norm_url(u) for u in rec.get("cited_urls", []) if str(u).strip()}
    return {"mention": mention, "top3": bool(rank is not None and rank <= 3), "rank": rank,
            "recommended": rec.get("recommended"),
            "citation": any(host_matches(u, domains) for u in cited),
            "cited": cited, "date": rec["date"]}


def _rate(k: int, n: int, sufficient: bool) -> dict:
    out = {"k": k, "n": n}
    if sufficient and n:
        out["rate"] = round(k / n, 3)
        out["interval_95"] = wilson(k, n)
    return out


def score_cell(key: tuple, scored: list[dict]) -> dict:
    n = len(scored)
    days = sorted({s["date"] for s in scored})
    sufficient = n >= MIN_RUNS and len(days) >= MIN_DAYS
    labelled = [s for s in scored if isinstance(s["recommended"], bool)]
    cell = dict(zip(CELL_KEYS, key))
    cell.update({
        "runs": n, "days": len(days), "dates": days,
        "verdict": "measured" if sufficient else "insufficient-sample",
        "mention": _rate(sum(s["mention"] for s in scored), n, sufficient),
        "top3_mention": _rate(sum(s["top3"] for s in scored), n, sufficient),
        "recommendation": _rate(sum(bool(s["recommended"]) for s in labelled), len(labelled),
                                sufficient),
        "recommendation_unlabelled": n - len(labelled),
        "citation": _rate(sum(s["citation"] for s in scored), n, sufficient),
        "cited_url_jaccard": mean_pairwise_jaccard([s["cited"] for s in scored]),
    })
    if not sufficient:
        cell["why"] = (f"{n} run(s) on {len(days)} day(s); a verdict needs at least "
                       f"{MIN_RUNS} runs on at least {MIN_DAYS} distinct days")
    return cell


def load_captures(path: str) -> tuple[list | None, str | None]:
    try:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
    except (OSError, UnicodeError) as exc:
        return None, "cannot read --captures: " + type(exc).__name__
    text = text.strip()
    if not text:
        return [], None
    try:
        data = json.loads(text)
    except ValueError:
        try:
            data = [json.loads(line) for line in text.splitlines() if line.strip()]
        except ValueError as exc:
            return None, "captures file is neither JSON nor JSONL: " + _flat(exc, 120)
    if isinstance(data, dict):
        data = data.get("captures")
    if not isinstance(data, list):
        return None, "captures must be a JSON array, an object with a `captures` array, or JSONL"
    return data, None


def build_report(records: list, brands: list[str], competitors: list[str],
                 domains: list[str]) -> dict:
    brand_rx = _alias_re(brands)
    competitor_rxs = [rx for rx in (_alias_re([c]) for c in competitors) if rx is not None]
    domains = [d.strip().lower().lstrip(".") for d in domains if d.strip()]
    rejected, cells = [], {}
    for i, rec in enumerate(records):
        why = validate_record(rec, i)
        if why:
            rejected.append(why)
            continue
        key = tuple(rec[k].strip() for k in CELL_KEYS)
        cells.setdefault(key, []).append(score_record(rec, brand_rx, competitor_rxs, domains))
    scored_cells = [score_cell(k, v) for k, v in sorted(cells.items())]
    measured = [c for c in scored_cells if c["verdict"] == "measured"]
    return {
        "cells": scored_cells,
        "valid_records": sum(len(v) for v in cells.values()),
        "rejected": rejected,
        "panel_verdict": ("measured" if measured else
                          "insufficient-sample" if scored_cells else "no-valid-record"),
        "interval_method": INTERVAL_METHOD,
        "min_runs": MIN_RUNS, "min_days": MIN_DAYS,
        "api_proxy_cells": sum(1 for c in scored_cells if c["source"] == "api-proxy"),
        "api_proxy_caveat": PROXY_CAVEAT,
    }


def _fmt_rate(r: dict) -> str:
    base = f"{r['k']}/{r['n']}"
    if "rate" in r:
        lo, hi = r["interval_95"]
        return f"{base} ({r['rate']:.0%}, 95% {lo:.0%} to {hi:.0%})"
    return base


def render_markdown(rep: dict) -> str:
    lines = ["# AI answer panel: mention, recommendation, citation", "",
             f"**Panel verdict: {rep['panel_verdict']}** · {rep['valid_records']} valid "
             f"record(s) in {len(rep['cells'])} cell(s) · {len(rep['rejected'])} rejected", ""]
    if rep["panel_verdict"] != "measured":
        lines += [f"> No cell has at least {rep['min_runs']} runs on {rep['min_days']} "
                  "distinct days, so no rate is printed. One transcript says what one answer "
                  "said; it is not a visibility verdict. Re-run each prompt and score again.", ""]
    lines += ["| prompt | engine | mode | account | locale | source | runs/days | verdict | "
              "mention | top-3 | recommended | cited | URL Jaccard |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for c in rep["cells"]:
        rec = _fmt_rate(c["recommendation"]) + (
            f" (+{c['recommendation_unlabelled']} unlabelled)" if c["recommendation_unlabelled"] else "")
        jac = "n/a" if c["cited_url_jaccard"] is None else f"{c['cited_url_jaccard']:.2f}"
        lines.append("| " + " | ".join(_flat(x, 60) for x in (
            c["prompt_id"], c["engine"], c["mode"], c["account_state"], c["locale"],
            c["source"], f"{c['runs']}/{c['days']}", c["verdict"], _fmt_rate(c["mention"]),
            _fmt_rate(c["top3_mention"]), rec, _fmt_rate(c["citation"]), jac)) + " |")
    lines += ["", "- Interval: " + rep["interval_method"] + "."]
    if rep["api_proxy_cells"]:
        lines.append("- ⚠ " + rep["api_proxy_caveat"] + ".")
    for why in rep["rejected"][:20]:
        lines.append("- rejected: " + _flat(why))
    if len(rep["rejected"]) > 20:
        lines.append(f"- rejected: {len(rep['rejected']) - 20} more, see --format json")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--captures", required=True, help="JSON array, {captures: [...]}, or JSONL")
    ap.add_argument("--brand", action="append", default=[], help="brand name or alias (repeatable)")
    ap.add_argument("--domain", action="append", default=[], help="owned domain (repeatable)")
    ap.add_argument("--competitor", action="append", default=[],
                    help="competitor name for the top-3 rank (repeatable)")
    ap.add_argument("--format", choices=["markdown", "json"], default="markdown")
    args = ap.parse_args(argv)
    if not args.brand or not args.domain:
        ap.error("pass at least one --brand and one --domain")

    records, error = load_captures(args.captures)
    input_errors = [{"code": "input_population_unknown", "detail": error}] if error else []
    rep = build_report(records or [], args.brand, args.competitor, args.domain)
    reasons = list(input_errors)
    if rep["rejected"]:
        reasons.append({"code": "record_rejected",
                        "detail": f"{len(rep['rejected'])} record(s) failed validation and were not scored."})
    insufficient = sum(1 for c in rep["cells"] if c["verdict"] != "measured")
    if insufficient:
        reasons.append({"code": "insufficient_sample",
                        "detail": f"{insufficient} cell(s) below {MIN_RUNS} runs on {MIN_DAYS} days; counts only, no rate."})
    if records == [] and not error:
        reasons.append({"code": "no_input", "detail": "The captures file holds no records."})
    n = None if records is None else len(records)
    coverage = collector_coverage(
        "capture_record",
        "Capture records in the --captures file. Returned counts records that passed "
        "validation and were scored; it says nothing about prompts never captured or "
        "engines never asked.",
        n, n, None if records is None else rep["valid_records"], None if n is None else 0,
        reasons)
    prov = provenance("ai_panel.py", argv,
                      f"captures {args.captures}: {rep['valid_records']} valid record(s), "
                      f"{len(rep['cells'])} cell(s); brand {', '.join(args.brand[:3])}; "
                      f"domain {', '.join(args.domain[:3])}")
    if args.format == "json":
        print(json.dumps({"producer": prov, **rep, "coverage": coverage,
                          "input_errors": input_errors}, indent=2))
    else:
        print(render_markdown(rep))
        print("\n" + collector_coverage_md(coverage))
        print("\n" + provenance_md(prov))
    return 0 if rep["valid_records"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
