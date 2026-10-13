#!/usr/bin/env python3
"""Offline loopback provenance controls; no provider calls or filesystem fixtures."""
import http.server
import importlib.util
from pathlib import Path
import socketserver
import sys
import threading
from unittest.mock import patch

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'plugins/seo-aeo-audit/skills/seo-aeo-audit/scripts/agent_surface.py'
spec = importlib.util.spec_from_file_location('surface', SOURCE)
ag = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ag)
failures = []
checks = 0


def check(value, name):
    global checks
    checks += 1
    if not value:
        failures.append(name)


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        routes = {'/start': (301, '/temporary'), '/temporary': (307, '/landing'),
                  '/missing-start': (302, '/missing'), '/failed-start': (308, '/drop')}
        if self.path in routes:
            status, target = routes[self.path]
            self.send_response(status)
            self.send_header('Location', target)
            self.end_headers()
        elif self.path == '/drop':
            self.close_connection = True
        else:
            self.send_response(404 if self.path == '/missing' else 200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<html><title>Fixture</title><body></body></html>')


with socketserver.TCPServer(('127.0.0.1', 0), Handler) as server:
    origin = f'http://127.0.0.1:{server.server_address[1]}'
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        moved = ag.fetch(origin + '/start')
        hops = getattr(moved, 'redirects', [])
        check(moved.status == 200 and moved.final_url == origin + '/landing', 'landing status and URL')
        check([h.get('status') for h in hops] == [301, 307], 'observed redirect statuses survive separately')
        check(hops and hops[0].get('url') == origin + '/start' and hops[-1].get('to_url') == origin + '/landing', 'redirect chain endpoints')
        missing = ag.fetch(origin + '/missing-start')
        check(missing.status == 404 and missing.final_url == origin + '/missing', 'HTTP error retains landing URL')
        check([h.get('status') for h in getattr(missing, 'redirects', [])] == [302], 'HTTP error retains redirect history')
        straight = ag.fetch(origin + '/landing')
        check(straight.status == 200 and getattr(straight, 'redirects', None) == [], 'direct response does not invent a redirect')
        try:
            failed = ag.fetch(origin + '/failed-start')
            check(failed.status is None and failed.final_url is None, 'transport failure has no fabricated landing')
            check([h.get('status') for h in getattr(failed, 'redirects', [])] == [308], 'observed hop survives later transport failure')
        except Exception as exc:
            check(False, 'transport failure must be a probe: ' + type(exc).__name__)
        with patch.object(ag, 'fetch', return_value=moved):
            report = ag.collect('', api_origin=origin)
            row = report['checks'][0]
            check(row.get('final_url') == moved.final_url, 'collection carries landing URL')
            check(row.get('redirects') == hops and bool(hops), 'collection carries redirect status evidence')
            rendered = ag.render(report)
            check('/landing' in rendered and '301' in rendered and '307' in rendered, 'human report carries hop and landing evidence')
            api = ag.collect_api_behaviour(origin + '/start')
            check(api.get('final_url') == moved.final_url and api.get('redirects') == hops, 'API probe has same provenance')
            api_rendered = ag.render({'api_behaviour': api})
            check('/landing' in api_rendered and '301' in api_rendered and '307' in api_rendered, 'API human output carries provenance')
        rendered = ag.render({'entry_points': [{'role': 'about', 'path': None,
            'redirects_to_root': ['/about'], 'linked_from_root': None,
            'answers_200': False, 'chars': None}]})
        check('301' not in rendered, 'root bounce without known code must not invent 301')
    finally:
        server.shutdown()
        thread.join()

for failure in failures:
    print('FAIL:', failure)
print(f'FW06 provenance: {checks - len(failures)}/{checks} controls passed')
sys.exit(bool(failures))
