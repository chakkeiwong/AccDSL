"""Recompute native complete outputs and preserve proposal binding evidence."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import importlib.util,sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import typed_return_transition_v1 as transition
spec=importlib.util.spec_from_file_location('composition_native_cases',HERE.parent/'typed-monetary-effects-20261024/examples.py')
fixtures=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixtures)
core=transition.core


def comparisons():
    rows=[]
    for name,state,event in fixtures.selected_cases():
        old=deepcopy((state,event));s,e=core.canonical(state),core.canonical(event)
        args=(s,sha256(s).hexdigest(),e,sha256(e).hexdigest())
        result=transition.propose(*args)
        applied=None
        try:
            after,journal,flows=transition.structure.native.transition(state,event)
            native={'status':'proposed','after':after,'journal':journal,'flows':flows}
            passed=result['status']=='proposed' and all(result['proposal'][k]==native[k] for k in ['after','journal','flows'])
            if passed:
                applied=transition.apply(*args,result['proposal'])
                passed=applied['status']=='applied_diagnostic' and applied['after']==after
        except transition.structure.native.Rejected as exc:
            native={'status':exc.status,'reason':exc.reason};passed=result['status']==exc.status
        rows.append({'case':name,'state_raw_sha256':args[1],'event_raw_sha256':args[3],
                     'result':result,'native':native,'applied':applied,'passed':passed and (state,event)==old})
    return rows
