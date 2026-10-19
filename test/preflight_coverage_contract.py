"""Offline preflight readiness coverage; no provider credentials."""
import importlib.util,json
from pathlib import Path
from unittest.mock import patch
from collector_coverage_contract import capture,coverage_records

def load(root):
 path=Path(root)/'plugins/seo-aeo-audit/skills/seo-aeo-audit/scripts/preflight.py'
 spec=importlib.util.spec_from_file_location('preflight_coverage_subject',path);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod,path

def run(check,root,workspace):
 mod,path=load(root);count=0
 def ok(cond,label):
  nonlocal count
  count+=1;check(cond,'B-9 preflight: '+label)
 def execute(args=(),token='offline-token',reply=None,fmt='json'):
  calls=[]
  def fake(url,**kwargs):
   calls.append(url)
   if reply:return reply(url,kwargs)
   body=json.dumps({'siteEntry':[{'siteUrl':'sc-domain:example.invalid','permissionLevel':'siteOwner'}]}) if '/sites' in url else json.dumps({'loadingExperience':{'metrics':{'LARGEST_CONTENTFUL_PAINT_MS':{'percentile':1000}}},'lighthouseResult':{'categories':{'performance':{'score':.9}}}}) if 'runPagespeed' in url else 'User-agent: *\n' if url.endswith('robots.txt') else '<html>fixture</html>'
   return mod.ProbeResponse(200,body) if hasattr(mod,'ProbeResponse') else (200,body)
  with patch.object(mod,'_get',side_effect=fake),patch.object(mod,'check_gcloud',return_value=(mod.probe('gcloud ADC',bool(token),'fixture','login' if not token else None),token)):
   code,out,err=capture(mod.main,[*args,'--format',fmt])
  return code,json.loads(out) if fmt=='json' else out,err,calls
 code,data,_,calls=execute(['--origin','https://example.invalid','--skip-psi'])
 ok(code==0 and isinstance(data.get('coverage'),list),'legacy track carrier and report exit preserved')
 ok('coverage_by_unit' in data,'separate common carrier emitted')
 if 'coverage_by_unit' not in data:
  print(f'B-9 preflight coverage: {count} controls (emission absent)');return
 for args,nlocal,nnetwork in [(['--origin','https://example.invalid','--skip-psi'],1,3),(['--origin','https://example.invalid'],1,4),(['--site','sc-domain:example.invalid'],2,1),(['--site','sc-domain:example.invalid','--origin','https://example.invalid'],2,5)]:
  code,data,_,calls=execute(args);records=data['coverage_by_unit'];coverage_records(data)
  ok(code==0 and records['local_probe']['requested']==records['local_probe']['returned']==nlocal and records['network_probe']['requested']==records['network_probe']['attempted']==records['network_probe']['returned']==nnetwork and len(calls)==nnetwork,'flag-defined local/network denominator, no property-row double count')
  ok(data['coverage']==mod.coverage_seed(data['probes']),'legacy seeded track meanings unchanged')
  code,md,_,_=execute(args,fmt='markdown');ok(code==0 and all(mod.collector_coverage_md(r) in md for r in records.values()),'default output includes identical common counts')
 code,data,_,calls=execute(['--site','sc-domain:example.invalid','--origin','https://example.invalid'],token=None)
 cov=data['coverage_by_unit']['network_probe'];ok(cov['requested']==5 and cov['attempted']==4 and cov['returned']==4 and cov['dropped']==1 and len(calls)==4,'missing ADC excludes exactly one known network prerequisite')
 ok(data['coverage_by_unit']['local_probe']['returned']==2 and data['coverage_by_unit']['local_probe']['state']=='partial','known failed local prerequisite outcome is not credential success')
 for envelope in ([],None,42,{'siteEntry':None},{'siteEntry':[None]},{'error':{'message':'refused'}}):
  def reply(url,kwargs):
   return mod.ProbeResponse(200,json.dumps(envelope)) if '/sites' in url else mod.ProbeResponse(200,'{}')
  code,data,_,calls=execute(['--site','sc-domain:example.invalid','--origin','https://example.invalid'],reply=reply)
  property_row=next(row for row in data['probes'] if row['source'].startswith('property '))
  ok(code==0 and len(calls)==5 and property_row['gate']=='unattempted' and data['coverage_by_unit']['network_probe']['state']=='partial','malformed property envelope cannot erase public probes or invent absence')
 for entries,reachable,gate in [([],False,'permission'),([None,{'siteUrl':'sc-domain:example.invalid','permissionLevel':'siteOwner'}],True,None),([None,{'siteUrl':'sc-domain:other.invalid'}],False,'unattempted')]:
  def reply(url,kwargs):return mod.ProbeResponse(200,json.dumps({'siteEntry':entries}))
  code,data,_,_=execute(['--site','sc-domain:example.invalid'],reply=reply);p=data['probes'][-1]
  ok(code==0 and p['reachable']==reachable and p['gate']==gate,'typed empty negative versus malformed unknown and retained valid match')
 for envelope in ([],None,42,{'error':{}},{'loadingExperience':[]},{'loadingExperience':{'metrics':[]}},{}):
  def reply(url,kwargs):return mod.ProbeResponse(200,json.dumps(envelope))
  code,data,_,_=execute(['--origin','https://example.invalid'],reply=reply)
  ok(code==0 and len(data['probes'])==5 and 'lab-only' not in data['probes'][-1]['detail'] and data['coverage_by_unit']['network_probe']['state']=='partial','malformed/empty PSI preserves prior probes without inventing lab')
 for value in (None,True,'10',-1,float('inf'),float('nan'),10**1000):
  payload={'loadingExperience':{'metrics':{'LARGEST_CONTENTFUL_PAINT_MS':{'percentile':value}}}}
  ok(not mod.has_crux_field_data(payload),'invalid recognized percentile is unknown')
  payload={'lighthouseResult':{'categories':{'performance':{'score':value}}}}
  ok(not mod.has_lab_score(payload),'invalid lab score is unknown')
 ok(mod.has_crux_field_data({'loadingExperience':{'metrics':{'LARGEST_CONTENTFUL_PAINT_MS':{'percentile':0}}}}) and mod.has_lab_score({'lighthouseResult':{'categories':{'performance':{'score':0}}}}),'zero field/lab observations remain real')
 for status,complete,expected_return in [(0,False,0),(404,True,3),(200,False,3)]:
  code,data,_,_=execute(['--origin','https://example.invalid','--skip-psi'],reply=lambda u,k:mod.ProbeResponse(status,'fixture',complete,'fixture limitation' if not complete else ''))
  cov=data['coverage_by_unit']['network_probe'];ok(cov['returned']==expected_return and cov['attempted']==3 and cov['state']=='partial','landing status return remains distinct from access/body completeness')
 for mode in ('markdown','coverage'):
  code,out,_,calls=execute(['--origin','https://example.invalid','--skip-psi'],fmt=mode)
  ok(code==0 and len(calls)==3 and '## Track coverage' in out and out.count('## Collector coverage')==2,'both rendered probe modes include separate common and track coverage')
 with patch.object(mod,'_get',side_effect=AssertionError('provenance must not probe')),patch.object(mod,'check_gcloud',side_effect=AssertionError('provenance must not request ADC')):
  code,out,_=capture(mod.main,['--site','sc-domain:example.invalid','--origin','https://example.invalid','--format','provenance'])
 ok(code==0 and '## Provenance' in out and '## Collector coverage' not in out,'provenance seeding remains no-probe mode')
 for operation in ('/sites','runPagespeed'):
  def deep(url,kwargs):
   return mod.ProbeResponse(200,'['*1500+'0'+']'*1500 if operation in url else '{}')
  code,data,_,calls=execute(['--site','sc-domain:example.invalid','--origin','https://example.invalid'],reply=deep)
  ok(code==0 and len(calls)==5 and data['coverage_by_unit']['network_probe']['state']=='partial','deep provider JSON retains other probe outcomes')
 response=mod._get('https://[malformed')
 ok(response[0]==0 and not response.complete,'invalid URL construction becomes a failed attempt')
 import subprocess,io,urllib.error,os,sys,threading,gzip,http.client
 from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
 with patch.object(mod.subprocess,'run',return_value=subprocess.CompletedProcess([],0,stdout='',stderr='')):
  row,token=mod.check_gcloud()
 ok(token is None and not row['reachable'],'empty ADC stdout is not a successful token')
 with patch.object(mod.subprocess,'run',side_effect=subprocess.CalledProcessError(1,[],stderr='secret-like-provider-output')):
  row,token=mod.check_gcloud()
 ok(token is None and 'secret-like-provider-output' not in json.dumps(row),'failed token command diagnostic withholds raw provider stderr')
 key='offline/key+secret';requests=[]
 metrics={name:{'percentile':v} for name,v in [('LARGEST_CONTENTFUL_PAINT_MS',1000),('INTERACTION_TO_NEXT_PAINT',100),('CUMULATIVE_LAYOUT_SHIFT_SCORE',5)]}
 class Handler(BaseHTTPRequestHandler):
  def log_message(self,*args):pass
  def do_GET(self):
   requests.append(self.path)
   if self.path.startswith('/error'):
    self.send_response(403);self.send_header('Content-Length','²');self.end_headers();self.wfile.write(b'offline/key+secret offline%2Fkey%2Bsecret');return
   if self.path.startswith('/duplicate-length'):
    self.send_response(200);self.send_header('Content-Length','2');self.send_header('Content-Length','900' if 'conflict' in self.path else '2');self.end_headers();self.wfile.write(b'{}');return
   if self.path.startswith('/transfer-and-length'):
    self.send_response(200);self.send_header('Transfer-Encoding','chunked');self.send_header('Content-Length','2');self.end_headers();self.wfile.write(b'2\r\n{}\r\n0\r\n\r\n');return
   if self.path.startswith('/bad-length'):
    self.send_response(200);self.send_header('Content-Length','²');self.end_headers();self.wfile.write(b'{}');return
   if self.path.startswith('/short'):
    self.send_response(200);self.send_header('Content-Length','100');self.end_headers();self.wfile.write(b'{}');return
   if self.path.startswith('/capped'):
    body=b'{}'+b' '*100
   elif self.path.startswith('/gzip'):
    body=gzip.compress(b'fixture'*30)
   elif self.path.startswith('/sites'):
    body=json.dumps({'siteEntry':[{'siteUrl':'sc-domain:example.invalid','permissionLevel':'siteOwner'}]}).encode()
   elif self.path.startswith('/runPagespeed'):
    body=json.dumps({'loadingExperience':{'metrics':metrics},'lighthouseResult':{'categories':{'performance':{'score':.8}}}}).encode()
   elif self.path.startswith('/robots.txt'):
    body=f'Sitemap: http://127.0.0.1:{self.server.server_port}/first.xml\nSitemap: http://127.0.0.1:{self.server.server_port}/second.xml\n'.encode()
   else:body=b'<html>fixture</html>'
   self.send_response(200);self.send_header('Content-Length',str(len(body)))
   if self.path.startswith('/gzip'):self.send_header('Content-Encoding','gzip')
   self.end_headers();self.wfile.write(body)
 server=ThreadingHTTPServer(('127.0.0.1',0),Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();origin=f'http://127.0.0.1:{server.server_port}'
 try:
  for suffix,budget in [('/error',4096),('/bad-length',4096),('/short',4096),('/capped',8),('/gzip',40)]:
   response=mod._get(origin+suffix,max_bytes=budget,secret=key)
   ok(response[0] in (200,403) and not response.complete,'actual incomplete/capped/gzip/error body preserves landing status')
  for suffix in ('/duplicate-length-conflict','/transfer-and-length'):
   response=mod._get(origin+suffix)
   ok(response[0]==200 and not response.complete,'conflicting duplicate or TE/CL framing remains partial with observed status')
  response=mod._get(origin+'/duplicate-length-same')
  ok(response[0]==200 and response.complete,'identical repeated Content-Length is a determinate positive')
  journal=mod.ReadinessJournal(None,origin,False)
  with patch.object(mod,'PSI',origin+'/duplicate-length-conflict'):
   rows=mod.check_public(origin,journal)+[mod.check_psi(origin,journal)]
  journal.note_local('python',mod.check_python());cov=journal.records()['network_probe']
  ok(len(rows)==4 and cov['returned']==4 and cov['state']=='partial' and 'unknown' in rows[-1]['detail'],'ambiguous PSI framing retains other public observations and status counts')
  with patch.object(mod,'GSC_SITES',origin+'/error'):
   rows=mod.check_gsc(key,'sc-domain:example.invalid',None)
  ok(key not in json.dumps(rows) and 'offline%2Fkey%2Bsecret' not in json.dumps(rows) and 'HTTP 403' in rows[0]['detail'],'actual GSC error diagnostics redact plain/encoded token echoes')
  class BrokenBody(io.BytesIO):
   def read(self,*a):raise OSError('offline/key+secret failed body')
  error=urllib.error.HTTPError(origin,404,'fixture',{},BrokenBody())
  with patch.object(mod.urllib.request,'urlopen',side_effect=error):response=mod._get(origin,secret=key)
  ok(response[0]==404 and not response.complete and key not in str(response)+response.error,'HTTPError body exception retains status without leaking token')
  # Standalone copy rewrites only two named endpoint constants. All external
  # transport stays loopback, and local fake ADC cannot invoke an installed gcloud.
  copy=Path(workspace)/'preflight-copy.py';source=path.read_text()
  gsc='GSC_SITES = "https://searchconsole.googleapis.com/webmasters/v3"';psi='PSI = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"'
  ok(source.count(gsc)==source.count(psi)==1,'copied CLI rewrites unique GSC/PSI endpoints')
  copy.write_text(source.replace(gsc,f'GSC_SITES = "{origin}"').replace(psi,f'PSI = "{origin}/runPagespeed"'))
  bindir=Path(workspace)/'bin';bindir.mkdir(exist_ok=True);fake=bindir/'gcloud';marker=Path(workspace)/'adc-calls'
  fake.write_text('#!'+sys.executable+'\nfrom pathlib import Path\np=Path('+repr(str(marker))+')\np.write_text(p.read_text()+"1" if p.exists() else "1")\nprint('+repr(key)+')\n');fake.chmod(0o755)
  env=dict(os.environ,PATH=str(bindir)+os.pathsep+os.environ.get('PATH',''))
  for fmt in ('json','markdown','coverage','provenance'):
   before=len(requests);proc=subprocess.run([sys.executable,'-B',str(copy),'--site','sc-domain:example.invalid','--origin',origin,'--format',fmt],cwd=workspace,env=env,capture_output=True,text=True,timeout=20)
   ok(proc.returncode==0 and key not in proc.stdout+proc.stderr and 'offline%2Fkey%2Bsecret' not in proc.stdout+proc.stderr,'actual standalone report has no credential echo')
   if fmt=='json':
    data=json.loads(proc.stdout);cov=data['coverage_by_unit'];ok(len(coverage_records(data))==2 and cov['network_probe']['returned']==5 and cov['network_probe']['state']=='complete' and data['total']==8,'standalone five requests differ from eight visible rows')
   elif fmt=='provenance':ok(len(requests)==before,'standalone provenance makes zero network calls')
   else:ok('## Track coverage' in proc.stdout and proc.stdout.count('## Collector coverage')==2,'standalone rendered mode retains both coverage vocabularies')
  ok(marker.read_text()=='111' and any('/first.xml' in url for url in requests) and not any('/second.xml' in url for url in requests),'three collector runs mint once each; provenance skips; only first sitemap is requested')
 finally:server.shutdown();server.server_close();thread.join(timeout=2)
 homes=('page_audit','url_inspection','sitemap_audit','agent_surface','gsc_pull','psi_pull','preflight','ai_panel','bwt_pull')
 blocks=[(path.parent/(home+'.py')).read_text().split('# ── collector coverage shared block',1)[1].split('# ── end collector coverage shared block',1)[0] for home in homes]
 ok(len(set(blocks))==1,'nine standalone common blocks stay byte-identical')
 # Independent admission must refuse the actual dropped-accounting source mutant.
 source=path.read_text();needle='"attempted": False, "status": None'
 ok(source.count(needle)==1,'excluded-operation mutation selector is unique')
 mutant=Path(workspace)/'preflight-mutant.py';mutant.write_text(source.replace(needle,'"attempted": True, "status": None',1))
 spec=importlib.util.spec_from_file_location('preflight_mutant',mutant);bad=importlib.util.module_from_spec(spec);spec.loader.exec_module(bad)
 journal=bad.ReadinessJournal(True,None,False);journal.note_local('python',bad.probe('python',True,'fixture'));journal.note_local('adc',bad.probe('ADC',False,'fixture'));journal.skip_network('property_list');cov=journal.records()['network_probe']
 ok(cov['dropped']!=1 or cov['attempted']!=0,'missing-prerequisite accounting control rejects false-attempt mutant')
 print(f'B-9 preflight coverage: {count} controls')

if __name__=='__main__':
 import residue
 failures=[];residue.open_case('preflight-coverage');work=residue.workspace('preflight-coverage')
 run(lambda cond,label:failures.append(label) if not cond else None,Path(__file__).resolve().parents[1],work)
 if not failures:residue.close_case('preflight-coverage')
 residue.report()
 if failures:print('FAIL: preflight coverage\n'+'\n'.join('  - '+s for s in failures));raise SystemExit(1)
 print('PASS: preflight coverage')
