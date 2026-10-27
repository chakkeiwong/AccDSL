"""Independent explicit balances/journals; never import or call the candidate."""
from pathlib import Path
from hashlib import sha256
from fractions import Fraction as F
from copy import deepcopy
import json
H=Path(__file__).resolve().parent
SAVED=json.loads((H.parent/'acquisition-consideration-20261027/attempt-01/cases.json').read_text())
def digest(x):return sha256(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
def frac(x):q=F(x);return str(q.numerator)+'/'+str(q.denominator)
def ser(x):return {k:frac(v) for k,v in x.items()}
def prior(election,mix):return next(x for x in SAVED if x['id']==election+'/'+mix)
def bind(b):b['payload']['books_sha256']=digest(b['payload']['books']);b['expected_payload_sha256']=digest(b['payload']);return b
CAL=dict(precontrol_receipt='2025-06-29T00:00:00Z',precontrol_close='2025-06-30T00:00:00Z',operating_receipt='2025-08-01T00:00:00Z',depreciation='2025-12-31T00:00:00Z',tax='2025-12-31T00:00:00Z')
EXTRA={'P':['inventory','intragroup_payable','merchandise_revenue','cost_of_sales','current_tax_expense','current_tax_payable'],
       'S':['inventory','receivable','merchandise_revenue','cost_of_sales','current_tax_expense','current_tax_payable']}
def fixture(election='proportional',mix='cash',settled=False,tax='recognised',sold='0/1'):
    old=prior(election,mix);r=F(sold);known=tax!='unresolved';books=deepcopy(old['result']['original_books'])
    for e in ['P','S']:
        for stage in ['opening','acquisition','closing']:books[e]['snapshots'][stage]['balances'].update({k:'0/1' for k in EXTRA[e]})
    pc=books['P']['snapshots']['closing']['balances'];sc=books['S']['snapshots']['closing']['balances']
    pc.update(cash=frac(F(pc['cash'])+40*r-(30 if settled else 0)),inventory=frac(30*(1-r)),intragroup_payable=frac(0 if settled else -30),merchandise_revenue=frac(-40*r),cost_of_sales=frac(30*r),current_tax_expense=frac(F(5,2)*r if known else 0),current_tax_payable=frac(-F(5,2)*r if known else 0))
    sc.update(cash=frac(70+(30 if settled else 0)),inventory='0/1',receivable=frac(0 if settled else 30),merchandise_revenue='-30/1',cost_of_sales='20/1',current_tax_expense=frac(F(5,2) if known else 0),current_tax_payable=frac(F(-5,2) if known else 0))
    purchase=dict(id='purchase-S-V-1',buyer='S',vendor='V',at='2025-09-01T00:00:00Z',currency='USD',unit='currency_unit',amount='20/1',tax_premise='No additional VAT or sales tax in this stipulated purchase')
    trade=dict(id='inventory-S-P-1',seller='S',buyer='P',at='2025-10-01T00:00:00Z',currency='USD',unit='currency_unit',cost='20/1',price='30/1',impairment='explicitly_none_synthetic')
    settlement=dict(id='settlement-P-S-1',trade_id='inventory-S-P-1',payer='P',payee='S',at='2025-11-01T00:00:00Z',amount='30/1',currency='USD',unit='currency_unit') if settled else None
    sale=dict(id='external-P-X-1',seller='P',customer='X',at='2025-12-01T00:00:00Z',currency='USD',unit='currency_unit',fraction=frac(r),receipts=frac(40*r),cost=frac(30*r),recognition='Stipulated customer contract, control transfer and fixed price; no returns or other obligations')
    taxes=dict(status='conditional',seller_rate='1/4',buyer_rate='1/4',tax_base=frac(30*(1-r)),recognition='stipulated_recoverable' if tax=='recognised' else 'stipulated_not_recognised',allocation='subsidiary_seller_stipulated_upstream',premise='Stipulated separate tax bases, rates, recognition and attribution; not actual tax authority') if known else dict(status='unresolved',reason='Current and deferred tax and allocation are not supplied')
    return bind(dict(profile='ConditionalUpstreamInventory/1',payload=dict(base_case=old['id'],base_request=deepcopy(old['request']),base_result_sha256=digest(old['result']),source_lock_sha256=sha256((H/'predecessor-lock.json').read_bytes()).hexdigest(),supplier_purchase=purchase,trade=trade,settlement=settlement,external_sale=sale,tax=taxes,elimination_fraction='1/1',books=books,books_sha256=digest(books),event_calendar=deepcopy(CAL),history_premise='Explicit synthetic dated events; balances do not establish actual history'),expected_payload_sha256=''))
def expected(election,mix,settled,tax,sold):
    old=deepcopy(prior(election,mix)['result']);b=fixture(election,mix,settled,tax,sold);p=b['payload'];r=F(sold);known=tax!='unresolved';rec=tax=='recognised';q=F(0) if election=='none' else F(1,4)
    result=dict(original_books=deepcopy(p['books']),tax=deepcopy(p['tax']),external_sale=deepcopy(p['external_sale']),supplier_purchase=deepcopy(p['supplier_purchase']))
    journals=[]
    def event(id,e,at,entries,origin):journals.append(dict(id=id,entity=e,at=at,entries=ser(entries),origin=origin))
    for e in ['P','S']:event('opening-'+e,e,'2025-01-01T00:00:00Z',p['books'][e]['snapshots']['opening']['balances'],'Supplied opening trial balance; no inferred capital event')
    event('precontrol-receipt','S',CAL['precontrol_receipt'],{'cash':20,'revenue':-20},'Stipulated pre-control cash sale')
    event('precontrol-close','S',CAL['precontrol_close'],{'revenue':20,'retained_pre':-20},'Stipulated interim profit close')
    c={'cash':{'cash':-120,'investment':120,'capital':0},'equity':{'cash':0,'investment':120,'capital':-120},'mixed':{'cash':-50,'investment':120,'capital':-70}}[mix]
    event('parent-acquisition','P','2025-07-01T00:00:00Z',c,'Supplied acquisition consideration components')
    event('controlled-receipt','S',CAL['operating_receipt'],{'cash':40,'revenue':-40},'Stipulated post-control operating receipt')
    event('external-inventory-purchase','S','2025-09-01T00:00:00Z',{'cash':-20,'inventory':20},'purchase-S-V-1')
    event('internal-sale-subsidiary','S','2025-10-01T00:00:00Z',{'receivable':30,'merchandise_revenue':-30,'cost_of_sales':20,'inventory':-20},'inventory-S-P-1')
    event('internal-purchase-parent','P','2025-10-01T00:00:00Z',{'inventory':30,'intragroup_payable':-30},'inventory-S-P-1')
    if settled:
        event('internal-settlement-parent','P','2025-11-01T00:00:00Z',{'cash':-30,'intragroup_payable':30},'settlement-P-S-1')
        event('internal-settlement-subsidiary','S','2025-11-01T00:00:00Z',{'cash':30,'receivable':-30},'settlement-P-S-1')
    if r:event('external-sale','P','2025-12-01T00:00:00Z',{'cash':40*r,'merchandise_revenue':-40*r,'cost_of_sales':30*r,'inventory':-30*r},'external-P-X-1')
    event('legal-depreciation','S',CAL['depreciation'],{'depreciation':7,'equipment':-7},'Supplied legal equipment expense')
    if known:
        event('seller-current-tax','S',CAL['tax'],{'current_tax_expense':F(5,2),'current_tax_payable':F(-5,2)},'Supplied seller tax on internal margin')
        event('buyer-current-tax','P',CAL['tax'],{'current_tax_expense':F(5,2)*r,'current_tax_payable':-F(5,2)*r},'Supplied buyer tax on external trading profit')
    result['legal_journals']=sorted(journals,key=lambda x:(x['at'],x['id']))
    result['intragroup_cash_origins']=[] if not settled else [dict(id='settlement-P-S-1/payment',entity='P',counterparty='S',at='2025-11-01T00:00:00Z',amount='-30/1',classification='operating',elimination='30/1'),dict(id='settlement-P-S-1/receipt',entity='S',counterparty='P',at='2025-11-01T00:00:00Z',amount='30/1',classification='operating',elimination='-30/1')]
    result['external_cash_origins']=[dict(id='purchase-S-V-1/payment',entity='S',counterparty='V',at='2025-09-01T00:00:00Z',amount='-20/1',classification='operating',elimination='0/1')]
    if r:result['external_cash_origins'].append(dict(id='external-P-X-1/receipt',entity='P',counterparty='X',at='2025-12-01T00:00:00Z',amount=frac(40*r),classification='operating',elimination='0/1'))
    for stage in ['acquisition','closing']:
        w=deepcopy(old[stage+'_worksheet']);w['raw']={e+'.'+k:v for e in ['P','S'] for k,v in p['books'][e]['snapshots'][stage]['balances'].items()}
        for e in ['P','S']:w['adjusted'].update({e+'.'+k:'0/1' for k in EXTRA[e]})
        if stage=='closing':
            a=w['adjusted'];a['P.cash']=p['books']['P']['snapshots'][stage]['balances']['cash'];a['S.cash']=p['books']['S']['snapshots'][stage]['balances']['cash']
            a.update({'P.inventory':frac(20*(1-r)),'P.merchandise_revenue':frac(-40*r),'P.cost_of_sales':frac(30*r),'S.cost_of_sales':frac(-10*r),'P.current_tax_expense':frac(F(5,2)*r if known else 0),'P.current_tax_payable':frac(-F(5,2)*r if known else 0),'S.current_tax_expense':frac(F(5,2) if known else 0),'S.current_tax_payable':frac(F(-5,2) if known else 0)})
            if known:a.update({'group.inventory_deferred_tax_asset':frac(F(5,2)*(1-r) if rec else 0),'S.intragroup_deferred_tax_expense':frac(-F(5,2)*(1-r) if rec else 0)})
            def adj(id,entries,origin='inventory-S-P-1'):w['journals'].append(dict(id=id,at='2026-01-01T00:00:00Z',origin=origin,entries=ser(entries)))
            if not settled:adj('reciprocal-balance',{'S.receivable':-30,'P.intragroup_payable':30})
            adj('intragroup-sale',{'S.merchandise_revenue':30,'S.cost_of_sales':-30})
            adj('unrealised-margin',{'S.cost_of_sales':10*(1-r),'P.inventory':-10*(1-r)})
            if known:adj('inventory-deferred-tax',{'group.inventory_deferred_tax_asset':F(5,2)*(1-r) if rec else 0,'S.intragroup_deferred_tax_expense':-F(5,2)*(1-r) if rec else 0},'Explicit supplied upstream tax/recoverability/attribution premises')
            z=w['balances'];z['cash']=frac(F(z['cash'])-20+40*r);z['inventory']=frac(20*(1-r));z['merchandise_revenue']=frac(-40*r);z['cost_of_sales']=frac(20*r)
            if known:z.update(current_tax_expense=frac(F(5,2)*(1+r)),current_tax_payable=frac(-F(5,2)*(1+r)),inventory_deferred_tax_asset=frac(F(5,2)*(1-r) if rec else 0),intragroup_deferred_tax_expense=frac(-F(5,2)*(1-r) if rec else 0))
            w['balances']={k:v for k,v in z.items() if F(v) or k=='nci'}
        result[stage+'_worksheet']=w
    if known:
        # Independent closed forms: seller recognised=7.5r, otherwise10r-2.5.
        seller=F(15,2)*r if rec else 10*r-F(5,2);buyer=F(15,2)*r
        profit=15*r if rec else F(35,2)*r-F(5,2);dta=F(5,2)*(1-r) if rec else F(0)
        report=deepcopy(old['report'])
        for k,delta in [('profit',profit),('owners_profit',profit-q*seller),('nci_profit',q*seller),('nci_closing',q*seller),('owners_equity_closing',profit-q*seller),('assets_closing',20*r+dta),('liabilities_closing',F(5,2)*(1+r)),('equity_closing',profit)]:report[k]=frac(F(report[k])+delta)
        report.update(acquisition_balances=result['acquisition_worksheet']['balances'],closing_balances=result['closing_worksheet']['balances'])
        report['cash']['operating']=frac(20+40*r);report['cash']['closing']=frac(F(old['report']['cash']['closing'])-20+40*r)
        report['parent_equity'].update(owners_profit=report['owners_profit'],closing=report['owners_equity_closing'])
        report['inventory']=ser(dict(group_carrying=20*(1-r),buyer_tax_base=30*(1-r),eliminated_margin=10*(1-r)))
        report['intragroup_tax']=ser(dict(current_expense=F(5,2)*(1+r),current_payable=F(5,2)*(1+r),deferred_asset=dta,deferred_income=dta,net_profit_effect=-5*r if rec else -F(5,2)*(1+r)))
        report['trade_profit']=ser(dict(subsidiary_contribution=seller,parent_contribution=buyer,total=profit,nci_contribution=q*seller))
        report['intragroup_cash']=ser(dict(receipts=30 if settled else 0,payments=30 if settled else 0,eliminated_receipts=30 if settled else 0,eliminated_payments=30 if settled else 0,group_net=0))
        result['report']=report
    return result
