from copy import deepcopy
from pathlib import Path
import importlib.util
import sys

ROOT = Path(__file__).resolve().parents[3]; sys.path.insert(0, str(ROOT / 'scripts'))
import declared_working_capital_v1 as schedules
spec = importlib.util.spec_from_file_location('schedule_operating_examples', ROOT / 'data/accounting-master/declared-operating-cycle-20261025/examples.py')
operating = importlib.util.module_from_spec(spec); spec.loader.exec_module(operating)
program = schedules.program


def fixture(owner='alpha', variant='normal'):
    body, _, _, mapping = operating.fixture(owner)
    selected = 'interim'
    if variant == 'stopped':
        event = deepcopy(body['commands'][2]);event['event'].update(id='late.unknown', date='2027-07-01')
        event['event']['inputs']['approved']['value'] = {'status': 'unknown', 'reason': 'No later finding'}
        body['commands'].append(event)
    elif variant in ['carry', 'second_period']:
        close = {'kind': 'carry', 'id': 'close.2027', 'cutoff': '2027-12-31', 'equity_movements': [], 'notes': [],
                 'retained_account': mapping['retained'], 'next_end_exclusive': '2029-01-01',
                 'memory_policies': {key: {'kind': 'preserve', 'provenance': 'Explicit carried synthetic premise'} for key in body['opening']['memory_types']}}
        body['commands'].append(close);selected = 'close.2027'
        if variant == 'second_period':
            collection = deepcopy(body['commands'][2]);collection['event'].update(id='collect.2028', date='2028-01-05')
            collection['event']['inputs']['amount']['value']['value'] = '15/1'
            payment = deepcopy(body['commands'][3]);payment['event'].update(id='pay.2028', date='2028-01-06')
            payment['event']['inputs']['amount']['value']['value'] = '10/1'
            body['commands'] += [collection, payment, {'kind': 'report', 'id': 'interim.2028', 'cutoff': '2028-06-30', 'equity_movements': [], 'notes': []}]
            selected = 'interim.2028'
    result = program.run(body)
    return schedules.request(body, result, selected, {k: mapping[k] for k in operating.operations.CLASSES}, '/stock/unit_cost')


def compare():
    rows = []
    for owner, variant in [('alpha', 'normal'), ('beta', 'normal'), ('alpha', 'stopped'), ('alpha', 'carry'), ('alpha', 'second_period')]:
        body = fixture(owner, variant); original = deepcopy(body); result = schedules.report(body)
        second = variant == 'second_period'
        controls = {'receivables': ('15/1', '0/1', '15/1', '0/1') if second else ('0/1', '50/1', '35/1', '15/1'),
                    'inventory': ('25/1', '0/1', '0/1', '25/1') if second else ('20/1', '30/1', '25/1', '25/1'),
                    'payables': ('10/1', '0/1', '10/1', '0/1') if second else ('0/1', '30/1', '20/1', '10/1'),
                    'payroll_payable': ('2/1', '0/1', '0/1', '2/1') if second else ('0/1', '10/1', '8/1', '2/1')}
        checks = {'reported': result['status'] == 'reported', 'input_unchanged': body == original,
                  'canonical_replay': schedules.verify(body, result), 'flags': all(result[k] is False for k in schedules.FLAGS)}
        for key, control in controls.items():
            row = result.get('schedules', {}).get(key, {})
            for field, value in zip(['opening', 'increases', 'decreases', 'closing'], control):checks[key + ':' + field] = row.get(field) == value
            checks[key + ':reconcile'] = row.get('reconciliation') == '0/1'
        checks['event_count'] = result.get('supported_events') == (2 if second else 6)
        checks['bridge'] = result.get('cash_diagnostic', {}).get('working_capital_contribution') == ('5/1' if second else '-8/1')
        checks['bridge_residual'] = result.get('cash_diagnostic', {}).get('unexplained_by_four_account_bridge') == '0/1'
        checks['missing_disclosures'] = len(result.get('unresolved', [])) == 6
        rows.append({'case': owner + '.' + variant, 'request': body, 'result': result, 'independent_controls': controls, 'checks': checks})
    return {'cases': rows, 'checks': [{'name': row['case'] + ':' + k, 'passed': bool(v)} for row in rows for k, v in row['checks'].items()]}


if __name__ == '__main__':
    import json
    result = compare(); failures = [c['name'] for c in result['checks'] if not c['passed']]
    print(json.dumps({'cases': len(result['cases']), 'checks': len(result['checks']), 'failures': failures}))
    raise SystemExit(bool(failures))
