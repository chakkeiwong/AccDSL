from pathlib import Path
from copy import deepcopy
from fractions import Fraction as Q
import importlib.util,sys
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'scripts'))
import shared_deferred_assessment_v1 as m
s=importlib.util.spec_from_file_location('deferred_reassessment_examples',ROOT/'data/accounting-master/shared-tax-reassessment-20261024/examples.py')
previous=importlib.util.module_from_spec(s);s.loader.exec_module(previous)
def known(value=True):
    return {'status':'known','value':value,'provenance':{'kind':'assumption',
        'reference':'Explicit hypothetical deferred-tax control; no actual company, recovery forecast or legal admission'}}

def scenario(ppe_base='60/1',debt_base='60/1',recognized='32/1',rate='1/4',capacity='32/1',taxable='21/1',paid=True):
    prior=previous.scenario(taxable,paid);r=m.prior.propose(prior);assert r['status']=='proposed'
    rows=m.population(r);items=[];bases={k:Q(0) for k in m.prior.population(r['continuation_result'])['basis_accounts']}
    for row in rows:
        base=row['carrying'] if row['kind']!='loss' else '0/1'
        if row['id']=='account/ppe':base=ppe_base
        if row['id']=='account/debt':base=debt_base
        items.append({'id':row['id'],'tax_base':known(base),'rate':known(rate),
            'recognized_deduction':known(recognized if row['id']=='account/debt' else '0/1'),
            'recorded_dta':known('10/1' if row['id']=='account/debt' else '0/1'),
            'recorded_dtl':known('4/1' if row['id']=='account/ppe' else '0/1'),
            'route':known('profit_or_loss'),'support':{k:known() for k in m.SUPPORT}})
        if row['account'] is not None:bases[row['account']]+=Q(base)
        if row['lease_id'] is not None:
            key='lease/'+m.prior.info.pointer(row['lease_id'])+'/'+m.prior.info.pointer(row['right_id'])+'/closing_'+row['kind']+'_tax_base'
            prior['information'][key]=known(base)
    for account,base in bases.items():prior['information']['basis/'+account+'/closing']=known(m.book.fmt(base))
    return m.request(prior,'deferred-assessment',{'profile':m.MODEL,'selected':known()},
        {k:known() for k in m.FINDINGS},known(capacity),items)

def item(q,identity):return next(x for x in q['items'] if x['id']==identity)

def change_base(q,identity,base):
    row=item(q,identity);delta=Q(base)-Q(row['tax_base']['value']);row['tax_base']=known(base)
    previous=m.prior.propose(q['prior_request']);p=next(x for x in m.population(previous) if x['id']==identity)
    if p['account'] is not None:
        key='basis/'+p['account']+'/closing';old=q['prior_request']['information'][key]['value']
        q['prior_request']['information'][key]=known(m.book.fmt(Q(old)+delta))
    if p['lease_id'] is not None:
        key='lease/'+m.prior.info.pointer(p['lease_id'])+'/'+m.prior.info.pointer(p['right_id'])+'/closing_'+p['kind']+'_tax_base'
        q['prior_request']['information'][key]=known(base)
    q['prior_sha256']=m.book.digest(q['prior_request'])

def cases():
    rows=[]
    def add(name,q,status='proposed'):rows.append({'case':name,'request':deepcopy(q),'expected_status':status})
    base=scenario();add('mixed_partial_recognition',base)
    add('zero_rate',scenario(rate='0/1'));add('fractional_rate',scenario(rate='1/3'))
    add('explicit_above_one_rate',scenario(rate='5/4'))
    add('unchanged_balances',scenario(ppe_base='84/1',recognized='40/1',capacity='40/1'))
    add('matching_bases',scenario(ppe_base='100/1',debt_base='100/1',recognized='0/1',capacity='0/1'))
    add('unrecognized_deductions',scenario(recognized='0/1',capacity='0/1'))
    q=scenario(ppe_base='140/1',debt_base='120/1',recognized='0/1',capacity='20/1')
    item(q,'account/ppe')['recognized_deduction']=known('20/1');add('opposite_signs',q)
    q=scenario(taxable='-19/1',paid=False);loss=next(i for i in q['items'] if i['id'].startswith('loss/'))
    loss['recognized_deduction']=known('10/1');add('capacity_reused_across_losses',q,'invalid')
    q['recovery_capacity']=known('42/1');add('loss_recognition',q)
    for name,mutate,status in [
        ('unknown_pool',lambda q:q['findings'].update(single_recovery_pool_supported={'status':'unknown','reason':'Unresolved'}),'unresolved'),
        ('false_pool',lambda q:q['findings'].update(single_recovery_pool_supported=known(False)),'unsupported'),
        ('unknown_capacity',lambda q:q.update(recovery_capacity={'status':'unknown','reason':'No capacity'}),'unresolved'),
        ('missing_item',lambda q:q['items'].pop(),'invalid'),
        ('duplicate_item',lambda q:q['items'].append(deepcopy(q['items'][0])),'invalid'),
        ('extra_item',lambda q:q['items'][0].update(id='invented'),'invalid'),
        ('duplicate_assessment',lambda q:q.update(id='replacement-assessment'),'invalid'),
        ('stale_prior',lambda q:q.update(prior_sha256='0'*64),'invalid'),
        ('unselected_model',lambda q:q['model'].update(selected=known(False)),'unsupported')]:
        q=deepcopy(base);mutate(q);add(name,q,status)
    for name,identity,field,value,status in [
        ('base_mismatch','account/ppe','tax_base',known('61/1'),'invalid'),
        ('lease_base_mismatch','lease/lease1/A/asset','tax_base',known('0/1'),'invalid'),
        ('lot_base_mismatch','inventory/lot/recovered','tax_base',known('1/1'),'invalid'),
        ('missing_opening_allocation','account/debt','recorded_dta',known('9/1'),'invalid'),
        ('opposite_opening_allocation','account/ppe','recorded_dta',known('1/1'),'invalid'),
        ('excess_recognition','account/debt','recognized_deduction',known('41/1'),'invalid'),
        ('taxable_cannot_be_deductible','account/ppe','recognized_deduction',known('1/1'),'invalid'),
        ('negative_rate','account/ppe','rate',known('-1/4'),'invalid'),
        ('unknown_rate','account/ppe','rate',{'status':'unknown','reason':'Missing'},'unresolved'),
        ('equity_route','account/ppe','route',known('equity'),'unsupported'),
        ('oci_route','account/ppe','route',known('other_comprehensive_income'),'unsupported'),
        ('offset_route','account/ppe','route',known('offset'),'unsupported')]:
        q=deepcopy(base);item(q,identity)[field]=value;add(name,q,status)
    return rows
