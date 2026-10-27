"""Explicit parameter substitution; native lifecycle construction is not imported."""
from copy import deepcopy
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE.parent/'complete-method-authoring-20261026'))
import frontend
base=frontend.v1;core=base.core;types=frontend.v2.types
PROFILE='ParameterizedCompanyMethod/1'
CALL='ParameterizedMethodConstruction/1'
TEXT={'kind':'text','context':{}}
DATE={'kind':'date','context':{}}

class Refusal(ValueError):
    def __init__(self,status,reason):
        self.status=status;self.reason=reason;super().__init__(reason)
def need(ok,reason):
    if not ok:raise Refusal('invalid',reason)
def closed(value,keys,reason):need(type(value) is dict and set(value)==set(keys),reason)
def exact(value):
    if value is None or type(value) in (str,int,bool):return
    if type(value) is list:
        for v in value:exact(v)
        return
    if type(value) is dict and all(type(k) is str for k in value):
        for v in value.values():exact(v)
        return
    raise Refusal('invalid','non_exact_json')

def construct(template,book,event,schemas,memory_definition,call):
    try:return _construct(template,book,event,schemas,memory_definition,call)
    except Refusal:raise
    except (ValueError,KeyError,TypeError,IndexError) as exc:
        raise Refusal('invalid',str(exc) or type(exc).__name__) from exc

def _construct(template,book,event,schemas,memory_definition,call):
    for value in (template,book,event,schemas,memory_definition,call):
        base.memory.bounded(value)
        exact(value);need(len(core.canonical(value))<=core.MAX_BYTES,'record_size_limit')
    closed(template,['profile','transition_profile','context','parameters','method_template','input_schema_definition','residuals'],'template_fields')
    need(template['profile']==PROFILE,'template_profile')
    need(template['transition_profile']==frontend.v2.PROFILE,'transition_profile')
    need(core.canonical(template['context'])==core.canonical(book['context']),'context_mismatch')
    need(type(template['residuals']) is list and all(type(x) is str and bool(x) for x in template['residuals']),'template_residuals')
    closed(call,['profile','template_sha256','state_sha256','event_sha256'],'call_fields')
    need(call['profile']==CALL,'call_profile')
    for name,value in [('template',template),('state',book),('event',event)]:need(call[name+'_sha256']==core.digest(value),'stale_'+name)
    closed(event,['id','date','inputs'],'event_fields');base.text(event['id'],'event_id');core.scalar(event['date'],'date')
    need(type(event['inputs']) is dict,'event_inputs')
    for name,record in event['inputs'].items():
        base.text(name,'event_input');closed(record,['type','value','provenance'],'event_input_fields')
        base.scalar_type(record['type'],book);base.text(record['provenance'],'event_provenance')
        core.validate_values({'inputs':{name:{'type':base.dimensions.encoded(record['type'])}}},{name:record['value']})
        if record['value']['status']=='unknown':raise Refusal('unresolved','unknown_event_input:'+name)
    need(type(schemas) is dict,'schemas')
    for h,shape in schemas.items():need(core.digest(shape)==h,'schema_digest')
    shape=types.compile_schema(template['input_schema_definition'],book);shape_hash=core.digest(shape)
    merged=deepcopy(schemas)
    need(shape_hash not in merged or core.canonical(merged[shape_hash])==core.canonical(shape),'schema_collision')
    merged[shape_hash]=shape
    need(type(template['parameters']) is list,'parameter_population')
    values={};declared_types={};lineage={};used=set()
    for param in template['parameters']:
        closed(param,['name','type','source'],'parameter_fields')
        name=param['name'];need(type(name) is str and bool(name) and name not in values,'duplicate_or_invalid_parameter')
        typ=param['type'];base.scalar_type(typ,book)
        source=param['source'];need(type(source) is dict,'parameter_source')
        kind=source.get('kind')
        if kind=='event_input':
            closed(source,['kind','name'],'event_source_fields');n=source['name']
            need(type(n) is str and n in event['inputs'],'missing_event_parameter')
            record=event['inputs'][n];need(core.canonical(record['type'])==core.canonical(typ),'parameter_type')
            value=record['value']['value'];origin={'event_sha256':core.digest(event),'input':n,'provenance':record['provenance']}
        elif kind=='event_metadata':
            closed(source,['kind','field'],'event_metadata_fields');field=source['field']
            need(field in ('id','date'),'event_metadata_field')
            need(typ==(DATE if field=='date' else TEXT),'parameter_type')
            value=event[field];origin={'event_sha256':core.digest(event),'field':field}
        elif kind=='book_metadata':
            closed(source,['kind','field'],'book_metadata_fields');field=source['field']
            need(field in ('date','memory_schema'),'book_metadata_field')
            need(typ==(DATE if field=='date' else TEXT),'parameter_type')
            value=book[field];origin={'state_sha256':core.digest(book),'field':field}
        elif kind=='input_schema':
            closed(source,['kind'],'schema_source_fields');need(typ==TEXT,'parameter_type')
            value=shape_hash;origin={'definition_sha256':core.digest(template['input_schema_definition']),'schema_sha256':shape_hash}
        elif kind=='pointer':
            closed(source,['kind','segments'],'pointer_source_fields');need(typ==TEXT,'parameter_type')
            need(type(source['segments']) is list and 0<len(source['segments'])<=core.MAX_DEPTH,'pointer_segments')
            segments=[];deps=[]
            for segment in source['segments']:
                need(type(segment) is dict and len(segment)==1,'pointer_segment')
                if 'literal' in segment:
                    token=segment['literal'];need(type(token) is str and bool(token),'pointer_literal')
                else:
                    need(set(segment)=={'parameter'},'pointer_segment');ref=segment['parameter']
                    need(type(ref) is str and ref in values,'forward_or_missing_parameter')
                    need(declared_types[ref]==TEXT,'pointer_parameter_type')
                    token=values[ref];used.add(ref);deps.append(ref)
                segments.append(token)
            value=types.pointer(segments)
            need(base.binding.pointer_parts(value)==segments,'pointer_roundtrip')
            origin={'segments':segments,'parameters':deps}
        else:raise Refusal('invalid','unsupported_parameter_source')
        core.scalar(value,typ['kind'])
        if typ['kind']=='rational':base.monetary.rational(value)
        values[name]=deepcopy(value);declared_types[name]=deepcopy(typ);lineage[name]=origin
    counter=[0]
    def expand(node,depth=0):
        counter[0]+=1;need(counter[0]<=core.MAX_NODES and depth<=core.MAX_DEPTH,'template_limit')
        need(type(node) is dict,'template_node')
        kind=node.get('node')
        if kind=='literal':
            closed(node,['node','value'],'literal_node')
            need(node['value'] is None or type(node['value']) in (str,int,bool),'literal_scalar')
            return deepcopy(node['value'])
        if kind=='parameter':
            closed(node,['node','name'],'parameter_node');name=node['name']
            need(type(name) is str and name in values,'unbound_parameter');used.add(name)
            return deepcopy(values[name])
        if kind=='object':
            closed(node,['node','fields'],'object_node');need(type(node['fields']) is dict,'object_fields')
            return {k:expand(v,depth+1) for k,v in node['fields'].items()}
        if kind=='array':
            closed(node,['node','items'],'array_node');need(type(node['items']) is list,'array_items')
            return [expand(v,depth+1) for v in node['items']]
        raise Refusal('invalid','unsupported_template_node')
    method=expand(template['method_template'])
    need(used==set(values),'unused_parameters')
    environment={'book':book,'event':event,'schemas':merged,'memory_definition':memory_definition}
    compiled=frontend.compile_typed(method,template['transition_profile'],environment)
    source=frontend.render(method,template['transition_profile'],environment)
    lowered=frontend.compile_text(source,environment)
    need(core.canonical(lowered['request'])==core.canonical(compiled['request']),'source_correspondence')
    return {'profile':PROFILE,'status':'constructed_method','template_sha256':core.digest(template),
            'state_sha256':core.digest(book),'event_sha256':core.digest(event),'parameters':values,'lineage':lineage,
            'request':compiled['request'],'source':source,'source_sha256':lowered['source_sha256'],
            'source_admission':False,'accounting_admission':False,'event_contract_portable':False,'production_ready':False}

def make_call(template,book,event):
    return {'profile':CALL,'template_sha256':core.digest(template),'state_sha256':core.digest(book),'event_sha256':core.digest(event)}
