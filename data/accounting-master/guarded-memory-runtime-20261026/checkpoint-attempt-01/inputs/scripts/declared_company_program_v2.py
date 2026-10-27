"""Bounded component-wise declared-book programs; v1 event/report/carry semantics."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path

import company_method_clock_v2 as methods
import company_book_reports_v1 as reports
import company_book_carry_v1 as carry

engine = methods.transition
core = engine.core
PROFILE = 'DeclaredCompanyProgram/2'
FLAGS = reports.FLAGS
MAX_COMMANDS = 64
MAX_TRACE_BYTES = 8 * 1024 * 1024
PINS = {
    'company_method_clock_v2.py': '44a3c7733e56240db24fd5699b048bd884576ec0e6b4a8eea27a984c2d74b44a',
    'company_book_reports_v1.py': '7418f0a6fc7169ac1b297b47891cb2f6f9075b3f2231366ea9f241589a753100',
    'company_book_carry_v1.py': '72a1b3d45b24742267b120b04ee0ba97e479b75b08710a66b014d32d88b70c5c',
}
digest = core.digest


def protected():
    folder = Path(__file__).resolve().parent
    for name, expected in PINS.items():
        core.need(sha256((folder / name).read_bytes()).hexdigest() == expected,
                  'dependency_hash:' + name)
    methods.protected()


def call(book, registry, command):
    return {'profile': methods.PROFILE, 'expected_state_sha256': digest(book),
            'expected_registry_sha256': digest(registry), 'registry': deepcopy(registry),
            'method_key': command['method_key'], 'event': deepcopy(command['event'])}


def identity(command):
    return command['event']['id'] if command['kind'] == 'event' else command['id']


def fresh_id(book):
    value = '__static_program_validation__'
    while value in book['seen']:
        value += '_'
    return value


def validate(body):
    protected()
    core.need(len(core.canonical(body)) <= core.MAX_BYTES, 'program_size_limit')
    engine.closed(body, ['profile', 'name', 'opening', 'schemas', 'registry', 'mapping', 'commands'])
    core.need(body['profile'] == PROFILE, 'program_profile')
    for key in ['opening', 'schemas', 'mapping']:
        engine.memory.bounded(body[key])
    methods.bounded_registry(body['registry'])
    core.need(type(body['commands']) is list and 0 < len(body['commands']) <= MAX_COMMANDS, 'command_limit')
    for command in body['commands']:
        engine.memory.bounded(command)
    engine.text(body['name'], 'program_name')
    book, schemas, registry = body['opening'], body['schemas'], body['registry']
    initial = reports.report(reports.request(book, book, schemas, body['mapping']))
    core.need(initial['status'] == 'reported', 'opening_report:' + initial.get('reason', ''))
    engine.closed(registry, ['profile', 'context', 'entries'])
    entries = registry['entries']
    core.need(type(entries) is dict and 0 < len(entries) <= methods.MAX_ENTRIES, 'registry_entry_limit')
    first = next(iter(entries))
    placeholder = {'id': fresh_id(book), 'date': book['date'], 'inputs': {
        key: {'type': deepcopy(typ), 'value': {'status': 'unknown', 'reason': 'static_only'},
              'provenance': 'Static program structure validation'}
        for key, typ in entries[first]['event_inputs'].items()}}
    methods.materialize(book, call(book, registry, {'method_key': first, 'event': placeholder}))
    for entry in entries.values():
        for key, shape in entry['schemas'].items():
            core.need(key in schemas and core.canonical(schemas[key]) == core.canonical(shape),
                      'program_schema_correspondence')
    commands = body['commands']
    core.need(type(commands) is list and 0 < len(commands) <= MAX_COMMANDS, 'command_limit')
    for command in commands:
        core.need(type(command) is dict, 'command_record')
        kind = command.get('kind')
        if kind == 'event':
            engine.closed(command, ['kind', 'method_key', 'event'])
            engine.closed(command['event'], ['id', 'date', 'inputs'])
            core.scalar(command['event']['date'], 'date')
            engine.text(command['event']['id'], 'event_id')
            # Check types/definitions now, but economic findings at the actual turn.
            probe = deepcopy(command)
            probe['event'].update(id=fresh_id(book), date=book['date'])
            methods.materialize(book, call(book, registry, probe))
        else:
            fields = ['kind', 'id', 'cutoff', 'equity_movements', 'notes']
            if kind == 'carry':
                fields += ['retained_account', 'next_end_exclusive', 'memory_policies']
            core.need(kind in ['report', 'carry'], 'command_kind')
            engine.closed(command, fields)
            engine.text(command['id'], 'command_id')
            core.scalar(command['cutoff'], 'date')
            core.need(type(command['equity_movements']) is list, 'equity_movements')
            core.need(type(command['notes']) is list, 'notes')
            for row in command['equity_movements']:
                engine.closed(row, ['id', 'event_id', 'date', 'account', 'amount', 'description'])
                for key in ['id', 'event_id', 'account', 'description']:
                    engine.text(row[key], key)
                core.scalar(row['date'], 'date'); reports.number(row['amount'])
            for row in command['notes']:
                engine.closed(row, ['id', 'label', 'status', 'reason'])
                for key in ['id', 'label', 'reason']:
                    engine.text(row[key], key)
                core.need(row['status'] in ['missing', 'unsupported', 'unresolved'], 'note_status')
            if kind == 'carry':
                engine.text(command['retained_account'], 'retained_account')
                core.scalar(command['next_end_exclusive'], 'date')
                core.need(type(command['memory_policies']) is dict, 'memory_policies')
                for policy in command['memory_policies'].values():
                    core.need(type(policy) is dict, 'memory_policy')
                    fields = ['kind', 'provenance'] + (['type', 'value'] if policy.get('kind') == 'reset' else [])
                    engine.closed(policy, fields)
                    engine.text(policy['provenance'], 'policy_provenance')
                    core.need(policy['kind'] in ['preserve', 'reset', 'next_period_start'], 'memory_policy_kind')
    return body


def failure(exc):
    return {'profile': PROFILE, **FLAGS,
            'status': 'unsupported' if isinstance(exc, methods.Unsupported) else 'invalid',
            'reason': str(exc)[:300] or type(exc).__name__}


def run(body):
    try:
        validate(body)
    except Exception as exc:
        return failure(exc)
    opening = deepcopy(body['opening']); current = deepcopy(opening)
    trace, report_index, archives = [], [], []
    used = set(opening['seen']); stop = None; trace_bytes = 2
    for index, command in enumerate(body['commands']):
        request = None; result = None; observation = None
        try:
            key = identity(command)
            core.need(key not in used, 'duplicate_command_identity')
            next_opening = opening
            if command['kind'] == 'event':
                request = call(current, body['registry'], command)
                result = methods.propose(current, request)
                success = result['status'] == 'proposed'
                after = result['transition']['after'] if success else current
            else:
                cutoff = command['cutoff']
                core.need(core.scalar(current['date'], 'date') <= core.scalar(cutoff, 'date') <
                          core.scalar(current['period']['end_exclusive'], 'date'), 'cutoff_chronology')
                observed = deepcopy(current); observed['date'] = cutoff
                observation = {'from_date': current['date'], 'cutoff': cutoff,
                               'before_sha256': digest(current), 'observed_sha256': digest(observed),
                               'scope': 'Explicit provisional observation; event completeness unknown'}
                request = reports.request(opening, observed, body['schemas'], body['mapping'],
                                          command['equity_movements'], command['notes'])
                if command['kind'] == 'report':
                    result = reports.report(request)
                    success = result['status'] == 'reported'; after = observed
                else:
                    request = carry.request(request, key, command['retained_account'],
                                            command['next_end_exclusive'], command['memory_policies'])
                    result = carry.propose(request)
                    success = result['status'] == 'proposed'
                    after = result['next_opening'] if success else current
                    next_opening = after if success else opening
            entry = {'index': index, 'command': deepcopy(command), 'request': request, 'result': result,
                     'before_sha256': digest(current), 'after_sha256': digest(after if success else current),
                     'opening_before_sha256': digest(opening), 'opening_after_sha256': digest(next_opening),
                     'observation': observation}
            size = len(core.canonical(entry))
            if trace_bytes + size > MAX_TRACE_BYTES:
                stop = {'index': index, 'command': deepcopy(command), 'status': 'invalid',
                        'reason': 'trace_size_limit', 'request_sha256': digest(request),
                        'result_sha256': digest(result), 'before_sha256': digest(current)}
                break
            if not success:
                stop = {**entry, 'status': result['status'], 'reason': result.get('reason',
                        result.get('transition', {}).get('reason', 'engine_refusal'))}
                break
            trace.append(entry); trace_bytes += size; used.add(key)
            current, opening = after, next_opening
            if command['kind'] in ['report', 'carry']:
                report = result if command['kind'] == 'report' else result['report']
                report_index.append({'command_id': key, 'index': index, 'report_sha256': digest(report)})
            if command['kind'] == 'carry':
                archives.append({'command_id': key, 'index': index, 'archive': deepcopy(result['archive'])})
        except Exception as exc:
            error = failure(exc)
            stop = {'index': index, 'command': deepcopy(command), 'request': request, 'result': result,
                    'status': error['status'], 'reason': error['reason'], 'observation': observation,
                    'before_sha256': digest(current)}
            break
    return {'profile': PROFILE, **FLAGS, 'status': 'stopped_provisional' if stop else 'complete_provisional',
            'program_sha256': digest(body), 'implementation_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
            'dependency_sha256': deepcopy(PINS), 'opening': opening, 'current': current,
            'trace': trace, 'stop': stop, 'remaining_commands': deepcopy(body['commands'][len(trace):]),
            'reports': report_index, 'archives': archives,
            'unresolved': ['Source and accounting admission', 'Event-population completeness',
                           'Complete note schedules', 'General clocks and fiscal policies', 'Durable execution']}


def verify(body, result):
    try:
        core.need(len(core.canonical(result)) <= MAX_TRACE_BYTES + 2 * core.MAX_BYTES, 'result_size_limit')
        return core.canonical(run(body)) == core.canonical(result)
    except Exception:
        return False
