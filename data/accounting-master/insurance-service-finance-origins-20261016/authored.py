"""Independent analytic targets; does not import the reference calculator."""
from pathlib import Path
from fractions import Fraction as Q
from copy import deepcopy
import hashlib,json
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
def ff(*keys):return {k:True for k in keys}
def req(op,data):return dict(wire='InsuranceOrigins/1',operation=op,
    context=dict(entity='Synthetic Insurer',group='G1',currency='CU',unit='currency units',rule='EU2023/1803-original-IFRS17'),
    findings=ff('source_profile_applicable','opening_balances_supported','complete_events','information_view_valid','no_tax_fx_or_unrecorded_cash'),data=data)
cases=[]
loss=dict(opening_date='2025-01-01',cash='200',liability='100',loss_component='20',
    findings=ff('proportional_allocation_supported','csm_zero','no_new_estimates','claim_ra_releases_supported','all_finance_in_profit','no_investment_or_acquisition_component'),
    periods=[dict(date='2026-01-01',information_date='2026-01-01',finance_expense='10',claim_release='50',ra_release='5',actual_claims='50',coverage_end=False),
             dict(date='2027-01-01',information_date='2027-01-01',finance_expense='-5',claim_release='45',ra_release='5',actual_claims='45',coverage_end=True)])
cases.append(dict(id='loss-service-finance',request=req('loss_schedule',loss),expected=dict(total_service_profit='10',total_finance_expense='5',total_profit='5',
    rows=[dict(liability='55',loss_component='11',cash='150',equity='95',loss_finance='2',claim_loss_release='10',ra_loss_release='1',loss_reversal='11',revenue='44',profit='-5'),
          dict(liability='0',loss_component='0',cash='105',equity='105',loss_finance='-1',claim_loss_release='9',ra_loss_release='1',loss_reversal='10',revenue='40',profit='10')])))
d=deepcopy(loss);d['loss_component']='0'
cases.append(dict(id='zero-loss-boundary',request=req('loss_schedule',d),expected=dict(total_profit='5',rows=[dict(loss_component='0',loss_reversal='0',revenue='55',profit='-5'),dict(loss_component='0',loss_reversal='0',revenue='50',profit='10') ])))
d=dict(cash='247/2',issued_claims='118',issued_ra='2',issued_loss='20',covered_claims='48',covered_loss='8',quota='1/2',held_ra='1/2',held_cost_csm='6',held_loss_recovery='4',covered_claim_decrease='4',
    findings=ff('timely_treaty','covered_loss_allocation_supported','zero_rates','no_other_changes','full_remaining_service','quota_terms_supported'))
cases.append(dict(id='recovery-change-once',request=req('recovery_change',d),expected=dict(opening_equity='34',total_profit='-5/2',
    change=dict(issued_liability='116',issued_loss='16',held_asset='57/2',held_cost_csm='6',held_loss_recovery='2',issued_loss_reversal='4',held_profit='-2',additional_component_expense='0',equity='36'),
    issued_service=dict(revenue='100',loss_reversal='16',claim_expense='114',profit='2'),held_service=dict(recovery='22',premium_allocation='53/2',loss_recovery_reversal='2',profit='-13/2'),closing=dict(cash='63/2',equity='63/2',issued_liability='0',held_asset='0'))))
d=deepcopy(d);d['covered_claim_decrease']='8'
cases.append(dict(id='covered-loss-exhausted',request=req('recovery_change',d),expected=dict(total_profit='-1/2',change=dict(issued_loss='12',held_asset='53/2',held_loss_recovery='0',held_profit='-4',additional_component_expense='0',equity='38'),closing=dict(cash='67/2',equity='67/2'))))
switch_findings=ff('direct_participation_at_origin','holding_change_supported','old_assumptions_supported','no_remaining_service_csm_ra','frozen_assumptions','comparatives_unchanged','post_change_cash_supported','underlying_measurement_supported')
def period(year,L,ap,ao,held):return dict(date=f'{year}-01-01',information_date=f'{year}-01-01',current_liability=L,asset_profit_income=ap,asset_oci_income=ao,actual_holdings=held,findings=ff('valuation_supported','all_changes_financial','no_interim_cash'))
for name,L,ao in [('matching-lower-current','130','-10/11'),('matching-higher-current','132','12/11')]:
    d=dict(date='2025-01-01',old_policy='88b',new_policy='89b',terminal='144',years=2,old_current_rate='1/10',old_allocation_rate='1/5',old_allocation_carrying='100',old_oci='-2300/121',post_change_cash='200',new_allocation_rate=None,
        periods=[period(2026,L,'1440/121',ao,True),period(2027,'144','1584/121',str(-Q(ao)),True)],findings=deepcopy(switch_findings))
    cases.append(dict(id=name,request=req('policy_switch',d),expected=dict(initial_liability='14400/121',total_profit='-2300/121',total_oci='2300/121',
        rows=[dict(old_reclassification_expense='980/121',old_oci='-120/11',counterfactual_current='1440/11',counterfactual_allocation='120',current_profit_expense='1440/121',current_oci=str(-Q(ao)),profit='-980/121'),
              dict(old_reclassification_expense='120/11',old_oci='0',new_oci='0',asset_oci='0',counterfactual_current='144',counterfactual_allocation='144',profit='-120/11')],closing=dict(cash='200',equity='200',liability='0',asset='0'))))
d=dict(date='2025-01-01',old_policy='89b',new_policy='88b',terminal='121',years=2,old_current_rate='0',old_allocation_rate='1/10',old_allocation_carrying='100',old_oci='-21',post_change_cash='200',new_allocation_rate='0',
    periods=[period(2026,'130','0','0',False),period(2027,'121','0','0',False)],findings=deepcopy(switch_findings))
cases.append(dict(id='former-matching-runoff',request=req('policy_switch',d),expected=dict(initial_liability='121',total_profit='-21',total_oci='21',
    rows=[dict(old_reclassification_expense='10',old_oci='-11',current_profit_expense='0',current_oci='-9',profit='-10',oci='1',equity='70'),
          dict(old_reclassification_expense='11',old_oci='0',current_oci='9',profit='-11',oci='20',equity='79')],closing=dict(cash='79',equity='79',liability='0'))))
for policy in ('88b','89b'):
    for sign in (-1,1):
        O=Q(sign*12);rec=O if policy=='88b' else Q(0)
        d=dict(origin_policy=policy,accumulated_oci=str(O),cash='200',other_assets='0',liability='100',transfer_cash='100',
            findings=ff('paragraph91_event','homogeneous_oci_origin','transfer_at_carrying','no_remaining_service_csm_ra','other_assets_unchanged','no_pending_policy_runoff'))
        cases.append(dict(id='derecognize-'+policy+'-'+str(sign),request=req('derecognize',d),expected=dict(profit_reclassification=str(rec),oci_reclassification=str(-rec),total_equity_change='0',closing=dict(cash='100',liability='0',equity='100',oci=str(O-rec)))))
def main():
    if (OUT/'authored-cases.json').exists():raise SystemExit('Frozen cases exist')
    (OUT/'authored-cases.json').write_text(json.dumps(dict(cases=cases),indent=2)+'\n')
    paths=['docs/plans/accounting-insurance-service-finance-origins-20261016.md','docs/design/research/p08-v3-preparation/eu-2023-1803-original.txt',str((OUT/'authored-cases.json').relative_to(ROOT)),
           'docs/design/proposal/manuscript-dated-credit-schedules-20261016/sections/insurance-treaty-changes.tex','docs/design/proposal/manuscript-dated-credit-schedules-20261016/sections/insurance-finance-process.tex']
    (OUT/'input-lock.json').write_text(json.dumps(dict(files=[dict(path=p,sha256=hashlib.sha256((ROOT/p).read_bytes()).hexdigest()) for p in paths]),indent=2)+'\n')
    print(json.dumps(dict(cases=len(cases),protected_inputs=len(paths))))
if __name__=='__main__':main()
