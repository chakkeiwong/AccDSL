"""Build a local three-role source ledger without modifying frozen corpus files."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os
import time

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
rel=lambda p:str(p.relative_to(ROOT))


def main():
    tick=time.monotonic();checks=[];inputs={}
    def ck(name,ok):checks.append(dict(id=name,passed=bool(ok)))
    def bind(p):inputs[rel(p)]=sha(p);return p
    b=read(bind(OUT/'baseline.json'));prior=ROOT/b['prior_manifest'];pm=read(prior)
    ck('prior identity',sha(prior)==b['prior_manifest_sha256']==read(prior.with_name('completion.json'))['manifest_sha256'])
    reloc={x['historical_path']:x['preserved_path'] for x in b['pointer_relocations']};inherited={reloc.get(p,p):h for p,h in pm['artifact_hashes'].items()}
    ck('1949 prior references',len(inherited)==1949 and all(sha(ROOT/p)==h for p,h in inherited.items()))
    complete=ROOT/'data/accounting-master/jpmorgan-complete-filings-20261011';acq=read(bind(complete/'acquisitions.json'));pdfchecks=read(bind(complete/'pdf-checks.json'));partial=read(bind(ROOT/'data/accounting-master/jpmorgan-filing-events-20261011/partial-annual-counterparts.json'));events=read(bind(ROOT/'data/accounting-master/jpmorgan-filing-events-20261011/filing-events.json'));leads=read(bind(ROOT/'data/accounting-master/jpmorgan-filing-events-20261011/complete-filing-leads.json'))
    cov=read(bind(ROOT/'data/financial-report-benchmark/coverage.json'))['rows'];frozen={x['document_id']:x for x in cov}
    ck('four source sets retained',len(acq)==len(pdfchecks)==len(partial)==len(leads['entries'])==4 and len(events)==20)
    ledger=[]
    for y in range(2022,2026):
        doc=f'jpmorgan-{y}-annual';selected=frozen[doc];old=next(x for x in partial if x['document_id']==doc);event=next(x for x in events if x['document_id']==doc);a=next(x for x in acq if x['year']==y);pc=next(x for x in pdfchecks if f'jpmorgan-{y}-10k.pdf' in x['pdf']);lead=next(x for x in leads['entries'] if x['year']==y)
        complete_pdf=ROOT/a['path'];complete_text=ROOT/pc['text'];
        row=dict(document_id=doc,issuer_id='jpmorgan',period_year=y,roles=dict(selected_annual=dict(role='selected_annual_counterpart',path=selected['local_path'],sha256=selected['sha256'],source_url=selected['source_url'],source_kind='frozen active corpus version',content_status='partial relative to corresponding Form 10-K',selection_status='accepted selected report; whole-filing semantic closure open',omission_notice=dict(excluded_filing_pages=old['excluded_filing_pages'],excerpt=old['notice_excerpt'],notice_text_offset=old['notice_text_offset'])),complete_issuer_10k=dict(role='complete_issuer_10k_candidate',path=a['path'],sha256=a['sha256'],source_url=a['url'],source_kind='new issuer-linked candidate',content_status='structurally complete Form 10-K candidate',selection_status='source-layer repair candidate; semantic package mapping pending',retrieved_at=a['started_at'],bytes=a['bytes'],pages=pc['meta']['Pages'],pdf_header=a['pdf_header'],structural_checks=pc['checks']),regulator_event=dict(role='regulator_filing_event',accession_number=event['filing_event']['accessionNumber'],form=event['form'],report_date=event['report_period_end'],filing_date=event['filing_event']['filingDate'],acceptance_date_time=event['filing_event']['acceptanceDateTime'],primary_document=event['filing_event']['primaryDocument'],metadata_sources=event['filing_event']['sources'])),relationships=dict(same_issuer=True,same_period=True,complete_candidate_matches_event=True,selected_annual_matches_event=True,selected_annual_complete_filing_equivalence='not checked',complete_candidate_regulator_byte_equivalence='not checked',selected_byte_available_at=None,as_of_admission=False,semantic_annotation_status='not started'),clock_policy=dict(retrieval_clock='recorded for new issuer candidate',filing_clock='SEC filingDate and acceptanceDateTime',publication_clock='not verified',semantic_clock='not established'),frozen_inputs=dict(selected_coverage_row_hash=sha(bind(ROOT/'data/financial-report-benchmark/coverage.json')),original_selected_pdf_preserved=True))
        ck(doc+' role separation',len(row['roles'])==3 and len({row['roles'][k]['role'] for k in row['roles']})==3)
        ck(doc+' selected hash preserved',sha(ROOT/selected['local_path'])==selected['sha256'])
        ck(doc+' complete hash and structure',sha(complete_pdf)==a['sha256'] and pc['checks']['has_form_10k'] and pc['checks']['has_jpmorgan'] and pc['checks']['has_item_1a'])
        ck(doc+' event identity bound',event['form']=='10-K' and event['report_period_end']==f'{y}-12-31' and event['filing_event']['accessionNumber'])
        ck(doc+' byte admission withheld',row['relationships']['selected_byte_available_at'] is None and not row['relationships']['as_of_admission'])
        ledger.append(row)
    frozen_ok=True
    for coverage_row in cov:
        if coverage_row['issuer_id']=='jpmorgan' and sha(ROOT/coverage_row['local_path'])!=coverage_row['sha256']:
            frozen_ok=False
    ck('frozen corpus file hashes unchanged',frozen_ok)
    ck('no frozen corpus writes',not (ROOT/'data/financial-report-benchmark/coverage.json').stat().st_mtime > prior.stat().st_mtime)
    ck('candidate unchanged',sha(ROOT/b['pdf']['path'])==b['pdf']['sha256'])
    (OUT/'package-ledger.json').write_text(json.dumps(dict(schema_version='accdsl.source_package_ledger.v1',created_at=datetime.now(timezone.utc).isoformat(),scope='JPMorgan 2022–2025 annual counterpart, complete issuer 10-K candidate and regulator event',records=ledger),indent=2,ensure_ascii=False)+'\n')
    result=dict(recorded_at=datetime.now(timezone.utc).isoformat(),passed=sum(x['passed'] for x in checks),failed=sum(not x['passed'] for x in checks),checks=checks,inputs=inputs,checker_sha256=sha(Path(__file__)),wall_seconds=time.monotonic()-tick,evidence_class='local source-role ledger; no semantic or historical-byte promotion')
    (OUT/'checks.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n');print(json.dumps(dict(passed=result['passed'],failed=[x['id'] for x in checks if not x['passed']],records=len(ledger))))
    assert result['failed']==0


if __name__=='__main__':
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1' and not (OUT/'checks.json').exists()
    main()
