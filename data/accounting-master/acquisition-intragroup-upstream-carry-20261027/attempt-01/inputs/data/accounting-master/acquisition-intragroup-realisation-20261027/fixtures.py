"""Independent legal journals and exact report expectations, without candidate calls."""
from pathlib import Path
from hashlib import sha256
from fractions import Fraction as F
from copy import deepcopy
import json
H=Path(__file__).resolve().parent
SAVED=json.loads((H.parent/'acquisition-intragroup-20261027/attempt-01/cases.json').read_text())
def digest(x):return sha256(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
def frac(x):q=F(x);return str(q.numerator)+'/'+str(q.denominator)
def prior(election,mix,settled,tax):return next(x for x in SAVED if x['id']=='/'.join([election,mix,'settled' if settled else 'credit',tax]))
def bind(b):b['payload']['books_sha256']=digest(b['payload']['books']);b['expected_payload_sha256']=digest(b['payload']);return b
CAL=dict(precontrol_receipt='2025-06-29T00:00:00Z',precontrol_close='2025-06-30T00:00:00Z',operating_receipt='2025-08-01T00:00:00Z',depreciation='2025-12-31T00:00:00Z',tax='2025-12-31T00:00:00Z')
def fixture(election='proportional',mix='cash',settled=False,tax='recognised',sold='1/2'):
    old=prior(election,mix,settled,tax);r=F(sold);books=deepcopy(old['result']['original_books'])
    for stage in ['opening','acquisition','closing']:books['S']['snapshots'][stage]['balances'].update(merchandise_revenue='0/1',cost_of_sales='0/1',current_tax_expense='0/1',current_tax_payable='0/1')
    sc=books['S']['snapshots']['closing']['balances'];sc['cash']=frac(F(sc['cash'])+40*r)
    sc.update(inventory=frac(30-30*r),merchandise_revenue=frac(-40*r),cost_of_sales=frac(30*r),current_tax_expense=frac(0 if tax=='unresolved' else F(5,2)*r),current_tax_payable=frac(0 if tax=='unresolved' else -F(5,2)*r))
    sale=dict(id='external-S-X-1',seller='S',customer='X',at='2025-12-01T00:00:00Z',currency='USD',unit='currency_unit',fraction=frac(r),receipts=frac(40*r),cost=frac(30*r),recognition='Stipulated customer contract, control transfer and fixed price; no returns or other obligations')
    return bind(dict(profile='ConditionalDownstreamRealisation/1',payload=dict(predecessor_request=deepcopy(old['request']),predecessor_result_sha256=digest(old['result']),source_lock_sha256=sha256((H/'predecessor-lock.json').read_bytes()).hexdigest(),external_sale=sale,event_calendar=deepcopy(CAL),history_premise='Explicit synthetic dated events; balances do not establish actual history',books=books,books_sha256=digest(books)),expected_payload_sha256=''))
def expected(election,mix,settled,tax,sold):
    old=deepcopy(prior(election,mix,settled,tax)['result']);b=fixture(election,mix,settled,tax,sold);p=b['payload'];r=F(sold)
    known=tax!='unresolved';rec=tax=='recognised';q=F(0) if election=='none' else F(1,4)
    result=dict(original_books=p['books'],tax=old['tax'],external_sale=p['external_sale'],intragroup_cash_origins=old['intragroup_cash_origins'])
    journals=[]
    def event(id,entity,at,entries,origin):journals.append(dict(id=id,entity=entity,at=at,origin=origin,entries={k:frac(v) for k,v in entries.items()}))
    for e in ['P','S']:event('opening-'+e,e,'2025-01-01T00:00:00Z',p['books'][e]['snapshots']['opening']['balances'],'Supplied opening trial balance; no inferred capital event')
    event('precontrol-receipt','S',CAL['precontrol_receipt'],{'cash':20,'revenue':-20},'Stipulated pre-control cash sale')
    event('precontrol-close','S',CAL['precontrol_close'],{'revenue':20,'retained_pre':-20},'Stipulated interim profit close')
    # Explicit three consideration journals; no candidate journal builder reused.
    acquisition={'cash':{'cash':-120,'investment':120,'capital':0},'equity':{'cash':0,'investment':120,'capital':-120},'mixed':{'cash':-50,'investment':120,'capital':-70}}[mix]
    event('parent-acquisition','P','2025-07-01T00:00:00Z',acquisition,'Supplied acquisition consideration components')
    event('controlled-receipt','S',CAL['operating_receipt'],{'cash':40,'revenue':-40},'Stipulated post-control operating receipt')
    event('internal-sale-parent','P','2025-10-01T00:00:00Z',{'receivable':30,'revenue':-30,'cost_of_sales':20,'inventory':-20},'inventory-P-S-1')
    event('internal-purchase-subsidiary','S','2025-10-01T00:00:00Z',{'inventory':30,'intragroup_payable':-30},'inventory-P-S-1')
    if settled:
        event('internal-settlement-parent','P','2025-11-01T00:00:00Z',{'cash':30,'receivable':-30},'settlement-P-S-1')
        event('internal-settlement-subsidiary','S','2025-11-01T00:00:00Z',{'cash':-30,'intragroup_payable':30},'settlement-P-S-1')
    if r:event('external-sale','S','2025-12-01T00:00:00Z',{'cash':40*r,'merchandise_revenue':-40*r,'cost_of_sales':30*r,'inventory':-30*r},'external-S-X-1')
    event('legal-depreciation','S',CAL['depreciation'],{'depreciation':7,'equipment':-7},'Supplied legal equipment expense')
    if known:
        event('seller-current-tax','P',CAL['tax'],{'current_tax_expense':F(5,2),'current_tax_payable':F(-5,2)},'Supplied seller tax on internal margin')
        event('buyer-current-tax','S',CAL['tax'],{'current_tax_expense':F(5,2)*r,'current_tax_payable':-F(5,2)*r},'Supplied buyer tax on external trading profit')
    result['legal_journals']=sorted(journals,key=lambda x:(x['at'],x['id']))
    result['external_cash_origins']=[] if not r else [dict(id='external-S-X-1/receipt',entity='S',counterparty='X',at='2025-12-01T00:00:00Z',amount=frac(40*r),classification='operating',elimination='0/1')]
    for stage in ['acquisition','closing']:
        w=deepcopy(old[stage+'_worksheet']);w['raw']={e+'.'+k:v for e in ['P','S'] for k,v in p['books'][e]['snapshots'][stage]['balances'].items()}
        w['adjusted'].update({'S.merchandise_revenue':'0/1','S.cost_of_sales':'0/1','S.current_tax_expense':'0/1','S.current_tax_payable':'0/1'})
        if stage=='closing':
            a=w['adjusted'];a['S.cash']=frac(F(a['S.cash'])+40*r)
            a.update({'S.inventory':frac(20*(1-r)),'P.cost_of_sales':frac(-10*r),'S.merchandise_revenue':frac(-40*r),'S.cost_of_sales':frac(30*r),'S.current_tax_expense':frac(F(5,2)*r if known else 0),'S.current_tax_payable':frac(-F(5,2)*r if known else 0)})
            if known:a.update({'group.inventory_deferred_tax_asset':frac(F(5,2)*(1-r) if rec else 0),'P.intragroup_deferred_tax_expense':frac(-F(5,2)*(1-r) if rec else 0)})
            for entry in w['journals']:
                if entry['id']=='unrealised-margin':entry['entries']={'P.cost_of_sales':frac(10*(1-r)),'S.inventory':frac(-10*(1-r))}
                if entry['id']=='inventory-deferred-tax':entry['entries']={'group.inventory_deferred_tax_asset':frac(F(5,2)*(1-r) if rec else 0),'P.intragroup_deferred_tax_expense':frac(-F(5,2)*(1-r) if rec else 0)}
            z=w['balances'];z['cash']=frac(F(z['cash'])+40*r);z['inventory']=frac(20*(1-r));z['merchandise_revenue']=frac(-40*r);z['cost_of_sales']=frac(20*r)
            if known:
                z['current_tax_expense']=frac(F(5,2)*(1+r));z['current_tax_payable']=frac(-F(5,2)*(1+r))
                if rec:z['inventory_deferred_tax_asset']=frac(F(5,2)*(1-r));z['intragroup_deferred_tax_expense']=frac(-F(5,2)*(1-r))
            z={k:v for k,v in z.items() if F(v)!=0 or k=='nci'};w['balances']=z
        result[stage+'_worksheet']=w
    if known:
        report=deepcopy(old['report']);buyer=F(15,2)*r;parent=F(15,2)*r if rec else 10*r;increment=buyer+parent
        for k,amount in [('profit',increment),('owners_profit',parent+(1-q)*buyer),('nci_profit',q*buyer),('nci_closing',q*buyer),('owners_equity_closing',parent+(1-q)*buyer),('assets_closing',F(35,2)*r if rec else 20*r),('liabilities_closing',F(5,2)*r),('equity_closing',increment)]:report[k]=frac(F(report[k])+amount)
        report.update(acquisition_balances=result['acquisition_worksheet']['balances'],closing_balances=result['closing_worksheet']['balances'])
        report['cash']['operating']=frac(40+40*r);report['cash']['closing']=frac(F(old['report']['cash']['closing'])+40*r)
        report['parent_equity'].update(owners_profit=report['owners_profit'],closing=report['owners_equity_closing'])
        report['inventory']={k:frac(value*(1-r)) for k,value in [('group_carrying',20),('buyer_tax_base',30),('eliminated_margin',10)]}
        report['intragroup_tax']=dict(current_expense=frac(F(5,2)*(1+r)),current_payable=frac(F(5,2)*(1+r)),deferred_asset=frac(F(5,2)*(1-r) if rec else 0),deferred_income=frac(F(5,2)*(1-r) if rec else 0),net_profit_effect=frac(-5*r if rec else -F(5,2)*(1+r)))
        report['external_trade']=dict(fraction=frac(r),receipts=frac(40*r),legal_cost=frac(30*r),group_cost=frac(20*r),group_pretax_profit=frac(20*r),buyer_after_tax_profit=frac(buyer))
        result['report']=report
    return result
