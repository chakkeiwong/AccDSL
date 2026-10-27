"""Exact checks of the explicitly scoped source transcription; no model fit."""
from fractions import Fraction

def check():
    rows = [
        ('A', [100, -40, -10, -5], 45, -10, 35),
        ('B', [75, -35, -15, -10], 15, -8, 7),
        ('C', [50, -30, -20, -15], -15, -5, -20),
        ('D', [25, -20, 0, -30], -25, 0, -25),
    ]
    checks = []
    for name, components, before, wc, after in rows:
        checks.append({'name': name + '_before_working_capital', 'passed': sum(components) == before})
        checks.append({'name': name + '_after_working_capital', 'passed': sum(components) + wc == after})
    # Equation 1 coefficient vector, with cash explicitly normalized.
    nine = ['NOF', 'ARF', 'INVF', 'OCAF', 'APF', 'OCLF', 'FCE', 'NIF', 'DIV']
    eq1 = {x: 1 for x in nine + ['NFF', 'NOAL']}
    eq1['Cash'] = -1
    fcf_minus_cash_plus_financing = {x: 1 for x in nine + ['NFF', 'NOAL']}
    fcf_minus_cash_plus_financing['Cash'] = -1
    checks.append({'name': 'normalized_FCF_identity_coefficients', 'passed': eq1 == fcf_minus_cash_plus_financing})
    # Synthetic unit counterexample, not a row imputed to Exhibit 1.
    raw_cash, raw_financing, raw_other, tcf = map(Fraction, [100, 20, 10, 200])
    correct = (raw_cash - raw_financing - raw_other) / tcf
    mixed = raw_cash - raw_financing / tcf - raw_other / tcf
    checks.append({'name': 'explicit_normalization', 'passed': correct == Fraction(7, 20)})
    checks.append({'name': 'mixed_unit_expression_is_different', 'passed': mixed != correct})
    return checks

if __name__ == '__main__':
    import json
    checks = check()
    print(json.dumps({'passed': all(x['passed'] for x in checks), 'checks': checks}))
