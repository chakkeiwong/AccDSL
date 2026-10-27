"""Continue a conditional assessed book with explicitly allocated tax payments."""
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json
import following_period_tax_v1 as assessment

carry=assessment.carry; continuation=carry.continuation
book=assessment.book; core=assessment.core; losses=assessment.losses
require=assessment.require; caller=continuation.caller
ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/'data/accounting-master/tax-vintage-continuation-20261024'
LOCK='a648cdc01411bd3ff1227bce2f7a637b22cf1e6920bccbd5bbec1ab316982741'
PROFILE='TaxVintageContinuation/1'
FLAGS={**assessment.FLAGS,'provisional':True}
UNRESOLVED=['Actual source and accounting admission','Complete fiscal event coverage',
    'Tax reassessment of activity after the recorded endpoint',
    'New-period deferred recognition','Repeated carry and annual completeness']


def protected():
    raw=(HERE/'source-lock.json').read_bytes()
    require(sha256(raw).hexdigest()==LOCK,'source_lock_changed')
    for name,h in json.loads(raw).items():
        require(sha256((ROOT/name).read_bytes()).hexdigest()==h,'protected_source_changed:'+name)


def request(prior,operations):
    return {'profile':PROFILE,'assessment_request':deepcopy(prior),
        'assessment_sha256':book.digest(prior),'operations':deepcopy(operations)}


def vintage_invariant(state,vintages):
    continuation.invariant(state)
    require(type(vintages) is list and len(vintages)==2,'two_vintages_required')
    ids=[v['id'] for v in vintages]
    require(len(set(ids))==len(ids),'duplicate_vintage')
    require([v['kind'] for v in vintages]==['carried','current'],'vintage_kinds')
    paid_by_event={};event_dates={};event_operations={}
    for v in vintages:
        opening=Q(v['opening_payable']);new=Q(v['new_assessment']);closing=Q(v['closing_payable'])
        require(min(opening,new,closing)>=0,'negative_vintage_balance')
        seen=set();paid=Q(0);last=None
        for s in v['settlements']:
            key=s['event_id'];day=core.scalar(s['date'],'date');amount=Q(s['amount'])
            require(key not in seen and key in state['seen'],'settlement_identity')
            require(amount>0,'positive_settlement_required')
            require(core.scalar(state['period']['start'],'date')<=day<=core.scalar(state['date'],'date'),'settlement_date')
            require(last is None or last<=day,'settlement_chronology')
            require(key not in event_dates or event_dates[key]==s['date'],'settlement_date_mismatch')
            require(key not in event_operations or event_operations[key]==s['operation_sha256'],'settlement_operation_mismatch')
            seen.add(key);last=day;paid+=amount
            paid_by_event[key]=paid_by_event.get(key,Q(0))+amount
            event_dates[key]=s['date'];event_operations[key]=s['operation_sha256']
        require(opening+new-paid==closing,'vintage_conservation')
    require(sum(Q(v['closing_payable']) for v in vintages)==-Q(state['balances']['income_tax_payable']),'aggregate_vintage_payable')
    flows=[f for f in state['flows'] if f['origin']=='explicit_conditional_current_tax_payment']
    require(len(flows)==len({f['event_id'] for f in flows}),'duplicate_tax_flow')
    require({f['event_id'] for f in flows}==set(paid_by_event),'settlement_flow_population')
    for f in flows:
        key=f['event_id']
        require(f['activity']=='operating' and f['date']==event_dates[key] and -Q(f['amount'])==paid_by_event[key],'settlement_flow_amount_or_date')
    for v in vintages:
        for s in v['settlements']:
            if 'payment_amount' in s:
                require(Q(s['payment_amount'])==paid_by_event[s['event_id']],'settlement_total_mismatch')
    return vintages


def transition(state,vintages,operation,assessed_until):
    vintage_invariant(state,vintages);core.closed(operation,['kind','event'],'operation')
    kind=operation['kind'];updated=deepcopy(vintages)
    if kind=='native':
        result=continuation.transition(state,operation,assessed_until)
    else:
        require(kind=='allocated_tax_payment','explicit_vintage_allocation_required','unsupported')
        event=operation['event']
        core.closed(event,['id','date','amount','authorization','allocations'],'allocated_payment')
        allocations=event['allocations']
        require(type(allocations) is list and bool(allocations),'nonempty_allocations_required')
        total=losses.tax.numeric(event['amount']);require(total>0,'positive_payment_required')
        by_id={v['id']:v for v in updated};seen=set();allocated=Q(0)
        for a in allocations:
            core.closed(a,['vintage_id','amount'],'allocation');key=a['vintage_id']
            core.text(key,'vintage_id');require(key in by_id,'unknown_vintage')
            require(key not in seen,'duplicate_vintage_allocation');seen.add(key)
            amount=losses.tax.numeric(a['amount']);require(amount>0,'positive_allocation_required')
            require(amount<=Q(by_id[key]['closing_payable']),'allocation_exceeds_vintage')
            allocated+=amount
        require(allocated==total,'allocation_sum_mismatch')
        kernel_operation={'kind':'tax_payment','event':{k:deepcopy(v) for k,v in event.items() if k!='allocations'}}
        result=continuation.transition(state,kernel_operation,assessed_until)
        financial_digest=book.digest(result)
        for a in allocations:
            v=by_id[a['vintage_id']]
            v['closing_payable']=book.fmt(Q(v['closing_payable'])-Q(a['amount']))
            v['settlements'].append({'event_id':event['id'],'date':event['date'],
                'amount':book.fmt(Q(a['amount'])),'payment_amount':book.fmt(total),
                'operation_sha256':book.digest(operation),'financial_result_sha256':financial_digest})
        result['operation_sha256']=book.digest(operation)
        result['details']={'kernel':'explicit_vintage_current_tax_payment',
            'financial_result_sha256':financial_digest,'allocations':deepcopy(allocations)}
    vintage_invariant(result['after'],updated)
    return {**result,'tax_vintages':updated,'before_vintages_sha256':book.digest(vintages)}


def run(body):
    base={'profile':PROFILE,**FLAGS}
    try:
        protected();caller.bounded(body)
        core.closed(body,['profile','assessment_request','assessment_sha256','operations'],'continuation_request')
        require(body['profile']==PROFILE,'profile')
        require(body['assessment_sha256']==book.digest(body['assessment_request']),'assessment_digest')
        require(type(body['operations']) is list,'operations_list')
        prior=assessment.propose(body['assessment_request'])
        base.update(assessment_result=prior,request_sha256=book.digest(body),
            source_bundle_sha256=LOCK,implementation_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
        require(prior['status']=='proposed','assessment:'+prior['status'],prior['status'])
        current=deepcopy(prior['after']);vintages=deepcopy(prior['tax_vintages'])
        vintage_invariant(current,vintages)
        trace=[];status='complete_provisional';stop=None;unassessed=[]
        for index,operation in enumerate(body['operations']):
            try:
                result=transition(current,vintages,operation,prior['assessed_until'])
                trace.append({'operation':deepcopy(operation),'status':'proposed','result':result})
                current=result['after'];vintages=result['tax_vintages']
                if operation['kind']=='native':unassessed.append(operation['event']['event']['id'])
            except (continuation.Refused,continuation.lease.Refused,losses.Refused) as exc:
                status='stopped_provisional';stop={'index':index,'status':exc.status,'reason':exc.reason};break
            except (ValueError,TypeError,KeyError,AttributeError,AssertionError,OverflowError,RecursionError) as exc:
                status='stopped_provisional';stop={'index':index,'status':'invalid','reason':str(exc)[:350]};break
        report=carry.statements(prior['opening'],current,assessment.classes(prior['carry_result']))
        report.update(scope='Recorded continuation after first following-period tax',unresolved=deepcopy(UNRESOLVED))
        return {**base,'status':status,'conditional_current_assessed':True,
            'opening':deepcopy(prior['opening']),'after':current,'tax_vintages':vintages,
            'trace':trace,'stop':stop,'remaining_operations':deepcopy(body['operations'][len(trace):]),
            'assessed_until':prior['assessed_until'],'unassessed_native_events':unassessed,
            'loss_state':deepcopy(prior['loss_state']),'findings':deepcopy(prior['findings']),
            'current_period_tax':'conditionally_assessed','current_period_deferred_tax':'unassessed',
            'recorded_statements':report,'unresolved':deepcopy(UNRESOLVED)}
    except (continuation.Refused,continuation.lease.Refused,losses.Refused) as exc:
        return {**base,'status':exc.status,'reason':exc.reason}
    except (ValueError,TypeError,KeyError,AttributeError,OSError,AssertionError,OverflowError,RecursionError) as exc:
        return {**base,'status':'invalid','reason':str(exc)[:350]}


def apply(body,result):
    expected=run(body)
    try:
        require(expected['status'] in ['complete_provisional','stopped_provisional'],'no_valid_prefix')
        require(caller.canonical(result)==caller.canonical(expected),'complete_result_mismatch')
        return {**deepcopy(expected),'status':'applied_provisional'}
    except (ValueError,TypeError,RecursionError,OverflowError) as exc:
        return {'profile':PROFILE,**FLAGS,'status':'invalid','reason':str(exc)[:350]}
