"""Bind SEC filing events, preserving partial annual counterparts and byte gaps."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os
import re
import time

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
CORPUS=ROOT/'data/financial-report-benchmark'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
rel=lambda p:str(p.relative_to(ROOT))


def save(name,value):
    with (OUT/name).open('x') as f:f.write(json.dumps(value,indent=2,ensure_ascii=False)+'\n')


def main():
    tick=time.monotonic();checks=[];inputs={}
    def ck(name,ok):checks.append(dict(id=name,passed=bool(ok)))
    def bind(p):inputs[rel(p)]=sha(p);return p
    base=read(bind(OUT/'baseline.json'));prior=ROOT/base['prior_manifest']
    ck('prior identity',sha(prior)==base['prior_manifest_sha256']==read(prior.with_name('completion.json'))['manifest_sha256'])
    reloc={x['historical_path']:x['preserved_path'] for x in base['pointer_relocations']}
    inherited={reloc.get(p,p):h for p,h in read(prior)['artifact_hashes'].items()}
    ck('1730 prior references',len(inherited)==1730 and all(sha(ROOT/p)==h for p,h in inherited.items()))
    plan=read(bind(OUT/'source-plan.json'));parent_path=bind(ROOT/plan['parent_index']);parent=read(parent_path)
    ck('parent source and issuer',sha(parent_path)==plan['parent_sha256'] and str(parent['cik']).lstrip('0')=='19617' and 'JPMORGAN' in parent['name'].upper())
    attempts=read(bind(OUT/'acquisitions.json'))
    ck('forty exact new routes',len(attempts)==40 and {x['name'] for x in attempts}=={x['name'] for x in plan['files']})
    sources=[(parent_path,parent['filings']['recent'])]
    for a in attempts:
        p=bind(ROOT/a['path']);ck('acquired '+a['name'],a['exit_code']==0 and a['curl_receipt'].startswith('200 ') and sha(p)==a['sha256'] and not a['cap_fired'] and a['bytes']<=a['stream_cap_bytes']==2097152);sources.append((p,read(p)))
    for x in plan['reused_shards']:
        p=bind(ROOT/x['path']);ck('reused '+x['name'],sha(p)==x['sha256']);sources.append((p,read(p)))
    filings={};duplicates=[]
    keys=['accessionNumber','filingDate','reportDate','acceptanceDateTime','form','primaryDocument','primaryDocDescription']
    for p,d in sources:
        ck('parallel fields '+p.name,len({len(d[k]) for k in keys})==1)
        for i,f in enumerate(d['form']):
            if f not in ['10-K','10-Q','10-K/A','10-Q/A']:continue
            row={k:d[k][i] for k in keys};acc=row['accessionNumber'];source=dict(path=rel(p),sha256=sha(p),row_index=i)
            if acc in filings:
                old=filings[acc];ck('duplicate accession agrees '+acc,all(old[k]==row[k] for k in keys));old['sources'].append(source);duplicates.append(acc)
            else:filings[acc]=row|dict(sources=[source])
    cov=read(bind(CORPUS/'coverage.json'))['rows'];results=[];partial=[]
    dates={'annual':('12-31','December 31'),'q1':('03-31','March 31'),'q2':('06-30','June 30'),'q3':('09-30','September 30')}
    exclusions={2022:'1-42, 304',2023:'1-44, 322',2024:'1-48, 334',2025:'1-42, 328'}
    for c in cov:
        if c['issuer_id']!='jpmorgan' or c['period_year'] not in range(2021,2026):continue
        year=c['period_year'];ending,textdate=dates[c['report_class']];period=f'{year}-{ending}';form='10-K' if c['report_class']=='annual' else '10-Q'
        choices=[x for x in filings.values() if x['reportDate']==period and x['form'] in [form,form+'/A']];originals=[x for x in choices if x['form']==form]
        ck(c['document_id']+' one original',len(originals)==1);event=originals[0]
        p=bind(ROOT/c['local_path']);t=bind(ROOT/c['extracted_text_path']);raw=t.read_text();compact=' '.join(raw.split())
        ck(c['document_id']+' retained PDF hash',sha(p)==c['sha256'])
        if c['report_class']=='annual' and year in exclusions:
            m=re.search(r'not included herein',raw,re.I);excerpt=' '.join(raw[max(0,m.start()-250):m.end()+100].split()) if m else ''
            ck(c['document_id']+' exclusion evidence',bool(m) and str(year) in excerpt and 'Form 10-K' in excerpt and exclusions[year] in excerpt)
            relationship='partial-content annual-report counterpart; expressly excludes Form 10-K pages'
            coverage='not a complete Form 10-K';evidence=dict(excluded_filing_pages=exclusions[year],notice_excerpt=excerpt,notice_text_offset=m.start() if m else None)
            partial.append(dict(document_id=c['document_id'],selected_pdf=rel(p),selected_pdf_sha256=sha(p),**evidence,required_repair='Acquire the exact complete filed 10-K or account for every missing component; preserve this annual report separately',claim_blocked='whole-filing coverage and filing-date availability of the entire annual-report PDF'))
        else:
            cover=' '.join(raw[:7000].split());tokens=['JPMorgan Chase & Co.',form,f'{textdate}, {year}']
            ck(c['document_id']+' cover identity',all(s.lower() in cover.lower() for s in tokens))
            relationship='same issuer/form/period on retained cover; no full content comparison';coverage='not established by cover identity';evidence=dict(cover_excerpt=cover[:1150],identity_tokens=tokens)
        results.append(dict(document_id=c['document_id'],issuer_cik='0000019617',form=form,report_period_end=period,filing_event=event,retrieved_amendments=[x for x in choices if x['form'].endswith('/A')],amendment_scope='retrieved metadata through retained current parent; later or missed source updates not excluded',selected_pdf=dict(path=rel(p),sha256=sha(p)),retained_text=dict(path=rel(t),sha256=sha(t)),relationship=relationship,whole_filing_coverage=coverage,identity_evidence=evidence,selected_byte_available_at=None,as_of_admission=False,clock_policy='retain SEC filingDate and acceptanceDateTime separately; no exact public-access or selected-byte date inference'))
    ck('twenty target periods',len(results)==20 and len({x['filing_event']['accessionNumber'] for x in results})==20)
    ck('four partial annual counterparts retained',len(partial)==4 and {x['document_id'] for x in partial}=={f'jpmorgan-{y}-annual' for y in range(2022,2026)})
    ck('all selected-byte admissions withheld',all(x['selected_byte_available_at'] is None and not x['as_of_admission'] for x in results))
    earlier=read(bind(ROOT/'data/accounting-master/publication-evidence-20261011/filing-events.json'))
    ck('32 unique annual/quarterly JPMorgan events combined',len(earlier)+len(results)==32 and len({x['document_id'] for x in earlier+results})==32)
    ck('unchanged candidate',sha(ROOT/base['pdf']['path'])==base['pdf']['sha256'])
    save('filing-events.json',results);save('partial-annual-counterparts.json',partial);save('duplicate-accessions.json',duplicates)
    save('checks.json',dict(recorded_at=datetime.now(timezone.utc).isoformat(),passed=sum(c['passed'] for c in checks),failed=sum(not c['passed'] for c in checks),checks=checks,inputs=inputs,checker_sha256=sha(Path(__file__)),wall_seconds=time.monotonic()-tick,evidence_class='metadata and retained-text identity; no complete filing or historical byte admission'))
    print(json.dumps(dict(passed=sum(c['passed'] for c in checks),failed=[c['id'] for c in checks if not c['passed']],events=len(results),partial_annual_counterparts=len(partial),duplicate_accessions=len(duplicates))))
    assert all(x['passed'] for x in checks)


if __name__=='__main__':
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1' and not (OUT/'checks.json').exists()
    main()
