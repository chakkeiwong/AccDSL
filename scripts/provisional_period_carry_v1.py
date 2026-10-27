"""Provisional recorded-balance carry; unresolved obligations survive execution."""
from copy import deepcopy
from datetime import timedelta
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json
import shared_tax_reassessment_v1 as assessment

continuation=assessment.continuation
book=assessment.book
core=assessment.core
losses=assessment.losses
require=assessment.require
ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/'data/accounting-master/provisional-period-carry-20261024'
LOCK='c7aef4327f6fec656e86da5c9a35e4c58c366103d0b7fbb734c0135122eb06b5'
PROFILE='ProvisionalSharedPeriodCarry/1'
MODEL='provisional_recorded_balance_carry_v1'
FINDINGS=['event_coverage','deferred_tax_assessment','source_admission','accounting_admission']
OBLIGATIONS=['Actual fiscal event coverage is not established',
             'Deferred-tax balances are carried recorded amounts; reassessment is pending',
             'Actual source and accounting admission remain pending',
             'New-period tax assessment and repeated period carry are not implemented']
FLAGS={**assessment.FLAGS,'provisional':True,'recorded_balance_carry':False,
       'annual_close_ready':False,'complete_financial_statements':False}


def protected():
    raw=(HERE/'source-lock.json').read_bytes()
    require(sha256(raw).hexdigest()==LOCK,'source_lock_changed')
    for name,h in json.loads(raw).items():
        require(sha256((ROOT/name).read_bytes()).hexdigest()==h,'protected_source_changed:'+name)


def request(prior,identity,model,next_period,findings,operations):
    return {'profile':PROFILE,'prior_request':deepcopy(prior),'prior_sha256':book.digest(prior),
            'id':identity,'model':deepcopy(model),'next_period':deepcopy(next_period),
            'findings':deepcopy(findings),'operations':deepcopy(operations)}


def findings_status(findings):
    core.closed(findings,FINDINGS,'carry_findings');status={}
    for key in FINDINGS:
        value=losses.declaration(findings[key],'boolean')
        status[key]='unresolved' if value is None else 'asserted_true' if value else 'asserted_false'
    return status


def opening_state(body,prior):
    closing=prior['after'];period=body['next_period']
    core.closed(period,['start','end_exclusive'],'next_period')
    start=core.scalar(period['start'],'date');end=core.scalar(period['end_exclusive'],'date')
    require(period['start']==closing['period']['end_exclusive'],'noncontiguous_next_period')
    require(end>start,'next_period_end')
    require(prior['assessed_until']==period['start']==prior['loss_state']['cursor'],
            'current_tax_or_loss_interval_incomplete','unresolved')
    require(core.scalar(closing['date'],'date')==start-timedelta(days=1),'closing_day_not_complete')
    require(body['id'] not in closing['seen'],'duplicate_carry_id')
    classes=prior['continuation_result']['native_report']['account_classes']
    profit=-sum(Q(closing['balances'][k]) for k in classes['income'])
    require(profit==Q(prior['recorded_statements']['recorded_profit']),'closing_profit_mismatch')
    new=deepcopy(closing);new['balances']['retained']=book.fmt(Q(closing['balances']['retained'])-profit)
    for key in classes['income']:new['balances'][key]='0/1'
    journal={key:book.fmt(Q(new['balances'][key])-Q(closing['balances'][key])) for key in new['balances']}
    require(sum(Q(v) for v in journal.values())==0,'carry_journal_unbalanced')
    new['period']=deepcopy(period);new['date']=period['start'];new['tax_closed_until']=period['start']
    new['flows']=[];new['tax_adjustments']=[];new['opening_interest_paid']='0/1'
    new['tax_premises']['opening_dta']=new['balances']['dta']
    new['tax_premises']['opening_dtl']=book.fmt(-Q(new['balances']['dtl']))
    new['seen'].append(body['id'])
    new['prior_years'].append({'period':deepcopy(closing['period']),
        'closing_sha256':book.digest(closing),'report_sha256':book.digest(prior['recorded_statements'])})
    continuation.invariant(new)
    return new,journal,book.fmt(profit)


def statements(opening,closing,classes):
    categories=deepcopy(classes);categories['liabilities'].append('income_tax_payable')
    flat=sum(categories.values(),[])
    require(len(flat)==len(set(flat)) and set(flat)==set(closing['balances']),'account_classification')
    b0=opening['balances'];b=closing['balances']
    require(all(b0[k]=='0/1' for k in categories['income']),'new_opening_income_not_zero')
    profit=-sum(Q(b[k]) for k in categories['income'])
    opening_equity=-sum(Q(b0[k]) for k in categories['equity'])
    equity=-sum(Q(b[k]) for k in categories['equity'])+profit
    assets=sum(Q(b[k]) for k in categories['assets']);liabilities=-sum(Q(b[k]) for k in categories['liabilities'])
    cf={}
    for activity in ['operating','investing','financing']:
        amounts=[Q(f['amount']) for f in closing['flows'] if f['activity']==activity]
        cf[activity]={'receipts':book.fmt(sum(v for v in amounts if v>=0)),
                      'payments':book.fmt(-sum(v for v in amounts if v<0)),
                      'net':book.fmt(sum(amounts))}
    bridge={'profit':profit,'depreciation':Q(b['depreciation']),'deferred_tax':Q(b['deferred_tax']),
            'remove_lease_gain':Q(b['other_gains']),'opening_interest_paid':-Q(closing['opening_interest_paid'])}
    for k in assessment.info.reports.WORKING_CAPITAL+['income_tax_payable']:
        bridge['change_'+k]=-(Q(b[k])-Q(b0[k]))
    cash=Q(b['cash'])-Q(b0['cash']);indirect=sum(bridge.values())
    ties={'balance_sheet':assets-liabilities-equity,'equity':opening_equity+profit-equity,
          'direct_cash':cash-sum(Q(x['net']) for x in cf.values()),'indirect_cash':indirect-Q(cf['operating']['net'])}
    require(all(v==0 for v in ties.values()),'statement_reconciliation')
    return {'scope':'provisional following-period completed prefix','period':deepcopy(closing['period']),
        'balance_sheet':{'total_assets':book.fmt(assets),'total_liabilities':book.fmt(liabilities),
                         'equity_including_profit':book.fmt(equity)},
        'recorded_profit':book.fmt(profit),'opening_equity':book.fmt(opening_equity),
        'cash_flows':{'activities':cf,'opening_cash':b0['cash'],'closing_cash':b['cash'],
                      'net_movement':book.fmt(cash),'gross_origins':deepcopy(closing['flows'])},
        'indirect_operating':{'items':{k:book.fmt(v) for k,v in bridge.items()},'net':book.fmt(indirect)},
        'reconciliations':{k:book.fmt(v) for k,v in ties.items()},'unresolved':deepcopy(OBLIGATIONS)}


def run(body):
    base={'profile':PROFILE,**FLAGS}
    try:
        protected();continuation.caller.bounded(body)
        core.closed(body,['profile','prior_request','prior_sha256','id','model','next_period','findings','operations'],'carry_request')
        require(body['profile']==PROFILE,'profile');core.text(body['id'],'carry_id')
        require(body['prior_sha256']==book.digest(body['prior_request']),'prior_digest')
        core.closed(body['model'],['profile','selected'],'carry_model')
        require(body['model']['profile']==MODEL,'strict_annual_or_other_carry_not_implemented','unsupported')
        losses.affirmative(body['model']['selected'],'provisional_carry_selected')
        finding_status=findings_status(body['findings'])
        require(type(body['operations']) is list,'operations_list')
        prior=assessment.propose(body['prior_request'])
        base.update(request_sha256=book.digest(body),prior_result=prior,
                    source_bundle_sha256=LOCK,implementation_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
        require(prior['status']=='proposed','prior:'+prior['status'],prior['status'])
        opening,journal,profit=opening_state(body,prior);current=deepcopy(opening)
        trace=[];status='complete_provisional';stop=None
        for index,operation in enumerate(body['operations']):
            try:
                result=continuation.transition(current,operation,opening['period']['start'])
                trace.append({'operation':deepcopy(operation),'status':'proposed','result':result});current=result['after']
            except (continuation.Refused,continuation.lease.Refused,losses.Refused) as exc:
                status='stopped_provisional';stop={'index':index,'status':exc.status,'reason':exc.reason};break
            except (ValueError,TypeError,KeyError,AttributeError,AssertionError,OverflowError,RecursionError) as exc:
                status='stopped_provisional';stop={'index':index,'status':'invalid','reason':str(exc)[:350]};break
        report=statements(opening,current,prior['continuation_result']['native_report']['account_classes'])
        return {**base,'recorded_balance_carry':True,'status':status,'opening':opening,'after':current,'carry_journal':journal,
            'carried_recorded_profit':profit,'loss_state':deepcopy(prior['loss_state']),
            'findings':deepcopy(body['findings']),'finding_status':finding_status,'unresolved':deepcopy(OBLIGATIONS),
            'trace':trace,'stop':stop,'remaining_operations':deepcopy(body['operations'][len(trace):]),
            'recorded_statements':report,'current_period_tax':'unassessed',
            'archive':{'prior_result_sha256':book.digest(prior),'closing_sha256':book.digest(prior['after']),
                       'report_sha256':book.digest(prior['recorded_statements']),
                       'prior_flows':deepcopy(prior['after']['flows']),
                       'prior_tax_adjustments':deepcopy(prior['after']['tax_adjustments']),
                       'interpretation':'retained recorded history; not a certified annual close'}}
    except (continuation.Refused,continuation.lease.Refused,losses.Refused) as exc:
        return {**base,'status':exc.status,'reason':exc.reason}
    except (ValueError,TypeError,KeyError,AttributeError,AssertionError,OSError,RecursionError,OverflowError) as exc:
        return {**base,'status':'invalid','reason':str(exc)[:350]}


def apply(body,result):
    expected=run(body)
    try:
        require(expected['status'] in ['complete_provisional','stopped_provisional'],'no_provisional_prefix')
        require(continuation.caller.canonical(result)==continuation.caller.canonical(expected),'complete_result_mismatch')
        return {'profile':PROFILE,**FLAGS,'recorded_balance_carry':True,'status':'applied_provisional','opening':deepcopy(expected['opening']),
                'after':deepcopy(expected['after']),'loss_state':deepcopy(expected['loss_state']),
                'findings':deepcopy(expected['findings']),'unresolved':deepcopy(expected['unresolved']),
                'archive':deepcopy(expected['archive']),'prior_result':deepcopy(expected['prior_result']),
                'request_sha256':expected['request_sha256'],
                'current_period_tax':'unassessed','stop':deepcopy(expected['stop'])}
    except (ValueError,TypeError,RecursionError,OverflowError) as exc:
        return {'profile':PROFILE,**FLAGS,'status':'invalid','reason':str(exc)[:350]}
