from pathlib import Path
from copy import deepcopy
import json,sys
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'scripts'))
import shared_book_successor_v1 as m

def sources():return json.loads((ROOT/'data/accounting-master/shared-state-compatibility-20261024/native-effects.json').read_text())
def opening():
    x=sources();s=deepcopy(x['typed_return']['before']);s['profile']=m.PROFILE;s['context']=deepcopy(m.CONTEXT)
    s['source']={'meaning':'declared_synthetic_book',
      'premise':'New synthetic joint owner; numeric templates are not admitted original books or issuer facts.',
      'numeric_lineage':'shared-state-compatibility-20261024/native-effects.json; return and lease component inputs reused. Opening equity expressly 20, not inferred.'}
    s['period']={'start':'2024-01-01','end_exclusive':'2026-01-01'};s['date']='2024-01-01';s['tax_closed_until']='2024-01-01'
    s['balances']={'cash':'500/1','inventory':'60/1','ppe':'100/1','recovery_asset':'16/1','investment':'80/1','dta':'10/1','dtl':'-4/1',
      'refund_liability':'-40/1','debt':'-100/1','receivable':'0/1','payable':'0/1','capital':'-600/1','retained':'-12/1',
      'original_equity':'20/1','revenue':'0/1','cogs':'0/1','selling_expense':'0/1','wages':'0/1','depreciation':'0/1',
      'finance_expense':'0/1','current_tax':'0/1','deferred_tax':'0/1','rou':'120/1','lease_liability':'-150/1','other_gains':'0/1'}
    s['leases']=deepcopy(x['shared_lease']['before']['leases'])
    for item in s['leases']:item['instantiation_premise']='New synthetic owner instantiates the retained component amounts and annual payment assumptions.'
    s['lease_membership']=True;s['lease_membership_premise']='This synthetic opening contains exactly the listed lease rights.'
    return s

def event(module,e):return {'profile':m.EVENT,'module':module,'event':deepcopy(e)}
def events():
    x=sources();reduce=x['shared_lease']['event'];settle=deepcopy(x['typed_return']['event']);settle['date']='2024-02-01'
    reduce={k:deepcopy(reduce[k]) for k in ['id','date','method','lease_id','parameters']}
    sale={'id':'sale','kind':'sell','method':'inventory.sell','date':'2024-03-01','source_pointer':settle['source_pointer'],'lot_id':settle['lot_id'],'fraction':'1/1','proceeds':'30/1','performance_complete':True}
    pay={'id':'lease_payment','date':'2025-01-01','method':'lease.pay','lease_id':'lease1','parameters':{'right_id':'A','amount':'121/1','one_year_elapsed':True,'no_intervening_accrual_or_modification':True}}
    dep={'id':'lease_depreciation','date':'2025-01-01','method':'lease.depreciate','lease_id':'lease1','parameters':{'right_id':'A','amount':'10/1','systematic_allocation_supported':True}}
    return [event('lease',reduce),event('return',settle),event('return',sale),event('lease',pay),event('lease',dep)]

def cases():
    rows=[]
    def add(name,s,ev,status,stop=None):rows.append({'case':name,'opening':s,'events':ev,'expected_status':status,'expected_stop':stop})
    add('mixed_lifecycle',opening(),events(),'complete')
    add('lease_only',opening(),[events()[0],events()[3],events()[4]],'complete')
    add('return_only',opening(),[events()[1],events()[2]],'complete')
    s=opening();s['balances']['cash']='130/1';s['balances']['original_equity']='390/1'
    add('shared_cash_competition',s,[events()[0],events()[1],events()[3]],'stopped','funding_failure')
    add('cash_control_lease_only',deepcopy(s),[events()[0],events()[3]],'complete')
    x=events()[1];x['event']['inventory_nrv']='unknown';add('unknown_return_nrv',opening(),[x],'stopped','unresolved')
    s=opening();s['lease_membership']='unknown';add('unknown_lease_membership',s,[events()[0]],'stopped','unresolved')
    x=events()[4];x['event']['parameters']['systematic_allocation_supported']=None;add('unknown_depreciation',opening(),[x],'stopped','unresolved')
    s=opening();s['context']['currency']='EUR';add('unsupported_fx',s,[events()[0]],'stopped','unsupported')
    x=events()[0];x['module']='tax';add('unsupported_tax',opening(),[x],'stopped','unsupported')
    s=opening();s['balances']['rou']='121/1';s['balances']['original_equity']='19/1';add('invalid_lease_allocation',s,[events()[0]],'stopped','invalid')
    add('duplicate_event',opening(),[events()[0],events()[0]],'stopped','invalid')
    add('out_of_order',opening(),[events()[1],events()[0]],'stopped','invalid')
    add('empty_valid_prefix',opening(),[],'complete')
    s=opening();s['balances']['cash']='0/1';add('empty_invalid_prefix',s,[],'stopped','invalid')
    return rows

def native_comparators():
    from hashlib import sha256
    rows=[];src=sources();new=opening();old_return=deepcopy(src['typed_return']['before']);old_lease=deepcopy(src['shared_lease']['before'])
    for event_body in events():
        proposed=m.propose(new,event_body);assert proposed['status']=='proposed',proposed
        ev=deepcopy(event_body['event'])
        if event_body['module']=='return':
            # The native comparison stays in its original 2025 period.
            ev['date']='2025'+ev['date'][4:];a=m.caller.canonical(old_return);b=m.caller.canonical(ev)
            original=m.returns.propose(a,sha256(a).hexdigest(),b,sha256(b).hexdigest());old_before=deepcopy(old_return)
            assert original['status']=='proposed',original;old_return=original['proposal']['after']
        else:
            ev={'profile':m.lease.EVENT,'kind':'lease','original_scope_sha256':m.lease.SCOPE_HASH,**ev}
            original=m.lease.propose(old_lease,ev);old_before=deepcopy(old_lease)
            assert original['status']=='proposed',original;old_lease=original['proposal']['after']
        rows.append({'module':event_body['module'],'successor_before':new,'successor_event':event_body,'successor_result':proposed,
                     'original_before':old_before,'original_event':ev,'original_result':original,
                     'comparison_scope':'same component numerical inputs; separately declared owner and return dates'})
        new=proposed['proposal']['after']
    return rows
