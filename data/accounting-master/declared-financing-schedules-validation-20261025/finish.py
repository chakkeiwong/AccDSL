from hashlib import sha256
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PLAN = 'docs/plans/accounting-declared-financing-schedules-integration-20261025.md'
REL = HERE.relative_to(ROOT).as_posix()


def sha(path):
    return sha256(path.read_bytes()).hexdigest()


def main():
    checks = json.loads((HERE / 'checks.json').read_text())
    comparison = json.loads((HERE / 'comparison.json').read_text())
    assert checks['passed'] and checks['focused_tests'] == 15
    assert checks['comparison_checks'] == 123
    assert all(row['passed'] for row in comparison['checks'])
    names = ['docs/plans/accounting-master-current.md',
             'docs/plans/accounting-master-checkpoint.md',
             'docs/plans/accounting-master-program.md',
             'docs/plans/accounting-mission-requirements.md',
             'docs/plans/accounting-product-design-checkpoint.md',
             'data/accounting-master/next-plan.md',
             'data/accounting-master/simulator-session-20261023.md',
             'data/accounting-master/next-plan.json',
             'scripts/accounting_master_catalog.json']
    before = {}
    note = (f'''## Financing schedule evidence repaired — 25 October 2026

The predecessor's 220-comparison claim was rejected. The corrected successor
records 15 focused tests and123 named comparison checks across two charts plus
working-capital v1/v2 equality. Missing accrual and next-period cases are explicit.
Result: {REL}/result.md. Next: {PLAN}.
Version4.14 remains511 pages,not_ready;Version4.15 is not yet accepted.
S1-S5 partial,S6 held,S7 deferred;no whole requirement closes.

''')
    for name in names:
        path = ROOT / name
        before[name] = sha(path)
        backup = HERE / 'control-before' / name
        backup.parent.mkdir(parents=True, exist_ok=True)
        backup.write_bytes(path.read_bytes())
        if name.endswith('.md'):
            title, rest = path.read_text().split('\n', 1)
            if 'master-current' in name or 'simulator-session' in name:
                rest = 'No command running. Continue corrected schedule integration.\\n'
            path.write_text(title + '\n\n' + note + rest.lstrip('\n'))
    for name, key in [('data/accounting-master/next-plan.json', 'active_execution'),
                      ('scripts/accounting_master_catalog.json', 'active_execution_note')]:
        path = ROOT / name
        data = json.loads(path.read_text())
        old = {k: v for k, v in data.items() if k != key}
        active = data[key]
        active.update(active_work_plan=PLAN, latest_result=REL + '/result.md',
                      updated='2026-10-25')
        if key == 'active_execution':
            active['latest_results'].append(REL + '/result.md')
            active['completed_increments'].append(
                'Schedule evidence repair:15 focused;123 named comparisons;missing accrual and next-period cases')
            active['next'][0] = 'Integrate corrected financing schedules into Version4.15'
        else:
            active['current_candidate'] = '4.14;511 pages;not_ready;4.15 pending schedule integration'
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')
        assert old == {k: v for k, v in json.loads(path.read_text()).items() if k != key}
    (HERE / 'control-refresh.json').write_text(json.dumps(
        {'before': before, 'after': {name: sha(ROOT / name) for name in names},
         'legacy_json_fields_unchanged': True}, indent=2) + '\n')
    print(json.dumps({'controls': len(names), 'next': PLAN, 'checks': checks['checks']}))


if __name__ == '__main__':
    main()
