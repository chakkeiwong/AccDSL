"""Original retained payloads; no inferred state or context conversion."""
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts'))
import module_invocation_v1 as caller
import henkel_lease_measurements_v1 as henkel

def payloads():
    p=json.loads((ROOT/'data/accounting-master/module-composition-audit-20261024/probe-results.json').read_text())
    state=caller.canonical(p['return']['before']).decode();event=caller.canonical(p['return']['request']).decode()
    return {'typed_return':{'state_text':state,'state_raw_sha256':sha256(state.encode()).hexdigest(),
                            'event_text':event,'event_raw_sha256':sha256(event.encode()).hexdigest()},
            'shared_lease':{'state':deepcopy(p['lease']['before']),'event':deepcopy(p['lease']['request'])},
            'sector_report':{'request':deepcopy(p['sector']['request'])},
            'henkel_measurements':{'request':henkel.fixture(),'budget':deepcopy(henkel.BUDGET)}}

def raw_edit(payload,part,edit):
    body=json.loads(payload[part+'_text']);edit(body);text=caller.canonical(body).decode()
    payload[part+'_text']=text;payload[part+'_raw_sha256']=sha256(text.encode()).hexdigest()

def cases():
    rows=[]
    def add(name,key,payload,status,native_status=None,operation=None):
        rows.append({'case':name,'request':caller.request(key,payload,operation),'expected_status':status,'expected_native_status':native_status})
    p=payloads()
    for key,status in [('typed_return','proposed'),('shared_lease','proposed'),('sector_report','conditional_complete'),('henkel_measurements','unresolved')]:
        add(key,key,p[key],'returned',status)
    x=deepcopy(p['shared_lease']);x['state']['collection_complete']='unknown'
    add('lease_missing_membership','shared_lease',x,'returned','unresolved')
    x=deepcopy(p['shared_lease']);x['state']['context']['currency']='EUR'
    add('lease_wrong_context','shared_lease',x,'returned','unsupported')
    x=deepcopy(p['typed_return']);raw_edit(x,'event',lambda e:e.update(all_rights_closed='unknown'))
    add('return_missing_finding','typed_return',x,'returned','unresolved')
    x=deepcopy(p['typed_return']);event_id=json.loads(x['event_text'])['id'];raw_edit(x,'state',lambda s:s['seen'].append(event_id))
    add('return_duplicate','typed_return',x,'returned','invalid')
    x=deepcopy(p['typed_return']);raw_edit(x,'event',lambda e:e.update(all_rights_closed=False))
    add('return_false_finding','typed_return',x,'returned','unsupported')
    x=deepcopy(p['typed_return']);raw_edit(x,'state',lambda s:s['source'].update(packet_sha256='0'*64))
    add('return_source_label_not_admitted','typed_return',x,'returned','proposed')
    x=deepcopy(p['typed_return']);raw_edit(x,'state',lambda s:s['context'].update(entity='X'))
    add('return_owner_label_not_admitted','typed_return',x,'returned','proposed')
    x=deepcopy(p['shared_lease']);x['event']['original_scope_sha256']='0'*64
    add('lease_changed_source_scope','shared_lease',x,'returned','unsupported')
    add('sector_cannot_propose','sector_report',p['sector_report'],'unsupported',operation='propose')
    add('measurements_cannot_propose','henkel_measurements',p['henkel_measurements'],'unsupported',operation='propose')
    add('proposal_cannot_commit','shared_lease',p['shared_lease'],'unsupported',operation='commit')
    x={'request':henkel.fixture(assume=True),'budget':deepcopy(henkel.BUDGET)}
    add('conditional_measurements','henkel_measurements',x,'returned','conditionally_feasible')
    return rows
