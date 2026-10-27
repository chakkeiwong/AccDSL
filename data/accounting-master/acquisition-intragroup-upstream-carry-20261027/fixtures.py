"""Independent upstream closed openings and complete second-year expectations."""
from pathlib import Path
from hashlib import sha256
from fractions import Fraction as F
from copy import deepcopy
import json
H=Path(__file__).resolve().parent
SAVED=json.loads((H.parent/'acquisition-intragroup-upstream-20261027/attempt-01/cases.json').read_text())
def frac(x):q=F(x);return str(q.numerator)+'/'+str(q.denominator)
def ser(x):return {k:frac(v) for k,v in x.items()}
def digest(x):return sha256(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
def prior(earlier,settled,tax):return next(x for x in SAVED if x['id']=='proportional/cash/'+('settled' if settled else 'credit')+'/'+tax+'/'+earlier)
def openings(earlier,settled,tax):
    r=F(earlier);old=prior(earlier,settled,tax)['result'];known=tax!='unresolved';rec=tax=='recognised'
    if not known:return {},{}
    legal={e+'.'+k:v for e in ['P','S'] for k,v in old['original_books'][e]['snapshots']['closing']['balances'].items()}
    group=deepcopy(old['closing_worksheet']['adjusted'])
    income=['P.merchandise_revenue','P.cost_of_sales','P.current_tax_expense','S.revenue','S.merchandise_revenue','S.cost_of_sales','S.depreciation','S.operating_expense','S.current_tax_expense']
    for k in income:legal[k]='0/1';group[k]='0/1'
    for k in ['group.depreciation','group.tax_expense','S.intragroup_deferred_tax_expense']:group[k]='0/1'
    u=F(15,2)*r if rec else 10*r-F(5,2)
    legal.update({'P.retained_post':frac(-F(15,2)*r),'S.retained_post':'-81/2'})
    group.update({'P.retained_post':frac(-F(15,2)*r),'S.retained_post':frac(-F(3,4)*(F(63,2)+u)),'group.nci':frac(-F(115,4)-(F(63,2)+u)/4)})
    return legal,group
def bind(b):
    p=b['payload'];p['opening_sha256']=digest(dict(legal=p['opening_legal'],group=p['opening_group']));b['expected_payload_sha256']=digest(p);return b
def fixture(earlier='0/1',settled=False,fraction='1/1',tax='recognised',continuation='known'):
    old=prior(earlier,settled,tax);legal,group=openings(earlier,settled,tax);sold=(1-F(earlier))*F(fraction)
    return bind(dict(profile='ConditionalUpstreamCarry/1',payload=dict(prior_request=deepcopy(old['request']),prior_result_sha256=digest(old['result']),source_lock_sha256=sha256((H/'predecessor-lock.json').read_bytes()).hexdigest(),opening_legal=legal,opening_group=group,opening_sha256='',period=dict(start='2026-01-01T00:00:00Z',end_exclusive='2027-01-01T00:00:00Z'),ownership='unchanged_75_percent_ordinary_control_through_2026',sale=dict(id='external-year2-P-X',at='2026-06-01T00:00:00Z',fraction_of_remaining=fraction,receipts=frac(40*sold),legal_cost=frac(30*sold),currency='USD',unit='currency_unit',recognition='Stipulated qualifying external control transfer at fixed cash price'),equipment=dict(legal_depreciation='14/1',additional_depreciation='4/1',tax_release='1/1',premise='Supplied full-year equipment and tax schedules; no inferred useful life'),tax_continuation='unresolved' if continuation=='unresolved' else 'supplied_same_rates_recoverability_and_upstream_allocation'),expected_payload_sha256=''))
def expected(earlier,settled,fraction,tax):
    r=F(earlier);s=(1-r)*F(fraction);total=r+s;rec=tax=='recognised';legal,group=openings(earlier,settled,tax)
    u=F(15,2)*r if rec else 10*r-F(5,2);reversal=F(5,2)*s if rec else F(0)
    bridge={k:'0/1' for k in set(legal)|set(group)}
    bridge.update({'P.investment':'-120/1','P.intragroup_payable':'0/1' if settled else '30/1','P.inventory':frac(-10*(1-r)),
       'S.capital':'80/1','S.retained_pre':'20/1','S.retained_post':frac(F(135,8)-F(3,4)*u),'S.equipment':'18/1','S.receivable':'0/1' if settled else '-30/1',
       'group.goodwill':'135/4','group.deferred_tax':'-9/2','group.inventory_deferred_tax_asset':frac(F(5,2)*(1-r) if rec else 0),'group.nci':frac(-F(115,4)-(F(63,2)+u)/4)})
    closing=deepcopy(legal);closing.update({'P.cash':frac(180-(30 if settled else 0)+40*total),'P.inventory':frac(30*(1-total)),
      'P.merchandise_revenue':frac(-40*s),'P.cost_of_sales':frac(30*s),'P.current_tax_expense':frac(F(5,2)*s),'P.current_tax_payable':frac(-F(5,2)*total),'S.depreciation':'14/1','S.equipment':'49/1'})
    events=[]
    def event(id,entries,origin):events.append(dict(id=id,at='2026-06-01T00:00:00Z' if id=='outside-sale' else '2026-12-31T00:00:00Z',origin=origin,entries=ser(entries)))
    if s:event('outside-sale',{'P.cash':40*s,'P.merchandise_revenue':-40*s,'P.cost_of_sales':30*s,'P.inventory':-30*s},'external-year2-P-X')
    event('legal-depreciation',{'S.depreciation':14,'S.equipment':-14},'Supplied year2 legal schedule')
    event('buyer-current-tax',{'P.current_tax_expense':F(5,2)*s,'P.current_tax_payable':-F(5,2)*s},'Supplied year2 buyer tax')
    js=[dict(id='carried-opening-bridge',at='2026-01-01T00:00:00Z',origin='Exact prior-year closed group minus closed legal accounts; no new acquisition',entries=bridge)]
    for id,entries,origin in [
      ('inventory-margin-release',{'P.inventory':10*s,'S.cost_of_sales':-10*s},'Release carried upstream inventory adjustment'),
      ('inventory-tax-reversal',{'group.inventory_deferred_tax_asset':-reversal,'S.inventory_tax_reversal_expense':reversal},'Use carried deductible inventory difference'),
      ('acquired-basis-depreciation',{'S.equipment':-4,'group.depreciation':4},'Supplied continuing acquisition basis'),
      ('acquired-tax-release',{'group.deferred_tax':1,'group.tax_expense':-1},'Supplied continuing acquisition tax schedule')]:
        js.append(dict(id=id,at='2026-12-31T00:00:00Z',origin=origin,profit_attribution='subsidiary_ordinary_rights',entries=ser(entries)))
    adjusted=deepcopy(group);adjusted.update({'P.cash':frac(180-(30 if settled else 0)+40*total),'P.inventory':frac(20*(1-total)),
      'P.merchandise_revenue':frac(-40*s),'P.cost_of_sales':frac(30*s),'S.cost_of_sales':frac(-10*s),'P.current_tax_expense':frac(F(5,2)*s),'P.current_tax_payable':frac(-F(5,2)*total),
      'S.depreciation':'14/1','S.equipment':'63/1','group.depreciation':'4/1','group.tax_expense':'-1/1','group.deferred_tax':'-7/2','group.inventory_deferred_tax_asset':frac(F(5,2)*(1-total) if rec else 0),'S.inventory_tax_reversal_expense':frac(reversal)})
    balances=ser(dict(parent_capital=-300,cash=250+40*total,current_tax_payable=-F(5,2)*(1+total),P_retained_post=-F(15,2)*r,S_retained_post=-F(3,4)*(F(63,2)+u),
      equipment=63,payable=-20,inventory=20*(1-total),deferred_tax=F(-7,2),goodwill=F(135,4),inventory_deferred_tax_asset=F(5,2)*(1-total) if rec else 0,nci=-F(115,4)-(F(63,2)+u)/4,
      merchandise_revenue=-40*s,cost_of_sales=20*s,current_tax_expense=F(5,2)*s,depreciation=18,tax_expense=-1,inventory_tax_reversal_expense=reversal))
    balances={k:v for k,v in balances.items() if F(v)}
    if rec:
        profit=15*s-17;np=F(15,8)*s-F(17,4);assets=F(1477,4)+F(35,2)*total;equity=F(1373,4)+15*total;nci=F(259,8)+F(15,8)*total
    else:
        profit=F(35,2)*s-17;np=F(5,2)*s-F(17,4);assets=F(1467,4)+20*total;equity=F(1363,4)+F(35,2)*total;nci=F(127,4)+F(5,2)*total
    report=ser(dict(profit=profit,owners_profit=profit-np,nci_profit=np,assets=assets,liabilities=26+F(5,2)*total,equity=equity,owners_equity=equity-nci,nci=nci,cash=250+40*total,inventory=20*(1-total),equipment=63,goodwill=F(135,4),inventory_deferred_tax_asset=F(5,2)*(1-total) if rec else 0,acquired_deferred_tax_liability=F(7,2),current_tax_payable=F(5,2)*(1+total)))
    return dict(opening_legal=legal,opening_group=group,opening_bridge=bridge,legal_journals=events,closing_legal=closing,group_journals=js,closing_adjusted=adjusted,closing_balances=balances,report=report,prior_report=deepcopy(prior(earlier,settled,tax)['result']['report']),cash_origins=[] if not s else [dict(entity='P',counterparty='X',at='2026-06-01T00:00:00Z',amount=frac(40*s),classification='operating',origin='external-year2-P-X')])
