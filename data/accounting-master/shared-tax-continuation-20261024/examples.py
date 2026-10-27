"""Explicit earlier assessment within a longer synthetic native period."""
from copy import deepcopy
from pathlib import Path
from fractions import Fraction as Q
import importlib.util
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts'))
import shared_tax_continuation_v1 as m


def load(name, relative):
    spec=importlib.util.spec_from_file_location(name,ROOT/relative)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


native=load('continuation_native_examples','data/accounting-master/shared-book-successor-20261024/examples.py')
info_examples=load('continuation_information_examples','data/accounting-master/shared-tax-readiness-20261024/examples.py')


def known(value=True):
    return {'status':'known','value':value,'provenance':{'kind':'assumption',
        'reference':'Explicit synthetic earlier assessment and continuation control; no actual company or tax law'}}


def accrual(taxable='2/1',cash='500/1'):
    opening=native.opening()
    if cash!='500/1':
        opening['balances']['cash']=cash
        opening['balances']['original_equity']=m.fmt(Q(520)-Q(cash))
        opening['source']['premise']='Explicit synthetic cash/equity control with unchanged total opening funding.'
    report=m.tax.losses.tax.information.reports.request(opening,[native.events()[0]])
    interval={'start':'2024-01-01','end_exclusive':'2025-01-01','activity_through':'2024-12-31'}
    info=info_examples.supplied(m.tax.losses.tax.information.request(report,interval,{}))
    info['information']['rate']=known('1/4')
    adjustment=m.fmt(Q(taxable)-20)
    info['information']['income/other_gains/current_adjustment']=known(adjustment)
    allocation=[{'id':'explicit-assessment-adjustment','account':'other_gains','amount':adjustment,
                  'origin':{'kind':'assumption','reference':'Synthetic taxable expression control independent of legal treatment'}}]
    calc=m.tax.losses.tax.request(info,{'profile':m.tax.losses.tax.MODEL,'selected':known()},allocation)
    loss_state={'profile':m.tax.losses.STATE,'context':deepcopy(opening['context']),
        'jurisdiction':info['information']['jurisdiction']['value'],'regime':info['information']['regime']['value'],
        'cursor':'2024-01-01','lots':[],'seen':[],'history':[],'opening_inventory':known()}
    generation=({'id':'explicit-generated-loss','eligible':known(),
                 'expiry':{'kind':'none','provenance':known()['provenance']}} if Q(taxable)<0 else None)
    loss=m.tax.losses.request(loss_state,calc,'first-assessment',
        {'profile':m.tax.losses.MODEL,'selected':known()},known('0/1'),[],generation)
    return m.tax.accrual_request(loss,'current-tax-assessment',known())


def origin(taxable='2/1',cash='500/1'):
    r=m.tax.propose(accrual(taxable,cash));assert r['status']=='proposed',r.get('reason')
    return r['after']


def ordinary(index, day=None):
    event=native.events()[index]
    event['event']['date']=day or '2025-01-01'
    return {'kind':'native','event':event}


def payment(amount='1/2',identity='tax-payment',day='2025-01-01'):
    return {'kind':'tax_payment','event':{'id':identity,'date':day,'amount':amount,'authorization':known()}}


def mixed():
    return [payment(),ordinary(1),ordinary(2),ordinary(3),ordinary(4)]


def cases():
    rows=[]
    def add(name,start,ops,status,stop=None):
        rows.append({'case':name,'request':m.request(start,ops),'expected_status':status,'expected_stop':stop})
    start=origin();low=origin(cash='485/4')
    add('mixed_paid',start,mixed(),'complete')
    add('mixed_unpaid',start,[ordinary(i) for i in [1,2,3,4]],'complete')
    add('empty_seed',start,[],'complete')
    add('zero_tax',origin('0/1'),[ordinary(i) for i in [1,2,3,4]],'complete')
    add('loss_generation',origin('-19/1'),[ordinary(1),ordinary(2)],'complete')
    add('lease_funding_control',low,[ordinary(3)],'complete')
    add('tax_first_funding_failure',low,[payment(),ordinary(3),ordinary(4)],'stopped','funding_failure')
    add('lease_first_funding_failure',low,[ordinary(3),payment()],'stopped','funding_failure')
    add('payment_on_accrual_day',start,[payment(day='2024-12-31')],'complete')
    add('native_on_last_assessed_day',start,[ordinary(1,'2024-12-31')],'stopped','invalid')
    add('native_on_exclusive_endpoint',start,[ordinary(1)],'complete')
    add('native_at_period_end',start,[ordinary(1,'2026-01-01')],'stopped','invalid')
    add('backdated_payment',start,[ordinary(1),payment(day='2024-12-31')],'stopped','invalid')
    add('duplicate_payment',start,[payment('1/4'),payment('1/4')],'stopped','invalid')
    add('accrual_id_collision',start,[payment(identity='current-tax-assessment')],'stopped','invalid')
    add('native_id_collision',start,[ordinary(0)],'stopped','invalid')
    add('overpayment',start,[payment('3/4')],'stopped','invalid')
    add('zero_payment',start,[payment('0/1')],'stopped','invalid')
    op=ordinary(1);op['event']['event']['inventory_nrv']='unknown'
    add('unknown_native_nrv',start,[op],'stopped','unresolved')
    op=payment();op['event']['authorization']={'status':'unknown','reason':'Missing instruction'}
    add('unknown_payment_authority',start,[op],'stopped','unresolved')
    op=payment();op['event']['authorization']=known(False)
    add('false_payment_authority',start,[op],'stopped','unsupported')
    add('unknown_module',start,[{'kind':'invented','event':{}}],'stopped','unsupported')
    q=m.tax.settlement_request(start,'prior-payment','2024-12-31','1/4',known())
    paid=m.tax.propose(q)['after'];add('preserve_origin_payment',paid,[payment('1/4')],'complete')
    q=m.request(start,[]);q['origin_sha256']='0'*64
    rows.append({'case':'stale_origin','request':q,'expected_status':'invalid','expected_stop':None})
    altered=deepcopy(start);altered['balances']['cash']='501/1';add('forged_origin',altered,[],'invalid')
    return rows
