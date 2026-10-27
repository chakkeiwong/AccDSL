#!/usr/bin/env python3
"""Close the Version 2.28 bounded manuscript integration."""
from __future__ import annotations
import hashlib,json,time
from pathlib import Path
import fitz
ROOT=Path(__file__).resolve().parents[3]; OUT=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 t=time.monotonic(); checks=[]
 def ck(name,ok): checks.append({'check':name,'passed':bool(ok)})
 pdf=ROOT/'docs/design/proposal/manuscript-jpmorgan-terms-20261011/accounting-product-proposal.pdf'; baseline=ROOT/'docs/design/proposal/manuscript-jpmorgan-guarantees-20261011/accounting-product-proposal.pdf'
 ck('candidate PDF bound',sha(pdf)=='23c4e9dd0df82a62cdfa4dcf76716f19cee7b8f47d3c50d588c66cc61791f6ab' and len(fitz.open(pdf))==169)
 ck('Version 2.27 protected',sha(baseline)=='933091db38e0006a0124418150b3115b608780b777aee7dfc94ba270eb77a3f0')
 ms=json.loads((OUT/'manuscript-checks.json').read_text()); ck('112 manuscript checks',ms['passed']==112 and ms['failed']==0)
 rm=json.loads((OUT/'render-manifest.json').read_text()); ck('nine renders bound',rm['pdf_sha256']==sha(pdf) and len(rm['images'])==9 and all(sha(ROOT/x['path'])==x['sha256'] for x in rm['images']))
 terms=json.loads((ROOT/'data/accounting-master/jpmorgan-instrument-terms-20261011/terms.json').read_text()); ck('source 48/0',terms['passed']==48 and terms['failed']==0)
 run=json.loads((OUT/'run-manifest.json').read_text()); ck('run manifest binds source and four controls',run['source_unit']['checks']==48 and len(run['controls'])==4 and all((ROOT/p).is_file() and sha(ROOT/p)==h for p,h in run['controls'].items()))
 base=json.loads((OUT/'baseline.json').read_text()); ck('four controls preserved before update',len(base['pointer_relocations'])==4 and all((ROOT/x['preserved_path']).is_file() and sha(ROOT/x['preserved_path'])==x['sha256'] for x in base['pointer_relocations']))
 for name in ['result.md','author-review.md','four-ledger-review.md','next-source-frontier.md','run-manifest.json','manuscript-checks.json','render-manifest.json','baseline.json','build-run.json']: ck('artifact '+name,(OUT/name).is_file())
 report={'recorded_at':'2026-10-11','candidate_pdf':{'path':str(pdf.relative_to(ROOT)),'sha256':sha(pdf),'pages':169},'checks':checks,'passed':sum(x['passed'] for x in checks),'failed':sum(not x['passed'] for x in checks),'wall_seconds':time.monotonic()-t,'scope':'Version 2.28 manuscript integration closeout; no accounting, legal, independent-reader or full-readiness claim.'}
 manifest_sha=sha(OUT/'run-manifest.json'); report['run_manifest_sha256']=manifest_sha
 (OUT/'closeout-checks.json').write_text(json.dumps(report,indent=2)+'\n'); (OUT/'completion.json').write_text(json.dumps({'recorded_at':'2026-10-11','status':'closed_bounded_integration','candidate_pdf':report['candidate_pdf'],'focused_checks':112,'closeout_checks':report['passed'],'run_manifest_sha256':manifest_sha,'readiness':'not_ready','independent_reader':'pending','domain_acceptance':'pending','legal_acceptance':'pending','next_frontier':'data/accounting-master/accounting-proposal-v228-integration-20261011/next-source-frontier.md'},indent=2)+'\n'); print(json.dumps({k:report[k] for k in ['passed','failed','wall_seconds']})); raise SystemExit(1 if report['failed'] else 0)
if __name__=='__main__': main()
