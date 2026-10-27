"""Exact diagnostic of two changing-family weight conventions; not a fitter."""

from collections import Counter, defaultdict
from fractions import Fraction as F
import json


def canonical(encodings):
    out = {}
    for semantic_id, feature, point in encodings:
        value = (feature, F(point))
        if semantic_id in out and out[semantic_id] != value:
            raise ValueError('conflicting_semantic_id')
        out[semantic_id] = value
    return out


def train_feature_means(origins, later_fit_cutoff):
    # Equal contribution per earlier origin within each feature; no branch-count pooling.
    values = defaultdict(list)
    for origin in origins:
        if not origin['forecast_lock'] < origin['outcome_release'] <= later_fit_cutoff:
            raise ValueError('unreleased_or_invalid_timing')
        groups = defaultdict(list)
        for feature, point in canonical(origin['encodings']).values():
            groups[feature].append(abs(point - origin['outcome']))
        for feature, losses in groups.items():
            values[feature].append(sum(losses, F(0)) / len(losses))
    return {feature: sum(losses, F(0)) / len(losses) for feature, losses in values.items()}


def weights_and_selector(encodings, trained, convention):
    family = canonical(encodings)
    if not family or any(feature not in trained for feature, point in family.values()):
        raise ValueError('law_unavailable_unseen_feature')
    if any(value < 0 for value in trained.values()):
        raise ValueError('invalid_loss')
    counts = Counter(feature for feature, point in family.values())
    scores = {feature: 1 / (1 + trained[feature]) for feature in counts}
    if convention == 'per_member':
        raw = {key: scores[feature] for key, (feature, point) in family.items()}
    elif convention == 'per_feature':
        raw = {key: scores[feature] / counts[feature] for key, (feature, point) in family.items()}
    else:
        raise ValueError('unknown_convention')
    total = sum(raw.values(), F(0))
    weights = {key: value / total for key, value in raw.items()}
    selected = min(family, key=lambda key: (trained[family[key][0]], key))
    return weights, selected


def group_mass(encodings, weights):
    out = defaultdict(F)
    for key, (feature, point) in canonical(encodings).items():
        out[feature] += weights[key]
    return dict(out)


def target_law_weights(encodings, trained):
    """Collapse same target law for E3 scoring while retaining history records."""
    family = canonical(encodings)
    law_feature = {}
    for semantic_id, (feature, point) in family.items():
        if feature not in trained:
            raise ValueError('law_unavailable_unseen_feature')
        if point in law_feature and law_feature[point] != feature:
            raise ValueError('ambiguous_feature_for_same_target_law')
        law_feature[point] = feature
    scores = {point: 1 / (1 + trained[feature]) for point, feature in law_feature.items()}
    total = sum(scores.values(), F(0))
    return {point: score / total for point, score in scores.items()}


def law_crps(weights, outcome):
    support = tuple(weights)
    masses = tuple(weights.values())
    return (sum((mass * abs(point - outcome) for point, mass in zip(support, masses)), F(0))
            - F(1, 2) * sum((mi * mj * abs(xi - xj)
                            for xi, mi in zip(support, masses)
                            for xj, mj in zip(support, masses)), F(0)))


def crps(encodings, weights, outcome):
    points = {key: value[1] for key, value in canonical(encodings).items()}
    return (sum((weights[key] * abs(point - outcome) for key, point in points.items()), F(0))
            - F(1, 2) * sum((weights[i] * weights[j] * abs(points[i] - points[j])
                            for i in points for j in points), F(0)))


def main():
    earlier = [
        {'forecast_lock': 2020, 'outcome_release': 2022, 'outcome': F(0),
         'encodings': [('old-a', 'a', 0), ('old-b', 'b', 2)]},
        {'forecast_lock': 2021, 'outcome_release': 2023, 'outcome': F(2),
         'encodings': [('later-a', 'a', 0), ('later-b', 'b', 2)]},
    ]
    trained = train_feature_means(earlier, 2024)
    # a-new and a-other differ in full history, but project to the same OCF law.
    base = [('a-new', 'a', 0), ('b-new', 'b', 2)]
    duplicate = base + [base[0]]
    expanded = base + [('a-other', 'a', 0)]
    member, selected = weights_and_selector(base, trained, 'per_member')
    member_expanded, _ = weights_and_selector(expanded, trained, 'per_member')
    feature_expanded, repaired_selector = weights_and_selector(expanded, trained, 'per_feature')
    # Splitting the feature category itself still changes its combined mass.
    repartitioned = [('a-new', 'a', 0), ('b-new', 'b', 2), ('a-other', 'a2', 0)]
    repartitioned_trained = dict(trained, a2=trained['a'])
    partition_weights, _ = weights_and_selector(repartitioned, repartitioned_trained, 'per_feature')
    target_base = target_law_weights(base, trained)
    target_expanded = target_law_weights(expanded, trained)
    checks = {
        'eligible_feature_means': trained == {'a': F(1), 'b': F(1)},
        'new_semantic_ids_supported_by_stable_features': set(member) == {'a-new', 'b-new'},
        'syntactic_duplicate_invariance': weights_and_selector(duplicate, trained, 'per_member') == (member, selected),
        'member_normalization_depends_on_distinct_member_count': group_mass(expanded, member_expanded) == {'a': F(2, 3), 'b': F(1, 3)},
        'feature_normalization_preserves_feature_mass': group_mass(expanded, feature_expanded) == {'a': F(1, 2), 'b': F(1, 2)},
        'equal_target_law_support_still_reweighted': crps(base, member, F(2)) == F(1, 2) and crps(expanded, member_expanded, F(2)) == F(8, 9),
        'feature_repair_preserves_law_in_this_case': all(crps(base, member, y) == crps(expanded, feature_expanded, y) for y in (F(0), F(1), F(2), F(3))),
        'feature_partition_remains_a_measure_choice': partition_weights['a-new'] + partition_weights['a-other'] == F(2, 3),
        'target_law_quotient_removes_semantic_multiplicity': target_expanded == target_base == {F(0): F(1, 2), F(2): F(1, 2)},
        'deterministic_fixed_selector': selected == repaired_selector == 'a-new',
        'simplex_validity': all(sum(ws.values(), F(0)) == 1 and all(w >= 0 for w in ws.values()) for ws in (member, member_expanded, feature_expanded)),
    }
    refusals = {}
    cases = {
        'label_not_yet_released': lambda: train_feature_means(earlier, 2022),
        'unseen_current_feature': lambda: weights_and_selector(base + [('c-new', 'c', 3)], trained, 'per_feature'),
        'conflicting_semantic_id': lambda: canonical(base + [('a-new', 'a', 3)]),
        'same_law_conflicting_features': lambda: target_law_weights(base + [('a-other', 'a2', 0)], dict(trained, a2=trained['a'])),
    }
    for name, fn in cases.items():
        try:
            fn()
        except ValueError as exc:
            refusals[name] = str(exc)
        else:
            raise AssertionError(name)
    checks['conflicting_features_for_same_law_refused'] = 'same_law_conflicting_features' in refusals
    assert all(checks.values()), checks
    return {
        'status': 'PASS', 'checks': checks, 'refusals': refusals,
        'base_weights': {k: str(v) for k, v in member.items()},
        'expanded_member_weights': {k: str(v) for k, v in member_expanded.items()},
        'expanded_feature_weights': {k: str(v) for k, v in feature_expanded.items()},
        'target_law_base_weights': {str(k): str(v) for k, v in target_base.items()},
        'target_law_expanded_weights': {str(k): str(v) for k, v in target_expanded.items()},
        'score_at_y2': {'base': str(crps(base, member, F(2))),
                        'expanded_per_member': str(crps(expanded, member_expanded, F(2))),
                        'expanded_per_feature': str(crps(expanded, feature_expanded, F(2)))},
        'fixed_selector': selected, 'company_data_used': False, 'model_adopted': False,
    }


if __name__ == '__main__':
    print(json.dumps(main(), sort_keys=True))
