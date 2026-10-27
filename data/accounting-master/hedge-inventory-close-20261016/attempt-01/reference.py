"""Replay a source-bound hedge, then purchase, settle, basis-adjust and sell."""
from copy import deepcopy
from datetime import date
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
LOCK=json.loads((OUT/'input-lock.json').read_text())['files']
HEDGE_PATH=ROOT/'data/accounting-master/repeated-rebalancing-20261016/reference.py'
FINDINGS={'all_designated_units_received','inventory_recognition_satisfied','acquisition_costs_complete',
    'nrv_supports_adjusted_cost','hedge_settlement_complete','settlement_at_carrying_no_fees',
    'early_settlement_permitted','no_further_valuation_movement','all_units_sold','sale_recognition_satisfied',
    'no_other_cash_or_earnings','pretax_scope'}
ACCOUNTS=('cash','inventory','derivative','cf_reserve','gains','capital','revenue','cogs')


class Refusal(Exception):
    def __init__(self,status,reason):self.status,self.reason=status,reason


def need(ok,reason,status='rejected'):
    if not ok:raise Refusal(status,reason)


def rational(value):
    need(isinstance(value,str) and re.fullmatch(r'(0|-?[1-9][0-9]*)(/[1-9][0-9]*)?',value),'rational_encoding')
    q=Q(value);need(str(q)==value,'rational_encoding');return q


def day(value):
    try:
        need(isinstance(value,str),'date_encoding');d=date.fromisoformat(value);need(d.isoformat()==value,'date_encoding');return d
    except ValueError:raise Refusal('rejected','date_encoding')


def encode(value):
    if isinstance(value,Q):return str(value)
    if isinstance(value,dict):return {k:encode(v) for k,v in value.items()}
    if isinstance(value,list):return [encode(v) for v in value]
    return value


def calculate(request,resolve_bytes=None):
    result=dict(wire='HedgeInventoryClose/1',status='rejected',reason=None,hedge=None,report=None,
                stages=[],journals=[],flows=[],mutations=[])
    try:
        need(isinstance(request,dict) and set(request)=={'wire','operation','hedge','context','opening_cash','purchase','settlement','sale','findings'},'request_shape')
        need(request['wire']=='HedgeInventoryClose/1' and request['operation']=='report','operation')
        findings=request['findings'];need(isinstance(findings,dict) and set(findings)==FINDINGS,'findings_shape')
        for key in sorted(FINDINGS):
            need(findings[key] is not None,'missing_'+key,'unresolved')
            need(type(findings[key]) is bool,'finding_type')
            need(findings[key],'finding_'+key,'unsupported')
        reader=resolve_bytes or (lambda p:p.read_bytes())
        for item in LOCK:
            try:payload=reader(ROOT/item['path'])
            except OSError:raise Refusal('unresolved','input_bytes_missing')
            need(hashlib.sha256(payload).hexdigest()==item['sha256'],'input_bytes_changed')
        spec=importlib.util.spec_from_file_location('inventory_close_hedge',HEDGE_PATH)
        hedge_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(hedge_module)
        hedge=hedge_module.calculate(request['hedge'])
        need(hedge['status']=='conditional_complete','hedge_'+str(hedge['reason']),hedge['status'])
        s=hedge['state']
        need(s['context']==request['context'],'context_mismatch')
        need(s['last_operation']=='measure','terminal_measurement_required')
        for key,fields in [('purchase',{'date','quantity','unit_price','supplier_cash'}),('settlement',{'date','cash'}),('sale',{'date','quantity','cash'})]:
            need(isinstance(request[key],dict) and set(request[key])==fields,key+'_shape')
        p,settle,sale=(request[k] for k in ('purchase','settlement','sale'))
        need(p['date']==settle['date']==s['date'],'terminal_date_mismatch')
        need(day(sale['date'])>day(p['date']),'sale_chronology')
        quantity=sum(Q(x['quantity']) for x in s['layers'])
        need(rational(p['quantity'])==rational(sale['quantity'])==quantity,'purchase_sale_population')
        price=rational(p['unit_price']);need(price==Q(s['price']),'purchase_price')
        C=rational(p['supplier_cash']);need(C==quantity*price and C>=0,'supplier_cost')
        D,R,I=(Q(s[k]) for k in ('D','reserve','profit'))
        need(rational(settle['cash'])==D,'settlement_carrying_value')
        opening=rational(request['opening_cash']);S=rational(sale['cash'])
        need(opening>=0 and S>=0,'negative_cash_input')
        adjusted=C-R;need(adjusted>=0,'negative_inventory_method','unsupported')
        books={k:Q(0) for k in ACCOUNTS}
        books.update(cash=opening,capital=-opening,derivative=D,cf_reserve=-R,gains=-I)
        need(sum(books.values())==0,'opening_books')
        stages=[];journals=[];flows=[]
        operations=[('purchase',p['date'],dict(inventory=C,cash=-C),('supplier',-C)),
            ('settle',settle['date'],dict(cash=D,derivative=-D),('hedge_settlement',D)),
            ('basis',p['date'],dict(cf_reserve=R,inventory=-R),None),
            ('sale',sale['date'],dict(cash=S,revenue=-S,cogs=adjusted,inventory=-adjusted),('inventory_sale',S))]
        before_sale=None
        for operation,when,entries,flow in operations:
            need(sum(entries.values())==0,'journal_balance')
            for key,value in entries.items():books[key]+=value
            need(sum(books.values())==0,'book_balance')
            need(books['cash']>=0,'funding_required','unsupported')
            journals.append(dict(operation=operation,date=when,entries=entries))
            if flow:flows.append(dict(origin=flow[0],activity='operating',date=when,amount=flow[1]))
            profit=-(books['gains']+books['revenue']+books['cogs'])
            stages.append(dict(operation=operation,date=when,books=deepcopy(books),pretax_profit=profit,
                pretax_equity=-books['capital']-books['cf_reserve']+profit))
            if operation=='basis':before_sale=deepcopy(stages[-1])
        profit=-(books['gains']+books['revenue']+books['cogs'])
        receipts=sum(max(Q(0),x['amount']) for x in flows)
        payments=-sum(min(Q(0),x['amount']) for x in flows)
        need(books['cash']-opening==receipts-payments,'gross_cash_bridge')
        need(books['cash']+books['inventory']==opening+profit,'final_equity_bridge')
        report=dict(quantity=quantity,supplier_cost=C,derivative_settlement=D,original_reserve=R,original_ineffectiveness=I,
            inventory_after_basis=before_sale['books']['inventory'],cash_before_sale=before_sale['books']['cash'],
            profit_before_sale=before_sale['pretax_profit'],equity_before_sale=before_sale['pretax_equity'],
            cost_of_sales=books['cogs'],sale_revenue=-books['revenue'],closing_cash=books['cash'],
            closing_inventory=books['inventory'],closing_derivative=books['derivative'],closing_reserve=-books['cf_reserve'],
            cumulative_pretax_profit=profit,closing_pretax_equity=opening+profit,operating_receipts=receipts,
            operating_payments=payments,net_cash=receipts-payments,oci_reclassification=Q(0),direct_basis_reserve_change=-R,
            basis_profit=Q(0),tax='not_calculated')
        result.update(status='conditional_complete',hedge=hedge,report=encode(report),stages=encode(stages),journals=encode(journals),flows=encode(flows))
    except Refusal as exc:result.update(status=exc.status,reason=exc.reason)
    return result
