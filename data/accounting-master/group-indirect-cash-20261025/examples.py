"""Matched legal traces for retained snapshots; explicit identity translation."""
from copy import deepcopy
from pathlib import Path
import importlib.util
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
import group_indirect_cash_v1 as bridge
import declared_operating_methods_v1 as helper

program = bridge.indirect.program
core = program.core
spec = importlib.util.spec_from_file_location('group_period_baseline', ROOT /
    'data/accounting-master/group-period-report-20261025/examples.py')
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)
VARIANTS = {
    'cross': ('investing', 'financing'),
    'operating': ('operating', 'operating'),
    'payer_operating': ('operating', 'financing'),
    'payee_operating': ('investing', 'operating'),
}
_cache = {}


def entry(book, schemas, key, postings, flow):
    engine = program.engine
    money = engine.money_type(book)
    identity = 'synthetic.group.' + key
    roles = {account: account for account, _ in postings}
    roles[book['cash_account']] = book['cash_account']
    pre_types = {'approved': core.BOOL}
    pre_rows = [('applicable', helper.ref('approved'), ['approved'], 'unsupported')]
    pre_bindings = {'approved': helper.event('approved')}
    if flow['amount'].startswith('-'):
        pre_types['available_cash'] = money
        pre_bindings['available_cash'] = helper.account(book['cash_account'])
        pre_rows.append(('cash_available', helper.binary('le', helper.constant(money, '30/1'),
                         helper.ref('available_cash')), ['available_cash'], 'invalid'))
    empty = {'type': 'object', 'properties': {}, 'required': [], 'additionalProperties': False}
    empty_sha = core.digest(empty)
    shapes = {**deepcopy(schemas), empty_sha: empty}
    method = {'profile': engine.METHOD, 'id': identity, 'version': '1',
        'context': deepcopy(book['context']), 'account_map': roles,
        'preconditions': {'manifest': helper.conditions(identity, pre_types, pre_rows), 'bindings': pre_bindings},
        'postconditions': {'manifest': helper.conditions(identity, {'closing_cash': money},
            [('cash_nonnegative', helper.binary('le', helper.constant(money, '0/1'),
              helper.ref('closing_cash')), ['closing_cash'], 'invalid')]),
            'bindings': {'closing_cash': helper.account(book['cash_account'])}},
        'monetary': {'definition': {'profile': engine.monetary.PROFILE, 'method_id': identity, 'version': '1',
            'inputs': {}, 'calculations': [], 'accounts': {a: deepcopy(money) for a in roles},
            'cash_account': book['cash_account'],
            'postings': [{'id': 'posting.' + str(i), 'account': a,
                          'expression': helper.constant(money, amount), 'requires': []}
                         for i, (a, amount) in enumerate(postings)],
            'flows': [{'id': flow['id'], 'activity': flow['activity'], 'origin': flow['origin'],
                       'expression': helper.constant(money, flow['amount']), 'requires': []}]}, 'bindings': {}},
        'memory': {'definition': {'profile': engine.memory.PROFILE, 'state_schema': book['memory_schema'],
                                 'input_schema': empty_sha, 'operations': []}, 'input_bindings': {}},
        'residual_prerequisites': ['Constructed fixed amounts and supplied classifications; no accounting admission.']}
    return {'method_sha256': core.digest(method), 'method': method, 'schemas': shapes,
            'account_classes': {a: book['accounts'][a]['classification'] for a in roles},
            'event_inputs': {'approved': deepcopy(core.BOOL)}, 'metadata_bindings': {},
            'clock': {'kind': 'direct_event_date'}}


def fixture(chart='named', variant='cross'):
    cache_key = chart, variant
    if cache_key in _cache:
        return deepcopy(_cache[cache_key])
    payer_activity, payee_activity = VARIANTS[variant]
    original = prior.fixture(chart, variant != 'operating')
    original['closing']['books']['P']['flows'][0]['activity'] = payer_activity
    original['closing']['books']['S']['flows'][0]['activity'] = payee_activity
    prior.refresh(original)
    for side, owner in [('payer', 'P'), ('payee', 'S')]:
        original['internal_cash_pairs'][0][side]['expected_flow_sha256'] = core.digest(original['closing']['books'][owner]['flows'][0])
    baseline = bridge.group.report(original)
    assert baseline['status'] == 'period_reported', baseline
    source = deepcopy(original)
    legal = {}
    translations = []
    adapted_schemas = None
    for owner in ['P', 'S']:
        opening = deepcopy(source['opening']['books'][owner])
        mapping = original['closing']['account_maps'][owner]
        account = lambda role: next(k for k, v in mapping.items() if v == role)
        entries, commands, classifications = {}, [], {}
        for flow in original['closing']['books'][owner]['flows']:
            key = flow['id']
            if key == 'internal-out':
                postings = [(account('receivable'), '30/1'), (account('cash'), '-30/1')]
                categories = {account('receivable'): 'working_capital' if flow['activity'] == 'operating' else 'nonoperating'}
                profits = {}
            elif key == 'internal-in':
                postings = [(account('cash'), '30/1'), (account('payable'), '-30/1')]
                categories = {account('payable'): 'working_capital' if flow['activity'] == 'operating' else 'nonoperating'}
                profits = {}
            else:
                assert key == 'customer'
                postings = [(account('cash'), '20/1'), (account('sales'), '-20/1')]
                categories, profits = {}, {account('sales'): 'operating'}
            method = entry(opening, original['opening']['schemas'], key, postings, flow)
            entries[key] = method
            classifications[method['method_sha256']] = {'accounts': categories, 'profit_accounts': profits,
                'premise': 'Explicit constructed ' + key + ' classified ' + flow['activity']}
            commands.append({'kind': 'event', 'method_key': key, 'event': {'id': flow['event_id'], 'date': flow['date'],
                'inputs': {'approved': {'type': deepcopy(core.BOOL), 'value': {'status': 'known', 'value': True},
                    'provenance': 'Constructed event premise; no source admission'}}}})
        report_req = original['legal_reports'][owner]
        commands.append({'kind': 'report', 'id': 'annual', 'cutoff': original['closing']['books'][owner]['date'],
                         'equity_movements': deepcopy(report_req['equity_movements']), 'notes': deepcopy(report_req['notes'])})
        schemas = deepcopy(next(iter(entries.values()))['schemas'])
        if adapted_schemas is None:
            adapted_schemas = schemas
        assert schemas == adapted_schemas
        body = {'profile': program.PROFILE, 'name': 'group-' + owner, 'opening': opening, 'schemas': schemas,
                'registry': {'profile': program.methods.REGISTRY, 'context': deepcopy(opening['context']), 'entries': entries},
                'mapping': deepcopy(report_req['mapping']), 'commands': commands}
        execution = program.run(body)
        assert execution['status'] == 'complete_provisional', execution.get('reason', execution.get('stop'))
        expected = deepcopy(original['closing']['books'][owner])
        for flow in expected['flows']:
            old = flow['id']; flow['id'] = core.digest([flow['event_id'], old])
            translations.append({'owner': owner, 'old': old, 'new': flow['id']})
        assert execution['current'] == expected, (owner, 'complete state mismatch')
        policy = {'profile': bridge.indirect.POLICY, 'context': deepcopy(opening['context']), 'methods': classifications}
        req = bridge.indirect.request(body, execution, 'annual', policy)
        res = bridge.indirect.report(req)
        assert res['status'] == 'explained_provisional', res
        legal[owner] = {'request': req, 'result': res}
        source['closing']['books'][owner] = expected
        source['legal_reports'][owner] = deepcopy(execution['trace'][-1]['request'])
    for snapshot in ['opening', 'closing']:
        source[snapshot]['schemas'] = deepcopy(adapted_schemas)
    prior.base.rehash(source['opening']); prior.base.rehash(source['closing'])
    for pair in source['internal_cash_pairs']:
        for side in ['payer', 'payee']:
            ref = pair[side]
            tr = next(t for t in translations if t['owner'] == ref['owner'] and t['old'] == ref['flow_id'])
            ref['flow_id'] = tr['new']
            flow = next(f for f in source['closing']['books'][ref['owner']]['flows'] if f['id'] == ref['flow_id'])
            ref['expected_flow_sha256'] = core.digest(flow)
    # Rebuild each independently supplied snapshot request using only the
    # documented identity and schema adaptation, then compare complete results.
    for owner in ['P', 'S']:
        expected_req = bridge.group.reports.request(source['opening']['books'][owner], source['closing']['books'][owner],
            adapted_schemas, original['legal_reports'][owner]['mapping'],
            original['legal_reports'][owner]['equity_movements'], original['legal_reports'][owner]['notes'])
        assert expected_req == source['legal_reports'][owner]
        assert bridge.group.reports.report(expected_req) == legal[owner]['result']['financial_report']
    result = bridge.group.report(source)
    assert result['status'] == 'period_reported', result
    assert result['cash_flows']['activities'] == baseline['cash_flows']['activities']
    assert result['equity'] == baseline['equity']
    expected_raw = {'cross': '20/1', 'operating': '20/1', 'payer_operating': '-10/1', 'payee_operating': '50/1'}[variant]
    expected_adjustment = {'cross': '0/1', 'operating': '0/1', 'payer_operating': '30/1', 'payee_operating': '-30/1'}[variant]
    value = {'request': bridge.request(source, result, legal), 'baseline_request': original, 'baseline_result': baseline,
        'adapter': {'flow_id_translation': translations,
                    'added_schemas': {k: v for k, v in adapted_schemas.items() if k not in original['opening']['schemas']},
                    'complete_states_and_reports_equal_after_declared_adaptation': True},
        'expected': {'raw': expected_raw, 'adjustment': expected_adjustment, 'profit': '20/1', 'operating': '20/1'}}
    _cache[cache_key] = value
    return deepcopy(value)


def checked_case(chart='named', variant='payer_operating'):
    value = fixture(chart, variant)
    result = bridge.report(value['request'])
    assert result['status'] == 'group_explained_provisional', result
    expected = value['expected']
    assert result['raw_legal_operating_cash'] == expected['raw']
    assert result['items']['internal_operating_cash_adjustment'] == expected['adjustment']
    assert result['items']['profit'] == expected['profit']
    assert result['items']['indirect_operating_cash'] == result['direct_group_operating_cash'] == expected['operating']
    assert all(result[k] is False for k in bridge.FLAGS)
    value['result'] = result
    return value


if __name__ == '__main__':
    import json
    for variant in ['payer_operating', 'payee_operating']:
        case = checked_case('named', variant)
        print(json.dumps({'variant': variant, 'expected': case['expected'], 'status': case['result']['status']}), flush=True)
