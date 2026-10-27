"""Explicit provisional closing and per-leaf memory carry; no fiscal admission."""
from copy import deepcopy
from datetime import timedelta
from hashlib import sha256
from pathlib import Path
import company_book_reports_v1 as reports

engine=reports.book_engine
core=reports.core
PROFILE='CompanyBookCarry/1'
REPORT_SHA256='7418f0a6fc7169ac1b297b47891cb2f6f9075b3f2231366ea9f241589a753100'
FLAGS=reports.FLAGS
digest=core.digest


def policy_stage(book,policies,schemas,start):
    core.need(type(policies) is dict and set(policies)==set(book['memory_types']),'complete_memory_policies')
    operations=[]
    for pointer,typ in book['memory_types'].items():
        policy=policies[pointer];core.need(type(policy) is dict,'memory_policy')
        kind=policy.get('kind')
        engine.closed(policy,['kind','type','value','provenance'] if kind=='reset' else ['kind','provenance'])
        engine.text(policy['provenance'],'policy_provenance')
        core.need(kind in ['preserve','reset','next_period_start'],'memory_policy_kind')
        if kind=='preserve':continue
        if kind=='next_period_start':core.need(typ['kind']=='date','date_policy_type');value=start
        else:
            core.need(policy['type']==typ,'reset_type_mismatch');value=policy['value'];core.scalar(value,typ['kind'])
            if typ['kind']=='rational':engine.monetary.rational(value)
        path=engine.binding.pointer_parts(pointer)
        operations.append({'id':'carry.'+str(len(operations)),'op':'replace','path':path,'value':{'kind':'literal','value':value}})
    empty={'type':'object','properties':{},'required':[],'additionalProperties':False};h=digest(empty)
    definition={'profile':engine.memory.PROFILE,'state_schema':book['memory_schema'],'input_schema':h,'operations':operations}
    key=digest(definition)
    result=engine.memory.stage({key:definition},key,{**deepcopy(schemas),h:empty},book['memory'],{})
    core.need(result['status']=='staged','memory_carry:'+result.get('reason','invalid'))
    return result


def request(report_request,close_id,retained_account,next_end_exclusive,memory_policies):
    report=reports.report(report_request)
    return {'profile':PROFILE,'report_request':deepcopy(report_request),'expected_report_sha256':digest(report),
            'close_id':close_id,'retained_account':retained_account,'next_end_exclusive':next_end_exclusive,
            'memory_policies':deepcopy(memory_policies)}


def propose(body):
    try:
        core.need(sha256(Path(reports.__file__).read_bytes()).hexdigest()==REPORT_SHA256,'report_dependency_hash')
        engine.memory.bounded(body)
        engine.closed(body,['profile','report_request','expected_report_sha256','close_id','retained_account','next_end_exclusive','memory_policies'])
        core.need(body['profile']==PROFILE,'carry_profile')
        report=reports.report(body['report_request'])
        core.need(report['status']=='reported','report_not_valid:'+report.get('reason',''))
        core.need(digest(report)==body['expected_report_sha256'],'stale_report')
        before=body['report_request']['closing'];schemas=body['report_request']['schemas']
        end=core.scalar(before['period']['end_exclusive'],'date')
        core.need(core.scalar(before['date'],'date')==end-timedelta(days=1),'last_period_day_required')
        core.need(core.scalar(body['next_end_exclusive'],'date')>end,'next_period_end')
        engine.text(body['close_id'],'close_id');core.need(body['close_id'] not in before['seen'],'duplicate_close_id')
        account=body['retained_account'];core.need(account in before['accounts'] and before['accounts'][account]['classification']=='equity','retained_equity_account')
        journal={k:'0/1' for k in before['accounts']};temporary=[]
        for key,row in before['accounts'].items():
            if row['classification'] in ['income','expense']:
                amount=reports.number(before['balances'][key]);temporary.append(amount);journal[key]=reports.fmt(-amount)
        journal[account]=reports.fmt(reports.total(temporary))
        core.need(reports.total(reports.number(v) for v in journal.values())==0,'closing_journal_balance')
        core.need(journal[before['cash_account']]=='0/1','closing_cash_effect')
        closed_book=deepcopy(before)
        closed_book['balances']={k:reports.fmt(reports.total([reports.number(v),reports.number(journal[k])])) for k,v in before['balances'].items()}
        closed_book['seen'].append(body['close_id']);engine.validate_book(closed_book,schemas)
        stage=policy_stage(before,body['memory_policies'],schemas,end.isoformat())
        after=deepcopy(closed_book);after['period']={'start':end.isoformat(),'end_exclusive':body['next_end_exclusive']}
        after['date']=end.isoformat();after['flows']=[];after['memory']=stage['after'];engine.validate_book(after,schemas)
        archive={'profile':'CompanyBookCarryArchive/1','context':deepcopy(before['context']),'period':deepcopy(before['period']),
                 'close_id':body['close_id'],'closing_before_sha256':digest(before),'closed_book_sha256':digest(closed_book),
                 'report_sha256':digest(report),'next_opening_sha256':digest(after),'memory_policies_sha256':digest(body['memory_policies']),
                 'scope':'Provisional recorded-balance carry; not admitted fiscal completion'}
        return {'profile':PROFILE,**FLAGS,'status':'proposed','request_sha256':digest(body),'report':report,
                'journal':journal,'cash_flows':[],'closed_book':closed_book,'next_opening':after,'memory_stage':stage,'archive':archive,
                'implementation_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),'report_implementation_sha256':REPORT_SHA256}
    except Exception as exc:return {'profile':PROFILE,**FLAGS,'status':'invalid','reason':str(exc)[:300] or type(exc).__name__}


def apply(body,proposal):
    try:
        engine.memory.bounded(proposal);expected=propose(body)
        core.need(core.canonical(expected)==core.canonical(proposal),'proposal_recomputation_mismatch')
        return {**deepcopy(expected),'status':'applied_provisional'} if expected['status']=='proposed' else expected
    except Exception as exc:return {'profile':PROFILE,**FLAGS,'status':'invalid','reason':str(exc)[:300] or type(exc).__name__}
