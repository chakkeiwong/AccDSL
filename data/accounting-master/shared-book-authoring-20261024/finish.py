from pathlib import Path
from hashlib import sha256
import json
import subprocess
import sys

HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[2]
REL = HERE.relative_to(ROOT).as_posix()
PLAN = 'docs/plans/accounting-shared-authoring-integration-20261024.md'
def sha(p): return sha256(p.read_bytes()).hexdigest()
def dump(p, value): p.write_text(json.dumps(value, indent=2) + '\n')


def main():
    assert not (HERE / 'control-refresh.json').exists(), 'already refreshed'
    replay = json.loads(subprocess.run([sys.executable, '-B', str(HERE / 'verify.py'), '--replay'],
        cwd=ROOT, capture_output=True, text=True, check=True).stdout)
    names = ['docs/plans/accounting-master-current.md', 'docs/plans/accounting-master-checkpoint.md',
        'docs/plans/accounting-master-program.md', 'docs/plans/accounting-mission-requirements.md',
        'docs/plans/accounting-product-design-checkpoint.md', 'data/accounting-master/next-plan.md',
        'data/accounting-master/simulator-session-20261023.md', 'data/accounting-master/next-plan.json',
        'scripts/accounting_master_catalog.json']
    before = {}
    for name in names:
        p = ROOT / name; before[name] = sha(p); backup = HERE / 'control-before' / name
        backup.parent.mkdir(parents=True, exist_ok=True); backup.write_bytes(p.read_bytes())
    note = f'''## Complete mixed-book authoring checked — 24 October 2026

289 checks preserve 152 files. Sixteen original requests reproduce complete
native results through text and typed records; three requests have explicit
compiler refusals. Eleven focused and 17 native regression methods pass.
Complete openings, ordered events, exact identities and unknowns are preserved.
Result: {REL}/result.md. Contract: {REL}/design.md.
Next: {PLAN}. Integrate the finite authoring route in protected Version 3.77,
then refresh all coverage and continue substantive simulator/DSL work.
Version 3.76 remains 475 pages, not_ready; S1–S5 partial, S6 held, S7 deferred.

'''
    for name in names:
        p = ROOT / name
        if name.endswith('.md'):
            title, rest = p.read_text().split('\n', 1)
            if 'simulator-session' in name:
                rest = 'No command running. Authoring evidence and controls are complete and frozen.\nBegin the protected Version 3.77 integration; preserve all predecessor evidence.\nNo commit, agents, outreach, forecasting or production promotion.\n'
            p.write_text(title + '\n\n' + note + rest.lstrip('\n'))
    for name, key in [('data/accounting-master/next-plan.json', 'active_execution'),
                      ('scripts/accounting_master_catalog.json', 'active_execution_note')]:
        p = ROOT / name; data = json.loads(p.read_text()); other = {k: v for k, v in data.items() if k != key}
        active = data[key]; active.update(active_work_plan=PLAN, latest_result=REL + '/result.md', updated='2026-10-24')
        if key == 'active_execution':
            active['latest_results'].append(REL + '/result.md')
            active['completed_increments'].append('Shared-book authoring: 289 checks; 16 exact matches, 3 compiler refusals; 11 focused and 17 regression methods')
            active['next'][0] = 'Integrate complete mixed-book authoring in protected Version 3.77'
        dump(p, data); assert other == {k: v for k, v in json.loads(p.read_text()).items() if k != key}
    dump(HERE / 'replay-observation.json', replay)
    dump(HERE / 'coverage-delta.json', {'whole_rows_closed': 0,
        'mc_scope': ['MC05','MC11','MC13','MC16','MC24','MC26','MC28'],
        'latest_full_inventory': 'data/accounting-master/shared-statement-coverage-20261024/inventory.json',
        'full_inventory_refresh_pending': True})
    dump(HERE / 'control-refresh.json', {'before': before, 'after': {n: sha(ROOT / n) for n in names},
                                       'legacy_json_fields_unchanged': True})
    print(json.dumps({'controls': len(names), 'checks': replay['checks'], 'next': PLAN}))


if __name__ == '__main__': main()
