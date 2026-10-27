from pathlib import Path
from fractions import Fraction as F
import hashlib
import json

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
CANDIDATE = ROOT / 'docs/design/proposal/manuscript-release-prep-v552r1-20261027'
fixture = ROOT / 'docs/design/fixtures/sectors.json'
data = json.loads(fixture.read_text())
checks = []
def check(name, actual, expected):
    checks.append({'name': name, 'actual': str(actual), 'expected': str(expected), 'pass': actual == expected})
def values(d):
    return {k: F(v) for k, v in d.items()}

b = data['bank']; o = values(b['opening']); e = values(b['events'])
bank = dict(cash=o['cash'] - e['external_transfer'] + e['loan_interest_cash'],
            gross_loans=o['gross_loans'] + e['origination'], allowance=e['allowance_target'],
            deposits=o['deposits'] + e['origination'] - e['external_transfer'] + e['deposit_interest_accrued'],
            equity=o['equity'] + e['loan_interest_cash'] - e['deposit_interest_accrued'] - (e['allowance_target'] - o['allowance']))
for k, v in bank.items(): check('bank_' + k, v, F(b['expected_before_runoff'][k]))
check('bank_identity', bank['cash'] + bank['gross_loans'] - bank['allowance'], bank['deposits'] + bank['equity'])
draw = min(F(b['facility_limit']), max(F(0), F(b['runoff']) - bank['cash']))
check('bank_draw', draw, F(b['expected_draw']))
check('bank_runoff_cash', bank['cash'] + draw - F(b['runoff']), F(b['expected_cash']))
check('bank_runoff_deposits', bank['deposits'] - F(b['runoff']), F(b['expected_deposits']))
check('bank_unpaid', max(F(0), F(b['default_runoff']) - bank['cash'] - F(b['facility_limit'])), F(b['expected_unpaid']))
check('illustrative_capital', bank['equity'] - F(b['regulatory_deduction']), F(b['expected_CET1']))
check('illustrative_RWA', bank['gross_loans'] * F(b['risk_weight']), F(b['expected_RWA']))

i = data['insurer']; x = values({k: v for k, v in i.items() if k != 'expected'})
revenue = x['premium'] * x['service_fraction']; ceded = x['ceded_premium'] * x['service_fraction']
gross = x['gross_claim_estimate'] + x['gross_risk_adjustment']
recovery = x['gross_claim_estimate'] * x['recovery_fraction'] + x['ceded_risk_adjustment']
ins = dict(cash=x['opening_equity'] + x['premium'] - x['ceded_premium'] - x['gross_claim_paid'] + x['recovery_paid'],
           remaining_coverage_liability=x['premium'] - revenue, incurred_claim_liability=gross - x['gross_claim_paid'],
           reinsurance_coverage_asset=x['ceded_premium'] - ceded, reinsurance_claim_asset=recovery - x['recovery_paid'],
           profit=revenue - gross - ceded + recovery)
ins.update(equity=x['opening_equity'] + ins['profit'], assets=ins['cash'] + ins['reinsurance_coverage_asset'] + ins['reinsurance_claim_asset'], liabilities=ins['remaining_coverage_liability'] + ins['incurred_claim_liability'])
for k, v in ins.items(): check('insurer_' + k, v, F(i['expected'][k]))
check('insurer_identity', ins['assets'], ins['liabilities'] + ins['equity'])

g = data['consolidation']; x = values({k: v for k, v in g.items() if k != 'expected'})
group = dict(cash=x['parent_cash'] + x['sub_cash'], plant=x['sub_plant'], owners_equity=x['parent_equity'], NCI=x['sub_equity'] * (1 - x['ownership']))
group['assets'] = group['cash'] + group['plant']
for k, v in group.items(): check('group_' + k, v, F(g['expected'][k]))
check('group_identity', group['assets'], group['owners_equity'] + group['NCI'])
check('group_intragroup_cash_invariant', x['parent_cash'] - x['intercompany_loan'] + x['sub_cash'] + x['intercompany_loan'], group['cash'])
check('group_disposal_gain', x['disposal_proceeds'] + group['NCI'] - x['sub_equity'], x['expected_disposal_gain'])
check('group_after_disposal_cash', x['parent_cash'] + x['disposal_proceeds'], x['expected_after_disposal_cash'])

reviews = [
 {'id': 'MC06', 'original_scope_verdict': 'The original condition requires dated control/adjustment types and acquisition/disposal/intragroup examples. It does not require every acquisition to arise from debt conversion.',
  'inspected': ['chapters/14-financing-groups.tex: Control and an elimination book', 'sections/group-bindings.tex: dated legal books, GroupForeignOperation/1, separate disposal branches and unknown-input behavior'],
  'supported': 'Existing explicit acquisition, reciprocal loan elimination and disposal arithmetic is present; the later group-binding text supplies date/control/book/currency owners and complete reported movement requirements.',
  'missing': 'Consolidate the selected group profile with the common source/history/report contract and independently review its stated accounting premises. Any promoted conversion-to-control path additionally needs its missing allocation/control evidence.',
  'selected_extension': 'Measured debt conversion-to-control remains open; it is a dependent-claim blocker, not the sole admissible acquisition example.'},
 {'id': 'MC21', 'original_scope_verdict': 'The original condition calls for bank structure, later-operation methods, accounting/prudential reconciliation and an appropriate worked case. Positive post-write-off recovery is not individually prescribed.',
  'inspected': ['chapters/15-banking.tex: opening structural scope; cash, allowance and capital worked path; following measurement interface'],
  'supported': 'The worked case separates loan/deposit creation, settlement cash, loss allowance, deposit runoff, bounded funding and unpaid obligations. Its supplied capital deduction and risk weight are explicitly illustrative.',
  'missing': 'Consolidate bank structural records and funding/credit/liquidity/capital method interfaces with explicit later-operation boundaries, and review the selected case and actual authority applicability. Positive recovery remains unsupported where factual admission is missing.',
  'selected_extension': 'Positive recovery admission is an additional operation/dependent claim. Its local evidence gap does not erase the existing worked bank case.'},
 {'id': 'MC22', 'original_scope_verdict': 'The original condition requires cohort/group state, movement attribution, declared measurement, separate reinsurance and a complete structural/roll-forward example. It does not uniquely prescribe the newest recovery-change stages.',
  'inspected': ['chapters/16-insurance.tex: cohort API and Insurance service and reinsurance in a complete cohort'],
  'supported': 'The one-year coverage example supplies a complete opening-to-half-year measurement under stated PAA assumptions, keeping gross and ceded identities, claims, service and cash separate. Exact endpoint arithmetic reconciles.',
  'missing': 'Bind the complete selected roll-forward to one explicit dated group/profile/report interface and inspect source applicability and actuarial/accounting assumptions. The half-year example is not silently promoted into evidence of every full-year lifecycle or the newer dated recovery interaction.',
  'selected_extension': 'The newer issued/held recovery-change join remains open. It is not automatically the only permissible example of the original roll-forward condition.'}
]
inputs = [fixture] + [CANDIDATE / p for p in ['chapters/14-financing-groups.tex', 'sections/group-bindings.tex', 'chapters/15-banking.tex', 'chapters/16-insurance.tex']]
result = {'date': '2026-10-27', 'reviews': reviews, 'checks': checks, 'pass': all(c['pass'] for c in checks), 'input_hashes': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}, 'evidence_class': 'Inspected manuscript scope and independent exact arithmetic from retained fixture inputs; no new authoritative accounting decision or broad acceptance', 'plan': str((HERE / 'consolidation-plan.md').relative_to(ROOT))}
(HERE / 'acceptance-case-review.json').write_text(json.dumps(result, indent=2) + chr(10))
old = ROOT / 'data/accounting-master/acceptance-priority-20261027/release-acceptance.json'
acceptance = json.loads(old.read_text())
acceptance['candidate'] = '5.52-R1 protected release-preparation successor; not_ready'
acceptance['predecessor'] = {'path': str(old.relative_to(ROOT)), 'sha256': hashlib.sha256(old.read_bytes()).hexdigest()}
acceptance['scope'] += ' Additive case-selection review corrects MC06/21/22 next-action classification without changing original acceptance wording or granting acceptance.'
for row in acceptance['rows']:
    match = next((r for r in reviews if r['id'] == row['id']), None)
    if match:
        row['previous_disposition'] = {k: row.get(k) for k in ['disposition', 'unresolved_subcondition', 'residual_status', 'current_actions', 'acceptance_reason']}
        row['necessary_condition_review'] = match
        row['current_supported_scope'] += ' ' + match['supported']
        # Preserve historical fields verbatim; consumers use explicit current review.
        row['current_release_disposition'] = 'design_partial_internal_consolidation_and_independent_acceptance_required; selected extension source gap remains local'
        row['current_missing_condition'] = match['missing']
        row['disposition'] = 'design_partial_internal_consolidation_and_independent_acceptance_required'
        row['unresolved_subcondition'] = match['missing']
        row['residual_status'] = 'internal_work_required; selected_extension_source_gap_local'
        row['acceptance_reason'] = match['original_scope_verdict'] + ' No broad acceptance or waiver.'
        row['current_actions'] = [{'phase': 'C2/C3/C4', 'action': match['missing'], 'evidence': 'data/accounting-master/release-plan-execution-20261027/acceptance-case-review.json'}]
        row['current_review_evidence'] = 'data/accounting-master/release-plan-execution-20261027/acceptance-case-review.json'
(HERE / 'release-acceptance.json').write_text(json.dumps(acceptance, indent=2) + chr(10))
lines = ['# Existing case evidence and necessary release conditions', '', '27 October 2026. Additive C0 review; no MC requirement waived or accepted.', '']
for r in reviews:
    lines += ['## ' + r['id'], '', r['original_scope_verdict'], '', r['supported'], '', '**Remaining requirement:** ' + r['missing'], '', '**Additional path:** ' + r['selected_extension'], '', 'Inspected: ' + '; '.join(r['inspected']), '']
lines += ['The ' + str(len(checks)) + ' exact arithmetic checks pass. They test the stated examples and expected fixtures, not recognition authority or general sector completeness. No original acceptance string changed. All non-reviewed rows retain their prior evidence and unresolved status.']
(HERE / 'acceptance-case-review.md').write_text(chr(10).join(lines) + chr(10))
lines = ['# Current release acceptance with reviewed case selection', '', 'Use release-acceptance.json for all original conditions. The preceding index remains unchanged. Current reviews of MC06/21/22 are in acceptance-case-review.md; their source gaps are local to the selected extension.', '']
for row in acceptance['rows']:
    lines += ['## ' + row['id'], '', str(row.get('current_supported_scope', '')), '', '**Current missing condition:** ' + str(row.get('current_missing_condition', row.get('missing_condition', row.get('unresolved_subcondition', 'Retain exact prior condition; see JSON.')))), '', '**Decision:** ' + str(row.get('current_release_disposition', row.get('decision', row.get('disposition', 'No broad acceptance; see exact prior record.')))), '']
(HERE / 'release-acceptance.md').write_text(chr(10).join(lines) + chr(10))
print(json.dumps({'pass': result['pass'], 'checks': len(checks), 'reviewed_requirements': [r['id'] for r in reviews], 'broad_acceptances': 0}))
