"""Authored fictional examples; values and outcomes predeclared in contract.md."""
from copy import deepcopy

EARLY = ['2030-12-01T00:00:00+00:00'] * 2
CUTOFF = ['2030-12-15T00:00:00+00:00'] * 2
CREATED = ['2030-12-16T00:00:00+00:00'] * 2
LOCK = ['2030-12-17T00:00:00+00:00'] * 2
DEADLINE = ['2030-12-31T00:00:00+00:00'] * 2
RELEASE = ['2032-02-01T00:00:00+00:00'] * 2
LATE = ['2032-02-02T00:00:00+00:00'] * 2


def examples():
    rows = []
    for name, weight in zip('ABCDEF', ('1/4', '1/4', '1/8', '1/8', '1/8', '1/8')):
        rows.append({'id': name, 'weight': weight, 'target_id': 'fictional-' + name,
                     'predictors': [deepcopy(EARLY)], 'training_labels': [deepcopy(EARLY)],
                     'cutoff': deepcopy(CUTOFF), 'created': deepcopy(CREATED),
                     'lock': deepcopy(LOCK), 'deadline': deepcopy(DEADLINE),
                     'outcome_release': deepcopy(RELEASE),
                     'exposure': 'supplied_review_supports_unexposed',
                     'candidate': {'id': 'candidate-v1', 'kind': 'point', 'value': '10', 'unresolved_mass': '0'},
                     'comparator': {'id': 'comparator-v1', 'kind': 'point', 'value': '11', 'unresolved_mass': '0'},
                     'outcome': {'status': 'admitted_first_release', 'version': 'first-v1', 'value': '10'},
                     'scale': {'status': 'admitted', 'value': '10', 'available': deepcopy(EARLY)}})
    rows[1]['candidate'] = {'id': 'candidate-v1', 'kind': 'incomplete_law', 'unresolved_mass': '1/4', 'value': None}
    rows[2]['candidate'] = {'id': 'candidate-v1', 'kind': 'numerical_failure', 'unresolved_mass': None, 'value': None}
    rows[2]['outcome'] = {'status': 'not_observed', 'version': None, 'value': None}
    rows[2]['outcome_release'] = None
    rows[3]['scale'] = {'status': 'missing', 'value': None, 'available': None}
    rows[4]['lock'] = deepcopy(LATE)
    rows[5]['predictors'] = [None]
    return {'fictional_only': True, 'expected_ids': list('ABCDEF'),
            'locked_primary_version': 'first-v1', 'rows': rows}
