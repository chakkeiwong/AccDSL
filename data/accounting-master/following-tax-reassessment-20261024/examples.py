from pathlib import Path
from copy import deepcopy
from fractions import Fraction as Q
import importlib.util,sys
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'scripts'))
import following_tax_reassessment_v1 as m
s=importlib.util.spec_from_file_location('reassessment_vintage_examples',ROOT/'data/accounting-master/tax-vintage-continuation-20261024/examples.py')
previous=importlib.util.module_from_spec(s);s.loader.exec_module(previous);known=previous.known

def scenario(taxable='28/1',prior=None,uses=None,cap='0/1',end='2027-01-01',through='2026-12-31'):
    prior=previous.scenario() if prior is None else prior
    r=m.continuation.run(prior);assert r['status']=='complete_provisional',r.get('reason',r.get('stop'))
    pop=m.population(r);info={}
    for key,kind in m.tax.fields(pop).items():
        info[key]=known(True if kind=='boolean' else '0/1' if kind=='rational' else 'Explicit hypothetical cumulative replacement information')
    info['rate']=known('1/4')
    for key in ['jurisdiction','regime']:info[key]=known(r['loss_state'][key])
    cs=m.first.classes(r['assessment_result']['carry_result'])
    for when,state in [('opening',r['opening']),('closing',r['after'])]:
        for account in pop['basis_accounts']:
            amount=Q(state['balances'][account])*(1 if account in cs['assets'] else -1)
            info['basis/'+account+'/'+when]=known(m.book.fmt(amount))
        for lease in state['leases']:
            for right in lease['component']['rights']:
                root='lease/'+m.tax.info.pointer(lease['component']['lease_id'])+'/'+m.tax.info.pointer(right['right_id'])+'/'+when
                for side,field in [('asset','rou'),('liability','liability')]:info[root+'_'+side+'_tax_base']=known(right[field])
    native=r['after']['tax_adjustments'];total=sum(Q(a['amount']) for a in native)
    allocations=[{'id':'native-'+a['event_id'],'account':'revenue','amount':a['amount'],
        'origin':{'kind':'native_return','event_id':a['event_id']}} for a in native]
    pretax=-sum(Q(r['after']['balances'][k]) for k in pop['pretax_accounts']);extra=Q(taxable)-pretax-total
    allocations.append({'id':'declared-adjustment','account':'other_gains','amount':m.book.fmt(extra),
        'origin':{'kind':'assumption','reference':'Explicit hypothetical taxable expression control'}})
    info['income/revenue/current_adjustment']=known(m.book.fmt(total))
    info['income/other_gains/current_adjustment']=known(m.book.fmt(extra))
    policy={'model':{'profile':m.losses.MODEL,'selected':known()},'utilization_cap':known(cap),
        'uses':deepcopy(uses or []),'generation':None}
    if Q(taxable)<0:policy['generation']={'id':'reassessed-loss','eligible':known(),'expiry':{'kind':'none','provenance':known()['provenance']}}
    return m.request(prior,'following-reassessment',{'profile':m.MODEL,'selected':known()},
        {'start':'2026-01-01','end_exclusive':end,'activity_through':through},info,allocations,policy)

def losses(use='19/1',taxable='20/1'):
    initial=previous.prior.loss_scenario()
    initial['interval'].update(end_exclusive='2026-07-01',activity_through='2026-06-30')
    continued=previous.scenario([previous.depreciation()],initial)
    return scenario(taxable,continued,[{'lot_id':'replacement-loss','amount':use}] if Q(use)>0 else [],'19/1')

def expiry(use='0/1'):
    initial=previous.prior.expiring_loss('1/1')
    initial['interval'].update(end_exclusive='2026-04-01',activity_through='2026-03-31')
    return scenario('20/1',previous.scenario([],initial),[{'lot_id':'replacement-loss','amount':use}] if Q(use)>0 else [],'19/1')

def cases():
    rows=[]
    def add(name,q,status='proposed'):rows.append({'case':name,'request':deepcopy(q),'expected_status':status})
    base=scenario();add('increase',base);add('decrease',scenario('12/1'));add('zero_increment',scenario('20/1'))
    add('paid_current_exact',scenario('8/1'));add('overpaid_current',scenario('4/1'),'unsupported')
    for old,new,label in [('0/1','0/1','unpaid'),('1/1','0/1','old_only'),('0/1','2/1','new_only'),('19/4','2/1','old_fully_paid')]:
        q=previous.assessment();ops=([previous.payment(q,old,new)] if Q(old)+Q(new)>0 else [])+[previous.depreciation()]
        add(label,scenario(prior=previous.scenario(ops,q)))
    q=previous.assessment();add('zero_tax',scenario('0/1',previous.scenario([],q)))
    add('new_loss',scenario('-7/1',previous.scenario([],q)))
    negative=previous.assessment(taxable='-5/1');add('replace_generated_loss',scenario('-7/1',previous.scenario([],negative)))
    add('loss_reuse_from_opening',losses());add('loss_reduced_use',losses('10/1'));add('loss_expiry',expiry())
    add('expired_loss_use',expiry('1/1'),'invalid')
    add('native_return',scenario('-18/1',previous.return_scenario()))
    add('same_endpoint_correction',scenario('28/1',previous.scenario([],q),end='2026-07-01',through='2026-06-30'))
    for name,mutate,status in [
        ('stale_predecessor',lambda q:q.update(continuation_sha256='0'*64),'invalid'),
        ('missing_rate',lambda q:q['information'].pop('rate'),'unresolved'),
        ('unknown_rate',lambda q:q['information'].update(rate={'status':'unknown','reason':'Missing'}),'unresolved'),
        ('negative_rate',lambda q:q['information'].update(rate=known('-1/4')),'invalid'),
        ('false_coverage',lambda q:q['information'].update(interval_coverage=known(False)),'unsupported'),
        ('changed_scope',lambda q:q['information'].update(jurisdiction=known('other')),'invalid'),
        ('changed_start',lambda q:q['interval'].update(start='2026-01-02'),'invalid'),
        ('shortened_endpoint',lambda q:q['interval'].update(end_exclusive='2026-06-01',activity_through='2026-05-31'),'invalid'),
        ('uncovered_event',lambda q:q['interval'].update(end_exclusive='2026-07-01',activity_through='2026-06-30'),'invalid'),
        ('wrong_last_day',lambda q:q['interval'].update(activity_through='2026-12-30'),'invalid'),
        ('beyond_year',lambda q:q['interval'].update(end_exclusive='2028-01-01',activity_through='2027-12-31'),'invalid'),
        ('duplicate_id',lambda q:q.update(id='following-assessment'),'invalid'),
        ('wrong_basis',lambda q:q['information'].update({'basis/rou/closing':known('1/1')}),'invalid'),
        ('wrong_adjustment',lambda q:q['allocations'][0].update(amount='1/1'),'invalid'),
        ('unselected_model',lambda q:q['model'].update(selected=known(False)),'unsupported'),
        ('unknown_model',lambda q:q['model'].update(selected={'status':'unknown','reason':'Missing'}),'unresolved'),
        ('wrong_model',lambda q:q['model'].update(profile='net_old_payments_v1'),'unsupported')]:
        bad=deepcopy(base);mutate(bad);add(name,bad,status)
    bad=deepcopy(base);p=bad['continuation_request'];p['operations'].append(previous.payment(p['assessment_request'],'4/1',identity='excess',day='2026-07-02'))
    bad['continuation_sha256']=m.book.digest(p);add('stopped_predecessor',bad,'unresolved')
    bad=scenario('-18/1',previous.return_scenario());bad['allocations']=[a for a in bad['allocations'] if a['origin']['kind']!='native_return'];add('missing_native_adjustment',bad,'invalid')
    add('loss_overuse',losses('20/1'),'invalid')
    bad=scenario('-7/1',previous.scenario([],negative));bad['loss_policy']['generation']['id']='following-loss';add('reused_provisional_loss',bad,'invalid')
    bad=scenario('20/1',previous.scenario([],negative),[{'lot_id':'following-loss','amount':'1/1'}],'1/1');add('use_provisional_loss',bad,'invalid')
    return rows
