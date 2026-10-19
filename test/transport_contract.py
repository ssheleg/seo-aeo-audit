"""Bounded standalone transport admission: only actual loopback responses."""
import gzip
import http.client
import importlib.util
import io
import json
import sys
import threading
import urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

HOMES = ('page_audit', 'agent_surface', 'sitemap_audit', 'psi_pull', 'gsc_pull', 'url_inspection', 'preflight', 'bwt_pull')


def load(root, name):
    path = Path(root) / 'plugins/seo-aeo-audit/skills/seo-aeo-audit/scripts' / (name + '.py')
    spec = importlib.util.spec_from_file_location('transport_' + name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod, path


def run(check, root, workspace):
    count = 0
    def ok(value, label):
        nonlocal count
        count += 1
        check(value, 'T1 transport: ' + label)
    mods = {name: load(root, name)[0] for name in HOMES}
    key = 'offline/key+transport'
    requests = []
    payloads = {
        'page_audit': b'<html><title>fixture</title><p>fixture</p></html>',
        'sitemap_audit': b'<urlset><url><loc>https://example.invalid/a</loc></url></urlset>',
        'agent_surface': b'<html>fixture</html>',
        'psi_pull': b'{"loadingExperience":{"metrics":{"LARGEST_CONTENTFUL_PAINT_MS":{"percentile":0}}}}',
        'gsc_pull': b'{"rows":[]}',
        'url_inspection': b'{"inspectionResult":{"indexStatusResult":{"verdict":"PASS"}}}',
        'preflight': b'{}',
        'bwt_pull': b'{"d":[]}',
    }
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args): pass
        def do_POST(self): self.do_GET()
        def do_GET(self):
            requests.append(self.path)
            name, mode = self.path.split('?')[0].strip('/').split('/')[:2]
            raw = payloads[name]
            if mode in ('raw-cap', 'gzip-cap'): raw += b' ' * 400
            if mode in ('gzip', 'gzip-cap', 'gzip-short'): raw = gzip.compress(raw)
            if mode == 'gzip-short': raw = raw[:-6]
            if mode == 'gzip-corrupt': raw = b'bad gzip'
            if mode == 'gzip-absent': raw = b''
            if mode == 'error': raw = (key + ' offline%2Fkey%2Btransport').encode()
            self.send_response(403 if mode == 'error' else 200)
            self.send_header('Content-Type', 'text/html' if name == 'page_audit' else 'application/json')
            if mode in ('gzip', 'gzip-cap', 'gzip-short', 'gzip-corrupt', 'gzip-absent'): self.send_header('Content-Encoding', 'gzip')
            if mode == 'encoding': self.send_header('Content-Encoding', 'br')
            if mode == 'content-repeat':
                self.send_header('Content-Encoding', 'identity'); self.send_header('Content-Encoding', 'br')
            if mode in ('chunked', 'te-cl'): self.send_header('Transfer-Encoding', 'chunked')
            if mode == 'te-unknown': self.send_header('Transfer-Encoding', 'unsupported')
            if mode not in ('chunked', 'te-unknown'):
                self.send_header('Content-Length', '²' if mode == 'malformed' else str(len(raw)))
            if mode == 'conflict': self.send_header('Content-Length', str(len(raw) + 900))
            if mode == 'equal': self.send_header('Content-Length', '00' + str(len(raw)))
            self.end_headers()
            if mode in ('chunked', 'te-cl'): raw = f'{len(raw):x}\r\n'.encode() + raw + b'\r\n0\r\n\r\n'
            self.wfile.write(raw)
    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
    origin = f'http://127.0.0.1:{server.server_port}'
    def invoke(name, mode, budget=4096):
        mod = mods[name]; url = origin + '/' + name + '/' + mode
        try:
            if name == 'page_audit':
                body, _, cut = mod.fetch(url, 3, 'offline', budget)
                return not cut, body
            if name == 'agent_surface':
                with patch.object(mod, 'MAX_BYTES', budget): result = mod.fetch(url)
                return result.body_complete, result
            if name == 'sitemap_audit':
                with patch.object(mod, 'MAX_BYTES_PER_MAP', budget): result = mod.fetch(url)
                return True, result
            if name == 'preflight':
                result = mod._get(url, max_bytes=budget, secret=key)
                return result.complete, result
            if name == 'bwt_pull':
                with patch.object(mod, 'MAX_RESPONSE_BYTES', budget), \
                        patch.object(mod, 'API_KEY_BASE', origin + '/bwt_pull'):
                    result = mod.call(mode, {'siteUrl': 'https://example.invalid/'}, ('key', key))
                return 'rows' in result, result
            with patch.object(mod, 'MAX_RESPONSE_BYTES', budget, create=True):
                if name == 'psi_pull':
                    with patch.object(mod, 'API', url): result = mod.fetch('https://example.invalid', 'mobile', key)
                elif name == 'gsc_pull':
                    with patch.object(mod, 'API', origin): result = mod.call('/' + name + '/' + mode, key, None)
                else:
                    with patch.object(mod, 'API', url): result = mod.inspect('sc-domain:example.invalid', 'https://example.invalid', key, None)
            return isinstance(result, dict) and '_error' not in result, result
        except (SystemExit, ValueError, OSError) as exc:
            return False, str(exc)
    try:
        for name in HOMES:
            for mode in ('good', 'equal', 'gzip', 'chunked'):
                valid, result = invoke(name, mode)
                ok(valid, name + ' admits complete ' + mode)
            for mode in ('conflict', 'malformed', 'te-cl', 'te-unknown', 'encoding', 'content-repeat', 'gzip-short', 'gzip-corrupt', 'gzip-absent', 'raw-cap', 'gzip-cap'):
                valid, result = invoke(name, mode, 128 if mode.endswith('cap') else 4096)
                ok(not valid, name + ' refuses complete-body claim for ' + mode)
                if name in ('agent_surface', 'preflight'):
                    status = result.status if name == 'agent_surface' else result[0]
                    ok(status == 200, name + ' preserves observed status for ' + mode)
            if name in ('psi_pull', 'gsc_pull', 'url_inspection', 'bwt_pull'):
                valid, result = invoke(name, 'error')
                text = str(result)
                ok(not valid and key not in text and 'offline%2Fkey%2Btransport' not in text and '403' in text, name + ' redacts bounded error-body echoes while preserving status')
        # Actual HTTPError handlers must contain read failure, not erase a report.
        for name in ('psi_pull', 'gsc_pull', 'url_inspection'):
            mod = mods[name]
            class Broken(io.BytesIO):
                def read(self, *args): raise http.client.IncompleteRead(b'partial ' + key.encode(), 100)
            error = urllib.error.HTTPError(origin, 403, 'fixture', {}, Broken())
            try:
                with patch.object(mod.urllib.request, 'urlopen', side_effect=error):
                    if name == 'psi_pull': result = mod.fetch('https://example.invalid', 'mobile', key)
                    elif name == 'gsc_pull': result = mod.call('/fixture', key, None)
                    else: result = mod.inspect('sc-domain:example.invalid', 'https://example.invalid', key, None)
            except SystemExit as exc: result = str(exc)
            except Exception as exc: result = {'escaped': type(exc).__name__}
            ok('escaped' not in str(result) and '403' in str(result) and key not in str(result), name + ' HTTPError IncompleteRead contained and redacted')
    finally:
        server.shutdown(); server.server_close(); thread.join(timeout=2)
    blocks = []
    for name in HOMES:
        source = load(root, name)[1].read_text()
        marker = '# BEGIN BOUNDED TRANSPORT'
        if marker in source: blocks.append(source.split(marker, 1)[1].split('# END BOUNDED TRANSPORT', 1)[0])
    ok(len(blocks) == 8 and len(set(blocks)) == 1, 'all eight standalone bounded transport blocks agree')
    from email.message import Message
    class Response(io.BytesIO):
        def __init__(self, body, fields=()):
            super().__init__(body); self.status = self.code = 200
            self.headers = Message()
            for key, value in fields: self.headers.add_header(key, value)
    subject = mods['preflight']
    for fields, expected in [
        ([('Content-Length', '2, 0002')], True),
        ([('Content-Length', '2, 3')], False),
        ([('Content-Length', '')], False),
        ([('Content-Length', '9' * 5000)], False),
        ([('Content-Length', '2'), ('Transfer-Encoding', 'identity')], False),
        ([('Content-Length', '0')], True),
    ]:
        body = b'' if fields == [('Content-Length', '0')] else b'{}'
        _, complete, _ = subject._bounded_response(Response(body, fields), 64)
        ok(complete is expected, 'ASCII/comma/zero/unbounded-header admission')
    for name in HOMES:
        original = load(root, name)[1]
        copied = Path(workspace) / (name + '-standalone.py'); copied.write_bytes(original.read_bytes())
        spec = importlib.util.spec_from_file_location('copied_transport_' + name, copied)
        isolated = importlib.util.module_from_spec(spec); sys.modules[spec.name] = isolated; spec.loader.exec_module(isolated)
        raw, complete, _ = isolated._bounded_response(Response(b'{}', [('Content-Length', '2'), ('Content-Length', '900')]), 64)
        ok(raw == b'{}' and not complete, name + ' standalone copy executes transport without sibling module')
    for name in HOMES:
        raw, complete, _ = mods[name]._bounded_gzip(b'', 128)
        ok(not complete, name + ' requires an actual gzip member')
        raw, complete, _ = mods[name]._bounded_gzip(gzip.compress(b''), 128)
        ok(raw == b'' and complete, name + ' valid compressed empty payload stays complete')
    sitemap = mods['sitemap_audit']
    try: sitemap.decode_body(b'', True)
    except sitemap.IncompleteBody: ok(True, 'local absent gzip member is incomplete transport')
    else: ok(False, 'local absent gzip member is incomplete transport')
    ok(sitemap.decode_body(gzip.compress(b''), True) == '', 'local compressed empty stream has complete transport, separately invalid XML')
    from collector_coverage_contract import capture
    empty_map = Path(workspace) / 'empty.xml.gz'; empty_map.write_bytes(b'')
    code, output, _ = capture(sitemap.main, ['--file', str(empty_map), '--format', 'json'])
    report = json.loads(output)
    ok(code == 1 and report['coverage']['attempted'] == 1 and report['coverage']['returned'] == 0 and 'valid member' in output, 'actual local empty .gz report records failure without losing carrier')

    original_gzip = gzip.GzipFile
    class BudgetedGzip(original_gzip):
        def read(self, size=-1):
            if size < 0 or size > 65: raise AssertionError('unbounded inflation read')
            return super().read(size)
    with patch.object(gzip, 'GzipFile', BudgetedGzip):
        raw, complete, _ = subject._bounded_gzip(gzip.compress(b'x' * 400), 64)
    ok(len(raw) == 64 and not complete, 'inflation requests bounded bytes before materializing output')
    source = load(root, 'preflight')[1].read_text()
    def mutant(name, old, new):
        ok(source.count(old) == 1, name + ' mutation selector is unique')
        path = Path(workspace) / (name + '.py'); path.write_text(source.replace(old, new, 1))
        spec = importlib.util.spec_from_file_location(name, path); result = importlib.util.module_from_spec(spec); spec.loader.exec_module(result); return result
    wrong = mutant('false_complete', 'return raw, not errors,', 'return raw, True,')
    result = wrong._read_probe(Response(b'{}', [('Content-Length', '2'), ('Content-Length', '900')]), 64)
    ok(result.complete, 'independent conflicting-length predicate detects false-complete mutant')
    wrong = mutant('uncapped_inflate', 'stream.read(max_bytes + 1)', 'stream.read()')
    caught = False
    try:
        with patch.object(gzip, 'GzipFile', BudgetedGzip): wrong._bounded_gzip(gzip.compress(b'x' * 400), 64)
    except AssertionError: caught = True
    ok(caught, 'inflation call-budget control detects uncapped-read mutant')
    try:
        with patch.object(subject.json, 'loads', side_effect=RecursionError('fixture decoder capacity')):
            subject._transport_json(Response(b'{}'), 4096)
    except ValueError: ok(True, 'decoder nesting failure becomes a reportable payload failure')
    else: ok(False, 'decoder nesting failure becomes a reportable payload failure')
    print(f'T1 bounded transport: {count} controls')


if __name__ == '__main__':
    import residue
    failures = []; residue.open_case('transport-contract'); workspace = residue.workspace('transport-contract')
    run(lambda cond, label: failures.append(label) if not cond else None, Path(__file__).resolve().parents[1], workspace)
    if not failures: residue.close_case('transport-contract')
    residue.report()
    if failures:
        print('FAIL: bounded transport\n' + '\n'.join('  - ' + item for item in failures)); raise SystemExit(1)
    print('PASS: bounded transport')
