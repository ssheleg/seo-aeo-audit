"""Offline baseline probes; no credential bootstrap or provider calls."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / 'plugins/seo-aeo-audit/skills/seo-aeo-audit/scripts'


def load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / (name + '.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def gsc_probe(fail_at=None):
    mod = load('gsc_pull')
    calls = []
    def fake(path, token, quota_project, body=None):
        calls.append({'path': path, 'dimensions': body.get('dimensions') if body else None})
        if len(calls) == fail_at:
            raise SystemExit('offline provider failure')
        if path == '/sites':
            return {'siteEntry': [{'siteUrl': 'sc-domain:example.invalid'}]}
        if path.endswith('/sitemaps'):
            return {'sitemap': []}
        dims = body['dimensions']
        keys = [{'date':'2026-01-01','query':'fixture','page':'https://example.invalid/'}[d] for d in dims]
        return {'rows':[{'keys':keys,'clicks':1,'impressions':10,'ctr':.1,'position':2}]}
    out, err = io.StringIO(), io.StringIO()
    with patch.object(mod,'access_token',return_value='offline-sentinel'), patch.object(mod,'call',side_effect=fake), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try: code=mod.main(['--site','sc-domain:example.invalid','--format','json'])
        except SystemExit as exc: code=str(exc)
    text=out.getvalue()
    payload=json.loads(text) if text else {}
    return {'case':'gsc','fail_at':fail_at,'calls':len(calls),'stdout_bytes':len(text.encode()),'exit':code,'coverage_present':bool(payload.get('coverage') or payload.get('coverage_by_unit'))}


def psi_probe():
    mod=load('psi_pull');out,err=io.StringIO(),io.StringIO()
    with patch.object(mod,'fetch',return_value={}), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code=mod.main(['--url','https://example.invalid/','--format','json'])
    payload=json.loads(out.getvalue())
    return {'case':'psi-empty-object','exit':code,'payload':payload}


if __name__ == '__main__':
    print(json.dumps([gsc_probe(),gsc_probe(3),psi_probe()],indent=2))
