"""Exact source scope and preservation for competition/product-transition reading."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,re,shutil,subprocess,sys,time
import fitz
from bs4 import BeautifulSoup

OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
PRIOR=ROOT/'data/accounting-master/apple-business-interruption-20261010/run-manifest.json'
PLAN=ROOT/'docs/plans/accounting-apple-competition-transition-20261010.md'
MAP=ROOT/'data/accounting-master/apple-business-interruption-20261010/coverage-update.json'
INVENTORY=ROOT/'data/accounting-master/apple-risk-coverage-20261010/risk-coverage.json'
POINTERS=['docs/plans/accounting-master-checkpoint.md','data/accounting-master/next-plan.md','docs/plans/accounting-continuation-requirements-20261007.md','docs/plans/accounting-master-current.md']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
rel=lambda p:str(p.relative_to(ROOT))
norm=lambda s:' '.join(s.split())


def save(name,d):
    p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x') as f:f.write(json.dumps(d,indent=2,ensure_ascii=False)+'\n')


def run():
    start=time.monotonic();now=datetime.now(timezone.utc);prior=read(PRIOR)
    assert sha(PRIOR)==read(PRIOR.with_name('completion.json'))['manifest_sha256']
    for n,v in prior['artifact_hashes'].items():assert sha(ROOT/n)==v,n
    pointers=[]
    for n in POINTERS:
        dst=OUT/'pointers-before'/n;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/n,dst)
        pointers.append(dict(historical_path=n,preserved_path=rel(dst),sha256=sha(dst)))
    save('baseline.json',dict(recorded_at=now.isoformat(),git_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        prior_manifest=rel(PRIOR),prior_manifest_sha256=sha(PRIOR),prior_artifact_count=len(prior['artifact_hashes']),
        prior_completion_sha256=sha(PRIOR.with_name('completion.json')),pointer_relocations=pointers,
        requirements_path='docs/plans/accounting-mission-requirements.md',requirements_sha256=sha(ROOT/'docs/plans/accounting-mission-requirements.md')))
    save('input-relocations.json',dict(relocations=[]))
    inputs={rel(p):sha(p) for p in [PRIOR,PRIOR.with_name('completion.json'),PLAN,MAP,INVENTORY]}
    checks=[];meaning=[];ck=lambda n,b:checks.append(dict(id=n,passed=bool(b)));mk=lambda n,b:meaning.append(dict(id=n,passed=bool(b)))
    txt=ROOT/'docs/design/cases/apple/annual-2024.txt';pdf=ROOT/'docs/design/cases/apple/annual-2024.pdf'
    html=ROOT/'docs/design/cases/apple/interim-2025q1.html';itxt=ROOT/'docs/design/cases/apple/interim-2025q1.txt'
    for p in [txt,pdf,html,itxt]:
        inputs[rel(p)]=sha(p);ck(rel(p)+' pinned hash',sha(p)==prior['artifact_hashes'][rel(p)])
    t=txt.read_text();original=norm(fitz.open(pdf)[9].get_text());spans={};units=[]
    recs=read(INVENTORY)['records'];current=read(MAP)['records']
    for index in [3,4]:
        r=next(x for x in recs if x['source']=='annual' and x['index']==index)
        status=next(x for x in current if x['source']=='annual' and x['index']==index)['retention_status']
        q=t[r['start']:r['body_end']];name=f'annual-{index:02}';p=OUT/'sources'/(name+'.txt');p.parent.mkdir(exist_ok=True);p.write_text(q)
        ck(name+' exact inventory source',q==(ROOT/r['body_path']).read_text());ck(name+' unworked at entry',status=='no prior retained reading')
        heading=t[r['start']:r['heading_end']];body=t[r['heading_end']:r['body_end']]
        furniture=list(re.finditer(r'Apple Inc\. \| 2024 Form 10-K \| 7',body));ck(name+' expected furniture count',len(furniture)==(1 if index==4 else 0))
        meaningful=body[:furniture[0].start()] if furniture else body
        offsets=[]
        for j,m in enumerate(re.finditer(r'\S.*?(?=\n\s*\n|\Z)',meaningful,flags=re.S),1):
            a=r['heading_end']+m.start();b=r['heading_end']+m.end();u=dict(id=name+f'.p{j}',source='annual',start=a,end=b,quote=t[a:b],quote_sha256=hashlib.sha256(t[a:b].encode()).hexdigest())
            units.append(u);offsets.append(u['id']);ck(u['id']+' exact source',t[a:b]==u['quote']);mk(u['id']+' original PDF',norm(u['quote']) in original)
        ck(name+' complete meaningful paragraph partition',norm(meaningful)==norm(' '.join(u['quote'] for u in units if u['id'] in offsets)))
        ck(name+' paragraphs',len(offsets)==(7 if index==3 else 1));mk(name+' heading original PDF',norm(heading) in original)
        spans[name]=dict(source='annual',start=r['start'],end=r['body_end'],quote=q,quote_sha256=sha(p),path=rel(p),heading_end=r['heading_end'],units=offsets,page=10,printed_page=7)
    deps=[]
    for unit,ident in [('apple-revenue-20261008','annual.revenue.control'),('apple-revenue-20261008','annual.revenue.bundles'),('apple-commitments-20261008','annual.note.12.custom')]:
        p=ROOT/'data/accounting-master'/unit/'source-claim-supplement.json';manifest=p.with_name('run-manifest.json');d=read(p);entry=next(u for u in d['units'] if u['id']==ident)
        inputs[rel(p)]=sha(p);inputs[rel(manifest)]=sha(manifest);ck(ident+' frozen supplement hash',read(manifest)['artifact_hashes'][rel(p)]==sha(p))
        a=entry.get('start',entry.get('source_start'));b=entry.get('end',entry.get('source_end'));q=entry['quote']
        ck(ident+' exact scope',t[a:b]==q)
        deps.append(dict(id=ident,source='annual',start=a,end=b,quote=q,quote_sha256=hashlib.sha256(q.encode()).hexdigest(),prior_supplement=rel(p),prior_manifest=rel(manifest),interpretation=entry.get('interpretation')))
    preamble=ROOT/'data/accounting-master/apple-risk-coverage-20261010/interim-preamble.txt';q=preamble.read_text();inputs[rel(preamble)]=sha(preamble)
    mk('interim incorporation original HTML',norm(q) in norm(BeautifulSoup(html.read_text(),'html.parser').get_text(' ',strip=True)))
    claims=[
        ('annual-03.p1','issuer market-condition assertion','Price competition, margin pressure, life cycles, standards and price sensitivity. No quantified own-price demand function.',['downward pressure on gross margins','short product life cycles']),
        ('annual-03.p2','issuer operating assertion and no-assurance qualification','Integrated design requires R&D; spending does not establish returns or successful marketing.',['must make significant investments in R&D','no assurance']),
        ('annual-03.p3','issuer IP/competitor assertion with conditional consequence','Reported rights and imitation/infringement allegations do not establish an adjudicated dispute or future remedy.',['patents, trademarks and copyrights','not consistently available']),
        ('annual-03.p4','issuer market-share/resource assertion and historical market description','Minority share is qualitative across three global device markets; competitor below-cost capacity is not Apple loss or numerical share.',['minority market share','little or no profit or even at a loss']),
        ('annual-03.p5','reported competition and management expectation','Imitation/collaboration are distinct mechanisms; expected intensification is not an observed future outcome.',['expects competition to intensify','work collaboratively']),
        ('annual-03.p6','issuer service-market assertion','Free-content and illegitimate-content alternatives are described, without identifying Apple service pricing.',['content to users for free','illegitimate means']),
        ('annual-03.p7','conditional performance dependence and no assurance','Continued improvement need not ensure effective competition.',['continually improve','no assurance']),
        ('annual-04.p1','conditional release requirements and downside possibility','Development, acceptance, ramp, third-party support, inventory, cost and quality are distinct. Replacement can lower revenue and margin.',['market acceptance','purchase commitments and inventory levels','lower revenues and lower profit margins'])]
    records=[]
    for ident,kind,explanation,anchors in claims:
        u=next(x for x in units if x['id']==ident)
        for a in anchors:mk(ident+' '+a,a in norm(u['quote']))
        records.append(dict(id=ident,source_quote_sha256=u['quote_sha256'],source_class=kind,author_interpretation=explanation,independent_acceptance='pending'))
    queries=[('release_profit','Does a successful release guarantee higher profit?','No. Replacement can reduce revenues and margins; development success and financial success differ.'),
        ('rnd_return','Does required R&D identify return or recognition?','No amount, return, capitalization test or expense allocation follows from the risk prose.'),
        ('share','What numerical share is established?','None; minority share describes the three named global device markets qualitatively.'),
        ('ip','Has a particular infringement been adjudicated?','Not by this risk assertion; named parties, rights, jurisdictions and decisions would be required.'),
        ('support','Is sufficient third-party support guaranteed?','No; application availability and component capacity are distinct conditional inputs.'),
        ('inventory','Which old-product inventory or commitments become unusable?','Unknown; require cohort, compatibility, quantities, terms, demand and actual dispositions.'),
        ('sale_clock','Does a launch date establish recognized revenue or cash?','No; the inspected revenue passages distinguish transfer of control, service delivery, allocation and collection.'),
        ('weights','How should alternative transitions be weighted?','The filing supplies no probability measure, substitution rates or branch weights.')]
    save('source-claim-supplement.json',dict(spans=spans,units=units,dependencies=deps,interim_context=dict(path=rel(preamble),sha256=sha(preamble),meaning='Annual incorporation with exceptions; no unchanged-exposure inference.'),coverage=dict(risk_bodies=2,paragraphs=8,dependencies=3,meaning='Bounded author reading; not whole-report semantic acceptance')))
    save('claim-query-ledger.json',dict(claims=records,queries=[dict(id=i,question=q,answer=a) for i,q,a in queries],probability_weights=None))
    save('source-checks.json',dict(checker_sha256=sha(Path(__file__)),inputs=[dict(path=p,sha256=h) for p,h in inputs.items()],checks=checks,passed=sum(x['passed'] for x in checks),failed=sum(not x['passed'] for x in checks)))
    mi={**inputs,rel(Path(__file__)):sha(Path(__file__)),rel(OUT/'source-claim-supplement.json'):sha(OUT/'source-claim-supplement.json'),rel(OUT/'claim-query-ledger.json'):sha(OUT/'claim-query-ledger.json')}
    save('meaning-checks.json',dict(inputs=mi,checks=meaning,passed=sum(x['passed'] for x in meaning),failed=sum(not x['passed'] for x in meaning)))
    image_records=[]
    for p,ns,group in [(pdf,[10],'original'),(ROOT/prior['pdf']['path'],[37,38,39],'baseline')]:
        d=fitz.open(p)
        for n in ns:
            f=OUT/'inspection'/group/f'page-{n:03}.png';f.parent.mkdir(parents=True,exist_ok=True);d[n-1].get_pixmap(matrix=fitz.Matrix(1.4,1.4)).save(f)
            image_records.append(dict(path=rel(f),sha256=sha(f),page=n,pdf=rel(p)))
    save('inspection/manifest.json',image_records)
    save('source-run-receipt.json',dict(command='CUDA_VISIBLE_DEVICES=-1 python3 '+rel(Path(__file__)),started_at=now.isoformat(),wall_seconds=time.monotonic()-start,exit_code=0 if all(x['passed'] for x in checks+meaning) else 1))
    print(json.dumps(dict(source_passed=sum(x['passed'] for x in checks),meaning_passed=sum(x['passed'] for x in meaning),failed=sum(not x['passed'] for x in checks+meaning))))
    assert all(x['passed'] for x in checks+meaning),[x for x in checks+meaning if not x['passed']]

if __name__=='__main__':
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1'
    assert not (OUT/'baseline.json').exists()
    run()
