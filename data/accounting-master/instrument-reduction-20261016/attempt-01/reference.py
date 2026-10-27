"""Exact designated-tenure histories, prospective reductions and gross closing."""
from copy import deepcopy
from datetime import date
from fractions import Fraction as Q
from pathlib import Path
import hashlib
import json

OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
SOURCE='docs/design/research/p08-v3-preparation/eu-2023-1803-original.txt'
CONTEXT=dict(entity='P',book='P-separate',currency='CU',quantity_unit='unit',price_unit='CU/unit',
    rule='EU2023/1803-original-IFRS9',relationship='hedge-components',designation_date='2025-01-01',maturity_date='2025-12-31')
FINDINGS={'eligible_external_nonoption_instruments','zero_initial_cost_and_value','whole_instrument_proportions','unchanged_hedged_item','no_other_cash_or_earnings','pretax_only'}
MEASURE={'complete_values','zero_discount_admitted','forecast_highly_probable','economic_relationship','credit_risk_not_dominant','ratio_eligible','reserve_loss_recoverable'}
REDUCE={'objective_unchanged','structural_ratio_change','documentation_updated','remaining_ratio_eligible','all_instruments_retained'}
SETTLE={'all_forecast_units_received','inventory_recognition','complete_costs','nrv_supported','no_fees','valuation_unchanged'}

class Refusal(Exception):
    def __init__(self,reason,status='rejected'):self.reason=reason;self.status=status
def fail(reason,status='rejected'):raise Refusal(reason,status)
def shape(x,keys,reason):
    if not isinstance(x,dict) or set(x)!=set(keys):fail(reason)
def num(x,key,signed=False,positive=False):
    if x is None:fail('missing_'+key,'unresolved')
    try:
        if not isinstance(x,str):raise ValueError()
        v=Q(x)
        if str(v)!=x:raise ValueError()
    except (ValueError,ZeroDivisionError):fail('number_encoding')
    if not signed and v<0 or positive and v<=0:fail('number_domain')
    return v
def identity(x):
    if not isinstance(x,str) or not x.strip() or x!=x.strip():fail('identity')
    return x
def findings(x,keys):
    shape(x,keys,'finding_shape')
    for key in sorted(keys):
        if x[key] is None:fail('missing_'+key,'unresolved')
        if x[key] is False:fail('outside_'+key,'unsupported')
        if x[key] is not True:fail('finding_encoding')
def encode(x):
    if isinstance(x,Q):return str(x)
    if isinstance(x,list):return [encode(v) for v in x]
    if isinstance(x,dict):return {k:encode(v) for k,v in x.items()}
    return x

def calculate(r,reader=lambda p:p.read_bytes()):
    empty=dict(state=None,stages=[],journals=[],cash_flows=[],closing=None,mutations=[])
    try:
        lock={x['path']:x['sha256'] for x in json.loads((OUT/'input-lock.json').read_text())['files']}
        try:raw=reader(ROOT/SOURCE)
        except FileNotFoundError:fail('source_unavailable','unresolved')
        if hashlib.sha256(raw).hexdigest()!=lock[SOURCE]:fail('source_changed')
        shape(r,{'wire','operation','context','opening_cash','findings','item','instruments','events'},'request_shape')
        if r['wire']!='InstrumentReduction/1':fail('wire')
        if r['operation']!='report':fail('report_only')
        if r['context']!=CONTEXT:fail('context')
        findings(r['findings'],FINDINGS)
        cash=num(r['opening_cash'],'opening_cash');capital=cash
        shape(r['item'],{'id','quantity','origin_price'},'item_shape');identity(r['item']['id'])
        quantity=num(r['item']['quantity'],'item_quantity',positive=True);origin=num(r['item']['origin_price'],'origin_price',positive=True)
        if not isinstance(r['instruments'],list) or len(r['instruments'])!=2:fail('two_instruments_required','unsupported')
        instruments={}
        for row in r['instruments']:
            shape(row,{'id','quantity'},'instrument_shape');id=identity(row['id'])
            if id in instruments:fail('duplicate_instrument')
            instruments[id]=dict(quantity=num(row['quantity'],'instrument_quantity',positive=True),fraction=Q(1),value=Q(0),settled_cash=Q(0),G=Q(0),U=Q(0),stops=[])
        instruments=dict(sorted(instruments.items()))
        if not isinstance(r['events'],list) or not r['events']:fail('events_shape')
        books={'cash':cash,'capital':-capital,'inventory':Q(0),'cf_reserve':Q(0),'earnings':Q(0)}
        for id in instruments:books['derivative:'+id]=Q(0)
        stages=[];journals=[];flows=[];seen=set();last_date=CONTEXT['designation_date'];last_operation=None
        price=origin;H=Q(0);reserve=Q(0);profit=Q(0);closed=False;closing=None
        def journal(event,entries):
            if sum(entries.values(),Q(0))!=0:fail('journal_balance')
            if any(entries.values()):
                for key,v in entries.items():books[key]+=v
                journals.append(dict(event=event['id'],date=event['date'],entries=entries))
        def state():
            return deepcopy(dict(item=dict(id=r['item']['id'],quantity=quantity,origin_price=origin,designation_date=CONTEXT['designation_date']),
                instruments=instruments,G=sum((x['G'] for x in instruments.values()),Q(0)),U=sum((x['U'] for x in instruments.values()),Q(0)),H=H,
                derivative=sum((x['value'] for x in instruments.values()),Q(0)),derivative_assets=sum((max(x['value'],Q(0)) for x in instruments.values()),Q(0)),
                derivative_liabilities=sum((max(-x['value'],Q(0)) for x in instruments.values()),Q(0)),reserve=reserve,profit=profit,
                designated_quantity=sum((x['quantity']*x['fraction'] for x in instruments.values()),Q(0)),cash=books['cash'],inventory=books['inventory'],
                equity=capital+profit+reserve,books=books,closed=closed))
        for event in r['events']:
            if closed:fail('event_after_close')
            if not isinstance(event,dict):fail('event_shape')
            op=event.get('operation');common={'id','operation','date','context','findings'}
            fields={'measure':{'price','marks'},'reduce_instruments':{'reductions'},'purchase_and_settle':{'quantity','unit_price','supplier_cash','settlements'}}
            if op not in fields:fail('operation','unsupported')
            shape(event,common|fields[op],'event_shape');id=identity(event['id'])
            if id in seen:fail('duplicate_event')
            seen.add(id)
            try:
                if date.fromisoformat(event['date']).isoformat()!=event['date']:raise ValueError()
            except (ValueError,TypeError):fail('date_encoding')
            if event['date']<last_date or event['date']>CONTEXT['maturity_date']:fail('chronology')
            if event['context']!=CONTEXT:fail('event_context')
            if op=='measure':
                findings(event['findings'],MEASURE);shape(event['marks'],instruments,'mark_inventory')
                price=num(event['price'],'price',positive=True);entries={}
                for key,x in instruments.items():
                    value=num(event['marks'][key],'mark',signed=True);delta=value-x['value']
                    x['G']+=x['fraction']*delta;x['U']+=(1-x['fraction'])*delta;x['value']=value
                    entries['derivative:'+key]=delta
                G=sum((x['G'] for x in instruments.values()),Q(0));U=sum((x['U'] for x in instruments.values()),Q(0))
                H=quantity*(origin-price)
                if G*H>0:fail('nonoffsetting_history','unsupported')
                newR=(1 if G>0 else -1 if G<0 else 0)*min(abs(G),abs(H));newP=G-newR+U
                entries.update(cf_reserve=reserve-newR,earnings=profit-newP)
                journal(event,entries);reserve=newR;profit=newP
            elif op=='reduce_instruments':
                findings(event['findings'],REDUCE)
                if last_operation!='measure' or event['date']!=last_date:fail('same_date_measurement_required')
                rows=event['reductions']
                if not isinstance(rows,list) or not rows:fail('reduction_shape')
                reduced=set()
                for row in rows:
                    shape(row,{'instrument','quantity'},'reduction_shape');key=row['instrument']
                    if key not in instruments or key in reduced:fail('reduction_identity')
                    reduced.add(key);x=instruments[key];cut=num(row['quantity'],'reduction_quantity',positive=True);fraction=cut/x['quantity']
                    if fraction>x['fraction']:fail('reduction_exceeds_designated')
                    x['stops'].append(dict(date=event['date'],quantity=cut,fraction=fraction,whole_mark=x['value'],portion_value=fraction*x['value']))
                    x['fraction']-=fraction
                if not any(x['fraction'] for x in instruments.values()):fail('full_discontinuation','unsupported')
            else:
                findings(event['findings'],SETTLE)
                if last_operation!='measure' or event['date']!=last_date:fail('same_date_measurement_required')
                if event['date']!=CONTEXT['maturity_date']:fail('settlement_date','unsupported')
                q=num(event['quantity'],'purchase_quantity',positive=True);p=num(event['unit_price'],'unit_price',positive=True)
                paid=num(event['supplier_cash'],'supplier_cash');shape(event['settlements'],instruments,'settlement_inventory')
                if q!=quantity or p!=price or paid!=q*p:fail('purchase_identity')
                if books['cash']<paid:fail('supplier_funding_required','unsupported')
                settlements={k:num(event['settlements'][k],'settlement',signed=True) for k in instruments}
                if any(settlements[k]!=instruments[k]['value'] for k in instruments):fail('settlement_identity')
                before=state();journal(event,dict(inventory=paid,cash=-paid));flows.append(dict(event=id,kind='supplier_payment',amount=-paid))
                for key,x in instruments.items():
                    value=settlements[key]
                    if books['cash']+value<0:fail('derivative_funding_required','unsupported')
                    journal(event,{'cash':value,'derivative:'+key:-value});flows.append(dict(event=id,kind='derivative_settlement',instrument=key,amount=value));x['settled_cash']+=value;x['value']=Q(0)
                journal(event,dict(cf_reserve=reserve,inventory=-reserve))
                closing=dict(before=before,supplier_cost=paid,basis_transfer=reserve,inventory=paid-reserve,cash=books['cash'],profit=profit,equity=capital+profit)
                reserve=Q(0);closed=True
            last_date=event['date'];last_operation=op
            stages.append(dict(id=id,operation=op,date=last_date,state=state()))
        if not closed:fail('closing_required','unresolved')
        return encode(dict(status='conditional_complete',reason='identified_instrument_reduction',state=state(),stages=stages,journals=journals,cash_flows=flows,closing=closing,mutations=[],posts=False))
    except Refusal as e:return dict(status=e.status,reason=e.reason,**empty)
