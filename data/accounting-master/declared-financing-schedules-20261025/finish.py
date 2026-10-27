from pathlib import Path
from hashlib import sha256
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PLAN = 'docs/plans/accounting-declared-financing-schedules-integration-20261025.md'
REL = HERE.relative_to(ROOT).as_posix()


def sha(p):
    return sha256(p.read_bytes()).hexdigest()


def main():
    assert not (HERE / 'control-refresh.json').exists()
    checks = json.loads((HERE / 'checks.json').read_text())
    assert checks['passed']
    comparison = json.loads((HERE / 'comparison.json').read_text())
    assert all(x['passed'] for x in comparison['checks'])
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
    note = (f'''## Financing schedules checked — 25 October 2026

DeclaredFinancingSchedules/1 derives debt,interest payable,equity and dividends
from verified v2 traces and keeps interest-date coverage separate. {checks['focused_tests']} focused tests and220 comparisons across two charts pass;working-capital v2 compatibility passes.
Result: {REL}/result.md. Next: {PLAN}.
Version4.14 remains511 pages,not_ready;S1-S5 partial,S6 held,S7 deferred.
No whole requirement closes;forecasting remains deferred.

''')
    for name in names:
        p = ROOT / name
        before[name] = sha(p)
        backup = HERE / 'control-before' / name
        backup.parent.mkdir(parents=True, exist_ok=True)
        backup.write_bytes(p.read_bytes())
        if name.endswith('.md'):
            title, rest = p.read_text().split('\n', 1)
            if 'master-current' in name or 'simulator-session' in name:
                rest = ('No command running. Preserve all recorded packages and unrelated dirty work.\n'
                        'Latest candidate:Version4.14,511 pages,not_ready.\n')
            p.write_text(title + '\n\n' + note + rest.lstrip('\n'))
    for name, key in [('data/accounting-master/next-plan.json', 'active_execution'),
                      ('scripts/accounting_master_catalog.json', 'active_execution_note')]:
        p = ROOT / name
        data = json.loads(p.read_text())
        old = {k: v for k, v in data.items() if k != key}
        active = data[key]
        active.update(active_work_plan=PLAN, latest_result=REL + '/result.md',
                      updated='2026-10-25')
        if key == 'active_execution':
            active['latest_results'].append(REL + '/result.md')
            active['completed_increments'].append(
                'DeclaredFinancingSchedules/1:10 focused;220 comparisons;working-capital v2 compatible')
            active['next'][0] = 'Integrate financing schedules into Version4.15'
        else:
            active['current_candidate'] = '4.14;511 pages;not_ready'
        p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')
        assert old == {k: v for k, v in json.loads(p.read_text()).items() if k != key}
    (HERE / 'control-refresh.json').write_text(json.dumps(
        {'before': before, 'after': {n: sha(ROOT / n) for n in names},
         'legacy_json_fields_unchanged': True}, indent=2) + '\n')
    print(json.dumps({'controls': len(names), 'next': PLAN, 'checks': checks['checks']}))


if __name__ == '__main__':
    main()
