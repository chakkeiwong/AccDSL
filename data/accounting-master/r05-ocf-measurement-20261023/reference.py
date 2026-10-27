"""Exact, finite-law arithmetic examples; no forecasting runtime or inference."""
from fractions import Fraction as F

ISSUERS = ('apple', 'caterpillar', 'jpmorgan', 'henkel', 'hsbc',
           'munich_re', 'saic_motor', 'ping_an', 'midea')


def crps(law, outcome):
    """E|X-y| - E|X-X'|/2 for an explicit finite probability law."""
    if type(outcome) is not F or type(law) is not tuple or not law:
        raise ValueError('exact outcome and explicit finite weighted law required')
    for atom in law:
        if type(atom) is not tuple or len(atom) != 2:
            raise ValueError('each atom needs a value and a probability')
        x, p = atom
        if type(x) is not F or type(p) is not F or p < 0:
            raise ValueError('exact values and nonnegative rational probabilities required')
    if sum((p for _, p in law), F(0)) != 1:
        raise ValueError('probabilities must sum to one')
    return (sum((p * abs(x - outcome) for x, p in law), F(0))
            - sum((p * q * abs(x - z) for x, p in law for z, q in law), F(0)) / 2)


def difference(candidate, comparator, outcome, assets):
    if type(assets) is not F or assets <= 0:
        raise ValueError('one common, fixed, strictly positive rational scale required')
    return (crps(candidate, outcome) - crps(comparator, outcome)) / assets


def weighted_effect(cells):
    """Rows: issuer, origin, issuer weight, origin weight, exact d or None.

    A zero-weight cell has zero contribution even if its score is undefined.
    Its undefined score remains visible; missing positive weight blocks full D.
    """
    keys = set()
    for issuer, origin, iw, ow, d in cells:
        if issuer not in ISSUERS or type(origin) is not str or not origin:
            raise ValueError('named issuer and nonempty origin ID required')
        if (issuer, origin) in keys:
            raise ValueError('duplicate issuer/origin ID')
        keys.add((issuer, origin))
        if type(iw) is not F or iw != F(1, 9):
            raise ValueError('each named issuer has weight one ninth')
        if type(ow) is not F or ow < 0:
            raise ValueError('origin weights must be nonnegative rationals')
        if d is not None and type(d) is not F:
            raise ValueError('loss difference must be exact or undefined')
    if {i for i, _, _, _, _ in cells} != set(ISSUERS):
        raise ValueError('the fixed nine-company panel is required')
    for issuer in ISSUERS:
        if sum((ow for i, _, _, ow, _ in cells if i == issuer), F(0)) != 1:
            raise ValueError('origin weights must sum to one for each issuer')
    contribution, covered_weight = F(0), F(0)
    missing_positive, undefined_zero = [], []
    for i, o, iw, ow, d in cells:
        weight = iw * ow
        if d is None:
            (missing_positive if weight > 0 else undefined_zero).append((i, o))
        else:
            contribution += weight * d
            covered_weight += weight
    return {'contribution': contribution, 'covered_weight': covered_weight,
            'conditional_mean': contribution / covered_weight if covered_weight else None,
            'full_D': None if missing_positive else contribution,
            'missing_positive': missing_positive, 'undefined_zero': undefined_zero}


def check():
    passed, refused = [], []

    def case(name, condition):
        assert condition, name
        passed.append(name)

    def reject(name, fn):
        try:
            fn()
        except ValueError:
            refused.append(name)
        else:
            raise AssertionError('accepted ' + name)

    point = lambda x: ((F(x), F(1)),)
    case('negative_means_candidate_lower_loss', difference(point(10), point(12), F(10), F(1)) == -2)
    case('positive_means_candidate_higher_loss', difference(point(8), point(10), F(10), F(1)) == 2)
    law = ((F(-1), F(1, 2)), (F(1), F(1, 2)))
    case('nondegenerate_crps', crps(law, F(0)) == F(1, 2))
    scaled = tuple((x / 3, p) for x, p in law)
    case('common_positive_scale_equivariance', crps(scaled, F(2, 3)) == crps(law, F(2)) / 3
         and difference(law, point(0), F(2), F(3)) == difference(scaled, point(0), F(2, 3), F(1)))
    cells = [('apple', 'o1', F(1, 9), F(1), F(-4))]
    cells += [(i, o, F(1, 9), F(1, 2), F(1)) for i in ISSUERS[1:] for o in ('o1', 'o2')]
    full = weighted_effect(cells)
    case('equal_companies_unequal_origin_counts', full['full_D'] == F(4, 9) and full['covered_weight'] == 1)
    case('equal_cells_changes_objective', sum((r[4] for r in cells), F(0)) / len(cells) == F(12, 17)
         and F(12, 17) != full['full_D'])
    partial = weighted_effect([('apple', 'o1', F(1, 9), F(1), None)] + cells[1:])
    case('positive_weight_undefined_blocks_full_D', partial['full_D'] is None
         and partial['contribution'] == F(8, 9) and partial['covered_weight'] == F(8, 9)
         and partial['conditional_mean'] == 1 and partial['missing_positive'] == [('apple', 'o1')])
    zero = weighted_effect(cells + [('apple', 'excluded', F(1, 9), F(0), None)])
    case('undefined_zero_weight_preserved_without_blocking', zero['full_D'] == full['full_D']
         and zero['covered_weight'] == 1 and zero['undefined_zero'] == [('apple', 'excluded')])
    absent = weighted_effect([(i, o, iw, ow, None) for i, o, iw, ow, _ in cells])
    case('no_scores_means_no_conditional_or_full_estimate', absent['full_D'] is None
         and absent['conditional_mean'] is None and absent['covered_weight'] == 0)
    # Two equiprobable joint worlds, perfectly correlated across the nine firms.
    # This is a complete fictional law, not an estimate of the actual future law.
    worlds = [weighted_effect([(i, 'o', F(1, 9), F(1), F(s)) for i in ISSUERS])['full_D']
              for s in (-1, 1)]
    case('expected_Delta_is_not_realised_D', sum(worlds, F(0)) / 2 == 0 and worlds == [F(-1), F(1)])
    reject('zero_scale', lambda: difference(point(0), point(1), F(0), F(0)))
    reject('negative_scale', lambda: difference(point(0), point(1), F(0), F(-1)))
    reject('unweighted_set', lambda: crps({F(-1), F(1)}, F(0)))
    reject('negative_probability', lambda: crps(((F(0), F(-1)), (F(1), F(2))), F(0)))
    reject('incomplete_probability_mass', lambda: crps(((F(0), F(1, 2)),), F(0)))
    reject('missing_issuer', lambda: weighted_effect(cells[1:]))
    reject('fictional_issuer_alias', lambda: weighted_effect([('i1', *cells[0][1:])] + cells[1:]))
    reject('wrong_issuer_weight', lambda: weighted_effect([(i, o, F(1, 8), ow, d) for i, o, _, ow, d in cells]))
    reject('time_weights_do_not_sum_to_one', lambda: weighted_effect([('apple', 'o1', F(1, 9), F(1, 2), F(-4))] + cells[1:]))
    reject('negative_time_weight_despite_unit_sum', lambda: weighted_effect([
        ('apple', 'o1', F(1, 9), F(-1), F(-4)), ('apple', 'o2', F(1, 9), F(2), F(-4))] + cells[1:]))
    reject('duplicate_issuer_origin_despite_unit_sum', lambda: weighted_effect([
        ('apple', 'o1', F(1, 9), F(1, 2), F(-4))] * 2 + cells[1:]))
    reject('nonrational_time_weight', lambda: weighted_effect([('apple', 'o1', F(1, 9), 1.0, F(-4))] + cells[1:]))
    return {'passed_cases': passed, 'passed_case_count': len(passed),
            'rejected_cases': refused, 'rejected_case_count': len(refused),
            'empirical_observations_used': 0, 'inference_admitted': False}


if __name__ == '__main__':
    import json
    print(json.dumps(check()))
