"""Finite documentary examples only; not a production forecast validator."""
from datetime import datetime
from fractions import Fraction as F
import json


def bounds(value):
    if value is None:
        return None
    assert isinstance(value, list) and len(value) == 2
    out = tuple(datetime.fromisoformat(v) for v in value)
    assert all(t.utcoffset() is not None for t in out)
    assert out[0] <= out[1]
    return out


def ordering(left, right, strict=False):
    a, b = bounds(left), bounds(right)
    if a is None or b is None:
        return 'unverified'
    if a[1] < b[0] if strict else a[1] <= b[0]:
        return 'supported'
    if a[0] >= b[1] if strict else a[0] > b[1]:
        return 'contradicted'
    return 'unverified'


def point_loss(arm, outcome):
    if arm['kind'] != 'point':
        assert arm['value'] is None
        return None
    assert F(arm['unresolved_mass']) == 0
    value = F(arm['value'])
    if outcome['value'] is None:
        return None
    return abs(value - F(outcome['value']))


def assess(row):
    assert row['candidate']['id'] == 'candidate-v1'
    assert row['comparator']['id'] == 'comparator-v1'
    time = {f'predictor_{i}': ordering(v, row['cutoff']) for i, v in enumerate(row['predictors'])}
    time.update({f'training_label_{i}': ordering(v, row['cutoff']) for i, v in enumerate(row['training_labels'])})
    time.update({'cutoff_creation': ordering(row['cutoff'], row['created']),
                 'creation_lock': ordering(row['created'], row['lock']),
                 'issue_deadline': ordering(row['lock'], row['deadline']),
                 'lock_release': ordering(row['lock'], row['outcome_release'], strict=True)})
    reasons = []
    for name in ('candidate', 'comparator'):
        if row[name]['kind'] != 'point':
            reasons.append(name + '_' + row[name]['kind'])
    if row['outcome']['status'] != 'admitted_first_release':
        assert row['outcome']['value'] is None
        reasons.append('outcome_' + row['outcome']['status'])
    else:
        assert row['outcome']['value'] is not None
    lc, lb = point_loss(row['candidate'], row['outcome']), point_loss(row['comparator'], row['outcome'])
    raw = lc - lb if lc is not None and lb is not None and not reasons else None
    scale = row['scale']
    if scale['status'] == 'admitted':
        assert F(scale['value']) > 0
        st = ordering(scale['available'], row['cutoff'])
        scale_reason = [] if st == 'supported' else ['scale_asof_' + st]
    else:
        assert scale['value'] is None
        scale_reason = ['scale_' + scale['status']]
    scaled = raw / F(scale['value']) if raw is not None and not scale_reason else None
    chronology_reasons = ['timing_' + k + '_' + v for k, v in time.items() if v != 'supported']
    if row['exposure'] != 'supplied_review_supports_unexposed':
        chronology_reasons.append('exposure_' + row['exposure'])
    prospective = scaled if not chronology_reasons else None
    return {'id': row['id'], 'raw_candidate_loss': None if lc is None else str(lc),
            'raw_comparator_loss': None if lb is None else str(lb),
            'raw': None if raw is None else str(raw), 'scaled': None if scaled is None else str(scaled),
            'prospective_screened_scaled': None if prospective is None else str(prospective),
            'raw_reasons': reasons, 'scaled_reasons': reasons + scale_reason,
            'prospective_reasons': reasons + scale_reason + chronology_reasons,
            'time_predicates': time,
            'actual_empirical_admission': False}


def summarize(packet):
    rows = packet['rows']
    assert packet['fictional_only'] is True
    assert len(rows) == len(packet['expected_ids']) == len({r['id'] for r in rows})
    assert {r['id'] for r in rows} == set(packet['expected_ids'])
    assert all(F(r['weight']) >= 0 for r in rows) and sum(F(r['weight']) for r in rows) == 1
    for row in rows:
        if row['outcome']['status'] == 'admitted_first_release':
            assert row['outcome']['version'] == packet['locked_primary_version']
    assessed = [assess(r) for r in rows]
    summaries = {}
    for metric in ('raw', 'scaled', 'prospective_screened_scaled'):
        pairs = [(r, a) for r, a in zip(rows, assessed) if a[metric] is not None]
        mass = sum((F(r['weight']) for r, a in pairs), F(0))
        contribution = sum((F(r['weight']) * F(a[metric]) for r, a in pairs), F(0))
        complete = all(a[metric] is not None or F(r['weight']) == 0 for r, a in zip(rows, assessed))
        summaries[metric] = {'eligible': len(rows), 'scorable': len(pairs),
            'ids': [r['id'] for r, a in pairs], 'weight': str(mass),
            'observed_contribution': str(contribution),
            'conditional_mean': str(contribution / mass) if mass else None,
            'full_effect': str(contribution) if complete else None}
    return {'rows': assessed, 'summaries': summaries, 'empirical_admission': False}


def append_event(store, event):
    encoded = json.dumps(event['payload'], sort_keys=True, separators=(',', ':'), allow_nan=False)
    key = event['event_id']
    if key in store:
        assert store[key] == encoded, 'conflicting retry'
        return 'identical_retry'
    store[key] = encoded
    return 'appended'
