"""Independent two-year openings, journal effects and closed-form report oracle."""
from pathlib import Path
from hashlib import sha256
from fractions import Fraction as F
from copy import deepcopy
import json
H=Path(__file__).resolve().parent
SAVED=json.loads((H.parent/'acquisition-intragroup-realisation-20261027/attempt-01/cases.json').read_text())
def frac(x):q=F(x);return str(q.numerator)+'/'+str(q.denominator)
def digest(x):return sha256(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
def prior(earlier,settled):return next(x for x in SAVED if x['id']=='proportional/cash/'+('settled' if settled else 'credit')+'/recognised/'+earlier)
def openings(earlier,settled):
    r=F(earlier);old=prior(earlier,settled)['result']
    legal={e+'.'+k:v for e in ['P','S'] for k,v in old['original_books'][e]['snapshots']['closing']['balances'].items()}
    # Explicit closed chart; retained amounts are separately derived from legal profit.
    for k in ['P.revenue','P.cost_of_sales','P.current_tax_expense','S.revenue','S.merchandise_revenue','S.cost_of_sales','S.depreciation','S.operating_expense','S.current_tax_expense']:legal[k]='0/1'
    legal['P.retained_post']='-15/2';legal['S.retained_post']=frac(-33-F(15,2)*r)
    group=deepcopy(old['closing_worksheet']['adjusted'])
    for k in ['P.revenue','P.cost_of_sales','P.current_tax_expense','P.intragroup_deferred_tax_expense','S.revenue','S.merchandise_revenue','S.cost_of_sales','S.depreciation','S.operating_expense','S.current_tax_expense','group.depreciation','group.tax_expense']:group[k]='0/1'
    group['P.retained_post']=frac(-F(15,2)*r);group['S.retained_post']=frac(-F(189,8)-F(45,8)*r)
    group['group.nci']=frac(-F(293,8)-F(15,8)*r)
    return legal,group
def bind(b):
    p=b['payload'];p['opening_sha256']=digest(dict(legal=p['opening_legal'],group=p['opening_group']));b['expected_payload_sha256']=digest(p);return b
def fixture(earlier='0/1',settled=False,fraction='1/1',tax='known'):
    old=prior(earlier,settled);legal,group=openings(earlier,settled);sold=(1-F(earlier))*F(fraction)
    return bind(dict(profile='ConditionalDownstreamCarry/1',payload=dict(prior_request=deepcopy(old['request']),prior_result_sha256=digest(old['result']),source_lock_sha256=sha256((H/'predecessor-lock.json').read_bytes()).hexdigest(),opening_legal=legal,opening_group=group,opening_sha256='',period=dict(start='2026-01-01T00:00:00Z',end_exclusive='2027-01-01T00:00:00Z'),ownership='unchanged_75_percent_ordinary_control_through_2026',sale=dict(id='external-year2-S-X',at='2026-06-01T00:00:00Z',fraction_of_remaining=fraction,receipts=frac(40*sold),legal_cost=frac(30*sold),currency='USD',unit='currency_unit',recognition='Stipulated qualifying external control transfer at fixed cash price'),equipment=dict(legal_depreciation='14/1',additional_depreciation='4/1',tax_release='1/1',premise='Supplied full-year equipment and tax schedules; no inferred useful life'),tax_continuation='unresolved' if tax=='unresolved' else 'supplied_same_rates_recoverability_and_downstream_allocation'),expected_payload_sha256=''))
def expected(earlier,settled,fraction):
    r=F(earlier);s=(1-r)*F(fraction);total=r+s;legal,group=openings(earlier,settled)
    # Account-specific opening adjustments; no candidate state subtraction.
    bridge={k:'0/1' for k in set(legal)|set(group)}
    bridge.update({'P.investment':'-120/1','P.receivable':'0/1' if settled else '-30/1','P.retained_post':frac(F(15,2)*(1-r)),
      'S.capital':'80/1','S.retained_pre':'20/1','S.retained_post':frac(F(75,8)+F(15,8)*r),'S.equipment':'18/1','S.inventory':frac(-10*(1-r)),
      'S.intragroup_payable':'0/1' if settled else '30/1','group.goodwill':'135/4','group.deferred_tax':'-9/2','group.inventory_deferred_tax_asset':frac(F(5,2)*(1-r)),
      'group.nci':frac(-F(293,8)-F(15,8)*r)})
    closing=deepcopy(legal);closing.update({'S.cash':frac((60 if settled else 90)+40*total),'S.inventory':frac(30*(1-total)),
      'S.merchandise_revenue':frac(-40*s),'S.cost_of_sales':frac(30*s),'S.current_tax_expense':frac(F(5,2)*s),
      'S.current_tax_payable':frac(-F(5,2)*total),'S.depreciation':'14/1','S.equipment':'49/1'})
    events=[]
    def event(id,entries,origin):events.append(dict(id=id,at='2026-06-01T00:00:00Z' if id=='outside-sale' else '2026-12-31T00:00:00Z',origin=origin,entries={k:frac(v) for k,v in entries.items()}))
    if s:event('outside-sale',{'S.cash':40*s,'S.merchandise_revenue':-40*s,'S.cost_of_sales':30*s,'S.inventory':-30*s},'external-year2-S-X')
    event('legal-depreciation',{'S.depreciation':14,'S.equipment':-14},'Supplied year2 legal schedule')
    event('buyer-current-tax',{'S.current_tax_expense':F(5,2)*s,'S.current_tax_payable':-F(5,2)*s},'Supplied year2 buyer tax')
    js=[dict(id='carried-opening-bridge',at='2026-01-01T00:00:00Z',origin='Exact prior-year closed group minus closed legal accounts; no new acquisition',entries=bridge)]
    for id,entries,attribution,origin in [
      ('inventory-margin-release',{'S.inventory':10*s,'S.cost_of_sales':-10*s},'parent_owners','Release carried downstream inventory adjustment'),
      ('inventory-tax-reversal',{'group.inventory_deferred_tax_asset':-F(5,2)*s,'P.inventory_tax_reversal_expense':F(5,2)*s},'parent_owners','Use carried deductible inventory difference'),
      ('acquired-basis-depreciation',{'S.equipment':-4,'group.depreciation':4},'subsidiary_ordinary_rights','Supplied continuing acquisition basis'),
      ('acquired-tax-release',{'group.deferred_tax':1,'group.tax_expense':-1},'subsidiary_ordinary_rights','Supplied continuing acquisition tax schedule')]:
        js.append(dict(id=id,at='2026-12-31T00:00:00Z',origin=origin,profit_attribution=attribution,entries={k:frac(v) for k,v in entries.items()}))
    adjusted=deepcopy(group);adjusted.update({'S.cash':frac((60 if settled else 90)+40*total),'S.inventory':frac(20*(1-total)),
      'S.merchandise_revenue':frac(-40*s),'S.cost_of_sales':frac(20*s),'S.current_tax_expense':frac(F(5,2)*s),'S.current_tax_payable':frac(-F(5,2)*total),
      'S.depreciation':'14/1','S.equipment':'63/1','group.depreciation':'4/1','group.tax_expense':'-1/1','group.deferred_tax':'-7/2',
      'group.inventory_deferred_tax_asset':frac(F(5,2)*(1-total)),'P.inventory_tax_reversal_expense':frac(F(5,2)*s)})
    balances=dict(parent_capital='-320/1',cash=frac(270+40*total),current_tax_payable=frac(-F(5,2)*(1+total)),P_retained_post=frac(-F(15,2)*r),S_retained_post=frac(-F(189,8)-F(45,8)*r),equipment='63/1',payable='-20/1',inventory=frac(20*(1-total)),deferred_tax='-7/2',goodwill='135/4',inventory_deferred_tax_asset=frac(F(5,2)*(1-total)),nci=frac(-F(293,8)-F(15,8)*r),merchandise_revenue=frac(-40*s),cost_of_sales=frac(20*s),current_tax_expense=frac(F(5,2)*s),depreciation='18/1',tax_expense='-1/1',inventory_tax_reversal_expense=frac(F(5,2)*s))
    balances={k:v for k,v in balances.items() if F(v)}
    report={k:frac(v) for k,v in dict(profit=15*s-17,owners_profit=F(105,8)*s-F(51,4),nci_profit=F(15,8)*s-F(17,4),
      assets=F(1557,4)+F(35,2)*total,liabilities=26+F(5,2)*total,equity=F(1453,4)+15*total,owners_equity=F(2647,8)+F(105,8)*total,
      nci=F(259,8)+F(15,8)*total,cash=270+40*total,inventory=20*(1-total),equipment=63,goodwill=F(135,4),inventory_deferred_tax_asset=F(5,2)*(1-total),acquired_deferred_tax_liability=F(7,2),current_tax_payable=F(5,2)*(1+total)).items()}
    return dict(opening_legal=legal,opening_group=group,opening_bridge=bridge,legal_journals=events,closing_legal=closing,group_journals=js,closing_adjusted=adjusted,closing_balances=balances,report=report,prior_report=deepcopy(prior(earlier,settled)['result']['report']),cash_origins=[] if not s else [dict(entity='S',counterparty='X',at='2026-06-01T00:00:00Z',amount=frac(40*s),classification='operating',origin='external-year2-S-X')])
