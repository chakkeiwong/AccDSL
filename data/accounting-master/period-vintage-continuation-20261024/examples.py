from pathlib import Path
from copy import deepcopy
from fractions import Fraction as Q
from functools import lru_cache
import importlib.util,sys
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'scripts'))
import period_vintage_continuation_v1 as m
s=importlib.util.spec_from_file_location('period_vintage_boundary_examples',ROOT/'data/accounting-master/second-assessed-carry-20261024/examples.py')
previous=importlib.util.module_from_spec(s);s.loader.exec_module(previous);known=previous.known
vintage=previous.previous.previous.previous

@lru_cache(maxsize=1)
def default_boundary():return previous.request()

def payment(prior=None,old='1/1',new='2/1',identity='period-payment',day='2027-01-01'):
    prior=default_boundary() if prior is None else prior
    initial=prior['prior_request']['prior_request']['continuation_request']['assessment_request']
    allocations=[{'vintage_id':key,'amount':value} for key,value in zip(vintage.ids(initial),[old,new]) if Q(value)!=0]
    return {'kind':'allocated_tax_payment','event':{'id':identity,'date':day,
        'amount':m.book.fmt(Q(old)+Q(new)),'authorization':known(),'allocations':allocations}}

def depreciation(amount='2/1',identity='period-depreciation',day='2027-01-02'):
    return vintage.depreciation(amount=amount,identity=identity,day=day)

def scenario(operations=None,prior=None):
    prior=default_boundary() if prior is None else prior
    return m.request(prior,[payment(prior),depreciation()] if operations is None else operations)

def funding_scenario():
    reassessment=previous.previous.previous
    carried=previous.request(previous.previous.scenario(reassessment.scenario('2000/1')))
    return scenario([payment(carried,old='0/1',new='400/1')],carried)

def retained_lot_scenario():
    prior=vintage.return_scenario();sale=deepcopy(prior['operations'].pop())
    reassessed=previous.previous.previous.scenario('20/1',prior)
    carried=previous.request(previous.previous.scenario(reassessed))
    sale['event']['event'].update(id='new-period-lot-sale',date='2027-01-01')
    return scenario([sale],carried)

def cases():
    rows=[];q=deepcopy(default_boundary())
    def add(name,body,status='complete_provisional',stop=None):
        rows.append({'case':name,'request':deepcopy(body),'expected_status':status,'expected_stop':stop})
    add('no_operations',scenario([],q));add('split_payment_then_native',scenario(prior=q))
    add('old_only',scenario([payment(q,'3/1','0/1')],q))
    add('recent_only',scenario([payment(q,'0/1','3/1')],q))
    add('clear_both',scenario([payment(q,'15/4','5/1')],q))
    add('fractional_split',scenario([payment(q,'1/3','2/3')],q))
    add('successive_payments',scenario([payment(q),payment(q,'11/4','3/1','second-payment','2027-01-02')],q))
    add('native_then_payment',scenario([depreciation(day='2027-01-01'),payment(q)],q))
    add('year_end_payment',scenario([payment(q,day='2027-12-31')],q))
    add('year_end_native',scenario([depreciation(day='2027-12-31')],q))
    add('zero_openings',scenario([],previous.paid_vintages()))
    add('loss_recognition',scenario([],previous.request(previous.previous.loss_scenario())))
    add('retained_lot_sale',retained_lot_scenario())
    add('cash_shortage',funding_scenario(),'stopped_provisional','funding_failure')
    for flag in [True,False]:
        add('findings_'+str(flag),scenario([],previous.request(findings={k:known(flag) for k in m.boundary.FINDINGS})))
    for name,mutate,stop in [
        ('unknown_authority',lambda e:e.update(authorization={'status':'unknown','reason':'No authority'}),'unresolved'),
        ('false_authority',lambda e:e.update(authorization=known(False)),'unsupported'),
        ('unknown_vintage',lambda e:e['allocations'][0].update(vintage_id='missing'),'invalid'),
        ('duplicate_allocation',lambda e:e['allocations'].append(deepcopy(e['allocations'][0])),'invalid'),
        ('sum_mismatch',lambda e:e.update(amount='4/1'),'invalid'),
        ('zero_allocation',lambda e:e['allocations'][0].update(amount='0/1'),'invalid'),
        ('negative_allocation',lambda e:e['allocations'][0].update(amount='-1/1'),'invalid'),
        ('zero_denominator',lambda e:e['allocations'][0].update(amount='1/0'),'invalid'),
        ('empty_allocations',lambda e:e.update(allocations=[]),'invalid'),
        ('extra_event_field',lambda e:e.update(policy='FIFO'),'invalid'),
        ('before_period',lambda e:e.update(date='2026-12-31'),'invalid'),
        ('at_endpoint',lambda e:e.update(date='2028-01-01'),'invalid'),
        ('historical_event_id',lambda e:e.update(id='allocated-payment'),'invalid'),
        ('boundary_event_id',lambda e:e.update(id='second-carry-2027'),'invalid')]:
        op=payment(q);mutate(op['event']);add(name,scenario([op],q),'stopped_provisional',stop)
    for name,op in [('overpay_old',payment(q,'4/1','0/1')),('overpay_recent',payment(q,'0/1','6/1')),
        ('native_before_period',depreciation(day='2026-12-31')),('native_at_endpoint',depreciation(day='2028-01-01'))]:
        add(name,scenario([op],q),'stopped_provisional','invalid')
    aggregate=payment(q);aggregate['kind']='tax_payment';aggregate['event'].pop('allocations')
    add('aggregate_only',scenario([aggregate],q),'stopped_provisional','unsupported')
    add('completed_prefix',scenario([payment(q),payment(q,'3/1','0/1','excess'),depreciation()],q),'stopped_provisional','invalid')
    add('duplicate_after_success',scenario([payment(q),payment(q)],q),'stopped_provisional','invalid')
    add('reverse_chronology',scenario([depreciation(),payment(q)],q),'stopped_provisional','invalid')
    bad=scenario([payment(q)],q);bad['operations'][0]['event']['allocations'][0]['amount']=1.0
    add('nonportable_float',bad,'invalid')
    bad=scenario([],q);bad['boundary_sha256']='0'*64;add('stale_boundary',bad,'invalid')
    bad=deepcopy(q);bad['model']['selected']={'status':'unknown','reason':'No model selection'}
    add('unknown_boundary',scenario([],bad),'unresolved')
    return rows
