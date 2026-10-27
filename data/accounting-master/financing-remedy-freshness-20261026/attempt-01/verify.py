"""One-shot typed conditional classifications and complete economic/history trace."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from datetime import datetime,timezone
import importlib.util,json,os,platform,sys,time
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

def expected_economic_digest(book):
    # Independent definition of the declared equivalence relation.
    expected={k:deepcopy(v) for k,v in book.items() if k not in {'date','seen','memory','memory_types'}}
    expected['memory']={k:deepcopy(v) for k,v in book['memory'].items() if k!='contract_status'}
    expected['memory_types']={k:deepcopy(v) for k,v in book['memory_types'].items()
                              if k.split('/')[1]!='contract_status'}
    return t.core.digest(expected)

def main():
    assert not OUT.exists(),'attempt_exists';OUT.mkdir();started=time.monotonic()
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1'
    old=read(E03/'contract-condition-results.json');settlement=read(E03/'settlement-cases.json')
    pins=read(HERE.parent/'financing-opening-invariants-20261026/attempt-02/source-lock.json')
    pins.update(read(HERE/'predecessor-lock.json'))
    for n,h in pins.items():assert sha(ROOT/n)==h,n
    sources=[Path(m.__file__).resolve() for m in list(sys.modules.values())
      if getattr(m,'__file__',None) and Path(m.__file__).resolve().is_relative_to(ROOT)]
    sources += [E03/'contract_conditions.py',E03/'contract-condition-results.json',E03/'contract-conditions.md',
                ROOT/'docs/plans/accounting-financing-remedy-freshness-20261026.md',ROOT/'docs/plans/accounting-financing-remedy-binding-20261026.md']
    pins.update({str(p.relative_to(ROOT)):sha(p) for p in sources if p.is_file()})
    save('source-lock.json',pins)
    for n in ['typed_conditions.py','remedy_execution.py','verify.py']:(OUT/n).write_bytes((HERE/n).read_bytes())
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
    initial=dict(series='hypothetical-A',clause_status='unknown',clause_date='unknown',
                 clause_kind='unknown',observed_economy_sha256='unknown',observed_evidence_revision='unknown',acceleration_status='not_satisfied',last_action='supplied_initial',evidence_digest='none')
    book,schemas,extension=e.extended_state(funded,original['program']['schemas'],initial,
      'Synthetic W05 hypothesis: selected E03 conditional clauses apply to this series; no issuer/legal admission')
    selection=e.make_selection(book,schemas,'hypothetical-A');start=deepcopy(book)
    observed=[];states={};ordinal=0
    def event(method,facts,date):
        nonlocal ordinal
        ordinal+=1
        return dict(id='remedy.'+str(ordinal),date=date,series='hypothetical-A',method=method,facts=deepcopy(facts),
                    evidence_revision='synthetic-view-1',provenance='Explicit conditional findings for the synthetic series; source applicability not admitted')
    def step(name,ev,changes):
        nonlocal book
        before=deepcopy(book);r=run(selection,book,ev,schemas)
        check(name+'.status',r['status'],'proposed_conditional_status')
        expected=deepcopy(before);expected['date']=ev['date'];expected['seen'].append(ev['id'])
        if ev['method']=='event_clause':
            changes=dict(changes,clause_kind=ev['facts']['kind'],observed_economy_sha256=expected_economic_digest(before),observed_evidence_revision=ev['evidence_revision'])
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

    # Reproduce the preserved same-day failure using the successor schema.
    discriminator=read(HERE.parent/'financing-remedy-binding-20261026/same-day-discriminator.json')
    check('predecessor_failure_retained',discriminator['discriminator_confirmed'])
    check('predecessor_incorrect_proposal',discriminator['result']['status'],'proposed_conditional_status')
    unpaid=states['unpaid_clause'];same_event=deepcopy(discriminator['payment_request']['event'])
    same_method=deepcopy(entry['method'])
    same_request=dict(profile=e.engine.PROFILE,expected_state_sha256=t.core.digest(unpaid),
      expected_method_sha256=t.core.digest(same_method),method=same_method,event=same_event,schemas=schemas)
    same_paid=e.engine.propose(unpaid,same_request)
    check('same_day_payment.proposed',same_paid['status'],'proposed')
    paid_state=same_paid['after']
    def old_economic_values(b):
        return dict(balances=b['balances'],flows=b['flows'],date=b['date'],
                    memory={k:v for k,v in b['memory'].items() if k!='contract_status'})
    check('same_day_payment.original_economic_result',old_economic_values(paid_state),old_economic_values(discriminator['paid_book']))
    stale=event('new_acceleration',by_id['nonbankruptcy_declared']['facts'],'2027-07-02')
    stale['id']=discriminator['command']['id']
    same_refusal=run(selection,paid_state,stale,schemas)
    refusal('same_day_stale_clause',same_refusal,'unresolved')
    check('same_day_stale_reason',same_refusal['reason'],'economic_state_changed_since_observation')
    check('paid_state_keeps_old_finding',paid_state['memory']['contract_status']['clause_status'],'satisfied')
    check('paid_state_no_invented_acceleration',paid_state['memory']['contract_status']['acceleration_status'],'not_satisfied')
    check('economic_projection_matches_oracle',e.economic_digest(paid_state),expected_economic_digest(paid_state))
    check('economic_change_detected',e.economic_digest(unpaid)!=e.economic_digest(paid_state))
    check('status_only_changes_do_not_invalidate',e.economic_digest(states['declared_acceleration']),e.economic_digest(unpaid))
    bad_event('changed_external_view',unpaid,'new_acceleration',by_id['nonbankruptcy_declared']['facts'],'2027-07-02','unresolved',lambda x:x.update(evidence_revision='synthetic-corrected-view-2'))
    bad_event('missing_external_view',unpaid,'new_acceleration',by_id['nonbankruptcy_declared']['facts'],'2027-07-02','unresolved',lambda x:x.update(evidence_revision=None))
    bad_event('automatic_from_principal',unpaid,'new_acceleration',by_id['automatic_qualified_event']['facts'],'2027-07-02','invalid')
    refreshed_event=event('event_clause',by_id['principal_paid']['facts'],'2027-07-02')
    refreshed=run(selection,paid_state,refreshed_event,schemas)
    check('same_day_fresh_paid_assessment',refreshed['status'],'proposed_conditional_status')
    refreshed_expected=deepcopy(paid_state);refreshed_expected['seen'].append(refreshed_event['id'])
    refreshed_expected['memory']['contract_status'].update(clause_status='not_satisfied',clause_date='2027-07-02',
      clause_kind='principal',observed_economy_sha256=expected_economic_digest(paid_state),
      observed_evidence_revision='synthetic-view-1',last_action='event_clause',evidence_digest=t.core.digest(refreshed_event))
    check('same_day_fresh_full_state',refreshed['after'],refreshed_expected)
    no_trigger_event=event('new_acceleration',by_id['acceleration_event_cured']['facts'],'2027-07-02')
    no_trigger=run(selection,refreshed['after'],no_trigger_event,schemas)
    check('same_day_fresh_no_trigger',no_trigger['status'],'proposed_conditional_status')
    no_trigger_expected=deepcopy(refreshed_expected);no_trigger_expected['seen'].append(no_trigger_event['id'])
    no_trigger_expected['memory']['contract_status'].update(last_action='new_acceleration',evidence_digest=t.core.digest(no_trigger_event))
    check('same_day_no_trigger_full_state',no_trigger['after'],no_trigger_expected)
    bankruptcy_event=event('event_clause',by_id['bankruptcy_supplied_finding']['facts'],'2027-07-02')
    bankruptcy=run(selection,start,bankruptcy_event,schemas)
    check('bankruptcy_observation',bankruptcy['status'],'proposed_conditional_status')
    automatic_event=event('new_acceleration',by_id['automatic_without_notice_facts']['facts'],'2027-07-02')
    automatic=run(selection,bankruptcy['after'],automatic_event,schemas)
    check('matched_automatic_route',automatic['status'],'proposed_conditional_status')
    auto_expected=deepcopy(start);auto_expected['seen'] += [bankruptcy_event['id'],automatic_event['id']]
    auto_expected['memory']['contract_status'].update(clause_status='satisfied',clause_date='2027-07-02',clause_kind='bankruptcy',
      observed_economy_sha256=expected_economic_digest(start),observed_evidence_revision='synthetic-view-1',
      acceleration_status='satisfied',last_action='new_acceleration',evidence_digest=t.core.digest(automatic_event))
    check('matched_automatic_full_state',automatic['after'],auto_expected)
    save('freshness-cases.json',dict(payment=same_paid,stale_refusal=same_refusal,
      refreshed=refreshed,no_trigger=no_trigger,bankruptcy=bankruptcy,automatic=automatic,
      scope='Hypothetical supplied views; no actual-source admission'))
    for n,h in pins.items():check('protected.'+n,sha(ROOT/n),h)
    save('classifications.json',translated);save('trace.json',dict(extension=extension,selection=selection,initial=start,trace=observed,final=book))
    save('controls.json',controls);save('checks.json',dict(passed=True,classifications=len(translated),transitions=len(observed),controls=len(controls),assertions=len(checks),checks=checks))
    summary=dict(passed=True,classifications=len(translated),transitions=len(observed),controls=len(controls),assertions=len(checks),protected_files=len(pins))
    save('run-manifest.json',dict(**summary,command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 data/accounting-master/financing-remedy-freshness-20261026/verify.py',
      git_commit='unusable repository marker; no commit invented',environment=dict(python=platform.python_version(),platform=platform.platform()),cpu_gpu='CPU; GPU intentionally hidden',
      random_seeds='N/A deterministic',wall_seconds=time.monotonic()-started,data_version=sha(E03/'contract-condition-results.json'),
      plan='docs/plans/accounting-financing-remedy-freshness-20261026.md',result='data/accounting-master/financing-remedy-freshness-20261026/result.md',
      artifact_paths=['source-lock.json','classifications.json','trace.json','controls.json','checks.json'],timestamp_utc=datetime.now(timezone.utc).isoformat()))
    print(json.dumps(summary))

if __name__=='__main__':main()
