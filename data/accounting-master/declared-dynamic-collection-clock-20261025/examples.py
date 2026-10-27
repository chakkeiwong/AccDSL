"""Synthetic receivable population; exact independent expectations, no source facts."""
from copy import deepcopy
from pathlib import Path
import importlib.util
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
import declared_collection_clock_v1 as clock
import declared_company_text_v2 as text

spec = importlib.util.spec_from_file_location('operating_clock_baseline',
    ROOT / 'data/accounting-master/declared-operating-cycle-20261025/examples.py')
operating = importlib.util.module_from_spec(spec); spec.loader.exec_module(operating)
program = clock.program


def event(body, key, identity, day, amount=None, approved=True):
    params = {'approved': approved}
    if amount is not None: params['amount'] = amount
    types = body['registry']['entries'][key]['event_inputs']
    return {'kind': 'event', 'method_key': key, 'event': {'id': identity, 'date': day,
        'inputs': {k: {'type': deepcopy(types[k]), 'value': program.engine.known(v),
                      'provenance': 'Explicit synthetic collection premise'} for k, v in params.items()}}}


def fixture(owner='alpha', carry=False):
    body, native_spec, _, mapping = operating.fixture(owner)
    book = body['opening']; money = program.engine.money_type(book)
    book['balances'] = {k: '0/1' for k in book['balances']}
    for role, value in [('cash', '100/1'), ('receivables', '100/1'), ('capital', '-200/1')]:
        book['balances'][mapping[role]] = value
    schema = deepcopy(body['schemas'][book['memory_schema']])
    row_schema = clock.record({'due': clock.scalar('date'), 'remaining': clock.scalar('rational'),
                               'assessed': clock.scalar('rational'), 'overdue': clock.scalar('rational')})
    schema['properties']['collection'] = clock.record({'cursor': clock.scalar('date'), 'assessed': {'type': 'boolean'},
                                                      'a': deepcopy(row_schema), 'b': deepcopy(row_schema)})
    schema['required'].append('collection')
    book['memory_schema'] = program.digest(schema)
    book['memory']['collection'] = {'cursor': '2027-01-01', 'assessed': False,
        'a': {'due': '2027-01-31', 'remaining': '60/1', 'assessed': '0/1', 'overdue': '0/1'},
        'b': {'due': '2027-02-28', 'remaining': '40/1', 'assessed': '0/1', 'overdue': '0/1'}}
    book['memory_types'].update({'/collection/cursor': deepcopy(clock.DATE), '/collection/assessed': deepcopy(clock.core.BOOL)})
    claims = []
    for key in ['a', 'b']:
        for field in ['due', 'remaining', 'assessed', 'overdue']:
            book['memory_types']['/collection/' + key + '/' + field] = deepcopy(clock.DATE if field == 'due' else money)
        claims.append({'id': 'invoice.' + key, 'due_date': book['memory']['collection'][key]['due'],
            'due_pointer': '/collection/' + key + '/due', 'balance_pointer': '/collection/' + key + '/remaining',
            'assessed_balance_pointer': '/collection/' + key + '/assessed', 'overdue_pointer': '/collection/' + key + '/overdue'})
    schemas = {book['memory_schema']: schema}
    roles = {k: mapping[k] for k in ['cash', 'receivables']}
    policy = {'profile': clock.POLICY, 'past_due': 'strictly_after_due_date', 'cursor_pointer': '/collection/cursor',
              'assessed_pointer': '/collection/assessed', 'provenance': 'Synthetic due-day convention, state-only assessment'}
    dates = ['2027-01-01', '2027-02-01', '2027-03-01', '2028-01-01', '2028-02-01']
    windows = [{'start': a, 'end_exclusive': b} for a, b in zip(dates, dates[1:])]
    registry = clock.build(book, schemas, roles, claims, windows, policy)
    for entry in registry['entries'].values(): schemas.update(deepcopy(entry['schemas']))
    body.update(profile=program.PROFILE, name='collections-' + owner, schemas=schemas, registry=registry)
    body['commands'] = [event(body, 'collect.1', 'receipt.a', '2027-01-15', '20/1'),
        event(body, 'assess.1', 'assessment.jan', '2027-01-31'),
        {'kind': 'report', 'id': 'jan', 'cutoff': '2027-01-31', 'equity_movements': [], 'notes': []},
        event(body, 'collect.2', 'receipt.b', '2027-02-15', '10/1'),
        event(body, 'assess.2', 'assessment.feb', '2027-02-28'),
        event(body, 'assess.3', 'assessment.year', '2027-12-31'),
        {'kind': 'report', 'id': 'annual', 'cutoff': '2027-12-31', 'equity_movements': [], 'notes': []}]
    if carry:
        body['commands'] += [{'kind': 'carry', 'id': 'boundary', 'cutoff': '2027-12-31',
            'equity_movements': [], 'notes': [], 'retained_account': mapping['retained'],
            'next_end_exclusive': '2029-01-01', 'memory_policies': {p: {'kind': 'preserve',
                'provenance': 'Keep contractual and assessment history'} for p in book['memory_types']}},
            event(body, 'collect.1', 'receipt.a.next', '2028-01-10', '40/1'),
            event(body, 'assess.4', 'assessment.next', '2028-01-31'),
            {'kind': 'report', 'id': 'next', 'cutoff': '2028-01-31', 'equity_movements': [], 'notes': []}]
    native_spec['opening'] = {role: book['balances'][account] for role, account in mapping.items()}
    return clock.request(body, roles, claims, windows, policy), mapping, native_spec


def compare():
    cases, checks = [], []
    for owner in ['alpha', 'beta']:
        for carry in [False, True]:
            q, mapping, spec = fixture(owner, carry); before = deepcopy(q)
            result = clock.run(q); p = q['program']; name = owner + ('.carry' if carry else '.annual')
            check = {'complete': result['status'] == 'complete_provisional', 'input_unchanged': q == before}
            if not check['complete']: raise AssertionError(result.get('reason', result.get('stop')))
            execution = result['program_result']; native = operating.native.Engine(spec)
            for i, amount in enumerate(['20/1', '10/1']):
                day = ['2027-01-15', '2027-02-15'][i]
                native.apply(operating.native.event(spec, 'receipt.' + str(i), 'collect', {'amount': amount}, period='2027', date_=day))
            annual = next(row['result'] for row in execution['trace'] if row['command'].get('id') == 'annual')
            expected = native.snapshot()['balances']
            annual_state = next(row['request']['closing'] for row in execution['trace'] if row['command'].get('id') == 'annual')
            check['native_all_balances'] = annual_state['balances'] == {mapping[k]: operating.fmt(v) for k, v in expected.items()}
            check.update(independent_assets=annual['balance_sheet']['total_assets'] == '200/1',
                         independent_profit=annual['income']['profit'] == '0/1',
                         independent_operating_cash=annual['cash_flows']['activities']['operating']['net'] == '30/1',
                         independent_receivable=annual_state['balances'][mapping['receivables']] == '70/1')
            for i, expected_overdue in enumerate([['0/1', '0/1'], ['40/1', '0/1'], ['40/1', '30/1']]):
                check['assessment_' + str(i)] = [r['assessed_overdue'] for r in result['assessments'][i]['observation']['claims']] == expected_overdue
            for row in execution['trace']:
                if row['command']['kind'] == 'event' and row['command']['method_key'].startswith('assess.'):
                    ident = row['command']['event']['id']; transition = row['result']['transition']
                    check[ident + ':zero_journal'] = all(v == '0/1' for v in transition['journal'].values())
                    check[ident + ':no_cash_flow'] = transition['flows'] == []
            if carry:
                check['next_cash'] = result['current']['balances'][mapping['cash']] == '170/1'
                check['next_receivable'] = result['current']['balances'][mapping['receivables']] == '30/1'
                boundary = next(row for row in execution['trace'] if row['command'].get('id') == 'boundary')
                check['carry_preserves_memory'] = boundary['result']['next_opening']['memory'] == annual_state['memory']
                check['next_overdue'] = [r['assessed_overdue'] for r in result['observation']['claims']] == ['0/1', '30/1']
            author, imports = text.from_program(p); source = text.render(author)
            check['matched_text_program'] = text.compile_text(source, imports)['program'] == p
            check['matched_text_result'] = clock.execute_text(source, imports, q['roles'], q['claims'], q['windows'], q['policy']) == result
            check['replay'] = clock.verify(q, result)
            check['admission_false'] = all(result[k] is False for k in clock.FLAGS)
            cases.append({'case': name, 'request': q, 'result': result, 'text': source, 'checks': check})
            checks.extend({'name': name + ':' + k, 'passed': bool(v)} for k, v in check.items())
    return {'cases': cases, 'checks': checks}
