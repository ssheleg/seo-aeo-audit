#!/usr/bin/env python3
"""Behaviour tests for scripts/bwt_pull.py and preflight.py's Bing probe.

Offline. The network is replaced by recorded responses in test/fixtures/bwt/, whose
shapes are Microsoft's documented JSON samples for GetQueryStats, GetPageStats,
GetUserSites and the error body (values invented). Exit 0 = pass.
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import sys
import urllib.error
from email.message import Message
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import residue  # noqa: E402

residue.open_case("bwt behaviour")
SCRIPTS = os.path.join(ROOT, "plugins", "seo-aeo-audit", "skills", "seo-aeo-audit", "scripts")
FIX = os.path.join(ROOT, "test", "fixtures", "bwt")
sys.dont_write_bytecode = True
failures: list[str] = []
SECRET = "fixture-secret-0123456789"


def load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(SCRIPTS, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


bwt = load("bwt_pull")
pre = load("preflight")


def check(cond, msg):
    if not cond:
        failures.append(msg)


def fixture(name):
    with open(os.path.join(FIX, name), "rb") as fh:
        return fh.read()


class Resp(io.BytesIO):
    def __init__(self, body, status=200):
        super().__init__(body)
        self.status = self.code = status
        self.headers = Message()
        self.headers["Content-Length"] = str(len(body))
        self.headers["Content-Type"] = "application/json"

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()


def fake(routes, seen):
    """routes: method name -> (status, fixture file) or an exception instance."""
    def urlopen(req, timeout=None):
        url = req.full_url if hasattr(req, "full_url") else req
        seen.append((url, dict(req.header_items()) if hasattr(req, "header_items") else {}))
        method = url.split("/json/", 1)[1].split("?", 1)[0]
        route = routes[method]
        if isinstance(route, Exception):
            raise route
        status, name = route
        body = fixture(name).replace(b"__SECRET__", SECRET.encode())
        if status != 200:
            hdrs = Message()
            hdrs["Content-Length"] = str(len(body))
            raise urllib.error.HTTPError(url, status, "fixture", hdrs, io.BytesIO(body))
        return Resp(body)
    return urlopen


def run(argv, routes, stdin_text=SECRET + "\n"):
    seen = []
    out, err = io.StringIO(), io.StringIO()
    with mock.patch.object(bwt.urllib.request, "urlopen", fake(routes, seen)), \
            contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = bwt.main(argv, stdin=io.StringIO(stdin_text))
    return rc, out.getvalue(), seen


OK = {"GetQueryStats": (200, "query-stats.json"), "GetPageStats": (200, "page-stats.json")}

# 1. Aggregation against hand-computed numbers.
rc, out, seen = run(["--site", "https://example.com/", "--key-stdin", "--format", "json"], OK)
data = json.loads(out)
q = data["reports"]["query"]
check(rc == 0, f"a run with rows exits 0, got {rc}")
check([r["key"] for r in q["rows"]] == ["invoice template", "acme pricing"],
      f"rows sorted by impressions, got {[r['key'] for r in q['rows']]}")
inv = q["rows"][0]
# 100 + 300 impressions, 10 + 15 clicks, CTR 25/400, position (4*100 + 8*300)/400 = 7.0
check((inv["impressions"], inv["clicks"], inv["ctr"], inv["avg_impression_position"])
      == (400, 25, 0.0625, 7.0), f"aggregation wrong: {inv}")
check((inv["first_date"], inv["last_date"]) == ("2025-10-12", "2025-10-19"),
      f"the /Date(ms-0700)/ stamps must parse to UTC dates: {inv}")
check(q["malformed"] == 1, "a row with non-numeric impressions is dropped and counted")
check(data["coverage"]["returned"] == 2 and data["coverage"]["state"] == "partial",
      f"two reports returned; the malformed row makes coverage partial: {data['coverage']}")

# 2. The key travels only as the documented apikey parameter to ssl.bing.com and is
#    never printed.
check(all(u.startswith("https://ssl.bing.com/webmaster/api.svc/json/") for u, _ in seen),
      f"key mode calls the documented key host: {[u for u, _ in seen]}")
check(all("apikey=" + SECRET in u for u, _ in seen), "the key is sent as apikey")
check(SECRET not in out, "the key never reaches the output")
check("| args |" not in out or SECRET not in out, "nor the producer block")

# 3. Token mode: bearer header, the OAuth host, no apikey in the URL.
rc, out, seen = run(["--site", "https://example.com/", "--token-stdin", "--report", "query"], OK)
check(rc == 0 and len(seen) == 1, "one report, one call")
check(seen[0][0].startswith("https://www.bing.com/webmaster/api.svc/json/GetQueryStats")
      and "apikey" not in seen[0][0], f"token mode uses the OAuth host and no apikey: {seen[0][0]}")
check(seen[0][1].get("Authorization") == "Bearer " + SECRET, "token sent as a Bearer header")
check("| invoice template | 400 | 25 | 6.25% | 7.0 |" in out, "the markdown table carries the sums")
check("impression-weighted" in out and "weekly" in out, "the method and the weekly cadence are stated")
check("| script | `bwt_pull.py` |" in out, "the default format carries the producer block")

# 4. Gates: invalid key -> login (redacted), 403 -> scope, no status -> network.
bad = {"GetQueryStats": (400, "error-invalid-key.json"), "GetPageStats": (403, "error-forbidden.json")}
rc, out, _ = run(["--site", "https://example.com/", "--key-stdin", "--format", "json"], bad)
d = json.loads(out)
check(rc == 1, "a run where every report failed exits 1")
check(d["reports"]["query"]["gate"] == "login", f"InvalidApiKey is the login gate: {d['reports']['query']}")
check(d["reports"]["page"]["gate"] == "scope", f"HTTP 403 is the scope gate: {d['reports']['page']}")
check(SECRET not in out, "an error body never echoes the key")
net = {"GetQueryStats": urllib.error.URLError("fixture: no route to " + SECRET)}
rc, out, _ = run(["--site", "https://example.com/", "--key-stdin", "--report", "query",
                  "--format", "json"], net)
check(json.loads(out)["reports"]["query"]["gate"] == "network" and SECRET not in out,
      "a transport failure is the network gate, with the key redacted")

# A provider error body that echoes the request URL must not carry the key out.
rc, out, _ = run(["--site", "https://example.com/", "--key-stdin", "--report", "query"],
                 {"GetQueryStats": (400, "error-echo.json")})
check(SECRET not in out and "<redacted>" in out, "an echoed apikey is redacted from the error")

# 5. Empty answer is measured nothing, and no credential never calls out.
rc, out, _ = run(["--site", "https://example.com/", "--key-stdin", "--report", "query"],
                 {"GetQueryStats": (200, "empty.json")})
check(rc == 1 and "NOTHING MEASURED" in out, "an empty report exits 1 and says NOTHING MEASURED")
rc, out, seen = run(["--site", "https://example.com/", "--key-stdin", "--format", "json"], OK,
                    stdin_text="")
check(rc == 1 and not seen and json.loads(out)["coverage"]["attempted"] == 0
      and json.loads(out)["reports"]["query"]["gate"] == "login",
      "no credential on stdin: no request, login gate, nothing attempted")
check(bwt.read_secret(None) == "", "no stream is no credential")

# 6. preflight names the failing Bing gate.
def bing_probe(route, site="https://example.com/", secret=SECRET, kind="key"):
    seen = []
    def urlopen(req, timeout=None):
        url = req.full_url
        seen.append(url)
        if isinstance(route, Exception):
            raise route
        status, name = route
        body = fixture(name)
        if status != 200:
            hdrs = Message()
            hdrs["Content-Length"] = str(len(body))
            raise urllib.error.HTTPError(url, status, "fixture", hdrs, io.BytesIO(body))
        return Resp(body)
    with mock.patch.object(pre.urllib.request, "urlopen", urlopen):
        return pre.check_bing(site, secret, kind), seen

row, _ = bing_probe((200, "user-sites.json"))
check(row["reachable"] and row.get("gate") is None, f"a verified listed site passes: {row}")
row, _ = bing_probe((200, "user-sites.json"), site="https://unverified.example")
check(not row["reachable"] and row["gate"] == "scope", f"listed but unverified is scope: {row}")
row, _ = bing_probe((200, "user-sites.json"), site="https://other.example/")
check(not row["reachable"] and row["gate"] == "scope", f"absent from the account is scope: {row}")
row, _ = bing_probe((400, "error-invalid-key.json"))
check(not row["reachable"] and row["gate"] == "login" and SECRET not in json.dumps(row),
      f"InvalidApiKey is login, redacted: {row}")
row, _ = bing_probe((403, "error-forbidden.json"))
check(row["gate"] == "scope", f"403 is scope: {row}")
row, seen = bing_probe((200, "user-sites.json"), secret="")
check(row["gate"] == "login" and not seen, "no credential: login gate and no request")
row, seen = bing_probe((200, "user-sites.json"), kind="token")
check(row["reachable"] and seen[0].startswith("https://www.bing.com/") and "apikey" not in seen[0],
      "token mode probes the OAuth host without an apikey")
for gate in ("login", "scope", "network", "http"):
    check(gate in pre.COVERAGE_GATES, f"gate {gate} must be declared in COVERAGE_GATES")

if not failures:
    residue.close_case("bwt behaviour")
residue.report()
if failures:
    print("FAIL: bwt behaviour")
    for f in failures:
        print(" - " + f)
    sys.exit(1)
print("PASS: bwt behaviour (recorded fixtures: aggregation, key and token transport, "
      "redaction, login/scope/network gates, empty report, preflight Bing probe)")
