"""Deterministic conditional difference test; never an actual Apple completion."""
import hashlib
import json
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

UNIT = Path(__file__).resolve().parent
ROOT = UNIT.parents[2]
if (UNIT / 'completion.json').exists():
    raise SystemExit('Completed unit; preserve evidence.')

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def save(name, value):
    (UNIT / name).write_text(json.dumps(value, indent=2) + '\n')

baseline = json.loads((UNIT / 'baseline.json').read_text())
checks = {}
for path, digest in baseline['dependencies'].items():
    checks['dependency:' + path] = sha(ROOT / path) == digest
renders = json.loads((UNIT / 'source-renders.json').read_text())
checks['annual_source'] = sha(ROOT / renders['source']) == renders['source_sha256']
for row in renders['images']:
    checks['source_image:' + str(row['pdf_page'])] = sha(ROOT / row['image']) == row['sha256']
    checks['source_text:' + str(row['pdf_page'])] = sha(ROOT / row['text']) == row['text_sha256']

assets = json.loads((ROOT / 'data/accounting-master/apple-assets-20261008/asset-history.json').read_text())
prior = json.loads((ROOT / 'data/accounting-master/apple-history-compatibility-20261013/compatibility.json').read_text())
annual = json.loads((ROOT / 'data/accounting-master/apple-statement-network-20261013/statement-readings.json').read_text())
rows = {row['id']: row for row in annual['rows']}
accounts = []
for history in assets['histories']:
    signed = defaultdict(int)
    for journal in history['journals']:
        checks[history['id'] + ':journal:' + journal['event']] = sum(
            p['debit'] - p['credit'] for p in journal['postings']) == 0
        for posting in journal['postings']:
            signed[posting['account']] += posting['debit'] - posting['credit']
    accounts.append(signed)
delta = {key: accounts[1][key] - accounts[0][key] for key in set(accounts[0]) | set(accounts[1])}
checks['prior_journal_delta'] = delta['capital_payable'] == -1000 and delta['retirement_loss'] == 1000
checks['prior_required_complement'] = prior['H2_minus_H1']['liabilities'] == 1000

def report(alpha, q=2000, expense_row='operations.products_cost',
           liability_row='balance.other_liabilities_current', duplicate=False,
           extra_tax=0):
    """Return H2-H1 under a fully declared linear reporting map.

    q is an independent hypothetical expense-liability obligation in H1.
    H2 has q-1000. Both journals debit expense and credit that liability.
    The capital payable maps to non-tax other current liabilities. Retirement
    loss maps to product cost. These are unadmitted mapping assumptions.
    All other activities, shares, OCI and distributions are fixed.
    """
    if q < 1000:
        raise ValueError('H2 expense-liability amount would be negative')
    d = {key: Fraction(0) for key in rows}
    expense_delta = (q - 1000) - q
    d['operations.products_cost'] += delta['retirement_loss']
    d[expense_row] += expense_delta
    d['operations.cost'] = d['operations.products_cost'] + d['operations.services_cost']
    d['operations.gross_margin'] = -d['operations.cost']
    d['operations.operating_expenses'] = d['operations.research'] + d['operations.selling']
    d['operations.operating_income'] = d['operations.gross_margin'] - d['operations.operating_expenses']
    d['operations.pretax'] = d['operations.operating_income'] + d['operations.other_income']
    d['operations.tax'] = Fraction(extra_tax)
    profit = d['operations.pretax'] - d['operations.tax']
    for key in ['operations.net_income', 'comprehensive.net_income',
                'comprehensive.comprehensive_income', 'equity.net_income',
                'equity.retained_closing', 'equity.closing', 'balance.retained',
                'balance.equity', 'cash_flow.net_income']:
        d[key] = profit
    for suffix in ['basic', 'diluted']:
        # Profit is USD millions; shares are reported in thousands.
        d['operations.eps_' + suffix] = 1000 * profit / Fraction(rows['operations.shares_' + suffix]['value'])
    d['balance.ppe'] = delta['ppe_cost'] + delta['accumulated_depreciation']
    d['balance.cash'] = delta['cash']
    d['balance.assets_current'] = d['balance.cash']
    d['balance.assets_noncurrent'] = d['balance.ppe']
    d['balance.assets'] = d['balance.assets_current'] + d['balance.assets_noncurrent']
    d['balance.other_liabilities_current'] += -delta['capital_payable'] + extra_tax
    d[liability_row] += expense_delta
    d['balance.liabilities_current'] = d['balance.payables'] + d['balance.other_liabilities_current']
    d['balance.liabilities_noncurrent'] = d['balance.other_liabilities_noncurrent']
    d['balance.liabilities'] = d['balance.liabilities_current'] + d['balance.liabilities_noncurrent']
    d['balance.liabilities_equity'] = d['balance.liabilities'] + d['balance.equity']
    # The exact same accrual is allocated once between the two adjustments.
    d['cash_flow.other_adjustments'] = delta['retirement_loss'] + alpha * expense_delta
    working_delta = expense_delta * (1 if duplicate else 1 - alpha)
    working_row = 'cash_flow.payables' if liability_row == 'balance.payables' else 'cash_flow.other_liabilities'
    d[working_row] = working_delta + extra_tax
    d['cash_flow.depreciation'] = delta['depreciation_expense']
    d['cash_flow.operating'] = sum(d[k] for k in [
        'cash_flow.net_income', 'cash_flow.depreciation', 'cash_flow.compensation',
        'cash_flow.other_adjustments', 'cash_flow.receivables', 'cash_flow.vendor_receivables',
        'cash_flow.inventory', 'cash_flow.other_assets', 'cash_flow.payables',
        'cash_flow.other_liabilities'])
    d['cash_flow.ppe_payments'] = delta['cash']
    d['cash_flow.investing'] = d['cash_flow.ppe_payments']
    d['cash_flow.change'] = d['cash_flow.operating'] + d['cash_flow.investing'] + d['cash_flow.financing']
    d['cash_flow.closing'] = d['cash_flow.change']
    return d

def serialize(d):
    return {k: int(v) if v.denominator == 1 else str(v) for k, v in d.items()}

arms = []
for alpha in [Fraction(0), Fraction(1, 2), Fraction(1)]:
    d = report(alpha)
    checks['alpha=' + str(alpha) + ':balance'] = d['balance.assets'] == d['balance.liabilities_equity']
    checks['alpha=' + str(alpha) + ':CFO'] = d['cash_flow.operating'] == 0
    checks['alpha=' + str(alpha) + ':other'] = d['cash_flow.other_adjustments'] == 1000 * (1 - alpha)
    checks['alpha=' + str(alpha) + ':working'] = d['cash_flow.other_liabilities'] == -1000 * (1 - alpha)
    arms.append({'alpha': str(alpha), 'delta': serialize(d),
                 'changed_rows': [k for k,v in d.items() if v],
                 'same_rows': not any(d.values())})
checks['ordinary_mapping_rejected'] = arms[0]['changed_rows'] == ['cash_flow.other_adjustments', 'cash_flow.other_liabilities']
checks['full_noncash_mapping_conditional_pass'] = arms[2]['same_rows']
checks['five_statement_population'] = {r['statement'] for r in rows.values()} == {
    'operations', 'comprehensive', 'balance', 'equity', 'cash_flow'}
checks['102_annual_rows'] = len(rows) == 102
checks['q_boundary'] = report(Fraction(1), q=1000) == report(Fraction(1), q=4000)
try:
    report(Fraction(1), q=999)
    checks['negative_hypothesis_rejected'] = False
except ValueError:
    checks['negative_hypothesis_rejected'] = True
counterexamples = {}
for label, kwargs in [
    ('different_expense_rows', {'expense_row': 'operations.research'}),
    ('different_liability_rows', {'liability_row': 'balance.payables'}),
    ('duplicated_noncash_addback', {'duplicate': True}),
    ('different_tax_consequences', {'extra_tax': 100}),
]:
    d = report(Fraction(1), **kwargs)
    counterexamples[label] = {k:v for k,v in serialize(d).items() if v}
checks['expense_mismatch_detected'] = counterexamples['different_expense_rows']['operations.products_cost'] == 1000 and counterexamples['different_expense_rows']['operations.research'] == -1000
checks['liability_mismatch_detected'] = counterexamples['different_liability_rows']['balance.payables'] == -1000 and counterexamples['different_liability_rows']['balance.other_liabilities_current'] == 1000
checks['duplicated_addback_detected'] = counterexamples['duplicated_noncash_addback']['cash_flow.operating'] == -1000
checks['tax_mismatch_detected'] = counterexamples['different_tax_consequences']['operations.net_income'] == -100
checks['EPS_unit_conversion'] = report(Fraction(1), extra_tax=100)['operations.eps_basic'] == Fraction(-100000, 15343783)
counterexamples['different_gross_asset_classes'] = {'machinery_gross': 1000, 'buildings_gross': -1000, 'gross_total': 0}
checks['gross_class_mismatch_detected'] = sum(counterexamples['different_gross_asset_classes'].values()) == 0 and counterexamples['different_gross_asset_classes']['machinery_gross'] != 0
tax = json.loads((ROOT / 'data/accounting-master/apple-tax-20261009/source-claim-supplement.json').read_text())
for name in ['annual_detail_current', 'annual_detail_noncurrent']:
    table = tax['support_tables'][name]['rows']
    for i in [0,1]:
        checks[name + ':column:' + str(i)] = table[0]['values'][i] + table[1]['values'][i] == table[2]['values'][i]
checks['operating_lease_liability'] = 1488 + 10046 == 11534
checks['finance_lease_liability'] = 144 + 752 == 896
checks['total_lease_liability'] = 11534 + 896 == 12430
checks['lease_ROU_distinct_population'] = 10234 + 1069 == 11303
save('conditional-repair.json', {
    'claimed_target': 'Conditional annual row-preserving difference transformation relative to an assumed feasible base',
    'computed': 'Journal-derived H2-H1 plus an independently hypothesized expense-liability amount difference; exact rational reporting maps',
    'verdict': 'Equal in the alpha=1 conditional map; alpha=0 and alpha=1/2 differ in two reported rows. Actual full completion is not established.',
    'units': 'USD millions except EPS/share rows retaining source units',
    'hypothetical_accruals': {'H1': 2000, 'H2': 1000, 'general_domain': 'q >= 1000', 'posting': 'Dr expense / Cr separate non-tax liability', 'evidence_status': 'independent economic premise missing; not a residual-derived event'},
    'source_row_count': len(rows), 'unchanged_activities': 'All other report primitives, share counts, distributions and OCI fixed by hypothesis; zero rows are consequences of this scope, not independent empirical observations.',
    'arms': arms, 'counterexamples': counterexamples,
    'note_conditions': ['Extra acquired and retired cost belong to the same gross PP&E class.', 'The two liabilities share the same Note 6 non-tax bucket.', 'Lease quantities, shares and commitments are held fixed; no offset is assigned to their separately disclosed populations.', 'Current/deferred tax bases and expense match; equal pretax profit alone does not establish this.'],
    'interim_status': 'Annual equality gives no settlement date or subsequent expense. Full annual/interim joint completion remains unresolved.',
    'source_admission': 'unresolved_missing_events_mappings_tax_and_base',
    'nonconclusions': ['No actual Apple provision, capital payable, retirement or release inferred.', 'No absolute feasible company history is constructed.', 'No current-authority, probability, forecast or completeness claim.']})
failed = [k for k,v in checks.items() if not v]
save('source-arithmetic-checks.json', {'checks':checks, 'passed':sum(checks.values()), 'failed':failed})
print(json.dumps({'passed':sum(checks.values()), 'failed':failed, 'conditional_alpha_1':arms[2]['same_rows'], 'ordinary_changed_rows':arms[0]['changed_rows'], 'actual_completion':'unresolved'}))
raise SystemExit(bool(failed))
