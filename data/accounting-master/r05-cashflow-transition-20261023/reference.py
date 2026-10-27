"""Exact synthetic reclassification identities, not an accounting engine."""
from fractions import Fraction as F


def totals(cash, categories):
    assert set(cash) == set(categories)
    assert set(categories.values()) <= {'operating', 'investing', 'financing'}
    return {category: sum((amount for flow, amount in cash.items() if categories[flow] == category), F(0))
            for category in ('operating', 'investing', 'financing')}


def check():
    cash = {'core': F(100), 'interest_paid': F(-12), 'interest_received': F(5),
            'dividends_received': F(3), 'dividends_paid': F(-8)}
    ordinary = {'core': 'operating', 'interest_paid': 'financing', 'interest_received': 'investing',
                'dividends_received': 'investing', 'dividends_paid': 'financing'}
    old_interest_operating = dict(ordinary, interest_paid='operating', interest_received='operating', dividends_received='operating')
    old_receipts_operating = dict(ordinary, interest_received='operating', dividends_received='operating')
    old_dividends_operating = dict(ordinary, dividends_paid='operating')
    new = totals(cash, ordinary)
    cases = []
    for name, old, delta in [('interest_and_receipts_reclassified', old_interest_operating, F(4)),
                             ('receipts_only_reclassified', old_receipts_operating, F(-8)),
                             ('dividends_paid_only_reclassified', old_dividends_operating, F(8))]:
        before = totals(cash, old)
        assert new['operating'] - before['operating'] == delta
        assert sum(new.values(), F(0)) == sum(before.values(), F(0)) == F(88)
        cases.append({'case': name, 'old_ocf': str(before['operating']), 'new_ocf': str(new['operating']),
                      'ocf_change': str(delta), 'total_cash_change': '0'})
    assert F(70) + F(26) == F(90) + F(6) == F(96)
    cases.append({'case': 'reconciliation_start_only', 'old_start': '70', 'old_adjustments': '26',
                  'new_start': '90', 'new_adjustments': '6', 'unchanged_ocf': '96'})
    # Conditional 34D example: interest expense in operating and financing;
    # all cash interest is assigned to either one associated category.
    choice_o = totals(cash, old_interest_operating)
    choice_f = totals(cash, dict(old_interest_operating, interest_paid='financing'))
    assert choice_o['operating'] == 96 and choice_f['operating'] == 108
    assert sum(choice_o.values(), F(0)) == sum(choice_f.values(), F(0)) == 88
    cases.append({'case': 'conditional_34D_whole_interest_policy', 'operating_policy_ocf': '96',
                  'financing_policy_ocf': '108', 'unchanged_total_cash': '88'})
    return {'exact_examples': cases, 'exact_example_count': len(cases), 'actual_issuer_values_used': 0,
            'issuer_policies_selected': False, 'empirical_execution': False}


if __name__ == '__main__':
    import json
    print(json.dumps(check()))
