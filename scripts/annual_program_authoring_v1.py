"""Data-only declarations lowering exactly to the checked finite annual program."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json,re
import annual_period_book_v1 as annual
import shared_book_authoring_v1 as older

lexical=older.lexical;syntax=older.syntax;core=annual.core;losses=annual.losses
ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/'data/accounting-master/annual-program-authoring-20261025'
LOCK='915ffd840e49c4b86af0b94660bf773858bc94608029f36a3e8ab7133ac927ba'
PROFILE='AnnualProgramAuthoring/1'
Invalid=older.Invalid;need=older.need;guarded=older.guarded
SINGLE={
    'native':['module','native_event'],
    'allocated_tax_payment':['date','amount','authorization'],
    'current_assessment':['mode','model','interval','loss_model','utilization_cap','generation'],
    'deferred_assessment':['model','measurement','recovery_capacity'],
    'provisional_carry':['model','next_period']}
MAP={'current_assessment':{'information':'information'},
     'deferred_assessment':{'finding':'findings'},'provisional_carry':{'finding':'findings'}}
LIST={'allocated_tax_payment':{'payment_allocation':'allocations'},
      'current_assessment':{'adjustment':'allocations','loss_use':'uses'},
      'deferred_assessment':{'item':'items'}}

def protected():
    raw=(HERE/'source-lock.json').read_bytes();need(sha256(raw).hexdigest()==LOCK,'source_lock_changed')
    for name,h in json.loads(raw).items():need(sha256((ROOT/name).read_bytes()).hexdigest()==h,'protected_source_changed:'+name)

def closed(x,keys,label):guarded(core.closed,x,keys,label)
def scalar(x,kind):return guarded(core.scalar,x,kind)
def declaration(x,kind):return guarded(losses.declaration,x,kind)
def model(x):
    closed(x,['profile','selected'],'model');scalar(x['profile'],'text');declaration(x['selected'],'boolean')
def period(x,assessment=False):
    closed(x,['start','end_exclusive']+(['activity_through'] if assessment else []),'interval')
    for v in x.values():scalar(v,'date')
def rational(x):return scalar(x,'rational')
def declarations(x,allowed,kind):
    need(type(x) is dict and set(x)<=set(allowed),'declaration_fields')
    for v in x.values():declaration(v,kind)

def information_kind(key):
    if key in annual.tax.info.GLOBAL_TEXT:return 'text'
    if key in annual.tax.info.GLOBAL_FINDINGS:return 'boolean'
    if key=='rate':return 'rational'
    if re.fullmatch(r'income/[^/]+/treatment',key):return 'text'
    if re.fullmatch(r'income/[^/]+/current_adjustment',key):return 'rational'
    if re.fullmatch(r'basis/[^/]+/(opening|closing)',key):return 'rational'
    if re.fullmatch(r'lease/[^/]+/[^/]+/(opening|closing)_(asset|liability)_tax_base',key):return 'rational'
    if re.fullmatch(r'lease/[^/]+/[^/]+/(deduction_timing|modification_gain_treatment)',key):return 'text'
    raise Invalid('unknown_information_field:'+key)

def validate_operation(op):
    closed(op,['kind','event'],'operation');kind=op['kind'];need(kind in SINGLE,'unsupported_operation')
    e=op['event']
    if kind=='native':
        guarded(older.validate_event,e);return e['event']['id']
    fields={
        'allocated_tax_payment':['id','date','amount','authorization','allocations'],
        'current_assessment':['id','mode','model','interval','information','allocations','loss_policy'],
        'deferred_assessment':['id','model','measurement','findings','recovery_capacity','items'],
        'provisional_carry':['id','model','next_period','findings']}[kind]
    closed(e,fields,'event');scalar(e['id'],'text')
    if kind=='allocated_tax_payment':
        scalar(e['date'],'date');rational(e['amount']);declaration(e['authorization'],'boolean')
        need(type(e['allocations']) is list,'allocations_list')
        for a in e['allocations']:
            closed(a,['vintage_id','amount'],'allocation');scalar(a['vintage_id'],'text');rational(a['amount'])
    elif kind=='current_assessment':
        need(e['mode'] in ['first','replace'],'assessment_mode');model(e['model']);period(e['interval'],True)
        need(type(e['information']) is dict,'information_map')
        for key,value in e['information'].items():declaration(value,information_kind(key))
        need(type(e['allocations']) is list,'adjustments_list')
        for a in e['allocations']:
            closed(a,['id','account','amount','origin'],'adjustment');scalar(a['id'],'text');scalar(a['account'],'text');rational(a['amount'])
            origin=a['origin'];need(type(origin) is dict,'adjustment_origin')
            if origin.get('kind')=='native_return':closed(origin,['kind','event_id'],'origin');scalar(origin['event_id'],'text')
            else:closed(origin,['kind','reference'],'origin');need(origin['kind']=='assumption','origin_kind');scalar(origin['reference'],'text')
        p=e['loss_policy'];closed(p,['model','utilization_cap','uses','generation'],'loss_policy');model(p['model']);declaration(p['utilization_cap'],'rational')
        need(type(p['uses']) is list,'loss_uses_list')
        for a in p['uses']:closed(a,['lot_id','amount'],'loss_use');scalar(a['lot_id'],'text');rational(a['amount'])
        if p['generation'] is not None:
            g=p['generation'];closed(g,['id','eligible','expiry'],'generation');scalar(g['id'],'text');declaration(g['eligible'],'boolean');guarded(losses.expiry,g['expiry'])
    elif kind=='deferred_assessment':
        model(e['model']);declarations(e['findings'],annual.deferred.FINDINGS,'boolean');declaration(e['recovery_capacity'],'rational')
        d=e['measurement'];closed(d,['at','state_sha256','jurisdiction','regime','account_bases','lease_bases'],'measurement')
        scalar(d['at'],'date');digest(d['state_sha256'])
        for key in ['jurisdiction','regime']:declaration(d[key],'text')
        for key in ['account_bases','lease_bases']:
            need(type(d[key]) is dict,'basis_map')
            for value in d[key].values():declaration(value,'rational')
        need(type(e['items']) is list,'items_list')
        for item in e['items']:
            closed(item,['id','tax_base','rate','recognized_deduction','recorded_dta','recorded_dtl','route','support'],'deferred_item')
            scalar(item['id'],'text')
            for key in ['tax_base','rate','recognized_deduction','recorded_dta','recorded_dtl']:declaration(item[key],'rational')
            declaration(item['route'],'text');declarations(item['support'],annual.deferred.SUPPORT,'boolean')
    else:
        model(e['model']);period(e['next_period']);declarations(e['findings'],annual.root.boundary.FINDINGS,'boolean')
    return e['id']

def digest(x):need(type(x) is str and len(x)==64 and all(c in '0123456789abcdef' for c in x),'digest')

def validate_program(program):
    guarded(lexical.bounded,program)
    closed(program,['profile','name','root_sha256','operations'],'program')
    need(program['profile']==PROFILE,'program_profile');guarded(older.identifier,program['name']);digest(program['root_sha256'])
    need(type(program['operations']) is list,'operations_list');seen=set()
    for op in program['operations']:
        key=validate_operation(op);need(key not in seen,'duplicate_operation_id');seen.add(key)
    return program

def from_request(body,name='annual_book'):
    guarded(annual.caller.bounded,body);closed(body,['profile','root_request','root_sha256','operations'],'request')
    need(body['profile']==annual.PROFILE,'request_profile');need(body['root_sha256']==annual.book.digest(body['root_request']),'root_digest')
    result={'profile':PROFILE,'name':name,'root_sha256':body['root_sha256'],'operations':deepcopy(body['operations'])}
    validate_program(result);return result

def flatten(op):
    kind=op['kind'];e=op['event']
    if kind=='native':return e['event']['id'],{'module':e['module'],'native_event':deepcopy(e['event'])}
    d={k:deepcopy(v) for k,v in e.items() if k!='id'}
    if kind=='current_assessment':
        p=d.pop('loss_policy');d.update(loss_model=p['model'],utilization_cap=p['utilization_cap'],uses=p['uses'],generation=p['generation'])
    return e['id'],d

def assemble(kind,identity,data):
    d=deepcopy(data)
    if kind=='native':
        need(d['native_event']['id']==identity,'native_header_identity')
        e={'profile':annual.book.EVENT,'module':d['module'],'event':d['native_event']}
    else:
        if kind=='current_assessment':
            d['loss_policy']={'model':d.pop('loss_model'),'utilization_cap':d.pop('utilization_cap'),
                'uses':d.pop('uses'),'generation':d.pop('generation')}
        e={'id':identity,**d}
    op={'kind':kind,'event':e};validate_operation(op);return op

def parse(source):
    source=guarded(lexical.source_text,source);stage='header';program=None;data=None;spans={'operations':[]}
    for number,raw in enumerate(source.split('\n'),1):
        line=raw.removesuffix('\r')
        if not line.strip(' \t'):continue
        try:
            reader=syntax.Reader(lexical.tokens(line));command=reader.take('word')
            if stage=='header':
                need(command=='annual_program','header_required');program={'profile':reader.string(),'name':reader.string(),'operations':[]}
                spans['program']={'start_line':number};stage='import'
            elif stage=='import':
                need(command=='import_root','import_required');program['root_sha256']=reader.string();spans['import_root']={'start_line':number,'end_line':number};stage='operations'
            elif stage=='operations':need(command=='operations','operations_required');stage='operation_header'
            elif stage=='operation_header':
                if command=='end_operations':stage='end'
                else:
                    need(command=='operation','operation_required');kind=reader.string();identity=reader.string();need(kind in SINGLE,'unsupported_operation')
                    data={field:{} for field in MAP.get(kind,{}).values()};data.update({field:[] for field in LIST.get(kind,{}).values()})
                    declared=set();span={'id':identity,'kind':kind,'start_line':number,'field_lines':{}};stage='operation'
            elif stage=='operation':
                if command=='end_operation':
                    need(declared==set(SINGLE[kind]),'required_operation_fields')
                    program['operations'].append(assemble(kind,identity,data));span['end_line']=number;spans['operations'].append(span);stage='operation_header'
                elif command in SINGLE[kind]:
                    need(command not in declared,'duplicate_field:'+command);declared.add(command);data[command]=reader.take('value');span['field_lines'][command]=[number]
                elif command in MAP.get(kind,{}):
                    key=reader.string();field=MAP[kind][command];need(key not in data[field],'duplicate_map_key:'+key)
                    data[field][key]=reader.take('value');span['field_lines'].setdefault(command,[]).append(number)
                elif command in LIST.get(kind,{}):
                    data[LIST[kind][command]].append(reader.take('value'));span['field_lines'].setdefault(command,[]).append(number)
                else:raise Invalid('unsupported_field:'+command)
            elif stage=='end':need(command=='end_program','end_program_required');stage='done';spans['program']['end_line']=number
            else:raise Invalid('declaration_after_end')
            reader.finish()
        except (ValueError,TypeError,KeyError,AttributeError,RecursionError,OverflowError) as exc:
            raise Invalid('line '+str(number)+': '+str(exc)[:350]) from exc
    need(stage=='done','incomplete_program:'+stage);validate_program(program);return program,spans

def lower(source):return parse(source)[0]
def token(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'))

def render(program):
    validate_program(program)
    lines=['annual_program '+token(PROFILE)+' '+token(program['name'])+';',
        'import_root '+token(program['root_sha256'])+';','operations;']
    for op in program['operations']:
        kind=op['kind'];identity,data=flatten(op);lines.append('operation '+token(kind)+' '+token(identity)+';')
        lines.extend(k+' '+token(data[k])+';' for k in SINGLE[kind])
        for command,field in MAP.get(kind,{}).items():
            lines.extend(command+' '+token(k)+' '+token(v)+';' for k,v in sorted(data[field].items()))
        for command,field in LIST.get(kind,{}).items():lines.extend(command+' '+token(v)+';' for v in data[field])
        lines.append('end_operation;')
    lines.extend(['end_operations;','end_program;']);source='\n'.join(lines)+'\n';guarded(lexical.source_text,source);return source

def compile_program(program,imports):
    protected();validate_program(program);need(type(imports) is dict,'imports_map');key=program['root_sha256']
    need(key in imports,'unresolved_root_import');origin=imports[key];guarded(annual.caller.bounded,origin)
    closed(origin,['profile','boundary_request','boundary_sha256','operations'],'root_request')
    need(origin['profile']==annual.root.PROFILE,'root_profile');need(annual.book.digest(origin)==key,'root_digest')
    need(origin['boundary_sha256']==annual.book.digest(origin['boundary_request']),'boundary_digest')
    request=annual.request(origin,program['operations']);guarded(annual.caller.bounded,request)
    return {'profile':PROFILE,'program':deepcopy(program),'request':request,
        'program_sha256':annual.book.digest(program),'request_sha256':annual.book.digest(request),
        'source_text_sha256':None,'source_spans':None,'executed':False}

def compile_text(source,imports):
    source=guarded(lexical.source_text,source);program,spans=parse(source);result=compile_program(program,imports)
    result.update(source_text_sha256=sha256(source.encode('utf-8')).hexdigest(),source_spans=spans);return result

def execute_program(program,imports):return annual.run(compile_program(program,imports)['request'])
def execute_text(source,imports):return annual.run(compile_text(source,imports)['request'])
