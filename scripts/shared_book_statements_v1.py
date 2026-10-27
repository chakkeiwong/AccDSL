"""Recorded-only financial views of a checked synthetic event prefix."""
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
from fractions import Fraction as Q
import json
import shared_book_successor_v1 as book

ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/'data/accounting-master/shared-book-statements-20261024'
LOCK='7f521e46669da26e8029fd49ffe5f84770ac4d3a50f6afbcb258c08a9ca39d02'
PROFILE='RecordedSharedBookStatements/1'
ASSETS=book.returns.structure.native.ASSETS+['rou']
LIABILITIES=book.returns.structure.native.LIABILITIES+['lease_liability']
EQUITY=book.returns.structure.native.EQUITY
INCOME=book.returns.structure.native.INCOME+['other_gains']
ACTIVITIES=['operating','investing','financing']
WORKING_CAPITAL=['inventory','receivable','payable','recovery_asset','refund_liability']
FLAGS={**book.FLAGS,'annual_close_ready':False,'complete_financial_statements':False}

def protected():
    raw=(HERE/'source-lock.json').read_bytes();book.need(sha256(raw).hexdigest()==LOCK,'source_lock_changed')
    for name,h in json.loads(raw).items():book.need(sha256((ROOT/name).read_bytes()).hexdigest()==h,'protected_source_changed:'+name)

def request(opening,events):
    return {'profile':PROFILE,'source_bundle_sha256':LOCK,'opening_sha256':book.digest(opening),
            'events_sha256':book.digest(events),'opening':deepcopy(opening),'events':deepcopy(events)}

def calculate(body):
    try:
        book.caller.bounded(body);book.caller.closed(body,['profile','source_bundle_sha256','opening_sha256','events_sha256','opening','events'])
        book.need(body['profile']==PROFILE,'profile');protected()
        book.need(body['source_bundle_sha256']==LOCK,'source_bundle_digest')
        opening=body['opening'];events=body['events']
        book.need(type(events) is list,'event_list_required')
        book.need(body['opening_sha256']==book.digest(opening) and body['events_sha256']==book.digest(events),'input_digest')
        book.invariant(opening)
        classes=ASSETS+LIABILITIES+EQUITY+INCOME
        book.need(len(classes)==len(set(classes)) and set(classes)==set(book.ACCOUNTS),'complete_account_classification')
        book.need(opening['date']==opening['period']['start'],'fresh_period_opening_required','unsupported')
        book.need(not opening['seen'] and not opening['flows'] and not opening['tax_adjustments'],'fresh_history_required','unsupported')
        book.need(all(book.amount(opening['balances'][k])==0 for k in INCOME),'opening_income_not_closed','unsupported')
        book.need(book.amount(opening['opening_interest_paid'])==0,'opening_interest_already_paid','unsupported')
        execution=book.run_prefix(opening,events);closing=execution['after'];b0=opening['balances'];b=closing['balances']
        book.invariant(closing)
        book.need(all(b[k]==b0[k] for k in EQUITY),'owner_movement_method_missing','unsupported')
        profit=-sum(book.amount(b[k]) for k in INCOME)
        assets={k:book.fmt(book.amount(b[k])) for k in ASSETS}
        liabilities={k:book.fmt(-book.amount(b[k])) for k in LIABILITIES}
        opening_equity=-sum(book.amount(b0[k]) for k in EQUITY)
        equity=-sum(book.amount(b[k]) for k in EQUITY)+profit
        total_assets=sum(Q(v) for v in assets.values());total_liabilities=sum(Q(v) for v in liabilities.values())
        book.need(total_assets-total_liabilities==equity,'balance_sheet_identity')
        book.need(opening_equity+profit==equity,'equity_rollforward_identity')
        cf={}
        book.need(all(f['activity'] in ACTIVITIES for f in closing['flows']),'unknown_cash_activity')
        for activity in ACTIVITIES:
            amounts=[book.amount(f['amount']) for f in closing['flows'] if f['activity']==activity]
            cf[activity]={'receipts':book.fmt(sum(x for x in amounts if x>=0)),
                         'payments':book.fmt(-sum(x for x in amounts if x<0)),
                         'net':book.fmt(sum(amounts))}
        cash_change=book.amount(b['cash'])-book.amount(b0['cash'])
        book.need(cash_change==sum(Q(v['net']) for v in cf.values()),'direct_cash_identity')
        bridge={'recorded_profit':profit,'depreciation':book.amount(b['depreciation']),
                'deferred_tax_recorded':book.amount(b['deferred_tax']),
                'remove_lease_gain':book.amount(b['other_gains']),
                **{'change_'+k:-(book.amount(b[k])-book.amount(b0[k])) for k in WORKING_CAPITAL},
                'opening_interest_paid':-book.amount(closing['opening_interest_paid'])}
        indirect=sum(bridge.values());book.need(indirect==Q(cf['operating']['net']),'indirect_cash_identity')
        completed=sum(x['result']['status']=='proposed' for x in execution['trace'])
        failed=execution['trace'][-1] if execution['status']=='stopped' and execution['trace'] else None
        coverage={'execution_status':execution['status'],'requested_events':len(events),'completed_events':completed,
          'unexecuted_events':len(events)-completed,'failed_event':deepcopy(failed),
          'last_completed_date':closing['date'],'declared_period':deepcopy(closing['period']),
          'period_completion':'unresolved','tax_assessment':'unresolved',
          'annual_completion':'unresolved','scope':'recorded postings through completed prefix only'}
        return {'profile':PROFILE,**FLAGS,'status':'recorded_prefix','request_sha256':book.digest(body),
          'source_bundle_sha256':LOCK,'implementation_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),
          'context':deepcopy(closing['context']),'source':deepcopy(closing['source']),
          'coverage':coverage,'execution':execution,'closing_state_sha256':book.digest(closing),
          'account_classes':deepcopy({'assets':ASSETS,'liabilities':LIABILITIES,'equity':EQUITY,'income':INCOME}),
          'balance_sheet_recorded':{'assets':assets,'liabilities':liabilities,
            'total_assets':book.fmt(total_assets),'total_liabilities':book.fmt(total_liabilities),
            'equity_including_recorded_profit':book.fmt(equity)},
          'income_recorded':{'revenue_and_gains':{k:book.fmt(-book.amount(b[k])) for k in ['revenue','other_gains']},
            'expenses':{k:b[k] for k in INCOME if k not in ['revenue','other_gains']},
            'recorded_profit':book.fmt(profit),'tax_assessment':'unresolved'},
          'equity_recorded':{'opening':book.fmt(opening_equity),'recorded_profit':book.fmt(profit),
            'owner_movement':book.fmt(-sum(book.amount(b[k])-book.amount(b0[k]) for k in EQUITY)),
            'closing':book.fmt(equity)},
          'cash_flows_recorded':{'activities':cf,'opening_cash':b0['cash'],'closing_cash':b['cash'],
            'net_movement':book.fmt(cash_change),'gross_origins':deepcopy(closing['flows'])},
          'indirect_operating_recorded':{'items':{k:book.fmt(v) for k,v in bridge.items()},'net':book.fmt(indirect)},
          'reconciliations':{'balance_sheet':book.fmt(total_assets-total_liabilities-equity),
            'equity':book.fmt(opening_equity+profit-equity),
            'direct_cash':book.fmt(cash_change-sum(Q(v['net']) for v in cf.values())),
            'indirect_cash':book.fmt(indirect-Q(cf['operating']['net']))},
          'outstanding':['Tax assessment and any unposted tax adjustments','Complete fiscal-period event coverage','Actual source and accounting admission']}
    except (book.Refused,book.lease.Refused) as exc:
        return {'profile':PROFILE,**FLAGS,'status':exc.status,'reason':exc.reason}
    except (ValueError,TypeError,KeyError,AttributeError,AssertionError,OSError,RecursionError,OverflowError) as exc:
        return {'profile':PROFILE,**FLAGS,'status':'invalid','reason':str(exc)[:300]}

def verify_result(body,result):
    try:
        return book.caller.canonical(result)==book.caller.canonical(calculate(body))
    except (ValueError,TypeError,RecursionError,OverflowError):return False
