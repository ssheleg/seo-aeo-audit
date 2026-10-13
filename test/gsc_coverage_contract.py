"""Offline GSC request/row accounting; no credential or provider access."""
import importlib.util
import json
import io
import math
from pathlib import Path
from unittest.mock import patch
from collector_coverage_contract import capture, coverage_records


def load(root):
    path=Path(root)/'plugins/seo-aeo-audit/skills/seo-aeo-audit/scripts/gsc_pull.py'
    spec=importlib.util.spec_from_file_location('gsc_coverage_subject',path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod


def row(dims):
    return {'keys':[{'date':'2026-01-01','query':'fixture','page':'https://example.invalid/'}[d] for d in dims], 'clicks':1,'impressions':10,'ctr':.1,'position':2}


def run(check,root,workspace):
    mod=load(root);count=0
    def ok(condition,label):
        nonlocal count
        count+=1;check(condition,'B-9 GSC: '+label)
    def execute(failure=None,transform=None,fmt='json',extra=()):
        calls=[]
        def fake(path,token,qp,body=None):
            calls.append((path,body))
            if len(calls)==failure:raise SystemExit('fixture provider failure')
            if path=='/sites':return {'siteEntry':[{'siteUrl':'sc-domain:example.invalid'}]}
            if path.endswith('/sitemaps'):return {'sitemap':[]}
            dims=body['dimensions'];rows=[row(dims)]
            return transform(dims,rows) if transform else {'rows':rows}
        with patch.object(mod,'access_token',return_value='offline-sentinel'),patch.object(mod,'call',side_effect=fake):
            try:code,out,err=capture(mod.main,['--site','sc-domain:example.invalid','--format',fmt,*extra])
            except (SystemExit,TypeError,KeyError,ValueError,OverflowError) as exc:return None,None,calls,str(exc)
        return code,json.loads(out) if fmt=='json' else out,calls,err
    code,data,calls,_=execute()
    ok(code==0 and len(calls)==6,'six independent full-report operations')
    ok(bool(data and data.get('coverage_by_unit')),'common records emitted')
    if not data or not data.get('coverage_by_unit'):
        print(f'B-9 GSC coverage: {count} controls (emission absent)');return
    records=coverage_records(data);cov=data['coverage_by_unit']
    ok(len(records)==5 and cov['api_request']['requested']==cov['api_request']['returned']==6,'requests and four row populations remain distinct')
    ok(all(cov[k]['requested'] is None and cov[k]['state']=='unknown' for k in ('date_row','query_row','page_row','query_page_row')),'provider row universe unknown even below cap')
    for failed in range(1,7):
        code,out,calls,_=execute(failed)
        ok(code==0 and len(calls)==6 and out['coverage_by_unit']['api_request']['returned']==5 and out['collection_errors'],'each failure preserves independent successful requests')
        if failed in (2,3,4,5):
            unit=('date_row','query_row','page_row','query_page_row')[failed-2]
            ok(out['coverage_by_unit'][unit]['attempted'] is None and out['coverage_by_unit'][unit]['returned'] is None,'failed envelope is unknown rows, not zero')
    code,out,_,_=execute(transform=lambda dims,rows:{})
    ok(code==1 and out['coverage_by_unit']['api_request']['returned']==6 and all(out['coverage_by_unit'][u]['returned']==0 for u in ('date_row','query_row','page_row','query_page_row')),'typed empty API response observed; no useful measurement')
    for bad in ([],{'rows':None},{'rows':'bad'},{'error':{'message':'no'}}):
        code,out,_,_=execute(transform=lambda dims,rows:bad)
        ok(code==1 and out['coverage_by_unit']['api_request']['returned']==2 and out['coverage_by_unit']['query_row']['returned'] is None,'malformed envelope never becomes measured zero')
    for field,value in [('clicks',True),('impressions','10'),('ctr',float('nan')),('position',float('inf')),('keys',[]),('clicks',-1)]:
        def changed(dims,rows):
            broken=dict(rows[0]);broken[field]=value
            return {'rows':[broken,*rows]}
        code,out,_,_=execute(transform=changed)
        obs=out['row_observations']['query']
        ok(code==0 and obs['received']==2 and obs['invalid']==1 and out['coverage_by_unit']['query_row']['attempted']==2 and out['coverage_by_unit']['query_row']['returned']==1,'invalid row remains failed attempt; valid sibling preserved')
    def noisy(dims,rows):
        if 'query' not in dims:return {'rows':rows}
        noise=dict(rows[0],keys=['https://noise.invalid/',*rows[0]['keys'][1:]])
        return {'rows':[noise,*rows]}
    code,out,_,_=execute(transform=noisy)
    c=out['coverage_by_unit']['query_row']
    ok(c['attempted']==1 and c['returned']==1 and c['dropped']==1 and out['row_observations']['query']['received']==2,'known noise excluded before attempts without double counting')
    def capped(dims,rows):return {'rows':rows*(25000 if dims==['date'] else 101)}
    code,out,_,_=execute(transform=capped)
    ok('date' in out['row_limit_reached'] and out['row_limits']['date']==25000,'date row cap is visible')
    ok(out['row_observations']['query']['display_omitted_json']==1 and out['coverage_by_unit']['query_row']['returned']==101 and out['coverage_by_unit']['query_row']['dropped']==0,'display slice does not remove analyzed input')
    ok('tail is missing' not in mod.ROW_LIMIT_NOTE,'cap cannot assert nonzero unseen tail')
    code,text,_,_=execute(failure=2,fmt='text')
    ok('no collapse detected' not in text and 'UNAVAILABLE' in text and '## Collector coverage' in text,'failed date dimension cannot print clean collapse verdict')
    code,text,_,_=execute(failure=6,fmt='text')
    ok('none submitted' not in text,'failed sitemap listing cannot become observed empty')
    code,text,_,_=execute(failure=5,fmt='text')
    ok('none found in the query x page' not in text,'failed pairs cannot claim measured negative')
    for days in ('0','-1','999999999999'):
        with patch.object(mod,'access_token',side_effect=AssertionError('must reject before credentials')):
            try:code,_,_=capture(mod.main,['--site','sc-domain:example.invalid','--days',days])
            except SystemExit as exc:code=exc.code
        ok(code!=0,'invalid date window refused before credentials')
    for dimension,expected in [('query',{'position_split','branded_split'}),('date',{'monthly','cliff'}),('query_page',{'cannibalization'})]:
        def overflowing(dims,rows):
            name='_'.join(dims)
            if name!=dimension:return {'rows':rows}
            values=[]
            for number in range(22 if name=='date' else 2):
                keys=([f'2026-01-{number+1:02}'] if name=='date' else [f'fixture-{number}'] if name=='query' else ['fixture',f'https://example.invalid/{number}'])
                values.append(dict(rows[0],keys=keys,clicks=1e308,impressions=1e308))
            return {'rows':values}
        for fmt in ('json','text'):
            code,out,calls,_=execute(transform=overflowing,fmt=fmt,extra=('--brand-terms','fixture'))
            ok(code==0 and len(calls)==6 and bool(out),'aggregate overflow preserves actual main report and other dimensions')
            if not out:continue
            if fmt=='json':
                failed={entry['operation'] for entry in out.get('derivation_errors',[])}
                ok(expected <= failed and all(out[name] is None for name in expected),'failed aggregates are explicit null with named derivation error')
                ok(out['coverage_by_unit']['api_request']['returned']==6 and out['top_pages'] and out['row_observations'][dimension].get('derivation_errors'),'envelope and individually usable row counts qualified separately from failed aggregates')
                ok('Infinity' not in json.dumps(out) and 'NaN' not in json.dumps(out),'nonfinite aggregates cannot escape as non-JSON tokens')
            else:
                ok('UNAVAILABLE' in out and all(name in out for name in expected),'text names failed aggregates without erasing independent evidence')
    def overflow_ratio(dims,rows):
        return {'rows':[dict(rows[0],clicks=1e308,impressions=1e-308)] if dims==['query'] else rows}
    for fmt in ('json','text'):
        code,out,calls,_=execute(transform=overflow_ratio,fmt=fmt)
        ok(code==0 and len(calls)==6 and bool(out),'finite operands with overflowing quotient preserve actual main output')
        if fmt=='json':
            ok(out['position_split'] is None and any(e['operation']=='position_split' for e in out.get('derivation_errors',[])) and 'Infinity' not in json.dumps(out),'recursive derived-result validation refuses overflowing quotient')
        else:
            ok('UNAVAILABLE position_split' in out and 'inf%' not in out.lower(),'text identifies unusable quotient instead of formatting infinity')
    code,out,_,_=execute(failure=3)
    ok(out['rows_dropped_as_noise'] is None,'failed query dimension does not invent aggregate zero noise')
    def zero(dims,rows): return {'rows':[dict(rows[0],clicks=0,impressions=0,ctr=0,position=0)]}
    code,out,_,_=execute(transform=zero)
    ok(code==0 and out['coverage_by_unit']['query_row']['returned']==1,'genuine numeric zero remains usable')
    def huge(dims,rows): return {'rows':[dict(rows[0],clicks=10**1000),*rows]}
    code,out,_,_=execute(transform=huge)
    ok(code==0 and out['row_observations']['query']['invalid']==1,'unrepresentable numeric value cannot erase valid siblings')
    for fmt in ('json','text'):
        with patch.object(mod,'access_token',return_value='offline-secret'),patch.object(mod,'call',side_effect=SystemExit('provider echoed offline-secret and line\nnext | field')):
            code,text,_=capture(mod.main,['--site','sc-domain:example.invalid','--format',fmt])
        ok(code==1 and 'offline-secret' not in text and '<redacted>' in text,'diagnostics redact credential before JSON/text rendering')
    for fmt in ('json','text'):
        with patch.object(mod,'access_token',side_effect=SystemExit('fixture bootstrap unavailable')):
            try: capture(mod.main,['--site','sc-domain:example.invalid','--format',fmt])
            except SystemExit as exc:ok(str(exc)=='fixture bootstrap unavailable','bootstrap retains explicit early boundary')
            else:ok(False,'bootstrap retains explicit early boundary')
    for args,expected in [(['--list','--site','sc-domain:example.invalid'],0),(['--list'],1),([],1)]:
        with patch.object(mod,'access_token',return_value='fixture'),patch.object(mod,'call',return_value={'siteEntry':[]}):
            code,_,_=capture(mod.main,args)
        ok(code==expected,'legacy listing/missing-site boundary preserved')
    # The copied standalone script uses real HTTP on loopback and a task-owned
    # gcloud executable; no provider endpoint or credential store is consulted.
    import http.server, socketserver, threading, subprocess, sys, os
    class Handler(http.server.BaseHTTPRequestHandler):
        calls=[]
        def log_message(self,*args):pass
        def do_GET(self):
            self.calls.append(self.path)
            payload={'siteEntry':[{'siteUrl':'sc-domain:example.invalid'}]} if self.path.endswith('/sites') else {'sitemap':[]}
            body=json.dumps(payload).encode();self.send_response(200);self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
        def do_POST(self):
            self.calls.append(self.path)
            request=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
            if request['dimensions']==['query']:
                body=b'fixture unavailable offline-secret';self.send_response(503)
            else:
                body=json.dumps({'rows':[row(request['dimensions'])]}).encode();self.send_response(200)
            self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
    with socketserver.TCPServer(('127.0.0.1',0),Handler) as server:
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        try:
            script=Path(workspace)/'gsc_pull.py'
            original=(Path(root)/'plugins/seo-aeo-audit/skills/seo-aeo-audit/scripts/gsc_pull.py').read_text()
            api='https://searchconsole.googleapis.com/webmasters/v3'
            ok(original.count('API = "'+api+'"')==1,'exact loopback transport seam')
            script.write_text(original.replace('API = "'+api+'"','API = "http://127.0.0.1:'+str(server.server_address[1])+'/webmasters/v3"'))
            bin_dir=Path(workspace)/'bin';bin_dir.mkdir(exist_ok=True)
            executable=bin_dir/'gcloud';executable.write_text('#!/bin/sh\n[ "$*" = "auth application-default print-access-token" ] || exit 3\nprintf offline-secret\n');executable.chmod(0o700)
            env=dict(os.environ,PATH=str(bin_dir)+os.pathsep+os.environ.get('PATH',''))
            for fmt in ('json','text'):
                Handler.calls.clear()
                result=subprocess.run([sys.executable,str(script),'--site','sc-domain:example.invalid','--format',fmt],env=env,capture_output=True,text=True,cwd=workspace)
                ok(result.returncode==0 and len(Handler.calls)==6 and 'offline-secret' not in result.stdout+result.stderr,'actual copied CLI retains dimensions after HTTP503 and redacts provider echo')
                if fmt=='json':
                    payload=json.loads(result.stdout)
                    ok(payload['coverage_by_unit']['api_request']['returned']==5 and payload['coverage_by_unit']['query_row']['returned'] is None,'actual HTTP refusal emits unknown row counts')
        finally:server.shutdown();thread.join()
    source=(Path(root)/'plugins/seo-aeo-audit/skills/seo-aeo-audit/scripts/gsc_pull.py').read_text()
    for label,old,new in [
        ('invented provider population', 'None, len(rows)-noise, len(accepted), noise, reasons)', 'len(rows), len(rows)-noise, len(accepted), noise, reasons)'),
        ('noise attempted twice', 'None, len(rows)-noise, len(accepted), noise, reasons)', 'None, len(rows), len(accepted), noise, reasons)'),
    ]:
        ok(source.count(old)==1,label+': exact executable plant selector')
        mutant=Path(workspace)/(label.replace(' ','_')+'.py');mutant.write_text(source.replace(old,new,1))
        spec=importlib.util.spec_from_file_location('gsc_coverage_mutant',mutant);changed=importlib.util.module_from_spec(spec);spec.loader.exec_module(changed)
        rows=[row(['query']),dict(row(['query']),keys=['https://noise.invalid/'])]
        _,_,record=changed.observe_rows('query',rows,['query'],5000,100)
        ok(record['requested'] is not None if label=='invented provider population' else record['attempted']!=1,label+': intended false accounting observed')
    scripts=Path(root)/'plugins/seo-aeo-audit/skills/seo-aeo-audit/scripts'
    blocks=[(scripts/(name+'.py')).read_text().split('# ── collector coverage shared block',1)[1].split('# ── end collector coverage shared block',1)[0] for name in ('page_audit','url_inspection','sitemap_audit','agent_surface','gsc_pull')]
    ok(len(set(blocks))==1,'five standalone common blocks byte-identical')
    print(f'B-9 GSC coverage: {count} controls')


if __name__=='__main__':
    import residue
    failures=[];residue.open_case('gsc-coverage');workspace=residue.workspace('gsc-coverage')
    run(lambda cond,label:failures.append(label) if not cond else None,Path(__file__).resolve().parents[1],workspace)
    if not failures:residue.close_case('gsc-coverage')
    residue.report()
    if failures:
        print('FAIL: GSC coverage');print('\n'.join('  - '+x for x in failures));raise SystemExit(1)
    print('PASS: GSC coverage')
