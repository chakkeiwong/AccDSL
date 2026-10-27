"""Explicit conditional carry; no annual acceptance inferred from findings."""
from pathlib import Path
from copy import deepcopy
import importlib.util,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts'))
import provisional_period_carry_v1 as m
spec=importlib.util.spec_from_file_location('carry_reassessment_examples',
    ROOT/'data/accounting-master/shared-tax-reassessment-20261024/examples.py')
previous=importlib.util.module_from_spec(spec);spec.loader.exec_module(previous)
known=previous.known


def request(taxable='21/1',paid=True,operations=None,findings=None):
    return m.request(previous.scenario(taxable,paid),'carry-2026',
        {'profile':m.MODEL,'selected':known()},
        {'start':'2026-01-01','end_exclusive':'2027-01-01'},
        findings if findings is not None else {k:{'status':'unknown','reason':'Not yet established for this synthetic carry'} for k in m.FINDINGS},
        operations or [])


def payment(amount='19/4',identity='carried-tax-payment',day='2026-01-01'):
    return {'kind':'tax_payment','event':{'id':identity,'date':day,'amount':amount,'authorization':known()}}


def depreciation(amount='10/1',identity='following-depreciation',day='2026-01-01'):
    return {'kind':'native','event':{'profile':m.book.EVENT,'module':'lease','event':{
        'id':identity,'date':day,'method':'lease.depreciate','lease_id':'lease1',
        'parameters':{'right_id':'A','amount':amount,'systematic_allocation_supported':True}}}}


def unsettled_return():
    start=previous.previous.origin()
    body=m.continuation.request(start,[])
    continued=m.continuation.run(body)
    prior=previous.from_continuation(body,continued)
    q=request();q['prior_request']=prior;q['prior_sha256']=m.book.digest(prior)
    q['operations']=[previous.previous.ordinary(i,'2026-01-01') for i in [1,2]]
    return q


def cases():
    rows=[]
    def add(name,body,status='complete_provisional',stop=None):
        rows.append({'case':name,'request':deepcopy(body),'expected_status':status,'expected_stop':stop})
    base=request()
    add('negative_profit',base);add('positive_profit',request('0/1',False))
    add('zero_profit',request('20/1',False));add('unpaid_tax',request('21/1',False))
    add('generated_loss',request('-19/1',False))
    q=deepcopy(base);origin=previous.origin_with_opening_loss(use='1/1')
    q['prior_request']=previous.scenario('21/1',False,origin=origin,
        uses=[{'lot_id':'original-loss','amount':'19/1'}],cap='19/1')
    q['prior_sha256']=m.book.digest(q['prior_request']);add('used_loss_history',q)
    add('pay_carried_tax',request(operations=[payment()]))
    add('payment_and_depreciation',request(operations=[payment(),depreciation()]))
    add('return_activity_after_carry',unsettled_return())
    for value,label in [(False,'false'),(True,'true')]:
        add('findings_'+label,request(findings={k:known(value) for k in m.FINDINGS}))
    for name,mutate,status in [
        ('strict_annual_mode',lambda q:q['model'].update(profile='strict_annual_close_v1'),'unsupported'),
        ('model_unknown',lambda q:q['model'].update(selected={'status':'unknown','reason':'Unselected'}),'unresolved'),
        ('model_false',lambda q:q['model'].update(selected=known(False)),'unsupported'),
        ('period_gap',lambda q:q['next_period'].update(start='2026-01-02'),'invalid'),
        ('period_overlap',lambda q:q['next_period'].update(start='2025-12-31'),'invalid'),
        ('empty_period',lambda q:q['next_period'].update(end_exclusive='2026-01-01'),'invalid'),
        ('duplicate_carry',lambda q:q.update(id='tax-payment'),'invalid'),
        ('stale_prior',lambda q:q.update(prior_sha256='0'*64),'invalid'),
        ('missing_finding',lambda q:q['findings'].pop('event_coverage'),'invalid'),
        ('mistyped_finding',lambda q:q['findings'].update(event_coverage=known(1)),'invalid')]:
        q=deepcopy(base);mutate(q);add(name,q,status)
    q=deepcopy(base);q['prior_request']['interval'].update(end_exclusive='2025-07-01',activity_through='2025-06-30')
    q['prior_sha256']=m.book.digest(q['prior_request']);add('incomplete_assessment',q,'unresolved')
    for name,op,stop in [('duplicate_prior_event',payment(identity='tax-payment'),'invalid'),
        ('duplicate_carry_event',payment(identity='carry-2026'),'invalid'),
        ('before_opening',payment(day='2025-12-31'),'invalid'),
        ('at_endpoint',payment(day='2027-01-01'),'invalid'),
        ('overpayment',payment('5/1'),'invalid'),
        ('unknown_payment',payment(),'unresolved')]:
        if name=='unknown_payment':op['event']['authorization']={'status':'unknown','reason':'No authority'}
        add(name,request(operations=[op]),'stopped_provisional',stop)
    add('cash_shortage',request('2000/1',True,operations=[payment('999/2')]),'stopped_provisional','funding_failure')
    add('completed_prefix',request(operations=[payment('1/1'),payment('5/1',identity='overpay')]),'stopped_provisional','invalid')
    return rows
