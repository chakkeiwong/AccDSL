"""Conditional, exact cash classification of immutable retained credit projections."""
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import credit_linked_book_v1 as bridge

PROFILE='CreditCashClassification/1'
ACTIVITIES=('operating','investing','financing')
class Invalid(ValueError):pass
def need(v,why):
    if not v:raise Invalid(why)
def closed(v,keys,why):need(type(v) is dict and set(v)==set(keys),why)
def text(v):need(type(v) is str and 0<len(v.strip())<=4096,'text_required')
def fmt(q):q=Q(q);return str(q.numerator)+'/'+str(q.denominator)
def amount(v):
    need(type(v) is str,'rational_string_required')
    try:q=Q(v)
    except (ValueError,ZeroDivisionError) as exc:raise Invalid('invalid_rational') from exc
    need(fmt(q)==v,'canonical_rational_required');return q
def digest(v):return bridge.digest(v)
def origin_digest(origin):return digest(origin)

class Library:
    def __init__(self):
        self.lock=json.loads((HERE/'source-lock.json').read_text())
        for path,h in self.lock['files'].items():need(sha256((ROOT/path).read_bytes()).hexdigest()==h,'source_changed:'+path)
        self.cases={row['id']:row for row in self.lock['cases']};self.cache={}
    def load(self,case_id,expected):
        need(case_id in self.cases,'unknown_case');entry=self.cases[case_id]
        need(expected==entry['sha256'],'case_hash')
        if case_id not in self.cache:
            self.cache[case_id]=json.loads((ROOT/entry['path']).read_text())
        return self.cache[case_id]

def validate(request,retained):
    closed(request,['profile','case_id','case_sha256','policy','classifications'],'request_fields')
    need(request['profile']==PROFILE,'profile')
    policy=request['policy'];closed(policy,['reference','status','context_sha256','rationale'],'policy_fields')
    text(policy['reference']);text(policy['rationale']);need(policy['status']=='caller_assumption','unadmitted_policy_status')
    result=retained['result'];need(policy['context_sha256']==digest(result['opening']['context']),'policy_context')
    origins=result['closing']['unclassified_cash_origins'];rows=request['classifications']
    need(type(rows) is list and len(rows)<=len(origins),'classification_count')
    selected={}
    for row in rows:
        need(type(row) is dict and row.get('status') in {'declared','unknown'},'classification_status')
        closed(row,['origin_index','origin_sha256','status']+(['components'] if row['status']=='declared' else ['reason']),'classification_fields')
        idx=row['origin_index'];need(type(idx) is int and 0<=idx<len(origins),'origin_index')
        need(idx not in selected,'duplicate_origin');need(row['origin_sha256']==origin_digest(origins[idx]),'origin_binding')
        selected[idx]=row
        if row['status']=='unknown':text(row['reason']);continue
        components=row['components'];need(type(components) is list and 1<=len(components)<=16,'component_count')
        ids=set();total=Q(0);native=Q(origins[idx]['amount'])
        for part in components:
            closed(part,['id','amount','activity','policy_reference'],'component_fields')
            text(part['id']);need(part['id'] not in ids,'duplicate_component');ids.add(part['id'])
            need(part['activity'] in ACTIVITIES,'unknown_activity');need(part['policy_reference']==policy['reference'],'policy_reference')
            q=amount(part['amount']);need(q*native>=0 and (native!=0 or q==0),'offsetting_components');total+=q
        need(total==native,'component_sum')
    return origins,selected

def evaluate(request,library):
    retained=library.load(request['case_id'],request['case_sha256']);origins,selected=validate(request,retained)
    result=retained['result'];opening=result['opening'];context=opening['context'];trace=result['trace']
    root=bridge.algebra.Root.create(result['root']['context'],result['root']['rate'])
    def value(w):return bridge.algebra.Expr.from_wire(root,w)
    # Original immutable native projection remains the financial comparator.
    need(result['status']=='proposed_exact_read_only' and result['mutations']==[],'projection_status')
    need(result['unclassified_report_probe']['result']['reason']=='statement_reconciliation','original_refusal_lost')
    ownership=[];prior=[]
    for journal in trace:
        current=journal['after']['unclassified_cash_origins']
        need(current[:len(prior)]==prior,'origin_history')
        for idx in range(len(prior),len(current)):
            origin=current[idx];need(origin['date']==journal['date'],'origin_date')
            ownership.append({'origin_index':idx,'native_journal_id':journal['native_journal_id'],
                'event_id':journal['event_id'],'origin':deepcopy(origin)})
        prior=current
    need(prior==origins and len(ownership)==len(origins),'origin_coverage')
    all_flows=[];origin_records=[]
    for owner in ownership:
        idx=owner['origin_index'];origin=origins[idx];row=selected.get(idx)
        reason='missing_classification' if row is None else row.get('reason')
        mapped={'origin_index':idx,'origin_sha256':origin_digest(origin),**deepcopy(owner),
            'classification':deepcopy(row) if row is not None else {'status':'unknown','reason':reason}}
        origin_records.append(mapped)
        if row is None or row['status']=='unknown':continue
        for part in row['components']:
            all_flows.append({'origin_index':idx,'component_id':part['id'],
                'host_flow':{'id':digest([PROFILE,request['case_sha256'],idx,part['id']]),
                    'entity':context['entity'],'book':context['book'],'currency':context['currency'],
                    'event_id':owner['event_id'],'date':origin['date'],'activity':part['activity'],
                    'origin':'native '+origin['kind']+'; component '+part['id']+'; '+request['policy']['reference'],
                    'amount':part['amount']}})
    mapping={'profile':bridge.reports.MAP,'context':deepcopy(context),'lines':[
        {'id':a,'label':a,'classification':info['classification'],'accounts':[a]} for a,info in opening['accounts'].items()]}
    rational={r['native_stage_id']:r for r in result['rational_host_checks']};observations=[]
    for observation in result['observations']:
        state=trace[observation['journal_prefix']-1]['after'];prefix=len(state['unclassified_cash_origins'])
        missing=[i for i in range(prefix) if i not in selected or selected[i]['status']=='unknown']
        flows=[deepcopy(f['host_flow']) for f in all_flows if f['origin_index']<prefix]
        activities={}
        for activity in ACTIVITIES:
            qs=[Q(f['amount']) for f in flows if f['activity']==activity]
            receipts=sum((q for q in qs if q>=0),Q(0));payments=-sum((q for q in qs if q<0),Q(0))
            activities[activity]={'receipts':fmt(receipts),'payments':fmt(payments),'net':fmt(receipts-payments)}
        cash=sum((Q(o['amount']) for o in origins[:prefix]),Q(0))
        need((value(observation['report']['cash_change'])-cash).zero,'native_cash_reconciliation')
        assigned=sum((Q(f['amount']) for f in flows),Q(0));unclassified=sum((Q(origins[i]['amount']) for i in missing),Q(0))
        need(assigned+unclassified==cash,'classified_prefix_reconciliation')
        if not missing:need(assigned==cash,'complete_cash_reconciliation')
        rc=rational[observation['native_stage_id']];host_report=None
        if not missing and rc['status']=='rational_book_validated':
            book=deepcopy(rc['book']);book['flows']=flows
            host_report=bridge.reports.report(bridge.reports.request(opening,book,result['schemas'],mapping))
            need(host_report['status']=='reported','rational_host_report_refused')
            need(host_report['cash_flows']['activities']==activities,'host_activity_mismatch')
            for target,native_key in [('total_assets','assets'),('total_liabilities','liabilities'),('equity_including_profit','equity_including_profit')]:
                need((value(observation['report'][native_key])-Q(host_report['balance_sheet'][target])).zero,'host_balance_mismatch')
            need((value(observation['report']['profit'])-Q(host_report['income']['profit'])).zero,'host_profit_mismatch')
        observations.append({'native_stage_id':observation['native_stage_id'],'date':observation['date'],
            'journal_prefix':observation['journal_prefix'],'origin_prefix':prefix,'state_sha256':observation['state_sha256'],
            'status':'unresolved' if missing else 'classified_under_supplied_premise',
            'missing_origin_indexes':missing,'known_activity_totals':activities,
            'totals_scope':'classified_subset_only' if missing else 'complete_retained_cash_origins',
            'unclassified_net':fmt(unclassified),'native_cash_change':fmt(cash),
            'gross_flows':flows,'native_report':deepcopy(observation['report']),
            'host_report':host_report,'host_comparison_status':'unresolved_classification' if missing else
                'checked' if host_report else 'nonrational_financial_state_not_rounded'})
    return {'profile':PROFILE,'status':observations[-1]['status'],'case_id':request['case_id'],
        'case_sha256':request['case_sha256'],'request_sha256':digest(request),'policy':deepcopy(request['policy']),
        'native_projection_sha256':digest(result),'root':deepcopy(result['root']),
        'origins':origin_records,'observations':observations,'mutations':[],
        'posts':False,'source_admission':False,'accounting_admission':False,'fiscal_complete':False,'notes_complete':False,
        'unresolved':['Actual classification-policy and issuer facts','Source/authority admission',
            'Full indirect cash bridge','General multi-root or arbitrary-operation support']}

def assess(request,library):
    try:return evaluate(request,library)
    except (Invalid,KeyError,TypeError,ValueError,IndexError) as exc:
        return {'profile':PROFILE,'status':'invalid','reason':str(exc),'mutations':[],
            'posts':False,'source_admission':False,'accounting_admission':False}
