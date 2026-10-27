"""Prepare a separate successor; never overwrite the date-only evidence."""
from pathlib import Path
from hashlib import sha256
import json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
OLD=HERE.parent/'financing-remedy-binding-20261026'
read=lambda p:json.loads(p.read_text())
sha=lambda p:sha256(p.read_bytes()).hexdigest()
assert not (HERE/'successor-sources.json').exists(),'already_prepared'
assert read(OLD/'attempt-01/checks.json')['passed']
assert read(OLD/'same-day-discriminator.json')['discriminator_confirmed']
for n,h in read(OLD/'attempt-01/source-lock.json').items():assert sha(ROOT/n)==h,n
text=(OLD/'remedy_execution.py').read_text()
text=text.replace('import typed_conditions as t','from pathlib import Path\nimport sys\nsys.path.append(str(Path(__file__).resolve().parent.parent/\'financing-remedy-binding-20261026\'))\nimport typed_conditions as t',1)
text=text.replace("PROFILE='SelectedConditionalRemedy/1'","PROFILE='SelectedConditionalRemedy/2'",1)
text=text.replace("'clause_date','acceleration_status'","'clause_date','clause_economic_sha256','acceleration_status'",1)
anchor='def make_selection(book,schemas,series):'
addition='''def economic_digest(book):
    """Fixed conservative projection; purely conditional bookkeeping is excluded."""
    economic={k:deepcopy(book[k]) for k in ['profile','context','period','accounts','balances','cash_account','flows']}
    economic['memory']={k:deepcopy(v) for k,v in book['memory'].items() if k!='contract_status'}
    economic['memory_types']={k:deepcopy(v) for k,v in book['memory_types'].items() if not k.startswith('/contract_status/')}
    return core.digest(economic)

'''
assert text.count(anchor)==1;text=text.replace(anchor,addition+anchor,1)
anchor="if status['clause_status']=='unknown' or status['clause_date']!=event['date']:"
replacement="if (status['clause_status']=='unknown' or status['clause_date']!=event['date'] or\n                status['clause_economic_sha256']!=economic_digest(book)):"
assert text.count(anchor)==1;text=text.replace(anchor,replacement,1)
text=text.replace("reason='same_date_clause_finding_required'","reason='current_economic_state_clause_finding_required'",1)
anchor="writes.update(clause_status=finding['status'],clause_date=event['date'])"
assert text.count(anchor)==1
text=text.replace(anchor,"writes.update(clause_status=finding['status'],clause_date=event['date'],clause_economic_sha256=economic_digest(book))",1)
assert not (HERE/'remedy_execution.py').exists();(HERE/'remedy_execution.py').write_text(text)
text=(OLD/'verify.py').read_text()
text=text.replace('import typed_conditions as t',"sys.path.append(str(Path(__file__).resolve().parent.parent/'financing-remedy-binding-20261026'))\nimport typed_conditions as t",1)
text=text.replace("clause_date='unknown',","clause_date='unknown',clause_economic_sha256='unknown',",1)
text=text.replace("for n in ['typed_conditions.py','remedy_execution.py','verify.py','audit.md']:","for n in ['remedy_execution.py','verify.py','audit.md']:",1)
text=text.replace("ROOT/'docs/plans/accounting-financing-remedy-binding-20261026.md'","ROOT/'docs/plans/accounting-financing-remedy-state-binding-20261026.md'",1)
text=text.replace("financing-remedy-binding-20261026/verify.py'","financing-remedy-state-binding-20261026/verify.py'",1)
text=text.replace("plan='docs/plans/accounting-financing-remedy-binding-20261026.md'","plan='docs/plans/accounting-financing-remedy-state-binding-20261026.md'",1)
text=text.replace("result='data/accounting-master/financing-remedy-binding-20261026/result.md'","result='data/accounting-master/financing-remedy-state-binding-20261026/result.md'",1)
anchor="    sources += [E03/'contract_conditions.py'"
replacement="""    predecessor=HERE.parent/'financing-remedy-binding-20261026'
    sources += [predecessor/n for n in ['remedy_execution.py','verify.py','typed_conditions.py',
      'same-day-discriminator.py','same-day-discriminator.json','result.md','attempt-01/checks.json','attempt-01/trace.json']]
    sources += [E03/'contract_conditions.py'"""
assert text.count(anchor)==1;text=text.replace(anchor,replacement,1)
anchor="        expected['memory']['contract_status'].update(last_action=ev['method'],evidence_digest=t.core.digest(ev),**changes)"
addition="""        if ev['method']=='event_clause':
            economic=dict(profile=before['profile'],context=before['context'],period=before['period'],
              accounts=before['accounts'],balances=before['balances'],cash_account=before['cash_account'],flows=before['flows'],
              memory={n:v for n,v in before['memory'].items() if n!='contract_status'},
              memory_types={n:v for n,v in before['memory_types'].items() if not n.startswith('/contract_status/')})
            changes=dict(changes,clause_economic_sha256=t.core.digest(economic))
"""
assert text.count(anchor)==1;text=text.replace(anchor,addition+anchor,1)
anchor="    for n,h in pins.items():check('protected.'+n,sha(ROOT/n),h)"
addition="""    # Retest the preserved defect with a payment at the exact observation date.
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
"""
assert text.count(anchor)==1;text=text.replace(anchor,addition+anchor,1)
assert not (HERE/'verify.py').exists();(HERE/'verify.py').write_text(text)
(HERE/'successor-sources.json').write_text(json.dumps(dict(predecessor={n:sha(OLD/n) for n in ['remedy_execution.py','verify.py','typed_conditions.py']},
 successor={n:sha(HERE/n) for n in ['remedy_execution.py','verify.py']},classification_unchanged=True),indent=2)+chr(10))
print(json.dumps(dict(prepared=True,successor='SelectedConditionalRemedy/2',classification_unchanged=True)))
