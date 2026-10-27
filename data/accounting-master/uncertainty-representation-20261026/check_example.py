"""Exact checks for an illustrative symbolic family; no forecasting benchmark."""
from fractions import Fraction as Q
from pathlib import Path
import json

def interest(alpha):
    return Q(5) + Q(2) * alpha

def cash(alpha):
    return Q(95) - interest(alpha)

initial = (Q(0), Q(1))
refined = (Q(1, 5), Q(2, 5))
boundary = Q(3, 10)
threshold = Q(447, 5)
assert (interest(initial[0]), interest(initial[1])) == (5, 7)
assert (interest(refined[0]), interest(refined[1])) == (Q(27, 5), Q(29, 5))
assert (cash(refined[1]), cash(refined[0])) == (Q(446, 5), Q(448, 5))
assert cash(boundary) == threshold
assert cash(refined[0]) > threshold > cash(refined[1])
for alpha in [*initial, *refined, boundary]:
    assert cash(alpha) + interest(alpha) == 95
# Coefficients prove the identity for the full family, beyond the witnesses.
assert Q(90) + Q(5) == 95
assert Q(-2) + Q(2) == 0
result = {
    'status': 'passed_exact_arithmetic',
    'assumptions': 'One-year full pass-through, no maturity, amortisation, hedge, cap or floor; interest is the only cash movement.',
    'interest_formula': '5 + 2*alpha',
    'cash_formula': '90 - 2*alpha',
    'initial_alpha': ['0', '1'],
    'refined_alpha': ['1/5', '2/5'],
    'initial_interest': ['5', '7'],
    'refined_interest': ['27/5', '29/5'],
    'refined_cash': ['446/5', '448/5'],
    'covenant': 'cash >= 447/5',
    'no_breach_region': 'alpha <= 3/10',
    'breach_region': 'alpha > 3/10',
    'joint_identity': 'cash + interest = 95',
    'probabilities': 'not assigned',
    'implementation_status': 'teaching arithmetic only; no symbolic executor implemented',
}
Path(__file__).with_name('arithmetic.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
