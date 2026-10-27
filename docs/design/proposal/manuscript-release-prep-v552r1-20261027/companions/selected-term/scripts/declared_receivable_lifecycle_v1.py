"""Finite identified credit sales, receipts and dated state-only assessments."""
from copy import deepcopy
from datetime import timedelta
from hashlib import sha256
from pathlib import Path

import company_book_transition_v2 as transition
import declared_operating_methods_v1 as operating
import company_book_reports_v1 as reports
import company_book_carry_v1 as carry

engine = transition.base
core = engine.core
PROFILE = 'DeclaredReceivableLifecycle/1'
POLICY = 'DeclaredReceivablePolicy/1'
TEXT = {'kind': 'text', 'context': {}}
DATE = {'kind': 'date', 'context': {}}
FLAGS = reports.FLAGS
MAX_COMMANDS = 64
PINS = {'company_book_reports_v1.py': '7418f0a6fc7169ac1b297b47891cb2f6f9075b3f2231366ea9f241589a753100',
        'company_book_carry_v1.py': '72a1b3d45b24742267b120b04ee0ba97e479b75b08710a66b014d32d88b70c5c',
        'declared_operating_methods_v1.py': '0201b1d8934e9ec40aeee301609090cc6f5d40829eb9d3dd603757f2a61a7590'}


def protected():
    transition.types.protected()
    for name, expected in PINS.items():
        core.need(sha256((Path(__file__).parent / name).read_bytes()).hexdigest() == expected, 'dependency_hash:' + name)


def scalar(typ): return {'node': 'scalar', 'type': deepcopy(typ)}
def record(fields): return {'node': 'record', 'fields': fields}
def literal(value): return {'kind': 'literal', 'value': value}
def read(name): return {'kind': 'read', 'source': 'inputs', 'pointer': '/' + name}


def claim_type(book):
    money = engine.money_type(book)
    return record({name: scalar(typ) for name, typ in {
        'customer': TEXT, 'due': DATE, 'issued': DATE, 'sale_event': TEXT,
        'remaining': money, 'assessed': core.BOOL, 'assessment_date': DATE,
        'assessed_remaining': money, 'overdue': money}.items()})


def prepare_opening(book, capacity):
    """Explicit empty population, with no invented opening claims."""
    core.need('claims' not in book['memory'] and 'collection_clock' not in book['memory'], 'reserved_memory_fields')
    def visit(value, path):
        if type(value) is dict: return record({k: visit(v, path + [k]) for k, v in value.items()})
        return scalar(book['memory_types'][transition.types.pointer(path)])
    definition = {'profile': transition.types.PROFILE, 'root': visit(book['memory'], [])}
    definition['root']['fields'].update(claims={'node': 'map', 'max_items': capacity, 'values': claim_type(book)},
                                       collection_clock=record({'cursor': scalar(DATE)}))
    after = deepcopy(book); after['memory'].update(claims={}, collection_clock={'cursor': book['date']})
    derived = transition.types.derive(definition, after['memory'], after)
    core.need(derived['status'] == 'typed', 'opening_types:' + derived.get('reason', ''))
    after.update(memory_types=derived['memory_types'], memory_schema=derived['schema_sha256'])
    return after, definition, {derived['schema_sha256']: derived['schema']}


def event_types(book, method):
    money = engine.money_type(book)
    if method == 'sale':
        return {'approved': core.BOOL, 'units': {**deepcopy(money), 'dimensions': {'goods:unit': 1}},
                'consideration': money, 'claim_id': TEXT, 'customer': TEXT, 'due': DATE}
    if method == 'collect': return {'approved': core.BOOL, 'amount': money, 'claim_id': TEXT, 'customer': TEXT}
    if method == 'assess': return {'approved': core.BOOL, 'start': DATE, 'end_exclusive': DATE}
    raise core.Invalid('unsupported_method:' + str(method))


def control(book, roles):
    claims = book['memory']['claims']; total = reports.total(reports.number(row['remaining']) for row in claims.values())
    core.need(total == reports.number(book['balances'][roles['receivables']]), 'claim_receivable_sum')
    cursor = book['memory']['collection_clock']['cursor']; core.scalar(cursor, 'date')
    for identity, row in claims.items():
        engine.text(identity, 'claim_id'); engine.text(row['customer'], 'customer')
        core.need(row['sale_event'] in book['seen'], 'claim_sale_event')
        core.need(row['issued'] <= row['due'] and row['issued'] <= book['date'], 'claim_dates')
        core.need(reports.number(row['remaining']) >= 0, 'negative_claim')
        core.need(reports.number(row['assessed_remaining']) >= 0 and reports.number(row['overdue']) >= 0, 'negative_assessment')
        if row['assessed']:
            core.need(row['issued'] <= row['assessment_date'] <= book['date'], 'assessment_chronology')
            expected = row['assessed_remaining'] if row['assessment_date'] > row['due'] else '0/1'
            core.need(row['overdue'] == expected, 'overdue_snapshot')
        else:
            core.need(row['assessed_remaining'] == row['overdue'] == '0/1', 'unassessed_placeholder')


def observation(book):
    rows = []
    for identity, row in book['memory']['claims'].items():
        at = row['assessment_date'] if row['assessed'] else None
        rows.append({'id': identity, 'customer': row['customer'], 'due': row['due'], 'issued': row['issued'],
            'remaining': row['remaining'], 'assessment_as_of': at,
            'assessed_remaining': row['assessed_remaining'] if at else None,
            'overdue': row['overdue'] if at else None,
            'status': 'unassessed' if at is None else 'current' if at == book['date'] else 'historical'})
    return {'as_of': book['date'], 'next_window_start': book['memory']['collection_clock']['cursor'],
            'claims': rows, 'scope': 'Declared state snapshots, not impairment or complete historical ageing'}


def make_request(book, body, command):
    event = command['event']; kind = command['method_key']
    values = {k: v['value']['value'] for k, v in event['inputs'].items()}
    day = event['date']; cursor = book['memory']['collection_clock']['cursor']
    if kind in ['sale', 'collect']: core.need(day >= cursor, 'assessment_day_sealed')
    registry = operating.build(book, body['schemas'], body['roles'], body['unit_cost_pointer'])
    method = deepcopy(registry['entries']['deliver' if kind == 'sale' else 'collect']['method'])
    schemas = deepcopy(body['schemas']); money = engine.money_type(book)
    operations, fields, bindings = [], {}, {}
    if kind == 'sale':
        identity = values['claim_id']; engine.text(identity, 'claim_id'); engine.text(values['customer'], 'customer')
        core.need(day <= values['due'], 'due_before_sale')
        core.need(identity not in book['memory']['claims'], 'duplicate_claim')
        row = {'customer': literal(values['customer']), 'due': literal(values['due']), 'issued': literal(day),
               'sale_event': literal(event['id']), 'remaining': read('amount'), 'assessed': literal(False),
               'assessment_date': literal(day), 'assessed_remaining': literal('0/1'), 'overdue': literal('0/1')}
        fields['amount'] = operating.declaration(money, 'amount')['type']
        bindings['amount'] = {'kind': 'monetary_input', 'name': 'consideration'}
        operations.append({'id': 'create', 'op': 'insert', 'path': ['claims', identity],
                           'value': {'kind': 'object', 'fields': row}})
    elif kind == 'collect':
        identity = values['claim_id']; claims = book['memory']['claims']
        core.need(identity in claims, 'unknown_claim'); row = claims[identity]
        core.need(values['customer'] == row['customer'], 'claim_customer_mismatch')
        pointer = transition.types.pointer(['claims', identity, 'remaining'])
        pre = method['preconditions']; pre['manifest']['inputs']['claim_remaining'] = operating.declaration(money, 'claim_remaining')
        pre['bindings']['claim_remaining'] = {'kind': 'memory', 'pointer': pointer}
        pre['manifest']['requirements'].append({'id': 'claim_available', 'guard': operating.constant(core.BOOL, True),
            'guard_requires': [], 'predicate': operating.binary('le', operating.ref('amount'), operating.ref('claim_remaining')),
            'requires': ['amount', 'claim_remaining'], 'admission_refs': [], 'on_false': 'invalid', 'on_unknown': 'unresolved'})
        monetary = method['monetary']; monetary['definition']['inputs']['claim_remaining'] = operating.declaration(money, 'claim_remaining')
        monetary['bindings']['claim_remaining'] = {'kind': 'memory', 'pointer': pointer}
        monetary['definition']['calculations'].append({'id': 'remaining_after', 'type': deepcopy(money),
            'expression': operating.binary('sub', operating.ref('claim_remaining'), operating.ref('amount')),
            'requires': ['claim_remaining', 'amount']})
        fields['amount'] = money; bindings['amount'] = {'kind': 'calculation', 'name': 'remaining_after'}
        operations.append({'id': 'collect', 'op': 'replace', 'path': ['claims', identity, 'remaining'], 'value': read('amount')})
    else:
        core.need(values['start'] == cursor, 'assessment_cursor')
        start, end = [core.scalar(values[k], 'date') for k in ['start', 'end_exclusive']]
        core.need(start < end and day == (end - timedelta(days=1)).isoformat(), 'assessment_window')
        core.need(values['end_exclusive'] <= book['period']['end_exclusive'], 'assessment_crosses_period')
        identity = 'synthetic.receivable.assess'
        pre = operating.conditions(identity, {'approved': core.BOOL}, [('approved', operating.ref('approved'), ['approved'], 'unsupported')])
        method = {'profile': engine.METHOD, 'id': identity, 'version': '1', 'context': deepcopy(book['context']),
            'account_map': {k: body['roles'][k] for k in ['cash', 'receivables']},
            'preconditions': {'manifest': pre, 'bindings': {'approved': operating.event('approved')}},
            'postconditions': {'manifest': operating.conditions(identity, {'cursor': DATE}, [
                ('cursor_advanced', operating.binary('eq', operating.ref('cursor'), operating.constant(DATE, values['end_exclusive'])),
                 ['cursor'], 'invalid')]), 'bindings': {'cursor': {'kind': 'memory', 'pointer': '/collection_clock/cursor'}}},
            'monetary': {'definition': {'profile': engine.monetary.PROFILE, 'method_id': identity, 'version': '1',
                'inputs': {}, 'calculations': [], 'accounts': {k: deepcopy(money) for k in ['cash', 'receivables']},
                'cash_account': 'cash', 'postings': [], 'flows': []}, 'bindings': {}},
            'residual_prerequisites': ['State-only due-date convention; no impairment or tax']}
        for identity, row in book['memory']['claims'].items():
            for name, value in {'assessed': True, 'assessment_date': day, 'assessed_remaining': row['remaining'],
                                'overdue': row['remaining'] if day > row['due'] else '0/1'}.items():
                operations.append({'id': 'assess.' + str(len(operations)), 'op': 'replace',
                                   'path': ['claims', identity, name], 'value': literal(value)})
        operations.append({'id': 'cursor', 'op': 'replace', 'path': ['collection_clock', 'cursor'], 'value': literal(values['end_exclusive'])})
    shape = transition.types.compile_schema({'profile': transition.types.PROFILE,
        'root': record({k: scalar(v) for k, v in fields.items()})}, book)
    h = core.digest(shape); schemas[h] = shape
    method['memory'] = {'definition': {'profile': engine.memory.PROFILE, 'state_schema': book['memory_schema'],
        'input_schema': h, 'operations': operations}, 'input_bindings': bindings}
    return {'profile': transition.PROFILE, 'expected_state_sha256': core.digest(book),
        'expected_method_sha256': core.digest(method), 'method': method, 'event': deepcopy(event),
        'schemas': schemas, 'memory_definition': deepcopy(body['memory_definition'])}


def validate(body):
    protected(); engine.memory.bounded(body)
    engine.closed(body, ['profile', 'name', 'opening', 'schemas', 'mapping', 'roles',
                         'memory_definition', 'unit_cost_pointer', 'policy', 'commands'])
    core.need(body['profile'] == PROFILE, 'profile'); engine.text(body['name'], 'name')
    engine.closed(body['policy'], ['profile', 'past_due', 'carry', 'provenance'])
    core.need(body['policy']['profile'] == POLICY and body['policy']['past_due'] == 'strictly_after_due_date'
              and body['policy']['carry'] == 'preserve_all_memory', 'explicit_policy')
    engine.text(body['policy']['provenance'], 'policy_provenance')
    book = body['opening']; transition.typed_book(book, body['memory_definition'], body['schemas'])
    fields = body['memory_definition']['root']['fields']
    core.need(fields['claims']['node'] == 'map' and fields['claims']['values'] == claim_type(book), 'claim_type_contract')
    core.need(fields['collection_clock'] == record({'cursor': scalar(DATE)}), 'clock_type_contract')
    core.need(book['memory']['claims'] == {}, 'empty_opening_claim_population_required')
    core.need(book['memory']['collection_clock']['cursor'] == book['date'], 'opening_cursor')
    operating.build(book, body['schemas'], body['roles'], body['unit_cost_pointer'])
    control(book, body['roles'])
    report = reports.report(reports.request(book, book, body['schemas'], body['mapping']))
    core.need(report['status'] == 'reported', 'opening_report:' + report.get('reason', ''))
    core.need(type(body['commands']) is list and 0 < len(body['commands']) <= MAX_COMMANDS, 'command_limit')


def run(body):
    try: validate(body)
    except Exception as exc: return {'profile': PROFILE, **FLAGS, 'status': 'invalid', 'reason': str(exc)[:300]}
    current = deepcopy(body['opening']); opening = deepcopy(current)
    trace, output_reports, ids = [], [], set(); stop = None
    for command in body['commands']:
        before = deepcopy(current)
        try:
            core.need(type(command) is dict, 'command_record'); kind = command.get('kind')
            if kind == 'event':
                engine.closed(command, ['kind', 'method_key', 'event'])
                event = command['event']; engine.closed(event, ['id', 'date', 'inputs']); identity = event['id']
            else:
                core.need(kind in ['report', 'carry'], 'command_kind')
                keys = ['kind', 'id', 'cutoff', 'equity_movements', 'notes']
                if kind == 'carry': keys += ['retained_account', 'next_end_exclusive']
                engine.closed(command, keys); identity = command['id']
            engine.text(identity, 'command_id'); core.need(identity not in ids and identity not in current['seen'], 'duplicate_command')
            control(current, body['roles']); transition.typed_book(current, body['memory_definition'], body['schemas'])
            if kind == 'event':
                core.need(current['date'] <= core.scalar(event['date'], 'date').isoformat() < current['period']['end_exclusive'], 'event_chronology')
                declared = event_types(current, command['method_key'])
                core.need(type(event['inputs']) is dict and set(event['inputs']) == set(declared), 'exact_event_inputs')
                unknown = []
                for name, record_ in event['inputs'].items():
                    engine.closed(record_, ['type', 'value', 'provenance'])
                    core.need(record_['type'] == declared[name], 'event_type:' + name)
                    engine.text(record_['provenance'], 'event_provenance')
                    core.validate_values({'inputs': {name: {'type': engine.dimensions.encoded(declared[name])}}}, {name: record_['value']})
                    if record_['value']['status'] == 'unknown': unknown.append(name)
                if unknown:
                    stop = {'status': 'unresolved', 'reason': 'unknown_event_inputs', 'inputs': unknown}; break
                if event['inputs']['approved']['value']['value'] is not True:
                    stop = {'status': 'unsupported', 'reason': 'applicability_not_selected'}; break
                request = make_request(current, body, command)
                result = transition.propose(current, request)
                if result['status'] != 'proposed':
                    stop = {'status': result['status'], 'reason': result.get('reason', 'transition_refusal'), 'result': result}; break
                after = result['after']; control(after, body['roles'])
                item = {'command': deepcopy(command), 'request': request, 'result': result}
            else:
                cutoff = core.scalar(command['cutoff'], 'date').isoformat()
                core.need(current['date'] <= cutoff < current['period']['end_exclusive'], 'report_chronology')
                closing = deepcopy(current); closing['date'] = cutoff
                request = reports.request(opening, closing, body['schemas'], body['mapping'], command['equity_movements'], command['notes'])
                if kind == 'report':
                    result = reports.report(request); core.need(result['status'] == 'reported', 'report:' + result.get('reason', ''))
                    after = closing
                else:
                    policies = {p: {'kind': 'preserve', 'provenance': body['policy']['provenance']} for p in current['memory_types']}
                    request = carry.request(request, identity, command['retained_account'], command['next_end_exclusive'], policies)
                    result = carry.propose(request); core.need(result['status'] == 'proposed', 'carry:' + result.get('reason', ''))
                    after = result['next_opening']; core.need(after['memory'] == current['memory'], 'carry_memory_preservation')
                control(after, body['roles']); transition.typed_book(after, body['memory_definition'], body['schemas'])
                item = {'command': deepcopy(command), 'request': request, 'result': result}
                output_reports.append({'id': identity, 'result': result if kind == 'report' else result['report'],
                                       'observation': observation(closing)})
                if kind == 'carry': opening = deepcopy(after)
            current = deepcopy(after); ids.add(identity)
            item.update(before_sha256=core.digest(before), after_sha256=core.digest(current), observation=observation(current))
            trace.append(item)
        except Exception as exc:
            stop = {'status': 'invalid', 'reason': str(exc)[:300]}; break
    return {'profile': PROFILE, **FLAGS, 'status': 'stopped_provisional' if stop else 'complete_provisional',
            'request_sha256': core.digest(body), 'current': current, 'current_sha256': core.digest(current),
            'successful_commands': len(trace), 'trace': trace, 'reports': output_reports,
            'observation': observation(current), 'stop': stop,
            'implementation_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
            'scope': 'Finite declared credit-sale lifecycle; no source, accounting or production admission'}


def verify(body, result):
    try: return core.canonical(run(body)) == core.canonical(result)
    except Exception: return False
