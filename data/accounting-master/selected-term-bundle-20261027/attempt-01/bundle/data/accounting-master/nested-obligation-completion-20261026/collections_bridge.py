"""Explicit projected complete collections into the retained collection engine."""
from copy import deepcopy
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'nested-map-projection-20261026'))
import projection as p
import method_collections_v1 as engine
core=p.core
PROFILE='ProjectedStateCollections/1';CALL='ProjectedStateCollectionsCall/1';MAX_SOURCES=16

def validate(spec,definition):
    p.base.memory.bounded(spec)
    core.closed(spec,['profile','context','definition','sources','bindings','residuals'],'projected_collections')
    core.need(spec['profile']==PROFILE,'projected_collections_profile');engine.validate(spec['definition'])
    core.need(spec['definition']['inputs']=={},'projected_collections_no_globals')
    sources=spec['sources'];bindings=spec['bindings'];collections=spec['definition']['collections']
    core.need(type(sources) is dict and 0<len(sources)<=MAX_SOURCES,'collection_source_limit')
    for name,source in sources.items():
        core.text(name,'source_name');p.compile_spec(source,definition)
        core.need(source['context']==spec['context'],'collection_source_context')
    core.need(type(bindings) is dict and set(bindings)==set(collections),'exact_collection_bindings')
    used=set()
    for name,binding in bindings.items():
        core.need(type(binding) is dict,'collection_binding');kind=binding.get('kind')
        core.need(kind in ('seen','projected'),'collection_binding_kind')
        core.closed(binding,['kind','fields']+(['source','filter'] if kind=='projected' else []),'collection_binding')
        fields=collections[name]['fields']
        core.need(type(binding['fields']) is dict and set(binding['fields'])==set(fields),'exact_collection_field_bindings')
        if kind=='projected':
            source_name=binding['source'];core.text(source_name,'binding_source');core.need(source_name in sources,'collection_source_missing')
            used.add(source_name);source=sources[source_name]
            condition=binding['filter']
            if condition is not None:
                core.closed(condition,['field','type','value'],'equality_filter')
                core.text(condition['field'],'filter_field');core.need(condition['field'] in source['fields'],'filter_field_missing')
                core.need(condition['type']==source['fields'][condition['field']]['type'],'filter_field_type')
                p.base.dimensions.typed(condition['type']);core.scalar(condition['value'],condition['type']['kind'])
        for field,target in binding['fields'].items():
            core.text(target,'projected_field');typ=p.guards.TEXT
            if kind=='seen':core.need(target=='value','seen_binding_value')
            else:
                core.need(target in source['fields'],'projection_field_missing');typ=source['fields'][target]['type']
            core.need(fields[field]['type']==typ and fields[field]['role']=='state','collection_binding_type_role')
    core.need(used==set(sources),'unused_collection_source')
    core.identifiers(spec['residuals'],'collection_residuals',True)

def make_call(spec,book,definition,schemas,coverages,selection):
    result=dict(profile=CALL,book_order_sha256=p.order_digest(book),spec_order_sha256=p.order_digest(spec),reviewed_selection=selection)
    for n,v in [('spec',spec),('book',book),('definition',definition),('schemas',schemas),('coverages',coverages)]:result[n+'_sha256']=core.digest(v)
    return result

def assess(spec,book,definition,schemas,coverages,selection,call):
    result=dict(profile=PROFILE,**p.FLAGS,method_eligible=False);stage='call'
    try:
        core.need(call==make_call(spec,book,definition,schemas,coverages,selection),'stale_collection_call')
        result.update({k:v for k,v in call.items() if k!='profile'})
        core.need(selection==core.digest(spec),'reviewed_collection_selection')
        stage='declaration';validate(spec,definition);core.need(spec['context']==book['context'],'collections_book_context')
        core.need(type(coverages) is dict and set(coverages)==set(spec['sources']),'exact_source_coverages')
        stage='projections';projected={}
        for name,source in spec['sources'].items():
            args=(source,book,definition,schemas,coverages[name]);projected[name]=p.project(*args,p.make_call(*args))
        result['projections']=projected
        statuses=[r['status'] for r in projected.values()]
        if any(s!='projected' for s in statuses):
            return dict(result,status='invalid' if 'invalid' in statuses else 'unresolved',reason='collection_projection_unavailable',failed_stage=stage)
        stage='binding';values={'globals':{},'collections':{}};lineage={};visits=0
        for name,b in spec['bindings'].items():
            rows=[];origins=[]
            if b['kind']=='seen':
                for i,value in enumerate(book['seen']):
                    rows.append({field:dict(status='known',value=value) for field in b['fields']})
                    origins.append(dict(source_index=i,fields={field:dict(path='/seen/'+str(i),kind='seen',type=p.guards.TEXT) for field in b['fields']}))
            else:
                source=projected[b['source']];condition=b['filter']
                for i,row in enumerate(source['rows']):
                    if condition is not None and core.scalar(row[condition['field']]['value'],condition['type']['kind'])!=core.scalar(condition['value'],condition['type']['kind']):continue
                    rows.append({field:deepcopy(row[target]) for field,target in b['fields'].items()})
                    origin=source['lineage'][i]
                    origins.append(dict(source_index=i,parent_key=origin['parent_key'],child_key=origin['child_key'],
                        fields={field:deepcopy(origin['fields'][target]) for field,target in b['fields'].items()}))
            visits+=len(rows);core.need(visits<=engine.MAX_ROWS,'combined_collection_row_limit')
            values['collections'][name]=dict(status='complete',rows=rows)
            lineage[name]=dict(binding=deepcopy(b),rows=origins,completeness='Explicit predicate over complete supplied source' if b['kind']=='projected' else 'Complete supplied book seen sequence')
        stage='assessment';assessment=engine.assess(spec['definition'],values,[])
        core.need('findings' in assessment,'collection_engine_failed:'+assessment.get('reason',''))
        return dict(result,status=assessment['status'],failed_stage=None,values=values,lineage=lineage,assessment=assessment,
            residuals=deepcopy(spec['residuals']))
    except (ValueError,TypeError,KeyError,IndexError,RecursionError,OverflowError) as exc:
        return dict(result,status='invalid',reason=str(exc)[:300],failed_stage=stage)
