"""Two exact source-bound events; amounts and prefix state are recomputed."""
from hashlib import sha256
from pathlib import Path
import importlib.util,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import retained_return_source_binding_v1 as binding
spec=importlib.util.spec_from_file_location('source_bound_cases',HERE.parent/'typed-monetary-effects-20261024/examples.py')
fixtures=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixtures)
core=binding.core


def comparisons():
    raw=(ROOT/binding.PACKET).read_bytes();rows=[]
    for (name,state,event),length in zip(fixtures.selected_cases()[:2],[1,10]):
        s,e=core.canonical(state),core.canonical(event)
        result=binding.bind_and_propose(raw,s,sha256(s).hexdigest(),e,sha256(e).hexdigest())
        after,journal,flows=binding.typed.structure.native.transition(state,event)
        passed=(result['status']=='source_bound_proposal' and len(result['prefix'])==length
                and result['recomputed_before_sha256']==core.digest(state)
                and all(result['result']['proposal'][k]==v for k,v in [('after',after),('journal',journal),('flows',flows)]))
        rows.append({'case':name,'result':result,'passed':passed,'prefix_events':length})
    return rows
