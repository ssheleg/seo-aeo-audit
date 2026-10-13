"""Offline and loopback acceptance for sitemap document coverage, not page totals."""
import contextlib
import gzip
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch
from collector_coverage_contract import capture, schema_errors


def load(root):
    path = Path(root) / 'plugins/seo-aeo-audit/skills/seo-aeo-audit/scripts/sitemap_audit.py'
    spec = importlib.util.spec_from_file_location('sitemap_coverage_subject', path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod, path


def run(check, root, workspace):
    sm, path = load(root)
    count = 0
    def ok(condition, label):
        nonlocal count
        count += 1
        check(condition, 'B-9 sitemap: ' + label)
    page = '<urlset><url><loc>https://example.invalid/a</loc></url></urlset>'
    empty = '<urlset/>'
    def index(*urls):
        return '<sitemapindex>' + ''.join('<sitemap><loc>' + u + '</loc></sitemap>' for u in urls) + '</sitemapindex>'
    base = 'https://example.invalid/'
    def scenario(name, bodies, cap, expected, exit_code, reason=None):
        args = ['--url', base + 'root', '--max-maps', str(cap)]
        def get(url):
            item = bodies[url[len(base):]]
            if isinstance(item, Exception): raise item
            return item
        with patch.object(sm, 'fetch', side_effect=get) as fetch:
            code, raw, _ = capture(sm.main, args + ['--format', 'json'])
            calls = fetch.call_count
        try: data = json.loads(raw)
        except ValueError:
            ok(False, name + ': JSON report absent'); return
        record = data.get('coverage')
        ok(not schema_errors(record), name + ': independently valid schema')
        ok(code == exit_code, name + ': exit semantics')
        ok(record is not None and all(record.get(k) == v for k, v in expected.items()), name + ': measured units/counts/state')
        ok(record is not None and record['attempted'] == calls, name + ': actual fetch count')
        ok(record and data.get('traversal', {}).get('known_discovered', -1) >= calls and len(data.get('sources', [])) == calls, name + ': observed discovery and legacy attempted sources')
        ok(record and len(data.get('errors', [])) == calls - record['returned'], name + ': failures remain explicit attempted documents')
        if name == 'failed child after success':
            ok(data['analysis']['urls_total'] == 1, name + ': earlier page result survives')
        if reason: ok(record and reason in {r['code'] for r in record['reasons']}, name + ': explicit reason')
        with patch.object(sm, 'fetch', side_effect=get):
            text_code, text, _ = capture(sm.main, args)
        ok(text_code == code and record is not None and sm.collector_coverage_md(record) in text, name + ': Markdown/JSON parity')
        return data
    scenarios = [
        ('complete', {'root': page}, 5, dict(requested=1, attempted=1, returned=1, dropped=0, state='complete'), 0, None),
        ('valid empty', {'root': empty}, 5, dict(requested=1, returned=1, state='complete'), 1, None),
        ('duplicate at cap', {'root': index(base+'child', base+'child'), 'child': page}, 2, dict(requested=2, attempted=2, returned=2, dropped=0, state='complete'), 0, None),
        ('nested cycle', {'root': index(base+'child'), 'child': index(base+'root', base+'leaf'), 'leaf': page}, 3, dict(requested=3, attempted=3, returned=3, dropped=0, state='complete'), 0, None),
        ('cap frontier', {'root': index(base+'child')}, 1, dict(requested=None, attempted=1, returned=1, dropped=1, state='unknown'), 1, 'unknown_frontier'),
        ('failed root', {'root': OSError('fixture failed')}, 5, dict(requested=None, attempted=1, returned=0, dropped=0, state='unknown'), 1, 'input_failed'),
        ('failed child after success', {'root': index(base+'good', base+'bad'), 'good': page, 'bad': OSError('fixture failed')}, 5, dict(requested=None, attempted=3, returned=2, dropped=0, state='unknown'), 1, 'unknown_frontier'),
        ('malformed XML', {'root': '<urlset>'}, 5, dict(requested=None, returned=0, state='unknown'), 1, 'input_failed'),
    ]
    for entry in scenarios: scenario(*entry)
    for cap in ('0', '-1'):
        with patch.object(sm, 'fetch', side_effect=AssertionError('must not fetch')):
            try: capture(sm.main, ['--url', base+'root', '--max-maps', cap])
            except SystemExit as exc: ok(exc.code == 2, 'nonpositive cap refused as usage')
            else: ok(False, 'nonpositive cap refused as usage')
    fixture = Path(workspace) / 'sitemap.xml'
    for body, expected, code in [(page, ('complete', 1, 1), 0), (empty, ('complete', 1, 1), 1), (index(base+'nested'), ('unknown', None, 1), 1), ('broken', ('unknown', None, 0), 1)]:
        fixture.write_text(body)
        actual, raw, _ = capture(sm.main, ['--file', str(fixture), '--format', 'json'])
        try: data = json.loads(raw); cov = data.get('coverage')
        except ValueError: cov = None
        ok(cov and not schema_errors(cov) and cov['unit'] == 'local_file' and (cov['state'], cov['requested'], cov['returned']) == expected and actual == code, 'offline document/empty/index/error semantics')
    with patch.object(sm, 'MAX_URLS_PER_MAP', 1):
        data = scenario('page URL cap', {'root': page.replace('</urlset>', '<url><loc>https://example.invalid/b</loc></url></urlset>')}, 5, dict(requested=1, returned=1, state='partial'), 0, 'page_url_cap')
        ok(data and data['analysis']['urls_truncated'] == 1, 'page entries separate from returned documents')

    # Transport fixture is a real loopback HTTP response; no external provider.
    import http.server, socketserver, threading
    class Handler(http.server.BaseHTTPRequestHandler):
        def log_message(self, *args): pass
        def do_GET(self):
            body = page.encode(); zipped = self.path.startswith('/gzip')
            if self.path == '/gzip-empty': body = b''
            if self.path == '/raw-limit': body += b' ' * 300
            if self.path == '/gzip-limit': body += b' ' * 300
            if zipped: body = gzip.compress(body)
            if self.path == '/gzip-cut': body = body[:-8]
            if self.path == '/gzip-corrupt': body = b'not gzip'
            self.send_response(200)
            if zipped: self.send_header('Content-Encoding', 'gzip')
            self.send_header('Content-Length', str(len(body) + (15 if self.path == '/short' else 0)))
            self.end_headers(); self.wfile.write(body)
    with socketserver.TCPServer(('127.0.0.1', 0), Handler) as server:
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        try:
            origin = f'http://127.0.0.1:{server.server_address[1]}'
            for route, returned, state, code, reason in [('/ok',1,'complete',0,None),('/gzip',1,'complete',0,None),('/gzip-empty',0,'unknown',1,'input_failed'),('/short',0,'unknown',1,'incomplete_body'),('/gzip-cut',0,'unknown',1,'incomplete_body'),('/gzip-corrupt',0,'unknown',1,'incomplete_body'),('/raw-limit',0,'unknown',1,'incomplete_body'),('/gzip-limit',0,'unknown',1,'incomplete_body')]:
                try:
                    with patch.object(sm, 'MAX_BYTES_PER_MAP', 200):
                        actual, raw, _ = capture(sm.main, ['--url', origin+route, '--format', 'json'])
                except (EOFError, OSError, ValueError) as exc:
                    ok(False, route + ': exception instead of report: ' + type(exc).__name__); continue
                try: cov = json.loads(raw).get('coverage')
                except ValueError: cov = None
                ok(cov and not schema_errors(cov) and (cov['returned'],cov['state'],actual) == (returned,state,code), route + ': bounded transport completeness')
                if reason: ok(cov and reason in {r['code'] for r in cov['reasons']}, route + ': failure reason')
        finally: server.shutdown(); thread.join()
    # The transport layer can prove empty bytes; XML usability is a separate test.
    ok(sm.decode_body(gzip.compress(b''), True) == '', 'complete empty gzip is not transport failure')
    for zipped in (False, True):
        for size, admitted in ((200, True), (201, False)):
            body = b'x' * size
            if zipped: body = gzip.compress(body)
            with patch.object(sm, 'MAX_BYTES_PER_MAP', 200):
                try: decoded = sm.decode_body(body, zipped)
                except sm.IncompleteBody: decoded = None
            ok((decoded is not None) == admitted, 'raw/decompressed exact boundary and sentinel')
    invalid_deflate = gzip.compress(page.encode())[:10] + b'\xff' * 10
    try: sm.decode_body(invalid_deflate, True)
    except sm.IncompleteBody: ok(True, 'invalid deflate is named incomplete body')
    else: ok(False, 'invalid deflate is named incomplete body')
    fixture.write_text('x' * 201)
    with patch.object(sm, 'MAX_BYTES_PER_MAP', 200):
        code, raw, _ = capture(sm.main, ['--file', str(fixture), '--format', 'json'])
    record = json.loads(raw)['coverage']
    ok(code == 1 and record['returned'] == 0 and any(r['code'] == 'incomplete_body' for r in record['reasons']), 'offline input byte budget measured')

    # Actual copied-source mutations: evidence predicates must reject the lie.
    source = path.read_text()
    mutants = [
        ('duplicate accounting', 'if nested not in discovered:', 'if True:',
         {'root': index(base+'child', base+'child'), 'child': page}, 2,
         lambda d: d['coverage']['requested'] == 2 and d['coverage']['dropped'] == 0 and d['coverage']['state'] == 'complete'),
        ('missing cap reason', '"code": "document_cap"', '"code": "unexplained_cap"',
         {'root': index(base+'child')}, 1,
         lambda d: any(r['code'] == 'document_cap' for r in d['coverage']['reasons'])),
        ('false complete state', '"state": state, "reasons": reasons', '"state": "complete", "reasons": reasons',
         {'root': index(base+'child')}, 1,
         lambda d: not schema_errors(d['coverage'])),
    ]
    for name, old, new, bodies, cap, accepts in mutants:
        ok(source.count(old) == 1, name + ': exact source mutation selector')
        changed = source.replace(old, new, 1)
        mutant = Path(workspace) / ('mutant_' + name.replace(' ', '_') + '.py'); mutant.write_text(changed)
        spec = importlib.util.spec_from_file_location('sitemap_mutant', mutant)
        mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
        with patch.object(mod, 'fetch', side_effect=lambda url: bodies[url[len(base):]]):
            _, raw, _ = capture(mod.main, ['--url', base+'root', '--max-maps', str(cap), '--format', 'json'])
        ok(not accepts(json.loads(raw)), name + ': intended real-source mutation rejected')
    fixture.write_text(page)
    copied = Path(workspace) / 'sitemap_audit.py'; copied.write_bytes(path.read_bytes())
    result = subprocess.run([sys.executable, str(copied), '--file', str(fixture), '--format', 'json'], cwd=workspace, capture_output=True, text=True)
    ok(result.returncode == 0 and json.loads(result.stdout).get('coverage', {}).get('state') == 'complete', 'standalone copied collector executes without siblings')
    for body, expected in [(empty, 'complete'), ('broken', 'unknown')]:
        fixture.write_text(body)
        result = subprocess.run([sys.executable, str(copied), '--file', str(fixture), '--format', 'json'], cwd=workspace, capture_output=True, text=True)
        ok(result.returncode == 1 and json.loads(result.stdout)['coverage']['state'] == expected, 'ordinary copied CLI empty/invalid input preserves report and exit')
    texts = [(path.parent / (n+'.py')).read_text() for n in ('page_audit', 'url_inspection', 'sitemap_audit')]
    blocks = [t.split('# ── collector coverage shared block',1)[-1].split('# ── end collector coverage shared block',1)[0] for t in texts]
    ok(len(set(blocks)) == 1 and 'def collector_coverage(' in blocks[0], 'three standalone copies byte-identical')
    print(f'B-9 sitemap coverage: {count} controls')


if __name__ == '__main__':
    import residue
    failures = []
    workspace = residue.workspace('sitemap-coverage')
    run(lambda cond, label: failures.append(label) if not cond else None, Path(__file__).resolve().parents[1], workspace)
    if not failures: residue.close_case('sitemap-coverage')
    residue.report()
    if failures:
        print('FAIL: sitemap coverage')
        for label in failures: print('  -', label)
        sys.exit(1)
    print('PASS: sitemap coverage')
