"""Explicit native dispatch for complete authored methods; no accounting admission."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE.parent/'complete-method-authoring-20261026'))
import frontend
import company_method_clock_v2 as prior
base=frontend.v1;core=base.core;digest=core.digest
REGISTRY='AuthoredMethodRegistry/1';PROFILE='AuthoredMethodCall/1'
MAX_ENTRIES=prior.MAX_ENTRIES;FLAGS=prior.FLAGS
Unsupported=prior.Unsupported
FIELDS=['method_sha256','method','schemas','account_classes','event_inputs','metadata_bindings','clock',
        'transition_profile','source','source_sha256']

def request_for(book,entry,event):
    request=prior.transition_request(book,entry,event)
    request['profile']=entry['transition_profile']
    if entry['transition_profile']==frontend.v2.PROFILE:request['memory_definition']=deepcopy(entry['memory_definition'])
    return request

def materialize(book,call):
    prior.protected();frontend.v2.types.protected()
    core.need(len(core.canonical(call))<=core.MAX_BYTES,'call_size_limit')
    base.closed(call,['profile','expected_state_sha256','expected_registry_sha256','registry','method_key','event'])
    core.need(call['profile']==PROFILE,'call_profile')
    core.need(call['expected_state_sha256']==digest(book),'stale_state')
    registry=call['registry'];base.closed(registry,['profile','context','entries'])
    core.need(registry['profile']==REGISTRY,'registry_profile')
    core.need(call['expected_registry_sha256']==digest(registry),'registry_digest')
    core.need(registry['context']==book['context'],'registry_context')
    entries=registry['entries'];core.need(type(entries) is dict and 0<len(entries)<=MAX_ENTRIES,'registry_entry_limit')
    event=call['event'];base.closed(event,['id','date','inputs'])
    base.text(event['id'],'event_id');core.scalar(event['date'],'date');core.need(type(event['inputs']) is dict,'event_inputs')
    for key,entry in entries.items():
        base.text(key,'method_key');core.need(type(entry) is dict,'entry_record')
        profile=entry.get('transition_profile')
        if profile not in frontend.ENGINES:raise Unsupported('transition_profile:'+str(profile))
        base.closed(entry,FIELDS+(['memory_definition'] if profile==frontend.v2.PROFILE else []))
        core.need(entry['method_sha256']==digest(entry['method']),'method_digest')
        core.need(type(entry['source']) is str,'source_text')
        core.need(sha256(entry['source'].encode('utf-8')).hexdigest()==entry['source_sha256'],'source_digest')
        authored=frontend.lower(entry['source'])
        core.need(authored['method']==entry['method'],'source_method_correspondence')
        core.need(authored['transition_profile']==profile,'source_transition_correspondence')
        base.closed(entry['clock'],['kind'])
        if entry['clock']['kind']!='direct_event_date':raise Unsupported('clock_family:'+str(entry['clock']['kind']))
        declared=prior.event_declarations(entry['method']);supplied=entry['event_inputs'];metadata=entry['metadata_bindings']
        core.need(type(supplied) is dict and type(metadata) is dict,'input_declarations')
        core.need(not set(supplied)&set(metadata),'metadata_input_overlap')
        core.need(set(supplied)|set(metadata)==set(declared),'event_input_population')
        for name,typ in supplied.items():
            base.text(name,'event_input');base.scalar_type(typ,book);core.need(typ==declared[name],'supplied_input_type')
        for name,field in metadata.items():
            base.text(name,'metadata_input');core.need(field in ['id','date'],'metadata_field')
            core.need(declared[name]=={'kind':'date' if field=='date' else 'text','context':{}},'metadata_type')
        mapping=entry['method']['account_map'];classes=entry['account_classes']
        core.need(type(classes) is dict and set(classes)==set(mapping),'role_class_population')
        for role,account in mapping.items():
            core.need(account in book['accounts'],'unregistered_account')
            core.need(book['accounts'][account]['classification']==classes[role],'role_class_mismatch')
        placeholder={'id':event['id'],'date':event['date'],'inputs':{
            name:{'type':deepcopy(typ),'value':{'status':'unknown','reason':'static_registry_check'},
                  'provenance':'Unknown structural probe only'} for name,typ in supplied.items()}}
        frontend.ENGINES[profile].prepare(book,request_for(book,entry,placeholder))
    selected=call['method_key'];base.text(selected,'selected_method')
    if selected not in entries:raise Unsupported('unregistered_method:'+selected)
    entry=entries[selected];core.need(set(event['inputs'])==set(entry['event_inputs']),'supplied_input_population')
    for name,value in event['inputs'].items():
        base.closed(value,['type','value','provenance']);core.need(value['type']==entry['event_inputs'][name],'event_type_mismatch')
    request=request_for(book,entry,event);frontend.ENGINES[entry['transition_profile']].prepare(book,request)
    return request

def failure(exc):
    return {'profile':PROFILE,**FLAGS,'status':'unsupported' if isinstance(exc,Unsupported) else 'invalid',
            'reason':str(exc)[:300] or type(exc).__name__}

def propose(book,call):
    try:
        request=materialize(book,call);engine=frontend.ENGINES[request['profile']]
        result=engine.propose(book,request)
        return {'profile':PROFILE,**FLAGS,'status':result['status'],'call_sha256':digest(call),'before_sha256':digest(book),
                'registry_sha256':digest(call['registry']),'method_key':call['method_key'],'materialized_request':request,
                'transition':result,'implementation_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),
                'frontend_sha256':sha256(Path(frontend.__file__).read_bytes()).hexdigest(),
                'engine_sha256':sha256(Path(engine.__file__).read_bytes()).hexdigest()}
    except Exception as exc:return failure(exc)

def apply(book,call,proposal):
    try:
        base.memory.bounded(proposal)
        expected=propose(book,call)
        core.need(core.canonical(expected)==core.canonical(proposal),'proposal_recomputation_mismatch')
        if expected['status']!='proposed':return expected
        request=expected['materialized_request'];engine=frontend.ENGINES[request['profile']]
        applied=engine.apply(book,request,expected['transition'])
        return {**deepcopy(expected),'status':applied['status'],'transition':applied}
    except Exception as exc:return failure(exc)
