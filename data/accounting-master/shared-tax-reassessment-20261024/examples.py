from copy import deepcopy
from pathlib import Path
from fractions import Fraction as Q
import importlib.util,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts'))
import shared_tax_reassessment_v1 as m
spec=importlib.util.spec_from_file_location('reassessment_continuation_examples',
    ROOT/'data/accounting-master/shared-tax-continuation-20261024/examples.py')
previous=importlib.util.module_from_spec(spec);spec.loader.exec_module(previous)
known=previous.known


def origin_with_opening_loss(taxable='2/1',use='0/1'):
    q=previous.accrual(taxable);loss=q['loss_request'];s=loss['state']
    s['lots']=[{'id':'original-loss','origin_reference':'Explicit hypothetical opening inventory',
        'available_from':'2024-01-01','expiry':{'kind':'none','provenance':known()['provenance']},
        'original':'19/1','remaining':'19/1','used':'0/1','expired':'0/1','eligible':known()}]
    loss['state_sha256']=m.book.digest(s)
    loss['utilization_cap']=known('19/1')
    loss['uses']=[] if use=='0/1' else [{'lot_id':'original-loss','amount':use}]
    q['loss_request_sha256']=m.book.digest(loss)
    r=m.tax.propose(q);assert r['status']=='proposed',r.get('reason')
    return r['after']


def scenario(taxable='21/1',paid=True,origin=None,uses=None,cap='0/1',generation_id='replacement-loss'):
    start=previous.origin() if origin is None else origin
    operations=([previous.payment()] if paid else [])+[previous.ordinary(i) for i in [1,2,3,4]]
    body=m.continuation.request(start,operations);continued=m.continuation.run(body)
    assert continued['status']=='complete',continued.get('reason',continued.get('stop'))
    return from_continuation(body,continued,taxable,uses,cap,generation_id)


def from_continuation(body,continued,taxable='21/1',uses=None,cap='0/1',generation_id='replacement-loss'):
    pop=m.population(continued);declarations={}
    for k,kind in m.fields(pop).items():
        declarations[k]=known(True if kind=='boolean' else '0/1' if kind=='rational'
                              else 'Explicit synthetic reassessment information; no legal admission')
    original=body['origin']['accrual_request']['loss_request']['state']
    for k in ['jurisdiction','regime']:declarations[k]=known(original[k])
    declarations['rate']=known('1/4')
    adjustments=continued['after']['tax_adjustments']
    allocations=[{'id':'native-'+a['event_id'],'account':'revenue','amount':a['amount'],
                  'origin':{'kind':'native_return','event_id':a['event_id']}} for a in adjustments]
    native_total=sum(Q(a['amount']) for a in adjustments)
    pretax=-sum(Q(continued['after']['balances'][k]) for k in pop['pretax_accounts'])
    extra=Q(taxable)-pretax-native_total
    allocations.append({'id':'explicit-extra','account':'other_gains','amount':m.book.fmt(extra),
        'origin':{'kind':'assumption','reference':'Explicit cumulative taxable-profit control'}})
    declarations['income/revenue/current_adjustment']=known(m.book.fmt(native_total))
    declarations['income/other_gains/current_adjustment']=known(m.book.fmt(extra))
    interval={'start':'2024-01-01','end_exclusive':'2026-01-01','activity_through':'2025-12-31'}
    policy={'model':{'profile':m.losses.MODEL,'selected':known()},'utilization_cap':known(cap),
            'uses':deepcopy(uses or []),'generation':None}
    if Q(taxable)<0:
        policy['generation']={'id':generation_id,'eligible':known(),
                              'expiry':{'kind':'none','provenance':known()['provenance']}}
    return m.request(body,'replacement-assessment',{'profile':m.MODEL,'selected':known()},
                     interval,declarations,allocations,policy)


def cases():
    rows=[]
    def add(name,body,status):rows.append({'case':name,'request':deepcopy(body),'expected_status':status})
    positive=scenario();unpaid=scenario('1/1',False);negative=scenario('-19/1',False)
    add('positive_paid',positive,'proposed');add('positive_unpaid',scenario('21/1',False),'proposed')
    add('unpaid_reversal',unpaid,'proposed');add('paid_refund_route_refused',scenario('1/1',True),'unsupported')
    add('zero_total',scenario('0/1',False),'proposed');add('negative_generates_loss',negative,'proposed')
    add('fractional_total',scenario('1/3',False),'proposed')
    generated=previous.origin('-19/1')
    add('replace_provisional_loss',scenario('-7/1',False,origin=generated),'proposed')
    opening=origin_with_opening_loss(use='1/1')
    usage=scenario('21/1',False,origin=opening,uses=[{'lot_id':'original-loss','amount':'19/1'}],cap='19/1')
    add('reuse_original_inventory',usage,'proposed')
    mutations=[('missing_payable_basis',lambda q:q['information'].pop('basis/income_tax_payable/closing'),'unresolved'),
      ('unknown_rate',lambda q:q['information'].update(rate={'status':'unknown','reason':'Missing rate'}),'unresolved'),
      ('false_coverage',lambda q:q['information'].update(interval_coverage=known(False)),'unsupported'),
      ('extra_information',lambda q:q['information'].update(invented=known('0/1')),'invalid'),
      ('changed_regime',lambda q:q['information'].update(regime=known('other')),'invalid'),
      ('negative_rate',lambda q:q['information'].update(rate=known('-1/4')),'invalid'),
      ('missing_native_adjustment',lambda q:q['allocations'].pop(0),'invalid'),
      ('duplicate_allocation',lambda q:q['allocations'].append(deepcopy(q['allocations'][0])),'invalid'),
      ('changed_native_amount',lambda q:q['allocations'][0].update(amount='-23/1'),'invalid'),
      ('lease_basis_mismatch',lambda q:q['information'].update({'basis/rou/closing':known('1/1')}),'invalid'),
      ('stale_continuation',lambda q:q.update(continuation_sha256='0'*64),'invalid'),
      ('wrong_loss_opening',lambda q:q.update(original_loss_opening_sha256='0'*64),'invalid'),
      ('same_assessment_endpoint',lambda q:q['interval'].update(end_exclusive='2025-01-01',activity_through='2024-12-31'),'invalid'),
      ('endpoint_after_period',lambda q:q['interval'].update(end_exclusive='2027-01-01',activity_through='2026-12-31'),'invalid'),
      ('unknown_model',lambda q:q['model'].update(selected={'status':'unknown','reason':'No selection'}),'unresolved'),
      ('false_model',lambda q:q['model'].update(selected=known(False)),'unsupported')]
    for name,mutate,status in mutations:
        q=deepcopy(positive);mutate(q);add(name,q,status)
    q=deepcopy(usage);q['loss_policy']['utilization_cap']=known('18/1');add('loss_cap_exceeded',q,'invalid')
    q=deepcopy(negative);q['loss_policy']['generation']['eligible']={'status':'unknown','reason':'No eligibility'}
    add('unknown_generation_eligibility',q,'unresolved')
    q=deepcopy(positive);q['continuation_request']['operations'].append(previous.payment())
    q['continuation_sha256']=m.book.digest(q['continuation_request']);add('stopped_prefix',q,'unresolved')
    return rows
