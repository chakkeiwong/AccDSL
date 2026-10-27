"""Authored fiscal clock cases; no estimates or issuer-specific tax claims."""
from copy import deepcopy
from pathlib import Path
from fractions import Fraction as Q
import importlib.util
import sys

ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'scripts'))
import mixed_event_timeline_v2 as timeline

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

scheduled=load('assessment_schedule_examples','data/accounting-master/state-decision-schedule-20261025/examples.py')
annual=load('assessment_annual_examples','data/accounting-master/reusable-annual-interface-20261025/examples.py')

def start():return scheduled.start()

def assessment(state,identity='timeline-assessment',mode='first',end='2027-01-03'):
    # Use no hypothetical current adjustment. The runtime computes taxable
    # income from the actual-turn book, not this construction-time snapshot.
    pretax=-sum(Q(state['after']['balances'][k]) for k in timeline.runtime.annual.population(state)['pretax_accounts'])
    op=annual.assessment(state,str(pretax),identity,mode,end)
    assert all(Q(row['amount'])==0 for row in op['event']['allocations'])
    for row in op['event']['allocations']:
        row['origin']['reference']='Authored zero current adjustment; no statutory or source admission.'
    return op

def root(state,assessment_first=False):
    body=scheduled.root(state);body['profile']=timeline.PROFILE
    body['schedules'][0]['calendar']={'kind':'explicit_dates','dates':['2027-01-02']}
    body['operations']=[{'id':'assess-through-jan2','priority':5 if assessment_first else 20,
        'date':'2027-01-02','operation':assessment(state)}]
    return body

def manual_decision(state,body,at='2027-01-02',index=0):
    schedule=body['schedules'][0];token=timeline.digest([body['id'],schedule['id'],index])
    template=deepcopy(schedule['template'])
    template['event'].update(id='scheduled-event:'+token,date=at)
    return {'profile':timeline.decision.PROFILE,'id':'scheduled-decision:'+token,
        'expected_state_sha256':timeline.digest(state),'context':deepcopy(body['context']),
        'decision_date':at,'scenario':deepcopy(body['scenario']),**template}

def replacement_root(state):
    body=root(state)
    sale=scheduled.decision_examples.native.sale('second-partial-sale','1/2','15/2',day='2027-01-03')
    replace=assessment(state,'timeline-replacement','replace','2027-01-04')
    body['operations'] += [
        {'id':'second-sale','date':'2027-01-03','priority':10,'operation':sale},
        {'id':'replacement','date':'2027-01-03','priority':20,'operation':replace}]
    return body

def cases():
    s=start();regular=root(s);early=root(s,True);unknown=deepcopy(regular);false=deepcopy(regular)
    unknown['operations'][0]['operation']['event']['information']['rate']={'status':'unknown','reason':'No rate supplied'}
    false['operations'][0]['operation']['event']['model']['selected']=annual.known(False)
    wrong=deepcopy(regular);wrong['operations'][0]['date']='2027-01-03'
    tie=deepcopy(regular);tie['operations'][0]['priority']=10
    bad=deepcopy(regular);bad['operations'][0]['operation']['event']['date']='2027-01-02'
    return {'sale_then_assessment':(s,regular,'complete_mixed_timeline'),
        'assessment_then_sale':(s,early,'stopped_provisional'),
        'replacement_after_second_sale':(s,replacement_root(s),'complete_mixed_timeline'),
        'unknown_rate_after_sale':(s,unknown,'stopped_provisional'),
        'false_model_after_sale':(s,false,'stopped_provisional'),
        'mismatched_timeline_date':(s,wrong,'invalid'),
        'ambiguous_priority':(s,tie,'unresolved'),
        'invented_event_date':(s,bad,'invalid')}
