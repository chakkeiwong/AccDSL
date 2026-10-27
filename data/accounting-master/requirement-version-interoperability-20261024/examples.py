"""Independent authored examples, with explicit derived-record provenance."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts'))
import method_requirements_v1 as core
import method_requirement_versions as versions
import method_requirement_text_v2 as text
import method_input_binding_v2 as binder


def known(value):
    return {'status':'known','value':value}


def fixture(version):
    ref=lambda key:{'op':'ref','id':key}
    money={'kind':'rational','context':{'entity':'Example','period':'FY2025'}}
    if version==1:
        money['context']['unit']='USD'
        types={'amount':money}
        predicate={'op':'eq','left':ref('amount'),'right':{'op':'const','type':deepcopy(money),'value':'6/1'}}
        values={'amount':known('6/1')}
    else:
        money.update(dimensions={'USD':1},scale='1/1')
        rate={'kind':'rational','context':deepcopy(money['context']),'dimensions':{},'scale':'1/1'}
        types={'amount':money,'rate':rate,'total':deepcopy(money)}
        predicate={'op':'eq','left':{'op':'mul','left':ref('amount'),'right':ref('rate')},'right':ref('total')}
        values={'amount':known('3/1'),'rate':known('2/1'),'total':known('6/1')}
    requirement={'id':'amount-relation','predicate':predicate,'requires':sorted(types),
                 'admission_refs':[],'on_false':'invalid','on_unknown':'unresolved'}
    d={'profile':'MethodRequirements/'+str(version),'method_id':'independent.interoperability',
       'version':str(version),'inputs':{key:{'type':t,'role':'state','source_ref':'constructed:'+key}
                                       for key,t in types.items()},
       'requirements':[requirement],'capabilities':['exact-assessment'],
       'residual_prerequisites':['Source meaning, accounting applicability and execution remain separate.']}
    if version==3:
        d['inputs']['active']={'type':deepcopy(core.BOOL),'role':'caller_finding','source_ref':'constructed:active'}
        requirement.update(guard=ref('active'),guard_requires=['active'])
        d['required_known']=['amount']
        values['active']=known(True)
    return d,values


def exchange(definition,values):
    return {'profile':text.EXCHANGE,'definition':deepcopy(definition),
            'selected_digest':core.digest(definition),'values':deepcopy(values),
            'available_capabilities':deepcopy(definition['capabilities'])}


def packet(definition,values):
    """The caller explicitly authors a new canonical derived input record."""
    d=deepcopy(definition)
    raw=core.canonical(values)
    raw_key=sha256(raw).hexdigest()
    shape={'profile':binder.SCHEMA,'requirements_profile':d['profile'],
           'schema_id':'independent-selected-inputs','fields':{}}
    entries=[]
    for key,declaration in d['inputs'].items():
        pointer='/'+key.replace('~','~0').replace('/','~1')
        declaration['source_ref']='sha256:'+raw_key+'#'+pointer
        shape['fields'][pointer]={'type':deepcopy(declaration['type']),'role':declaration['role'],
                                  'encoding':'tagged_binding','missing':'unresolved'}
        entries.append({'input':key,'record':'derived','pointer':pointer})
    key=core.digest(d)
    schema_key=core.digest(shape)
    return {'plan':{'profile':binder.PROFILE,'manifest_digest':key,
                   'records':{'derived':{'raw_sha256':raw_key,'schema_digest':schema_key}},
                   'bindings':entries},'manifests':{key:d},'schemas':{schema_key:shape},
            'blobs':{raw_key:raw},'available_capabilities':d['capabilities']}


def assess(packet):
    return binder.assess_bound(**packet)
