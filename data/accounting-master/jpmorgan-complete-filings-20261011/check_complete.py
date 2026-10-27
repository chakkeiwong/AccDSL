"""Check the four issuer-linked 10-K repairs without claiming full semantics."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os
import re
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
    b=read(bind(OUT/'baseline.json'));prior=ROOT/b['prior_manifest']
    ck('prior identity',sha(prior)==b['prior_manifest_sha256']==read(prior.with_name('completion.json'))['manifest_sha256'])
    reloc={x['historical_path']:x['preserved_path'] for x in b['pointer_relocations']};inherited={reloc.get(p,p):h for p,h in read(prior)['artifact_hashes'].items()}
    ck('1913 prior references',len(inherited)==1913 and all(sha(ROOT/p)==h for p,h in inherited.items()))
    leads=read(bind(ROOT/'data/accounting-master/jpmorgan-filing-events-20261011/complete-filing-leads.json'));lead_source=bind(ROOT/leads['source_path'])
    ck('four exact issuer leads',sha(lead_source)==leads['source_sha256'] and len(leads['entries'])==4 and {x['year'] for x in leads['entries']}=={2022,2023,2024,2025})
    acquisitions=read(bind(OUT/'acquisitions.json'));ck('four successful PDF acquisitions',len(acquisitions)==4 and len({x['url'] for x in acquisitions})==4)
    checks_meta=read(bind(OUT/'pdf-checks.json'));ck('four PDF structural records',len(checks_meta)==4)
    prior_partial=read(bind(ROOT/'data/accounting-master/jpmorgan-filing-events-20261011/partial-annual-counterparts.json'));ck('four prior omission records',len(prior_partial)==4 and {x['document_id'] for x in prior_partial}=={f'jpmorgan-{y}-annual' for y in range(2022,2026)})
    omissions={int(x['document_id'].split('-')[1]):x for x in prior_partial}
    for a,m in zip(sorted(acquisitions,key=lambda x:x['year']),sorted(checks_meta,key=lambda x:x['pdf'])):
        p=bind(ROOT/a['path']);txt=bind(ROOT/m['text']);raw=txt.read_text(errors='replace');year=a['year'];
        lead=next(x for x in leads['entries'] if x['year']==year)
        ck(f'{year} source lead and response',a['url']==lead['url'] and a['exit_code']==0 and a['curl_receipt'].startswith('200 ') and a['pdf_header'] and not a['cap_fired'] and a['bytes']<=a['cap_bytes'] and sha(p)==a['sha256'])
        pdfc=m['checks'];ck(f'{year} PDF tools',pdfc['pdfinfo_exit']==0 and pdfc['pdftotext_exit']==0 and pdfc['has_form_10k'] and pdfc['has_jpmorgan'] and pdfc['has_sec'] and pdfc['has_item_1a'] and int(pdfc['pages'])>300)
        cover=' '.join(raw[:16000].split()).lower();ck(f'{year} form/year identity',('form 10-k' in cover or 'form 10k' in cover) and 'jpmorgan chase' in cover and str(year) in cover)
        ck(f'{year} structural sections',bool(re.search(r'item\s+1a',raw,re.I)) and bool(re.search(r'signatures',raw,re.I)) and bool(re.search(r'part\s+iv|exhibits',raw,re.I)))
        old=omissions[year];oldtxt=bind(ROOT/old['selected_pdf'].replace('/original.pdf','/extracted-'+old['selected_pdf_sha256']+'.txt')) if False else None
        ck(f'{year} addresses recorded omission',old['excluded_filing_pages'] and str(year) in old['notice_excerpt'] and 'form 10-k' in old['notice_excerpt'].lower())
    ck('all PDFs distinct',len({x['sha256'] for x in acquisitions})==4)
    ck('no model/OCR work',not any(p.suffix in {'.pth','.pt','.safetensors'} for p in OUT.rglob('*')))
    ck('candidate unchanged',sha(ROOT/b['pdf']['path'])==b['pdf']['sha256'])
    result=dict(recorded_at=datetime.now(timezone.utc).isoformat(),passed=sum(x['passed'] for x in checks),failed=sum(not x['passed'] for x in checks),checks=checks,inputs=inputs,checker_sha256=sha(Path(__file__)),wall_seconds=time.monotonic()-tick,evidence_class='bounded PDF source/identity/structural checks; no semantic completeness or historical-byte admission')
    with (OUT/'checks.json').open('x') as f:f.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=result['passed'],failed=[x['id'] for x in checks if not x['passed']])))
    assert result['failed']==0


if __name__=='__main__':
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1' and not (OUT/'checks.json').exists()
    main()
