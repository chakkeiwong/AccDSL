import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
REL=HERE.relative_to(ROOT).as_posix()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v): p.write_text(json.dumps(v,indent=2)+'\n')
def main():
 assert not (HERE/'control-refresh.json').exists()
 checks=json.loads((HERE/'checks.json').read_text()); assert checks['passed'] and len(checks['checks'])==359
 plan='docs/plans/accounting-company-family-20261023.md'
 assert (ROOT/plan).is_file()
 note=('## 23 October 2026 — whole-language scope reviewed\n\n'
 'All 53 obligations, six interactions and 46 operations have distinct syntax,\n'
 'semantics, connected-execution and acceptance assessments. Recorded and\n'
 'read-only review checks pass (359); 59 prior operation-evidence files retain\n'
 'their recorded hashes. The 14-kind company frontend supports bounded paths;\n'
 'general expressions, family authoring, richer module joins and durable\n'
 'recovery remain. See `'+REL+'/review.md` and `inventory.json`.\n\n'
 'Next: `'+plan+'` — matched text/typed unweighted\n'
 'scenario families retaining every joint path and failure outcome. This is\n'
 'explicit scenario authoring, not historical-family reconstruction.\n'
 'Version 3.53 remains 413 pages, not_ready, unchanged. S1–S5 stay partial,\n'
 'S6 held and S7 deferred; no whole requirement closes. Earlier entries below\n'
 'are historical checkpoints.\n\n')
 names=['docs/plans/accounting-master-current.md','docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-program.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-product-design-checkpoint.md','data/accounting-master/next-plan.md','data/accounting-master/simulator-session-20261023.md','data/accounting-master/next-plan.json','scripts/accounting_master_catalog.json']
 before={}
 for name in names:
  p=ROOT/name; before[name]=sha(p); dest=HERE/'control-before'/name
  dest.parent.mkdir(parents=True,exist_ok=True); dest.write_bytes(p.read_bytes())
  if name.endswith('.md'):
   title,rest=p.read_text().split('\n',1)
   if 'simulator-session' in name:
    rest='Protected manuscript: docs/design/proposal/manuscript-company-authoring-20261023/accounting-product-proposal.pdf\nSHA256: 5bf364ae6c78bddcf833331d408c447ddd5f540aba1e47d4d28bc7e648c09893.\nNo active diagnostic. Do not repeat one-time records or the protected manuscript build.\nPolicy information: 93 checks and replay; result is linked in the prior checkpoint.\nPreserve dirty work; no new commit, subagent, controller or forecast experiment.\n'
   p.write_text(title+'\n\n'+note+rest.lstrip('\n'))
 p=ROOT/'data/accounting-master/next-plan.json'; d=json.loads(p.read_text()); old={k:v for k,v in d.items() if k!='active_execution'}
 a=d['active_execution']; a['active_work_plan']=plan; a['latest_result']=REL+'/review.md'; a['latest_results'].append(a['latest_result'])
 a['completed_increments'].append('Whole-language review:53 obligations,6 interactions,46 operations;359 coverage/binding checks;59 evidence files unchanged')
 a['next'][0]='Authored unweighted company scenario families, then typed policy expressions and focused recovery contracts'
 dump(p,d); assert old=={k:v for k,v in json.loads(p.read_text()).items() if k!='active_execution'}
 p=ROOT/'scripts/accounting_master_catalog.json'; d=json.loads(p.read_text()); old={k:v for k,v in d.items() if k!='active_execution_note'}
 d['active_execution_note'].update(active_work_plan=plan,latest_result=REL+'/review.md'); dump(p,d)
 assert old=={k:v for k,v in json.loads(p.read_text()).items() if k!='active_execution_note'}
 dump(HERE/'control-refresh.json',{'before':before,'after':{n:sha(ROOT/n) for n in names},'legacy_json_fields_unchanged':True,'whole_rows_closed':0})
 print(json.dumps({'controls':len(names),'next':plan,'legacy_fields_unchanged':True}))
if __name__=='__main__': main()
