"""Read preserved examples; check accounting and prefix liquidity independently."""
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
SOURCE = ROOT / 'data/accounting-master/corporate-portable-20261015/portable-exchanges.json'
SCHEMAS = SOURCE.with_name('record-schemas.json')
PLAN = ROOT / 'docs/design/proposal/architecture/simulator-design-delta-20261023.md'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rational(value):
    return Q(int(value['n']), int(value['d']))


def affine(value, share):
    return rational(value['constant']) + share * rational(value['coefficient_x'])


def replay(opening, journals, plan, share, enforce_liquidity):
    balances = deepcopy(opening)
    flows = dict.fromkeys(('operating', 'investing', 'financing'), Q(0))
    minimum = balances['cash']
    applied = []
    for journal in journals:
        kind = journal['event_kind']
        amounts = [(line['account'], affine(line['signed_amount'], share))
                   for line in journal['lines']]
        assert sum((v for _, v in amounts), Q(0)) == 0, kind
        cash_delta = sum((v for account, v in amounts if account == 'cash'), Q(0))
        if enforce_liquidity and balances['cash'] + cash_delta < 0:
            return {'status': 'funding_failure', 'event': kind,
                    'available_cash': balances['cash'], 'amount_due': -cash_delta,
                    'shortfall': -(balances['cash'] + cash_delta),
                    'balances': balances, 'flows': flows, 'applied': applied,
                    'minimum_cash': minimum}
        for account, value in amounts:
            balances[account] += value
        category = plan[kind]['cash_class']
        if cash_delta:
            assert category in flows, (kind, category)
            flows[category] += cash_delta
        minimum = min(minimum, balances['cash'])
        applied.append(kind)
    return {'status': 'complete', 'balances': balances, 'flows': flows,
            'minimum_cash': minimum, 'applied': applied}


def main():
    start = time.perf_counter()
    started = datetime.now(timezone.utc).isoformat()
    hashes = {str(p.relative_to(ROOT)): digest(p) for p in (SOURCE, SCHEMAS)}
    data = json.loads(SOURCE.read_text())
    records, aliases = data['record_registry'], data['aliases']
    checks, cases = [], []

    def body(name):
        return records[aliases[name]['digest']]['body']

    def check(name, condition, details=None):
        checks.append({'name': name, 'passed': bool(condition), 'details': details})

    for scenario in ('stress7', 'stress9'):
        p = body('projection.' + scenario)
        opening = {k: rational(v) for k, v in records[p['opening_ref']['digest']]['body']['balances'].items()}
        journal = p['proposed_journals']
        events = {e['event_kind']: e for e in p['event_plan']}
        for share in (Q(0), Q(1, 2), Q(1)):
            tag = scenario + ':x=' + str(share)
            baseline = replay(opening, journal, events, share, True)
            expected = {k: affine(v, share) for k, v in p['closing_balances'].items()}
            lines = {k: affine(v, share) for k, v in p['lines'].items()}
            check(tag + ':all_closing_accounts', baseline['status'] == 'complete' and baseline['balances'] == expected)
            check(tag + ':cash_flow_categories', all(baseline['flows'][k] == lines[k + '_cash'] for k in baseline['flows']))
            check(tag + ':cash_bridge', opening['cash'] + sum(baseline['flows'].values()) == lines['cash'])
            check(tag + ':balance_sheet', lines['assets'] == lines['payables'] + lines['debt'] + lines['equity'])
            check(tag + ':income_and_equity', lines['profit'] == lines['revenue'] - sum(lines[k] for k in ('cost_of_sales', 'payroll', 'depreciation', 'interest', 'tax')) and lines['equity'] == lines['opening_equity'] + lines['profit'] - lines['dividends'])
            check(tag + ':indirect_operating_cash', lines['operating_cash'] == lines['profit'] + lines['depreciation'] - (lines['receivables'] - opening['receivables']) - (lines['inventory'] - opening['inventory']) + (lines['payables'] + opening['payables']) - (lines['tax_prepaid'] - opening['tax_prepaid']))
            reordered = deepcopy(journal)
            i = next(i for i, x in enumerate(reordered) if x['event_kind'] == 'collection')
            j = next(i for i, x in enumerate(reordered) if x['event_kind'] == 'supplier_payment')
            reordered[i], reordered[j] = reordered[j], reordered[i]
            unconstrained = replay(opening, reordered, events, share, False)
            rejected = replay(opening, reordered, events, share, True)
            prefix = replay(opening, reordered[:i], events, share, True)
            check(tag + ':annual_algebra_same', unconstrained['balances'] == baseline['balances'] and unconstrained['flows'] == baseline['flows'])
            check(tag + ':timing_failure', rejected['status'] == 'funding_failure' and rejected['event'] == 'supplier_payment' and rejected['shortfall'] == Q(427, 5))
            check(tag + ':refused_payment_atomic', rejected['balances'] == prefix['balances'] and rejected['flows'] == prefix['flows'] and rejected['applied'] == prefix['applied'])
            check(tag + ':positive_final_cash_is_insufficient', unconstrained['balances']['cash'] > 0 and unconstrained['minimum_cash'] == -Q(427, 5))
            cases.append({'case': tag, 'baseline_closing_cash': lines['cash'],
                          'original_minimum_cash': baseline['minimum_cash'],
                          'reordered_unconstrained_minimum_cash': unconstrained['minimum_cash'],
                          'refusal': {k: rejected[k] for k in ('status', 'event', 'available_cash', 'amount_due', 'shortfall')},
                          'future_after_failure': 'not computed'})

    # The same two known events have two admissible orders when timing is absent.
    # One feasible witness does not establish feasibility for both schedules.
    check('unknown_timing_preserves_both_orders', len(cases) == 6 and all(c['original_minimum_cash'] >= 0 and c['reordered_unconstrained_minimum_cash'] < 0 for c in cases))
    # Pure concept bridge only: stipulated principal is not a Northstar 2025 event.
    cfo, stipulated_principal = Q(50), Q(20)
    check('separate_statement_and_after_principal_concepts', cfo - stipulated_principal == Q(30) and cfo != cfo - stipulated_principal)
    check('preserved_source_bytes', all(digest(ROOT / p) == h for p, h in hashes.items()))
    result = {'passed': all(x['passed'] for x in checks), 'check_count': len(checks),
              'scope': 'exact documentary timing diagnostic; no product endpoint or empirical forecast',
              'timing_assumption': 'original supplied event order versus explicit supplier-before-collection variant',
              'funding_assumption': 'no eligible committed facility; full payment or no payment',
              'unknown_timing_status': 'unresolved feasibility with feasible and funding-failure schedules retained',
              'cases': cases, 'checks': checks}
    (OUT / 'checks.json').write_text(json.dumps(result, indent=2, default=str) + chr(10))
    manifest = {'git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                'command': 'env CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B data/accounting-master/simulator-timing-20261023/verify.py',
                'environment': {'executable': sys.executable, 'python': platform.python_version(), 'dependencies': 'standard library'},
                'cpu_gpu': 'CPU exact arithmetic; GPU intentionally hidden; no ML framework imported',
                'cuda_visible_devices': os.environ.get('CUDA_VISIBLE_DEVICES'),
                'data_version': hashes, 'random_seeds': 'N/A: deterministic rational checks',
                'started_utc': started, 'wall_seconds': time.perf_counter() - start,
                'plan_file': str(PLAN.relative_to(ROOT)),
                'result_file': str((OUT / 'result.md').relative_to(ROOT)),
                'artifacts': {str(p.relative_to(ROOT)): digest(p) for p in (Path(__file__), OUT / 'checks.json')}}
    (OUT / 'run-manifest.json').write_text(json.dumps(manifest, indent=2) + chr(10))
    print(json.dumps({'passed': result['passed'], 'checks': len(checks), 'cases': len(cases),
                      'failures': [c for c in checks if not c['passed']]}))
    if not result['passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
