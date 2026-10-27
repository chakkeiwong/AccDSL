"""Create protected successors for nested eligibility and full composition."""
from pathlib import Path
from hashlib import sha256
import json
HERE=Path(__file__).resolve().parent
source=HERE.parent/'ordered-event-eligibility-20261026/gate.py'
target=HERE/'nested_gate.py';assert not target.exists()
text=source.read_text();edits=[]
def replace(old,new):
    global text
    assert text.count(old)==1,old[:100]
    text=text.replace(old,new);edits.append(dict(before=old,after=new))
replace("PROFILE = 'OrderedEventEligibility/1'","PROFILE = 'OrderedNestedEventEligibility/1'")
replace("CALL = 'OrderedEligibilityCall/1'","CALL = 'OrderedNestedEligibilityCall/1'")
marker="        if kind == 'calendar_adjacent':"
addition='''        if kind == 'text_nonblank':
            c.closed(source,['kind','value'],'text_nonblank_source')
            c.need(infer(source['value'],depth+1)==TEXT,'text_nonblank_type');return BOOL
        if kind in ('nested_map_contains','nested_map_field'):
            keys=['kind','pointer','key_input','parent_after_stage','child_pointer','child_key_input']
            if kind=='nested_map_field':keys+=['field','after_stage']
            c.closed(source,keys,'nested_map_source')
            c.need(template['input_types'].get(source['key_input'])==TEXT and template['input_types'].get(source['child_key_input'])==TEXT,'nested_key_type')
            c.need(proofs.get(source['parent_after_stage'])==(source['pointer'],source['key_input']),'unproved_parent_presence')
            node=schema_node(definition,source['pointer'])
            c.need(node['node']=='map' and node['values']['node']=='record','nested_parent_map')
            child=node['values']
            for part in base.binding.pointer_parts(source['child_pointer']):
                c.need(child['node']=='record' and part in child['fields'],'nested_child_path');child=child['fields'][part]
            c.need(child['node']=='map' and child['values']['node']=='record','nested_child_map')
            if kind=='nested_map_contains':return BOOL
            identity=(source['pointer'],source['key_input'],source['child_pointer'],source['child_key_input'])
            c.need(proofs.get(source['after_stage'])==identity,'unproved_child_presence')
            fields=child['values']['fields']
            c.need(source['field'] in fields and fields[source['field']]['node']=='scalar','nested_scalar_field')
            return fields[source['field']]['type']
'''
replace(marker,addition+marker)
replace("            if source['kind'] == 'map_contains':\n                proofs[name] = (source['pointer'], source['key_input'])",
"""            if source['kind'] == 'map_contains':
                proofs[name] = (source['pointer'], source['key_input'])
            elif source['kind']=='nested_map_contains':
                proofs[name]=(source['pointer'],source['key_input'],source['child_pointer'],source['child_key_input'])""")
marker="    if kind == 'calendar_adjacent':"
addition='''    if kind=='text_nonblank':
        value=resolve(source['value'],book,event)
        if value['status']=='unknown':return value
        try:base.text(value['value'],'nonblank_text');valid=True
        except ValueError:valid=False
        return base.known(valid)
    if kind in ('nested_map_contains','nested_map_field'):
        parent_key=event['inputs'][source['key_input']]['value']
        child_key=event['inputs'][source['child_key_input']]['value']
        if parent_key['status']=='unknown':return deepcopy(parent_key)
        if child_key['status']=='unknown':return deepcopy(child_key)
        found,parents=base.binding.located(book['memory'],source['pointer'])
        c.need(found and parent_key['value'] in parents,'parent_presence_prerequisite_failed')
        found,children=base.binding.located(parents[parent_key['value']],source['child_pointer'])
        c.need(found and type(children) is dict,'nested_map_population')
        if kind=='nested_map_contains':return base.known(child_key['value'] in children)
        c.need(child_key['value'] in children,'child_presence_prerequisite_failed')
        return base.known(deepcopy(children[child_key['value']][source['field']]))
'''
# Restrict to the resolve body; the infer block has an extra indentation level.
offset=text.index('def resolve(');head=text[:offset];tail=text[offset:]
assert tail.count(marker)==1
tail=tail.replace(marker,addition+marker);text=head+tail;edits.append(dict(resolve_addition=addition))
target.write_text(text)
source2=HERE.parent/'term-event-carry-binding-20261026/composition.py'
target2=HERE/'full_composition.py';assert not target2.exists()
text=source2.read_text().replace('import gate','import nested_gate as gate')
text=text.replace("PROFILE='SelectedTermCommand/1'","PROFILE='SelectedTermCommand/2'")
text=text.replace("core.closed(rules,['assessment','carry'],'term_rules')","core.closed(rules,['assessment','amendment','collection','carry'],'term_rules')")
text=text.replace("core.need(request['operation']=='assess','unsupported_term_operation')\n            rule=rules['assessment'];event=request['event'];stage='eligibility'",
"""core.need(request['operation'] in ('assess','amend','collect'),'unsupported_term_operation')
            selected={'assess':'assessment','amend':'amendment','collect':'collection'}[request['operation']]
            rule=rules[selected];core.closed(rule,['eligibility','construction'],'event_rule')
            core.need(rule['eligibility']['operation']==request['operation'],'event_operation_binding')
            event=request['event'];stage='eligibility'""")
text=text.replace("construction=expander.construct(*args,expander.make_call(template,book,event,order));result['construction']=construction\n            typed=construction['construction']['request'];stage='transition'",
"""if request['operation']=='assess':
                construction=expander.construct(*args,expander.make_call(template,book,event,order))
                typed=construction['construction']['request']
            else:
                construction=expander.c.construct(*args,expander.c.make_call(template,book,event))
                typed=construction['request']
            result['construction']=construction;result['typed_request']=typed;stage='transition'""")
text=text.replace('Selected synthetic assessment/carry only; supplied completeness inherited after exact transition',
                  'Selected synthetic term events/carry; supplied completeness inherited after exact transition')
target2.write_text(text)
(HERE/'successor-sources.json').write_text(json.dumps(dict(gate=dict(source=str(source),before=sha256(source.read_bytes()).hexdigest(),after=sha256(target.read_bytes()).hexdigest(),edits=edits),
    composition=dict(source=str(source2),before=sha256(source2.read_bytes()).hexdigest(),after=sha256(target2.read_bytes()).hexdigest())),indent=2)+chr(10))
print(json.dumps(dict(created=[target.name,target2.name])))
