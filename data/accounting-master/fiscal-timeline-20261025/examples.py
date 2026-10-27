"""Explicitly authored fiscal cases; measurement bytes never rebound by runner."""
from copy import deepcopy
from pathlib import Path
from functools import lru_cache
import importlib.util,sys
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'scripts'))
import mixed_event_timeline_v3 as timeline

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
previous=load('fiscal_current_examples','data/accounting-master/assessment-timeline-20261025/examples.py')
annual=previous.annual
start=previous.start

@lru_cache(maxsize=1)
def _prepared():
    state=start();body=previous.root(state);body['profile']=timeline.PROFILE
    body['schedules'][0]['calendar']={'kind':'explicit_dates','dates':['2027-12-31']}
    first=previous.assessment(state,'year-end-current',end='2028-01-01')
    body['operations']=[{'id':'year-end-current-entry','priority':20,'date':'2027-12-31','operation':first}]
    request=previous.manual_decision(state,body,at='2027-12-31')
    sale=timeline.decision.apply(state,request,timeline.decision.propose(state,request))
    assert sale['status']=='applied_provisional',sale
    current=timeline.runtime.transition(sale['after'],first)
    # This is scenario authoring using the exact explicit prefix. The timeline
    # receives already fixed bytes; it cannot generate or refresh measurements.
    deferred=annual.deferred(current['after'],'year-end-deferred',capacity='12/1',recognized='12/1')
    recognition=timeline.runtime.transition(current['after'],deferred)
    carry=annual.carry(recognition['after'],'year-end-carry')
    final=timeline.runtime.transition(recognition['after'],carry)
    body['operations'] += [
        {'id':'deferred-entry','priority':40,'date':'2027-12-31','operation':deferred},
        {'id':'carry-entry','priority':10,'date':'2028-01-01','operation':carry}]
    return state,body,{'request':request,'sale':sale,'current':current,'deferred':recognition,'carry':final}

def prepared():return deepcopy(_prepared())

def payment_variant(refresh=False,after_deferred=False):
    state,body,manual=prepared()
    before=manual['deferred']['after'] if after_deferred else manual['current']['after']
    payment=annual.payment(before,['1/1','0/1','0/1'],'payment-at-close','2027-12-31')
    body['operations'].append({'id':'payment-entry','date':'2027-12-31',
        'priority':50 if after_deferred else 30,'operation':payment})
    paid=timeline.runtime.transition(before,payment)
    if refresh:
        # The caller expressly supplies a different measurement request and ID.
        # It is a new scenario, not an automatic repair of a stale request.
        op=annual.deferred(paid['after'],'expressly-new-deferred',capacity='12/1',recognized='12/1')
        body['operations'][1]['operation']=op
    return state,body

def next_period(state):
    body=previous.scheduled.root(state);body['profile']=timeline.PROFILE
    body['id']='next-period-calendar'
    body['schedules'][0]['calendar']={'kind':'explicit_dates','dates':['2028-01-02']}
    body['operations']=[]
    return body

def cases():
    state,body,manual=prepared();unknown=deepcopy(body);false=deepcopy(body)
    unknown['operations'][1]['operation']['event']['recovery_capacity']={'status':'unknown','reason':'No supplied recovery estimate'}
    # Use an actual native finding name; never invent a shape to test truth.
    false=deepcopy(body);key=timeline.runtime.annual.deferred.FINDINGS[0]
    false['operations'][1]['operation']['event']['findings'][key]=annual.known(False)
    before=deepcopy(body);before['operations'][1]['priority']=15
    missing=deepcopy(body);missing['operations'].pop(1)
    wrong=deepcopy(body);wrong['operations'][1]['date']='2027-12-30'
    wrong_carry=deepcopy(body);wrong_carry['operations'][2]['date']='2027-12-31'
    tie=deepcopy(body);tie['operations'][1]['priority']=20
    stale=payment_variant();fresh=payment_variant(True);late=payment_variant(after_deferred=True)
    return {'sale_current_deferred_carry':(state,body,'complete_mixed_timeline'),
        'stale_measurement_after_payment':(*stale,'stopped_provisional'),
        'explicit_new_measurement_after_payment':(*fresh,'complete_mixed_timeline'),
        'payment_after_deferred_blocks_carry':(*late,'stopped_provisional'),
        'unknown_capacity':(state,unknown,'stopped_provisional'),
        'false_deferred_finding':(state,false,'stopped_provisional'),
        'deferred_before_current':(state,before,'stopped_provisional'),
        'carry_without_deferred':(state,missing,'stopped_provisional'),
        'wrong_measurement_schedule_date':(state,wrong,'invalid'),
        'wrong_carry_schedule_date':(state,wrong_carry,'invalid'),
        'tied_assessments':(state,tie,'unresolved')}

if __name__=='__main__':
    import json
    s,b,m=prepared();r=timeline.run(s,b)
    print(json.dumps({'status':r['status'],'reason':r.get('reason'),
        'closing_balances':m['deferred']['after']['after']['balances'],
        'opening_balances':m['carry']['after']['after']['balances'],
        'carry_profit':m['carry']['details']['carried_profit'],
        'deferred_journal':m['deferred']['journal']}))
