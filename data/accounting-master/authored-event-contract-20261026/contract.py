"""Explicitly selected retained lifecycle contract; no generic callback dispatch."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE.parent/'authored-state-invariants-20261026'))
import guarded_runner as prior
import declared_receivable_lifecycle_v1 as native
core=prior.core;base=prior.base;digest=core.digest
PROFILE='SelectedReceivableEventContract/1'
class ContractFailure(ValueError):
    def __init__(self,status,reason,evidence=None):
        self.status=status;self.evidence=evidence or {};super().__init__(reason)
def native_body(body,commands=None):
    selected=body['event_contract']
    if commands is None:
        commands=[]
        for command in body['commands']:
            c=deepcopy(command)
            if c['kind']=='event':
                c.pop('registry_sha256');c['event']=deepcopy(selected['intents'][c['event']['id']])
            elif c['kind']=='carry':c.pop('memory_policies')
            commands.append(c)
    return {'profile':native.PROFILE,'name':body['name'],'opening':deepcopy(body['opening']),
        'schemas':deepcopy(body['schemas']),'mapping':deepcopy(body['mapping']),
        'memory_definition':deepcopy(body['memory_definition']),'roles':deepcopy(selected['roles']),
        'unit_cost_pointer':selected['unit_cost_pointer'],'policy':deepcopy(selected['policy']),'commands':commands}
def validate(body):
    selected=body['event_contract']
    base.closed(selected,['profile','native_sha256','roles','unit_cost_pointer','policy','intents'])
    core.need(selected['profile']==PROFILE,'event_contract_profile')
    core.need(selected['native_sha256']==sha256(Path(native.__file__).read_bytes()).hexdigest(),'native_contract_hash')
    core.need(body['expected_event_contract_sha256']==digest(selected),'event_contract_hash')
    core.need(type(selected['intents']) is dict,'intent_population')
    ids={c['event']['id'] for c in body['commands'] if c['kind']=='event'}
    core.need(set(selected['intents'])==ids,'exact_intent_population')
    for key,event in selected['intents'].items():
        base.closed(event,['id','date','inputs']);core.need(event['id']==key,'intent_identity')
    native.validate(native_body(body))
def control(body,book):native.control(book,body['event_contract']['roles'])
def before(body,book,command):
    control(body,book)
    if command['kind']=='report':return None
    if command['kind']=='carry':
        expected={p:{'kind':'preserve','provenance':body['event_contract']['policy']['provenance']} for p in book['memory_types']}
        core.need(command['memory_policies']==expected,'selected_carry_policy')
        return {'scope':'selected_native_carry_policy','book_sha256':digest(book)}
    event=body['event_contract']['intents'][command['event']['id']];kind=command['method_key']
    declared=native.event_types(book,kind);base.closed(event,['id','date','inputs'])
    core.need(book['date']<=core.scalar(event['date'],'date').isoformat()<book['period']['end_exclusive'],'event_chronology')
    core.need(type(event['inputs']) is dict and set(event['inputs'])==set(declared),'exact_event_inputs')
    unknown=[]
    for name,record in event['inputs'].items():
        base.closed(record,['type','value','provenance']);core.need(record['type']==declared[name],'event_type:'+name)
        base.text(record['provenance'],'event_provenance')
        core.validate_values({'inputs':{name:{'type':base.dimensions.encoded(declared[name])}}},{name:record['value']})
        if record['value']['status']=='unknown':unknown.append(name)
    if unknown:raise ContractFailure('unresolved','unknown_event_inputs',{'inputs':unknown})
    if event['inputs']['approved']['value']['value'] is not True:raise ContractFailure('unsupported','applicability_not_selected')
    intended=native.make_request(book,native_body(body),{'kind':'event','method_key':kind,'event':deepcopy(event)})
    projected=deepcopy(intended);declared=prior.methods.prior.event_declarations(projected['method'])
    removed={k:deepcopy(v) for k,v in projected['event']['inputs'].items() if k not in declared}
    projected['event']['inputs']={k:v for k,v in projected['event']['inputs'].items() if k in declared}
    registry=body['registries'][command['registry_sha256']];entry=registry['entries'].get(kind)
    core.need(entry is not None,'unregistered_method')
    selected_profile=entry['transition_profile']
    if selected_profile==base.PROFILE:
        core.need(kind=='collect','scalar_transition_contract');projected['profile']=base.PROFILE;projected.pop('memory_definition')
    else:core.need(selected_profile==prior.typed.PROFILE,'selected_transition_contract')
    call={'profile':prior.methods.PROFILE,'expected_state_sha256':digest(book),'expected_registry_sha256':command['registry_sha256'],
        'registry':registry,'method_key':kind,'event':command['event']}
    authored=prior.methods.materialize(book,call)
    core.need(core.canonical(authored)==core.canonical(projected),'selected_method_intent_mismatch')
    return {'profile':PROFILE,'native_request':intended,'derived_request_sha256':digest(projected),
        'full_intent_sha256':digest(event),'removed_event_inputs':removed,'native_source_sha256':body['event_contract']['native_sha256'],
        'scope':'Explicit selected native specialization contract, not a general method evaluator'}
