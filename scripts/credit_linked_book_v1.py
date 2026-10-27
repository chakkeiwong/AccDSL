"""Optional, read-only single-root projection of retained credit journals."""
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path

import credit_linked_algebra_v1 as algebra
import credit_linked_schedule_v1 as linked
import company_book_transition_v1 as host
import company_book_reports_v1 as reports

PROFILE = 'CreditLinkedBook/1'
STATE = 'CreditLinkedBookState/1'
MAX_REQUEST_BYTES = 128 * 1024
MAX_RESULT_BYTES = 8 * 1024 * 1024
MAX_JOURNALS = MAX_OBSERVATIONS = 128
ROLES = {'cash':'asset','gross':'asset','allowance':'asset',
         'interest':'income','impairment':'income','catchup':'income'}
FLAGS = {**reports.FLAGS, 'posts':False,'host_book_admission':False,
         'native_accounting_admission':False,'source_complete':False}
PINS = {
 'credit_linked_algebra_v1.py':'304757ecf5cec55f798a894b10ff0ff9a100bae3e30eac0e14279d91e2439479',
 'credit_linked_schedule_v1.py':'e2f4b395007e9ef43ecab823c535e0ff6bdf7921eb6b0ffad497b44e27c0d997',
 'company_book_transition_v1.py':'3f46df2d4c7b65f344c0a1234177503a0869b9162b4a85bdda224c2eddbea8ff',
 'company_book_reports_v1.py':'7418f0a6fc7169ac1b297b47891cb2f6f9075b3f2231366ea9f241589a753100',
}
need, digest = algebra.need, algebra.digest


def fmt(q):
    q=Q(q); return str(q.numerator)+'/'+str(q.denominator)


def closed(value, keys, name):
    need(type(value) is dict and set(value)==set(keys),name+'_shape')


def protected():
    for name,h in PINS.items():
        need(sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()==h,'dependency_hash:'+name)
    host.protected(); linked.protected()


def prepare(body):
    protected()
    need(len(algebra.canonical(body).encode())<=MAX_REQUEST_BYTES,'request_budget','unsupported')
    closed(body,['profile','operation','linked_request','expected_linked_result_sha256',
                 'opening','schemas','roles','context_adapter'],'credit_linked_book')
    need(body['profile']==PROFILE,'profile')
    need(body['operation']=='project','operation_unsupported','unsupported')
    exact=linked.calculate(body['linked_request'])
    if exact['status']!='certified_read_only':
        raise UpstreamRefusal(exact)
    need(digest(exact)==body['expected_linked_result_sha256'],'linked_result_binding')
    native_request=body['linked_request']['native_request']
    selected=next(row for row in linked.retained() if row['id']==exact['case_id'])
    need(digest(selected['result'])==exact['native_result_sha256'],'native_result_binding')
    opening,schemas,roles=body['opening'],body['schemas'],body['roles']
    host.validate_book(opening,schemas)
    need(type(schemas) is dict,'schemas')
    for h,schema in schemas.items(): need(h==host.digest(schema),'schema_digest')
    closed(roles,ROLES,'roles')
    need(all(type(v) is str for v in roles.values()),'role_encoding')
    need(len(set(roles.values()))==len(roles),'injective_roles')
    for role,kind in ROLES.items():
        need(roles[role] in opening['accounts'],'missing_account:'+role)
        need(opening['accounts'][roles[role]]['classification']==kind,'role_classification:'+role)
    need(roles['cash']==opening['cash_account'],'cash_role')
    need(opening['context']['entity']==native_request['context']['entity'],'native_entity_binding')
    need(native_request['context']['currency']=='CU' and opening['context']['currency']=='XCU','illustrative_currency_alias')
    adapter=body['context_adapter']
    closed(adapter,['native_context_sha256','host_context_sha256','unit_scale','premise'],'context_adapter')
    need(adapter['native_context_sha256']==digest(native_request['context']) and
         adapter['host_context_sha256']==digest(opening['context']),'context_adapter_binding')
    need(adapter['unit_scale']=='1/1','unit_scale_one_required')
    need(type(adapter['premise']) is str and 0<len(adapter['premise'].strip())<=4096,'alias_premise')
    need(native_request['context']['unit']=='currency units','native_monetary_unit')
    need(opening['date']==opening['period']['start']==native_request['acquisition']['date'],'opening_date')
    need(opening['period']['end_exclusive']>exact['schedule']['closing']['date'],'native_dates_within_period')
    need(not opening['flows'],'empty_opening_flows')
    for role,account in roles.items():
        target=Q(native_request['opening_cash']) if role=='cash' else Q(0)
        need(host.monetary.rational(opening['balances'][account])==target,'native_opening_balance:'+role)
    for account,info in opening['accounts'].items():
        if info['classification'] in ['income','expense']:
            need(host.monetary.rational(opening['balances'][account])==0,'opening_temporary_balance')
    root=algebra.Root.create(exact['root']['context'],exact['root']['rate'])
    need(root.identity==exact['root_sha256'],'root_binding')
    return exact,selected['result'],root


class UpstreamRefusal(Exception):
    def __init__(self,result):self.result=result


def timeline(request, schedule):
    """Use native event order, including distinct observations at the same date."""
    need(len(schedule['journals'])<=MAX_JOURNALS and len(schedule['stages'])<=MAX_OBSERVATIONS,
         'sequence_budget','unsupported')
    commands=[('journal','acquisition'),('stage','acquisition')]
    for event in request['events']:
        identity=event['id']; kind=event['operation']
        commands.extend([('journal',identity+'_accrual'),('stage',identity+'_accrual')])
        if kind=='credit_revision':
            commands.append(('journal',identity+'_credit'))
            if Q(event['writeoff']['fraction']):commands.append(('journal',identity+'_writeoff'))
        elif kind=='estimate_revision':commands.append(('journal',identity+'_estimate'))
        elif kind=='collect':
            commands.append(('journal',identity+'_cash'))
            if event['close']:commands.append(('journal',identity+'_clear'))
        else:need(kind=='advance','event_unsupported','unsupported')
        commands.append(('stage',identity))
    for category,key in [('journal','journals'),('stage','stages')]:
        need([identity for c,identity in commands if c==category]==[r['id'] for r in schedule[key]],
             'native_sequence:'+category)
    return commands


def project(body):
    exact,native,root=prepare(body)
    opening=body['opening']; roles=body['roles']; req=body['linked_request']['native_request']
    schedule=exact['schedule']; zero=root.value(0)
    balances={a:root.value(host.monetary.rational(v)) for a,v in opening['balances'].items()}
    initial=deepcopy(balances); seen=list(opening['seen']); cash_origins=[]
    journals={j['id']:j for j in schedule['journals']}; stages={s['id']:s for s in schedule['stages']}
    trace=[]; observations=[]; checks=[]; rational_checks=[]
    def prove(name,left,right=zero):
        need((left-right).zero,'identity_not_certified:'+name,'not_certified')
        checks.append({'identity':name,'status':'certified_equal'})
    def value(wire):return algebra.Expr.from_wire(root,wire)
    def state(date):
        return {'profile':STATE,'context':deepcopy(opening['context']),'period':deepcopy(opening['period']),
                'date':date,'accounts':deepcopy(opening['accounts']),'cash_account':roles['cash'],
                'amount_type':{'profile':'SingleRootCurrency/1','host_context_sha256':digest(opening['context']),
                    'currency':opening['context']['currency'],'unit_scale':'1/1','native_root_sha256':root.identity,
                    'context_adapter_sha256':digest(body['context_adapter'])},
                'balances':{a:x.wire() for a,x in balances.items()},'seen':list(seen),
                'memory_schema':opening['memory_schema'],'memory_types':deepcopy(opening['memory_types']),
                'memory':deepcopy(opening['memory']),'unclassified_cash_origins':deepcopy(cash_origins)}
    def summary():
        totals={kind:zero for kind in reports.CLASSES}
        for account,x in balances.items():totals[opening['accounts'][account]['classification']]+=x
        profit=-totals['income']-totals['expense']; equity=-totals['equity']+profit
        return {'assets':totals['asset'],'liabilities':-totals['liability'],'equity_including_profit':equity,
                'income':-totals['income'],'expenses':totals['expense'],'profit':profit,
                'cash':balances[roles['cash']], 'cash_change':balances[roles['cash']]-initial[roles['cash']]}
    def host_projection(date):
        try:projected={a:fmt(x.rational_projection()) for a,x in balances.items()}
        except algebra.Refusal as exc:
            need(exc.reason=='rational_projection_not_certified',exc.reason,exc.status)
            return {'status':'nonrational_amounts','book':None}
        book=deepcopy(opening);book.update(date=date,balances=projected,seen=list(seen))
        host.validate_book(book,body['schemas'])
        return {'status':'rational_book_validated','book':book,'cash_classification':'unresolved',
                'meaning':'Balance/type comparison only; absent classified flows do not imply absent movements'}
    before=state(opening['date']); running_cash=Q(0); prefix=0
    cash_source=iter(schedule['cash_flows'])
    for category,identity in timeline(req,schedule):
        if category=='journal':
            journal=journals[identity]; date=journal['date']; event_id='credit.'+exact['case_id']+'.'+identity
            need(event_id not in seen,'duplicate_event_identity')
            gross=[]; delta={a:zero for a in balances}
            for role,wire in journal['entries'].items():
                need(role in roles,'native_journal_role')
                amount=value(wire); account=roles[role]; delta[account]+=amount
                gross.append({'role':role,'account':account,'amount':wire})
            prove('journal:'+identity,sum(delta.values(),zero))
            for account,amount in delta.items():balances[account]+=amount
            prove('book:'+identity,sum(balances.values(),zero))
            seen.append(event_id);prefix+=1
            count=3 if identity=='acquisition' else 1 if identity.endswith('_cash') else 0
            new_origins=[]
            for _ in range(count):
                origin=next(cash_source);need(origin['date']==date,'native_cash_date')
                new_origins.append(origin);cash_origins.append(origin);running_cash+=Q(origin['amount'])
            prove('journal_cash_origins:'+identity,delta[roles['cash']],root.value(sum((Q(o['amount']) for o in new_origins),Q(0))))
            after=state(date)
            for account in sorted(set(balances)-set(roles.values())):prove('complement:'+identity+':'+account,balances[account],initial[account])
            trace.append({'native_journal_id':identity,'event_id':event_id,'date':date,'native_journal':deepcopy(journal),
                          'gross_postings':gross,'journal':{a:x.wire() for a,x in delta.items()},
                          'before_sha256':digest(before),'after_sha256':digest(after),'after':after})
            before=after
        else:
            stage=stages[identity]
            need(stage['date']==before['date'],'stage_date')
            for role in roles:
                amount=value(stage[role]);amount=-amount if role in ['allowance','interest','impairment','catchup'] else amount
                prove('stage:'+identity+':'+role,balances[roles[role]],amount)
            totals=summary();prove('stage:'+identity+':profit',totals['profit'],value(stage['profit']))
            prove('stage:'+identity+':balance_sheet',totals['assets']-totals['liabilities']-totals['equity_including_profit'])
            prove('stage:'+identity+':cash_origins',totals['cash_change'],root.value(running_cash))
            observation={'native_stage_id':identity,'date':stage['date'],'journal_prefix':prefix,
                         'state_sha256':digest(before),'native_stage':deepcopy(stage),
                         'report':{k:v.wire() for k,v in totals.items()},'report_scope':'cumulative_balance_profit_unclassified_cash',
                         'classification_admission':False}
            observations.append(observation)
            rational_checks.append({'native_stage_id':identity,**host_projection(stage['date'])})
    need(next(cash_source,None) is None,'unconsumed_cash_origins')
    need(cash_origins==schedule['cash_flows'],'complete_cash_origins')
    mapping={'profile':reports.MAP,'context':deepcopy(opening['context']),
             'lines':[{'id':a,'label':a,'classification':i['classification'],'accounts':[a]} for a,i in opening['accounts'].items()]}
    first=rational_checks[0]['book'];need(first is not None,'rational_acquisition_required')
    probe_request=reports.request(opening,first,body['schemas'],mapping)
    probe=reports.report(probe_request)
    need(probe['status']=='invalid' and probe['reason']=='statement_reconciliation','cash_classification_probe')
    return {'profile':PROFILE,**FLAGS,'status':'proposed_exact_read_only','mutations':[],
            'request_sha256':digest(body),'root':root.wire(),'root_sha256':root.identity,
            'opening':deepcopy(opening),'schemas':deepcopy(body['schemas']),
            'context_adapter':deepcopy(body['context_adapter']),'roles':deepcopy(roles),
            'native_request':deepcopy(req),'native_result':deepcopy(native),'linked_result':exact,
            'trace':trace,'observations':observations,'closing':before,'identity_checks':checks,
            'rational_host_checks':rational_checks,
            'unclassified_report_probe':{'request':probe_request,'result':probe,
                'meaning':'Acquisition cash movement lacks classification; this is not a complete host report'},
            'unresolved':['Cash-flow classification','Annual carry policy','Complete notes and source population',
                          'Accounting and posting admission','Multiple roots and arbitrary company operations'],
            'implementation_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),'dependency_sha256':deepcopy(PINS)}


def propose(body):
    try:
        result=project(body)
        need(len(algebra.canonical(result).encode())<=MAX_RESULT_BYTES,'result_budget','unsupported')
        return result
    except UpstreamRefusal as exc:
        return {'profile':PROFILE,**FLAGS,'status':exc.result['status'],'reason':'linked_refusal',
                'linked_refusal':exc.result,'mutations':[]}
    except algebra.Refusal as exc:
        return {'profile':PROFILE,**FLAGS,'status':exc.status,'reason':exc.reason,'mutations':[]}
    except Exception as exc:
        return {'profile':PROFILE,**FLAGS,'status':'invalid','reason':str(exc)[:350] or type(exc).__name__,'mutations':[]}


def verify(body,result):
    try:
        if len(algebra.canonical(result).encode())>MAX_RESULT_BYTES:return False
        return algebra.canonical(propose(body))==algebra.canonical(result)
    except Exception:return False
