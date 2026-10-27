"""Constructed opening books and independent checks for exact credit mapping."""
from copy import deepcopy
from datetime import date,timedelta
from fractions import Fraction as Q
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'scripts'))
import credit_linked_book_v1 as bridge

def fixture(case='partial-early-writeoff',chart='named',complement=True):
    linked_request=bridge.linked.request(case);exact=bridge.linked.calculate(linked_request)
    req=linked_request['native_request'];roles={r:('credit.'+r if chart=='named' else 'C'+str(100+i)) for i,r in enumerate(bridge.ROLES)}
    capital='owner.capital' if chart=='named' else 'H901'
    equipment='owner.equipment' if chart=='named' else 'H902'
    context={'entity':req['context']['entity'],'book':'legal','currency':'XCU','case_id':'retained-credit-'+case,'mode':'synthetic'}
    shape={'type':'object','properties':{'tag':{'type':'string','minLength':1,'maxLength':4096}},'required':['tag'],'additionalProperties':False}
    h=bridge.host.digest(shape);accounts={roles[r]:{'classification':c} for r,c in bridge.ROLES.items()}
    accounts[capital]={'classification':'equity'}
    balances={a:'0/1' for a in accounts};balances[roles['cash']]=bridge.fmt(req['opening_cash'])
    balances[capital]=bridge.fmt(-Q(req['opening_cash'])-(17 if complement else 0))
    if complement:accounts[equipment]={'classification':'asset'};balances[equipment]='17/1'
    start=req['acquisition']['date'];end=(date.fromisoformat(exact['schedule']['closing']['date'])+timedelta(days=1)).isoformat()
    opening={'profile':bridge.host.BOOK,'context':context,'period':{'start':start,'end_exclusive':end},'date':start,
        'accounts':accounts,'balances':balances,'cash_account':roles['cash'],'memory_schema':h,
        'memory_types':{'/tag':{'kind':'text','context':{}}},'memory':{'tag':'Preserve quoted "credit" and Ω'},
        'seen':[],'flows':[]}
    return {'profile':bridge.PROFILE,'operation':'project','linked_request':linked_request,
        'expected_linked_result_sha256':bridge.digest(exact),'opening':opening,'schemas':{h:shape},'roles':roles,
        'context_adapter':{'native_context_sha256':bridge.digest(req['context']),'host_context_sha256':bridge.digest(context),
            'unit_scale':'1/1','premise':'XCU is an illustrative host label for CU at scale1/1; no FX or accounting admission.'}}

def checked_case(case,chart,complement):
    request=fixture(case,chart,complement);before=deepcopy(request);result=bridge.propose(request)
    assert result['status']=='proposed_exact_read_only',result
    assert request==before and result['mutations']==[]
    assert all(result[k] is False for k in bridge.FLAGS)
    root=bridge.algebra.Root.create(result['root']['context'],result['root']['rate'])
    def value(w):return bridge.algebra.Expr.from_wire(root,w)
    roles=request['roles'];exact=result['linked_result']['schedule'];opening=request['opening']
    native_stages={s['id']:s for s in exact['stages']}
    assert len(result['trace'])==len(exact['journals']) and len(result['observations'])==len(exact['stages'])
    for actual,native in zip(result['trace'],exact['journals']):
        assert actual['native_journal']==native and actual['date']==native['date']
        assert [p['role'] for p in actual['gross_postings']]==list(native['entries'])
        assert [p['amount'] for p in actual['gross_postings']]==list(native['entries'].values())
        assert actual['after']['memory']==opening['memory']
        for account,amount in opening['balances'].items():
            if account not in roles.values():assert value(actual['after']['balances'][account]).rational_projection()==Q(amount)
    for row in result['observations']:
        stage=native_stages[row['native_stage_id']];state=result['trace'][row['journal_prefix']-1]['after']
        assert bridge.digest(state)==row['state_sha256']
        report=row['report']; extra=17 if complement else 0
        assert (value(report['assets'])-value(stage['cash'])-value(stage['net'])-extra).zero
        assert value(report['liabilities']).zero
        assert (value(report['profit'])-value(stage['profit'])).zero
        assert (value(report['equity_including_profit'])-Q(request['linked_request']['native_request']['opening_cash'])-extra-value(stage['profit'])).zero
        assert (value(state['balances'][roles['allowance']])+value(stage['allowance'])).zero
    assert result['closing']['unclassified_cash_origins']==exact['cash_flows']
    assert result['unclassified_report_probe']['result']['reason']=='statement_reconciliation'
    if case in ['unchanged-annual','zero-rate','three-irregular-receipts']:
        assert all(r['status']=='rational_book_validated' for r in result['rational_host_checks'])
    return {'id':'.'.join([case,chart,'complement' if complement else 'plain']),
        'request':request,'result':result,'expected':{'chart':chart,'complement':complement,
            'journal_count':len(exact['journals']),'stage_count':len(exact['stages']),
            'native_final_cash':str(value(exact['closing']['cash']).rational_projection()),
            'unclassified_report_refused':True}}
