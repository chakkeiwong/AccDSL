"""Explicit text commands matched to the frozen prospective term operations."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path

import declared_company_text_v2 as syntax
import declared_receivable_text_v1 as header
import receivable_term_history_v1 as terms

PROFILE = 'ReceivableTermText/1'
PROGRAM = 'ReceivableTermProgram/1'
CONFIG = 'ReceivableTermImports/1'
core = terms.core
FIELDS = ['memory_definition', 'roles', 'unit_cost_pointer', 'migration']
PINS = {
    'receivable_term_history_v1.py': 'c0c9629b24826cc9c4814e0c3975c8ed25b4c6fa935f939085341dc0605867e1',
    'declared_company_text_v2.py': '21dcc69802ec61aa1620d35f0d93b006d13a442139443500deb4b793c409218c',
    'declared_receivable_text_v1.py': 'ba7d58e57bbba8f57ba6a56592dbf1d194931205183e59a8445bf9b322a47672',
}


def protected():
    for name, expected in PINS.items():
        core.need(sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() == expected,
                  'term_text_dependency:' + name)
    syntax.protected()
    terms.protected()


def invalid(exc):
    return {'profile': PROFILE, **terms.FLAGS, 'status': 'invalid', 'reason': str(exc)[:350]}


def validate(body):
    protected()
    terms.bounded(body)
    core.closed(body, ['profile', 'name', 'state', 'report_context', 'commands'], 'term_program')
    core.need(body['profile'] == PROGRAM, 'term_program_profile')
    terms.text(body['name'], 'program_name')
    book = terms.validate(body['state'])
    context = body['report_context']
    core.closed(context, ['opening', 'mapping'], 'term_report_context')
    report = terms.life.reports.report(terms.life.reports.request(
        context['opening'], book, body['state']['schemas'], context['mapping']))
    core.need(report['status'] == 'reported', 'term_report_context:' + report.get('reason', 'invalid'))
    commands = body['commands']
    core.need(type(commands) is list and 0 < len(commands) <= syntax.runner.MAX_COMMANDS, 'command_limit')
    for command in commands:
        core.need(type(command) is dict, 'command_record')
        if command.get('kind') == 'event':
            core.closed(command, ['kind', 'method_key', 'event'], 'term_command')
            event = command['event']
            core.closed(event, ['id', 'date', 'inputs'], 'term_event')
            terms.text(event['id'], 'event_id')
            core.scalar(event['date'], 'date')
            kinds = terms.event_types(book, command['method_key'])
            core.need(type(event['inputs']) is dict and set(event['inputs']) == set(kinds), 'exact_event_inputs')
            for name, record in event['inputs'].items():
                core.closed(record, ['type', 'value', 'provenance'], 'term_input')
                core.need(record['type'] == kinds[name], 'event_type:' + name)
                terms.text(record['provenance'], 'event_provenance')
                core.validate_values({'inputs': {name: {'type': terms.engine.dimensions.encoded(kinds[name])}}},
                                     {name: record['value']})
        else:
            core.need(command.get('kind') == 'carry', 'unsupported_term_command')
            core.closed(command, ['kind', 'id', 'cutoff', 'equity_movements', 'notes',
                                  'retained_account', 'next_end_exclusive'], 'term_carry_command')
            terms.text(command['id'], 'carry_id')
            terms.text(command['retained_account'], 'retained_account')
            for name in ['cutoff', 'next_end_exclusive']:
                core.scalar(command[name], 'date')
            core.need(type(command['equity_movements']) is list and type(command['notes']) is list,
                      'carry_report_lists')


def from_program(body):
    validate(body)
    state = body['state']
    config = {'profile': CONFIG, **{k: deepcopy(state[k]) for k in FIELDS}}
    objects = {'opening': state['book'], 'schemas': state['schemas'],
               'registry': config, 'mapping': body['report_context']}
    imports = {core.digest(v): deepcopy(v) for v in objects.values()}
    commands = deepcopy(body['commands'])
    for command in commands:
        if command['kind'] == 'event':
            for record in command['event']['inputs'].values():
                record.pop('type')
        else:
            command['memory_policies'] = {}
    author = {'profile': syntax.PROFILE, 'name': body['name'],
              'imports': {k: core.digest(v) for k, v in objects.items()}, 'commands': commands}
    source = header.translate_header(syntax.render(author), syntax.PROFILE, PROFILE)
    return source, imports


def compile_text(source, imports):
    try:
        protected()
        syntax.lexical.source_text(source)
        translated = header.translate_header(source, PROFILE, syntax.PROFILE)
        author = syntax.lower(translated)
        core.need(type(imports) is dict and set(imports) == set(author['imports'].values()),
                  'exact_import_population')
        resolved = {}
        for name, key in author['imports'].items():
            value = imports[key]
            terms.bounded(value)
            core.need(core.digest(value) == key, 'import_digest_mismatch')
            resolved[name] = deepcopy(value)
        config = resolved['registry']
        core.closed(config, ['profile', *FIELDS], 'term_config')
        core.need(config['profile'] == CONFIG, 'term_config_profile')
        state = {'profile': terms.PROFILE, 'book': resolved['opening'], 'schemas': resolved['schemas'],
                 **{k: config[k] for k in FIELDS}}
        terms.validate(state)
        commands = deepcopy(author['commands'])
        for command in commands:
            if command['kind'] == 'event':
                kinds = terms.event_types(state['book'], command['method_key'])
                core.need(set(command['event']['inputs']) == set(kinds), 'exact_event_inputs')
                for name, record in command['event']['inputs'].items():
                    record['type'] = deepcopy(kinds[name])
            else:
                core.need(command['kind'] == 'carry', 'unsupported_term_command')
                core.need(command.pop('memory_policies') == {}, 'fixed_term_carry_policy')
        body = {'profile': PROGRAM, 'name': author['name'], 'state': state,
                'report_context': resolved['mapping'], 'commands': commands}
        validate(body)
        return {'profile': PROFILE, **terms.FLAGS, 'status': 'compiled', 'program': body,
                'source_sha256': sha256(source.encode('utf-8')).hexdigest(),
                'program_sha256': core.digest(body), 'dependency_sha256': deepcopy(PINS),
                'implementation_sha256': sha256(Path(__file__).read_bytes()).hexdigest()}
    except Exception as exc:
        return invalid(exc)


def run(body):
    try:
        validate(body)
    except Exception as exc:
        return invalid(exc)
    current = deepcopy(body['state'])
    context = deepcopy(body['report_context'])
    trace, ids, stop = [], set(), None
    for command in body['commands']:
        try:
            identity = command['event']['id'] if command['kind'] == 'event' else command['id']
            core.need(identity not in ids and identity not in current['book']['seen'], 'duplicate_command')
            if command['kind'] == 'event':
                request = {'profile': terms.STEP, 'expected_state_sha256': core.digest(current),
                           'operation': command['method_key'], 'event': deepcopy(command['event'])}
                result = terms.step(current, request)
            else:
                core.need(command['cutoff'] == current['book']['date'], 'carry_cutoff_must_match_state')
                report = terms.life.reports.request(context['opening'], current['book'], current['schemas'],
                                                   context['mapping'], command['equity_movements'], command['notes'])
                request = {'profile': terms.CARRY, 'expected_state_sha256': core.digest(current),
                           'report_request': report, 'close_id': identity,
                           'retained_account': command['retained_account'],
                           'next_end_exclusive': command['next_end_exclusive']}
                result = terms.carry(current, request)
            if result['status'] != 'proposed':
                stop = {'command_index': len(trace), 'command': deepcopy(command),
                        'status': result['status'], 'request': request, 'result': result}
                break
            trace.append({'command': deepcopy(command), 'request': request, 'result': result,
                          'before_sha256': core.digest(current), 'after_sha256': result['after_sha256']})
            current = deepcopy(result['after'])
            ids.add(identity)
            if command['kind'] == 'carry':
                context['opening'] = deepcopy(current['book'])
        except Exception as exc:
            stop = {'command_index': len(trace), 'command': deepcopy(command),
                    'status': 'invalid', 'reason': str(exc)[:350]}
            break
    return {'profile': PROGRAM, **terms.FLAGS,
            'status': 'stopped_provisional' if stop else 'complete_provisional',
            'program_sha256': core.digest(body), 'current': current, 'current_sha256': core.digest(current),
            'report_context': context, 'successful_commands': len(trace), 'trace': trace, 'stop': stop,
            'implementation_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
            'scope': 'Matched constructed date-only term commands; no source/accounting/production admission'}


def execute_text(source, imports):
    compiled = compile_text(source, imports)
    return run(compiled['program']) if compiled['status'] == 'compiled' else compiled


def verify(body, result):
    try:
        return core.canonical(run(body)) == core.canonical(result)
    except Exception:
        return False
