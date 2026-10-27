"""Authored corporate example and independent manual engine composition."""
from copy import deepcopy
from pathlib import Path
import importlib.util
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
import declared_company_program_v1 as program


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


ex = load('declared_book_examples', 'data/accounting-master/company-book-transition-20261025/examples.py')
clock = load('declared_clock_examples', 'data/accounting-master/company-method-clock-20261025/examples.py')
engine = program.engine


def fixture(owner='alpha'):
    book, payment = ex.fixture(owner)
    ids = list(book['accounts']); equity = ids[3]
    stock, income, expense = ('stock.' + owner, 'sales.' + owner, 'cost.' + owner) if owner == 'alpha' else ('160', '410', '510')
    book['accounts'].update({stock: {'classification': 'asset'}, income: {'classification': 'income'}, expense: {'classification': 'expense'}})
    book['balances'].update({stock: '20/1', income: '0/1', expense: '0/1', equity: '-100/1'})
    schemas = deepcopy(payment['schemas'])
    empty = ex.record({}); schemas[program.digest(empty)] = empty
    money = engine.money_type(book); zero = ex.const(money, '0/1')
    identity = 'synthetic.declared.inventory.sale'
    pre_types = {'inventory': money, 'cost': money, 'proceeds': money, 'approved': ex.core.BOOL}
    pre = ex.conditions(identity, pre_types, [
        ('cost_nonnegative', ex.binary('le', deepcopy(zero), ex.ref('cost')), ['cost'], 'invalid'),
        ('within_inventory', ex.binary('le', ex.ref('cost'), ex.ref('inventory')), ['cost', 'inventory'], 'invalid'),
        ('proceeds_nonnegative', ex.binary('le', deepcopy(zero), ex.ref('proceeds')), ['proceeds'], 'invalid'),
        ('applicable', ex.ref('approved'), ['approved'], 'unsupported')])
    post = ex.conditions(identity, {'inventory': money}, [
        ('inventory_nonnegative', ex.binary('le', deepcopy(zero), ex.ref('inventory')), ['inventory'], 'invalid')])
    negative = lambda name: ex.binary('sub', deepcopy(zero), ex.ref(name))
    monetary = {'profile': engine.monetary.PROFILE, 'method_id': identity, 'version': '1',
                'inputs': {k: ex.decl(money, k, 'reported_measurement') for k in ['cost', 'proceeds']},
                'calculations': [], 'accounts': {k: deepcopy(money) for k in ['cash', 'inventory', 'income', 'expense']},
                'cash_account': 'cash', 'postings': [
                    {'id': 'cash', 'account': 'cash', 'expression': ex.ref('proceeds'), 'requires': ['proceeds']},
                    {'id': 'income', 'account': 'income', 'expression': negative('proceeds'), 'requires': ['proceeds']},
                    {'id': 'inventory', 'account': 'inventory', 'expression': negative('cost'), 'requires': ['cost']},
                    {'id': 'expense', 'account': 'expense', 'expression': ex.ref('cost'), 'requires': ['cost']}],
                'flows': [{'id': 'receipt', 'activity': 'operating', 'origin': 'authored_inventory_sale',
                           'expression': ex.ref('proceeds'), 'requires': ['proceeds']}]}
    method = {'profile': engine.METHOD, 'id': identity, 'version': '1', 'context': deepcopy(book['context']),
              'account_map': {'cash': book['cash_account'], 'inventory': stock, 'income': income, 'expense': expense},
              'preconditions': {'manifest': pre, 'bindings': {'inventory': ex.account('inventory'),
                               **{k: ex.event(k) for k in ['cost', 'proceeds', 'approved']}}},
              'postconditions': {'manifest': post, 'bindings': {'inventory': ex.account('inventory')}},
              'monetary': {'definition': monetary, 'bindings': {k: ex.event(k) for k in ['cost', 'proceeds']}},
              'memory': {'definition': {'profile': engine.memory.PROFILE, 'state_schema': book['memory_schema'],
                         'input_schema': program.digest(empty), 'operations': []}, 'input_bindings': {}},
              'residual_prerequisites': ['Authored aggregate cost and applicability; no lot valuation, tax or actual-company admission.']}
    registry = clock.bind_request(book, payment)['registry']
    types = program.methods.event_declarations(method)
    registry['entries']['sell'] = {'method_sha256': program.digest(method), 'method': method, 'schemas': deepcopy(schemas),
                                  'account_classes': {r: book['accounts'][a]['classification'] for r, a in method['account_map'].items()},
                                  'event_inputs': types, 'metadata_bindings': {}, 'clock': {'kind': 'direct_event_date'}}
    mapping = {'profile': program.reports.MAP, 'context': deepcopy(book['context']),
               'lines': [{'id': 'line.' + str(i), 'label': a, 'classification': row['classification'], 'accounts': [a]}
                         for i, (a, row) in enumerate(book['accounts'].items())]}
    policies = {k: {'kind': 'preserve', 'provenance': 'Authored lifetime loan memory and fixed complementary state'} for k in book['memory_types']}
    notes = [{'id': 'debt_terms', 'label': 'Debt terms and maturity', 'status': 'missing',
              'reason': 'Synthetic loan has no source disclosure package'}]

    def event(key, ident, day, values):
        declared = registry['entries'][key]['event_inputs']
        return {'kind': 'event', 'method_key': key, 'event': {'id': ident, 'date': day, 'inputs': {
            k: {'type': deepcopy(declared[k]), 'value': engine.known(v), 'provenance': 'Authored synthetic event'} for k, v in values.items()}}}

    def report(ident, cutoff):
        return {'kind': 'report', 'id': ident, 'cutoff': cutoff, 'equity_movements': [], 'notes': deepcopy(notes)}

    def close(year):
        return {**report('close.' + str(year), str(year) + '-12-31'), 'kind': 'carry', 'retained_account': equity,
                'next_end_exclusive': str(year + 2) + '-01-01', 'memory_policies': deepcopy(policies)}

    commands = [event('sell', 'sale.2027', '2027-02-01', {'proceeds': '40/1', 'cost': '15/1', 'approved': True}),
                report('interim.2027', '2027-06-30'),
                event('pay', 'pay.2027', '2027-07-01', {'amount': '7/2', 'approved': True}),
                report('annual.2027', '2027-12-31'), close(2027),
                event('sell', 'sale.2028', '2028-02-01', {'proceeds': '8/1', 'cost': '5/1', 'approved': True}),
                event('pay', 'pay.2028', '2028-03-01', {'amount': '53/2', 'approved': True}),
                report('annual.2028', '2028-12-31'), close(2028), report('opening.2029', '2029-01-01')]
    return {'profile': program.PROFILE, 'name': 'two-period-' + owner, 'opening': book, 'schemas': schemas,
            'registry': registry, 'mapping': mapping, 'commands': commands}


def manual(body):
    """Separate explicit engine calls; no runner request helper or future hashes."""
    opening = deepcopy(body['opening']); current = deepcopy(opening); rows = []
    for command in body['commands']:
        before = program.digest(current); basis = program.digest(opening)
        if command['kind'] == 'event':
            request = {'profile': program.methods.PROFILE, 'expected_state_sha256': program.digest(current),
                       'expected_registry_sha256': program.digest(body['registry']), 'registry': deepcopy(body['registry']),
                       'method_key': command['method_key'], 'event': deepcopy(command['event'])}
            result = program.methods.propose(current, request)
            assert result['status'] == 'proposed', result
            current = result['transition']['after']
        else:
            snapshot = deepcopy(current); snapshot['date'] = command['cutoff']
            request = program.reports.request(opening, snapshot, body['schemas'], body['mapping'],
                                              command['equity_movements'], command['notes'])
            if command['kind'] == 'report':
                result = program.reports.report(request); assert result['status'] == 'reported', result
                current = snapshot
            else:
                request = program.carry.request(request, command['id'], command['retained_account'],
                                                command['next_end_exclusive'], command['memory_policies'])
                result = program.carry.propose(request); assert result['status'] == 'proposed', result
                current = result['next_opening']; opening = deepcopy(current)
        rows.append({'command': deepcopy(command), 'request': request, 'result': result,
                     'before_sha256': before, 'after_sha256': program.digest(current),
                     'opening_before_sha256': basis, 'opening_after_sha256': program.digest(opening)})
    return rows, current, opening


def compare():
    cases = []
    for owner in ['alpha', 'beta']:
        body = fixture(owner); original = deepcopy(body); result = program.run(body)
        rows, current, opening = manual(body)
        checks = {'complete': result['status'] == 'complete_provisional', 'current': result.get('current') == current,
                  'opening': result.get('opening') == opening, 'input_unchanged': body == original,
                  'replay': program.verify(body, result), 'trace_count': len(result.get('trace', [])) == 10}
        for i, expected in enumerate(rows):
            observed = result.get('trace', [])[i] if i < len(result.get('trace', [])) else {}
            for key, value in expected.items():checks[str(i) + ':' + key] = observed.get(key) == value
        balances = current['balances']; keys = list(body['opening']['accounts'])
        expected = {keys[0]: '118/1', keys[1]: '0/1', keys[2]: '10/1', keys[3]: '-128/1',
                    keys[4]: '0/1', keys[5]: '0/1', keys[6]: '0/1'}
        checks['independent_final_balances'] = balances == expected
        final = rows[7]['result']; first = rows[3]['result']
        checks['first_cash'] = first['cash_flows']['closing_cash'] == '273/2'
        checks['first_equity'] = first['equity']['closing'] == '125/1'
        checks['first_profit'] = first['income']['profit'] == '25/1'
        checks['second_cash'] = final['cash_flows']['closing_cash'] == '118/1'
        checks['second_profit'] = final['income']['profit'] == '3/1'
        checks['second_equity'] = final['equity']['closing'] == '128/1'
        checks['second_ocf'] = final['cash_flows']['activities']['operating']['net'] == '8/1'
        checks['second_financing'] = final['cash_flows']['activities']['financing']['net'] == '-53/2'
        leaf = current['memory']['loan'] if owner == 'alpha' else current['memory']['contracts']['obligation']
        checks['loan_memory'] = leaf == {'outstanding': '0/1', 'paid': '30/1', 'last_date': '2028-03-01', 'last_event': 'pay.2028'}
        checks['history'] = current['seen'] == ['sale.2027', 'pay.2027', 'close.2027', 'sale.2028', 'pay.2028', 'close.2028']
        checks['period'] = current['period'] == {'start': '2029-01-01', 'end_exclusive': '2030-01-01'}
        checks['flags'] = all(result[k] is False for k in program.FLAGS)
        cases.append({'case': owner, 'program': body, 'result': result, 'manual': rows, 'checks': checks})
    return {'cases': cases, 'checks': [{'name': c['case'] + ':' + k, 'passed': bool(v)} for c in cases for k, v in c['checks'].items()]}


if __name__ == '__main__':
    result = compare(); failures = [x['name'] for x in result['checks'] if not x['passed']]
    print(json.dumps({'cases': len(result['cases']), 'checks': len(result['checks']), 'failures': failures}))
    raise SystemExit(bool(failures))
