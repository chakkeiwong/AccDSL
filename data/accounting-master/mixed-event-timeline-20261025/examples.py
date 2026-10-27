from copy import deepcopy
from pathlib import Path
import importlib.util
import sys
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'scripts'))
import mixed_event_timeline_v1 as timeline
spec=importlib.util.spec_from_file_location('mixed_schedule_examples',ROOT/'data/accounting-master/state-decision-schedule-20261025/examples.py')
scheduled=importlib.util.module_from_spec(spec);spec.loader.exec_module(scheduled)
def start():return scheduled.start()
def root(state,payment_first=True):
    body=scheduled.root(state);body['profile']=timeline.PROFILE
    schedule=body['schedules'][0];schedule['calendar']={'kind':'explicit_dates','dates':['2027-01-02']}
    template=schedule['template'];program=template['model']['program'];money=timeline.decision.types(state)['cash']
    program['inputs']['cash']={'type':deepcopy(money),'value':'unknown'}
    program['inputs']['threshold']={'type':deepcopy(money),'value':'unknown'}
    program['nodes'] += [{'id':'cash','op':'input','target':'cash'},{'id':'threshold','op':'input','target':'threshold'},
                         {'id':'below_threshold','op':'lt','args':['cash','threshold']},
                         {'id':'cash_guard','op':'if','args':['below_threshold','act','disabled']}]
    program['outputs']['execute']='cash_guard'
    template['bindings']['cash']={'kind':'state_cash'}
    template['bindings']['threshold']={'kind':'scenario','type':deepcopy(money),'value':'450/1','available_on':'2027-01-01','provenance':'Synthetic cash-sensitive rule for order testing; not an estimated reserve'}
    template['model']['provenance']='Authored stock/reserve rule enabled only below explicit cash threshold'
    operation=scheduled.decision_examples.native.previous.payment(state,['4/1','0/1'],'tax-cash','2027-01-02')
    operation['event']['authorization']['provenance']['reference']='Explicit hypothetical authorization for carried tax payment; no legal or source admission'
    body['operations']=[{'id':'pay-carried-tax','priority':5 if payment_first else 20,'date':'2027-01-02','operation':operation}]
    return body
