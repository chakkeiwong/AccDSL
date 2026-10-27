"""Finite supplied collection prerequisites; no accounting state is executed."""
from copy import deepcopy
import method_requirements_v1 as core
import method_requirements_v2 as dimensions
import method_requirements_v3 as guarded

PROFILE='MethodCollections/1'
MAX_ROWS=256
MAX_CONSTRAINTS=128
MAX_EXPANDED_NODES=65536
BOUNDARY={'executed':False,'method_eligible':False,'source_admission':False,
          'accounting_admission':False,'scope':'selected_collection_requirements_only'}


def declarations(inputs):
    core.need(type(inputs) is dict,'input_declarations')
    for key,item in inputs.items():
        core.text(key,'field_name')
        core.closed(item,['type','role','source_ref'],'field_declaration')
        dimensions.typed(item['type'])
        core.need(type(item['role']) is str and item['role'] in core.ROLES,'field_role')
        core.need(item['role']!='caller_finding' or item['type']['kind']=='boolean','finding_boolean')
        core.text(item['source_ref'],'field_source_ref')


def node_count(value):
    if type(value) is dict:
        return 1+sum(node_count(item) for item in value.values())
    if type(value) is list:
        return 1+sum(node_count(item) for item in value)
    return 1


def validate(definition):
    core.need(len(core.canonical(definition))<=core.MAX_BYTES,'definition_size_limit')
    core.closed(definition,['profile','method_id','version','inputs','collections',
                           'constraints','residual_prerequisites'],'collection_definition')
    core.need(definition['profile']==PROFILE,'collection_profile')
    for key in ['method_id','version']:
        core.text(definition[key],key)
    declarations(definition['inputs'])
    core.need(type(definition['collections']) is dict,'collections')
    for name,collection in definition['collections'].items():
        core.text(name,'collection_name')
        core.closed(collection,['fields'],'collection_declaration')
        declarations(collection['fields'])
        core.need(bool(collection['fields']),'empty_collection_fields')
    rules=definition['constraints']
    core.need(type(rules) is list and 0<len(rules)<=MAX_CONSTRAINTS,'constraint_limit')
    seen=set()
    def field(collection,key):
        core.text(collection,'collection_name')
        core.text(key,'field_name')
        core.need(collection in definition['collections'],'undeclared_collection')
        fields=definition['collections'][collection]['fields']
        core.need(key in fields,'undeclared_field')
        return fields[key]
    for rule in rules:
        core.need(type(rule) is dict,'constraint')
        core.text(rule.get('id'),'constraint_id')
        core.need(rule['id'] not in seen,'duplicate_constraint')
        seen.add(rule['id'])
        op=rule.get('op')
        if op in ['unique','ordered']:
            core.closed(rule,['id','op','collection','field'],'field_constraint')
            t=field(rule['collection'],rule['field'])['type']
            if op=='ordered':
                core.need(t['kind'] in ['date','rational'],'ordered_field_type')
        elif op=='references':
            core.closed(rule,['id','op','source','field','target','target_field'],'reference_constraint')
            a=field(rule['source'],rule['field'])
            b=field(rule['target'],rule['target_field'])
            core.need(a['type']==b['type'],'reference_type_or_context_mismatch')
        elif op=='each':
            core.closed(rule,['id','op','collection','definition','bindings'],'each_constraint')
            core.need(type(rule['collection']) is str and rule['collection'] in definition['collections'],
                      'undeclared_collection')
            guarded.compile_manifest(rule['definition'])
            core.need(type(rule['bindings']) is dict and set(rule['bindings'])==set(rule['definition']['inputs']),
                      'inexact_template_binding')
            for key,binding in rule['bindings'].items():
                core.closed(binding,['scope','field'],'template_binding')
                core.text(binding['field'],'binding_field')
                if binding['scope']=='row':
                    declaration=field(rule['collection'],binding['field'])
                else:
                    core.need(binding['scope']=='global','binding_scope')
                    core.need(binding['field'] in definition['inputs'],'undeclared_global')
                    declaration=definition['inputs'][binding['field']]
                expected=rule['definition']['inputs'][key]
                core.need(declaration['type']==expected['type'] and declaration['role']==expected['role'],
                          'template_type_or_role_mismatch')
        else:
            raise core.Invalid('unsupported_collection_operator')
    core.identifiers(definition['residual_prerequisites'],'residual_prerequisites',True)
    return definition


def validate_values(definition,values):
    core.need(len(core.canonical(values))<=core.MAX_BYTES,'values_size_limit')
    core.closed(values,['globals','collections'],'collection_values')
    core.validate_values({'inputs':definition['inputs']},values['globals'])
    core.need(type(values['collections']) is dict,'collection_bindings')
    core.need(set(values['collections'])<=set(definition['collections']),'extra_collection')
    count=0
    for name,collection in values['collections'].items():
        core.need(type(collection) is dict,'collection_value')
        status=collection.get('status')
        if status=='complete':
            core.closed(collection,['status','rows'],'complete_collection')
        else:
            core.need(status=='partial','collection_status')
            core.closed(collection,['status','rows','reason'],'partial_collection')
            core.text(collection['reason'],'partial_reason')
        core.need(type(collection['rows']) is list,'collection_rows')
        count+=len(collection['rows'])
        core.need(count<=MAX_ROWS,'row_limit')
        for row in collection['rows']:
            core.validate_values({'inputs':definition['collections'][name]['fields']},row)
    return values


def assess(definition,values,available_capabilities):
    try:
        validate(definition)
        validate_values(definition,values)
        core.identifiers(available_capabilities,'available_capabilities')
        collections={name:values['collections'].get(name,
                     {'status':'partial','rows':[],'reason':'missing_collection'})
                     for name in definition['collections']}
        work=sum(node_count(r['definition'])*len(collections[r['collection']]['rows'])
                 for r in definition['constraints'] if r['op']=='each')
        core.need(work<=MAX_EXPANDED_NODES,'expanded_work_limit')
        findings=[]
        def projection(name,key):
            collection=collections[name]
            observed,missing=[],{}
            kind=definition['collections'][name]['fields'][key]['type']['kind']
            for index,row in enumerate(collection['rows']):
                value=row.get(key,{'status':'unknown','reason':'missing_row_field'})
                path=name+'/'+str(index)+'/'+key
                if value['status']=='known':
                    observed.append((index,core.scalar(value['value'],kind)))
                else:
                    missing[path]=value['reason']
            if collection['status']=='partial':
                missing[name]=collection['reason']
            return observed,missing
        for rule in definition['constraints']:
            op=rule['op']
            missing,details={},[]
            if op in ['unique','ordered']:
                observed,missing=projection(rule['collection'],rule['field'])
                if op=='unique':
                    first={}
                    for index,value in observed:
                        if value in first:
                            details.append({'rows':[first[value],index],'reason':'duplicate_known_key'})
                        else:
                            first[value]=index
                else:
                    for (i,a),(j,b) in zip(observed,observed[1:]):
                        if a>b:
                            details.append({'rows':[i,j],'reason':'known_order_reversal'})
                consequence='invalid' if details else 'unresolved' if missing else 'satisfied'
            elif op=='references':
                sources,source_missing=projection(rule['source'],rule['field'])
                targets,target_missing=projection(rule['target'],rule['target_field'])
                missing.update(source_missing)
                for index,value in sources:
                    matches=[j for j,v in targets if v==value]
                    if len(matches)>1 or (not matches and not target_missing):
                        details.append({'source_row':index,'target_rows':matches,'reason':'reference_not_unique'})
                    elif target_missing:
                        missing.update(target_missing)
                # Unknown source values require target information as well; an empty
                # complete source collection imposes no target existence obligation.
                if source_missing:
                    missing.update(target_missing)
                consequence='invalid' if details else 'unresolved' if missing else 'satisfied'
            else:
                collection=collections[rule['collection']]
                statuses=[]
                for index,row in enumerate(collection['rows']):
                    bound,lineage={},{}
                    for key,binding in rule['bindings'].items():
                        global_input=binding['scope']=='global'
                        source=values['globals'] if global_input else row
                        field=binding['field']
                        item=source.get(field,{'status':'unknown','reason':
                            'missing_global_input' if global_input else 'missing_row_field'})
                        bound[key]=deepcopy(item)
                        lineage[key]={'scope':binding['scope'],'field':field,
                                      'collection':None if global_input else rule['collection'],
                                      'row':None if global_input else index}
                        if item['status']=='unknown':
                            missing[('global' if global_input else rule['collection']+'/'+str(index))+'/'+field]=item['reason']
                    d=rule['definition'];h=core.digest(d)
                    result=guarded.assess({h:d},h,bound,available_capabilities)
                    core.need('findings' in result,'row_evaluation_invalid:'+result.get('reason',''))
                    statuses.append(result['status'])
                    details.append({'row':index,'bindings':lineage,'assessment':result})
                if collection['status']=='partial':
                    statuses.append('unresolved')
                    missing[rule['collection']]=collection['reason']
                consequence=next((s for s in ['invalid','unsupported','unresolved'] if s in statuses),'satisfied')
            findings.append({'id':rule['id'],'operator':op,'consequence':consequence,
                             'unresolved_inputs':missing,'details':details})
        status=next((s for s in ['invalid','unsupported','unresolved']
                     if any(f['consequence']==s for f in findings)),'collection_requirements_satisfied')
        return {**BOUNDARY,'profile':PROFILE,'status':status,'definition_sha256':core.digest(definition),
                'values_sha256':core.digest(values),'findings':findings,
                'input_declarations':deepcopy(definition['inputs']),
                'collection_declarations':deepcopy(definition['collections']),
                'residual_prerequisites':deepcopy(definition['residual_prerequisites']),
                'expanded_template_nodes':work}
    except (ValueError,TypeError,KeyError,RecursionError,OverflowError) as exc:
        return {**BOUNDARY,'status':'invalid','reason':str(exc)[:250]}
