"""Cumulative following-period assessment retaining explicit vintage settlements."""
from copy import deepcopy
from datetime import timedelta
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json
import tax_vintage_continuation_v1 as continuation

first=continuation.assessment;tax=first.tax;losses=first.losses
book=first.book;core=first.core;require=first.require;carry=first.carry
ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/'data/accounting-master/following-tax-reassessment-20261024'
LOCK='ccb76ca52bb058474209d9eba524377ffe56c41cd5a9d415b69a009a352979eb'
PROFILE='FollowingPeriodTaxReassessment/1'
MODEL='cumulative_vintage_replacement_no_credits_v1'
FLAGS={**continuation.FLAGS,'conditional_current_assessed':False}
UNRESOLVED=['Actual source and accounting admission','Complete fiscal event coverage',
    'New-period deferred recognition','Subsequent continuation and repeated reassessment',
    'Credit/refund representation','Repeated carry and annual completeness']


def protected():
    raw=(HERE/'source-lock.json').read_bytes()
    require(sha256(raw).hexdigest()==LOCK,'source_lock_changed')
    for name,h in json.loads(raw).items():
        require(sha256((ROOT/name).read_bytes()).hexdigest()==h,'protected_source_changed:'+name)


def request(previous,identity,model,interval,information,allocations,loss_policy):
    return {'profile':PROFILE,'continuation_request':deepcopy(previous),
        'continuation_sha256':book.digest(previous),'id':identity,'model':deepcopy(model),
        'interval':deepcopy(interval),'information':deepcopy(information),
        'allocations':deepcopy(allocations),'loss_policy':deepcopy(loss_policy)}


def population(result):
    pop=first.population(result['assessment_result']['carry_result'])
    states=[result['opening'],result['assessment_result']['after'],result['after']]
    states += [t['result']['after'] for t in result['trace']]
    rights={(r['lease_id'],r['right_id']) for r in pop['lease_rights']}
    rights.update((a['component']['lease_id'],r['right_id']) for s in states
                  for a in s['leases'] for r in a['component']['rights'])
    pop['lease_rights']=[{'lease_id':a,'right_id':b} for a,b in sorted(rights)]
    return pop


def propose(body):
    base={'profile':PROFILE,**FLAGS}
    try:
        protected();continuation.caller.bounded(body)
        core.closed(body,['profile','continuation_request','continuation_sha256','id',
            'model','interval','information','allocations','loss_policy'],'reassessment_request')
        require(body['profile']==PROFILE,'profile');core.text(body['id'],'assessment_id')
        require(body['continuation_sha256']==book.digest(body['continuation_request']),'continuation_digest')
        core.closed(body['model'],['profile','selected'],'model')
        require(body['model']['profile']==MODEL,'model_not_implemented','unsupported')
        losses.affirmative(body['model']['selected'],'model_selection')
        prior=continuation.run(body['continuation_request'])
        base.update(continuation_result=prior,request_sha256=book.digest(body),
            source_bundle_sha256=LOCK,implementation_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
        require(prior['status']=='complete_provisional','continuation_incomplete',
            'unresolved' if prior['status']=='stopped_provisional' else prior['status'])
        initial=prior['assessment_result'];opening=prior['opening'];closing=prior['after']
        original=initial['carry_result']['loss_state'];superseded=prior['loss_state']
        interval=body['interval'];core.closed(interval,['start','end_exclusive','activity_through'],'interval')
        start,end,through=[core.scalar(interval[k],'date') for k in ['start','end_exclusive','activity_through']]
        require(interval['start']==opening['period']['start']==original['cursor'],'cumulative_start')
        require(start<end and core.scalar(prior['assessed_until'],'date')<=end<=core.scalar(closing['period']['end_exclusive'],'date'),'assessment_endpoint')
        require(through==end-timedelta(days=1),'exclusive_endpoint')
        require(core.scalar(closing['date'],'date')<=through,'recorded_events_after_assessment')
        require(body['id'] not in closing['seen'] and body['id'] not in original['seen']
            and body['id'] not in superseded['seen'],'reused_assessment_id')
        pop=population(prior);values=tax.assess(body['information'],pop)
        for key in ['jurisdiction','regime']:require(values[key]==original[key],'tax_scope_changed:'+key)
        require(original['context']==closing['context'],'loss_context_changed')
        calculation=tax.reconcile(closing,interval,values,pop,body['allocations'])
        calc_digest=book.digest({'request_sha256':base['request_sha256'],'calculation':calculation})
        loss_result=tax.replacement_losses(original,interval,calculation,body['loss_policy'],body['id'],calc_digest,superseded)
        old_v,current_v=prior['tax_vintages'];old=Q(closing['balances']['current_tax'])
        require(current_v['opening_payable']=='0/1' and Q(current_v['new_assessment'])==old,'current_vintage_expense_identity')
        paid=sum(Q(s['amount']) for s in current_v['settlements'])
        new=Q(loss_result['conditional_gross_current_tax']);delta=new-old
        remaining=new-paid;old_remaining=Q(old_v['closing_payable'])
        financial={'previous_expense':book.fmt(old),'replacement_expense':book.fmt(new),
            'current_vintage_paid':book.fmt(paid),'carried_remaining':book.fmt(old_remaining),
            'incremental_expense':book.fmt(delta),'replacement_current_payable':book.fmt(remaining),
            'replacement_total_payable':book.fmt(old_remaining+remaining)}
        base.update(population=pop,calculation=calculation,financial_calculation=financial,
            replacement_loss_result=loss_result,original_loss_opening_sha256=book.digest(original))
        require(remaining>=0,'current_tax_receivable_or_refund_route_required','unsupported')
        after=deepcopy(closing);after['balances']['current_tax']=book.fmt(new)
        after['balances']['income_tax_payable']=book.fmt(-(old_remaining+remaining))
        after['date']=interval['activity_through'];after['seen'].append(body['id'])
        journal={k:'0/1' for k in after['balances']}
        journal.update(current_tax=book.fmt(delta),income_tax_payable=book.fmt(-delta))
        require(sum(Q(v) for v in journal.values())==0,'journal_unbalanced')
        updated=deepcopy(current_v)
        updated.update(assessment_id=body['id'],interval=deepcopy(interval),
            assessment_request_sha256=base['request_sha256'],new_assessment=book.fmt(new),
            closing_payable=book.fmt(remaining))
        updated['supersession_history']=[{'previous_vintage':deepcopy(current_v),
            'previous_loss_state_sha256':book.digest(superseded),
            'previous_assessment_result_sha256':book.digest(initial),
            'replacement_assessment_id':body['id'],'replacement_request_sha256':base['request_sha256']}]
        vintages=[deepcopy(old_v),updated];continuation.vintage_invariant(after,vintages)
        report=carry.statements(opening,after,first.classes(initial['carry_result']))
        report.update(scope='Conditional cumulative following-period current tax',unresolved=deepcopy(UNRESOLVED))
        return {**base,'status':'proposed','conditional_current_assessed':True,'opening':deepcopy(opening),
            'after':after,'journal':journal,'tax_vintages':vintages,'recorded_statements':report,
            'loss_state':deepcopy(loss_result['after']),'assessed_until':interval['end_exclusive'],
            'unassessed_native_events':[],'findings':deepcopy(prior['findings']),
            'current_period_tax':'conditionally_assessed','current_period_deferred_tax':'unassessed',
            'superseded':{'assessment_request_sha256':book.digest(body['continuation_request']['assessment_request']),
                'assessment_end_exclusive':prior['assessed_until'],'loss_state_sha256':book.digest(superseded),
                'tax_vintages_sha256':book.digest(prior['tax_vintages'])},'unresolved':deepcopy(UNRESOLVED)}
    except (carry.continuation.Refused,carry.continuation.lease.Refused,losses.Refused) as exc:
        return {**base,'status':exc.status,'reason':exc.reason}
    except (ValueError,TypeError,KeyError,AttributeError,OSError,AssertionError,OverflowError,RecursionError) as exc:
        return {**base,'status':'invalid','reason':str(exc)[:350]}


def apply(body,proposal):
    expected=propose(body)
    try:
        require(expected['status']=='proposed','proposal_not_available')
        require(continuation.caller.canonical(proposal)==continuation.caller.canonical(expected),'complete_proposal_mismatch')
        return {**deepcopy(expected),'status':'applied'}
    except (ValueError,TypeError,RecursionError,OverflowError) as exc:
        return {'profile':PROFILE,**FLAGS,'status':'invalid','reason':str(exc)[:350]}
