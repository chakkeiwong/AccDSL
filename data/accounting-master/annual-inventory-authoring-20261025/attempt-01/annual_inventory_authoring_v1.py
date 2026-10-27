"""Pure authoring for the optional full-state annual inventory program."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json
import annual_program_authoring_v1 as base
import annual_inventory_program_v1 as runtime

annual = runtime.annual
lexical = base.lexical
syntax = base.syntax
Invalid = base.Invalid
need = base.need
guarded = base.guarded
ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / 'data/accounting-master/annual-inventory-authoring-20261025'
LOCK = '75cb41024fbc8550760e4959b1b00875fd9cf383638da3d8b557b9be92ec53bd'
PROFILE = 'AnnualInventoryAuthoring/1'
SINGLE = {**deepcopy(base.SINGLE), 'partial_inventory_sale':
          ['sale_profile', 'date', 'method', 'lot_id', 'sold_units', 'proceeds']}
MAP = {**deepcopy(base.MAP), 'partial_inventory_sale': {'finding': 'findings'}}
LIST = deepcopy(base.LIST)


def protected():
    raw = (HERE/'source-lock.json').read_bytes()
    need(sha256(raw).hexdigest() == LOCK, 'source_lock_changed')
    for name, expected in json.loads(raw).items():
        need(sha256((ROOT/name).read_bytes()).hexdigest() == expected, 'protected_source_changed:' + name)
    base.protected(); runtime.protected()


def validate_operation(operation):
    base.closed(operation, ['kind', 'event'], 'operation')
    if operation['kind'] != 'partial_inventory_sale':
        return base.validate_operation(operation)
    e = operation['event']
    base.closed(e, ['profile', 'id', 'date', 'method', 'lot_id', 'sold_units', 'proceeds', 'findings'], 'sale')
    need(e['profile'] == runtime.partial.PROFILE, 'sale_profile')
    for key in ['id', 'method', 'lot_id']:
        base.scalar(e[key], 'text')
    base.scalar(e['date'], 'date')
    for key in ['sold_units', 'proceeds']:
        base.rational(e[key])
    base.closed(e['findings'], runtime.partial.FINDINGS, 'findings')
    for value in e['findings'].values():
        base.declaration(value, 'boolean')
    return e['id']


def validate_program(program):
    guarded(lexical.bounded, program)
    base.closed(program, ['profile', 'name', 'root_sha256', 'operations'], 'program')
    need(program['profile'] == PROFILE, 'program_profile')
    guarded(base.older.identifier, program['name']); base.digest(program['root_sha256'])
    need(type(program['operations']) is list, 'operations_list'); seen = set()
    for operation in program['operations']:
        identity = validate_operation(operation)
        need(identity not in seen, 'duplicate_operation_id'); seen.add(identity)
    return program


def from_request(body, name='annual_inventory_book'):
    guarded(annual.caller.bounded, body)
    base.closed(body, ['profile', 'root_request', 'root_sha256', 'operations'], 'request')
    need(body['profile'] == runtime.PROFILE, 'request_profile')
    need(body['root_sha256'] == annual.book.digest(body['root_request']), 'root_digest')
    program = {'profile': PROFILE, 'name': name, 'root_sha256': body['root_sha256'],
               'operations': deepcopy(body['operations'])}
    validate_program(program)
    return program


def flatten(operation):
    if operation['kind'] != 'partial_inventory_sale':
        return base.flatten(operation)
    data = deepcopy(operation['event']); identity = data.pop('id')
    data['sale_profile'] = data.pop('profile')
    return identity, data


def assemble(kind, identity, data):
    if kind != 'partial_inventory_sale':
        return base.assemble(kind, identity, data)
    event = deepcopy(data); event['profile'] = event.pop('sale_profile')
    event['id'] = identity
    operation = {'kind': kind, 'event': event}
    validate_operation(operation)
    return operation


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

def compile_program(program, imports):
    protected(); validate_program(program)
    need(type(imports) is dict, 'imports_map'); key = program['root_sha256']
    need(key in imports, 'unresolved_root_import'); origin = imports[key]
    guarded(annual.caller.bounded, origin)
    base.closed(origin, ['profile', 'boundary_request', 'boundary_sha256', 'operations'], 'root_request')
    need(origin['profile'] == annual.root.PROFILE, 'root_profile')
    need(annual.book.digest(origin) == key, 'root_digest')
    need(origin['boundary_sha256'] == annual.book.digest(origin['boundary_request']), 'boundary_digest')
    request = runtime.request(origin, program['operations'])
    guarded(annual.caller.bounded, request)
    return {'profile': PROFILE, 'program': deepcopy(program), 'request': request,
            'program_sha256': annual.book.digest(program), 'request_sha256': annual.book.digest(request),
            'source_text_sha256': None, 'source_spans': None, 'executed': False}


def compile_text(source, imports):
    source = guarded(lexical.source_text, source)
    program, spans = parse(source)
    result = compile_program(program, imports)
    result.update(source_text_sha256=sha256(source.encode('utf-8')).hexdigest(), source_spans=spans)
    return result


def execute_program(program, imports):
    return runtime.run(compile_program(program, imports)['request'])


def execute_text(source, imports):
    return runtime.run(compile_text(source, imports)['request'])
