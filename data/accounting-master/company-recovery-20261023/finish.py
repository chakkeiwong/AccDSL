import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; HERE=Path(__file__).resolve().parent
REL=HERE.relative_to(ROOT).as_posix(); PLAN='docs/plans/accounting-company-language-integration-20261023.md'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v): p.write_text(json.dumps(v,indent=2)+'\n')
def main():
 assert not (HERE/'control-refresh.json').exists()
 c=json.loads((HERE/'checks.json').read_text()); assert c['passed'] and len(c['checks'])==57
 for n,h in json.loads((HERE/'manifest.json').read_text())['files'].items(): assert sha(ROOT/n)==h,n
 names=['docs/plans/accounting-master-current.md','docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-program.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-product-design-checkpoint.md','data/accounting-master/next-plan.md','data/accounting-master/simulator-session-20261023.md','data/accounting-master/next-plan.json','scripts/accounting_master_catalog.json']
 note=('## 23 October 2026 — company-family recovery checked\n\n'
 'Company-family checkpoint and publication exchanges pass 57 checks and\n'
 'read-only replay; 372 protected files remain unchanged. Every budget split\n'
 'preserves the full family; partial accounting is finished work, exact retries\n'
 'retain immutable decisions, and both lost-acknowledgement worlds are explicit.\n'
 'This is a member-boundary reference, not physical durability evidence.\n'
 'Result: '+REL+'/result.md.\n\n'
 'Next: '+PLAN+'.\n'
 'Integrate the coherent timing/family/expression/recovery design into a\n'
 'protected successor. Version 3.53 stays 413 pages, not_ready and unchanged\n'
 'until verified integration. S1–S5 partial; S6 held; S7 deferred. No whole\n'
 'requirement closes. Earlier entries are historical checkpoints.\n\n')
 before={}
 for n in names:
  p=ROOT/n; before[n]=sha(p); dest=HERE/'control-before'/n
  dest.parent.mkdir(parents=True,exist_ok=True); dest.write_bytes(p.read_bytes())
  if n.endswith('.md'):
   title,rest=p.read_text().split('\n',1)
   if 'simulator-session' in n: rest='Protected PDF: docs/design/proposal/manuscript-company-authoring-20261023/accounting-product-proposal.pdf\nSHA256: 5bf364ae6c78bddcf833331d408c447ddd5f540aba1e47d4d28bc7e648c09893.\nNo active diagnostic. Preserve dirty work and one-time records. No commit/subagents.\nScope:359 checks; policy timing:93; family:96; expressions:79; recovery:57.\nUse bounded tool payloads. Next prepare baseline boundary renders before copying manuscript.\n'
   p.write_text(title+'\n\n'+note+rest.lstrip('\n'))
 p=ROOT/'data/accounting-master/next-plan.json'; d=json.loads(p.read_text()); old={k:v for k,v in d.items() if k!='active_execution'}
 a=d['active_execution']; a.update(active_work_plan=PLAN,latest_result=REL+'/result.md'); a['latest_results'].append(a['latest_result'])
 a['completed_increments'].append('Company-family recovery:57 checks/replay;all budget splits,partial-member work,exact retry and atomic publication worlds')
 a['next'][0]='Integrate checked policy timing,scenario families,typed expressions and member-boundary recovery into protected Version 3.54'
 dump(p,d); assert old=={k:v for k,v in json.loads(p.read_text()).items() if k!='active_execution'}
 p=ROOT/'scripts/accounting_master_catalog.json'; d=json.loads(p.read_text()); old={k:v for k,v in d.items() if k!='active_execution_note'}
 d['active_execution_note'].update(active_work_plan=PLAN,latest_result=REL+'/result.md'); dump(p,d)
 assert old=={k:v for k,v in json.loads(p.read_text()).items() if k!='active_execution_note'}
 dump(HERE/'coverage-delta.json',{'advanced':['MC08','MC11','MC18','MC24','MC25','MC28','MC34','G1','G2','G18'],'evidence':REL+'/checks.json','remaining':'Intra-member recovery,physical durability,efficient persistence,general migration and full profile admission','whole_rows_closed':0})
 dump(HERE/'replay-observation.json',{'checks':57,'passed':True,'wall_seconds':44.061,'protected_files':372,'tool_session':42429})
 dump(HERE/'control-refresh.json',{'before':before,'after':{n:sha(ROOT/n) for n in names},'legacy_json_fields_unchanged':True,'whole_rows_closed':0})
 print(json.dumps({'controls':len(names),'next':PLAN,'legacy_fields_unchanged':True}))
if __name__=='__main__': main()
