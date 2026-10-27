"""One-time active-control refresh, preserving unrelated historical fields."""
from pathlib import Path
from hashlib import sha256
import json
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REL = HERE.relative_to(ROOT).as_posix()
PLAN = 'docs/plans/accounting-temporal-network-integration-20261024.md'

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
    note = f"""## Retained statement network checked — 24 October 2026

The requested 101-relation system remains unresolved on a retained debt-issuance
dash. An explicitly narrower 100-relation/229-observation system is conditionally
feasible with exact witness checks. All 256 source observations and 143 relation
dispositions remain, including three omission-dependent and 39 other unsupported
relations. Targeted regressions and semantic replay pass; see recorded checks.
Result: {REL}/result.md. Scope: {REL}/design.md.
Next: {PLAN}. Integrate temporal types and the selected statement network,
then audit remaining state/history dependencies against existing reconstruction.
Version 3.63 remains 441 pages, not_ready; temporal/network increments are not yet
integrated. S1–S5 partial, S6 held, S7 deferred; no whole requirement closes.

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
                rest='No command running. Preserve all recorded packages and unrelated dirty work.\nLatest candidate: Version 3.63, 441 pages, not_ready.\nNo commit, subagents, background campaign, outreach or forecast run.\nRead the current next plan; detailed history is in linked result files.\n'
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
            a['completed_increments'].append('Statement network:101 requested unresolved;100 explicitly selected feasible;229 quantities;full source preserved')
            a['next'][0] = 'Integrate temporal/network semantics and audit admissible state/history dependencies'
        dump(p, d)
        assert old == {k:v for k,v in json.loads(p.read_text()).items() if k != key}
    dump(HERE/'replay-observation.json', replay)
    dump(HERE/'coverage-delta.json', {'whole_rows_closed':0, 'scope':'Selected source measurement consistency; full historical reconstruction and method admission remain open'})
    dump(HERE/'control-refresh.json', {'before':before, 'after':{n:sha(ROOT/n) for n in names},
                                      'legacy_json_fields_unchanged':True})
    print(json.dumps({'controls':len(names), 'checks':replay['checks'], 'next':PLAN}))

if __name__ == '__main__':
    main()
