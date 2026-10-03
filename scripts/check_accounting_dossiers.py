#!/usr/bin/env python3
"""Exact calculations and balanced journals for the three preparation dossiers.

These are authored examples and counterexamples, not accounting eligibility
decisions or a general accounting engine.
"""
from collections import defaultdict
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[1]


def main():
    start = time.monotonic()
    checks, journals, values = [], {}, {}

    def check(name, condition):
        if not condition:
            raise AssertionError(name)
        checks.append(dict(name=name, passed=True))

    def post(book, entries, name, **amounts):
        amounts = {k: Q(v) for k, v in amounts.items()}
        if sum(amounts.values()) != 0:
            raise AssertionError(f'Unbalanced journal: {name}')
        for account, value in amounts.items():
            book[account] += value
        entries.append(dict(operation=name, debit_positive={k: str(v) for k, v in amounts.items()}))

    # The same 20 physical units, followed by one sale of 12, under three rules.
    costs = {'FIFO': Q(10)*5 + Q(2)*7, 'LIFO': Q(10)*7 + Q(2)*5, 'average': Q(12)*Q(120, 20)}
    expected = {'FIFO': (64, 56), 'LIFO': (80, 40), 'average': (72, 48)}
    for method, cost in costs.items():
        check('cost_and_stock_' + method, (cost, 120-cost) == expected[method])
    impaired = min(Q(56), Q(50))
    recovered = min(Q(56), Q(54))
    check('impairment_then_partial_reversal', (56-impaired, recovered-impaired, recovered) == (6, 4, 54))
    check('reversal_capped_at_original_cost', min(Q(56), Q(60))-impaired == 6)
    values['inventory'] = dict(costs={k: str(v) for k, v in costs.items()},
                               original_cost='56', impaired='50', recovered='54', capped_recovery='56')

    liability = Q(5)/Q('1.1') + Q(105)/Q('1.21')
    equity = 100-liability
    check('bond_issue_components', (liability, equity) == (Q(11050,121), Q(1050,121)))
    book, rows = defaultdict(Q), []
    post(book, rows, 'issue', cash=100, liability=-liability, conversion_equity=-equity)
    for period in [1, 2]:
        expense = -book['liability'] * Q(1, 10)
        post(book, rows, f'interest_{period}', interest_expense=expense, liability=-expense)
        post(book, rows, f'coupon_{period}', liability=5, cash=-5)
        check(f'carrying_after_coupon_{period}', -book['liability'] == [Q(1050,11), Q(100)][period-1])
    check('coupon_and_discount_accretion', book['interest_expense'] == Q(2260,121))
    redeemed, converted = book.copy(), book.copy()
    redemption_rows, conversion_rows = list(rows), list(rows)
    post(redeemed, redemption_rows, 'redemption_at_maturity', liability=100, cash=-100)
    post(converted, conversion_rows, 'conversion_at_maturity', liability=100, issued_share_equity=-100)
    check('bond_settlement_paths', redeemed['liability'] == converted['liability'] == 0 and
          converted['cash'] == 90 and converted['conversion_equity'] == -equity)
    check('coupon_equals_yield_boundary', Q(5)/Q('1.05')+Q(105)/Q('1.1025') == 100)
    journals['bond_redemption'], journals['bond_conversion'] = redemption_rows, conversion_rows
    values['bond'] = dict(issue_liability=str(liability), issue_equity=str(equity),
                          total_interest_expense=str(book['interest_expense']))

    # Independent risk-transfer/non-performance inputs demonstrate why ceded
    # claims state must not be computed by halving every gross balance.
    for name, ceded_ra, nonperformance, expected in [
        ('base', Q(1), Q(0), (Q(119), Q(72), Q(47), Q(27), Q(6))),
        ('separate_transferred_risk', Q('1.5'), Q(0), (Q('119.5'), Q(72), Q('47.5'), Q('27.5'), Q('6.5'))),
        ('nonperformance_loss', Q(1), Q(2), (Q(117), Q(72), Q(45), Q(25), Q(4)))]:
        b, rows = defaultdict(Q), []
        post(b, rows, 'capital', cash=20, capital=-20)
        post(b, rows, 'premium_received', cash=120, remaining_coverage=-120)
        post(b, rows, 'reinsurance_premium_paid', reinsurance_coverage=24, cash=-24)
        post(b, rows, 'half_gross_service', remaining_coverage=60, revenue=-60)
        post(b, rows, 'half_ceded_service', reinsurance_expense=12, reinsurance_coverage=-12)
        post(b, rows, 'incurred_claims_and_risk', claims_expense=42, incurred_claims=-42)
        post(b, rows, 'claims_paid', incurred_claims=30, cash=-30)
        recovery = Q(40)*Q(1,2)+ceded_ra-nonperformance
        post(b, rows, 'recognise_recovery', reinsurance_claims=recovery, recovery_income=-recovery)
        post(b, rows, 'recovery_received', cash=15, reinsurance_claims=-15)
        profit = -sum(b[a] for a in ['revenue', 'reinsurance_expense', 'claims_expense', 'recovery_income'])
        assets = sum(b[a] for a in ['cash', 'reinsurance_coverage', 'reinsurance_claims'])
        liabilities = -sum(b[a] for a in ['remaining_coverage', 'incurred_claims'])
        eq = -b['capital']+profit
        check('insurance_' + name, (assets, liabilities, eq, profit, b['reinsurance_claims']) == expected)
        check('insurance_balance_' + name, assets == liabilities+eq and b['cash'] == 101)
        journals['insurance_' + name] = rows
        values['insurance_' + name] = {k: str(v) for k, v in dict(assets=assets, liabilities=liabilities,
            equity=eq, profit=profit, cash=b['cash'], recovery_asset=b['reinsurance_claims']).items()}

    sources = [ROOT/'docs/design/research/standards-support.json', Path(__file__)]
    report = dict(status='passed', count=len(checks), checks=checks, calculations=values, journals=journals,
                  command='python3 scripts/check_accounting_dossiers.py',
                  timestamp_utc=datetime.now(timezone.utc).isoformat(), wall_seconds=time.monotonic()-start,
                  sha256={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
                  scope='Exact arithmetic and signed journal reconciliation under stated dossier assumptions; no source applicability or professional assurance verdict.')
    out = ROOT/'docs/design/review/accounting-dossier-checks.json'
    out.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({k: report[k] for k in ['status', 'count', 'wall_seconds']}))


if __name__ == '__main__':
    main()
