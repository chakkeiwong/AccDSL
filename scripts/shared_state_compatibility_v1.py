"""Read-only compatibility of two native state views; never composes books."""
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import json
import module_invocation_v1 as caller

ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/'data/accounting-master/shared-state-compatibility-20261024'
LOCK='9f9f0c6d33f47f3d7603b4049e128a71fd71609dd18f139dec6249157cdab1f6'
PROFILE='SharedStateCompatibility/1'
FLAGS={'executed':False,'committed':False,'source_admission':False,
       'accounting_admission':False,'shared_book_composition_established':False}
MODULES={'typed_return':'NativeReturnBookReference/1','shared_lease':'SharedLeaseBook/1'}

def protected():
    raw=(HERE/'source-lock.json').read_bytes()
    caller.need(sha256(raw).hexdigest()==LOCK,'source_lock_changed')
    for name,h in json.loads(raw).items():
        caller.need(sha256((ROOT/name).read_bytes()).hexdigest()==h,'protected_source_changed:'+name)

def request(left_module,left_state,right_module,right_state):
    def side(module,state):return {'module_id':module,'state':deepcopy(state),'state_sha256':caller.digest(state)}
    return {'profile':PROFILE,'left':side(left_module,left_state),'right':side(right_module,right_state)}

def validation(key,state):
    try:
        if key=='typed_return':
            import native_return_state_structure_v1 as native
            native.validate(state,native.schema());native.native.invariant(state)
            caller.need(state['context']['currency']=='USD' and state['context']['book_role']=='legal','selected_USD_legal_profile_only')
        else:
            import lease_shared_book_v1 as native
            native.invariant(state)
        return {'status':'valid'}
    except (ValueError,KeyError,TypeError,AttributeError,RecursionError) as exc:
        return {'status':getattr(exc,'status','invalid'),'reason':getattr(exc,'reason',str(exc))[:300]}

def dimensions(key,state):
    c=state.get('context',{});c=c if type(c) is dict else {}
    return {'owner':c.get('entity' if key=='typed_return' else 'entity_id'),
            'book':c.get('book_role' if key=='typed_return' else 'book_id'),
            'currency':c.get('currency'),'date':state.get('date'),'period':state.get('period')}

def unknown(value):
    if type(value) is dict:return any(unknown(x) for x in value.values())
    if type(value) is list:return any(unknown(x) for x in value)
    return value is None or value=='unknown'

def assess(body):
    try:
        caller.bounded(body);caller.closed(body,['profile','left','right'])
        caller.need(body['profile']==PROFILE,'profile');protected()
        for side in ['left','right']:
            x=body[side];caller.closed(x,['module_id','state','state_sha256'])
            caller.need(type(x['module_id']) is str and x['module_id'] in MODULES,'unknown_module')
            caller.need(type(x['state']) is dict,'state_object')
            caller.need(x['state_sha256']==caller.digest(x['state']),'stale_state_digest')
        l,r=body['left'],body['right'];ls,rs=l['state'],r['state']
        validations={k:validation(body[k]['module_id'],body[k]['state']) for k in ['left','right']}
        dl,dr=dimensions(l['module_id'],ls),dimensions(r['module_id'],rs)
        conflicts=[];missing=[]
        for field in dl:
            if unknown(dl[field]) or unknown(dr[field]):missing.append({'field':field,'reason':'unknown_context'})
            elif dl[field]!=dr[field]:conflicts.append({'field':field,'left':dl[field],'right':dr[field]})
        same=l['module_id']==r['module_id']
        if not same:
            conflicts.append({'field':'native_profile','left':MODULES[l['module_id']],'right':MODULES[r['module_id']]})
            for field in ['account_semantics','module_memory','flow_ownership','tax_policy','report_policy','source_scope']:
                missing.append({'field':field,'reason':'no_cross_profile_adapter'})
        elif ls!=rs:conflicts.append({'field':'before_state','reason':'different_state_snapshots'})
        for side,v in validations.items():
            if v['status']!='valid':
                target=missing if v['status']=='unresolved' else conflicts
                target.append({'field':side+'_native_validation','reason':v['status']+':'+v.get('reason','')})
        lb=ls.get('balances',{});rb=rs.get('balances',{})
        caller.need(type(lb) is dict and type(rb) is dict,'balance_objects')
        account_comparison={'shared_names':sorted(set(lb)&set(rb)),
          'left_only':sorted(set(lb)-set(rb)),'right_only':sorted(set(rb)-set(lb)),
          'shared_names_prove_equivalence':False,
          'mapping_status':'same_native_registry' if same else 'unresolved'}
        status='incompatible' if conflicts else 'unresolved' if missing else 'compatible'
        return {'profile':PROFILE,**FLAGS,'status':status,'request_sha256':caller.digest(body),
                'source_bundle_sha256':LOCK,'native_validations':validations,'conflicts':conflicts,
                'missing_evidence':missing,'accounts':account_comparison,
                'scope':'same-profile same-state compatibility only; no joint transition authorization'}
    except (ValueError,KeyError,TypeError,AttributeError,OSError,RecursionError,OverflowError) as exc:
        return {'profile':PROFILE,**FLAGS,'status':'invalid','reason':str(exc)[:300]}

def verify_result(body,result):return result==assess(body)
