"""Create a scoped successor without modifying the protected scalar expander."""
from pathlib import Path
from hashlib import sha256
import json
HERE=Path(__file__).resolve().parent
source=HERE.parent/'ordered-assessment-expansion-20261026/expander.py'
target=HERE/'nested_expander.py';assert not target.exists(),'successor_exists'
text=source.read_text();edits=[]
def replace(before,after):
    global text
    assert text.count(before)==1,before[:100]
    text=text.replace(before,after);edits.append(dict(before=before,after=after))
replace('Explicit bounded ordered expansion; no native lifecycle specializer.',
        'Bounded nested-record expansion; preserved scalar expression semantics.')
replace("PROFILE='OrderedMethodExpansion/1'","PROFILE='OrderedNestedMethodExpansion/1'")
replace("'map_pointer','row_types','row_operations'","'map_pointer','row_definition','row_operations'")
replace("fields=node['values']['fields'];c.need(type(template['row_types']) is dict and set(template['row_types'])==set(fields),'row_type_population')\n    for name,typ in template['row_types'].items():\n        c.base.scalar_type(typ,book);c.need(fields[name]=={'node':'scalar','type':typ},'row_type_mismatch')",
"""fields=node['values']['fields']
    c.need(template['row_definition']==node['values'],'row_definition_mismatch')
    row_types={name:field['type'] for name,field in fields.items() if field['node']=='scalar'}""")
replace("c.need(row_allowed and expr['field'] in template['row_types'],'row_field')\n            return template['row_types'][expr['field']]",
        "c.need(row_allowed and expr['field'] in row_types,'row_field')\n            return row_types[expr['field']]")
replace("c.closed(expr,['expr','prefix'],'operation_id_expression');c.need(row_allowed,'operation_id_scope');c.base.text(expr['prefix'],'operation_prefix');return c.TEXT",
        "c.closed(expr,['expr','prefix'],'operation_id_expression');c.base.text(expr['prefix'],'operation_prefix');return c.TEXT")
start=text.index('    def validate_operation(');end=text.index('    for expr in template[',start)
old=text[start:end]
new='''    def validate_operation(expr,row_allowed):
        inferred=infer(expr,row_allowed)
        c.need(set(inferred)=={'record'} and set(inferred['record'])=={'id','op','path','value'},'operation_expression_shape')
        operation=expr['fields'];shape=inferred['record']
        c.need(shape['id']==shape['op']==c.TEXT,'operation_expression_type')
        op_expr=operation['op']
        c.need(op_expr.get('expr')=='literal' and op_expr.get('type')==c.TEXT and op_expr.get('value') in ('replace','insert'),'declared_write_operation')
        op=op_expr['value'];tokens=operation['path']['items']
        c.need(set(shape['path'])=={'array'} and all(t==c.TEXT for t in shape['path']['array']),'operation_path_type')
        c.need(bool(tokens),'nonempty_write_path')
        current=memory_definition['root'];parent=None
        if row_allowed:
            c.need(len(tokens)>len(parts)+1,'row_write_path')
            for token,part in zip(tokens,parts):
                c.need(token=={'expr':'literal','type':c.TEXT,'value':part},'row_write_prefix')
            c.need(tokens[len(parts)]=={'expr':'key'},'row_write_key')
        for token in tokens:
            parent=current
            if current['node']=='record':
                c.need(token.get('expr')=='literal' and token.get('type')==c.TEXT and token.get('value') in current['fields'],'record_write_field')
                current=current['fields'][token['value']]
            elif current['node']=='map':
                c.need(infer(token,row_allowed)==c.TEXT,'map_key_text_type');current=current['values']
            else:raise c.Refusal('invalid','scalar_write_parent')
        c.need(parent['node']=='map' if op=='insert' else current['node']=='scalar','write_target_kind')
        def check_value(value,target):
            c.need(value.get('expr')=='object','memory_template_object')
            fields=value['fields'];kind=fields.get('kind',{})
            if target['node']=='scalar':
                c.need(set(fields)=={'kind','value'} and kind=={'expr':'literal','type':c.TEXT,'value':'literal'},'scalar_template_shape')
                c.need(infer(fields['value'],row_allowed)==target['type'],'write_value_type')
            else:
                c.need(set(fields)=={'kind','fields'} and kind=={'expr':'literal','type':c.TEXT,'value':'object'},'record_template_shape')
                body=fields['fields'];c.need(body.get('expr')=='object','record_template_fields')
                body=body['fields']
                if target['node']=='record':
                    c.need(set(body)==set(target['fields']),'complete_record_fields')
                    for name,item in body.items():check_value(item,target['fields'][name])
                else:
                    c.need(len(body)<=target['max_items'],'memory_map_capacity')
                    for name,item in body.items():
                        c.base.text(name,'map_key');check_value(item,target['values'])
        check_value(operation['value'],current)
'''
replace(old,new)
replace("row=population[key];c.need(type(row) is dict and set(row)==set(template['row_types']),'row_population')\n        for name,typ in template['row_types'].items():",
        "row=population[key];c.need(type(row) is dict and set(row)==set(fields),'row_population')\n        for name,typ in row_types.items():")
replace("evaluate(expr,None,None,None)","evaluate(expr,None,None,len(operations))")
target.write_text(text)
(HERE/'successor-diff.json').write_text(json.dumps(dict(source=str(source),source_sha256=sha256(source.read_bytes()).hexdigest(),
    target_sha256=sha256(target.read_bytes()).hexdigest(),edits=edits),indent=2)+chr(10))
print(json.dumps(dict(created=str(target),edits=len(edits))))
