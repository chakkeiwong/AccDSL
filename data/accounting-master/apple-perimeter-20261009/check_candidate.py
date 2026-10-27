"""Check the bounded V2.15 manuscript and preserved source/evidence records."""
from datetime import datetime, timezone
import difflib
import hashlib
import json
import os
from pathlib import Path
import re
import time

import fitz

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
OLD=ROOT/'docs/design/proposal/manuscript-segments-20261009'
NEW=ROOT/'docs/design/proposal/manuscript-perimeter-20261009'
assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1'
assert not (OUT/'candidate-checks.json').exists(),'Preserve earlier check report'
timer=time.monotonic()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
norm=lambda s:' '.join(s.split())
inputs={};checks=[]
def read(p):
    inputs[str(p.relative_to(ROOT))]=sha(p)
    return json.loads(p.read_text())
def check(name,ok,detail=None):checks.append(dict(name=name,passed=bool(ok),detail=detail))
def verify(name,hashes):
    bad=[p for p,h in hashes.items() if not (ROOT/p).is_file() or sha(ROOT/p)!=h]
    check(name,not bad,bad)
def displays(s):
    return re.findall(r'\\\[.*?\\\]|\\begin\{(?:equation\*?|align\*?|gather\*?|displaymath)\}.*?\\end\{(?:equation\*?|align\*?|gather\*?|displaymath)\}',s,re.S)
sources=lambda base:{p.relative_to(base):p for p in base.rglob('*') if p.is_file() and p.suffix in {'.tex','.bib','.lark'}}
old,new=sources(OLD),sources(NEW)
check('all prior authoring sources retained',old.keys()<=new.keys())
changed=[];delta=[];before=[];after=[];changed_displays=[]
for name in sorted(new):
    a=old[name].read_text() if name in old else '';b=new[name].read_text()
    inputs[str(new[name].relative_to(ROOT))]=sha(new[name])
    if a!=b:
        changed.append(str(name));delta.extend(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile=str(OLD/name),tofile=str(NEW/name)))
    if name.suffix=='.tex':
        before.append(a);after.append(b)
        if name in old and displays(a)!=displays(b):changed_displays.append(str(name))
(OUT/'manuscript-delta.diff').write_text(''.join(delta))
section='sections/apple-perimeter.tex';chapter='chapters/13-reference-company.tex'
check('only version/inclusion/new section changed',set(changed)=={'accounting-product-proposal.tex',chapter,section},changed)
check('chapter only appends inclusion',(NEW/chapter).read_text()==(OLD/chapter).read_text()+'\\input{sections/apple-perimeter}\n')
check('title only changes version',(NEW/'accounting-product-proposal.tex').read_text().replace('Version 2.15','Version 2.14')==(OLD/'accounting-product-proposal.tex').read_text())
check('other previous source bytes unchanged',all(new[n].read_bytes()==p.read_bytes() for n,p in old.items() if str(n) not in {'accounting-product-proposal.tex',chapter}))
a,b='\n'.join(before),'\n'.join(after)
check('all prior displays unchanged and no additions',not changed_displays and len(displays(a))==48 and displays(a)==displays(b))
ob,nb=(OLD/'references.bib').read_text(),(NEW/'references.bib').read_text()
keys=lambda s:re.findall(r'@\w+\s*\{\s*([^,\s]+)',s)
cites=lambda s:{k.strip() for g in re.findall(r'\\cite\w*\*?(?:\[[^\]]*\])*\{([^}]+)\}',s) for k in g.split(',')}
check('all 66 bibliography entries byte-preserved',ob==nb and len(keys(nb))==66)
check('citations preserved and resolved',cites(a)<=cites(b)<=set(keys(nb)))
labels=re.findall(r'\\label\{([^}]+)\}',b);refs=re.findall(r'\\(?:ref|eqref|pageref|autoref|cref)\{([^}]+)\}',b)
check('unique labels and resolved references',len(labels)==len(set(labels)) and set(refs)<=set(labels))
pdf=NEW/'accounting-product-proposal.pdf';doc=fitz.open(pdf);pdftext=norm(' '.join(p.get_text() for p in doc))
check('version and page count',len(doc)==155 and 'Version 2.15' in pdftext)
s=read(OUT/'source-claim-supplement.json');e=read(OUT/'source-checks.json')
check('79 passing current source checks',e['passed']==79 and e['failed']==0 and all(r['passed'] for r in e['checks']) and e['checker_sha256']==sha(OUT/'work_unit.py'))
verify('source inputs preserved',e['inputs'])
check('two notes / complete declared population',len(s['notes'])==2 and len(s['material_units'])==13 and len(s['dependencies'])==10 and len(s['entities'])==18 and len(s['queries'])==9)
page=doc[27];lines=[norm(t) for t in page.get_text().splitlines() if norm(t)]
flat=[value for r in s['entities'] for value in [r['name'],r['incorporation_jurisdiction']]]
start=lines.index(s['entities'][0]['name'])
check('all eighteen PDF entity pairs in original order',lines[start:start+36]==flat)
nd=norm((NEW/section).read_text())
check('complete omission quote reaches manuscript',s['omission_footnote'] in nd)
check('complete omission quote reaches PDF',s['omission_footnote'].replace('Company’s',"Company's") in pdftext)
check('positive scope and uncertainty explained',all(term in nd for term in ['wholly owned subsidiaries','immediate parent','share class','effective interval','Singapore','functional currency','tax residence','operative US GAAP']))
check('no invented entity identity or actual ownership path',all(term in nd for term in ['invented identity','hypothetical example','does not select either arrangement','general customer-location rule','without naming those subsidiaries']))
check('derivative prior reading is preserved as a dependency', 'already include full Note 4 readings' in next(u['remaining'] for u in s['material_units'] if u['id']=='annual.derivatives'))
warnings=[line for line in (NEW/'accounting-product-proposal.log').read_text().splitlines() if any(w in line for w in ['Warning','Overfull','Underfull','! '])]
check('clean final TeX log',not warnings,warnings)
check('clean bibliography log',not re.search(r'Warning--|error message|I couldn.t open',(NEW/'accounting-product-proposal.blg').read_text()))
build=read(OUT/'build-01/receipt.json')
check('successful build binds current PDF/log',build['exit_code']==0 and build['pdf_sha256']==sha(pdf) and build['log_sha256']==sha(OUT/'build-01/build.log'))
render=read(OUT/'render-manifest.json')
check('render binds final PDF/read scope',render['pdf_sha256']==sha(pdf) and render['body_pages']==list(range(26,32)))
verify('render images preserved',{r['path']:r['sha256'] for r in render['rendered_images']+[render['navigation_sheet']]})
sr=read(OUT/'source-render-receipt.json')
check('source render bindings current',sr['source_supplement_sha256']==sha(OUT/'source-claim-supplement.json') and sr['derived_html_sha256']==sha(ROOT/sr['derived_html']) and sr['derived_pdf_sha256']==sha(ROOT/sr['derived_pdf']))
verify('original source renders preserved',{r['path']:r['sha256'] for r in sr['rendered_images']})
# The source semantic repair did not change the inspected images.
arch=OUT/'source-attempt-02/source-render'
check('source reread images identical after residual-language repair',all(sha(OUT/'source-render'/p.relative_to(arch))==sha(p) for p in arch.rglob('*.png')))
author=OUT/'author-review.md';inputs[str(author.relative_to(ROOT))]=sha(author)
check('author review binds scope and pending acceptance',sha(pdf) in author.read_text() and 'independent_reader_pending' in author.read_text())
base=read(OUT/'baseline.json');verify('immediate baseline preserved',base['protected_hashes'])
check('immediate counts recomputed',len(base['protected_hashes'])==178 and base['prior_manifest_references']==176)
rel={r['historical_path']:r['preserved_path'] for r in base['pointer_relocations']}
prior_path=ROOT/base['prior_manifest'];prior=read(prior_path)
check('prior manifest/completion match',sha(prior_path)==base['prior_manifest_sha256']==read(prior_path.parent/'completion.json')['manifest_sha256'])
verify('prior live records resolve through preservation',{rel.get(p,p):h for p,h in prior['artifact_hashes'].items()})
for name in base['ancestor_counts']:
    verify(name+' protected baseline',read(ROOT/'data/accounting-master'/name/'baseline.json')['protected_hashes'])
history=read(ROOT/'data/accounting-master/direct-p19-20261007/recovery-entry-v1.json')
for key in base['history_counts']:verify(key,history[key])
p19=read(ROOT/'data/accounting-master/continuation-20261007/baseline-manifest.json');pr={x['historical_path']:x['preserved_path'] for x in p19['relocations']}
verify('P19 historical pointer relocation',{pr.get(p,p):h for p,h in p19['p19_historical_artifact_hashes'].items()})
ready=read(ROOT/'data/accounting-master/deliverables/P19/readiness.json')
check('five wider blockers remain',ready['status']=='not_ready' and set(ready['remaining_blockers'])=={'P15-'+x for x in ['E01','E05','E07','E08','E14']})
report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),checker_sha256=sha(Path(__file__)),inputs=inputs,
    pdf=dict(path=str(pdf.relative_to(ROOT)),sha256=sha(pdf),pages=len(doc)),changed_sources=changed,
    baseline_displays=len(displays(a)),candidate_displays=len(displays(b)),bibliography_keys=len(keys(nb)),
    checks=checks,passed=sum(r['passed'] for r in checks),failed=sum(not r['passed'] for r in checks),wall_seconds=time.monotonic()-timer)
(OUT/'candidate-checks.json').write_text(json.dumps(report,indent=2)+'\n')
(OUT/'render-review.json').write_text(json.dumps(dict(pdf_sha256=sha(pdf),render_manifest_sha256=sha(OUT/'render-manifest.json'),
    author_review_sha256=sha(author),continuous_read_pages=list(range(26,32)),navigation_pages=list(range(1,8)),
    independent_reader='pending',human_acceptance='pending'),indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['passed','failed','pdf','baseline_displays','candidate_displays','bibliography_keys']}))
if report['failed']:
    print(json.dumps([r for r in checks if not r['passed']]))
    raise SystemExit(1)
