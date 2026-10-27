"""Authored expectations from retained worked methods, independent of verifier."""
from copy import deepcopy
from fractions import Fraction as F

CASES=[]
FIND=dict(finding_supported=True,finding_evidence='synthetic-conditional-finding')
EXTRAS=dict(fees=0,servicing=False,prior_oci=0)
VALUE=dict(measurement_available=True,measurement_evidence='supplied-valuation')
CASH=dict(cash_evidence='confirmed-cash')

def case(name,tag,c,asset=0):
    ca=dict(id=name,tag=tag,currency='USD',source_family='AU_AASB',opening_component=c,
            opening_balances=dict(cash=200,transferred_asset=asset,capital=-200-asset),steps=[])
    CASES.append(ca);return ca

def step(ca,method,date,p,patch,j=None,cash=None,oci=0,equity=None):
    old=ca['steps'][-1]['after'] if ca['steps'] else ca['opening_component']
    after=deepcopy(old);after.update(patch)
    ca['steps'].append(dict(method=method,event_date=date,parameters=p,after=after,
        journal=j or {},cash_change=cash or {},oci_change={'fair_value':oci},equity_change=equity or {}))

def transfer():
    return dict(contract_id='illustrative-transfer',phase='unassessed',initial_asset=100,asset=100,
       liability=0,principal_funding=0,sold_fv=0,retained_fv=0,asset_rate=F(1,10),liability_rate=F(1,10),
       accrual_date='2025-01-01',asset_accrued=False,liability_accrued=False,finding_evidence=None)

ca=case('partial-relative-values','transfer',transfer(),100)
step(ca,'transfer.partial','2024-01-01',dict(**FIND,**EXTRAS,**CASH,sold_fv=45,retained_fv=55,
     proceeds=46,eligible_part=True,derecognition_supported=True,nontrading_investment=True),
     dict(asset=55,sold_fv=45,retained_fv=55,phase='partial',finding_evidence=FIND['finding_evidence']),
     dict(cash=46,transferred_asset=-45,disposal_gain=-1),dict(investing=46))

ca=case('retained-risk-borrowing','transfer',transfer(),100)
step(ca,'transfer.retain_risks','2024-01-01',dict(**FIND,**EXTRAS,**CASH,proceeds=46),
     dict(liability=46,principal_funding=46,phase='funded',finding_evidence=FIND['finding_evidence']),
     dict(cash=46,transfer_liability=-46),dict(financing=46))
step(ca,'transfer.asset_income','2025-01-01',dict(original_eir_supported=True),
     dict(asset=110,asset_accrued=True),dict(transferred_asset=10,asset_interest_income=-10))
step(ca,'transfer.liability_expense','2025-01-01',dict(separate_eir_supported=True),
     dict(liability=F(253,5),liability_accrued=True),dict(transfer_liability=F(-23,5),liability_interest_expense=F(23,5)))
step(ca,'transfer.repay','2025-01-01',dict(**CASH,amount=F(253,5),interest_component=F(23,5),
     contractual_interest_allocation_supported=True,discharge_supported=True),
     dict(liability=0,phase='settled'),dict(cash=F(-253,5),transfer_liability=F(253,5)),
     dict(financing=-46,operating=F(-23,5)))

ca=case('guarantee-no-claim','guarantee',dict(contract_id='illustrative-guarantee',phase='unassessed',
     initial_asset=100,asset=100,liability=0,allowance=0,cap=0,initial_fee=0,service_fraction=0,
     expiry_date='2024-12-31',finding_evidence=None),100)
step(ca,'guarantee.start','2024-01-01',dict(**FIND,**EXTRAS,**CASH,**VALUE,proceeds=103,cap=20,
     guarantee_fv=3,continuing_involvement_supported=True),
     dict(asset=20,liability=23,cap=20,initial_fee=3,phase='active',finding_evidence=FIND['finding_evidence']),
     dict(cash=103,transferred_asset=-80,transfer_liability=-23),dict(unclassified=103))
step(ca,'guarantee.service','2024-05-01',dict(cumulative_fraction=F(1,3),equal_service_performed=True,
     revenue_method_admitted=True,service_evidence='four-month-service'),
     dict(liability=22,service_fraction=F(1,3)),dict(transfer_liability=1,guarantee_income=-1))
step(ca,'guarantee.measure_loss','2024-06-30',dict(**VALUE,expected_loss=2),
     dict(allowance=2),dict(loss_allowance=-2,impairment_expense=2))
step(ca,'guarantee.expire','2024-12-31',dict(no_claim_supported=True,rights_expired=True,expiry_evidence='no-claim-expiry'),
     dict(asset=0,liability=0,allowance=0,phase='expired',service_fraction=1),
     dict(loss_allowance=2,impairment_expense=-2,transferred_asset=-20,transfer_liability=22,guarantee_income=-2))

def option(kind,s,kc,kp,tc,tp):
    return dict(contract_id='illustrative-'+kind,kind=kind,phase='unassessed',initial_asset=s,
       asset=s,liability=0,spot=s,call_strike=kc,put_strike=kp,call_time=tc,put_time=tp,
       expiry_date='2025-12-31',finding_evidence=None)

def option_start(ca,s,tc,tp,proceeds,a,l):
    step(ca,'option.start','2024-01-01',dict(**FIND,**EXTRAS,**CASH,**VALUE,spot=s,call_time=tc,put_time=tp,
         proceeds=proceeds,continuing_involvement_supported=True,zero_day_one_gain_supported=True),
         dict(asset=a,liability=l,phase='active',finding_evidence=FIND['finding_evidence']),
         dict(cash=proceeds,transferred_asset=a-s,transfer_liability=-l),dict(unclassified=proceeds))

ca=case('fv-call','option',option('call',80,95,0,5,0),80)
option_start(ca,80,5,0,75,80,75)
step(ca,'option.remeasure','2024-12-31',dict(**VALUE,spot=100,call_time=4,put_time=0),
     dict(asset=100,liability=91,spot=100,call_time=4),dict(transferred_asset=20,transfer_liability=-16,fair_value_gain=-4))
step(ca,'option.expire','2025-12-31',dict(**VALUE,spot=110,call_time=0,put_time=0,rights_expired=True,expiry_evidence='option-expiry'),
     dict(asset=110,liability=95,spot=110,call_time=0,phase='expired'),
     dict(transferred_asset=10,transfer_liability=-4,fair_value_gain=-6))
step(ca,'option.exercise','2025-12-31',dict(**CASH,side='call',amount=95,physical_settlement_supported=True),
     dict(liability=0,phase='exercised'),dict(cash=-95,transfer_liability=95),dict(unclassified=-95))

ca=case('fv-put','option',option('put',120,0,100,0,5),120)
option_start(ca,120,0,5,125,100,105)
step(ca,'option.remeasure','2024-12-31',dict(**VALUE,spot=90,call_time=0,put_time=4),
     dict(asset=90,liability=104,spot=90,put_time=4),dict(transferred_asset=-10,transfer_liability=1,fair_value_expense=9))
step(ca,'option.expire','2025-12-31',dict(**VALUE,spot=80,call_time=0,put_time=0,rights_expired=True,expiry_evidence='option-expiry'),
     dict(asset=80,liability=100,spot=80,put_time=0,phase='expired'),
     dict(transferred_asset=-10,transfer_liability=4,fair_value_expense=6))
step(ca,'option.exercise','2025-12-31',dict(**CASH,side='put',amount=100,physical_settlement_supported=True),
     dict(liability=0,phase='exercised'),dict(cash=-100,transfer_liability=100),dict(unclassified=-100))

for branch in ['upper','lower']:
    ca=case('fv-collar-'+branch,'option',option('collar',100,120,80,5,1),100)
    option_start(ca,100,5,1,96,100,96)
    if branch=='upper':
        step(ca,'option.remeasure','2024-12-31',dict(**VALUE,spot=130,call_time=2,put_time=1),
             dict(asset=130,liability=119,spot=130,call_time=2),
             dict(transferred_asset=30,transfer_liability=-23,fair_value_gain=-7))
        step(ca,'option.expire','2025-12-31',dict(**VALUE,spot=130,call_time=0,put_time=0,rights_expired=True,expiry_evidence='option-expiry'),
             dict(liability=120,call_time=0,put_time=0,phase='expired'),dict(transfer_liability=-1,fair_value_expense=1))
        side,price='call',120
    else:
        step(ca,'option.remeasure','2024-12-31',dict(**VALUE,spot=70,call_time=1,put_time=2),
             dict(asset=70,liability=81,spot=70,call_time=1,put_time=2),
             dict(transferred_asset=-30,transfer_liability=15,fair_value_expense=15))
        step(ca,'option.expire','2025-12-31',dict(**VALUE,spot=70,call_time=0,put_time=0,rights_expired=True,expiry_evidence='option-expiry'),
             dict(liability=80,call_time=0,put_time=0,phase='expired'),dict(transfer_liability=1,fair_value_gain=-1))
        side,price='put',80
    step(ca,'option.exercise','2025-12-31',dict(**CASH,side=side,amount=price,physical_settlement_supported=True),
         dict(liability=0,phase='exercised'),dict(cash=-price,transfer_liability=price),dict(unclassified=-price))

ca=case('ac-option-separate-rates','ac_option',dict(contract_id='illustrative-ac-option',phase='unassessed',
     asset=98,liability=0,asset_terminal=100,liability_terminal=100,asset_rate=F(1,49),liability_rate=F(1,19),
     strike=102,accrual_date='2025-01-01',asset_accrued=False,liability_accrued=False,
     zero_allowance_isolation=True,finding_evidence=None),98)
step(ca,'ac_option.start','2024-01-01',dict(**FIND,**EXTRAS,**CASH,proceeds=95,zero_allowance_isolation_supported=True),
     dict(liability=95,phase='active',finding_evidence=FIND['finding_evidence']),dict(cash=95,transfer_liability=-95),dict(unclassified=95))
step(ca,'ac_option.accrue_asset','2025-01-01',dict(original_eir_supported=True,zero_allowance_isolation_supported=True),
     dict(asset=100,asset_accrued=True),dict(transferred_asset=2,asset_interest_income=-2))
step(ca,'ac_option.accrue_liability','2025-01-01',dict(separate_eir_supported=True),
     dict(liability=100,liability_accrued=True),dict(transfer_liability=-5,liability_interest_expense=5))
step(ca,'ac_option.exercise','2025-01-01',dict(**CASH,amount=102,physical_settlement_supported=True),
     dict(liability=0,phase='exercised'),dict(cash=-102,transfer_liability=100,liability_interest_expense=2),dict(unclassified=-102))

def investment(instrument='debt'):
    return dict(contract_id='illustrative-investment',instrument=instrument,phase='unassessed',classification='pending',
        business_model='unknown',sppi='unknown',fvtpl_designated=False,equity_elected=False,assessment_evidence=None,
        asset=0,allowance=0,ecl=0,reserve=0,probe_contractual=0,probe_benchmark=0,probe_status='not_run',reserve_transferred=False)

for route in ['AC','debt_FVOCI','FVTPL','equity_FVOCI','mismatch_FVTPL','equity_FVTPL','sppi_FVTPL']:
    instrument='equity' if route.startswith('equity') else 'debt'
    ca=case('investment-'+route,'asset',investment(instrument))
    model='collect_sell' if route=='debt_FVOCI' else 'other' if route=='FVTPL' else 'collect' if instrument=='debt' else 'unknown'
    elected=route=='equity_FVOCI';designated=route=='mismatch_FVTPL'
    assessed='fail' if route=='sppi_FVTPL' else 'pass' if instrument=='debt' else 'not_applicable'
    classification='FVTPL' if route in ['mismatch_FVTPL','equity_FVTPL','sppi_FVTPL'] else route
    step(ca,'asset.classify','2024-01-01',dict(business_model=model,sppi=assessed,assessment_evidence='supplied-classification',
         equity_election=elected,held_for_trading=False,initial_recognition=True,fvtpl_designation=designated,
         mismatch_eligible=True if designated else None),
         dict(classification=classification,business_model=model,sppi=assessed,fvtpl_designated=designated,
              equity_elected=elected,assessment_evidence='supplied-classification',phase='classified'))
    step(ca,'asset.acquire','2024-01-01',dict(**CASH,cost=100,fees=0,nontrading_investment=True),
         dict(asset=100,phase='held'),dict(cash=-100,transferred_asset=100),dict(investing=-100))
    if classification!='AC':
        reserve=0 if classification=='FVTPL' else -2
        j=dict(transferred_asset=-2,**({'fair_value_expense':2} if classification=='FVTPL' else {'fair_value_reserve':2}))
        step(ca,'asset.remeasure','2024-12-31',dict(**VALUE,fair_value=98),dict(asset=98,reserve=reserve),j,oci=reserve)
    if classification in ['AC','debt_FVOCI']:
        step(ca,'asset.impair','2024-12-31',dict(**VALUE,expected_loss=3),
             dict(ecl=3,allowance=3 if classification=='AC' else 0,reserve=1 if classification=='debt_FVOCI' else 0),
             dict(impairment_expense=3,**({'loss_allowance':-3} if classification=='AC' else {'fair_value_reserve':-3})),
             oci=3 if classification=='debt_FVOCI' else 0)
    j=dict(cash=98,transferred_asset=-100,loss_allowance=3,disposal_gain=-1) if classification=='AC' else (
      dict(cash=98,transferred_asset=-98,fair_value_reserve=1,disposal_gain=-1) if classification=='debt_FVOCI' else dict(cash=98,transferred_asset=-98))
    step(ca,'asset.dispose','2025-01-01',dict(**CASH,proceeds=98,rights_transferred=True),
         dict(asset=0,allowance=0,ecl=0,phase='disposed',**({'reserve':0} if classification=='debt_FVOCI' else {})),
         j,dict(investing=98),oci=-1 if classification=='debt_FVOCI' else 0)
    if classification=='equity_FVOCI':
        step(ca,'asset.transfer_reserve','2025-01-01',dict(within_equity_elected=True),
             dict(reserve=0,reserve_transferred=True),dict(fair_value_reserve=-2,retained=2),
             equity=dict(reserve_transfer=2,retained_transfer=-2))

ca=case('modified-time-value-probe','asset',investment())
step(ca,'asset.time_value_probe','2024-01-01',dict(principal=100,contract_rate=F(3,25),benchmark_rate=F(3,50),
     months=6,matched_benchmark_supported=True,scenario_evidence='single-supplied-scenario'),
     dict(probe_contractual=106,probe_benchmark=103,probe_status='explanatory_only'))
