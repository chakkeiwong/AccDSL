"""Check bounded structural section mapping against the role ledger."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os
import re
import time

OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text());rel=lambda p:str(p.relative_to(ROOT))
def main():
    tick=time.monotonic();checks=[];inputs={}
    def ck(n,o):checks.append(dict(id=n,passed=bool(o)))
    def bind(p):inputs[rel(p)]=sha(p);return p
    b=read(bind(OUT/'baseline.json'));prior=ROOT/b['prior_manifest'];pm=read(prior);ck('prior identity',sha(prior)==b['prior_manifest_sha256']==read(prior.with_name('completion.json'))['manifest_sha256'])
    reloc={x['historical_path']:x['preserved_path'] for x in b['pointer_relocations']};inherited={reloc.get(p,p):h for p,h in pm['artifact_hashes'].items()};ck('1965 prior references',len(inherited)==1965 and all(sha(ROOT/p)==h for p,h in inherited.items()))
    inv=read(bind(OUT/'pdf-inventory.json'));anchors=read(bind(OUT/'complete-text-anchors.json'));ledger=read(bind(ROOT/'data/accounting-master/accounting-package-ledger-20261011/package-ledger.json'))
    ck('four inventory rows per role',len(inv)==8 and len(anchors)==4 and len(ledger['records'])==4)
    for y in range(2022,2026):
        sel=next(x for x in inv if x['year']==y and x['role']=='selected_annual');comp=next(x for x in inv if x['year']==y and x['role']=='complete_10k');a=next(x for x in anchors if x['year']==y);row=next(x for x in ledger['records'] if x['period_year']==y)
        ck(f'{y} hashes bound',row['roles']['selected_annual']['sha256']==sel['sha256'] and row['roles']['complete_issuer_10k']['sha256']==comp['sha256'])
        ck(f'{y} complete longer than selected',comp['pages']>sel['pages'])
        required={'form','item1','item1a','item7','item8','item15','signatures'};got={x['label'] for x in a['anchors'] if x['count']>0};ck(f'{y} structural section anchors',required<=got and a['pages']==comp['pages']+1)
        notice=row['roles']['selected_annual']['omission_notice'];excluded=notice['excluded_filing_pages'];ck(f'{y} omission retained',str(y) in notice['excerpt'] and 'form 10-k' in notice['excerpt'].lower() and excluded)
        ck(f'{y} no semantic promotion',row['relationships']['semantic_annotation_status']=='not started' and row['relationships']['selected_byte_available_at'] is None)
    ck('candidate unchanged',sha(ROOT/b['pdf']['path'])==b['pdf']['sha256'])
    result=dict(recorded_at=datetime.now(timezone.utc).isoformat(),passed=sum(x['passed'] for x in checks),failed=sum(not x['passed'] for x in checks),checks=checks,inputs=inputs,checker_sha256=sha(Path(__file__)),wall_seconds=time.monotonic()-tick,evidence_class='structural section anchors only; no semantic completeness or byte admission')
    (OUT/'checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(passed=result['passed'],failed=[x['id'] for x in checks if not x['passed']])))
    assert result['failed']==0
if __name__=='__main__':
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1' and not (OUT/'checks.json').exists();main()
