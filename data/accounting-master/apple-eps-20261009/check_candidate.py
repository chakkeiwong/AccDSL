"""Check the final bounded EPS candidate and preserved prior evidence."""
from datetime import datetime, timezone
import difflib
import hashlib
import json
from pathlib import Path
import re
import time
import fitz

OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
OLD=ROOT/'docs/design/proposal/manuscript-tax-20261009'
NEW=ROOT/'docs/design/proposal/manuscript-eps-20261009'
START=time.monotonic()
if (OUT/'completion.json').exists():raise SystemExit('Closed unit')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks=[];inputs={}
def check(n,ok,detail=None):checks.append(dict(name=n,passed=bool(ok),detail=detail))
def read(p):inputs[str(p.relative_to(ROOT))]=sha(p);return json.loads(p.read_text())
def verify(n,hashes):
    bad=[p for p,h in hashes.items() if not (ROOT/p).exists() or sha(ROOT/p)!=h]
    check(n,not bad,bad)
def displays(s):return re.findall(r'\\\[.*?\\\]|\\begin\{(?:equation\*?|align\*?|gather\*?|displaymath)\}.*?\\end\{(?:equation\*?|align\*?|gather\*?|displaymath)\}',s,re.S)
source=lambda base:{p.relative_to(base):p for p in base.rglob('*') if p.is_file() and p.suffix in {'.tex','.bib','.lark','.png','.jpg','.svg'}}
old,new=source(OLD),source(NEW)
check('every prior manuscript source retained',old.keys()<=new.keys())
changed=[];delta=[];display_changes=[];before=[];after=[]
for n in sorted(new):
    a=old[n].read_text() if n in old else '';b=new[n].read_text()
    if a!=b:
        changed.append(str(n));delta+=list(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile=str(OLD/n) if n in old else '/dev/null',tofile=str(NEW/n)))
    if n.suffix=='.tex':
        before.append(a);after.append(b)
        if n in old and displays(a)!=displays(b):display_changes.append(str(n))
(OUT/'manuscript-delta.diff').write_text(''.join(delta))
newsection='sections/apple-eps-ownership.tex';chapter='chapters/14-financing-groups.tex'
check('bounded three-file source delta',set(changed)=={'accounting-product-proposal.tex',chapter,newsection},changed)
check('earlier chapter preserved around one inclusion',(NEW/chapter).read_text().replace('\\input{sections/apple-eps-ownership}\n\n','')==(OLD/chapter).read_text())
check('title changes only version',(NEW/'accounting-product-proposal.tex').read_text().replace('Version 2.11','Version 2.10')==(OLD/'accounting-product-proposal.tex').read_text())
check('grammar listing preserved',(NEW/'spec/core-0.lark').read_bytes()==(OLD/'spec/core-0.lark').read_bytes())
a,b='\n'.join(before),'\n'.join(after);nd=(NEW/newsection).read_text()
check('41 old displays retained and one timing equation added',not display_changes and len(displays(a))==41 and len(displays(b))==42 and len(displays(nd))==1,display_changes)
keys=lambda s:re.findall(r'@\w+\s*\{\s*([^,\s]+)',s)
ob,nb=(OLD/'references.bib').read_text(),(NEW/'references.bib').read_text()
check('all 66 bibliography entries preserved exactly',ob==nb and len(keys(nb))==66)
cites=lambda s:{k.strip() for g in re.findall(r'\\cite\w*\*?(?:\[[^\]]*\])*\{([^}]+)\}',s) for k in g.split(',')}
check('citations retained and resolved',cites(a)<=cites(b)<=set(keys(nb)))
labels=re.findall(r'\\label\{([^}]+)\}',b);refs=re.findall(r'\\(?:ref|eqref|pageref|autoref|cref)\{([^}]+)\}',b)
check('unique labels and resolved references',len(labels)==len(set(labels)) and set(refs)<=set(labels))
check('scope qualifications present',all(s in ' '.join(nd.split()) for s in ['deliberately simplified','first-quarter fiscal 2024','no probability','not a complete reconstruction','different remaining recognition periods','At the displayed centres','differences remain unallocated']))
pdf=NEW/'accounting-product-proposal.pdf';doc=fitz.open(pdf)
text=' '.join(' '.join(p.get_text().split()) for p in doc);text=re.sub(r'(?<=\d),\s+(?=\d)',',',text)
check('key numerical consequences reach final PDF',all(s in text for s in ['Version 2.11','6.109','6.201','15,343,783','15,509,763','15,469,465,000','15,535,562,000','99,790','23,735','95,846','94,949','23,606','3,286']))
log=(NEW/'accounting-product-proposal.log').read_text()
warnings=[s for s in log.splitlines() if any(w in s for w in ['Warning','Overfull','Underfull','! '])]
check('clean final LuaLaTeX log','LuaHBTeX' in log and not warnings,warnings)
check('clean bibliography log',not re.search(r'Warning--|error message|I couldn.t open',(NEW/'accounting-product-proposal.blg').read_text()))
e=read(OUT/'evidence-checks.json')
check('final source/arithmetic checks pass',e['failed']==0 and e['passed']==167 and e['checker_sha256']==sha(OUT/'prepare_evidence.py'))
verify('source inputs current',e['inputs']);verify('source outputs current',e['output_hashes'])
c=read(OUT/'source-claim-supplement.json')
check('bounded coverage retained',len(c['notes'])==6 and len(c['units'])==16 and len(c['dependencies'])==15 and c['coverage']['note_numeric_cells']==89 and len(c['queries'])==10 and c['coverage']['whole_apple_package']=='open')
calc=read(OUT/'calculations.json');w=calc['quantity_model']['witnesses']
# Re-read the authored TeX table against independent checked event data.
table_rows=re.findall(r'^([^\n]+?) & \$([+-][\d{},]+)\\;\((\d+)\)\$ & \$([+-][\d{},]+)\\;\((\d+)\)\$ \\\\',nd,re.M)
parsed=[[],[]]
for _,q1,d1,q2,d2 in table_rows:
    for i,q,d in [(0,q1,d1),(1,q2,d2)]:parsed[i].append((int(d),int(re.sub(r'[{},]','',q))*1000))
check('manuscript event tables match computed witnesses',len(table_rows)==8 and all(sorted(parsed[i])==sorted((r['elapsed_days'],r['change_shares']) for r in w[i]['events']) for i in range(2)))
render=read(OUT/'render-manifest.json');review=read(OUT/'render-review.json')
check('render bound to final PDF',render['pdf_sha256_before']==render['pdf_sha256_after']==sha(pdf))
verify('render image hashes current',{r['path']:r['sha256'] for g in ['rendered_pages','contact_sheets'] for r in render[g].values()})
check('actual author review bound',review['render_manifest_sha256']==sha(OUT/'render-manifest.json') and review['author_review_sha256']==sha(OUT/'author-review.md') and review['page_numbers']==render['page_numbers'] and review['continuous_read_pages']==list(range(82,88)))
check('independent/human acceptance pending',review['independent_reader']==review['human_acceptance']=='pending')
sr=read(OUT/'source-render-receipt.json')
check('derived source render text and inputs current',all(sha(Path(r['source_html']))==r['sha256'] and sha(Path(r['pdf']))==r['pdf_sha256'] and r['text_preserved_after_namespace_unwrap'] for r in sr['records']))
verify('original and derived source images preserved',{r['path']:r['sha256'] for r in sr['rendered_images']})
build=read(OUT/'build-receipt.json')
check('successful build receipt binds PDF and log',build['exit_code']==0 and build['pdf_sha256']==sha(pdf) and build['log_sha256']==sha(OUT/'build.log'))
baseline=read(OUT/'baseline.json');verify('baseline candidate and closed-unit files preserved',baseline['protected_hashes'])
rel={r['historical_path']:r['preserved_path'] for r in baseline['pointer_relocations']}
previous=read(ROOT/baseline['prior_manifest'])
verify('preceding manifest resolves preserved live pointers',{rel.get(n,n):h for n,h in previous['artifact_hashes'].items()})
history=read(ROOT/'data/accounting-master/direct-p19-20261007/recovery-entry-v1.json');counts={}
for k in ['protected_hashes','upstream_reference_hashes','controller_hashes']:
    verify('historical '+k,history[k]);counts[k]=len(history[k])
p19=read(ROOT/'data/accounting-master/continuation-20261007/baseline-manifest.json');rel={r['historical_path']:r['preserved_path'] for r in p19['relocations']}
verify('P19 historical hashes resolved',{rel.get(n,n):h for n,h in p19['p19_historical_artifact_hashes'].items()})
r=read(ROOT/'data/accounting-master/deliverables/P19/readiness.json')
check('full readiness remains negative',r['status']=='not_ready' and not r['ready'] and set(r['remaining_blockers'])=={'P15-'+x for x in ['E01','E05','E07','E08','E14']})
report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),checker_sha256=sha(Path(__file__)),inputs=inputs,pdf=dict(path=str(pdf.relative_to(ROOT)),sha256=sha(pdf),pages=len(doc)),changed_sources=changed,baseline_displays=41,candidate_displays=42,bibliography_keys=66,preservation_counts=counts,checks=checks,passed=sum(c['passed'] for c in checks),failed=sum(not c['passed'] for c in checks),wall_seconds=time.monotonic()-START)
(OUT/'candidate-checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['passed','failed','pdf','preservation_counts']}))
if report['failed']:
    print(json.dumps([c for c in checks if not c['passed']]))
    raise SystemExit(1)
