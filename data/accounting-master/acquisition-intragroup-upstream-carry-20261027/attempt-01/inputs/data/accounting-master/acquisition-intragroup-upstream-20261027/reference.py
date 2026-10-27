"""Fixed upstream profile: source-bound journals, complete worksheets and NCI."""
from pathlib import Path
from hashlib import sha256
from fractions import Fraction as F
from copy import deepcopy
import importlib.util,json
H=Path(__file__).resolve().parent;R=H.parents[2];S=H.parent/'acquisition-consideration-20261027'
spec=importlib.util.spec_from_file_location('upstream_acquisition_base',S/'reference.py')
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
h=base.h;num=base.number;fmt=base.fmt;serial=base.serial;FLAGS=base.FLAGS
PROFILE='ConditionalUpstreamInventory/1'
CAL=dict(precontrol_receipt='2025-06-29T00:00:00Z',precontrol_close='2025-06-30T00:00:00Z',operating_receipt='2025-08-01T00:00:00Z',depreciation='2025-12-31T00:00:00Z',tax='2025-12-31T00:00:00Z')
EXTRA={'P':['inventory','intragroup_payable','merchandise_revenue','cost_of_sales','current_tax_expense','current_tax_payable'],
       'S':['inventory','receivable','merchandise_revenue','cost_of_sales','current_tax_expense','current_tax_payable']}
def report(body):
    try:
        h.need(len(json.dumps(body,allow_nan=False))<900000,'request_size')
        h.fields(body,['profile','payload','expected_payload_sha256'],'envelope')
        h.need(body['profile']==PROFILE,'profile');p=body['payload']
        h.need(h.digest(p)==body['expected_payload_sha256'],'payload_binding')
        h.fields(p,['base_case','base_request','base_result_sha256','source_lock_sha256','supplier_purchase','trade','settlement','external_sale','tax','elimination_fraction','books','books_sha256','event_calendar','history_premise'],'payload')
        lock=H/'predecessor-lock.json'
        h.need(sha256(lock.read_bytes()).hexdigest()==p['source_lock_sha256'],'source_lock_binding')
        for name,d in json.loads(lock.read_text()).items():h.need(sha256((R/name).read_bytes()).hexdigest()==d,'protected_dependency:'+name)
        saved=json.loads((S/'attempt-01/cases.json').read_text())
        allowed=[x for x in saved if x['id'] in [e+'/'+m for e in ['proportional','fair_value','none'] for m in ['cash','equity','mixed']]]
        selected=next((x for x in allowed if x['id']==p['base_case']),None)
        h.need(selected is not None,'selected_base_case')
        h.need(p['base_request']==selected['request'],'selected_base_request')
        prior=base.report(p['base_request'])
        h.need(prior['status']=='conditional_worksheet','base_status')
        h.need(prior==selected['result'] and h.digest(prior)==p['base_result_sha256'],'base_result_binding')
        sp=p['base_request']['payload']['symbolic_request']['payload'];ownership=num(sp['ownership']['fraction']);q=1-ownership
        h.need(p['event_calendar']==CAL,'selected_event_calendar')
        h.need(p['history_premise']=='Explicit synthetic dated events; balances do not establish actual history','history_premise')
        currency=sp['acquisition']['currency'];unit=sp['acquisition']['unit'];end=sp['scope_request']['history_request']['interval']['end_exclusive']
        purchase=p['supplier_purchase']
        h.fields(purchase,['id','buyer','vendor','at','currency','unit','amount','tax_premise'],'supplier_purchase')
        h.need(purchase['id']=='purchase-S-V-1' and purchase['buyer']=='S' and purchase['vendor']=='V','supplier_parties')
        h.need(purchase['at']=='2025-09-01T00:00:00Z','supplier_date')
        h.need(purchase['currency']==currency and purchase['unit']==unit,'supplier_units')
        h.need(num(purchase['amount'])==20,'supplier_amount')
        h.need(purchase['tax_premise']=='No additional VAT or sales tax in this stipulated purchase','supplier_tax_premise')
        t=p['trade'];h.fields(t,['id','seller','buyer','at','currency','unit','cost','price','impairment'],'trade')
        h.need(t['id']=='inventory-S-P-1' and t['seller']=='S' and t['buyer']=='P','upstream_parties')
        h.need(t['at']=='2025-10-01T00:00:00Z','trade_date')
        h.need(t['currency']==currency and t['unit']==unit,'trade_units')
        cost=num(t['cost']);price=num(t['price']);margin=price-cost
        h.need(cost==20 and price==30,'trade_amounts')
        h.need(t['impairment']=='explicitly_none_synthetic','impairment_scope')
        h.need(num(p['elimination_fraction'])==1,'full_elimination_required')
        settled=p['settlement'] is not None
        if settled:
            s=p['settlement'];h.fields(s,['id','trade_id','payer','payee','at','amount','currency','unit'],'settlement')
            h.need(s['id']=='settlement-P-S-1' and s['trade_id']==t['id'] and s['payer']=='P' and s['payee']=='S','settlement_pair')
            h.need(s['at']=='2025-11-01T00:00:00Z','settlement_date')
            h.need(num(s['amount'])==price and s['currency']==currency and s['unit']==unit,'settlement_amount_units')
        sale=p['external_sale'];h.fields(sale,['id','seller','customer','at','currency','unit','fraction','receipts','cost','recognition'],'external_sale')
        h.need(sale['id']=='external-P-X-1' and sale['seller']=='P' and sale['customer']=='X','external_parties')
        h.need(sale['at']=='2025-12-01T00:00:00Z','external_date')
        h.need(sale['currency']==currency and sale['unit']==unit,'external_units')
        fraction=num(sale['fraction']);h.need(fraction in [F(0),F(1,2),F(1)],'selected_resale_fraction')
        receipts=num(sale['receipts']);legalcost=num(sale['cost'])
        h.need(receipts==40*fraction and legalcost==price*fraction,'external_amounts')
        h.need(sale['recognition']=='Stipulated customer contract, control transfer and fixed price; no returns or other obligations','revenue_premise')
        tax=p['tax'];h.need(type(tax) is dict and 'status' in tax,'tax_disposition_required');known=tax['status']=='conditional'
        if known:
            h.fields(tax,['status','seller_rate','buyer_rate','tax_base','recognition','allocation','premise'],'tax')
            h.need(num(tax['seller_rate'])==F(1,4) and num(tax['buyer_rate'])==F(1,4),'selected_tax_rates')
            h.need(num(tax['tax_base'])==price*(1-fraction),'tax_base')
            h.need(tax['recognition'] in ['stipulated_recoverable','stipulated_not_recognised'],'recognition_disposition')
            h.need(tax['allocation']=='subsidiary_seller_stipulated_upstream','tax_allocation_required');h.text(tax['premise'])
            seller_tax=margin*num(tax['seller_rate']);buyer_tax=(receipts-legalcost)*num(tax['buyer_rate'])
            dta=(num(tax['tax_base'])-cost*(1-fraction))*num(tax['buyer_rate']) if tax['recognition']=='stipulated_recoverable' else F(0)
        else:
            h.fields(tax,['status','reason'],'tax');h.need(tax['status']=='unresolved','tax_disposition_required');h.text(tax['reason'])
            seller_tax=buyer_tax=dta=F(0)
        books=deepcopy(prior['original_books'])
        for e in ['P','S']:
            for snapshot in books[e]['snapshots'].values():snapshot['balances'].update({k:'0/1' for k in EXTRA[e]})
        journals=[]
        def event(id,e,at,entries,origin):
            h.need(sum(entries.values())==0,'legal_journal_balance')
            journals.append(dict(id=id,entity=e,at=at,origin=origin,entries=serial(entries)))
        for e in ['P','S']:event('opening-'+e,e,books[e]['snapshots']['opening']['at'],{k:num(v) for k,v in books[e]['snapshots']['opening']['balances'].items()},'Supplied opening trial balance; no inferred capital event')
        event('precontrol-receipt','S',CAL['precontrol_receipt'],dict(cash=F(20),revenue=F(-20)),'Stipulated pre-control cash sale')
        event('precontrol-close','S',CAL['precontrol_close'],dict(revenue=F(20),retained_pre=F(-20)),'Stipulated interim profit close')
        c=p['base_request']['payload']['consideration'];cash=num(c['cash']);equity=num(c['new_parent_equity'])
        event('parent-acquisition','P',sp['acquisition']['at'],dict(cash=-cash,investment=cash+equity,capital=-equity),'Supplied acquisition consideration components')
        event('controlled-receipt','S',CAL['operating_receipt'],dict(cash=F(40),revenue=F(-40)),'Stipulated post-control operating receipt')
        event('external-inventory-purchase','S',purchase['at'],dict(cash=-cost,inventory=cost),purchase['id'])
        event('internal-sale-subsidiary','S',t['at'],dict(receivable=price,merchandise_revenue=-price,cost_of_sales=cost,inventory=-cost),t['id'])
        event('internal-purchase-parent','P',t['at'],dict(inventory=price,intragroup_payable=-price),t['id'])
        if settled:
            event('internal-settlement-parent','P',s['at'],dict(cash=-price,intragroup_payable=price),s['id'])
            event('internal-settlement-subsidiary','S',s['at'],dict(cash=price,receivable=-price),s['id'])
        if fraction:event('external-sale','P',sale['at'],dict(cash=receipts,merchandise_revenue=-receipts,cost_of_sales=legalcost,inventory=-legalcost),sale['id'])
        event('legal-depreciation','S',CAL['depreciation'],dict(depreciation=F(7),equipment=F(-7)),'Supplied legal equipment expense')
        if known:
            event('seller-current-tax','S',CAL['tax'],dict(current_tax_expense=seller_tax,current_tax_payable=-seller_tax),'Supplied seller tax on internal margin')
            event('buyer-current-tax','P',CAL['tax'],dict(current_tax_expense=buyer_tax,current_tax_payable=-buyer_tax),'Supplied buyer tax on external trading profit')
        journals.sort(key=lambda x:(x['at'],x['id']))
        for e in ['P','S']:
            for snapshot in books[e]['snapshots'].values():
                state={k:F(0) for k in snapshot['balances']}
                for ev in journals:
                    if ev['entity']==e and h.moment(ev['at'])<=h.moment(snapshot['at']):
                        for k,v in ev['entries'].items():state[k]+=num(v)
                        h.need(state['cash']>=0,'negative_cash_requires_method')
                snapshot['balances']=serial(state)
        h.need(h.digest(p['books'])==p['books_sha256'],'books_binding');h.need(p['books']==books,'complete_legal_books')
        def adjustment(id,entries,origin):
            h.need(sum(entries.values())==0,'adjustment_balance')
            return dict(id=id,at=end,origin=origin,entries=serial(entries))
        extra=[]
        if not settled:extra.append(adjustment('reciprocal-balance',{'S.receivable':-price,'P.intragroup_payable':price},t['id']))
        extra.extend([adjustment('intragroup-sale',{'S.merchandise_revenue':price,'S.cost_of_sales':-price},t['id']),
                      adjustment('unrealised-margin',{'S.cost_of_sales':margin*(1-fraction),'P.inventory':-margin*(1-fraction)},t['id'])])
        if known:extra.append(adjustment('inventory-deferred-tax',{'group.inventory_deferred_tax_asset':dta,'S.intragroup_deferred_tax_expense':-dta},'Explicit supplied upstream tax/recoverability/attribution premises'))
        def worksheet(stage):
            raw={e+'.'+k:num(v) for e in ['P','S'] for k,v in books[e]['snapshots'][stage]['balances'].items()}
            entries=deepcopy(prior[stage+'_worksheet']['journals'])+(deepcopy(extra) if stage=='closing' else [])
            adjusted=deepcopy(raw)
            for entry in entries:
                for k,v in entry['entries'].items():adjusted[k]=adjusted.get(k,F(0))+num(v)
            h.need(sum(adjusted.values())==0,'adjusted_balance');aggregate={}
            for k,v in adjusted.items():
                e,n=k.split('.');n='parent_capital' if e=='P' and n=='capital' else n
                aggregate[n]=aggregate.get(n,F(0))+v
            aggregate={k:v for k,v in aggregate.items() if v};aggregate.setdefault('nci',F(0))
            return dict(raw=serial(raw),journals=entries,adjusted=serial(adjusted),balances=serial(aggregate))
        acq=worksheet('acquisition');close=worksheet('closing')
        origins=[]
        if settled:origins=[dict(id=s['id']+'/payment',entity='P',counterparty='S',at=s['at'],amount=fmt(-price),classification='operating',elimination=fmt(price)),dict(id=s['id']+'/receipt',entity='S',counterparty='P',at=s['at'],amount=fmt(price),classification='operating',elimination=fmt(-price))]
        outside=[dict(id=purchase['id']+'/payment',entity='S',counterparty='V',at=purchase['at'],amount=fmt(-cost),classification='operating',elimination='0/1')]
        if fraction:outside.append(dict(id=sale['id']+'/receipt',entity='P',counterparty='X',at=sale['at'],amount=fmt(receipts),classification='operating',elimination='0/1'))
        result=dict(profile=PROFILE,**FLAGS,request_sha256=h.digest(body),base_result_sha256=h.digest(prior),original_books=books,legal_journals=journals,acquisition_worksheet=acq,closing_worksheet=close,intragroup_cash_origins=origins,external_cash_origins=outside,tax=deepcopy(tax),external_sale=deepcopy(sale),supplier_purchase=deepcopy(purchase))
        if not known:return dict(result,status='tax_method_required',outstanding=['current_and_deferred_tax','tax_attribution','actual_source_and_accounting_admission'])
        seller=margin*fraction-seller_tax+dta;buyer=receipts-legalcost-buyer_tax;increment=seller+buyer
        r=deepcopy(prior['report'])
        for k,delta in [('profit',increment),('owners_profit',ownership*seller+buyer),('nci_profit',q*seller),('owners_equity_closing',ownership*seller+buyer),('nci_closing',q*seller),('assets_closing',receipts-cost*fraction+dta),('liabilities_closing',seller_tax+buyer_tax),('equity_closing',increment)]:r[k]=fmt(num(r[k])+delta)
        r.update(acquisition_balances=acq['balances'],closing_balances=close['balances'])
        r['cash']['operating']=fmt(num(r['cash']['operating'])-cost+receipts);r['cash']['closing']=fmt(num(r['cash']['closing'])-cost+receipts)
        r['parent_equity'].update(owners_profit=r['owners_profit'],closing=r['owners_equity_closing'])
        r['inventory']=serial(dict(group_carrying=cost*(1-fraction),buyer_tax_base=price*(1-fraction),eliminated_margin=margin*(1-fraction)))
        r['intragroup_tax']=serial(dict(current_expense=seller_tax+buyer_tax,current_payable=seller_tax+buyer_tax,deferred_asset=dta,deferred_income=dta,net_profit_effect=dta-seller_tax-buyer_tax))
        r['trade_profit']=serial(dict(subsidiary_contribution=seller,parent_contribution=buyer,total=increment,nci_contribution=q*seller))
        r['intragroup_cash']=serial(dict(receipts=price if settled else 0,payments=price if settled else 0,eliminated_receipts=price if settled else 0,eliminated_payments=price if settled else 0,group_net=0))
        h.need(num(r['assets_closing'])-num(r['liabilities_closing'])==num(r['equity_closing']),'report_balance')
        h.need(num(r['owners_profit'])+num(r['nci_profit'])==num(r['profit']),'profit_allocation')
        h.need(num(r['owners_equity_closing'])+num(r['nci_closing'])==num(r['equity_closing']),'equity_allocation')
        h.need(sum(num(books[e]['snapshots']['closing']['balances']['cash']) for e in ['P','S'])==num(r['cash']['closing']),'cash_report')
        return dict(result,status='conditional_upstream_worksheet',report=r,outstanding=['actual_source_and_accounting_admission','general_upstream_tax_and_costing','cross_year_upstream','ownership_fx_impairment_and_complete_notes'])
    except Exception as exc:return dict(profile=PROFILE,status='invalid',**FLAGS,reason=str(exc)[:350] or type(exc).__name__)
