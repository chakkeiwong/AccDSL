"""Check source positions and declared limits, not independent interpretation."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os
import re
import time

OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
norm=lambda s:' '.join(s.split())
rel=lambda p:str(p.relative_to(ROOT))


def main():
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1'
    assert not (OUT/'checks.json').exists()
    tick=time.monotonic();checks=[];inputs={}
    def bind(p):inputs[rel(p)]=sha(p);return p
    def ck(label,ok):checks.append(dict(id=label,passed=bool(ok)))
    a=read(bind(OUT/'annotations.json'));b=read(bind(OUT/'baseline.json'))
    ledger=read(bind(ROOT/'data/accounting-master/accounting-package-ledger-20261011/package-ledger.json'))
    prior=ROOT/b['prior_manifest'];pm=read(bind(prior));done=read(bind(prior.with_name('completion.json')))
    ck('prior manifest identity',sha(prior)==b['prior_manifest_sha256']==done['manifest_sha256'])
    reloc={r['historical_path']:r['preserved_path'] for r in b['pointer_relocations']}
    inherited={reloc.get(p,p):h for p,h in pm['artifact_hashes'].items()}
    ck('1982 inherited references',len(inherited)==1982 and all((ROOT/p).is_file() and sha(ROOT/p)==h for p,h in inherited.items()))
    ck('unchanged manuscript',sha(ROOT/b['pdf']['path'])==b['pdf']['sha256'])
    ck('four packages and bounded semantic status',len(a['packages'])==4 and not a['full_package_semantics'] and a['author_review_only'])
    quotes={q['id']:q for q in a['quotes']}
    ck('unique quotes',len(quotes)==len(a['quotes']))
    rejected={(r['year'],r['pdf_page']) for r in a['layout_dispositions'] if r['status']=='rejected_for_annotation'}
    ck('full-width crops excluded',len(rejected)==8 and not any(q['mode']=='columns' and (q['year'],q['pdf_page']) in rejected for q in quotes.values()))
    for pack in a['packages']:
        y=pack['year'];old=next(r for r in ledger['records'] if r['period_year']==y)
        ck(f'{y} three roles and clocks preserved',pack['roles']==old['roles'] and pack['clock_policy']==old['clock_policy'] and not pack['as_of_admission'] and pack['selected_byte_available_at'] is None and pack['complete_issuer_byte_available_at'] is None)
        ck(f'{y} PDF identities',all(sha(bind(ROOT/pack['roles'][k]['path']))==pack['roles'][k]['sha256'] for k in ['selected_annual','complete_issuer_10k']))
        q=quotes[f'{y}-signature']['quote'];date=re.search(r'February \d+, \d{4}',q).group()
        ck(f'{y} signature date matches date field only',datetime.strptime(date,'%B %d, %Y').date().isoformat()==pack['roles']['regulator_event']['filing_date'])
        ck(f'{y} conditional funding and risk scope retained',all(t in quotes[f'{y}-parent-funding']['quote'] for t in ['substantially all','if certain capital or liquidity','Board of Directors']) and 'complete set of all potential risks' in quotes[f'{y}-risk-scope']['quote'])
        ck(f'{y} website non-incorporation and proxy distinction', 'not incorporated by reference' in quotes[f'{y}-website-boundary']['quote'] and 'incorporated by reference' in quotes[f'{y}-proxy']['quote'] and '120 days' in quotes[f'{y}-proxy']['quote'])
        ck(f'{y} exhibit filed/furnished distinction','(b) Filed herewith.' in quotes[f'{y}-exhibit-footnotes']['quote'] and '(c) Furnished herewith.' in quotes[f'{y}-exhibit-footnotes']['quote'] and '(c)' in quotes[f'{y}-exhibit32']['quote'])
    text_cache={}
    for q in quotes.values():
        p=bind(ROOT/q['source_text'])
        if p not in text_cache:text_cache[p]=p.read_text()
        body=text_cache[p]
        if q['mode']=='front':
            parts=body.split('\f');raw=parts[q['pdf_page']-3]
            offset=sum(len(t)+1 for t in parts[:q['pdf_page']-3])
        else:raw=body;offset=0
        s=norm(raw)
        old=bind(ROOT/q['original_layout_text']);op=old.read_text().split('\f')[q['pdf_page']-1]
        ok=(sha(p)==q['source_text_sha256'] and sha(old)==q['original_layout_sha256']
            and q['quote']==s[q['normalized_start']:q['normalized_end']]
            and offset==q['page_raw_offset'] and q['pdf_page']-2==q['printed_page']
            and op.rstrip().splitlines()[-1]==q['printed_page_footer']
            and re.search(r'(?<!\d)'+str(q['printed_page'])+r'(?!\d)',q['printed_page_footer']))
        ck(q['id']+' exact source span and printed page',ok)
    ck('assertion and dependency references',all(r['quotes'] and all(x in quotes and quotes[x]['year']==r['year'] for x in r['quotes']) for r in a['assertions']+a['dependencies']))
    ck('unknowns retained with assertions',all(r['unresolved_query'] and r['local_consequence'] and 'pending' in r['acceptance'] for r in a['assertions']))
    ck('no dependency date inferred',all(r['publication_at'] is None and not r['historical_byte_admission'] for r in a['dependencies']))
    ck('segment change is dated',all(t in quotes['2024-segments']['quote'] for t in ['second quarter of 2024','three reportable business']) and 'four major reportable' in quotes['2023-segments']['quote'] and 'Commercial & Investment Bank' in quotes['2025-segments']['quote'])
    ck('2022 unusual plan-year preserved','December 31, 2019' in quotes['2022-exhibit22-1']['quote'])
    r=a['reference_repairs'][0]
    ck('2023 wrong target retained',r['literal_reference_printed_page']==156 and 'commencing on page 156.' in quotes['2023-financial-statement-reference']['quote'] and quotes['2023-wrong-target']['quote']=='Management’s discussion and analysis')
    ck('2023 corrected navigation source-bound',r['actual_auditor_printed_page']==163 and '163–309' in quotes['2023-item8-range']['quote'] and quotes['2023-actual-auditor']['pdf_page']==165 and quotes['2023-actual-auditor']['quote']=='Report of Independent Registered Public Accounting Firm')
    ck('no accounting-conflict promotion',not r['e05_accounting_conflict'] and not r['full_statement_audit'])
    for filename in ['extractions.json','column-extractions.json','reference-repair-extractions.json']:
        receipts=read(bind(OUT/filename))['receipts'];ok=True
        for receipt in receipts:
            p=bind(ROOT/receipt['text']);ok &= sha(p)==receipt['sha256']
            for col in receipt.get('columns',[]):
                p=bind(ROOT/col['text']);ok &= sha(p)==col['sha256'] and col['exit_code']==0
        ck(filename+' retained extraction identities',ok)
    result=dict(recorded_at=datetime.now(timezone.utc).isoformat(),passed=sum(c['passed'] for c in checks),
        failed=sum(not c['passed'] for c in checks),checks=checks,inputs=inputs,
        checker_sha256=sha(Path(__file__)),builder_sha256=sha(OUT/'build_annotations.py'),
        wall_seconds=time.monotonic()-tick,evidence_class='source positions, identities and explicit interpretation limits; author review only')
    (OUT/'checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=result['passed'],failed=[c['id'] for c in checks if not c['passed']])))
    assert result['failed']==0


if __name__=='__main__':main()
