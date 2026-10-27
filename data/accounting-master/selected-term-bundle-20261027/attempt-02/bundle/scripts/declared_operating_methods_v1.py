"""Six synthetic operating methods over an explicit declared book and role map."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path

import company_method_clock_v1 as methods

engine = methods.transition
core = engine.core
PROFILE = 'DeclaredOperatingMethods/1'
BINDER_SHA256 = '39d9499cf9a36fa14eb3ec0d4d68f23e7a47c137e0494a4d83c2101e317b2f8d'
CLASSES = {'cash': 'asset', 'receivables': 'asset', 'inventory': 'asset',
           'payables': 'liability', 'payroll_payable': 'liability',
           'revenue': 'income', 'cost_of_sales': 'expense', 'payroll': 'expense'}
KINDS = ('purchase', 'deliver', 'collect', 'supplier_pay', 'payroll_accrue', 'payroll_pay')


def ref(name):return {'op': 'ref', 'id': name}
def binary(op, left, right):return {'op': op, 'left': left, 'right': right}
def constant(typ, value):return {'op': 'const', 'type': deepcopy(typ), 'value': value}
def declaration(typ, name):
    return {'type': deepcopy(typ), 'role': 'state', 'source_ref': 'declared-operating-premise:' + name}
def account(role):return {'kind': 'account', 'role': role}
def event(name):return {'kind': 'event', 'name': name}


def conditions(identity, types, rows):
    return {'profile': engine.requirements.PROFILE, 'method_id': identity, 'version': '1',
            'inputs': {k: declaration(t, k) for k, t in types.items()},
            'requirements': [{'id': name, 'guard': constant(core.BOOL, True), 'guard_requires': [],
                              'predicate': predicate, 'requires': deps, 'admission_refs': [],
                              'on_false': status, 'on_unknown': 'unresolved'}
                             for name, predicate, deps, status in rows],
            'required_known': [], 'capabilities': [],
            'residual_prerequisites': ['Synthetic fixed-unit-cost operating method; no source or accounting admission.']}


def build(book, schemas, roles, unit_cost_pointer):
    """Return data definitions; execute no economic event and mutate no input."""
    core.need(sha256(Path(methods.__file__).read_bytes()).hexdigest() == BINDER_SHA256, 'binder_dependency_hash')
    methods.protected(); engine.validate_book(book, schemas)
    core.need(type(roles) is dict and set(roles) == set(CLASSES), 'complete_operating_roles')
    core.need(len(set(roles.values())) == len(roles), 'injective_operating_roles')
    for role, classification in CLASSES.items():
        core.need(roles[role] in book['accounts'] and book['accounts'][roles[role]]['classification'] == classification,
                  'operating_role_class:' + role)
    core.need(roles['cash'] == book['cash_account'], 'operating_cash_role')
    money = engine.money_type(book)
    quantity = {**deepcopy(money), 'dimensions': {'goods:unit': 1}}
    price = {**deepcopy(money), 'dimensions': {'currency:' + book['context']['currency']: 1, 'goods:unit': -1}}
    core.need(unit_cost_pointer in book['memory_types'], 'unit_cost_leaf')
    core.need(core.canonical(book['memory_types'][unit_cost_pointer]) == core.canonical(price), 'unit_cost_dimensions')
    found, unit_cost = engine.binding.located(book['memory'], unit_cost_pointer)
    core.need(found and engine.monetary.rational(unit_cost) > 0, 'positive_unit_cost')
    empty = {'type': 'object', 'properties': {}, 'required': [], 'additionalProperties': False}
    shapes = {**deepcopy(schemas), core.digest(empty): empty}; entries = {}
    zero = constant(money, '0/1')
    negative = lambda expression: binary('sub', deepcopy(zero), expression)
    cost = binary('mul', ref('units'), ref('unit_cost'))
    for kind in KINDS:
        identity = 'synthetic.operating.' + kind
        pre_types = {'approved': core.BOOL}; pre_bindings = {'approved': event('approved')}
        pre_rows = [('applicable', ref('approved'), ['approved'], 'unsupported')]
        numeric = {}; numeric_bindings = {}; post_types = {}; post_bindings = {}; post_rows = []
        supplied = {'approved': deepcopy(core.BOOL)}

        def numeric_event(name, typ):
            numeric[name] = typ; numeric_bindings[name] = event(name)
            supplied[name] = deepcopy(typ); pre_types[name] = typ; pre_bindings[name] = event(name)
            pre_rows.append((name + '_nonnegative', binary('le', constant(typ, '0/1'), ref(name)), [name], 'invalid'))

        def control(role):
            pre_types[role] = money; pre_bindings[role] = account(role)
            post_types[role] = money; post_bindings[role] = account(role)
            predicate = binary('le', ref(role), deepcopy(zero)) if CLASSES[role] == 'liability' else binary('le', deepcopy(zero), ref(role))
            row = (role + '_sign', predicate, [role], 'invalid')
            pre_rows.append(row); post_rows.append(deepcopy(row))

        if kind in ['purchase', 'deliver']:
            numeric_event('units', quantity)
            numeric['unit_cost'] = price; numeric_bindings['unit_cost'] = {'kind': 'memory', 'pointer': unit_cost_pointer}
            pre_types['unit_cost'] = price; pre_bindings['unit_cost'] = deepcopy(numeric_bindings['unit_cost'])
            pre_rows.append(('positive_unit_cost', binary('lt', constant(price, '0/1'), ref('unit_cost')), ['unit_cost'], 'invalid'))
        else:
            numeric_event('amount', money)
        flows = []
        if kind == 'purchase':
            posting = [('inventory', deepcopy(cost), ['units', 'unit_cost']), ('payables', negative(deepcopy(cost)), ['units', 'unit_cost'])]
            control('inventory'); control('payables')
        elif kind == 'deliver':
            numeric_event('consideration', money)
            posting = [('receivables', ref('consideration'), ['consideration']), ('revenue', negative(ref('consideration')), ['consideration']),
                       ('cost_of_sales', deepcopy(cost), ['units', 'unit_cost']), ('inventory', negative(deepcopy(cost)), ['units', 'unit_cost'])]
            control('receivables'); control('inventory')
            pre_rows.append(('inventory_available', binary('le', deepcopy(cost), ref('inventory')), ['units', 'unit_cost', 'inventory'], 'invalid'))
        elif kind == 'collect':
            posting = [('cash', ref('amount'), ['amount']), ('receivables', negative(ref('amount')), ['amount'])]
            control('cash'); control('receivables')
            pre_rows.append(('receivable_available', binary('le', ref('amount'), ref('receivables')), ['amount', 'receivables'], 'invalid'))
            flows = [('collect', ref('amount'))]
        elif kind == 'payroll_accrue':
            posting = [('payroll', ref('amount'), ['amount']), ('payroll_payable', negative(ref('amount')), ['amount'])]
            control('payroll_payable')
        else:
            liability = 'payables' if kind == 'supplier_pay' else 'payroll_payable'
            posting = [(liability, ref('amount'), ['amount']), ('cash', negative(ref('amount')), ['amount'])]
            control('cash'); control(liability)
            pre_rows += [('obligation_available', binary('le', ref('amount'), negative(ref(liability))), ['amount', liability], 'invalid'),
                         ('cash_available', binary('le', ref('amount'), ref('cash')), ['amount', 'cash'], 'invalid')]
            flows = [(kind, negative(ref('amount')))]
        included = {'cash'} | {role for role, _, _ in posting}
        monetary = {'profile': engine.monetary.PROFILE, 'method_id': identity, 'version': '1',
                    'inputs': {k: declaration(t, k) for k, t in numeric.items()}, 'calculations': [],
                    'accounts': {k: deepcopy(money) for k in sorted(included)}, 'cash_account': 'cash',
                    'postings': [{'id': role, 'account': role, 'expression': node, 'requires': deps} for role, node, deps in posting],
                    'flows': [{'id': origin, 'activity': 'operating', 'origin': origin, 'expression': node, 'requires': ['amount']} for origin, node in flows]}
        method = {'profile': engine.METHOD, 'id': identity, 'version': '1', 'context': deepcopy(book['context']),
                  'account_map': {k: roles[k] for k in sorted(included)},
                  'preconditions': {'manifest': conditions(identity, pre_types, pre_rows), 'bindings': pre_bindings},
                  'postconditions': {'manifest': conditions(identity, post_types, post_rows), 'bindings': post_bindings},
                  'monetary': {'definition': monetary, 'bindings': numeric_bindings},
                  'memory': {'definition': {'profile': engine.memory.PROFILE, 'state_schema': book['memory_schema'],
                             'input_schema': core.digest(empty), 'operations': []}, 'input_bindings': {}},
                  'residual_prerequisites': ['Synthetic declared fixed unit cost; maturity, tax, valuation and complete notes are not supplied.']}
        entries[kind] = {'method_sha256': core.digest(method), 'method': method, 'schemas': deepcopy(shapes),
                         'account_classes': {k: CLASSES[k] for k in sorted(included)}, 'event_inputs': supplied,
                         'metadata_bindings': {}, 'clock': {'kind': 'direct_event_date'}}
    return {'profile': methods.REGISTRY, 'context': deepcopy(book['context']), 'entries': entries}


def refusal_diagnostic(call_result):
    """Explain liquidity separately while preserving the primitive refusal record."""
    transition = call_result.get('transition', {})
    findings = transition.get('preconditions', {}).get('findings', [])
    cash = next((r for r in findings if r['id'] == 'cash_available' and r['body_truth'] == 'false'), None)
    others = [r for r in findings if r['id'] != 'cash_available' and r['consequence'] not in ['satisfied', 'not_applicable']]
    if cash is not None and not others:
        return {'category': 'economic_funding_failure', 'criterion': 'cash_available',
                'scope': 'Supplied payment exceeds recorded cash; no financing policy supplied',
                'primitive_status': call_result['status'], 'result_sha256': core.digest(call_result)}
    return {'category': call_result['status'], 'result_sha256': core.digest(call_result)}
