"""Exact annual POCI terminal-claim measurement with a signed loss component."""
from copy import deepcopy
from datetime import date
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import re

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
LOCK=json.loads((OUT/'input-lock-v2.json').read_text())['files']
CONTEXT={'entity','book','currency','unit','rule','contract','calendar'}
ACQUIRE={'poci_at_initial_recognition','amortised_cost_classification','price_equals_fair_value',
         'no_integral_fees_or_costs','complete_initial_expected_cash','contract_terms_admitted',
         'no_modification_fx_tax_or_other_cash','no_full_or_partial_writeoff_required'}
ADVANCE={'information_view_admitted','credit_assessment_unchanged','no_interim_cash_or_modification',
         'no_full_or_partial_writeoff_required'}
REVISE={'credit_cash_forecast_admitted','contract_terms_unchanged','no_full_or_partial_writeoff_required'}
CLOSE={'receipt_confirmed','no_reasonable_further_recovery','contractual_population_complete'}


class Refusal(Exception):
    def __init__(self,status,reason):self.status,self.reason=status,reason


def need(ok,reason,status='rejected'):
    if not ok:raise Refusal(status,reason)


def rational(value,key):
    need(value is not None,'missing_'+key,'unresolved')
    need(isinstance(value,str) and re.fullmatch(r'(0|-?[1-9][0-9]*)(/[1-9][0-9]*)?',value),'rational_encoding')
    q=Q(value);need(str(q)==value,'rational_encoding');return q


def day(value):
    need(isinstance(value,str),'date_encoding')
    try:d=date.fromisoformat(value)
    except ValueError:raise Refusal('rejected','date_encoding')
    need(d.isoformat()==value,'date_encoding');return d


def findings(value,fields):
    need(isinstance(value,dict) and set(value)==fields,'findings_shape')
    for key in sorted(fields):
        need(value[key] is not None,'missing_'+key,'unresolved')
        need(type(value[key]) is bool,'finding_type')
        need(value[key],'finding_'+key,'unsupported')


def encode(value):
    if isinstance(value,Q):return str(value)
    if isinstance(value,dict):return {k:encode(v) for k,v in value.items()}
    if isinstance(value,list):return [encode(v) for v in value]
    return value


def calculate(request,resolve_bytes=None):
    result=dict(wire='POCIAnnualTerminal/1',status='rejected',reason=None,
        report=None,trace=[],journals=[],flows=[],mutations=[])
    try:
        need(isinstance(request,dict) and set(request)=={'wire','operation','context','opening_cash','acquisition','events'},'request_shape')
        need(request['wire']=='POCIAnnualTerminal/1' and request['operation']=='report','report_only')
        reader=resolve_bytes or (lambda p:p.read_bytes())
        for item in LOCK:
            try:payload=reader(ROOT/item['path'])
            except OSError:raise Refusal('unresolved','input_bytes_missing')
            need(isinstance(payload,bytes),'input_bytes_type')
            need(hashlib.sha256(payload).hexdigest()==item['sha256'],'input_bytes_changed')
        context=request['context']
        need(isinstance(context,dict) and set(context)==CONTEXT and all(isinstance(v,str) and v for v in context.values()),'context_shape')
        need(context['rule']=='EU2023/1803-original-POCI','different_rule','unsupported')
        need(context['unit']=='currency units' and context['calendar']=='annual-anniversary','different_units_calendar','unsupported')
        a=request['acquisition']
        need(isinstance(a,dict) and set(a)=={'date','price','contractual_receipt','expected_receipt','credit_adjusted_rate','term_years','findings'},'acquisition_shape')
        findings(a['findings'],ACQUIRE)
        start=day(a['date']);term=a['term_years']
        need(type(term) is int and term>0,'positive_integer_term')
        def anniversary(t):
            try:return date(start.year+t,start.month,start.day)
            except (ValueError,OverflowError):raise Refusal('unsupported','different_anniversary_calendar')
        anniversary(term)
        price=rational(a['price'],'price');C=rational(a['contractual_receipt'],'contractual_receipt')
        E0=rational(a['expected_receipt'],'expected_receipt');r=rational(a['credit_adjusted_rate'],'credit_adjusted_rate')
        need(price>0 and C>0 and 0<E0<=C,'initial_amounts')
        need(r>-1,'positive_discount_base','unsupported')
        need(E0/(1+r)**term==price,'initial_rate_value_mismatch')
        opening=rational(request['opening_cash'],'opening_cash');need(opening>=0,'negative_opening_cash')
        books=dict(cash=opening,gross=Q(0),allowance=Q(0),interest=Q(0),impairment=Q(0),capital=-opening)
        journals=[];trace=[];flows=[];period=0;expected=E0;closed=False;uncollected=None
        def post(id,operation,when,entries):
            need(sum(entries.values())==0,'journal_balance')
            for key,value in entries.items():books[key]+=value
            need(sum(books.values())==0,'book_balance')
            need(books['cash']>=0,'funding_required','unsupported')
            journals.append(dict(event_id=id,operation=operation,date=when,entries=deepcopy(entries)))
        def snapshot(id,when):
            G=books['gross'];L=-books['allowance'];N=G-L
            interest=-books['interest'];impairment=-books['impairment'];profit=interest+impairment
            need(books['cash']+N==opening+profit,'net_asset_equity')
            need(books['cash']==opening+sum(x['amount'] for x in flows),'cash_origin_bridge')
            if not closed:
                need(G==price*(1+r)**period,'original_gross_path')
                need(N==expected/(1+r)**(term-period),'direct_net_present_value')
                need(L==((C-expected)-(C-E0))/(1+r)**(term-period),'cumulative_loss_change')
            trace.append(dict(id=id,date=when,period=period,state=dict(gross=G,allowance=L,net=N,
                interest=interest,impairment_gain=impairment,cash=books['cash'],profit=profit,
                equity=opening+profit,credit_adjusted_rate=r,poci_origin=True,closed=closed)))
        post('acquisition','purchase',a['date'],dict(gross=price,cash=-price))
        flows.append(dict(origin='asset_purchase',date=a['date'],amount=-price))
        snapshot('acquisition',a['date']);ids={'acquisition'}
        need(isinstance(request['events'],list),'events_shape')
        for event in request['events']:
            need(isinstance(event,dict),'event_shape');op=event.get('operation')
            need(op in ('advance','revise_credit','collect_close'),'different_operation','unsupported')
            fields={'id','operation','date','context','findings'}| (set() if op=='advance' else
                {'expected_receipt','credit_improved','information_date'} if op=='revise_credit' else {'cash','information_date'})
            need(set(event)==fields,'event_shape')
            id=event['id'];need(isinstance(id,str) and id and id not in ids and not id.endswith('_measure'),'event_id');ids.add(id)
            need(event['context']==context,'context_mismatch');when=day(event['date'])
            need(not closed,'already_closed')
            if op=='advance':
                findings(event['findings'],ADVANCE)
                need(period<term,'past_maturity')
                need(when==anniversary(period+1),'annual_step_date')
                G=books['gross'];L=-books['allowance'];N=G-L
                post(id,'interest_and_allowance_unwind',event['date'],dict(gross=r*G,allowance=-r*L,interest=-r*N))
                period+=1
            else:
                need(when==anniversary(period),'assessment_date')
                known=day(event['information_date']);need(start<=known<=when,'future_or_preacquisition_information')
                if op=='revise_credit':
                    findings(event['findings'],REVISE)
                    need(event['credit_improved'] is not None,'missing_credit_improved','unresolved')
                    need(type(event['credit_improved']) is bool,'finding_type')
                    updated=rational(event['expected_receipt'],'expected_receipt')
                    need(0<=updated<=C,'receipt_exceeds_contract_or_negative')
                    need(updated>0 or period==term,'early_zero_recovery_method','unsupported')
                    # The improvement flag records a finding; it never changes POCI origin or r.
                else:
                    findings(event['findings'],CLOSE)
                    need(period==term,'terminal_collection_only','unsupported')
                    updated=rational(event['cash'],'receipt_cash')
                    need(0<=updated<=C,'receipt_exceeds_contract_or_negative')
                old_N=books['gross']+books['allowance'];new_N=updated/(1+r)**(term-period)
                gain=new_N-old_N;expected=updated
                post(id,'credit_remeasurement',event['date'],dict(allowance=gain,impairment=-gain))
                if op=='collect_close':
                    snapshot(id+'_measure',event['date'])
                    G=books['gross'];L=-books['allowance']
                    post(id,'collection_and_financial_derecognition',event['date'],dict(cash=updated,gross=-G,allowance=L))
                    flows.append(dict(origin='confirmed_collection',date=event['date'],amount=updated))
                    closed=True;uncollected=C-updated
            snapshot(id,event['date'])
        report=dict(context=deepcopy(context),acquisition_date=a['date'],maturity_date=anniversary(term).isoformat(),
            original_credit_adjusted_rate=r,initial_expected_receipt=E0,contractual_receipt=C,acquisition_value=price,
            initial_credit_shortfall_present_value=(C-E0)/(1+r)**term,initial_loss_allowance=Q(0),
            final=deepcopy(trace[-1]['state']),uncollected_contractual_amount=uncollected,
            legal_release='not_assessed',financial_asset_derecognized=closed,
            tax='not_calculated',forecast_calibration='not_established',posts=False)
        result.update(status='conditional_complete',report=encode(report),trace=encode(trace),
            journals=encode(journals),flows=encode(flows))
    except Refusal as exc:result.update(status=exc.status,reason=exc.reason)
    return result
