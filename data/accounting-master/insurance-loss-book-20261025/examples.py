"""Explicit host books and independent retained insurer schedule expectations."""
from copy import deepcopy
from pathlib import Path
from fractions import Fraction
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts'))
import insurance_loss_book_v1 as bridge


def record(fields):return {'type':'object','properties':fields,'required':list(fields),'additionalProperties':False}
def scalar(kind):return {'type':'string','minLength':1,'maxLength':4096,'x-exact-kind':kind}


def fixture(chart='named',case='loss-service-finance',complement=True):
    native=bridge.native_case(case);request=native['request'];data=request['data']
    roles={r:('ins.'+r if chart=='named' else 'I'+str(101+i)) for i,r in enumerate(bridge.ROLES)}
    capital='host.capital' if chart=='named' else 'H901'
    extra='host.equipment' if chart=='named' else 'H902'
    context={'entity':request['context']['entity'],'book':'legal','currency':'XCU',
        'case_id':'retained-insurer-'+case,'mode':'synthetic'}
    accounts={roles[r]:{'classification':kind} for r,kind in bridge.ROLES.items()}
    accounts[capital]={'classification':'equity'}
    balances={a:'0/1' for a in accounts};balances.update({roles['cash']:'200/1',roles['liability']:'-100/1',capital:'-100/1'})
    if complement:
        accounts[extra]={'classification':'asset'};balances[extra]='17/1';balances[capital]='-117/1'
    shape=record({'insurance':record({'loss_component':scalar('rational'),'next_step':scalar('rational'),'case_ref':scalar('text')}),
                  'complement':record({'tag':scalar('text')})})
    h=bridge.core.digest(shape)
    book={'profile':bridge.engine.BOOK,'context':context,'period':{'start':'2025-01-01','end_exclusive':'2027-01-02'},
        'date':'2025-01-01','accounts':accounts,'balances':balances,'cash_account':roles['cash'],
        'memory_schema':h,'memory_types':{},
        'memory':{'insurance':{'loss_component':bridge.fmt(data['loss_component']),'next_step':'0/1',
            'case_ref':bridge.core.digest(request)},'complement':{'tag':'Preserve quoted "claims" and Ω'}},'seen':[],'flows':[]}
    money=bridge.engine.money_type(book)
    count={'kind':'rational','context':bridge.engine.type_context(book),'dimensions':{},'scale':'1/1'}
    book['memory_types']={'/insurance/loss_component':money,'/insurance/next_step':count,
        '/insurance/case_ref':deepcopy(bridge.TEXT),'/complement/tag':deepcopy(bridge.TEXT)}
    mapping={'profile':bridge.program.reports.MAP,'context':deepcopy(context),
        'lines':[{'id':a,'label':a,'classification':row['classification'],'accounts':[a]} for a,row in accounts.items()]}
    return {'profile':bridge.PROFILE,'case_id':case,'native_request':request,'native_result':native['result'],
        'native_request_sha256':bridge.core.digest(request),'native_result_sha256':bridge.core.digest(native['result']),
        'opening':book,'schemas':{h:shape},'roles':roles,
        'memory_map':{k:'/insurance/'+k for k in ['loss_component','next_step','case_ref']},
        'context_adapter':{'native_context_sha256':bridge.core.digest(request['context']),
            'host_context_sha256':bridge.core.digest(context),'unit_scale':'1/1',
            'premise':'XCU is an explicit host label for the retained illustrative CU, one for one; no FX or currency admission.'},
        'mapping':mapping,'cash_policy':{'claims_activity':'operating',
            'premise':'Constructed insurer claims are operating payments in this finite host-book illustration.'}}


def checked_case(chart='named',case='loss-service-finance',complement=True):
    request=fixture(chart,case,complement);before=deepcopy(request)
    result=bridge.propose(request)
    assert result['status']=='proposed_provisional',result
    assert request==before
    assert all(result[k] is False for k in bridge.FLAGS)
    events=[r for r in result['execution']['trace'] if r['command']['kind']=='event']
    reports=[r['result'] for r in result['execution']['trace'] if r['command']['kind']=='report']
    assert len(events)==6 and len(reports)==2
    assert [r['income']['profit'] for r in reports]==['-5/1','5/1']
    assert [r['cash_flows']['closing_cash'] for r in reports]==['150/1','105/1']
    assert [r['balance_sheet']['total_liabilities'] for r in reports]==['55/1','0/1']
    extra=17 if complement else 0
    assert [r['equity']['closing'] for r in reports]==[bridge.fmt(95+extra),bridge.fmt(105+extra)]
    assert [r['cash_flows']['activities']['operating']['payments'] for r in reports]==['50/1','95/1']
    assert result['execution']['current']['memory']['insurance']['next_step']=='6/1'
    assert result['execution']['current']['memory']['insurance']['loss_component']=='0/1'
    roles=set(request['roles'].values())
    for row in events:
        after=row['result']['transition']['after']
        for account,value in request['opening']['balances'].items():
            if account not in roles:assert after['balances'][account]==value
        assert after['memory']['complement']==request['opening']['memory']['complement']
    origins=[o for step in result['expected_steps'] for o in step['loss_origins']]
    assert origins==request['native_result']['report']['loss_origins']
    assert result['native_result']==request['native_result']
    assert request['native_result']['posts'] is False
    return {'request':request,'result':result,'expected':{'cash':['150/1','105/1'],'liability':['55/1','0/1'],
        'cumulative_profit':['-5/1','5/1'],'six_journals':True,'loss_origins_once':True,'complement':complement}}


if __name__=='__main__':
    import json
    row=checked_case()
    print(json.dumps({'status':row['result']['status'],'expected':row['expected']}))
