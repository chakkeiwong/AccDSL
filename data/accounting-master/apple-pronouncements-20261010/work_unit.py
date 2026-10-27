"""Bounded disclosure-transition reading with preserved documentary evidence."""
from datetime import datetime, timezone
from pathlib import Path
import difflib
import hashlib
import importlib.util
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time

import fitz
from bs4 import BeautifulSoup

sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
OLD=ROOT/'docs/design/proposal/manuscript-legal-20261010'
NEW=ROOT/'docs/design/proposal/manuscript-pronouncements-20261010'
PRIOR=ROOT/'data/accounting-master/apple-legal-20261010/run-manifest.json'
PLAN=ROOT/'docs/plans/accounting-apple-pronouncements-20261010.md'
helper=ROOT/'data/accounting-master/apple-legal-20261010/work_unit.py'
spec=importlib.util.spec_from_file_location('prior_document_helpers',helper);w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)
w.OUT,w.OLD,w.NEW,w.PRIOR,w.PLAN=OUT,OLD,NEW,PRIOR,PLAN
sha,read,norm,rel,save,verify=w.sha,w.read,w.norm,w.rel,w.save,w.verify
SOURCE_SPEC=[
 ('annual.tax','annual.pronouncements','Income Taxes','Segment Reporting','ASU 2023-09',2026,'prospective',
  'Rate reconciliation and threshold-qualified items; tax paid by federal/state/foreign and significant jurisdictions. Threshold value absent.'),
 ('annual.segment','annual.pronouncements','Segment Reporting',None,'ASU 2023-07',2025,'retrospective',
  'Significant segment expenses regularly provided to CODM, CODM title/position and use of profit/loss. Prior segment-unit dependency.'),
 ('interim.expense','interim.pronouncements','Disaggregation of Income Statement Expenses','Income Taxes','ASU 2024-03',2028,'prospective',
  'Purchases of inventory, employee compensation, depreciation, intangible amortization as applicable in certain captions; qualitative remaining amounts and selling-expense amount/definition. January 2025 ASU 2025-01 clarification is reported after period-end.'),
 ('interim.tax','interim.pronouncements','Income Taxes','Segment Reporting','ASU 2023-09',2026,'prospective',
  'Same reported tax-disclosure scope and plan; amounts and threshold not supplied.'),
 ('interim.segment','interim.pronouncements','Segment Reporting',None,'ASU 2023-07',2025,'retrospective',
  'Same reported segment-disclosure scope and plan; actual later recast figures not supplied.'),
 ('annual.estimates','annual.estimates','Critical Accounting Estimates','Uncertain Tax Positions',None,None,None,
  'Management judgment/assumptions/estimates, Note 1 reference, historical experience and other assumptions for carrying values; no numerical model supplied.'),
 ('annual.uncertain_tax','annual.estimates','Uncertain Tax Positions','Legal and Other Contingencies',None,None,None,
  'Complex tax/GAAP judgment, belief reserves reasonable without assured outcome, adjustments as facts change; tax unit remains dependency.'),
 ('annual.legal','annual.estimates','Legal and Other Contingencies',None,None,None,None,
  'Probable incurred loss and reasonable estimability; significant judgment and outcome risk. Completed legal dependency.'),
 ('interim.estimates','interim.estimates','Critical Accounting Estimates',None,None,None,None,
  'Judgment/assumptions/estimates; interim and annual Note 1 incorporation; no material changes to critical estimates, not numerical equality.')]

def baseline():
    p=read(PRIOR);assert sha(PRIOR)==read(PRIOR.parent/'completion.json')['manifest_sha256'];verify(p['artifact_hashes'])
    assert p['pdf']['pages']==157 and p['full_readiness']=='not_ready'
    protected={rel(f):sha(f) for base in [PRIOR.parent,OLD] for f in base.rglob('*') if f.is_file() and '__pycache__' not in f.parts}
    protected[rel(ROOT/'docs/plans/accounting-apple-legal-20261010.md')]=sha(ROOT/'docs/plans/accounting-apple-legal-20261010.md')
    reloc=[]
    for n in w.POINTERS:
        f=OUT/'pointers-before'/n;f.parent.mkdir(parents=True,exist_ok=True);assert not f.exists();shutil.copy2(ROOT/n,f)
        reloc.append(dict(historical_path=n,preserved_path=rel(f),sha256=sha(f)))
    verify(read(PRIOR.parent/'baseline.json')['protected_hashes'])
    save('baseline.json',dict(recorded_at=datetime.now(timezone.utc).isoformat(),git_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        prior_manifest=rel(PRIOR),prior_manifest_sha256=sha(PRIOR),prior_manifest_references=len(p['artifact_hashes']),protected_hashes=protected,
        pointer_relocations=reloc,ancestor_counts=w.ancestry(),baseline_pdf=p['pdf'],baseline_pages=w.render(OLD/'accounting-product-proposal.pdf',[31,32,33],OUT/'baseline-render')))
    print(json.dumps(dict(protected_files=len(protected),prior_references=len(p['artifact_hashes']))))

def sources():
    ss=read(w.SUPP)['sources'];inputs={rel(w.SUPP):sha(w.SUPP),rel(helper):sha(helper)};texts={};spans={};checks=[];units=[]
    def check(n,ok):checks.append(dict(id=n,passed=bool(ok)))
    for k in ['annual','interim']:
        for kind in ['original','extraction']:
            f=ROOT/ss[k][kind+'_path'];assert sha(f)==ss[k][kind+'_sha256'];inputs[rel(f)]=sha(f)
        texts[k]=(ROOT/ss[k]['extraction_path']).read_text()
    pdf=fitz.open(ROOT/ss['annual']['original_path']);original={'annual':norm(' '.join(p.get_text() for p in pdf)),
        'interim':norm(BeautifulSoup((ROOT/ss['interim']['original_path']).read_text(),'html.parser').get_text(' ',strip=True))}
    for k in ['annual','interim']:
        t=texts[k];a=t.index('Recent Accounting Pronouncements');b=t.index('Critical Accounting Estimates',a)
        end=t.index('Item 7A.' if k=='annual' else 'Item 3.',b)
        for name,x,y in [('pronouncements',a,b),('estimates',b,end)]:
            q=t[x:y].rstrip()
            if k=='annual' and name=='estimates':q=q[:q.index('Apple Inc. | 2024 Form 10-K | 26')].rstrip()
            row=dict(source_id=k,start=x,end=x+len(q),offset_unit='Unicode code points',quote=q,span_sha256=hashlib.sha256(q.encode()).hexdigest(),**ss[k])
            f=OUT/'sources'/(k+'.'+name+'.txt');f.parent.mkdir(exist_ok=True);f.write_text(q+'\n');row['retained_span']=rel(f);spans[k+'.'+name]=row
            check(k+'.'+name+' exact extraction',t[x:x+len(q)]==q);check(k+'.'+name+' original text',norm(q) in original[k])
    for ident,parent,opening,ending,asu,year,method,meaning in SOURCE_SPEC:
        s=spans[parent];q=s['quote'];a=q.index(opening);b=q.index(ending,a+len(opening)) if ending else len(q);part=q[a:b].rstrip();start=s['start']+a
        row=dict(id=ident,parent=parent,start=start,end=start+len(part),quote=part,source_id=s['source_id'],meaning=meaning,
                 support_class='issuer-reported plan/policy; operative text not inspected',asu=asu,planned_fiscal_year=year,
                 planned_fiscal_quarter=4 if year else None,transition_method=method,actual_adoption=None,probability=None)
        units.append(row);check(ident+' exact body',texts[s['source_id']][start:start+len(part)]==part)
        check(ident+' original body',norm(part) in original[s['source_id']])
        if asu:
            check(ident+' adoption sentence',f'The Company will adopt {asu} in its fourth quarter of {year} using a {method} transition method.' in norm(part))
    for parent,s in spans.items():
        group=[u for u in units if u['parent']==parent]
        q=s['quote'];body=q[q.index(group[0]['quote']):]
        check(parent+' complete body partition',norm(' '.join(u['quote'] for u in group))==norm(body))
    it=next(u['quote'] for u in units if u['id']=='interim.expense')
    check('January clarification/date preserved','in January 2025' in it and '2025-01' in it)
    check('expense population qualified',all(x in norm(it) for x in ['as applicable','certain expense captions','qualitatively describe remaining amounts','Company’s definition of selling expenses']))
    check('interim material qualifier preserved','no material changes to the Company’s critical accounting estimates' in spans['interim.estimates']['quote'])
    queries=[
      ('known original-period component amounts','not identified','New disclosure plans do not populate old expense/tax/segment components.'),
      ('later retrospective segment comparison','requires later evidence','Keep original and later recast views, basis, affected periods and availability separate.'),
      ('prospective tax/expense history','not supplied by these plans','No backward allocation or presumption of restated figures.'),
      ('operative applicability and threshold','not checked','Need ASU text/amendments/entity dates and exact clauses; issuer description only.'),
      ('actual adoption','not established','Future quarter is reported plan; inspect later filing before admitting an adoption event.'),
      ('constant critical estimates','unsupported','No material change does not mean all estimates/values exactly unchanged.'),
      ('historical information cutoff','separate evidence needed','January 2025 event postdates December 28 period-end; no publication/byte-vintage repair.')]
    save('source-claim-supplement.json',dict(spans=spans,units=units,queries=[dict(query=a,status=b,reason=c) for a,b,c in queries],
        report_periods={'annual':'2024-09-28','interim':'2024-12-28'},source_support='Issuer statements only; no operative ASU or actual adoption verification'))
    images=w.render(ROOT/ss['annual']['original_path'],[29],OUT/'source-render/annual')
    import html
    content='<h1>Derived interim pronouncement/estimate view</h1><p>Reflow of retained HTML text, not original pagination.</p>'+''.join('<p>'+html.escape(s['quote']).replace('\n','<br>')+'</p>' for s in spans.values() if s['source_id']=='interim')
    hp=OUT/'sources/interim-print.html';hp.write_text(content);dp=OUT/'source-render/interim-derived.pdf'
    story=fitz.Story(html=content,user_css='body{font-family:serif;font-size:11pt}h1{font-size:15pt}');writer=fitz.DocumentWriter(str(dp));page=fitz.paper_rect('a4');more=True;n=0
    while more:
        n+=1;assert n<5;dev=writer.begin_page(page);more,_=story.place(page+(40,40,-40,-40));story.draw(dev);writer.end_page()
    writer.close();images+=w.render(dp,list(range(1,n+1)),OUT/'source-render/interim')
    save('source-render.json',dict(images=images,html_path=rel(hp),html_sha256=sha(hp),pdf_path=rel(dp),pdf_sha256=sha(dp)))
    report=dict(checker_sha256=sha(Path(__file__)),inputs=inputs,checks=checks,passed=sum(c['passed'] for c in checks),failed=sum(not c['passed'] for c in checks))
    save('source-checks.json',report);print(json.dumps(dict(passed=report['passed'],failed=report['failed'],units=len(units))))
    assert not report['failed'],[c for c in checks if not c['passed']]

def render():
    pdf=NEW/'accounting-product-proposal.pdf';d=fitz.open(pdf);heading='When later disclosures change the historical query'
    start=max(i+1 for i,p in enumerate(d) if heading in norm(p.get_text()));end=next(i+1 for i in range(start,len(d)) if 'Representing a company’s historical record' in norm(d[i].get_text()))
    body=list(range(start-1,end+1));nav=list(range(1,8));images=w.render(pdf,sorted(set(body+nav)),OUT/'render')
    save('render-manifest.json',dict(pdf=dict(path=rel(pdf),sha256=sha(pdf),pages=len(d)),body_pages=body,navigation_pages=nav,images=images));print(json.dumps(dict(pages=len(d),body_pages=body,pdf_sha256=sha(pdf))))

def revalidate_sources():
    global OUT
    original=OUT
    OUT=original/'source-revalidation-02';OUT.mkdir()
    w.OUT=OUT
    try:sources()
    finally:OUT=original;w.OUT=original

def check():
    old={p.relative_to(OLD):p for p in OLD.rglob('*') if p.suffix in {'.tex','.bib','.lark'}};new={p.relative_to(NEW):p for p in NEW.rglob('*') if p.suffix in {'.tex','.bib','.lark'}}
    inputs={};checks=[];changed=[];deltas=[];before=[];after=[]
    def ck(n,ok):checks.append(dict(id=n,passed=bool(ok)))
    ck('prior source names retained',old.keys()<=new.keys())
    for n,p in new.items():
        a=old[n].read_text() if n in old else '';b=p.read_text();inputs[rel(p)]=sha(p)
        if a!=b:changed.append(str(n));deltas.extend(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile=str(OLD/n),tofile=str(NEW/n)))
        if p.suffix=='.tex':before.append(a);after.append(b)
    ck('only title inclusion and new section changed',set(changed)=={'accounting-product-proposal.tex','chapters/13-reference-company.tex','sections/apple-pronouncements.tex'})
    ck('chapter only appends inclusion',(NEW/'chapters/13-reference-company.tex').read_text()==(OLD/'chapters/13-reference-company.tex').read_text()+'\\input{sections/apple-pronouncements}\n')
    ck('only title version changes',(NEW/'accounting-product-proposal.tex').read_text().replace('Version 2.17','Version 2.16')==(OLD/'accounting-product-proposal.tex').read_text())
    dis=lambda s:re.findall(r'\\\[.*?\\\]|\\begin\{(?:equation\*?|align\*?|gather\*?|displaymath)\}.*?\\end\{(?:equation\*?|align\*?|gather\*?|displaymath)\}',s,re.S)
    a,b='\n'.join(before),'\n'.join(after);ck('48 display contents unchanged',sorted(dis(a))==sorted(dis(b)) and len(dis(a))==48)
    bib=(NEW/'references.bib').read_text();keys=re.findall(r'@\w+\s*\{\s*([^,\s]+)',bib);ck('66 bibliography entries unchanged',bib==(OLD/'references.bib').read_text() and len(keys)==66)
    cites=lambda s:{k.strip() for q in re.findall(r'\\cite\w*\*?(?:\[[^\]]*\])*\{([^}]+)\}',s) for k in q.split(',')}
    ck('citations preserved resolved',cites(a)<=cites(b)<=set(keys))
    labels=re.findall(r'\\label\{([^}]+)\}',b);refs=re.findall(r'\\(?:ref|eqref|pageref|autoref|cref)\{([^}]+)\}',b)
    ck('labels unique references resolved',len(labels)==len(set(labels)) and set(refs)<=set(labels))
    for name in ['source-claim-supplement.json','source-checks.json','source-render.json','render-manifest.json','author-review.md','build-01/receipt.json']:
        inputs[rel(OUT/name)]=sha(OUT/name)
    sc=read(OUT/'source-revalidation-02/source-checks.json');ck('source checks current and passing',sc['failed']==0 and sc['checker_sha256']==sha(Path(__file__)));verify(sc['inputs'])
    s=read(OUT/'source-claim-supplement.json');ck('fresh source ledger exactly reproduces prior reading',s==json.loads(json.dumps(read(OUT/'source-revalidation-02/source-claim-supplement.json'),ensure_ascii=False).replace('source-revalidation-02/','')));ck('nine complete units four spans seven queries',len(s['units'])==9 and len(s['spans'])==4 and len(s['queries'])==7)
    d=fitz.open(NEW/'accounting-product-proposal.pdf');pt=norm(' '.join(p.get_text() for p in d));ck('version rendered','Version 2.17' in pt)
    ck('three plans and no historical inference',all(x in pt for x in ['2023-09','2023-07','2024-03','2025-01','prospective','retrospective','2028','2026','2025','historical components','operative']))
    r=read(OUT/'render-manifest.json');ck('render bound',r['pdf']['sha256']==sha(NEW/'accounting-product-proposal.pdf'));verify({x['path']:x['sha256'] for x in r['images']})
    sr=read(OUT/'source-render.json');verify({x['path']:x['sha256'] for x in sr['images']});ck('derived source binding',sha(ROOT/sr['html_path'])==sr['html_sha256'] and sha(ROOT/sr['pdf_path'])==sr['pdf_sha256'])
    build=read(OUT/'build-01/receipt.json');ck('successful bound build',build['exit_code']==0 and build['pdf_sha256']==r['pdf']['sha256'] and build['log_sha256']==sha(OUT/'build-01/build.log'))
    ck('clean TeX/bibliography logs',not any(x in (NEW/'accounting-product-proposal.log').read_text() for x in ['Warning','Overfull','Underfull','! ']) and not re.search(r'Warning--|error message|I couldn.t open',(NEW/'accounting-product-proposal.blg').read_text()))
    author=(OUT/'author-review.md').read_text();ck('author review bound pending',r['pdf']['sha256'] in author and 'independent_reader_pending' in author)
    base=read(OUT/'baseline.json');verify(base['protected_hashes']);verify(read(PRIOR.parent/'baseline.json')['protected_hashes']);w.ancestry()
    reloc={x['historical_path']:x['preserved_path'] for x in base['pointer_relocations']};verify({reloc.get(p,p):h for p,h in read(PRIOR)['artifact_hashes'].items()})
    ck('prior manifest/completion intact',sha(PRIOR)==base['prior_manifest_sha256']==read(PRIOR.parent/'completion.json')['manifest_sha256'])
    ck('negative readiness preserved',read(ROOT/'data/accounting-master/deliverables/P19/readiness.json')['status']=='not_ready')
    (OUT/'manuscript-delta.diff').write_text(''.join(deltas));report=dict(checker_sha256=sha(Path(__file__)),inputs=inputs,checks=checks,passed=sum(c['passed'] for c in checks),failed=sum(not c['passed'] for c in checks),pdf=r['pdf'],changed_sources=changed)
    save('candidate-checks-final.json',report);print(json.dumps({k:report[k] for k in ['passed','failed','pdf']}));assert not report['failed'],[c for c in checks if not c['passed']]

def freeze():
    c=read(OUT/'candidate-checks-final.json');s=read(OUT/'source-revalidation-02/source-checks.json');base=read(OUT/'baseline.json')
    assert c['failed']==s['failed']==0 and c['checker_sha256']==sha(Path(__file__)) and s['checker_sha256']==sha(OUT/'work_unit.py')
    verify(c['inputs']);verify(s['inputs']);verify(base['protected_hashes']);w.ancestry()
    reloc={x['historical_path']:x['preserved_path'] for x in base['pointer_relocations']};verify({reloc.get(p,p):h for p,h in read(PRIOR)['artifact_hashes'].items()})
    pointers={}
    for n in w.POINTERS:
        t=(ROOT/n).read_text();assert 'Version 2.17' in t and c['pdf']['sha256'] in t and 'not_ready' in t,n
        assert 'general-litigation' in norm(t),n
        pointers[n]=sha(ROOT/n)
    road=(ROOT/w.POINTERS[3]).read_text();oldroad=(ROOT/reloc[w.POINTERS[3]]).read_text();gaps=lambda t:[x for x in t.splitlines() if re.match(r'^\| G\d+ ',x)]
    assert len(gaps(road))==18 and gaps(road)==gaps(oldroad)
    for label,target in [('Latest substantive result',OUT/'result.md'),('Current manuscript',NEW/'accounting-product-proposal.pdf')]:
        row=next(x for x in road.splitlines() if x.startswith(label+': '));link=re.search(r'\]\(([^)]+)\)',row).group(1)
        assert (ROOT/'docs/plans'/link).resolve()==target.resolve()
    now=datetime.now(timezone.utc);save('closeout-checks.json',dict(passed=True,pointers=pointers,all_eighteen_gap_rows_preserved=True))
    hashes={rel(p):sha(p) for d in [OUT,NEW] for p in d.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name not in ['run-manifest.json','completion.json']}
    hashes.update(pointers);hashes[rel(PLAN)]=sha(PLAN);hashes[rel(helper)]=sha(helper)
    commands=[json.loads(x) for x in (OUT/'commands.jsonl').read_text().splitlines()]
    commands.append(dict(command='CUDA_VISIBLE_DEVICES=-1 python3 '+rel(Path(__file__))+' freeze',exit_code=0))
    manifest=dict(recorded_at=now.isoformat(),unit='Apple reported disclosure transitions E01/C03/E07/C08',git_commit=base['git_commit'],plan=rel(PLAN),result=rel(OUT/'result.md'),pdf=c['pdf'],artifact_hashes=hashes,
        environment=dict(python=sys.version,platform=platform.platform(),CUDA_VISIBLE_DEVICES='-1',cpu_gpu_status='CPU only; GPU devices intentionally hidden',conda_env='N/A system python3'),
        data_version='Pinned FY2024 annual/FY2025 Q1 interim Apple originals; source hashes and spans retained',random_seeds='N/A deterministic documentary work',
        commands=commands,wall_seconds=(now-datetime.fromisoformat(base['recorded_at'])).total_seconds(),prior_manifest=rel(PRIOR),prior_manifest_sha256=sha(PRIOR),pointer_relocations=base['pointer_relocations'],
        full_readiness='not_ready',independent_reader='pending',human_acceptance='pending',network_requests=0)
    save('run-manifest.json',manifest);verify(hashes)
    result=dict(status='bounded_unit_complete',manifest_sha256=sha(OUT/'run-manifest.json'),pdf=c['pdf'],source_checks=s['passed'],candidate_checks=c['passed'],manifest_bound_files=len(hashes),full_readiness='not_ready',next_work='Annual general-litigation risk, indemnification, defense costs and insurance')
    save('completion.json',result);print(json.dumps(result))

if __name__=='__main__':
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1';assert not (OUT/'completion.json').exists()
    action=sys.argv[1];start=datetime.now(timezone.utc);timer=time.monotonic();code=0
    try:{'baseline':baseline,'sources':sources,'revalidate-sources':revalidate_sources,'copy':w.copy,'build':w.build,'render':render,'check':check,'freeze':freeze}[action]()
    except BaseException:code=1;raise
    finally:
        if action!='freeze':
            with (OUT/'commands.jsonl').open('a') as f:f.write(json.dumps(dict(command='CUDA_VISIBLE_DEVICES=-1 python3 '+rel(Path(__file__))+' '+action,exit_code=code,started_at=start.isoformat(),wall_seconds=time.monotonic()-timer))+'\n')
