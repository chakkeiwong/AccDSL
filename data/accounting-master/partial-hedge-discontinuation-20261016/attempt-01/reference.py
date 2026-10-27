"""Preserve reserve origins through one matched homogeneous partial discontinuation."""
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
BASELINE='data/accounting-master/repeated-rebalancing-20261016/reference.py'
GLOBAL={'single_external_nonoption_derivative','original_zero_cost','homogeneous_paired_portions',
        'proportional_entire_instrument','no_other_cash_or_earnings','pretax_scope','baseline_reserve_recoverable'}
STOP={'remaining_qualifies','documentation_updated','identified_matching_portions','continuing_reserve_recoverable'}
MEASURE={'continuing_qualifies','complete_valuation_effects','zero_discount_admitted',
         'continuing_reserve_recoverable','stopped_expectation_unchanged','stopped_loss_assessment_unchanged'}
CLOSE={'all_expected_units_received','inventory_recognition_satisfied','costs_complete',
       'nrv_supports_adjusted_cost','no_further_value_movement','early_settlement_permitted',
       'settlement_at_carrying_no_fees'}


class Refusal(Exception):
    def __init__(self,status,reason):self.status,self.reason=status,reason


def need(ok,reason,status='rejected'):
    if not ok:raise Refusal(status,reason)


def rational(value):
    need(isinstance(value,str) and re.fullmatch(r'(0|-?[1-9][0-9]*)(/[1-9][0-9]*)?',value),'rational_encoding')
    q=Q(value);need(str(q)==value,'rational_encoding');return q


def day(value):
    need(isinstance(value,str),'date_encoding')
    try:d=date.fromisoformat(value)
    except ValueError:raise Refusal('rejected','date_encoding')
    need(d.isoformat()==value,'date_encoding');return d


def boolean(value,key):
    need(value is not None,'missing_'+key,'unresolved')
    need(type(value) is bool,'finding_type');return value


def findings(value,fields):
    need(isinstance(value,dict) and set(value)==fields,'findings_shape')
    for key in sorted(fields):need(boolean(value[key],key),'finding_'+key,'unsupported')


def encode(value):
    if isinstance(value,Q):return str(value)
    if isinstance(value,dict):return {k:encode(v) for k,v in value.items()}
    if isinstance(value,list):return [encode(v) for v in value]
    return value


def reserve(D,H):
    need(D*H<=0,'nonoffsetting_cumulative_values','unsupported')
    return (1 if D>0 else -1 if D<0 else 0)*min(abs(D),abs(H))


def calculate(request,resolve_bytes=None):
    result=dict(wire='PartialHedgeDiscontinuation/1',status='rejected',reason=None,
                report=None,trace=[],journals=[],flows=[],mutations=[])
    try:
        need(isinstance(request,dict) and set(request)=={'wire','operation','baseline_hedge','context',
             'opening_cash','findings','discontinuation','events'},'request_shape')
        need(request['wire']=='PartialHedgeDiscontinuation/1' and request['operation']=='report','report_only')
        findings(request['findings'],GLOBAL)
        reader=resolve_bytes or (lambda p:p.read_bytes());payloads={}
        for item in LOCK:
            try:payload=reader(ROOT/item['path'])
            except OSError:raise Refusal('unresolved','input_bytes_missing')
            need(isinstance(payload,bytes),'input_bytes_type')
            need(hashlib.sha256(payload).hexdigest()==item['sha256'],'input_bytes_changed')
            payloads[item['path']]=payload
        namespace={'__name__':'checked_partial_hedge_baseline','__file__':str(ROOT/BASELINE)}
        exec(compile(payloads[BASELINE],str(ROOT/BASELINE),'exec'),namespace)
        baseline=namespace['calculate'](request['baseline_hedge'])
        need(baseline['status']=='conditional_complete','baseline_'+str(baseline['reason']),baseline['status'])
        s=baseline['state'];context=s['context']
        need(request['context']==context,'context_mismatch')
        need(len(s['layers'])==1,'multiple_origin_allocation_required','unsupported')
        need(s['last_operation']=='measure','measure_before_stop')
        original=s['layers'][0];quantity=Q(original['quantity']);origin=Q(original['price'])
        D,R,I=(Q(s[k]) for k in ('D','reserve','profit'))
        opening=rational(request['opening_cash']);need(opening>=0,'negative_opening_cash')
        books=dict(cash=opening,inventory=Q(0),derivative=D,cf_reserve=-R,gains=-I,capital=-opening)
        continuing_R=R;stopped_R=Q(0);released=Q(0);basis_transferred=Q(0)
        trace=[];journals=[];flows=[];closed=False;close_report=None
        def post(id,operation,when,entries):
            need(sum(entries.values())==0,'journal_balance')
            for key,value in entries.items():books[key]+=value
            need(sum(books.values())==0,'book_balance')
            need(books['cash']>=0,'funding_required','unsupported')
            journals.append(dict(event_id=id,operation=operation,date=when,entries=deepcopy(entries)))
        def snapshot(id,when):
            p=-books['gains'];r=-books['cf_reserve']
            need(r==continuing_R+stopped_R,'reserve_portions')
            need(books['cash']+books['inventory']+books['derivative']==opening+p+r,'net_asset_equity')
            need(books['cash']==opening+sum(x['amount'] for x in flows),'cash_origin_bridge')
            trace.append(dict(id=id,date=when,state=dict(derivative=books['derivative'],reserve=r,profit=p,
                continuing_reserve=continuing_R,stopped_reserve=stopped_R,released=released,
                cash=books['cash'],inventory=books['inventory'],equity=opening+p+r,closed=closed)))
        snapshot('baseline',s['date'])
        stop=request['discontinuation']
        need(isinstance(stop,dict) and set(stop)=={'id','date','quantity','expected','unrecoverable_loss','highly_probable','findings'},'stop_shape')
        findings(stop['findings'],STOP)
        need(isinstance(stop['id'],str) and stop['id'] and stop['id']!='baseline','event_id')
        need(stop['date']==s['date'],'stop_measurement_date')
        need(not boolean(stop['highly_probable'],'stopped_highly_probable'),'still_qualifying_cannot_stop','unsupported')
        removed=rational(stop['quantity']);need(0<removed<quantity,'partial_quantity')
        fraction=removed/quantity;remaining=quantity-removed
        continuing_R=(1-fraction)*R;stopped_R=fraction*R
        stopped_D0=fraction*D;stopped_I0=fraction*I
        # Partitioning itself is a state split, not an additional book gain.
        need(continuing_R==reserve((1-fraction)*D,(1-fraction)*Q(s['H'])),'homogeneous_split')
        need(stopped_R==reserve(fraction*D,fraction*Q(s['H'])),'homogeneous_split')
        expected=boolean(stop['expected'],'stopped_expected')
        def assessment(id,when,wanted,loss):
            nonlocal stopped_R,released,expected
            new_expected=boolean(wanted,'stopped_expected');loss=rational(loss)
            need(loss>=0,'negative_unrecoverable_loss')
            need(not (expected is False and new_expected is True),'new_forecast_requires_separate_method','unsupported')
            if new_expected:
                need(loss<=max(Q(0),-stopped_R),'loss_exceeds_remaining_reserve')
                transfer=-loss
            else:
                need(loss==0,'cancellation_loss_double_count')
                transfer=stopped_R
            stopped_R-=transfer;released+=transfer;expected=new_expected
            post(id,'reserve_to_profit',when,dict(cf_reserve=transfer,gains=-transfer))
        assessment(stop['id'],stop['date'],stop['expected'],stop['unrecoverable_loss'])
        snapshot(stop['id'],stop['date'])
        ids={'baseline',stop['id']};when=day(stop['date']);last_mark=s['date'];price=Q(s['price'])
        need(isinstance(request['events'],list),'events_shape')
        for event in request['events']:
            need(isinstance(event,dict),'event_shape');op=event.get('operation')
            need(op in ('measure','assess_stopped','purchase_and_settle'),'different_operation','unsupported')
            fields={'id','operation','date','context','findings'}|({'price','derivative'} if op=='measure' else
                {'expected','unrecoverable_loss'} if op=='assess_stopped' else {'quantity','unit_price','supplier_cash','settlement_cash'})
            need(set(event)==fields,'event_shape')
            need(isinstance(event['id'],str) and event['id'] and event['id'] not in ids,'event_id');ids.add(event['id'])
            need(event['context']==context,'context_mismatch')
            current=day(event['date']);need(when<=current<day(context['maturity_date']),'event_date');when=current
            need(not closed,'already_closed')
            if op=='measure':
                findings(event['findings'],MEASURE)
                D=rational(event['derivative']);price=rational(event['price'])
                H=-remaining*(price-origin)
                new_R=reserve((1-fraction)*D,H)
                new_I=(1-fraction)*D-new_R
                profit=new_I+stopped_I0+(fraction*D-stopped_D0)+released
                post(event['id'],op,event['date'],dict(derivative=D-books['derivative'],
                    cf_reserve=-(new_R-continuing_R),gains=-profit-books['gains']))
                continuing_R=new_R;last_mark=event['date']
            elif op=='assess_stopped':
                findings(event['findings'],{'facts_admitted'})
                assessment(event['id'],event['date'],event['expected'],event['unrecoverable_loss'])
            else:
                findings(event['findings'],CLOSE)
                need(event['date']==last_mark,'measure_immediately_before_close')
                purchased=remaining+(removed if expected else Q(0))
                need(rational(event['quantity'])==purchased,'purchase_population')
                need(rational(event['unit_price'])==price,'purchase_price')
                cost=rational(event['supplier_cash']);need(cost==purchased*price and cost>=0,'supplier_cost')
                settlement=rational(event['settlement_cash']);need(settlement==books['derivative'],'settlement_carrying_value')
                basis_transferred=continuing_R+stopped_R;adjusted=cost-basis_transferred
                need(adjusted>=0,'negative_inventory_method','unsupported')
                post(event['id'],'purchase',event['date'],dict(inventory=cost,cash=-cost))
                flows.append(dict(origin='inventory_supplier',date=event['date'],amount=-cost))
                post(event['id'],'settle_whole_derivative',event['date'],dict(cash=settlement,derivative=-settlement))
                flows.append(dict(origin='derivative_settlement',date=event['date'],amount=settlement))
                post(event['id'],'basis_transfer',event['date'],dict(cf_reserve=basis_transferred,inventory=-basis_transferred))
                continuing_R=stopped_R=Q(0);closed=True
                close_report=dict(quantity=purchased,supplier_cost=cost,basis_transferred=basis_transferred,
                    net_cash=sum(x['amount'] for x in flows),equity=opening-books['gains'])
            snapshot(event['id'],event['date'])
        report=dict(context=deepcopy(context),removed_quantity=removed,continuing_quantity=remaining,
            original_quantity=quantity,original_price=origin,stopped_derivative_origin=stopped_D0,
            stopped_prior_profit=stopped_I0,stopped_reserve_at_discontinuation=fraction*R,
            stopped_expected=expected,close=close_report,final=deepcopy(trace[-1]['state']),
            baseline_module_sha256=hashlib.sha256(payloads[BASELINE]).hexdigest(),
            tax='not_calculated',cash_activity_classification='not_concluded',posts=False)
        result.update(status='conditional_complete',report=encode(report),trace=encode(trace),
                      journals=encode(journals),flows=encode(flows))
    except Refusal as exc:result.update(status=exc.status,reason=exc.reason)
    return result
