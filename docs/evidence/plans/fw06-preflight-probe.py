"""Read-only source probes; mocks/owned UTF-8 fixture, no network or credentials."""
import contextlib,importlib.util,io,json,sys
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'test'))
import residue
residue.open_case('preflight-packet');work=residue.workspace('preflight-packet')
def load(name):
 p=ROOT/'plugins/seo-aeo-audit/skills/seo-aeo-audit/scripts'/f'{name}.py'
 spec=importlib.util.spec_from_file_location(name,p);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
pre=load('preflight');psi=load('psi_pull')
results=[]
def capture(label,fn):
 out=io.StringIO();err=io.StringIO()
 try:
  with contextlib.redirect_stdout(out),contextlib.redirect_stderr(err):value=fn()
  results.append({'case':label,'return':value,'stdout_bytes':len(out.getvalue().encode()),'result_json':json.loads(out.getvalue()) if out.getvalue().startswith('{') else None})
 except Exception as exc:results.append({'case':label,'exception':type(exc).__name__,'stdout_bytes':len(out.getvalue().encode())})
with patch.object(pre,'_get',return_value=(200,'[]')):capture('PSI scalar envelope',lambda:pre.main(['--origin','https://example.invalid','--format','json']))
with patch.object(pre,'_get',return_value=(200,'{}')):capture('PSI empty object',lambda:pre.check_psi('https://example.invalid'))
class Reply:
 def __enter__(self):return self
 def __exit__(self,*args):pass
 def read(self):return b'{"siteEntry":[null]}'
with patch.object(pre.urllib.request,'urlopen',return_value=Reply()):capture('GSC malformed property row',lambda:pre.check_gsc('offline-fixture','sc-domain:example.invalid',None))
bad=Path(work)/'non-utf8.txt';bad.write_bytes(b'\xff')
capture('PSI non-UTF8 input list',lambda:psi.main(['--urls-file',str(bad),'--format','json']))
with patch.object(pre,'check_public',return_value=[pre.probe('homepage',False,'fixture failure','http')]):capture('preflight legacy carrier',lambda:pre.main(['--origin','https://example.invalid','--skip-psi','--format','json']))
print(json.dumps(results,indent=2));residue.close_case('preflight-packet');residue.report()
