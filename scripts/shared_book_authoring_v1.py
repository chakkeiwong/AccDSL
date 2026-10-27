"""Finite data-only authoring of complete synthetic return/lease books."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json
import re
import conditional_family_text_v1 as lexical
import method_requirement_text_v1 as syntax
import shared_book_statements_v1 as reports

book = reports.book
ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / 'data/accounting-master/shared-book-authoring-20261024'
LOCK = '3ef781e68017152eb503e15efd055c17306be74dd38d6dcb57b4a74482c7bda5'
PROFILE = 'SharedBookProgram/1'
FIELDS = tuple(k for k in book.schema()['properties']
               if k not in ['profile', 'balances', 'lots', 'leases'])
REQUEST_FIELDS = ['profile', 'source_bundle_sha256', 'opening_sha256',
                  'events_sha256', 'opening', 'events']


class Invalid(ValueError):
    pass


def need(ok, reason):
    if not ok:
        raise Invalid(reason)


def guarded(fn, *args):
    try:
        return fn(*args)
    except (ValueError, TypeError, KeyError, AttributeError, OSError,
            RecursionError, OverflowError, AssertionError) as exc:
        raise Invalid(str(exc)[:350]) from exc


def protected():
    raw = (HERE / 'source-lock.json').read_bytes()
    need(sha256(raw).hexdigest() == LOCK, 'source_lock_changed')
    for name, expected in json.loads(raw).items():
        need(sha256((ROOT / name).read_bytes()).hexdigest() == expected,
             'protected_source_changed:' + name)


def closed(value, keys, where):
    need(type(value) is dict and set(value) == set(keys), 'closed_fields:' + where)


def identifier(value):
    need(type(value) is str and re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]{0,79}', value),
         'program_name')


def validate_event(value):
    closed(value, ['profile', 'module', 'event'], 'event')
    need(value['profile'] == book.EVENT, 'event_profile')
    event = value['event']
    need(type(event) is dict, 'event_record')
    if value['module'] == 'return':
        need(event.get('kind') in ['settle', 'sell'], 'selected_return_methods_only')
        guarded(book.returns.structure.validate, event, book.returns.event_schema())
    elif value['module'] == 'lease':
        closed(event, ['id', 'date', 'method', 'lease_id', 'parameters'], 'lease_event')
        for key in ['id', 'lease_id']:
            need(type(event[key]) is str and bool(event[key]), 'lease_event_' + key)
        guarded(book.returns.structure.validate, event['date'], book.schema()['properties']['date'])
        need(type(event['method']) is str and event['method'] in book.lease.FOOTPRINT,
             'selected_lease_methods_only')
        guarded(book.lease.typed, event['parameters'], book.lease.types.EVENTS[event['method']][1])
    else:
        raise Invalid('unsupported_module')


def validate_program(program):
    guarded(lexical.bounded, program)
    closed(program, ['profile', 'name', 'request'], 'program')
    need(program['profile'] == PROFILE, 'program_profile')
    identifier(program['name'])
    body = program['request']
    closed(body, REQUEST_FIELDS, 'request')
    need(body['profile'] == reports.PROFILE, 'recorded_report_required')
    need(body['source_bundle_sha256'] == reports.LOCK, 'source_bundle_digest')
    guarded(book.returns.structure.validate, body['opening'], book.schema())
    need(type(body['events']) is list, 'event_list_required')
    for event in body['events']:
        validate_event(event)
    need(body['opening_sha256'] == book.digest(body['opening']), 'opening_digest')
    need(body['events_sha256'] == book.digest(body['events']), 'events_digest')
    # Financial balance, funding, dates, membership and prerequisite findings
    # are deliberately left to the original executor. Compilation is structural.
    return program


def from_request(body, name='shared_book'):
    program = {'profile': PROFILE, 'name': name, 'request': deepcopy(body)}
    validate_program(program)
    return program


def lower(source):
    source = guarded(lexical.source_text, source)
    stage, block, opening, events, body = 'header', None, {}, [], None
    name, declared, count = None, set(), 0
    properties = book.schema()['properties']
    for number, raw in enumerate(source.split('\n'), 1):
        line = raw.removesuffix('\r')
        if not line.strip(' \t'):
            continue
        count += 1
        try:
            need(count <= lexical.core.MAX_NODES, 'declaration_limit')
            reader = syntax.Reader(lexical.tokens(line))
            command = reader.take('word')
            if stage == 'header':
                need(command == 'shared_book', 'header_required')
                need(reader.string() == PROFILE, 'program_profile')
                name = reader.string(); identifier(name); stage = 'opening_header'
            elif stage == 'opening_header':
                need(command == 'opening', 'opening_required')
                opening['profile'] = reader.string()
                need(opening['profile'] == book.PROFILE, 'opening_profile')
                stage = 'opening'
            elif stage == 'opening':
                if block:
                    if command == 'end_' + block:
                        field = {'accounts': 'balances', 'lots': 'lots', 'leases': 'leases'}[block]
                        guarded(book.returns.structure.validate, opening[field], properties[field])
                        block = None
                    elif block in ['accounts', 'lots']:
                        need(command == ('account' if block == 'accounts' else 'lot'), 'block_declaration')
                        field = 'balances' if block == 'accounts' else 'lots'
                        key = reader.string(); value = reader.take('value')
                        need(key not in opening[field], 'duplicate_' + command + ':' + key)
                        if block == 'accounts':
                            need(key in book.ACCOUNTS, 'unknown_account:' + key)
                            guarded(book.returns.structure.validate, value, properties['balances']['properties'][key])
                        else:
                            guarded(book.returns.structure.validate, {key: value}, properties['lots'])
                        opening[field][key] = value
                    elif block == 'leases':
                        need(command == 'lease', 'block_declaration')
                        value = reader.take('value')
                        guarded(book.returns.structure.validate, value, properties['leases']['items'])
                        opening['leases'].append(value)
                elif command in ['accounts', 'lots', 'leases']:
                    need(command not in declared, 'duplicate_block:' + command)
                    declared.add(command); block = command
                    field = 'balances' if command == 'accounts' else command
                    opening[field] = [] if command == 'leases' else {}
                elif command in FIELDS:
                    need(command not in opening, 'duplicate_field:' + command)
                    value = reader.take('value')
                    guarded(book.returns.structure.validate, value, properties[command])
                    opening[command] = value
                elif command == 'end_opening':
                    need(declared == {'accounts', 'lots', 'leases'}, 'explicit_collections_required')
                    guarded(book.returns.structure.validate, opening, book.schema())
                    stage = 'events_header'
                else:
                    raise Invalid('unsupported_opening_declaration:' + command)
            elif stage == 'events_header':
                need(command == 'events', 'events_required'); stage = 'events'
            elif stage == 'events':
                if command == 'end_events':
                    stage = 'report'
                else:
                    need(command == 'event', 'event_required')
                    value = {'profile': book.EVENT, 'module': reader.string(), 'event': reader.take('value')}
                    validate_event(value); events.append(value)
            elif stage == 'report':
                need(command == 'report', 'report_required')
                body = dict(zip(REQUEST_FIELDS[:4], [reader.string() for _ in range(4)]))
                body.update(opening=opening, events=events)
                validate_program({'profile': PROFILE, 'name': name, 'request': body})
                stage = 'end'
            elif stage == 'end':
                need(command == 'end_program', 'end_program_required'); stage = 'done'
            else:
                raise Invalid('declaration_after_end')
            reader.finish()
        except (ValueError, TypeError, KeyError, AttributeError, RecursionError, OverflowError) as exc:
            raise Invalid('line ' + str(number) + ': ' + str(exc)[:350]) from exc
    need(stage == 'done', 'line ' + str(len(source.split('\n'))) + ': incomplete_program:' + stage)
    program = {'profile': PROFILE, 'name': name, 'request': body}
    validate_program(program)
    return program


def token(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def render(program):
    validate_program(program)
    body = program['request']; opening = body['opening']
    lines = ['shared_book ' + token(PROFILE) + ' ' + token(program['name']) + ';',
             'opening ' + token(opening['profile']) + ';']
    lines.extend(key + ' ' + token(opening[key]) + ';' for key in FIELDS)
    lines.append('accounts;')
    lines.extend('account ' + token(key) + ' ' + token(opening['balances'][key]) + ';' for key in book.ACCOUNTS)
    lines.extend(['end_accounts;', 'lots;'])
    lines.extend('lot ' + token(key) + ' ' + token(value) + ';' for key, value in sorted(opening['lots'].items()))
    lines.extend(['end_lots;', 'leases;'])
    lines.extend('lease ' + token(value) + ';' for value in opening['leases'])
    lines.extend(['end_leases;', 'end_opening;', 'events;'])
    lines.extend('event ' + token(e['module']) + ' ' + token(e['event']) + ';' for e in body['events'])
    lines.extend(['end_events;', 'report ' + ' '.join(token(body[k]) for k in REQUEST_FIELDS[:4]) + ';', 'end_program;'])
    source = '\n'.join(lines) + '\n'
    guarded(lexical.source_text, source)
    return source


def compile_program(program):
    protected(); validate_program(program)
    return {'profile': PROFILE, 'program': deepcopy(program),
            'program_sha256': book.digest(program),
            'request_sha256': book.digest(program['request']), 'source_text_sha256': None}


def compile_text(source):
    text = guarded(lexical.source_text, source)
    result = compile_program(lower(text))
    result['source_text_sha256'] = sha256(text.encode('utf-8')).hexdigest()
    return result


def execute_program(program):
    compiled = compile_program(program)
    return reports.calculate(compiled['program']['request'])


def execute_text(source):
    compiled = compile_text(source)
    return reports.calculate(compiled['program']['request'])
