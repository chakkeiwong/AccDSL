from pathlib import Path
from copy import deepcopy
from fractions import Fraction as Q
import importlib.util,sys
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'scripts'))
import following_deferred_assessment_v1 as m
s=importlib.util.spec_from_file_location('following_deferred_prior_examples',ROOT/'data/accounting-master/following-tax-reassessment-20261024/examples.py')
previous=importlib.util.module_from_spec(s);s.loader.exec_module(previous);known=previous.known

def scenario(prior=None,ppe_base='80/1',debt_base='60/1',recognized='20/1',capacity='20/1',rate='1/4'):
    prior=previous.scenario() if prior is None else prior
    r=m.prior.propose(prior);assert r['status']=='proposed',r.get('reason')
    rows=m.population(r);items=[];bases={k:Q(0) for k in r['population']['basis_accounts']};rights={}
    for row in rows:
        base=row['carrying'] if row['kind']!='loss' else '0/1'
        if row['id']=='account/ppe':base=ppe_base
        if row['id']=='account/debt':base=debt_base
        items.append({'id':row['id'],'tax_base':known(base),'rate':known(rate),
            'recognized_deduction':known(recognized if row['id']=='account/debt' else '0/1'),
            'recorded_dta':known(r['after']['balances']['dta'] if row['id']=='account/debt' else '0/1'),
            'recorded_dtl':known(m.book.fmt(-Q(r['after']['balances']['dtl'])) if row['id']=='account/ppe' else '0/1'),
            'route':known('profit_or_loss'),'support':{k:known() for k in m.SUPPORT}})
        if row['account'] is not None:bases[row['account']]+=Q(base)
        if row['lease_id'] is not None:
            key='lease/'+m.prior.tax.info.pointer(row['lease_id'])+'/'+m.prior.tax.info.pointer(row['right_id'])+'/'+row['kind']
            rights[key]=known(base)
    measurement={'at':r['after']['date'],'state_sha256':m.book.digest(r['after']),
        'jurisdiction':known(r['loss_state']['jurisdiction']),'regime':known(r['loss_state']['regime']),
        'account_bases':{k:known(m.book.fmt(v)) for k,v in bases.items()},'lease_bases':rights}
    return m.request(prior,'following-deferred-assessment',{'profile':m.MODEL,'selected':known()},
        measurement,{k:known() for k in m.FINDINGS},known(capacity),items)

def item(q,identity):return next(i for i in q['items'] if i['id']==identity)

def loss_scenario(capacity='29/1'):
    q=scenario(previous.losses('10/1'),capacity=capacity)
    item(q,'loss/replacement-loss')['recognized_deduction']=known('9/1')
    return q

def cases():
    rows=[]
    def add(name,q,status='proposed'):rows.append({'case':name,'request':deepcopy(q),'expected_status':status})
    base=scenario();add('remeasure_carried',base)
    add('unchanged',scenario(ppe_base='60/1',recognized='32/1',capacity='32/1'))
    add('zero_rate',scenario(rate='0/1'));add('fractional_rate',scenario(rate='1/3'))
    add('no_recognition',scenario(recognized='0/1',capacity='0/1'))
    add('reverse_all',scenario(ppe_base='100/1',debt_base='100/1',recognized='0/1',capacity='0/1'))
    add('loss_and_debt',loss_scenario());add('capacity_reused',loss_scenario('20/1'),'invalid')
    add('return_loss',scenario(previous.scenario('-18/1',previous.previous.return_scenario())))
    for name,mutate,status in [
        ('stale_prior',lambda q:q.update(prior_sha256='0'*64),'invalid'),
        ('duplicate_id',lambda q:q.update(id='following-reassessment'),'invalid'),
        ('unselected_model',lambda q:q['model'].update(selected=known(False)),'unsupported'),
        ('unknown_model',lambda q:q['model'].update(selected={'status':'unknown','reason':'Missing'}),'unresolved'),
        ('wrong_model',lambda q:q['model'].update(profile='renew_old_capacity_v1'),'unsupported'),
        ('stale_measurement',lambda q:q['measurement'].update(state_sha256='0'*64),'invalid'),
        ('wrong_measurement_date',lambda q:q['measurement'].update(at='2026-06-30'),'invalid'),
        ('wrong_measurement_scope',lambda q:q['measurement'].update(jurisdiction=known('other')),'invalid'),
        ('unknown_measurement_scope',lambda q:q['measurement'].update(regime={'status':'unknown','reason':'Missing'}),'unresolved'),
        ('missing_account_base',lambda q:q['measurement']['account_bases'].pop('income_tax_payable'),'invalid'),
        ('missing_lease_base',lambda q:q['measurement']['lease_bases'].pop('lease/lease1/A/asset'),'invalid'),
        ('extra_account_base',lambda q:q['measurement']['account_bases'].update(invented=known('0/1')),'invalid'),
        ('unknown_post_base',lambda q:q['measurement']['account_bases'].update(income_tax_payable={'status':'unknown','reason':'Not measured'}),'unresolved'),
        ('stale_payable_base',lambda q:q['measurement']['account_bases'].update(income_tax_payable=known('27/4')),'invalid'),
        ('unknown_capacity',lambda q:q.update(recovery_capacity={'status':'unknown','reason':'No renewed recovery premise'}),'unresolved'),
        ('negative_capacity',lambda q:q.update(recovery_capacity=known('-1/1')),'invalid'),
        ('unknown_pool',lambda q:q['findings'].update(single_recovery_pool_supported={'status':'unknown','reason':'Missing'}),'unresolved'),
        ('false_population',lambda q:q['findings'].update(complete_scoped_population=known(False)),'unsupported'),
        ('missing_item',lambda q:q['items'].pop(),'invalid'),
        ('duplicate_item',lambda q:q['items'].append(deepcopy(q['items'][0])),'invalid'),
        ('unknown_item',lambda q:q['items'][0].update(id='invented'),'invalid')]:
        q=deepcopy(base);mutate(q);add(name,q,status)
    for name,identity,field,value,status in [
        ('base_mismatch','account/ppe','tax_base',known('81/1'),'invalid'),
        ('lease_mismatch','lease/lease1/A/asset','tax_base',known('1/1'),'invalid'),
        ('lot_mismatch','inventory/lot/recovered','tax_base',known('1/1'),'invalid'),
        ('recorded_asset_mismatch','account/debt','recorded_dta',known('7/1'),'invalid'),
        ('recorded_liability_mismatch','account/ppe','recorded_dtl',known('9/1'),'invalid'),
        ('opposite_recorded','account/debt','recorded_dtl',known('1/1'),'invalid'),
        ('excess_recognition','account/debt','recognized_deduction',known('41/1'),'invalid'),
        ('taxable_recognition','account/ppe','recognized_deduction',known('1/1'),'invalid'),
        ('negative_rate','account/ppe','rate',known('-1/4'),'invalid'),
        ('unknown_rate','account/ppe','rate',{'status':'unknown','reason':'No rate'},'unresolved'),
        ('oci_route','account/ppe','route',known('other_comprehensive_income'),'unsupported'),
        ('equity_route','account/ppe','route',known('equity'),'unsupported'),
        ('offset_route','account/ppe','route',known('offset'),'unsupported')]:
        q=deepcopy(base);item(q,identity)[field]=value;add(name,q,status)
    q=deepcopy(base);item(q,'account/ppe')['support']['recognition_supported']={'status':'unknown','reason':'Missing'};add('unknown_support',q,'unresolved')
    q=deepcopy(base);q['prior_request']=previous.scenario('4/1');q['prior_sha256']=m.book.digest(q['prior_request']);add('unsupported_current_credit',q,'unsupported')
    return rows
