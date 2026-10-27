"""Exact totals over explicit complete collections, assessed by preserved v3."""
from copy import deepcopy
from fractions import Fraction
import method_requirements_v1 as core
import method_requirements_v3 as guarded
import method_collections_v1 as snapshot

PROFILE='MethodCollectionTotals/1'
MAX_SUM_VISITS=8192
BOUNDARY={**snapshot.BOUNDARY,'scope':'selected_collection_totals_only'}


def validate(definition):
    core.need(len(core.canonical(definition))<=core.MAX_BYTES,'definition_size_limit')
    core.closed(definition,['profile','method_id','version','snapshot','assessment','bindings',
                           'residual_prerequisites'],'total_definition')
    core.need(definition['profile']==PROFILE,'totals_profile')
    for key in ['method_id','version']:core.text(definition[key],key)
    snapshot.validate(definition['snapshot'])
    guarded.compile_manifest(definition['assessment'])
    bindings=definition['bindings'];inputs=definition['assessment']['inputs']
    core.need(type(bindings) is dict and set(bindings)==set(inputs),'inexact_total_bindings')
    for key,binding in bindings.items():
        core.need(type(binding) is dict,'total_binding')
        kind=binding.get('kind')
        if kind=='global':
            core.closed(binding,['kind','input'],'global_total_binding')
            core.text(binding['input'],'global_input')
            core.need(binding['input'] in definition['snapshot']['inputs'],'undeclared_global')
            declaration=definition['snapshot']['inputs'][binding['input']]
        else:
            core.need(kind=='sum','total_binding_kind')
            core.closed(binding,['kind','collection','field'],'sum_binding')
            core.text(binding['collection'],'sum_collection');core.text(binding['field'],'sum_field')
            collections=definition['snapshot']['collections']
            core.need(binding['collection'] in collections,'undeclared_collection')
            fields=collections[binding['collection']]['fields']
            core.need(binding['field'] in fields,'undeclared_sum_field')
            declaration=fields[binding['field']]
            core.need(declaration['type']['kind']=='rational','sum_rational_required')
        expected=inputs[key]
        core.need(declaration['type']==expected['type'] and declaration['role']==expected['role'],
                  'total_type_or_role_mismatch')
    core.identifiers(definition['residual_prerequisites'],'residual_prerequisites',True)
    return definition


def assess(definition,values,available_capabilities):
    try:
        validate(definition)
        snapshot.validate_values(definition['snapshot'],values)
        base=snapshot.assess(definition['snapshot'],values,available_capabilities)
        core.need('findings' in base,'snapshot_structure_invalid:'+base.get('reason',''))
        visits=sum(len(values['collections'].get(b['collection'],{}).get('rows',[]))
                   for b in definition['bindings'].values() if b['kind']=='sum')
        core.need(visits<=MAX_SUM_VISITS,'sum_work_limit')
        bound,lineage={},{}
        for key,binding in definition['bindings'].items():
            if binding['kind']=='global':
                value=values['globals'].get(binding['input'],{'status':'unknown','reason':'missing_global_input'})
                bound[key]=deepcopy(value)
                lineage[key]={**deepcopy(binding),'value':deepcopy(value)}
                continue
            name,field=binding['collection'],binding['field']
            collection=values['collections'].get(name,{'status':'partial','rows':[],'reason':'missing_collection'})
            subtotal=Fraction(0);contributors=[];missing={}
            for i,row in enumerate(collection['rows']):
                value=row.get(field,{'status':'unknown','reason':'missing_row_field'})
                contributors.append({'row':i,'value':deepcopy(value)})
                if value['status']=='known':subtotal+=core.scalar(value['value'],'rational')
                else:missing[name+'/'+str(i)+'/'+field]=value['reason']
            if collection['status']=='partial':missing[name]=collection['reason']
            coefficient=f'{subtotal.numerator}/{subtotal.denominator}'
            bound[key]=({'status':'unknown','reason':'collection_total_unresolved'} if missing else
                        {'status':'known','value':coefficient})
            lineage[key]={**deepcopy(binding),'collection_status':collection['status'],
                'contributors':contributors,'unresolved_inputs':missing,'observed_subtotal':coefficient,
                'subtotal_meaning':'diagnostic only when incomplete; not a total binding',
                'type':deepcopy(definition['assessment']['inputs'][key]['type'])}
        d=definition['assessment'];h=core.digest(d)
        result=guarded.assess({h:d},h,bound,available_capabilities)
        core.need('findings' in result,'total_assessment_failed:'+result.get('reason',''))
        status=next((s for s in ['invalid','unsupported','unresolved']
                     if s in [base['status'],result['status']]),'collection_total_requirements_satisfied')
        return {**BOUNDARY,'profile':PROFILE,'status':status,'definition_sha256':core.digest(definition),
            'values_sha256':core.digest(values),'snapshot_assessment':base,'assessment':result,
            'bound_values':bound,'lineage':lineage,'sum_visits':visits,
            'residual_prerequisites':deepcopy(definition['residual_prerequisites'])}
    except (ValueError,TypeError,KeyError,RecursionError,OverflowError) as exc:
        return {**BOUNDARY,'status':'invalid','reason':str(exc)[:250]}
