"""One-time explicit authoring of four complete parameterized method records."""
from copy import deepcopy
from pathlib import Path
from hashlib import sha256
import json
import constructor as c
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
AUDIT=HERE.parent/'event-specialization-audit-20261026'
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def slot(n):return {'__authoring_parameter__':n}
def encode(v):
    if type(v) is dict and set(v)=={'__authoring_parameter__'}:return {'node':'parameter','name':v['__authoring_parameter__']}
    if type(v) is dict:return {'node':'object','fields':{k:encode(x) for k,x in v.items()}}
    if type(v) is list:return {'node':'array','items':[encode(x) for x in v]}
    return {'node':'literal','value':v}
def main():
    out=HERE/'templates';assert not out.exists();out.mkdir()
    rows=json.loads((AUDIT/'request-comparisons.json').read_text())
    lock=json.loads((AUDIT/'source-lock.json').read_text())
    for p in [AUDIT/'audit.py',AUDIT/'result.md',AUDIT/'checks.json',AUDIT/'request-comparisons.json',AUDIT/'operation-map.json']:
        lock[str(p.relative_to(ROOT))]=sha(p)
    dump(HERE/'source-lock.json',lock)
    mappings=[]
    for owner in ('alpha','beta'):
        for kind in ('sale','collect'):
            row=next(x for x in rows if x['company']==owner and x['method']==kind)
            request=row['request'];method=deepcopy(request['method'])
            params=[]
            def parameter(n,t,source):params.append({'name':n,'type':t,'source':source})
            parameter('state_schema',c.TEXT,{'kind':'book_metadata','field':'memory_schema'})
            parameter('input_schema',c.TEXT,{'kind':'input_schema'})
            parameter('claim_id',c.TEXT,{'kind':'event_input','name':'claim_id'})
            method['memory']['definition']['state_schema']=slot('state_schema')
            method['memory']['definition']['input_schema']=slot('input_schema')
            op=method['memory']['definition']['operations'][0];op['path'][1]=slot('claim_id')
            if kind=='sale':
                for name,typ in [('customer',c.TEXT),('due',c.DATE)]:parameter(name,typ,{'kind':'event_input','name':name})
                parameter('event_id',c.TEXT,{'kind':'event_metadata','field':'id'})
                parameter('event_date',c.DATE,{'kind':'event_metadata','field':'date'})
                fields=op['value']['fields']
                for field,name in [('customer','customer'),('due','due'),('issued','event_date'),('sale_event','event_id'),('assessment_date','event_date')]:
                    fields[field]['value']=slot(name)
            else:
                parameter('claim_pointer',c.TEXT,{'kind':'pointer','segments':[{'literal':'claims'},{'parameter':'claim_id'},{'literal':'remaining'}]})
                for part in ('preconditions','monetary'):method[part]['bindings']['claim_remaining']['pointer']=slot('claim_pointer')
            input_types=c.frontend.v2.input_types(row['before'],request['method'])
            definition={'profile':c.types.PROFILE,'root':{'node':'record','fields':{c.base.binding.pointer_parts(pointer)[0]:{'node':'scalar','type':typ} for pointer,typ in input_types.items()}}}
            template={'profile':c.PROFILE,'transition_profile':request['profile'],'context':deepcopy(row['before']['context']),
                'parameters':params,'method_template':encode(method),'input_schema_definition':definition,
                'residuals':['Fixed chart, roles and unit-cost pointer; full native eligibility remains separately selected.',
                             'No source/accounting admission; no assessment iteration; literal financial algorithms remain explicit.']}
            file=out/(owner+'.'+kind+'.json');dump(file,template)
            mappings.append({'company':owner,'kind':kind,'source_request_index':row['index'],'file':str(file.relative_to(HERE)),
                             'sha256':sha(file),'parameters':[x['name'] for x in params],'native_specializer_called':False})
    dump(HERE/'template-provenance.json',mappings)
    print(json.dumps({'templates':len(mappings),'protected_files':len(lock)}))
if __name__=='__main__':main()
