"""Conditional annual-label feasibility; no model or real data admission."""
from datetime import datetime, timezone

ISSUERS = ('apple', 'caterpillar', 'jpmorgan', 'henkel', 'hsbc',
           'munich_re', 'saic_motor', 'ping_an', 'midea')


def opportunities(years, training_labels, validation_origins):
    """Optimistic same-issuer bound under adjacent ordinary full fiscal years.

    At a strict pre-start cutoff for y, y-1 is unfinished. Even y-2 and older
    are only potential labels here: actual release/mapping may exclude them.
    Each inner origin must have its own training_labels older labels, and its
    outcome must also be complete by the outer cutoff.
    """
    if (type(years) is not tuple or not years or any(type(y) is not int for y in years)
            or years != tuple(range(years[0], years[-1] + 1))):
        raise ValueError('unique consecutive annual label grid required')
    if type(training_labels) is not int or training_labels < 1:
        raise ValueError('positive integer training-label minimum required')
    if type(validation_origins) is not int or validation_origins < 0:
        raise ValueError('nonnegative integer validation-origin count required')
    rows = []
    for y in years:
        train = [h for h in years if h <= y - 2]
        inner = [h for h in years if h <= y - 2
                 and len([k for k in years if k <= h - 2]) >= training_labels]
        rows.append({'target_label': y, 'potential_training_labels': train,
                     'potential_inner_origins': inner,
                     'possible_outer': len(train) >= training_labels and len(inner) >= validation_origins})
    return rows


def label_eligibility(period_end, available_lower, available_upper, cutoff, mapped):
    """Instants denote half-open period ends; unknown availability is preserved."""
    values = (period_end, cutoff) + tuple(v for v in (available_lower, available_upper) if v is not None)
    if any(type(v) is not datetime or v.tzinfo is None or v.utcoffset() is None for v in values):
        raise ValueError('timezone-aware instants required')
    if type(mapped) is not bool:
        raise ValueError('mapping status must be explicit')
    if (available_lower is None) != (available_upper is None):
        raise ValueError('availability needs both bounds or neither')
    if available_lower is not None and available_lower > available_upper:
        raise ValueError('inverted availability bounds')
    if period_end > cutoff:
        return 'unfinished'
    if available_lower is None:
        return 'availability_unverified'
    if available_lower > cutoff:
        return 'late'
    if available_upper > cutoff:
        return 'availability_unverified'
    if not mapped:
        return 'mapping_unverified'
    return 'eligible_under_supplied_evidence'


def common_start_cohorts(outer_labels):
    """Conditional unchanged calendars: Apple label y starts in y-1."""
    if set(outer_labels) != set(ISSUERS):
        raise ValueError('fixed named panel required')
    cohorts = [{y - (i == 'apple') for y in outer_labels[i]} for i in ISSUERS]
    return sorted(set.intersection(*cohorts))


def check():
    passed, refused = [], []

    def case(name, value):
        assert value, name
        passed.append(name)

    def reject(name, fn):
        try:
            fn()
        except ValueError:
            refused.append(name)
        else:
            raise AssertionError('accepted ' + name)

    years = tuple(range(2018, 2026))
    expected = {(1, 0): [2020, 2021, 2022, 2023, 2024, 2025],
                (3, 0): [2022, 2023, 2024, 2025], (5, 0): [2024, 2025],
                (1, 2): [2023, 2024, 2025], (3, 2): [2025], (5, 2): []}
    for (r, v), wanted in expected.items():
        rows = opportunities(years, r, v)
        case(f'upper_bound_r{r}_v{v}', [x['target_label'] for x in rows if x['possible_outer']] == wanted)
    row = opportunities(years, 3, 2)[-1]
    case('nested_labels_are_release_ordered', row['potential_training_labels'] == list(range(2018, 2024))
         and row['potential_inner_origins'] == [2022, 2023])
    case('no_adjacent_preceding_label', all(y['target_label'] - 1 not in y['potential_training_labels']
         for y in opportunities(years, 1, 0)))
    case('start_year_grouping_can_remove_only_common_outer',
         common_start_cohorts({i: [2025] for i in ISSUERS}) == [])
    case('two_labels_supply_one_complete_start_year_cohort',
         common_start_cohorts({i: [2024, 2025] for i in ISSUERS}) == [2024])
    t = lambda s: datetime.fromisoformat(s).replace(tzinfo=timezone.utc)
    cutoff = t('2025-12-31T12:00:00')
    end = t('2025-01-01T00:00:00')
    case('unfinished_label_even_with_early_announcement', label_eligibility(t('2026-01-01T00:00:00'),
         t('2025-12-01T00:00:00'), t('2025-12-01T00:00:00'), cutoff, True) == 'unfinished')
    case('complete_but_late', label_eligibility(end, t('2026-02-01T00:00:00'),
         t('2026-02-01T00:00:00'), cutoff, True) == 'late')
    case('unknown_byte_time', label_eligibility(end, None, None, cutoff, True) == 'availability_unverified')
    case('bounds_straddle_cutoff', label_eligibility(end, t('2025-12-31T00:00:00'),
         t('2026-01-01T00:00:00'), cutoff, True) == 'availability_unverified')
    case('known_time_unknown_mapping', label_eligibility(end, end, end, cutoff, False) == 'mapping_unverified')
    case('availability_equal_cutoff_allowed', label_eligibility(end, cutoff, cutoff, cutoff, True)
         == 'eligible_under_supplied_evidence')
    reject('duplicate_year_label', lambda: opportunities((2018, 2018), 1, 0))
    reject('missing_calendar_year', lambda: opportunities((2018, 2020), 1, 0))
    reject('zero_training_minimum', lambda: opportunities(years, 0, 0))
    reject('negative_validation_count', lambda: opportunities(years, 1, -1))
    reject('naive_cutoff', lambda: label_eligibility(end, end, end, datetime(2025, 12, 31), True))
    reject('inverted_time_bounds', lambda: label_eligibility(end, cutoff, end, cutoff, True))
    return {'passed_cases': passed, 'passed_case_count': len(passed), 'rejected_cases': refused,
            'rejected_case_count': len(refused), 'empirical_observations_used': 0,
            'window_selected': False, 'inference_admitted': False}


if __name__ == '__main__':
    import json
    print(json.dumps(check()))
