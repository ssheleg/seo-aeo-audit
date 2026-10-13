import ast,os,re,tempfile,json,subprocess,sys
from pathlib import Path
owner=Path(__file__).resolve().parents[4];hub=Path(sys.argv[1]);text=hub.read_text();tree=ast.parse(text)
names={'SHARED_SIMILARITY','SHARED_MIN_COPIES','_SHARED_DECL','_SHARED_DIVERGES','_MODULE_CONST'}
selected=[]
for node in tree.body:
 if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id in names for t in node.targets):selected.append(node)
 if isinstance(node,ast.FunctionDef) and node.name=='check_a_copied_mechanism_declares_its_divergence':selected.append(node)
with tempfile.TemporaryDirectory(prefix='seo-shared-header-') as folder:
 root=Path(folder);(root/'test').mkdir();(root/'skills/seo-aeo-audit/test').mkdir(parents=True)
 for name in ('owner_board.py','owner_release.py'):
  original=subprocess.check_output(['git','show','5e9f6af67f9f01f70250465d63b0bb5f04983229:test/'+name],text=True)
  reference=re.sub(r'(?m)^# diverges: .*$', '# diverges: none', original)
  (root/'test'/name).write_text(reference);(root/'skills/seo-aeo-audit/test'/name).write_text((owner/'test'/name).read_text())
 errors=[];ns={'os':os,'re':re,'ROOT':str(root),'manifest':{'skills':[{'name':'seo-aeo-audit'}]},'_skips':[],'fail':errors.append}
 exec(compile(ast.Module(body=selected,type_ignores=[]),str(hub),'exec'),ns);ns['check_a_copied_mechanism_declares_its_divergence']()
 print(json.dumps({'errors':errors,'observations':ns['_skips']},indent=2))
 raise SystemExit(bool(errors))
