"""Recorded conditional period statements from explicit declared company maps."""
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import company_book_transition_v1 as book_engine

core=book_engine.core
PROFILE='CompanyBookReport/1'
MAP='CompanyStatementMap/1'
BOOK_SHA256='3f46df2d4c7b65f344c0a1234177503a0869b9162b4a85bdda224c2eddbea8ff'
CLASSES=['asset','liability','equity','income','expense']
FLAGS={**book_engine.FLAGS,'fiscal_complete':False,'notes_complete':False}
digest=core.digest
number=book_engine.monetary.rational
fmt=book_engine.monetary.fmt


def total(values):
    answer=Q(0)
    for value in values:answer=book_engine.monetary.bounded(answer+value)
    return answer


def validate(body):
    core.need(sha256(Path(book_engine.__file__).read_bytes()).hexdigest()==BOOK_SHA256,'book_dependency_hash')
    book_engine.protected();book_engine.memory.bounded(body)
    book_engine.closed(body,['profile','opening','closing','schemas','mapping','expected_opening_sha256',
                            'expected_closing_sha256','expected_mapping_sha256','equity_movements','notes'])
    core.need(body['profile']==PROFILE,'report_profile')
    opening,closing,mapping=body['opening'],body['closing'],body['mapping']
    for name in ['opening','closing','mapping']:core.need(body['expected_'+name+'_sha256']==digest(body[name]),'stale_'+name)
    schemas=body['schemas'];core.need(type(schemas) is dict,'schema_registry')
    for h,shape in schemas.items():core.need(h==digest(shape),'schema_digest');book_engine.memory.check_schema(shape)
    for book in [opening,closing]:book_engine.validate_book(book,schemas)
    for key in ['context','period','accounts','cash_account']:
        core.need(core.canonical(opening[key])==core.canonical(closing[key]),'book_correspondence:'+key)
    core.need(opening['date']==opening['period']['start'],'opening_at_period_start')
    core.need(not opening['flows'],'empty_opening_flows_required')
    core.need(core.scalar(opening['date'],'date')<=core.scalar(closing['date'],'date'),'report_chronology')
    core.need(closing['seen'][:len(opening['seen'])]==opening['seen'],'event_history_prefix')
    suffix=set(closing['seen'][len(opening['seen']):])
    core.need(all(flow['event_id'] in suffix for flow in closing['flows']),'current_period_flow_event')
    for key,row in opening['accounts'].items():
        if row['classification'] in ['income','expense']:core.need(number(opening['balances'][key])==0,'opening_temporary_balance')
    book_engine.closed(mapping,['profile','context','lines'])
    core.need(mapping['profile']==MAP,'map_profile');core.need(mapping['context']==opening['context'],'map_context')
    core.need(type(mapping['lines']) is list and 0<len(mapping['lines'])<=256,'statement_line_limit')
    line_ids=set();seen=set()
    for line in mapping['lines']:
        book_engine.closed(line,['id','label','classification','accounts'])
        for key in ['id','label']:book_engine.text(line[key],key)
        core.need(line['id'] not in line_ids,'duplicate_line_id');line_ids.add(line['id'])
        core.need(line['classification'] in CLASSES,'line_classification')
        core.identifiers(line['accounts'],'line_accounts',True)
        for key in line['accounts']:
            core.need(key in opening['accounts'],'unknown_line_account');core.need(key not in seen,'overlapping_line_account');seen.add(key)
            core.need(opening['accounts'][key]['classification']==line['classification'],'line_account_classification')
    core.need(seen==set(opening['accounts']),'complete_account_partition')
    core.need(type(body['equity_movements']) is list and len(body['equity_movements'])<=256,'equity_movement_limit')
    movement_ids=set()
    for row in body['equity_movements']:
        book_engine.closed(row,['id','event_id','date','account','amount','description'])
        for key in ['id','event_id','account','description']:book_engine.text(row[key],key)
        core.need(row['id'] not in movement_ids,'duplicate_equity_movement');movement_ids.add(row['id'])
        core.need(row['event_id'] in suffix,'equity_event_unrecorded')
        core.need(opening['date']<=core.scalar(row['date'],'date').isoformat()<=closing['date'],'equity_movement_chronology')
        core.need(row['account'] in opening['accounts'] and opening['accounts'][row['account']]['classification']=='equity','equity_movement_account')
        number(row['amount'])
    core.need(type(body['notes']) is list and len(body['notes'])<=256,'note_limit');note_ids=set()
    for row in body['notes']:
        book_engine.closed(row,['id','label','status','reason'])
        for key in ['id','label','reason']:book_engine.text(row[key],key)
        core.need(row['id'] not in note_ids,'duplicate_note');note_ids.add(row['id'])
        core.need(row['status'] in ['missing','unsupported','unresolved'],'note_status')
    return opening,closing,mapping


def request(opening,closing,schemas,mapping,equity_movements=None,notes=None):
    return {'profile':PROFILE,'opening':deepcopy(opening),'closing':deepcopy(closing),'schemas':deepcopy(schemas),
            'mapping':deepcopy(mapping),'expected_opening_sha256':digest(opening),'expected_closing_sha256':digest(closing),
            'expected_mapping_sha256':digest(mapping),'equity_movements':deepcopy(equity_movements or []),'notes':deepcopy(notes or [])}


def report(body):
    try:
        opening,closing,mapping=validate(body)
        groups={k:[] for k in CLASSES};opening_totals={k:Q(0) for k in CLASSES};closing_totals={k:Q(0) for k in CLASSES}
        for line in mapping['lines']:
            sign=-1 if line['classification'] in ['liability','equity','income'] else 1
            a=sign*total(number(opening['balances'][k]) for k in line['accounts'])
            b=sign*total(number(closing['balances'][k]) for k in line['accounts'])
            groups[line['classification']].append({**deepcopy(line),'opening':fmt(a),'closing':fmt(b)})
            opening_totals[line['classification']]=total([opening_totals[line['classification']],a])
            closing_totals[line['classification']]=total([closing_totals[line['classification']],b])
        p=total([closing_totals['income'],-closing_totals['expense']]);equity=total([closing_totals['equity'],p])
        activities={}
        for kind in ['operating','investing','financing']:
            amounts=[number(f['amount']) for f in closing['flows'] if f['activity']==kind]
            receipts=total(v for v in amounts if v>=0);payments=-total(v for v in amounts if v<0)
            activities[kind]={'receipts':fmt(receipts),'payments':fmt(payments),'net':fmt(receipts-payments)}
        movements=body['equity_movements'];by_account={}
        for account,row in opening['accounts'].items():
            if row['classification']=='equity':
                declared=total(number(x['amount']) for x in movements if x['account']==account)
                change=total([number(opening['balances'][account]),-number(closing['balances'][account])])
                core.need(declared==change,'unexplained_equity_movement:'+account);by_account[account]=fmt(declared)
        direct=total(number(x['amount']) for x in movements)
        cash=closing['cash_account'];cash0=number(opening['balances'][cash]);cash1=number(closing['balances'][cash])
        checks={'balance_sheet':total([closing_totals['asset'],-closing_totals['liability'],-equity]),
                'cash':total([cash1,-cash0,-total(number(x['net']) for x in activities.values())]),
                'equity':total([opening_totals['equity'],direct,p,-equity])}
        core.need(all(x==0 for x in checks.values()),'statement_reconciliation')
        return {'profile':PROFILE,**FLAGS,'status':'reported','scope':'recorded_period_only',
                'context':deepcopy(closing['context']),'period':deepcopy(closing['period']),'as_of':closing['date'],
                'statement_lines':groups,'opening_totals':{k:fmt(v) for k,v in opening_totals.items()},
                'closing_totals':{k:fmt(v) for k,v in closing_totals.items()},
                'balance_sheet':{'total_assets':fmt(closing_totals['asset']),'total_liabilities':fmt(closing_totals['liability']),
                                 'equity_including_profit':fmt(equity)},
                'income':{'income':fmt(closing_totals['income']),'expenses':fmt(closing_totals['expense']),'profit':fmt(p)},
                'cash_flows':{'activities':activities,'opening_cash':fmt(cash0),'closing_cash':fmt(cash1),'net_movement':fmt(cash1-cash0),
                              'gross_origins':deepcopy(closing['flows'])},
                'equity':{'opening':fmt(opening_totals['equity']),'direct_movements':fmt(direct),'profit':fmt(p),'closing':fmt(equity),
                          'by_account':by_account,'movements':deepcopy(movements)},
                'reconciliations':{k:fmt(v) for k,v in checks.items()},'notes':deepcopy(body['notes']),
                'unresolved':['Event-population completeness','Source and accounting admission','Complete note package','Indirect operating cash-flow bridge'],
                'request_sha256':digest(body),'opening_sha256':digest(opening),'closing_sha256':digest(closing),'mapping_sha256':digest(mapping),
                'implementation_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),'book_sha256':BOOK_SHA256}
    except Exception as exc:return {'profile':PROFILE,**FLAGS,'status':'invalid','reason':str(exc)[:300] or type(exc).__name__}


def verify(body,result):
    try:
        book_engine.memory.bounded(result)
        return core.canonical(report(body))==core.canonical(result)
    except Exception:return False
