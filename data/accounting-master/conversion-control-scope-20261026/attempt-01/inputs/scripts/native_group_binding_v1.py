"""Select two legal-book views of a retained native group, without posting."""
from copy import deepcopy
from datetime import timedelta
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import json
import re
from jsonschema import Draft202012Validator, FormatChecker
import company_world_envelope_v1 as world

ROOT=Path(__file__).resolve().parents[1];core=world.core
PROFILE='NativeGroupReferenceBinding/1';SELECTOR='NativeGroupBookSelection/1'
FOLDER=ROOT/'data/accounting-master/company-composition-20261016/attempt-03'
PINS={'portable-exchanges.json':'690265c8b88b620ebb5de0e9aa3544428f6895e41343b6098f13ae1a72b76612',
      'record-schemas.json':'cc9be9b672bbf07d37e7cc11b64df4b90a2b238ec0abbd20a1e1413815da4fe2'}
WORLD_SHA256='a048be2290e1d6631e40887f625d387608191c400e96b0bb5300f6c52fb73b2a'
FLAGS={**world.FLAGS,'selected_references_resolved':False,'group_recomputed':False}

def load_native():
    values=[]
    for name,h in PINS.items():
        path=FOLDER/name;core.need(path.stat().st_size<=32_000_000,'native_file_size')
        raw=path.read_bytes();core.need(sha256(raw).hexdigest()==h,'native_bytes:'+name)
        values.append(json.loads(raw))
    return tuple(values)

def references(value,blob=False):
    if type(value) is dict:
        fields={'path','sha256','byte_length'} if blob else {'kind','schema','digest'}
        if set(value)==fields:yield value
        else:
            for child in value.values():yield from references(child,blob)
    elif type(value) is list:
        for child in value:yield from references(child,blob)

def numbers(value):
    if type(value) is str and re.fullmatch(r'-?(0|[1-9][0-9]*)(/[1-9][0-9]*)?',value):
        core.need(str(Fraction(value))==value,'native_noncanonical_rational')
    elif type(value) is dict:
        for child in value.values():numbers(child)
    elif type(value) is list:
        for child in value:numbers(child)

def checked_blob(ref,index):
    core.closed(ref,['path','sha256','byte_length'],'native_blob')
    world.digest(ref['sha256'],'blob_digest');world.text(ref['path'],'blob_path')
    core.need(type(ref['byte_length']) is int and 0<=ref['byte_length']<=128_000_000,'blob_size')
    core.need(ref['sha256'] in index and index[ref['sha256']]==ref,'native_blob_index')
    path=(ROOT/ref['path']).resolve();core.need(path.is_relative_to(ROOT),'blob_outside_workspace')
    core.need(path.stat().st_size==ref['byte_length'],'blob_length')
    h=sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
    core.need(h.hexdigest()==ref['sha256'],'blob_digest')
    return deepcopy(ref)

def resolve(packet,schemas,roots):
    found={};active=set();blobs={}
    def visit(ref,depth=0):
        core.closed(ref,['kind','schema','digest'],'native_reference')
        h=ref['digest'];core.need(h in packet['record_registry'],'missing_native_record')
        record=packet['record_registry'][h]
        core.need((ref['kind'],ref['schema'])==(record['kind'],record['schema']),'native_reference_type')
        core.need(h not in active,'native_reference_cycle')
        if h in found:return
        core.need(depth<=48 and len(found)+len(active)<4096,'native_closure_limit')
        core.closed(record,['kind','schema','key','body','dependencies'],'native_record')
        world.text(record['key'],'native_key')
        core.need(record['kind'] in schemas['schema_ids'] and schemas['schema_ids'][record['kind']]==record['schema'],'native_schema')
        identity=('accdsl.portable.v1/'+record['schema']).encode()+bytes([0])+core.canonical(record)
        core.need(sha256(identity).hexdigest()==h,'native_record_digest')
        errors=Draft202012Validator(schemas['$defs'][record['kind']],format_checker=FormatChecker()).iter_errors(record['body'])
        core.need(next(errors,None) is None,'native_body_schema');numbers(record['body'])
        deps={core.canonical(r):r for r in references(record['body'])}
        core.need(record['dependencies']==[deps[k] for k in sorted(deps)],'native_dependencies')
        active.add(h)
        for child in record['dependencies']:visit(child,depth+1)
        for blob in references(record['body'],blob=True):
            if blob['sha256'] not in blobs:blobs[blob['sha256']]=checked_blob(blob,packet['blobs'])
            else:core.need(blobs[blob['sha256']]==blob,'native_blob_conflict')
        active.remove(h);found[h]=deepcopy(record)
    for ref in roots:visit(ref)
    return {k:found[k] for k in sorted(found)},{k:blobs[k] for k in sorted(blobs)}

def selector(state_ref,member):
    core.need(member in ['P','S'],'native_member')
    return {'profile':SELECTOR,'state_ref':deepcopy(state_ref),'member':member,'pointer':'/books/'+member}

def bind(request):
    try:
        core.need(sha256(Path(world.__file__).read_bytes()).hexdigest()==WORLD_SHA256,'world_dependency_hash')
        world.bounded(request)
        core.closed(request,['profile','world','snapshot','members','control_edge_id'],'group_binding')
        core.need(request['profile']==PROFILE,'binding_profile');world.validate(request['world'])
        core.need(request['snapshot'] in ['initial','final'],'native_snapshot')
        core.closed(request['members'],['P','S'],'member_population')
        core.need(all(type(v) is str for v in request['members'].values()),'member_component_id')
        core.need(len(set(request['members'].values()))==2,'duplicate_member_component')
        packet,schemas=load_native();snapshot=packet[request['snapshot']+'_world']
        roots=list(references(snapshot))+[packet['aliases']['profile'],packet['aliases']['source']]
        records,blobs=resolve(packet,schemas,roots)
        def body(ref):return records[ref['digest']]['body']
        state=body(snapshot['head']);view=body(snapshot['view']);profile=body(packet['aliases']['profile'])
        source=packet['aliases']['source']
        core.need(profile['name']=='CompanyComposition/1' and profile['execution']=='documentary_only','native_profile_scope')
        core.need(profile['source']==source and view['profile']==packet['aliases']['profile'],'native_profile_source_view')
        core.need(view['information_mode']=='archival_synthetic','native_view_scope')
        core.need(body(source)['status']=='historical_conditional_not_current_admission','native_source_scope')
        core.need(state['entities']==['P','S'] and set(state['books'])=={'P','S'},'native_entity_population')
        selections={};books=request['world']['books'];components=request['world']['components']
        for member,cid in request['members'].items():
            core.need(cid in components,'missing_component');component=components[cid];book=books[component['owner']]
            core.need(component['sector']=='corporate' and component['profile']==profile['name'],'native_component_profile')
            core.need(book['entity']==member and book['book']==member,'native_member_owner')
            core.need(book['currency']==state['currency'],'native_currency_binding')
            selection=selector(snapshot['head'],member)
            core.need(book['state_ref']==core.digest(selection),'native_member_selector_binding')
            core.need(book['source_ref']==source['digest'] and book['view_ref']==snapshot['view']['digest'],'native_source_view_binding')
            selections[member]={'component_id':cid,'selector':selection,'selector_sha256':core.digest(selection),
                'balances':deepcopy(state['books'][member]),'scope':'Selected balances only; shared group state remains required'}
        edges=[e for e in request['world']['control_edges'] if e['id']==request['control_edge_id']]
        core.need(len(edges)==1,'native_control_edge');edge=edges[0]
        core.need(edge['parent']==state['parent'] and edge['child']==state['subsidiary'],'native_control_parties')
        core.need(Fraction(edge['ownership_fraction'])==Fraction(state['parent_fraction']),'native_ownership_fraction')
        next_day=(core.scalar(state['date'],'date')+timedelta(days=1)).isoformat()
        core.need(edge['start']==state['date'] and edge['end_exclusive']==next_day,'native_snapshot_interval')
        core.need(state['control_start']<=edge['start']<edge['end_exclusive']<=state['control_end_exclusive'],'native_control_interval')
        core.need(edge['control_premise']=='Supplied native control premise:'+snapshot['head']['digest'],'native_control_premise')
        return {'profile':PROFILE,**FLAGS,'selected_references_resolved':True,'status':'group_references_resolved',
            'request_sha256':core.digest(request),'world':deepcopy(request['world']),'native_snapshot':deepcopy(snapshot),
            'native_state':deepcopy(state),'member_selections':selections,'records':records,'blobs':blobs,
            'source_scope':body(source)['status'],'unresolved_obligations':deepcopy(request['world']['obligations']),
            'native_pins':deepcopy(PINS),'implementation_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),
            'scope':'Two read-only book selectors within one retained group; no independent CompanyBook, consolidation recomputation, control assessment or posting'}
    except Exception as exc:return {'profile':PROFILE,**FLAGS,'status':'invalid','reason':str(exc)[:350]}

def verify(request,result):
    try:return core.canonical(bind(request))==core.canonical(result)
    except Exception:return False
