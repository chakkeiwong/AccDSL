"""One-shot typed conditional classifications and complete economic/history trace."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from datetime import datetime,timezone
import importlib.util,json,os,platform,sys,time
sys.path.append(str(Path(__file__).resolve().parent.parent/'financing-remedy-binding-20261026'))
import typed_conditions as t
import remedy_execution as e
import company_method_clock_v1 as clock
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
E03=HERE.parent/'gap-program-20261026';OUT=HERE/'attempt-01'
checks=[];controls=[]
def read(p):return json.loads(p.read_text())
def sha(p):return sha256(p.read_bytes()).hexdigest()
def save(n,v):(OUT/n).write_text(json.dumps(v,indent=2,ensure_ascii=False)+chr(10))
def check(n,a,b=True):
    checks.append(dict(id=n,passed=a==b,actual_sha256=t.core.digest(a),expected_sha256=t.core.digest(b)))
    if a!=b:save('failed.json',dict(id=n,actual=a,expected=b));raise AssertionError(n)
def refusal(name,result,status):
    check(name+'.status',result['status'],status);check(name+'.no_after','after' not in result)
    controls.append(dict(case=name,result=result))
def run(k,b,event,s):
    h=t.core.digest(k);return e.execute(k,b,event,s,h,e.make_call(k,b,event,s,h))

def main():
    assert not OUT.exists(),'attempt_exists';OUT.mkdir();started=time.monotonic()
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1'
    old=read(E03/'contract-condition-results.json');settlement=read(E03/'settlement-cases.json')
    pins=read(HERE.parent/'financing-opening-invariants-20261026/attempt-02/source-lock.json')
    for n,h in pins.items():assert sha(ROOT/n)==h,n
    sources=[Path(m.__file__).resolve() for m in list(sys.modules.values())
      if getattr(m,'__file__',None) and Path(m.__file__).resolve().is_relative_to(ROOT)]
    predecessor=HERE.parent/'financing-remedy-binding-20261026'
    sources += [predecessor/n for n in ['remedy_execution.py','verify.py','typed_conditions.py',
      'same-day-discriminator.py','same-day-discriminator.json','result.md','attempt-01/checks.json','attempt-01/trace.json']]
    sources += [E03/'contract_conditions.py',E03/'contract-condition-results.json',E03/'contract-conditions.md',
                HERE/'audit.md',ROOT/'docs/plans/accounting-financing-remedy-state-binding-20261026.md']
    pins.update({str(p.relative_to(ROOT)):sha(p) for p in sources if p.is_file()})
    save('source-lock.json',pins)
    for n in ['remedy_execution.py','verify.py','audit.md']:(OUT/n).write_bytes((HERE/n).read_bytes())
    # Retained literal expected outcomes are independent of this translation.
    translated=[]
    for row in old['cases']:
        facts=deepcopy(row['facts']);r=t.assess(row['method'],facts)
        check(row['id']+'.classification',r['status'],row['expected'])
        check(row['id']+'.input_preserved',facts,row['facts'])
        check(row['id']+'.admission',r['source_admission'] is False and r['accounting_admission'] is False)
        translated.append(dict(case=row['id'],expected=row['expected'],result=r))
    by_id={x['id']:x for x in old['cases']}
    for row in old['mutations']:
        result=t.assess(by_id[row['case']]['method'],by_id[row['case']]['facts'])
        check(row['id']+'.contrary_policy_rejected',result['status']!=row['incorrect_result'])

    original=settlement[1];funded=original['independent_prefixes'][3]['after']
    initial=dict(series='hypothetical-A',clause_status='unknown',clause_date='unknown',clause_economic_sha256='unknown',
                 acceleration_status='not_satisfied',last_action='supplied_initial',evidence_digest='none')
    book,schemas,extension=e.extended_state(funded,original['program']['schemas'],initial,
      'Synthetic W05 hypothesis: selected E03 conditional clauses apply to this series; no issuer/legal admission')
    selection=e.make_selection(book,schemas,'hypothetical-A');start=deepcopy(book)
    observed=[];states={};ordinal=0
    def event(method,facts,date):
        nonlocal ordinal
        ordinal+=1
        return dict(id='remedy.'+str(ordinal),date=date,series='hypothetical-A',method=method,facts=deepcopy(facts),
                    provenance='Explicit conditional findings for the synthetic series; source applicability not admitted')
    def step(name,ev,changes):
        nonlocal book
        before=deepcopy(book);r=run(selection,book,ev,schemas)
        check(name+'.status',r['status'],'proposed_conditional_status')
        expected=deepcopy(before);expected['date']=ev['date'];expected['seen'].append(ev['id'])
        if ev['method']=='event_clause':
            economic=dict(profile=before['profile'],context=before['context'],period=before['period'],
              accounts=before['accounts'],balances=before['balances'],cash_account=before['cash_account'],flows=before['flows'],
              memory={n:v for n,v in before['memory'].items() if n!='contract_status'},
              memory_types={n:v for n,v in before['memory_types'].items() if not n.startswith('/contract_status/')})
            changes=dict(changes,clause_economic_sha256=t.core.digest(economic))
        expected['memory']['contract_status'].update(last_action=ev['method'],evidence_digest=t.core.digest(ev),**changes)
        check(name+'.full_after',r['after'],expected)
        check(name+'.journal',r['transition']['journal'],{a:'0/1' for a in before['accounts']})
        check(name+'.flows',r['transition']['flows'],[])
        check(name+'.input_preserved',book,before)
        check(name+'.history',r['after']['memory']['debt_terms'],before['memory']['debt_terms'])
        observed.append(dict(case=name,event=ev,before=before,result=r,expected=expected))
        book=deepcopy(r['after']);states[name]=deepcopy(book)
    ev=event('event_clause',by_id['actual_applicability_unknown']['facts'],'2027-07-02')
    refusal('unknown_applicability',run(selection,book,ev,schemas),'unresolved')
    step('unpaid_clause',event('event_clause',by_id['principal_unpaid_due']['facts'],'2027-07-02'),
         dict(clause_status='satisfied',clause_date='2027-07-02'))
    check('clause_does_not_accelerate',book['memory']['contract_status']['acceleration_status'],'not_satisfied')
    step('no_declaration',event('new_acceleration',by_id['nonbankruptcy_no_declaration']['facts'],'2027-07-02'),{})
    step('declared_acceleration',event('new_acceleration',by_id['nonbankruptcy_declared']['facts'],'2027-07-02'),
         dict(acceleration_status='satisfied'))

    # Extend only the existing late-settlement schema; preserve its expressions.
    entry=deepcopy(original['program']['registry']['entries']['settle_late'])
    old_method=deepcopy(entry['method']);entry['method']['memory']['definition']['state_schema']=book['memory_schema']
    changed=deepcopy(old_method);changed['memory']['definition']['state_schema']=book['memory_schema']
    check('settlement_only_schema_change',entry['method'],changed)
    command=deepcopy(original['program']['commands'][4]);command['event']['id']='settlement.after_acceleration'
    request=dict(profile=e.engine.PROFILE,expected_state_sha256=t.core.digest(book),expected_method_sha256=t.core.digest(entry['method']),
                 method=entry['method'],event=clock.event_for(entry,command['event']),schemas=schemas)
    before=deepcopy(book);settled=e.engine.propose(book,request)
    check('late_settlement.proposed',settled['status'],'proposed')
    expected=deepcopy(book);expected['date']='2027-07-03';expected['seen'].append(command['event']['id'])
    roles=entry['method']['account_map'];expected['balances'][roles['cash']]='0/1';expected['balances'][roles['debt']]='0/1'
    expected['memory']['debt_terms'].update(outstanding='0/1',arrears='0/1')
    flow=dict(id=t.core.digest([command['event']['id'],'settle_late']),entity=book['context']['entity'],book=book['context']['book'],
      currency='USD',event_id=command['event']['id'],date='2027-07-03',activity='financing',origin='settle_late',amount='-40/1')
    expected['flows'].append(flow)
    journal={a:'0/1' for a in book['accounts']};journal[roles['cash']]='-40/1';journal[roles['debt']]='40/1'
    check('late_settlement.full_after',settled['after'],expected)
    check('late_settlement.journal',settled['journal'],journal);check('late_settlement.flows',settled['flows'],[flow])
    observed.append(dict(case='late_settlement',before=before,event=command['event'],result=settled,expected=expected));book=deepcopy(settled['after'])
    step('paid_clause',event('event_clause',by_id['principal_paid']['facts'],'2027-07-03'),dict(clause_status='not_satisfied',clause_date='2027-07-03'))
    step('no_new_trigger_after_cure',event('new_acceleration',by_id['acceleration_event_cured']['facts'],'2027-07-03'),{})
    step('cure_without_rescission',event('after_rescission',by_id['cure_without_rescission']['facts'],'2027-07-03'),dict(acceleration_status='satisfied'))
    step('effective_rescission',event('after_rescission',by_id['rescission_complete']['facts'],'2027-07-03'),dict(acceleration_status='not_satisfied'))
    check('history_retained_after_rescission',book['memory']['debt_terms']['missed_amount'],'40/1')
    check('missed_flag_retained_after_rescission',book['memory']['debt_terms']['missed'],True)

    def bad_event(name,state,method,facts,date,expected_status,patch=None):
        ev=event(method,facts,date)
        if patch:patch(ev)
        original_state=deepcopy(state);r=run(selection,state,ev,schemas)
        refusal(name,r,expected_status);check(name+'.input_preserved',state,original_state)
    bad_event('false_unpaid_after_payment',book,'event_clause',by_id['principal_unpaid_due']['facts'],'2027-07-03','invalid')
    bad_event('false_continuing_after_payment',states['paid_clause'],'new_acceleration',by_id['nonbankruptcy_declared']['facts'],'2027-07-03','invalid')
    bad_event('stale_clause_observation',states['unpaid_clause'],'new_acceleration',by_id['nonbankruptcy_declared']['facts'],'2027-07-03','unresolved')
    bad_event('contradictory_existing_acceleration',states['effective_rescission'],'after_rescission',by_id['rescission_complete']['facts'],'2027-07-03','invalid')
    bad_event('unknown_rescission_deposit',states['cure_without_rescission'],'after_rescission',by_id['rescission_deposit_missing']['facts'],'2027-07-03','unresolved')
    bad_event('wrong_series',start,'event_clause',by_id['principal_unpaid_due']['facts'],'2027-07-02','invalid',lambda x:x.update(series='B'))
    bad_event('earlier_event_date',book,'event_clause',by_id['principal_paid']['facts'],'2027-07-01','invalid')
    duplicate=observed[-1]['event']['id']
    bad_event('duplicate_event',book,'event_clause',by_id['principal_paid']['facts'],'2027-07-03','invalid',lambda x:x.update(id=duplicate))
    ev=event('event_clause',by_id['principal_paid']['facts'],'2027-07-03');call=e.make_call(selection,book,ev,schemas,t.core.digest(selection))
    ev['provenance']='Changed evidence'
    refusal('stale_event',e.execute(selection,book,ev,schemas,t.core.digest(selection),call),'invalid')
    h='0'*64;refusal('unreviewed_selection',e.execute(selection,book,ev,schemas,h,e.make_call(selection,book,ev,schemas,h)),'invalid')
    # Retest the preserved defect with a payment at the exact observation date.
    source=states['unpaid_clause'];same_event=deepcopy(command['event'])
    same_event.update(id='same_day_settlement',date='2027-07-02')
    same_request=deepcopy(request);same_request.update(expected_state_sha256=t.core.digest(source),
      event=clock.event_for(entry,same_event))
    same_paid=e.engine.propose(source,same_request)
    check('same_day.payment',same_paid['status'],'proposed')
    same_book=same_paid['after'];ev=event('new_acceleration',by_id['nonbankruptcy_declared']['facts'],'2027-07-02')
    refusal('same_day_stale_acceleration',run(selection,same_book,ev,schemas),'unresolved')
    check('payment_changes_economic_digest',e.economic_digest(source)!=e.economic_digest(same_book))
    check('pure_remedy_preserves_economic_digest',e.economic_digest(start),e.economic_digest(states['declared_acceleration']))
    for name,change in [
      ('balanced_reallocation',lambda b:b['balances'].update({roles['cash']:'39/1',roles['debt']:'-39/1'})),
      ('noncontract_memory',lambda b:b['memory']['complement'].update(tag='new_evidence')),
      ('cash_flow_evidence',lambda b:b['flows'][-1].update(origin='revised_origin'))]:
        altered=deepcopy(source);change(altered);e.engine.validate_book(altered,schemas)
        refusal(name+'.stale',run(selection,altered,ev,schemas),'unresolved')
    refreshed_event=event('event_clause',by_id['principal_paid']['facts'],'2027-07-02')
    fresh=run(selection,same_book,refreshed_event,schemas)
    check('same_day_fresh_observation',fresh['status'],'proposed_conditional_status')
    next_event=event('new_acceleration',by_id['acceleration_event_cured']['facts'],'2027-07-02')
    no_trigger=run(selection,fresh['after'],next_event,schemas)
    check('same_day_consistent_no_trigger',no_trigger['status'],'proposed_conditional_status')
    check('same_day_paid_no_acceleration',no_trigger['after']['memory']['contract_status']['acceleration_status'],'not_satisfied')
    check('same_day_history_retained',no_trigger['after']['memory']['debt_terms']['missed_amount'],'40/1')
    save('same-day-repair.json',dict(payment_request=same_request,payment=same_paid,
      stale_event=ev,refreshed_event=refreshed_event,refreshed=fresh,next_event=next_event,result=no_trigger))
    for n,h in pins.items():check('protected.'+n,sha(ROOT/n),h)
    save('classifications.json',translated);save('trace.json',dict(extension=extension,selection=selection,initial=start,trace=observed,final=book))
    save('controls.json',controls);save('checks.json',dict(passed=True,classifications=len(translated),transitions=len(observed),controls=len(controls),assertions=len(checks),checks=checks))
    summary=dict(passed=True,classifications=len(translated),transitions=len(observed),controls=len(controls),assertions=len(checks),protected_files=len(pins))
    save('run-manifest.json',dict(**summary,command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 data/accounting-master/financing-remedy-state-binding-20261026/verify.py',
      git_commit='unusable repository marker; no commit invented',environment=dict(python=platform.python_version(),platform=platform.platform()),cpu_gpu='CPU; GPU intentionally hidden',
      random_seeds='N/A deterministic',wall_seconds=time.monotonic()-started,data_version=sha(E03/'contract-condition-results.json'),
      plan='docs/plans/accounting-financing-remedy-state-binding-20261026.md',result='data/accounting-master/financing-remedy-state-binding-20261026/result.md',
      artifact_paths=['source-lock.json','classifications.json','trace.json','controls.json','checks.json'],timestamp_utc=datetime.now(timezone.utc).isoformat()))
    print(json.dumps(summary))

if __name__=='__main__':main()
