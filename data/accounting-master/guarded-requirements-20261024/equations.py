"""Guarded opening equations under the retained return profile's selected scope."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import importlib.util
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
sys.path.insert(0,str(HERE.parent/'company-return-schema-20261023'))
import method_requirements_v1 as v1
import method_requirements_v3 as v3
import retained_fixture
import return_schema
spec=importlib.util.spec_from_file_location('dimensional_allocation_equations',
    HERE.parent/'dimensional-requirements-20261024/equations.py')
prior=importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)


def ref(key):
    return {'op':'ref','id':key}


def binary(op,a,b):
    return {'op':op,'left':a,'right':b}


def constant(value,t):
    return {'op':'const','type':deepcopy(t),'value':value}


def authored(body):
    # Preserve the broad source record but select opening equations only.
    # The prior constructor needs settlement event fields; use a copy of the
    # retained event purely to author types, then bind all source refs below.
    baseline,_=retained_fixture.fixture()
    seed=deepcopy(body)
    seed['events']=baseline['events']
    definition,values=prior.authored(seed)
    definition['requirements']=definition['requirements'][:4]
    used={key for req in definition['requirements'] for key in req['requires']}
    definition['inputs']={k:v for k,v in definition['inputs'].items() if k in used}
    values={k:v for k,v in values.items() if k in used}
    h=sha256(v1.canonical(body)).hexdigest()
    for declaration in definition['inputs'].values():
        declaration['source_ref']='sha256:'+h+'#'+declaration['source_ref'].split('#',1)[1]
    amount_type=definition['inputs']['refund']['type']
    additions={'settled':('/component/settled',deepcopy(v1.BOOL),'state'),
               'refund_base':('/tax/refund_tax_base',deepcopy(amount_type),'state'),
               'recovery_base':('/tax/recovery_tax_base',deepcopy(amount_type),'state')}
    for key,(pointer,t,role) in additions.items():
        value=body
        for token in pointer[1:].split('/'):
            value=value[token]
        definition['inputs'][key]={'type':t,'role':role,'source_ref':'sha256:'+h+'#'+pointer}
        values[key]=({'status':'unknown','reason':'retained_explicit_unknown'} if value=='unknown' else
                     {'status':'known','value':value})
    unsettled={'op':'not','arg':ref('settled')}
    for req in definition['requirements']:
        if req['id'] in ['refund_allocation','recovery_allocation']:
            req.update(guard=deepcopy(unsettled),guard_requires=['settled'])
        else:
            base='refund_base' if req['id']=='opening_dta' else 'recovery_base'
            req.update(guard=binary('eq',ref(base),constant('0/1',amount_type)),guard_requires=[base])
    def add(key,guard,gdeps,predicate,deps,consequence='invalid'):
        definition['requirements'].append({'id':key,'guard':guard,'guard_requires':gdeps,
            'predicate':predicate,'requires':deps,'admission_refs':[],
            'on_false':consequence,'on_unknown':'unresolved'})
    for key in ['refund','recovery']:
        add('settled.'+key,ref('settled'),['settled'],
            binary('eq',ref(key),constant('0/1',amount_type)),[key])
    for key in ['refund_base','recovery_base']:
        add('scope.'+key,constant(True,v1.BOOL),[],
            binary('eq',ref(key),constant('0/1',amount_type)),[key],'unsupported')
    definition.update(profile=v3.PROFILE,method_id='retained.return.guarded_opening',version='3',
        required_known=sorted(definition['inputs']),
        residual_prerequisites=[
            'Nonnegative recovery estimate and all other scalar/domain conditions remain separately required.',
            'Lot/event order, caller findings, state allocation, source authority and execution are not assessed.',
            'Context and dimension assignments remain explicit caller declarations for this synthetic method.'])
    return definition,values


def settled_body(body):
    body=deepcopy(body)
    body['component'].update(settled=True,refund='0/1',recovery='0/1')
    body['tax'].update(opening_dta='0/1',opening_dtl='0/1')
    body['lots']=[{'id':'recovered','component_id':body['component']['id'],'units':'2/1',
                  'carrying':'20/1','tax_base':'20/1','acquired':'2024-12-31'}]
    body['events']=body['events'][1:]
    return body


def comparisons():
    base,raw=retained_fixture.fixture()
    settled=settled_body(base)
    cases=[('unsettled',base,[],'requirements_satisfied'),
           ('settled',settled,[],'requirements_satisfied'),
           ('unknown_settlement',base,[(('component','settled'),'unknown')],'unresolved'),
           ('wrong_refund',base,[(('component','refund'),'41/1')],'invalid'),
           ('unknown_refund',base,[(('component','refund'),'unknown')],'unresolved'),
           ('wrong_recovery',base,[(('component','recovery'),'17/1')],'invalid'),
           ('wrong_dta',base,[(('tax','opening_dta'),'11/1')],'invalid'),
           ('nonzero_refund_base',base,[(('tax','refund_tax_base'),'1/1')],'unsupported'),
           ('unknown_refund_base',base,[(('tax','refund_tax_base'),'unknown')],'unresolved'),
           ('settled_refund_remains',settled,[(('component','refund'),'1/1')],'invalid'),
           ('settled_recovery_remains',settled,[(('component','recovery'),'1/1')],'invalid'),
           ('inactive_unknown_estimate_required',settled,[(('component','expected_units'),'unknown')],'unresolved'),
           ('unknown_and_known_contradiction',base,[(('tax','rate'),'unknown'),(('component','refund'),'41/1')],'invalid'),
           ('unknown_and_unsupported',base,[(('tax','rate'),'unknown'),(('tax','refund_tax_base'),'1/1')],'unsupported')]
    rows=[]
    for name,body,edits,expected in cases:
        body=deepcopy(body)
        for path,value in edits:
            body[path[0]][path[1]]=value
        definition,values=authored(body)
        key=v1.digest(definition)
        result=v3.assess({key:definition},key,values,definition['capabilities'])
        old=return_schema.assess(body)
        mapped='requirements_satisfied' if old['status']=='statically_eligible' else old['status']
        rows.append({'case':name,'expected':expected,'legacy_status':old['status'],
                     'passed':expected==mapped==result['status'],
                     'manifest':definition,'values':values,'result':result})
    return rows,sha256(raw).hexdigest()
