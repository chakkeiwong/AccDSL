"""Explicit classifications and independent arithmetic for constructed cases."""
from copy import deepcopy
from pathlib import Path
import importlib.util
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
import declared_indirect_cash_v1 as bridge

spec = importlib.util.spec_from_file_location('indirect_financing_examples', ROOT /
    'data/accounting-master/declared-financing-clock-20261025/examples.py')
fin = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fin)


def policy(body, result, report_id, mapping, interest='operating', overrides=None):
    start, selected, _, _ = bridge.period(result, report_id)
    book = body['opening']
    reverse = {v: k for k, v in mapping.items()}
    methods = {}
    for row in result['trace'][start:selected + 1]:
        if row['command']['kind'] != 'event':
            continue
        key = row['result']['method_key']
        entry = row['request']['registry']['entries'][key]
        accounts = {entry['method']['account_map'][p['account']]
                    for p in row['result']['transition']['monetary']['diagnostics']['postings']}
        classified = {}
        for account in accounts:
            kind = book['accounts'][account]['classification']
            if account == book['cash_account'] or kind in ['income', 'expense']:
                continue
            role = reverse[account]
            if kind == 'equity':
                category = 'owner'
            elif role in ['receivables', 'inventory', 'payables', 'payroll_payable']:
                category = 'working_capital'
            elif role == 'interest_payable':
                category = ('working_capital' if interest == 'operating' else
                            'noncash_profit' if key.startswith('interest_accrue.') else 'nonoperating')
            elif role in ['debt', 'dividend_payable', 'plant_cost']:
                category = 'nonoperating'
            else:
                raise AssertionError('No constructed classification: ' + role)
            classified[account] = (overrides or {}).get((key, role), category)
        methods[entry['method_sha256']] = {'accounts': classified,
            'premise': 'Explicit constructed movement interpretation; interest cash classified ' + interest}
    return {'profile': bridge.POLICY, 'context': deepcopy(book['context']), 'methods': methods}


def fixture(chart='alpha', variant='combined'):
    activity = 'financing' if variant == 'financing_interest' else 'operating'
    body, _, _, mapping = fin.fixture(chart, activity)
    report_id = 'annual'
    expected = {'profit': '44/5', 'working_capital': '-29/5', 'noncash_profit': '0/1',
                'indirect_operating_cash': '3/1'}
    overrides = {}
    if variant == 'financing_interest':
        expected.update(working_capital='-8/1', noncash_profit='31/5', indirect_operating_cash='7/1')
    elif variant == 'stopped':
        command = deepcopy(body['commands'][-1])
        command.update(id='bad.report', cutoff='2027-01-01')
        body['commands'].append(command)
    elif variant in ['carry', 'second_period']:
        close = deepcopy(body['commands'][-1])
        close.update(kind='carry', id='close', retained_account=mapping['retained'],
                     next_end_exclusive='2029-01-01', memory_policies={p: {
                         'kind': 'next_period_start' if p == '/finance/cursor' else 'preserve',
                         'provenance': 'Explicit constructed carried state'} for p in body['opening']['memory_types']})
        body['commands'].append(close)
        report_id = 'close'
        if variant == 'second_period':
            command = fin.event(body, 'collect', 'collect.next', '2028-01-05', {'amount': '15/1'})
            body['commands'] += [command, {'kind': 'report', 'id': 'next', 'cutoff': '2028-01-31',
                                          'equity_movements': [], 'notes': []}]
            report_id = 'next'
            expected = {'profit': '0/1', 'working_capital': '15/1', 'noncash_profit': '0/1',
                        'indirect_operating_cash': '15/1'}
    elif variant in ['noncash_asset', 'disposal_gain', 'depreciation', 'zero_net']:
        entry = deepcopy(body['registry']['entries']['debt_issue'])
        method = entry['method']
        identity = 'synthetic.indirect.' + variant
        method['id'] = identity
        for part in ['preconditions', 'postconditions']:
            method[part]['manifest']['method_id'] = identity
        monetary = method['monetary']['definition']
        monetary['method_id'] = identity
        money = bridge.program.engine.money_type(body['opening'])
        helper = fin.financing
        if variant == 'noncash_asset':
            postings = [('plant_cost', '25/1'), ('debt', '-25/1')]
            flows = []
            amount = '25/1'
            expected = dict.fromkeys(expected, '0/1')
        elif variant == 'disposal_gain':
            postings = [('cash', '12/1'), ('plant_cost', '-10/1'), ('revenue', '-2/1')]
            flows = [{'id': 'disposal', 'activity': 'investing', 'origin': 'constructed_disposal',
                      'expression': helper.constant(money, '12/1'), 'requires': []}]
            amount = '0/1'
            expected = {'profit': '2/1', 'working_capital': '0/1', 'noncash_profit': '-2/1',
                        'indirect_operating_cash': '0/1'}
            # A single asset movement includes both cost removed and proceeds/gain.
            # This profile cannot split that account's movement into two categories.
            # Use separate recorded gain-reversal cash classification test below instead.
        elif variant == 'depreciation':
            postings = [('depreciation', '5/1'), ('plant_cost', '-5/1')]
            flows = []
            amount = '0/1'
            overrides[(variant, 'plant_cost')] = 'noncash_profit'
            expected = {'profit': '-5/1', 'working_capital': '0/1', 'noncash_profit': '5/1',
                        'indirect_operating_cash': '0/1'}
        else:
            postings = [('plant_cost', '5/1'), ('plant_cost', '-5/1')]
            flows = []
            amount = '0/1'
            expected = dict.fromkeys(expected, '0/1')
        if variant in ['disposal_gain', 'depreciation']:
            body['opening']['balances'][mapping['plant_cost']] = '20/1'
            body['opening']['balances'][mapping['capital']] = '-140/1'
        for role, _ in postings:
            method['account_map'][role] = mapping[role]
            monetary['accounts'][role] = deepcopy(money)
            entry['account_classes'][role] = body['opening']['accounts'][mapping[role]]['classification']
        monetary['postings'] = [{'id': 'posting.' + str(i), 'account': role,
                                'expression': helper.constant(money, value), 'requires': []}
                               for i, (role, value) in enumerate(postings)]
        monetary['flows'] = flows
        entry['method_sha256'] = bridge.core.digest(method)
        body['registry']['entries'][variant] = entry
        body['commands'] = [fin.event(body, variant, variant + '.1', '2027-01-01', {'amount': amount}),
                            {'kind': 'report', 'id': 'annual', 'cutoff': '2027-01-01',
                             'equity_movements': [], 'notes': []}]
    result = bridge.program.run(body)
    assert result['status'] in ['complete_provisional', 'stopped_provisional'], result.get('reason')
    assert result['reports'], result.get('stop')
    configured = policy(body, result, report_id, mapping, activity, overrides)
    return bridge.request(body, result, report_id, configured), expected


def cases():
    output = {}
    for chart in ['alpha', 'beta']:
        for variant in ['combined', 'financing_interest', 'stopped', 'carry', 'second_period',
                        'noncash_asset', 'depreciation', 'zero_net']:
            request_, expected = fixture(chart, variant)
            result = bridge.report(request_)
            assert result['status'] == 'explained_provisional', (chart, variant, result)
            assert result['items'] == expected, (chart, variant, result['items'], expected)
            output[chart + '.' + variant] = {'request': request_, 'result': result, 'expected': expected}
    return output
