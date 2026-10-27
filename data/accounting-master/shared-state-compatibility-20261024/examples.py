from pathlib import Path
from copy import deepcopy
import json,sys
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'scripts'))
import shared_state_compatibility_v1 as m

def originals():
    rows=json.loads((ROOT/'data/accounting-master/module-invocation-20261024/cases.json').read_text())
    return {x['case']:x for x in rows if x['case'] in ['typed_return','shared_lease']}

def states():
    x=originals()
    return {'typed_return':json.loads(x['typed_return']['request']['payload']['state_text']),
            'shared_lease':x['shared_lease']['request']['payload']['state']}

def cases():
    s=states();out=[]
    def add(name,a,b,left,right,status):
        out.append({'case':name,'request':m.request(a,left,b,right),'expected_status':status})
    for a in s:
        add(a+'_same_state',a,a,s[a],s[a],'compatible')
    add('return_lease','typed_return','shared_lease',s['typed_return'],s['shared_lease'],'incompatible')
    add('lease_return','shared_lease','typed_return',s['shared_lease'],s['typed_return'],'incompatible')
    x=deepcopy(s['typed_return']);x['context']['entity']='unknown'
    add('unknown_owner','typed_return','typed_return',x,x,'unresolved')
    x=deepcopy(s['shared_lease']);x['original_scope_sha256']='0'*64
    add('changed_lease_source','shared_lease','shared_lease',x,x,'incompatible')
    x=deepcopy(s['shared_lease']);x['collection_complete']='unknown'
    add('unknown_membership','shared_lease','shared_lease',x,x,'unresolved')
    x=originals()['typed_return']['result']['native_result']['proposal']['after']
    add('different_valid_snapshots','typed_return','typed_return',s['typed_return'],x,'incompatible')
    x=deepcopy(s['typed_return']);x['balances']['cash']='0/1'
    add('same_invalid_state','typed_return','typed_return',x,x,'incompatible')
    x=deepcopy(s['shared_lease']);x['context']['entity_id']='P';x['context']['book_id']='legal';x['period']=deepcopy(s['typed_return']['period']);x['date']=s['typed_return']['date']
    add('renaming_does_not_compose','typed_return','shared_lease',s['typed_return'],x,'incompatible')
    row=deepcopy(out[0]);row['case']='stale_digest';row['request']['left']['state']['date']='2025-01-02';row['expected_status']='invalid';out.append(row)
    return out
