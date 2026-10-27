"""One-time active-control refresh, preserving unrelated historical fields."""
from pathlib import Path
from hashlib import sha256
import json
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REL = HERE.relative_to(ROOT).as_posix()
PLAN = 'docs/plans/accounting-ordered-identity-requirements-20261024.md'

def sha(p):
    return sha256(p.read_bytes()).hexdigest()

def dump(p, value):
    p.write_text(json.dumps(value, indent=2) + '\n')

def main():
    assert not (HERE / 'control-refresh.json').exists(), 'already refreshed'
    run = subprocess.run([sys.executable, '-B', str(HERE/'verify.py'), '--replay'],
                         cwd=ROOT, capture_output=True, text=True, check=True)
    replay = json.loads(run.stdout)
    checks = json.loads((HERE/'checks.json').read_text())
    names = ['docs/plans/accounting-master-current.md',
             'docs/plans/accounting-master-checkpoint.md',
             'docs/plans/accounting-master-program.md',
             'docs/plans/accounting-mission-requirements.md',
             'docs/plans/accounting-product-design-checkpoint.md',
             'data/accounting-master/next-plan.md',
             'data/accounting-master/simulator-session-20261023.md',
             'data/accounting-master/next-plan.json',
             'scripts/accounting_master_catalog.json']
    note = f'''## Finite collection prerequisites checked — 24 October 2026

The collection layer passes 259 checks, 69 combined unit-test methods and
15 retained cases with 198 protected inputs. Eleven selected comparisons agree;
four preserved lifecycle counterexamples reject full-method promotion and trigger
the next ordered-identity repair. Complete and partial collections remain distinct.
Result: {REL}/result.md.
Scope and decisions: {REL}/design.md.

Next: {PLAN}.
Preserve supplied event order while checking identity creation and consumption,
then continue shared-book state invariants and effects. No execution is authorized
by a selected snapshot pass. Version 3.60 remains 432 pages, not_ready;
S1–S5 partial, S6 held, S7 deferred.

'''
    before = {}
    for name in names:
        p = ROOT/name
        before[name] = sha(p)
        backup = HERE/'control-before'/name
        backup.parent.mkdir(parents=True, exist_ok=True)
        backup.write_bytes(p.read_bytes())
        if name.endswith('.md'):
            title, rest = p.read_text().split('\n', 1)
            p.write_text(title+'\n\n'+note+rest.lstrip('\n'))
    for name, key in [('data/accounting-master/next-plan.json', 'active_execution'),
                      ('scripts/accounting_master_catalog.json', 'active_execution_note')]:
        p = ROOT/name
        d = json.loads(p.read_text())
        old = {k:v for k,v in d.items() if k != key}
        a = d[key]
        a.update(active_work_plan=PLAN, latest_result=REL+'/result.md', updated='2026-10-24')
        if key == 'active_execution':
            a['latest_results'].append(REL+'/result.md')
            a['completed_increments'].append('Finite collections:259 checks;69 unit methods;15 cases;4 lifecycle counterexamples;198 protected inputs')
            a['next'][0] = 'Ordered identity creation/consumption; then shared-book invariants and effects'
        dump(p, d)
        assert old == {k:v for k,v in json.loads(p.read_text()).items() if k != key}
    dump(HERE/'replay-observation.json', replay)
    dump(HERE/'coverage-delta.json', {'whole_rows_closed':0, 'scope':'Selected reusable predicates; full method admission remains open'})
    dump(HERE/'control-refresh.json', {'before':before, 'after':{n:sha(ROOT/n) for n in names},
                                      'legacy_json_fields_unchanged':True})
    print(json.dumps({'controls':len(names), 'checks':replay['checks'], 'next':PLAN}))

if __name__ == '__main__':
    main()
