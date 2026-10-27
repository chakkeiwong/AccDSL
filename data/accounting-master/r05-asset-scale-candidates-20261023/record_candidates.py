"""Record inspected total-assets candidates without as-of admissions."""
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path

U = Path(__file__).resolve().parent
R = U.parents[2]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
bind = lambda p: {'path': str(p.relative_to(R)), 'sha256': sha(p)}

SPECS = {
 'apple': ('359241', 1000000, '2025-09-27', [(1154,1161),(1196,1203)], 'USD remains proposed from dollar display and reporting context'),
 'caterpillar': ('98585', 1000000, '2025-12-31', [(3205,3209),(3223,3225)], 'consolidated statement; supplemental MP&E/Financial Products columns have different perimeters'),
 'jpmorgan': ('4424900', 1000000, '2025-12-31', [(12274,12278),(12290,12294)], 'USD remains proposed from dollar display and reporting context; retain total-assets footnote'),
 'henkel': ('32533', 1000000, '2025-12-31', [(19602,19607),(19620,19626),(7136,7139),(7164,7167)], '2025 is the second amount column, interleaved with percentages; HGB parent total differs; comparative amended'),
 'hsbc': ('3233034', 1000000, '2025-12-31', [(21536,21541),(21553,21557),(22016,22018),(22028,22031)], 'HSBC Holdings parent total293020 differs from group'),
 'munich_re': ('279934', 1000000, '2025-12-31', [(14064,14071),(14098,14104)], 'damaged text separators resolved by actual viewing of physical226/printed224; comparative adjusted underIAS8'),
 'saic_motor': ('960207461450.69', 1, '2025-12-31', [(3311,3315),(3363,3367),(3435,3439),(3481,3484)], 'parent total312099055843.14 differs from consolidated'),
 'ping_an': ('13898471', 1000000, '2025-12-31', [(8611,8618),(8647,8650)], 'consolidated group; do not substitute parent or investment-asset totals'),
 'midea': ('608791766', 1000, '2025-12-31', [(8044,8052),(8084,8087)], 'four columns: consolidated2025/2024,parent2025/2024; parent2025 total295444621')
}


def main():
    assert os.environ.get('CUDA_VISIBLE_DEVICES') == '-1'
    assert not (U/'candidates.json').exists()
    previous = R/'data/accounting-master/r05-ocf-measurement-20261023/measurement-map.json'
    prior = json.loads(previous.read_text())
    rows = []
    for source in prior['rows']:
        issuer = source['issuer_id']
        amount, multiplier, date, spans, issue = SPECS[issuer]
        lines = (R/source['text']['path']).read_text().split('\n')
        assert Fraction(amount)>0
        rows.append({'issuer_id':issuer,'document_id':source['document_id'],
            'original':source['original'],'text':source['text'],'source_url':source['source_url'],
            'reported_total_assets':amount,'unit_multiplier':multiplier,
            'native_currency_proposal':source['reported_value']['currency_proposal'],
            'reporting_date':date,'scope':'consolidated group as reported',
            'basis':source['reported_value']['basis'],'caveat':issue,
            'anchors':[{'start_line':a,'end_line':b,'quote':'\n'.join(lines[a-1:b])} for a,b in spans],
            'displayed_amount_exact_rational':str(Fraction(amount)),
            'amount_in_currency_units':str(Fraction(amount)*multiplier),
            'measurement_precision':'reported display precision; not an exact underlying economic quantity',
            'selected_for_actual_cutoff':False,'selected_byte_available_at':None,'as_of_admission':False})
    value={'scope':'nine FY2025 annual closing total-assets mapping examples only',
           'rows':rows,'predecessor_measurement_map':bind(previous),
           'actually_viewed_source_page':dict(bind(U/'munich-balance-sheet-page226.png'),physical_page=226,printed_page=224,
                                              total_assets_eur_million='279934'),
           'scale_policy':'most recent eligible reporting-date consolidated total assets available by each cutoff; no actual value admitted',
           'cross_company_currency_conversion_required':False,
           'within_company_compatible_currency_and_units_required':True,
           'historical_vintage_admissions':0,'empirical_execution':False}
    with (U/'candidates.json').open('x') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'candidates':9,'source_anchors':sum(len(r['anchors']) for r in rows),'actually_viewed_pages':1,'as_of_admissions':0}))


if __name__=='__main__':main()
