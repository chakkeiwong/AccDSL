"""Explicit guard activation; no execution or full-method admission is inferred."""
from copy import deepcopy
import re
import method_requirements_v1 as v1
import method_requirements_v2 as v2

PROFILE='MethodRequirements/3'


def compile_manifest(manifest):
    v1.need(len(v1.canonical(manifest))<=v1.MAX_BYTES,'manifest_size_limit')
    v1.closed(manifest,['profile','method_id','version','inputs','requirements','required_known',
                       'capabilities','residual_prerequisites'],'guarded_manifest')
    v1.need(manifest['profile']==PROFILE,'profile')
    v1.need(type(manifest['inputs']) is dict,'inputs')
    v1.identifiers(manifest['required_known'],'required_known')
    v1.need(set(manifest['required_known'])<=set(manifest['inputs']),'undeclared_required_known')
    v1.need(type(manifest['requirements']) is list and bool(manifest['requirements']),'requirements')
    lowered={k:deepcopy(value) for k,value in manifest.items() if k!='required_known'}
    lowered['profile']=v2.PROFILE
    lowered['requirements']=[]
    seen=set()
    for i,req in enumerate(manifest['requirements']):
        v1.closed(req,['id','guard','guard_requires','predicate','requires','admission_refs',
                       'on_false','on_unknown'],'guarded_requirement')
        v1.text(req['id'],'requirement_id')
        v1.need(req['id'] not in seen,'duplicate_requirement')
        seen.add(req['id'])
        for suffix,field,deps in [('guard','guard','guard_requires'),('body','predicate','requires')]:
            lowered['requirements'].append({'id':str(i)+'.'+suffix,'predicate':deepcopy(req[field]),
                'requires':deepcopy(req[deps]),'admission_refs':deepcopy(req['admission_refs']),
                'on_false':req['on_false'],'on_unknown':req['on_unknown']})
    for key in manifest['required_known']:
        lowered['requirements'].append({'id':'known.'+key,
            'predicate':{'op':'eq','left':{'op':'ref','id':key},'right':{'op':'ref','id':key}},
            'requires':[key],'admission_refs':[],'on_false':'invalid','on_unknown':'unresolved'})
    v2.compile_manifest(lowered)
    return lowered


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
        lowered=compile_manifest(manifest)
        key=v1.digest(lowered)
        result=v2.assess({key:lowered},key,values,available_capabilities)
        if 'findings' not in result:
            raise v1.Invalid('lowered_assessment_failed:'+result.get('reason',result['status']))
        found={r['id']:r for r in result['findings']}
        findings=[]
        consequences=['unsupported'] if result['missing_capabilities'] else []
        for i,req in enumerate(manifest['requirements']):
            guard,body=found[str(i)+'.guard'],found[str(i)+'.body']
            if guard['truth']=='false':
                consequence='not_applicable'
                activation='inactive'
            elif guard['truth']=='unknown':
                consequence='unresolved'
                activation='unknown'
            else:
                consequence=body['consequence']
                activation='active'
            consequences.append(consequence)
            findings.append({'id':req['id'],'activation':activation,'guard_truth':guard['truth'],
                'body_truth':body['truth'],'consequence':consequence,
                'guard_dependencies':guard['dependencies'],'body_dependencies':body['dependencies'],
                'dependencies':sorted(set(guard['dependencies'])|set(body['dependencies'])),
                'unresolved_inputs':{**guard['unresolved_inputs'],**body['unresolved_inputs']},
                'admission_refs':deepcopy(req['admission_refs'])})
        known=[]
        for key in manifest['required_known']:
            item=values.get(key,{'status':'unknown','reason':'missing_input'})
            consequence='satisfied' if item['status']=='known' else 'unresolved'
            consequences.append(consequence)
            known.append({'input':key,'consequence':consequence,
                          'reason':None if item['status']=='known' else item['reason']})
        success='requirements_satisfied' if any(f['activation']=='active' for f in findings) else 'no_active_requirements'
        status=next((s for s in ['invalid','unsupported','unresolved'] if s in consequences),success)
        return {**boundary,'profile':PROFILE,'status':status,'selected_digest':selected_digest,
                'method_id':manifest['method_id'],'version':manifest['version'],'values_sha256':v1.digest(values),
                'findings':findings,'required_known_findings':known,
                'missing_capabilities':result['missing_capabilities'],
                'input_declarations':deepcopy(manifest['inputs']),
                'residual_prerequisites':deepcopy(manifest['residual_prerequisites']),
                'products':result['products'],'lowering_manifest_sha256':v1.digest(lowered),
                'lowering_semantics':v2.PROFILE}
    except (ValueError,TypeError,KeyError,RecursionError,OverflowError) as exc:
        return {**boundary,'status':'invalid','reason':str(exc)[:250]}
