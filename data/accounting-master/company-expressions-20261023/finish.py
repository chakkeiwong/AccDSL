import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; HERE=Path(__file__).resolve().parent
REL=HERE.relative_to(ROOT).as_posix(); PLAN='docs/plans/accounting-company-recovery-20261023.md'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v): p.write_text(json.dumps(v,indent=2)+'\n')
def main():
 assert not (HERE/'control-refresh.json').exists()
 c=json.loads((HERE/'checks.json').read_text()); assert c['passed'] and len(c['checks'])==79
 for n,h in json.loads((HERE/'manifest.json').read_text())['files'].items(): assert sha(ROOT/n)==h,n
 names=['docs/plans/accounting-master-current.md','docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-program.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-product-design-checkpoint.md','data/accounting-master/next-plan.md','data/accounting-master/simulator-session-20261023.md','data/accounting-master/next-plan.json','scripts/accounting_master_catalog.json']
 note=('## 23 October 2026 — typed policy expressions checked\n\n'
 'CompanyExpressionsDraft/1 passes 79 checks and read-only replay; 339 protected\n'
 'files are unchanged. Exact typed/text expressions feed the protected policy\n'
 'and reproduce its whole path/result. Conditional 4/5 collection changes cash\n'
 'by -38.4 and receivables by +38.4 without changing profit. Unknown inputs,\n'
 'unit/context mismatches and unsupported structure remain explicit.\n'
 'Result: '+REL+'/result.md.\n\n'
 'Next: '+PLAN+'.\n'
 'Version 3.53 stays 413 pages, not_ready and unchanged. Policy information,\n'
 'families and expressions await coherent integration. S1–S5 partial, S6 held,\n'
 'S7 deferred; no whole requirement closes. Older entries are historical.\n\n')
 before={}
 for n in names:
  p=ROOT/n; before[n]=sha(p); dest=HERE/'control-before'/n
  dest.parent.mkdir(parents=True,exist_ok=True); dest.write_bytes(p.read_bytes())
  if n.endswith('.md'):
   title,rest=p.read_text().split('\n',1)
   if 'simulator-session' in n: rest='Protected PDF: docs/design/proposal/manuscript-company-authoring-20261023/accounting-product-proposal.pdf\nSHA256: 5bf364ae6c78bddcf833331d408c447ddd5f540aba1e47d4d28bc7e648c09893.\nNo active diagnostic. Preserve dirty work and one-time records. No commit or subagents.\nScope review:359 checks; policy timing:93; family:96; expressions:79.\nNo historical controller, forecast experiment, outreach or paid review.\n'
   p.write_text(title+'\n\n'+note+rest.lstrip('\n'))
 p=ROOT/'data/accounting-master/next-plan.json'; d=json.loads(p.read_text()); old={k:v for k,v in d.items() if k!='active_execution'}
 a=d['active_execution']; a.update(active_work_plan=PLAN,latest_result=REL+'/result.md'); a['latest_results'].append(a['latest_result'])
 a['completed_increments'].append('CompanyExpressionsDraft/1:79 checks/replay;typed DAG,conditional/unknown rules,protected policy/full-result match')
 a['next'][0]='Focused company-family checkpoints and exact-retry recovery exchanges, then coherent manuscript integration'
 dump(p,d); assert old=={k:v for k,v in json.loads(p.read_text()).items() if k!='active_execution'}
 p=ROOT/'scripts/accounting_master_catalog.json'; d=json.loads(p.read_text()); old={k:v for k,v in d.items() if k!='active_execution_note'}
 d['active_execution_note'].update(active_work_plan=PLAN,latest_result=REL+'/result.md'); dump(p,d)
 assert old=={k:v for k,v in json.loads(p.read_text()).items() if k!='active_execution_note'}
 dump(HERE/'coverage-delta.json',{'predecessor':'data/accounting-master/language-scope-review-20261023/inventory.json','advanced':['MC10','MC13','MC14','MC18','MC23','MC24','MC25','MC26','MC28','G2','G6','G14','G15'],'evidence':REL+'/checks.json','remaining':'General functions,source maps,typed portable wrapping,expression information admission,endogenous scheduling,module interfaces','whole_rows_closed':0})
 dump(HERE/'replay-observation.json',{'checks':79,'passed':True,'wall_seconds':0.408,'protected_files':339})
 dump(HERE/'control-refresh.json',{'before':before,'after':{n:sha(ROOT/n) for n in names},'legacy_json_fields_unchanged':True,'whole_rows_closed':0})
 print(json.dumps({'controls':len(names),'next':PLAN,'legacy_fields_unchanged':True}))
if __name__=='__main__': main()
