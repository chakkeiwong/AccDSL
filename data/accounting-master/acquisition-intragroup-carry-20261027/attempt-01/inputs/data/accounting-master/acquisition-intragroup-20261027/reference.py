"""Conditional downstream transfer: exact books, full elimination, explicit tax."""
from pathlib import Path
from hashlib import sha256
from fractions import Fraction as F
from copy import deepcopy
import importlib.util,json
H=Path(__file__).resolve().parent;R=H.parents[2];S=H.parent/'acquisition-consideration-20261027'
spec=importlib.util.spec_from_file_location('intragroup_base',S/'reference.py')
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
h=base.h;num=base.number;fmt=base.fmt;serial=base.serial
PROFILE='ConditionalDownstreamInventory/1';FLAGS=base.FLAGS
EXTRA={'P':['inventory','receivable','revenue','cost_of_sales','current_tax_expense','current_tax_payable'],
       'S':['inventory','intragroup_payable']}
def report(body):
    try:
        h.need(len(json.dumps(body,allow_nan=False))<650000,'request_size')
        h.fields(body,['profile','payload','expected_payload_sha256'],'envelope')
        h.need(body['profile']==PROFILE,'profile');p=body['payload']
        h.need(h.digest(p)==body['expected_payload_sha256'],'payload_binding')
        h.fields(p,['base_request','base_result_sha256','source_lock_sha256','books','books_sha256','trade','settlement','elimination_fraction','tax'],'payload')
        lock=H/'predecessor-lock.json'
        h.need(sha256(lock.read_bytes()).hexdigest()==p['source_lock_sha256'],'source_lock_binding')
        for name,d in json.loads(lock.read_text()).items():
            h.need(sha256((R/name).read_bytes()).hexdigest()==d,'protected_dependency:'+name)
        original=base.report(p['base_request'])
        h.need(original['status']=='conditional_worksheet','base:'+original.get('reason',original['status']))
        h.need(h.digest(original)==p['base_result_sha256'],'base_result_binding')
        sp=p['base_request']['payload']['symbolic_request']['payload']
        acquisition=sp['acquisition']['at'];end=sp['scope_request']['history_request']['interval']['end_exclusive']
        currency=sp['acquisition']['currency'];unit=sp['acquisition']['unit']
        t=p['trade'];h.fields(t,['id','seller','buyer','at','currency','unit','cost','price','inventory_remaining','impairment'],'trade')
        h.need(t['id']=='inventory-P-S-1','trade_identity')
        h.need(t['seller']=='P' and t['buyer']=='S','downstream_only')
        h.need(h.moment(acquisition)<h.moment(t['at'])<h.moment(end),'post_control_trade')
        h.need(t['currency']==currency and t['unit']==unit,'trade_units')
        cost=num(t['cost']);price=num(t['price']);margin=price-cost
        h.need(margin>=0,'loss_requires_impairment_method')
        h.need(cost==20 and price==30,'fixed_lot_amounts')
        h.need(t['inventory_remaining']=='all' and t['impairment']=='explicitly_none_synthetic','inventory_scope')
        h.need(num(p['elimination_fraction'])==1,'full_elimination_required')
        settled=p['settlement'] is not None
        if settled:
            s=p['settlement'];h.fields(s,['id','trade_id','payer','payee','at','amount','currency','unit'],'settlement')
            h.need(s['id']=='settlement-P-S-1' and s['trade_id']==t['id'],'settlement_pair')
            h.need(s['payer']=='S' and s['payee']=='P','settlement_parties')
            h.need(h.moment(t['at'])<=h.moment(s['at'])<h.moment(end),'settlement_date')
            h.need(num(s['amount'])==price,'settlement_amount')
            h.need(s['currency']==currency and s['unit']==unit,'settlement_units')
        tax=p['tax'];h.need(type(tax) is dict and 'status' in tax,'tax_disposition_required')
        known=tax['status']=='conditional'
        if known:
            h.fields(tax,['status','tax_base','seller_rate','buyer_rate','current_tax','recognition','premise','allocation'],'tax')
            h.text(tax['premise']);h.need(tax['allocation']=='parent_owners_stipulated_downstream','tax_allocation_required')
            taxbase=num(tax['tax_base']);rs=num(tax['seller_rate']);rb=num(tax['buyer_rate']);current=num(tax['current_tax'])
            h.need(taxbase==price and 0<=rs<=1 and 0<=rb<=1,'tax_basis_or_rate')
            h.need(current==margin*rs,'current_tax_binding')
            h.need(tax['recognition'] in ['stipulated_recoverable','stipulated_not_recognised'],'recognition_disposition')
            deferred=(taxbase-cost)*rb if tax['recognition']=='stipulated_recoverable' else F(0)
        else:
            h.fields(tax,['status','reason'],'tax');h.need(tax['status']=='unresolved','tax_disposition_required');h.text(tax['reason'])
            current=deferred=F(0) # Arithmetic-only pretax branch; no report is produced.
        books=p['books'];h.need(h.digest(books)==p['books_sha256'],'books_binding')
        expected=deepcopy(original['original_books'])
        for entity in ['P','S']:
            for stage in ['opening','acquisition','closing']:
                balances=expected[entity]['snapshots'][stage]['balances']
                balances.update({key:'0/1' for key in EXTRA[entity]})
                if entity=='P':
                    balances['inventory']=fmt(cost);balances['capital']=fmt(num(balances['capital'])-cost)
        pc=expected['P']['snapshots']['closing']['balances'];sc=expected['S']['snapshots']['closing']['balances']
        pc.update(inventory='0/1',revenue=fmt(-price),cost_of_sales=fmt(cost),receivable=fmt(0 if settled else price),current_tax_expense=fmt(current),current_tax_payable=fmt(-current))
        sc.update(inventory=fmt(price),intragroup_payable=fmt(0 if settled else -price))
        if settled:pc['cash']=fmt(num(pc['cash'])+price);sc['cash']=fmt(num(sc['cash'])-price)
        h.need(books==expected,'complete_legal_progression')
        for entity in ['P','S']:
            for stage in ['opening','acquisition','closing']:
                balances=books[entity]['snapshots'][stage]['balances']
                h.need(sum(num(x) for x in balances.values())==0,'legal_balance')
                h.need(num(balances['cash'])>=0,'negative_cash_requires_method')
        def journal(id,entries,origin):
            h.need(sum(entries.values())==0,'journal_balance')
            return dict(id=id,origin=origin,at=end,entries=serial(entries))
        eliminations=[]
        if not settled:eliminations.append(journal('reciprocal-balance',{'P.receivable':-price,'S.intragroup_payable':price},t['id']))
        eliminations.extend([journal('intragroup-sale',{'P.revenue':price,'P.cost_of_sales':-price},t['id']),
                             journal('unrealised-margin',{'P.cost_of_sales':margin,'S.inventory':-margin},t['id'])])
        if known:eliminations.append(journal('inventory-deferred-tax',{'group.inventory_deferred_tax_asset':deferred,'P.intragroup_deferred_tax_expense':-deferred},'Explicit supplied tax/recoverability/attribution premises'))
        def worksheet(stage):
            raw={entity+'.'+key:num(v) for entity in ['P','S'] for key,v in books[entity]['snapshots'][stage]['balances'].items()}
            entries=deepcopy(original[stage+'_worksheet']['journals'])+(deepcopy(eliminations) if stage=='closing' else [])
            adjusted=deepcopy(raw)
            for entry in entries:
                for key,value in entry['entries'].items():adjusted[key]=adjusted.get(key,F(0))+num(value)
            h.need(sum(adjusted.values())==0,'worksheet_balance')
            aggregate={}
            for key,value in adjusted.items():
                if not value:continue
                entity,name=key.split('.');name='parent_capital' if entity=='P' and name=='capital' else name
                aggregate[name]=aggregate.get(name,F(0))+value
            aggregate={k:v for k,v in aggregate.items() if v};aggregate.setdefault('nci',F(0))
            return dict(raw=serial(raw),journals=entries,adjusted=serial(adjusted),balances=serial(aggregate))
        acquisition_ws=worksheet('acquisition');closing_ws=worksheet('closing')
        origins=[]
        if settled:
            origins=[dict(id=p['settlement']['id']+'/receipt',entity='P',counterparty='S',at=p['settlement']['at'],amount=fmt(price),classification='operating',elimination=fmt(-price)),
                     dict(id=p['settlement']['id']+'/payment',entity='S',counterparty='P',at=p['settlement']['at'],amount=fmt(-price),classification='operating',elimination=fmt(price))]
        result=dict(profile=PROFILE,**FLAGS,request_sha256=h.digest(body),base_result_sha256=h.digest(original),original_books=deepcopy(books),base_report=deepcopy(original['report']),
                    acquisition_worksheet=acquisition_ws,closing_worksheet=closing_ws,trade=deepcopy(t),settlement=deepcopy(p['settlement']),tax=deepcopy(tax),intragroup_cash_origins=origins)
        if not known:
            result.update(status='tax_method_required',outstanding=['current_tax','tax_base_and_rates','recoverability','owner_attribution','actual_authority_and_source_admission'])
            return result
        r=deepcopy(original['report']);nettax=deferred-current
        r.update(acquisition_balances=acquisition_ws['balances'],closing_balances=closing_ws['balances'])
        for key,delta in [('profit',nettax),('owners_profit',nettax),('owners_equity_closing',cost+nettax),('assets_closing',cost+deferred),('liabilities_closing',current),('equity_closing',cost+nettax)]:r[key]=fmt(num(r[key])+delta)
        r['parent_equity']['opening']=fmt(num(r['parent_equity']['opening'])+cost)
        r['parent_equity']['owners_profit']=r['owners_profit'];r['parent_equity']['closing']=r['owners_equity_closing']
        r['inventory']=serial(dict(group_carrying=cost,buyer_tax_base=taxbase,eliminated_margin=margin))
        r['intragroup_tax']=serial(dict(current_expense=current,current_payable=current,deferred_asset=deferred,deferred_income=deferred,net_profit_effect=nettax))
        r['intragroup_cash']=serial(dict(receipts=price if settled else 0,payments=price if settled else 0,eliminated_receipts=price if settled else 0,eliminated_payments=price if settled else 0,group_net=0))
        h.need(num(r['assets_closing'])-num(r['liabilities_closing'])==num(r['equity_closing']),'group_equity')
        h.need(num(r['owners_profit'])+num(r['nci_profit'])==num(r['profit']),'profit_attribution')
        h.need(num(r['owners_equity_closing'])+num(r['nci_closing'])==num(r['equity_closing']),'equity_attribution')
        h.need(num(pc['cash'])+num(sc['cash'])==num(r['cash']['closing']),'group_cash')
        result.update(status='conditional_intragroup_worksheet',report=r,outstanding=['source_and_accounting_admission','general_tax_and_attribution','upstream_and_external_resale','loss_impairment_ownership_fx','general_items_and_notes'])
        return result
    except Exception as exc:return dict(profile=PROFILE,status='invalid',**FLAGS,reason=str(exc)[:350] or type(exc).__name__)
