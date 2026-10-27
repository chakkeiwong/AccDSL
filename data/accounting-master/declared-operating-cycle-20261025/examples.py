"""Synthetic full operating cycle and separate native monetary comparator."""
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]; sys.path.insert(0, str(ROOT / 'scripts'))
import declared_operating_methods_v1 as operations
import declared_company_program_v1 as program
import declared_company_text_v1 as text
import company_execution_v1 as native

NATIVE_SHA256 = '5d2cc7d17b78bb8daf20c6db8895f37e4b6d0c80f641e6ef21bbf5db6eeae3d0'


def fmt(value):
    q = Q(value); return str(q.numerator) + '/' + str(q.denominator)


def record(fields):return {'type': 'object', 'properties': fields, 'required': list(fields), 'additionalProperties': False}
def scalar(kind):return {'type': 'string', 'minLength': 1, 'maxLength': 4096, 'x-exact-kind': kind}


def fixture(owner='alpha'):
    mapping = {key: key if owner == 'alpha' else 'A' + str(500 - i * 7) for i, key in enumerate(native.ACCOUNTS)}
    context = {'entity': 'Operating-' + owner, 'book': 'legal-' + owner, 'currency': 'USD',
               'case_id': 'synthetic-cycle-' + owner, 'mode': 'synthetic'}
    balances = {key: '0/1' for key in native.ACCOUNTS}; balances.update(cash='100/1', inventory='20/1', capital='-120/1')
    classes = {**{a: 'asset' for a in native.ASSETS}, **{a: 'liability' for a in native.LIABILITIES},
               'capital': 'equity', 'retained': 'equity', **{a: 'income' if a == 'revenue' else 'expense' for a in native.TEMP}}
    book = {'profile': program.engine.BOOK, 'context': context, 'period': {'start': '2027-01-01', 'end_exclusive': '2028-01-01'},
            'date': '2027-01-01', 'accounts': {mapping[a]: {'classification': classes[a]} for a in native.ACCOUNTS},
            'balances': {mapping[a]: v for a, v in balances.items()}, 'cash_account': mapping['cash'], 'seen': [], 'flows': []}
    money = program.engine.money_type(book)
    price = {**deepcopy(money), 'dimensions': {'currency:USD': 1, 'goods:unit': -1}}
    schema = record({'stock': record({'unit_cost': scalar('rational')}), 'complement': record({'tag': scalar('text')})})
    book.update(memory={'stock': {'unit_cost': '5/1'}, 'complement': {'tag': 'preserve-me'}}, memory_schema=program.digest(schema),
                memory_types={'/stock/unit_cost': price, '/complement/tag': {'kind': 'text', 'context': {}}})
    schemas = {program.digest(schema): schema}; roles = {k: mapping[k] for k in operations.CLASSES}
    registry = operations.build(book, schemas, roles, '/stock/unit_cost')
    for entry in registry['entries'].values():schemas.update(deepcopy(entry['schemas']))
    native_spec = {'context': {'entity': context['entity'], 'basis': 'DemoCorporate/1', 'currency': 'USD',
                              'unit': 'one currency unit', 'calendar': 'gregorian'},
                   'opening': balances, 'assets': [], 'inventory_unit_cost': '5/1',
                   'periods': [{'id': '2027', 'start': '2027-01-01', 'date': '2027-12-31'}],
                   'source': 'Explicit synthetic operating-cycle premises; no historical disclosure admission'}
    commands = []; native_events = []
    rows = [('purchase', {'units': '6/1'}), ('deliver', {'units': '5/1', 'consideration': '50/1'}),
            ('collect', {'amount': '35/1'}), ('supplier_pay', {'amount': '20/1'}),
            ('payroll_accrue', {'amount': '10/1'}), ('payroll_pay', {'amount': '8/1'})]
    for i, (kind, params) in enumerate(rows):
        ident = 'op.' + str(i + 1); day = '2027-01-' + str(i + 2).zfill(2)
        types = registry['entries'][kind]['event_inputs']
        inputs = {k: {'type': deepcopy(types[k]), 'value': program.engine.known(v), 'provenance': 'Authored synthetic operating premise'}
                  for k, v in {**params, 'approved': True}.items()}
        commands.append({'kind': 'event', 'method_key': kind, 'event': {'id': ident, 'date': day, 'inputs': inputs}})
        native_events.append(native.event(native_spec, ident, kind, params, period='2027', date_=day,
                                          depends=[native_events[-1]['id']] if native_events else ()))
    commands.append({'kind': 'report', 'id': 'interim', 'cutoff': '2027-06-30', 'equity_movements': [],
                     'notes': [{'id': 'working_capital', 'label': 'Maturity and valuation schedules', 'status': 'missing',
                                'reason': 'The cycle supplies movements but no invoice ageing or valuation evidence'}]})
    report_map = {'profile': program.reports.MAP, 'context': deepcopy(context),
                  'lines': [{'id': a, 'label': a, 'classification': classes[a], 'accounts': [mapping[a]]} for a in native.ACCOUNTS]}
    body = {'profile': program.PROFILE, 'name': 'operating-' + owner, 'opening': book, 'schemas': schemas,
            'registry': registry, 'mapping': report_map, 'commands': commands}
    return body, native_spec, native_events, mapping


def compare():
    assert sha256(Path(native.__file__).read_bytes()).hexdigest() == NATIVE_SHA256
    cases = []
    for owner in ['alpha', 'beta']:
        body, spec, events, mapping = fixture(owner); original = deepcopy(body)
        result = program.run(body); baseline = native.Engine(spec)
        checks = {'complete': result['status'] == 'complete_provisional', 'input_unchanged': body == original}
        native_rows = []
        for i, event in enumerate(events):
            before = baseline.snapshot(); outcome = baseline.apply(event); after = baseline.snapshot()
            expected_journal = {mapping[a]: '0/1' for a in native.ACCOUNTS}
            for line in after['journals'][-1]['postings']:
                key = mapping[line['account']]; expected_journal[key] = fmt(Q(expected_journal[key]) + Q(line['signed_amount']))
            row = result.get('trace', [])[i] if i < len(result.get('trace', [])) else {}
            generic = row.get('result', {}).get('transition', {})
            checks[str(i) + ':native_applied'] = outcome['status'] == 'Applied'
            checks[str(i) + ':journal'] = generic.get('journal') == expected_journal
            checks[str(i) + ':all_balances'] = generic.get('after', {}).get('balances') == {mapping[k]: fmt(v) for k, v in after['balances'].items()}
            checks[str(i) + ':memory_unchanged'] = generic.get('after', {}).get('memory') == body['opening']['memory']
            checks[str(i) + ':native_assets_unchanged'] = before['assets'] == after['assets'] == []
            flows = generic.get('flows', []); delta = Q(after['balances']['cash']) - Q(before['balances']['cash'])
            checks[str(i) + ':cash'] = sum(Q(f['amount']) for f in flows) == delta
            checks[str(i) + ':cash_origin'] = all(f['activity'] == 'operating' and f['origin'] == event['op'] for f in flows)
            native_rows.append({'event': event, 'before': before, 'outcome': outcome, 'after': after})
        closing = result.get('current', {}).get('balances', {})
        independent = {mapping[a]: '0/1' for a in native.ACCOUNTS}
        independent.update({mapping[a]: v for a, v in {'cash': '107/1', 'receivables': '15/1', 'inventory': '25/1',
            'payables': '-10/1', 'payroll_payable': '-2/1', 'capital': '-120/1', 'revenue': '-50/1', 'cost_of_sales': '25/1', 'payroll': '10/1'}.items()})
        checks['independent_all_balances'] = closing == independent
        report = result['trace'][-1]['result'] if result.get('trace') else {}
        checks['independent_assets'] = report.get('balance_sheet', {}).get('total_assets') == '147/1'
        checks['independent_liabilities'] = report.get('balance_sheet', {}).get('total_liabilities') == '12/1'
        checks['independent_equity'] = report.get('equity', {}).get('closing') == '135/1'
        checks['independent_profit'] = report.get('income', {}).get('profit') == '15/1'
        checks['independent_ocf'] = report.get('cash_flows', {}).get('activities', {}).get('operating', {}).get('net') == '7/1'
        checks['independent_cash_bridge'] = Q(15) - Q(15) - Q(5) + Q(10) + Q(2) == Q(7)
        author, imports = text.from_program(body); source = text.render(author)
        checks['text_program'] = text.compile_text(source, imports)['program'] == body
        checks['text_result'] = text.execute_text(source, imports) == result
        checks['replay'] = program.verify(body, result)
        checks['flags'] = all(result[k] is False for k in program.FLAGS)
        cases.append({'case': owner, 'program': body, 'result': result, 'native': native_rows, 'source': source, 'checks': checks})
    return {'cases': cases, 'checks': [{'name': row['case'] + ':' + key, 'passed': bool(v)} for row in cases for key, v in row['checks'].items()]}


if __name__ == '__main__':
    import json
    result = compare(); bad = [x['name'] for x in result['checks'] if not x['passed']]
    print(json.dumps({'cases': len(result['cases']), 'checks': len(result['checks']), 'failures': bad}))
    raise SystemExit(bool(bad))
