"""Direct source composition over unchanged selected-company execution."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json,sys
HERE=Path(__file__).resolve().parent
for folder in ('method-recipe-source-20261026','opening-admission-source-20261026','invariant-source-authoring-20261026','admitted-program-binding-20261026'):
    sys.path.insert(0,str(HERE.parent/folder))
import recipe_text as recipe
import expansion_text as expansion
import opening_text as opening
import invariant_text_unicode as invariant
import binding
eligibility=recipe.syntax;core=binding.core;c=binding.c
Invalid=eligibility.Invalid;need=eligibility.need
PROFILE='SelectedCompanyText/1'
IMPORTS=('opening','schemas','mapping','memory_definition')

def j(value):return json.dumps(value,ensure_ascii=False,separators=(',',':'),allow_nan=False)

def lower(source,resources):
    location=None
    try:
        rows=eligibility.source_rows(source);raw=source.encode();state='header';used=set();facts={};spans=[];blocks=[]
        selected={};rules={};commands=[];selection_residuals=[];program_residuals=[];opening_template=None;state_invariant=None
        rule=None;command=None;index=0;import_index=0
        need(type(resources) is dict and len(resources)<=core.MAX_NODES,'resource_population')
        need(len(core.canonical(resources))<=core.MAX_BYTES,'resource_size_limit')
        def unique(obj,key,value):need(key not in obj,'duplicate_declaration:'+key,location);obj[key]=value
        def embedded(end_marker,parser,kind):
            nonlocal index
            start=raw.find(b'\n',location['byte_end'])+1
            need(start>0,'embedded_newline_required',location);first_line=location['line']+1
            while index<len(rows) and rows[index][0].strip()!=end_marker:index+=1
            need(index<len(rows),'unterminated_'+kind,location)
            end=rows[index][1]['byte_start'];nested=raw[start:end].decode();index+=1
            try:result=parser(nested)
            except Exception as exc:
                loc=getattr(exc,'location',None)
                if loc:
                    loc=eligibility.span(source,start+loc['byte_start'],start+loc['byte_end'],first_line+loc['line']-1,loc.get('granularity','declaration'))
                else:loc=eligibility.span(source,start,end,first_line,'block')
                raise Invalid(getattr(exc,'reason',str(exc)),loc) from exc
            blocks.append(dict(kind=kind,source_sha256=sha256(nested.encode()).hexdigest(),
                               location=eligibility.span(source,start,end,first_line,'block')))
            return result
        while index<len(rows):
            line,location=rows[index];index+=1
            if not line.strip():continue
            spans.append(location);need(state!='done','declaration_after_end',location)
            r=eligibility.Reader(source,line,location);word=r.take('word')
            if state=='header':
                need(word=='selected_company' and r.string()==PROFILE,'source_profile',location)
                bound_profile,program_profile,native_profile,name=r.string(),r.string(),r.string(),r.string()
                need(bound_profile==binding.PROFILE and program_profile==binding.composer.PROFILE and native_profile=='DeclaredReceivableLifecycle/1','selected_profiles',location)
                selected['roles']={};state='imports'
            elif state=='imports':
                key=IMPORTS[import_index];need(word=='import_'+key,'required_import:'+key,location)
                digest=r.string();need(digest in resources,'missing_resource:'+digest,location)
                value=resources[digest];c.base.memory.bounded(value);c.exact(value)
                need(core.digest(value)==digest,'resource_digest:'+digest,location);facts[key]=deepcopy(value);used.add(digest)
                import_index+=1
                if import_index==len(IMPORTS):state='body'
            elif state=='rule':
                if word=='begin_eligibility':
                    need('eligibility' not in rule,'duplicate_eligibility',location);r.finish()
                    lowered=embedded('end_eligibility_source;',eligibility.lower,'eligibility');rule['eligibility']=lowered['template'];continue
                elif word=='begin_recipe':
                    need('construction' not in rule,'duplicate_recipe',location);kind=r.take('word');r.finish()
                    need(kind in ('scalar','ordered'),'recipe_kind',location)
                    lowered=embedded('end_recipe_source;',(recipe if kind=='scalar' else expansion).lower,'recipe')
                    rule['construction']=lowered['template'];continue
                else:
                    need(word=='end_rule','rule_declaration:'+word,r.location(0))
                    need(set(rule)=={'eligibility','construction'},'complete_rule',location)
                    need(rule['eligibility']['operation']==rule_key,'rule_operation',location)
                    rules[rule_key]=dict(eligibility=rule['eligibility'],eligibility_sha256=core.digest(rule['eligibility']),
                        construction=rule['construction'],construction_sha256=core.digest(rule['construction']))
                    rule=None;state='body'
            elif state=='command':
                kind=command['kind']
                if word=='input':
                    need(kind=='event','event_input_scope',location);key=r.string();typ=r.take('value');status=r.take('word')
                    need(status in ('known','unknown'),'input_status',location)
                    value={'status':status,('value' if status=='known' else 'reason'):r.take('value')}
                    unique(command['event']['inputs'],key,dict(type=typ,value=value,provenance=r.string()))
                elif word=='order':
                    need(kind=='event','order_event_scope',location);unique(command,'order',r.take('value'))
                elif word in ('equity_movements','notes'):
                    need(kind in ('report','carry'),'report_field_scope',location);unique(command,word,r.take('value'))
                elif word=='memory_policy':
                    need(kind=='carry','memory_policy_scope',location);unique(command['memory_policies'],r.string(),r.take('value'))
                else:
                    need(word=='end_'+kind,'command_declaration:'+word,r.location(0))
                    need('order' in command if kind=='event' else all(k in command for k in ('equity_movements','notes')),'incomplete_command',location)
                    commands.append(command);need(len(commands)<=binding.composer.MAX_COMMANDS,'command_limit',location);command=None;state='body'
            elif state=='body':
                if word=='role':unique(selected['roles'],r.string(),r.string())
                elif word=='unit_cost_pointer':unique(selected,word,r.string())
                elif word=='policy':unique(selected,word,dict(profile=r.string(),past_due=r.string(),carry=r.string(),provenance=r.string()))
                elif word=='selection_residual':selection_residuals.append(r.string())
                elif word=='program_residual':program_residuals.append(r.string())
                elif word=='begin_opening':
                    need(opening_template is None,'duplicate_opening',location);r.finish()
                    opening_template=embedded('end_opening_source;',opening.compile_text,'opening')['template'];continue
                elif word=='begin_invariant':
                    need(state_invariant is None,'duplicate_invariant',location);r.finish()
                    state_invariant=embedded('end_invariant_source;',invariant.lower,'invariant')['invariant'];continue
                elif word=='rule':
                    rule_key=r.string();need(rule_key not in rules,'duplicate_rule',location);need(len(rules)<64,'rule_limit',location)
                    rule={};state='rule'
                elif word in ('event','report','carry'):
                    kind=word;ident=r.string()
                    if kind=='event':command=dict(kind=kind,method_key=r.string(),event=dict(id=ident,date=r.string(),inputs={}))
                    else:
                        command=dict(kind=kind,id=ident,cutoff=r.string())
                        if kind=='carry':command.update(retained_account=r.string(),next_end_exclusive=r.string(),memory_policies={})
                    state='command'
                else:need(word=='end_company','company_declaration:'+word,r.location(0));state='done'
            r.finish()
        need(state=='done','incomplete_source:'+state,location)
        need(set(resources)==used,'exact_resource_population',location)
        need(opening_template is not None and state_invariant is not None and rules and commands,'required_component',location)
        need(set(selected)=={'roles','unit_cost_pointer','policy'},'selected_contract',location)
        # Retain command declaration order while fixing record field order explicitly.
        ordered_commands=[]
        for command in commands:
            if command['kind']=='event':ordered_commands.append(command);continue
            keys=['kind','id','cutoff','equity_movements','notes']
            if command['kind']=='carry':keys+=['retained_account','next_end_exclusive','memory_policies']
            ordered_commands.append({k:command[k] for k in keys})
        program=dict(name=name,**facts,state_invariant=state_invariant,profile=program_profile,
            invariant_sha256=core.digest(state_invariant),rules=rules,commands=ordered_commands,
            carry_policy=dict(mode=selected['policy']['carry'],provenance=selected['policy']['provenance']),residuals=program_residuals)
        native_input=dict(profile=native_profile,name=name,**facts,roles=selected['roles'],
            unit_cost_pointer=selected['unit_cost_pointer'],policy=selected['policy'],commands=binding.project_commands(program))
        selection=dict(profile=binding.SELECTION,context=deepcopy(opening_template['context']),native_profile=native_profile,program_profile=program_profile,
            roles=deepcopy(selected['roles']),unit_cost_pointer=selected['unit_cost_pointer'],policy=deepcopy(selected['policy']),
            invariant_sha256=core.digest(state_invariant),rules_sha256=core.digest(rules),template_sha256=core.digest(opening_template),residuals=selection_residuals)
        need(len(core.canonical(program))<=core.MAX_BYTES,'program_size_limit',location)
        call=binding.make_call(selection,opening_template,native_input,program)
        return dict(profile=PROFILE,status='lowered_structural',selection=selection,opening_template=opening_template,
            input=native_input,program=program,call=call,source_sha256=sha256(raw).hexdigest(),source_spans=spans,blocks=blocks,
            resources=sorted(used),executed=False,opening_admitted=False,source_admission=False,accounting_admission=False)
    except Exception as exc:
        if isinstance(exc,Invalid):raise
        raise Invalid(getattr(exc,'reason',str(exc)),location) from exc

def execute_source(source,resources):
    result=lower(source,resources)
    return binding.execute(result['selection'],result['opening_template'],result['input'],result['program'],result['call'])

def render(selection,opening_template,program):
    resources={};rows=[]
    def add(word,*values):rows.append(word+(' '+' '.join(j(x) for x in values) if values else '')+';')
    def block(start,end,value):add(start);rows.extend(value.rstrip('\n').split('\n'));add(end)
    add('selected_company',PROFILE,binding.PROFILE,program['profile'],selection['native_profile'],program['name'])
    for key in IMPORTS:
        value=program[key];digest=core.digest(value);resources[digest]=deepcopy(value);add('import_'+key,digest)
    for key,value in selection['roles'].items():add('role',key,value)
    add('unit_cost_pointer',selection['unit_cost_pointer']);p=selection['policy'];add('policy',*[p[k] for k in ('profile','past_due','carry','provenance')])
    for value in selection['residuals']:add('selection_residual',value)
    for value in program['residuals']:add('program_residual',value)
    block('begin_opening','end_opening_source',opening.render(opening_template))
    block('begin_invariant','end_invariant_source',invariant.render(program['state_invariant']))
    for key,rule in program['rules'].items():
        add('rule',key);block('begin_eligibility','end_eligibility_source',eligibility.render(rule['eligibility']))
        module=recipe if rule['construction']['profile']==c.PROFILE else expansion
        rows.append('begin_recipe '+('scalar' if module is recipe else 'ordered')+';')
        rows.extend(module.render(rule['construction']).rstrip('\n').split('\n'));add('end_recipe_source');add('end_rule')
    for command in program['commands']:
        kind=command['kind']
        if kind=='event':
            event=command['event'];add('event',event['id'],command['method_key'],event['date'])
            for key,record in event['inputs'].items():
                v=record['value'];rows.append('input '+' '.join([j(key),j(record['type']),v['status'],j(v['value'] if v['status']=='known' else v['reason']),j(record['provenance'])])+';')
            add('order',command['order'])
        else:
            args=[command['id'],command['cutoff']]
            if kind=='carry':args+=[command['retained_account'],command['next_end_exclusive']]
            add(kind,*args);add('equity_movements',command['equity_movements']);add('notes',command['notes'])
            if kind=='carry':
                for key,value in command['memory_policies'].items():add('memory_policy',key,value)
        add('end_'+kind)
    add('end_company');source='\n'.join(rows)+'\n';lowered=lower(source,resources)
    need(core.canonical(lowered['program'])==core.canonical(program),'render_program_roundtrip')
    need(core.canonical(lowered['selection'])==core.canonical(selection),'render_selection_roundtrip')
    return source,resources
