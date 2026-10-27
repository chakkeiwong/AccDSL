from pathlib import Path
from copy import deepcopy
from fractions import Fraction as Q
import importlib.util,sys
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'scripts'))
import tax_vintage_continuation_v1 as m
s=importlib.util.spec_from_file_location('vintage_prior_examples',ROOT/'data/accounting-master/following-period-tax-20261024/examples.py')
prior=importlib.util.module_from_spec(s);s.loader.exec_module(prior)
known=prior.known

def assessment(payment='0/1',taxable='20/1',full_year=False):
    q=prior.scenario(taxable,payment=payment)
    if not full_year:q['interval'].update(end_exclusive='2026-07-01',activity_through='2026-06-30')
    return q

def ids(q):
    original=q['carry_request']['prior_request']['prior_request']
    return ['carried:'+m.book.digest(original),'current:'+q['id']]

def payment(q,old='0/1',new='0/1',identity='allocated-payment',day='2026-06-30'):
    values=[old,new];allocations=[{'vintage_id':key,'amount':value} for key,value in zip(ids(q),values) if Q(value)!=0]
    return {'kind':'allocated_tax_payment','event':{'id':identity,'date':day,
        'amount':m.book.fmt(sum(Q(v) for v in values)),'authorization':known(),'allocations':allocations}}

def depreciation(amount='2/1',day='2026-07-01',identity='post-assessment-depreciation'):
    return prior.previous.depreciation(amount=amount,day=day,identity=identity)

def scenario(operations=None,q=None):
    q=assessment() if q is None else q
    return m.request(q,[payment(q,'1/1','2/1'),depreciation()] if operations is None else operations)

def return_scenario():
    source=prior.return_scenario();carried=deepcopy(source['carry_request'])
    operations=carried.pop('operations');carried['operations']=[]
    q=prior.scenario('20/1',payment='0/1',carry_request=carried)
    q['interval'].update(end_exclusive='2026-07-01',activity_through='2026-06-30')
    for i,op in enumerate(operations):op['event']['event']['date']='2026-07-0'+str(i+1)
    return m.request(q,operations)

def cases():
    rows=[];q=assessment()
    def add(name,body,status='complete_provisional',stop=None):
        rows.append({'case':name,'request':deepcopy(body),'expected_status':status,'expected_stop':stop})
    add('no_operations',scenario([],q));add('split_payment_then_native',scenario(q=q))
    add('old_only',scenario([payment(q,'3/1')],q));add('current_only',scenario([payment(q,new='3/1')],q))
    add('clear_both',scenario([payment(q,'19/4','5/1')],q))
    add('fractional_split',scenario([payment(q,'1/3','2/3')],q))
    add('successive_payments',scenario([payment(q,'1/1','2/1'),payment(q,'15/4','3/1','second-payment','2026-07-01')],q))
    partial=assessment(payment='1/1');add('prior_partial_settlement',scenario([payment(partial,'15/4','1/1')],partial))
    paid=assessment(payment='19/4');add('zero_old_retained',scenario([payment(paid,new='2/1')],paid))
    add('ordinary_then_payment',scenario([depreciation(),payment(q,'1/1','2/1',day='2026-07-01')],q))
    add('native_return',return_scenario())
    full=assessment(full_year=True);add('year_end_payment',scenario([payment(full,new='1/1',day='2026-12-31')],full))
    for name,op,stop in [
        ('aggregate_only',prior.previous.payment(),'unsupported'),
        ('unknown_authority',payment(q,'1/1'),'unresolved'),
        ('false_authority',payment(q,'1/1'),'unsupported'),
        ('overpay_old',payment(q,'5/1'),'invalid'),
        ('overpay_current',payment(q,new='6/1'),'invalid'),
        ('no_allocations',payment(q),'invalid'),
        ('negative_allocation',payment(q,'-1/1','2/1'),'invalid'),
        ('before_assessment',payment(q,'1/1',day='2026-06-29'),'invalid'),
        ('financial_endpoint',payment(q,'1/1',day='2027-01-01'),'invalid'),
        ('duplicate_assessment',payment(q,'1/1',identity=q['id']),'invalid'),
        ('native_before_endpoint',depreciation(day='2026-06-30'),'invalid')]:
        if name=='unknown_authority':op['event']['authorization']={'status':'unknown','reason':'Missing authorization'}
        if name=='false_authority':op['event']['authorization']=known(False)
        add(name,scenario([op],q),'stopped_provisional',stop)
    for name,mutate in [
        ('unknown_vintage',lambda e:e['allocations'][0].update(vintage_id='missing')),
        ('duplicate_allocation',lambda e:e['allocations'].append(deepcopy(e['allocations'][0]))),
        ('sum_mismatch',lambda e:e.update(amount='4/1')),
        ('zero_allocation',lambda e:e['allocations'][0].update(amount='0/1')),
        ('extra_event_field',lambda e:e.update(policy='FIFO'))]:
        op=payment(q,'1/1','2/1');mutate(op['event']);add(name,scenario([op],q),'stopped_provisional','invalid')
    add('completed_prefix',scenario([payment(q,'1/1'),payment(q,'4/1',identity='excess'),depreciation()],q),'stopped_provisional','invalid')
    add('duplicate_after_success',scenario([payment(q,'1/1'),payment(q,new='1/1')],q),'stopped_provisional','invalid')
    high=assessment(taxable='2000/1');add('cash_shortage',scenario([payment(high,new='400/1')],high),'stopped_provisional','funding_failure')
    add('year_end_native_refused',scenario([depreciation(day='2027-01-01')],full),'stopped_provisional','invalid')
    bad=scenario([],q);bad['assessment_sha256']='0'*64;add('stale_assessment',bad,'invalid')
    bad=deepcopy(q);bad['information']['rate']={'status':'unknown','reason':'No rate'}
    add('unknown_predecessor',scenario([],bad),'unresolved')
    return rows
