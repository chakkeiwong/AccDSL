"""First conditional current tax after carry, with separate liability vintages."""
from copy import deepcopy
from datetime import timedelta
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json
import assessed_period_carry_v1 as carry
tax=carry.assessment.prior;losses=tax.losses;core=tax.core;book=tax.book;require=tax.require
ROOT=Path(__file__).resolve().parents[1];HERE=ROOT/'data/accounting-master/following-period-tax-20261024'
LOCK='fa3776f3a3f40ce81d420550e6424deaabd02d3bdc7dc21157ac0be2846a4f65'
PROFILE='FollowingPeriodCurrentTax/1';MODEL='first_period_accrual_no_credits_v1'
FLAGS={**carry.FLAGS,'conditional_current_assessed':False}
UNRESOLVED=['Actual source and accounting admission','Complete fiscal event coverage',
    'New-period deferred-tax assessment','Later payments and reassessment by tax vintage','Repeated carry and annual completeness']

def protected():
    raw=(HERE/'source-lock.json').read_bytes();require(sha256(raw).hexdigest()==LOCK,'source_lock_changed')
    for n,h in json.loads(raw).items():require(sha256((ROOT/n).read_bytes()).hexdigest()==h,'protected_source_changed:'+n)

def request(previous,identity,model,interval,information,allocations,loss_policy):
    return {'profile':PROFILE,'carry_request':deepcopy(previous),'carry_sha256':book.digest(previous),
        'id':identity,'model':deepcopy(model),'interval':deepcopy(interval),'information':deepcopy(information),
        'allocations':deepcopy(allocations),'loss_policy':deepcopy(loss_policy)}

def classes(result):return result['prior_result']['prior_result']['continuation_result']['native_report']['account_classes']

def population(result):
    states=[result['opening'],result['after']]+[t['result']['after'] for t in result['trace']]
    rights=sorted({(a['component']['lease_id'],r['right_id']) for s in states for a in s['leases'] for r in a['component']['rights']})
    c=classes(result)
    return {'pretax_accounts':[k for k in c['income'] if k not in ['current_tax','deferred_tax']],
        'basis_accounts':[k for k in c['assets']+c['liabilities'] if k not in ['dta','dtl']]+['income_tax_payable'],
        'lease_rights':[{'lease_id':a,'right_id':b} for a,b in rights]}

def carried_payments(result,body):
    opening=result['opening'];closing=result['after']
    require(opening['balances']['current_tax']==closing['balances']['current_tax']=='0/1','new_period_tax_already_recorded','unsupported')
    require(result['current_period_tax']=='unassessed','already_assessed','unsupported')
    p0=-Q(opening['balances']['income_tax_payable']);settlements=[]
    for t in result['trace']:
        if t['operation']['kind']=='tax_payment':
            e=t['operation']['event'];settlements.append({'event_id':e['id'],'date':e['date'],'amount':e['amount'],
                'operation_sha256':book.digest(t['operation']),'result_sha256':book.digest(t['result'])})
    paid=sum(Q(e['amount']) for e in settlements);remaining=p0-paid
    require(0<=paid<=p0 and remaining==-Q(closing['balances']['income_tax_payable']),'carried_payment_identity')
    flows=[f for f in closing['flows'] if f['origin']=='explicit_conditional_current_tax_payment']
    require([(f['event_id'],f['date'],Q(f['amount'])) for f in flows]==
            [(e['event_id'],e['date'],-Q(e['amount'])) for e in settlements],'payment_flow_identity')
    old_request=body['carry_request']['prior_request']['prior_request'];old_result=result['prior_result']['prior_result']
    return {'id':'carried:'+book.digest(old_request),'kind':'carried','assessment_id':old_request['id'],
        'interval':deepcopy(old_request['interval']),'assessment_request_sha256':book.digest(old_request),
        'assessment_result_sha256':book.digest(old_result),'opening_payable':book.fmt(p0),
        'new_assessment':'0/1','settlements':settlements,'closing_payable':book.fmt(remaining)}

def propose(body):
    base={'profile':PROFILE,**FLAGS}
    try:
        protected();carry.continuation.caller.bounded(body)
        core.closed(body,['profile','carry_request','carry_sha256','id','model','interval','information','allocations','loss_policy'],'new_tax_request')
        require(body['profile']==PROFILE,'profile');core.text(body['id'],'assessment_id')
        require(body['carry_sha256']==book.digest(body['carry_request']),'carry_digest')
        core.closed(body['model'],['profile','selected'],'model')
        require(body['model']['profile']==MODEL,'model_not_implemented','unsupported');losses.affirmative(body['model']['selected'],'model_selection')
        previous=carry.run(body['carry_request']);base.update(carry_result=previous,request_sha256=book.digest(body),
            source_bundle_sha256=LOCK,implementation_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
        require(previous['status']=='complete_provisional','carry_incomplete','unresolved' if previous['status']=='stopped_provisional' else previous['status'])
        opening=previous['opening'];closing=previous['after'];inventory=previous['loss_state'];interval=body['interval']
        core.closed(interval,['start','end_exclusive','activity_through'],'interval')
        start=core.scalar(interval['start'],'date');end=core.scalar(interval['end_exclusive'],'date');through=core.scalar(interval['activity_through'],'date')
        require(interval['start']==opening['period']['start']==inventory['cursor'],'opening_interval_mismatch')
        require(start<end<=core.scalar(closing['period']['end_exclusive'],'date'),'assessment_endpoint')
        require(through==end-timedelta(days=1) and core.scalar(closing['date'],'date')<=through,'activity_after_assessment')
        require(body['id'] not in closing['seen'] and body['id'] not in inventory['seen'],'duplicate_assessment')
        vintage=carried_payments(previous,body);pop=population(previous);values=tax.assess(body['information'],pop)
        for key in ['jurisdiction','regime']:require(values[key]==inventory[key],'tax_scope_changed:'+key)
        require(inventory['context']==closing['context'],'loss_context_changed')
        calc=tax.reconcile(closing,interval,values,pop,body['allocations'])
        digest=book.digest({'request_sha256':base['request_sha256'],'calculation':calc})
        loss_result=tax.replacement_losses(inventory,interval,calc,body['loss_policy'],body['id'],digest,inventory)
        loss_result['scope']='First assessment from actual carried loss opening; no provisional supersession'
        new=Q(loss_result['conditional_gross_current_tax']);remaining=Q(vintage['closing_payable'])
        after=deepcopy(closing);after['balances']['current_tax']=book.fmt(new)
        after['balances']['income_tax_payable']=book.fmt(-(remaining+new));after['date']=interval['activity_through'];after['seen'].append(body['id'])
        carry.continuation.invariant(after)
        journal={k:'0/1' for k in after['balances']};journal.update(current_tax=book.fmt(new),income_tax_payable=book.fmt(-new))
        require(sum(Q(v) for v in journal.values())==0,'journal_unbalanced')
        current={'id':'current:'+body['id'],'kind':'current','assessment_id':body['id'],'interval':deepcopy(interval),
            'assessment_request_sha256':base['request_sha256'],'opening_payable':'0/1','new_assessment':book.fmt(new),
            'settlements':[],'closing_payable':book.fmt(new)}
        vintages=[vintage,current];require(sum(Q(v['closing_payable']) for v in vintages)==-Q(after['balances']['income_tax_payable']),'vintage_sum')
        report=carry.statements(opening,after,classes(previous));report['scope']='Conditional first current-tax assessment in following period';report['unresolved']=deepcopy(UNRESOLVED)
        return {**base,'status':'proposed','conditional_current_assessed':True,'opening':deepcopy(opening),
            'after':after,'journal':journal,'population':pop,'calculation':calc,'loss_result':loss_result,
            'loss_state':deepcopy(loss_result['after']),'tax_vintages':vintages,'assessed_until':interval['end_exclusive'],
            'recorded_statements':report,'current_period_tax':'conditionally_assessed','current_period_deferred_tax':'unassessed',
            'findings':deepcopy(previous['findings']),'unresolved':deepcopy(UNRESOLVED)}
    except (carry.continuation.Refused,carry.continuation.lease.Refused,losses.Refused) as exc:
        return {**base,'status':exc.status,'reason':exc.reason}
    except (ValueError,TypeError,KeyError,AttributeError,OSError,RecursionError,OverflowError,AssertionError) as exc:
        return {**base,'status':'invalid','reason':str(exc)[:350]}

def apply(body,proposal):
    expected=propose(body)
    try:
        require(expected['status']=='proposed','no_proposal')
        require(carry.continuation.caller.canonical(proposal)==carry.continuation.caller.canonical(expected),'complete_proposal_mismatch')
        return {**deepcopy(expected),'status':'applied'}
    except (ValueError,TypeError,RecursionError,OverflowError) as exc:
        return {'profile':PROFILE,**FLAGS,'status':'invalid','reason':str(exc)[:350]}
