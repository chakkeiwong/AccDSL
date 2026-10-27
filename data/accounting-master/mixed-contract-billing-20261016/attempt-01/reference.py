"""Read-only exact documentary composition; no service or accounting runtime."""
from datetime import date
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
CONTEXT=dict(entity='synthetic-builder',book='separate',contract='mixed-A',currency='CU',
             unit='currency units',rule='AASB15-compilation8-AU-for-profit')
GLOBAL={'contract_eligibility_9','construction_over_time','visits_distinct','allocations_admitted',
        'expected_payment_transfer_interval_leq_year','financing_expedient_elected',
        'no_tax_fx_variable_consideration_refunds_or_onerous_loss'}
COMMON={'zero_impairment_assessed','admitted_contract_facts_remain_valid'}
FINDINGS=dict(advance=COMMON,collect=COMMON,invoice=COMMON|{'unconditional_right'},
    perform=COMMON|{'faithful_cost_progress','visits_transferred','all_costs_expensed_on_performance'},
    amend=COMMON|{'approved_enforceable','mixed_modification_not_separate','allocations_admitted',
                 'faithful_cost_progress','expected_payment_transfer_interval_leq_year'})
FIELDS=dict(advance={'advance_id','amount'},collect={'settlement_id','invoice_id','amount'},
    invoice={'invoice_id','gross','credits'},perform={'construction_cash_cost','visits','visit_cash_cost'},
    amend={'new_construction_price','new_expected_cost','new_visits_total'})

class Refusal(Exception):
    def __init__(self,status,reason):self.status=status;self.reason=reason

def fail(reason,status='rejected'):raise Refusal(status,reason)
def shape(x,keys,reason):
    if not isinstance(x,dict) or set(x)!=set(keys):fail(reason)
def number(x,name,positive=False,integer=False):
    if x is None:fail('missing_'+name,'unresolved')
    try:
        if not isinstance(x,str):raise ValueError()
        n=Q(x)
        if str(n)!=x:raise ValueError()
    except (ValueError,ZeroDivisionError):fail('amount_encoding')
    if n<0 or (positive and n==0) or (integer and n.denominator!=1):fail('amount_domain')
    return n
def identity(x):
    if not isinstance(x,str) or not x.strip() or x!=x.strip():fail('identity')
    return x
def day(x):
    try:
        d=date.fromisoformat(x)
        if d.isoformat()!=x:raise ValueError()
    except (ValueError,TypeError):fail('date_encoding')
    return d
def findings(x,keys):
    shape(x,keys,'finding_shape')
    for k in sorted(keys):
        if x[k] is None:fail('missing_'+k,'unresolved')
        if x[k] is False:fail('outside_'+k,'unsupported')
        if x[k] is not True:fail('finding_encoding')
def encode(x):
    if isinstance(x,Q):return str(x)
    if isinstance(x,dict):return {k:encode(v) for k,v in x.items()}
    if isinstance(x,list):return [encode(v) for v in x]
    return x

def calculate(request,reader=lambda p:p.read_bytes()):
    empty=dict(report=None,trace=[],journals=[],cash_flows=[],mutations=[])
    try:
        lock=json.loads((OUT/'input-lock.json').read_text())
        for row in lock['files']:
            if '/sources/' not in row['path']:continue
            try:raw=reader(ROOT/row['path'])
            except FileNotFoundError:fail('source_unavailable','unresolved')
            if hashlib.sha256(raw).hexdigest()!=row['sha256']:fail('source_changed')
        shape(request,{'wire','operation','context','annual_start','as_of','opening_cash','terms','findings','events'},'request_shape')
        if request['wire']!='MixedContractBilling/1':fail('wire')
        if request['operation']!='report':fail('report_only')
        if request['context']!=CONTEXT:fail('context')
        start=day(request['annual_start']);cut=day(request['as_of'])
        if not date(2023,1,1)<=start<date(2026,7,1):fail('source_interval','unsupported')
        if start.month!=1 or start.day!=1 or cut.year!=start.year or cut<start:fail('annual_calendar','unsupported')
        findings(request['findings'],GLOBAL)
        t=request['terms'];shape(t,{'construction_price','expected_cost','visit_price','visits_total'},'terms_shape')
        price=number(t['construction_price'],'construction_price',True);expected=number(t['expected_cost'],'expected_cost',True)
        visit_price=number(t['visit_price'],'visit_price',True);total_visits=number(t['visits_total'],'visits_total',True,True)
        capital=number(request['opening_cash'],'opening_cash')
        cost=Q(0);visit_cost=Q(0);done=Q(0);construction=Q(0);visits_earned=Q(0)
        A=Q(0);G=Q(0);K=Q(0);C=Q(0);cash=capital
        advances={};invoices={};credits={};settlements={};ids=set();last=start;modified=False
        trace=[];journals=[];flows=[]
        def state():
            r=construction+visits_earned;tally=G+A-K;ar=G-K-C;ca=max(r-tally,Q(0));cl=max(tally-r,Q(0));expense=cost+visit_cost
            return dict(cash=cash,receivable=ar,contract_asset=ca,contract_liability=cl,revenue=r,expense=expense,
                profit=r-expense,equity=capital+r-expense,construction_revenue=construction,visit_revenue=visits_earned,
                advances=A,gross_invoices=G,credits=K,collections=C,paid_or_due=tally,price=price+visit_price*total_visits)
        def book(s):return dict(cash=s['cash'],receivable=s['receivable'],contract_asset=s['contract_asset'],
            contract_liability=-s['contract_liability'],income=-s['revenue'],expense=s['expense'],capital=-capital)
        previous=book(state())
        if not isinstance(request['events'],list):fail('event_list')
        for e in request['events']:
            if not isinstance(e,dict):fail('event_shape')
            op=e.get('operation')
            if not isinstance(op,str) or op not in FIELDS:fail('different_operation','unsupported')
            shape(e,{'id','operation','date','information_date','context','findings'}|FIELDS[op],'event_shape')
            id=identity(e['id'])
            if id in ids:fail('event_identity')
            ids.add(id)
            d=day(e['date']);info=day(e['information_date'])
            if d<last or d>cut or d.year!=start.year:fail('event_date_or_cutoff')
            if info<start or info>d:fail('information_cutoff')
            last=d
            if e['context']!=CONTEXT:fail('context')
            findings(e['findings'],FINDINGS[op])
            def flow(kind,amount):
                if amount:flows.append(dict(id=id,date=e['date'],kind=kind,amount=amount,category='operating'))
            if op=='advance':
                aid=identity(e['advance_id']);amount=number(e['amount'],'amount',True)
                if aid in advances:fail('advance_identity')
                advances[aid]=dict(contract=CONTEXT['contract'],received=amount,credited=Q(0));A+=amount;cash+=amount
                flow('advance_receipt',amount)
            elif op=='perform':
                addcost=number(e['construction_cash_cost'],'construction_cash_cost');n=number(e['visits'],'visits',integer=True)
                vcost=number(e['visit_cash_cost'],'visit_cash_cost')
                if cost+addcost>expected or done+n>total_visits:fail('performance_exceeds_obligation')
                if n==0 and vcost:fail('visit_cost_without_performance','unsupported')
                if cash<addcost+vcost:fail('cash_funding_required','unsupported')
                cost+=addcost;done+=n;visit_cost+=vcost;cash-=addcost+vcost
                construction=price*cost/expected;visits_earned+=visit_price*n
                flow('construction_cash_cost',-addcost);flow('visit_cash_cost',-vcost)
            elif op=='amend':
                if modified:fail('repeated_amendment','unsupported')
                newprice=number(e['new_construction_price'],'new_construction_price',True)
                newexpected=number(e['new_expected_cost'],'new_expected_cost',True)
                newvisits=number(e['new_visits_total'],'new_visits_total',True,True)
                if not 0<cost<expected or newexpected<=cost or newvisits<=done:fail('mixed_amendment_stage','unsupported')
                price=newprice;expected=newexpected;total_visits=newvisits;construction=price*cost/expected;modified=True
            elif op=='invoice':
                iid=identity(e['invoice_id']);gross=number(e['gross'],'gross',True)
                if iid in invoices:fail('invoice_identity')
                if not isinstance(e['credits'],list):fail('credits_shape')
                credited=Q(0)
                for credit in e['credits']:
                    shape(credit,{'credit_id','contract','advance_id','amount'},'credit_shape')
                    cid=identity(credit['credit_id']);aid=identity(credit['advance_id']);amount=number(credit['amount'],'credit_amount',True)
                    if cid in credits:fail('credit_identity')
                    if credit['contract']!=CONTEXT['contract']:fail('credit_contract')
                    if aid not in advances:fail('unknown_advance')
                    if amount>advances[aid]['received']-advances[aid]['credited']:fail('advance_overcredit')
                    advances[aid]['credited']+=amount;credited+=amount
                    credits[cid]=dict(contract=CONTEXT['contract'],advance_id=aid,invoice_id=iid,amount=amount)
                if credited>gross:fail('invoice_overcredit')
                invoices[iid]=dict(contract=CONTEXT['contract'],gross=gross,credited=credited,collected=Q(0))
                G+=gross;K+=credited
            elif op=='collect':
                sid=identity(e['settlement_id']);iid=identity(e['invoice_id']);amount=number(e['amount'],'amount',True)
                if sid in settlements:fail('settlement_identity')
                if iid not in invoices:fail('unknown_invoice')
                inv=invoices[iid]
                if amount>inv['gross']-inv['credited']-inv['collected']:fail('overcollection')
                inv['collected']+=amount;C+=amount;cash+=amount
                settlements[sid]=dict(contract=CONTEXT['contract'],invoice_id=iid,amount=amount);flow('invoice_collection',amount)
            current=state()
            if G>current['price'] or current['paid_or_due']>current['price']:fail('entitlement_exceeds_price')
            if current['receivable']<0 or current['cash']<0:fail('negative_asset')
            if current['cash']+current['receivable']+current['contract_asset']-current['contract_liability']!=current['equity']:fail('accounting_identity')
            updated=book(current);entries={k:updated[k]-previous[k] for k in updated if updated[k]!=previous[k]}
            if sum(entries.values(),Q(0))!=0:fail('journal_balance')
            journals.append(dict(id=id,date=e['date'],entries=entries));trace.append(dict(id=id,date=e['date'],state=current));previous=updated
        final=state()
        report=dict(posts=False,as_of=request['as_of'],final=final,advances=advances,invoices=invoices,credits=credits,
            settlements=settlements,performance_complete=cost==expected and done==total_visits,
            financially_settled=final['receivable']==final['contract_asset']==final['contract_liability']==0,
            direct_operating_cash=A+C-cost-visit_cost,
            indirect_operating_cash=final['profit']-final['receivable']-final['contract_asset']+final['contract_liability'],
            opening_capital=capital,other_comprehensive_income=Q(0))
        return encode(dict(status='conditional_complete',reason='admitted_finite_composition',report=report,
            trace=trace,journals=journals,cash_flows=flows,mutations=[]))
    except Refusal as e:return dict(status=e.status,reason=e.reason,**empty)
