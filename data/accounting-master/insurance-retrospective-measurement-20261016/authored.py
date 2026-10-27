"""Independent full/modified measurements and prior-basis bridges."""
from pathlib import Path
from copy import deepcopy
import hashlib,json
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
def ff(*keys):return {k:True for k in keys}
common=ff('scope_nonparticipating','grouping_supported','complete_cash_including_expired','zero_rates_supported','no_tax_fx_oci','equal_service_units_supported','no_changes_in_remaining_expectations','no_incurred_unpaid_claims','prior_basis_balances_supported','transition_cash_unchanged')
def request(route='full',premium='120',claims='30'):
    q=dict(wire='InsuranceRetrospective/1',operation='report',context=dict(entity='Synthetic Insurer',group='G1',currency='CU',unit='currency units',rule='EU2023/1803-original-IFRS17'),route=route,
        dates=dict(acquisition_payment='2020-12-31',recognition='2021-01-01',transition='2022-01-01',initial_application='2023-01-01'),
        cash_history=dict(capital='100',premium_received=premium,acquisition_paid='10',claims_paid=claims,reinsurance_premium_paid='0',recoveries_received='0'),
        measurement=dict(remaining_claims='60',remaining_ra='4',rate='0',coverage_units_past='1',coverage_units_remaining='2'),
        acquisition=dict(allocation_mode='supported',recognized_group='6',future_group='4',findings=ff('allocation_supported','future_asset_recoverable','same_post_transition_allocation_method')),
        history=None,modified=None,treaty=None,prior_basis=dict(liability='80',acquisition_asset='10',held_asset='0'),findings=deepcopy(common))
    if route=='full':q['history']=dict(initial_claims='90',initial_ra='6',expected_past_claim_release='30',expected_past_ra_release='2',information_date='2021-01-01',findings=ff('contemporaneous_information','no_hindsight','full_retrospective_practicable'))
    else:q['modified']=dict(modifications=['C12','C14','C15b','C14B'],similar_contract_past_ra_release='2',information_date='2022-01-01',findings=ff('full_retrospective_impracticable','reasonable_supportable_modified_information','c12_history_unavailable','c14_history_unavailable','c15b_history_unavailable','acquisition_modification_admitted','similar_contract_ra_supported','maximise_available_retrospective_information'))
    return q
cases=[]
for route in ('full','modified'):
    q=request(route)
    cases.append(dict(id=route+'-baseline',request=q,expected=dict(initial=dict(expected_claims='90',ra='6',acquisition_adjustment='6',csm='18',loss_component='0'),transition=dict(cash='180',fcf='64',csm='12',loss_component='0',liability='76',acquisition_asset='4',held_asset='0',equity='108',oci='0'),prior_equity='110',equity_adjustment='-2',known_acquisition_cash='10')))
    q=request(route,claims='35')
    cases.append(dict(id=route+'-different-claims-experience',request=q,expected=dict(initial=dict(expected_claims='90' if route=='full' else '95',csm='18' if route=='full' else '13'),transition=dict(cash='175',fcf='64',csm='12' if route=='full' else '26/3',liability='76' if route=='full' else '218/3',equity='103' if route=='full' else '319/3'),prior_equity='105',equity_adjustment='-2' if route=='full' else '4/3')))
q=request('modified');q['acquisition']=dict(allocation_mode='C14D_nil',recognized_group=None,future_group=None,findings=ff('c14b_information_unavailable','c14d_applies'));q['modified']['modifications'][-1]='C14D'
cases.append(dict(id='modified-acquisition-information-nil',request=q,expected=dict(initial=dict(acquisition_adjustment='0',csm='24'),transition=dict(cash='180',fcf='64',csm='16',liability='80',acquisition_asset='0',equity='100'),prior_equity='110',equity_adjustment='-10',known_acquisition_cash='10')))
for route in ('full','modified'):
    q=request(route,premium='80');q['prior_basis']['liability']='70'
    cases.append(dict(id=route+'-onerous',request=q,expected=dict(initial=dict(csm='0',loss_component='22'),transition=dict(cash='140',fcf='64',csm='0',loss_component='44/3',liability='64',acquisition_asset='4',equity='80'),prior_equity='80',equity_adjustment='0')))
    q=deepcopy(q);q['cash_history'].update(reinsurance_premium_paid='49',recoveries_received='15');q['prior_basis']['held_asset']='30'
    q['treaty']=dict(quota='1/2',initial_ra='3',remaining_ra='2',recovery_mode='supported',information_date='2021-01-01' if route=='full' else '2022-01-01',findings=ff('timely_treaty','all_claims_covered','quota_terms_supported','separate_ra_supported','ordinary_held_measurement_supported','same_service_pattern','loss_recovery_supported'))
    cases.append(dict(id=route+'-onerous-treaty',request=q,expected=dict(transition=dict(cash='106',fcf='64',loss_component='44/3',liability='64',acquisition_asset='4',held_asset='40',held_fcf='32',held_cost_csm='8',loss_recovery='22/3',equity='86'),held=dict(ordinary_initial_cost_csm='1',ordinary_remaining_cost_csm='2/3'),prior_equity='76',equity_adjustment='10')))
q=deepcopy(cases[-1]['request']);q['treaty']['recovery_mode']='C16C_none';q['treaty']['findings'].pop('loss_recovery_supported');q['treaty']['findings'].update(c16a_information_unavailable=True,c16c_applies=True)
cases.append(dict(id='modified-unavailable-recovery-information',request=q,expected=dict(transition=dict(cash='106',liability='64',held_asset='98/3',held_fcf='32',held_cost_csm='2/3',loss_recovery='0',acquisition_asset='4',equity='236/3'),prior_equity='76',equity_adjustment='8/3')))
def main():
    p=OUT/'authored-cases.json';assert not p.exists()
    p.write_text(json.dumps(dict(cases=cases),indent=2)+'\n')
    paths=['docs/plans/accounting-insurance-retrospective-measurement-20261016.md','docs/design/research/p08-v3-preparation/eu-2023-1803-original.txt',str(p.relative_to(ROOT)),
           'docs/design/proposal/manuscript-insurance-service-finance-origins-20261016/sections/insurance-methods.tex']
    (OUT/'input-lock.json').write_text(json.dumps(dict(files=[dict(path=p,sha256=hashlib.sha256((ROOT/p).read_bytes()).hexdigest()) for p in paths]),indent=2)+'\n')
    print(json.dumps(dict(cases=len(cases),protected_inputs=len(paths))))
if __name__=='__main__':main()
