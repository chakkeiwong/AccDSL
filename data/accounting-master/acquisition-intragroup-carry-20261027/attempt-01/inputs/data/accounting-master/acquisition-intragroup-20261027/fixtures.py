"""Hand-specified incremental books and independent complete-output expectations."""
from pathlib import Path
from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha256
import json
H=Path(__file__).resolve().parent;R=H.parents[2]
SAVED=json.loads((H.parent/'acquisition-consideration-20261027/attempt-01/cases.json').read_text())
def digest(x):return sha256(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
def frac(x):q=F(x);return str(q.numerator)+'/'+str(q.denominator)
def bind(b):
    b['payload']['books_sha256']=digest(b['payload']['books'])
    b['expected_payload_sha256']=digest(b['payload']);return b
def prior(election,mix):return next(x for x in SAVED if x['id']==election+'/'+mix)
def fixture(election='proportional',mix='cash',settled=False,tax='recognised'):
    old=prior(election,mix);books=deepcopy(old['result']['original_books'])
    for stage in ['opening','acquisition','closing']:
        p=books['P']['snapshots'][stage]['balances'];s=books['S']['snapshots'][stage]['balances']
        p.update(inventory='20/1',receivable='0/1',revenue='0/1',cost_of_sales='0/1',current_tax_expense='0/1',current_tax_payable='0/1')
        p['capital']=frac(F(p['capital'])-20);s.update(inventory='0/1',intragroup_payable='0/1')
    p=books['P']['snapshots']['closing']['balances'];s=books['S']['snapshots']['closing']['balances']
    p.update(inventory='0/1',receivable='0/1' if settled else '30/1',revenue='-30/1',cost_of_sales='20/1',current_tax_expense='0/1' if tax=='unresolved' else '5/2',current_tax_payable='0/1' if tax=='unresolved' else '-5/2')
    s.update(inventory='30/1',intragroup_payable='0/1' if settled else '-30/1')
    if settled:p['cash']=frac(F(p['cash'])+30);s['cash']=frac(F(s['cash'])-30)
    treatment=dict(status='unresolved',reason='Tax law, rates, recoverability and attribution not supplied') if tax=='unresolved' else dict(status='conditional',tax_base='30/1',seller_rate='1/4',buyer_rate='1/4',current_tax='5/2',recognition='stipulated_recoverable' if tax=='recognised' else 'stipulated_not_recognised',premise='Synthetic separate-taxpayer case: margin taxable now; buyer basis retained; future deduction and rates stipulated; no actual tax admission',allocation='parent_owners_stipulated_downstream')
    payload=dict(base_request=deepcopy(old['request']),base_result_sha256=digest(old['result']),source_lock_sha256=sha256((H/'predecessor-lock.json').read_bytes()).hexdigest(),books=books,books_sha256=digest(books),
        trade=dict(id='inventory-P-S-1',seller='P',buyer='S',at='2025-10-01T00:00:00Z',currency='USD',unit='currency_unit',cost='20/1',price='30/1',inventory_remaining='all',impairment='explicitly_none_synthetic'),
        settlement=dict(id='settlement-P-S-1',trade_id='inventory-P-S-1',payer='S',payee='P',at='2025-11-01T00:00:00Z',amount='30/1',currency='USD',unit='currency_unit') if settled else None,
        elimination_fraction='1/1',tax=treatment)
    return bind(dict(profile='ConditionalDownstreamInventory/1',payload=payload,expected_payload_sha256=''))
def expected(election,mix,settled,tax):
    old=deepcopy(prior(election,mix)['result']);body=fixture(election,mix,settled,tax);p=body['payload']
    known=tax!='unresolved';deferred=tax=='recognised';current='5/2' if known else '0/1'
    end='2026-01-01T00:00:00Z'
    # Explicit journal maps: no production function or balancing plug used.
    elimination=[]
    if not settled:elimination.append(dict(id='reciprocal-balance',origin='inventory-P-S-1',at=end,entries={'P.receivable':'-30/1','S.intragroup_payable':'30/1'}))
    elimination.extend([dict(id='intragroup-sale',origin='inventory-P-S-1',at=end,entries={'P.revenue':'30/1','P.cost_of_sales':'-30/1'}),
                        dict(id='unrealised-margin',origin='inventory-P-S-1',at=end,entries={'P.cost_of_sales':'10/1','S.inventory':'-10/1'})])
    if known:elimination.append(dict(id='inventory-deferred-tax',origin='Explicit supplied tax/recoverability/attribution premises',at=end,entries={'group.inventory_deferred_tax_asset':'5/2' if deferred else '0/1','P.intragroup_deferred_tax_expense':'-5/2' if deferred else '0/1'}))
    result=dict(original_books=deepcopy(p['books']),base_report=old['report'],trade=p['trade'],settlement=p['settlement'],tax=p['tax'])
    for stage in ['acquisition','closing']:
        w=deepcopy(old[stage+'_worksheet'])
        raw={entity+'.'+key:value for entity in ['P','S'] for key,value in p['books'][entity]['snapshots'][stage]['balances'].items()}
        adj=w['adjusted'];adj['P.capital']=frac(F(adj['P.capital'])-20)
        adj.update({'P.inventory':'20/1' if stage=='acquisition' else '0/1','P.receivable':'0/1','P.revenue':'0/1','P.cost_of_sales':'0/1','P.current_tax_expense':current if stage=='closing' else '0/1','P.current_tax_payable':frac(-F(current)) if stage=='closing' else '0/1','S.inventory':'20/1' if stage=='closing' else '0/1','S.intragroup_payable':'0/1'})
        if stage=='closing':
            if settled:adj['P.cash']=frac(F(adj['P.cash'])+30);adj['S.cash']=frac(F(adj['S.cash'])-30)
            if known:adj.update({'group.inventory_deferred_tax_asset':'5/2' if deferred else '0/1','P.intragroup_deferred_tax_expense':'-5/2' if deferred else '0/1'})
        balances=w['balances'];balances['parent_capital']=frac(F(balances['parent_capital'])-20);balances['inventory']='20/1'
        if stage=='closing' and known:
            balances.update(current_tax_expense='5/2',current_tax_payable='-5/2')
            if deferred:balances.update(inventory_deferred_tax_asset='5/2',intragroup_deferred_tax_expense='-5/2')
        w.update(raw=raw,adjusted=adj,balances=balances)
        if stage=='closing':w['journals']+=elimination
        result[stage+'_worksheet']=w
    result['intragroup_cash_origins']=[] if not settled else [
        dict(id='settlement-P-S-1/receipt',entity='P',counterparty='S',at='2025-11-01T00:00:00Z',amount='30/1',classification='operating',elimination='-30/1'),
        dict(id='settlement-P-S-1/payment',entity='S',counterparty='P',at='2025-11-01T00:00:00Z',amount='-30/1',classification='operating',elimination='30/1')]
    if known:
        r=deepcopy(old['report']);net=F(0) if deferred else F(-5,2)
        r['acquisition_balances']=result['acquisition_worksheet']['balances'];r['closing_balances']=result['closing_worksheet']['balances']
        # Independent absolute totals for the nine base scenarios, with explicit
        # retained inventory/tax effects from the stipulated case.
        assets={'proportional':{'cash':F(1629,4),'equity':F(2109,4),'mixed':F(1909,4)},'fair_value':{'cash':F(837,2),'equity':F(1077,2),'mixed':F(977,2)},'none':{'cash':F(757,2),'equity':F(997,2),'mixed':F(897,2)}}
        owners={'proportional':{'cash':F(2749,8),'equity':F(3709,8),'mixed':F(3309,8)},'fair_value':{'cash':F(2749,8),'equity':F(3709,8),'mixed':F(3309,8)},'none':{'cash':F(703,2),'equity':F(943,2),'mixed':F(843,2)}}
        equity={'proportional':{'cash':F(1521,4),'equity':F(2001,4),'mixed':F(1801,4)},'fair_value':{'cash':F(783,2),'equity':F(1023,2),'mixed':F(923,2)},'none':{'cash':F(703,2),'equity':F(943,2),'mixed':F(843,2)}}
        r.update(profit=frac(F(63,2)+net),owners_profit=frac((F(63,2) if election=='none' else F(189,8))+net),owners_equity_closing=frac(owners[election][mix]+net),assets_closing=frac(assets[election][mix]+net),liabilities_closing='27/1',equity_closing=frac(equity[election][mix]+net))
        r['parent_equity'].update(opening='320/1',owners_profit=r['owners_profit'],closing=r['owners_equity_closing'])
        r['inventory']=dict(group_carrying='20/1',buyer_tax_base='30/1',eliminated_margin='10/1')
        r['intragroup_tax']=dict(current_expense='5/2',current_payable='5/2',deferred_asset='5/2' if deferred else '0/1',deferred_income='5/2' if deferred else '0/1',net_profit_effect=frac(net))
        r['intragroup_cash']={k:('30/1' if settled else '0/1') for k in ['receipts','payments','eliminated_receipts','eliminated_payments']};r['intragroup_cash']['group_net']='0/1'
        result['report']=r
    return result
