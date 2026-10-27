from pathlib import Path
from copy import deepcopy
from functools import lru_cache
import importlib.util,sys
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'scripts'))
import annual_program_authoring_v1 as m
s=importlib.util.spec_from_file_location('authoring_annual_examples',ROOT/'data/accounting-master/reusable-annual-interface-20261025/examples.py')
previous=importlib.util.module_from_spec(s);s.loader.exec_module(previous)

@lru_cache(maxsize=1)
def base_request():return previous.repeated_scenario()

def fixtures():
    base=deepcopy(base_request());root=base['root_request'];rows=[]
    def add(name,q,status='complete_provisional',stop=None):
        p=m.from_request(q,name);rows.append({'case':name,'program':p,'request':q,
            'imports':{q['root_sha256']:deepcopy(q['root_request'])},'source':m.render(p),
            'expected_status':status,'expected_stop':stop})
    add('repeated_periods',base)
    add('empty',m.annual.request(root,[]))
    op=previous.previous.depreciation(identity='authored-native',day='2027-01-03')
    add('native_only',m.annual.request(root,[op]))
    q=deepcopy(base);q['operations'][0]['event']['information']['rate']={'status':'unknown','reason':'Explicitly unavailable'}
    add('unknown_rate',q,'stopped_provisional','unresolved')
    q=deepcopy(base);q['operations'][1]['event']['authorization']=previous.known(False)
    add('false_authority',q,'stopped_provisional','unsupported')
    q=deepcopy(base);q['operations'][1]['event']['allocations'][0]['amount']='100/1'
    add('overallocated_payment',q,'stopped_provisional','invalid')
    origin,state=previous.start(root);first=previous.assessment(state,'2000/1');state=m.annual.transition(state,first)['after']
    add('cash_shortage',m.annual.request(origin,[first,previous.payment(state,['0/1','0/1','400/1'])]),'stopped_provisional','funding_failure')
    q=deepcopy(base);q['operations'][4]['event']['recovery_capacity']={'status':'unknown','reason':'No fresh capacity'}
    add('unknown_capacity',q,'stopped_provisional','unresolved')
    q=deepcopy(base);q['operations'][4]['event']['measurement']['state_sha256']='0'*64
    add('stale_measurement',q,'stopped_provisional','invalid')
    q=deepcopy(base);q['operations'][5]['event']['findings']={k:previous.known(False) for k in m.annual.root.boundary.FINDINGS}
    add('false_carry_findings_preserved',q)
    return rows
