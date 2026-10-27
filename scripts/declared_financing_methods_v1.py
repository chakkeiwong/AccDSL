"""Synthetic financing methods with exact finite simple-interest intervals."""
from copy import deepcopy
from datetime import timedelta
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path

import declared_operating_methods_v1 as helpers
import company_method_clock_v2 as methods

MATERIALIZER_SHA256 = '44a3c7733e56240db24fd5699b048bd884576ec0e6b4a8eea27a984c2d74b44a'
engine = helpers.engine
core = helpers.core
PROFILE = 'DeclaredFinancingMethods/1'
POLICY = 'SyntheticActual365Simple/1'
HELPER_SHA256 = '0201b1d8934e9ec40aeee301609090cc6f5d40829eb9d3dd603757f2a61a7590'
DATE = {'kind': 'date', 'context': {}}
CLASSES = {'cash': 'asset', 'debt': 'liability', 'interest': 'expense',
           'interest_payable': 'liability', 'capital': 'equity',
           'retained': 'equity', 'dividend_payable': 'liability'}
KINDS = ('debt_issue', 'debt_redeem', 'interest_pay', 'equity_issue',
         'dividend_declare', 'dividend_pay')
ref, binary, constant = helpers.ref, helpers.binary, helpers.constant
account, event = helpers.account, helpers.event


def fmt(value):
    q = Q(value)
    return f'{q.numerator}/{q.denominator}'


def memory(pointer):
    return {'kind': 'memory', 'pointer': pointer}


def record(fields):
    return {'type': 'object', 'properties': fields, 'required': list(fields),
            'additionalProperties': False}


def scalar(kind):
    return {'type': 'string', 'minLength': 1, 'maxLength': 4096, 'x-exact-kind': kind}


def declaration(typ, name):
    return {'type': deepcopy(typ), 'role': 'state',
            'source_ref': 'declared-financing-premise:' + name}


def conditions(identity, types, rows):
    result = helpers.conditions(identity, types, rows)
    result['inputs'] = {k: declaration(t, k) for k, t in types.items()}
    result['residual_prerequisites'] = [
        'Synthetic financing applicability; no contract, valuation or accounting admission.']
    return result


def build(book, schemas, roles, cursor_pointer, debt_pointer, policy, intervals):
    """Build immutable data definitions, not callbacks or current-state requests."""
    core.need(sha256(Path(helpers.__file__).read_bytes()).hexdigest() == HELPER_SHA256,
              'helper_dependency_hash')
    core.need(sha256(Path(methods.__file__).read_bytes()).hexdigest() == MATERIALIZER_SHA256,
              'materializer_dependency_hash')
    methods.protected()
    engine.validate_book(book, schemas)
    core.need(type(roles) is dict and set(roles) == set(CLASSES), 'financing_roles')
    core.need(len(set(roles.values())) == len(roles), 'injective_financing_roles')
    for role, classification in CLASSES.items():
        core.need(roles[role] in book['accounts'] and
                  book['accounts'][roles[role]]['classification'] == classification,
                  'financing_role_class:' + role)
    core.need(roles['cash'] == book['cash_account'], 'financing_cash_role')
    money = engine.money_type(book)
    for pointer, typ in [(cursor_pointer, DATE), (debt_pointer, money)]:
        core.need(book['memory_types'].get(pointer) == typ, 'financing_memory_type')
    _, cursor = engine.binding.located(book['memory'], cursor_pointer)
    _, debt = engine.binding.located(book['memory'], debt_pointer)
    core.need(cursor == book['date'], 'initial_accrual_cursor')
    core.need(debt == book['balances'][roles['debt']] and Q(debt) <= 0,
              'initial_tracked_debt')
    engine.closed(policy, ['profile', 'convention', 'annual_rate',
                           'interest_cash_activity', 'provenance'])
    core.need(policy['profile'] == POLICY and policy['convention'] == 'actual_days/365_simple',
              'synthetic_interest_convention')
    core.need(engine.monetary.rational(policy['annual_rate']) >= 0, 'nonnegative_rate')
    core.need(policy['interest_cash_activity'] in ['operating', 'financing'],
              'explicit_interest_cash_policy')
    engine.text(policy['provenance'], 'policy_provenance')
    core.need(type(intervals) is list and 0 < len(intervals) <= 16, 'finite_intervals')
    next_start = cursor
    windows = []
    for window in intervals:
        engine.closed(window, ['start', 'end_exclusive'])
        start, end = (core.scalar(window[k], 'date') for k in ['start', 'end_exclusive'])
        core.need(window['start'] == next_start and start < end, 'contiguous_positive_intervals')
        core.need(book['period']['start'] <= window['start'] and
                  window['end_exclusive'] <= book['period']['end_exclusive'], 'interval_period')
        windows.append((window, (end - timedelta(days=1)).isoformat(), Q((end-start).days, 365)))
        next_start = window['end_exclusive']
    context = engine.type_context(book)
    def dimension(dims):
        return {'kind': 'rational', 'context': deepcopy(context), 'dimensions': dims, 'scale': '1/1'}
    rate_type = dimension({'time:year': -1})
    years_type = dimension({'time:year': 1})
    shares_type = dimension({'equity:share': 1})
    price_type = dimension({'currency:' + book['context']['currency']: 1, 'equity:share': -1})
    zero = constant(money, '0/1')
    negative = lambda node: binary('sub', deepcopy(zero), node)
    entries = {}
    policy_ref = 'Synthetic policy ' + core.digest(policy) + ': ' + policy['provenance']
    variants = [(k, None) for k in KINDS] + [
        ('interest_accrue.' + str(i+1), w) for i, w in enumerate(windows)]
    for key, window in variants:
        accrue = window is not None
        identity = 'synthetic.financing.' + key
        pre_types = {'approved': core.BOOL, 'debt': money, 'tracked_debt': money}
        pre_bindings = {'approved': event('approved'), 'debt': account('debt'),
                        'tracked_debt': memory(debt_pointer)}
        pre_rows = [('applicable', ref('approved'), ['approved'], 'unsupported'),
                    ('debt_matches_memory', binary('eq', ref('debt'), ref('tracked_debt')),
                     ['debt', 'tracked_debt'], 'invalid'),
                    ('debt_sign', binary('le', ref('debt'), deepcopy(zero)), ['debt'], 'invalid')]
        post_types = {'debt': money, 'tracked_debt': money}
        post_bindings = {'debt': account('debt'), 'tracked_debt': memory(debt_pointer)}
        post_rows = deepcopy(pre_rows[1:])
        numeric, numeric_bindings, supplied = {}, {}, {'approved': deepcopy(core.BOOL)}
        calculations, operations, input_bindings, input_fields = [], [], {}, {}
        metadata = {}
        included = {'cash', 'debt'}

        def numeric_event(name, typ):
            numeric[name] = typ
            numeric_bindings[name] = event(name)
            supplied[name] = deepcopy(typ)
            pre_types[name] = typ
            pre_bindings[name] = event(name)
            pre_rows.append((name + '_nonnegative', binary('le', constant(typ, '0/1'), ref(name)),
                             [name], 'invalid'))

        def control(role):
            if role == 'debt':
                return
            pre_types[role] = money
            pre_bindings[role] = account(role)
            post_types[role] = money
            post_bindings[role] = account(role)
            predicate = (binary('le', ref(role), deepcopy(zero)) if CLASSES[role] == 'liability'
                         else binary('le', deepcopy(zero), ref(role)))
            row = (role + '_sign', predicate, [role], 'invalid')
            pre_rows.append(row)
            post_rows.append(deepcopy(row))

        def write(pointer, value):
            path = [t.replace('~1', '/').replace('~0', '~') for t in pointer[1:].split('/')]
            operations.append({'id': 'write.' + str(len(operations)), 'op': 'replace',
                               'path': path, 'value': value})

        if key in ['debt_issue', 'debt_redeem'] or accrue:
            pre_types.update(cursor=DATE, event_date=DATE)
            pre_bindings.update(cursor=memory(cursor_pointer), event_date=event('event_date'))
            metadata['event_date'] = 'date'
            predicate = binary('eq', ref('cursor'), ref('event_date'))
            deps = ['cursor', 'event_date']
            if accrue:
                interval, at, years = window
                predicate = binary('eq', ref('cursor'), constant(DATE, interval['start']))
                deps = ['cursor']
                pre_rows.append(('interval_event_date', binary('eq', ref('event_date'), constant(DATE, at)),
                                 ['event_date'], 'invalid'))
            pre_rows.append(('accrual_boundary', predicate, deps, 'invalid'))

        flows = []
        if accrue:
            interval, at, years = window
            numeric['principal_signed'] = money
            numeric_bindings['principal_signed'] = account('debt')
            amount = binary('mul', binary('mul', negative(ref('principal_signed')),
                                         constant(rate_type, policy['annual_rate'])),
                            constant(years_type, fmt(years)))
            posting = [('interest', amount, ['principal_signed']),
                       ('interest_payable', negative(deepcopy(amount)), ['principal_signed'])]
            control('interest_payable')
            write(cursor_pointer, {'kind': 'literal', 'value': interval['end_exclusive']})
            post_types['cursor'] = DATE
            post_bindings['cursor'] = memory(cursor_pointer)
            post_rows.append(('cursor_advanced', binary('eq', ref('cursor'),
                              constant(DATE, interval['end_exclusive'])), ['cursor'], 'invalid'))
        elif key == 'equity_issue':
            numeric_event('shares', shares_type)
            numeric_event('price', price_type)
            amount = binary('mul', ref('shares'), ref('price'))
            posting = [('cash', amount, ['shares', 'price']),
                       ('capital', negative(deepcopy(amount)), ['shares', 'price'])]
            flows = [('financing', amount, ['shares', 'price'])]
            control('cash')
        else:
            numeric_event('amount', money)
            if key == 'debt_issue':
                posting = [('cash', ref('amount'), ['amount']),
                           ('debt', negative(ref('amount')), ['amount'])]
                flows = [('financing', ref('amount'), ['amount'])]
                control('cash')
            elif key == 'dividend_declare':
                posting = [('retained', ref('amount'), ['amount']),
                           ('dividend_payable', negative(ref('amount')), ['amount'])]
                control('dividend_payable')
            else:
                liability = {'debt_redeem': 'debt', 'interest_pay': 'interest_payable',
                             'dividend_pay': 'dividend_payable'}[key]
                posting = [(liability, ref('amount'), ['amount']),
                           ('cash', negative(ref('amount')), ['amount'])]
                control('cash')
                control(liability)
                pre_rows += [('obligation_available', binary('le', ref('amount'), negative(ref(liability))),
                              ['amount', liability], 'invalid'),
                             ('cash_available', binary('le', ref('amount'), ref('cash')),
                              ['amount', 'cash'], 'invalid')]
                activity = policy['interest_cash_activity'] if key == 'interest_pay' else 'financing'
                flows = [(activity, negative(ref('amount')), ['amount'])]
            if key in ['debt_issue', 'debt_redeem']:
                numeric['principal_signed'] = money
                numeric_bindings['principal_signed'] = account('debt')
                calculations.append({'id': 'next_debt', 'type': deepcopy(money),
                                     'expression': binary('sub' if key == 'debt_issue' else 'add',
                                                          ref('principal_signed'), ref('amount')),
                                     'requires': ['principal_signed', 'amount']})
                input_fields['next_debt'] = scalar('rational')
                input_bindings['next_debt'] = {'kind': 'calculation', 'name': 'next_debt'}
                write(debt_pointer, {'kind': 'read', 'source': 'inputs', 'pointer': '/next_debt'})
        included |= {r for r, _, _ in posting}
        input_shape = record(input_fields)
        shapes = {**deepcopy(schemas), core.digest(input_shape): input_shape}
        monetary = {'profile': engine.monetary.PROFILE, 'method_id': identity, 'version': '1',
                    'inputs': {k: declaration(t, k) for k, t in numeric.items()},
                    'calculations': calculations, 'accounts': {k: deepcopy(money) for k in sorted(included)},
                    'cash_account': 'cash',
                    'postings': [{'id': r, 'account': r, 'expression': node, 'requires': deps}
                                 for r, node, deps in posting],
                    'flows': [{'id': key, 'activity': activity, 'origin': key, 'expression': node,
                               'requires': deps} for activity, node, deps in flows]}
        method = {'profile': engine.METHOD, 'id': identity, 'version': '1', 'context': deepcopy(book['context']),
                  'account_map': {k: roles[k] for k in sorted(included)},
                  'preconditions': {'manifest': conditions(identity, pre_types, pre_rows), 'bindings': pre_bindings},
                  'postconditions': {'manifest': conditions(identity, post_types, post_rows), 'bindings': post_bindings},
                  'monetary': {'definition': monetary, 'bindings': numeric_bindings},
                  'memory': {'definition': {'profile': engine.memory.PROFILE, 'state_schema': book['memory_schema'],
                                           'input_schema': core.digest(input_shape), 'operations': operations},
                             'input_bindings': input_bindings},
                  'residual_prerequisites': [policy_ref,
                     'Synthetic simple interest; no valuation, contract admission, complete notes or lawful-distribution finding.']}
        if accrue:
            method['residual_prerequisites'].append(
                'Exact interval [' + interval['start'] + ',' + interval['end_exclusive'] +
                '); actual days/365=' + fmt(years))
        entries[key] = {'method_sha256': core.digest(method), 'method': method, 'schemas': shapes,
                        'account_classes': {k: CLASSES[k] for k in sorted(included)},
                        'event_inputs': supplied, 'metadata_bindings': metadata,
                        'clock': {'kind': 'direct_event_date'}}
    return {'profile': methods.REGISTRY, 'context': deepcopy(book['context']), 'entries': entries}
