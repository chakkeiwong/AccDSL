"""Check finite fictional protocol cases; --record is a one-time action."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import json
import os
from pathlib import Path
import sys
import time
from examples import examples
from reference import append_event, ordering, summarize

U = Path(__file__).resolve().parent
R = U.parents[2]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_text())
rel = lambda p: str(p.relative_to(R))


def moment(day, hour=0):
    return f'2030-12-{day:02}T{hour:02}:00:00+00:00'


def interval(day1, day2=None):
    return [moment(day1), moment(day1 if day2 is None else day2)]


def reject(call):
    try:
        call()
    except (AssertionError, ValueError, TypeError):
        return True
    raise AssertionError('invalid control accepted')


def calculate():
    timing = [
        ('inclusive-before', interval(1), interval(2), False, 'supported'),
        ('inclusive-equal', interval(2), interval(2), False, 'supported'),
        ('inclusive-safe-bounds', interval(1, 2), interval(2, 3), False, 'supported'),
        ('inclusive-definitely-late', interval(3, 4), interval(1, 2), False, 'contradicted'),
        ('inclusive-overlap', interval(1, 3), interval(2), False, 'unverified'),
        ('inclusive-unknown', None, interval(2), False, 'unverified'),
        ('strict-before', interval(1), interval(2), True, 'supported'),
        ('strict-equal', interval(2), interval(2), True, 'contradicted'),
        ('strict-late', interval(3), interval(2), True, 'contradicted'),
        ('strict-overlap', interval(1, 3), interval(2, 4), True, 'unverified'),
        ('strict-touch', interval(1, 2), interval(2, 3), True, 'unverified'),
        ('strict-unknown', interval(1), None, True, 'unverified')]
    time_results = []
    for name, left, right, strict, expected in timing:
        actual = ordering(left, right, strict)
        assert actual == expected, name
        time_results.append({'id': name, 'result': actual})
    invalid_bounds = [interval(3, 1), [moment(1)], ['2030-12-01', '2030-12-02'], ['invalid', moment(2)]]
    for value in invalid_bounds:
        reject(lambda: ordering(value, interval(2)))

    packet = examples()
    calculated = summarize(packet)
    expected = {
        'raw': {'eligible': 6, 'scorable': 4, 'ids': list('ADEF'), 'weight': '5/8',
                'observed_contribution': '-5/8', 'conditional_mean': '-1', 'full_effect': None},
        'scaled': {'eligible': 6, 'scorable': 3, 'ids': list('AEF'), 'weight': '1/2',
                   'observed_contribution': '-1/20', 'conditional_mean': '-1/10', 'full_effect': None},
        'prospective_screened_scaled': {'eligible': 6, 'scorable': 1, 'ids': ['A'], 'weight': '1/4',
                   'observed_contribution': '-1/40', 'conditional_mean': '-1/10', 'full_effect': None}}
    assert calculated['summaries'] == expected
    assert set(calculated['rows'][2]['raw_reasons']) == {'candidate_numerical_failure', 'outcome_not_observed'}
    assert calculated['rows'][4]['time_predicates']['lock_release'] == 'contradicted'
    assert calculated['rows'][5]['time_predicates']['predictor_0'] == 'unverified'
    assert calculated['rows'][4]['raw'] == calculated['rows'][5]['raw'] == '-1'
    zero = deepcopy(packet)
    for row in zero['rows']:
        row['candidate'] = {'id': 'candidate-v1', 'kind': 'not_attempted', 'value': None, 'unresolved_mass': None}
    zero_results = summarize(zero)['summaries']
    assert all(v['scorable'] == 0 and v['conditional_mean'] is None and v['full_effect'] is None for v in zero_results.values())
    zero_weight = deepcopy(packet)
    for row in zero_weight['rows']:
        row['weight'] = '1' if row['id'] == 'A' else '0'
    zero_weight_results = summarize(zero_weight)['summaries']
    assert zero_weight_results['raw']['full_effect'] == '-1'
    assert zero_weight_results['prospective_screened_scaled']['full_effect'] == '-1/10'
    assert all(v['eligible'] == 6 for v in zero_weight_results.values())

    corruptions = []
    def refusal(name, change):
        altered = deepcopy(packet)
        change(altered)
        reject(lambda: summarize(altered))
        corruptions.append(name)
    refusal('omitted_eligible_row', lambda p: p['rows'].pop())
    refusal('extra_eligible_row', lambda p: p['rows'].append(deepcopy(p['rows'][0])))
    refusal('duplicate_eligible_id', lambda p: p['rows'][1].update(id='A'))
    refusal('incomplete_law_zero_fill', lambda p: p['rows'][1]['candidate'].update(value='0'))
    refusal('incomplete_law_relabelled_point', lambda p: p['rows'][1]['candidate'].update(kind='point', value='10'))
    refusal('later_outcome_as_primary', lambda p: p['rows'][0]['outcome'].update(version='restatement-v2', value='12'))
    refusal('nonpositive_scale_admitted', lambda p: p['rows'][0]['scale'].update(value='0'))
    refusal('comparator_changed', lambda p: p['rows'][0]['comparator'].update(id='chosen-after-outcome'))
    refusal('missing_outcome_zero_fill', lambda p: p['rows'][2]['outcome'].update(value='0'))
    refusal('lost_original_weight', lambda p: p['rows'][0].update(weight='1/2'))
    first, restated = F(10), F(12)
    primary = abs(F(10) - first) - abs(F(11) - first)
    sensitivity = abs(F(10) - restated) - abs(F(11) - restated)
    assert (primary, sensitivity) == (F(-1), F(1))
    events = {}
    e = {'event_id': 'attempt-A-score-v1', 'payload': calculated['rows'][0]}
    assert append_event(events, e) == 'appended'
    assert append_event(events, deepcopy(e)) == 'identical_retry'
    assert len(events) == 1
    changed = deepcopy(e)
    changed['payload']['raw'] = '0'
    reject(lambda: append_event(events, changed))
    assert len(events) == 1
    return {'timing': time_results, 'invalid_time_bounds_rejected': 4,
            'six_cell_evaluation': calculated, 'empty_coverage': zero_results,
            'zero_weight_missing_cells': zero_weight_results, 'refused_corruptions': corruptions,
            'first_release': {'primary': str(primary), 'sensitivity': str(sensitivity), 'primary_unchanged': True},
            'retry': {'unique_events': 1, 'identical_retry': 'no_change', 'conflicting_retry': 'rejected'},
            'counts': {'timing_cases': 12, 'invalid_bounds': 4, 'eligible_cells': 6,
                       'coverage_tables': 3, 'corruptions_rejected': 10,
                       'boundary_aggregations': 2, 'retry_cases': 3},
            'actual_empirical_admission': False, 'weights_selected': False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--record', action='store_true')
    args = parser.parse_args()
    assert os.environ.get('CUDA_VISIBLE_DEVICES') == '-1'
    out, manifest = U / 'calculation.json', U / 'calculation-manifest.json'
    if args.record:
        assert not out.exists() and not manifest.exists()
    started, t0 = datetime.now(timezone.utc).isoformat(), time.monotonic()
    result = calculate()
    elapsed = time.monotonic() - t0
    if args.record:
        with out.open('x') as f:
            json.dump(result, f, indent=2)
            f.write('\n')
        value = {'git_commit': load(U / 'protection.json')['head'], 'environment': sys.executable,
            'command': 'env CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B ' + rel(Path(__file__).resolve()) + ' --record',
            'cpu_gpu': 'CPU only; GPU devices intentionally hidden; standard library only',
            'seeds': 'N/A deterministic authored examples', 'started_utc': started, 'wall_seconds': elapsed,
            'data_version': 'Fictional point laws, supplied evidence statuses and exact weights in contract.md/examples.py',
            'plan': 'docs/plans/accounting-r05-forecast-accountability-20261023.md',
            'result': rel(U / 'result.md'), 'output': rel(out),
            'bindings': {rel(p): sha(p) for p in [U / 'contract.md', U / 'examples.py', U / 'reference.py', Path(__file__).resolve(), out]}}
        with manifest.open('x') as f:
            json.dump(value, f, indent=2)
            f.write('\n')
    elif out.exists():
        assert result == load(out)
    print(json.dumps({'status': 'recorded' if args.record else 'read-only examples passed', **result['counts']}))


if __name__ == '__main__':
    main()
