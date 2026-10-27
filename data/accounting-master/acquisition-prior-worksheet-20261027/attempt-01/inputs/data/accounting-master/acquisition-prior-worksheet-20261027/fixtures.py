from pathlib import Path
from hashlib import sha256
from copy import deepcopy
from fractions import Fraction as F
import json
H=Path(__file__).resolve().parent
BASE=json.loads((H.parent/'acquisition-consideration-20261027/attempt-01/cases.json').read_text())[0]
SCOPE=next(x for x in json.loads((H.parent/'acquisition-prior-interest-scope-20261027/attempt-01/cases.json').read_text()) if x['id']=='preserved/proportional/equity/fvtpl/none')
def digest(x):return sha256(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
def frac(x):q=F(x);return str(q.numerator)+'/'+str(q.denominator)
def ser(x):return {k:frac(v) for k,v in x.items()}
def bind(b):b['payload']['books_sha256']=digest(b['payload']['books']);b['expected_payload_sha256']=digest(b['payload']);return b
def fixture(carrying=35):
    c=F(carrying);src=dict(text='Synthetic measured prior-equity schedule; not actual fair values or tax law',subject=['P','S'],actor='manager',available_at='2025-01-01T00:00:00Z');books=deepcopy(BASE['result']['original_books'])
    books['P']['snapshots']['opening']['balances']=ser(dict(cash=300-c,investment=c,capital=-300,prior_remeasurement_gain=0))
    for stage in ['acquisition','closing']:books['P']['snapshots'][stage]['balances']=ser(dict(cash=220-c,investment=120,capital=-300,prior_remeasurement_gain=c-40))
    schedule=dict(prior_carrying=frac(c),prior_fair_value='40/1',new_cash='80/1',prior_fraction='1/5',new_fraction='11/20',combined_measurement=dict(status='supplied',acquisition='120/1',closing='120/1',premise='Independent synthetic combined investment fair values at both dates; not inferred from transaction amounts'),separate_books='supplied_aasb9_fvtpl',tax='explicit_zero_current_and_deferred_on_prior_gain',at='2025-07-01T00:00:00Z',closing_at='2026-01-01T00:00:00Z',currency='USD',unit='currency_unit',premise='Prior equity/FVTPL and explicit legal,control,valuation and tax schedules',evidence_sha256=digest(src))
    return bind(dict(profile='ConditionalPriorEquityWorksheet/1',payload=dict(scope_request=deepcopy(SCOPE['request']),scope_result_sha256=digest(SCOPE['result']),base_request=deepcopy(BASE['request']),base_result_sha256=digest(BASE['result']),source_lock_sha256=sha256((H/'predecessor-lock.json').read_bytes()).hexdigest(),schedule=schedule,source=src,books=books,books_sha256=''),expected_payload_sha256=''))
def expected(carrying):
    c=F(carrying);b=fixture(c);books=b['payload']['books'];old=BASE['result'];out=dict(original_books=books);journals=[]
    def event(id,entity,at,entries,origin):journals.append(dict(id=id,entity=entity,at=at,origin=origin,entries=ser(entries)))
    for e in ['P','S']:event('opening-'+e,e,'2025-01-01T00:00:00Z',books[e]['snapshots']['opening']['balances'],'Supplied opening state; prior investment already exists')
    event('precontrol-receipt','S','2025-06-29T00:00:00Z',{'cash':20,'revenue':-20},'Supplied pre-control receipt')
    event('precontrol-close','S','2025-06-30T00:00:00Z',{'revenue':20,'retained_pre':-20},'Supplied pre-control close')
    event('prior-equity-update','P','2025-07-01T00:00:00Z',{'investment':40-c,'prior_remeasurement_gain':c-40},'Supplied prior FVTPL fair-value update; no cash')
    event('new-share-purchase','P','2025-07-01T00:00:00Z',{'investment':80,'cash':-80},'New cash paid to external former owners; separate from prior fair value')
    event('controlled-receipt','S','2025-08-01T00:00:00Z',{'cash':40,'revenue':-40},'Supplied controlled receipt')
    event('legal-depreciation','S','2025-12-31T00:00:00Z',{'depreciation':7,'equipment':-7},'Supplied legal equipment schedule');out['legal_journals']=journals
    for stage in ['acquisition','closing']:
        w=deepcopy(old[stage+'_worksheet']);w['raw']={e+'.'+k:v for e in ['P','S'] for k,v in books[e]['snapshots'][stage]['balances'].items()}
        w['adjusted'].update({'P.cash':frac(220-c),'P.prior_remeasurement_gain':frac(c-40)})
        w['balances'].update(cash=frac((270 if stage=='acquisition' else 310)-c),prior_remeasurement_gain=frac(c-40));w['balances']={k:v for k,v in w['balances'].items() if F(v)};out[stage+'_worksheet']=w
    report=deepcopy(old['report']);report.update(ser(dict(profit=F(143,2)-c,owners_profit=F(509,8)-c,nci_profit=F(63,8),owners_equity_closing=F(2909,8)-c,nci_closing=F(293,8),assets_closing=F(1699,4)-c,liabilities_closing=F(49,2),equity_closing=F(1601,4)-c)))
    report.update(acquisition_balances=out['acquisition_worksheet']['balances'],closing_balances=out['closing_worksheet']['balances'])
    report['cash']=ser(dict(acquired=50,acquisition_net=-30,closing=310-c,consideration_paid=80,noncash_equity=0,opening=300-c,operating=40))
    report['parent_equity']=ser(dict(closing=F(2909,8)-c,new_equity=0,opening=300,owners_profit=F(509,8)-c))
    report['prior_equity']=ser(dict(opening_carrying=c,acquisition_fair_value=40,noncash_gain=40-c,new_cash=80,combined_investment=120));out['report']=report
    out['cash_origins']=[dict(entity='P',counterparty='former_owners',at='2025-07-01T00:00:00Z',amount='-80/1',classification='acquisition_consideration'),dict(entity='S',at='2025-07-01T00:00:00Z',amount='50/1',classification='cash_acquired'),dict(entity='S',at='2025-08-01T00:00:00Z',amount='40/1',classification='operating')]
    return out
