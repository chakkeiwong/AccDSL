"""Complete bounded method syntax; all financial semantics belong to retained engines."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import method_requirement_text_v2 as requirements
import company_book_transition_v1 as v1
import company_book_transition_v2 as v2
core=v1.core
PROFILE='CompanyMethodAuthoring/1'
ENGINES={v1.PROFILE:v1,v2.PROFILE:v2}
FLAGS={'executed':False,'committed':False,'source_admission':False,'accounting_admission':False,'method_eligible':False}
NL=chr(10)

def need(condition,reason):core.need(condition,reason)
def reader(line):return requirements.Reader(requirements.prior.tokens(line))
def value(r):return r.take('value')

def money_expression(r,depth=0,counter=None):
    counter=[0] if counter is None else counter;counter[0]+=1
    need(depth<=core.MAX_DEPTH and counter[0]<=core.MAX_NODES,'expression_limit')
    r.take('(');op=r.take('word')
    if op=='ref':node={'op':op,'id':r.string()}
    elif op=='const':node={'op':op,'type':value(r),'value':value(r)}
    else:
        need(op in ['add','sub','mul','min'],'monetary_expression_operator')
        node={'op':op,'left':money_expression(r,depth+1,counter),'right':money_expression(r,depth+1,counter)}
    r.take(')');return node

def lower(source):
    need(type(source) is str and len(source.encode('utf-8'))<=core.MAX_BYTES,'source_size_or_type')
    need(not source.startswith(chr(65279)),'bom_unsupported')
    need(chr(13) not in source.replace(chr(13)+NL,''),'lone_cr')
    need(all(ord(c)>=32 or c in [chr(9),chr(13),NL] for c in source) and chr(127) not in source,'source_control')
    method=None;transition=None;section=None;block=[];seen=set();ended=False;spans=[];offset=0
    for number,raw in enumerate(source.splitlines(keepends=True),1):
        line=raw.rstrip(chr(13)+NL);start=offset;offset+=len(raw.encode('utf-8'))
        if not line.strip():continue
        need(len(spans)<core.MAX_NODES,'declaration_limit')
        spans.append({'line':number,'byte_start':start,'byte_end':start+len(line.encode('utf-8')),
                      'slice_sha256':sha256(line.encode('utf-8')).hexdigest()})
        try:
            need(not ended,'content_after_end_method')
            if section in ['preconditions','postconditions']:
                if line.strip()=='end_'+section+';':
                    exchange=requirements.lower(NL.join(block)+NL)
                    need(exchange['values']=={} and exchange['available_capabilities']==[], 'manifest_block_has_event_values_or_capabilities')
                    method[section]['manifest']=exchange['definition'];section=None;block=[]
                else:block.append(line)
                continue
            r=reader(line);command=r.take('word')
            if method is None:
                need(command=='company_method','header_required')
                need(r.string()==PROFILE,'authoring_profile');transition=r.string();need(transition in ENGINES,'transition_profile')
                method={'profile':r.string(),'id':r.string(),'version':r.string(),'account_map':{},
                        'preconditions':{'bindings':{}},'postconditions':{'bindings':{}},
                        'monetary':{'bindings':{}},'memory':{},'residual_prerequisites':[]}
            elif section=='monetary':
                d=method['monetary']['definition']
                if command=='end_monetary':need('cash_account' in d,'cash_account_required');section=None
                elif command=='money_input':
                    key=r.string();need(key not in d['inputs'],'duplicate_money_input')
                    d['inputs'][key]={'type':value(r),'role':r.take('word'),'source_ref':r.string()}
                elif command=='money_account':
                    key=r.string();need(key not in d['accounts'],'duplicate_money_account');d['accounts'][key]=value(r)
                elif command=='cash_account':need('cash_account' not in d,'duplicate_cash_account');d['cash_account']=r.string()
                else:
                    need(command in ['calculation','posting','flow'],'monetary_declaration')
                    row={'id':r.string()}
                    if command=='calculation':row['type']=value(r)
                    elif command=='posting':row['account']=r.string()
                    else:row.update(activity=r.string(),origin=r.string())
                    row['requires']=value(r);row['expression']=money_expression(r)
                    d[{'calculation':'calculations','posting':'postings','flow':'flows'}[command]].append(row)
            elif section=='memory':
                part=method['memory']
                if command=='end_memory':section=None
                elif command=='memory_input':
                    key=r.string();need(key not in part['input_bindings'],'duplicate_memory_input');part['input_bindings'][key]=value(r)
                else:
                    need(command=='write','memory_declaration')
                    part['definition']['operations'].append({'id':r.string(),'op':r.string(),'path':value(r),'value':value(r)})
            elif command=='context':need('context' not in method,'duplicate_context');method['context']=value(r)
            elif command=='account_map':
                key=r.string();need(key not in method['account_map'],'duplicate_account_map');method['account_map'][key]=r.string()
            elif command=='input_binding':
                target=r.string();need(target in ['preconditions','postconditions','monetary'],'binding_section')
                key=r.string();need(key not in method[target]['bindings'],'duplicate_input_binding');method[target]['bindings'][key]=value(r)
            elif command in ['begin_preconditions','begin_postconditions','begin_monetary','begin_memory']:
                section=command.removeprefix('begin_');need(section not in seen,'duplicate_section');seen.add(section)
                if section=='monetary':
                    method['monetary']['definition']={'profile':r.string(),'method_id':r.string(),'version':r.string(),
                        'inputs':{},'accounts':{},'calculations':[],'postings':[],'flows':[]}
                elif section=='memory':
                    method['memory']={'definition':{'profile':r.string(),'state_schema':r.string(),'input_schema':r.string(),'operations':[]},'input_bindings':{}}
            elif command=='residual':method['residual_prerequisites'].append(r.string())
            else:need(command=='end_method','unknown_declaration');ended=True
            r.finish()
        except (ValueError,TypeError,KeyError,AttributeError,RecursionError,OverflowError) as exc:
            raise core.Invalid('line '+str(number)+': '+str(exc)[:280]) from exc
    need(method is not None and ended and section is None,'incomplete_method')
    need(seen=={'preconditions','postconditions','monetary','memory'} and 'context' in method,'required_sections')
    core.need(len(core.canonical(method))<=core.MAX_BYTES,'method_size')
    return {**FLAGS,'profile':PROFILE,'status':'lowered_syntax_only','transition_profile':transition,'method':method,
            'source_sha256':sha256(source.encode('utf-8')).hexdigest(),'source_spans':spans}

def compile_typed(method,transition_profile,environment):
    need(transition_profile in ENGINES,'transition_profile');engine=ENGINES[transition_profile]
    keys=['book','event','schemas']+(['memory_definition'] if transition_profile==v2.PROFILE else [])
    core.closed(environment,keys,'method_compilation_environment')
    request={'profile':transition_profile,'expected_state_sha256':core.digest(environment['book']),
             'expected_method_sha256':core.digest(method),'method':deepcopy(method),
             'event':deepcopy(environment['event']),'schemas':deepcopy(environment['schemas'])}
    if transition_profile==v2.PROFILE:request['memory_definition']=deepcopy(environment['memory_definition'])
    engine.prepare(environment['book'],request)
    return {**FLAGS,'profile':PROFILE,'status':'compiled_method','transition_profile':transition_profile,
            'method':deepcopy(method),'method_sha256':core.digest(method),'request':request,
            'request_sha256':core.digest(request),'source_sha256':None,'source_spans':None}

def compile_text(source,environment):
    lowered=lower(source)
    result=compile_typed(lowered['method'],lowered['transition_profile'],environment)
    result.update(source_sha256=lowered['source_sha256'],source_spans=lowered['source_spans'])
    return result

def render(method,transition_profile,environment):
    compile_typed(method,transition_profile,environment)
    j=requirements.prior.json_token
    line=lambda command,*tokens:command+' '+' '.join(tokens)+';'
    rows=[line('company_method',*[j(x) for x in [PROFILE,transition_profile,method['profile'],method['id'],method['version']]]),
          line('context',j(method['context']))]
    rows += [line('account_map',j(k),j(v)) for k,v in sorted(method['account_map'].items())]
    def bindings(section):
        return [line('input_binding',j(section),j(k),j(v)) for k,v in sorted(method[section]['bindings'].items())]
    def requirement_block(section):
        definition=method[section]['manifest']
        exchange={'profile':requirements.EXCHANGE,'definition':definition,'selected_digest':core.digest(definition),
                  'values':{},'available_capabilities':[]}
        return ['begin_'+section+';',*requirements.render(exchange).splitlines(),'end_'+section+';',*bindings(section)]
    rows+=requirement_block('preconditions')
    d=method['monetary']['definition']
    rows.append(line('begin_monetary',*[j(d[k]) for k in ['profile','method_id','version']]))
    for key,item in sorted(d['inputs'].items()):
        rows.append(line('money_input',j(key),j(item['type']),item['role'],j(item['source_ref'])))
    for row in d['calculations']:
        rows.append(line('calculation',j(row['id']),j(row['type']),j(row['requires']),requirements.render_expression(row['expression'])))
    rows += [line('money_account',j(k),j(v)) for k,v in sorted(d['accounts'].items())]
    rows.append(line('cash_account',j(d['cash_account'])))
    for row in d['postings']:
        rows.append(line('posting',j(row['id']),j(row['account']),j(row['requires']),requirements.render_expression(row['expression'])))
    for row in d['flows']:
        rows.append(line('flow',j(row['id']),j(row['activity']),j(row['origin']),j(row['requires']),requirements.render_expression(row['expression'])))
    rows+=['end_monetary;',*bindings('monetary')]
    part=method['memory'];d=part['definition']
    rows.append(line('begin_memory',*[j(d[k]) for k in ['profile','state_schema','input_schema']]))
    rows += [line('memory_input',j(k),j(v)) for k,v in sorted(part['input_bindings'].items())]
    for row in d['operations']:rows.append(line('write',*[j(row[k]) for k in ['id','op','path','value']]))
    rows+=['end_memory;',*requirement_block('postconditions')]
    rows += [line('residual',j(x)) for x in method['residual_prerequisites']]
    rows.append('end_method;');source=NL.join(rows)+NL
    need(lower(source)['method']==method,'render_correspondence')
    return source
