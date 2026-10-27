"""Exact diagnostic of debt conventions, not a calibrated financing model."""
from fractions import Fraction as Q
import json
from pathlib import Path

face, rate, probability, recovery = Q(100), Q(5, 100), Q(1, 10), Q(40)
expected_payoff = (1 - probability) * face + probability * recovery
proceeds = expected_payoff / (1 + rate)
yield_face = face / proceeds - 1
yield_printed = (face * (1 + rate) - probability * recovery) / (face * (1 - probability)) - 1
proceeds_printed = face / (1 + yield_printed)
residual = expected_payoff - proceeds_printed * (1 + rate)
assert expected_payoff == 94
assert proceeds == Q(1880, 21)
assert yield_face == Q(11, 94)
assert yield_printed == Q(11, 90)
assert residual == Q(44, 101)
assert proceeds * (1 + rate) == expected_payoff
assert face * (1 + rate) == probability * recovery + (1 - probability) * face * (1 + yield_printed)
for p, rec in [(Q(0), Q(40)), (Q(1, 10), Q(0))]:
    payoff = (1-p)*face + p*rec
    y_consistent = face*(1+rate)/payoff-1
    y_printed = (face*(1+rate)-p*rec)/(face*(1-p))-1
    assert y_consistent == y_printed
cash, debt, equity = Q(95), Q(100), Q(-5)
assert cash == debt + equity
branches = {}
for name, expense in [('fixed', Q(5)), ('floating', Q(7))]:
    closing_cash, closing_equity = cash-expense, equity-expense
    assert closing_cash == debt + closing_equity
    branches[name] = {'interest': str(expense), 'cash': str(closing_cash), 'debt': str(debt), 'equity': str(closing_equity)}
result = {'status': 'passed_exact_diagnostic', 'inputs_are_synthetic': True,
          'scope': 'Cash-convention algebra with held-fixed default probability; no endogenous equilibrium, calibration or ranking.',
          'face': str(face), 'risk_free_rate': str(rate), 'default_probability': str(probability),
          'default_recovery': str(recovery), 'expected_payoff': str(expected_payoff),
          'consistent_proceeds': str(proceeds), 'consistent_yield': str(yield_face),
          'printed_convention_yield': str(yield_printed), 'printed_convention_proceeds': str(proceeds_printed),
          'actual_payoff_break_even_residual': str(residual),
          'zero_recovery_and_no_default_coincidence': True, 'history_branches': branches}
destination = Path(__file__).with_name('arithmetic.json')
destination.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
