"""Pinned structural validation of the complete retained native legal-book state."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import importlib.util,re
from jsonschema import Draft202012Validator,FormatChecker
import method_requirements_v1 as core
import method_input_binding_v1 as binding

ROOT=Path(__file__).resolve().parents[1]
PROFILE='NativeReturnStateStructure/1'
PINNED={
 'data/accounting-master/company-return-schema-20261023/return_schema.py':'638f10a4af2593371f80d4b93bc9fa5fccc49870a740b8f2e7b4c478d4fce1e3',
 'data/accounting-master/company-return-execution-20261024/native_returns.py':'0e7c18be351f2f7d1e806bf1edf2e4833aaeadb031615d765c52eeff91e71f14',
 'data/accounting-master/company-return-execution-20261024/native_reports.py':'f2f75338ebedc6c9fd7f5bb4d2f8eaabe4d9c6a4c3ee000c6d8b9d8117fb2f12'}


def load(name,path):
    core.need(sha256((ROOT/path).read_bytes()).hexdigest()==PINNED[path],'pinned_structure_source_changed')
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


author=load('state_structure_authoring',next(iter(PINNED)))
native=load('state_structure_native',list(PINNED)[1])
core.need(sha256((ROOT/list(PINNED)[2]).read_bytes()).hexdigest()==PINNED[list(PINNED)[2]],'pinned_carry_source_changed')


def schema():
    source=author.schema()['properties']
    text={'type':'string','minLength':1,'maxLength':core.MAX_SCALAR}
    ident=deepcopy(source['component']['properties']['id'])
    day={'type':'string','format':'date','pattern':r'^\d{4}-\d{2}-\d{2}$','x-exact-kind':'date'}
    digest={'type':'string','pattern':'^[0-9a-f]{64}$'}
    rational={'type':'string','pattern':r'^(0|-?[1-9][0-9]*)/[1-9][0-9]*$','x-exact-kind':'rational'}
    unknown={'oneOf':[deepcopy(rational),{'const':'unknown'}]}
    pointer={'type':'string','pattern':r'^/record_registry/[0-9a-f]{64}/body(?:/(?:[^~/]|~[01])*)*$'}
    component=deepcopy(source['component'])
    for key in author.NUMBERS:
        component['properties'][key]=deepcopy(rational if key in ['refund','recovery'] else unknown)
    component['properties']['settled']={'type':'boolean'}
    component['properties']['source_pointer']=deepcopy(pointer)
    tax=deepcopy(source['tax'])
    for key in author.TAX_NUMBERS:
        tax['properties'][key]=deepcopy(rational if key in ['opening_dta','opening_dtl'] else unknown)
    for key in ['source_pointer','opening_source_pointer']:tax['properties'][key]=deepcopy(pointer)
    lot=author.closed({'id':deepcopy(ident),'component_id':deepcopy(ident),
        **{key:deepcopy(rational) for key in ['units','carrying','tax_base']},
        'acquired':deepcopy(day),'disposed':{'type':'boolean'}})
    period=author.closed({'start':deepcopy(day),'end_exclusive':deepcopy(day)})
    flow=author.closed({'entity':deepcopy(text),'activity':{'enum':['operating','investing','financing']},
        'amount':deepcopy(rational),'origin':deepcopy(text),'date':deepcopy(day),'event_id':deepcopy(text)})
    adjustment=author.closed({'event_id':deepcopy(text),'date':deepcopy(day),'amount':deepcopy(rational)})
    prior=author.closed({'period':deepcopy(period),'closing_sha256':deepcopy(digest),'report_sha256':deepcopy(digest)})
    return {'$schema':'https://json-schema.org/draft/2020-12/schema',**author.closed({
        'profile':{'const':native.PROFILE},'context':deepcopy(source['context']),
        'source':deepcopy(source['source']),'period':period,'date':deepcopy(day),
        'balances':author.closed({key:deepcopy(rational) for key in native.ACCOUNTS}),
        'component':component,'lots':{'type':'object','propertyNames':deepcopy(ident),'additionalProperties':lot},
        'other_inventory':deepcopy(rational),'tax_premises':tax,
        'tax_adjustments':{'type':'array','items':adjustment},'tax_closed_until':deepcopy(day),
        'seen':{'type':'array','items':deepcopy(text)},'flows':{'type':'array','items':flow},
        'opening_interest_remaining':deepcopy(rational),'opening_interest_paid':deepcopy(rational),
        'prior_years':{'type':'array','items':prior},'conditional':{'const':True,'type':'boolean'}})}


def validate(value,shape):
    errors=list(Draft202012Validator(shape,format_checker=FormatChecker()).iter_errors(value))
    if errors:
        error=errors[0]
        path='/'+('/'.join(str(x).replace('~','~0').replace('/','~1') for x in error.absolute_path))
        raise core.Invalid('structure:'+path+':'+error.message[:180])
    def walk(item,rule,path=''):
        if 'oneOf' in rule:
            matching=[r for r in rule['oneOf'] if Draft202012Validator(r,format_checker=FormatChecker()).is_valid(item)]
            core.need(len(matching)==1,'ambiguous_structure:'+path)
            return walk(item,matching[0],path)
        if 'x-exact-kind' in rule:
            try:core.scalar(item,rule['x-exact-kind'])
            except ValueError as exc:raise core.Invalid('scalar:'+path+':'+str(exc)) from exc
        if type(item) is dict:
            for key,child in item.items():
                core.text(key,'object_key')
                child_rule=rule.get('properties',{}).get(key,rule.get('additionalProperties',{}))
                walk(child,child_rule,path+'/'+key.replace('~','~0').replace('/','~1'))
        elif type(item) is list:
            for i,child in enumerate(item):walk(child,rule['items'],path+'/'+str(i))
        elif type(item) is str:
            core.text(item,'scalar:'+path)
            core.need(not any(ch in item for ch in '\x85\u2028\u2029'),'single_line_scalar:'+path)
    walk(value,shape)
    return value


def inspect(raw,raw_sha256,schema_digest):
    boundary={'executed':False,'method_eligible':False,'source_admission':False,
              'accounting_admission':False,'profile':PROFILE,'scope':'complete_retained_state_structure_only'}
    try:
        binding.hash_string(raw_sha256);binding.hash_string(schema_digest)
        core.need(type(raw) is bytes and len(raw)<=core.MAX_BYTES,'raw_bytes_limit')
        core.need(sha256(raw).hexdigest()==raw_sha256,'raw_digest_mismatch')
        shape=schema();core.need(core.digest(shape)==schema_digest,'schema_digest_mismatch')
        value=binding.portable.decode(raw);binding.bounded(value);validate(value,shape)
        return {**boundary,'status':'structure_valid','raw_sha256':raw_sha256,'schema_digest':schema_digest,
                'decoded_sha256':core.digest(value),'value':deepcopy(value)}
    except (ValueError,TypeError,KeyError,RecursionError,OverflowError) as exc:
        return {**boundary,'status':'invalid','reason':str(exc)[:300]}
