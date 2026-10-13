"""PSI input/measurement coverage; offline and loopback only."""
import importlib.util
import json
from pathlib import Path
from unittest.mock import patch
from collector_coverage_contract import capture, coverage_records


def load(root):
    path=Path(root)/'plugins/seo-aeo-audit/skills/seo-aeo-audit/scripts/psi_pull.py'
    spec=importlib.util.spec_from_file_location('psi_coverage_subject',path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod,path


def run(check,root,workspace):
    mod,path=load(root);count=0
    def ok(cond,label):
        nonlocal count
        count+=1;check(cond,'B-9 PSI: '+label)
    metrics={'LARGEST_CONTENTFUL_PAINT_MS':{'percentile':1000},'INTERACTION_TO_NEXT_PAINT':{'percentile':100},'CUMULATIVE_LAYOUT_SHIFT_SCORE':{'percentile':5}}
    field={'loadingExperience':{'metrics':metrics}}
    lab={'lighthouseResult':{'categories':{'performance':{'score':.9}}}}
    origin={'originLoadingExperience':{'metrics':metrics}}
    def execute(payloads,fmt='json',extra=()):
        args=[arg for i in range(len(payloads)) for arg in ('--url','https://example.invalid/same')]+['--format',fmt,*extra]
        with patch.object(mod,'fetch',side_effect=payloads):code,out,err=capture(mod.main,args)
        return code,json.loads(out) if fmt=='json' else out,err
    code,out,_=execute([{}]);ok(code==1,'empty object is not useful measurement')
    ok('coverage' in out,'common coverage record emitted')
    if 'coverage' not in out:
        print(f'B-9 PSI coverage: {count} controls (emission absent)');return
    for payload,returned,state in [(field,1,'partial'),(lab,1,'partial'),(origin,0,'partial'),({},0,'partial'),(dict(field,**lab),1,'complete')]:
        code,out,_=execute([payload]);cov=coverage_records(out)[0]
        ok((cov['requested'],cov['attempted'],cov['returned'],cov['dropped'],cov['state'])==(1,1,returned,0,state) and code==(0 if returned else 1),'component return predicate and scope state')
        text_code,text,_=execute([payload],fmt='markdown')
        ok(text_code==code and mod.collector_coverage_md(cov) in text,'JSON/default format count and exit parity')
        if payload is origin:ok(out['results'][0]['origin_field_data'] and out['results'][0]['field_data'] is None,'origin context retained without URL-field substitution')
    code,out,_=execute([{},dict(field,**lab),{'_error':'fixture network failure'}]);cov=out['coverage']
    ok(cov['requested']==cov['attempted']==3 and cov['returned']==1 and len(out['results'])==3,'duplicates and mixed failures preserve all inputs')
    for value in (None,True,'10',-1,float('nan'),float('inf'),{},[]):
        payload={'loadingExperience':{'metrics':{'LARGEST_CONTENTFUL_PAINT_MS':{'percentile':value}}}}
        code,out,_=execute([payload,dict(field,**lab)])
        r=out['results'][0]
        ok(code==0 and out['coverage']['returned']==1 and r['field_data']['LCP']['p75'] is None and r['field_data']['LCP']['band']=='unknown','invalid/missing percentile remains unknown while next URL survives')
    for value in (True,'0.5',-1,1.1,float('nan'),float('inf'),{},[]):
        payload={'lighthouseResult':{'categories':{'performance':{'score':value}}}}
        code,out,_=execute([payload,dict(field,**lab)])
        ok(code==0 and out['coverage']['returned']==1 and out['results'][0]['lab_performance_score'] is None,'malformed lab score never becomes measurement')
    for payload in (None,[],42,{'error':{'message':'fixture refusal'}},{'loadingExperience':[]},{'loadingExperience':{'metrics':[]}}, {'loadingExperience':{'metrics':{'LARGEST_CONTENTFUL_PAINT_MS':[]}}}):
        code,out,_=execute([payload,dict(field,**lab)])
        ok(code==0 and out['coverage']['returned']==1 and out['coverage']['state']=='partial','malformed envelope/component preserves following URL')
    for payload in [dict(lab,loadingExperience=[]),dict(field,lighthouseResult={'categories':[]})]:
        code,out,_=execute([payload]);ok(code==0 and out['coverage']['returned']==1 and out['results'][0]['payload_errors'],'valid component survives malformed sibling')
    zero={'loadingExperience':{'metrics':{'LARGEST_CONTENTFUL_PAINT_MS':{'percentile':0}}},'lighthouseResult':{'categories':{'performance':{'score':0}}}}
    code,out,_=execute([zero]);ok(code==0 and out['coverage']['returned']==1 and out['results'][0]['lab_performance_score']==0 and out['results'][0]['field_data']['LCP']['p75']==0,'zero is real data')
    code,out,_=execute([{}]);note=out['results'][0]['field_note']
    ok('too little traffic' not in note and 'NOT a pass' in note,'field absence states uncertainty without guessing cause')
    for fmt in ('json','markdown'):
        code,out,err=execute([{'_error':'echo fake/key+sentinel encoded fake%2Fkey%2Bsentinel'}],fmt=fmt,extra=('--key','fake/key+sentinel'))
        raw=json.dumps(out) if fmt=='json' else out
        ok(code==1 and 'fake/key+sentinel' not in raw+err and 'fake%2Fkey%2Bsentinel' not in raw+err,'plain and encoded credential echoes redacted')
    for payload in ({'_error':''},{'error':None},{'error':0},{'_error':False}):
        for fmt in ('json','markdown'):
            code,out,_=execute([payload,dict(field,**lab)],fmt=fmt)
            ok(code==0 and ('input_failed' in (json.dumps(out) if fmt=='json' else out)), 'empty/false error envelope preserves later measurements')
    unknown={'loadingExperience':{'metrics':{'LARGEST_CONTENTFUL_PAINT_MS':{}}}}
    code,out,_=execute([unknown]);code2,md,_=execute([unknown],fmt='markdown')
    ok(code==code2==1 and out['results'][0]['component_status']['url_field']=='unavailable' and 'None' not in md and 'unknown' in md,'present metric without percentile remains visibly unknown')
    for component in ('loadingExperience','originLoadingExperience','lighthouseResult'):
        code,out,_=execute([{component:{'unexpected':float('inf')}},dict(field,**lab)])
        ok(code==0 and 'Infinity' not in json.dumps(out) and 'NaN' not in json.dumps(out),'unselected nested nonfinite values cannot leak into output')
    # Error-body read failures happen inside HTTPError handling, not its sibling
    # exception handler. Preserve the status and the next independently useful row.
    import io,urllib.error,urllib.parse,sys,subprocess,threading
    from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
    class BrokenBody(io.BytesIO):
        def read(self,*args):raise OSError('fake/key+sentinel body read failed')
    err=urllib.error.HTTPError('https://example.invalid',503,'fixture',{},BrokenBody())
    with patch.object(mod.urllib.request,'urlopen',side_effect=err):
        payload=mod.fetch('https://example.invalid','mobile','fake/key+sentinel')
    ok('HTTP 503' in payload['_error'] and 'fake/key+sentinel' not in payload['_error'] and 'HTTP body read failed' in payload['_error'],'error-body read failure preserves status and redacts echo')
    requests=[]
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def do_GET(self):
            query=urllib.parse.parse_qs(urllib.parse.urlsplit(self.path).query);url=query['url'][0];requests.append(url)
            if url.endswith('/refused'):
                self.send_response(429);self.end_headers();self.wfile.write(b'echo fake/key+sentinel encoded fake%2Fkey%2Bsentinel');return
            if url.endswith('/bad-json'):
                self.send_response(200);self.end_headers();self.wfile.write(b'not JSON');return
            body=json.dumps(dict(field,**lab) if url.endswith('/good') else {}).encode()
            self.send_response(200);self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    copied=Path(workspace)/'psi-standalone.py'
    source=path.read_text();api='API = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"'
    ok(source.count(api)==1,'standalone loopback rewrites only one endpoint')
    copied.write_text(source.replace(api,f'API = "http://127.0.0.1:{server.server_port}/psi"',1))
    try:
        for fmt in ('json','markdown'):
            args=[sys.executable,'-B',str(copied),'--key','fake/key+sentinel','--format',fmt]
            for suffix in ('good','refused','bad-json','empty'):args+=['--url','https://example.invalid/'+suffix]
            proc=subprocess.run(args,capture_output=True,text=True,timeout=15,cwd=workspace)
            allout=proc.stdout+proc.stderr
            ok(proc.returncode==0 and 'fake/key+sentinel' not in allout and 'fake%2Fkey%2Bsentinel' not in allout and 'HTTP 429' not in allout and '429' in allout,'actual standalone mixed transport run preserves report and redacts diagnostic key')
            if fmt=='json':
                report=json.loads(proc.stdout);c=coverage_records(report)[0]
                ok(c['requested']==c['attempted']==4 and c['returned']==1 and c['state']=='partial' and len(report['results'])==4,'actual standalone JSON preserves all four input entries')
            else:ok('returned=1' in proc.stdout and 'requested=4' in proc.stdout and 'could not measure' in proc.stdout,'standalone Markdown count/error parity')
        ok(len(requests)==8,'one logical provider call per duplicate-preserving supplied entry')
    finally:server.shutdown();server.server_close();thread.join(timeout=2)
    # A source mutant of the old false-success predicate must fail the empty
    # envelope control through actual main(), not only a structural text check.
    mutant=Path(workspace)/'psi-false-return.py'
    needle='return 0 if returned else 1';ok(source.count(needle)==1,'false-return plant selector is unique')
    mutant.write_text(source.replace(needle,'return 0',1))
    spec=importlib.util.spec_from_file_location('psi_false_return',mutant);bad=importlib.util.module_from_spec(spec);spec.loader.exec_module(bad)
    with patch.object(bad,'fetch',return_value={}):badcode,_,_=capture(bad.main,['--url','https://example.invalid','--format','json'])
    ok(badcode!=1,'empty-envelope regression control rejects an actual false-success source mutant')
    homes=('page_audit','url_inspection','sitemap_audit','agent_surface','gsc_pull','psi_pull')
    blocks=[(path.parent/(home+'.py')).read_text().split('# ── collector coverage shared block',1)[1].split('# ── end collector coverage shared block',1)[0] for home in homes]
    ok(len(set(blocks))==1,'all six standalone common coverage blocks stay byte-identical')
    with patch.object(mod,'fetch',side_effect=AssertionError('bootstrap must not make a request')):
        for args,requested,dropped,reason in [([],0,0,'no_input'), (['--urls-file',str(Path(workspace)/'absent')],None,None,'input_population_unknown')]:
            code,out,_=capture(mod.main,[*args,'--format','json'])
            report=json.loads(out);cov=coverage_records(report)[0]
            ok(code==1 and report['results']==[] and (cov['requested'],cov['attempted'],cov['returned'],cov['dropped'],cov['state'])==(requested,0,0,dropped,'unknown' if requested is None else 'partial') and any(r['code']==reason for r in cov['reasons']),'bootstrap report preserves empty versus unknown population without provider calls')
    print(f'B-9 PSI coverage: {count} controls')


if __name__=='__main__':
    import residue
    failures=[];residue.open_case('psi-coverage');workspace=residue.workspace('psi-coverage')
    run(lambda cond,label:failures.append(label) if not cond else None,Path(__file__).resolve().parents[1],workspace)
    if not failures:residue.close_case('psi-coverage')
    residue.report()
    if failures:
        print('FAIL: PSI coverage');print('\n'.join('  - '+x for x in failures));raise SystemExit(1)
    print('PASS: PSI coverage')
