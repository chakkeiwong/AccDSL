from pathlib import Path
from copy import deepcopy
from fractions import Fraction as Q
from functools import lru_cache
import importlib.util,sys
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'scripts'))
import annual_period_book_v1 as m
s=importlib.util.spec_from_file_location('annual_root_examples',ROOT/'data/accounting-master/period-vintage-continuation-20261024/examples.py')
previous=importlib.util.module_from_spec(s);s.loader.exec_module(previous);known=previous.known

@lru_cache(maxsize=1)
def root_request():return previous.scenario()

def assessment(state,taxable='16/1',identity='annual-first',mode='first',end='2027-07-01',uses=None,cap='0/1',generation=None):
    pop=m.population(state);info={};classes=state['account_classes']
    for key,kind in m.tax.fields(pop).items():
        info[key]=known(True if kind=='boolean' else '0/1' if kind=='rational' else 'Explicit hypothetical reusable-period control')
    info['rate']=known('1/4')
    for key in ['jurisdiction','regime']:info[key]=known(state['opening_loss'][key])
    for when,financial in [('opening',state['opening']),('closing',state['after'])]:
        for account in pop['basis_accounts']:
            value=Q(financial['balances'][account])*(1 if account in classes['assets'] else -1)
            info['basis/'+account+'/'+when]=known(m.book.fmt(value))
        for lease in financial['leases']:
            for r in lease['component']['rights']:
                prefix='lease/'+m.tax.info.pointer(lease['component']['lease_id'])+'/'+m.tax.info.pointer(r['right_id'])+'/'+when
                for side,field in [('asset','rou'),('liability','liability')]:info[prefix+'_'+side+'_tax_base']=known(r[field])
    native=state['after']['tax_adjustments'];total=sum(Q(a['amount']) for a in native)
    allocations=[{'id':'native-'+a['event_id'],'account':'revenue','amount':a['amount'],
        'origin':{'kind':'native_return','event_id':a['event_id']}} for a in native]
    pretax=-sum(Q(state['after']['balances'][k]) for k in pop['pretax_accounts']);extra=Q(taxable)-pretax-total
    allocations.append({'id':'declared-adjustment','account':'other_gains','amount':m.book.fmt(extra),
        'origin':{'kind':'assumption','reference':'Explicit hypothetical taxable control, not law'}})
    info['income/revenue/current_adjustment']=known(m.book.fmt(total));info['income/other_gains/current_adjustment']=known(m.book.fmt(extra))
    if Q(taxable)<0 and generation is None:generation={'id':identity+'-loss','eligible':known(),'expiry':{'kind':'none','provenance':known()['provenance']}}
    return {'kind':'current_assessment','event':{'id':identity,'mode':mode,
        'model':{'profile':m.CURRENT_MODEL,'selected':known()},
        'interval':{'start':state['after']['period']['start'],'end_exclusive':end,
                    'activity_through':str(m.core.scalar(end,'date')-m.timedelta(days=1))},
        'information':info,'allocations':allocations,'loss_policy':{
            'model':{'profile':m.losses.MODEL,'selected':known()},'utilization_cap':known(cap),
            'uses':deepcopy(uses or []),'generation':deepcopy(generation)}}}

def payment(state,amounts,identity='annual-payment',day='2027-06-30'):
    return {'kind':'allocated_tax_payment','event':{'id':identity,'date':day,
        'amount':m.book.fmt(sum(Q(x) for x in amounts)),'authorization':known(),
        'allocations':[{'vintage_id':v['id'],'amount':amount} for v,amount in zip(state['period_vintages'],amounts) if Q(amount)!=0]}}

def start(origin=None):
    origin=root_request() if origin is None else origin;r=m.run(m.request(origin,[]))
    assert r['status']=='complete_provisional',r.get('reason');return origin,r['period_book']

def scenario():
    origin,state=start();first=assessment(state);state=m.transition(state,first)['after']
    paid=payment(state,['1/1','1/1','2/1']);state=m.transition(state,paid)['after']
    replace=assessment(state,'12/1','annual-replace','replace')
    return m.request(origin,[first,paid,replace])

def deferred(state,identity='annual-deferred',capacity='20/1',recognized='20/1'):
    rows=m.deferred_population(state);items=[];bases={k:Q(0) for k in m.population(state)['basis_accounts']};rights={}
    for row in rows:
        base=row['carrying'] if row['kind']!='loss' else '0/1'
        if row['id']=='account/ppe':base='80/1'
        if row['id']=='account/debt':base='60/1'
        items.append({'id':row['id'],'tax_base':known(base),'rate':known('1/4'),
            'recognized_deduction':known(recognized if row['id']=='account/debt' else '0/1'),
            'recorded_dta':known(state['after']['balances']['dta'] if row['id']=='account/debt' else '0/1'),
            'recorded_dtl':known(m.book.fmt(-Q(state['after']['balances']['dtl'])) if row['id']=='account/ppe' else '0/1'),
            'route':known('profit_or_loss'),'support':{k:known() for k in m.deferred.SUPPORT}})
        if row['account'] is not None:bases[row['account']]+=Q(base)
        if row['lease_id'] is not None:
            key='lease/'+m.tax.info.pointer(row['lease_id'])+'/'+m.tax.info.pointer(row['right_id'])+'/'+row['kind'];rights[key]=known(base)
    return {'kind':'deferred_assessment','event':{'id':identity,
        'model':{'profile':m.deferred.MODEL,'selected':known()},
        'measurement':{'at':state['after']['date'],'state_sha256':m.book.digest(state['after']),
            'jurisdiction':known(state['loss_state']['jurisdiction']),'regime':known(state['loss_state']['regime']),
            'account_bases':{k:known(m.book.fmt(v)) for k,v in bases.items()},'lease_bases':rights},
        'findings':{k:known() for k in m.deferred.FINDINGS},'recovery_capacity':known(capacity),'items':items}}

def carry(state,identity='annual-carry',end='2029-01-01'):
    return {'kind':'provisional_carry','event':{'id':identity,
        'model':{'profile':m.root.boundary.MODEL,'selected':known()},
        'next_period':{'start':state['after']['period']['end_exclusive'],'end_exclusive':end},
        'findings':{k:{'status':'unknown','reason':'No new admission evidence'} for k in m.root.boundary.FINDINGS}}}

def repeated_scenario():
    q=scenario();r=m.run(q);assert r['status']=='complete_provisional',r.get('stop');state=r['period_book']
    def add(op):
        nonlocal state
        state=m.transition(state,op)['after'];q['operations'].append(op)
    add(assessment(state,'12/1','annual-year-end','replace','2028-01-01'))
    add(deferred(state));add(carry(state))
    add(assessment(state,'8/1','next-year-first','first','2029-01-01'))
    return q
