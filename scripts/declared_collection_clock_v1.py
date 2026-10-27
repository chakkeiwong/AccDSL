"""Finite declared receivable clocks on the existing scalar company book."""
from copy import deepcopy
from datetime import timedelta
from hashlib import sha256
from pathlib import Path

import declared_operating_methods_v1 as helpers
import declared_company_program_v2 as program

PROFILE = 'DeclaredCollectionClock/1'
POLICY = 'SyntheticDueDateAssessment/1'
engine, core = program.engine, program.core
DATE = {'kind': 'date', 'context': {}}
FLAGS = program.FLAGS
MAX_CLAIMS, MAX_WINDOWS = 8, 16
PINS = {
    'declared_operating_methods_v1.py': '0201b1d8934e9ec40aeee301609090cc6f5d40829eb9d3dd603757f2a61a7590',
    'declared_company_program_v2.py': 'aa69e8bfb4628ddff5867bb243996b32d43c56119bd61f2baf1b87b23d5d1633',
}
ref, binary, constant = helpers.ref, helpers.binary, helpers.constant
fmt, number = program.reports.fmt, program.reports.number


def protected():
    folder = Path(__file__).resolve().parent
    for name, expected in PINS.items():
        core.need(sha256((folder / name).read_bytes()).hexdigest() == expected, 'dependency_hash:' + name)
    program.protected()


def leaf(book, pointer):
    found, value = engine.binding.located(book['memory'], pointer)
    core.need(found, 'missing_collection_memory:' + pointer)
    return value


def record(fields):
    return {'type': 'object', 'properties': fields, 'required': list(fields), 'additionalProperties': False}


def scalar(kind):
    return {'type': 'string', 'minLength': 1, 'maxLength': 4096, 'x-exact-kind': kind}


def conditions(identity, types, rows):
    result = helpers.conditions(identity, types, rows)
    for key, declaration in result['inputs'].items():
        declaration['source_ref'] = 'declared-collection-premise:' + key
    result['residual_prerequisites'] = [
        'Explicit synthetic receivable and date policy; source, impairment and tax admission remain unresolved.']
    return result


def build(book, schemas, roles, claims, windows, policy):
    """Build finite methods. No payment or assessment executes during building."""
    protected(); engine.validate_book(book, schemas)
    engine.closed(roles, ['cash', 'receivables'])
    core.need(len(set(roles.values())) == 2 and roles['cash'] == book['cash_account'], 'collection_roles')
    for account in roles.values():
        core.need(account in book['accounts'] and book['accounts'][account]['classification'] == 'asset', 'collection_account_class')
    engine.closed(policy, ['profile', 'past_due', 'cursor_pointer', 'assessed_pointer', 'provenance'])
    core.need(policy['profile'] == POLICY and policy['past_due'] == 'strictly_after_due_date', 'explicit_collection_policy')
    engine.text(policy['provenance'], 'policy_provenance')
    money = engine.money_type(book); cp, ap = policy['cursor_pointer'], policy['assessed_pointer']
    pointers = {cp: DATE, ap: core.BOOL}
    core.need(cp != ap, 'aliased_clock_pointers')
    core.need(type(claims) is list and 0 < len(claims) <= MAX_CLAIMS, 'claim_limit')
    identities = set()
    for claim in claims:
        engine.closed(claim, ['id', 'due_date', 'due_pointer', 'balance_pointer', 'assessed_balance_pointer', 'overdue_pointer'])
        engine.text(claim['id'], 'claim_id'); core.need(claim['id'] not in identities, 'duplicate_claim')
        identities.add(claim['id']); core.scalar(claim['due_date'], 'date')
        for field, typ in [('due_pointer', DATE), ('balance_pointer', money), ('assessed_balance_pointer', money), ('overdue_pointer', money)]:
            pointer = claim[field]; engine.binding.pointer_parts(pointer)
            core.need(pointer not in pointers, 'aliased_claim_pointer'); pointers[pointer] = typ
        core.need(leaf(book, claim['due_pointer']) == claim['due_date'], 'declared_due_date_mismatch')
        core.need(number(leaf(book, claim['balance_pointer'])) >= 0, 'negative_claim')
        for field in ['assessed_balance_pointer', 'overdue_pointer']:
            core.need(leaf(book, claim[field]) == '0/1', 'initial_unassessed_placeholder')
    for pointer, typ in pointers.items():
        core.need(book['memory_types'].get(pointer) == typ, 'collection_memory_type:' + pointer)
    core.need(leaf(book, cp) == book['date'] and leaf(book, ap) is False, 'initial_unassessed_clock')
    total = sum(number(leaf(book, c['balance_pointer'])) for c in claims)
    core.need(total == number(book['balances'][roles['receivables']]), 'opening_claim_sum')
    core.need(type(windows) is list and 0 < len(windows) <= MAX_WINDOWS, 'assessment_window_limit')
    cursor = book['date']; dated = []
    for window in windows:
        engine.closed(window, ['start', 'end_exclusive'])
        start, end = [core.scalar(window[k], 'date') for k in ['start', 'end_exclusive']]
        core.need(window['start'] == cursor and start < end, 'contiguous_positive_windows')
        dated.append((window, (end - timedelta(days=1)).isoformat())); cursor = window['end_exclusive']
    zero = constant(money, '0/1')
    claim_sum = ref('claim0')
    for i in range(1, len(claims)): claim_sum = binary('add', claim_sum, ref('claim' + str(i)))
    entries = {}
    variants = [('collect.' + str(i + 1), i, None) for i in range(len(claims))]
    variants += [('assess.' + str(i + 1), None, window) for i, window in enumerate(dated)]
    for key, selected, dated_window in variants:
        identity = 'synthetic.collection.' + key
        pre_types = {'approved': core.BOOL, 'event_date': DATE, 'cursor': DATE, 'receivables': money}
        pre_bindings = {'approved': helpers.event('approved'), 'event_date': helpers.event('event_date'),
                        'cursor': {'kind': 'memory', 'pointer': cp}, 'receivables': helpers.account('receivables')}
        rows = [('applicable', ref('approved'), ['approved'], 'unsupported')]
        for i, claim in enumerate(claims):
            name = 'claim' + str(i); due = 'due' + str(i)
            pre_types.update({name: money, due: DATE})
            pre_bindings[name] = {'kind': 'memory', 'pointer': claim['balance_pointer']}
            pre_bindings[due] = {'kind': 'memory', 'pointer': claim['due_pointer']}
            rows += [(name + '_nonnegative', binary('le', deepcopy(zero), ref(name)), [name], 'invalid'),
                     (due + '_preserved', binary('eq', ref(due), constant(DATE, claim['due_date'])), [due], 'invalid')]
        deps = ['claim' + str(i) for i in range(len(claims))]
        rows.append(('claim_sum', binary('eq', deepcopy(claim_sum), ref('receivables')), deps + ['receivables'], 'invalid'))
        post_types = {k: deepcopy(v) for k, v in pre_types.items() if k not in ['approved', 'event_date', 'cursor']}
        post_bindings = {k: deepcopy(pre_bindings[k]) for k in post_types}
        post_rows = deepcopy(rows[1:])
        numeric, bindings, calculations, postings, flows = {}, {}, [], [], []
        writes, inputs, fields = [], {}, {}
        supplied = {'approved': deepcopy(core.BOOL)}

        def write(pointer, value):
            writes.append({'id': 'write.' + str(len(writes)), 'op': 'replace',
                           'path': engine.binding.pointer_parts(pointer), 'value': value})

        def copy_amount(name, pointer):
            numeric[name] = helpers.declaration(money, name)
            bindings[name] = {'kind': 'memory', 'pointer': pointer}
            calculations.append({'id': name + '_value', 'type': deepcopy(money), 'expression': ref(name), 'requires': [name]})
            fields[name] = scalar('rational'); inputs[name] = {'kind': 'calculation', 'name': name + '_value'}
            return {'kind': 'read', 'source': 'inputs', 'pointer': '/' + name}

        if selected is not None:
            claim = claims[selected]; name = 'claim' + str(selected)
            pre_types['amount'] = money; pre_bindings['amount'] = helpers.event('amount'); supplied['amount'] = deepcopy(money)
            rows += [('amount_nonnegative', binary('le', deepcopy(zero), ref('amount')), ['amount'], 'invalid'),
                     ('claim_available', binary('le', ref('amount'), ref(name)), ['amount', name], 'invalid'),
                     ('assessment_day_sealed', binary('le', ref('cursor'), ref('event_date')), ['cursor', 'event_date'], 'invalid')]
            numeric = {k: helpers.declaration(money, k) for k in ['amount', 'remaining']}
            bindings = {'amount': helpers.event('amount'), 'remaining': {'kind': 'memory', 'pointer': claim['balance_pointer']}}
            calculations = [{'id': 'next_remaining', 'type': deepcopy(money), 'expression': binary('sub', ref('remaining'), ref('amount')),
                             'requires': ['remaining', 'amount']}]
            fields['next_remaining'] = scalar('rational'); inputs['next_remaining'] = {'kind': 'calculation', 'name': 'next_remaining'}
            write(claim['balance_pointer'], {'kind': 'read', 'source': 'inputs', 'pointer': '/next_remaining'})
            postings = [{'id': 'receipt', 'account': 'cash', 'expression': ref('amount'), 'requires': ['amount']},
                        {'id': 'settlement', 'account': 'receivables', 'expression': binary('sub', deepcopy(zero), ref('amount')), 'requires': ['amount']}]
            flows = [{'id': 'receipt', 'activity': 'operating', 'origin': 'collect', 'expression': ref('amount'), 'requires': ['amount']}]
        else:
            window, at = dated_window
            rows += [('window_cursor', binary('eq', ref('cursor'), constant(DATE, window['start'])), ['cursor'], 'invalid'),
                     ('assessment_date', binary('eq', ref('event_date'), constant(DATE, at)), ['event_date'], 'invalid')]
            for i, claim in enumerate(claims):
                value = copy_amount('remaining' + str(i), claim['balance_pointer'])
                write(claim['assessed_balance_pointer'], value)
                overdue = deepcopy(value) if at > claim['due_date'] else {'kind': 'literal', 'value': '0/1'}
                write(claim['overdue_pointer'], overdue)
            write(cp, {'kind': 'literal', 'value': window['end_exclusive']})
            write(ap, {'kind': 'literal', 'value': True})
        shape = record(fields); h = core.digest(shape); shapes = {**deepcopy(schemas), h: shape}
        monetary = {'profile': engine.monetary.PROFILE, 'method_id': identity, 'version': '1', 'inputs': numeric,
                    'calculations': calculations, 'accounts': {k: deepcopy(money) for k in roles}, 'cash_account': 'cash',
                    'postings': postings, 'flows': flows}
        method = {'profile': engine.METHOD, 'id': identity, 'version': '1', 'context': deepcopy(book['context']),
                  'account_map': deepcopy(roles), 'preconditions': {'manifest': conditions(identity, pre_types, rows), 'bindings': pre_bindings},
                  'postconditions': {'manifest': conditions(identity, post_types, post_rows), 'bindings': post_bindings},
                  'monetary': {'definition': monetary, 'bindings': bindings},
                  'memory': {'definition': {'profile': engine.memory.PROFILE, 'state_schema': book['memory_schema'], 'input_schema': h, 'operations': writes},
                             'input_bindings': inputs},
                  'residual_prerequisites': ['Synthetic declared claims and due dates; no impairment, tax, source or population admission.',
                                             'Policy SHA256 ' + core.digest(policy), 'Claim population SHA256 ' + core.digest(claims)]}
        entries[key] = {'method_sha256': core.digest(method), 'method': method, 'schemas': shapes,
                        'account_classes': {k: 'asset' for k in roles}, 'event_inputs': supplied,
                        'metadata_bindings': {'event_date': 'date'}, 'clock': {'kind': 'direct_event_date'}}
    return {'profile': program.methods.REGISTRY, 'context': deepcopy(book['context']), 'entries': entries}


def request(body, roles, claims, windows, policy):
    return {'profile': PROFILE, 'program': deepcopy(body), 'roles': deepcopy(roles),
            'claims': deepcopy(claims), 'windows': deepcopy(windows), 'policy': deepcopy(policy)}


def observation(book, claims, policy):
    assessed = leaf(book, policy['assessed_pointer'])
    cursor = leaf(book, policy['cursor_pointer'])
    at = (core.scalar(cursor, 'date') - timedelta(days=1)).isoformat() if assessed else None
    rows = []
    for claim in claims:
        balance = leaf(book, claim['balance_pointer'])
        rows.append({'id': claim['id'], 'due_date': claim['due_date'], 'remaining': balance,
                     'assessed_remaining': leaf(book, claim['assessed_balance_pointer']) if assessed else None,
                     'assessed_overdue': leaf(book, claim['overdue_pointer']) if assessed else None})
    return {'as_of': book['date'], 'assessment_as_of': at, 'next_window_start': cursor,
            'status': 'unassessed' if not assessed else 'current' if at == book['date'] else 'historical',
            'claims': rows, 'scope': 'Declared claim population; recorded assessment is not impairment or complete ageing'}


def run(body):
    """Pure guarded replay; reject unsafe effects before publishing their state."""
    try:
        protected(); core.need(len(core.canonical(body)) <= core.MAX_BYTES, 'collection_program_size_limit')
        engine.closed(body, ['profile', 'program', 'roles', 'claims', 'windows', 'policy'])
        core.need(body['profile'] == PROFILE, 'collection_profile')
        source = body['program']; program.validate(source)
        claims, policy, roles = body['claims'], body['policy'], body['roles']
        registry = build(source['opening'], source['schemas'], roles, claims, body['windows'], policy)
        by_hash = {e['method_sha256']: key for key, e in registry['entries'].items()}
        for entry in source['registry']['entries'].values():
            key = by_hash.get(entry['method_sha256'])
            if key is not None:
                for field in ['event_inputs', 'metadata_bindings', 'clock', 'account_classes']:
                    core.need(core.canonical(entry[field]) == core.canonical(registry['entries'][key][field]),
                              'collection_call_binding:' + field)
        protected_paths = [policy['cursor_pointer'], policy['assessed_pointer']]
        protected_paths += [c[k] for c in claims for k in ['due_pointer', 'balance_pointer', 'assessed_balance_pointer', 'overdue_pointer']]
        execution = program.run(source)
        core.need(execution['status'] in ['complete_provisional', 'stopped_provisional'], 'program_invalid:' + execution.get('reason', ''))
        guard_stop = None; assessments = []; reports = []
        current = deepcopy(source['opening'])
        for i, step in enumerate(execution['trace']):
            command = step['command']
            try:
                if command['kind'] == 'event':
                    entry = source['registry']['entries'][command['method_key']]
                    kind = by_hash.get(entry['method_sha256'])
                    if kind is None:
                        method = entry['method']
                        core.need(not any(method['account_map'][p['account']] == roles['receivables']
                                          for p in method['monetary']['definition']['postings']), 'unclassified_receivable_posting')
                        for operation in method['memory']['definition']['operations']:
                            path = '/' + '/'.join(t.replace('~', '~0').replace('/', '~1') for t in operation['path'])
                            core.need(not any(path == p or path.startswith(p + '/') or p.startswith(path + '/')
                                              for p in protected_paths), 'unclassified_collection_memory_write')
                    after = step['result']['transition']['after']
                    core.need(sum(number(leaf(after, c['balance_pointer'])) for c in claims) ==
                              number(after['balances'][roles['receivables']]), 'claim_sum_after_event')
                    if kind is None:
                        core.need(all(leaf(after, p) == leaf(current, p) for p in protected_paths), 'hidden_collection_mutation')
                    elif kind.startswith('assess.'):
                        core.need(all(v == '0/1' for v in step['result']['transition']['journal'].values()) and
                                  step['result']['transition']['flows'] == [], 'assessment_has_monetary_effect')
                        assessments.append({'event_id': command['event']['id'], 'trace_index': i,
                                            'observation': observation(after, claims, policy)})
                else:
                    closing = step['request']['closing'] if command['kind'] == 'report' else step['request']['report_request']['closing']
                    if command['kind'] == 'carry':
                        core.need(all(command['memory_policies'].get(p, {}).get('kind') == 'preserve' for p in protected_paths),
                                  'collection_carry_must_preserve')
                        after = step['result']['next_opening']
                        core.need(all(leaf(after, p) == leaf(current, p) for p in protected_paths), 'carry_changed_collection_memory')
                    else:
                        after = closing
                    reports.append({'command_id': command['id'], 'trace_index': i, 'observation': observation(closing, claims, policy)})
                current = after
            except Exception as exc:
                guard_stop = {'index': i, 'command': deepcopy(command), 'status': 'invalid', 'reason': str(exc)[:300],
                              'before_sha256': program.digest(current)}
                break
        if guard_stop is not None:
            prefix = deepcopy(source); prefix['commands'] = prefix['commands'][:guard_stop['index']]
            execution = program.run(prefix) if prefix['commands'] else None
        stop = guard_stop or (execution['stop'] if execution else None)
        count = len(execution['trace']) if execution else 0
        current = execution['current'] if execution else deepcopy(source['opening'])
        return {'profile': PROFILE, **FLAGS, 'status': 'stopped_provisional' if stop else 'complete_provisional',
                'request_sha256': core.digest(body), 'program_result': execution, 'stop': stop,
                'successful_commands': count, 'remaining_commands': deepcopy(source['commands'][count:]),
                'current': current, 'assessments': assessments, 'reports': reports,
                'observation': observation(current, claims, policy),
                'implementation_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
                'dependency_sha256': deepcopy(PINS),
                'unresolved': ['Actual payment terms and source admission', 'Impairment and tax measurement',
                               'Complete receivable population and note package', 'Dynamic claim insertion and revision',
                               'General fiscal coverage and durable execution']}
    except Exception as exc:
        return {'profile': PROFILE, **FLAGS, 'status': 'invalid', 'reason': str(exc)[:300] or type(exc).__name__}


def verify(body, result):
    try:
        core.need(len(core.canonical(result)) <= program.MAX_TRACE_BYTES + 3 * core.MAX_BYTES, 'collection_result_size_limit')
        return core.canonical(run(body)) == core.canonical(result)
    except Exception:
        return False


def execute_text(source, imports, roles, claims, windows, policy):
    import declared_company_text_v2 as text
    return run(request(text.compile_text(source, imports)['program'], roles, claims, windows, policy))
