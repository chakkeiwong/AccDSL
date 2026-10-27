"""Authored common operating/financing book and separate monetary comparator."""
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import importlib.util
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
import declared_financing_methods_v1 as financing
import declared_company_program_v2 as program
import declared_company_text_v2 as text
import company_execution_v1 as native

spec = importlib.util.spec_from_file_location('financing_operating_examples',
    ROOT / 'data/accounting-master/declared-operating-cycle-20261025/examples.py')
op = importlib.util.module_from_spec(spec)
spec.loader.exec_module(op)
fmt = op.fmt
INTERVALS = [{'start': '2027-01-01', 'end_exclusive': '2027-04-01'},
             {'start': '2027-04-01', 'end_exclusive': '2027-07-01'},
             {'start': '2027-07-01', 'end_exclusive': '2028-01-01'}]
POLICY = {'profile': financing.POLICY, 'convention': 'actual_days/365_simple',
          'annual_rate': '73/1000', 'interest_cash_activity': 'operating',
          'provenance': 'Explicit synthetic fixed-rate policy; no source admission'}


def event(body, key, ident, day, values):
    types = body['registry']['entries'][key]['event_inputs']
    return {'kind': 'event', 'method_key': key, 'event': {'id': ident, 'date': day,
        'inputs': {k: {'type': deepcopy(types[k]), 'value': program.engine.known(v),
                      'provenance': 'Authored synthetic financing premise'}
                   for k, v in {**values, 'approved': True}.items()}}}


def fixture(owner='alpha', activity='operating'):
    body, native_spec, _, mapping = op.fixture(owner)
    book = body['opening']
    shape = deepcopy(body['schemas'][book['memory_schema']])
    shape['properties']['finance'] = op.record({'cursor': op.scalar('date'), 'debt': op.scalar('rational')})
    shape['required'].append('finance')
    book['memory'].update(finance={'cursor': book['date'], 'debt': '0/1'})
    book['memory_types'].update({'/finance/cursor': deepcopy(financing.DATE),
                                 '/finance/debt': program.engine.money_type(book)})
    book['memory_schema'] = program.digest(shape)
    schemas = {program.digest(shape): shape}
    policy = {**deepcopy(POLICY), 'interest_cash_activity': activity}
    registry = financing.build(book, schemas, {k: mapping[k] for k in financing.CLASSES},
                               '/finance/cursor', '/finance/debt', policy, deepcopy(INTERVALS))
    operating = op.operations.build(book, schemas, {k: mapping[k] for k in op.operations.CLASSES},
                                    '/stock/unit_cost')
    registry['entries'].update(operating['entries'])
    for entry in registry['entries'].values():
        schemas.update(deepcopy(entry['schemas']))
    body.update(profile=program.PROFILE, registry=registry, schemas=schemas, name='financing-' + owner)
    operating_commands = deepcopy(body['commands'][:6])
    rows = [('debt_issue', 'issue.1', '2027-01-01', {'amount': '100/1'}),
            ('interest_accrue.1', 'interest.1', '2027-03-31', {}),
            ('debt_redeem', 'redeem.1', '2027-04-01', {'amount': '40/1'}),
            ('debt_issue', 'issue.2', '2027-04-01', {'amount': '20/1'}),
            ('equity_issue', 'equity.1', '2027-04-02', {'shares': '10/1', 'price': '3/1'}),
            ('dividend_declare', 'dividend.1', '2027-04-03', {'amount': '12/1'}),
            ('dividend_pay', 'dividend.pay.1', '2027-04-04', {'amount': '5/1'}),
            ('interest_accrue.2', 'interest.2', '2027-06-30', {}),
            ('interest_accrue.3', 'interest.3', '2027-12-31', {}),
            ('interest_pay', 'interest.pay.1', '2027-12-31', {'amount': '4/1'})]
    commands = [event(body, *row) for row in rows]
    commands[1:1] = operating_commands
    movements = [
        {'id': 'explain.equity', 'event_id': 'equity.1', 'date': '2027-04-02',
         'account': mapping['capital'], 'amount': '30/1', 'description': 'Synthetic contribution'},
        {'id': 'explain.dividend', 'event_id': 'dividend.1', 'date': '2027-04-03',
         'account': mapping['retained'], 'amount': '-12/1', 'description': 'Synthetic dividend declaration'}]
    commands.append({'kind': 'report', 'id': 'annual', 'cutoff': '2027-12-31',
                     'equity_movements': movements, 'notes': [
                         {'id': 'financing_terms', 'label': 'Financing and distributions',
                          'status': 'missing', 'reason': 'No real contracts, valuation or legal distribution evidence'}]})
    body['commands'] = commands
    native_events = []
    for command in commands[:-1]:
        key = command['method_key']
        params = {k: v['value']['value'] for k, v in command['event']['inputs'].items() if k != 'approved'}
        if key.startswith('interest_accrue.'):
            n = int(key.rsplit('.', 1)[1]) - 1
            params = {'rate': policy['annual_rate'], 'years': ['18/73', '91/365', '184/365'][n]}
            key = 'interest_accrue'
        native_events.append(native.event(native_spec, command['event']['id'], key, params,
            period='2027', date_=command['event']['date'],
            depends=[native_events[-1]['id']] if native_events else ()))
    return body, native_spec, native_events, mapping


def compare():
    assert sha256(Path(native.__file__).read_bytes()).hexdigest() == op.NATIVE_SHA256
    cases = []
    for owner in ['alpha', 'beta']:
        body, spec, events, mapping = fixture(owner)
        original = deepcopy(body)
        result = program.run(body)
        checks = {'complete': result['status'] == 'complete_provisional', 'unchanged': body == original}
        baseline = native.Engine(spec)
        native_rows = []
        for i, event_ in enumerate(events):
            before = baseline.snapshot()
            outcome = baseline.apply(event_)
            after = baseline.snapshot()
            row = result.get('trace', [])[i] if i < len(result.get('trace', [])) else {}
            transition = row.get('result', {}).get('transition', {})
            expected = {mapping[a]: '0/1' for a in native.ACCOUNTS}
            for posting in after['journals'][-1]['postings']:
                key = mapping[posting['account']]
                expected[key] = fmt(Q(expected[key]) + Q(posting['signed_amount']))
            checks[str(i) + ':native_applied'] = outcome['status'] == 'Applied'
            checks[str(i) + ':journal'] = transition.get('journal') == expected
            checks[str(i) + ':all_balances'] = transition.get('after', {}).get('balances') == {
                mapping[a]: fmt(v) for a, v in after['balances'].items()}
            checks[str(i) + ':cash'] = sum(Q(f['amount']) for f in transition.get('flows', [])) == (
                Q(after['balances']['cash']) - Q(before['balances']['cash']))
            checks[str(i) + ':cash_category'] = all(
                f['activity'] == native.CASH_CLASS[event_['op']] for f in transition.get('flows', []))
            checks[str(i) + ':complement'] = transition.get('after', {}).get('memory', {}).get('complement') == book_complement(body)
            native_rows.append({'event': event_, 'before': before, 'result': outcome, 'after': after})
        expected = {mapping[a]: '0/1' for a in native.ACCOUNTS}
        expected.update({mapping[k]: v for k, v in {
            'cash': '208/1', 'receivables': '15/1', 'inventory': '25/1', 'payables': '-10/1',
            'payroll_payable': '-2/1', 'debt': '-80/1', 'interest_payable': '-11/5',
            'dividend_payable': '-7/1', 'capital': '-150/1', 'retained': '12/1',
            'revenue': '-50/1', 'cost_of_sales': '25/1', 'payroll': '10/1', 'interest': '31/5'}.items()})
        checks['independent_balances'] = result.get('current', {}).get('balances') == expected
        checks['independent_clock'] = result.get('current', {}).get('memory', {}).get('finance') == {
            'cursor': '2028-01-01', 'debt': '-80/1'}
        checks['interval_union'] = sum(
            (financing.core.scalar(w['end_exclusive'], 'date') - financing.core.scalar(w['start'], 'date')).days
            for w in INTERVALS) == 365
        report = result.get('trace', [{}])[-1].get('result', {})
        checks['assets'] = report.get('balance_sheet', {}).get('total_assets') == '248/1'
        checks['liabilities'] = report.get('balance_sheet', {}).get('total_liabilities') == '506/5'
        checks['profit'] = report.get('income', {}).get('profit') == '44/5'
        checks['equity'] = report.get('equity', {}).get('closing') == '734/5'
        cash = report.get('cash_flows', {}).get('activities', {})
        checks['operating_cash'] = cash.get('operating', {}).get('net') == '3/1'
        checks['financing_cash'] = cash.get('financing', {}).get('net') == '105/1'
        if checks['complete']:
            author, imports = text.from_program(body)
            source = text.render(author)
            checks['text_program'] = text.compile_text(source, imports)['program'] == body
            checks['text_result'] = text.execute_text(source, imports) == result
            checks['replay'] = program.verify(body, result)
        else:
            source = ''
        cases.append({'case': owner, 'program': body, 'result': result, 'native': native_rows,
                      'source': source, 'checks': checks})
    return {'cases': cases, 'checks': [{'name': row['case'] + ':' + k, 'passed': bool(v)}
                                     for row in cases for k, v in row['checks'].items()]}


def book_complement(body):
    return body['opening']['memory']['complement']


if __name__ == '__main__':
    import json
    x = compare()
    bad = [r['name'] for r in x['checks'] if not r['passed']]
    print(json.dumps({'cases': len(x['cases']), 'checks': len(x['checks']), 'failures': bad[:20]}))
    raise SystemExit(bool(bad))
