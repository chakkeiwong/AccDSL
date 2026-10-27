from pathlib import Path
from copy import deepcopy
import hashlib,json
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
keys=['compatible_historical_profiles','legal_opening_supported','control_retained','equal_ordinary_rights','no_goodwill_or_purchase_difference','event_rates_exact','tax_law_supplied','loss_dta_recovery_supported','guarantee_tax_deductible_as_booked','outside_basis_exception_supported','no_tax_on_translation','deposit_cash_equivalent','deposit_counterpart_verified','no_deposit_interest_or_movements','no_other_events','parent_cost_investment_policy','guarantee_ifrs9_scope','guarantee_ecl_supported','guarantee_service_release_supported','operating_cash_policy_supported']
deposit=dict(id='D1',creditor='I',debtor='B',currency='FCU',amount='20',cutoff='both-period-closes')
keys+=['contractual_cash_allocation_supported','opening_guarantee_measurement_supported']
q=dict(wire='SectorCompany/1',operation='report',context=dict(group='G',parent='P',bank='B',insurer='I',presentation_currency='USD',foreign_currency='FCU',rule='EU2023/1803-original',periods=['2025-01-01/2026-01-01','2026-01-01/2027-01-01']),
    opening=dict(parent_cash='500',bank_cash='300',bank_deposits='200',insurer_cash='200',insurance_liability='100',parent_investment_bank='80',parent_investment_insurer='80'),
    rates=dict(opening='1',period1_event='11/10',period1_close='6/5',period2_event='5/4',period2_close='13/10'),tax_rate='1/5',
    ownership=dict(bank_initial='4/5',insurer='4/5',bank_after='9/10',purchase_price='15',purchase_timing='after_period1_close'),
    deposit=dict(bank_record=deepcopy(deposit),insurer_record=deepcopy(deposit)),
    guarantee=dict(id='EXT-G1',beneficiary='external_creditor',opening_unamortized='6',income_releases=['2','2'],ecl=['7','3']),
    loan_cash_allocation=[dict(principal='50',coupon_interest='5'),dict(principal='52',coupon_interest='17/2')],
    component_maps=dict(bank=dict(source_entity='Synthetic Bank',target_entity='B',source_currency='CU',target_currency='FCU',unit_scale='1',opening_capital_action='ignore_component_capital'),insurance=dict(source_entity='Synthetic Insurer',target_entity='I',source_currency='CU',target_currency='FCU',unit_scale='1',opening_capital_action='ignore_component_capital')),
    findings={k:True for k in keys})
cases=[dict(id='joined-sector-group',request=q,expected=dict(opening=dict(cash='980',equity='694',parent_equity='654',nci='40'),rows=[
    dict(legal=dict(P=dict(cash='485',investments='175',dta='1/5',guarantee='7',equity='3266/5'),B=dict(cash='253',loan='55',dta='0',deposits='200',equity='108'),I=dict(cash='150',dta='1',insurance_liability='55',equity='96')),
        group=dict(cash='4723/5',assets='1012',liabilities='289',equity='723',parent_equity='687',nci='36',profit='18/5',oci='202/5',parent_profit='68/25',nci_profit='22/25',parent_oci='808/25',nci_oci='202/25',bank_profit='44/5',bank_oci='104/5',insurer_profit='-22/5',insurer_oci='98/5'),
        ownership=dict(nci_removed='324/25',parent_equity_transaction='-51/25',cash='-15'),cash_flow=dict(opening='980',operating='-967/10',financing='-15',fx='763/10',closing='4723/5'),deposit_elimination=dict(cash='24',deposits='24',cash_fx='4')),
    dict(legal=dict(P=dict(cash='2422/5',investments='175',dta='0',guarantee='3',equity='3282/5'),B=dict(cash='1562/5',loan='0',dta='0',deposits='200',equity='562/5'),I=dict(cash='104',dta='0',insurance_liability='0',equity='104')),
        group=dict(cash='24993/25',assets='24993/25',liabilities='237',equity='19068/25',parent_equity='180267/250',nci='10413/250',profit='187/10',oci='1051/50',parent_profit='323/20',nci_profit='51/20',parent_oci='8959/500',nci_oci='1551/500',bank_profit='11/2',bank_oci='551/50',insurer_profit='10',insurer_oci='10'),
        cash_flow=dict(opening='4723/5',operating='323/20',financing='0',fx='3897/100',closing='24993/25'),deposit_elimination=dict(cash='26',deposits='26',cash_fx='2'))]))]
r=deepcopy(q);r['rates']={k:'1' for k in r['rates']}
cases.append(dict(id='constant-fx',request=r,expected=dict(rows=[dict(group=dict(cash='868',equity='3411/5',parent_equity='3261/5',nci='30',profit='16/5',oci='0'),cash_flow=dict(operating='-97',financing='-15',fx='0')),
    dict(group=dict(cash='4404/5',equity='3489/5',parent_equity='16644/25',nci='801/25',profit='78/5',oci='0'),cash_flow=dict(operating='64/5',financing='0',fx='0'))])))
r=deepcopy(q);r['ownership'].update(bank_after='4/5',purchase_price='0')
cases.append(dict(id='unchanged-ownership',request=r,expected=dict(rows=[dict(group=dict(cash='4798/5',equity='738',nci='1224/25',parent_equity='17226/25'),ownership=dict(nci_removed='0',parent_equity_transaction='0',cash='0')),
    dict(group=dict(cash='25368/25',equity='19443/25',nci='7033/125',parent_equity='90182/125'))])))

def main():
    target=OUT/'authored-cases.json';assert not target.exists();target.write_text(json.dumps(dict(cases=cases),indent=2)+'\n')
    paths=['docs/plans/accounting-sector-company-composition-20261016.md','docs/design/research/p08-v3-preparation/eu-2023-1803-original.txt',str(target.relative_to(ROOT))]
    for folder,names in [('dated-credit-schedules-20261016',['reference.py','bounds.py','authored-cases.json','input-lock.json']),('insurance-service-finance-origins-20261016',['reference.py','authored-cases-v2.json','input-lock-v2.json'])]:
        for name in names:paths.append('data/accounting-master/'+folder+'/'+name)
    (OUT/'input-lock.json').write_text(json.dumps(dict(files=[dict(path=p,sha256=hashlib.sha256((ROOT/p).read_bytes()).hexdigest()) for p in paths]),indent=2)+'\n')
    print(json.dumps(dict(cases=len(cases),protected_inputs=len(paths))))
if __name__=='__main__':main()
