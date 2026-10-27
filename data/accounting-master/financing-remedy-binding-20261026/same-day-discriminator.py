"""Preserved successor diagnostic: a date match does not establish fresh state."""
from copy import deepcopy
from pathlib import Path
from hashlib import sha256
import json
import remedy_execution as r
import company_method_clock_v1 as clock
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
out=HERE/'same-day-discriminator.json'
assert not out.exists(),'discriminator_already_recorded'
read=lambda p:json.loads(p.read_text())
for n,h in read(HERE/'attempt-01/source-lock.json').items():
    assert sha256((ROOT/n).read_bytes()).hexdigest()==h,n
trace=read(HERE/'attempt-01/trace.json');before=trace['trace'][0]['result']['after']
old=read(HERE.parent/'gap-program-20261026/settlement-cases.json')[1]
entry=deepcopy(old['program']['registry']['entries']['settle_late'])
entry['method']['memory']['definition']['state_schema']=before['memory_schema']
schemas=deepcopy(old['program']['schemas'])
# The first saved remedy request retains the extended state schema.
schemas[before['memory_schema']]=trace['trace'][0]['result']['request']['schemas'][before['memory_schema']]
event=deepcopy(old['program']['commands'][4]['event'])
event.update(id='same_day_settlement',date='2027-07-02')
request=dict(profile=r.engine.PROFILE,expected_state_sha256=r.core.digest(before),
 expected_method_sha256=r.core.digest(entry['method']),method=entry['method'],
 event=clock.event_for(entry,event),schemas=schemas)
paid=r.engine.propose(before,request);assert paid['status']=='proposed',paid.get('reason')
cases=read(HERE.parent/'gap-program-20261026/contract-condition-results.json')['cases']
facts=next(x['facts'] for x in cases if x['id']=='nonbankruptcy_declared')
command=dict(id='stale_same_day_acceleration',date='2027-07-02',series='hypothetical-A',
 method='new_acceleration',facts=facts,provenance='Hypothetical stale continuing-event finding after same-date payment')
selection=trace['selection'];h=r.core.digest(selection)
result=r.execute(selection,paid['after'],command,schemas,h,r.make_call(selection,paid['after'],command,schemas,h))
assert paid['after']['memory']['debt_terms']['outstanding']=='0/1'
assert result['status']=='proposed_conditional_status',result
payload=dict(discriminator_confirmed=True,defect='Same-date payment leaves stored satisfied clause stale; date-only binding accepts new acceleration',
 paid_book=paid['after'],payment_request=request,payment_result=paid,selection=selection,command=command,result=result,
 expected_successor_status='unresolved',required_repair='Bind the clause observation to the economic state, in addition to its date',
 predecessor_checks_unchanged=True,scope='Synthetic implementation mismatch; no actual legal conclusion')
out.write_text(json.dumps(payload,indent=2)+chr(10))
print(json.dumps({k:payload[k] for k in ['discriminator_confirmed','defect','expected_successor_status']}))
