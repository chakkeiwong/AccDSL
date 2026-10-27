"""Preservation and candidate checks; freeze only after four live records agree."""
from datetime import datetime, timezone
import difflib
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import time

import fitz
import work_unit as w

OUT,ROOT,OLD,NEW = w.OUT,w.ROOT,w.OLD,w.NEW
sha,read,norm,rel = w.sha,w.read,w.norm,w.rel
assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1'
assert not (OUT/'completion.json').exists(),'Preserve frozen outputs'
action=sys.argv[1];timer=time.monotonic()
inputs={};checks=[]
def check(n,ok,detail=None):checks.append(dict(id=n,passed=bool(ok),detail=detail))
def load(p):inputs[rel(p)]=sha(p);return read(p)
def verify(n,hashes):
    bad=[p for p,h in hashes.items() if not (ROOT/p).is_file() or sha(ROOT/p)!=h]
    check(n,not bad,bad)
displays=lambda s:re.findall(r'\\\[.*?\\\]|\\begin\{(?:equation\*?|align\*?|gather\*?|displaymath)\}.*?\\end\{(?:equation\*?|align\*?|gather\*?|displaymath)\}',s,re.S)
sources=lambda b:{str(p.relative_to(b)):p for p in b.rglob('*') if p.is_file() and p.suffix in {'.tex','.bib','.lark'}}
pdf=NEW/'accounting-product-proposal.pdf';doc=fitz.open(pdf)
pdfrow=dict(path=rel(pdf),sha256=sha(pdf),pages=len(doc))

if action=='check':
    assert not (OUT/'candidate-checks.json').exists()
    old,new=sources(OLD),sources(NEW);changed=[];deltas=[];before=[];after=[]
    check('all prior authoring sources retained',old.keys()<=new.keys())
    for n,p in new.items():
        a=old[n].read_text() if n in old else '';b=p.read_text();inputs[rel(p)]=sha(p)
        if a!=b:
            changed.append(n);deltas.extend(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile=str(OLD/n),tofile=str(NEW/n)))
        if p.suffix=='.tex':before.append(a);after.append(b)
    (OUT/'manuscript-delta.diff').write_text(''.join(deltas))
    changed_set={'accounting-product-proposal.tex','chapters/13-reference-company.tex','sections/apple-legal.tex'}
    check('only title inclusion and legal section changed',set(changed)==changed_set,changed)
    check('previous body bytes retained',all(p.read_bytes()==new[n].read_bytes() for n,p in old.items() if n not in changed_set))
    check('chapter only appends legal inclusion',(NEW/'chapters/13-reference-company.tex').read_text()==(OLD/'chapters/13-reference-company.tex').read_text()+'\\input{sections/apple-legal}\n')
    title=(NEW/'accounting-product-proposal.tex').read_text()
    check('title only changes version/date',title.replace('Version 2.16','Version 2.15').replace('10 October 2026','9 October 2026')==(OLD/'accounting-product-proposal.tex').read_text())
    a,b='\n'.join(before),'\n'.join(after)
    # Compare display multisets: source tree traversal order is not an equation order contract.
    check('48 prior displays unchanged no new equations',len(displays(a))==len(displays(b))==48 and sorted(displays(a))==sorted(displays(b)))
    bib=(NEW/'references.bib').read_text();keys=re.findall(r'@\w+\s*\{\s*([^,\s]+)',bib)
    check('66 bibliography entries byte-preserved',bib==(OLD/'references.bib').read_text() and len(keys)==66)
    cites=lambda s:{k.strip() for g in re.findall(r'\\cite\w*\*?(?:\[[^\]]*\])*\{([^}]+)\}',s) for k in g.split(',')}
    check('citations retained and resolved',cites(a)<=cites(b)<=set(keys))
    labels=re.findall(r'\\label\{([^}]+)\}',b);refs=re.findall(r'\\(?:ref|eqref|pageref|autoref|cref)\{([^}]+)\}',b)
    check('unique labels and resolved references',len(labels)==len(set(labels)) and set(refs)<=set(labels))
    check('version and pages',len(doc)==157 and 'Version 2.16' in doc[0].get_text())
    ptext=norm(' '.join(p.get_text() for p in doc));s=load(OUT/'source-claim-supplement.json');sc=load(OUT/'source-checks.json')
    check('current passing source checks',sc['failed']==0 and sc['passed']==100 and all(c['passed'] for c in sc['checks']) and sc['checker_sha256']==sha(OUT/'work_unit.py'))
    verify('original source inputs preserved',sc['inputs'])
    check('declared complete source population',len(s['spans'])==10 and len(s['matters'])==8 and sum(len(m['assertions']) for m in s['matters'])==39 and len(s['queries'])==8)
    check('no probabilities or matter-level amounts invented',s['no_probability'] and s['no_numeric_fine_calculation'] and all(c['probability'] is None and c['matter_accrual'] is None and c['matter_payment'] is None for m in s['matters'] for c in m['assertions']))
    sentence=norm(s['spans']['annual.contingency']['quote']).split('In the opinion',1)[1]
    check('complete management assessment in PDF','In the opinion'+sentence.rstrip('.') in ptext)
    for n,terms in {
        'recognition boundary':['probable that a loss has been incurred','reasonably estimable','operative US GAAP'],
        'DMA conditions':['preliminary findings','up to 10%','annual worldwide net sales','unless a stay','not a fine already imposed'],
        'DOJ relief':['DOJ seeks equitable relief','monetary damages and other nonmonetary relief'],
        'Epic scope and procedure':['U.S. storefront of the iOS and iPadOS','reported as pending','30 September 2024'],
        'Google proposed remedies':['DOJ proposed remedies','up to ten years','not reported here as imposed'],
        'settlement date separation':['fourth quarter of fiscal 2024','first quarter of fiscal 2025'],
        'tax duplicate and no calculation':['not be counted again as a DMA loss','without assigning probabilities or producing numerical journals']}.items():
        check(n,all(t in ptext for t in terms))
    warnings=[x for x in (NEW/'accounting-product-proposal.log').read_text().splitlines() if any(t in x for t in ['Warning','Overfull','Underfull','! '])]
    check('clean final TeX log',not warnings,warnings)
    check('clean bibliography log',not re.search(r'Warning--|error message|I couldn.t open',(NEW/'accounting-product-proposal.blg').read_text()))
    build=load(OUT/'build-01/receipt.json')
    check('build binds current PDF/log',build['exit_code']==0 and build['pdf_sha256']==sha(pdf) and build['log_sha256']==sha(OUT/'build-01/build.log'))
    r=load(OUT/'render-manifest.json');verify('final rendered images preserved',{x['path']:x['sha256'] for x in r['images']+[r['navigation_sheet']]})
    check('render binds final PDF and five-page read',r['pdf_sha256']==sha(pdf) and r['body_pages']==[29,30,31,32,33])
    sr=load(OUT/'source-render-receipt.json');verify('source images preserved',{x['path']:x['sha256'] for x in sr['images']})
    check('interim reflow bindings',sha(ROOT/sr['derived_html'])==sr['derived_html_sha256'] and sha(ROOT/sr['derived_pdf'])==sr['derived_pdf_sha256'])
    author=OUT/'author-review.md';inputs[rel(author)]=sha(author)
    check('author review bound with pending acceptance',sha(pdf) in author.read_text() and 'independent_reader_pending' in author.read_text())
    base=load(OUT/'baseline.json');verify('immediate frozen baseline preserved',base['protected_hashes'])
    prior=load(w.PRIOR);pr={x['historical_path']:x['preserved_path'] for x in base['pointer_relocations']}
    check('prior manifest completion match',sha(w.PRIOR)==base['prior_manifest_sha256']==load(w.PRIOR.parent/'completion.json')['manifest_sha256'])
    verify('prior live record hashes relocated',{pr.get(n,n):h for n,h in prior['artifact_hashes'].items()})
    check('ancestor hashes intact',w.ancestry()==base['ancestor_counts'])
    ready=load(ROOT/'data/accounting-master/deliverables/P19/readiness.json')
    check('five wider blockers unchanged',ready['status']=='not_ready' and set(ready['remaining_blockers'])=={'P15-'+x for x in ['E01','E05','E07','E08','E14']})
    report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),checker_sha256=sha(Path(__file__)),inputs=inputs,pdf=pdfrow,
        checks=checks,passed=sum(c['passed'] for c in checks),failed=sum(not c['passed'] for c in checks),
        changed_sources=changed,baseline_displays=48,candidate_displays=48,bibliography_keys=66,wall_seconds=time.monotonic()-timer)
    w.save('candidate-checks.json',report)
    print(json.dumps(dict(passed=report['passed'],failed=report['failed'],pdf=pdfrow)))
    assert not report['failed'],[c for c in checks if not c['passed']]
elif action=='freeze':
    c=load(OUT/'candidate-checks.json');sc=load(OUT/'source-checks.json');base=load(OUT/'baseline.json')
    assert c['failed']==sc['failed']==0 and c['pdf']==pdfrow
    assert c['checker_sha256']==sha(Path(__file__)) and sc['checker_sha256']==sha(OUT/'work_unit.py')
    w.verify(c['inputs']);w.verify(sc['inputs']);w.verify(base['protected_hashes']);w.ancestry()
    pr={x['historical_path']:x['preserved_path'] for x in base['pointer_relocations']}
    w.verify({pr.get(n,n):h for n,h in read(w.PRIOR)['artifact_hashes'].items()})
    pointers={}
    for n in w.POINTERS:
        s=(ROOT/n).read_text()
        assert 'Version 2.16' in s and sha(pdf) in s and 'not_ready' in s,n
        assert 'Recent Accounting Pronouncements' in s,n
        assert all(line==line.rstrip(' \t') for line in s.splitlines()),n
        pointers[n]=sha(ROOT/n)
    road=(ROOT/w.POINTERS[3]).read_text();oldroad=(ROOT/pr[w.POINTERS[3]]).read_text()
    gaps=lambda s:[x for x in s.splitlines() if re.match(r'^\| G\d+ ',x)]
    assert len(gaps(road))==18 and gaps(road)==gaps(oldroad)
    for label,target in [('Latest substantive result',OUT/'result.md'),('Current manuscript',pdf)]:
        lines=[x for x in road.splitlines() if x.startswith(label+': ')];assert len(lines)==1
        m=re.search(r'\]\(([^)]+)\)',lines[0]);assert m
        assert (ROOT/'docs/plans'/m.group(1)).resolve()==target.resolve()
    assert sha(pdf) in (OUT/'result.md').read_text()
    now=datetime.now(timezone.utc)
    w.save('closeout-checks.json',dict(recorded_at=now.isoformat(),passed=True,pointers=pointers,
        baseline_files=len(base['protected_hashes']),prior_manifest_references=base['prior_manifest_references'],
        ancestor_counts=base['ancestor_counts'],all_eighteen_gap_rows_unchanged=True,full_readiness='not_ready'))
    artifacts={rel(p):sha(p) for directory in [OUT,NEW] for p in directory.rglob('*') if p.is_file()
               and p.name not in {'run-manifest.json','completion.json'} and '__pycache__' not in p.parts}
    artifacts[rel(w.PLAN)]=sha(w.PLAN);artifacts.update(pointers)
    commands=[json.loads(x) for x in (OUT/'commands.jsonl').read_text().splitlines()]
    commands.extend([dict(command='CUDA_VISIBLE_DEVICES=-1 python3 '+rel(Path(__file__))+' check',exit_code=0,wall_seconds=c['wall_seconds']),
                     dict(command='CUDA_VISIBLE_DEVICES=-1 python3 '+rel(Path(__file__))+' freeze',exit_code=0)])
    manifest=dict(schema_version='accdsl.bounded-unit-manifest.v1',recorded_at=now.isoformat(),unit='Apple legal proceedings E01/C03/C08',
        git_commit=base['git_commit'],git_branch=subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip(),
        plan=rel(w.PLAN),result=rel(OUT/'result.md'),pdf=pdfrow,environment=dict(python=sys.version,platform=platform.platform(),
            conda_env='N/A: system python3',CUDA_VISIBLE_DEVICES='-1',cpu_gpu_status='CPU only; GPU devices intentionally hidden',pymupdf=fitz.VersionBind),
        data_version='Pinned Apple FY2024 PDF/FY2025 Q1 HTML, exact source spans in source-claim-supplement.json',
        random_seeds='N/A: deterministic documentary checks',commands=commands,
        wall_seconds=(now-datetime.fromisoformat(base['recorded_at'])).total_seconds(),output_paths=[rel(OUT),rel(NEW)],
        network_requests=0,full_readiness='not_ready',independent_reader='pending',human_acceptance='pending',artifact_hashes=artifacts,
        prior_manifest=base['prior_manifest'],prior_manifest_sha256=base['prior_manifest_sha256'],pointer_relocations=base['pointer_relocations'])
    w.save('run-manifest.json',manifest);w.verify(artifacts)
    completion=dict(recorded_at=now.isoformat(),status='bounded_unit_complete',manifest_sha256=sha(OUT/'run-manifest.json'),pdf=pdfrow,
        source_checks=sc['passed'],candidate_checks=c['passed'],manifest_bound_files=len(artifacts),full_readiness='not_ready',
        next_work='Complete annual/interim Recent Accounting Pronouncements and dated transition/query meaning')
    w.save('completion.json',completion);print(json.dumps(completion))
else:raise SystemExit('check or freeze required')
