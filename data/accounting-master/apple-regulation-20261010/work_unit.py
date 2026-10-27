"""Source-bound litigation-risk preparation. Frozen outputs are immutable."""
from datetime import datetime, timezone
from pathlib import Path
import difflib, hashlib, html, importlib.util, json, os, platform, re, shutil, subprocess, sys, time
import fitz
from bs4 import BeautifulSoup
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
OLD=ROOT/'docs/design/proposal/manuscript-litigation-risk-20261010'
NEW=ROOT/'docs/design/proposal/manuscript-regulation-20261010'
PRIOR=ROOT/'data/accounting-master/apple-litigation-risk-20261010/run-manifest.json'
PLAN=ROOT/'docs/plans/accounting-apple-regulation-20261010.md'
HELPER=ROOT/'data/accounting-master/apple-legal-20261010/work_unit.py'
spec=importlib.util.spec_from_file_location('document_helpers',HELPER);w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)
w.OUT,w.OLD,w.NEW,w.PRIOR,w.PLAN=OUT,OLD,NEW,PRIOR,PLAN
sha,read,norm,rel,save,verify=w.sha,w.read,w.norm,w.rel,w.save,w.verify
TITLE='A regulation can change the feasible operating plan'
VERSION='Version 2.19';OLDVERSION='Version 2.18';SECTION='apple-regulation'
NEXT='risk-coverage reconciliation'

def baseline():
    p=read(PRIOR);assert sha(PRIOR)==read(PRIOR.parent/'completion.json')['manifest_sha256'];verify(p['artifact_hashes'])
    assert p['pdf']['pages']==160 and p['full_readiness']=='not_ready'
    protected={rel(f):sha(f) for base in [PRIOR.parent,OLD] for f in base.rglob('*') if f.is_file() and '__pycache__' not in f.parts}
    protected[rel(ROOT/'docs/plans/accounting-apple-litigation-risk-20261010.md')]=sha(ROOT/'docs/plans/accounting-apple-litigation-risk-20261010.md')
    pointers=[]
    for n in w.POINTERS:
        f=OUT/'pointers-before'/n;f.parent.mkdir(parents=True,exist_ok=True);assert not f.exists();shutil.copy2(ROOT/n,f)
        pointers.append(dict(historical_path=n,preserved_path=rel(f),sha256=sha(f)))
    verify(read(PRIOR.parent/'baseline.json')['protected_hashes'])
    save('baseline.json',dict(recorded_at=datetime.now(timezone.utc).isoformat(),git_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        prior_manifest=rel(PRIOR),prior_manifest_sha256=sha(PRIOR),prior_manifest_references=len(p['artifact_hashes']),protected_hashes=protected,
        pointer_relocations=pointers,ancestor_counts=w.ancestry(),baseline_pdf=p['pdf'],baseline_pages=w.render(OLD/'accounting-product-proposal.pdf',[34,35,36],OUT/'baseline-render')))
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
    clean=lambda t:re.sub(r'Apple Inc\. \| 2024 Form 10-K \| 13','',t).replace('\f',' ')
    heading='The Company is subject to complex and changing laws and regulations worldwide'
    starts=['The Company’s global operations are subject','Compliance with these laws and regulations','Regulatory changes and other actions']
    for k in ['annual','interim']:
        t=texts[k];a=t.index(heading,50000);ending='Expectations relating to environmental, social and governance' if k=='annual' else 'The technology industry, including, in some instances, the Company'
        b=t.index(ending,a);q=t[a:b].rstrip();f=OUT/'sources'/(k+'.general-regulation.txt');f.parent.mkdir(exist_ok=True);f.write_text(q+'\n')
        spans[k]=dict(source_id=k,start=a,end=a+len(q),quote=q,offset_unit='Unicode code points',span_sha256=hashlib.sha256(q.encode()).hexdigest(),retained_span=rel(f),**ss[k])
        ck(k+' exact source',t[a:a+len(q)]==q);ck(k+' original body',norm(clean(q)) in norm(clean(original[k])))
        openings=[heading]+starts[:2]+(['Risks and costs related to new and changing'] if k=='interim' else [])+starts[2:]
        roles=['risk-heading','regulated-subjects','costs-and-interpretation']+(['technology-and-policy'] if k=='interim' else [])+['notice-trade-mitigation']
        offsets=[q.index(x) for x in openings]
        for i,(role,x) in enumerate(zip(roles,offsets)):
            y=offsets[i+1] if i+1<len(offsets) else len(q);part=q[x:y].rstrip()
            units.append(dict(id=k+'.'+role,parent=k,start=a+x,end=a+x+len(part),quote=part,meaning='Issuer risk/policy assertion; no operative law, event or monetary effect inferred.',actual_measure=None,probability=None))
        ck(k+' complete partition',norm(' '.join(u['quote'] for u in units if u['parent']==k))==norm(q))
    for u in units:ck(u['id']+' source position',texts[u['parent']][u['start']:u['end']]==u['quote'])
    annual,interim=norm(clean(spans['annual']['quote'])),norm(clean(spans['interim']['quote']))
    ck('national security added','national security;' in interim and 'national security;' not in annual)
    ck('executive-order wording explicit three times',interim.count('executive orders, directives, and enforcement priorities')==3 and 'executive orders' not in annual)
    notice={k:norm(clean(next(u['quote'] for u in units if u['id']==k+'.notice-trade-mitigation'))) for k in ['annual','interim']}
    ck('notice/trade paragraph repeated exactly',notice['annual']==notice['interim'])
    for k,q in [('annual',annual),('interim',interim)]:
        ck(k+' policy-versus-outcome qualifiers',all(x in q for x in ['designed to ensure compliance','no assurance','employees, contractors or agents','If the Company is found']))
        ck(k+' cost/operation channels',all(x in q for x in ['increasing the Company’s costs','product, service or feature','customer demand','business or supply chain']))
        ck(k+' uncertain notice and imports',all(x in q for x in ['little or no advance notice','may not be able to effectively mitigate','banned, delayed or prohibited from importation']))
    queries=[('new operative rule or violation','not established','Disclosure wording is not a legal instrument or finding; need named rule, edition, effective date, entity/product and jurisdiction.'),('regulation-induced sales/supply effect','channel identified; amount unresolved','Need affected products/routes, inventory, timing, customer demand and response; no tariff rate or general sales haircut.'),('effective compliance controls','not established','Designed policies plus no assurance do not prove absence of violation or effectiveness.'),('unchanged import risk','unsupported','Repeated risk paragraph is disclosure continuity, not identical underlying exposure.'),('historical knowledge date','not established','Period end and text change do not establish event timing or availability of exact bytes.'),('complete legal/risk semantic coverage','not established','Two full risk bodies; ESG, data protection and other risks retain separate obligations.')]
    comparison=dict(national_security='Added to interim subject list',action_scope='Interim adds executive orders, directives, enforcement priorities three times',paragraph_structure='Annual combined costs/policy paragraph split and expanded in interim',notice_trade_equal=True,interpretation='Source comparison only; no causal attribution, new-law event or materiality threshold')
    save('source-claim-supplement.json',dict(spans=spans,units=units,queries=[dict(query=a,status=b,reason=c) for a,b,c in queries],comparison=comparison))
    images=w.render(ROOT/ss['annual']['original_path'],[16,17],OUT/'source-render/annual')
    content='<h1>Interim regulation risk (derived HTML reflow)</h1>'+''.join('<p>'+html.escape(u['quote'])+'</p>' for u in units if u['parent']=='interim')
    hp=OUT/'sources/interim-print.html';hp.write_text(content);dp=OUT/'source-render/interim-derived.pdf';story=fitz.Story(html=content,user_css='body{font-family:serif;font-size:11pt}h1{font-size:15pt}');writer=fitz.DocumentWriter(str(dp));page=fitz.paper_rect('a4');more=True;n=0
    while more:
        n+=1;assert n<=3;dev=writer.begin_page(page);more,_=story.place(page+(40,40,-40,-40));story.draw(dev);writer.end_page()
    writer.close();images+=w.render(dp,list(range(1,n+1)),OUT/'source-render/interim')
    save('source-render.json',dict(images=images,html_path=rel(hp),html_sha256=sha(hp),pdf_path=rel(dp),pdf_sha256=sha(dp),annual_pages=[16,17],interim_original_pagination=False))
    report=dict(checker_sha256=sha(Path(__file__)),inputs=inputs,checks=checks,passed=sum(c['passed'] for c in checks),failed=sum(not c['passed'] for c in checks));save('source-checks.json',report)
    print(json.dumps(dict(passed=report['passed'],failed=report['failed'],units=len(units))));assert not report['failed'],[x for x in checks if not x['passed']]

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
    q=read(OUT/'source-claim-supplement.json');ck('9 units 2 spans 6 queries',len(q['units'])==9 and len(q['spans'])==2 and len(q['queries'])==6)
    r=read(OUT/'render-manifest.json');ck('render PDF bound',r['pdf']['sha256']==sha(NEW/'accounting-product-proposal.pdf'));verify({x['path']:x['sha256'] for x in r['images']})
    sr=read(OUT/'source-render.json');verify({x['path']:x['sha256'] for x in sr['images']});ck('source reflow bound',sha(ROOT/sr['html_path'])==sr['html_sha256'] and sha(ROOT/sr['pdf_path'])==sr['pdf_sha256'])
    pt=norm(' '.join(p.get_text() for p in fitz.open(NEW/'accounting-product-proposal.pdf')));ck('candidate version and argument rendered',all(x in pt for x in [VERSION,TITLE,'national security','executive orders','enforcement priorities','operative','effective date']))
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
    save('run-manifest.json',dict(recorded_at=now.isoformat(),unit='Apple general-regulation risk E01/C03/C08',git_commit=base['git_commit'],plan=rel(PLAN),result=rel(OUT/'result.md'),pdf=c['pdf'],artifact_hashes=hashes,
        environment=dict(python=sys.version,platform=platform.platform(),CUDA_VISIBLE_DEVICES='-1',cpu_gpu_status='CPU only; GPU devices intentionally hidden',conda_env='N/A system python3'),data_version='Pinned FY2024 annual/FY2025 Q1 interim originals; exact spans',random_seeds='N/A deterministic documentary work',commands=commands,wall_seconds=(now-datetime.fromisoformat(base['recorded_at'])).total_seconds(),prior_manifest=rel(PRIOR),prior_manifest_sha256=sha(PRIOR),pointer_relocations=base['pointer_relocations'],full_readiness='not_ready',independent_reader='pending',human_acceptance='pending',network_requests=0));verify(hashes)
    result=dict(status='bounded_unit_complete',manifest_sha256=sha(OUT/'run-manifest.json'),pdf=c['pdf'],source_checks=s['passed'],candidate_checks=c['passed'],manifest_bound_files=len(hashes),full_readiness='not_ready',next_work='Annual/interim risk-coverage reconciliation');save('completion.json',result);print(json.dumps(result))

if __name__=='__main__':
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1';assert not (OUT/'completion.json').exists();action=sys.argv[1];start=datetime.now(timezone.utc);timer=time.monotonic();code=0
    try:{'baseline':baseline,'sources':sources,'copy':w.copy,'build':w.build,'render':render,'check':check,'freeze':freeze}[action]()
    except BaseException:code=1;raise
    finally:
        if action!='freeze':
            with (OUT/'commands.jsonl').open('a') as f:f.write(json.dumps(dict(command='CUDA_VISIBLE_DEVICES=-1 python3 '+rel(Path(__file__))+' '+action,exit_code=code,started_at=start.isoformat(),wall_seconds=time.monotonic()-timer))+'\n')
