"""Bounded command text over explicit hashed company definitions."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json
import re

import conditional_family_text_v1 as lexical
import method_requirement_text_v1 as syntax
import declared_company_program_v1 as runner

PROFILE = 'DeclaredCompanyText/1'
IMPORTS = ('opening', 'schemas', 'registry', 'mapping')
core = runner.core
PINS = {
    'declared_company_program_v1.py': '3c3a020fcc0bf6422d967725a3a4de53f8ebd89195575124b2db32156ed9e430',
    'conditional_family_text_v1.py': 'beab3057dd22e37eedec5fdae6dc3dc548a2608e2e399541561a2694965c2ed6',
    'method_requirement_text_v1.py': 'bbc5bfa49da6b8b511dcecdbbbb1907ca5cb8a679f5a7f878a83db123f52f28b',
}


class Invalid(ValueError):
    def __init__(self, reason, stage='parse', line=None, column=None, offset=None):
        self.reason, self.stage = str(reason)[:350], stage
        self.line, self.column, self.offset = line, column, offset
        location = '' if line is None else f' line {line}, column {column}, offset {offset}'
        super().__init__(stage + location + ': ' + self.reason)


def need(ok, reason):
    if not ok:
        raise Invalid(reason)


def protected():
    root = Path(__file__).resolve().parent
    for name, expected in PINS.items():
        need(sha256((root / name).read_bytes()).hexdigest() == expected, 'dependency_hash:' + name)
    runner.protected()


def text(value, label):
    need(type(value) is str and bool(value.strip()), label)
    lexical.bounded(value)
    return value


def value_token(value):
    need(type(value) in (str, bool), 'string_or_boolean_required')
    lexical.bounded(value)
    return value


def digest_token(value):
    need(type(value) is str and re.fullmatch('[0-9a-f]{64}', value) is not None, 'sha256_required')
    return value


class Reader(syntax.Reader):
    def __init__(self, line):
        # The checked lexer defines token semantics; retain their source offsets.
        self.columns = []
        items, pos = [], 0
        while pos < len(line):
            if line[pos] in ' \t':
                pos += 1; continue
            self.columns.append(pos)
            try:
                if line[pos] == ';':
                    items.append((';', ';')); pos += 1
                elif line[pos] in '"[{-0123456789' or any(line.startswith(x, pos) for x in ['null', 'true', 'false']):
                    value, end = lexical.DECODER.raw_decode(line, pos)
                    lexical.bounded(value); items.append(('value', value)); pos = end
                else:
                    match = re.match('[A-Za-z_][A-Za-z0-9_]*', line[pos:])
                    need(match is not None, 'unexpected_token')
                    items.append(('word', match.group(0))); pos += len(match.group(0))
                need(len(items) <= 32, 'declaration_token_limit')
            except Exception as exc:
                raise Invalid(str(exc), column=pos + 1, offset=pos) from exc
        need(items == lexical.tokens(line), 'lexer_correspondence')
        self.end_column = len(line)
        super().__init__(items)

    def word(self, word):
        return self.take('word', word)

    def string(self):
        return text(self.take('value'), 'nonempty_string_required')

    def scalar(self):
        return value_token(self.take('value'))

    def at(self):
        return self.columns[self.pos] if self.pos < len(self.columns) else self.end_column


def parse(source):
    try:
        source = lexical.source_text(source)
    except Exception as exc:
        raise Invalid(str(exc), line=1, column=1, offset=0) from exc
    author = None; active = None; stage = 'header'; import_index = 0
    spans = {'imports': {}, 'commands': []}; absolute = 0; declarations = 0
    for number, raw in enumerate(source.splitlines(keepends=True), 1):
        line = raw.removesuffix('\n').removesuffix('\r')
        start = absolute; absolute += len(raw)
        if not line.strip(' \t'):
            continue
        reader = None
        location = {'line': number, 'column': 1, 'offset': start}
        try:
            declarations += 1; need(declarations <= core.MAX_NODES, 'declaration_limit')
            reader = Reader(line); command = reader.take('word')
            if stage == 'header':
                need(command == 'company_program', 'header_required')
                need(reader.string() == PROFILE, 'profile')
                author = {'profile': PROFILE, 'name': reader.string(), 'imports': {}, 'commands': []}
                spans['program'] = dict(location); stage = 'imports'
            elif stage == 'imports':
                kind = IMPORTS[import_index]
                need(command == 'import_' + kind, 'required_import:' + kind)
                author['imports'][kind] = digest_token(reader.string())
                spans['imports'][kind] = dict(location); import_index += 1
                if import_index == len(IMPORTS): stage = 'commands'
            elif stage == 'commands':
                if command == 'end_program':
                    need(bool(author['commands']), 'commands_required'); stage = 'done'
                    spans['program']['end_line'] = number
                else:
                    need(command in ['event', 'report', 'carry'], 'command_kind')
                    need(len(author['commands']) < runner.MAX_COMMANDS, 'command_limit')
                    ident = reader.string()
                    if command == 'event':
                        reader.word('method'); key = reader.string(); reader.word('on'); day = reader.string()
                        core.scalar(day, 'date')
                        active = {'kind': command, 'method_key': key, 'event': {'id': ident, 'date': day, 'inputs': {}}}
                    else:
                        reader.word('at'); day = reader.string(); core.scalar(day, 'date')
                        active = {'kind': command, 'id': ident, 'cutoff': day, 'equity_movements': [], 'notes': []}
                        if command == 'carry':active['memory_policies'] = {}
                    span = {**location, 'id': ident, 'kind': command, 'fields': []}; stage = 'block'
            elif stage == 'block':
                kind = active['kind']
                if command == 'end_' + kind:
                    if kind == 'carry':
                        need('retained_account' in active and 'next_end_exclusive' in active, 'required_carry_fields')
                    author['commands'].append(active); span['end_line'] = number
                    spans['commands'].append(span); active = None; stage = 'commands'
                else:
                    span['fields'].append({**location, 'declaration': command})
                    if kind == 'event':
                        need(command == 'input', 'event_input_required')
                        key = reader.string(); need(key not in active['event']['inputs'], 'duplicate_input:' + key)
                        status = reader.take('word'); need(status in ['known', 'unknown'], 'input_status')
                        value = {'status': status, 'value': reader.scalar()} if status == 'known' else {'status': status, 'reason': reader.string()}
                        reader.word('because'); provenance = reader.string()
                        active['event']['inputs'][key] = {'value': value, 'provenance': provenance}
                    elif command == 'equity':
                        row = {'id': reader.string()}; reader.word('event'); row['event_id'] = reader.string()
                        reader.word('on'); row['date'] = reader.string(); core.scalar(row['date'], 'date')
                        reader.word('account'); row['account'] = reader.string(); reader.word('amount')
                        row['amount'] = reader.string(); runner.reports.number(row['amount'])
                        reader.word('because'); row['description'] = reader.string()
                        active['equity_movements'].append(row)
                    elif command == 'note':
                        row = {'id': reader.string()}; reader.word('label'); row['label'] = reader.string()
                        reader.word('status'); row['status'] = reader.string()
                        need(row['status'] in ['missing', 'unsupported', 'unresolved'], 'note_status')
                        reader.word('because'); row['reason'] = reader.string(); active['notes'].append(row)
                    elif kind == 'carry' and command in ['retained_account', 'next_end_exclusive']:
                        need(command not in active, 'duplicate_field:' + command); active[command] = reader.string()
                        if command == 'next_end_exclusive':core.scalar(active[command], 'date')
                    elif kind == 'carry' and command == 'memory':
                        pointer = reader.string(); need(pointer not in active['memory_policies'], 'duplicate_memory:' + pointer)
                        policy = {'kind': reader.take('word')}
                        need(policy['kind'] in ['preserve', 'next_period_start', 'reset'], 'memory_policy_kind')
                        if policy['kind'] == 'reset':policy['value'] = reader.scalar()
                        reader.word('because'); policy['provenance'] = reader.string()
                        active['memory_policies'][pointer] = policy
                    else:
                        raise Invalid('unsupported_field:' + command)
            else:
                raise Invalid('declaration_after_end')
            reader.finish()
        except Exception as exc:
            column = reader.at() if reader is not None else (getattr(exc, 'offset', None) or 0)
            raise Invalid(getattr(exc, 'reason', str(exc)), line=number, column=column + 1, offset=start + column) from exc
    if stage != 'done':
        raise Invalid('incomplete_program:' + stage, line=source.count('\n') + 1, column=1, offset=len(source))
    lexical.bounded(author)
    return author, spans


def lower(source):
    return parse(source)[0]


def token(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'))


def render(author):
    """Round-trip validation prevents silently dropping extra record fields."""
    try:
        lexical.bounded(author)
        runner.engine.closed(author, ['profile', 'name', 'imports', 'commands'])
        need(author['profile'] == PROFILE, 'profile')
        runner.engine.closed(author['imports'], IMPORTS)
        lines = ['company_program ' + token(PROFILE) + ' ' + token(author['name']) + ';']
        lines += ['import_' + kind + ' ' + token(author['imports'][kind]) + ';' for kind in IMPORTS]
        for command in author['commands']:
            kind = command['kind']
            if kind == 'event':
                event = command['event']
                lines.append('event ' + token(event['id']) + ' method ' + token(command['method_key']) + ' on ' + token(event['date']) + ';')
                for name, record in event['inputs'].items():
                    binding = record['value']; status = binding['status']
                    value = binding['value'] if status == 'known' else binding['reason']
                    lines.append('input ' + token(name) + ' ' + status + ' ' + token(value) + ' because ' + token(record['provenance']) + ';')
            else:
                need(kind in ['report', 'carry'], 'command_kind')
                lines.append(kind + ' ' + token(command['id']) + ' at ' + token(command['cutoff']) + ';')
                if kind == 'carry':
                    lines += [key + ' ' + token(command[key]) + ';' for key in ['retained_account', 'next_end_exclusive']]
                    for pointer, policy in command['memory_policies'].items():
                        value = ' ' + token(policy['value']) if policy['kind'] == 'reset' else ''
                        lines.append('memory ' + token(pointer) + ' ' + policy['kind'] + value + ' because ' + token(policy['provenance']) + ';')
                for row in command['equity_movements']:
                    lines.append('equity ' + token(row['id']) + ' event ' + token(row['event_id']) + ' on ' + token(row['date']) +
                                 ' account ' + token(row['account']) + ' amount ' + token(row['amount']) + ' because ' + token(row['description']) + ';')
                for row in command['notes']:
                    lines.append('note ' + token(row['id']) + ' label ' + token(row['label']) + ' status ' + token(row['status']) + ' because ' + token(row['reason']) + ';')
            lines.append('end_' + kind + ';')
        lines.append('end_program;')
        source = '\n'.join(lines) + '\n'
        need(core.canonical(lower(source)) == core.canonical(author), 'author_roundtrip_mismatch')
        return source
    except Exception as exc:
        raise Invalid(getattr(exc, 'reason', str(exc)), stage='author') from exc


def compile_program(author, imports):
    stage = 'author'
    try:
        protected(); render(author)
        stage = 'imports'
        need(type(imports) is dict and set(imports) == set(author['imports'].values()), 'exact_import_population')
        resolved = {}; dependencies = []
        for kind in IMPORTS:
            stage = 'import:' + kind; key = author['imports'][kind]
            value = imports[key]; runner.engine.memory.bounded(value)
            need(runner.digest(value) == key, 'import_digest_mismatch')
            resolved[kind] = deepcopy(value)
            dependencies.append({'role': kind, 'sha256': key})
        commands = deepcopy(author['commands'])
        for i, command in enumerate(commands):
            stage = 'command:' + str(i)
            if command['kind'] == 'event':
                key = command['method_key']
                need(key in resolved['registry']['entries'], 'unregistered_method:' + key)
                types = resolved['registry']['entries'][key]['event_inputs']
                need(set(command['event']['inputs']) == set(types), 'exact_event_inputs')
                for name, record in command['event']['inputs'].items():record['type'] = deepcopy(types[name])
            elif command['kind'] == 'carry':
                types = resolved['opening']['memory_types']
                for pointer, policy in command['memory_policies'].items():
                    if policy['kind'] == 'reset':
                        need(pointer in types, 'undeclared_memory_leaf:' + pointer)
                        policy['type'] = deepcopy(types[pointer])
                        core.scalar(policy['value'], policy['type']['kind'])
                        if policy['type']['kind'] == 'rational':runner.reports.number(policy['value'])
        stage = 'program'
        body = {'profile': runner.PROFILE, 'name': author['name'], **resolved, 'commands': commands}
        runner.validate(body)
        return {'profile': PROFILE, 'author': deepcopy(author), 'program': body,
                'author_sha256': runner.digest(author), 'program_sha256': runner.digest(body),
                'dependencies': dependencies, 'implementation_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
                'dependency_sha256': deepcopy(PINS), 'source_text_sha256': None, 'source_spans': None,
                'executed': False, **runner.FLAGS}
    except Exception as exc:
        raise Invalid(getattr(exc, 'reason', str(exc)), stage=stage) from exc


def compile_text(source, imports):
    source = lexical.source_text(source); author, spans = parse(source)
    try:
        result = compile_program(author, imports)
    except Invalid as exc:
        location = spans['program']
        if exc.stage.startswith('import:'):location = spans['imports'][exc.stage.split(':', 1)[1]]
        if exc.stage.startswith('command:'):location = spans['commands'][int(exc.stage.split(':', 1)[1])]
        raise Invalid(exc.reason, exc.stage, location['line'], location['column'], location['offset']) from exc
    result.update(source_text_sha256=sha256(source.encode('utf-8')).hexdigest(), source_spans=spans)
    return result


def from_program(body):
    """Project redundant types only after checking the declared type correspondence."""
    try:
        protected(); runner.validate(body)
        imports = {runner.digest(body[k]): deepcopy(body[k]) for k in IMPORTS}
        author = {'profile': PROFILE, 'name': body['name'],
                  'imports': {k: runner.digest(body[k]) for k in IMPORTS}, 'commands': deepcopy(body['commands'])}
        for command in author['commands']:
            if command['kind'] == 'event':
                types = body['registry']['entries'][command['method_key']]['event_inputs']
                for name, record in command['event']['inputs'].items():
                    need(core.canonical(record['type']) == core.canonical(types[name]), 'input_type_correspondence')
                    del record['type']
            elif command['kind'] == 'carry':
                for pointer, policy in command['memory_policies'].items():
                    if policy['kind'] == 'reset':
                        need(pointer in body['opening']['memory_types'], 'undeclared_memory_leaf')
                        need(core.canonical(policy['type']) == core.canonical(body['opening']['memory_types'][pointer]), 'reset_type_correspondence')
                        del policy['type']
        compiled = compile_program(author, imports)
        need(core.canonical(compiled['program']) == core.canonical(body), 'engine_program_roundtrip_mismatch')
        return author, imports
    except Exception as exc:
        raise Invalid(getattr(exc, 'reason', str(exc)), stage='from_program') from exc


def execute_text(source, imports):
    return runner.run(compile_text(source, imports)['program'])


def execute_program(author, imports):
    return runner.run(compile_program(author, imports)['program'])
