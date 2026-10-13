"""Source-bound loopback/pure baseline; never uses provider endpoints or secrets."""
import contextlib,gzip,http.client,importlib.util,io,json,sys,threading,urllib.error
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'test'))
import residue
residue.open_case('transport-packet');work=residue.workspace('transport-packet')
def load(name):
 path=ROOT/'plugins/seo-aeo-audit/skills/seo-aeo-audit/scripts'/f'{name}.py'
 spec=importlib.util.spec_from_file_location('probe_'+name,path);mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod;spec.loader.exec_module(mod);return mod
mods={name:load(name) for name in ('page_audit','agent_surface','sitemap_audit','psi_pull','gsc_pull','url_inspection')}
metrics={name:{'percentile':v} for name,v in [('LARGEST_CONTENTFUL_PAINT_MS',1000),('INTERACTION_TO_NEXT_PAINT',100),('CUMULATIVE_LAYOUT_SHIFT_SCORE',5)]}
valid_psi={'loadingExperience':{'metrics':metrics},'lighthouseResult':{'categories':{'performance':{'score':.9}}}}
valid_index={'inspectionResult':{'indexStatusResult':{'verdict':'PASS','coverageState':'Submitted and indexed'}}}
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def do_POST(self):self.do_GET()
 def do_GET(self):
  route=self.path.split('?')[0];content_type='application/json'
  if route.startswith('/page'):
   body=b'<html><title>Fixture</title><body>known</body></html>';content_type='text/html'
  elif route.startswith('/gzip-page'):
   body=gzip.compress(b'<html><title>Fixture</title><body>'+b'x'*5000+b'</body></html>');content_type='text/html'
  elif route.startswith('/sitemap'):
   body=b'<urlset><url><loc>https://example.invalid/page</loc></url></urlset>';content_type='application/xml'
  elif route.startswith('/psi'):body=json.dumps(valid_psi).encode()
  elif route.startswith('/gsc'):body=b'{"rows":[]}'
  elif route.startswith('/inspection'):body=json.dumps(valid_index).encode()
  else:body=b'{}'
  self.send_response(200);self.send_header('Content-Type',content_type);self.send_header('Content-Length',str(len(body)))
  if route.startswith('/gzip-page'):self.send_header('Content-Encoding','gzip')
  else:self.send_header('Content-Length',str(len(body)+900))
  self.end_headers();self.wfile.write(body)
server=ThreadingHTTPServer(('127.0.0.1',0),Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();origin=f'http://127.0.0.1:{server.server_port}'
observations=[]
def observe(label,fn):
 out=io.StringIO();err=io.StringIO()
 try:
  with contextlib.redirect_stdout(out),contextlib.redirect_stderr(err):value=fn()
  observations.append({'case':label,'observed':value,'stdout_bytes':len(out.getvalue().encode())})
 except BaseException as exc:observations.append({'case':label,'exception':type(exc).__name__,'stdout_bytes':len(out.getvalue().encode())})
try:
 m=mods['page_audit']
 observe('page conflicting lengths',lambda:{'truncated':m.fetch(origin+'/page',5,m.DEFAULT_UA,4096)[2]})
 observe('page decoded gzip exceeds requested budget',lambda:(lambda r:{'decoded_characters':len(r[0]),'budget':128,'truncated':r[2]})(m.fetch(origin+'/gzip-page',5,m.DEFAULT_UA,128)))
 m=mods['agent_surface'];observe('agent conflicting lengths',lambda:(lambda p:{'status':p.status,'body_complete':p.body_complete})(m.fetch(origin+'/agent')))
 m=mods['sitemap_audit'];observe('sitemap conflicting lengths',lambda:{'parseable_page_count':len(m.parse_sitemap(m.fetch(origin+'/sitemap'))[0])})
 m=mods['psi_pull']
 with patch.object(m,'API',origin+'/psi'):observe('PSI conflicting lengths',lambda:{'useful_measurement':m.useful_measurement(m.parse(m.fetch('https://example.invalid','mobile',None),'https://example.invalid'))})
 m=mods['gsc_pull']
 with patch.object(m,'API',origin+'/gsc'):observe('GSC conflicting lengths',lambda:{'usable_rows':m.collection_rows(m.call('/fixture','offline-fixture',None),'rows')})
 m=mods['url_inspection']
 with patch.object(m,'API',origin+'/inspection'):observe('inspection conflicting lengths',lambda:{'answered':len(m.answered_rows([m.parse(m.inspect('sc-domain:example.invalid','https://example.invalid','offline-fixture',None),'https://example.invalid')]))})
 for payload in ([],{'inspectionResult':{'indexStatusResult':{'verdict':1}}},{'inspectionResult':{'indexStatusResult':{'unknown':1}}}):
  with patch.object(m,'access_token',return_value='offline-fixture'),patch.object(m,'inspect',return_value=payload):
   def run_inspection():
    output=io.StringIO()
    with contextlib.redirect_stdout(output):code=m.main(['--site','sc-domain:example.invalid','--urls','https://example.invalid','--format','json'])
    result=json.loads(output.getvalue());return {'exit':code,'returned':result['coverage']['returned'],'findings':[f['code'] for row in result['results'] for f in row.get('findings',[])]}
   observe('inspection payload '+str(payload),run_inspection)
 class BrokenBody(io.BytesIO):
  def read(self,*args):raise http.client.IncompleteRead(b'fixture',100)
 m=mods['gsc_pull'];error=urllib.error.HTTPError(origin,403,'fixture',{},BrokenBody())
 with patch.object(m,'access_token',return_value='offline-fixture'),patch.object(m.urllib.request,'urlopen',side_effect=error):observe('GSC error-body incomplete main',lambda:m.main(['--site','sc-domain:example.invalid','--format','json']))
 m=mods['url_inspection'];error=urllib.error.HTTPError(origin,403,'fixture',{},BrokenBody())
 with patch.object(m,'access_token',return_value='offline-fixture'),patch.object(m.urllib.request,'urlopen',side_effect=error):observe('inspection error-body incomplete main',lambda:m.main(['--site','sc-domain:example.invalid','--urls','https://example.invalid','--format','json']))
finally:server.shutdown();server.server_close();thread.join(timeout=2)
print(json.dumps(observations,indent=2));residue.close_case('transport-packet');residue.report()
