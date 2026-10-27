"""Verify source identity and bounded notice observations; no legal admission."""
from pathlib import Path
from datetime import datetime, timezone
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
    b=read(bind(OUT/'baseline.json'));prior=ROOT/b['prior_manifest']
    ck('previous manifest identity',sha(prior)==b['prior_manifest_sha256']==read(prior.with_name('completion.json'))['manifest_sha256'])
    reloc={x['historical_path']:x['preserved_path'] for x in b['pointer_relocations']}
    inherited={reloc.get(p,p):h for p,h in read(prior)['artifact_hashes'].items()}
    ck('1595 prior references preserved',len(inherited)==1595 and all(sha(ROOT/p)==h for p,h in inherited.items()))
    records=read(bind(OUT/'acquisitions.json'));ck('twelve unique successful sources',len(records)==12 and len({r['url'] for r in records})==12)
    tree=read(bind(OUT/'sources/craft-tree.json'));ref=read(bind(OUT/'sources/craft-master-ref.json'))
    ck('CRAFT exact complete tree',tree['sha']==ref['object']['sha']=='e332dd8b718e291f51b66ff8f9ef2c98ee4474c8' and not tree['truncated'])
    for r in records:
        p=bind(ROOT/r['path']);raw=p.read_bytes()
        ck('retrieved '+p.name,r['exit_code']==0 and r['curl_receipt'].startswith('200 ') and sha(p)==r['sha256'])
        if 'upstream_path' in r:
            blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
            upstream=next(x['sha'] for x in tree['tree'] if x['path']==r['upstream_path'])
            ck('Git blob '+p.name,blob==upstream==r['computed_blob'])
    license=(OUT/'sources/craft-LICENSE.txt').read_text();body=(OUT/'sources/craft-README.md').read_text()
    ck('NAVER MIT notice retained','Copyright (c) 2019-present NAVER Corp.' in license and 'included in' in license and license.strip() in body)
    ck('three author model links','1Jk4eGD7crsqCCg9C9VjCLkMN3ze8kutZ' in body and 'IC15' in body and 'LinkRefiner' in body)
    assets=read(bind(ROOT/'data/accounting-master/easyocr-assets-20261010/asset-records.json'))
    hub=(OUT/'sources/easyocr-modelhub.txt').read_text();ck('model hub agrees with selected URLs',len(assets)==2 and all(a['url'] in hub for a in assets))
    terms=(OUT/'sources/easyocr-terms-readable.txt').read_text();ck('terms effective date and service clause','Effective: May 19, 2021.' in terms and 'personal, non-commercial use' in terms)
    comment=read(OUT/'sources/craft-issue-105-comments.json');ck('comment authority remains unestablished',len(comment)==1 and comment[0]['author_association']=='NONE')
    ck('CRAFT 161 no returned comments',read(OUT/'sources/craft-issue-161-comments.json')==[])
    narrow=read(OUT/'sources/easyocr-rights-issues.json');wide=read(OUT/'sources/easyocr-license-issues.json')
    ck('search scope retained',narrow['total_count']==0 and wide['total_count']==26 and len(wide['items'])==20 and not wide['incomplete_results'])
    ck('no local model bytes in unit',not any(p.suffix in {'.pth','.pt','.zip','.safetensors'} for p in OUT.rglob('*')))
    ck('candidate unchanged',sha(ROOT/b['pdf']['path'])==b['pdf']['sha256'])
    result=dict(recorded_at=datetime.now(timezone.utc).isoformat(),passed=sum(x['passed'] for x in checks),failed=sum(not x['passed'] for x in checks),checks=checks,inputs=inputs,checker_sha256=sha(Path(__file__)),wall_seconds=time.monotonic()-tick,evidence_class='documentary identity/notice checks; no model-rights admission or runtime evidence')
    with (OUT/'checks.json').open('x') as f:f.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=result['passed'],failed=[x['id'] for x in checks if not x['passed']])))
    assert result['failed']==0


if __name__=='__main__':
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1' and not (OUT/'checks.json').exists()
    main()
