"""One-time active-control refresh, preserving unrelated historical fields."""
from pathlib import Path
from hashlib import sha256
import json
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REL = HERE.relative_to(ROOT).as_posix()
PLAN = 'docs/plans/accounting-company-functions-integration-20261025.md'

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
    note = f"""## Reusable pure functions checked — 25 October 2026

CompanyFunctions/1 lowers typed declarations to the pinned expression engine.
23 focused methods,79 regression checks and46 comparisons over six cases pass;
complete three-year results match the existing policy and accounting engine.
Recorded verification1262 checks; read-only replay{replay['checks']} checks.
412 protected files remain unchanged. Types,unknowns,lexical scope and bounds
retain explicit refusal semantics. Textual function authoring remains open.
Result: {REL}/result.md. Design: {REL}/design.md.
Next: {PLAN}. Integrate the checked source comparison and function semantics.
Version3.99 remains497 pages,not_ready;S1-S5 partial,S6 held,S7 deferred.
No whole requirement closes. Forecasting remains deferred.

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
            a['completed_increments'].append(f"Pure functions:23 focused methods,79 regression checks,46 comparisons;{replay['checks']} checks;source/function manuscript integration selected")
            a['next'][0] = 'Integrate inspected simulator equations and checked pure functions in protected Version4.00'
        dump(p, d)
        assert old == {k:v for k,v in json.loads(p.read_text()).items() if k != key}
    dump(HERE/'replay-observation.json', replay)
    dump(HERE/'coverage-delta.json', {'whole_rows_closed':0, 'scope':'Optional typed pure functions checked;full language and empirical behavior remain open'})
    dump(HERE/'control-refresh.json', {'before':before, 'after':{n:sha(ROOT/n) for n in names},
                                      'legacy_json_fields_unchanged':True})
    print(json.dumps({'controls':len(names), 'checks':replay['checks'], 'next':PLAN}))

if __name__ == '__main__':
    main()
