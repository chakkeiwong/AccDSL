"""Named data-only methods and direct-event clocks; no posting admission."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import company_book_transition_v1 as transition

core=transition.core
REGISTRY='CompanyMethodRegistry/1'
PROFILE='CompanyMethodCall/1'
MAX_ENTRIES=32
TRANSITION_SHA256='3f46df2d4c7b65f344c0a1234177503a0869b9162b4a85bdda224c2eddbea8ff'
FLAGS=transition.FLAGS
digest=core.digest


class Unsupported(ValueError):pass


def protected():
    core.need(sha256(Path(transition.__file__).read_bytes()).hexdigest()==TRANSITION_SHA256,'transition_dependency_hash')
    transition.protected()


def event_declarations(method):
    declarations={}
    for key in ['preconditions','postconditions','monetary']:
        part=method[key];inputs=part['definition' if key=='monetary' else 'manifest']['inputs']
        for name,source in part['bindings'].items():
            if source['kind']=='event':
                event_name=source['name'];typ=inputs[name]['type']
                core.need(event_name not in declarations or declarations[event_name]==typ,'conflicting_event_types')
                declarations[event_name]=deepcopy(typ)
    return declarations


def event_for(entry,event):
    inputs=deepcopy(event['inputs'])
    for name,field in entry['metadata_bindings'].items():
        inputs[name]={'type':{'kind':'date' if field=='date' else 'text','context':{}},
                      'value':transition.known(event[field]),
                      'provenance':'Bound from actual event metadata:'+field}
    return {'id':event['id'],'date':event['date'],'inputs':inputs}


def transition_request(book,entry,event):
    return {'profile':transition.PROFILE,'expected_state_sha256':digest(book),
            'expected_method_sha256':entry['method_sha256'],'method':deepcopy(entry['method']),
            'event':event_for(entry,event),'schemas':deepcopy(entry['schemas'])}


def materialize(book,call):
    protected();transition.memory.bounded(call)
    transition.closed(call,['profile','expected_state_sha256','expected_registry_sha256','registry','method_key','event'])
    core.need(call['profile']==PROFILE,'call_profile')
    core.need(call['expected_state_sha256']==digest(book),'stale_state')
    registry=call['registry'];core.need(call['expected_registry_sha256']==digest(registry),'registry_digest')
    transition.closed(registry,['profile','context','entries'])
    core.need(registry['profile']==REGISTRY,'registry_profile')
    core.need(registry['context']==book['context'],'registry_context')
    entries=registry['entries'];core.need(type(entries) is dict and 0<len(entries)<=MAX_ENTRIES,'registry_entry_limit')
    event=call['event'];transition.closed(event,['id','date','inputs'])
    transition.text(event['id'],'event_id');core.scalar(event['date'],'date')
    core.need(type(event['inputs']) is dict,'event_inputs')
    for name,entry in entries.items():
        transition.text(name,'method_key')
        transition.closed(entry,['method_sha256','method','schemas','account_classes','event_inputs','metadata_bindings','clock'])
        core.need(entry['method_sha256']==digest(entry['method']),'method_digest')
        transition.closed(entry['clock'],['kind']);transition.text(entry['clock']['kind'],'clock_kind')
        if entry['clock']['kind']!='direct_event_date':raise Unsupported('clock_family:'+entry['clock']['kind'])
        declared=event_declarations(entry['method'])
        supplied=entry['event_inputs'];metadata=entry['metadata_bindings']
        core.need(type(supplied) is dict and type(metadata) is dict,'input_declarations')
        core.need(not set(supplied)&set(metadata),'metadata_input_overlap')
        core.need(set(supplied)|set(metadata)==set(declared),'event_input_population')
        for key,typ in supplied.items():
            transition.text(key,'event_input');transition.scalar_type(typ,book)
            core.need(typ==declared[key],'supplied_input_type')
        for key,field in metadata.items():
            transition.text(key,'metadata_input')
            core.need(field in ['id','date'],'metadata_field')
            typ={'kind':'date' if field=='date' else 'text','context':{}}
            core.need(declared[key]==typ,'metadata_type')
        mapping=entry['method']['account_map'];classes=entry['account_classes']
        core.need(type(classes) is dict and set(classes)==set(mapping),'role_class_population')
        for role,account in mapping.items():
            core.need(account in book['accounts'],'unregistered_account')
            core.need(book['accounts'][account]['classification']==classes[role],'role_class_mismatch')
        # Static validation of every entry; prepare evaluates no prerequisites.
        placeholder={'id':event['id'],'date':event['date'],'inputs':{
            k:{'type':deepcopy(t),'value':{'status':'unknown','reason':'static_registry_check'},
               'provenance':'Unknown placeholder for structural validation only'} for k,t in supplied.items()}}
        transition.prepare(book,transition_request(book,entry,placeholder))
    key=call['method_key'];transition.text(key,'selected_method')
    if key not in entries:raise Unsupported('unregistered_method:'+key)
    selected=entries[key]
    core.need(set(event['inputs'])==set(selected['event_inputs']),'supplied_input_population')
    for name,value in event['inputs'].items():
        transition.closed(value,['type','value','provenance'])
        core.need(value['type']==selected['event_inputs'][name],'event_type_mismatch')
    request=transition_request(book,selected,event)
    transition.prepare(book,request)
    return request


def failure(exc):
    return {'profile':PROFILE,**FLAGS,'status':'unsupported' if isinstance(exc,Unsupported) else 'invalid',
            'reason':str(exc)[:300] or type(exc).__name__}


def propose(book,call):
    try:
        request=materialize(book,call);result=transition.propose(book,request)
        return {'profile':PROFILE,**FLAGS,'status':result['status'],'call_sha256':digest(call),
                'before_sha256':digest(book),'registry_sha256':digest(call['registry']),
                'method_key':call['method_key'],'materialized_request':request,'transition':result,
                'implementation_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),
                'transition_sha256':TRANSITION_SHA256}
    except Exception as exc:return failure(exc)


def apply(book,call,proposal):
    try:
        transition.memory.bounded(proposal)
        expected=propose(book,call)
        core.need(core.canonical(expected)==core.canonical(proposal),'proposal_recomputation_mismatch')
        if expected['status']!='proposed':return expected
        result=transition.apply(book,expected['materialized_request'],expected['transition'])
        return {**deepcopy(expected),'status':result['status'],'transition':result}
    except Exception as exc:return failure(exc)
