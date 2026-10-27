from copy import deepcopy
from pathlib import Path
from functools import lru_cache
import importlib.util
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
import annual_scenario_family_v1 as m

spec = importlib.util.spec_from_file_location(
    'annual_family_authoring_examples',
    ROOT / 'data/accounting-master/annual-program-authoring-20261025/examples.py')
previous = importlib.util.module_from_spec(spec)
spec.loader.exec_module(previous)


@lru_cache(maxsize=1)
def fixture():
    cases = {r['case']: r for r in previous.fixtures()}
    first = cases['repeated_periods']['request']
    period = {'start': '2027-01-01', 'end_exclusive': '2028-01-01'}
    periods = [period] + [deepcopy(op['event']['next_period']) for op in first['operations']
                          if op['kind'] == 'provisional_carry']
    members = []
    for key in ['repeated_periods', 'unknown_rate', 'false_authority',
                'unknown_capacity', 'stale_measurement', 'false_carry_findings_preserved']:
        members.append({'id': key, 'assumptions': [
            {'id': 'scenario', 'statement': 'Hypothetical ' + key,
             'provenance': 'Frozen annual authoring reference fixture; no issuer claim'}],
            'operations': deepcopy(cases[key]['request']['operations'])})
    # A failure before the carry does not erase the intended later horizon.
    shortage = deepcopy(cases['cash_shortage']['request']['operations'])
    shortage.extend(deepcopy(first['operations'][2:]))
    members.append({'id': 'cash_shortage', 'assumptions': [
        {'id': 'shortage', 'statement': 'Explicit payment exceeds available cash',
         'provenance': 'Frozen annual authoring cash-shortage control'}],
        'operations': shortage})
    same = deepcopy(members[0]); same['id'] = '同額別案'
    same['assumptions'] = [{'id': 'distinct-premise', 'statement': 'A separately named identical path',
                            'provenance': 'Authored distinction; no implied frequency'}]
    members.append(same)
    return m.request(first['root_request'], periods, members, len(members))


def variant(budget=None, empty=False):
    result = deepcopy(fixture())
    if budget is not None:
        result['budget']['max_members'] = budget
    if empty:
        result['members'] = []
    return result
