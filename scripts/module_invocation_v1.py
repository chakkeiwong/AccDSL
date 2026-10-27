"""Pinned finite module invocation; no shared-book merge or durable commit."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import importlib.util
import json

ROOT=Path(__file__).resolve().parents[1]
PACKAGE=ROOT/'data/accounting-master/module-invocation-20261024'
LOCK_SHA256='5a0fcd4b08703ea7422328872743dc1b2c3761b2d6963574ccd80ce56ea081ca'
PROFILE='ModuleInvocation/1'
RESULT='ModuleResult/1'
MAX_BYTES=2000000
MAX_NODES=100000
MAX_DEPTH=64
FLAGS={'executed':False,'committed':False,'physical_durability':False,
       'source_admission':False,'accounting_admission':False,'method_eligible':False,
       'shared_book_composition_established':False}
SPECS={
 'typed_return':('transition_proposal','propose','scripts/typed_return_transition_v1.py',
                 ['state_text','state_raw_sha256','event_text','event_raw_sha256'],
                 ['scripts/native_return_state_structure_v1.py','data/accounting-master/company-return-schema-20261023/return_schema.py']),
 'shared_lease':('transition_proposal','propose','scripts/lease_shared_book_v1.py',
                 ['state','event'],['scripts/lease_shared_book_v1.py','data/accounting-master/extended-method-exchanges-20261015/corporate-residuals/type_design.py']),
 'henkel_measurements':('measurement','assess','scripts/henkel_lease_measurements_v1.py',
                 ['request','budget'],['scripts/henkel_lease_measurements_v1.py']),
 'sector_report':('report','report','data/accounting-master/sector-company-composition-20261016/reference.py',
                 ['request'],['data/accounting-master/sector-company-composition-20261016/reference.py']),
}

class Invalid(ValueError):pass
def need(ok,why):
    if not ok:raise Invalid(why)
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def digest(x):return sha256(canonical(x)).hexdigest()
def closed(x,fields):need(type(x) is dict and set(x)==set(fields),'closed_fields')

def bounded(value):
    stack=[(value,0)];count=0
    while stack:
        x,depth=stack.pop();count+=1
        need(count<=MAX_NODES and depth<=MAX_DEPTH,'input_structure_limit')
        if type(x) is dict:
            need(all(type(k) is str for k in x),'string_keys_required')
            stack.extend((v,depth+1) for v in x.values())
        elif type(x) is list:stack.extend((v,depth+1) for v in x)
        else:need(type(x) in [str,int,bool,type(None)],'portable_input_type')
    need(len(canonical(value))<=MAX_BYTES,'input_byte_limit')

def dependencies():
    raw=(PACKAGE/'dependency-lock.json').read_bytes()
    need(sha256(raw).hexdigest()==LOCK_SHA256,'dependency_lock_changed')
    d=json.loads(raw)
    for name,h in d.items():need(sha256((ROOT/name).read_bytes()).hexdigest()==h,'dependency_changed:'+name)
    return d

def registry():
    locks=dependencies();entries={}
    for key,(capability,operation,path,fields,schemas) in SPECS.items():
        entries[key]={'module_id':key,'capability':capability,'operation':operation,
                      'implementation':{'path':path,'sha256':locks[path]},
                      'payload_fields':fields,'schema_authorities':{n:locks[n] for n in schemas},
                      'bundle_sha256':LOCK_SHA256,'commit_supported':False,
                      'scope':'exact native profile; no owner/currency conversion or state merge'}
    return {'profile':'ModuleRegistry/1','caller_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),'entries':entries}

def request(module_id,payload,operation=None):
    r=registry();need(type(module_id) is str and module_id in r['entries'],'unknown_module')
    d=r['entries'][module_id]
    return {'profile':PROFILE,'module_id':module_id,'operation':d['operation'] if operation is None else operation,
            'registry_sha256':digest(r),'descriptor_sha256':digest(d),'payload_sha256':digest(payload),'payload':deepcopy(payload)}

def prepare(body):
    bounded(body);closed(body,['profile','module_id','operation','registry_sha256','descriptor_sha256','payload_sha256','payload'])
    need(body['profile']==PROFILE,'profile')
    r=registry();key=body['module_id'];need(type(key) is str and key in r['entries'],'unknown_module')
    d=r['entries'][key]
    need(body['registry_sha256']==digest(r),'registry_hash')
    need(body['descriptor_sha256']==digest(d),'descriptor_hash')
    need(body['payload_sha256']==digest(body['payload']),'payload_hash')
    need(type(body['operation']) is str,'operation_type')
    closed(body['payload'],d['payload_fields'])
    return d

def native_call(key,payload):
    # The dispatch table is code-owned. No request field is a module path,
    # Python callable or caller-selected callback.
    if key=='typed_return':
        import typed_return_transition_v1 as native
        need(type(payload['state_text']) is str and type(payload['event_text']) is str,'raw_text_required')
        return native.propose(payload['state_text'].encode('utf-8'),payload['state_raw_sha256'],
                              payload['event_text'].encode('utf-8'),payload['event_raw_sha256'])
    if key=='shared_lease':
        import lease_shared_book_v1 as native
        return native.propose(deepcopy(payload['state']),deepcopy(payload['event']))
    if key=='henkel_measurements':
        import henkel_lease_measurements_v1 as native
        return native.assess(deepcopy(payload['request']),deepcopy(payload['budget']))
    path=ROOT/SPECS['sector_report'][2]
    spec=importlib.util.spec_from_file_location('invocation_fixed_sector_report',path)
    native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native)
    return native.calculate(deepcopy(payload['request']))

def invoke(body):
    try:
        d=prepare(body)
        if body['operation']!=d['operation']:
            return {'profile':RESULT,**FLAGS,'status':'unsupported','reason':'capability_mismatch',
                    'module_id':body['module_id'],'capability':d['capability'],'supported_operation':d['operation'],
                    'request_sha256':digest(body),'native_result':None}
        result=native_call(body['module_id'],body['payload'])
        need(type(result) is dict and type(result.get('status')) is str,'native_result_shape')
        return {'profile':RESULT,**FLAGS,'status':'returned','module_id':body['module_id'],
                'capability':d['capability'],'operation':body['operation'],'request_sha256':digest(body),
                'descriptor_sha256':digest(d),'bundle_sha256':LOCK_SHA256,
                'native_status':result['status'],'native_result':result,'native_result_sha256':digest(result)}
    except (Invalid,ValueError,TypeError,KeyError,AttributeError,OSError,RecursionError,OverflowError) as exc:
        return {'profile':RESULT,**FLAGS,'status':'invalid','reason':str(exc)[:300],'native_result':None}

def verify_result(body,result):
    """Replay caller bindings and all native fields; allow valid solver witnesses."""
    try:
        replay=invoke(body)
        need(type(result) is dict and set(result)==set(replay),'result_fields')
        if replay['status']!='returned':return result==replay
        for key in replay:
            if key not in ['native_result','native_result_sha256']:need(result[key]==replay[key],'result_changed:'+key)
        need(result['native_result_sha256']==digest(result['native_result']),'native_result_hash')
        if body['module_id']=='henkel_measurements':
            import henkel_lease_measurements_v1 as native
            need(native.verify_result(body['payload']['request'],body['payload']['budget'],result['native_result']),'native_measurement_replay')
        else:need(canonical(result['native_result'])==canonical(replay['native_result']),'native_result_replay')
        return True
    except (Invalid,ValueError,TypeError,KeyError,AttributeError,OSError,RecursionError,OverflowError):return False
