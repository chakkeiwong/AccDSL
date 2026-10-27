"""Pure input binding with pinned record/schema identities and explicit conventions."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import importlib.util
import re
import method_requirements_v1 as core

ROOT=Path(__file__).resolve().parents[1]
PROFILE='MethodInputBinding/1'
SCHEMA='RequirementInputSchema/1'
HELPERS={
    'data/accounting-master/company-portable-authoring-20261023/portable.py':
        '96f91ddd00e600764ce5568170d1387660d908c23c029eb5c0e97dab1fb712c2',
    'data/accounting-master/company-path-admission-20261023/admission.py':
        '334e6172fac9708982ee896b5c9d1dc0161b0e3362df9da4d83abe66a7ae6efc'}
for name,h in HELPERS.items():
    core.need(sha256((ROOT/name).read_bytes()).hexdigest()==h,'pinned_helper_changed:'+name)
spec=importlib.util.spec_from_file_location('requirement_portable_decoder',ROOT/next(iter(HELPERS)))
portable=importlib.util.module_from_spec(spec)
spec.loader.exec_module(portable)


class Unavailable(ValueError):
    pass


def hash_string(value):
    core.need(type(value) is str and re.fullmatch('[0-9a-f]{64}',value) is not None,'digest')


def pointer_parts(pointer):
    core.need(type(pointer) is str and len(pointer)<=core.MAX_SCALAR,'pointer')
    if pointer=='':
        return []
    core.need(pointer.startswith('/'),'pointer_prefix')
    tokens=pointer[1:].split('/')
    core.need(len(tokens)<=core.MAX_DEPTH,'pointer_depth')
    for token in tokens:
        core.need(re.search(r'~(?![01])',token) is None,'pointer_escape')
    return [token.replace('~1','/').replace('~0','~') for token in tokens]


def located(value,pointer):
    """Validate traversal shape; use the retained selector for a successful read."""
    original=value
    for token in pointer_parts(pointer):
        if type(value) is dict:
            if token not in value:
                return False,None
            value=value[token]
        elif type(value) is list:
            core.need(re.fullmatch(r'0|[1-9][0-9]*',token) is not None,'array_index')
            index=int(token)
            if index>=len(value):
                return False,None
            value=value[index]
        else:
            raise core.Invalid('scalar_pointer_traversal')
    return True,portable.select(original,pointer)


def bounded(value):
    stack=[(value,0)]
    count=0
    while stack:
        item,depth=stack.pop()
        count+=1
        core.need(count<=core.MAX_NODES and depth<=core.MAX_DEPTH,'record_structure_limit')
        if type(item) is dict:
            stack.extend((v,depth+1) for v in item.values())
        elif type(item) is list:
            stack.extend((v,depth+1) for v in item)


def schema(value):
    core.closed(value,['profile','schema_id','fields'],'input_schema')
    core.need(value['profile']==SCHEMA,'input_schema_profile')
    core.text(value['schema_id'],'schema_id')
    core.need(type(value['fields']) is dict and bool(value['fields']),'schema_fields')
    for pointer,field in value['fields'].items():
        pointer_parts(pointer)
        core.closed(field,['type','role','encoding','missing'],'input_schema_field')
        core.typed(field['type'])
        core.need(type(field['role']) is str and field['role'] in core.ROLES,'input_role')
        core.need(field['encoding'] in ['scalar','legacy_unknown_string','tagged_binding'],'input_encoding')
        core.need(field['missing'] in ['invalid','unresolved'],'missing_policy')
    return value


def record(registry,key,kind):
    core.need(type(registry) is dict,'registry:'+kind)
    hash_string(key)
    if key not in registry:
        raise Unavailable(kind+'_unavailable:'+key)
    value=registry[key]
    core.need(core.digest(value)==key,kind+'_digest_mismatch')
    return value


def bind(plan, manifests, schemas, blobs):
    boundary={'executed':False,'source_admission':False,'accounting_admission':False,
              'method_eligible':False,'schema_meaning':'caller_declared_selected_fields_only'}
    try:
        core.need(type(blobs) is dict,'blob_registry')
        core.need(len(core.canonical(plan))<=core.MAX_BYTES,'plan_size_limit')
        core.closed(plan,['profile','manifest_digest','records','bindings'],'binding_plan')
        core.need(plan['profile']==PROFILE,'binding_profile')
        manifest=record(manifests,plan['manifest_digest'],'manifest')
        core.validate_manifest(manifest)
        core.need(type(plan['records']) is dict,'records')
        core.need(type(plan['bindings']) is list,'bindings')
        seen=set()
        used_records=set()
        for entry in plan['bindings']:
            core.closed(entry,['input','record','pointer'],'binding')
            for key in ['input','record']:
                core.text(entry[key],key)
            pointer_parts(entry['pointer'])
            core.need(entry['input'] not in seen,'duplicate_input_binding')
            seen.add(entry['input'])
            used_records.add(entry['record'])
        core.need(seen==set(manifest['inputs']),'incomplete_or_extra_input_mapping')
        core.need(used_records==set(plan['records']),'unused_or_missing_record')
        loaded={}
        for name,reference in plan['records'].items():
            core.text(name,'record_name')
            core.closed(reference,['raw_sha256','schema_digest'],'record_reference')
            h=reference['raw_sha256']
            hash_string(h)
            shape=schema(record(schemas,reference['schema_digest'],'schema'))
            if h not in blobs:
                raise Unavailable('record_bytes_unavailable:'+h)
            raw=blobs[h]
            core.need(type(raw) is bytes and len(raw)<=core.MAX_BYTES,'raw_bytes_limit')
            core.need(sha256(raw).hexdigest()==h,'raw_digest_mismatch')
            data=portable.decode(raw)
            bounded(data)
            loaded[name]=(reference,shape,data)
        values,lineage={},{}
        for entry in plan['bindings']:
            key,pointer=entry['input'],entry['pointer']
            reference,shape,data=loaded[entry['record']]
            core.need(pointer in shape['fields'],'undeclared_field_pointer')
            field=shape['fields'][pointer]
            declaration=manifest['inputs'][key]
            core.need(field['type']==declaration['type'],'binding_type_or_context_mismatch')
            core.need(field['role']==declaration['role'],'binding_role_mismatch')
            expected_ref='sha256:'+reference['raw_sha256']+'#'+pointer
            core.need(declaration['source_ref']==expected_ref,'binding_source_ref_mismatch')
            found,value=located(data,pointer)
            if not found:
                core.need(field['missing']=='unresolved','required_path_missing')
                item={'status':'unknown','reason':'missing_declared_path'}
            elif field['encoding']=='legacy_unknown_string' and value=='unknown':
                item={'status':'unknown','reason':'legacy_explicit_unknown'}
            elif field['encoding']=='tagged_binding':
                item=value
            else:
                item={'status':'known','value':value}
            core.validate_values(manifest,{key:item})
            values[key]=deepcopy(item)
            lineage[key]={'record':entry['record'],**reference,'pointer':pointer,
                          'type':deepcopy(field['type']),'role':field['role'],
                          'encoding':field['encoding'],'missing':field['missing'],
                          'source_ref':expected_ref}
        return {**boundary,'status':'bound','plan_digest':core.digest(plan),
                'manifest_digest':plan['manifest_digest'],'values':values,'lineage':lineage}
    except Unavailable as exc:
        return {**boundary,'status':'unsupported','reason':str(exc)}
    except (ValueError,TypeError,KeyError,RecursionError,OverflowError) as exc:
        return {**boundary,'status':'invalid','reason':str(exc)[:250]}


def assess_bound(plan,manifests,schemas,blobs,available_capabilities):
    result=bind(plan,manifests,schemas,blobs)
    if result['status']!='bound':
        return result
    result['assessment']=core.assess(manifests,plan['manifest_digest'],result['values'],available_capabilities)
    return result
