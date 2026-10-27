"""Exact documentary illustrations; no accounting runtime is exercised."""
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
checks, groups = [], {}


def ck(name, actual, expected):
    checks.append(dict(name=name, actual=str(actual), expected=str(expected),
                       passed=actual == expected))


def journal(name, entries):
    ck(name + '/balanced', sum(entries.values()), 0)
    return {key: str(value) for key, value in entries.items()}


# The announcement is not binding under the supplied facts. Legal release
# occurs at acceptance, before administrative delivery of fixed ordinary shares.
face, old_price, new_price = F(1000), F(25), F(20)
old_shares, new_shares = face / old_price, face / new_price
increment = new_shares - old_shares
loss = increment * 40
debt, old_equity, cash = F(960), F(60), F(1020)
ck('inducement/original-shares', old_shares, 40)
ck('inducement/revised-shares', new_shares, 50)
ck('inducement/amendment-date-loss', loss, 400)
ck('inducement/announcement-quote-understates', loss - increment * 30, 100)
ck('inducement/delivery-quote-overstates', increment * 50 - loss, 100)
issue_equity = debt + loss
ck('inducement/equity-to-issue', issue_equity, 1360)
ck('inducement/balance-after-release', old_equity + issue_equity - loss, cash)
ck('inducement/total-equity-change', issue_equity - loss, debt)
groups['delayed_share_delivery'] = {
    'binding_amendment': '2024-01-05', 'legal_release': '2024-01-05',
    'announcement': '2024-01-01', 'delivery': '2024-01-20',
    'illustrative_dates_only': True, 'announcement_entry': [],
    'amendment': journal('inducement/amendment', {
        'debit-debt': debt, 'debit-expense': loss,
        'credit-equity-to-issue': -issue_equity}),
    'delivery': journal('inducement/delivery', {
        'debit-equity-to-issue': issue_equity,
        'credit-issued-equity': -issue_equity}),
    'closing_cash': str(cash), 'closing_debt': '0',
    'closing_total_equity': str(cash), 'issued_shares': str(new_shares),
    'classification': 'Fixed qualifying ordinary shares; no cash alternative',
}

# Fixed extra cash is a liability while it awaits settlement. Zero discount
# and no debt accrual between legal release and payment are explicit inputs.
bonus = F(100)
cash_equity_at_release = old_equity + debt - bonus
ck('cash-inducement/equity-at-release', cash_equity_at_release, 920)
ck('cash-inducement/balance-at-release', cash_equity_at_release + bonus, cash)
ck('cash-inducement/settled-cash', cash - bonus, 920)
ck('cash-inducement/settled-equity', cash_equity_at_release, cash - bonus)
ck('cash-inducement/no-second-expense', bonus + F(0), 100)
ck('cash-inducement/wrong-equity-credit-overstates', old_equity + debt - cash_equity_at_release, bonus)
groups['delayed_cash_bonus'] = {
    'amendment': journal('cash-inducement/amendment', {
        'debit-debt': debt, 'debit-expense': bonus,
        'credit-equity-to-issue': -debt, 'credit-bonus-payable': -bonus}),
    'payment': journal('cash-inducement/payment', {
        'debit-bonus-payable': bonus, 'credit-cash': -bonus}),
    'closing_cash': '920', 'closing_equity': '920',
    'cash_flow': 'Financing outflow 100; share conversion is noncash',
}

# Original and incremental value use different dates, but identical remaining
# service periods in the first case. All 100 instruments ultimately vest.
quantity, grant_value = F(100), F(3)
original_cost = quantity * grant_value
incremental_cost = quantity * (F(4) - F(2))
original_annual = original_cost / 3
incremental_annual = incremental_cost / 2
charges = [original_annual, original_annual + incremental_annual,
           original_annual + incremental_annual]
ck('award/original-floor', original_cost, 300)
ck('award/modification-increment', incremental_cost, 200)
ck('award/annual-charges', charges, [100, 200, 200])
ck('award/cumulative-total', sum(charges), 500)
ck('award/wrong-replace-with-current-value', sum(charges) - quantity * 4, 100)
ck('award/wrong-grant-date-subtraction', incremental_cost - quantity * (4 - grant_value), 100)
for year, charge in enumerate(charges, 1):
    journal(f'award/year-{year}', {'debit-service-expense': charge,
                                 'credit-award-equity': -charge})
ck('award/total-equity-unchanged', 1000 + sum(charges) - sum(charges), 1000)
groups['beneficial_repricing'] = {
    'original_grant_cost': str(original_cost),
    'incremental_cost': str(incremental_cost),
    'annual_expenses': list(map(str, charges)),
    'closing_award_equity': '500', 'closing_retained_result': '-500',
}

# Additional instruments vest in one year; the unchanged original grant
# continues over its original three years (B43(b)). This is not a shortened
# original service condition under B43(c).
added_value = F(20) * 4
two_clocks = [original_annual, original_annual + added_value, original_annual]
ck('additional/value-at-modification', added_value, 80)
ck('additional/annual-charges', two_clocks, [100, 180, 100])
ck('additional/total', sum(two_clocks), 380)
ck('additional/wrong-two-year-spread-year2-shortfall', two_clocks[1] - (100 + added_value / 2), 40)
ck('adverse/modification-retains-original-total', 3 * original_annual, 300)
groups['separate_service_periods'] = {
    'original': {'quantity': 100, 'grant_value': 3, 'service_years': [1, 2, 3]},
    'additional': {'quantity': 20, 'modification_value': 4, 'service_years': [2]},
    'annual_expenses': list(map(str, two_clocks)),
    'adverse_value_only_modification_total': '300',
}

# Two-thirds of service has been received when cash awards are replaced.
# Carrying amount already includes modification-date cash remeasurement.
liability, equity_value, completed = F(180), F(300), F(2, 3)
equity_now = equity_value * completed
difference = equity_now - liability
remaining = equity_value - equity_now
ck('cash-to-equity/equity-for-service', equity_now, 200)
ck('cash-to-equity/immediate-expense', difference, 20)
ck('cash-to-equity/remaining-service-expense', remaining, 100)
ck('cash-to-equity/lifetime-expense', liability + difference + remaining, 300)
ck('cash-to-equity/equity-after-modification', 1000 - liability - difference + equity_now, 1000)
ck('cash-to-equity/equity-after-completion', 1000 - 300 + equity_value, 1000)
ck('cash-to-equity/higher-liability-gives-credit', equity_now - 220, -20)
groups['cash_to_equity'] = {
    'modification': journal('cash-to-equity/modification', {
        'debit-liability': liability, 'debit-expense': difference,
        'credit-award-equity': -equity_now}),
    'remaining_service': journal('cash-to-equity/remaining', {
        'debit-expense': remaining, 'credit-award-equity': -remaining}),
    'closing_liability': '0', 'closing_award_equity': '300',
    'cash_paid': '0', 'lifetime_expense': '300',
}

# Gross cash sales and consumed services, same earning period, euro per dollar.
# Full forward designated; no forward points/discount/credit effects.
sales, services, r0, r1 = F(100), F(80), F(1), F(11, 10)
net = sales - services
sale_change, expense_change = sales * (r1-r0), -services * (r1-r0)
forward = -net * (r1-r0)
ck('net/gross-sales-change', sale_change, 10)
ck('net/gross-expense-change', expense_change, -8)
ck('net/forward-change', forward, -2)
ck('net/effectiveness-gross-comparison', forward + expense_change, -sale_change)
ck('net/gross-revenue', sales*r1, 110)
ck('net/gross-service-expense', services*r1, 88)
profit = sales*r1 - services*r1 + forward
ck('net/profit', profit, net*r0)
ck('net/closing-cash', 200 + sales*r1 - services*r1 + forward, 220)
ck('net/closing-equity', 200 + profit, 220)
ck('net/wrong-adjusted-revenue', sales*r1 - (sales*r1 + forward), 2)
groups['same_period_net_hedge'] = {
    'gross_USD_sales': '100', 'gross_USD_consumed_services': '80',
    'EUR_per_USD_designation': '1', 'EUR_per_USD_execution': '11/10',
    'forward_remeasurement': journal('net/remeasure', {
        'debit-OCI': -forward, 'credit-forward-liability': forward}),
    'reserve_release': journal('net/release', {
        'debit-separate-hedge-expense': -forward, 'credit-OCI': forward}),
    'forward_settlement': journal('net/settlement', {
        'debit-forward-liability': -forward, 'credit-cash': forward}),
    'profit': str(profit), 'net_OCI': '0', 'closing_reserve': '0',
    'gross_revenue': '110', 'gross_service_expense': '88',
    'separate_hedge_result': '-2', 'closing_cash_and_equity': '220',
}

# Sales precede expenses. The sales FX effect enters the hedge timing
# adjustment only when revenue is recognized; the expense is still forecast.
period1_hedge_result = -sale_change
reserve1 = forward - period1_hedge_result
period1_profit = sales*r1 + period1_hedge_result
period1_cash = F(200) + sales*r1
period1_equity = F(200) + period1_profit + reserve1
ck('timing/period1-separate-hedge-loss', period1_hedge_result, -10)
ck('timing/period1-profit', period1_profit, 100)
ck('timing/period1-reserve', reserve1, 8)
ck('timing/period1-equity', period1_equity, 308)
ck('timing/period1-balance', period1_cash, period1_equity - forward)
period2_profit = -services*r1 + reserve1
period2_cash_flow = -services*r1 + forward
ck('timing/period2-profit', period2_profit, -80)
ck('timing/period2-cash-flow', period2_cash_flow, -90)
ck('timing/lifetime-profit', period1_profit+period2_profit, profit)
ck('timing/closing-cash', period1_cash+period2_cash_flow, 220)
ck('timing/closing-equity', period1_equity+period2_profit-reserve1, 220)
ck('timing/wrong-release-only-forward-period1', sales*r1 + forward - period1_profit, 8)
groups['different_period_net_hedge'] = {
    'same_facts_except_service_period': True,
    'period1_sale_timing': journal('timing/sale-adjustment', {
        'debit-separate-hedge-expense': sale_change, 'credit-OCI': -sale_change}),
    'period1': {'revenue': '110', 'service_expense': '0', 'hedge_result': '-10',
                'profit': '100', 'OCI': '8', 'reserve': '8', 'cash': '310',
                'forward_liability': '2', 'equity': '308'},
    'period2_release': journal('timing/release', {
        'debit-OCI': reserve1, 'credit-separate-hedge-income': -reserve1}),
    'period2': {'revenue': '0', 'service_expense': '88', 'hedge_result': '8',
                'profit': '-80', 'OCI': '-8', 'reserve': '0', 'cash': '220',
                'forward_liability': '0', 'equity': '220'},
}

# Nil position has no derivative. Eligibility depends on all four separately
# supplied rolling-strategy facts, not on the arithmetic equality alone.
nil_expense = sales
nil_reserve1 = sales*(r1-r0)
nil_profit1 = sales*r1 - nil_reserve1
nil_profit2 = -nil_expense*r1 + nil_reserve1
ck('nil/net-exposure', sales-nil_expense, 0)
ck('nil/period1-reserve', nil_reserve1, 10)
ck('nil/period1-profit', nil_profit1, 100)
ck('nil/period2-profit', nil_profit2, -100)
ck('nil/lifetime-profit', nil_profit1+nil_profit2, 0)
ck('nil/lifetime-cash', sales*r1-nil_expense*r1, 0)
ck('nil/period1-balance', 200+sales*r1, 200+nil_profit1+nil_reserve1)
groups['nil_position'] = {
    'designation_conditions': [
        'Actual rolling net-risk strategy', 'Changes in position size over time',
        'Eligible instruments and hedge accounting normally used when nonnil',
        'Without nil designation offsetting-risk recognition would be inconsistent'],
    'derivative': None, 'period1_profit': '100', 'period1_reserve': '10',
    'period2_profit': '-100', 'period2_reserve': '0',
    'absent_strategy': 'Not eligible for nil hedge designation; not a zero-valued derivative',
}

sources = [ROOT/'docs/design/research/p08-v3-preparation'/name
           for name in ['eu-2023-1803-original.pdf', 'eu-2023-1803-original.txt']]
result = dict(passed=all(c['passed'] for c in checks), count=len(checks),
              group_count=len(groups), groups=groups, checks=checks,
              sources=[dict(path=str(p.relative_to(ROOT)),
                            sha256=hashlib.sha256(p.read_bytes()).hexdigest())
                       for p in sources],
              evidence_role='Deterministic conditional arithmetic, not application admission or runtime conformance')
(OUT/'cases.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps({k: result[k] for k in ['passed', 'count', 'group_count']}))
assert result['passed'], [c for c in checks if not c['passed']]
