from pathlib import Path
from hashlib import sha256
from copy import deepcopy
from datetime import datetime,timezone
import json,time,sys,platform,os
import compose
import independent_check
H=Path(__file__).resolve().parent;R=H.parents[2];B=H.parent
def read(p):return json.loads(p.read_text())
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def main():
 out=H/'attempt-01';out.mkdir(exist_ok=False);start=time.monotonic();checks=[];lock={}
 def check(ok,name):checks.append(dict(name=name,passed=bool(ok)));assert ok,name
 for folder,file,field in [('retained-population-overlap-20261025','manifest.json','inputs'),('debt-dash-source-20261027','attempt-01/source-lock.json',None)]:
  p=B/folder/file;lock[str(p.relative_to(R))]=sha(p);data=read(p);data=data[field] if field else data
  for n,h in data.items():check(sha(R/n)==h,'prior_input:'+n);lock[n]=h
 source=B/'retained-population-overlap-20261025/exchanges.json';rs=B/'debt-dash-source-20261027/attempt-01/reading.json'
 for p in [source,rs,H/'compose.py',H/'independent_check.py',Path(__file__),R/'docs/plans/accounting-debt-reading-network-20261027.md']:lock[str(p.relative_to(R))]=sha(p)
 cases=read(source);old=next(x for x in cases if x['name']=='full_source_dash');parent=old['result']['source_result'];budget=old['budget'];reading=read(rs);rounding=old['source_request']['rounding_hypothesis']
 before=compose.digest([parent,reading,rounding,budget]);result=compose.assess(parent,reading,rounding,budget)
 dump(out/'full-result.json',result)
 check(result['status']=='conditionally_feasible','full_selected_conjunction')
 check(len(result['definition']['observations'])==236 and len(result['definition']['relations'])==101,'full_selection_preserved')
 check(result['source_parent']==parent,'complete_original_parent')
 check(result['source_parent']['preserved_report']==parent['preserved_report'],'all_source_dispositions')
 check(result['definition']['relations']==parent['definition']['relations'],'all_original_equations')
 check(result['interpretation']['original']['interval'] is None,'original_dash_interval_remains_unknown')
 check(compose.digest([parent,reading,rounding,budget])==before,'inputs_unmodified')
 witness=result['assessment']['joint_assessment']['witness'];first=independent_check.check(result['definition'],witness)
 check(first==dict(complete_values=236,checked_intervals=236,checked_equations=101),'independent_full_witness')
 # A separate explanatory restriction is never inserted into the original source.
 extra=deepcopy(result['definition']);typ=deepcopy(extra['observations'][compose.OBS]['type']['value_type'])
 extra['relations'].append(dict(id='diagnostic_nonzero_issuance',kind='same_time',terms=[dict(observation=compose.OBS,coefficient='1/1')],rhs='1/4',identity_premise=dict(id='diagnostic_nonzero_issuance',status='proposed',meaning='An explanatory witness request sets latent issuance to 1/4 USD million within its declared rounded-zero interval; no issuer fact.')))
 alt=compose.temporal.assess(extra,budget);dump(out/'nonzero-diagnostic.json',alt)
 check(alt['status']=='conditionally_feasible','nonzero_issuance_still_possible')
 aw=alt['joint_assessment']['witness'];independent_check.check(extra,aw);independent_check.check(result['definition'],aw)
 check(aw[compose.OBS]=='1/4','nonzero_witness_value')
 controls=[]
 def case(name,p,r,rounding,b,expected):
  value=compose.assess(p,r,rounding,b);check(value['status']==expected,name);controls.append(dict(name=name,expected=expected,result=value));return value
 case('missing_reading',parent,None,rounding,budget,'unresolved')
 case('missing_rounding',parent,reading,None,budget,'unresolved')
 bad=deepcopy(parent);bad['definition']['relations'].pop();case('dropped_equation',bad,reading,rounding,budget,'invalid')
 bad=deepcopy(parent);bad['definition']['observations'][compose.OBS]['type']['time']['start']='2023-01-01';case('wrong_period',bad,reading,rounding,budget,'invalid')
 bad=deepcopy(parent);bad['preserved_report']['observations']['annual.cash_flow.debt_issuance']['observation']['record']['body']['literal']='0';case('coerced_original_dash',bad,reading,rounding,budget,'invalid')
 bad=deepcopy(reading);bad['exact_economic_zero']=True;case('exact_zero_claim',parent,bad,rounding,budget,'invalid')
 bad=deepcopy(reading);bad['occurrences'][0]['context']['entity']['identifier']='wrong';case('wrong_issuer',parent,bad,rounding,budget,'invalid')
 bad=deepcopy(rounding);bad['mode']='exact';case('changed_rounding_rule',parent,reading,bad,budget,'invalid')
 zb=deepcopy(budget);zb['max_cells']=0;case('zero_budget',parent,reading,rounding,zb,'unknown')
 corrupt=deepcopy(witness);corrupt[compose.OBS]='1/2'
 try:independent_check.check(result['definition'],corrupt)
 except AssertionError:check(True,'open_endpoint_rejected')
 else:raise AssertionError('invalid endpoint accepted')
 original=compose.temporal.assess(parent['definition'],budget);check(original['status']=='unresolved','original_pdf_only_stays_unresolved')
 dump(out/'controls.json',[dict(name=x['name'],expected=x['expected'],status=x['result']['status'],reason=x['result'].get('reason')) for x in controls])
 dump(out/'witnesses.json',dict(primary=witness,nonzero=aw,independent_checks=first,nonzero_issuance='1/4'))
 for module in list(sys.modules.values()):
  path=getattr(module,'__file__',None)
  if path:
   p=Path(path).resolve()
   if p.suffix=='.py' and p.is_relative_to(R):lock.setdefault(str(p.relative_to(R)),sha(p))
 for n,h in lock.items():check(sha(R/n)==h,'protected_after:'+n)
 dump(out/'source-lock.json',lock);dump(out/'verification.json',dict(passed=True,checks=checks,observations=236,equations=101,full_source_observations=256,full_source_relations=143,controls=len(controls)+1,independent_witnesses=2,protected_files=len(lock)))
 dump(out/'run-manifest.json',dict(timestamp_utc=datetime.now(timezone.utc).isoformat(),git_commit='unavailable',command='CUDA_VISIBLE_DEVICES=-1 python3 -B data/accounting-master/debt-reading-network-20261027/verify.py',python=sys.version,executable=sys.executable,platform=platform.platform(),z3=compose.temporal.joint.z3.get_version_string(),cpu_gpu='CPU-only Python/Z3; GPU intentionally hidden; no TensorFlow import',cuda_visible_devices=os.environ.get('CUDA_VISIBLE_DEVICES'),random_seeds='N/A exact deterministic conjunction; no statistical ranking',wall_seconds=time.monotonic()-start,data_version=sha(out/'source-lock.json'),plan='docs/plans/accounting-debt-reading-network-20261027.md',result=str((H/'result.md').relative_to(R)),artifacts=['full-result.json','nonzero-diagnostic.json','controls.json','witnesses.json','verification.json']))
 print(json.dumps(dict(passed=True,checks=len(checks),observations=236,equations=101,controls=len(controls)+1,independent_witnesses=2,protected_files=len(lock))))
if __name__=='__main__':main()
