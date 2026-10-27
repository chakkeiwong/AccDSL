"""Exact diagnostic monetary derivation; never admits or commits a method."""
from copy import deepcopy
from fractions import Fraction
import re
import method_requirements_v1 as core
import method_requirements_v2 as dimensions

PROFILE = 'MethodMonetaryEffects/1'
MAX_ENTRIES = 256
MAX_BITS = 4096
BOUNDARY = {'executed': False, 'source_admission': False,
            'accounting_admission': False, 'method_eligible': False,
            'committed': False, 'scope': 'selected_monetary_derivation_only'}


def bounded(value):
    core.need(max(abs(value.numerator).bit_length(), value.denominator.bit_length())
              <= MAX_BITS, 'rational_bit_limit')
    return value


def rational(value):
    return bounded(core.scalar(value, 'rational'))


def numeric_type(value):
    dimensions.typed(value)
    core.need(value['kind'] == 'rational', 'numeric_type')
    rational(value['scale'])
    return value


def expression(node, symbols, counter, depth=0):
    counter[0] += 1
    core.need(counter[0] <= core.MAX_NODES and depth <= core.MAX_DEPTH,
              'expression_limit')
    core.need(type(node) is dict and type(node.get('op')) is str, 'expression')
    op = node['op']
    if op == 'ref':
        core.closed(node, ['op', 'id'], 'ref')
        core.text(node['id'], 'reference')
        core.need(node['id'] in symbols, 'undeclared_or_forward_reference')
        item = symbols[node['id']]
        return item['type'], set(item['dependencies'])
    if op == 'const':
        core.closed(node, ['op', 'type', 'value'], 'const')
        numeric_type(node['type'])
        rational(node['value'])
        return node['type'], set()
    core.need(op in ['add', 'sub', 'mul', 'min'], 'unsupported_operator:'+op)
    core.closed(node, ['op', 'left', 'right'], op)
    a, ar = expression(node['left'], symbols, counter, depth+1)
    b, br = expression(node['right'], symbols, counter, depth+1)
    if op == 'mul':
        t = numeric_type(dimensions.product_type(a, b))
    else:
        core.need(a == b, 'type_or_context_mismatch')
        t = a
    return t, ar | br


def compile_definition(definition):
    core.need(len(core.canonical(definition)) <= core.MAX_BYTES, 'definition_size_limit')
    core.closed(definition, ['profile', 'method_id', 'version', 'inputs',
                            'calculations', 'accounts', 'cash_account',
                            'postings', 'flows'], 'monetary_definition')
    core.need(definition['profile'] == PROFILE, 'profile')
    core.text(definition['method_id'], 'method_id')
    core.text(definition['version'], 'version')
    inputs, accounts = definition['inputs'], definition['accounts']
    core.need(type(inputs) is dict and len(inputs) <= MAX_ENTRIES, 'input_limit')
    core.need(type(accounts) is dict and 0 < len(accounts) <= MAX_ENTRIES, 'account_limit')
    symbols, original = {}, {}
    for key, item in inputs.items():
        core.text(key, 'input_id')
        core.closed(item, ['type', 'role', 'source_ref'], 'input_declaration')
        numeric_type(item['type'])
        core.need(type(item['role']) is str and item['role'] in core.ROLES
                  and item['role'] != 'caller_finding', 'numeric_input_role')
        core.text(item['source_ref'], 'source_ref')
        symbols[key] = {'type': deepcopy(item['type']), 'dependencies': [key]}
        original[key] = {**deepcopy(item), 'type': dimensions.encoded(item['type'])}
    core.text(definition['cash_account'], 'cash_account')
    core.need(definition['cash_account'] in accounts, 'cash_account_unregistered')
    cash_type = numeric_type(accounts[definition['cash_account']])
    dims = cash_type['dimensions']
    core.need(len(dims) == 1 and next(iter(dims)).startswith('currency:')
              and len(next(iter(dims))) > len('currency:')
              and next(iter(dims.values())) == 1, 'currency_amount_type')
    for key, t in accounts.items():
        core.text(key, 'account_id')
        numeric_type(t)
        core.need(t == cash_type, 'account_monetary_context_mismatch')
    counter, used, compiled = [0], set(), {}
    for category in ['calculations', 'postings', 'flows']:
        rows = definition[category]
        core.need(type(rows) is list and len(rows) <= MAX_ENTRIES, category+'_limit')
        compiled[category], seen = [], set()
        for row in rows:
            fields = ['id', 'expression', 'requires']
            fields += {'calculations': ['type'], 'postings': ['account'],
                       'flows': ['activity', 'origin']}[category]
            core.closed(row, fields, category)
            core.text(row['id'], category+'_id')
            core.need(row['id'] not in seen, 'duplicate_'+category+'_id')
            seen.add(row['id'])
            t, dependencies = expression(row['expression'], symbols, counter)
            core.identifiers(row['requires'], 'requires')
            core.need(set(row['requires']) == dependencies, 'inexact_dependency_declaration')
            used |= dependencies
            if category == 'calculations':
                core.need(row['id'] not in symbols, 'calculation_identity_collision')
                numeric_type(row['type'])
                core.need(t == row['type'], 'calculation_type_mismatch')
                symbols[row['id']] = {'type': deepcopy(t), 'dependencies': sorted(dependencies)}
            elif category == 'postings':
                core.text(row['account'], 'account')
                core.need(row['account'] in accounts, 'unknown_account')
                core.need(t == accounts[row['account']], 'posting_type_mismatch')
            else:
                core.need(type(row['activity']) is str and row['activity'] in
                          ['operating', 'investing', 'financing'], 'cash_activity')
                core.text(row['origin'], 'cash_origin')
                core.need(t == cash_type, 'cash_flow_type_mismatch')
            compiled[category].append({'type': deepcopy(t), 'dependencies': sorted(dependencies)})
    core.need(used == set(inputs), 'unused_input_declaration')
    return compiled, original


def evaluate(node, values):
    op = node['op']
    if op == 'ref':
        item = values[node['id']]
        return item['value'], deepcopy(item['unresolved_inputs'])
    if op == 'const':
        return rational(node['value']), {}
    a, missing_a = evaluate(node['left'], values)
    b, missing_b = evaluate(node['right'], values)
    missing = {**missing_a, **missing_b}
    if missing:
        return None, missing
    if op == 'add':
        result = a+b
    elif op == 'sub':
        result = a-b
    elif op == 'mul':
        result = a*b
    elif op == 'min':
        result = min(a, b)
    else:
        raise core.Invalid('unsupported_operator:'+op)
    return bounded(result), {}


def fmt(value):
    return f'{value.numerator}/{value.denominator}'


def derive(registry, selected_digest, values):
    """Derive from a pinned definition; diagnostics are never posting authority."""
    try:
        core.need(type(registry) is dict, 'registry')
        core.need(type(selected_digest) is str and re.fullmatch('[0-9a-f]{64}', selected_digest)
                  is not None, 'selection_digest')
        if selected_digest not in registry:
            return {**BOUNDARY, 'status':'unsupported', 'reason':'definition_unavailable',
                    'selected_digest':selected_digest}
        definition = registry[selected_digest]
        core.need(core.digest(definition) == selected_digest, 'definition_digest_mismatch')
        compiled, original = compile_definition(definition)
        core.validate_values({'inputs':original}, values)
        symbols = {}
        for key in original:
            item = values.get(key, {'status':'unknown', 'reason':'missing_input'})
            symbols[key] = ({'value':rational(item['value']), 'unresolved_inputs':{}}
                            if item['status'] == 'known' else
                            {'value':None, 'unresolved_inputs':{key:item['reason']}})
        results, pending = {}, {}
        for category in ['calculations', 'postings', 'flows']:
            results[category] = []
            for row, meta in zip(definition[category], compiled[category]):
                value, missing = evaluate(row['expression'], symbols)
                pending.update(missing)
                binding = ({'status':'unknown', 'reason':'monetary_operand_unresolved'} if missing
                           else {'status':'known', 'value':fmt(value)})
                result = {'id':row['id'], **deepcopy(meta), 'binding':binding,
                          'unresolved_inputs':missing}
                for key in ['account', 'activity', 'origin']:
                    if key in row:
                        result[key] = row[key]
                results[category].append(result)
                if category == 'calculations':
                    symbols[row['id']] = {'value':value, 'unresolved_inputs':missing}
        answer = {**BOUNDARY, 'profile':PROFILE, 'selected_digest':selected_digest,
                  'values_sha256':core.digest(values), 'method_id':definition['method_id'],
                  'version':definition['version'], 'input_declarations':deepcopy(definition['inputs']),
                  'diagnostics':results, 'unresolved_inputs':pending}
        if pending:
            return {**answer, 'status':'unresolved'}
        journal = {key:Fraction(0) for key in definition['accounts']}
        for row in results['postings']:
            key = row['account']
            journal[key] = bounded(journal[key]+rational(row['binding']['value']))
        total = Fraction(0)
        for value in journal.values():
            total = bounded(total+value)
        core.need(total == 0, 'unbalanced_derived_journal')
        flows, cash = [], Fraction(0)
        for row in results['flows']:
            value = rational(row['binding']['value'])
            cash = bounded(cash+value)
            flows.append({'id':row['id'], 'activity':row['activity'], 'origin':row['origin'], 'amount':fmt(value)})
        core.need(cash == journal[definition['cash_account']], 'derived_gross_cash_mismatch')
        return {**answer, 'status':'derived', 'journal':{k:fmt(v) for k,v in journal.items()},
                'flows':flows, 'meaning':'exact supplied-input derivation; financial domains and admission remain separate'}
    except (ValueError, TypeError, KeyError, RecursionError, OverflowError) as exc:
        return {**BOUNDARY, 'status':'invalid', 'reason':str(exc)[:250]}
