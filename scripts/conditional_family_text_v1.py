"""Strict data-only declarations for complete conditional family definitions."""
from copy import deepcopy
import json
import re
import method_requirement_text_v1 as lexical
import joint_measurement_constraints_v1 as joint
import temporal_measurement_constraints_v1 as temporal
import conditional_history_family_v1 as monetary
import typed_affine_history_v1 as typed
import history_measurement_attachment_v1 as attachment

core = joint.core
EXCHANGE = 'ConditionalFamilyExchange/1'
MODULES = {m.PROFILE:m for m in [joint,temporal,monetary,typed,attachment]}
HISTORIES = {monetary.PROFILE,typed.PROFILE}
SINGLETONS = {'scope','value_type','opening_date','dates','balance_premise','obligations'}
MAPS = {'account':'accounts','memory':'memory','template':'templates',
        'observation':'observations','binding':'bindings'}
LISTS = {'event':'events','measurement':'measurements','state_constraint':'state_constraints',
         'equation':'equations','relation':'relations'}
MAX_NODES = 20000


def reject_number(value):
    raise core.Invalid('noninteger_json_number:'+value[:40])


def integer(value):
    core.need(len(value) <= 12, 'integer_token_limit')
    return int(value)


DECODER = json.JSONDecoder(object_pairs_hook=lexical.unique_object,
    parse_constant=reject_number, parse_float=reject_number, parse_int=integer)


def source_text(source):
    core.need(type(source) in [str,bytes], 'text_or_bytes_required')
    if type(source) is bytes:
        core.need(len(source) <= core.MAX_BYTES, 'source_size_limit')
        try: source = source.decode('utf-8','strict')
        except UnicodeError as exc: raise core.Invalid('invalid_utf8') from exc
    try: encoded = source.encode('utf-8','strict')
    except UnicodeError as exc: raise core.Invalid('invalid_unicode_scalar') from exc
    core.need(len(encoded) <= core.MAX_BYTES, 'source_size_limit')
    core.need(not source.startswith('\ufeff'), 'bom_not_supported')
    core.need(not any(c in source for c in '\x85\u2028\u2029'), 'unicode_line_separator')
    core.need(re.search(r'\r(?!\n)',source) is None, 'bare_carriage_return')
    depth, quoted, escaped = 0, False, False
    for ch in source:
        if quoted:
            if escaped: escaped = False
            elif ch == '\\': escaped = True
            elif ch == '"': quoted = False
        elif ch == '"': quoted = True
        elif ch in '[{':
            depth += 1
            core.need(depth <= core.MAX_DEPTH, 'json_nesting_limit')
        elif ch in ']}':
            depth -= 1
            core.need(depth >= 0, 'json_nesting_balance')
    core.need(depth == 0 and not quoted, 'incomplete_json_token')
    return source


def bounded(value):
    stack = [(value,0)]
    count = 0
    while stack:
        item, depth = stack.pop(); count += 1
        core.need(count <= MAX_NODES and depth <= core.MAX_DEPTH, 'exchange_structure_limit')
        if type(item) is dict:
            for key, child in item.items():
                core.need(type(key) is str, 'json_key_type')
                stack.extend([(key,depth+1),(child,depth+1)])
        elif type(item) is list:
            stack.extend((child,depth+1) for child in item)
        elif type(item) is str:
            core.need(len(item) <= core.MAX_SCALAR, 'string_limit')
            core.need(not any(ord(c)<32 or ord(c)==127 or 0xD800<=ord(c)<=0xDFFF
                              or c in '\x85\u2028\u2029' for c in item), 'invalid_string_scalar')
        else:
            core.need(item is None or type(item) is bool or
                      type(item) is int and len(str(item)) <= 12, 'json_scalar_type')
    core.need(len(core.canonical(value)) <= core.MAX_BYTES, 'exchange_size_limit')


def validate_definition(definition, budget):
    bounded(definition); bounded(budget)
    core.need(type(definition) is dict and type(definition.get('profile')) is str,
              'definition_profile')
    profile = definition['profile']
    core.need(profile in MODULES, 'unsupported_profile')
    if profile == joint.PROFILE: joint.validate(definition,budget)
    elif profile == temporal.PROFILE: temporal.lower(definition,budget)
    elif profile == monetary.PROFILE: monetary.validate(definition,budget)
    elif profile == typed.PROFILE: typed.validate_and_lower(definition,budget)
    else: attachment.prepare(definition,budget)
    return definition


def validate_exchange(value):
    bounded(value)
    core.closed(value,['profile','definition','selected_digest','budget'],'family_exchange')
    core.need(value['profile'] == EXCHANGE, 'exchange_profile')
    validate_definition(value['definition'],value['budget'])
    core.need(value['selected_digest'] == core.digest(value['definition']), 'selection_hash')
    return json.loads(core.canonical(value))


def exchange(definition,budget):
    return validate_exchange({'profile':EXCHANGE,'definition':deepcopy(definition),
        'selected_digest':core.digest(definition),'budget':deepcopy(budget)})


def decode_exchange(source):
    source = source_text(source)
    try: value = DECODER.decode(source)
    except (ValueError,RecursionError) as exc: raise core.Invalid('exchange_json:'+str(exc)[:150]) from exc
    return validate_exchange(value)


def tokens(line):
    out, pos = [], 0
    while pos < len(line):
        if line[pos] in ' \t': pos += 1; continue
        if line[pos] == ';': out.append((';',';')); pos += 1
        elif line[pos] in '"[{-0123456789' or any(line.startswith(x,pos) for x in ['null','true','false']):
            value,end = DECODER.raw_decode(line,pos)
            bounded(value);out.append(('value',value));pos=end
        else:
            match = re.match(r'[A-Za-z_][A-Za-z0-9_]*',line[pos:])
            core.need(match is not None, 'unexpected_token')
            word=match.group(0);out.append(('word',word));pos += len(word)
        core.need(len(out)<=32,'declaration_token_limit')
    return out


def empty_family(profile):
    core.need(profile in MODULES, 'unsupported_profile')
    if profile == joint.PROFILE: return {'profile':profile,'observations':{},'equations':[]}
    if profile == temporal.PROFILE: return {'profile':profile,'observations':{},'relations':[]}
    if profile == attachment.PROFILE: return {'profile':profile,'bindings':{}}
    result={'profile':profile,'accounts':{},'memory':{},'templates':{},'events':[],'measurements':[]}
    if profile == typed.PROFILE: result['state_constraints']=[]
    return result


def lower(source):
    source=source_text(source)
    families, refs, budget = {}, {}, None
    active, name, selected = None, None, None
    started, ended, declarations = False, False, 0
    for number, raw in enumerate(source.split('\n'),1):
        line=raw[:-1] if raw.endswith('\r') else raw
        if not line.strip(' \t'): continue
        declarations += 1
        core.need(declarations <= core.MAX_NODES, 'declaration_limit')
        try:
            core.need(not ended,'declaration_after_end')
            r=lexical.Reader(tokens(line));command=r.take('word')
            if not started:
                core.need(command=='conditional_exchange','header_required')
                core.need(r.string()==EXCHANGE,'exchange_profile');started=True
            elif active is not None:
                profile=active['profile']
                if command=='end_family':
                    bounded(active)
                    families[name]=active;active=None
                elif command in SINGLETONS and (profile in HISTORIES or
                                                profile==attachment.PROFILE and command=='obligations'):
                    core.need(command not in active,'duplicate_singleton:'+command)
                    active[command]=r.take('value')
                elif command in MAPS and MAPS[command] in active:
                    key=r.string();field=MAPS[command]
                    core.need(key not in active[field],'duplicate_declaration:'+key)
                    active[field][key]=r.take('value')
                elif command in LISTS and LISTS[command] in active:
                    active[LISTS[command]].append(r.take('value'))
                elif command in ['use_history','use_measurements'] and profile==attachment.PROFILE:
                    field='history' if command=='use_history' else 'measurements'
                    core.need(field not in active,'duplicate_parent')
                    parent=r.string();core.need(parent in families,'unavailable_parent')
                    active[field]=deepcopy(families[parent]);refs[name].append(parent)
                else: raise core.Invalid('unsupported_declaration:'+command)
            elif command=='budget':
                core.need(budget is None and not families and selected is None,'duplicate_or_late_budget')
                budget=r.take('value')
                core.closed(budget,joint.BUDGET_FIELDS,'budget')
                joint.solver.Budget(**budget)
            elif command=='family':
                core.need(budget is not None and selected is None,'budget_required_or_selection_closed')
                name=r.string();core.need(name not in families,'duplicate_family')
                active=empty_family(r.string());refs[name]=[]
            elif command=='select':
                core.need(selected is None,'duplicate_selection')
                selected=(r.string(),r.string())
                core.need(selected[0] in families,'unavailable_selection')
            elif command=='end_exchange':
                core.need(selected is not None,'selection_required');ended=True
            else: raise core.Invalid('unsupported_declaration:'+command)
            r.finish()
        except (ValueError,TypeError,KeyError,AttributeError,RecursionError,OverflowError) as exc:
            raise core.Invalid('line '+str(number)+': '+str(exc)[:200]) from exc
    core.need(started and ended and active is None,'incomplete_exchange')
    reachable=set()
    def visit(key):
        if key not in reachable:
            reachable.add(key)
            for parent in refs[key]:visit(parent)
    visit(selected[0])
    core.need(reachable==set(families),'unused_family')
    return validate_exchange({'profile':EXCHANGE,'definition':families[selected[0]],
        'selected_digest':selected[1],'budget':budget})


def assess_exchange(value):
    value=validate_exchange(value)
    return MODULES[value['definition']['profile']].assess(value['definition'],value['budget'])


def assess_source(source):
    return assess_exchange(lower(source))


def render(value):
    value=validate_exchange(value)
    def js(x):return json.dumps(x,ensure_ascii=False,separators=(',',':'),sort_keys=True,allow_nan=False)
    def line(command,*values):return command+(' '+' '.join(js(x) for x in values) if values else '')+';'
    out=[line('conditional_exchange',EXCHANGE),line('budget',value['budget'])]
    def emit(name,d):
        profile=d['profile']
        if profile==attachment.PROFILE:
            emit(name+'_history',d['history']);emit(name+'_measurements',d['measurements'])
        out.append(line('family',name,profile))
        if profile in HISTORIES:
            for field in ['scope','value_type','opening_date','dates','balance_premise','obligations']:
                out.append(line(field,d[field]))
            commands=['account','memory','template','event','measurement']
            if profile==typed.PROFILE:commands.append('state_constraint')
        elif profile==attachment.PROFILE:
            out.extend([line('use_history',name+'_history'),line('use_measurements',name+'_measurements'),
                        line('obligations',d['obligations'])]);commands=['binding']
        else:commands=['observation','equation' if profile==joint.PROFILE else 'relation']
        for command in commands:
            if command in MAPS:
                for key,item in sorted(d[MAPS[command]].items()):out.append(line(command,key,item))
            else:
                for item in d[LISTS[command]]:out.append(line(command,item))
        out.append(line('end_family'))
    emit('selected',value['definition'])
    out.extend([line('select','selected',value['selected_digest']),line('end_exchange')])
    result='\n'.join(out)+'\n';source_text(result)
    return result
