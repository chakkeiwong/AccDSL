"""Capture inspected statement rows and check their declared relationships.

Geometry is specific to the five visually inspected retained pages. This is an
author evidence record, not a general parser or a runtime implementation.
"""
import hashlib
import json
import re
from decimal import Decimal
from pathlib import Path

import fitz

UNIT = Path(__file__).resolve().parent
ROOT = UNIT.parents[2]
if (UNIT / 'completion.json').exists():
    raise SystemExit('Completed unit; preserve evidence.')


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save(name, data):
    (UNIT / name).write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')


source = ROOT / 'docs/design/cases/apple/annual-2024.pdf'
assert sha(source) == 'ec74758cd767465362c641cf2fd5d8fedd477aed2bf7f62117e67610435dcb88'
doc = fitz.open(source)
# Ordered from the inspected images, with literal signs and precision retained.
specs = {
    'operations': (32,
        'products_revenue services_revenue revenue products_cost services_cost cost gross_margin research selling operating_expenses operating_income other_income pretax tax net_income eps_basic eps_diluted shares_basic shares_diluted',
        '294,866 96,169 391,035 185,233 25,119 210,352 180,683 31,370 26,097 57,467 123,216 269 123,485 29,749 93,736 6.11 6.08 15,343,783 15,408,095'),
    'comprehensive': (33,
        'net_income fx derivatives_fv derivatives_reclassification derivatives_total securities_fv securities_reclassification securities_total oci comprehensive_income',
        '93,736 395 (832) (1,337) (2,169) 5,850 204 6,054 4,280 98,016'),
    'balance': (34,
        'cash securities_current receivables vendor_receivables inventory other_assets_current assets_current securities_noncurrent ppe other_assets_noncurrent assets_noncurrent assets payables other_liabilities_current deferred_revenue commercial_paper debt_current liabilities_current debt_noncurrent other_liabilities_noncurrent liabilities_noncurrent liabilities capital retained aoci equity liabilities_equity',
        '29,943 35,228 33,410 32,833 7,286 14,287 152,987 91,479 45,680 74,834 211,993 364,980 68,960 78,304 8,249 9,967 10,912 176,392 85,750 45,888 131,638 308,030 83,276 (19,154) (7,172) 56,950 364,980'),
    'equity': (35,
        'opening capital_opening issued withheld_capital compensation capital_closing retained_opening net_income dividends withheld_retained repurchases retained_closing aoci_opening oci aoci_closing closing dividend_per_unit',
        '62,146 73,812 1,423 (3,993) 12,034 83,276 (214) 93,736 (15,218) (1,612) (95,846) (19,154) (11,452) 4,280 (7,172) 56,950 0.98'),
    'cash_flow': (36,
        'opening net_income depreciation compensation other_adjustments receivables vendor_receivables inventory other_assets payables other_liabilities operating securities_purchases securities_maturities securities_sales ppe_payments investing_other investing award_tax dividends repurchases debt_issuance debt_repayments commercial_paper financing_other financing change closing income_tax_paid',
        '30,737 93,736 11,445 11,688 (2,266) (3,788) (1,356) (1,046) (11,731) 6,020 15,552 118,254 (48,656) 51,211 11,135 (9,447) (1,308) 2,935 (5,441) (15,234) (94,949) — (9,958) 3,960 (361) (121,983) (794) 29,943 26,102'),
}
opening_literals = '29,965 31,590 29,508 31,477 6,331 14,695 143,566 100,544 43,715 64,758 209,017 352,583 62,611 58,829 8,061 5,985 9,822 145,308 95,281 49,848 145,129 290,437 73,812 (214) (11,452) 62,146 352,583'.split()
checks = {}
rows = []
narratives = {}
values = {}


def number(literal):
    if literal == '—':
        return None
    return str(Decimal(literal.replace(',', '').replace('(', '-').replace(')', '')))


for statement, (page_no, ids, literals) in specs.items():
    spans = [s for b in doc[page_no - 1].get_text('dict')['blocks'] for l in b.get('lines', []) for s in l['spans']]
    right = 508.2 if statement == 'balance' else 434.2
    cells = sorted([s for s in spans if abs(s['bbox'][2] - right) < 2
                    and re.fullmatch(r'[()\d,.]+|—', s['text'].strip())
                    and 130 < s['bbox'][1] < 610], key=lambda s: s['bbox'][1])
    keys = ids.split()
    checks['complete_inspected_column:' + statement] = [s['text'].strip() for s in cells] == literals.split() and len(cells) == len(keys)
    if not checks['complete_inspected_column:' + statement]:
        raise ValueError(statement)
    narratives[statement] = [{'literal': s['text'], 'bbox': s['bbox']} for s in spans
                            if s['bbox'][0] < (470 if statement == 'balance' else 380)]
    for key, cell in zip(keys, cells):
        literal = cell['text'].strip()
        near = sorted([s for s in spans if abs(s['bbox'][1] - cell['bbox'][1]) < 1
                       and s['bbox'][0] < (470 if statement == 'balance' else 380)], key=lambda s: s['bbox'][0])
        label = ' '.join(s['text'].strip() for s in near if s['text'].strip() != '$')
        if statement == 'balance' and key == 'capital':
            label = ' '.join(s['text'].strip() for s in spans if 0 <= cell['bbox'][1] - s['bbox'][1] < 21
                             and s['bbox'][0] < 470)
        unit = 'USD million'
        if key.startswith('eps_') or key == 'dividend_per_unit':
            unit = 'USD per share' if key != 'dividend_per_unit' else 'USD per share or RSU'
        if key.startswith('shares_'):
            unit = 'thousand weighted-average shares'
        row = {'id': statement + '.' + key, 'statement': statement, 'label': label,
               'period': '2024-09-28' if statement == 'balance' else 'FY2024: 2023-10-01 through 2024-09-28',
               'entity': 'Apple Inc. consolidated', 'basis': 'US GAAP issuer report',
               'unit': unit, 'status': 'reported reading', 'literal': literal,
               'value': number(literal), 'precision': 'displayed units; no exact unrounded equality claimed',
               'source': str(source.relative_to(ROOT)), 'source_sha256': sha(source),
               'pdf_page': page_no, 'printed_page': page_no - 3, 'bbox': cell['bbox'],
               'label_spans': [{'literal': s['text'], 'bbox': s['bbox']} for s in near]}
        if statement == 'balance' or statement in {'equity', 'cash_flow'} and (key in {'opening', 'closing'} or key.endswith(('_opening', '_closing'))):
            row['measurement_kind'] = 'instant balance'
            row['measurement_date'] = '2023-09-30' if key == 'opening' or key.endswith('_opening') else '2024-09-28'
        else:
            row['measurement_kind'] = 'period amount or period statistic'
        if literal == '—':
            row['arithmetic_convention'] = 'No contribution for displayed total check only; source dash remains a dash, not an identified exact zero.'
        if statement == 'balance':
            older = [s for s in spans if abs(s['bbox'][1] - cell['bbox'][1]) < 1 and abs(s['bbox'][2] - 592.6) < 2
                     and re.fullmatch(r'[()\d,.]+|—', s['text'].strip())]
            assert len(older) == 1
            prior_literal = older[0]['text'].strip()
            checks['opening_literal:' + key] = prior_literal == opening_literals[keys.index(key)]
            row['opening'] = {'date': '2023-09-30', 'literal': prior_literal, 'value': number(prior_literal), 'bbox': older[0]['bbox']}
            values['opening.' + key] = Decimal(number(prior_literal))
        rows.append(row)
        values[row['id']] = Decimal(number(literal)) if literal != '—' else Decimal(0)

balance_text = doc[33].get_text()
checks['nonmonetary_equity_annotation'] = all(t in balance_text for t in ['0.00001', '50,400,000', '15,116,786', '15,550,061'])
checks['blank_commitments_retained'] = 'Commitments and contingencies' in balance_text
save('statement-readings.json', {'scope': 'Complete selected FY2024 statement rows plus FY2023 balance-sheet endpoints; other comparative columns retained in source pages only',
     'rows': rows, 'narrative_spans': narratives,
     'nonamount_rows': [{'statement': 'balance', 'label': 'Commitments and contingencies', 'value': None, 'meaning': 'Source row has no amount; no zero liability inferred', 'pdf_page': 34}],
     'share_annotation': {'par_value_USD': '0.00001', 'authorized_thousand_shares': '50400000', 'closing_thousand_shares': '15116786', 'opening_thousand_shares': '15550061', 'pdf_page': 34, 'status': 'reported; distinct from monetary capital and weighted averages'},
     'source_dash_policy': 'Preserve dash as null reading; zero contribution is explicitly confined to displayed financing total arithmetic'})

relations = []


def relation(name, terms, target, purpose, role='pass/fail at displayed precision'):
    computed = sum(Decimal(str(coef)) * values[key] for coef, key in terms)
    rhs = values[target] if isinstance(target, str) else Decimal(str(target))
    record = {'id': name, 'terms': [{'coefficient': str(c), 'row': k} for c, k in terms],
              'target': str(target), 'computed': str(computed), 'target_value': str(rhs),
              'residual': str(computed - rhs), 'purpose': purpose, 'diagnostic_role': role}
    relations.append(record)
    if role.startswith('pass/fail'):
        checks['relation:' + name] = computed == rhs
    return computed


def total(name, prefix, inputs, output):
    return relation(name, [(c, prefix + '.' + k) for c, k in inputs], prefix + '.' + output, 'Same-statement subtotal; displayed amounts only')


for name, inputs, output in [
    ('sales', [(1, 'products_revenue'), (1, 'services_revenue')], 'revenue'),
    ('cost', [(1, 'products_cost'), (1, 'services_cost')], 'cost'),
    ('margin', [(1, 'revenue'), (-1, 'cost')], 'gross_margin'),
    ('expenses', [(1, 'research'), (1, 'selling')], 'operating_expenses'),
    ('operating', [(1, 'gross_margin'), (-1, 'operating_expenses')], 'operating_income'),
    ('pretax', [(1, 'operating_income'), (1, 'other_income')], 'pretax'),
    ('income', [(1, 'pretax'), (-1, 'tax')], 'net_income')]:
    total(name, 'operations', inputs, output)
for prefix in ['balance', 'opening']:
    for name, inputs, output in [
        ('current_assets', ['cash', 'securities_current', 'receivables', 'vendor_receivables', 'inventory', 'other_assets_current'], 'assets_current'),
        ('noncurrent_assets', ['securities_noncurrent', 'ppe', 'other_assets_noncurrent'], 'assets_noncurrent'),
        ('assets', ['assets_current', 'assets_noncurrent'], 'assets'),
        ('current_liabilities', ['payables', 'other_liabilities_current', 'deferred_revenue', 'commercial_paper', 'debt_current'], 'liabilities_current'),
        ('noncurrent_liabilities', ['debt_noncurrent', 'other_liabilities_noncurrent'], 'liabilities_noncurrent'),
        ('liabilities', ['liabilities_current', 'liabilities_noncurrent'], 'liabilities'),
        ('equity', ['capital', 'retained', 'aoci'], 'equity'),
        ('liabilities_equity', ['liabilities', 'equity'], 'liabilities_equity')]:
        total(prefix + ':' + name, prefix, [(1, k) for k in inputs], output)
    relation(prefix + ':identity', [(1, prefix + '.assets')], prefix + '.liabilities_equity', 'Balance-sheet identity')
for name, inputs, output in [
    ('derivatives', ['derivatives_fv', 'derivatives_reclassification'], 'derivatives_total'),
    ('securities', ['securities_fv', 'securities_reclassification'], 'securities_total'),
    ('oci', ['fx', 'derivatives_total', 'securities_total'], 'oci'),
    ('comprehensive', ['net_income', 'oci'], 'comprehensive_income')]:
    total(name, 'comprehensive', [(1, k) for k in inputs], output)
for name, inputs, output in [
    ('capital', ['capital_opening', 'issued', 'withheld_capital', 'compensation'], 'capital_closing'),
    ('retained', ['retained_opening', 'net_income', 'dividends', 'withheld_retained', 'repurchases'], 'retained_closing'),
    ('aoci', ['aoci_opening', 'oci'], 'aoci_closing'),
    ('equity_opening', ['capital_opening', 'retained_opening', 'aoci_opening'], 'opening'),
    ('equity_closing', ['capital_closing', 'retained_closing', 'aoci_closing'], 'closing')]:
    total(name, 'equity', [(1, k) for k in inputs], output)
for name, inputs, output in [
    ('operating_cash', ['net_income', 'depreciation', 'compensation', 'other_adjustments', 'receivables', 'vendor_receivables', 'inventory', 'other_assets', 'payables', 'other_liabilities'], 'operating'),
    ('investing_cash', ['securities_purchases', 'securities_maturities', 'securities_sales', 'ppe_payments', 'investing_other'], 'investing'),
    ('financing_cash', ['award_tax', 'dividends', 'repurchases', 'debt_issuance', 'debt_repayments', 'commercial_paper', 'financing_other'], 'financing'),
    ('cash_change', ['operating', 'investing', 'financing'], 'change'),
    ('cash_closing', ['opening', 'change'], 'closing')]:
    total(name, 'cash_flow', [(1, k) for k in inputs], output)
for target in ['comprehensive.net_income', 'equity.net_income', 'cash_flow.net_income']:
    relation('income_to:' + target, [(1, 'operations.net_income')], target, 'Same reported FY2024 income across statements')
relation('oci_to_equity', [(1, 'comprehensive.oci')], 'equity.oci', 'Same net-of-tax period OCI')
for eq, bs in [('opening', 'opening.equity'), ('closing', 'balance.equity'), ('capital_opening', 'opening.capital'),
               ('capital_closing', 'balance.capital'), ('retained_opening', 'opening.retained'), ('retained_closing', 'balance.retained'),
               ('aoci_opening', 'opening.aoci'), ('aoci_closing', 'balance.aoci')]:
    relation('equity_to_balance:' + eq, [(1, 'equity.' + eq)], bs, 'Equity component endpoint and same consolidated balance-sheet endpoint')
relation('closing_cash_population_match', [(1, 'cash_flow.closing')], 'balance.cash', 'Closing amounts match; does not establish unrestricted availability')
relation('whole_equity_bridge', [(1, 'equity.opening'), (1, 'comprehensive.comprehensive_income')]
         + [(1, 'equity.' + k) for k in ['issued', 'withheld_capital', 'compensation', 'dividends', 'withheld_retained', 'repurchases']],
         'equity.closing', 'Comprehensive income plus all reported other equity movements; not all are cash flows')
relation('balance_changes', [(1, 'balance.assets'), (-1, 'opening.assets'), (-1, 'balance.liabilities'), (1, 'opening.liabilities')],
         values['balance.equity'] - values['opening.equity'], 'Change in net assets equals change in equity')
relation('other_equity_movements', [(1, 'equity.' + k) for k in ['issued', 'withheld_capital', 'compensation', 'dividends', 'withheld_retained', 'repurchases']],
         -103212, 'All reported equity movements apart from net income and OCI; not all are cash flows')
relation('operating_reconciliation_adjustments', [(1, 'cash_flow.' + k) for k in ['depreciation', 'compensation', 'other_adjustments']],
         20867, 'Reported adjustments before the operating-asset/liability movements')
relation('operating_asset_liability_adjustments', [(1, 'cash_flow.' + k) for k in ['receivables', 'vendor_receivables', 'inventory', 'other_assets', 'payables', 'other_liabilities']],
         3651, 'All six reported indirect operating-asset/liability adjustments; no balance-sheet scope equivalence imposed')

residual_specs = [
    ('opening_cash_population', [(1, 'cash_flow.opening'), (-1, 'opening.cash')], 'Earlier 772 cash-population difference; location and cause unallocated; not the closing 2.6 billion escrow.'),
    ('receivables', [(1, 'balance.receivables'), (-1, 'opening.receivables'), (1, 'cash_flow.receivables')], 'Account-stock change plus indirect adjustment; no collection or FX cause identified.'),
    ('vendor_receivables', [(1, 'balance.vendor_receivables'), (-1, 'opening.vendor_receivables'), (1, 'cash_flow.vendor_receivables')], 'An exact opposite movement still does not identify gross transactions or dates.'),
    ('inventory', [(1, 'balance.inventory'), (-1, 'opening.inventory'), (1, 'cash_flow.inventory')], 'Retains the prior -91 inventory residual; no write-down or settlement cause assigned.'),
    ('payables', [(1, 'balance.payables'), (-1, 'opening.payables'), (-1, 'cash_flow.payables')], 'Stock increase exceeds indirect cash adjustment; purchases and settlement schedules remain unknown.'),
    ('repurchases', [(-1, 'equity.repurchases'), (1, 'cash_flow.repurchases')], 'Equity reduction less cash outflow; prior 897 result remains unassigned.'),
    ('award_withholding', [(-1, 'equity.withheld_capital'), (-1, 'equity.withheld_retained'), (1, 'cash_flow.award_tax')], 'Prior 164 cash/equity difference remains unassigned.'),
    ('compensation', [(1, 'equity.compensation'), (-1, 'cash_flow.compensation')], 'Prior 346 equity/expense difference remains unassigned.'),
    ('dividends', [(-1, 'cash_flow.dividends'), (1, 'equity.dividends')], 'Cash paid exceeds declarations by 16; no payable vintage or cause is identified.'),
    ('tax_expense_cash', [(1, 'operations.tax'), (-1, 'cash_flow.income_tax_paid')], 'Expense less net cash paid differs in measurement and timing; not an identified tax payable movement.'),
    ('term_debt', [(1, 'balance.debt_current'), (1, 'balance.debt_noncurrent'), (-1, 'opening.debt_current'), (-1, 'opening.debt_noncurrent'), (-1, 'cash_flow.debt_issuance'), (-1, 'cash_flow.debt_repayments')], 'Carrying-value movement less cash issuance/repayment; source dash convention only; no FX/hedge allocation.'),
    ('commercial_paper', [(1, 'balance.commercial_paper'), (-1, 'opening.commercial_paper'), (-1, 'cash_flow.commercial_paper')], 'Carrying-value movement less net cash flow; do not infer an amortization or currency journal.'),
]
unknowns = []
for name, terms, explanation in residual_specs:
    amount = relation('diagnostic:' + name, terms, 0, explanation, 'explanatory residual; never a balancing journal')
    unknowns.append({'id': name, 'displayed_residual': str(amount), 'status': 'unallocated' if amount else 'matched aggregates with unidentified gross history', 'meaning': explanation})

dependencies = {}
for name, filenames in {
    'apple-assets-20261008': ['result.md', 'asset-history.json'],
    'apple-tax-20261009': ['result.md', 'tax-bridges.json'],
    'apple-eps-20261009': ['result.md', 'source-claim-supplement.json'],
    'apple-debt-20261009': ['result.md', 'source-claim-supplement.json'],
    'apple-liquidity-20261009': ['result.md', 'source-claim-supplement.json'],
    'chapter2-source-crosswalk-20261010': ['result.md'],
}.items():
    for filename in filenames:
        path = ROOT / 'data/accounting-master' / name / filename
        dependencies[name + '/' + filename] = {'path': str(path.relative_to(ROOT)), 'sha256': sha(path),
                                               'review_basis': 'Reuse completed scoped note evidence; no rerun or new independent acceptance'}
prior_eq = json.loads((ROOT / dependencies['apple-eps-20261009/source-claim-supplement.json']['path']).read_text())['numeric_tables']['annual.equity']['rows']
checks['prior_equity_reading_agrees'] = [r['value'] for r in rows if r['statement'] == 'equity'] == [r['values'][0] for r in prior_eq]
checks['102_numeric_or_dash_rows'] = len(rows) == 102
checks['unique_ids'] = len({r['id'] for r in rows}) == len(rows)
checks['one_dash_not_zero_reading'] = [(r['id'], r['value']) for r in rows if r['literal'] == '—'] == [('cash_flow.debt_issuance', None)]
save('relationship-ledger.json', {'relations': relations, 'interpretation': 'Displayed statement consistency and explanatory differences; no invented source-to-journal edges'})
save('unresolved-edges.json', {'residuals': unknowns, 'other_unresolved': [
    'Broad indirect other-assets/liabilities rows are not disjoint partitions of balance-sheet labels; retain the missing scope mapping.',
    'PP&E depreciation differs from broad D&A; prior conditional subsystem histories have not been embedded in a full company journal.',
    'Marketable-securities purchases, maturities, sales and OCI do not identify security lots, tax effects or settlement dates.',
    'Income/revenue/cost totals do not identify customer collections, purchases, allocations or all material narrative dependencies.',
    'A complete five-statement table does not close notes, incorporated references, historical availability or a real conditional forecast.']})
save('dependencies.json', dependencies)
failed = [key for key, value in checks.items() if not value]
save('source-arithmetic-checks.json', {'passed': sum(checks.values()), 'failed': failed, 'checks': checks,
                                    'evidence_class': 'Deterministic source and displayed arithmetic; no statistical ranking'})
print(json.dumps({'rows': len(rows), 'relations': len(relations), 'passed': sum(checks.values()), 'failed': failed}))
raise SystemExit(bool(failed))
