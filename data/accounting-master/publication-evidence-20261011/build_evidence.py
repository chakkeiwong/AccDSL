"""Identify filing events while leaving selected-byte as-of admission open."""
from pathlib import Path
from datetime import datetime, timezone
import collections
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
    b=read(bind(OUT/'baseline.json'));prior=ROOT/b['prior_manifest']
    ck('prior identity',sha(prior)==b['prior_manifest_sha256']==read(prior.with_name('completion.json'))['manifest_sha256'])
    reloc={x['historical_path']:x['preserved_path'] for x in b['pointer_relocations']}
    inherited={reloc.get(f,f):h for f,h in read(prior)['artifact_hashes'].items()}
    ck('1638 prior references',len(inherited)==1638 and all(sha(ROOT/f)==h for f,h in inherited.items()))
    cov=read(bind(CORPUS/'coverage.json'))['rows'];src=read(bind(CORPUS/'resolved-sources.json'))
    log=bind(CORPUS/'acquisition-results.jsonl');versions={}
    for line in log.read_text().splitlines():
        x=json.loads(line)
        if x.get('local_path'):versions[(x['document_id'],x['local_path'])]=x
    inventory=[];dated_alternates=[]
    for c in cov:
        x=versions[(c['document_id'],c['local_path'])];meta=x.get('source_metadata',{})
        dated=[v for v in src.get(c['document_id'],[]) if v.get('publication_date')]
        inventory.append(dict(document_id=c['document_id'],selected_path=c['local_path'],selected_sha256=c['sha256'],selected_date=meta.get('publication_date'),selected_date_status=meta.get('publication_date_status','not_verified'),dated_source_candidates=len(dated)))
        if not meta.get('publication_date') and dated:
            dated_alternates.append(dict(document_id=c['document_id'],selected_source=c['source_url'],candidate_sources=dated,selected_byte_date_transfer='not justified by a date-only join'))
    count=sum(bool(x['selected_date']) for x in inventory)
    ck('56 dated and 136 unverified active records',len(inventory)==192 and count==56)
    ck('ten dated alternate-source slots',len(dated_alternates)==10 and sum(bool(x['dated_source_candidates']) for x in inventory)==66)
    attempts=read(bind(OUT/'acquisitions.json'));live=read(bind(OUT/'live-source-plan.json'));original=read(bind(OUT/'source-plan.json'))
    bind(ROOT/original['parent_index']);parent=read(bind(OUT/'sources/CIK0000019617.json'))
    ck('SEC parent identity',str(parent['cik']).lstrip('0')=='19617' and 'JPMORGAN' in parent['name'].upper())
    ck('14 unique metadata requests',len(attempts)==14 and len({x['url'] for x in attempts})==14)
    all_filings=[];ranges=[]
    for a in attempts:
        p=bind(ROOT/a['path']);d=read(p)
        ck('source '+a['name'],a['exit_code']==0 and a['curl_receipt'].startswith('200 ') and sha(p)==a['sha256'])
        if a['name']=='CIK0000019617.json':continue
        fields=['accessionNumber','filingDate','reportDate','acceptanceDateTime','form','primaryDocument','primaryDocDescription']
        ck('parallel fields '+a['name'],len({len(d[k]) for k in fields})==1)
        for i,f in enumerate(d['form']):
            if f in ['10-K','10-Q','10-K/A','10-Q/A']:
                all_filings.append({k:d[k][i] for k in fields}|dict(source_path=rel(p),source_sha256=sha(p),row_index=i))
        declared=next(x for x in live['files'] if x['name']==a['name'])
        ranges.append(dict(name=a['name'],declared_from=declared['filingFrom'],declared_to=declared['filingTo'],actual_from=min(d['filingDate']),actual_to=max(d['filingDate'])))
    ck('all current planned shards acquired',{x['name'] for x in live['files']}=={x['name'] for x in attempts if 'submissions-' in x['name']})
    stream=[x for x in attempts if 'stream_cap_bytes' in x]
    ck('12 repaired streamed caps respected',len(stream)==12 and all(not x['cap_fired'] and x['bytes']<=x['stream_cap_bytes']==2097152 for x in stream))
    parent_attempt=next(x for x in attempts if x['name']=='CIK0000019617.json')
    ck('oversized initial parent exception retained',parent_attempt['bytes']==4642815 and parent_attempt['bytes']>2097152 and 'stream_cap_bytes' not in parent_attempt)
    result=[]
    enddates={'annual':('12-31','December 31'),'q1':('03-31','March 31'),'q2':('06-30','June 30'),'q3':('09-30','September 30')}
    for c in cov:
        if c['issuer_id']!='jpmorgan' or c['period_year'] not in [2018,2019,2020]:continue
        ending,textdate=enddates[c['report_class']];period=f"{c['period_year']}-{ending}";form='10-K' if c['report_class']=='annual' else '10-Q'
        matches=[x for x in all_filings if x['reportDate']==period and x['form'] in [form,form+'/A']]
        originals=[x for x in matches if x['form']==form]
        ck(c['document_id']+' unique retrieved original',len(originals)==1)
        p=bind(ROOT/c['local_path']);t=bind(ROOT/c['extracted_text_path']);text=t.read_text();compact=' '.join(text[:6500].split())
        tokens=['JPMorgan Chase & Co.',form,f'{textdate}, {c["period_year"]}']
        identity=all(s.lower() in compact.lower() for s in tokens)
        ck(c['document_id']+' retained cover identity and PDF hash',identity and sha(p)==c['sha256'])
        event=originals[0]
        ck(c['document_id']+' accession and date schema',bool(re.fullmatch(r'\d{10}-\d{2}-\d{6}',event['accessionNumber'])) and event['filingDate']>period and bool(event['primaryDocument']))
        result.append(dict(document_id=c['document_id'],issuer_cik='0000019617',form=form,report_period_end=period,filing_event=event,retrieved_amendments=[x for x in matches if x['form'].endswith('/A')],amendment_scope='only retrieved historical date window; later amendments not excluded',selected_pdf=dict(path=rel(p),sha256=sha(p)),retained_text=dict(path=rel(t),sha256=sha(t),cover_excerpt=compact[:1100],identity_tokens=tokens),relationship='same issuer/form/period on retained cover; selected PDF bytes not compared with filed primary document',event_date_status='official SEC filingDate retained',selected_byte_available_at=None,as_of_admission=False,clock_policy='retain filingDate and acceptanceDateTime exactly as returned; neither proves selected PDF earliest public availability'))
    ck('twelve target filing events',len(result)==12 and len({x['filing_event']['accessionNumber'] for x in result})==12)
    ck('twelve selected-byte admissions remain withheld',all(x['selected_byte_available_at'] is None and x['as_of_admission'] is False for x in result))
    ck('candidate unchanged',sha(ROOT/b['pdf']['path'])==b['pdf']['sha256'])
    save('selected-date-inventory.json',inventory);save('dated-alternate-sources.json',dated_alternates);save('filing-events.json',result);save('index-range-observations.json',ranges)
    save('checks.json',dict(recorded_at=datetime.now(timezone.utc).isoformat(),passed=sum(x['passed'] for x in checks),failed=sum(not x['passed'] for x in checks),checks=checks,inputs=inputs,checker_sha256=sha(Path(__file__)),wall_seconds=time.monotonic()-tick,evidence_class='source/identity metadata checks; no selected-byte historical admission'))
    print(json.dumps(dict(passed=sum(x['passed'] for x in checks),failed=[x['id'] for x in checks if not x['passed']],events=len(result),selected_byte_admissions=0)))
    assert all(x['passed'] for x in checks)


if __name__=='__main__':
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1' and not (OUT/'checks.json').exists()
    main()
