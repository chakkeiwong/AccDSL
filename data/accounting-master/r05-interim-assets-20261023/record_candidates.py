"""Record inspected source quantities, without selecting an as-of value."""
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path

U = Path(__file__).resolve().parent
R = U.parents[2]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
bind = lambda p: {'path': str(p.relative_to(R)), 'sha256': sha(p)}

# Values and spans were inspected in coverage-selected texts before recording.
SPECS = {
    'apple': ('331495', 1000000, '2025-06-28', 'USD proposed from dollar display and issuer context', [(339,345),(381,388)],
              'First column is June 2025; interim financial statements are unaudited.'),
    'caterpillar': ('93722', 1000000, '2025-09-30', 'USD proposed from dollar display and issuer context', [(390,398),(439,446)],
                    'Use consolidated financial position, not reportable segment or supplemental industry columns.'),
    'jpmorgan': ('4560205', 1000000, '2025-09-30', 'USD proposed from dollar display and issuer context', [(5099,5104),(5117,5121)],
                 'Consolidated balance sheet, not period-average assets, managed assets or segment/VIE subtotals.'),
    'henkel': ('32791', 1000000, '2025-06-30', 'EUR', [(1174,1178),(1198,1205)],
               'Current period is third amount column; two older periods and percentages precede it. Purchase-price allocation revisions affect comparatives.'),
    'hsbc': ('3214371', 1000000, '2025-06-30', 'USD', [(15,18),(6309,6313),(6326,6329)],
             'Use consolidated balance sheet; regional assets and assets under management are different quantities.'),
    'munich_re': ('275688', 1000000, '2025-06-30', 'EUR', [(789,798),(827,833)],
                  'Damaged text separators resolved by actual image reading of physical page14/printed12; comparative adjusted under IAS8.'),
    'saic_motor': ('925657233746.15', 1, '2025-06-30', 'CNY', [(1442,1447),(1497,1500)],
                   'Consolidated assets in yuan; separate parent statement is not the group.'),
    'ping_an': ('13509559', 1000000, '2025-06-30', 'CNY', [(5186,5194),(5223,5225)],
                'Unaudited consolidated statement; investment assets and parent assets differ.'),
    'midea': ('638033509', 1000, '2025-06-30', 'CNY', [(5872,5879),(5908,5911)],
              'Four amount columns: group2025/group2024/parent2025/parent2024; parent2025 is318666285 thousand CNY.')
}

def main():
    assert os.environ['CUDA_VISIBLE_DEVICES'] == '-1'
    target = U / 'candidates.json'
    assert not target.exists()
    timing_path = R / 'data/accounting-master/r05-source-timing-feasibility-20261023/matrix.json'
    coverage_path = R / 'data/financial-report-benchmark/coverage.json'
    timing = json.loads(timing_path.read_text())
    coverage = {r['document_id']: r for r in json.loads(coverage_path.read_text())['rows']}
    rows = []
    for index, row in enumerate(timing['rows']):
        if row['input_candidate_kind'] != 'latest_interim':
            continue
        source = coverage[row['document_id']]
        assert source['local_path'] == row['selected']['path']
        assert sha(R / source['local_path']) == source['sha256'] == row['selected']['sha256']
        amount, multiplier, date, currency, spans, caveat = SPECS[row['issuer_id']]
        text = R / source['extracted_text_path']
        lines = text.read_text().split('\n')
        rows.append({'issuer_id': row['issuer_id'], 'document_id': row['document_id'],
            'original': bind(R / source['local_path']), 'text': bind(text),
            'source_url': source['source_url'], 'coverage_standard_family': source['standard_family'],
            'reporting_basis_detail': 'Interim basis/transition paragraph not separately adjudicated in this scale inquiry',
            'reported_total_assets': amount, 'unit_multiplier': multiplier,
            'amount_in_currency_units': str(Fraction(amount) * multiplier),
            'currency': currency, 'reporting_date': date, 'scope': 'consolidated group as reported',
            'measurement_precision': 'reported display precision; underlying economic precision unknown',
            'anchors': [{'start_line': a, 'end_line': b, 'quote': '\n'.join(lines[a-1:b])} for a,b in spans],
            'caveat': caveat, 'timing_matrix_pointer': f'/rows/{index}', 'date_roles': row['date_roles'],
            'conditional_cutoff_date': row['illustrative_cutoff_date'],
            'latest_retained_not_latest_public_claim': True,
            'selected_byte_available_at': None, 'selected_for_actual_cutoff': False, 'as_of_admission': False})
    data = {'scope': 'Nine latest retained interim scale candidates; not a complete public-source search',
            'timing_matrix': bind(timing_path), 'coverage': bind(coverage_path), 'rows': rows,
            'actually_viewed_source_page': dict(bind(U / 'munich-interim-assets-page14.png'),
                physical_page=14, printed_page=12, total_assets_eur_million='275688'),
            'historical_vintage_admissions': 0, 'empirical_execution': False}
    with target.open('x') as f:
        json.dump(data, f, indent=2, ensure_ascii=False); f.write('\n')
    print(json.dumps({'candidates': len(rows), 'anchors': sum(len(r['anchors']) for r in rows),
        'with_dated_roles': sum(any(d['date'] for d in r['date_roles']) for r in rows), 'as_of_admissions': 0}))

if __name__ == '__main__':
    main()
