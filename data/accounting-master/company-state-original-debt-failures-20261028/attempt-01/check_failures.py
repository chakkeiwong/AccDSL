"""Original debt discriminators through the existing compiler and family solver."""
import argparse
from copy import deepcopy
from dataclasses import replace
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
from test_accounting_p03 import BASE, bindings
from core0_frontends_v1 import compile_source
from reconstruction_v1 import from_p03
from rational_solver_v1 import Budget, q, solve

PLAN = 'docs/plans/company-state-original-debt-failures-20261028.md'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    out = parser.parse_args().output.resolve(); out.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    source_inputs = [ROOT / PLAN, Path(__file__), ROOT / 'docs/design/fixtures/borrowing.acc',
                     ROOT / 'docs/design/fixtures/borrowings.json', ROOT / 'docs/design/fixtures/demo-debt-package.json',
                     ROOT / 'data/accounting-master/unified-program-20261028/failure-map.json']
    fixture = json.loads(source_inputs[3].read_text())['exact']
    compiled = compile_source(BASE, bindings())
    checks, results = [], {}
    def check(name, actual, expected):
        checks.append(dict(name=name, passed=actual == expected, actual=actual, expected=expected))
    check('compiler accepts retained source', compiled.valid, True)
    if not compiled.valid:
        raise RuntimeError('retained compiler baseline rejected')
    problem = from_p03(compiled.ir, bindings(), {'DemoDebt@1/DebtMix': 'fixed-floating-amounts-v1'})
    check('native family supported', problem.unsupported, [])
    fixed, floating = problem.outputs['fixed'], problem.outputs['floating']
    historical_interest = q(fixture['historical_rate']) * (fixed + floating)
    problem.add('original:historical-interest', historical_interest == q(fixture['historical_interest']))
    cash = q(fixture['cash']) - problem.outputs['interest']
    budget = Budget(10, 10000, 100, 100, 10000, 1000, 1000000)
    def run(name, objective=None, extra=(), selected_budget=budget):
        result = solve(problem, selected_budget, objective, extra=extra)
        results[name] = result
        return result
    r = run('whole interest family', problem.outputs['interest'])
    check('family feasible', r['feasibility'], 'Feasible')
    check('family search coverage complete', r['coverage']['complete'], True)
    check('interest exact endpoints', [r['bounds'][k]['value'] for k in ['lower', 'upper']], ['5', '7'])
    r = run('whole cash family', cash)
    check('cash exact endpoints', [r['bounds'][k]['value'] for k in ['lower', 'upper']], ['88', '90'])
    snapshots = []
    for name, f, v, interest, cash_value in [('fixed', '100', '0', '5', '90'),
                                           ('floating', '0', '100', '7', '88'),
                                           ('interior', '50', '50', '6', '89')]:
        extra = (fixed == q(f), floating == q(v))
        r = run(name, problem.outputs['interest'], extra)
        check(name + ' historical and stress family feasible', r['feasibility'], 'Feasible')
        check(name + ' exact stress interest', [r['bounds'][k]['value'] for k in ['lower', 'upper']], [interest] * 2)
        snapshots.append(dict(name=name, fixed=f, floating=v, principal='100', historical_interest='5',
                              stress_interest=interest, closing_cash=cash_value, probability=None))
        check(name + ' independent interest', str(Q(f) * Q(fixture['fixed_rate']) + Q(v) * Q(fixture['stress_rate'])), interest)
        check(name + ' independent cash', str(Q(fixture['cash']) - Q(interest)), cash_value)
    r = run('joint impossible pair', extra=(problem.outputs['interest'] == q(7), cash == q(90)))
    check('original marginal combination rejected', r['feasibility'], 'Infeasible')
    check('joint rejection complete', r['coverage']['complete'], True)
    r = run('joint identity violation', extra=(cash + problem.outputs['interest'] != q(95),))
    check('joint identity universally holds within declared family', r['feasibility'], 'Infeasible')
    # These are additional observations of unchanged coupons, not independent likelihoods.
    before = deepcopy(problem.constraints)
    for year in ['second_pre_reset_period', 'third_pre_reset_period']:
        problem.add('original:repeated-interest:' + year, historical_interest == q(5))
    for name, f, expected in [('fixed', 100, '5'), ('floating', 0, '7'), ('interior', 50, '6')]:
        r = run('repeated unchanged observations ' + name, problem.outputs['interest'], (fixed == q(f),))
        check('uninformative repeats preserve ' + name, r['feasibility'], 'Feasible')
        check('uninformative repeats preserve later amount ' + name, r['bounds']['lower']['value'], expected)
    check('repeated observations retained', len(problem.constraints), len(before) + 2)
    r = run('zero-cell budget', problem.outputs['interest'], selected_budget=replace(budget, max_cells=0))
    check('resource stop is not infeasible', r['feasibility'], 'Unknown')
    check('resource stop coverage incomplete', r['coverage']['complete'], False)
    check('resource stop no fabricated cells', r['coverage']['completed'], 0)
    check('resource stop retains remainder', r['coverage']['unresolved'] > 0, True)
    check('resource stop retains formula', bool(r['coverage']['unvisited']['retained_formula']), True)
    check('no probabilities assigned', [v['probability'] for v in snapshots], [None] * 3)
    original = json.loads((ROOT / 'data/accounting-master/unified-program-20261028/failure-map.json').read_text())
    wanted = {'SIM-F005', 'SIM-F007', 'SIM-F009', 'SIM-F014'}
    rows = [r['original_row'] for r in original['rows'] if r['original_row']['id'] in wanted]
    check('all four exact original rows retained', sorted(r['id'] for r in rows), sorted(wanted))
    for module in list(sys.modules.values()):
        p = getattr(module, '__file__', None)
        if p and Path(p).is_file() and Path(p).resolve().is_relative_to(ROOT):
            source_inputs.append(Path(p).resolve())
    failed = [c for c in checks if not c['passed']]
    verification = dict(status='fail' if failed else 'pass', checks=len(checks), cases=len(results), failed=failed,
                        original_rows=sorted(wanted), original_statuses_changed=False, empirical_forecast=False)
    manifest = dict(git_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        command=[sys.executable, *sys.argv], environment=sys.version, cpu_gpu='CPU-only exact rational SMT; no accelerator imports',
        random_seeds='N/A exact deterministic claims; no stochastic inference',
        data_version='Retained synthetic borrowing.acc/borrowings.json with explicit historical-interest equality',
        utc=datetime.now(timezone.utc).isoformat(), wall_seconds=time.monotonic() - start,
        plan_file=PLAN, result_file=str((HERE / 'result.md').relative_to(ROOT)),
        source_hashes={str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in sorted(set(source_inputs))})
    for name, value in [('verification', verification), ('checks', checks), ('results', results), ('run-manifest', manifest),
                        ('original-rows', rows), ('ir', compiled.ir), ('witnesses', snapshots)]:
        (out / (name + '.json')).write_text(json.dumps(value, indent=2) + '\n')
    (out / 'family.smt2').write_text('\n'.join(label + ': ' + expr.sexpr() for label, expr in problem.constraints) + '\n')
    (out / 'check_failures.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps(verification))
    return bool(failed)


if __name__ == '__main__':
    raise SystemExit(main())
