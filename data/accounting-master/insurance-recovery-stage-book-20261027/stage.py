"""Read-only stage ledger; no dated or shared-group admission."""
from pathlib import Path
from fractions import Fraction as Q
from hashlib import sha256
from copy import deepcopy
import json
H=Path(__file__).resolve().parent;R=H.parents[2]
N=H.parent/'insurance-service-finance-origins-20261016'
PROFILE='InsuranceRecoveryStageLedger/1'
CASES=('recovery-change-once','covered-loss-exhausted')
ACCOUNTS=('cash','held_fcf','held_cost_csm','issued_liability','opening_equity',
          'issued_revenue','issued_loss_reversal','claims_expense','held_change_expense',
          'premium_allocation','held_component_expense','held_recovery_income')
ISSUED=('issued_revenue','issued_loss_reversal','claims_expense')
HELD=('held_change_expense','premium_allocation','held_component_expense','held_recovery_income')
FLAGS={'posts':False,'mutations':[],'accounting_admission':False,'fiscal_admission':False,
       'separate_group_identity_admission':False,'cash_classification_admission':False}
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False)
def digest(x):return sha256(canonical(x).encode()).hexdigest()
def need(ok,reason):
    if not ok:raise ValueError(reason)
def protected():
    lock=json.loads((H/'source-lock.json').read_text())
    for p,h in lock.items():need(sha256((R/p).read_bytes()).hexdigest()==h,'source_drift:'+p)
    return lock
def retained(ident):
    need(ident in CASES,'retained_case_required')
    return next(x for x in json.loads((N/'attempt-02/exchanges.json').read_text()) if x['id']==ident)
def request(ident):
    row=retained(ident)
    return {'profile':PROFILE,'case_id':ident,'native_request_sha256':digest(row['request']),
            'native_result_sha256':digest(row['result'])}
def project(body):
    protected();need(type(body) is dict and set(body)=={'profile','case_id','native_request_sha256','native_result_sha256'},'request_shape')
    need(body['profile']==PROFILE,'profile');row=retained(body['case_id']);req=row['request'];native=row['result']
    need(digest(req)==body['native_request_sha256'] and digest(native)==body['native_result_sha256'],'native_binding')
    need(req['operation']=='recovery_change' and native['status']=='conditional_complete','native_scope')
    d=req['data'];report=native['report'];change=report['change'];issued=report['issued_service'];held=report['held_service']
    balances={a:Q(0) for a in ACCOUNTS}
    balances.update(cash=Q(d['cash']),held_fcf=Q(d['covered_claims'])*Q(d['quota'])+Q(d['held_ra']),
        held_cost_csm=Q(d['held_cost_csm']),issued_liability=-Q(d['issued_claims'])-Q(d['issued_ra']),
        opening_equity=-Q(report['opening_equity']))
    memory={'issued_loss':Q(d['issued_loss']),'held_loss_recovery':Q(d['held_loss_recovery'])}
    journals=[];origins=[];flows=[];states=[]
    def record(name):
        need(sum(balances.values(),Q(0))==0,'trial_balance:'+name)
        ip=-sum((balances[a] for a in ISSUED),Q(0));hp=-sum((balances[a] for a in HELD),Q(0))
        equity=-balances['opening_equity']+ip+hp
        assets=sum((balances[a] for a in ['cash','held_fcf','held_cost_csm']),Q(0));liabilities=-balances['issued_liability']
        need(assets==liabilities+equity,'financial_identity:'+name)
        cashchange=balances['cash']-Q(d['cash'])
        need(cashchange==sum((Q(f['amount']) for f in flows),Q(0)),'cash_origins:'+name)
        for k in memory:
            need(memory[k]==Q(d[k])+sum((Q(o['delta']) for o in origins if o['component']==k),Q(0)),'memory_origins:'+name)
        states.append({'stage':name,'date':None,'issued_group_id':None,'held_group_id':None,
            'balances':{a:str(v) for a,v in balances.items()},'memory':{a:str(v) for a,v in memory.items()},
            'issued_profit':str(ip),'held_profit':str(hp),'total_profit':str(ip+hp),'assets':str(assets),
            'liabilities':str(liabilities),'equity':str(equity),'cash_change':str(cashchange),
            'journal_count':len(journals),'memory_origin_count':len(origins),'cash_flow_count':len(flows)})
    def apply(name,postings,mem,source,flow=None):
        postings={a:Q(v) for a,v in postings.items()};need(sum(postings.values(),Q(0))==0,'journal_balance:'+name)
        journals.append({'stage':name,'native_source':source,'postings':[{'account':a,'debit_change':str(v)} for a,v in postings.items()]})
        for a,v in postings.items():balances[a]+=v
        for k,value in mem.items():
            value=Q(value);origins.append({'stage':name,'component':k,'before':str(memory[k]),'delta':str(value-memory[k]),
                                         'after':str(value),'native_source':source});memory[k]=value
        if flow is not None:flows.append({'stage':name,**deepcopy(flow)})
        record(name)
    record('opening')
    old_held=balances['held_fcf']+balances['held_cost_csm'];loss_reverse=Q(change['issued_loss_reversal'])
    held_change=Q(change['held_asset'])-old_held
    need(change['additional_component_expense']=='0','double_component_expense')
    apply('estimate_change',{'issued_liability':loss_reverse,'issued_loss_reversal':-loss_reverse,
        'held_fcf':held_change,'held_change_expense':-held_change},
        {'issued_loss':change['issued_loss'],'held_loss_recovery':change['held_loss_recovery']},'report/change')
    apply('issued_service',{'issued_liability':change['issued_liability'],'issued_revenue':-Q(issued['revenue']),
        'issued_loss_reversal':-Q(issued['loss_reversal']),'claims_expense':issued['claim_expense'],
        'cash':-Q(issued['claim_expense'])},{'issued_loss':'0'},'report/issued_service',report['cash_flows'][0])
    apply('held_service',{'held_fcf':-balances['held_fcf'],'held_cost_csm':-balances['held_cost_csm'],
        'premium_allocation':held['premium_allocation'],'held_component_expense':held['loss_recovery_reversal'],
        'held_recovery_income':-Q(held['recovery']),'cash':held['recovery']},
        {'held_loss_recovery':'0'},'report/held_service',report['cash_flows'][1])
    need(states[-1]['total_profit']==report['total_profit'],'native_profit')
    need(states[-1]['equity']==report['closing']['equity'] and states[-1]['balances']['cash']==report['closing']['cash'],'native_closing')
    return {'profile':PROFILE,'status':'checked_stage_only','case_id':body['case_id'],
        'native_request_sha256':digest(req),'native_result_sha256':digest(native),'native_context':deepcopy(req['context']),
        'native_result':deepcopy(native),'stages':states,'journals':journals,'memory_origins':origins,'cash_origins':flows,
        'unresolved':['economic_dates','distinct_issued_and_held_group_identifiers','fiscal_opening_and_carry',
                      'applicable_accounting_admission','cash_flow_classification'],**deepcopy(FLAGS)}
def assess(body):
    try:return project(body)
    except (ValueError,TypeError,KeyError,OSError,IndexError) as exc:return {'profile':PROFILE,'status':'rejected','reason':str(exc),**deepcopy(FLAGS)}
def validate(body,record,identity):
    try:
        need(digest(record)==identity,'record_hash');need(canonical(project(body))==canonical(record),'record_mismatch')
        return {'status':'verified_stage_only'}
    except (ValueError,TypeError,KeyError,OSError,IndexError) as exc:return {'status':'rejected','reason':str(exc)}
