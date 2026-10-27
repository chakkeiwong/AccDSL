"""Second provisional boundary retaining lifetime tax and recognition history."""
from copy import deepcopy
from datetime import timedelta
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json
import following_deferred_assessment_v1 as assessment

prior=assessment.prior;book=assessment.book;core=assessment.core
losses=assessment.losses;require=assessment.require;carry=prior.carry
ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/'data/accounting-master/second-assessed-carry-20261024'
LOCK='eb83f144b69da8d87d9bd017289f361f182832437472596d8f8e08e5730362ac'
PROFILE='SecondAssessedProvisionalCarry/1'
MODEL='provisional_boundary_with_vintage_openings_v1'
FINDINGS=carry.FINDINGS
FLAGS={**assessment.FLAGS,'conditional_current_assessed':False,
    'conditional_deferred_assessed':False,'deferred_asset_recognized':False,'recorded_balance_carry':False}
UNRESOLVED=['Actual source and accounting admission','Complete fiscal event coverage',
    'New-period current and deferred assessment','Compatible period-vintage event continuation',
    'General repeated annual execution and annual completeness']

def protected():
    raw=(HERE/'source-lock.json').read_bytes()
    require(sha256(raw).hexdigest()==LOCK,'source_lock_changed')
    for name,h in json.loads(raw).items():
        require(sha256((ROOT/name).read_bytes()).hexdigest()==h,'protected_source_changed:'+name)

def request(previous,identity,model,next_period,findings):
    return {'profile':PROFILE,'prior_request':deepcopy(previous),'prior_sha256':book.digest(previous),
        'id':identity,'model':deepcopy(model),'next_period':deepcopy(next_period),'findings':deepcopy(findings)}

def classes(result):
    initial=result['prior_result']['continuation_result']['assessment_result']
    return prior.first.classes(initial['carry_result'])

def period_opening_invariant(state,historical,period_vintages):
    carry.continuation.invariant(state)
    require(type(period_vintages) is list and len(period_vintages)==len(historical),'period_vintage_population')
    require([v['id'] for v in period_vintages]==[v['id'] for v in historical],'period_vintage_identity')
    require(len({v['id'] for v in period_vintages})==len(period_vintages),'duplicate_period_vintage')
    for old,new in zip(historical,period_vintages):
        core.closed(new,['id','prior_vintage_sha256','period','opening_payable','settlements','closing_payable'],'period_vintage')
        require(new['prior_vintage_sha256']==book.digest(old),'historical_vintage_digest')
        require(new['period']==state['period'],'vintage_period')
        amount=Q(old['closing_payable'])
        require(amount>=0 and new['opening_payable']==new['closing_payable']==book.fmt(amount),'vintage_opening_amount')
        require(new['settlements']==[],'boundary_has_new_settlements')
    require(sum(Q(v['opening_payable']) for v in period_vintages)==-Q(state['balances']['income_tax_payable']),'opening_vintage_sum')
    require(state['flows']==[] and state['tax_adjustments']==[],'boundary_has_new_movements')
    return period_vintages

def run(body):
    base={'profile':PROFILE,**FLAGS}
    try:
        protected();prior.continuation.caller.bounded(body)
        core.closed(body,['profile','prior_request','prior_sha256','id','model','next_period','findings'],'carry_request')
        require(body['profile']==PROFILE,'profile');core.text(body['id'],'carry_id')
        require(body['prior_sha256']==book.digest(body['prior_request']),'prior_digest')
        core.closed(body['model'],['profile','selected'],'model')
        require(body['model']['profile']==MODEL,'model_not_implemented','unsupported')
        losses.affirmative(body['model']['selected'],'provisional_carry_selection')
        finding_status=carry.findings_status(body['findings'])
        previous=assessment.propose(body['prior_request'])
        base.update(prior_result=previous,request_sha256=book.digest(body),
            source_bundle_sha256=LOCK,implementation_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
        require(previous['status']=='proposed','prior:'+previous['status'],previous['status'])
        closing=previous['after'];period=body['next_period']
        core.closed(period,['start','end_exclusive'],'next_period')
        start=core.scalar(period['start'],'date');end=core.scalar(period['end_exclusive'],'date')
        require(period['start']==closing['period']['end_exclusive'],'noncontiguous_next_period')
        require(start<end,'next_period_end')
        require(previous['assessed_until']==period['start']==previous['loss_state']['cursor'],'assessment_or_loss_incomplete','unresolved')
        require(previous['current_period_tax']==previous['current_period_deferred_tax']=='conditionally_assessed','assessments_incomplete','unresolved')
        require(core.scalar(closing['date'],'date')==start-timedelta(days=1),'closing_day_incomplete')
        require(body['id'] not in closing['seen'],'duplicate_carry_id')
        prior.continuation.vintage_invariant(closing,previous['tax_vintages'])
        categories=classes(previous);profit=-sum(Q(closing['balances'][k]) for k in categories['income'])
        require(profit==Q(previous['recorded_statements']['recorded_profit']),'closing_profit_mismatch')
        new=deepcopy(closing);new['balances']['retained']=book.fmt(Q(closing['balances']['retained'])-profit)
        for key in categories['income']:new['balances'][key]='0/1'
        journal={k:book.fmt(Q(new['balances'][k])-Q(v)) for k,v in closing['balances'].items()}
        require(sum(Q(v) for v in journal.values())==0,'carry_journal_unbalanced')
        new['period']=deepcopy(period);new['date']=period['start'];new['tax_closed_until']=period['start']
        new['flows']=[];new['tax_adjustments']=[];new['opening_interest_paid']='0/1'
        new['tax_premises']['opening_dta']=new['balances']['dta']
        new['tax_premises']['opening_dtl']=book.fmt(-Q(new['balances']['dtl']))
        new['seen'].append(body['id'])
        new['prior_years'].append({'period':deepcopy(closing['period']),
            'closing_sha256':book.digest(closing),'report_sha256':book.digest(previous['recorded_statements'])})
        historical=deepcopy(previous['tax_vintages'])
        period_vintages=[{'id':v['id'],'prior_vintage_sha256':book.digest(v),'period':deepcopy(period),
            'opening_payable':v['closing_payable'],'settlements':[],'closing_payable':v['closing_payable']} for v in historical]
        period_opening_invariant(new,historical,period_vintages)
        report=carry.statements(new,new,categories)
        report.update(scope='Second provisional financial opening; no new-period events',unresolved=deepcopy(UNRESOLVED))
        return {**base,'status':'complete_provisional','recorded_balance_carry':True,
            'opening':new,'after':deepcopy(new),'carry_journal':journal,'carried_recorded_profit':book.fmt(profit),
            'loss_state':deepcopy(previous['loss_state']),'tax_vintages':historical,'period_vintages':period_vintages,
            'findings':deepcopy(body['findings']),'finding_status':finding_status,
            'prior_findings':{'carry':deepcopy(previous['prior_findings']),'deferred':deepcopy(previous['findings'])},
            'current_period_tax':'unassessed','current_period_deferred_tax':'unassessed',
            'recorded_statements':report,'unresolved':deepcopy(UNRESOLVED),
            'archive':{'prior_result_sha256':book.digest(previous),'closing_sha256':book.digest(closing),
                'report_sha256':book.digest(previous['recorded_statements']),
                'prior_period':deepcopy(closing['period']),'prior_flows':deepcopy(closing['flows']),
                'prior_tax_adjustments':deepcopy(closing['tax_adjustments']),
                'recognition_calculation':deepcopy(previous['calculation']),
                'recognition_findings':deepcopy(previous['findings']),
                'recognition_capacity':deepcopy(previous['recovery_capacity']),
                'recognition_measurement':deepcopy(previous['measurement']),
                'earlier_recognition':deepcopy(previous['historical_recognition']),
                'interpretation':'Historical assessed closing book; no renewed capacity or annual acceptance'}}
    except (carry.continuation.Refused,carry.continuation.lease.Refused,losses.Refused) as exc:
        return {**base,'status':exc.status,'reason':exc.reason}
    except (ValueError,TypeError,KeyError,AttributeError,OSError,AssertionError,OverflowError,RecursionError) as exc:
        return {**base,'status':'invalid','reason':str(exc)[:350]}

def apply(body,result):
    expected=run(body)
    try:
        require(expected['status']=='complete_provisional','no_provisional_opening')
        require(prior.continuation.caller.canonical(result)==prior.continuation.caller.canonical(expected),'complete_result_mismatch')
        return {**deepcopy(expected),'status':'applied_provisional'}
    except (ValueError,TypeError,RecursionError,OverflowError) as exc:
        return {'profile':PROFILE,**FLAGS,'status':'invalid','reason':str(exc)[:350]}
