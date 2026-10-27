"""Source-bound litigation-risk preparation. Frozen outputs are immutable."""
from datetime import datetime, timezone
from pathlib import Path
import difflib, hashlib, html, importlib.util, json, os, platform, re, shutil, subprocess, sys, time
import fitz
from bs4 import BeautifulSoup
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
OLD=ROOT/'docs/design/proposal/manuscript-pronouncements-20261010'
NEW=ROOT/'docs/design/proposal/manuscript-litigation-risk-20261010'
PRIOR=ROOT/'data/accounting-master/apple-pronouncements-20261010/run-manifest.json'
PLAN=ROOT/'docs/plans/accounting-apple-litigation-risk-20261010.md'
HELPER=ROOT/'data/accounting-master/apple-legal-20261010/work_unit.py'
spec=importlib.util.spec_from_file_location('document_helpers',HELPER);w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)
w.OUT,w.OLD,w.NEW,w.PRIOR,w.PLAN=OUT,OLD,NEW,PRIOR,PLAN
sha,read,norm,rel,save,verify=w.sha,w.read,w.norm,w.rel,w.save,w.verify
TITLE='Claims against another party can still affect Apple'
VERSION='Version 2.18';OLDVERSION='Version 2.17';SECTION='apple-litigation-risk'
NEXT='general-regulation'

def baseline():
    p=read(PRIOR);assert sha(PRIOR)==read(PRIOR.parent/'completion.json')['manifest_sha256'];verify(p['artifact_hashes'])
    assert p['pdf']['pages']==159 and p['full_readiness']=='not_ready'
    protected={rel(f):sha(f) for base in [PRIOR.parent,OLD] for f in base.rglob('*') if f.is_file() and '__pycache__' not in f.parts}
    protected[rel(ROOT/'docs/plans/accounting-apple-pronouncements-20261010.md')]=sha(ROOT/'docs/plans/accounting-apple-pronouncements-20261010.md')
    pointers=[]
    for n in w.POINTERS:
        f=OUT/'pointers-before'/n;f.parent.mkdir(parents=True,exist_ok=True);assert not f.exists();shutil.copy2(ROOT/n,f)
        pointers.append(dict(historical_path=n,preserved_path=rel(f),sha256=sha(f)))
    verify(read(PRIOR.parent/'baseline.json')['protected_hashes'])
    save('baseline.json',dict(recorded_at=datetime.now(timezone.utc).isoformat(),git_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        prior_manifest=rel(PRIOR),prior_manifest_sha256=sha(PRIOR),prior_manifest_references=len(p['artifact_hashes']),protected_hashes=protected,
        pointer_relocations=pointers,ancestor_counts=w.ancestry(),baseline_pdf=p['pdf'],baseline_pages=w.render(OLD/'accounting-product-proposal.pdf',[33,34,35],OUT/'baseline-render')))
    print(json.dumps(dict(protected_files=len(protected),prior_references=len(p['artifact_hashes']))))

def sources():
    ss=read(w.SUPP)['sources'];inputs={rel(w.SUPP):sha(w.SUPP),rel(HELPER):sha(HELPER)};texts={};checks=[];spans={};units=[]
    def ck(n,ok):checks.append(dict(id=n,passed=bool(ok)))
    for k in ['annual','interim']:
        for kind in ['original','extraction']:
            f=ROOT/ss[k][kind+'_path'];assert sha(f)==ss[k][kind+'_sha256'];inputs[rel(f)]=sha(f)
        texts[k]=(ROOT/ss[k]['extraction_path']).read_text()
    pdf=fitz.open(ROOT/ss['annual']['original_path']);original={'annual':norm(' '.join(p.get_text() for p in pdf)),
      'interim':norm(BeautifulSoup((ROOT/ss['interim']['original_path']).read_text(),'html.parser').get_text(' ',strip=True))}
    def capture(ident,k,opening,ending,start=0):
        t=texts[k];a=t.index(opening,start);b=t.index(ending,a+len(opening));q=t[a:b].rstrip()
        f=OUT/'sources'/(ident+'.txt');f.parent.mkdir(exist_ok=True);f.write_text(q+'\n')
        row=dict(source_id=k,start=a,end=a+len(q),offset_unit='Unicode code points',quote=q,span_sha256=hashlib.sha256(q.encode()).hexdigest(),retained_span=rel(f),**ss[k]);spans[ident]=row
        ck(ident+' exact extraction',t[a:a+len(q)]==q);ck(ident+' original text',norm(q) in original[k]);return row
    general=capture('annual.general-litigation','annual','The Company’s business, results of operations and financial condition could be adversely impacted by unfavorable results of legal proceedings or','The Company is subject to complex and changing laws and regulations worldwide',50000)
    ops=capture('annual.operation-insurance','annual','Following any interruption to its business,','Apple Inc. | 2024 Form 10-K | 6')
    cyber=capture('annual.data-insurance','annual','While the Company maintains insurance coverage that is intended to address certain aspects of data security risks,','Investment in new business strategies and acquisitions')
    trade=capture('annual.receivable-support','annual','The Company distributes its products and certain of its services through third-party cellular network carriers,','The Company is subject to changes in tax rates,',texts['annual'].index('The Company is exposed to credit risk on its trade accounts receivable'))
    interim=capture('interim.risk-incorporation','interim','The Company’s business, reputation, results of operations, financial condition and stock price can be affected by a number of factors,','The Company is subject to complex and changing laws and regulations worldwide',texts['interim'].index('Item 1A.\u00a0'))
    starts=[general['quote'].index(x) for x in ['The Company’s business, results of operations','The Company is subject to various claims,','The Company has faced and continues to face','Regardless of the merit of particular claims,','The outcome of litigation or government investigations','While the Company maintains insurance coverage for certain types of claims,']]
    meanings=[('risk-heading','Conditional adverse-result risk; not a realised amount.'),('indemnified-party','Agreements sometimes include indemnification; claim against indemnified third party can subject Apple to costs/damages. Actual parties, triggers and limits absent.'),('patent-claims','Company reports cellular-product patent claims, defense in US/international courts and requested injunctions/damages; no claim schedule or operative court conclusion.'),('defense-settlement','Defense/responding can be costly regardless of merit; settlement availability/terms uncertain and can change cost of sales, operating expenses and offerings.'),('adverse-resolution','Conditional result above management expectations can affect reporting period; monetary, disgorgement, remedial and injunctive channels remain separate.'),('claim-insurance','Certain claim types covered; insufficiency possible for loss amount and claim type. No recovery amount, receivable or net liability.')]
    for i,(kind,meaning) in enumerate(meanings):
        a=starts[i];b=starts[i+1] if i+1<len(starts) else len(general['quote']);q=general['quote'][a:b].rstrip()
        units.append(dict(id='annual.'+kind,parent='annual.general-litigation',start=general['start']+a,end=general['start']+a+len(q),quote=q,meaning=meaning,support='issuer assertion; contracts/operative rules not established'))
    for ident,s,meaning in [('annual.operation-insurance',ops,'Certain types of losses; recovery costs, lost sales and concentrated suppliers; no quantified coverage.'),('annual.data-insurance',cyber,'Intended certain aspects of data-security risks; no universal coverage or claim amount.'),('annual.receivable-support',trade,'Substantial majority outstanding trade receivables lack listed support including credit insurance; no numeric threshold or every-receivable claim.'),('interim.risk-incorporation',interim,'Annual risk incorporation and no material changes except subsequent items; not unchanged individual exposure/policy/contract.')]:
        units.append(dict(id=ident,parent=ident,start=s['start'],end=s['end'],quote=s['quote'],meaning=meaning,support='issuer assertion; affected facts remain unknown'))
    ck('complete general-litigation partition',norm(' '.join(u['quote'] for u in units if u['parent']=='annual.general-litigation'))==norm(general['quote']))
    for u in units:ck(u['id']+' exact position',texts[spans[u['parent']]['source_id']][u['start']:u['end']]==u['quote'])
    q=norm(general['quote'])
    for name,terms in [('third-party trigger',['sometimes include indemnification provisions','claim against an indemnified third party']),('defense irrespective of merit',['Regardless of the merit','expensive, time-consuming','cost of sales and operating expenses']),('conditional remedy',['If one or more legal matters','above management’s expectations','disgorgement','injunctive relief']),('insurance limitation',['certain types of claims','insufficient to cover all losses or all types of claims'])]:ck(name,all(x in q for x in terms))
    ck('risk-incorporation exception retained','Except as set forth below' in interim['quote'] and 'no material changes' in interim['quote'])
    ck('no numeric trade qualifier','A substantial majority' in trade['quote'] and 'credit insurance' in trade['quote'])
    queries=[('indemnity liability','not identified','Need dated agreement, indemnified party, trigger, scope, recognition and claim facts.'),('defense or settlement expense/cash','not identified','Need service/payment periods, amounts, accrued balances, settlement terms and applicable treatment.'),('operating remedy','channel identified; magnitude unknown','Need affected patent/product/market, term, injunction, pricing and response.'),('insurance recovery/net loss','not identified','Need policy period, insured/beneficiary, coverage, exclusion, deductible, limit, occurrence/claim, enforceability, insurer and recovery timing/treatment.'),('trade credit protection percentage','not identified','Substantial majority is qualitative; coverage populations cannot be merged.'),('interim unchanged legal exposure','unsupported','Qualified risk continuity does not supply a matter/policy/amount equality.'),('claim probability or full risk closure','not established','Risk prose and bounded partition supply neither probability nor all risks.')]
    save('source-claim-supplement.json',dict(spans=spans,units=units,queries=[dict(query=a,status=b,reason=c) for a,b,c in queries],scope='Full general-litigation risk, three bounded dependencies and interim preamble only; all other risk bodies remain separate',probability=None))
    pages=sorted({i+1 for i,p in enumerate(pdf) if any(norm(s['quote'][:100]) in norm(p.get_text()) for s in spans.values() if s['source_id']=='annual')})
    images=w.render(ROOT/ss['annual']['original_path'],pages,OUT/'source-render/annual')
    content='<h1>Interim incorporation (derived HTML reflow)</h1><p>'+html.escape(interim['quote'])+'</p>'
    hp=OUT/'sources/interim-print.html';hp.write_text(content);dp=OUT/'source-render/interim-derived.pdf';story=fitz.Story(html=content,user_css='body{font-family:serif;font-size:11pt}');writer=fitz.DocumentWriter(str(dp));page=fitz.paper_rect('a4');dev=writer.begin_page(page);more,_=story.place(page+(40,40,-40,-40));assert not more;story.draw(dev);writer.end_page();writer.close()
    images+=w.render(dp,[1],OUT/'source-render/interim');save('source-render.json',dict(images=images,html_path=rel(hp),html_sha256=sha(hp),pdf_path=rel(dp),pdf_sha256=sha(dp),annual_pages=pages,interim_original_pagination=False))
    report=dict(checker_sha256=sha(Path(__file__)),inputs=inputs,checks=checks,passed=sum(c['passed'] for c in checks),failed=sum(not c['passed'] for c in checks));save('source-checks.json',report)
    print(json.dumps(dict(passed=report['passed'],failed=report['failed'],units=len(units),annual_pages=pages)));assert not report['failed'],[x for x in checks if not x['passed']]

def render():
    pdf=NEW/'accounting-product-proposal.pdf';d=fitz.open(pdf);start=max(i+1 for i,p in enumerate(d) if TITLE in norm(p.get_text()));end=next(i+1 for i in range(start,len(d)) if 'Representing a company’s historical record' in norm(d[i].get_text()))
    body=list(range(start-1,end+1));nav=list(range(1,8));images=w.render(pdf,sorted(set(body+nav)),OUT/'render');save('render-manifest.json',dict(pdf=dict(path=rel(pdf),sha256=sha(pdf),pages=len(d)),body_pages=body,navigation_pages=nav,images=images));print(json.dumps(dict(pages=len(d),body_pages=body,pdf_sha256=sha(pdf))))

def check():
    old={p.relative_to(OLD):p for p in OLD.rglob('*') if p.suffix in {'.tex','.bib','.lark'}};new={p.relative_to(NEW):p for p in NEW.rglob('*') if p.suffix in {'.tex','.bib','.lark'}};inputs={};checks=[];changed=[];delta=[];before=[];after=[]
    def ck(n,ok):checks.append(dict(id=n,passed=bool(ok)))
    ck('source names retained',old.keys()<=new.keys())
    for n,p in new.items():
        a=old[n].read_text() if n in old else '';b=p.read_text();inputs[rel(p)]=sha(p)
        if a!=b:changed.append(str(n));delta.extend(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile=str(OLD/n),tofile=str(NEW/n)))
        if p.suffix=='.tex':before.append(a);after.append(b)
    ck('bounded changed sources',set(changed)=={'accounting-product-proposal.tex','chapters/13-reference-company.tex','sections/'+SECTION+'.tex'})
    ck('only chapter input appended',(NEW/'chapters/13-reference-company.tex').read_text()==(OLD/'chapters/13-reference-company.tex').read_text()+'\\input{sections/'+SECTION+'}\n')
    ck('only title version changes',(NEW/'accounting-product-proposal.tex').read_text().replace(VERSION,OLDVERSION)==(OLD/'accounting-product-proposal.tex').read_text())
    dis=lambda s:re.findall(r'\\\[.*?\\\]|\\begin\{(?:equation\*?|align\*?|gather\*?|displaymath)\}.*?\\end\{(?:equation\*?|align\*?|gather\*?|displaymath)\}',s,re.S)
    a,b='\n'.join(before),'\n'.join(after);ck('48 displays unchanged',sorted(dis(a))==sorted(dis(b)) and len(dis(a))==48)
    bib=(NEW/'references.bib').read_text();keys=re.findall(r'@\w+\s*\{\s*([^,\s]+)',bib);ck('66 bibliography entries unchanged',bib==(OLD/'references.bib').read_text() and len(keys)==66)
    cites=lambda s:{k.strip() for q in re.findall(r'\\cite\w*\*?(?:\[[^\]]*\])*\{([^}]+)\}',s) for k in q.split(',')};ck('citations preserved resolved',cites(a)<=cites(b)<=set(keys))
    labels=re.findall(r'\\label\{([^}]+)\}',b);refs=re.findall(r'\\(?:ref|eqref|pageref|autoref|cref)\{([^}]+)\}',b);ck('unique labels resolved references',len(labels)==len(set(labels)) and set(refs)<=set(labels))
    for n in ['source-claim-supplement.json','source-checks.json','source-render.json','render-manifest.json','author-review.md','surface-audit.json','surface-disposition.md','build-01/receipt.json']:inputs[rel(OUT/n)]=sha(OUT/n)
    s=read(OUT/'source-checks.json');ck('current source checker passing',s['failed']==0 and s['checker_sha256']==sha(Path(__file__)));verify(s['inputs'])
    q=read(OUT/'source-claim-supplement.json');ck('10 units 5 spans 7 queries',len(q['units'])==10 and len(q['spans'])==5 and len(q['queries'])==7)
    r=read(OUT/'render-manifest.json');ck('render PDF bound',r['pdf']['sha256']==sha(NEW/'accounting-product-proposal.pdf'));verify({x['path']:x['sha256'] for x in r['images']})
    sr=read(OUT/'source-render.json');verify({x['path']:x['sha256'] for x in sr['images']});ck('source reflow bound',sha(ROOT/sr['html_path'])==sr['html_sha256'] and sha(ROOT/sr['pdf_path'])==sr['pdf_sha256'])
    pt=norm(' '.join(p.get_text() for p in fitz.open(NEW/'accounting-product-proposal.pdf')));ck('candidate version and argument rendered',all(x in pt for x in [VERSION,TITLE,'indemnified third party','Regardless of','insurance','recovery','recognition']))
    build=read(OUT/'build-01/receipt.json');ck('successful current build',build['exit_code']==0 and build['pdf_sha256']==r['pdf']['sha256'] and build['log_sha256']==sha(OUT/'build-01/build.log'))
    ck('clean logs',not any(x in (NEW/'accounting-product-proposal.log').read_text() for x in ['Warning','Overfull','Underfull','! ']) and not re.search(r'Warning--|error message|I couldn.t open',(NEW/'accounting-product-proposal.blg').read_text()))
    au=(OUT/'author-review.md').read_text();ck('bound author review pending',r['pdf']['sha256'] in au and 'independent_reader_pending' in au)
    base=read(OUT/'baseline.json');verify(base['protected_hashes']);verify(read(PRIOR.parent/'baseline.json')['protected_hashes']);w.ancestry();reloc={x['historical_path']:x['preserved_path'] for x in base['pointer_relocations']};verify({reloc.get(n,n):h for n,h in read(PRIOR)['artifact_hashes'].items()})
    ck('prior manifest/completion preserved',sha(PRIOR)==base['prior_manifest_sha256']==read(PRIOR.parent/'completion.json')['manifest_sha256']);ck('readiness negative',read(ROOT/'data/accounting-master/deliverables/P19/readiness.json')['status']=='not_ready')
    (OUT/'manuscript-delta.diff').write_text(''.join(delta));report=dict(checker_sha256=sha(Path(__file__)),inputs=inputs,checks=checks,passed=sum(x['passed'] for x in checks),failed=sum(not x['passed'] for x in checks),pdf=r['pdf'],changed_sources=changed);save('candidate-checks.json',report);print(json.dumps({k:report[k] for k in ['passed','failed','pdf']}));assert not report['failed'],[x for x in checks if not x['passed']]

def freeze():
    c=read(OUT/'candidate-checks.json');s=read(OUT/'source-checks.json');base=read(OUT/'baseline.json');assert c['failed']==s['failed']==0 and c['checker_sha256']==s['checker_sha256']==sha(Path(__file__));verify(c['inputs']);verify(s['inputs']);verify(base['protected_hashes']);w.ancestry()
    reloc={x['historical_path']:x['preserved_path'] for x in base['pointer_relocations']};verify({reloc.get(n,n):h for n,h in read(PRIOR)['artifact_hashes'].items()});pointers={}
    for n in w.POINTERS:
        t=(ROOT/n).read_text();assert all(x in t for x in [VERSION,c['pdf']['sha256'],'not_ready',NEXT]),n;pointers[n]=sha(ROOT/n)
    road=(ROOT/w.POINTERS[3]).read_text();old=(ROOT/reloc[w.POINTERS[3]]).read_text();gaps=lambda t:[x for x in t.splitlines() if re.match(r'^\| G\d+ ',x)];assert len(gaps(road))==18 and gaps(road)==gaps(old)
    for label,target in [('Latest substantive result',OUT/'result.md'),('Current manuscript',NEW/'accounting-product-proposal.pdf')]:
        row=next(x for x in road.splitlines() if x.startswith(label+': '));link=re.search(r'\]\(([^)]+)\)',row).group(1);assert (ROOT/'docs/plans'/link).resolve()==target.resolve()
    now=datetime.now(timezone.utc);save('closeout-checks.json',dict(passed=True,pointers=pointers,all_eighteen_gap_rows_preserved=True))
    hashes={rel(p):sha(p) for d in [OUT,NEW] for p in d.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name not in ['run-manifest.json','completion.json']};hashes.update(pointers);hashes[rel(PLAN)]=sha(PLAN);hashes[rel(HELPER)]=sha(HELPER)
    commands=[json.loads(x) for x in (OUT/'commands.jsonl').read_text().splitlines()];commands.append(dict(command='CUDA_VISIBLE_DEVICES=-1 python3 '+rel(Path(__file__))+' freeze',exit_code=0))
    save('run-manifest.json',dict(recorded_at=now.isoformat(),unit='Apple general-litigation risk E01/C03/C08',git_commit=base['git_commit'],plan=rel(PLAN),result=rel(OUT/'result.md'),pdf=c['pdf'],artifact_hashes=hashes,
        environment=dict(python=sys.version,platform=platform.platform(),CUDA_VISIBLE_DEVICES='-1',cpu_gpu_status='CPU only; GPU devices intentionally hidden',conda_env='N/A system python3'),data_version='Pinned FY2024 annual/FY2025 Q1 interim originals; exact spans',random_seeds='N/A deterministic documentary work',commands=commands,wall_seconds=(now-datetime.fromisoformat(base['recorded_at'])).total_seconds(),prior_manifest=rel(PRIOR),prior_manifest_sha256=sha(PRIOR),pointer_relocations=base['pointer_relocations'],full_readiness='not_ready',independent_reader='pending',human_acceptance='pending',network_requests=0));verify(hashes)
    result=dict(status='bounded_unit_complete',manifest_sha256=sha(OUT/'run-manifest.json'),pdf=c['pdf'],source_checks=s['passed'],candidate_checks=c['passed'],manifest_bound_files=len(hashes),full_readiness='not_ready',next_work='Annual/interim general-regulation risk and dated update comparison');save('completion.json',result);print(json.dumps(result))

if __name__=='__main__':
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1';assert not (OUT/'completion.json').exists();action=sys.argv[1];start=datetime.now(timezone.utc);timer=time.monotonic();code=0
    try:{'baseline':baseline,'sources':sources,'copy':w.copy,'build':w.build,'render':render,'check':check,'freeze':freeze}[action]()
    except BaseException:code=1;raise
    finally:
        if action!='freeze':
            with (OUT/'commands.jsonl').open('a') as f:f.write(json.dumps(dict(command='CUDA_VISIBLE_DEVICES=-1 python3 '+rel(Path(__file__))+' '+action,exit_code=code,started_at=start.isoformat(),wall_seconds=time.monotonic()-timer))+'\n')
