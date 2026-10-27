from pathlib import Path
from copy import deepcopy
import importlib.util
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
spec=importlib.util.spec_from_file_location('tax_state_fixture',ROOT/'tests/test_shared_tax_state_v1.py')
fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture)
m=fixture.m

def cases():
    rows=[]
    def add(name,body,status):rows.append({'case':name,'request':deepcopy(body),'expected_status':status})
    for name in ['generate_19','consume_19_from_21','zero_taxable_profit','zero_explicit_use','partial_use_7']:
        add('accrual_'+name,fixture.accrual(name),'proposed')
    base=m.propose(fixture.accrual())['after']
    add('payment_partial',fixture.payment(base),'proposed')
    add('payment_full',fixture.payment(base,'1/2'),'proposed')
    add('payment_fraction',fixture.payment(base,'1/3'),'proposed')
    partial=m.propose(fixture.payment(base))['after']
    add('payment_second',fixture.payment(partial,'1/4','second'),'proposed')
    add('payment_duplicate',fixture.payment(partial),'invalid')
    add('payment_accrual_collision',fixture.payment(base,identity='tax-accrual'),'invalid')
    for amount in ['0/1','-1/4','3/4']:
        add('payment_quantity_'+amount,fixture.payment(base,amount),'invalid')
    for day in ['2026-12-30','2027-01-01']:
        add('payment_date_'+day,fixture.payment(base,day=day),'invalid')
    for kind in ['recognition','payment']:
        for val,status in [(fixture.known(False),'unsupported'),({'status':'unknown','reason':'Missing premise'},'unresolved')]:
            q=fixture.accrual() if kind=='recognition' else fixture.payment(base)
            if kind=='recognition':q['recognition']=val
            else:q['event']['authorization']=val
            add(kind+'_'+status,q,status)
    for name,status in [('generation_eligibility_unknown','unresolved'),('generation_ineligible','unsupported'),('forged_state_identity','invalid')]:
        add('upstream_'+name,fixture.accrual(name),status)
    empty=m.propose(fixture.lower_cash(fixture.accrual()))['after']
    add('payment_no_cash',fixture.payment(empty),'funding_failure')
    for key,value in [('date','2026-12-30'),('assessed_until','2027-02-01'),('native_tax_closed_until','2027-01-01')]:
        q=fixture.payment(base);q['state'][key]=value;q['state_sha256']=m.book.digest(q['state'])
        add('forged_'+key,q,'invalid')
    q=fixture.payment(base);q['state_sha256']='0'*64;add('stale_state',q,'invalid')
    q=fixture.accrual();q['loss_request_sha256']='0'*64;add('stale_loss_request',q,'invalid')
    return rows
