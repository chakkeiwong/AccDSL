"""Explicit profit exclusions, compared with protected v1 and exact arithmetic."""
from copy import deepcopy
from pathlib import Path
import importlib.util
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
import declared_indirect_cash_v2 as bridge

spec = importlib.util.spec_from_file_location('indirect_v1_examples', ROOT /
    'data/accounting-master/declared-indirect-cash-20261025/examples.py')
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)
_fixtures = {}


def fixture(chart='alpha', variant='combined'):
    key = (chart, variant)
    if key in _fixtures:
        return deepcopy(_fixtures[key])
    original_variant = 'disposal_gain' if variant == 'disposal_loss' else variant
    old, old_expected = prior.fixture(chart, original_variant)
    body, execution = old['program'], old['result']
    mapping = prior.fin.fixture(chart)[3]
    if variant == 'disposal_loss':
        entry = body['registry']['entries']['disposal_gain']
        monetary = entry['method']['monetary']['definition']
        money = bridge.program.engine.money_type(body['opening'])
        monetary['postings'][0]['expression'] = prior.fin.financing.constant(money, '8/1')
        monetary['postings'][2]['expression'] = prior.fin.financing.constant(money, '2/1')
        monetary['flows'][0]['expression'] = prior.fin.financing.constant(money, '8/1')
        entry['method_sha256'] = bridge.core.digest(entry['method'])
        execution = bridge.program.run(body)
        assert execution['status'] == 'complete_provisional', execution
        old['result'] = execution
        old['program_sha256'] = bridge.core.digest(body)
        old['result_sha256'] = bridge.core.digest(execution)
        old['policy'] = prior.policy(body, execution, old['report_id'], mapping)
        old_expected = {'profit': '-2/1', 'working_capital': '0/1', 'noncash_profit': '0/1',
                        'indirect_operating_cash': '0/1'}
    request = deepcopy(old)
    request['profile'] = bridge.PROFILE
    policy = request['policy']
    policy['profile'] = bridge.POLICY
    start, selected, _, _ = bridge.period(execution, old['report_id'])
    for row in execution['trace'][start:selected + 1]:
        if row['command']['kind'] != 'event':
            continue
        entry = row['request']['registry']['entries'][row['result']['method_key']]
        m = policy['methods'][entry['method_sha256']]
        gross = row['result']['transition']['monetary']['diagnostics']['postings']
        accounts = {entry['method']['account_map'][p['account']] for p in gross}
        m['profit_accounts'] = {a: 'operating' for a in accounts
            if body['opening']['accounts'][a]['classification'] in ['income', 'expense']}
        if variant in ['disposal_gain', 'disposal_loss']:
            m['profit_accounts'][mapping['revenue']] = 'nonoperating'
            m['premise'] = 'Constructed sale of plant: explicitly exclude its gain or loss from operating cash'
        if variant == 'financing_interest':
            if mapping['interest_payable'] in m['accounts']:
                m['accounts'][mapping['interest_payable']] = 'nonoperating'
            if mapping['interest'] in m['profit_accounts']:
                m['profit_accounts'][mapping['interest']] = 'nonoperating'
    expected = {**old_expected, 'nonoperating_profit_adjustment': '0/1'}
    if variant == 'disposal_gain':
        expected.update(noncash_profit='0/1', nonoperating_profit_adjustment='-2/1')
    elif variant == 'disposal_loss':
        expected['nonoperating_profit_adjustment'] = '2/1'
    elif variant == 'financing_interest':
        expected.update(noncash_profit='0/1', nonoperating_profit_adjustment='31/5')
    _fixtures[key] = (request, expected)
    return deepcopy(_fixtures[key])


VARIANTS = ('combined', 'financing_interest', 'stopped', 'carry', 'second_period',
            'noncash_asset', 'depreciation', 'zero_net', 'disposal_gain', 'disposal_loss')


def checked_case(chart, variant):
    request, expected = fixture(chart, variant)
    result = bridge.report(request)
    assert result['status'] == 'explained_provisional', (chart, variant, result)
    assert result['items'] == expected, (chart, variant, result['items'], expected)
    assert result['direct_operating_cash'] == expected['indirect_operating_cash']
    assert all(result[k] is False for k in bridge.FLAGS)
    return {'request': request, 'result': result, 'expected': expected}
