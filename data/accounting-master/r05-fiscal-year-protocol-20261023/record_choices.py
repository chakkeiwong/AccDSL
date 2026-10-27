"""One-time documentary choice/source record; no forecast or source acquisition."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path

U = Path(__file__).resolve().parent
R = U.parents[2]


def bound(p):
    return {'path': str(p.relative_to(R)), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}


def main():
    assert os.environ.get('CUDA_VISIBLE_DEVICES') == '-1'
    assert (U/'protection.json').is_file()
    assert not any((U/name).exists() for name in ('choice.json', 'calendar-sources.json'))
    oldpath = R/'data/accounting-master/r05-repeated-origins-20261023/choice.json'
    old = json.loads(oldpath.read_text())
    answers = [
        {'question': 'For the first E3 comparison on the named companies, what operating-cash-flow forecast should the protocol target?',
         'answer': 'Next complete fiscal year, using a named information cutoff before that year starts (recommended)'},
        {'question': 'How should the named companies contribute to the main E3 result? The existing design scales each company’s losses by its as-of total assets before aggregation.',
         'answer': 'Equal contribution per company (recommended)'}]
    choice = {
        'schema': 'accdsl.documentary.e3_fiscal_year_equal_issuers.v1',
        'authority': 'Explicit user answers, 23 October 2026 Asia/Hong_Kong',
        'recorded_utc': datetime.now(timezone.utc).isoformat(),
        'answers_verbatim': answers, 'predecessor_choice': bound(oldpath),
        'selected_design': old['selected_design'], 'active_panel': old['active_panel'],
        'named_companies': old['named_companies'], 'frozen_e3': old['frozen_e3'],
        'forecast_task': {'target': 'operating_cash_flow', 'interval_rule': 'next_complete_fiscal_year',
                          'cutoff_rule': 'named_information_cutoff_strictly_before_target_start',
                          'exact_cutoff_instants': None, 'origin_grouping': None},
        'issuer_weights': {c['issuer_id']: '1/9' for c in old['named_companies']},
        'within_issuer_origin_weights': None,
        'population_status': {'issuer_membership': 'selected_fixed_panel',
                              'future_origin_law': None, 'regime_or_stability': None,
                              'deployment_population_admitted': False},
        'unresolved': ['exact_future_calendar_and_cutoff_evidence', 'origin_grouping_and_joint_law',
                       'within_issuer_time_weights', 'forecast_issue_deadline', 'refit_and_tuning_policy',
                       'service_failure_policy', 'financial_scope_and_target_mapping',
                       'improvement_margin', 'confidence_level', 'inference_procedure', 'sample_size'],
        'historical_vintage_admissions': 0, 'empirical_execution': False,
        'future_issuer_generalization_selected': False,
        'historical_null_records_preserved': True}
    coveragepath = R/'data/financial-report-benchmark/coverage.json'
    coverage = json.loads(coveragepath.read_text())
    ranges = {'apple': [(9,9), (194,194), (598,599)],
              'caterpillar': [(18,18), (3356,3359)], 'jpmorgan': [(12381,12385)],
              'henkel': [(26735,26740)], 'hsbc': [(21850,21854)],
              'munich_re': [(24022,24030)], 'saic_motor': [(4207,4210)],
              'ping_an': [(9347,9349)], 'midea': [(245,245), (8551,8553)]}
    rows = []
    for index, row in enumerate(coverage['rows']):
        if row['period_year'] != 2025 or row['report_class'] != 'annual':
            continue
        issuer = row['issuer_id']
        textpath, original = R/row['extracted_text_path'], R/row['local_path']
        # LF lines match rg -n; form feeds are retained inside a line.
        lines = textpath.read_text().split('\n')
        anchors = [{'start_line': a, 'end_line': b, 'quote': '\n'.join(lines[a-1:b])}
                   for a,b in ranges[issuer]]
        assert bound(original)['sha256'] == row['sha256']
        rows.append({'issuer_id': issuer, 'document_id': row['document_id'],
                     'coverage_pointer': f'/rows/{index}', 'source_url': row['source_url'],
                     'original': bound(original), 'text': bound(textpath), 'anchors': anchors,
                     'calendar_observation': '52_or_53_weeks_ending_last_saturday_september' if issuer == 'apple' else 'calendar_year_in_2025_report',
                     'reported_end': '2025-09-27' if issuer == 'apple' else '2025-12-31',
                     'start_interpretation': '2024-09-29 derived from stated 52-week span' if issuer == 'apple' else '2025-01-01; explicit range/policy or ordinary full-year reading of statement header',
                     'future_calendar_admitted': False, 'selected_byte_availability_admitted': False,
                     'cash_flow_mapping_admitted': False})
    assert len(rows) == 9
    sources = {'scope': 'calendar passages only, not whole-report or accounting validation',
               'line_convention': 'one-based LF-delimited lines; preserve form feeds',
               'coverage': bound(coveragepath), 'rows': rows,
               'reading_repair': 'Initial splitlines excerpts used form-feed-sensitive numbering. Re-read all affected anchors using LF lines before recording; no source bytes changed.'}
    for name,value in [('choice.json', choice), ('calendar-sources.json', sources)]:
        with (U/name).open('x') as f:
            json.dump(value, f, ensure_ascii=False, indent=2)
            f.write('\n')
    print(json.dumps({'recorded_answers': len(answers), 'issuer_weights': len(choice['issuer_weights']),
                      'calendar_sources': len(rows), 'source_anchors': sum(len(r['anchors']) for r in rows)}))


if __name__ == '__main__':
    main()
