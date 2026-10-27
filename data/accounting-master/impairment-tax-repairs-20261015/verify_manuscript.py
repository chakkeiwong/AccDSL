from pathlib import Path
from collections import Counter
import hashlib,json,re,subprocess
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
b=json.loads((OUT/'manuscript-baseline.json').read_text());old=ROOT/b['baseline'];new=ROOT/b['candidate'];checks=[]
def ck(n,v):checks.append({'name':n,'passed':bool(v)})
ck('old-pdf',sha(old/'accounting-product-proposal.pdf')==b['pdf_sha256']);changed=[]
for x in b['source_files']:
 ck('protected/'+x['path'],sha(old/x['path'])==x['sha256'])
 if sha(new/x['path'])!=x['sha256']:changed.append(x['path'])
ck('intended-changes',set(changed)=={'accounting-product-proposal.tex','sections/corporate-methods.tex','references.bib'})
ck('prior-methods-preserved',(new/'sections/corporate-methods.tex').read_text().replace('\n\n\\input{sections/impairment-tax}','')==(old/'sections/corporate-methods.tex').read_text())
ck('prior-bibliography-preserved',(new/'references.bib').read_text().startswith((old/'references.bib').read_text()))
texts=['\n'.join(p.read_text() for p in sorted(d.rglob('*.tex'))) for d in [old,new]];counts={}
for k,p in {'displays':r'\\\[.*?\\\]|\\begin\{(?:equation\*?|align\*?)\}.*?\\end\{(?:equation\*?|align\*?)\}','labels':r'\\label\{[^}]+\}','citations':r'\\cite\w*\*?(?:\[[^]]*\]){0,2}\{([^}]+)\}'}.items():
 a,z=[Counter(re.findall(p,t,re.S)) for t in texts];counts[k]={'before':sum(a.values()),'after':sum(z.values()),'removed':list((a-z).elements())};ck(k+'/preserved',not(a-z))
build=json.loads((OUT/'build-run.json').read_text());render=json.loads((OUT/'render-v2/render-manifest.json').read_text());h=sha(new/'accounting-product-proposal.pdf')
ck('clean-build',build['exit_code']==0 and not build['diagnostics']);ck('render-bound',build['pdf_sha256']==render['pdf_sha256']==h)
for n,row in render['pages'].items():ck('page/'+n,sha(ROOT/row['path'])==row['sha256'])
cases=json.loads((OUT/'cases.json').read_text());ck('independent-arithmetic',cases['passed'])
for x in cases['sources']:ck('authority/'+x['path'],sha(ROOT/x['path'])==x['sha256'])
ck('index-preserved',subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT)==(ROOT/'data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt').read_bytes())
out={'passed':all(x['passed'] for x in checks),'count':len(checks),'counts':counts,'checks':checks,'pdf_sha256':h,'page_count':build['page_count']};(OUT/'manuscript-checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='checks'}));assert out['passed']
