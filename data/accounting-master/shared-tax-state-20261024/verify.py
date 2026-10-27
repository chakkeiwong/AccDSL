"""Bounded deterministic conformance recording; no statutory or annual promotion."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
from fractions import Fraction as Q
import json, os, platform, subprocess, sys, time
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from examples import cases, m


def sha(p): return sha256(p.read_bytes()).hexdigest()
def dump(p, value): p.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')
def canonical(value): return m.book.caller.canonical(value)


def conformance():
    checks = []; observations = []
    def check(name, value): checks.append({'name': name, 'passed': bool(value)})
    lock = json.loads((HERE / 'source-lock.json').read_text())
    for path, expected in lock.items(): check('protected:' + path, sha(ROOT / path) == expected)
    tests = json.loads((HERE / 'test-observation.json').read_text())
    check('tests_pass', tests['exit_code'] == 0)
    for path, expected in tests['files'].items(): check('tested_bytes:' + path, sha(ROOT / path) == expected)
    for row in cases():
        body = row['request']; before = canonical(body); result = m.propose(body); name = row['case']
        check(name + ':status', result['status'] == row['expected_status'])
        check(name + ':inputs_unchanged', canonical(body) == before)
        check(name + ':no_promotion', all(result[k] is False for k in m.FLAGS))
        if result['status'] == 'proposed':
            state = result['after']; native = result['native_report']; closing = native['execution']['after']
            check(name + ':journal_balanced', sum(Q(v) for v in result['journal'].values()) == 0)
            check(name + ':state_balanced', sum(Q(v) for v in state['balances'].values()) == 0)
            check(name + ':four_statement_ties', set(result['recorded_statements']['reconciliations'].values()) == {'0/1'})
            check(name + ':original_close_preserved', state['native_tax_closed_until'] == closing['tax_closed_until'])
            check(name + ':deferred_and_other_balances_preserved', all(state['balances'][k] == v for k,v in closing['balances'].items() if k not in ['cash','current_tax']))
            check(name + ':full_native_report', canonical(native) == canonical(result['loss_result']['reconciliation_result']['information_result']['native_report']))
            check(name + ':full_loss_state', canonical(state['loss_state']) == canonical(result['loss_result']['proposal']['after']))
            applied = m.apply(body, result)
            check(name + ':apply_exact', applied['status'] == 'applied' and canonical(applied['after']) == canonical(state))
        observations.append({**row, 'result': result})
    by = {r['case']: r['result'] for r in observations}
    check('half_unit_accrual', by['accrual_consume_19_from_21']['after']['balances']['current_tax'] == '1/2')
    check('no_cash_at_accrual', by['accrual_consume_19_from_21']['after']['balances']['cash'] == '500/1')
    check('full_payment_cash', by['payment_full']['after']['balances']['cash'] == '999/2')
    check('partial_payment_remaining', by['payment_partial']['after']['balances']['income_tax_payable'] == '-1/4')
    check('loss_quantity_is_not_dta', by['accrual_generate_19']['after']['balances']['dta'] == by['accrual_generate_19']['native_report']['execution']['after']['balances']['dta'])
    return checks, observations, tests, lock


def main():
    mode = sys.argv[1] if len(sys.argv) == 2 else '--check'
    assert mode in ['--check','--record','--replay']
    assert mode != '--record' or not (HERE / 'manifest.json').exists(), 'already frozen'
    start = time.monotonic(); started = datetime.now(timezone.utc).isoformat()
    if mode == '--replay':
        manifest = json.loads((HERE / 'manifest.json').read_text())
        for group in ['inputs', 'files']:
            for name, expected in manifest[group].items(): assert sha(ROOT / name) == expected, name
    checks, rows, tests, lock = conformance()
    passed = all(c['passed'] for c in checks)
    observation = {'passed': passed, 'checks': len(checks), 'cases': len(rows),
                   'protected_files': len(lock), 'test_methods': tests['test_methods'],
                   'regression_methods': tests['regression_methods'], 'whole_requirements_closed': 0,
                   'actual_tax_assessed': False, 'committed': False, 'native_financial_carry': False}
    if not passed: dump(HERE / ('failure-' + str(time.time_ns()) + '.json'), checks)
    if passed and mode == '--record':
        dump(HERE / 'checks.json', checks); dump(HERE / 'cases.json', rows)
        dump(HERE / 'check-names.json', [c['name'] for c in checks])
        selected = [p for p in HERE.iterdir() if p.is_file() and p.suffix in ['.py','.json','.md','.txt']]
        selected += [ROOT / 'scripts/shared_tax_state_v1.py', ROOT / 'tests/test_shared_tax_state_v1.py',
                     ROOT / 'docs/plans/accounting-tax-state-integration-20261024.md']
        dump(HERE / 'manifest.json', {'recorded_at': started, 'git_commit': subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'command': 'python3 -B data/accounting-master/shared-tax-state-20261024/verify.py --record',
            'environment': {'python': platform.python_version(), 'executable': sys.executable},
            'cpu_gpu': 'CPU only; CUDA_VISIBLE_DEVICES=-1; no GPU framework imported',
            'random_seeds': 'N/A: deterministic conformance', 'wall_seconds': time.monotonic()-start,
            'data_version': 'source-lock.json', 'plan': 'docs/plans/accounting-shared-tax-state-20261024.md',
            'result': str((HERE/'result.md').relative_to(ROOT)), 'observation': observation,
            'inputs': lock, 'files': {str(p.relative_to(ROOT)): sha(p) for p in selected}})
    elif passed and mode == '--replay':
        assert canonical(checks) == canonical(json.loads((HERE / 'checks.json').read_text()))
        assert canonical(rows) == canonical(json.loads((HERE / 'cases.json').read_text()))
    print(json.dumps(observation)); return not passed


if __name__ == '__main__': raise SystemExit(main())
