"""Declared synthetic company books; composed typed effects, no durable commit."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import re
import method_requirements_v1 as core
import method_requirements_v2 as dimensions
import method_requirements_v3 as requirements
import method_monetary_effects_v1 as monetary
import method_memory_effects_v1 as memory
import method_input_binding_v1 as binding

BOOK='CompanyBook/1';METHOD='CompanyBookMethod/1';PROFILE='CompanyBookTransition/1'
FLAGS={'committed':False,'physical_durability':False,'source_admission':False,
       'accounting_admission':False,'method_eligible':False,'posting_authorized':False}
PINS={'method_requirements_v1.py':'6d176e25dada74da4623a0628e265ff88c7e06cdcf995a064e7d9186cd10b53a',
      'method_requirements_v2.py':'2262c15bcc13e01b00e406c33ba25641f22443b25c6607b94f761d2c5fc0826d',
      'method_requirements_v3.py':'1293522aa8cf636a7ba728ab3213e4bd426eb27725466f68f1d49defe17a9217',
      'method_monetary_effects_v1.py':'19fb02abd353202b31dc54adac6ad6414ec15b298a5f78f4b5e92bcb55e2d876',
      'method_memory_effects_v1.py':'ec7face2aff8071935a75c61180b929c71ac7ae7a7fb03306973d8aab264df72',
      'method_input_binding_v1.py':'433633f1d5941d707f26495050bb27ec2ff8002b0edfdb5097ccceb3a2a375ee'}
digest=core.digest


def closed(value,fields):core.closed(value,fields,'company_book')
def text(value,label):
    core.text(value,label);core.need(bool(value.strip()),label+'_blank')
def protected():
    folder=Path(__file__).resolve().parent
    for name,h in PINS.items():core.need(sha256((folder/name).read_bytes()).hexdigest()==h,'dependency_hash:'+name)
def type_context(book):return {k:v for k,v in book['context'].items() if k!='currency'}
def money_type(book):return {'kind':'rational','context':type_context(book),'dimensions':{'currency:'+book['context']['currency']:1},'scale':'1/1'}
def known(value):return {'status':'known','value':value}
def scalar_type(typ,book):
    dimensions.typed(typ)
    if typ['kind']=='rational':core.need(typ['context']==type_context(book),'numeric_company_context')
def leaf_values(value,prefix=''):
    if type(value) is dict:
        out={}
        for key,child in value.items():out.update(leaf_values(child,prefix+'/'+key.replace('~','~0').replace('/','~1')))
        return out
    if type(value) is list:
        out={}
        for index,child in enumerate(value):out.update(leaf_values(child,prefix+'/'+str(index)))
        return out
    return {prefix:value}


def validate_book(book,schemas):
    memory.bounded(book)
    closed(book,['profile','context','period','date','accounts','balances','cash_account','memory_schema','memory_types','memory','seen','flows'])
    core.need(book['profile']==BOOK,'book_profile')
    closed(book['context'],['entity','book','currency','case_id','mode'])
    for key,value in book['context'].items():text(value,key)
    core.need(book['context']['mode']=='synthetic','synthetic_book_only')
    core.need(re.fullmatch('[A-Z]{3}',book['context']['currency']) is not None,'currency_code')
    closed(book['period'],['start','end_exclusive'])
    start,end,at=[core.scalar(value,'date') for value in [book['period']['start'],book['period']['end_exclusive'],book['date']]]
    core.need(start<=at<end,'book_period')
    core.need(type(book['accounts']) is dict and 0<len(book['accounts'])<=monetary.MAX_ENTRIES,'account_limit')
    for key,row in book['accounts'].items():
        text(key,'account_id');closed(row,['classification'])
        core.need(row['classification'] in ['asset','liability','equity','income','expense'],'account_class')
    core.need(type(book['balances']) is dict and set(book['balances'])==set(book['accounts']),'balance_population')
    core.need(sum(monetary.rational(v) for v in book['balances'].values())==0,'book_unbalanced')
    core.need(book['cash_account'] in book['accounts'] and book['accounts'][book['cash_account']]['classification']=='asset','cash_account')
    shape=binding.record(schemas,book['memory_schema'],'memory_schema');memory.check_schema(shape);memory.validate(book['memory'],shape)
    leaves=leaf_values(book['memory']);core.need(type(book['memory_types']) is dict and set(leaves)==set(book['memory_types']),'exact_memory_leaf_types')
    for pointer,value in leaves.items():
        typ=book['memory_types'][pointer];scalar_type(typ,book);core.scalar(value,typ['kind'])
    core.identifiers(book['seen'],'seen_events');core.need(type(book['flows']) is list,'flows')
    ids=set()
    for flow in book['flows']:
        closed(flow,['id','entity','book','currency','event_id','date','activity','origin','amount'])
        for key in ['id','event_id','origin']:text(flow[key],key)
        core.need(flow['id'] not in ids,'duplicate_flow_id');ids.add(flow['id'])
        core.need(all(flow[k]==book['context'][k] for k in ['entity','book','currency']),'flow_context')
        core.need(flow['event_id'] in book['seen'],'flow_event')
        core.need(start<=core.scalar(flow['date'],'date')<=at,'flow_chronology')
        core.need(flow['activity'] in ['operating','investing','financing'],'flow_activity');monetary.rational(flow['amount'])


def values_for(book,event,method,inputs,bindings):
    core.need(type(bindings) is dict and set(bindings)==set(inputs),'exact_method_bindings')
    values={}
    for key,declaration in inputs.items():
        source=bindings[key];core.need(type(source) is dict,'binding_record');kind=source.get('kind')
        if kind=='account':
            closed(source,['kind','role']);core.need(source['role'] in method['account_map'],'account_role')
            typ=money_type(book);value=known(book['balances'][method['account_map'][source['role']]])
        elif kind=='memory':
            closed(source,['kind','pointer']);core.need(source['pointer'] in book['memory_types'],'memory_leaf')
            found,item=binding.located(book['memory'],source['pointer']);core.need(found,'memory_path')
            typ=book['memory_types'][source['pointer']];value=known(item)
        elif kind=='event':
            closed(source,['kind','name']);core.need(source['name'] in event['inputs'],'event_input')
            record=event['inputs'][source['name']];typ=record['type'];value=record['value']
        else:raise core.Invalid('unsupported_binding')
        core.need(typ==declaration['type'],'binding_type_mismatch:'+key);values[key]=deepcopy(value)
    return values


def assessment(book,event,method,part):
    manifest=part['manifest'];values=values_for(book,event,method,manifest['inputs'],part['bindings'])
    h=digest(manifest)
    return requirements.assess({h:manifest},h,values,[])


def prepare(book,request):
    protected();memory.bounded(request)
    closed(request,['profile','expected_state_sha256','expected_method_sha256','method','event','schemas'])
    core.need(request['profile']==PROFILE,'request_profile')
    core.need(request['expected_state_sha256']==digest(book),'stale_state')
    method=request['method'];core.need(request['expected_method_sha256']==digest(method),'method_hash')
    schemas=request['schemas'];core.need(type(schemas) is dict,'schema_registry')
    for key,shape in schemas.items():core.need(key==digest(shape),'schema_digest');memory.check_schema(shape)
    validate_book(book,schemas)
    closed(method,['profile','id','version','context','account_map','preconditions','monetary','memory','postconditions','residual_prerequisites'])
    core.need(method['profile']==METHOD,'method_profile');text(method['id'],'method_id');text(method['version'],'method_version')
    core.need(method['context']==book['context'],'method_context')
    mapping=method['account_map'];core.need(type(mapping) is dict and bool(mapping),'account_map')
    core.need(len(set(mapping.values()))==len(mapping),'account_map_not_injective')
    for role,account in mapping.items():text(role,'account_role');core.need(account in book['accounts'],'unregistered_account')
    core.identifiers(method['residual_prerequisites'],'residual_prerequisites',True)
    event=request['event'];closed(event,['id','date','inputs']);text(event['id'],'event_id')
    core.need(event['id'] not in book['seen'],'duplicate_event')
    core.need(core.scalar(book['date'],'date')<=core.scalar(event['date'],'date')<core.scalar(book['period']['end_exclusive'],'date'),'event_chronology')
    core.need(type(event['inputs']) is dict,'event_inputs')
    for key,record in event['inputs'].items():
        text(key,'event_input_name');closed(record,['type','value','provenance']);scalar_type(record['type'],book);text(record['provenance'],'input_provenance')
        core.validate_values({'inputs':{key:{'type':dimensions.encoded(record['type'])}}},{key:record['value']})
    for name in ['preconditions','postconditions']:
        part=method[name];closed(part,['manifest','bindings']);requirements.compile_manifest(part['manifest'])
        values_for(book,event,method,part['manifest']['inputs'],part['bindings'])
    part=method['monetary'];closed(part,['definition','bindings']);definition=part['definition'];monetary.compile_definition(definition)
    core.need(set(definition['accounts'])==set(mapping),'monetary_account_roles')
    core.need(all(typ==money_type(book) for typ in definition['accounts'].values()),'monetary_book_type')
    core.need(mapping[definition['cash_account']]==book['cash_account'],'cash_role_mapping')
    values_for(book,event,method,definition['inputs'],part['bindings'])
    part=method['memory'];closed(part,['definition','input_bindings'])
    memory.compile_definition(part['definition'],schemas)
    core.need(part['definition']['state_schema']==book['memory_schema'],'memory_state_schema')
    shape=schemas[part['definition']['input_schema']]
    core.need(shape.get('type')=='object' and 'properties' in shape,'memory_input_record')
    core.need(type(part['input_bindings']) is dict and set(part['input_bindings'])==set(shape['properties']),'memory_input_population')
    calculations={row['id'] for row in method['monetary']['definition']['calculations']}
    for record in part['input_bindings'].values():
        closed(record,['kind','name']);kind,name=record['kind'],record['name']
        core.need(kind in ['monetary_input','calculation','event'],'memory_input_kind')
        core.need(name in (set(method['monetary']['definition']['inputs']) if kind=='monetary_input' else calculations if kind=='calculation' else {'id','date'}),'memory_input_name')
    return method,event,schemas


def invalid(exc):return {'profile':PROFILE,**FLAGS,'status':'invalid','reason':str(exc)[:300] or type(exc).__name__}
def propose(book,request):
    try:
        method,event,schemas=prepare(book,request)
        result={'profile':PROFILE,**FLAGS,'before_sha256':digest(book),'request_sha256':digest(request),
                'method_sha256':digest(method),'implementation_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),
                'dependency_sha256':deepcopy(PINS),'residual_prerequisites':deepcopy(method['residual_prerequisites'])}
        pre=assessment(book,event,method,method['preconditions']);result['preconditions']=pre
        if pre['status'] not in ['requirements_satisfied','no_active_requirements']:return {**result,'status':pre['status'],'reason':'preconditions'}
        definition=method['monetary']['definition'];values=values_for(book,event,method,definition['inputs'],method['monetary']['bindings']);h=digest(definition)
        amounts=monetary.derive({h:definition},h,values);result['monetary']=amounts
        if amounts['status']!='derived':return {**result,'status':amounts['status'],'reason':'monetary'}
        inputs={};calcs={row['id']:row['binding']['value'] for row in amounts['diagnostics']['calculations']}
        for key,source in method['memory']['input_bindings'].items():
            inputs[key]=values[source['name']]['value'] if source['kind']=='monetary_input' else calcs[source['name']] if source['kind']=='calculation' else event[source['name']]
        memdef=method['memory']['definition'];h=digest(memdef);staged=memory.stage({h:memdef},h,schemas,book['memory'],inputs);result['memory']=staged
        if staged['status']!='staged':return {**result,'status':staged['status'],'reason':'memory'}
        after=deepcopy(book);after['memory']=staged['after'];journal={key:'0/1' for key in book['accounts']}
        for role,value in amounts['journal'].items():
            key=method['account_map'][role];journal[key]=value;after['balances'][key]=monetary.fmt(monetary.bounded(monetary.rational(book['balances'][key])+monetary.rational(value)))
        flows=[{'id':digest([event['id'],row['id']]),'entity':book['context']['entity'],'book':book['context']['book'],'currency':book['context']['currency'],
                'event_id':event['id'],'date':event['date'],'activity':row['activity'],'origin':row['origin'],'amount':row['amount']} for row in amounts['flows']]
        after['date']=event['date'];after['seen'].append(event['id']);after['flows'].extend(flows);validate_book(after,schemas)
        post=assessment(after,event,method,method['postconditions']);result['postconditions']=post
        if post['status'] not in ['requirements_satisfied','no_active_requirements']:return {**result,'status':post['status'],'reason':'postconditions'}
        return {**result,'status':'proposed','after':after,'journal':journal,'flows':flows,'after_sha256':digest(after)}
    except Exception as exc:return invalid(exc)


def apply(book,request,proposal):
    try:
        expected=propose(book,request);core.need(expected==proposal,'proposal_recomputation_mismatch')
        if expected['status']!='proposed':return expected
        return {**deepcopy(expected),'status':'applied_provisional'}
    except Exception as exc:return invalid(exc)
