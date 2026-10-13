"""Check selected source readings and exact, explicitly hypothetical rounding."""
import json
import re
from decimal import Decimal as D

from prepare_sources import BASE, ROOT, SOURCE, UNIT, save, sha

if (UNIT / 'completion.json').exists():
    raise SystemExit('Completed unit; preserve evidence.')

base = json.loads((UNIT / 'baseline.json').read_text())
sources = json.loads((UNIT / 'source-pages.json').read_text())
checks = {'source_identity': sha(SOURCE) == base['source_sha256'] == sources['source_sha256'],
          'baseline_pdf': sha(BASE / 'accounting-product-proposal.pdf') == base['baseline_pdf_sha256']}
texts = {}
for item in sources['pages']:
    page = item['pdf_page']
    raw = (ROOT / item['text_path']).read_text()
    texts[page] = re.sub(r'\s+', ' ', raw)
    checks[f'text_hash:{page}'] = sha(ROOT / item['text_path']) == item['text_sha256']
    checks[f'image_hash:{page}'] = sha(ROOT / item['image_path']) == item['image_sha256']

anchors = [
    (3, 'German original is binding'),
    (157, 'Amounts are rounded to million euros'),
    (157, 'there may be minor deviations in totals and percentages'),
    (157, 'as adopted by the EU'),
    (167, 'initial recognition of profitable groups of insurance contracts thus does not affect profit or loss'),
    (168, 'onerous insurance contracts are not combined with profitable ones'),
    (168, 'We use this option for a substantial part of our property-casualty primary insurance business'),
    (179, 'Acquisition costs are recognised in insurance service expenses in the same amount as used to determine insurance revenue'),
    (254, 'general measurement model or the variable fee approach is predominantly used'),
    (254, 'property-casualty reinsurance and ERGO Property-casualty Germany segments are not shown'),
    (254, 'ERGO Life and Health Germany segment'),
    (254, 'measured under the general measurement model and the variable fee approach'),
    (255, 'Insurance contracts issued (concluded)'),
    (255, 'Insurance contracts issued (acquired)'),
    (256, 'forecast of the recognition in profit or loss of the contractual service margin'),
    (266, 'in the financial year from insurance contracts issued measured using the variable fee approach or the general measurement model'),
]
for page, quote in anchors:
    checks[f'anchor:{page}:{quote[:40]}'] = quote in texts[page]

raw = (UNIT / 'source-pages/page-255.txt').read_text()
first = raw.split('Prev. year', 1)[0]
# Raw PDF control characters separate digits. They are retained above and
# interpreted here only after inspecting the corresponding image.
flat = re.sub(r'\s+', ' ', re.sub(r'[\x12\x1c]', ',', first)).replace('–', '-')
rows = [
    ('inflows', 'Estimated present value of future cash inflows', [2842, 17, 0, 0, 2859]),
    ('claims_expenses_investment', 'Expected future claims, expenses and investment components', [-2438, -12, 0, 0, -2450]),
    ('acquisition', 'Acquisition costs', [-243, -25, 0, 0, -268]),
    ('risk_adjustment', 'Risk adjustment', [-8, 0, 0, 0, -8]),
    ('csm', 'Contractual service margin', [-154, None, 0, None, -154]),
]
readings = []
for key, label, values in rows:
    tokens = [f'{v:,}' for v in values if v is not None]
    needle = label + ' ' + ' '.join(tokens)
    checks['table_reading:' + key] = needle in flat
    readings.append({'row': key, 'source_label': label, 'pdf_page': 255, 'printed_page': 253,
                     'values': values, 'blank_policy': 'None preserves a blank source cell; not a reported zero.'})
checks['table_totals'] = 'Total 0 -21 0 0 -21' in flat
checks['table_outflow_subtotals'] = '-2,681 -37 0 0 -2,718' in flat

nononerous_sum = 2842 - 2438 - 243 - 8 - 154
onerous_sum = 17 - 12 - 25 - 0
checks['nononerous_display_discrepancy'] = nononerous_sum == -1 and nononerous_sum != 0
checks['onerous_display_discrepancy'] = onerous_sum == -20 and onerous_sum != -21

# A consistency witness under nearest-million rounding, not recovered issuer
# data. No value sits on a half-unit boundary. The source specifies rounding
# to millions, but does not disclose a tie-breaking convention.
hidden = {
    'inflows': [D('2842.3'), D('16.6')],
    'claims_expenses_investment': [D('-2437.8'), D('-12.1')],
    'acquisition': [D('-242.8'), D('-25.2')],
    'risk_adjustment': [D('-7.8'), D('-0.3')],
    'csm': [D('-153.9'), D('0')],
}
for key, _, values in rows:
    a, b = hidden[key]
    checks['round_nononerous:' + key] = abs(a - D(values[0])) < D('.5')
    if values[1] is not None:
        checks['round_onerous:' + key] = abs(b - D(values[1])) < D('.5')
    checks['round_total:' + key] = abs(a + b - D(values[4])) < D('.5')
group_totals = [sum(vals[i] for vals in hidden.values()) for i in range(2)]
checks['joint_column_totals'] = group_totals == [D('0'), D('-21.0')]
outflows = [hidden['claims_expenses_investment'][i] + hidden['acquisition'][i] for i in range(2)]
checks['joint_outflow_subtotals'] = all(abs(v - D(display)) < D('.5') for v, display in zip(outflows, [-2681, -37]))
checks['joint_outflow_total'] = abs(sum(outflows) - D(-2718)) < D('.5')
checks['joint_total_balance'] = sum(group_totals) == -21
checks['onerous_blank_is_not_source_zero'] = readings[-1]['values'][1] is None

revenue_raw = (UNIT / 'source-pages/page-266.txt').read_text().split('The table below presents', 1)[0]
revenue_flat = re.sub(r'\s+', ' ', re.sub(r'[\x12\x1c]', ',', revenue_raw)).replace('–', '-')
checks['revenue_recovery_reading'] = 'recovery of acquisition costs 202 192' in revenue_flat
checks['revenue_csm_reading'] = 'Contractual service margin for services provided in the reporting period 819 948' in revenue_flat
checks['revenue_total_reading'] = '9,942 9,802' in revenue_flat
checks['revenue_total_sum'] = 6912 + 35 + 819 + 202 - 3 + 0 + 1976 == 9941  # source total is 9942
checks['revenue_measurement_split'] = 7966 + 1976 == 9942
checks['new_business_acquisition_not_recovery'] = 268 != 202
checks['new_csm_not_period_release'] = 154 != 819
checks['full_expense_reading'] = 'Recovery of acquisition costs –637 –637' in texts[232]
checks['acquisition_cash_reading'] = 'Acquisition costs 978 978' in texts[233]
checks['expense_recovery_residual'] = 637 - 202 == 435
checks['cash_expense_residual'] = 978 - 637 == 341

save('source-readings.json', {'source_sha256': sha(SOURCE), 'unit': 'EUR million', 'period': '2023',
    'columns': ['concluded_nononerous', 'concluded_onerous', 'acquired_nononerous', 'acquired_onerous', 'total'],
    'scope': 'Newly recognised ERGO Life and Health Germany contracts; GMM/VFA combined',
    'rows': readings, 'outflow_subtotals': [-2681, -37, 0, 0, -2718], 'totals': [0, -21, 0, 0, -21],
    'inspected_source_images': [p['pdf_page'] for p in sources['pages']],
    'reported_period_recovery_revenue': 202, 'reported_period_csm_release': 819,
    'reported_period_recovery_expense': 637, 'reported_acquisition_cash': 978,
    'expense_less_recovery': {'value': 435, 'status': 'Arithmetic residual only; cause not identified here.'},
    'separate_prior_acquisition_asset': 'not identified by these tables',
    'rounding_witness': {key: [str(v) for v in vals] for key, vals in hidden.items()},
    'rounding_witness_status': 'Hypothetical consistency witness only; onerous CSM zero is an assumption of this witness, not a reported numeric cell.',
    'display_discrepancies': {'nononerous_sum': nononerous_sum, 'nononerous_reported_total': 0,
                              'onerous_sum_excluding_blank_csm': onerous_sum, 'onerous_reported_total': -21},
    'human_review': 'pending', 'accounting_acceptance': 'pending'})
failed = [key for key, passed in checks.items() if not passed]
save('source-calculation-checks.json', {'checks': checks, 'passed': sum(checks.values()), 'failed': failed})
print(json.dumps({'passed': sum(checks.values()), 'failed': failed, 'source_pages': len(sources['pages'])}))
raise SystemExit(bool(failed))
