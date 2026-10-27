"""Preserve the full review universe; recording is separate from read-only verification."""
import csv
import hashlib
import json
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
REL=HERE.relative_to(ROOT).as_posix()
INPUTS={
 'assessment':'data/accounting-master/readability-repair-20261022-theta/assessment-successor.json',
 'operations':'data/accounting-master/readability-repair-20261022-theta/operation-successor.json',
 'integrated_coverage':'data/accounting-master/company-authoring-integration-20261023/coverage-delta.json',
 'policy_coverage':'data/accounting-master/company-policy-information-20261023/coverage-delta.json',
 'frontend':'data/accounting-master/company-text-20261023/frontend.py',
 'path_schema':'data/accounting-master/company-operation-path-20261023/schema.json',
 'execution':'data/accounting-master/company-operation-path-20261023/composition.py',
 'core_contract':'docs/design/spec/core-contract.md',
 'core_schema':'docs/design/spec/core-ir.schema.json',
 'language':'docs/design/proposal/manuscript-company-authoring-20261023/chapters/06-language.tex',
 'company':'data/accounting-master/company-composition-20261016/semantic-contract.md',
 'sector':'data/accounting-master/sector-company-composition-20261016/semantic-contract.md',
 'plan':'docs/plans/accounting-language-scope-review-20261023.md',
}
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def read(name): return json.loads((ROOT/name).read_text())
def dump(path,value): path.write_text(json.dumps(value,indent=2)+'\n')
def tsv(name):
 with (HERE/name).open() as stream: return list(csv.DictReader(stream,delimiter='\t'))
def construct():
 a=read(INPUTS['assessment']); o=read(INPUTS['operations'])
 c=read(INPUTS['integrated_coverage']); p=read(INPUTS['policy_coverage'])
 out={'date':'2026-10-23','candidate':'3.53','readiness':'not_ready','whole_rows_closed':0,
      'scope':'Documentary scope review; no full prior-method re-execution or full manuscript reread',
      'source_hashes':{v:sha(ROOT/v) for v in INPUTS.values()}}
 for key, source, filename in [('obligations',a['rows'],'row-decisions.tsv'),('interactions',a['interactions'],'interaction-decisions.tsv'),('operations',o['rows'],'operation-decisions.tsv')]:
  decisions=tsv(filename)
  assert len(decisions)==len({r['id'] for r in decisions})
  assert {r['id'] for r in source}=={r['id'] for r in decisions}
  byid={r['id']:r for r in decisions}
  out[key]=[{'id':r['id'],'prior_record':r,'review':byid[r['id']],'full_requirement_closed':False} for r in source]
 for row in out['obligations']:
  row['integrated_delta']=next(r for r in c['rows'] if r['id']==row['id'])
  row['policy_delta']=next(r for r in p['rows'] if r['id']==row['id'])
 schema=read(INPUTS['path_schema'])
 out['company_operation_kinds']=[r['properties']['kind']['const'] for r in schema['properties']['initial_year']['properties']['operations']['items']['oneOf']]
 out['next_plan']='docs/plans/accounting-company-family-20261023.md'
 return out
def main():
 start=time.monotonic(); recorded='--record' in sys.argv
 assert set(sys.argv[1:]) <= {'--record'}
 inventory=construct(); checks=[]
 def check(name,passed):
  checks.append({'name':name,'passed':bool(passed)})
  assert passed,name
 for key,n in [('obligations',53),('interactions',6),('operations',46)]:
  rows=inventory[key]; check(key+'_count_and_identity',len(rows)==n and len({r['id'] for r in rows})==n)
  for row in rows:
   check(row['id']+'_complete_review',all(isinstance(v,str) and v.strip() for v in row['review'].values()))
   check(row['id']+'_keeps_prior_record',row['prior_record']['id']==row['id'] and not row['full_requirement_closed'])
 check('four_dimensions',all(set(r['review'])=={'id','syntax','semantics','connected_execution','acceptance','residual_and_next'} for r in inventory['obligations']))
 expected={'purchase','delivery','collection','supplier_payment','payroll','dividend','plant_addition','facility_draw','facility_interest','facility_repayment','depreciation','interest','tax','close'}
 check('actual_operation_kinds',set(inventory['company_operation_kinds'])==expected)
 check('no_whole_requirement_closure',inventory['whole_rows_closed']==0 and inventory['readiness']=='not_ready')
 evidence={}
 for row in inventory['operations']:
  for item in row['prior_record']['evidence']:
   check(row['id']+'_prior_evidence_'+item['path'],sha(ROOT/item['path'])==item['sha256'])
   evidence[item['path']]=item['sha256']
 checks_record={'passed':True,'checks':checks,'counts':{k:len(inventory[k]) for k in ['obligations','interactions','operations']},'prior_operation_evidence_files':len(evidence),'interpretation':'Coverage/binding checks; authored classifications are not independently validated'}
 if recorded:
  assert not (HERE/'manifest.json').exists(),'already recorded'
  dump(HERE/'inventory.json',inventory); dump(HERE/'checks.json',checks_record)
  files={str(p.relative_to(ROOT)):sha(p) for p in HERE.iterdir() if p.is_file()}
  dump(HERE/'manifest.json',{'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'command':'CUDA_VISIBLE_DEVICES=-1 python3 '+REL+'/build.py --record','environment':platform.python_version(),'cpu_gpu':'CPU-only documentary validation; GPU intentionally hidden','random_seeds':'N/A: deterministic','data_version':inventory['source_hashes'],'plan':INPUTS['plan'],'result':REL+'/review.md','started_utc':datetime.now(timezone.utc).isoformat(),'wall_seconds':time.monotonic()-start,'files':files,'prior_operation_evidence':evidence})
 else:
  assert read(REL+'/inventory.json')==inventory,'recorded inventory mismatch'
  prior=read(REL+'/checks.json'); assert prior==checks_record
  m=read(REL+'/manifest.json')
  for name,h in m['files'].items(): assert sha(ROOT/name)==h,name
 print(json.dumps({'passed':True,'checks':len(checks_record['checks']),'counts':checks_record['counts'],'prior_operation_evidence_files':len(evidence),'recorded':recorded}))
if __name__=='__main__': main()
