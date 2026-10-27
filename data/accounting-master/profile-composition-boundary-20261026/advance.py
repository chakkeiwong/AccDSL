from hashlib import sha256
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];REL=HERE.relative_to(ROOT).as_posix()
NEXT='docs/plans/accounting-profile-interface-integration-20261026.md'
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,d):p.write_text(json.dumps(d,indent=2)+chr(10))
assert not (HERE/'control-refresh.json').exists()
check=json.loads((HERE/'checks.json').read_text());assert check['status']=='passed_bounded_documentary_composition'
manifest=json.loads((HERE/'run-manifest.json').read_text())
for p,h in manifest['artifacts'].items():assert sha(ROOT/p)==h,p
note=f'''## Native composition checked — 26 October 2026

Version 4.40 remains 534 pages, not_ready. S1–S5 partial; S6 held; S7/E3 deferred.
RetainedProfileComposition/1 passes 77 text/typed cases, including 66 native
sequences and 14 malformed-input refusals. Cross-profile insurance state transfer
remains unsupported; unknown dependencies propagate; positive receipt use is
unexercised. No whole requirement closes.
Result: {REL}/result.md.
Next plan: {NEXT}.

'''
names=['docs/plans/accounting-master-current.md','docs/plans/accounting-current-program-20261025.md',
 'docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-program.md',
 'docs/plans/accounting-mission-requirements.md','docs/plans/accounting-product-design-checkpoint.md',
 'data/accounting-master/next-plan.md','data/accounting-master/simulator-session-20261023.md',
 'data/accounting-master/next-plan.json','scripts/accounting_master_catalog.json']
before={}
for name in names:
 p=ROOT/name;before[name]=sha(p);saved=HERE/'control-before'/name;saved.parent.mkdir(parents=True,exist_ok=True);saved.write_bytes(p.read_bytes())
 if p.suffix=='.md':
  title,rest=p.read_text().split(chr(10),1)
  if name in names[:2]+names[6:8]:
   rest=rest[rest.index('Mission:'):]
   start=rest.index('Current question:');end=rest.index('Full residuals:')
   rest=rest[:start]+'Current question: how should the checked identity, publication and dependency distinctions appear in the governing specification?'+chr(10)+'Next action: execute '+NEXT+'.'+chr(10)*2+rest[end:]
  p.write_text(title+chr(10)*2+note+rest.lstrip())
for name,key in [(names[8],'active_execution'),(names[9],'active_execution_note')]:
 p=ROOT/name;d=json.loads(p.read_text());a=d[key];a.update(updated='2026-10-26',active_work_plan=NEXT,latest_result=REL+'/result.md')
 if key=='active_execution':
  a['latest_results'].append(REL+'/result.md');a['completed_increments'].append('RetainedProfileComposition/1: native sequences, exact imports, typed/text findings and transitive unknowns checked')
  a['next']=['Integrate checked profile interfaces into preserved Version 4.41','Specify missing cross-profile state/source/authority admission without hidden conversion','Continue broader methods and whole-company evidence; forecasting deferred']
 dump(p,d)
dump(HERE/'control-refresh.json',{'before':before,'after':{n:sha(ROOT/n) for n in names},'next_plan':NEXT})
dump(HERE/'coverage-delta.json',{'baseline':'data/accounting-master/current-design-reconciliation-20261025/coverage.json','affected':['MC20','MC24','MC25','MC33','MC34','G2','G18','I04'],'whole_rows_closed':0,'evidence':REL+'/result.md'})
for name in ['result.md','advance.py','coverage-delta.json']:manifest['artifacts'][REL+'/'+name]=sha(HERE/name)
manifest['control_refresh_command']='python3 '+REL+'/advance.py';dump(HERE/'run-manifest.json',manifest)
print(json.dumps({'controls':len(names),'next_plan':NEXT}))
