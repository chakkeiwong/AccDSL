"""One-time active-control refresh, preserving unrelated historical fields."""
from pathlib import Path
from hashlib import sha256
import json
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REL = HERE.relative_to(ROOT).as_posix()
PLAN = 'docs/plans/accounting-company-functions-20261025.md'

def sha(p):
    return sha256(p.read_bytes()).hexdigest()

def dump(p, value):
    p.write_text(json.dumps(value, indent=2) + '\n')

def main():
    assert not (HERE / 'control-refresh.json').exists(), 'already refreshed'
    run = subprocess.run([sys.executable, '-B', str(HERE/'verify.py')],
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
    note = f"""## Simulator source recovery checked — 25 October 2026

Gentry/Hoque1990 is retained and technically inspected as a distinct comparator.
{replay['checks']} verification checks preserve {replay['protected_files']} files;
all53 obligations,6 interactions and46 operations remain exactly referenced.
Nine obligations receive scoped source evidence; no whole requirement closes.
ACTUS matched-core and Gentry1974/1979 and Francis/Rowell1978 gaps remain open.
Result: {REL}/result.md. Synthesis: docs/design/research/simulator-equations-and-events-20261025.md.
Next: {PLAN}. Extend pure policy functions through the checked expression engine,
then integrate the new source/design evidence into a protected successor.
Version3.99 remains497 pages,not_ready; S1-S5 partial,S6 held,S7 deferred.

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
                rest='No command running. Preserve all recorded packages and unrelated dirty work.\nLatest candidate: Version 3.99, 497 pages, not_ready.\nNo commit, subagents, background campaign, outreach or forecast run.\nRead the current next plan; detailed history is in linked result files.\n'
            p.write_text(title+'\n\n'+note+rest.lstrip('\n'))
    for name, key in [('data/accounting-master/next-plan.json', 'active_execution'),
                      ('scripts/accounting_master_catalog.json', 'active_execution_note')]:
        p = ROOT/name
        d = json.loads(p.read_text())
        old = {k:v for k,v in d.items() if k != key}
        a = d[key]
        a.update(active_work_plan=PLAN, latest_result=REL+'/result.md', updated='2026-10-25')
        if key == 'active_execution':
            a['latest_results'].append(REL+'/result.md')
            a['completed_increments'].append(f"Simulator source recovery:53/6/46 retained;{replay['checks']} checks;pure-function extension selected")
            a['next'][0] = 'Implement and verify optional reusable pure policy functions against existing expression semantics'
        dump(p, d)
        assert old == {k:v for k,v in json.loads(p.read_text()).items() if k != key}
    dump(HERE/'replay-observation.json', replay)
    dump(HERE/'coverage-delta.json', {'whole_rows_closed':0, 'scope':'Distinct1990 comparator inspected;remaining source gaps preserved;no model adoption'})
    dump(HERE/'control-refresh.json', {'before':before, 'after':{n:sha(ROOT/n) for n in names},
                                      'legacy_json_fields_unchanged':True})
    print(json.dumps({'controls':len(names), 'checks':replay['checks'], 'next':PLAN}))

if __name__ == '__main__':
    main()
