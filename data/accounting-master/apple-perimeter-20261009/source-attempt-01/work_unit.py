"""Bounded, CPU-only source and document work; never rerun into frozen outputs."""
from datetime import datetime, timezone
from pathlib import Path
from collections import Counter
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
OLD = ROOT / 'docs/design/proposal/manuscript-segments-20261009'
NEW = ROOT / 'docs/design/proposal/manuscript-perimeter-20261009'
PLAN = ROOT / 'docs/plans/accounting-apple-perimeter-20261009.md'
PRIOR = ROOT / 'data/accounting-master/apple-segments-20261009/run-manifest.json'
SUPP = ROOT / 'docs/design/cases/apple/continuation-20261007/case-supplement-v1.json'
POINTERS = ['docs/plans/accounting-master-checkpoint.md', 'data/accounting-master/next-plan.md',
            'docs/plans/accounting-continuation-requirements-20261007.md', 'docs/plans/accounting-master-current.md']
PAIRS = [
    ('Apple Asia Limited', 'Hong Kong'), ('Apple Asia LLC', 'Delaware, U.S.'),
    ('Apple Canada Inc.', 'Canada'), ('Apple Computer Trading (Shanghai) Co., Ltd.', 'China'),
    ('Apple Distribution International Limited', 'Ireland'), ('Apple India Private Limited', 'India'),
    ('Apple Insurance Company, Inc.', 'Arizona, U.S.'), ('Apple Japan, Inc.', 'Japan'),
    ('Apple Korea Limited', 'South Korea'), ('Apple Operations International Limited', 'Ireland'),
    ('Apple Operations Limited', 'Ireland'), ('Apple Operations Mexico, S.A. de C.V.', 'Mexico'),
    ('Apple Pty Limited', 'Australia'), ('Apple Sales International Limited', 'Ireland'),
    ('Apple South Asia (Thailand) Limited', 'Thailand'), ('Apple Vietnam Limited Liability Company', 'Vietnam'),
    ('Braeburn Capital, Inc.', 'Nevada, U.S.'), ('iTunes K.K.', 'Japan')]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
norm = lambda s: ' '.join(s.split())
relative = lambda p: str(p.relative_to(ROOT))


def save(name, obj):
    p = OUT / name
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('x') as f:
        f.write(json.dumps(obj, indent=2, ensure_ascii=False) + '\n')


def verify(hashes):
    bad = [n for n, h in hashes.items() if not (ROOT/n).is_file() or sha(ROOT/n) != h]
    assert not bad, bad


def render(pdf, pages, directory):
    doc = fitz.open(pdf)
    directory.mkdir(parents=True, exist_ok=True)
    records = []
    for n in pages:
        p = directory / f'page-{n:03}.png'
        assert not p.exists(), p
        doc[n-1].get_pixmap(matrix=fitz.Matrix(1.65, 1.65)).save(p)
        records.append(dict(page=n, path=relative(p), sha256=sha(p)))
    return records


def baseline():
    prior = read(PRIOR)
    completion = read(PRIOR.parent/'completion.json')
    assert sha(PRIOR) == completion['manifest_sha256']
    assert prior['pdf']['pages'] == 152 and prior['full_readiness'] == 'not_ready'
    verify(prior['artifact_hashes'])
    assert sha(ROOT/prior['pdf']['path']) == prior['pdf']['sha256']
    protected = {relative(p): sha(p) for base in [PRIOR.parent, OLD] for p in base.rglob('*')
                 if p.is_file() and '__pycache__' not in p.parts}
    for name in ['MISSION_CONTROL.md', 'docs/plans/accounting-mission-requirements.md',
                 'docs/plans/accounting-product-design-checkpoint.md', 'scripts/accounting_master_catalog.json',
                 'docs/plans/accounting-apple-segments-20261009.md']:
        protected[name] = sha(ROOT/name)
    preserved = []
    for name in POINTERS:
        dst = OUT/'pointers-before'/name
        dst.parent.mkdir(parents=True, exist_ok=True)
        assert not dst.exists()
        shutil.copy2(ROOT/name, dst)
        preserved.append(dict(historical_path=name, preserved_path=relative(dst), sha256=sha(dst)))
    ancestor_counts = {}
    for name in ['apple-segments-20261009', 'apple-liquidity-20261009', 'apple-debt-20261009']:
        hashes = read(ROOT/'data/accounting-master'/name/'baseline.json')['protected_hashes']
        verify(hashes)
        ancestor_counts[name] = len(hashes)
    history = read(ROOT/'data/accounting-master/direct-p19-20261007/recovery-entry-v1.json')
    history_counts = {}
    for key in ['protected_hashes', 'upstream_reference_hashes', 'controller_hashes']:
        verify(history[key])
        history_counts[key] = len(history[key])
    p19 = read(ROOT/'data/accounting-master/continuation-20261007/baseline-manifest.json')
    reloc = {r['historical_path']:r['preserved_path'] for r in p19['relocations']}
    verify({reloc.get(p,p): h for p,h in p19['p19_historical_artifact_hashes'].items()})
    pages = render(OLD/'accounting-product-proposal.pdf', [26,27,28], OUT/'baseline-render')
    save('baseline.json', dict(recorded_at=datetime.now(timezone.utc).isoformat(),
        git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        protected_hashes=protected, pointer_relocations=preserved, prior_manifest=relative(PRIOR),
        prior_manifest_sha256=sha(PRIOR), prior_manifest_references=len(prior['artifact_hashes']),
        ancestor_counts=ancestor_counts, history_counts=history_counts, baseline_pages=pages,
        baseline_pdf=prior['pdf'], worktree='Pre-existing dirty files preserved; no broad staging or controller'))
    print(json.dumps(dict(protected_files=len(protected), prior_manifest_references=len(prior['artifact_hashes']),
                         ancestor_counts=ancestor_counts, history_counts=history_counts)))


def sources():
    d = read(SUPP)
    source_records = {k:d['sources'][k] for k in ['annual','interim']}
    inputs = {relative(SUPP):sha(SUPP)}
    texts = {}
    for k,s in source_records.items():
        for kind in ['original','extraction']:
            p = ROOT/s[kind+'_path']
            assert sha(p) == s[kind+'_sha256'], p
            inputs[relative(p)] = sha(p)
        texts[k] = (ROOT/s['extraction_path']).read_text()
    checks = []
    def check(label, ok, detail=None):
        checks.append(dict(id=label, passed=bool(ok), detail=detail))
    spans = {}
    annual = fitz.open(ROOT/source_records['annual']['original_path'])
    annual_texts = [norm(p.get_text()) for p in annual]
    def span(key, source, opening, ending, start_at=0):
        s = texts[source]
        a = s.index(opening, start_at)
        b = s.index(ending, a+len(opening))
        q = s[a:b].rstrip()
        b = a+len(q)
        p = OUT/'sources'/(key+'.txt')
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open('x') as f:f.write(q+'\n')
        pages = []
        if source == 'annual':
            # The extraction uses a form feed at every PDF page boundary.
            pages = list(range(s.count('\f',0,a)+1, s.count('\f',0,b)+2))
            pages = [n for n in pages if 1 <= n <= len(annual)]
        row = dict(source_id=source, start=a, end=b, offset_unit='Unicode code points', quote=q,
                   span_sha256=hashlib.sha256(q.encode()).hexdigest(), source_pages=pages,
                   retained_span=relative(p), **source_records[source])
        spans[key] = row
        check(key+' roundtrip',texts[source][a:b]==q)
        return q
    an = span('annual.note.1','annual','Note 1 – Summary of Significant Accounting Policies','Note 2 – Revenue')
    it = span('interim.note.1','interim','Note 1 –','Note 2 –')
    frontier = next(r for r in d['reference_frontier'] if r['id']=='annual.exhibit.21.1')
    ts = frontier['target_span'];q = texts['annual'][ts['start']:ts['end']]
    check('previously retained exhibit span', hashlib.sha256(q.encode()).hexdigest()==ts['span_sha256'])
    exhibit = span('annual.exhibit.21.1','annual','Exhibit 21.1\n','\f',ts['start']-1)
    check('exhibit substantive span is within prior locator',ts['start']==spans['annual.exhibit.21.1']['start'] and spans['annual.exhibit.21.1']['end']<ts['end'])
    span('annual.company_definition','annual','Unless otherwise stated, all information presented herein','PART I')
    span('annual.business_segments','annual','Segments\nThe Company manages','Markets and Distribution')
    span('annual.distribution','annual','Markets and Distribution\n','Competition\n')
    span('annual.outsourcing_risk','annual','The Company depends on component and product manufacturing','Future operating results depend')
    span('annual.tax_jurisdiction_risk','annual','The Company is subject to changes in tax rates','The Company is also subject to the examination')
    span('annual.manufacturing_mda','annual','Manufacturing Purchase Obligations\n','Other Purchase Obligations\n')
    span('annual.state_aid_mda','annual','State Aid Decision Tax Payable\n','Capital Return Program\n')
    span('annual.fx_mda','annual','Foreign Exchange Rate Risk\n','The Company applied a value-at-risk',texts['annual'].index('Item 7A.   Quantitative',100000))
    span('annual.state_aid_branches','annual','European Commission State Aid Decision\n','Provision for Income Taxes and Effective Tax Rate\n')
    span('annual.segment_attribution','annual','Note 13 – Segment Information','The following table shows information by reportable segment:')
    note_units = [
        ('annual.basis','annual.note.1','Basis of Presentation and Preparation','The Company’s fiscal year',
         'Consolidated Apple Inc. and wholly owned subsidiary scope; management estimates and comparative reclassification.',
         'A01/A03 retained dependencies; dated immediate control graph and actual entity books not supplied.'),
        ('annual.calendar','annual.note.1','The Company’s fiscal year','Revenue\n',
         'Last Saturday September, 52/53-week calendar; FY2023 extra week, FY2024/2022 52 weeks.',
         'A02 retained; entity control dates and contract calendars require separate facts.'),
        ('annual.revenue','annual.note.1','Revenue\n','Share-Based Compensation\n',
         'Revenue excludes customer taxes remitted to governmental authorities.', 'Prior revenue unit dependency; tax amounts and legal seller identities not allocated.'),
        ('annual.compensation','annual.note.1','Share-Based Compensation\n','Cash Equivalents\n',
         'Straight-line expense for estimated awards ultimately vesting.', 'Prior EPS/compensation unit; actual cohorts/operative award methods unresolved.'),
        ('annual.cash','annual.note.1','Cash Equivalents\n','Marketable Securities\n',
         'Highly liquid investments, three months or less at purchase.', 'Prior liquidity unit; functional currency and entity allocation absent.'),
        ('annual.securities','annual.note.1','Marketable Securities\n','Inventories\n',
         'Specific identification of cost of securities sold.', 'Prior liquidity unit; lots/counterparties and entity allocation absent.'),
        ('annual.inventory','annual.note.1','Inventories\n','Property, Plant and Equipment\n',
         'FIFO measurement.', 'Prior asset unit; actual lots and intra-group transfers absent.'),
        ('annual.ppe','annual.note.1','Property, Plant and Equipment\n','Derivative Instruments\n',
         'Straight-line depreciation.', 'Prior asset unit; lives, location/custody/ownership and entity books absent.'),
        ('annual.derivatives','annual.note.1','Derivative Instruments\n','Income Taxes\n',
         'Gross fair-value presentation of derivative assets/liabilities.', 'Debt/liquidity dependencies; complete derivative/OCI note reading remains next internal work.'),
        ('annual.tax','annual.note.1','Income Taxes\n','Leases\n',
         'Certain deferred taxes relate to TCJA minimum tax on foreign earnings.', 'Prior tax unit; entity tax residence/bases and allocation absent.'),
        ('annual.leases','annual.note.1','Leases\n',None,
         'Combine lease/nonlease components for corporate/data-center/retail facilities.', 'Prior commitment unit; actual lessees/contracts/operative policy remain required.'),
        ('interim.basis','interim.note.1','Basis of Presentation and Preparation','The Company’s fiscal year',
         'Wholly-owned condensed consolidated scope; management normal-recurring adjustment opinion, estimates and annual incorporation.',
         'I01 retained; no updated subsidiary list or entity control history supplied by this note.'),
        ('interim.calendar','interim.note.1','The Company’s fiscal year',None,
         'Last Saturday September calendar and 52-week FY2025/FY2024.', 'I02 retained; no control-history inference from unchanged calendar.')]
    units = []
    for ident,parent,opening,ending,meaning,residual in note_units:
        full = spans[parent];a=full['quote'].index(opening)
        b=full['quote'].index(ending,a+len(opening)) if ending else len(full['quote'])
        sub=full['quote'][a:b].strip()
        off=a+len(full['quote'][a:b])-len(full['quote'][a:b].lstrip())
        units.append(dict(id=ident,parent=parent,start=full['start']+off,end=full['start']+off+len(sub),
                          quote=sub,meaning=meaning,remaining=residual,disposition='source meaning/dependency retained; author interpretation, no human admission'))
        check(ident+' exact partition span',texts[full['source_id']][units[-1]['start']:units[-1]['end']]==sub)
        if full['source_id']=='annual':
            check(ident+' matches original PDF',norm(sub) in ' '.join(annual_texts[n-1] for n in full['source_pages']))
    # Each heading begins exactly one policy unit; no body text may be skipped between units.
    for parent in ['annual.note.1','interim.note.1']:
        group=[u for u in units if u['parent']==parent]
        check(parent+' partition body coverage', all(not texts[spans[parent]['source_id']][u['end']:v['start']].strip() for u,v in zip(group,group[1:]))
              and not texts[spans[parent]['source_id']][group[-1]['end']:spans[parent]['end']].replace('Apple Inc. | 2024 Form 10-K | 34','').strip())
    extracted=[]
    for line in exhibit.splitlines():
        parts=re.split(r'\s{2,}',line.strip())
        if len(parts)==2 and (parts[0].startswith('Apple ') or parts[0].startswith('Braeburn') or parts[0]=='iTunes K.K.'):
            extracted.append(tuple(parts))
    check('complete eighteen-row extraction',extracted==PAIRS)
    pdf_lines=[norm(s) for s in annual[113].get_text().splitlines() if norm(s)]
    start=pdf_lines.index(PAIRS[0][0]);flat=[s for pair in PAIRS for s in pair]
    check('complete original table positional order',pdf_lines[start:start+36]==flat)
    entities=[]
    for i,(name,jurisdiction) in enumerate(PAIRS,1):
        check('entity '+str(i)+' original pair',pdf_lines[start+2*(i-1):start+2*i]==[name,jurisdiction])
        entities.append(dict(id=f'listed-{i:02}',name=name,incorporation_jurisdiction=jurisdiction,
            source='annual.exhibit.21.1',row=i,report_period_end='2024-09-28',
            relationship='issuer reports subsidiary of Apple Inc.; general wholly-owned consolidation assertion retained separately',
            immediate_parent=None,ownership_class=None,control_effective_interval=None,
            functional_currency=None,tax_residence=None,segment_assignment=None,intercompany_relationships=None,
            identity_status='exact filing name; no registry identifier or name-based external match'))
    foot='Pursuant to Item 601(b)(21)(ii) of Regulation S-K, the names of other subsidiaries of Apple Inc. are omitted because, considered in the aggregate, they would not constitute a significant subsidiary as of the end of the year covered by this report.'
    check('complete omission footnote in extraction',foot in norm(exhibit))
    check('complete omission footnote in original PDF',foot in norm(annual[113].get_text()))
    check('annual wholly-owned scope', 'include the accounts of Apple Inc. and its wholly owned subsidiaries.' in norm(an))
    check('interim wholly-owned scope', 'include the accounts of Apple Inc. and its wholly owned subsidiaries' in norm(it))
    original_html=BeautifulSoup((ROOT/source_records['interim']['original_path']).read_text(),'html.parser')
    html_text=norm(original_html.get_text(' ',strip=True))
    for u in [u for u in units if u['parent']=='interim.note.1']:
        check(u['id']+' original HTML meaning/text',norm(u['quote']) in html_text)
    check('fourteen distinct jurisdiction labels',len(Counter(j for _,j in PAIRS))==14)
    check('four Ireland rows',Counter(j for _,j in PAIRS)['Ireland']==4)
    check('two Japan rows',Counter(j for _,j in PAIRS)['Japan']==2)
    check('no Singapore exhibit row',all(j!='Singapore' for _,j in PAIRS))
    check('Singapore subsidiaries in source risk', 'including Ireland and Singapore, where a number of the Company’s subsidiaries are organized.' in norm(spans['annual.tax_jurisdiction_risk']['quote']))
    check('India included in Europe source definition','as well as India, the Middle East and Africa.' in norm(spans['annual.business_segments']['quote']))
    check('general customer attribution retained','generally based on the location of customers and retail stores' in norm(spans['annual.segment_attribution']['quote']))
    check('outsourced manufacturing qualifier','Substantially all of the Company’s manufacturing is performed in whole or in part by outsourcing partners' in norm(spans['annual.outsourcing_risk']['quote']))
    check('partner-held equipment is disclosed','much of which is held at certain of its outsourcing partners' in norm(spans['annual.outsourcing_risk']['quote']))
    check('direct/indirect channels preserved','38% and 62%' in norm(spans['annual.distribution']['quote']))
    check('Irish branches do not identify named entities','Irish branches of two subsidiaries' in norm(spans['annual.state_aid_branches']['quote']) and all(name not in spans['annual.state_aid_branches']['quote'] for name,_ in PAIRS))
    check('FX passage describes group exposure, not entity currency','net receiver of currencies other than the U.S. dollar' in norm(spans['annual.fx_mda']['quote']))
    queries = [
        ('consolidated scope','source-supported','Accounts of Apple Inc. and wholly owned subsidiaries; estimates/qualifications retained. Not an independently reconstructed graph.'),
        ('named subsidiary/jurisdiction','source-supported','Eighteen exact name/jurisdiction assertions. No registry identifiers or inference of all subsidiaries.'),
        ('complete group enumeration','not identified','Footnote omits others; Singapore risk confirms organized subsidiaries outside displayed jurisdiction rows; names/count unresolved.'),
        ('immediate ownership/control history','not identified','General wholly-owned membership does not specify direct versus indirect ownership, share classes or dated control events.'),
        ('legal seller/segment mapping','not identified','Customer geography and direct/indirect channel statistics do not identify legal sellers or associate a company with all sales in its incorporation jurisdiction.'),
        ('outsourcing/custody/control','not identified','Equipment custody and manufacturing relationship do not establish corporate control of a partner or location of entity ownership.'),
        ('entity tax and branches','not identified','Organization jurisdiction/risk and unnamed historic Irish branches do not identify current entity tax residence, branch map or tax bases.'),
        ('functional currency and FX','not identified','Group presentation/FX receipts do not assign entity functional currencies or currency exposures.'),
        ('intercompany elimination and dated views','not identified','Need matched legal entity books, counterparties, event/control dates, compatible accounting bases and applicable operative US GAAP methods.')]
    record=dict(recorded_at=datetime.now(timezone.utc).isoformat(),sources=source_records,
        notes={k:spans[k] for k in ['annual.note.1','interim.note.1']},exhibit=spans['annual.exhibit.21.1'],
        prior_frontier_identity=frontier['id'], prior_frontier_status=frontier['semantic_status'],
        material_units=units,entities=entities,omission_footnote=foot,
        dependencies={k:v for k,v in spans.items() if k not in ['annual.note.1','interim.note.1','annual.exhibit.21.1']},
        queries=[dict(id=k,status=status,consequence=c) for k,status,c in queries],
        acceptance='bounded author source preparation; no human admission, full-package closure or operative-authority verification')
    save('source-claim-supplement.json',record)
    # Preserve original annual readings and an explicitly derived complete interim Note 1 view.
    pages=sorted({n for s in spans.values() if s['source_id']=='annual' for n in s['source_pages']})
    images=render(ROOT/source_records['annual']['original_path'],pages,OUT/'source-render/annual')
    view='<h1>Apple FY2025 Q1 — derived Note 1 reading view</h1><p>Local reflow of pinned SEC HTML, not original pagination.</p><p>'+html.escape(it).replace('\n','<br>')+'</p>'
    hp=OUT/'sources/interim-note1-print.html';hp.write_text(view)
    dp=OUT/'source-render/interim-note1-derived.pdf'
    story=fitz.Story(html=view,user_css='body{font-family:serif;font-size:11pt}h1{font-size:16pt}')
    writer=fitz.DocumentWriter(str(dp));page=fitz.paper_rect('a4');where=page+(40,40,-40,-40)
    more=True;count=0
    while more:
        count+=1
        assert count<=3,'Unexpected derived-page count'
        dev=writer.begin_page(page);more,_=story.place(where);story.draw(dev);writer.end_page()
    writer.close()
    images+=render(dp,list(range(1,count+1)),OUT/'source-render/interim')
    save('source-render-receipt.json',dict(annual_pages=pages,derived_pages=count,rendered_images=images,
        annual_sha256=sha(ROOT/source_records['annual']['original_path']),interim_original_sha256=sha(ROOT/source_records['interim']['original_path']),
        source_supplement_sha256=sha(OUT/'source-claim-supplement.json'),derived_html=relative(hp),derived_html_sha256=sha(hp),
        derived_pdf=relative(dp),derived_pdf_sha256=sha(dp)))
    report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),checker_sha256=sha(Path(__file__)),inputs=inputs,
        checks=checks,passed=sum(r['passed'] for r in checks),failed=sum(not r['passed'] for r in checks),
        note_units=len(units),dependency_spans=len(record['dependencies']),entity_pairs=len(entities),queries=len(queries),
        scope='Finite source/position/meaning checks; no completeness or acceptance score')
    save('source-checks.json',report)
    print(json.dumps({k:report[k] for k in ['passed','failed','note_units','dependency_spans','entity_pairs','queries']}))
    assert report['failed']==0,[r for r in checks if not r['passed']]


def copy():
    assert read(OUT/'source-checks.json')['failed']==0
    assert not NEW.exists(),'Preserve existing candidate'
    copied={}
    for p in sorted(OLD.rglob('*')):
        if p.is_file() and p.suffix in {'.tex','.bib','.lark'}:
            dst=NEW/p.relative_to(OLD);dst.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(p,dst);copied[relative(dst)]=sha(dst)
    save('candidate-copy-receipt.json',dict(baseline=relative(OLD),candidate=relative(NEW),copied_hashes=copied))
    print(json.dumps(dict(copied_sources=len(copied))))


def build():
    attempt=1
    while (OUT/f'build-{attempt:02}').exists():attempt+=1
    assert attempt<=3,'Build budget exhausted: diagnose before revising plan'
    run=OUT/f'build-{attempt:02}';run.mkdir()
    cache=Path('/tmp/accdsl-perimeter-tex-cache-20261009');cache.mkdir(exist_ok=True)
    env=dict(CUDA_VISIBLE_DEVICES='-1',TEXMFVAR=str(cache),TEXMFCACHE=str(cache))
    command=['latexmk','-lualatex','-interaction=nonstopmode','-halt-on-error','accounting-product-proposal.tex']
    start=time.monotonic()
    with (run/'build.log').open('w') as log:
        try:code=subprocess.run(command,cwd=NEW,env={**os.environ,**env},stdout=log,stderr=subprocess.STDOUT,timeout=240).returncode
        except subprocess.TimeoutExpired:code=124
    pdf=NEW/'accounting-product-proposal.pdf'
    save(f'build-{attempt:02}/receipt.json',dict(command=command,cwd=relative(NEW),environment=env,exit_code=code,
        wall_seconds=time.monotonic()-start,log_sha256=sha(run/'build.log'),pdf_sha256=sha(pdf) if pdf.exists() else None))
    print(json.dumps(dict(attempt=attempt,exit_code=code,wall_seconds=time.monotonic()-start,pdf_sha256=sha(pdf) if pdf.exists() else None)))
    assert code==0


def candidate_render():
    pdf=NEW/'accounting-product-proposal.pdf';doc=fitz.open(pdf)
    # Determine the complete new section and its immediate adjacent pages from body headings.
    heading='From geographic sales to legal entities'
    hits=[i+1 for i,p in enumerate(doc) if heading in norm(p.get_text()) and '2.' in p.get_text()]
    start=max(hits)
    end=next(i+1 for i in range(start,len(doc)) if 'Representing a company’s historical record' in norm(doc[i].get_text()))
    body=list(range(start-1,end+1));nav=list(range(1,8))
    images=render(pdf,sorted(set(body+nav)),OUT/'render')
    sheet=Image.new('RGB',(1000,710),'white');draw=ImageDraw.Draw(sheet)
    for i,n in enumerate(nav):
        p=OUT/'render'/f'page-{n:03}.png';im=Image.open(p);im.thumbnail((244,327))
        x=(i%4)*250;y=(i//4)*355;sheet.paste(im,(x,y+20));draw.text((x+8,y+3),str(n),fill='black')
    sp=OUT/'render/navigation.png';sheet.save(sp)
    save('render-manifest.json',dict(pdf_path=relative(pdf),pdf_sha256=sha(pdf),pages=len(doc),body_pages=body,
        navigation_pages=nav,rendered_images=images,navigation_sheet=dict(path=relative(sp),sha256=sha(sp))))
    print(json.dumps(dict(pdf_pages=len(doc),body_pages=body,navigation_pages=nav,pdf_sha256=sha(pdf))))


if __name__=='__main__':
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1','CPU-only environment required'
    assert not (OUT/'completion.json').exists(),'Unit frozen: use a new output path'
    started=datetime.now(timezone.utc);timer=time.monotonic()
    action=sys.argv[1]
    actions={'baseline':baseline,'sources':sources,'copy':copy,'build':build,'render':candidate_render}
    try:
        actions[action]()
    finally:
        log=OUT/'commands.jsonl'
        with log.open('a') as f:f.write(json.dumps(dict(command='CUDA_VISIBLE_DEVICES=-1 python3 '+relative(Path(__file__))+' '+action,
            started_at=started.isoformat(),wall_seconds=time.monotonic()-timer))+'\n')
