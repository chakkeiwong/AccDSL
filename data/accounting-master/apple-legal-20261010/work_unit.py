"""CPU-only documentary work. Closed outputs must never be overwritten."""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import difflib
import hashlib
import html
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
from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
OLD = ROOT / 'docs/design/proposal/manuscript-perimeter-20261009'
NEW = ROOT / 'docs/design/proposal/manuscript-legal-20261010'
PLAN = ROOT / 'docs/plans/accounting-apple-legal-20261010.md'
PRIOR = ROOT / 'data/accounting-master/apple-perimeter-20261009/run-manifest.json'
SUPP = ROOT / 'docs/design/cases/apple/continuation-20261007/case-supplement-v1.json'
POINTERS = ['docs/plans/accounting-master-checkpoint.md', 'data/accounting-master/next-plan.md',
            'docs/plans/accounting-continuation-requirements-20261007.md', 'docs/plans/accounting-master-current.md']
HEADINGS = ['Digital Markets Act Investigations', 'Department of Justice Lawsuit', 'Epic Games', 'Other Legal Proceedings']
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
norm = lambda s: ' '.join(s.split())
rel = lambda p: str(p.relative_to(ROOT))


def save(name, obj):
    p = OUT / name
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('x') as f:
        f.write(json.dumps(obj, indent=2, ensure_ascii=False) + '\n')


def verify(hashes):
    bad = [n for n,h in hashes.items() if not (ROOT/n).is_file() or sha(ROOT/n) != h]
    assert not bad, bad


def render(pdf, pages, directory):
    doc = fitz.open(pdf); directory.mkdir(parents=True, exist_ok=True)
    records = []
    for n in pages:
        p = directory / f'page-{n:03}.png'
        assert not p.exists(), p
        doc[n-1].get_pixmap(matrix=fitz.Matrix(1.65,1.65)).save(p)
        records.append(dict(page=n, path=rel(p), sha256=sha(p)))
    return records


def ancestry():
    counts = {}
    for name in ['apple-perimeter-20261009','apple-segments-20261009','apple-liquidity-20261009','apple-debt-20261009']:
        b = read(ROOT/'data/accounting-master'/name/'baseline.json')
        verify(b['protected_hashes']); counts[name] = len(b['protected_hashes'])
    history = read(ROOT/'data/accounting-master/direct-p19-20261007/recovery-entry-v1.json')
    for k in ['protected_hashes','upstream_reference_hashes','controller_hashes']:
        verify(history[k]); counts[k] = len(history[k])
    p19 = read(ROOT/'data/accounting-master/continuation-20261007/baseline-manifest.json')
    reloc = {r['historical_path']:r['preserved_path'] for r in p19['relocations']}
    verify({reloc.get(n,n):h for n,h in p19['p19_historical_artifact_hashes'].items()})
    return counts


def baseline():
    prior = read(PRIOR)
    assert sha(PRIOR) == read(PRIOR.parent/'completion.json')['manifest_sha256']
    verify(prior['artifact_hashes'])
    assert prior['pdf']['pages'] == 155 and prior['full_readiness'] == 'not_ready'
    protected = {rel(p):sha(p) for base in [PRIOR.parent,OLD] for p in base.rglob('*')
                 if p.is_file() and '__pycache__' not in p.parts}
    for n in ['MISSION_CONTROL.md','docs/plans/accounting-mission-requirements.md',
              'docs/plans/accounting-product-design-checkpoint.md','scripts/accounting_master_catalog.json',
              'docs/plans/accounting-apple-perimeter-20261009.md']:
        protected[n] = sha(ROOT/n)
    pointers = []
    for n in POINTERS:
        p = OUT/'pointers-before'/n; p.parent.mkdir(parents=True,exist_ok=True)
        assert not p.exists(); shutil.copy2(ROOT/n,p)
        pointers.append(dict(historical_path=n,preserved_path=rel(p),sha256=sha(p)))
    save('baseline.json',dict(recorded_at=datetime.now(timezone.utc).isoformat(),
        git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        protected_hashes=protected,pointer_relocations=pointers,prior_manifest=rel(PRIOR),
        prior_manifest_sha256=sha(PRIOR),prior_manifest_references=len(prior['artifact_hashes']),
        ancestor_counts=ancestry(),baseline_pdf=prior['pdf'],
        baseline_pages=render(OLD/'accounting-product-proposal.pdf',[29,30,31],OUT/'baseline-render')))
    print(json.dumps(dict(protected_files=len(protected),prior_manifest_references=len(prior['artifact_hashes']))))


def sources():
    d = read(SUPP); records = {k:d['sources'][k] for k in ['annual','interim']}
    texts = {}; inputs = {rel(SUPP):sha(SUPP)}; checks = []; spans = {}; matters = []
    def check(n, ok, detail=None): checks.append(dict(id=n,passed=bool(ok),detail=detail))
    for k,v in records.items():
        for kind in ['original','extraction']:
            p=ROOT/v[kind+'_path']; assert sha(p)==v[kind+'_sha256']; inputs[rel(p)]=sha(p)
        texts[k]=(ROOT/v['extraction_path']).read_text()
    annual=fitz.open(ROOT/records['annual']['original_path'])
    ah=norm(' '.join(p.get_text() for p in annual))
    it_html=BeautifulSoup((ROOT/records['interim']['original_path']).read_text(),'html.parser')
    ih=norm(it_html.get_text(' ',strip=True))
    def span(key,k,a,b):
        q=texts[k][a:b].rstrip(); b=a+len(q)
        p=OUT/'sources'/(key+'.txt');p.parent.mkdir(exist_ok=True)
        with p.open('x') as f:f.write(q+'\n')
        pages=list(range(texts[k].count('\f',0,a)+1,texts[k].count('\f',0,b)+2)) if k=='annual' else []
        row=dict(source_id=k,start=a,end=b,offset_unit='Unicode code points',quote=q,
                 span_sha256=hashlib.sha256(q.encode()).hexdigest(),retained_span=rel(p),source_pages=pages,
                 **records[k]);spans[key]=row
        check(key+' exact extraction',texts[k][a:b]==q)
        check(key+' original text',norm(q) in (ah if k=='annual' else ih))
        return row
    def locate(key,k,opening,ending,start=0):
        t=texts[k];a=t.index(opening,start);b=t.index(ending,a+len(opening));return span(key,k,a,b)
    for k,a,b,h in [('annual',103510,107860,'43d42cd8fbd565628fbacee844cec184f767634f8c309004a527347e54a3cbfe'),
                    ('interim',53800,58229,'fc40f30a6ce71df57f4c8f2ac58fd595f80054d6f716565b51f68b0977118cae')]:
        check(k+' selected frontier hash',hashlib.sha256(texts[k][a:b].encode()).hexdigest()==h)
        row=span(k+'.legal',k,a,b)
        # Full interim footer is retained; it is not a proceeding assertion.
        content_end=row['quote'].find('Apple Inc. | Q1 2025 Form 10-Q | 18') if k=='interim' else len(row['quote'])
        body=row['quote'][:content_end].rstrip()
        starts=[body.index(h) for h in HEADINGS]
        check(k+' four ordered headings',starts==sorted(starts) and len(set(starts))==4)
        for i,h in enumerate(HEADINGS):
            end=starts[i+1] if i<3 else len(body)
            part=body[starts[i]:end];q=part.strip();offset=starts[i]+len(part)-len(part.lstrip())
            off=a+offset
            matter=dict(id=k+'.'+['dma','doj','epic','other'][i],heading=h,parent=k+'.legal',
                report_period_end='2024-09-28' if k=='annual' else '2024-12-28',
                source_assertion_status='dated issuer report; author interpretation; no independent legal adjudication',
                start=off,end=off+len(q),quote=q,assertions=[])
            check(matter['id']+' exact body',texts[k][matter['start']:matter['end']]==q)
            check(matter['id']+' original body',norm(q) in (ah if k=='annual' else ih))
            sentence_body=q[len(h):].strip()
            # Legal abbreviations are not split: only sentence punctuation followed by a capitalized clause.
            clauses=re.split(r'(?<=[.])\s+(?=(?:On |The |In addition|Epic |A motion|Although |If |The outcome))',sentence_body)
            cursor=off+q.index(sentence_body)
            for j,c in enumerate(clauses,1):
                pos=texts[k].index(c,cursor);cursor=pos+len(c)
                if c.startswith('If '): role='conditional consequence'
                elif c.startswith('Although '): role='reported appeal/effectiveness condition'
                elif 'believes' in c: role='management position'
                elif 'settled certain' in c: role='reported settlement and material-impact qualifier'
                elif 'District Court found' in c: role='reported court finding and injunction'
                elif 'seeking' in c or 'seeks' in c: role='requested relief or contested motion'
                elif 'alleging' in c or 'investigation' in c: role='allegation/investigation; preliminary status retained'
                elif 'implemented a plan' in c: role='reported company action; compliance not adjudicated'
                else: role='reported scope or uncertainty'
                assertion=dict(id=matter['id']+f'.{j:02}',start=pos,end=pos+len(c),quote=c,role=role,
                    event_dates=re.findall(r'(?:January|March|June|August|September) \d{1,2}, \d{4}',norm(c)),
                    reporter='Apple',probability=None,matter_accrual=None,matter_payment=None)
                matter['assertions'].append(assertion)
                check(assertion['id']+' exact assertion',texts[k][pos:pos+len(c)]==c)
            check(matter['id']+' complete sentence body',norm(' '.join(c['quote'] for c in matter['assertions']))==norm(sentence_body))
            matters.append(matter)
        check(k+' full legal partition',norm(' '.join(m['quote'] for m in matters if m['parent']==k+'.legal'))==norm(body[starts[0]:]))
    locate('annual.contingency','annual','Contingencies\n','Concentrations in the Available Sources of Supply',texts['annual'].index('Note 12 – Commitments'))
    locate('interim.contingency','interim','Note 9 –','Note 10 –',30000)
    locate('annual.recognition','annual','Legal and Other Contingencies\n','Apple Inc. | 2024 Form 10-K | 26',120000)
    risk_head='The technology industry, including, in some instances, the Company, is subject to intense media, political and regulatory scrutiny'
    locate('annual.antitrust_risk','annual',risk_head,'The Company’s business is subject to a variety of U.S. and international laws')
    locate('interim.antitrust_risk','interim',risk_head,'Item 2.',58229)
    locate('interim.risk_incorporation','interim','Item 1A.', 'The Company is subject to complex',58229)
    locate('annual.regulatory_risk','annual','The Company is subject to complex and changing laws','Expectations relating to environmental, social',65000)
    locate('interim.regulatory_risk','interim','The Company is subject to complex and changing laws',risk_head,58229)
    # Strip known extraction page furniture only for text equivalence; retain exact quotes in records.
    clean=lambda s: re.sub(r'Apple Inc\. \| (?:2024|Q1 2025) Form 10-[KQ] \| \d+','',s).replace('\f','').replace('®','')
    differences=[]
    for ident in ['dma','doj','epic','other']:
        x=next(m for m in matters if m['id']=='annual.'+ident);y=next(m for m in matters if m['id']=='interim.'+ident)
        xx=norm(clean(x['quote']));yy=norm(clean(y['quote']))
        differences.append(dict(matter=ident,annual=x['id'],interim=y['id'],exact_normalized_equal=xx==yy,
            disposition={'dma':'Interim expands EU/DMA acronym definition; same stated investigation/remedy content.',
                         'doj':'Same normalized issuer narrative; no new disposition reported in these bodies.',
                         'epic':'Registered-mark typography differs; same stated injunction/compliance and pending-motion content.',
                         'other':'Settlements refer to Q4 FY2024 versus Q1 FY2025; distinct period assertions, amounts and case identities absent.'}[ident]))
    check('DOJ matched narrative',next(v for v in differences if v['matter']=='doj')['exact_normalized_equal'])
    check('Epic matched narrative after trademark removal',next(v for v in differences if v['matter']=='epic')['exact_normalized_equal'])
    for k in ['annual','interim']:
        q=norm(spans[k+'.contingency']['quote'])
        check(k+' full qualified assessment',all(v in q for v in ['In the opinion of management','not at least a reasonable possibility','incurred a material loss','material loss greater than a recorded accrual','asserted legal and other claims']))
    check('reported recognition policy', 'probable that a loss has been incurred and the amount is reasonably estimable' in norm(spans['annual.recognition']['quote']))
    check('annual Google licensing exposure', 'Google LLC' in spans['annual.antitrust_risk']['quote'])
    check('interim Google dated finding/proposed duration',all(t in norm(spans['interim.antitrust_risk']['quote']) for t in ['August 5, 2024','DOJ has proposed remedies','up to 10 years','If implemented']))
    for k in ['annual','interim']:
        q=norm(next(m['quote'] for m in matters if m['id']==k+'.dma'))
        check(k+' conditional cap and stay',all(t in q for t in ['If the Commission makes a final determination','up to 10%','annual worldwide net sales','unless a stay','Company believes']))
        check(k+' Epic US scope', 'U.S. storefront of the iOS and iPadOS' in norm(next(m['quote'] for m in matters if m['id']==k+'.epic')))
    queries=[
        dict(query='DMA final liability or expected fine',status='not identified',reason='Conditional issuer cap; no final violation, applicable base, law, amount or probability established.'),
        dict(query='DOJ damages',status='not identified',reason='DOJ requests equitable relief; related civil claims seek damages/other relief without quantified matter accounts.'),
        dict(query='Epic operating exposure',status='source-supported scope; magnitude unresolved',reason='Reported US storefront injunction and disputed compliance; contracts, effective remedial details and response absent.'),
        dict(query='Zero legal exposure or zero accrual',status='unsupported',reason='Qualified management material-loss assessment neither states zero exposure nor discloses a total or matter accrual.'),
        dict(query='Settlement cash/expense roll-forward',status='not identified',reason='Q4/Q1 settlements have no disclosed amounts, case linkage, accrual timing or payment schedule in these passages.'),
        dict(query='Google distribution revenue loss',status='not identified',reason='Interim reports proposed remedies against Google; actual agreement economics and realised outcome missing.'),
        dict(query='As-of historical exposure',status='not established by event dates',reason='Report dates and event dates differ; availability/byte vintage must be evidenced separately.'),
        dict(query='Full legal or filing closure',status='not established',reason='Issuer-selected discussion and other unresolved proceedings; law/dockets and wider package remain open.')]
    for m in matters:
        m['remaining']='Operative authority/docket, matter-level amounts, recognition facts, contract terms and remedy response; no numerical threshold or probability inferred.'
    save('source-claim-supplement.json',dict(records=records,spans=spans,matters=matters,dated_comparison=differences,
        queries=queries,interpretation='Author preparation; issuer assertions separated from operative legal/accounting authority',
        no_probability=True,no_numeric_fine_calculation=True,prior_state_aid_dependency='apple-tax-20261009; do not merge with DMA or recognise the same tax twice'))
    # Source equivalence permits known footer furniture; report rather than silently masking other mismatches.
    for c in checks:
        if not c['passed'] and c['id'].endswith('original text'):
            key=c['id'].removesuffix(' original text');row=spans[key]
            c['passed']=norm(clean(row['quote'])) in norm(clean(ah if row['source_id']=='annual' else ih))
            c['detail']='Comparison removes retained page furniture and registered-mark typography only.'
    annual_pages=sorted(set(n for s in spans.values() for n in s['source_pages'] if 1<=n<=len(annual)))
    images=render(ROOT/records['annual']['original_path'],annual_pages,OUT/'source-render/annual')
    p=OUT/'sources/interim-print.html'
    content=''.join('<h2>'+html.escape(k)+'</h2><pre style="white-space:pre-wrap">'+html.escape(s['quote'])+'</pre>' for k,s in spans.items() if s['source_id']=='interim')
    p.write_text('<meta charset="utf-8"><style>@page{size:A4;margin:18mm}body{font:11pt serif}pre{font:inherit}</style>'+content)
    derived=OUT/'source-render/interim-derived.pdf'
    story=fitz.Story(html=content,user_css='body{font-family:serif;font-size:11pt}h2{font-size:14pt}pre{white-space:pre-wrap;font-family:serif}')
    writer=fitz.DocumentWriter(str(derived));page=fitz.paper_rect('a4');where=page+(40,40,-40,-40)
    more=True;count=0
    while more:
        count+=1;assert count<=12,'Unexpected source reflow size'
        device=writer.begin_page(page);more,_=story.place(where);story.draw(device);writer.end_page()
    writer.close()
    images+=render(derived,list(range(1,len(fitz.open(derived))+1)),OUT/'source-render/interim')
    save('source-render-receipt.json',dict(original_inputs=inputs,derived_html=rel(p),derived_html_sha256=sha(p),
        derived_pdf=rel(derived),derived_pdf_sha256=sha(derived),status='Interim source text verified against retained HTML; derived print reflow only',images=images))
    report=dict(checker_sha256=sha(Path(__file__)),inputs=inputs,checks=checks,passed=sum(c['passed'] for c in checks),failed=sum(not c['passed'] for c in checks))
    save('source-checks.json',report)
    print(json.dumps(dict(passed=report['passed'],failed=report['failed'],matters=len(matters),assertions=sum(len(m['assertions']) for m in matters),source_pages=annual_pages)))
    assert not report['failed'],[c for c in checks if not c['passed']]


def copy():
    assert not NEW.exists(); copied={}
    for p in OLD.rglob('*'):
        if p.is_file() and p.suffix in {'.tex','.bib','.lark'}:
            dst=NEW/p.relative_to(OLD);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst);copied[rel(dst)]=sha(dst)
    save('candidate-copy-receipt.json',dict(baseline=rel(OLD),candidate=rel(NEW),copied_hashes=copied))
    print(json.dumps(dict(copied_sources=len(copied))))


def build():
    attempt=1
    while (OUT/f'build-{attempt:02}').exists():attempt+=1
    assert attempt<=3,'Build budget exhausted: diagnose before revising plan'
    run=OUT/f'build-{attempt:02}';run.mkdir()
    cache=Path('/tmp/accdsl-legal-tex-cache-20261010');cache.mkdir(exist_ok=True)
    env={**os.environ,'CUDA_VISIBLE_DEVICES':'-1','TEXMFVAR':str(cache),'TEXMFCACHE':str(cache)}
    command=['latexmk','-lualatex','-interaction=nonstopmode','-halt-on-error','accounting-product-proposal.tex']
    start=time.monotonic()
    with (run/'build.log').open('w') as log:
        try:code=subprocess.run(command,cwd=NEW,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=240).returncode
        except subprocess.TimeoutExpired:code=124
    pdf=NEW/'accounting-product-proposal.pdf'
    save(f'build-{attempt:02}/receipt.json',dict(command=command,environment={k:env[k] for k in ['CUDA_VISIBLE_DEVICES','TEXMFVAR','TEXMFCACHE']},
        exit_code=code,wall_seconds=time.monotonic()-start,log_sha256=sha(run/'build.log'),pdf_sha256=sha(pdf) if pdf.exists() else None))
    print(json.dumps(dict(attempt=attempt,exit_code=code,wall_seconds=time.monotonic()-start)))
    assert code==0


def candidate_render():
    pdf=NEW/'accounting-product-proposal.pdf';doc=fitz.open(pdf)
    heading='Legal proceedings beyond the booked liability'
    start=max(i+1 for i,p in enumerate(doc) if heading in norm(p.get_text()))
    end=next(i+1 for i in range(start,len(doc)) if 'Representing a company’s historical record' in norm(doc[i].get_text()))
    body=list(range(start-1,end+1));nav=list(range(1,8))
    images=render(pdf,sorted(set(body+nav)),OUT/'render')
    sheet=Image.new('RGB',(1000,710),'white');draw=ImageDraw.Draw(sheet)
    for i,n in enumerate(nav):
        im=Image.open(OUT/'render'/f'page-{n:03}.png');im.thumbnail((244,327));x=i%4*250;y=i//4*355
        sheet.paste(im,(x,y+20));draw.text((x+8,y+3),str(n),fill='black')
    p=OUT/'render/navigation.png';sheet.save(p)
    save('render-manifest.json',dict(pdf_path=rel(pdf),pdf_sha256=sha(pdf),pages=len(doc),body_pages=body,navigation_pages=nav,
        images=images,navigation_sheet=dict(path=rel(p),sha256=sha(p))))
    print(json.dumps(dict(pdf_pages=len(doc),body_pages=body,pdf_sha256=sha(pdf))))


if __name__=='__main__':
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1','CPU-only environment required'
    assert not (OUT/'completion.json').exists(),'Frozen: use a new output path'
    action=sys.argv[1];started=datetime.now(timezone.utc);timer=time.monotonic()
    try:
        {'baseline':baseline,'sources':sources,'copy':copy,'build':build,'render':candidate_render}[action]()
    finally:
        with (OUT/'commands.jsonl').open('a') as f:f.write(json.dumps(dict(command='CUDA_VISIBLE_DEVICES=-1 python3 '+rel(Path(__file__))+' '+action,
            started_at=started.isoformat(),wall_seconds=time.monotonic()-timer))+'\n')
