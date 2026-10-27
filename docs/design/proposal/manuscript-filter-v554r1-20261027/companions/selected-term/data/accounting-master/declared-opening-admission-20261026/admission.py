"""Explicit finite opening admission; no lifecycle or operating-builder import."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json,sys

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE.parent/'ordered-event-eligibility-20261026'))
import gate
import company_book_reports_v1 as reports
c=gate.c;core=c.core;base=c.base;typed=c.frontend.v2
PROFILE='DeclaredOpeningAdmission/1'
FLAGS=dict(executed=False,source_admission=False,accounting_admission=False,
           future_commands_validated=False,production_ready=False)

def order_digest(value):
    return sha256(json.dumps(value,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()).hexdigest()

def make_call(template,body):
    return dict(profile=PROFILE,template_sha256=core.digest(template),input_sha256=core.digest(body),
                input_order_sha256=order_digest(body))

def path_valid(path):
    c.need(type(path) is list and len(path)<=core.MAX_DEPTH,'source_path')
    for x in path:base.text(x,'path_segment')

def at(body,path):
    value=body
    for key in path:value=value[key]
    return value

def source_type(source):
    c.need(type(source) is dict,'source_record');kind=source.get('kind')
    if kind=='path':c.closed(source,['kind','path','type'],'path_source');path_valid(source['path'])
    elif kind=='role_balance':c.closed(source,['kind','role','type'],'balance_source');base.text(source['role'],'role')
    elif kind=='memory_pointer':c.closed(source,['kind','type'],'memory_pointer_source')
    else:raise c.Refusal('invalid','unsupported_binding_source')
    base.dimensions.typed(source['type']);return source['type']

def bind(body,source):
    if source['kind']=='path':value=at(body,source['path'])
    elif source['kind']=='role_balance':value=body['opening']['balances'][body['roles'][source['role']]]
    else:
        found,value=base.binding.located(body['opening']['memory'],body['unit_cost_pointer'])
        c.need(found,'unit_cost_leaf')
    core.scalar(value,source['type']['kind']);return base.known(deepcopy(value))

def compile_template(template):
    base.memory.bounded(template);c.exact(template)
    c.closed(template,['profile','context','dependency_pins','stages','residuals'],'opening_template_fields')
    c.need(template['profile']==PROFILE,'opening_profile');c.need(type(template['context']) is dict,'template_context')
    core.identifiers(template['residuals'],'residuals',True)
    c.need(type(template['dependency_pins']) is list and bool(template['dependency_pins']),'dependency_pins')
    names=set()
    for pin in template['dependency_pins']:
        c.closed(pin,['file','sha256','reason'],'dependency_fields');base.text(pin['file'],'dependency_file')
        c.need(Path(pin['file']).name==pin['file'] and pin['file'] not in names,'dependency_name')
        c.need(type(pin['sha256']) is str and len(pin['sha256'])==64 and all(x in '0123456789abcdef' for x in pin['sha256']),'dependency_digest')
        base.text(pin['reason'],'dependency_reason');names.add(pin['file'])
    c.need(type(template['stages']) is list and 0<len(template['stages'])<=64,'stage_population')
    seen=set()
    extras={'record_fields':['path','fields'],'record_values':['path','values'],'text':['path','label'],'equals':['path','value'],
            'typed_book':[],'map_values':['path','values'],'role_population':['roles'],
            'role_injective':[],'role_classes':['classes'],'cash_role':['role'],
            'memory_leaf':[],'memory_type':['type'],'predicate':['manifest','bindings'],
            'opening_report':[],'commands':['maximum']}
    for stage in template['stages']:
        c.need(type(stage) is dict,'stage_record');op=stage.get('op');c.need(op in extras,'unsupported_stage')
        c.closed(stage,['id','op','reason']+extras[op],'stage_fields')
        base.text(stage['id'],'stage_id');base.text(stage['reason'],'stage_reason')
        c.need(stage['id'] not in seen,'duplicate_stage');seen.add(stage['id'])
        if 'path' in stage:path_valid(stage['path'])
        if op=='record_fields':core.identifiers(stage['fields'],'record_fields',True)
        elif op=='record_values':
            c.need(type(stage['values']) is dict and bool(stage['values']),'record_values')
            for k,v in stage['values'].items():base.text(k,'record_key');c.exact(v)
        elif op=='text':base.text(stage['label'],'text_label')
        elif op=='equals':c.exact(stage['value'])
        elif op=='map_values':
            typed.types.compile_schema({'profile':typed.types.PROFILE,'root':{'node':'record','fields':{'row':stage['values']}}},dict(context=template['context']))
        elif op=='role_population':core.identifiers(stage['roles'],'role_population',True)
        elif op=='role_classes':
            c.need(type(stage['classes']) is list and bool(stage['classes']),'role_classes');roles=set()
            for row in stage['classes']:
                c.closed(row,['role','classification'],'role_class');base.text(row['role'],'role')
                c.need(row['role'] not in roles,'duplicate_role_class');roles.add(row['role'])
                c.need(row['classification'] in ('asset','liability','equity','income','expense'),'account_class')
        elif op=='cash_role':base.text(stage['role'],'cash_role')
        elif op=='memory_type':base.dimensions.typed(stage['type'])
        elif op=='predicate':
            manifest=stage['manifest'];gate.guarded.compile_manifest(manifest)
            c.need(len(manifest['requirements'])==1,'one_opening_predicate')
            req=manifest['requirements'][0]
            c.need(req['guard']=={'op':'const','type':core.BOOL,'value':True},'unconditional_opening_predicate')
            c.need(type(stage['bindings']) is dict and set(stage['bindings'])==set(manifest['inputs']),'exact_bindings')
            for name,source in stage['bindings'].items():
                typ=source_type(source)
                c.need(manifest['inputs'][name]['type']==typ,'binding_type_mismatch')
                c.need(manifest['inputs'][name]['role']=='state','binding_state_role')
        elif op=='commands':c.need(type(stage['maximum']) is int and 0<stage['maximum']<=64,'command_maximum')
    return template

def assess(template,body,call):
    result=dict(profile=PROFILE,**FLAGS);trace=[];stage_id='selection'
    try:
        c.closed(call,['profile','template_sha256','input_sha256','input_order_sha256'],'call_fields')
        c.need(call['profile']==PROFILE,'call_profile')
        c.need(call['template_sha256']==core.digest(template),'stale_template')
        c.need(call['input_sha256']==core.digest(body),'stale_input')
        c.need(call['input_order_sha256']==order_digest(body),'stale_input_order')
        result.update(call);stage_id='compile';compile_template(template)
        stage_id='dependencies'
        for pin in template['dependency_pins']:
            c.need(sha256((ROOT/'scripts'/pin['file']).read_bytes()).hexdigest()==pin['sha256'],pin['reason'])
        typed.types.protected();stage_id='structure';base.memory.bounded(body);c.exact(body)
        for stage in template['stages']:
            stage_id=stage['id'];op=stage['op'];reason=stage['reason'];evidence=None
            if op=='record_fields':base.closed(at(body,stage['path']),stage['fields'])
            elif op=='record_values':
                record=at(body,stage['path'])
                c.need(all(record[k]==v for k,v in stage['values'].items()),reason)
            elif op=='text':base.text(at(body,stage['path']),stage['label'])
            elif op=='equals':c.need(at(body,stage['path'])==stage['value'],reason)
            elif op=='typed_book':
                evidence=typed.typed_book(body['opening'],body['memory_definition'],body['schemas'])
                c.need(body['opening']['context']==template['context'],'opening_context_mismatch')
            elif op=='map_values':
                node=at(body,stage['path']);c.need(node['node']=='map' and node['values']==stage['values'],reason)
            elif op=='role_population':c.need(type(body['roles']) is dict and set(body['roles'])==set(stage['roles']),reason)
            elif op=='role_injective':c.need(len(set(body['roles'].values()))==len(body['roles']),reason)
            elif op=='role_classes':
                for row in stage['classes']:
                    account=body['roles'][row['role']]
                    c.need(account in body['opening']['accounts'] and body['opening']['accounts'][account]['classification']==row['classification'],reason+row['role'])
            elif op=='cash_role':c.need(body['roles'][stage['role']]==body['opening']['cash_account'],reason)
            elif op=='memory_leaf':c.need(body['unit_cost_pointer'] in body['opening']['memory_types'],reason)
            elif op=='memory_type':c.need(body['opening']['memory_types'][body['unit_cost_pointer']]==stage['type'],reason)
            elif op=='predicate':
                manifest=stage['manifest'];h=core.digest(manifest)
                values={name:bind(body,source) for name,source in stage['bindings'].items()}
                evidence=gate.guarded.assess({h:manifest},h,values,[])
                if evidence['status']!='requirements_satisfied':
                    status=evidence['status'] if evidence['status'] in ('invalid','unsupported','unresolved') else 'invalid'
                    return dict(result,status=status,reason=reason,failed_stage=stage_id,trace=trace+[dict(stage=stage_id,evidence=evidence)])
            elif op=='opening_report':
                evidence=reports.report(reports.request(body['opening'],body['opening'],body['schemas'],body['mapping']))
                c.need(evidence['status']=='reported',reason+evidence.get('reason',''))
            elif op=='commands':c.need(type(body['commands']) is list and 0<len(body['commands'])<=stage['maximum'],reason)
            trace.append(dict(stage=stage_id,status='satisfied',evidence=evidence))
        return dict(result,status='opening_admitted',failed_stage=None,trace=trace,
                    scope='Selected finite empty-opening contract; future commands retain their own validation')
    except (ValueError,TypeError,KeyError,IndexError,RecursionError,OverflowError) as exc:
        return dict(result,status=getattr(exc,'status','invalid'),reason=str(exc)[:300] or type(exc).__name__,failed_stage=stage_id,trace=trace)
