"""Finite typed pure expressions; no host eval, I/O, mutation or temporal admission."""
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
import json
import re
from jsonschema import Draft202012Validator

PROFILE='CompanyExpressionsDraft/1'
RAT=r'^(unknown|(?:0|-?[1-9][0-9]*)/[1-9][0-9]*)$'
BOOL={'kind':'boolean'}
SCALAR={'kind':'number','dimensions':{},'context':None}
FLAGS={'temporal_admission':False,'historical_execution_established':False,'forecast_admission':False,'real_behavior_evidence':False}
ARITY={'neg':1,'not':1,'add':2,'sub':2,'mul':2,'div':2,'lt':2,'le':2,'eq':2,'and':2,'or':2,'if':3}
def canonical(x): return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def digest(x): return sha256(canonical(x)).hexdigest()
def closed(p): return {'type':'object','properties':p,'required':list(p),'additionalProperties':False}
def schema():
    name={'type':'string','pattern':r'^[A-Za-z][A-Za-z0-9_]*$'}
    number=closed({'kind':{'const':'number'},'dimensions':{'type':'object','propertyNames':name,'additionalProperties':{'type':'integer','not':{'const':0}}},'context':{'type':['string','null'],'minLength':1}})
    typ={'oneOf':[number,closed({'kind':{'const':'boolean'}})]}
    value={'oneOf':[{'type':'string','pattern':RAT},{'type':'boolean'}]}
    variants=[closed({'id':name,'op':{'const':'literal'},'type':typ,'value':value}),
              closed({'id':name,'op':{'const':'input'},'target':name})]
    for op,arity in ARITY.items():
        variants.append(closed({'id':name,'op':{'const':op},'args':{'type':'array','minItems':arity,'maxItems':arity,'items':name}}))
    return dict(closed({'profile':{'const':PROFILE},'name':{'type':'string','minLength':1},
                       'inputs':{'type':'object','propertyNames':name,'additionalProperties':closed({'type':typ,'value':value})},
                       'nodes':{'type':'array','minItems':1,'items':{'oneOf':variants}},
                       'outputs':{'type':'object','minProperties':1,'propertyNames':name,'additionalProperties':name}}),
                **{'$schema':'https://json-schema.org/draft/2020-12/schema'})
def q(value):
    if not isinstance(value,str) or not re.fullmatch(RAT,value) or value=='unknown': raise ValueError('exact rational required')
    number=Fraction(value)
    if value!=str(number.numerator)+'/'+str(number.denominator): raise ValueError('noncanonical rational')
    return number
def wire(value): return str(value.numerator)+'/'+str(value.denominator)
def typed_value(typ,value):
    if typ['kind']=='number':
        if any(type(e) is not int or e==0 for e in typ['dimensions'].values()): raise ValueError('dimension exponent must be nonzero integer')
        if value!='unknown': q(value)
    elif value!='unknown' and type(value) is not bool: raise ValueError('Boolean value required')
def compatible(a,b):
    if digest(a)!=digest(b): raise ValueError('incompatible types or contexts')
    return deepcopy(a)
def combine(a,b,sign):
    if a['kind']!='number' or b['kind']!='number': raise ValueError('numeric operands required')
    if a['context']==b['context']: context=a['context']
    elif a['context'] is None and not a['dimensions']: context=b['context']
    elif b['context'] is None and not b['dimensions']: context=a['context']
    else: raise ValueError('incompatible multiplication contexts')
    dims=deepcopy(a['dimensions'])
    for k,v in b['dimensions'].items(): dims[k]=dims.get(k,0)+sign*v
    return {'kind':'number','dimensions':{k:v for k,v in dims.items() if v},'context':context}

def analyze(body):
    Draft202012Validator(schema()).validate(body)
    for item in body['inputs'].values(): typed_value(item['type'],item['value'])
    nodes={n['id']:n for n in body['nodes']}
    if len(nodes)!=len(body['nodes']): raise ValueError('duplicate node identity')
    types={}; dependencies={}; visiting=set()
    def visit(ident):
        if ident in types: return types[ident]
        if ident in visiting: raise ValueError('cyclic expression dependency')
        if ident not in nodes: raise ValueError('missing node reference: '+ident)
        visiting.add(ident); node=nodes[ident]; op=node['op']; deps=set()
        if op=='literal':
            typed_value(node['type'],node['value']); typ=deepcopy(node['type'])
        elif op=='input':
            if node['target'] not in body['inputs']: raise ValueError('missing input: '+node['target'])
            typ=deepcopy(body['inputs'][node['target']]['type']); deps={node['target']}
        else:
            args=[visit(x) for x in node['args']]
            for x in node['args']: deps.update(dependencies[x])
            if op in ['neg','add','sub','lt','le']:
                if any(t['kind']!='number' for t in args): raise ValueError('numeric operands required')
                if len(args)==2: compatible(args[0],args[1])
                typ=deepcopy(BOOL if op in ['lt','le'] else args[0])
            elif op=='eq': compatible(args[0],args[1]); typ=deepcopy(BOOL)
            elif op in ['mul','div']: typ=combine(args[0],args[1],1 if op=='mul' else -1)
            elif op in ['not','and','or']:
                if any(t!=BOOL for t in args): raise ValueError('Boolean operands required')
                typ=deepcopy(BOOL)
            elif op=='if':
                if args[0]!=BOOL: raise ValueError('Boolean guard required')
                typ=compatible(args[1],args[2])
            else: raise ValueError('unsupported operation')
        visiting.remove(ident); types[ident]=typ; dependencies[ident]=sorted(deps)
        return typ
    for ident in nodes: visit(ident)
    for ident in body['outputs'].values(): visit(ident)
    return {'types':types,'dependencies':dependencies,'outputs':{k:deepcopy(types[v]) for k,v in body['outputs'].items()}}

def evaluate(body):
    try: analysis=analyze(body)
    except Exception as exc: return dict(FLAGS,status='invalid',reason='expression_static',detail=type(exc).__name__+':'+str(exc).splitlines()[0][:250])
    nodes={n['id']:n for n in body['nodes']}; cache={}
    def result(ident,status,**extra):
        return dict(type=deepcopy(analysis['types'][ident]),status=status,
                    declared_dependencies=analysis['dependencies'][ident],**extra)
    def visit(ident):
        if ident in cache: return cache[ident]
        node=nodes[ident]; op=node['op']; used=set()
        if op in ['literal','input']:
            item=node if op=='literal' else body['inputs'][node['target']]
            if op=='input': used.add(node['target'])
            r=result(ident,'unresolved',reason='unknown_value') if item['value']=='unknown' else result(ident,'known',value=item['value'])
        elif op=='if':
            guard=visit(node['args'][0]); used.update(guard['evaluated_inputs'])
            if guard['status']!='known': r=result(ident,guard['status'],reason='guard_'+guard['status'])
            else:
                chosen=visit(node['args'][1 if guard['value'] is True else 2]); used.update(chosen['evaluated_inputs'])
                r=result(ident,chosen['status'],**({'value':chosen['value']} if chosen['status']=='known' else {'reason':chosen.get('reason','selected_branch')}))
        else:
            args=[visit(x) for x in node['args']]
            for a in args: used.update(a['evaluated_inputs'])
            if any(a['status']=='invalid' for a in args): r=result(ident,'invalid',reason='operand_invalid')
            elif op=='div' and args[1]['status']=='known' and q(args[1]['value'])==0:
                r=result(ident,'invalid',reason='division_by_zero')
            elif any(a['status']!='known' for a in args): r=result(ident,'unresolved',reason='operand_unknown')
            else:
                vals=[a['value'] if a['type']['kind']=='boolean' else q(a['value']) for a in args]
                if op=='neg': v=-vals[0]
                elif op=='not': v=not vals[0]
                elif op=='add': v=vals[0]+vals[1]
                elif op=='sub': v=vals[0]-vals[1]
                elif op=='mul': v=vals[0]*vals[1]
                elif op=='div': v=vals[0]/vals[1]
                elif op=='lt': v=vals[0]<vals[1]
                elif op=='le': v=vals[0]<=vals[1]
                elif op=='eq': v=vals[0]==vals[1]
                elif op=='and': v=vals[0] and vals[1]
                elif op=='or': v=vals[0] or vals[1]
                r=result(ident,'known',value=v if type(v) is bool else wire(v))
        r['evaluated_inputs']=sorted(used); cache[ident]=r; return r
    outputs={k:visit(v) for k,v in body['outputs'].items()}
    statuses={v['status'] for v in outputs.values()}
    status='invalid' if 'invalid' in statuses else 'unresolved' if 'unresolved' in statuses else 'evaluated'
    return dict(FLAGS,status=status,program_sha256=digest(body),outputs=outputs,analysis=analysis)
