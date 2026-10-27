"""Exact finite contract-cost impairment, onerous provision and settlement."""
from copy import deepcopy
from datetime import date
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import re

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
LOCK=json.loads((OUT/'input-lock.json').read_text())['files']
CONTEXT={'entity','book','currency','unit','rule','contract'}
SHARED={'eligible_original_cost','one_remaining_point_in_time_service','no_prior_service_or_amortisation',
        'no_advance_receivable_tax_fx_or_reimbursement','time_value_immaterial','contract_enforceable'}
ASSESS={'other_standard_impairment_completed','no_additional_cgu_loss','complete_disjoint_direct_costs',
        'no_future_noncash_costs','reliable_best_estimates','collectible_fixed_consideration',
        'available_enforceable_exit','no_other_exit_benefits_or_costs'}
SETTLE={'confirmed_same_contract_cash','complete_performance_or_termination','no_other_rights_or_obligations',
        'no_alternative_use_of_remaining_cost_asset','admin_unrelated_to_contract'}


class Refusal(Exception):
    def __init__(self,status,reason):self.status,self.reason=status,reason


def need(ok,reason,status='rejected'):
    if not ok:raise Refusal(status,reason)


def amount(x,key):
    need(x is not None,'missing_'+key,'unresolved')
    need(isinstance(x,str) and re.fullmatch(r'(0|[1-9][0-9]*)(/[1-9][0-9]*)?',x),'nonnegative_rational_encoding')
    q=Q(x);need(str(q)==x,'nonnegative_rational_encoding');return q


def day(x):
    need(isinstance(x,str),'date_encoding')
    try:d=date.fromisoformat(x)
    except ValueError:raise Refusal('rejected','date_encoding')
    need(d.isoformat()==x,'date_encoding');return d


def findings(x,fields):
    need(isinstance(x,dict) and set(x)==fields,'findings_shape')
    for key in sorted(fields):
        need(x[key] is not None,'missing_'+key,'unresolved')
        need(type(x[key]) is bool,'finding_type')
        need(x[key],'finding_'+key,'unsupported')


def encode(x):
    if isinstance(x,Q):return str(x)
    if isinstance(x,list):return [encode(v) for v in x]
    if isinstance(x,dict):return {k:encode(v) for k,v in x.items()}
    return x


def calculate(request,reader=None):
    answer=dict(wire='OnerousContractSequence/1',status='rejected',reason=None,report=None,trace=[],journals=[],cash_flows=[],mutations=[])
    try:
        need(isinstance(request,dict) and set(request)=={'wire','operation','context','opening_date','opening_cash','original_unamortized_cost','findings','events'},'request_shape')
        need(request['wire']=='OnerousContractSequence/1' and request['operation']=='report','report_only')
        read=reader or (lambda p:p.read_bytes())
        for item in LOCK:
            try:b=read(ROOT/item['path'])
            except OSError:raise Refusal('unresolved','input_bytes_missing')
            need(isinstance(b,bytes),'source_bytes_type')
            need(hashlib.sha256(b).hexdigest()==item['sha256'],'input_bytes_changed')
        c=request['context'];need(isinstance(c,dict) and set(c)==CONTEXT and all(isinstance(v,str) and v for v in c.values()),'context_shape')
        need(c['unit']=='currency units' and c['rule']=='EU2023/1803-original-IFRS15-IAS37','different_rule_or_unit','unsupported')
        findings(request['findings'],SHARED)
        opening=amount(request['opening_cash'],'opening_cash');original=amount(request['original_unamortized_cost'],'original_unamortized_cost')
        initial=day(request['opening_date']);last=initial
        books=dict(cash=opening,asset=original,provision=Q(0),asset_loss=Q(0),provision_expense=Q(0),
            service_expense=Q(0),revenue=Q(0),admin_expense=Q(0),capital=-opening-original)
        trace=[];journals=[];flows=[];ids=set();previous=None;closed=False;fixed_B=None
        def post(id,kind,entries):
            need(sum(entries.values())==0,'journal_balance')
            for k,v in entries.items():books[k]+=v
            need(sum(books.values())==0,'book_balance')
            journals.append(dict(id=id,kind=kind,entries=deepcopy(entries)))
        need(isinstance(request['events'],list) and request['events'],'events_shape')
        for event in request['events']:
            need(isinstance(event,dict),'event_shape');op=event.get('operation')
            need(op in ('assess','fulfil','cancel'),'different_operation','unsupported')
            fields={'id','operation','date','context','findings'}|({'information_date','consideration','incremental_cash','allocated_direct_cash','exit_compensation'} if op=='assess' else
                {'receipt','incremental_cash','allocated_direct_cash','exit_compensation','unrelated_admin_cash'})
            need(set(event)==fields,'event_shape');need(not closed,'already_closed')
            id=event['id'];need(isinstance(id,str) and id and id not in ids,'event_identity');ids.add(id)
            need(event['context']==c,'context_mismatch');when=day(event['date'])
            need(last<=when and when.year==initial.year,'event_date_or_period');last=when
            if op=='assess':
                findings(event['findings'],ASSESS)
                known=day(event['information_date']);need(initial<=known<=when,'information_cutoff')
                B=amount(event['consideration'],'consideration');inc=amount(event['incremental_cash'],'incremental_cash')
                allocated=amount(event['allocated_direct_cash'],'allocated_direct_cash');K=amount(event['exit_compensation'],'exit_compensation')
                need(fixed_B is None or B==fixed_B,'changed_consideration_method','unsupported');fixed_B=B
                D=inc+allocated;new_A=min(original,max(B-D,Q(0)));loss=books['asset']-new_A
                # The asset test precedes the separate current obligation.
                post(id,'contract_cost_impairment_or_reversal',dict(asset=-loss,asset_loss=loss))
                F=max(D+new_A-B,Q(0));new_P=min(F,K);change=new_P+books['provision']
                post(id,'onerous_provision_remeasurement',dict(provision=-change,provision_expense=change))
                previous=dict(consideration=B,incremental_cash=inc,allocated_direct_cash=allocated,exit_compensation=K)
                detail=dict(recoverable_cost_ceiling=max(B-D,Q(0)),post_impairment_asset=new_A,
                    fulfilment_loss=F,available_exit=K,provision=new_P,cgu_result='supplied_no_additional_loss')
            else:
                findings(event['findings'],SETTLE);need(previous is not None,'assessment_required','unresolved')
                values={key:amount(event[key],key) for key in ('receipt','incremental_cash','allocated_direct_cash','exit_compensation','unrelated_admin_cash')}
                P=-books['provision'];A=books['asset'];admin=values['unrelated_admin_cash']
                if op=='fulfil':
                    need(values['receipt']==previous['consideration'] and all(values[k]==previous[k] for k in ('incremental_cash','allocated_direct_cash')) and values['exit_compensation']==0,'actual_cost_or_receipt_requires_review','unsupported')
                    D=values['incremental_cash']+values['allocated_direct_cash'];B=values['receipt']
                    need(books['cash']>=D+admin,'cash_funding_required','unsupported')
                    post(id,'perform_and_collect',dict(cash=B,revenue=-B));flows.append(dict(id=id,origin='customer_receipt',amount=B))
                    post(id,'fulfilment_cost_and_provision_use',dict(cash=-D,asset=-A,provision=P,service_expense=D+A-P))
                    flows.extend([dict(id=id,origin='incremental_contract_cash',amount=-values['incremental_cash']),dict(id=id,origin='allocated_direct_contract_cash',amount=-values['allocated_direct_cash'])])
                else:
                    need(values['receipt']==values['incremental_cash']==values['allocated_direct_cash']==0 and values['exit_compensation']==previous['exit_compensation'],'cancellation_terms_mismatch')
                    K=values['exit_compensation'];need(books['cash']>=K+admin,'cash_funding_required','unsupported')
                    post(id,'termination_cost_asset_loss',dict(asset=-A,asset_loss=A))
                    post(id,'cancellation_and_provision_use',dict(cash=-K,provision=P,service_expense=K-P))
                    flows.append(dict(id=id,origin='contract_cancellation_cash',amount=-K))
                post(id,'unrelated_administration',dict(cash=-admin,admin_expense=admin))
                flows.append(dict(id=id,origin='unrelated_administration_cash',amount=-admin))
                closed=True;detail=dict(settlement=op,provision_used=P,management_choice='supplied_not_selected')
            settlement=-books['revenue']-books['service_expense']
            profit=settlement-books['asset_loss']-books['provision_expense']-books['admin_expense']
            equity=opening+original+profit;P=-books['provision']
            need(books['cash']+books['asset']-P==equity,'net_asset_equity')
            need(books['cash']==opening+sum(x['amount'] for x in flows),'cash_origin_bridge')
            trace.append(dict(id=id,date=event['date'],detail=detail,state=dict(cash=books['cash'],asset=books['asset'],provision=P,
                asset_loss=books['asset_loss'],provision_expense=books['provision_expense'],settlement_result=settlement,
                admin_expense=books['admin_expense'],profit=profit,equity=equity)))
        report=dict(context=deepcopy(c),closed=closed,final=deepcopy(trace[-1]['state']),opening_capital=opening+original,
            pretax=True,tax='not_calculated',present_law='not_admitted',posts=False,management_choice='supplied_not_selected')
        answer.update(status='conditional_complete',report=encode(report),trace=encode(trace),journals=encode(journals),cash_flows=encode(flows))
    except Refusal as exc:answer.update(status=exc.status,reason=exc.reason)
    return answer
