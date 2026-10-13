"""Check source-bound CSM movements and nested reconciliation scopes."""
import json
import re

from prepare_sources import BASE, ROOT, SOURCE, UNIT, save, sha

if (UNIT / 'completion.json').exists():
    raise SystemExit('Completed unit; preserve evidence.')
baseline = json.loads((UNIT / 'baseline.json').read_text())
manifest = json.loads((UNIT / 'source-pages.json').read_text())
checks = {'source_identity': sha(SOURCE) == baseline['source_sha256'] == manifest['source_sha256'],
          'prior_candidate_preserved': sha(BASE / 'accounting-product-proposal.pdf') == baseline['baseline_pdf_sha256']}
texts = {}
for p in manifest['pages']:
    n = p['pdf_page']
    raw = (ROOT / p['text_path']).read_text()
    texts[n] = re.sub(r'\s+', ' ', re.sub(r'[\x12\x1c]', ',', raw)).replace('–', '-').replace('−', '-')
    checks[f'text_hash:{n}'] = sha(ROOT / p['text_path']) == p['text_sha256']
    checks[f'image_hash:{n}'] = sha(ROOT / p['image_path']) == p['image_sha256']
prior_unit = ROOT / 'data/accounting-master/munich-new-contracts-20261013'
prior_pages = json.loads((prior_unit / 'source-pages.json').read_text())
prior = {p['pdf_page']: p for p in prior_pages['pages']}
for p in manifest['pages']:
    n = p['pdf_page']
    if n in prior:
        checks[f'carried_review_text:{n}'] = p['text_sha256'] == prior[n]['text_sha256']
        checks[f'carried_review_image:{n}'] = p['image_sha256'] == prior[n]['image_sha256']
for n, quote in [
    (243, 'include the entire liability from insurance contracts issued which were measured using the general measurement model and the variable fee approach'),
    (243, 'and the liability for incurred claims for insurance contracts issued which were measured using the premium allocation approach'),
    (243, 'The liability for remaining coverage for insurance contracts issued which were measured using the premium allocation approach is not included'),
    (249, 'in the amount of -€1m (-62m) for the ERGO Life and Health Germany segment is not included'),
]:
    checks[f'scope:{n}:{quote[:35]}'] = quote in texts[n]

# Each vector retains the source column order PV, RA, CSM, Total; None is
# a blank cell. The exact row sequence is bound to the inspected source.
rows = [
    ('opening', 'Carrying amount at 1 January - Insurance portfolios (net)', [-98464, -580, -10449, -109494]),
    ('service', 'Contractual service margin for services provided in the reporting period', [None, None, 819, 819]),
    ('new_business', 'Effects of contracts initially recognised in the period', [141, -8, -154, -21]),
    ('estimates', 'Changes in estimates adjusting the contractual service margin', [-261, 15, 214, -32]),
    ('derecognition', 'Effects from derecognition and changes in consolidated group', [12, 0, 1, 13]),
    ('premium', 'Premiums received', [-8471, None, None, -8471]),
    ('acquisition_cash', 'Acquisition costs', [502, None, None, 502]),
    ('closing', 'Carrying amount at 31 December - Insurance portfolios (net)', [-102699, -539, -9569, -112807]),
]
for key, label, vector in rows:
    exact = label + ' ' + ' '.join(f'{v:,}' for v in vector if v is not None)
    checks['source_row:' + key] = exact in texts[248]
checks['opening_full'] = '-107,654 -26 -1,876 -109,556' in texts[232]
checks['closing_full'] = '-110,885 -19 -1,903 -112,808' in texts[233]
checks['premium_full'] = 'Premiums received -10,406 -10,406' in texts[233]
checks['acquisition_cash_full'] = 'Acquisition costs 978 978' in texts[233]
checks['service_cross_table'] = 'Contractual service margin for services provided in the reporting period 819 948' in texts[266]
checks['new_business_cross_table'] = 'Contractual service margin -154 0 -154' in texts[255].split('Prev. year')[0]
checks['current_forecast_opening'] = '-12,530 -9,569 -2,868 -24,967' in texts[256]
checks['comparative_opening'] = '-123,705 -1,038 -9,412 -134,156' in texts[249]
checks['comparative_service'] = 'Contractual service margin for services provided in the reporting period 948 948' in texts[249]
checks['comparative_new'] = 'Effects of contracts initially recognised in the period 222 -14 -221 -13' in texts[249]
checks['comparative_estimates'] = 'Changes in estimates adjusting the contractual service margin 1,330 423 -1,764 -11' in texts[249]
checks['comparative_closing'] = '-98,464 -580 -10,449 -109,494' in texts[249]

checks['signed_csm_bridge'] = -10449 + 819 - 154 + 214 + 1 == -9569
checks['positive_magnitude_bridge'] = 10449 + 154 - 819 - 214 - 1 == 9569
checks['service_subtotal_not_added_twice'] = 819 - 154 + 214 == 879
checks['signed_csm_change'] = -9569 - (-10449) == 880
checks['comparative_csm_bridge'] = -9412 + 948 - 221 - 1764 == -10449
checks['year_continuity'] = rows[0][2][2] == -10449
checks['paa_opening_difference'] = -109556 - (-109494) == -62
checks['paa_closing_difference'] = -112808 - (-112807) == -1
checks['paa_signed_balance_change'] = -1 - (-62) == 61
checks['omitted_premium_movement'] = -10406 - (-8471) == -1935
checks['omitted_acquisition_movement'] = 978 - 502 == 476
checks['cash_difference_not_expense_residual'] = 476 != 637 - 202
checks['difference_between_different_residuals'] = 476 - (637 - 202) == 41
checks['expense_residual_preserved'] = 637 - 202 == 435
# No claim that all table totals conserve exact unrounded amounts.
checks['full_table_display_discrepancy'] = -109556 + 1180 - 2983 - 33 - 3100 + 1685 - (-112808) == 1
checks['subset_table_display_discrepancy'] = -109494 - 362 - 2959 + 11 - 3100 + 3096 - (-112807) == -1

readings = {'source_sha256': sha(SOURCE), 'units': 'EUR million, rounded source values',
    'scope': 'ERGO Life and Health Germany; measurement components include GMM/VFA balances and PAA incurred claims, excluding PAA remaining coverage',
    'source_column_order': ['present_value', 'risk_adjustment', 'csm', 'total'],
    'rows': [{'id': k, 'source_label': label, 'values': values, 'pdf_page': 248} for k, label, values in rows],
    'csm_signed_movements': {'opening': -10449, 'service': 819, 'new_business': -154, 'estimates': 214, 'derecognition': 1, 'closing': -9569},
    'csm_zero_or_blank_rows': 'Retained literally in source; no conversion of blanks into reported zeros',
    'nested_scope_differences': {'opening_paa_lrc': -62, 'closing_paa_lrc': -1, 'premium_movement': -1935, 'acquisition_cash_movement': 476},
    'unexplained_expense_residual': 435,
    'interpretation_limit': 'The cash differences concern the omitted PAA remaining-coverage portion at displayed precision, not all PAA cash flows or the identified cause of the expense residual.',
    'freshly_inspected_images': [243, 248, 249], 'carried_inspected_images_by_hash': [232, 233, 255, 256, 266],
    'human_review': 'pending', 'accounting_acceptance': 'pending'}
save('source-readings.json', readings)
failed = [k for k, passed in checks.items() if not passed]
save('source-calculation-checks.json', {'checks': checks, 'passed': sum(checks.values()), 'failed': failed})
print(json.dumps({'passed': sum(checks.values()), 'failed': failed, 'source_pages': len(manifest['pages'])}))
raise SystemExit(bool(failed))
