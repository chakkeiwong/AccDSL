from __future__ import annotations

from fractions import Fraction
from itertools import product
from math import isfinite


def point_crps(points: tuple[Fraction, ...], weights: tuple[Fraction, ...], y: Fraction) -> Fraction:
    if len(points) != len(weights) or not points:
        raise ValueError('law_unavailable')
    if any(w < 0 for w in weights) or sum(weights) != 1:
        raise ValueError('invalid_law_weights')
    return sum(w * abs(x - y) for x, w in zip(points, weights)) - Fraction(1, 2) * sum(
        wi * wj * abs(xi - xj)
        for xi, wi in zip(points, weights)
        for xj, wj in zip(points, weights)
    )


def mixture(laws: dict[str, tuple[Fraction, ...]], weights: dict[str, Fraction]):
    if set(laws) != set(weights) or not laws:
        raise ValueError('law_unavailable')
    if any(w < 0 for w in weights.values()) or sum(weights.values()) != 1:
        raise ValueError('invalid_combination_weights')
    support = sorted({x for law in laws.values() for x in law})
    mass = {x: Fraction(0) for x in support}
    for key, law in laws.items():
        # Each law is a point mass for this exact reference.
        for x in law:
            mass[x] += weights[key] / len(law)
    return tuple(support), tuple(mass[x] for x in support)


def cdf_crps(support: tuple[Fraction, ...], masses: tuple[Fraction, ...], y: Fraction) -> Fraction:
    if len(support) != len(masses) or not support:
        raise ValueError('law_unavailable')
    if any(m < 0 for m in masses) or sum(masses) != 1:
        raise ValueError('invalid_law_weights')
    # Integrate the squared CDF difference on every interval between support points.
    points = sorted(set(support + (y,)))
    out = Fraction(0)
    for left, right in zip(points, points[1:]):
        cdf = sum(m for x, m in zip(support, masses) if x <= left)
        target = Fraction(1) if y <= left else Fraction(0)
        out += (right - left) * (cdf - target) ** 2
    return out


def component_losses(laws, outcomes):
    return {k: tuple(point_crps((x,), (Fraction(1),), y) for y in outcomes) for k, x in laws.items()}


def mean(xs):
    return sum(xs, Fraction(0)) / len(xs)


def fit_grid(laws, outcomes):
    # Exact bounded development grid for two components; this is a fixture, not a production optimizer.
    keys = tuple(sorted(laws))
    if len(keys) != 2:
        raise ValueError('fixture_requires_two_components')
    best = None
    for n in range(0, 11):
        w = Fraction(n, 10)
        ws = {keys[0]: w, keys[1]: 1 - w}
        support, masses = mixture({k: (laws[k],) for k in keys}, ws)
        loss = mean(tuple(cdf_crps(support, masses, y) for y in outcomes))
        candidate = (loss, w, ws)
        if best is None or candidate[:2] < best[:2]:
            best = candidate
    return best


def locked_selector(laws, outcomes):
    losses = component_losses(laws, outcomes)
    # A deterministic lexical tie rule is part of the contract.
    return min(sorted(laws), key=lambda k: (mean(losses[k]), k)), losses


def canonicalize(encodings):
    # Every encoding is (semantic_id, future_point); duplicate semantic IDs are one component.
    out = {}
    for semantic_id, future_point in encodings:
        if semantic_id in out and out[semantic_id] != future_point:
            raise ValueError('inconsistent_semantic_fingerprint')
        out[semantic_id] = future_point
    return out


def require_timing(label_release, cutoff):
    if label_release > cutoff:
        raise ValueError('late_label')


def require_validation_timing(forecast_lock, outcome_release, later_fit_cutoff):
    # The validation label follows its own forecast and is available by the
    # later fit that consumes its score.
    if not forecast_lock < outcome_release <= later_fit_cutoff:
        raise ValueError('validation_outcome_timing')


def main():
    laws = {'a_history_zero': Fraction(0), 'b_history_two': Fraction(2)}
    outcomes = (Fraction(0), Fraction(2))
    fit_loss, fit_weight, fit_weights = fit_grid(laws, outcomes)
    selector, losses = locked_selector(laws, outcomes)
    support, masses = mixture({k: (laws[k],) for k in laws}, fit_weights)
    abs_scores = tuple(point_crps(support, masses, y) for y in outcomes)
    cdf_scores = tuple(cdf_crps(support, masses, y) for y in outcomes)
    split = canonicalize((('a_history_zero', Fraction(0)), ('a_history_zero', Fraction(0)), ('b_history_two', Fraction(2))))
    split_support, split_masses = mixture({k: (x,) for k, x in split.items()}, fit_weights)
    checks = {
        'simplex_sum': sum(fit_weights.values()) == 1,
        'simplex_nonnegative': all(w >= 0 for w in fit_weights.values()),
        'mixture_grid_weight': fit_weight == Fraction(1, 2),
        'selector_tie_lexical': selector == 'a_history_zero',
        'crps_independent_agreement': abs_scores == cdf_scores,
        'semantic_duplicate_conserves_law': (split_support, split_masses) == (support, masses),
        'released_validation_precedes_later_fit': require_validation_timing(2022, 2023, 2024) is None,
    }
    refusals = {}
    for name, fn in {
        'negative_weight': lambda: mixture({'a': (Fraction(0),), 'b': (Fraction(2),)}, {'a': Fraction(-1, 10), 'b': Fraction(11, 10)}),
        'missing_component': lambda: mixture({'a': (Fraction(0),), 'b': (Fraction(2),)}, {'a': Fraction(1)}),
        'late_label': lambda: require_timing(2026, 2025),
        'validation_outcome_not_yet_released': lambda: require_validation_timing(2022, 2024, 2023),
        'invalid_law': lambda: point_crps((Fraction(0), Fraction(2)), (Fraction(1, 2), Fraction(1, 4)), Fraction(0)),
    }.items():
        try:
            fn()
        except ValueError:
            refusals[name] = True
        else:
            refusals[name] = False
    assert all(checks.values()), checks
    assert all(refusals.values()), refusals
    return {'status':'PASS','checks':checks,'refusals':refusals,'fit_weight':str(fit_weight),'fit_loss':str(fit_loss),'selector':selector,'mixture_support':[str(x) for x in support],'mixture_masses':[str(x) for x in masses]}

if __name__ == '__main__':
    import json
    print(json.dumps(main(), sort_keys=True))
