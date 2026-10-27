"""Complete stipulated legal journals and same-period downstream realisation."""
from pathlib import Path
from hashlib import sha256
from fractions import Fraction as F
from copy import deepcopy
import importlib.util,json
H=Path(__file__).resolve().parent;R=H.parents[2];S=H.parent/'acquisition-intragroup-20261027'
spec=importlib.util.spec_from_file_location('realisation_base',S/'reference.py');base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
h=base.h;num=base.num;fmt=base.fmt;serial=base.serial;FLAGS=base.FLAGS
PROFILE='ConditionalDownstreamRealisation/1'
CALENDAR=dict(precontrol_receipt='2025-06-29T00:00:00Z',precontrol_close='2025-06-30T00:00:00Z',operating_receipt='2025-08-01T00:00:00Z',depreciation='2025-12-31T00:00:00Z',tax='2025-12-31T00:00:00Z')
def report(body):
    try:
        h.need(len(json.dumps(body,allow_nan=False))<900000,'request_size')
        h.fields(body,['profile','payload','expected_payload_sha256'],'envelope');h.need(body['profile']==PROFILE,'profile');p=body['payload']
        h.need(h.digest(p)==body['expected_payload_sha256'],'payload_binding')
        h.fields(p,['predecessor_request','predecessor_result_sha256','source_lock_sha256','external_sale','event_calendar','history_premise','books','books_sha256'],'payload')
        lock=H/'predecessor-lock.json';h.need(sha256(lock.read_bytes()).hexdigest()==p['source_lock_sha256'],'source_lock_binding')
        for name,d in json.loads(lock.read_text()).items():h.need(sha256((R/name).read_bytes()).hexdigest()==d,'protected_dependency:'+name)
        b=p['predecessor_request'];prior=base.report(b)
        h.need(prior['status'] in ['conditional_intragroup_worksheet','tax_method_required'],'predecessor:'+prior.get('reason',prior['status']))
        h.need(h.digest(prior)==p['predecessor_result_sha256'],'predecessor_binding')
        bp=b['payload'];sp=bp['base_request']['payload']['symbolic_request']['payload'];ownership=num(sp['ownership']['fraction']);q=1-ownership
        h.need(bp['trade']['at']=='2025-10-01T00:00:00Z' and (bp['settlement'] is None or bp['settlement']['at']=='2025-11-01T00:00:00Z'),'selected_transfer_calendar')
        tax=bp['tax'];known=tax['status']=='conditional';recognised=known and tax['recognition']=='stipulated_recoverable'
        if known:h.need(num(tax['seller_rate'])==F(1,4) and num(tax['buyer_rate'])==F(1,4),'selected_tax_rates')
        h.need(p['event_calendar']==CALENDAR,'selected_event_calendar')
        h.need(p['history_premise']=='Explicit synthetic dated events; balances do not establish actual history','history_premise')
        sale=p['external_sale'];h.fields(sale,['id','seller','customer','at','currency','unit','fraction','receipts','cost','recognition'],'external_sale')
        h.need(sale['id']=='external-S-X-1' and sale['seller']=='S' and sale['customer']=='X','external_parties')
        end=sp['scope_request']['history_request']['interval']['end_exclusive'];at=sale['at']
        h.need(h.moment(bp['trade']['at'])<h.moment(at)<h.moment(end),'external_date')
        h.need(at=='2025-12-01T00:00:00Z','selected_external_calendar')
        h.need(sale['currency']==sp['acquisition']['currency'] and sale['unit']==sp['acquisition']['unit'],'external_units')
        fraction=num(sale['fraction']);h.need(fraction in [F(0),F(1,2),F(1)],'selected_resale_fraction')
        receipts=num(sale['receipts']);cost=num(sale['cost'])
        h.need(receipts==40*fraction and cost==30*fraction,'external_amounts')
        h.need(sale['recognition']=='Stipulated customer contract, control transfer and fixed price; no returns or other obligations','revenue_premise')
        current=F(5,2)*fraction if known else F(0);dta=F(5,2)*(1-fraction) if recognised else F(0)
        books=deepcopy(prior['original_books'])
        for stage in ['opening','acquisition','closing']:
            books['S']['snapshots'][stage]['balances'].update(merchandise_revenue='0/1',cost_of_sales='0/1',current_tax_expense='0/1',current_tax_payable='0/1')
        sc=books['S']['snapshots']['closing']['balances'];sc['cash']=fmt(num(sc['cash'])+receipts);sc['inventory']=fmt(30*(1-fraction))
        sc.update(merchandise_revenue=fmt(-receipts),cost_of_sales=fmt(cost),current_tax_expense=fmt(current),current_tax_payable=fmt(-current))
        h.need(h.digest(p['books'])==p['books_sha256'],'books_binding');h.need(p['books']==books,'complete_legal_books')
        journals=[]
        def add(id,entity,when,entries,origin):
            h.need(sum(entries.values())==0,'legal_journal_balance')
            journals.append(dict(id=id,entity=entity,at=when,origin=origin,entries=serial(entries)))
        for entity in ['P','S']:
            snap=books[entity]['snapshots']['opening'];add('opening-'+entity,entity,snap['at'],{k:num(v) for k,v in snap['balances'].items()},'Supplied opening trial balance; no inferred capital event')
        add('precontrol-receipt','S',CALENDAR['precontrol_receipt'],dict(cash=F(20),revenue=F(-20)),'Stipulated pre-control cash sale')
        add('precontrol-close','S',CALENDAR['precontrol_close'],dict(revenue=F(20),retained_pre=F(-20)),'Stipulated interim profit close')
        consideration=bp['base_request']['payload']['consideration'];cash=num(consideration['cash']);equity=num(consideration['new_parent_equity'])
        add('parent-acquisition','P',sp['acquisition']['at'],dict(cash=-cash,investment=cash+equity,capital=-equity),'Supplied acquisition consideration components')
        add('controlled-receipt','S',CALENDAR['operating_receipt'],dict(cash=F(40),revenue=F(-40)),'Stipulated post-control operating receipt')
        add('internal-sale-parent','P',bp['trade']['at'],dict(receivable=F(30),revenue=F(-30),cost_of_sales=F(20),inventory=F(-20)),bp['trade']['id'])
        add('internal-purchase-subsidiary','S',bp['trade']['at'],dict(inventory=F(30),intragroup_payable=F(-30)),bp['trade']['id'])
        if bp['settlement']:
            s=bp['settlement'];add('internal-settlement-parent','P',s['at'],dict(cash=F(30),receivable=F(-30)),s['id'])
            add('internal-settlement-subsidiary','S',s['at'],dict(cash=F(-30),intragroup_payable=F(30)),s['id'])
        if fraction:add('external-sale','S',at,dict(cash=receipts,merchandise_revenue=-receipts,cost_of_sales=cost,inventory=-cost),sale['id'])
        add('legal-depreciation','S',CALENDAR['depreciation'],dict(depreciation=F(7),equipment=F(-7)),'Supplied legal equipment expense')
        if known:
            add('seller-current-tax','P',CALENDAR['tax'],dict(current_tax_expense=F(5,2),current_tax_payable=F(-5,2)),'Supplied seller tax on internal margin')
            add('buyer-current-tax','S',CALENDAR['tax'],dict(current_tax_expense=current,current_tax_payable=-current),'Supplied buyer tax on external trading profit')
        journals.sort(key=lambda x:(x['at'],x['id']))
        for entity in ['P','S']:
            for stage,snapshot in books[entity]['snapshots'].items():
                state={k:F(0) for k in snapshot['balances']}
                for event in journals:
                    if event['entity']==entity and h.moment(event['at'])<=h.moment(snapshot['at']):
                        for key,value in event['entries'].items():state[key]+=num(value)
                h.need(serial(state)==snapshot['balances'],'journal_stage:'+entity+'/'+stage)
        # Existing acquired-asset basis remains unchanged; only transfer effects vary.
        acquisition=deepcopy(prior['acquisition_worksheet']);closing=deepcopy(prior['closing_worksheet'])
        for stage,w in [('acquisition',acquisition),('closing',closing)]:
            w['raw']={entity+'.'+key:value for entity in ['P','S'] for key,value in books[entity]['snapshots'][stage]['balances'].items()}
            if stage=='closing':
                for entry in w['journals']:
                    if entry['id']=='unrealised-margin':entry['entries']=serial({'P.cost_of_sales':10*(1-fraction),'S.inventory':-10*(1-fraction)})
                    if entry['id']=='inventory-deferred-tax':entry['entries']=serial({'group.inventory_deferred_tax_asset':dta,'P.intragroup_deferred_tax_expense':-dta})
            adjusted={k:num(v) for k,v in w['raw'].items()}
            for entry in w['journals']:
                for key,value in entry['entries'].items():adjusted[key]=adjusted.get(key,F(0))+num(value)
            h.need(sum(adjusted.values())==0,'adjusted_balance')
            balances={}
            for key,value in adjusted.items():
                if not value:continue
                entity,name=key.split('.');name='parent_capital' if entity=='P' and name=='capital' else name
                balances[name]=balances.get(name,F(0))+value
            balances={k:v for k,v in balances.items() if v};balances.setdefault('nci',F(0))
            w.update(adjusted=serial(adjusted),balances=serial(balances))
        external_cash=[] if not fraction else [dict(id=sale['id']+'/receipt',entity='S',counterparty='X',at=at,amount=fmt(receipts),classification='operating',elimination='0/1')]
        result=dict(profile=PROFILE,**FLAGS,request_sha256=h.digest(body),predecessor_result_sha256=h.digest(prior),original_books=deepcopy(books),legal_journals=journals,
                    acquisition_worksheet=acquisition,closing_worksheet=closing,intragroup_cash_origins=deepcopy(prior['intragroup_cash_origins']),external_cash_origins=external_cash,tax=deepcopy(tax),external_sale=deepcopy(sale))
        if not known:return dict(result,status='tax_method_required',outstanding=['seller_and_buyer_tax','tax_base_rates_recoverability_attribution','source_and_accounting_admission'])
        r=deepcopy(prior['report']);old_dta=F(5,2) if recognised else F(0);dta_change=dta-old_dta
        buyerprofit=receipts-cost-current;parentprofit=10*fraction+dta_change;profit=buyerprofit+parentprofit
        for key,delta in [('profit',profit),('owners_profit',parentprofit+ownership*buyerprofit),('nci_profit',q*buyerprofit),('nci_closing',q*buyerprofit),('owners_equity_closing',parentprofit+ownership*buyerprofit),('assets_closing',receipts-20*fraction+dta_change),('liabilities_closing',current),('equity_closing',profit)]:r[key]=fmt(num(r[key])+delta)
        r['acquisition_balances']=acquisition['balances'];r['closing_balances']=closing['balances']
        r['cash']['operating']=fmt(num(r['cash']['operating'])+receipts);r['cash']['closing']=fmt(num(r['cash']['closing'])+receipts)
        r['parent_equity'].update(owners_profit=r['owners_profit'],closing=r['owners_equity_closing'])
        r['inventory']=serial(dict(group_carrying=20*(1-fraction),buyer_tax_base=30*(1-fraction),eliminated_margin=10*(1-fraction)))
        r['intragroup_tax']=serial(dict(current_expense=F(5,2)+current,current_payable=F(5,2)+current,deferred_asset=dta,deferred_income=dta,net_profit_effect=dta-F(5,2)-current))
        r['external_trade']=serial(dict(fraction=fraction,receipts=receipts,legal_cost=cost,group_cost=20*fraction,group_pretax_profit=20*fraction,buyer_after_tax_profit=buyerprofit))
        h.need(num(r['owners_profit'])+num(r['nci_profit'])==num(r['profit']),'profit_allocation')
        h.need(num(r['assets_closing'])-num(r['liabilities_closing'])==num(r['equity_closing']),'report_balance')
        h.need(num(r['owners_equity_closing'])+num(r['nci_closing'])==num(r['equity_closing']),'equity_allocation')
        h.need(sum(num(books[e]['snapshots']['closing']['balances']['cash']) for e in ['P','S'])==num(r['cash']['closing']),'cash_report')
        return dict(result,status='conditional_realisation_worksheet',report=r,outstanding=['actual_source_revenue_tax_admission','upstream_and_cross_year','multi_lot_costing_fx_ownership','actor_availability_and_complete_notes'])
    except Exception as exc:return dict(profile=PROFILE,status='invalid',**FLAGS,reason=str(exc)[:350] or type(exc).__name__)
