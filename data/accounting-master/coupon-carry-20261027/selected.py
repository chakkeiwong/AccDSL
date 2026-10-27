"""Explicit all-preserve carry bound to an externally verified coupon record."""
from copy import deepcopy as cp
from pathlib import Path
from datetime import date,timedelta
import sys
R=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(R/'scripts'))
import company_book_carry_v1 as carry
core=carry.core;identity=core.digest
FLAGS=dict(source_admission=False,accounting_admission=False,fiscal_admission=False,production_ready=False,durable=False)

def request(record,rid,close_id,next_end):
    book=record['execution']['current'];body=record['program']
    rr=carry.reports.request(body['opening'],book,body['schemas'],body['mapping'])
    policies={p:dict(kind='preserve',provenance='Selected coupon history: preserve every supplied leaf') for p in book['memory_types']}
    out=carry.request(rr,close_id,record['mapping']['capital'],next_end,policies)
    return dict(profile='SelectedUnpaidCouponCarryRequest/1',record_sha256=rid,carry=out)

def propose(record,rid,req):
    base=dict(profile='SelectedUnpaidCouponCarry/1',**FLAGS,record_sha256=rid,request_sha256=identity(req))
    try:
        core.need(identity(record)==rid,'external_verified_record_identity')
        core.need(set(req)=={'profile','record_sha256','carry'} and req['profile']=='SelectedUnpaidCouponCarryRequest/1' and req['record_sha256']==rid,'request_binding')
        prior=record['execution'];book=prior['current'];body=record['program'];arg=req['carry'];rr=arg['report_request']
        core.need(prior['status'] in ('stopped_provisional','complete_provisional'),'upstream_execution_scope')
        core.need(rr==carry.reports.request(body['opening'],book,body['schemas'],body['mapping']),'exact_record_report_request')
        core.need(arg['expected_report_sha256']==identity(record['report']),'exact_verified_report')
        core.need(arg['retained_account']==record['mapping']['capital'],'selected_retained_account')
        core.need(set(arg['memory_policies'])==set(book['memory_types']),'complete_memory_preservation')
        for p,v in arg['memory_policies'].items():
            core.need(set(v)=={'kind','provenance'} and v['kind']=='preserve','history_reset_forbidden:'+p)
        if date.fromisoformat(book['date'])!=date.fromisoformat(book['period']['end_exclusive'])-timedelta(days=1):
            return dict(base,status='unassessed_not_period_end',reason='retained_prefix_has_not_reached_period_end',carry=None)
        result=carry.propose(arg)
        if result['status']!='proposed':return dict(base,status=result['status'],reason=result.get('reason'),carry=None)
        after=result['next_opening']
        core.need(after['memory']==book['memory'] and after['memory_types']==book['memory_types'] and after['memory_schema']==book['memory_schema'],'complete_contract_history_preserved')
        core.need(after['balances'][book['cash_account']]==book['balances'][book['cash_account']],'carry_does_not_settle_cash')
        for a,row in book['accounts'].items():
            if row['classification'] not in ('income','expense','equity'):core.need(after['balances'][a]==book['balances'][a],'balance_preserved:'+a)
        core.need(result['closed_book']['flows']==book['flows'] and after['flows']==[],'period_flow_separation')
        core.need(after['seen']==book['seen']+[arg['close_id']],'event_history_preserved')
        report=carry.reports.report(carry.reports.request(after,after,body['schemas'],body['mapping']))
        core.need(report['status']=='reported','next_opening_valid')
        archive=dict(profile='CouponRefusalCarryArchive/1',source_record_sha256=rid,
                     refusal=cp(prior['stop']),remaining_commands=cp(prior['remaining_commands']),
                     prior_status=prior['status'],prior_current_sha256=identity(book),prior_report_sha256=identity(record['report']),
                     next_opening_sha256=identity(after),carry_archive_sha256=identity(result['archive']),
                     history_scope='same_verified_prefix_no_later_settlement_inferred')
        return dict(base,status='proposed_selected_coupon_carry',carry=result,opening_report=report,history_archive=archive)
    except (ValueError,TypeError,KeyError,AssertionError) as exc:
        return dict(base,status='invalid',reason=str(exc)[:300],carry=None)
