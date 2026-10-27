from pathlib import Path
from collections import Counter
import hashlib,json,re,subprocess,time
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
started=time.perf_counter();checks=[]
def ck(n,b,detail=None):checks.append({'name':n,'passed':bool(b),'detail':detail})
base=json.loads((OUT/'manuscript-baseline.json').read_text());old=(ROOT/base['baseline_pdf']).parent;new=ROOT/base['candidate']
ck('old-pdf',sha(ROOT/base['baseline_pdf'])==base['baseline_pdf_sha256'])
changed=[]
for x in base['source_files']:
    n=x['path'];ck('protected/'+n,sha(old/n)==x['sha256'])
    if (old/n).read_bytes()!=(new/n).read_bytes():changed.append(n)
ck('intended-changes',set(changed)=={'accounting-product-proposal.tex','sections/corporate-methods.tex','sections/customer-obligations.tex','references.bib'},changed)
addition={str(p.relative_to(new)) for p in new.rglob('*') if p.suffix in ['.tex','.bib','.lark']}-{x['path'] for x in base['source_files']}
ck('intended-additions',addition=={'sections/corporate-residuals.tex'})
ck('prior-corporate',(new/'sections/corporate-methods.tex').read_text().replace('\n\\input{sections/corporate-residuals}\n','')==(old/'sections/corporate-methods.tex').read_text())
ck('bibliography-append-only',(new/'references.bib').read_text().startswith((old/'references.bib').read_text()))
texts=['\n'.join(p.read_text() for p in sorted(d.rglob('*.tex'))) for d in [old,new]]
counts={}
for n,p in {'displays':r'\\\[.*?\\\]|\\begin\{(?:equation\*?|align\*?|gather\*?)\}.*?\\end\{(?:equation\*?|align\*?|gather\*?)\}',
 'labels':r'\\label\{[^}]+\}','citations':r'\\cite\w*\*?(?:\[[^]]*\]){0,2}\{([^}]+)\}'}.items():
    a,b=[Counter(re.findall(p,t,re.S)) for t in texts];counts[n]={'before':sum(a.values()),'after':sum(b.values()),'removed':list((a-b).elements())};ck('preserved/'+n,not(a-b),counts[n])
build=json.loads((OUT/'build-run.json').read_text());review=json.loads((OUT/'render-review.json').read_text());render=json.loads((OUT/'accepted-final/render-manifest.json').read_text())
pdf=new/'accounting-product-proposal.pdf'
ck('clean-build',build['exit_code']==0 and not build['diagnostics'])
ck('same-final-bytes',sha(pdf)==build['pdf_sha256']==review['pdf_sha256']==render['pdf_sha256'])
for page in review['physical_pages']:
    row=render['pages'][str(page)];ck('render/'+str(page),sha(ROOT/row['path'])==row['sha256'])
fls=(new/'accounting-product-proposal.fls').read_text().splitlines();cwd=Path(next(x[4:] for x in fls if x.startswith('PWD ')))
paths={(cwd/x[6:]).resolve() for x in fls if x.startswith('INPUT ')}
external=[str(p) for p in paths if p.is_relative_to(ROOT) and not p.is_relative_to(new)]
ck('self-contained',not external,external)
arithmetic=json.loads((OUT/'independent-checks.json').read_text());tax=json.loads((OUT/'uncertain-tax-cases.json').read_text())
ck('arithmetic',arithmetic['passed'] and all(c['passed'] for c in arithmetic['details']))
ck('tax',tax['passed'] and all(c['passed'] for c in tax['details']))
ck('unrelated-index',subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT)==(ROOT/'data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt').read_bytes())
res={'passed':all(c['passed'] for c in checks),'check_count':len(checks),'counts':counts,'checks':checks,'pdf_sha256':sha(pdf),'wall_seconds':time.perf_counter()-started}
(OUT/'manuscript-checks.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps({k:res[k] for k in ['passed','check_count','counts','pdf_sha256']}))
assert res['passed'],[c for c in checks if not c['passed']]
