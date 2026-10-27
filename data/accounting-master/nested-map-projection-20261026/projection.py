"""Bounded typed nested-map rows; no financial or history-selection semantics."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json,sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'authored-state-invariants-20261026'))
import guards
core=guards.core;base=guards.base;types=guards.types
PROFILE='NestedMapProjection/1';POPULATION='SuppliedNestedPopulation/1'
CALL='NestedMapProjectionCall/1';MAX_ROWS=256;MAX_GROUPS=256
FLAGS=dict(executed=False,source_admission=False,accounting_admission=False,
           actual_population_completeness=False,production_ready=False)

def order_digest(value):
    return sha256(json.dumps(value,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()).hexdigest()

def exact_pointer(pointer):
    parts=base.binding.pointer_parts(pointer)
    core.need(bool(parts) and types.pointer(parts)==pointer,'canonical_nonempty_pointer')
    return parts

def record_path(node,pointer):
    for key in exact_pointer(pointer):
        core.need(node['node']=='record' and key in node['fields'],'record_path')
        node=node['fields'][key]
    return node

def compile_spec(spec,definition):
    base.memory.bounded(spec);base.memory.bounded(definition)
    core.closed(spec,['profile','context','parent_pointer','child_pointer','fields','residuals'],'projection_fields')
    core.need(spec['profile']==PROFILE and type(spec['context']) is dict,'projection_profile_context')
    core.identifiers(spec['residuals'],'residuals',True)
    parent=record_path(definition['root'],spec['parent_pointer'])
    core.need(parent['node']=='map' and parent['values']['node']=='record','parent_map_record')
    child=record_path(parent['values'],spec['child_pointer'])
    core.need(child['node']=='map' and child['values']['node']=='record','child_map_record')
    core.need(type(spec['fields']) is dict and 0<len(spec['fields'])<=64,'projection_field_limit')
    for name,b in spec['fields'].items():
        core.text(name,'projection_field')
        kind=b.get('kind');core.need(kind in ('parent_key','child_key','parent_field','child_field'),'binding_kind')
        core.closed(b,['kind','type']+(['pointer'] if kind.endswith('_field') else []),'field_binding')
        base.dimensions.typed(b['type'])
        if kind.endswith('_key'):actual=guards.TEXT
        else:
            node=record_path(parent['values'] if kind=='parent_field' else child['values'],b['pointer'])
            core.need(node['node']=='scalar','scalar_field_required')
            actual=node['type']
        core.need(actual==b['type'],'declared_field_type:'+name)
    return parent,child

def population(spec,book,status,provenance):
    return dict(profile=POPULATION,status=status,book_sha256=core.digest(book),
                parent_pointer=spec['parent_pointer'],child_pointer=spec['child_pointer'],provenance=provenance)

def make_call(spec,book,definition,schemas,coverage):
    result=dict(profile=CALL,book_order_sha256=order_digest(book))
    for name,value in [('spec',spec),('book',book),('definition',definition),('schemas',schemas),('population',coverage)]:
        result[name+'_sha256']=core.digest(value)
    return result

def project(spec,book,definition,schemas,coverage,call):
    result=dict(profile=PROFILE,**FLAGS);stage='call'
    try:
        core.need(call==make_call(spec,book,definition,schemas,coverage),'stale_projection_call')
        result.update({k:v for k,v in call.items() if k!='profile'})
        stage='declaration';compile_spec(spec,definition)
        stage='typed_book';guards.program.typed.typed_book(book,definition,schemas)
        core.need(spec['context']==book['context'],'projection_context')
        stage='population'
        core.closed(coverage,['profile','status','book_sha256','parent_pointer','child_pointer','provenance'],'population_fields')
        core.need(coverage['profile']==POPULATION,'population_profile')
        core.need(coverage['status'] in ('complete','partial','unknown'),'population_status')
        core.text(coverage['provenance'],'population_provenance')
        core.need(coverage['book_sha256']==core.digest(book),'population_book')
        core.need((coverage['parent_pointer'],coverage['child_pointer'])==(spec['parent_pointer'],spec['child_pointer']),'population_scope')
        if coverage['status']!='complete':
            return dict(result,status='unresolved',reason='complete_supplied_population_required',failed_stage=stage)
        stage='projection'
        _,parents=base.binding.located(book['memory'],spec['parent_pointer'])
        core.need(len(parents)<=MAX_GROUPS,'group_limit')
        rows=[];groups=[];lineage=[]
        for parent_key,parent_value in parents.items():
            parent_path=types.pointer(exact_pointer(spec['parent_pointer'])+[parent_key])
            _,children=base.binding.located(parent_value,spec['child_pointer'])
            first=len(rows)
            core.need(first+len(children)<=MAX_ROWS,'row_limit')
            for child_key,child_value in children.items():
                child_path=types.pointer(exact_pointer(parent_path)+exact_pointer(spec['child_pointer'])+[child_key])
                row={};fields={}
                for name,b in spec['fields'].items():
                    kind=b['kind']
                    if kind=='parent_key':value=parent_key;path=parent_path
                    elif kind=='child_key':value=child_key;path=child_path
                    else:
                        value_root=parent_value if kind=='parent_field' else child_value
                        found,value=base.binding.located(value_root,b['pointer']);core.need(found,'missing_field')
                        path=(parent_path if kind=='parent_field' else child_path)+b['pointer']
                        core.need(book['memory_types'][path]==b['type'],'bound_field_type:'+name)
                    core.scalar(value,b['type']['kind'])
                    row[name]=base.known(deepcopy(value))
                    fields[name]=dict(path='/memory'+path,kind=kind,type=deepcopy(b['type']))
                rows.append(row)
                lineage.append(dict(parent_key=parent_key,child_key=child_key,parent_path='/memory'+parent_path,
                                    child_path='/memory'+child_path,fields=fields))
            groups.append(dict(parent_key=parent_key,parent_path='/memory'+parent_path,
                               child_map_path='/memory'+parent_path+spec['child_pointer'],
                               row_start=first,row_count=len(rows)-first))
        return dict(result,status='projected',failed_stage=None,rows=rows,groups=groups,lineage=lineage,
                    collection_status='complete_supplied_internal',residuals=deepcopy(spec['residuals']))
    except (ValueError,TypeError,KeyError,IndexError,RecursionError,OverflowError) as exc:
        return dict(result,status='invalid',reason=str(exc)[:300],failed_stage=stage)
