"""Exact documentary examples; no insurance runtime or stochastic experiment."""
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
checks, groups = [], {}


def ck(name, actual, expected):
    checks.append(dict(name=name, actual=str(actual), expected=str(expected), passed=actual == expected))


def journal(name, values):
    ck(name + '/balanced', sum(values.values()), 0)
    return {k: str(v) for k, v in values.items()}


# GMM, no interval accrual/FX/tax/OCI: a new contract is required by para72.
# Old FCF100 = claims90 + RA10; removed FCF40 = claims36 + RA4.
# New obligations52 = claims48 + RA4; equivalent premium60, actual extra10.
old_fcf, old_csm, removed, equivalent, extra, new_fcf = map(F, [100, 30, 40, 60, 10, 52])
deemed = equivalent-extra
csm_delta = removed-deemed
old_after = old_fcf-removed+old_csm+csm_delta
new_csm = equivalent-new_fcf
new_after = new_fcf+new_csm
ck('modification/deemed-premium', deemed, 50)
ck('modification/old-csm-change', csm_delta, -10)
ck('modification/old-csm', old_csm+csm_delta, 20)
ck('modification/old-lrc', old_after, 80)
ck('modification/new-csm', new_csm, 8)
ck('modification/new-lrc', new_after, 60)
ck('modification/liabilities', old_after+new_after, 140)
ck('modification/cash-equity', 200+extra-old_after-new_after, 70)
ck('modification/old-coverage-units', 3-1, 2)
ck('modification/old-full-service-profit', old_after-54, 26)
ck('modification/new-full-service-profit', new_after-48, 12)
ck('modification/closing-cash', 200+extra-54-48, 108)
ck('modification/closing-equity', 70+26+12, 108)
ck('modification/wrong-pro-rata-csm', (30-30*F(40,100))-(old_csm+csm_delta), -2)
groups['contract_modification'] = {
    'deemed_premium': str(deemed), 'old_lrc': str(old_after), 'new_lrc': str(new_after),
    'internal_transfer': journal('modification/transfer', {'debit-old-lrc': 50, 'credit-new-lrc': -50}),
    'actual_cash': journal('modification/cash', {'debit-cash': 10, 'credit-new-lrc': -10}),
    'closing_cash_equity': 108,
}

# Transfer is a distinct actual cash payment, with the same adjustment50.
ck('transfer/remaining-lrc', 100-40+30+(40-50), 80)
ck('transfer/cash', 200-50, 150)
ck('transfer/equity', 150-80, 70)
# Insufficient CSM: -10 uses6, then service loss4; LC is inside LRC.
ck('modification/insufficient-csm-loss', max(deemed-removed-6, F(0)), 4)
ck('modification/onerous-old-lrc', 100-40, 60)
ck('modification/onerous-equity', 210-(60+60), (200-106)-4)
groups['transfer_and_margin_exhaustion'] = {
    'transfer': journal('transfer/cash', {'debit-old-lrc': 50, 'credit-cash': -50}),
    'low_margin_old_csm': 0, 'low_margin_loss_component': 4,
    'low_margin_service_loss': 4, 'low_margin_new_csm': 8,
    'OCI_disposal': {'88b': 'recycle allocated remaining OCI', '89b': 'do not recycle'},
}

# One-year PAA; zero LRC financing under56, premium120 and acquisition12.
# Uniform risk/service, no claim before coverage end; future-claim assumptions
# exclude an onerous trigger in the base. At end, LIC PV40 + RA2.
cash = F(200+120-12)
deferred_lrc = F(120-12)
expensed_lrc = F(120)
ck('paa/cash-after-acquisition', cash, 308)
ck('paa/deferred-initial-equity', cash-deferred_lrc, 200)
ck('paa/expensed-initial-equity', cash-expensed_lrc, 188)
deferred_mid = deferred_lrc+6-60
expensed_mid = expensed_lrc-60
ck('paa/deferred-mid-lrc', deferred_mid, 54)
ck('paa/expensed-mid-lrc', expensed_mid, 60)
ck('paa/deferred-mid-profit', cash-deferred_mid-200, 54)
ck('paa/expensed-mid-profit', cash-expensed_mid-200, 48)
ck('paa/end-deferred-lrc', deferred_mid+6-60, 0)
ck('paa/end-expensed-lrc', expensed_mid-60, 0)
ck('paa/end-coverage-equity', cash-(40+2), 200+120-12-42)
ck('paa/onerous-addition', F(70)-deferred_mid, 16)
ck('paa/onerous-total-lrc', deferred_mid+16, 70)
ck('paa/wrong-full-addition-overstates', deferred_mid+70-70, 54)
groups['paa_acquisition_and_onerous'] = {
    'mid_lrc': {'deferred': 54, 'expensed': 60}, 'coverage_end_cash': 308,
    'coverage_end_LRC': 0, 'coverage_end_LIC': 42, 'coverage_end_equity': 266,
    'deferred_cost': journal('paa/defer', {'debit-lrc': 12, 'credit-cash': -12}),
    'cost_amortisation': journal('paa/amortise', {'debit-acquisition-expense': 6, 'credit-lrc': -6}),
    'onerous': journal('paa/onerous', {'debit-service-loss': 16, 'credit-lrc': -16}),
}

# Claim incurred at coverage end, settlement two years later. Claim-incurrence
# rate10%; group's inception rate5% is not the LIC OCI allocation rate.
# Current rate falls to0 after one year and stays0. RA2 releases1 each year,
# wholly in service result; no finance disaggregation of RA is used.
claim = F(242,5)
pv0 = claim/F(11,10)**2
shadow1 = pv0*F(11,10)
shadow2 = shadow1*F(11,10)
ck('paa-lic/initial-pv', pv0, 40)
ck('paa-lic/locked-first-finance', shadow1-pv0, 4)
ck('paa-lic/current-first-finance', claim-pv0, F(42,5))
ck('paa-lic/first-oci-expense', claim-shadow1, F(22,5))
ck('paa-lic/year1-total-liability', claim+1, F(247,5))
ck('paa-lic/year1-equity', cash-claim-1, F(1293,5))
ck('paa-lic/second-profit-finance', shadow2-shadow1, F(22,5))
ck('paa-lic/second-oci-income', shadow2-shadow1, claim-shadow1)
ck('paa-lic/terminal-shadow', shadow2, claim)
ck('paa-lic/cumulative-finance', (shadow1-pv0)+(shadow2-shadow1), F(42,5))
ck('paa-lic/closing-cash', cash-claim, F(1298,5))
ck('paa-lic/lifetime-profit', 120-12-42+2-F(42,5), cash-claim-200)
ck('paa-lic/wrong-inception-rate-first-finance', pv0*F(5,100), 2)
groups['paa_claim_finance'] = {
    'claim': str(claim), 'initial_PV': str(pv0), 'initial_RA': 2,
    'finance_profit_expenses': ['4', '22/5'], 'finance_OCI_expenses': ['22/5', '-22/5'],
    'RA_service_releases': [1, 1], 'closing_cash_equity': str(cash-claim),
    'year1': journal('paa/lic-year1', {'debit-finance-profit': 4, 'debit-finance-oci': F(22,5),
                                     'credit-lic-finance': -F(42,5)}),
}

# Admitted direct participation; underlying100, policyholder80%, remaining
# nonfinancial claims10 and RA2, two equal coverage units, no rates/FX/tax.
u0, u1, share = F(100), F(120), F(4,5)
fcf0 = share*u0+10+2
csm0 = u0-fcf0
fcf1 = share*u1+10+2
csm1 = csm0+(1-share)*(u1-u0)
ck('vfa/initial-fcf', fcf0, 92)
ck('vfa/initial-csm', csm0, 8)
ck('vfa/remeasured-fcf', fcf1, 108)
ck('vfa/remeasured-csm', csm1, 12)
ck('vfa/total-liability-finance', fcf1+csm1-(fcf0+csm0), 20)
ck('vfa/asset-finance-offset', (u1-u0)-20, 0)
release = csm1/2
revenue = 5+1+release
ck('vfa/first-revenue', revenue, 12)
ck('vfa/first-service-profit', revenue-5, 7)
ck('vfa/first-lrc', 96+5+1+(csm1-release), 108)
ck('vfa/first-equity', 195+120-108, 207)
ck('vfa/final-investment-component', share*u1, 96)
ck('vfa/final-cash', 200-5-5+120-96, 214)
ck('vfa/final-equity', 200+2*(revenue-5), 214)
ck('vfa/non-revenue-investment-repayment', 96, share*u1)
ck('vfa/matching-profit-finance', 8-8, 0)
ck('vfa/matching-oci-finance', 12-12, 0)
ck('vfa/matching-total-finance', 8+12, 20)
groups['vfa_service_and_finance'] = {
    'before_service': {'FCF': 108, 'CSM': 12, 'LRC': 120},
    'first_service': {'revenue': 12, 'claim_expense': 5, 'cash': 195,
                      'underlying_asset': 120, 'LRC': 108, 'equity': 207},
    'closing_cash_equity': 214, 'investment_component_repayment': 96,
    'finance_matching_alternative': {'underlying_profit': 8, 'underlying_OCI': 12,
                                    'insurance_profit_expense': 8, 'insurance_OCI_expense': 12},
}

# Separate branches from the initial VFA position, before service.
shock = F(15)
loss = shock-csm0
ck('vfa-loss/loss', loss, 7)
ck('vfa-loss/liability', fcf0+shock, 107)
ck('vfa-loss/equity', 300-107, 200-loss)
ck('vfa-loss/after-first-reversal-component', loss-6, 1)
ck('vfa-loss/after-first-reversal-liability', fcf0+shock-6, 101)
ck('vfa-loss/further-reversal-csm', 4-(loss-6), 3)
ck('vfa-loss/final-liability', fcf0+shock-6-4+3, 100)
ck('mitigation/without-csm', csm0-6, 2)
ck('mitigation/without-liability', fcf0+6+csm0-6, 100)
ck('mitigation/without-equity', 300+6-100, 206)
ck('mitigation/with-liability', fcf0+6+csm0, 106)
ck('mitigation/with-equity', 300+6-106, 200)
ck('mitigation/with-net-profit', 6-6, 0)
groups['vfa_loss_and_risk_mitigation'] = {
    'adverse_cost_loss_component': 7, 'reversal_sequence': [6, 4], 'final_CSM': 3,
    'financial_guarantee_increase': 6, 'derivative_gain': 6,
    'without_mitigation': {'CSM': 2, 'LRC': 100, 'equity': 206},
    'with_eligible_mitigation': {'CSM': 8, 'LRC': 106, 'equity': 200},
}

# B132, no remaining service/CSM/nonfinancial risk: revised nominal benefit144,
# current PV discounted10%, shadow100, two years remaining. Revised constant
# allocation rate20%, not the former10% that would accrue to121.
expected, shadow0, rate, current_rate = F(144), F(100), F(1,5), F(1,10)
current0 = expected/(1+current_rate)**2
current1 = expected/(1+current_rate)
shadow1 = shadow0*(1+rate)
shadow2 = shadow1*(1+rate)
initial_oci = current0-shadow0
oci1 = (current1-current0)-(shadow1-shadow0)
oci2 = (expected-current1)-(shadow2-shadow1)
ck('variable-finance/current-PV', current0, F(14400,121))
ck('variable-finance/initial-OCI-expense', initial_oci, F(2300,121))
ck('variable-finance/first-profit-expense', shadow1-shadow0, 20)
ck('variable-finance/second-profit-expense', shadow2-shadow1, 24)
ck('variable-finance/first-OCI-expense', oci1, -F(980,121))
ck('variable-finance/second-OCI-expense', oci2, -F(120,11))
ck('variable-finance/lifetime-OCI', initial_oci+oci1+oci2, 0)
ck('variable-finance/lifetime-profit-finance', shadow2-shadow0, 44)
ck('variable-finance/wrong-original-rate-terminal', shadow0*F(11,10)**2, 121)
ck('variable-finance/wrong-terminal-shortfall', expected-shadow0*F(11,10)**2, 23)
ck('variable-finance/final-equity', 200-expected, 100-44)
groups['variable_payment_finance'] = {
    'revised_benefit': '144', 'current_PV': str(current0), 'shadow_rate': '1/5',
    'profit_expenses': ['20', '24'], 'OCI_expenses': [str(initial_oci), str(oci1), str(oci2)],
    'closing_cash_equity': 56,
}

# Full finite joint family: each claim is0 or40 with probability1/2.
# Let a=P(40,40). Marginals force P(0,0)=a and cross-cells=1/2-a.
laws = []
for name, a in [('opposite', F(0)), ('independent', F(1,4)), ('together', F(1,2))]:
    law = [(0, 0, a), (0, 40, F(1,2)-a), (40, 0, F(1,2)-a), (40, 40, a)]
    ck(f'law/{name}/normalisation', sum(p for _, _, p in law), 1)
    ck(f'law/{name}/first-mean', sum(x*p for x, _, p in law), 20)
    ck(f'law/{name}/second-mean', sum(y*p for _, y, p in law), 20)
    ck(f'law/{name}/aggregate-mean', sum((x+y)*p for x, y, p in law), 40)
    recovery = sum(max(x+y-60, 0)*p for x, y, p in law)
    ck(f'law/{name}/stop-loss', recovery, 20*a)
    conditional_high = a/F(1,2)
    conditional_low = (F(1,2)-a)/F(1,2)
    ck(f'law/{name}/conditional-second-high', conditional_high, 2*a)
    ck(f'law/{name}/conditional-second-low', conditional_low, 1-2*a)
    ck(f'law/{name}/conditional-recovery', F(1,2)*(20*conditional_high), recovery)
    laws.append(dict(name=name, a=str(a), expected_claim='40', expected_recovery=str(recovery),
                     second_high_given_first_high=str(conditional_high),
                     second_high_given_first_low=str(conditional_low)))
ck('law/plug-in-mean-recovery', max(40-60, 0), 0)
ck('law/exact-recovery-lower', 20*F(0), 0)
ck('law/exact-recovery-upper', 20*F(1,2), 10)
groups['joint_process_law'] = {'support': [0, 40], 'joint_probability_interval': ['0', '1/2'],
                              'laws': laws, 'expected_recovery_interval': ['0', '10'],
                              'weights_between_laws': 'unspecified; not a probability mixture'}

sources = [ROOT/'docs/design/research/p08-v3-preparation'/name
           for name in ['eu-2023-1803-original.pdf', 'eu-2023-1803-original.txt']]
result = dict(passed=all(c['passed'] for c in checks), count=len(checks), group_count=len(groups),
              groups=groups, checks=checks,
              sources=[dict(path=str(p.relative_to(ROOT)), sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sources],
              evidence_role='Exact conditional insurance derivations; no calibration, simulated experiment or runtime execution')
(OUT/'cases.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps({k: result[k] for k in ['passed', 'count', 'group_count']}))
assert result['passed'], [c for c in checks if not c['passed']]
