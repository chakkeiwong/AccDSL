"""Explicit synthetic fixtures for typed-map book transitions."""
from copy import deepcopy
from pathlib import Path
import importlib.util
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
import company_book_transition_v2 as engine


def load(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


old = load('typed_book_old_examples', 'data/accounting-master/company-book-transition-20261025/examples.py')
operating = load('typed_book_operating_examples', 'data/accounting-master/declared-operating-cycle-20261025/examples.py')
core = engine.core


def scalar(typ): return {'node': 'scalar', 'type': deepcopy(typ)}
def record(fields): return {'node': 'record', 'fields': fields}


def definition(book):
    def visit(value, path):
        if type(value) is dict: return record({k: visit(v, path + [k]) for k, v in value.items()})
        return scalar(book['memory_types'][engine.types.pointer(path)])
    return {'profile': engine.types.PROFILE, 'root': visit(book['memory'], [])}


def rehash(book, request):
    request['expected_state_sha256'] = core.digest(book)
    request['expected_method_sha256'] = core.digest(request['method'])


def configure(book, request, decl):
    derived = engine.types.derive(decl, book['memory'], book)
    assert derived['status'] == 'typed', derived
    book['memory_schema'] = derived['schema_sha256']; book['memory_types'] = derived['memory_types']
    request['schemas'][book['memory_schema']] = derived['schema']
    request['method']['memory']['definition']['state_schema'] = book['memory_schema']
    request.update(profile=engine.PROFILE, memory_definition=decl); rehash(book, request)


def fixed_fixture(owner='alpha'):
    book, request = old.fixture(owner)
    configure(book, request, definition(book))
    return book, request


def sale_fixture(owner='alpha', claim_id='invoice/a~1', due='2027-01-31', capacity=3):
    body, _, _, mapping = operating.fixture(owner); book = body['opening']
    request = {'method': deepcopy(body['registry']['entries']['deliver']['method']),
               'event': deepcopy(body['commands'][1]['event']), 'schemas': deepcopy(body['schemas'])}
    request['event'].update(id='sale.1', date='2027-01-02')
    request['event']['inputs']['units']['value'] = engine.base.known('2/1')
    request['event']['inputs']['consideration']['value'] = engine.base.known('30/1')
    money = engine.base.money_type(book); decl = definition(book)
    decl['root']['fields']['claims'] = {'node': 'map', 'max_items': capacity,
        'values': record({'due': scalar({'kind': 'date', 'context': {}}),
                          'remaining': scalar(money), 'sale_event': scalar({'kind': 'text', 'context': {}})})}
    book['memory']['claims'] = {}
    shape = old.record({'amount': old.scalar('rational'), 'event_id': old.scalar('text')})
    request['schemas'][core.digest(shape)] = shape
    request['method']['memory'] = {'definition': {'profile': engine.base.memory.PROFILE,
        'state_schema': book['memory_schema'], 'input_schema': core.digest(shape),
        'operations': [{'id': 'create_claim', 'op': 'insert', 'path': ['claims', claim_id],
            'value': {'kind': 'object', 'fields': {
                'due': {'kind': 'literal', 'value': due},
                'remaining': {'kind': 'read', 'source': 'inputs', 'pointer': '/amount'},
                'sale_event': {'kind': 'read', 'source': 'inputs', 'pointer': '/event_id'}}}}]},
        'input_bindings': {'amount': {'kind': 'monetary_input', 'name': 'consideration'},
                           'event_id': {'kind': 'event', 'name': 'id'}}}
    configure(book, request, decl)
    return book, request, mapping


def lifecycle_fixture(owner='alpha'):
    import declared_receivable_lifecycle_v1 as life
    body, native_spec, _, mapping = operating.fixture(owner)
    book, decl, schemas = life.prepare_opening(body['opening'], 4)
    result = {'profile': life.PROFILE, 'name': 'identified-' + owner,
        'opening': book, 'memory_definition': decl, 'schemas': schemas, 'mapping': body['mapping'],
        'roles': {k: mapping[k] for k in life.operating.CLASSES}, 'unit_cost_pointer': '/stock/unit_cost',
        'policy': {'profile': life.POLICY, 'past_due': 'strictly_after_due_date',
            'carry': 'preserve_all_memory', 'provenance': 'Explicit synthetic assessment and carry convention'},
        'commands': []}
    def event(kind, identity, day, **values):
        types = life.event_types(book, kind)
        return {'kind': 'event', 'method_key': kind, 'event': {'id': identity, 'date': day,
            'inputs': {k: {'type': deepcopy(types[k]), 'value': life.engine.known(v),
                'provenance': 'Explicit synthetic lifecycle premise'} for k, v in {'approved': True, **values}.items()}}}
    report = lambda identity, cutoff: {'kind': 'report', 'id': identity, 'cutoff': cutoff, 'equity_movements': [], 'notes': []}
    result['commands'] = [
        event('sale', 'sale.1', '2027-01-02', units='2/1', consideration='30/1', claim_id='invoice/a~1', customer='Customer A', due='2027-01-31'),
        event('collect', 'receipt.1', '2027-01-15', amount='10/1', claim_id='invoice/a~1', customer='Customer A'),
        event('assess', 'assess.jan', '2027-01-31', start='2027-01-01', end_exclusive='2027-02-01'),
        report('jan', '2027-01-31'),
        event('assess', 'assess.feb', '2027-02-28', start='2027-02-01', end_exclusive='2027-03-01'),
        event('assess', 'assess.year', '2027-12-31', start='2027-03-01', end_exclusive='2028-01-01'),
        report('annual', '2027-12-31'),
        {**report('boundary', '2027-12-31'), 'kind': 'carry', 'retained_account': mapping['retained'], 'next_end_exclusive': '2029-01-01'},
        event('collect', 'receipt.2', '2028-01-10', amount='20/1', claim_id='invoice/a~1', customer='Customer A'),
        event('assess', 'assess.next', '2028-01-31', start='2028-01-01', end_exclusive='2028-02-01'),
        report('next', '2028-01-31')]
    return result, mapping, native_spec


def compare():
    import declared_receivable_lifecycle_v1 as life
    import declared_receivable_text_v1 as text
    from fractions import Fraction as Q
    checks, cases = [], []
    def check(name, value):
        checks.append({'name': name, 'passed': bool(value)})
        if not value: raise AssertionError(name)
    for owner in ['alpha', 'beta']:
        body, mapping, native_spec = lifecycle_fixture(owner); before = deepcopy(body)
        result = life.run(body); prefix = owner + ':'
        check(prefix + 'complete', result['status'] == 'complete_provisional')
        check(prefix + 'inputs_unchanged', body == before)
        native = operating.native.Engine(native_spec)
        for i, (kind, values, date_) in enumerate([
                ('deliver', {'units': '2/1', 'consideration': '30/1'}, '2027-01-02'),
                ('collect', {'amount': '10/1'}, '2027-01-15')]):
            event = operating.native.event(native_spec, ['sale.1', 'receipt.1'][i], kind, values, period='2027', date_=date_)
            outcome = native.apply(event); snapshot = native.snapshot()
            row = result['trace'][i]['result']
            expected = {mapping[a]: '0/1' for a in operating.native.ACCOUNTS}
            for line in snapshot['journals'][-1]['postings']:
                key = mapping[line['account']]; expected[key] = operating.fmt(Q(expected[key]) + Q(line['signed_amount']))
            check(prefix + kind + ':native_applied', outcome['status'] == 'Applied')
            check(prefix + kind + ':full_journal', row['journal'] == expected)
            check(prefix + kind + ':all_balances', row['after']['balances'] == {mapping[k]: operating.fmt(v) for k, v in snapshot['balances'].items()})
        annual = next(r['result'] for r in result['reports'] if r['id'] == 'annual')
        annual_book = result['trace'][6]['request']['closing']
        expected = {mapping[a]: '0/1' for a in operating.native.ACCOUNTS}
        expected.update({mapping[k]: v for k, v in {'cash': '110/1', 'receivables': '20/1', 'inventory': '10/1',
                        'capital': '-120/1', 'revenue': '-30/1', 'cost_of_sales': '10/1'}.items()})
        check(prefix + 'annual_all_balances', annual_book['balances'] == expected)
        for name, actual, expected_value in [('assets', annual['balance_sheet']['total_assets'], '140/1'),
                ('profit', annual['income']['profit'], '20/1'), ('operating_cash', annual['cash_flows']['activities']['operating']['net'], '10/1')]:
            check(prefix + 'annual_' + name, actual == expected_value)
        for index, overdue in [(2, '0/1'), (4, '20/1'), (5, '20/1'), (9, '0/1')]:
            row = result['trace'][index]
            check(prefix + 'assessment:' + str(index) + ':overdue', row['observation']['claims'][0]['overdue'] == overdue)
            check(prefix + 'assessment:' + str(index) + ':no_journal', set(row['result']['journal'].values()) == {'0/1'})
            check(prefix + 'assessment:' + str(index) + ':no_flow', row['result']['flows'] == [])
        boundary = result['trace'][7]['result']
        check(prefix + 'carry_exact_memory', boundary['closed_book']['memory'] == boundary['next_opening']['memory'])
        check(prefix + 'carry_profit', boundary['next_opening']['balances'][mapping['retained']] == '-20/1')
        check(prefix + 'next_cash', result['current']['balances'][mapping['cash']] == '130/1')
        check(prefix + 'next_receivable', result['current']['balances'][mapping['receivables']] == '0/1')
        check(prefix + 'next_operating_cash', result['reports'][-1]['result']['cash_flows']['activities']['operating']['net'] == '20/1')
        source, imports = text.from_program(body)
        check(prefix + 'text_program', text.compile_text(source, imports)['program'] == body)
        check(prefix + 'text_execution', text.execute_text(source, imports) == result)
        check(prefix + 'replay', life.verify(body, result))
        check(prefix + 'admission_false', all(result[k] is False for k in life.FLAGS))
        cases.append({'case': owner, 'request': body, 'result': result, 'source': source, 'imports': imports})
    return {'cases': cases, 'checks': checks}
