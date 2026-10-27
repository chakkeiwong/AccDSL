from pathlib import Path
from collections import Counter
import hashlib,json,re,subprocess
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
base=json.loads((OUT/'baseline.json').read_text());prep=json.loads((OUT/'manuscript-preparation.json').read_text())
old=ROOT/base['candidate'];new=ROOT/prep['candidate'];checks=[]
def ck(n,b):checks.append({'name':n,'passed':bool(b)})
ck('protected-pdf',sha(old/'accounting-product-proposal.pdf')==base['pdf_sha256'])
changed=[]
for x in base['source_files']:
 ck('protected/'+x['path'],sha(old/x['path'])==x['sha256'])
 if sha(new/x['path'])!=x['sha256']:changed.append(x['path'])
ck('intended-changes',set(changed)==set(prep['intended_changed']))
added={str(p.relative_to(new)) for p in new.rglob('*') if p.suffix in ['.tex','.bib','.lark']}-{x['path'] for x in base['source_files']}
ck('intended-additions',added==set(prep['intended_added']))
ck('prior-validation-preserved',(new/'chapters/10-validation.tex').read_text().replace('\\input{sections/future-validation}\n\n','')==(old/'chapters/10-validation.tex').read_text())
ck('prior-bibliography-preserved',(new/'references.bib').read_text().startswith((old/'references.bib').read_text()))
texts=['\n'.join(p.read_text() for p in sorted(d.rglob('*.tex'))) for d in [old,new]];counts={}
for name,pattern in {'displays':r'\\\[.*?\\\]|\\begin\{(?:equation\*?|align\*?)\}.*?\\end\{(?:equation\*?|align\*?)\}','labels':r'\\label\{[^}]+\}','citations':r'\\cite\w*\*?(?:\[[^]]*\]){0,2}\{([^}]+)\}'}.items():
 a,b=[Counter(re.findall(pattern,t,re.S)) for t in texts];counts[name]={'before':sum(a.values()),'after':sum(b.values()),'removed':list((a-b).elements())};ck('preservation/'+name,not(a-b))
build=json.loads((OUT/'build-run.json').read_text());render=json.loads((OUT/'render-final/render-manifest.json').read_text())
ck('clean-build',build['exit_code']==0 and not build['diagnostics'])
ck('current-render',sha(new/'accounting-product-proposal.pdf')==render['pdf_sha256']==build['pdf_sha256'])
for n,row in render['pages'].items():ck('render/'+n,sha(ROOT/row['path'])==row['sha256'])
ck('protocol-checks',json.loads((OUT/'protocol-checks.json').read_text())['passed'])
ck('no-duplicated-citation','Gneiting and Raftery \\citep' not in (new/'sections/future-validation.tex').read_text())
ck('index-preserved',subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT)==(ROOT/'data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt').read_bytes())
out={'passed':all(c['passed'] for c in checks),'count':len(checks),'counts':counts,'checks':checks,'pdf_sha256':sha(new/'accounting-product-proposal.pdf'),'page_count':build['page_count']}
(OUT/'manuscript-checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='checks'}));assert out['passed']
