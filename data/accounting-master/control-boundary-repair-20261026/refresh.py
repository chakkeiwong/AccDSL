"""Advance only this financing lane while preserving concurrent master work."""
from pathlib import Path
from hashlib import sha256
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
OLD='docs/plans/accounting-contingent-conversion-authority-20261026.md'
NEXT='docs/plans/accounting-conversion-control-scope-20261026.md'
RESULT=str((HERE/'result.md').relative_to(ROOT))

def main():
    assert not (HERE/'refresh.json').exists()
    assert json.loads((HERE/'attempt-01/verification.json').read_text())['status']=='PASS'
    names=['MISSION_CONTROL.md','docs/plans/accounting-master-checkpoint.md',
           'docs/plans/accounting-product-design-checkpoint.md','docs/plans/accounting-mission-requirements.md',
           'docs/plans/accounting-master-current.md','data/accounting-master/next-plan.md',
           'data/accounting-master/recovery-current-20261026.md',
           'scripts/accounting_master_catalog.json','data/accounting-master/next-plan.json']
    before={name:(ROOT/name).read_bytes() for name in names}
    cat=json.loads(before[names[-2]])
    active=cat['active_execution_note']
    for key in ['current_pdf','standalone_pdf']:
        assert sha256((ROOT/active[key]).read_bytes()).hexdigest()==active[key+'_sha256']
    candidate=active['current_candidate']
    note=f'''## Financing authority continuation — 26 October2026

Current governing candidate: {candidate}. The live manuscript and independent
execution lane remain unchanged. ConversionScopeDependencies/2 passes30 cases,
23 controls and295 assertions. It repairs the earlier unknown-prior and
loss-of-control boundaries, preserves possible intervening changes and requires
canonical dates. Original source/case evidence and failures remain retained.
The source/control review also remains a conditional companion, not actual
authority or measurement admission.
Result: {RESULT}.
Active financing plan: {NEXT}.
Full program: {active['full_gap_program']}.
All53 obligations, six interactions,46 operations and18 packages remain.
S1–S5 partial; S6 held; E3 deferred. Continue feasible internal work.

'''
    backup=HERE/'control-before';backup.mkdir(exist_ok=False)
    for name,data in before.items():
        p=backup/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    updates={}
    for name in names[:4]:
        first,_,rest=before[name].decode().partition('\n')
        updates[name]=(first+'\n\n'+note+rest.lstrip()).encode()
    for name in names[4:6]:
        text=before[name].decode().replace(OLD,NEXT)
        updates[name]=(text+'\n'+note).encode()
    updates[names[6]]=('# Current recovery pointer\n\n'+
        'Authoritative concise state: docs/plans/accounting-master-current.md.\n'+
        'Historical pointer preserved in control-boundary-repair-20261026/control-before/.\n\n'+note+
        'Other active plans: '+', '.join(p for p in active.get('active_work_plans',[]) if p!=OLD)+'.\n').encode()
    def advance(a):
        if a.get('active_work_plan')==OLD:a['active_work_plan']=NEXT
        a['active_work_plans']=[NEXT if p==OLD else p for p in a.get('active_work_plans',[])]
        if NEXT not in a['active_work_plans']:a['active_work_plans'].append(NEXT)
        a['financing_authority_result']=RESULT
        a['financing_next_plan']=NEXT
        a['latest_internal_results']=list(dict.fromkeys([*a.get('latest_internal_results',[]),RESULT]))
        a['next']=[s.replace(OLD,NEXT) for s in a.get('next',[])]
    advance(active)
    updates[names[-2]]=(json.dumps(cat,indent=2,ensure_ascii=False)+'\n').encode()
    nxt=json.loads(before[names[-1]]);advance(nxt['active_execution'])
    updates[names[-1]]=(json.dumps(nxt,indent=2,ensure_ascii=False)+'\n').encode()
    for name,data in before.items():assert (ROOT/name).read_bytes()==data,'concurrent change: '+name
    for name,data in updates.items():(ROOT/name).write_bytes(data)
    for name,data in updates.items():assert (ROOT/name).read_bytes()==data
    record=dict(status='PASS',candidate=candidate,controls=len(updates),next_plan=NEXT,
                before={k:sha256(v).hexdigest() for k,v in before.items()},
                after={k:sha256(v).hexdigest() for k,v in updates.items()})
    (HERE/'refresh.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({k:v for k,v in record.items() if k not in ['before','after']}))

if __name__=='__main__':main()
