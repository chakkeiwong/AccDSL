"""Continue a provisional period without replaying historical tax settlements."""
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json
import second_assessed_carry_v1 as boundary

book=boundary.book; core=boundary.core; losses=boundary.losses
require=boundary.require; carry=boundary.carry
continuation=carry.continuation; caller=continuation.caller
ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/'data/accounting-master/period-vintage-continuation-20261024'
LOCK='c2fbe817b6a41c7c57401a0644fe53cbd97672144cdc8df55a1143d829a918fe'
PROFILE='PeriodVintageContinuation/1'
FLAGS={**boundary.FLAGS,'recorded_balance_carry':True}
UNRESOLVED=['Actual source and accounting admission','Complete fiscal event coverage',
    'Current-period current and deferred assessment',
    'Reusable multi-vintage annual interface and annual completeness']


def protected():
    raw=(HERE/'source-lock.json').read_bytes()
    require(sha256(raw).hexdigest()==LOCK,'source_lock_changed')
    for name,h in json.loads(raw).items():
        require(sha256((ROOT/name).read_bytes()).hexdigest()==h,'protected_source_changed:'+name)


def request(previous,operations):
    return {'profile':PROFILE,'boundary_request':deepcopy(previous),
        'boundary_sha256':book.digest(previous),'operations':deepcopy(operations)}


def period_invariant(state,historical,vintages):
    continuation.invariant(state)
    require(type(vintages) is list and len(vintages)==len(historical),'period_vintage_population')
    require([v['id'] for v in vintages]==[v['id'] for v in historical],'period_vintage_identity')
    require(len({v['id'] for v in vintages})==len(vintages),'duplicate_period_vintage')
    payments={}
    for old,v in zip(historical,vintages):
        core.closed(v,['id','prior_vintage_sha256','period','opening_payable','settlements','closing_payable'],'period_vintage')
        require(v['prior_vintage_sha256']==book.digest(old),'historical_vintage_digest')
        require(v['period']==state['period'],'vintage_period')
        opening=losses.tax.numeric(v['opening_payable']);closing=losses.tax.numeric(v['closing_payable'])
        require(v['opening_payable']==old['closing_payable'],'vintage_opening_amount')
        require(min(opening,closing)>=0,'negative_vintage_balance')
        require(type(v['settlements']) is list,'settlements_list')
        paid=Q(0);seen=set();last=None
        for s in v['settlements']:
            core.closed(s,['event_id','date','amount','payment_amount','operation_sha256','financial_result_sha256'],'settlement')
            key=s['event_id'];core.text(key,'event_id')
            day=core.scalar(s['date'],'date');amount=losses.tax.numeric(s['amount'])
            total=losses.tax.numeric(s['payment_amount'])
            require(key not in seen and key in state['seen'],'settlement_identity')
            require(amount>0 and total>=amount,'positive_settlement_required')
            require(core.scalar(state['period']['start'],'date')<=day<=core.scalar(state['date'],'date'),'settlement_date')
            require(last is None or last<=day,'settlement_chronology')
            for name in ['operation_sha256','financial_result_sha256']:
                h=s[name]
                require(type(h) is str and len(h)==64 and all(c in '0123456789abcdef' for c in h),'settlement_digest')
            metadata=(s['date'],total,s['operation_sha256'],s['financial_result_sha256'])
            if key not in payments:payments[key]={'metadata':metadata,'amount':Q(0)}
            require(payments[key]['metadata']==metadata,'settlement_metadata_mismatch')
            payments[key]['amount']+=amount;seen.add(key);last=day;paid+=amount
        require(opening-paid==closing,'period_vintage_conservation')
    require(sum(Q(v['closing_payable']) for v in vintages)==-Q(state['balances']['income_tax_payable']),'aggregate_vintage_payable')
    flows=[f for f in state['flows'] if f['origin']=='explicit_conditional_current_tax_payment']
    require(len(flows)==len({f['event_id'] for f in flows}),'duplicate_tax_flow')
    require({f['event_id'] for f in flows}==set(payments),'settlement_flow_population')
    for f in flows:
        payment=payments[f['event_id']];day,total,_,_=payment['metadata']
        require(payment['amount']==total,'settlement_total_mismatch')
        require(f['activity']=='operating' and f['date']==day and -Q(f['amount'])==total,'settlement_flow_amount_or_date')
    return vintages


def transition(state,historical,vintages,operation):
    period_invariant(state,historical,vintages);core.closed(operation,['kind','event'],'operation')
    updated=deepcopy(vintages);kind=operation['kind']
    if kind=='native':
        result=continuation.transition(state,operation,state['period']['start'])
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
        kernel={'kind':'tax_payment','event':{k:deepcopy(v) for k,v in event.items() if k!='allocations'}}
        result=continuation.transition(state,kernel,state['period']['start'])
        financial_digest=book.digest(result)
        for a in allocations:
            v=by_id[a['vintage_id']]
            v['closing_payable']=book.fmt(Q(v['closing_payable'])-Q(a['amount']))
            v['settlements'].append({'event_id':event['id'],'date':event['date'],
                'amount':book.fmt(Q(a['amount'])),'payment_amount':book.fmt(total),
                'operation_sha256':book.digest(operation),'financial_result_sha256':financial_digest})
        result['operation_sha256']=book.digest(operation)
        result['details']={'kernel':'explicit_period_vintage_tax_payment',
            'financial_result_sha256':financial_digest,'allocations':deepcopy(allocations)}
    period_invariant(result['after'],historical,updated)
    return {**result,'period_vintages':updated,'before_vintages_sha256':book.digest(vintages),
        'historical_vintages_sha256':book.digest(historical)}


def run(body):
    base={'profile':PROFILE,**FLAGS}
    try:
        protected();caller.bounded(body)
        core.closed(body,['profile','boundary_request','boundary_sha256','operations'],'continuation_request')
        require(body['profile']==PROFILE,'profile')
        require(body['boundary_sha256']==book.digest(body['boundary_request']),'boundary_digest')
        require(type(body['operations']) is list,'operations_list')
        prior=boundary.run(body['boundary_request'])
        base.update(boundary_result=prior,request_sha256=book.digest(body),
            source_bundle_sha256=LOCK,implementation_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
        require(prior['status']=='complete_provisional','boundary:'+prior['status'],prior['status'])
        current=deepcopy(prior['after']);historical=deepcopy(prior['tax_vintages'])
        vintages=deepcopy(prior['period_vintages']);period_invariant(current,historical,vintages)
        trace=[];status='complete_provisional';stop=None;unassessed=[]
        for index,operation in enumerate(body['operations']):
            try:
                result=transition(current,historical,vintages,operation)
                trace.append({'operation':deepcopy(operation),'status':'proposed','result':result})
                current=result['after'];vintages=result['period_vintages']
                if operation['kind']=='native':unassessed.append(operation['event']['event']['id'])
            except (continuation.Refused,continuation.lease.Refused,losses.Refused) as exc:
                status='stopped_provisional';stop={'index':index,'status':exc.status,'reason':exc.reason};break
            except (ValueError,TypeError,KeyError,AttributeError,AssertionError,OverflowError,RecursionError) as exc:
                status='stopped_provisional';stop={'index':index,'status':'invalid','reason':str(exc)[:350]};break
        report=carry.statements(prior['opening'],current,boundary.classes(prior['prior_result']))
        report.update(scope='Recorded period-aware continuation after second provisional opening',unresolved=deepcopy(UNRESOLVED))
        preserved={k:deepcopy(prior[k]) for k in ['opening','loss_state','findings','finding_status',
            'prior_findings','archive','current_period_tax','current_period_deferred_tax']}
        return {**base,**preserved,'status':status,'after':current,
            'tax_vintages':historical,'period_vintages':vintages,'trace':trace,'stop':stop,
            'remaining_operations':deepcopy(body['operations'][len(trace):]),
            'unassessed_native_events':unassessed,'recorded_statements':report,'unresolved':deepcopy(UNRESOLVED)}
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
