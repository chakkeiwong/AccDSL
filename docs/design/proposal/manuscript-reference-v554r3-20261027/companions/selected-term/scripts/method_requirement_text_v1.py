"""Named requirement declarations and strict exchange; core semantics are reused."""
import json
import re
import method_requirements_v1 as core

EXCHANGE = 'MethodRequirementExchange/1'


def unique_object(pairs):
    value = {}
    for key, item in pairs:
        core.need(key not in value, 'duplicate_json_key:' + key)
        value[key] = item
    return value


def nonfinite(value):
    raise core.Invalid('nonfinite_json:' + value)


DECODER = json.JSONDecoder(object_pairs_hook=unique_object, parse_constant=nonfinite)


def validate_exchange(value):
    core.closed(value, ['profile','definition','selected_digest','values',
                        'available_capabilities'], 'exchange')
    core.need(value['profile'] == EXCHANGE, 'exchange_profile')
    core.need(len(core.canonical(value)) <= core.MAX_BYTES, 'exchange_size_limit')
    core.validate_manifest(value['definition'])
    core.need(value['selected_digest'] == core.digest(value['definition']), 'selection_hash')
    core.validate_values(value['definition'], value['values'])
    core.identifiers(value['available_capabilities'], 'available_capabilities')
    return value


def decode_exchange(text):
    core.need(type(text) is str and len(text.encode('utf-8')) <= core.MAX_BYTES,
              'exchange_text_limit')
    return validate_exchange(DECODER.decode(text))


def assess_exchange(value):
    validate_exchange(value)
    key = value['selected_digest']
    return core.assess({key:value['definition']}, key, value['values'],
                       value['available_capabilities'])


def tokens(line):
    result, pos = [], 0
    while pos < len(line):
        ch = line[pos]
        if ch in ' \t\r':
            pos += 1
            continue
        if ch in '();':
            result.append((ch,ch))
            pos += 1
        elif ch in '"[{' or ch in '-0123456789':
            value, end = DECODER.raw_decode(line,pos)
            result.append(('value',value))
            pos = end
        else:
            word = re.match(r'[A-Za-z_][A-Za-z0-9_]*',line[pos:])
            core.need(word is not None, 'unexpected_token')
            value = word.group(0)
            pos += len(value)
            if value in ['true','false','null']:
                result.append(('value',{'true':True,'false':False,'null':None}[value]))
            else:
                result.append(('word',value))
        core.need(len(result) <= core.MAX_NODES*12, 'token_limit')
    return result


class Reader:
    def __init__(self, items):
        self.items = items
        self.pos = 0
        self.nodes = 0

    def take(self, kind, exact=None):
        core.need(self.pos < len(self.items), 'missing_token')
        actual, value = self.items[self.pos]
        core.need(actual == kind and (exact is None or value == exact), 'token_kind:' + kind)
        self.pos += 1
        return value

    def string(self):
        value = self.take('value')
        core.text(value,'string_token')
        return value

    def expression(self, depth=0):
        self.nodes += 1
        core.need(depth <= core.MAX_DEPTH and self.nodes <= core.MAX_NODES, 'expression_limit')
        self.take('(')
        op = self.take('word')
        if op == 'ref':
            value = {'op':op,'id':self.string()}
        elif op == 'const':
            kind = self.take('word')
            context = self.take('value')
            value = {'op':op,'type':{'kind':kind,'context':context},'value':self.take('value')}
        elif op in ['eq','le','lt','add','sub']:
            value = {'op':op,'left':self.expression(depth+1),'right':self.expression(depth+1)}
        elif op == 'not':
            value = {'op':op,'arg':self.expression(depth+1)}
        elif op in ['all','any']:
            args = []
            while self.pos < len(self.items) and self.items[self.pos][0] == '(':
                args.append(self.expression(depth+1))
            core.need(bool(args),'empty_boolean_expression')
            value = {'op':op,'args':args}
        else:
            raise core.Invalid('unknown_operator:' + op)
        self.take(')')
        return value

    def finish(self):
        self.take(';')
        core.need(self.pos == len(self.items),'trailing_tokens')


def lower(text):
    core.need(type(text) is str and len(text.encode('utf-8')) <= core.MAX_BYTES,
              'authoring_text_limit')
    definition, selection, values, available = None, None, {}, []
    ended, count = False, 0
    for number, line in enumerate(text.split('\n'),1):
        if not line.strip():
            continue
        count += 1
        core.need(count <= core.MAX_NODES,'declaration_limit')
        try:
            core.need(not ended,'declaration_after_end')
            r = Reader(tokens(line))
            command = r.take('word')
            if definition is None:
                core.need(command == 'requirements','header_required')
                definition = {'profile':r.string(),'method_id':r.string(),'version':r.string(),
                              'inputs':{},'requirements':[],'capabilities':[],
                              'residual_prerequisites':[]}
            elif command == 'input':
                key, kind, role = r.string(), r.take('word'), r.take('word')
                core.need(key not in definition['inputs'],'duplicate_input')
                definition['inputs'][key] = {'type':{'kind':kind,'context':r.take('value')},
                                             'role':role,'source_ref':r.string()}
            elif command == 'require':
                req = {'id':r.string(),'on_false':r.take('word'),'on_unknown':r.take('word'),
                       'requires':r.take('value'),'admission_refs':r.take('value')}
                req['predicate'] = r.expression()
                definition['requirements'].append(req)
            elif command in ['capability','residual']:
                key = 'capabilities' if command == 'capability' else 'residual_prerequisites'
                definition[key].append(r.string())
            elif command == 'select':
                core.need(selection is None,'duplicate_selection')
                selection = r.string()
            elif command == 'bind':
                key, status = r.string(), r.take('word')
                core.need(key not in values,'duplicate_binding')
                core.need(status in ['known','unknown'],'binding_status')
                values[key] = {'status':status,
                               ('value' if status == 'known' else 'reason'):r.take('value')}
            elif command == 'available':
                available.append(r.string())
            elif command == 'end_requirements':
                ended = True
            else:
                raise core.Invalid('unknown_declaration:' + command)
            r.finish()
        except (ValueError, TypeError, RecursionError) as exc:
            raise core.Invalid('line '+str(number)+': '+str(exc)[:200]) from exc
    core.need(definition is not None and selection is not None and ended,'incomplete_document')
    return validate_exchange({'profile':EXCHANGE,'definition':definition,'selected_digest':selection,
                              'values':values,'available_capabilities':available})


def json_token(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)


def render_expression(node):
    op = node['op']
    if op == 'ref':
        args = [json_token(node['id'])]
    elif op == 'const':
        args = [node['type']['kind'],json_token(node['type']['context']),json_token(node['value'])]
    elif op in ['all','any']:
        args = [render_expression(child) for child in node['args']]
    elif op == 'not':
        args = [render_expression(node['arg'])]
    else:
        args = [render_expression(node['left']),render_expression(node['right'])]
    return '('+' '.join([op]+args)+')'


def render(exchange):
    validate_exchange(exchange)
    d = exchange['definition']
    rows = ['requirements '+' '.join(json_token(d[k]) for k in ['profile','method_id','version'])+';']
    for key,item in sorted(d['inputs'].items()):
        rows.append('input '+' '.join([json_token(key),item['type']['kind'],item['role'],
                    json_token(item['type']['context']),json_token(item['source_ref'])])+';')
    for req in d['requirements']:
        rows.append('require '+' '.join([json_token(req['id']),req['on_false'],req['on_unknown'],
                    json_token(req['requires']),json_token(req['admission_refs']),
                    render_expression(req['predicate'])])+';')
    for command,key in [('capability','capabilities'),('residual','residual_prerequisites')]:
        rows.extend(command+' '+json_token(value)+';' for value in d[key])
    rows.append('select '+json_token(exchange['selected_digest'])+';')
    for key,item in sorted(exchange['values'].items()):
        value = item['value'] if item['status']=='known' else item['reason']
        rows.append('bind '+' '.join([json_token(key),item['status'],json_token(value)])+';')
    rows.extend('available '+json_token(value)+';' for value in exchange['available_capabilities'])
    rows.append('end_requirements;')
    output = '\n'.join(rows)+'\n'
    core.need(len(output.encode('utf-8')) <= core.MAX_BYTES,'rendered_text_limit')
    return output
