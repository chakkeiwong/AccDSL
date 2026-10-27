"""One-shot saved-evidence audit; no original solver, writer or model executes."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import json, os, platform, subprocess, sys, time
from decisions import DECISIONS
H=Path(__file__).resolve().parent; R=H.parents[2]; B=H.parent
def read(p):return json.loads(p.read_text())
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def main():
 out=H/'attempt-01';out.mkdir(exist_ok=False);started=time.monotonic();checks=[];lock={}
 def check(ok,name):checks.append(dict(name=name,passed=bool(ok)));assert ok,name
 def protect(p,expected=None):
  key=str(p.relative_to(R));h=sha(p)
  if expected is not None:check(h==expected,'inherited_identity:'+key)
  if key in lock:check(lock[key]==h,'consistent_identity:'+key)
  lock[key]=h
 for directory,file,field in [
  ('real-company-input-readiness-20261024','source-lock.json',None),
  ('retained-population-overlap-20261025','manifest.json','inputs'),
  ('conditional-continuation-20261025','source-lock.json',None)]:
  p=B/directory/file;protect(p);d=read(p);d=d[field] if field else d
  for n,h in d.items():protect(R/n,h)
 files=['real-company-input-readiness-20261024/readiness.json','real-company-input-readiness-20261024/requirements.py',
  'statement-context-coverage-20261024/statements.json','retained-population-overlap-20261025/exchanges.json',
  'cash-population-reconciliation-20261025/source-ledger.json','conditional-continuation-20261025/comparison.json',
  'history-to-opening-20261025/comparison.json','fiscal-timeline-20261025/manifest.json',
  'real-company-acceptance-20261027/decisions.py','real-company-acceptance-20261027/audit.md',
  'real-company-acceptance-20261027/reconcile.py']
 files+=sorted({e for d in DECISIONS.values() for e in d['evidence']})
 for n in files:protect(B/n)
 for n in ['scripts/retained_network_history_v1.py','scripts/conditional_company_opening_v1.py',
           'scripts/conditional_company_continuation_v1.py','scripts/mixed_event_timeline_v3.py',
           'docs/plans/accounting-real-company-acceptance-20261027.md']:protect(R/n)
 original=read(B/'real-company-input-readiness-20261024/readiness.json');rows=[]
 ids=list(DECISIONS)
 check(len(ids)==15,'fifteen_current_decisions')
 for target,value in original.items():
  check([d['id'] for d in value['dependencies']]==ids,'original_order:'+target)
  check(value['status']=='blocked' and value['executable_opening'] is None and value['executed'] is False,'original_refusal:'+target)
 for key in ids:
  d=DECISIONS[key];check(all(d[k] for k in ['current_capability','remaining_issuer_dependency','next_discriminating_action','evidence']),'meaningful_decision:'+key)
  rows.append(dict(id=key,original_by_target={t:next(x for x in v['dependencies'] if x['id']==key) for t,v in original.items()},**d))
 statements=read(B/'statement-context-coverage-20261024/statements.json')
 full=statements['CompanyOperationsDraft/1:combined']
 check(len(full['observations'])==256 and len(full['relations'])==143,'full_statement_inventory')
 check(full['observations']['annual.cash_flow.debt_issuance']['observation']['record']['body']['literal']=='—','literal_dash_preserved')
 check(full['observations']['annual.cash_flow.debt_issuance']['declaration']['measurement_time']==dict(kind='period',start='2023-10-01',end_exclusive='2024-09-29'),'original_fiscal_interval')
 unresolved=[r['id'] for r in full['relations'] if r['arithmetic']['status']=='unresolved']
 check(unresolved==['annual.financing_cash','annual.diagnostic:term_debt'],'two_unresolved_original_relations')
 for name,s in statements.items():check(s['executable_opening'] is None and s['executed'] is False,'statement_not_company:'+name)
 cases=read(B/'retained-population-overlap-20261025/exchanges.json')
 expected={'both_instants':'conditionally_feasible','opening_only':'conditionally_feasible','closing_only':'conditionally_feasible',
  'false_opening_equality':'conditionally_infeasible','missing_projection':'unresolved','cross_date':'invalid','full_source_dash':'unresolved','zero_budget':'unknown'}
 check([c['name'] for c in cases]==list(expected),'all_overlap_cases')
 summaries=[]
 for c in cases:
  name=c['name'];r=c['result'];check(r['status']==expected[name],'saved_status:'+name)
  check(all(r[k] is False for k in ['executed','source_admission','accounting_admission','posting_authorized']),'no_admission:'+name)
  check(r['actual_history']=='unknown' and r['executable_opening'] is None and r['membership_identity']=='unresolved','unknown_population:'+name)
  if 'source_result' in r:
   p=r['source_result'];check(p['preserved_report']==full,'complete_source_report:'+name)
   parent=p['definition'];child=r['definition']
   check(all(child['observations'].get(k)==v for k,v in parent['observations'].items()),'original_observations:'+name)
   check(child['relations'][:len(parent['relations'])]==parent['relations'],'original_equations:'+name)
  summaries.append(dict(name=name,status=r['status'],original_observations=r.get('original_observation_count'),original_relations=r.get('original_relation_count'),actual_history=r['actual_history']))
 both=cases[0]['result'];check((len(both['definition']['observations']),len(both['definition']['relations']))==(120,42),'overlap_additions_only')
 wide=next(c['result']['source_result'] for c in cases if c['name']=='full_source_dash')
 check(wide['selection_coverage']==dict(total_source_relations=143,supported_relations=101,selected_relations=101,selected_observations=236,all_supported_selected=True,excluded_supported_relations=[],whole_statement_history_complete=False),'supported_is_not_complete')
 check(len(wide['unresolved_measurements'])==1 and wide['unresolved_measurements'][0]['alias']=='annual.cash_flow.debt_issuance' and wide['unresolved_measurements'][0]['literal']=='—','full_selection_dash_unresolved')
 continuations=read(B/'conditional-continuation-20261025/comparison.json')['cases'];cs=[]
 check(len(continuations)==4,'four_conditional_continuations')
 for c in continuations:
  req=c['request'];r=c['result'];name=c['case'];book=req['opening_result']['opening'];cash=book['cash_account'];eq=next(k for k,v in book['accounts'].items() if v['classification']=='equity')
  memory='5/1' if '(10, 2, 3)' in name else '7/1'
  check(r['status']=='conditional_continuation','conditional_status:'+name)
  check(r['opening_result']==req['opening_result'],'complete_opening_retained:'+name)
  check(r['current']['balances']=={cash:'14/1',eq:'-14/1'} and r['transition']['journal']=={cash:'-1/1',eq:'1/1'},'distribution_amounts:'+name)
  check(r['current']['memory']==book['memory'] and r['current']['memory']['history']['sales/a~1']==memory,'history_memory:'+name)
  check(r['report']['income']['profit']=='0/1' and r['report']['cash_flows']['activities']['financing']['net']=='-1/1' and r['report']['equity']['closing']=='14/1','complete_report_amounts:'+name)
  check(all(r[k] is False for k in ['source_admission','accounting_admission','execution_clearance','family_complete','posting_authorized','committed']),'conditional_not_admitted:'+name)
  check(book['context']['mode']=='synthetic','not_issuer_opening:'+name)
  cs.append(dict(case=name,status=r['status'],cash='14/1',equity='14/1',sales_memory=memory))
 ledger=read(B/'cash-population-reconciliation-20261025/source-ledger.json')
 for n,h in ledger['source_sha256'].items():protect(R/n,h)
 check(ledger['source_admission'] is False and ledger['accounting_admission'] is False and ledger['population_membership']=='unresolved','cash_source_limits')
 for n,h in lock.items():check(sha(R/n)==h,'protected_after:'+n)
 dump(out/'source-lock.json',lock);dump(out/'current-decisions.json',dict(original_targets=list(original),rows=rows,broad_closures=0))
 dump(out/'saved-result-checks.json',dict(overlap=summaries,conditional_continuations=cs,unresolved_statement_relations=unresolved,whole_company_admitted=False))
 dump(out/'verification.json',dict(passed=True,checks=checks,original_dependencies=15,original_target_records=30,protected_files=len(lock),executed_original_writers=False,executed_solvers=False))
 lines=['# Current retained-company dependencies','','27 October 2026. Both original targets remain blocked. Later capabilities and missing issuer facts are distinct. All fifteen original records per target are preserved in attempt-01/current-decisions.json.','']
 for d in rows:
  lines += ['## '+d['id'],'',d['current_capability'],'','Remaining issuer dependency: '+d['remaining_issuer_dependency'],'','Next: '+d['next_discriminating_action'],'','Evidence: '+', '.join(d['evidence'])+'.','']
 (H/'current-decisions.md').write_text('\n'.join(lines))
 git=subprocess.run(['git','rev-parse','HEAD'],cwd=R,capture_output=True,text=True)
 dump(out/'run-manifest.json',dict(timestamp_utc=datetime.now(timezone.utc).isoformat(),git_commit=git.stdout.strip() if git.returncode==0 else 'unavailable',command='CUDA_VISIBLE_DEVICES=-1 python3 -B data/accounting-master/real-company-acceptance-20261027/reconcile.py',python=sys.version,executable=sys.executable,platform=platform.platform(),cpu_gpu='CPU-only JSON/source inspection; GPU intentionally hidden; no numerical framework imported',cuda_visible_devices=os.environ.get('CUDA_VISIBLE_DEVICES'),random_seeds='N/A deterministic saved-result predicates',wall_seconds=time.monotonic()-started,data_version=sha(out/'source-lock.json'),plan='docs/plans/accounting-real-company-acceptance-20261027.md',result=str((H/'result.md').relative_to(R)),artifacts=['current-decisions.md','attempt-01/current-decisions.json','attempt-01/saved-result-checks.json','attempt-01/verification.json']))
 print(json.dumps(dict(passed=True,dependencies=len(rows),original_records=30,checks=len(checks),protected_files=len(lock))))
if __name__=='__main__':main()
