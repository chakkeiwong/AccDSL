#!/usr/bin/env python3
"""Create a separate Version 2.34 candidate from protected Version 2.33."""
import hashlib
import json
import shutil
from pathlib import Path

out=Path(__file__).resolve().parent
repo=out.parents[2]
base=repo/'docs/design/proposal/manuscript-jpmorgan-commitments-20261012'
cand=repo/'docs/design/proposal/manuscript-historical-credit-loss-20261012'
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
assert sha(base/'accounting-product-proposal.pdf')=='48bce1dae3f6b23b88a540489d064258870250673a57fce0ae681cc7ce598496'
assert not cand.exists(), 'Never overwrite an existing candidate'
sources=[p for p in base.rglob('*') if p.is_file() and p.suffix in {'.tex','.bib','.lark'}]
source_hashes={str(p.relative_to(base)):sha(p) for p in sources}
for p in sources:
    target=cand/p.relative_to(base)
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(p,target)
title=cand/'accounting-product-proposal.tex'
old=title.read_text()
assert old.count('Version 2.33 (proposal candidate) \\quad 11 October 2026')==1
title.write_text(old.replace('Version 2.33 (proposal candidate) \\quad 11 October 2026',
                             'Version 2.34 (proposal candidate) \\quad 12 October 2026'))
chapter=cand/'chapters/15-banking.tex'
old=chapter.read_text()
marker='A commitment to acquire loans makes the time distinction especially clear.'
assert old.count(marker)==1
chapter.write_text(old.replace(marker,(out/'addition.tex').read_text()+marker))
bib=cand/'references.bib'
bib.write_text(bib.read_text().rstrip()+'\n\n'+(out/'bib-addition.bib').read_text())
snapshots=[]
for name in ['docs/plans/accounting-master-checkpoint.md',
             'docs/plans/accounting-master-current.md',
             'docs/plans/accounting-continuation-requirements-20261007.md',
             'data/accounting-master/next-plan.md']:
    p=repo/name
    dst=out/'pointers-before'/p.name
    dst.parent.mkdir(exist_ok=True)
    shutil.copyfile(p,dst)
    snapshots.append({'live':name,'snapshot':str(dst.relative_to(repo)),'sha256':sha(dst)})
baseline={'baseline_pdf':{'path':str((base/'accounting-product-proposal.pdf').relative_to(repo)),
                          'sha256':sha(base/'accounting-product-proposal.pdf'),'pages':173},
          'candidate':str(cand.relative_to(repo)),
          'source_hashes':source_hashes,'pointer_snapshots':snapshots,
          'source_units':['data/accounting-master/asu2016-credit-loss-20261012',
                          'data/accounting-master/asu2018-credit-loss-bridge-20261012',
                          'data/accounting-master/asu2019-credit-loss-chain-20261012',
                          'data/accounting-master/asu2019-05-transition-20261012',
                          'data/accounting-master/asu2019-10-effective-dates-20261012',
                          'data/accounting-master/credit-loss-update-index-20261012']}
(out/'baseline.json').write_text(json.dumps(baseline,indent=2)+'\n')
print(json.dumps({'candidate':baseline['candidate'],'author_sources':len(sources),
                  'controls_preserved':len(snapshots)}))
