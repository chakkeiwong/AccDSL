from pathlib import Path
from copy import deepcopy
from fractions import Fraction as Q
import importlib.util,sys
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'scripts'))
import second_assessed_carry_v1 as m
s=importlib.util.spec_from_file_location('second_carry_deferred_examples',ROOT/'data/accounting-master/following-deferred-assessment-20261024/examples.py')
previous=importlib.util.module_from_spec(s);s.loader.exec_module(previous);known=previous.known

def request(prior=None,findings=None):
    return m.request(previous.scenario() if prior is None else prior,'second-carry-2027',
        {'profile':m.MODEL,'selected':known()},{'start':'2027-01-01','end_exclusive':'2028-01-01'},
        findings if findings is not None else {k:{'status':'unknown','reason':'No new admission evidence'} for k in m.FINDINGS})

def positive_profit():
    reassessment=previous.previous
    return request(previous.scenario(reassessment.scenario('-18/1',reassessment.previous.return_scenario())))

def zero_profit():
    reassessment=previous.previous;vintage=reassessment.previous
    initial=vintage.assessment();continued=vintage.scenario([vintage.depreciation()],initial)
    q=reassessment.scenario('0/1',continued)
    return request(previous.scenario(q,ppe_base='100/1',recognized='40/1',capacity='40/1'))

def paid_vintages(old='19/4',new='5/1'):
    reassessment=previous.previous;vintage=reassessment.previous
    initial=vintage.assessment();ops=[vintage.payment(initial,old,new),vintage.depreciation()]
    q=reassessment.scenario('20/1',vintage.scenario(ops,initial))
    return request(previous.scenario(q))

def cases():
    rows=[]
    def add(name,q,status='complete_provisional'):rows.append({'case':name,'request':deepcopy(q),'expected_status':status})
    base=request();add('negative_profit',base);add('positive_profit',positive_profit());add('zero_profit',zero_profit())
    add('fully_paid_vintages',paid_vintages());add('old_paid_current_partial',paid_vintages(new='2/1'))
    reassessment=previous.previous;vintage=reassessment.previous;initial=vintage.assessment()
    add('unpaid_vintages',request(previous.scenario(reassessment.scenario('20/1',vintage.scenario([vintage.depreciation()],initial)))))
    add('loss_and_recognition_history',request(previous.loss_scenario()))
    for value,name in [(True,'asserted_true'),(False,'asserted_false')]:
        add(name,request(findings={k:known(value) for k in m.FINDINGS}))
    for name,mutate,status in [
        ('stale_prior',lambda q:q.update(prior_sha256='0'*64),'invalid'),
        ('duplicate_carry',lambda q:q.update(id='following-deferred-assessment'),'invalid'),
        ('gap',lambda q:q['next_period'].update(start='2027-01-02'),'invalid'),
        ('overlap',lambda q:q['next_period'].update(start='2026-12-31'),'invalid'),
        ('empty_period',lambda q:q['next_period'].update(end_exclusive='2027-01-01'),'invalid'),
        ('unselected_model',lambda q:q['model'].update(selected=known(False)),'unsupported'),
        ('unknown_model',lambda q:q['model'].update(selected={'status':'unknown','reason':'Missing'}),'unresolved'),
        ('strict_annual_model',lambda q:q['model'].update(profile='certified_annual_close_v1'),'unsupported'),
        ('missing_finding',lambda q:q['findings'].pop('event_coverage'),'invalid'),
        ('mistyped_finding',lambda q:q['findings'].update(event_coverage=known(1)),'invalid'),
        ('operations_not_supported',lambda q:q.update(operations=[]),'invalid')]:
        q=deepcopy(base);mutate(q);add(name,q,status)
    partial=reassessment.scenario(end='2026-10-01',through='2026-09-30')
    add('incomplete_year',request(previous.scenario(partial)),'unresolved')
    q=deepcopy(base);q['prior_request']['recovery_capacity']={'status':'unknown','reason':'Missing'}
    q['prior_sha256']=m.book.digest(q['prior_request']);add('prior_unknown',q,'unresolved')
    return rows
