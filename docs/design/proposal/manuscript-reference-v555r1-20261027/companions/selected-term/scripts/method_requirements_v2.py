"""Dimensional products lowered to the unchanged v1 requirement semantics."""
from copy import deepcopy
from fractions import Fraction
import re
import method_requirements_v1 as v1

PROFILE='MethodRequirements/2'
PRIVATE='@product/'
RESERVED={'@dimensions','@scale'}
UNIT_KEYS={'unit','units','currency','scale'}


def typed(t):
    v1.need(type(t) is dict,'type')
    if t.get('kind')!='rational':
        v1.typed(t)
    else:
        v1.closed(t,['kind','context','dimensions','scale'],'dimensional_type')
        v1.typed({'kind':'rational','context':t['context']})
        v1.need(not (set(t['context']) & UNIT_KEYS),'unit_must_be_explicit_dimension')
        d=t['dimensions']
        v1.need(type(d) is dict and len(d)<=32,'dimensions')
        for key,power in d.items():
            v1.text(key,'dimension_name')
            v1.need(type(power) is int and power!=0 and abs(power)<=32,'dimension_exponent')
        v1.need(v1.scalar(t['scale'],'rational')>0,'positive_scale')
    v1.need(not (set(t['context']) & RESERVED),'reserved_context_key')
    return t


def encoded(t):
    typed(t)
    if t['kind']!='rational':
        return deepcopy(t)
    return {'kind':'rational','context':{**t['context'],
        '@dimensions':v1.canonical(t['dimensions']).decode(), '@scale':t['scale']}}


def product_type(a,b):
    v1.need(a['kind']==b['kind']=='rational','product_numeric_type')
    v1.need(a['context']==b['context'],'product_context_mismatch')
    dims={key:a['dimensions'].get(key,0)+b['dimensions'].get(key,0)
          for key in set(a['dimensions'])|set(b['dimensions'])}
    dims={key:power for key,power in dims.items() if power}
    scale=Fraction(a['scale'])*Fraction(b['scale'])
    result={'kind':'rational','context':deepcopy(a['context']),'dimensions':dims,
            'scale':f'{scale.numerator}/{scale.denominator}'}
    return typed(result)


def compile_manifest(manifest):
    v1.need(len(v1.canonical(manifest))<=v1.MAX_BYTES,'manifest_size_limit')
    v1.closed(manifest,['profile','method_id','version','inputs','requirements',
                       'capabilities','residual_prerequisites'],'manifest')
    v1.need(manifest['profile']==PROFILE,'profile')
    v1.need(type(manifest['inputs']) is dict,'inputs')
    lowered=deepcopy(manifest)
    lowered['profile']=v1.PROFILE
    for key,declaration in manifest['inputs'].items():
        v1.text(key,'input_id')
        v1.need(not key.startswith(PRIVATE),'reserved_input_identity')
        v1.closed(declaration,['type','role','source_ref'],'input_declaration')
        lowered['inputs'][key]['type']=encoded(declaration['type'])
    original_inputs=deepcopy(lowered['inputs'])
    products={}
    counter=[0]

    def walk(node,depth=0):
        counter[0]+=1
        v1.need(counter[0]<=v1.MAX_NODES and depth<=v1.MAX_DEPTH,'expression_limit')
        v1.need(type(node) is dict and type(node.get('op')) is str,'expression')
        op=node['op']
        if op=='ref':
            v1.closed(node,['op','id'],'ref')
            v1.text(node['id'],'input_id')
            v1.need(node['id'] in manifest['inputs'],'undeclared_input')
            return manifest['inputs'][node['id']]['type'],{node['id']},deepcopy(node)
        if op=='const':
            v1.closed(node,['op','type','value'],'const')
            t=typed(node['type'])
            v1.scalar(node['value'],t['kind'])
            return t,set(),{'op':'const','type':encoded(t),'value':node['value']}
        if op in ['eq','le','lt','add','sub','mul']:
            v1.closed(node,['op','left','right'],op)
            a,ar,al=walk(node['left'],depth+1)
            b,br,bl=walk(node['right'],depth+1)
            if op=='mul':
                t=product_type(a,b)
                key=PRIVATE+str(len(products))
                products[key]={'expression':deepcopy(node),'type':deepcopy(t),'dependencies':sorted(ar|br)}
                lowered['inputs'][key]={'type':encoded(t),'role':'state',
                                        'source_ref':'derived-product:'+v1.digest(node)}
                return t,ar|br,{'op':'ref','id':key}
            v1.need(a==b,'type_or_context_mismatch')
            if op in ['add','sub']:
                v1.need(a['kind']=='rational','numeric_type')
            if op in ['le','lt']:
                v1.need(a['kind'] in ['rational','date'],'ordered_type')
            t=a if op in ['add','sub'] else v1.BOOL
            return t,ar|br,{'op':op,'left':al,'right':bl}
        if op in ['all','any']:
            v1.closed(node,['op','args'],op)
            v1.need(type(node['args']) is list and bool(node['args']),'nonempty_args')
            args,refs=[],set()
            for child in node['args']:
                t,r,lower=walk(child,depth+1)
                v1.need(t['kind']=='boolean','boolean_operand')
                args.append(lower)
                refs|=r
            return v1.BOOL,refs,{'op':op,'args':args}
        if op=='not':
            v1.closed(node,['op','arg'],op)
            t,refs,lower=walk(node['arg'],depth+1)
            v1.need(t['kind']=='boolean','boolean_operand')
            return v1.BOOL,refs,{'op':op,'arg':lower}
        raise v1.Invalid('unsupported_operator:'+op)

    v1.need(type(manifest['requirements']) is list and bool(manifest['requirements']),'requirements')
    used=set()
    lower_used=set()
    for req,new in zip(manifest['requirements'],lowered['requirements']):
        v1.closed(req,['id','predicate','requires','admission_refs','on_false','on_unknown'],'requirement')
        t,refs,predicate=walk(req['predicate'])
        v1.need(t['kind']=='boolean','predicate_boolean_required')
        v1.identifiers(req['requires'],'requires')
        v1.need(set(req['requires'])==refs,'inexact_dependency_declaration')
        used|=refs
        _,internal=v1.expression(predicate,lowered['inputs'])
        lower_used|=internal
        new['predicate']=predicate
        new['requires']=sorted(internal)
    v1.need(used==set(manifest['inputs']),'unused_input_declaration')
    # Validate all original declarations, even if they appear only inside products.
    for key,declaration in original_inputs.items():
        v1.need(type(declaration['role']) is str and declaration['role'] in v1.ROLES,'role')
        v1.need(declaration['role']!='caller_finding' or declaration['type']['kind']=='boolean',
                'finding_boolean_required')
        v1.text(declaration['source_ref'],'source_ref')
    lowered['inputs']={key:declaration for key,declaration in lowered['inputs'].items() if key in lower_used}
    v1.validate_manifest(lowered)
    return lowered,products,original_inputs


def numeric(node,manifest,values):
    op=node['op']
    if op=='ref':
        key=node['id']
        item=values.get(key,{'status':'unknown','reason':'missing_input'})
        if item['status']=='unknown':
            return None,{key:item['reason']}
        return v1.scalar(item['value'],'rational'),{}
    if op=='const':
        return v1.scalar(node['value'],'rational'),{}
    a,ad=numeric(node['left'],manifest,values)
    b,bd=numeric(node['right'],manifest,values)
    missing={**ad,**bd}
    if missing:
        return None,missing
    if op=='mul':
        return a*b,{}
    if op=='add':
        return a+b,{}
    if op=='sub':
        return a-b,{}
    raise v1.Invalid('non_numeric_product_operand')


def assess(registry,selected_digest,values,available_capabilities):
    boundary={'executed':False,'source_admission':False,'accounting_admission':False,
              'method_eligible':False,'scope':'selected_requirements_only'}
    try:
        v1.need(type(registry) is dict,'registry')
        v1.need(type(selected_digest) is str and re.fullmatch('[0-9a-f]{64}',selected_digest) is not None,'selection_digest')
        v1.identifiers(available_capabilities,'available_capabilities')
        if selected_digest not in registry:
            return {**boundary,'status':'unsupported','reason':'definition_unavailable','selected_digest':selected_digest}
        manifest=registry[selected_digest]
        v1.need(v1.digest(manifest)==selected_digest,'definition_digest_mismatch')
        lowered,products,original=compile_manifest(manifest)
        v1.validate_values({'inputs':original},values)
        bound={key:deepcopy(value) for key,value in values.items() if key in lowered['inputs']}
        computed={}
        for key,product in products.items():
            value,missing=numeric(product['expression'],manifest,values)
            binding=({'status':'unknown','reason':'product_operand_unresolved'} if missing else
                     {'status':'known','value':f'{value.numerator}/{value.denominator}'})
            computed[key]={**deepcopy(product),'binding':binding,'unresolved_inputs':missing,
                           'meaning':'exact derived coefficient; not an independently admitted source'}
            if key in lowered['inputs']:
                bound[key]=binding
        lower_digest=v1.digest(lowered)
        answer=v1.assess({lower_digest:lowered},lower_digest,bound,available_capabilities)
        if 'findings' not in answer:
            raise v1.Invalid('lowered_assessment_failed:'+answer.get('reason',answer['status']))
        for row,req in zip(answer['findings'],manifest['requirements']):
            row['dependencies']=sorted(req['requires'])
            row['unresolved_inputs']={key:values.get(key,{'reason':'missing_input'})['reason']
                for key in req['requires'] if values.get(key,{}).get('status')!='known'}
        answer.update(profile=PROFILE,selected_digest=selected_digest,values_sha256=v1.digest(values),
                      input_declarations=deepcopy(manifest['inputs']),products=computed,
                      lowering_manifest_sha256=lower_digest,lowering_semantics=v1.PROFILE)
        return answer
    except (ValueError,TypeError,KeyError,RecursionError,OverflowError) as exc:
        return {**boundary,'status':'invalid','reason':str(exc)[:250]}
