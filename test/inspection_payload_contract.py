"""URL Inspection typed admission; official schema, offline provider envelopes."""
import importlib.util
import json
from pathlib import Path
from unittest.mock import patch
from collector_coverage_contract import capture, coverage_records


def run(check, root, workspace):
    path = Path(root) / 'plugins/seo-aeo-audit/skills/seo-aeo-audit/scripts/url_inspection.py'
    spec = importlib.util.spec_from_file_location('inspection_payload', path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    count = 0
    def ok(value, label):
        nonlocal count
        count += 1; check(value, 'T2 inspection: ' + label)
    def parsed(raw):
        try:
            result = mod.parse(raw, 'https://example.invalid/a')
            result['findings'] = mod.findings(result)
            return result
        except Exception as exc:
            return {'escaped': type(exc).__name__}
    def answer(fields): return {'inspectionResult': {'indexStatusResult': fields}}
    for raw in ([], None, 1, 'text', {'inspectionResult': []}, answer({}), answer({'unknown': 1}), answer({'verdict': 1}), answer({'verdict': 'FUTURE_STATE'})):
        result = parsed(raw)
        ok('escaped' not in result and not mod.answered_rows([result]) and not any(f['code'] in ('never-crawled', 'not-indexed') for f in result.get('findings', [])), 'malformed/unknown-only payload cannot crash or answer')
    positives = [
        {'verdict': 'PASS'}, {'verdict': 'FAIL'}, {'coverageState': 'Discovered - currently not indexed'},
        {'robotsTxtState': 'DISALLOWED'}, {'pageFetchState': 'NOT_FOUND'},
        {'lastCrawlTime': '2026-10-13T06:00:00.123456789Z'},
        {'googleCanonical': 'https://example.invalid/a'}, {'sitemap': ['https://example.invalid/sitemap.xml']},
    ]
    for fields in positives:
        result = parsed(answer(fields))
        ok('escaped' not in result and bool(mod.answered_rows([result])) and not result.get('payload_errors'), 'recognized typed index observation remains usable')
    fields = ('verdict', 'coverageState', 'indexingState', 'robotsTxtState', 'pageFetchState', 'lastCrawlTime', 'crawledAs', 'googleCanonical', 'userCanonical', 'referringUrls', 'sitemap')
    for field in fields:
        for value in (True, 1, {}):
            result = parsed(answer({field: value}))
            ok('escaped' not in result and not mod.answered_rows([result]) and bool(result.get('payload_errors')), field + ' wrong type is a diagnosed missing observation')
    for field, value, forbidden in [
        ('lastCrawlTime', 'not-a-date', 'never-crawled'),
        ('lastCrawlTime', '2026-99-99T00:00:00Z', 'never-crawled'),
        ('userCanonical', {'bad': 1}, 'canonical-undeclared'),
        ('googleCanonical', 'https://[bad', 'canonical-disagreement'),
        ('pageFetchState', 'FUTURE_STATE', 'fetch-failed'),
    ]:
        fields = {'verdict': 'PASS', 'googleCanonical': 'https://example.invalid/a', 'userCanonical': 'https://example.invalid/a', field: value}
        result = parsed(answer(fields))
        ok('escaped' not in result and bool(mod.answered_rows([result])) and bool(result.get('payload_errors')) and forbidden not in {f['code'] for f in result.get('findings', [])}, 'valid sibling retained without false negative from ' + field)
    for fields in ({'verdict': 'PARTIAL'}, {'verdict': 'VERDICT_UNSPECIFIED'}, {'indexingState': 'BLOCKED_BY_ROBOTS_TXT'}, {'sitemap': []}, {'referringUrls': []}):
        result = parsed(answer(fields))
        ok(not mod.answered_rows([result]), 'reserved/unspecified/empty-only field is no useful index answer')
    mixed = parsed(answer({'verdict': 'PASS', 'sitemap': ['https://example.invalid/map.xml', 1, 'https://[bad']}))
    ok(mixed['sitemaps'] == ['https://example.invalid/map.xml'] and bool(mixed['payload_errors']) and bool(mod.answered_rows([mixed])), 'mixed URL array retains typed members without erasing valid index answer')
    rich = parsed({'inspectionResult': {'richResultsResult': {'verdict': 'PASS', 'detectedItems': [{'richResultType': 'Product'}, {'richResultType': 1}, 1]}}})
    ok(not mod.answered_rows([rich]) and rich['rich_result_types'] == ['Product'] and bool(rich['payload_errors']), 'rich-result observations alone do not certify index status')
    with patch.object(mod, 'access_token', return_value='offline-token'), patch.object(mod, 'inspect', return_value=answer({'verdict': 'PASS', 'lastCrawlTime': 1})):
        code, out, _ = capture(mod.main, ['--site', 'sc-domain:example.invalid', '--urls', 'https://example.invalid/a', '--format', 'json'])
    report = json.loads(out)
    ok(code == 0 and report['coverage']['returned'] == 1 and report['coverage']['state'] == 'partial' and 'never-crawled' not in {f['code'] for f in report['results'][0]['findings']}, 'usable return with malformed sibling stays partial and does not invent missing-crawl evidence')
    for fmt in ('json', 'markdown'):
        with patch.object(mod, 'access_token', return_value='offline-token'), patch.object(mod, 'inspect', side_effect=[[], answer({'verdict': 1}), answer({'verdict': 'PASS', 'lastCrawlTime': 1})]), patch.object(mod.time, 'sleep'):
            try: code, out, err = capture(mod.main, ['--site', 'sc-domain:example.invalid', '--urls', 'https://example.invalid/a', 'https://example.invalid/b', 'https://example.invalid/c', '--format', fmt])
            except Exception as exc: code, out, err = 99, '', type(exc).__name__
        ok(code == 0 and bool(out), 'actual ' + fmt + ' main preserves valid sibling after malformed rows')
        if fmt == 'json' and out:
            data = json.loads(out); cov = coverage_records(data)[0]
            ok(cov['requested'] == cov['attempted'] == 3 and cov['returned'] == 1 and cov['state'] == 'partial' and len(data['results']) == 3, 'actual mixed payload counts admission once per URL')
        if fmt == 'markdown' and out:
            ok('payload' in out.lower() and 'lastCrawlTime' in out, 'default output exposes typed payload limitation')
    source = path.read_text()
    needle = 'result["has_index_status"] = any(bool(result[output]) for output in INDEX_FIELDS.values())'
    ok(source.count(needle) == 1, 'false index-answer mutation selector unique')
    bad_path = Path(workspace) / 'inspection-false-answer.py'
    bad_path.write_text(source.replace(needle, 'result["has_index_status"] = bool(idx)', 1))
    spec = importlib.util.spec_from_file_location('inspection_false_answer', bad_path)
    mutant = importlib.util.module_from_spec(spec); spec.loader.exec_module(mutant)
    result = mutant.parse(answer({'unknown': 1}), 'https://example.invalid/a')
    ok(bool(mutant.answered_rows([result])), 'unknown-only negative detects false-answer source mutation')
    import os, subprocess, sys, threading
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    calls = []
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args): pass
        def do_POST(self):
            data = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
            calls.append(data['inspectionUrl'])
            value = [] if data['inspectionUrl'].endswith('/a') else answer({'verdict': 1}) if data['inspectionUrl'].endswith('/b') else answer({'verdict': 'PASS', 'lastCrawlTime': 1})
            raw = json.dumps(value).encode(); self.send_response(200); self.send_header('Content-Length', str(len(raw))); self.end_headers(); self.wfile.write(raw)
    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
    try:
        endpoint = 'API = "https://searchconsole.googleapis.com/v1"'
        ok(source.count(endpoint) == 1, 'standalone endpoint rewrite unique')
        copy = Path(workspace) / 'url-inspection-copy.py'
        copy.write_text(source.replace(endpoint, f'API = "http://127.0.0.1:{server.server_port}"'))
        bindir = Path(workspace) / 'bin'; bindir.mkdir(exist_ok=True)
        fake = bindir / 'gcloud'; fake.write_text('#!' + sys.executable + '\nprint("offline-token")\n'); fake.chmod(0o755)
        env = dict(os.environ, PATH=str(bindir) + os.pathsep + os.environ.get('PATH', ''))
        for fmt in ('json', 'markdown'):
            proc = subprocess.run([sys.executable, '-B', str(copy), '--site', 'sc-domain:example.invalid', '--urls', 'https://example.invalid/a', 'https://example.invalid/b', 'https://example.invalid/c', '--format', fmt], cwd=workspace, env=env, capture_output=True, text=True, timeout=15)
            ok(proc.returncode == 0 and 'offline-token' not in proc.stdout + proc.stderr, 'actual copied ' + fmt + ' CLI preserves mixed typed observations without token echo')
            if fmt == 'json':
                report = json.loads(proc.stdout)
                ok(report['coverage']['returned'] == 1 and report['coverage']['state'] == 'partial' and len(report['results']) == 3, 'actual copied CLI uses one typed-answer predicate')
            else: ok('payload limitation' in proc.stdout and '1 of 3' in proc.stdout, 'actual copied default report scopes evidence to admitted fields')
        ok(len(calls) == 6, 'two copied runs attempted each declared input once using loopback only')
    finally: server.shutdown(); server.server_close(); thread.join(timeout=2)
    print(f'T2 URL Inspection payload: {count} controls')


if __name__ == '__main__':
    import residue
    failures = []; residue.open_case('inspection-payload'); work = residue.workspace('inspection-payload')
    run(lambda cond, label: failures.append(label) if not cond else None, Path(__file__).resolve().parents[1], work)
    if not failures: residue.close_case('inspection-payload')
    residue.report()
    if failures:
        print('FAIL: inspection payload\n' + '\n'.join('  - ' + item for item in failures)); raise SystemExit(1)
    print('PASS: inspection payload')
