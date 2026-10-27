"""One-time active-control refresh, preserving unrelated historical fields."""
from pathlib import Path
from hashlib import sha256
import json
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REL = HERE.relative_to(ROOT).as_posix()
PLAN = 'docs/plans/accounting-joint-source-constraints-audit-20261024.md'

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
    note = f"""## Simulator phase gaps refreshed — 24 October 2026

All 53 obligations, six interactions and 46 operation IDs retain their exact
prior records. Scoped updates incorporate real statement contexts and typed
transitions; joint measurement consistency is the next substantive question.
Result: {REL}/result.md. Phase gaps and decisions: {REL}/review.md.
Next: {PLAN}. Inspect the existing exact reconstruction solver and source
interval contracts before implementing a joint-constraint repair.
Version 3.62 is 439 pages, not_ready; S1–S5 partial, S6 held, S7 deferred.

"""
    before = {}
    for name in names:
        p = ROOT/name
        before[name] = sha(p)
        backup = HERE/'control-before'/name
        backup.parent.mkdir(parents=True, exist_ok=True)
        backup.write_bytes(p.read_bytes())
        if name.endswith('.md'):
            title, rest = p.read_text().split('\n', 1)
            if 'simulator-session' in name:
                rest='No command running. Preserve all recorded packages and unrelated dirty work.\nNo commit, subagents, background campaign, outreach or forecast run.\nRead the current next plan; detailed history is in linked results.\n'
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
            a['completed_increments'].append('Coverage refresh:53 obligations;6 interactions;46 operations;joint measurement consistency selected next')
            a['next'][0] = 'Audit joint source measurement constraints against existing exact reconstruction capability'
        dump(p, d)
        assert old == {k:v for k,v in json.loads(p.read_text()).items() if k != key}
    dump(HERE/'replay-observation.json', replay)
    dump(HERE/'coverage-delta.json', {'whole_rows_closed':0, 'scope':'Selected reusable predicates; full method admission remains open'})
    dump(HERE/'control-refresh.json', {'before':before, 'after':{n:sha(ROOT/n) for n in names},
                                      'legacy_json_fields_unchanged':True})
    print(json.dumps({'controls':len(names), 'checks':replay['checks'], 'next':PLAN}))

if __name__ == '__main__':
    main()
