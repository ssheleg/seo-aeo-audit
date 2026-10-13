"""Bounded network/local coverage acceptance; no provider or credentials."""
import importlib.util
import json
from pathlib import Path
from unittest.mock import patch
from collector_coverage_contract import capture, schema_errors, coverage_records


def load(root):
    path = Path(root) / 'plugins/seo-aeo-audit/skills/seo-aeo-audit/scripts/agent_surface.py'
    spec = importlib.util.spec_from_file_location('agent_coverage_subject', path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod, path


def run(check, root, workspace):
    mod, path = load(root)
    count = 0
    def ok(cond, label):
        nonlocal count
        count += 1
        check(cond, 'B-9 agent surface: ' + label)
    calls = []
    def fake(url, accept='', user_agent=mod.UA):
        calls.append((url, accept, user_agent))
        if url == 'https://example.invalid/':
            return mod.Probe(url, 200, 'text/html', '<html><body>root</body></html>')
        return mod.Probe(url, 404, 'text/plain', 'not found')
    with patch.object(mod, 'fetch', side_effect=fake):
        data = mod.collect('https://example.invalid')
    cov = data.get('coverage_by_unit', {}).get('network_probe')
    ok(len(calls) == 47 and len(data['checks']) == 23, 'frozen hidden-alternative denominator counterexample')
    ok(cov and not schema_errors(cov) and (cov['requested'], cov['attempted'], cov['returned'], cov['state']) == (47,47,47,'complete'), 'all executed probes rather than selected note rows')
    journal = data.get('network_probes', [])
    ok(len(journal) == len(calls), 'one journal entry per logical invocation')
    ok([(r.get('url'),r.get('accept'),r.get('user_agent')) for r in journal] == calls, 'header variants and actual invocation order preserved')
    ok('coverage' not in data, 'legacy singular carrier not silently retyped')
    # All fetch failures block the homepage-dependent discovery branch.
    with patch.object(mod, 'fetch', side_effect=lambda url, **kw: mod.Probe(url,None,error='fixture refused')):
        data = mod.collect('https://example.invalid')
    cov = data.get('coverage_by_unit', {}).get('network_probe')
    ok(cov and not schema_errors(cov) and cov['requested'] is None and cov['returned'] == 0 and cov['state'] == 'unknown', 'failed discovery prerequisite preserves unknown input population')
    with patch.object(mod, 'fetch', side_effect=lambda url, **kw: mod.Probe(url,None,error='fixture refused')):
        data = mod.collect('', 'https://api.invalid')
    cov = data.get('coverage_by_unit', {}).get('network_probe')
    ok(cov and not schema_errors(cov) and (cov['requested'],cov['attempted'],cov['returned'],cov['state']) == (1,1,0,'partial'), 'fixed failed input is known partial, not an invented unknown universe')
    def missing_prerequisite(url, **kwargs):
        if url.endswith('/agent-surface-probe-404-check'):
            return mod.Probe(url,None,error='fixture missing-path response failed')
        return fake(url, **kwargs)
    with patch.object(mod,'fetch',side_effect=missing_prerequisite):
        data=mod.collect('https://example.invalid')
    cov=data['coverage_by_unit']['network_probe']
    ok(cov['requested'] is None and cov['attempted']==46 and cov['state']=='unknown' and any(r['code']=='unknown_discovery' for r in cov['reasons']), 'missing-path prerequisite failure retains unknown conditional negotiation frontier')
    file = Path(workspace) / 'openapi.json'
    good = {'openapi':'3.0.0','info':{'title':'Fixture','version':'1'},'paths':{}}
    for obj, returned, state, expected_code in [(good,1,'complete',0), ([],0,'partial',1)]:
        file.write_text(json.dumps(obj))
        try: code, raw, _ = capture(mod.main, ['--openapi-file',str(file),'--format','json'])
        except (TypeError, AttributeError, ValueError):
            ok(False, 'offline non-object payload must not erase report'); continue
        data = json.loads(raw); cov = data.get('coverage_by_unit',{}).get('local_file')
        ok(cov and not schema_errors(cov) and (cov['requested'],cov['attempted'],cov['returned'],cov['state']) == (1,1,returned,state) and code == expected_code, 'offline file separate measured unit/exit')
        text_code, text, _ = capture(mod.main, ['--openapi-file',str(file)])
        ok(cov and text_code == code and mod.collector_coverage_md(cov) in text, 'offline JSON/Markdown agreement')
    file.write_text(json.dumps(good)); calls.clear()
    with patch.object(mod,'fetch',side_effect=fake):
        code, raw, _ = capture(mod.main,['--origin','https://example.invalid','--openapi-file',str(file),'--api-probe','https://api.invalid/endpoint','--format','json'])
    data=json.loads(raw); records=data.get('coverage_by_unit',{})
    ok(set(records)=={'network_probe','local_file'} and all(not schema_errors(r) for r in records.values()), 'mixed inputs keep typed records separate')
    ok(records and records['network_probe']['attempted']==len(calls)==48 and records['local_file']['attempted']==1, 'API probe outside collect included without summing local file')
    file.write_text('{broken')
    code, raw, _ = capture(mod.main,['--openapi-file',str(file),'--format','json'])
    cov=json.loads(raw).get('coverage_by_unit',{}).get('local_file')
    ok(cov and cov['returned']==0 and cov['state']=='partial' and code==1, 'malformed local JSON emits measured failed file')
    with patch.object(mod,'fetch',return_value=mod.Probe('https://example.invalid/spec',200,'application/json',json.dumps(good))):
        code,raw,_=capture(mod.main,['--openapi','https://example.invalid/spec','--format','json'])
    cov=json.loads(raw).get('coverage_by_unit',{}).get('network_probe')
    ok(cov and cov['attempted']==1 and cov['returned']==1 and code==0, 'remote OpenAPI outside collect counted')
    # Mixed inputs preserve successful network evidence when offline payloads fail.
    for content in ('{broken', json.dumps({'paths':['not-an-object']})):
        file.write_text(content)
        with patch.object(mod,'fetch',side_effect=fake):
            code,raw,_=capture(mod.main,['--origin','https://example.invalid','--openapi-file',str(file),'--format','json'])
        mixed=json.loads(raw)
        ok(code==0 and mixed['coverage_by_unit']['network_probe']['returned']==47 and mixed['coverage_by_unit']['local_file']['returned']==0 and mixed['payload_errors'], 'mixed bad local input retains observed network responses and explicit file failure')
    code,raw,_=capture(mod.main,['--openapi-file',str(Path(workspace)/'absent.json'),'--format','json'])
    ok(code==1 and json.loads(raw)['coverage_by_unit']['local_file']['returned']==0, 'absent local file is one attempted failed file')
    file.write_text('{broken')
    # Closed carriers preserve old object/array consumers and keep units separate.
    base = mod.collector_coverage('network_probe','fixture',1,1,1,0,[])
    local = mod.collector_coverage('local_file','fixture',1,1,1,0,[])
    for payload, expected in [({'coverage':base},1),([{'coverage':base},{'coverage':base}],1),({'coverage_by_unit':{'network_probe':base,'local_file':local}},2),({'coverage':{'track':'unlooked'},'coverage_by_unit':{'network_probe':base}},1)]:
        ok(len(coverage_records(payload)) == expected, 'reader preserves supported carriers without summing units/copies')
    for payload in [{'coverage':base,'coverage_by_unit':{'network_probe':base}}, {'coverage':dict(base,schema='collector-coverage/2'),'coverage_by_unit':{'network_probe':base}}, {'coverage_by_unit':{}}, {'coverage_by_unit':{'wrong':base}}, {'coverage':{'track':'unlooked'}}, [{'coverage':base},{'coverage':local}], [{'coverage':base,'coverage_by_unit':{'local_file':local}}], [{'coverage':base},{'coverage':base,'coverage_by_unit':{'local_file':local}}], {'coverage_by_unit':{'network_probe':dict(base,state='unknown')}}]:
        try: coverage_records(payload)
        except ValueError: ok(True,'reader refuses ambiguous/malformed/track-only carrier')
        else: ok(False,'reader refuses ambiguous/malformed/track-only carrier')
    journal = mod.ProbeJournal()
    with patch.object(mod,'fetch',return_value=mod.Probe('https://example.invalid/a',200,body='',redirects=[{'url':'a','status':302,'to_url':'b'},{'url':'b','status':307,'to_url':'c'}])):
        journal.request('https://example.invalid/a'); journal.request('https://example.invalid/a')
    ok(journal.record()['attempted']==2 and len(journal.entries)==2 and len(journal.entries[0]['redirects'])==2, 'repeat invocations count twice; physical redirect hops do not')
    # A hidden near-miss response is still an observed response for the exit rule.
    def hidden_only(url, **kwargs):
        return mod.Probe(url,404,'text/plain','missing') if any(url.endswith(x) for x in mod.AGENT_FILE_NEAR_MISSES) else mod.Probe(url,None,error='no response')
    with patch.object(mod,'fetch',side_effect=hidden_only):
        code,raw,err=capture(mod.main,['--origin','https://example.invalid','--format','json'])
    ok(code==0 and 'Nothing answered' not in err and json.loads(raw)['coverage_by_unit']['network_probe']['returned']>0, 'hidden landing responses satisfy documented answered predicate')

    import gzip, http.server, socketserver, threading, subprocess, sys
    class Handler(http.server.BaseHTTPRequestHandler):
        def log_message(self,*args): pass
        def do_GET(self):
            if self.path=='/redirect':
                self.send_response(302); self.send_header('Location','/ok'); self.end_headers(); return
            body=b'body'
            if self.path=='/spec': body=json.dumps(good).encode()
            if self.path in ('/large','/gzip-large'): body=b'x'*201
            if self.path=='/empty': body=b''
            zipped=self.path.startswith('/gzip')
            if zipped: body=gzip.compress(body)
            if self.path=='/gzip-cut': body=body[:-8]
            if self.path=='/gzip-bad': body=b'bad gzip'
            self.send_response(404 if self.path in ('/missing','/length-bad-404') else 200)
            if zipped:self.send_header('Content-Encoding','gzip')
            self.send_header('Content-Type','application/json' if self.path=='/spec' else 'text/plain')
            self.send_header('Content-Length','²' if self.path.startswith('/length-bad') else str(len(body)+(20 if self.path=='/short' else 0)))
            self.end_headers(); self.wfile.write(body)
    with socketserver.TCPServer(('127.0.0.1',0),Handler) as server:
        thread=threading.Thread(target=server.serve_forever,daemon=True); thread.start()
        try:
            origin=f'http://127.0.0.1:{server.server_address[1]}'
            for route,complete,status in [('/ok',True,200),('/empty',True,200),('/missing',True,404),('/redirect',True,200),('/gzip',True,200),('/large',False,200),('/gzip-large',False,200),('/gzip-cut',False,200),('/gzip-bad',False,200),('/short',False,200),('/length-bad-200',False,200),('/length-bad-404',False,404)]:
                try:
                    with patch.object(mod,'MAX_BYTES',200): probe=mod.fetch(origin+route)
                except ValueError:
                    ok(False,route+': malformed header must not erase observed response'); continue
                ok(probe.status==status and probe.body_complete==complete, route+': landing status separate from complete body')
                if not complete: ok(bool(probe.body_error),route+': named body limitation')
                if route.startswith('/length-bad'): ok('Content-Length' in probe.body_error,route+': malformed length diagnosed explicitly')
                if route=='/redirect':ok(len(probe.redirects)==1 and probe.final_url==origin+'/ok','actual redirect chain observed once')
            copied=Path(workspace)/'agent_surface.py';copied.write_bytes(path.read_bytes())
            result=subprocess.run([sys.executable,str(copied),'--openapi',origin+'/spec','--format','json'],cwd=workspace,capture_output=True,text=True)
            ok(result.returncode==0 and json.loads(result.stdout)['coverage_by_unit']['network_probe']['returned']==1,'standalone copied CLI includes external-to-collect OpenAPI request')
            for route, status in [('/length-bad-200',200),('/length-bad-404',404)]:
                result=subprocess.run([sys.executable,str(copied),'--openapi',origin+route,'--format','json'],cwd=workspace,capture_output=True,text=True)
                out=json.loads(result.stdout); record=out['coverage_by_unit']['network_probe']
                ok(result.returncode==0 and out['network_probes'][0]['status']==status and record['attempted']==1 and record['returned']==0 and record['state']=='partial' and any(r['code']=='incomplete_body' for r in record['reasons']),route+': actual copied CLI retains landing observation and partial report')

        finally: server.shutdown();thread.join()
    for url in ('https://[bad','file:///not-used'):
        probe=mod.fetch(url)
        ok(probe.status is None and not probe.body_complete and bool(probe.error),'malformed/refused URL produces failed logical probe')
    for args, expected in [(['--openapi-file',str(file)],1),(['--origin','https://[bad'],1)]:
        for fmt in ('json','markdown'):
            result=subprocess.run([sys.executable,str(copied),*args,'--format',fmt],cwd=workspace,capture_output=True,text=True)
            ok(result.returncode==expected and bool(result.stdout) and 'Traceback' not in result.stderr,'ordinary copied CLI malformed local/URL inputs keep report')
    file.write_text(json.dumps(good))
    result=subprocess.run([sys.executable,str(copied),'--openapi-file',str(file),'--format','json'],cwd=workspace,capture_output=True,text=True)
    ok(result.returncode==0 and json.loads(result.stdout)['coverage_by_unit']['local_file']['returned']==1,'ordinary copied CLI valid offline input')
    # Land executable defects in owned standalone copies and require the intended
    # evidence predicate to reject, not merely any checker exception.
    source=path.read_text()
    for label,old,new in [
        ('hidden request bypass','last = journal.request(origin + alt)','last = fetch(origin + alt)'),
        ('incomplete body counted','returned = sum(e["status"] is not None and e["body_complete"] for e in self.entries)','returned = sum(e["status"] is not None for e in self.entries)'),
        ('CLI request bypass','p = journal.request(args.openapi)','p = fetch(args.openapi)'),
    ]:
        ok(source.count(old)==1,label+': exact mutation selector')
        mutant=Path(workspace)/('mutant_'+label.replace(' ','_')+'.py');mutant.write_text(source.replace(old,new,1))
        spec=importlib.util.spec_from_file_location('agent_coverage_mutant',mutant);changed=importlib.util.module_from_spec(spec);spec.loader.exec_module(changed)
        if label=='hidden request bypass':
            calls.clear()
            with patch.object(changed,'fetch',side_effect=fake): out=changed.collect('https://example.invalid')
            ok(out['coverage_by_unit']['network_probe']['attempted']!=len(calls),label+': intended denominator mismatch observed')
        elif label=='incomplete body counted':
            journal=changed.ProbeJournal()
            with patch.object(changed,'fetch',return_value=changed.Probe('https://example.invalid',200,body_complete=False,body_error='cut')): journal.request('https://example.invalid')
            ok(journal.record()['returned']!=0,label+': false return counterexample observed')
        else:
            with patch.object(changed,'fetch',return_value=changed.Probe('https://example.invalid/spec',200,'application/json',json.dumps(good))):
                _,raw,_=capture(changed.main,['--openapi','https://example.invalid/spec','--format','json'])
            ok(json.loads(raw)['coverage_by_unit']['network_probe']['attempted']!=1,label+': missing CLI attempt observed')
    texts=[(path.parent/(name+'.py')).read_text() for name in ('page_audit','url_inspection','sitemap_audit','agent_surface')]
    blocks=[text.split('# ── collector coverage shared block',1)[-1].split('# ── end collector coverage shared block',1)[0] for text in texts]
    ok(len(set(blocks))==1,'four standalone schema/Markdown blocks byte-identical')
    print(f'B-9 agent coverage: {count} controls')


if __name__ == '__main__':
    import residue
    failures=[]; residue.open_case('agent-coverage'); workspace=residue.workspace('agent-coverage')
    run(lambda cond,label: failures.append(label) if not cond else None,Path(__file__).resolve().parents[1],workspace)
    if not failures: residue.close_case('agent-coverage')
    residue.report()
    if failures:
        print('FAIL: agent coverage')
        for label in failures: print('  -',label)
        raise SystemExit(1)
    print('PASS: agent coverage')
