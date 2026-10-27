from pathlib import Path
from fractions import Fraction as Q
from copy import deepcopy
import importlib.util,sys
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'scripts'))
import following_period_tax_v1 as m
s=importlib.util.spec_from_file_location('following_tax_carry_examples',ROOT/'data/accounting-master/assessed-period-carry-20261024/examples.py')
previous=importlib.util.module_from_spec(s);s.loader.exec_module(previous);known=previous.known

def scenario(taxable='20/1',payment='19/4',carry_request=None,uses=None,cap='0/1'):
    if carry_request is None:
        ops=([previous.payment(payment)] if Q(payment)>0 else [])+[previous.depreciation()]
        carry_request=previous.request(operations=ops)
    result=m.carry.run(carry_request);assert result['status']=='complete_provisional',result.get('reason',result.get('stop'))
    pop=m.population(result);info={}
    for key,kind in m.tax.fields(pop).items():
        info[key]=known(True if kind=='boolean' else '0/1' if kind=='rational' else 'Explicit hypothetical following-period information')
    info['rate']=known('1/4')
    for key in ['jurisdiction','regime']:info[key]=known(result['loss_state'][key])
    cs=m.classes(result)
    for when,state in [('opening',result['opening']),('closing',result['after'])]:
        for account in pop['basis_accounts']:
            amount=Q(state['balances'][account])*(1 if account in cs['assets'] else -1)
            info['basis/'+account+'/'+when]=known(m.book.fmt(amount))
        for lease in state['leases']:
            for right in lease['component']['rights']:
                root='lease/'+m.tax.info.pointer(lease['component']['lease_id'])+'/'+m.tax.info.pointer(right['right_id'])+'/'+when
                for side,field in [('asset','rou'),('liability','liability')]:info[root+'_'+side+'_tax_base']=known(right[field])
    native=result['after']['tax_adjustments'];total=sum(Q(a['amount']) for a in native)
    allocations=[{'id':'native-'+a['event_id'],'account':'revenue','amount':a['amount'],
        'origin':{'kind':'native_return','event_id':a['event_id']}} for a in native]
    pretax=-sum(Q(result['after']['balances'][k]) for k in pop['pretax_accounts'])
    extra=Q(taxable)-pretax-total
    allocations.append({'id':'declared-adjustment','account':'other_gains','amount':m.book.fmt(extra),
        'origin':{'kind':'assumption','reference':'Explicit hypothetical taxable expression control'}})
    info['income/revenue/current_adjustment']=known(m.book.fmt(total))
    info['income/other_gains/current_adjustment']=known(m.book.fmt(extra))
    policy={'model':{'profile':m.losses.MODEL,'selected':known()},'utilization_cap':known(cap),
        'uses':deepcopy(uses or []),'generation':None}
    if Q(taxable)<0:policy['generation']={'id':'following-loss','eligible':known(),'expiry':{'kind':'none','provenance':known()['provenance']}}
    return m.request(carry_request,'following-assessment',{'profile':m.MODEL,'selected':known()},
        {'start':'2026-01-01','end_exclusive':'2027-01-01','activity_through':'2026-12-31'},info,allocations,policy)

def loss_scenario(use='19/1',taxable='20/1'):
    original=previous.deferred.scenario(taxable='-19/1',paid=False)
    carried=previous.request(original,operations=[previous.depreciation()])
    return scenario(taxable,'0/1',carried,[{'lot_id':'replacement-loss','amount':use}] if Q(use)>0 else [],'19/1')

def expiring_loss(use='0/1'):
    original=previous.deferred.scenario(taxable='-19/1',paid=False)
    original['prior_request']['loss_policy']['generation']['expiry']={
        'kind':'date','end_exclusive':'2026-06-01','provenance':known()['provenance']}
    original['prior_sha256']=m.book.digest(original['prior_request'])
    carried=previous.request(original,operations=[previous.depreciation()])
    return scenario('20/1','0/1',carried,[{'lot_id':'replacement-loss','amount':use}] if Q(use)>0 else [],'19/1')

def return_scenario():
    older=previous.old.unsettled_return();reassessment=older['prior_request']
    d=previous.deferred.m;result=d.prior.propose(reassessment);assert result['status']=='proposed'
    items=[];totals={k:Q(0) for k in d.prior.population(result['continuation_result'])['basis_accounts']}
    for row in d.population(result):
        base=row['carrying'] if row['kind']!='loss' else '0/1'
        items.append({'id':row['id'],'tax_base':known(base),'rate':known('1/4'),
            'recognized_deduction':known('0/1'),'recorded_dta':known('10/1' if row['id']=='account/debt' else '0/1'),
            'recorded_dtl':known('4/1' if row['id']=='account/ppe' else '0/1'),
            'route':known('profit_or_loss'),'support':{k:known() for k in d.SUPPORT}})
        if row['account'] is not None:totals[row['account']]+=Q(base)
        if row['lease_id'] is not None:
            key='lease/'+d.prior.info.pointer(row['lease_id'])+'/'+d.prior.info.pointer(row['right_id'])+'/closing_'+row['kind']+'_tax_base'
            reassessment['information'][key]=known(base)
    for account,base in totals.items():reassessment['information']['basis/'+account+'/closing']=known(d.book.fmt(base))
    deferred=d.request(reassessment,'deferred-return-opening',{'profile':d.MODEL,'selected':known()},
        {k:known() for k in d.FINDINGS},known('0/1'),items)
    carried=previous.request(deferred,operations=older['operations'])
    return scenario('-18/1','0/1',carried)

def cases():
    rows=[]
    def add(name,q,status='proposed'):rows.append({'case':name,'request':deepcopy(q),'expected_status':status})
    base=scenario();add('prior_paid',base);add('prior_unpaid',scenario(payment='0/1'))
    add('prior_partial',scenario(payment='1/1'));add('zero_tax',scenario('0/1',payment='0/1'))
    add('new_loss',scenario('-7/1',payment='0/1'));add('loss_use',loss_scenario())
    add('loss_expiry',expiring_loss());add('expired_loss_use',expiring_loss('1/1'),'invalid')
    q=expiring_loss('1/1');q['interval'].update(end_exclusive='2026-04-01',activity_through='2026-03-31')
    add('loss_use_before_expiry',q);add('native_return',return_scenario())
    for rate,label in [('0/1','zero_rate'),('1/3','fractional_rate')]:
        q=deepcopy(base);q['information']['rate']=known(rate);add(label,q)
    for name,mutate,status in [
        ('missing_rate',lambda q:q['information'].pop('rate'),'unresolved'),
        ('unknown_rate',lambda q:q['information'].update(rate={'status':'unknown','reason':'Missing'}),'unresolved'),
        ('negative_rate',lambda q:q['information'].update(rate=known('-1/4')),'invalid'),
        ('false_coverage',lambda q:q['information'].update(interval_coverage=known(False)),'unsupported'),
        ('changed_scope',lambda q:q['information'].update(jurisdiction=known('other')),'invalid'),
        ('start_mismatch',lambda q:q['interval'].update(start='2026-01-02'),'invalid'),
        ('endpoint_after_period',lambda q:q['interval'].update(end_exclusive='2028-01-01'),'invalid'),
        ('wrong_last_day',lambda q:q['interval'].update(activity_through='2026-12-30'),'invalid'),
        ('duplicate_id',lambda q:q.update(id='assessed-carry-2026'),'invalid'),
        ('stale_carry',lambda q:q.update(carry_sha256='0'*64),'invalid'),
        ('allocation_amount',lambda q:q['allocations'][0].update(amount='29/1'),'invalid'),
        ('duplicate_allocation',lambda q:q['allocations'].append(deepcopy(q['allocations'][0])),'invalid'),
        ('basis_mismatch',lambda q:q['information'].update({'basis/rou/closing':known('1/1')}),'invalid'),
        ('unselected_model',lambda q:q['model'].update(selected=known(False)),'unsupported'),
        ('unsupported_model',lambda q:q['model'].update(profile='net_carried_payments_v1'),'unsupported')]:
        q=deepcopy(base);mutate(q);add(name,q,status)
    q=deepcopy(base);q['carry_request']['operations'].append(previous.payment('1/1',identity='overpay'))
    q['carry_sha256']=m.book.digest(q['carry_request']);add('stopped_predecessor',q,'unresolved')
    q=return_scenario();q['allocations']=[a for a in q['allocations'] if a['origin']['kind']!='native_return']
    add('missing_native_adjustment',q,'invalid')
    add('loss_overuse',loss_scenario('20/1'),'invalid')
    q=loss_scenario('0/1','-7/1');q['loss_policy']['generation']['id']='replacement-loss';add('reused_loss_identity',q,'invalid')
    return rows
