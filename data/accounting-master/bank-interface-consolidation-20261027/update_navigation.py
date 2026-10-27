"""Guard current controls, add bank evidence and reconcile the pursuit memo."""
from hashlib import sha256
from datetime import datetime, timezone
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
digest=lambda p:sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
supplement=read(HERE/'acceptance-supplement.json')
for p,h in {**supplement['baseline_records'],**supplement['evidence']}.items():assert digest(ROOT/p)==h,p
prefix=str(HERE.relative_to(ROOT))
paths=['scripts/accounting_master_catalog.json','data/accounting-master/next-plan.json',
       'MISSION_CONTROL.md','docs/plans/accounting-master-checkpoint.md',
       'docs/plans/accounting-master-program.md','docs/plans/accounting-mission-requirements.md',
       'docs/plans/accounting-product-design-checkpoint.md','docs/plans/accounting-master-current.md',
       'data/accounting-master/next-plan.md',
       'data/accounting-master/release-pursuit-20261027/state.json',
       'data/accounting-master/release-pursuit-20261027/reset-memo.md',
       'data/accounting-master/release-pursuit-20261027/progress.md']
before={p:(ROOT/p).read_bytes() for p in paths};new={};retained={}
now=datetime.now(timezone.utc).isoformat()
for p,key in [(paths[0],'active_execution_note'),(paths[1],'active_execution')]:
    obj=json.loads(before[p]);current=obj[key]
    retained[p]={k:v for k,v in current.items() if k in ['current_candidate','current_pdf','standalone_pdf',
        'active_work_plan','latest_manuscript_result','latest_package_result','manuscript_review_frontier','timed_release_pursuit']}
    current.update(latest_internal_result=prefix+'/result.md',latest_reset_memo=prefix+'/reset-memo.md')
    current['bank_interface_consolidation']=dict(result=prefix+'/result.md',
        acceptance_supplement=prefix+'/acceptance-supplement.json',compatibility_map=prefix+'/compatibility-map.md',
        archive=prefix+'/bank-interface-bundle.tar.gz',included_in_selected_manuscript_package=False)
    current.setdefault('latest_internal_results',[]).append(prefix+'/result.md')
    current.setdefault('completed_plan_evidence',{})['docs/plans/accounting-bank-consolidation-20261027.md']=prefix+'/result.md'
    assert all(current[k]==v for k,v in retained[p].items())
    new[p]=json.dumps(obj,indent=2,ensure_ascii=False)+chr(10)
obj=json.loads(new[paths[1]]);h=sha256(new[paths[0]].encode()).hexdigest();obj['catalog_sha256']=h
for value in obj.values():
    if isinstance(value,dict) and paths[0] in value:value[paths[0]]=h
new[paths[1]]=json.dumps(obj,indent=2,ensure_ascii=False)+chr(10)
old='Latest technical result: data/accounting-master/insurance-paa-dated-book-20261027/result.md.'
replacement=(f'Latest technical result: {prefix}/result.md.\n'
             f'Bank compatibility and acceptance evidence: {prefix}/acceptance-supplement.md.\n'
             'Four retained bank profiles reproduce 1,659 original exchanges and 63 exact-time cases.\n'
             'The existing US book-to-capital connection is checked; AU and US profiles remain separate.\n'
             'All four original MC21 clauses have explicit evidence and remaining conditions; broad acceptance remains open.')
for p in paths[2:9]:
    head,tail=before[p].decode().split('Historical assessments below are preserved.',1)
    assert head.count(old)==1,p
    new[p]=head.replace(old,replacement)+'Historical assessments below are preserved.'+tail
state=json.loads(before[paths[9]])
for unit in ['internal-evidence-companion-20261027','intragroup-evidence-replay-20261027',
             'insurance-paa-dated-book-20261027','bank-interface-consolidation-20261027']:
    result='data/accounting-master/'+unit+'/result.md'
    assert (ROOT/result).is_file()
    if not any(r['result']==result for r in state['completed_units']):
        state['completed_units'].append(dict(id=unit,result=result,status='checked_separate_internal_supplement'))
state.update(last_update_utc=now,latest_technical_result=prefix+'/result.md',
    goal_tool_status_observed='No goal entry returned on recovery; current user continuation and saved authorized window govern work',
    current_unit='Integrate checked dated insurance interface and bank compatibility/reproduction references; then resume ordered manuscript reading',
    next_check='Protect 5.54-R2 package revision 2; preserve original acceptance and exact source identities before a new integration')
new[paths[9]]=json.dumps(state,indent=2)+chr(10)
reset=before[paths[10]].decode()
reset=reset.replace('The goal tool still reports its earlier blocked status; explicit continuation\nsupports supervised local work. No tool resume or completion is claimed.',
    'The goal tool returns no entry on recovery. Current user continuation and the\nsaved authorized window govern work; no goal completion is claimed.')
reset+='\nLatest reconciled supplement: '+prefix+'/result.md. All four bank profiles\nreproduce from a declared-input copy. The US book/capital case is already connected;\nAU profiles remain separate. Insurance, intragroup and internal companion results\nare also reconciled in state.json. Next integrate the dated PAA interface and bank\ncompatibility/reproduction references in a protected successor, then continue\nordered reading from163. The selected PDFs and four stable links are unchanged.\n'
new[paths[10]]=reset
new[paths[11]]=before[paths[11]].decode()+'\n'+now+': bank consolidation passes 20,339 original checks over1,659 complete exchanges plus63 exact-time cases,42 retries and12 additional controls. The1,452-input separate copy and internal archive preserve every declared input. Four MC21 clauses receive evidence-specific dispositions without broad closure. Three preceding supplements are reconciled in pursuit state; the selected manuscript remains5.54-R2 package revision2.\n'
backup=HERE/'navigation-before';backup.mkdir(exist_ok=False)
for p,content in before.items():
    target=backup/p;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(content)
assert all((ROOT/p).read_bytes()==content for p,content in before.items())
for p,content in new.items():
    assert (ROOT/p).read_bytes()==before[p],p
    (ROOT/p).write_text(content)
for p,h in supplement['baseline_records'].items():assert digest(ROOT/p)==h
record=dict(timestamp_utc=now,passed=True,controls={p:dict(before=sha256(before[p]).hexdigest(),after=digest(ROOT/p)) for p in paths},
    selected_manuscript_controls_preserved=retained,frozen_acceptance_preserved=supplement['baseline_records'],
    stable_links_changed=False,manuscript_bytes_changed=False)
with (HERE/'navigation-update.json').open('x') as f:json.dump(record,f,indent=2);f.write(chr(10))
print(json.dumps(dict(passed=True,controls=len(paths),manuscript_selection_preserved=True)))
