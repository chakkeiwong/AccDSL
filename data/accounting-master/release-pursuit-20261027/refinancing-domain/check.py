"""Check the derived cash domain against separate dated event sums; no grid completeness claim."""
from datetime import datetime, timezone
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import hashlib
import json
import os
import platform
import sys
import time

os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
D = Path(__file__).resolve().parent
R = D.parents[3]
start = time.monotonic()
assert not (D / 'checks.json').exists()
baseline = json.loads((D / 'baseline.json').read_text())
for p, h in baseline['sources'].items():
    assert hashlib.sha256((R / p).read_bytes()).hexdigest() == h, p

def run_events(z, a, b, receipt, q, covenant, receipt_first=True):
    reasons = []
    if z not in (F(0), F(1, 2), F(1)):
        reasons.append('sale_not_offered')
    if not 0 < a <= 30:
        reasons.append('bridge_amount_outside_offer')
    if not 0 <= b <= 40:
        reasons.append('term_amount_outside_offer')
    if b > 0 and covenant and 20 * (1-z) < 10:
        reasons.append('term_inventory_covenant')
    if q <= 0:
        reasons.append('nonpositive_supplied_price')
    events = [('day1_opening', F(12)), ('day3_wages', F(-10)),
              ('day4_sale', 15*z), ('day4_bridge_net', a-1),
              ('day4_old_principal', F(-30)), ('day4_old_coupon', F(-2))]
    receipt_event = ('day5_receipt', receipt)
    term_event = ('day5_term_net', q*b-2 if b > 0 else F(0))
    events += [receipt_event, term_event] if receipt_first else [term_event, receipt_event]
    events += [('day6_bridge_repayment', -(a+1))]
    cash, trace = F(0), []
    for name, amount in events:
        cash += amount
        trace.append({'event': name, 'change': amount, 'cash': cash})
    return {'admitted': not reasons, 'reasons': reasons, 'trace': trace,
            'feasible': not reasons and all(x['cash'] >= 0 for x in trace),
            'final_cash': cash, 'minimum_cash': min(x['cash'] for x in trace),
            'remaining_term_face': b, 'inventory': 20*(1-z),
            'bridge_cost': F(2), 'term_fee': F(2) if b > 0 else F(0)}

def derived_domain(z, a, b, receipt, q, covenant):
    u = int(b > 0)
    return (z in (0, F(1, 2), 1) and q > 0 and 0 < a <= 30
            and 0 <= b <= 40 and (not u or not covenant or 20*(1-z) >= 10)
            and 31-15*z <= a and 15*z+receipt+q*b-32-2*u >= 0)

checks = []
def check(name, passed, detail=None):
    checks.append({'check': name, 'passed': bool(passed), 'detail': detail})
    assert passed, (name, detail)

records = []
regimes = []
for z, receipt, q, covenant in product((F(0), F(1, 2), F(1)),
                                      (F(18), F(0)), (F(9, 10), F(3, 5)), (False, True)):
    amin = 31-15*z
    bneed = (34-15*z-receipt)/q
    amounts = sorted({F(0), amin-F(1, 4), amin, (amin+30)/2, F(30), F(121, 4)})
    faces = sorted({F(0), F(1), F(10, 9), F(10), F(20), F(40), F(41),
                    bneed-F(1, 100), bneed, bneed+F(1, 100)})
    for a, b in product(amounts, faces):
        actual = run_events(z, a, b, receipt, q, covenant)
        expected = derived_domain(z, a, b, receipt, q, covenant)
        check('event_domain_agreement', actual['feasible'] == expected,
              {'z': z, 'a': a, 'b': b, 'R': receipt, 'q': q, 'covenant': covenant})
        check('day4_identity', actual['trace'][5]['cash'] == a+15*z-31)
        check('day6_identity', actual['final_cash'] == 15*z+receipt+q*b-32-2*int(b>0))
        if actual['feasible']:
            reduced = run_events(z, amin, b, receipt, q, covenant)
            check('minimum_bridge_preserves_feasibility', reduced['feasible'])
            check('minimum_bridge_preserves_final_cash', reduced['final_cash'] == actual['final_cash'])
        records.append({'parameters': {'z': z, 'a': a, 'b': b, 'R': receipt,
                        'q': q, 'inventory_covenant': covenant}, 'result': actual})
    # This is a small independent hand case table, not a search-completeness oracle.
    expected_existence = (z == 1 and (receipt == 18 or not covenant)) or (
        z == F(1, 2) and (receipt == 18 or q == F(9, 10)))
    b = F(0) if 15*z+receipt >= 32 else bneed
    witness = run_events(z, amin, b, receipt, q, covenant)
    check('hand_regime_existence', witness['feasible'] == expected_existence)
    regimes.append({'z': z, 'R': receipt, 'q': q, 'inventory_covenant': covenant,
                    'expected_existence': expected_existence, 'witness': witness})

# The exact endpoints must be included; a slightly lower quote fails even at cap.
for receipt, threshold in [(F(18), F(17, 80)), (F(0), F(53, 80))]:
    for epsilon in [F(-1, 10000), F(0), F(1, 10000)]:
        q = threshold + epsilon
        r = run_events(F(1, 2), F(47, 2), F(40), receipt, q, True)
        check('exact_quote_boundary', r['feasible'] == (epsilon >= 0))

minimal = run_events(F(1), F(16), F(0), F(18), F(9, 10), True)
buffered = run_events(F(1), F(17), F(0), F(18), F(9, 10), True)
check('both_bridge_paths_feasible', minimal['feasible'] and buffered['feasible'])
check('same_final_cash', minimal['final_cash'] == buffered['final_cash'] == 1)
check('same_bridge_cost', minimal['bridge_cost'] == buffered['bridge_cost'] == 2)
check('different_minimum_cash', minimal['minimum_cash'] == 0 and buffered['minimum_cash'] == 1)
check('no_residual_bridge_or_term_in_example', minimal['remaining_term_face'] == buffered['remaining_term_face'] == 0)

receipt_first = run_events(F(1), F(16), F(10, 9), F(18), F(9, 10), False)
issue_first = run_events(F(1), F(16), F(10, 9), F(18), F(9, 10), False, False)
check('same_day_order_changes_feasibility', receipt_first['feasible'] and not issue_first['feasible'])
check('daily_net_hides_prefix', receipt_first['final_cash'] == issue_first['final_cash'] == 0)
check('opposite_order_shortfall', issue_first['minimum_cash'] == -1)

def dump(name, value):
    (D / name).write_text(json.dumps(value, indent=2, default=str, ensure_ascii=False)+'\n')

dump('traces.json', {'cases': records, 'regimes': regimes,
    'liquidity_counterexample': {'minimum_funding': minimal, 'buffered': buffered},
    'same_day_counterexample': {'receipt_first': receipt_first, 'issue_first': issue_first}})
dump('checks.json', {'passed': True, 'checks': checks, 'case_count': len(records),
    'regime_count': len(regimes), 'scope': 'Dated rational arithmetic and selected boundary checks; continuous completeness follows only from the written derivation, not the sample.',
    'not_concluded': ['stochastic ranking', 'market equilibrium', 'issuer facts',
        'accounting compliance', 'unrestricted policy completeness', 'independent human acceptance']})
dump('run-manifest.json', {'command': [sys.executable, str(Path(__file__).resolve())],
    'git_commit': 'unavailable; unusable marker retained', 'python': sys.version,
    'platform': platform.platform(), 'device': 'CPU-only Fraction arithmetic; no GPU framework imported',
    'environment': {'CUDA_VISIBLE_DEVICES': '-1'}, 'seeds': 'N/A deterministic',
    'data_version': baseline, 'plan': baseline['plan'], 'result': str(D/'result.md'),
    'outputs': ['checks.json', 'traces.json'], 'wall_seconds': time.monotonic()-start,
    'timestamp_utc': datetime.now(timezone.utc).isoformat()})
print(json.dumps({'passed': True, 'checks': len(checks), 'cases': len(records), 'regimes': len(regimes)}))
