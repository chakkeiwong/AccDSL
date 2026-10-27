"""Independent financing schedule amounts and explicit adverse fixtures."""
from copy import deepcopy
from pathlib import Path
import importlib.util
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
import declared_financing_schedules_v1 as schedules
import declared_working_capital_v1 as wc1
import declared_working_capital_v2 as wc2


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


finance = load('validated_finance_examples', 'data/accounting-master/declared-financing-clock-20261025/examples.py')
program = finance.program


def fixture(owner='alpha'):
    body, _, _, mapping = finance.fixture(owner)
    return body, mapping


def subset(body, indices):
    body = deepcopy(body)
    body['commands'] = [body['commands'][i] for i in indices]
    return prune(body)


def prune(body):
    keys = {c['method_key'] for c in body['commands'] if c['kind'] == 'event'}
    body['registry']['entries'] = {k: v for k, v in body['registry']['entries'].items() if k in keys}
    return body


def report_command(ident, date):
    return {'kind': 'report', 'id': ident, 'cutoff': date, 'equity_movements': [], 'notes': []}


def carry_command(body, mapping):
    return {**report_command('carry', '2027-12-31'), 'kind': 'carry',
            'retained_account': mapping['retained'], 'next_end_exclusive': '2029-01-01',
            'memory_policies': {p: {'kind': 'preserve', 'provenance': 'Explicit preservation diagnostic'}
                                for p in body['opening']['memory_types']}}


def request(body, result, mapping, report_id='annual'):
    return schedules.request(body, result, report_id,
        {k: mapping[k] for k in finance.financing.CLASSES},
        '/finance/cursor', '/finance/debt', finance.POLICY, finance.INTERVALS)


def unknown_method(body, gross=False):
    entry = deepcopy(body['registry']['entries']['debt_issue'])
    method = entry['method']
    identity = 'diagnostic.gross_offset' if gross else 'diagnostic.cursor_change'
    method['id'] = identity
    for key in ['preconditions', 'postconditions']:
        method[key]['manifest']['method_id'] = identity
    monetary = method['monetary']['definition']
    monetary['method_id'] = identity
    if gross:
        money = program.engine.money_type(body['opening'])
        monetary['postings'] = [
            {'id': name, 'account': 'debt', 'expression': finance.financing.constant(money, amount), 'requires': []}
            for name, amount in [('gross-debit', '1/1'), ('gross-credit', '-1/1')]]
    else:
        method['memory']['definition']['operations'].append(
            {'id': 'change-cursor', 'op': 'replace', 'path': ['finance', 'cursor'],
             'value': {'kind': 'literal', 'value': '2027-02-01'}})
    entry['method_sha256'] = program.digest(method)
    body['registry']['entries']['foreign'] = entry
    body['commands'] = [finance.event(body, 'foreign', 'foreign', '2027-01-01', {'amount': '0/1'}),
                        report_command('annual', '2027-01-01')]
    return prune(body)


def compare():
    cases = []
    for owner in ['alpha', 'beta']:
        body, mapping = fixture(owner)
        result = program.run(body)
        output = schedules.report(request(body, result, mapping))
        checks = {'program_complete': result['status'] == 'complete_provisional',
                  'reported': output['status'] == 'reported'}
        assert checks['reported'], output
        expected = {'debt': ('0/1', '120/1', '40/1', '80/1'),
                    'interest_payable': ('0/1', '31/5', '4/1', '11/5'),
                    'capital': ('120/1', '30/1', '0/1', '150/1'),
                    'retained': ('0/1', '0/1', '12/1', '-12/1'),
                    'dividend_payable': ('0/1', '12/1', '5/1', '7/1')}
        for key, amounts in expected.items():
            row = output['schedules'][key]
            for field, value in zip(['opening', 'increases', 'decreases', 'closing'], amounts):
                checks[key + ':' + field] = row[field] == value
            checks[key + ':reconciliation'] = row['reconciliation'] == '0/1'
            for movement in row['movements']:
                step = result['trace'][movement['trace_index']]
                checks[key + ':event:' + movement['event_id']] = (
                    movement['request_sha256'] == program.digest(step['request']) and
                    movement['result_sha256'] == program.digest(step['result']) and
                    movement['inputs'] == step['command']['event']['inputs'])
        checks['interest_expense'] = output['interest_expense'] == '31/5'
        checks['cash_by_activity'] = output['financing_cash']['by_activity'] == {
            'operating': '-4/1', 'investing': '0/1', 'financing': '105/1'}
        coverage = output['interest_coverage']
        checks['coverage_complete'] = coverage['complete_for_selected_period'] and not coverage['needs']
        checks['actual_intervals'] = [(x['start'], x['end_exclusive'], x['days'], x['principal'], x['interest'])
            for x in coverage['intervals']] == [
                ('2027-01-01', '2027-04-01', 90, '100/1', '9/5'),
                ('2027-04-01', '2027-07-01', 91, '80/1', '182/125'),
                ('2027-07-01', '2028-01-01', 184, '80/1', '368/125')]
        checks['out_of_scope_operating_events'] = len(output['out_of_scope_events']) == 6
        checks['completeness_flags_false'] = all(output[k] is False for k in program.FLAGS)
        working = wc2.report(wc2.request(body, result, 'annual',
            {k: mapping[k] for k in finance.op.operations.CLASSES}, '/stock/unit_cost'))
        checks['working_capital_reported'] = working['status'] == 'reported'
        checks['working_capital_residual'] = working.get('cash_diagnostic', {}).get('unexplained_by_four_account_bridge') == '11/5'
        cases.append({'case': owner, 'request': request(body, result, mapping), 'schedule': output,
                      'working_capital': working, 'checks': checks})
    # Explicitly convert protocol identity and compare actual v1/v2 amounts.
    original, _, _, mapping = finance.op.fixture()
    converted = deepcopy(original)
    converted['profile'] = program.PROFILE
    converted['registry']['profile'] = program.methods.REGISTRY
    a = finance.op.program.run(original)
    b = program.run(converted)
    roles = {k: mapping[k] for k in finance.op.operations.CLASSES}
    x = wc1.report(wc1.request(original, a, 'interim', roles, '/stock/unit_cost'))
    y = wc2.report(wc2.request(converted, b, 'interim', roles, '/stock/unit_cost'))
    checks = {'both_reported': x['status'] == y['status'] == 'reported',
              'financial_report_equality': a['trace'][-1]['result'] == b['trace'][-1]['result'],
              'cash_diagnostic_equality': x.get('cash_diagnostic') == y.get('cash_diagnostic')}
    for key in wc1.SCOPED:
        for field in ['opening', 'increases', 'decreases', 'net_change', 'closing', 'categories', 'reconciliation']:
            checks[key + ':' + field] = x['schedules'][key][field] == y['schedules'][key][field]
    cases.append({'case': 'working-capital-compatibility', 'before': x, 'after': y, 'checks': checks})
    return {'cases': cases, 'checks': [{'name': c['case'] + ':' + k, 'passed': bool(v)}
                                     for c in cases for k, v in c['checks'].items()]}
