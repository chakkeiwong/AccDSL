"""One-time conditional upper bounds from retained annual label inventory."""
import hashlib
import json
import os
from pathlib import Path
from reference import ISSUERS, opportunities

U = Path(__file__).resolve().parent
R = U.parents[2]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_text())
bind = lambda p: {'path': str(p.relative_to(R)), 'sha256': sha(p)}


def compute():
    coverage = R / 'data/financial-report-benchmark/coverage.json'
    vintage = R / 'data/accounting-master/r05-vintage-admission-20261018/reconciliation.json'
    calendars = R / 'data/accounting-master/r05-fiscal-year-protocol-20261023/calendar-sources.json'
    rows = load(coverage)['rows']
    old = load(vintage)['rows']
    panel = []
    for issuer in ISSUERS:
        annuals = sorted([(n, r) for n, r in enumerate(rows)
                          if r['issuer_id'] == issuer and r['report_class'] == 'annual'],
                         key=lambda pair: pair[1]['period_year'])
        years = tuple(r['period_year'] for _, r in annuals)
        assert years == tuple(range(2018, 2026))
        assert all(sha(R / r['local_path']) == r['sha256'] for _, r in annuals)
        admitted = [r for r in old if r['issuer_id'] == issuer and r['as_of_admission']]
        assert not admitted
        panel.append({'issuer_id': issuer, 'annual_label_years': list(years),
            'coverage_pointers': [f'/rows/{n}' for n, _ in annuals],
            'document_ids': [r['document_id'] for _, r in annuals],
            'actual_admitted_as_of_reports': 0,
            'interpretation': 'conditional same-issuer upper bounds; no release/calendar/OCF admission'})
    grid = []
    for r in (1, 3, 5):
        for v in (0, 2):
            detail = opportunities(tuple(range(2018, 2026)), r, v)
            outer = [x['target_label'] for x in detail if x['possible_outer']]
            grid.append({'minimum_training_labels': r, 'minimum_inner_validation_origins': v,
                         'possible_outer_year_labels_per_issuer': outer,
                         'possible_outer_count_per_issuer': len(outer),
                         'all_issuers_cell_count_upper_bound': 9 * len(outer),
                         'independent_replication_count': None, 'detail': detail})
    return {'scope': 'optimistic same-issuer annual refit feasibility on 2018–2025 label grid',
        'assumptions': ['adjacent ordinary full fiscal years', 'strict pre-start cutoffs',
                        'all y-2 and older labels instantly usable', 'same-issuer training and validation'],
        'not_selected_defaults': {'training_label_minima': [1, 3, 5], 'validation_origin_minima': [0, 2]},
        'sources': [bind(p) for p in (coverage, vintage, calendars)],
        'panel': panel, 'conditional_grid': grid, 'annual_report_count': 72,
        'actual_as_of_admissions': 0, 'actual_scored_forecasts': 0,
        'empirical_execution': False, 'inference_admitted': False}


def main():
    assert os.environ.get('CUDA_VISIBLE_DEVICES') == '-1'
    assert not (U / 'feasibility.json').exists()
    value = compute()
    with (U / 'feasibility.json').open('x') as f:
        json.dump(value, f, indent=2)
        f.write('\n')
    print(json.dumps({'annual_reports': 72, 'issuers': 9, 'conditional_designs': 6,
                      'actual_as_of_admissions': 0, 'actual_forecasts': 0}))


if __name__ == '__main__':
    main()
