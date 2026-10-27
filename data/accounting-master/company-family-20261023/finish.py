import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; HERE=Path(__file__).resolve().parent
REL=HERE.relative_to(ROOT).as_posix(); PLAN='docs/plans/accounting-company-expressions-20261023.md'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v): p.write_text(json.dumps(v,indent=2)+'\n')
def main():
 assert not (HERE/'control-refresh.json').exists()
 c=json.loads((HERE/'checks.json').read_text()); assert c['passed'] and len(c['checks'])==96
 for n,h in json.loads((HERE/'manifest.json').read_text())['files'].items(): assert sha(ROOT/n)==h,n
 names=['docs/plans/accounting-master-current.md','docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-program.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-product-design-checkpoint.md','data/accounting-master/next-plan.md','data/accounting-master/simulator-session-20261023.md','data/accounting-master/next-plan.json','scripts/accounting_master_catalog.json']
 note=('## 23 October 2026 — authored scenario families checked\n\n'
 'CompanyScenarioFamilyDraft/1 passes 96 checks and read-only replay; all 311\n'
 'protected files are unchanged. Six named paths retain four complete and two\n'
 'partial outcomes, matched text/typed input, common opening and joint reports.\n'
 'The preserved first Unicode identity defect is repaired. No weights,\n'
 'historical-family admission or general portable/runtime claim is made.\n'
 'Result: '+REL+'/result.md.\n\n'
 'Next: '+PLAN+'.\n'
 'Version 3.53 remains 413 pages, not_ready and unchanged. This increment and\n'
 'policy-information await integration. S1–S5 partial; S6 held; S7 deferred.\n'
 'No whole requirement closes. Earlier entries are historical checkpoints.\n\n')
 before={}
 for n in names:
  p=ROOT/n; before[n]=sha(p); dest=HERE/'control-before'/n
  dest.parent.mkdir(parents=True,exist_ok=True); dest.write_bytes(p.read_bytes())
  if n.endswith('.md'):
   title,rest=p.read_text().split('\n',1)
   if 'simulator-session' in n:
    rest='Protected PDF: docs/design/proposal/manuscript-company-authoring-20261023/accounting-product-proposal.pdf\nSHA256: 5bf364ae6c78bddcf833331d408c447ddd5f540aba1e47d4d28bc7e648c09893.\nNo active diagnostic. Do not repeat one-time recordings, protected builds or historical controllers.\nScope review:53/6/46 identities,359 checks; policy information:93 checks.\nPreserve dirty work. No commit, subagent, outreach or empirical forecast requested.\n'
   p.write_text(title+'\n\n'+note+rest.lstrip('\n'))
 p=ROOT/'data/accounting-master/next-plan.json'; d=json.loads(p.read_text()); old={k:v for k,v in d.items() if k!='active_execution'}
 a=d['active_execution']; a.update(active_work_plan=PLAN,latest_result=REL+'/result.md')
 a['latest_results'].append(a['latest_result']); a['completed_increments'].append('CompanyScenarioFamilyDraft/1:96 checks/replay;6 paths,complete/partial joint reports;Unicode identity repaired')
 a['next'][0]='Typed policy expressions feeding the existing settlement generator, then focused recovery and manuscript integration'
 dump(p,d); assert old=={k:v for k,v in json.loads(p.read_text()).items() if k!='active_execution'}
 p=ROOT/'scripts/accounting_master_catalog.json'; d=json.loads(p.read_text()); old={k:v for k,v in d.items() if k!='active_execution_note'}
 d['active_execution_note'].update(active_work_plan=PLAN,latest_result=REL+'/result.md'); dump(p,d)
 assert old=={k:v for k,v in json.loads(p.read_text()).items() if k!='active_execution_note'}
 dump(HERE/'coverage-delta.json',{'predecessor':'data/accounting-master/language-scope-review-20261023/inventory.json','predecessor_sha256':sha(ROOT/'data/accounting-master/language-scope-review-20261023/inventory.json'),'advanced':['MC08','MC10','MC11','MC12','MC13','MC14','MC15','MC16','MC18','MC23','MC24','MC25','MC26','MC28','MC34','G2','G6','G14','G15','G18'],'evidence':REL+'/checks.json','remaining':'General expressions, endogenous policy, reconstruction, module imports, real admission and durability remain separate','whole_rows_closed':0})
 dump(HERE/'replay-observation.json',{'checks':96,'passed':True,'wall_seconds':19.492,'protected_files':311,'tool_session':86206})
 dump(HERE/'control-refresh.json',{'before':before,'after':{n:sha(ROOT/n) for n in names},'legacy_json_fields_unchanged':True,'whole_rows_closed':0})
 print(json.dumps({'controls':len(names),'next':PLAN,'legacy_fields_unchanged':True}))
if __name__=='__main__': main()
