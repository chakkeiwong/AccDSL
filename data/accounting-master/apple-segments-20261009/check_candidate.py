"""Check the bounded segment manuscript, evidence links and frozen baseline."""
from datetime import datetime, timezone
import difflib
import hashlib
import json
from pathlib import Path
import re
import time

import fitz

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
OLD=ROOT/'docs/design/proposal/manuscript-liquidity-20261009'
NEW=ROOT/'docs/design/proposal/manuscript-segments-20261009'
if (OUT/'candidate-checks.json').exists():raise SystemExit('Preserve previous candidate checks')
start=time.monotonic()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inputs,checks={},[]


def read(p):
    inputs[str(p.relative_to(ROOT))]=sha(p)
    return json.loads(p.read_text())


def check(name,ok,detail=None):
    checks.append(dict(name=name,passed=bool(ok),detail=detail))


def verify(name,hashes):
    bad=[p for p,h in hashes.items() if not (ROOT/p).is_file() or sha(ROOT/p)!=h]
    check(name,not bad,bad)


def displays(s):
    return re.findall(r'\\\[.*?\\\]|\\begin\{(?:equation\*?|align\*?|gather\*?|displaymath)\}.*?\\end\{(?:equation\*?|align\*?|gather\*?|displaymath)\}',s,re.S)


sources=lambda base:{p.relative_to(base):p for p in base.rglob('*') if p.is_file() and p.suffix in {'.tex','.bib','.lark'}}
old,new=sources(OLD),sources(NEW)
check('every prior manuscript source retained',old.keys()<=new.keys())
changed,delta,before,after,changed_displays=[],[],[],[],[]
for name in sorted(new):
    a=old[name].read_text() if name in old else '';b=new[name].read_text()
    if a!=b:
        changed.append(str(name));delta.extend(difflib.unified_diff(a.splitlines(True),b.splitlines(True),
            fromfile=str(OLD/name) if name in old else '/dev/null',tofile=str(NEW/name)))
    if name.suffix=='.tex':
        before.append(a);after.append(b)
        if name in old and displays(a)!=displays(b):changed_displays.append(str(name))
(OUT/'manuscript-delta.diff').write_text(''.join(delta))
section='sections/apple-segments.tex';chapter='chapters/13-reference-company.tex'
check('only bounded three-file source delta',set(changed)=={'accounting-product-proposal.tex',chapter,section},changed)
check('prior chapter unchanged except appended inclusion',(NEW/chapter).read_text()==(OLD/chapter).read_text()+'\\input{sections/apple-segments}\n')
check('title changes only version',(NEW/'accounting-product-proposal.tex').read_text().replace('Version 2.14','Version 2.13')==(OLD/'accounting-product-proposal.tex').read_text())
a,b='\n'.join(before),'\n'.join(after)
check('46 previous displays retained and two added',not changed_displays and len(displays(a))==46 and len(displays(b))==48,dict(old=len(displays(a)),new=len(displays(b)),changed=changed_displays))
ob,nb=(OLD/'references.bib').read_text(),(NEW/'references.bib').read_text()
keys=lambda s:re.findall(r'@\w+\s*\{\s*([^,\s]+)',s)
cites=lambda s:{k.strip() for g in re.findall(r'\\cite\w*\*?(?:\[[^\]]*\])*\{([^}]+)\}',s) for k in g.split(',')}
check('66 bibliography entries retained exactly',ob==nb and len(keys(nb))==66)
check('citations retained and resolved',cites(a)<=cites(b)<=set(keys(nb)))
labels=re.findall(r'\\label\{([^}]+)\}',b);refs=re.findall(r'\\(?:ref|eqref|pageref|autoref|cref)\{([^}]+)\}',b)
check('unique labels and resolved references',len(labels)==len(set(labels)) and set(refs)<=set(labels))
check('earlier source files unchanged except expected insertion',all(new[n].read_bytes()==p.read_bytes() for n,p in old.items() if str(n) not in {'accounting-product-proposal.tex',chapter}))
nd=' '.join((NEW/section).read_text().split())
check('source and assumption limits preserved',all(s in nd for s in [
    'general attribution rule','four other product and service rows sum to 189,852',
    'mathematical witness constructions, not issuer allocations','no disclosed tolerance',
    'not an estimated shock','dated issuer statement','not a reconstructed Apple segment']))
pdf=NEW/'accounting-product-proposal.pdf';doc=fitz.open(pdf)
pdftext=' '.join(' '.join(p.get_text().split()) for p in doc)
pdftext=re.sub(r'(?<=\d),\s+(?=\d)',',',pdftext)
check('candidate version and 152 pages',len(doc)==152 and 'Version 2.14' in pdftext)
check('key results reach PDF',all(s in pdftext for s in ['38,828','22,082','21,082','24,849','35,664','4,797','5,219','189,852','122,900','324,083','3,600','3,800','ASU 2023-07']))
warnings=[s for s in (NEW/'accounting-product-proposal.log').read_text().splitlines() if any(w in s for w in ['Warning','Overfull','Underfull','! '])]
check('final TeX log clean',not warnings,warnings)
check('bibliography log clean',not re.search(r'Warning--|error message|I couldn.t open',(NEW/'accounting-product-proposal.blg').read_text()))
e=read(OUT/'evidence-checks.json');t=read(OUT/'table-checks.json')
check('83 source/meaning checks pass',e['passed']==83 and e['failed']==0 and e['checker_sha256']==sha(OUT/'prepare_evidence.py'))
check('107 positional/witness checks pass',t['passed']==107 and t['failed']==0 and t['checker_sha256']==sha(OUT/'check_tables.py'))
verify('source inputs retained',e['inputs']);verify('evidence outputs retained',e['output_hashes'])
check('table checks bind current source and calculation records',t['source_supplement_sha256']==sha(OUT/'source-claim-supplement.json') and t['calculations_sha256']==sha(OUT/'calculations.json'))
supp=read(OUT/'source-claim-supplement.json')
check('declared bounded source population retained',len(supp['notes'])==2 and len(supp['material_units'])==7 and len(supp['dependencies'])==14 and len(supp['queries'])==7 and t['note_numeric_cells']==90 and t['dependency_numeric_cells']==47)
check('all displayed country table values source-matched',all(f'{v:,}' in (NEW/section).read_text() for v in [142196,66952,181887,391035,35664,4797,5219,45680]))
render=read(OUT/'render-manifest.json')
check('final renders bound to current PDF',render['pdf_sha256_before']==render['pdf_sha256_after']==sha(pdf) and render['script_sha256']==sha(OUT/'render_candidate.py'))
verify('rendered files retained',{r['path']:r['sha256'] for group in ['rendered_pages','contact_sheets'] for r in render[group].values()})
prior_render_path=OUT/'build-02/candidate-before-attribution-repair/render-manifest.json'
pr=read(prior_render_path)
same=[n for n in render['page_numbers'] if render['rendered_pages'][str(n)]['sha256']==pr['rendered_pages'][str(n)]['sha256']]
check('previously inspected navigation/adjacent pages unchanged',all(n in same for n in list(range(1,8))+[24,28]),same)
author=OUT/'author-review.md';inputs[str(author.relative_to(ROOT))]=sha(author)
check('author review binds final PDF and scoped pending acceptance',sha(pdf) in author.read_text() and 'independent_reader_pending' in author.read_text())
sr=read(OUT/'source-render-receipt.json');archived_t=OUT/'table-attempt-02/table-checks.json'
check('source render uses preserved passing table snapshot',sr['table_checks_sha256']==sha(archived_t) and read(archived_t)['source_rows']==t['source_rows'])
check('source render source bindings',sr['source_supplement_sha256']==sha(OUT/'source-claim-supplement.json') and sr['script_sha256']==sha(OUT/'render_sources.py') and
      sr['derived_html_sha256']==sha(ROOT/sr['derived_html']) and sr['derived_pdf_sha256']==sha(ROOT/sr['derived_pdf']))
verify('source renders preserved',{r['path']:r['sha256'] for r in sr['rendered_images']})
build=read(OUT/'build-03/receipt.json')
check('final successful build binds PDF and log',build['exit_code']==0 and build['pdf_sha256']==sha(pdf) and build['log_sha256']==sha(OUT/'build-03/build.log') and build['script_sha256']==sha(OUT/'build_candidate.py'))
base=read(OUT/'baseline.json');verify('252 immediate baseline files retained',base['protected_hashes'])
check('baseline count recomputed',len(base['protected_hashes'])==252 and base['prior_manifest_references']==249)
rel={r['historical_path']:r['preserved_path'] for r in base['pointer_relocations']}
pm=read(ROOT/base['prior_manifest'])
verify('prior 249 manifest references resolve',{rel.get(p,p):h for p,h in pm['artifact_hashes'].items()})
history=read(ROOT/'data/accounting-master/direct-p19-20261007/recovery-entry-v1.json')
counts={}
for k in ['protected_hashes','upstream_reference_hashes','controller_hashes']:
    verify('historical '+k,history[k]);counts[k]=len(history[k])
p19=read(ROOT/'data/accounting-master/continuation-20261007/baseline-manifest.json')
r={x['historical_path']:x['preserved_path'] for x in p19['relocations']}
verify('P19 historical relocations resolve',{r.get(p,p):h for p,h in p19['p19_historical_artifact_hashes'].items()})
ready=read(ROOT/'data/accounting-master/deliverables/P19/readiness.json')
check('five wider blockers remain',ready['status']=='not_ready' and not ready['ready'] and set(ready['remaining_blockers'])=={'P15-'+s for s in ['E01','E05','E07','E08','E14']})
review=dict(recorded_at=datetime.now(timezone.utc).isoformat(),render_manifest_sha256=sha(OUT/'render-manifest.json'),
    author_review_sha256=sha(author),pdf_sha256=sha(pdf),continuous_read_pages=list(range(24,29)),
    final_reread_pages=[25,26,27],unchanged_inspected_pages=same,navigation_inspection_pages=list(range(1,8)),
    independent_reader='pending',human_acceptance='pending')
(OUT/'render-review.json').write_text(json.dumps(review,indent=2)+'\n')
report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),checker_sha256=sha(Path(__file__)),inputs=inputs,
    pdf=dict(path=str(pdf.relative_to(ROOT)),sha256=sha(pdf),pages=len(doc)),changed_sources=changed,
    baseline_displays=46,candidate_displays=48,bibliography_keys=66,preservation_counts=counts,
    checks=checks,passed=sum(c['passed'] for c in checks),failed=sum(not c['passed'] for c in checks),wall_seconds=time.monotonic()-start)
(OUT/'candidate-checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['passed','failed','pdf','preservation_counts']}))
if report['failed']:
    print(json.dumps([c for c in checks if not c['passed']]))
    raise SystemExit(1)
