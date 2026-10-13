"""Shared collector coverage acceptance checks, invoked by test_output_contracts.

Only local fixture input and mocked URL Inspection responses are used. Provider
credentials are never read. Each collector remains a standalone script.
"""
import contextlib
import io
import json
from pathlib import Path
from unittest.mock import patch


def capture(fn, argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = fn(argv)
    return code, out.getvalue(), err.getvalue()


def basic_emission_checks(pa, ui, check, root):
    args = ['--file', str(Path(root) / 'test/fixtures/good-page.html'), '--format', 'json']
    code, out, _ = capture(pa.main, args)
    record = json.loads(out)[0].get('coverage')
    check(code == 0 and isinstance(record, dict), 'B-9 page audit emits common invocation coverage')
    with patch.object(ui, 'access_token', return_value='fixture-not-a-key'), \
         patch.object(ui, 'inspect', return_value={'inspectionResult': {'indexStatusResult': {'verdict': 'PASS'}}}), \
         patch.object(ui.time, 'sleep'):
        code, out, _ = capture(ui.main, ['--site', 'sc-domain:example.invalid', '--urls', 'https://example.invalid/a', '--format', 'json'])
    check(code == 0 and isinstance(json.loads(out).get('coverage'), dict), 'B-9 URL Inspection emits common invocation coverage')


def schema_errors(record):
    """Independent acceptance reader; does not call the producer under test."""
    if not isinstance(record, dict):
        return ['record absent']
    keys = {'schema', 'unit', 'scope', 'requested', 'attempted', 'returned', 'dropped', 'state', 'reasons'}
    errors = []
    if set(record) != keys or record.get('schema') != 'collector-coverage/1':
        errors.append('schema fields')
    if not all(isinstance(record.get(k), str) and record[k].strip() for k in ('unit', 'scope')):
        errors.append('scope/unit')
    counts = [record.get(k) for k in ('requested', 'attempted', 'returned', 'dropped')]
    if not all(x is None or (type(x) is int and x >= 0) for x in counts):
        return errors + ['count type']
    requested, attempted, returned, dropped = counts
    reasons = record.get('reasons')
    if not isinstance(reasons, list) or any(not isinstance(r, dict) or not all(isinstance(r.get(k), str) and r[k].strip() for k in ('code', 'detail')) for r in reasons):
        return errors + ['reasons']
    if None not in (requested, attempted, dropped) and attempted + dropped != requested:
        errors.append('input accounting')
    if requested is not None and any(v is not None and v > requested for v in (attempted, returned, dropped)):
        errors.append('known count exceeds input population')
    if None not in (returned, attempted) and returned > attempted:
        errors.append('returned exceeds attempts')
    unknown = None in counts
    partial = unknown or dropped or returned != attempted or bool(reasons)
    expected = 'unknown' if unknown else 'partial' if partial else 'complete'
    if record.get('state') != expected:
        errors.append('state overclaim')
    if partial and not reasons:
        errors.append('missing gap reason')
    return errors



def run(pa, ui, check, root, workspace):
    import gzip
    import http.server
    import socketserver
    import subprocess
    import sys
    import threading

    basic_emission_checks(pa, ui, check, root)
    paths = [Path(root) / 'plugins/seo-aeo-audit/skills/seo-aeo-audit/scripts' / (n + '.py') for n in ('page_audit', 'url_inspection')]
    blocks = [p.read_text().split('# ── collector coverage shared block', 1)[-1].split('# ── end collector coverage shared block', 1)[0] for p in paths]
    check(blocks[0] == blocks[1] and 'def collector_coverage(' in blocks[0], 'B-9 standalone coverage copies stay byte-identical')

    for mod in (pa, ui):
        builder = getattr(mod, 'collector_coverage', None)
        if not callable(builder):
            check(False, 'B-9 common coverage builder exists')
            return
        empty = builder('input_url', 'enumerated empty test input', 0, 0, 0, 0, [])
        check(not schema_errors(empty) and empty['state'] == 'complete', 'B-9 counted empty input is known zero')
        unknown = builder('input_url', 'input population unavailable', None, 0, 0, None,
                          [{'code': 'unknown_input', 'detail': 'The input population was not enumerable.'}])
        check(not schema_errors(unknown) and unknown['state'] == 'unknown' and unknown['requested'] is None,
              'B-9 unavailable population stays null with reason')
        check('requested=unknown' in mod.collector_coverage_md(unknown), 'B-9 text preserves unknown counts')
        for counts in [(True, 1, 1, 0), (1.0, 1, 1, 0), (-1, 0, 0, 0), (2, 1, 1, 0), (1, 1, 2, 0), (None, 0, 0, None)]:
            try:
                builder('input_url', 'test', *counts, [])
            except ValueError:
                check(True, f'B-9 builder refuses invalid/unsupported counts {counts!r}')
            else:
                check(False, f'B-9 builder refuses invalid/unsupported counts {counts!r}')
        for counts in [(1, 2, 1, None), (1, None, 2, None), (1, None, None, 2)]:
            reasons = [{'code': 'unknown_quantity', 'detail': 'One other quantity is not known.'}]
            try:
                builder('input_url', 'test', *counts, reasons)
            except ValueError:
                check(True, 'B-9 known quantity cannot exceed requested despite other unknown counts')
            else:
                check(False, 'B-9 known quantity cannot exceed requested despite other unknown counts')
            malformed = dict(unknown, requested=counts[0], attempted=counts[1], returned=counts[2], dropped=counts[3])
            check(bool(schema_errors(malformed)), 'B-9 independent reader refuses known count exceeding requested with null peers')
        for bad in [dict(empty, state='partial'), dict(empty, unit=''), dict(empty, requested=True), dict(unknown, state='complete'), dict(unknown, reasons=[])]:
            check(bool(schema_errors(bad)), 'B-9 independent reader refuses a malformed/overclaimed record')

    def page(args, expected, label):
        code, raw, _ = capture(pa.main, args + ['--format', 'json'])
        rows = json.loads(raw)
        records = [r.get('coverage') for r in rows]
        record = records[0] if records else None
        check(all(r == record for r in records), label + ': repeated invocation record agrees')
        check(not schema_errors(record), label + ': coverage schema')
        check(record and all(record.get(k) == v for k, v in expected.items()), label + ': bounded counts/state')
        text_code, text, _ = capture(pa.main, args)
        check(code == text_code, label + ': text/JSON exit parity')
        if record:
            check(f"State: **{record['state']}**" in text and all(f'{k}={record[k]}' in text for k in ('requested', 'attempted', 'returned', 'dropped')), label + ': text/JSON coverage agreement')
        return code, record

    class Handler(http.server.BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass
        def do_GET(self):
            if self.path == '/redirect':
                self.send_response(307); self.send_header('Location', '/ok'); self.end_headers(); return
            if self.path == '/drop':
                self.close_connection = True; return
            body = b'<html><title>Fixture</title><body>' + b'word ' * 200 + b'</body></html>'
            if self.path == '/empty': body = b''
            zipped = self.path.startswith('/gzip')
            if zipped:
                body = gzip.compress(body)
                if self.path == '/gzip-cut': body = body[:-8]
                if self.path == '/gzip-corrupt': body = b'broken-gzip'
            self.send_response(404 if self.path == '/missing' else 200)
            self.send_header('Content-Type', 'text/html')
            if zipped: self.send_header('Content-Encoding', 'gzip')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers(); self.wfile.write(body)

    with socketserver.TCPServer(('127.0.0.1', 0), Handler) as server:
        origin = f'http://127.0.0.1:{server.server_address[1]}'
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        try:
            for path, returned, state in [('/ok', 1, 'complete'), ('/empty', 1, 'complete'), ('/redirect', 1, 'complete'), ('/missing', 0, 'partial'), ('/drop', 0, 'partial'), ('/gzip', 1, 'complete'), ('/gzip-cut', 0, 'partial'), ('/gzip-corrupt', 0, 'partial')]:
                page(['--url', origin + path], {'requested': 1, 'attempted': 1, 'returned': returned, 'dropped': 0, 'state': state}, 'B-9 ' + path)
            _, record = page(['--url', origin + '/ok', '--max-bytes', '20'], {'returned': 0, 'state': 'partial'}, 'B-9 capped body')
            check(any(r['code'] == 'incomplete_body' for r in record['reasons']), 'B-9 capped body retains explicit incompleteness reason')
            path = Path(workspace) / 'coverage-urls.txt'; path.write_text(origin + '/ok\n' + origin + '/drop\n' + origin + '/ok\n')
            page(['--url-list', str(path)], {'requested': 3, 'attempted': 3, 'returned': 2, 'dropped': 0, 'state': 'partial'}, 'B-9 duplicate input entries and failure')
        finally:
            server.shutdown(); thread.join()

    _, record = page(['--file', str(Path(root) / 'test/fixtures/good-page.html')], {'unit': 'local_file', 'requested': 1, 'returned': 1, 'state': 'complete'}, 'B-9 local HTML')
    good = {'inspectionResult': {'indexStatusResult': {'verdict': 'PASS'}}}
    for payloads, cap, expected in [([good], 1, (1, 1, 0, 'complete')), ([good], 1, (2, 1, 1, 'partial')), ([{'_error': 'fixture refusal'}, {}], 2, (2, 0, 0, 'partial')), ([good, {}], 2, (2, 1, 0, 'partial'))]:
        requested, returned, dropped, state = expected
        urls = ['https://example.invalid/' + str(i) for i in range(requested)]
        args = ['--site', 'sc-domain:example.invalid', '--urls', *urls, urls[0], '--max-urls', str(cap)]
        with patch.object(ui, 'access_token', return_value='fixture-not-a-key'), patch.object(ui.time, 'sleep'), patch.object(ui, 'inspect', side_effect=payloads):
            code, out, _ = capture(ui.main, args + ['--format', 'json'])
        data = json.loads(out); record = data.get('coverage')
        check(not schema_errors(record), 'B-9 inspection schema')
        check(record and [record[k] for k in ('requested', 'attempted', 'returned', 'dropped', 'state')] == [requested, min(requested, cap), returned, dropped, state], 'B-9 inspection dedup/cap/no-answer counts')
        with patch.object(ui, 'access_token', return_value='fixture-not-a-key'), patch.object(ui.time, 'sleep'), patch.object(ui, 'inspect', side_effect=payloads):
            text_code, text, _ = capture(ui.main, args)
        check(code == text_code and f'State: **{state}**' in text and f'returned={returned}' in text, 'B-9 inspection text/JSON agreement')
    for cap in ('0', '-1'):
        with patch.object(ui, 'access_token', side_effect=AssertionError('must not mint credentials')):
            try:
                capture(ui.main, ['--site', 'sc-domain:example.invalid', '--urls', 'https://example.invalid/', '--max-urls', cap])
            except SystemExit as exc:
                check(exc.code == 2, 'B-9 invalid cap refused before credential access')
            else:
                check(False, 'B-9 invalid cap did not fail')
    # Copied scripts must still start alone, from a caller-owned unrelated cwd.
    for path in paths:
        copied = Path(workspace) / path.name; copied.write_bytes(path.read_bytes())
        p = subprocess.run([sys.executable, str(copied), '--help'], cwd=workspace, capture_output=True)
        check(p.returncode == 0, 'B-9 standalone copied collector imports without siblings')


_run_controls = run

def run(pa, ui, check, root, workspace):
    total = 0
    failed = 0
    def measured(condition, label):
        nonlocal total, failed
        total += 1
        failed += not bool(condition)
        check(condition, label)
    _run_controls(pa, ui, measured, root, workspace)
    print(f"B-9 collector coverage: {total - failed}/{total} controls passed")
