"""Explicit bounded ordered expansion; no native lifecycle specializer."""
from copy import deepcopy
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'parameterized-method-construction-20261026'))
import constructor as c
PROFILE='OrderedMethodExpansion/1'
BOOL={'kind':'boolean','context':{}}

def make_call(template,book,event,order):
    return {'profile':PROFILE,'template_sha256':c.core.digest(template),'state_sha256':c.core.digest(book),
            'event_sha256':c.core.digest(event),'order':deepcopy(order),'order_sha256':c.core.digest(order)}

def encode(value):
    if type(value) is dict:return {'node':'object','fields':{k:encode(v) for k,v in value.items()}}
    if type(value) is list:return {'node':'array','items':[encode(v) for v in value]}
    return {'node':'literal','value':deepcopy(value)}

def construct(template,book,event,schemas,memory_definition,call):
    try:return _construct(template,book,event,schemas,memory_definition,call)
    except c.Refusal:raise
    except (ValueError,KeyError,TypeError,IndexError) as exc:raise c.Refusal('invalid',str(exc) or type(exc).__name__) from exc

def _construct(template,book,event,schemas,memory_definition,call):
    for value in (template,book,event,schemas,memory_definition,call):
        c.base.memory.bounded(value);c.exact(value)
        c.need(len(c.core.canonical(value))<=c.core.MAX_BYTES,'record_size_limit')
    c.closed(template,['profile','base_template','map_pointer','row_types','row_operations','suffix_operations','residuals'],'expansion_fields')
    c.need(template['profile']==PROFILE,'expansion_profile')
    c.closed(call,['profile','template_sha256','state_sha256','event_sha256','order','order_sha256'],'expansion_call_fields')
    c.need(call['profile']==PROFILE,'expansion_call_profile')
    for name,value in [('template',template),('state',book),('event',event),('order',call['order'])]:
        c.need(call[name+'_sha256']==c.core.digest(value),'stale_'+name)
    c.frontend.v2.typed_book(book,memory_definition,schemas)
    c.closed(event,['id','date','inputs'],'event_fields');c.base.text(event['id'],'event_id');c.core.scalar(event['date'],'date')
    c.need(type(event['inputs']) is dict,'event_inputs')
    for name,r in event['inputs'].items():
        c.closed(r,['type','value','provenance'],'event_input_fields');c.base.scalar_type(r['type'],book);c.base.text(r['provenance'],'event_provenance')
        c.core.validate_values({'inputs':{name:{'type':c.base.dimensions.encoded(r['type'])}}},{name:r['value']})
        if r['value']['status']=='unknown':raise c.Refusal('unresolved','unknown_event_input:'+name)
    parts=c.base.binding.pointer_parts(template['map_pointer']);node=memory_definition['root']
    for part in parts:
        c.need(node['node']=='record' and part in node['fields'],'declared_map_path');node=node['fields'][part]
    c.need(node['node']=='map' and node['values']['node']=='record','declared_record_map')
    fields=node['values']['fields'];c.need(type(template['row_types']) is dict and set(template['row_types'])==set(fields),'row_type_population')
    for name,typ in template['row_types'].items():
        c.base.scalar_type(typ,book);c.need(fields[name]=={'node':'scalar','type':typ},'row_type_mismatch')
    found,population=c.base.binding.located(book['memory'],template['map_pointer'])
    c.need(found and type(population) is dict,'map_population')
    order=call['order'];c.need(type(order) is list and all(type(x) is str for x in order),'order_type')
    c.need(len(order)==len(set(order)),'duplicate_order_key')
    c.need(set(order)==set(population),'order_coverage')
    c.need(type(template['row_operations']) is list and bool(template['row_operations']),'row_operations')
    c.need(type(template['suffix_operations']) is list,'suffix_operations')
    c.need(type(template['residuals']) is list and all(type(x) is str for x in template['residuals']),'expansion_residuals')
    count=len(order)*len(template['row_operations'])+len(template['suffix_operations'])
    c.need(count<=c.base.memory.MAX_OPERATIONS,'operation_limit')
    # Validate row expressions even for an empty population. Values are supplied
    # only after a full structural/type traversal of both conditional branches.
    counter=[0]
    def infer(expr,row_allowed):
        counter[0]+=1;c.need(counter[0]<=c.core.MAX_NODES,'expression_node_limit')
        c.need(type(expr) is dict,'expression_record');kind=expr.get('expr')
        if kind=='literal':
            c.closed(expr,['expr','type','value'],'literal_expression');typ=expr['type'];c.base.scalar_type(typ,book);c.core.scalar(expr['value'],typ['kind'])
            return typ
        if kind=='row':
            c.closed(expr,['expr','field'],'row_expression');c.need(row_allowed and expr['field'] in template['row_types'],'row_field')
            return template['row_types'][expr['field']]
        if kind=='key':
            c.closed(expr,['expr'],'key_expression');c.need(row_allowed,'key_scope');return c.TEXT
        if kind=='event_metadata':
            c.closed(expr,['expr','field'],'event_metadata_expression');c.need(expr['field'] in ('id','date'),'event_metadata_field')
            return c.DATE if expr['field']=='date' else c.TEXT
        if kind=='event_input':
            c.closed(expr,['expr','name','type'],'event_input_expression');c.need(expr['name'] in event['inputs'],'event_input_missing')
            c.need(event['inputs'][expr['name']]['type']==expr['type'],'event_input_type');return expr['type']
        if kind in ('date_lt','date_le'):
            c.closed(expr,['expr','left','right'],'date_comparison');left=infer(expr['left'],row_allowed);right=infer(expr['right'],row_allowed)
            c.need(left==right==c.DATE,'date_comparison_type');return BOOL
        if kind=='if':
            c.closed(expr,['expr','condition','then','else'],'if_expression')
            cond=infer(expr['condition'],row_allowed);a=infer(expr['then'],row_allowed);b=infer(expr['else'],row_allowed)
            c.need(cond==BOOL,'condition_type');c.need(a==b and 'kind' in a,'branch_type');return a
        if kind=='operation_id':
            c.closed(expr,['expr','prefix'],'operation_id_expression');c.need(row_allowed,'operation_id_scope');c.base.text(expr['prefix'],'operation_prefix');return c.TEXT
        if kind=='object':
            c.closed(expr,['expr','fields'],'object_expression');c.need(type(expr['fields']) is dict,'object_expression_fields')
            return {'record':{k:infer(v,row_allowed) for k,v in expr['fields'].items()}}
        if kind=='array':
            c.closed(expr,['expr','items'],'array_expression');c.need(type(expr['items']) is list,'array_expression_items')
            return {'array':[infer(v,row_allowed) for v in expr['items']]}
        raise c.Refusal('invalid','unsupported_expression')
    def validate_operation(expr,row_allowed):
        inferred=infer(expr,row_allowed)
        c.need(set(inferred)=={'record'} and set(inferred['record'])=={'id','op','path','value'},'operation_expression_shape')
        fields=expr['fields'];shape=inferred['record']
        c.need(shape['id']==shape['op']==c.TEXT,'operation_expression_type')
        c.need(fields['op']=={'expr':'literal','type':c.TEXT,'value':'replace'},'declared_replace_operation')
        c.need(set(shape['path'])=={'array'} and all(t==c.TEXT for t in shape['path']['array']),'operation_path_type')
        tokens=fields['path']['items']
        if row_allowed:
            c.need(len(tokens)==len(parts)+2,'row_write_path')
            for token,part in zip(tokens,parts):
                c.need(token=={'expr':'literal','type':c.TEXT,'value':part},'row_write_prefix')
            c.need(tokens[-2]=={'expr':'key'},'row_write_key')
            last=tokens[-1];c.need(last.get('expr')=='literal' and last.get('type')==c.TEXT and last.get('value') in template['row_types'],'row_write_field')
            target=template['row_types'][last['value']]
        else:
            c.need(all(t.get('expr')=='literal' and t.get('type')==c.TEXT for t in tokens),'suffix_literal_path')
            pointer=c.types.pointer([t['value'] for t in tokens]);c.need(pointer in book['memory_types'],'suffix_target')
            target=book['memory_types'][pointer]
        c.need(set(shape['value'])=={'record'} and set(shape['value']['record'])=={'kind','value'},'write_value_shape')
        c.need(fields['value']['fields']['kind']=={'expr':'literal','type':c.TEXT,'value':'literal'},'write_value_literal_kind')
        c.need(shape['value']['record']['value']==target,'write_value_type')
    for expr in template['row_operations']:validate_operation(expr,True)
    for expr in template['suffix_operations']:validate_operation(expr,False)
    def evaluate(expr,row,key,index):
        kind=expr['expr']
        if kind=='literal':return deepcopy(expr['value'])
        if kind=='row':return deepcopy(row[expr['field']])
        if kind=='key':return key
        if kind=='event_metadata':return event[expr['field']]
        if kind=='event_input':return deepcopy(event['inputs'][expr['name']]['value']['value'])
        if kind in ('date_lt','date_le'):
            a=c.core.scalar(evaluate(expr['left'],row,key,index),'date');b=c.core.scalar(evaluate(expr['right'],row,key,index),'date')
            return a<b if kind=='date_lt' else a<=b
        if kind=='if':return evaluate(expr['then'] if evaluate(expr['condition'],row,key,index) else expr['else'],row,key,index)
        if kind=='operation_id':return expr['prefix']+str(index)
        if kind=='object':return {k:evaluate(v,row,key,index) for k,v in expr['fields'].items()}
        return [evaluate(v,row,key,index) for v in expr['items']]
    operations=[]
    for key in order:
        row=population[key];c.need(type(row) is dict and set(row)==set(template['row_types']),'row_population')
        for name,typ in template['row_types'].items():
            pointer=c.types.pointer(parts+[key,name]);c.need(book['memory_types'].get(pointer)==typ,'row_leaf_type')
            c.core.scalar(row[name],typ['kind'])
        for expr in template['row_operations']:operations.append(evaluate(expr,row,key,len(operations)))
    for expr in template['suffix_operations']:operations.append(evaluate(expr,None,None,None))
    base=deepcopy(template['base_template'])
    destination=base['method_template']['fields']['memory']['fields']['definition']['fields']
    c.need(destination['operations']=={'node':'array','items':[]},'base_operations_not_empty')
    destination['operations']=encode(operations)
    constructed=c.construct(base,book,event,schemas,memory_definition,c.make_call(base,book,event))
    return {'profile':PROFILE,'status':'constructed_method','template_sha256':c.core.digest(template),
            'state_sha256':c.core.digest(book),'event_sha256':c.core.digest(event),'order':deepcopy(order),
            'order_sha256':c.core.digest(order),'operations':operations,'construction':constructed,
            'source_admission':False,'accounting_admission':False,'event_contract_portable':False,'production_ready':False}
