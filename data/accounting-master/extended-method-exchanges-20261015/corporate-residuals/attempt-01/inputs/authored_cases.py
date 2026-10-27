"""Separately authored expected amounts; never imports financial reconstruction."""
from copy import deepcopy
from fractions import Fraction as F
CASES=[]
def case(name,tag,state,balances):
    ca=dict(id=name,tag=tag,currency='USD',source_family='EU_IFRS',opening_component=deepcopy(state),opening_balances=balances,steps=[])
    CASES.append(ca);return ca
def step(ca,method,p,j=None,change=None,when='2024-06-30',cash=None,oci=None,equity=None):
    s=deepcopy(ca['steps'][-1]['after'] if ca['steps'] else ca['opening_component']);s.update(deepcopy(change or {}))
    ca['steps'].append(dict(method=method,parameters=deepcopy(p),journal=j or {},after=s,event_date=when,
        cash_change=cash or {},oci_change=oci or {},equity_change=equity or {}))

# A=2(12-3-1)=16, L=2*20=40. Actual handling is expensed only once.
return_state=dict(contract_id='return-contract',sold_units=10,expected_units=2,unit_refund=20,unit_cost=12,
    estimated_handling=3,estimated_deterioration=1,refund=40,recovery=16,inventory=0,settled=False)
for name,r,j,inventory,paid in [
 ('return-expected',2,dict(refund_liability=40,recovery_asset=-16,inventory=20,cash=-48,cost_of_sales=-4,cost_expense=8),20,48),
 ('return-fewer',1,dict(refund_liability=40,recovery_asset=-16,inventory=10,cash=-24,revenue=-20,cost_of_sales=6,cost_expense=4),10,24),
 ('return-more',3,dict(refund_liability=40,recovery_asset=-16,inventory=30,cash=-72,revenue=20,cost_of_sales=-14,cost_expense=12),30,72),
 ('return-nrv-cap',2,dict(refund_liability=40,recovery_asset=-16,inventory=14,cash=-48,cost_of_sales=2,cost_expense=8),14,48)]:
    c=case(name,'rcost',return_state,dict(cash=100,recovery_asset=16,refund_liability=-40,original_equity=-76))
    step(c,'rcost.settle',dict(actual_units=r,unit_handling=4,unit_deterioration=2,refund_cash=r*20,handling_cash=r*4,
        inventory_nrv=inventory,all_rights_closed=True,handling_is_selling_cost=True),j,
        dict(refund=0,recovery=0,inventory=inventory,settled=True),cash={'operating':-paid})

assets=[dict(asset_id='A',carrying=40,no_impairment=100,recoverable_cap=45),dict(asset_id='B',carrying=60,no_impairment=150,recoverable_cap=150)]
c=case('cgu-cap-redistribution','cgu',dict(cgu_id='cgu1',assets=assets,goodwill=10),dict(cash=100,ppe=100,goodwill=10,original_equity=-210))
step(c,'cgu.reverse',dict(recoverable=170,changed_estimates=True,passage_only=False),dict(ppe=60,other_gains=-60),
    dict(assets=[{**assets[0],'carrying':45},{**assets[1],'carrying':115}]))
zero_assets=[dict(asset_id='A',carrying=0,no_impairment=30,recoverable_cap=30),dict(asset_id='B',carrying=0,no_impairment=70,recoverable_cap=70)]
c=case('cgu-zero-no-reversal','cgu',dict(cgu_id='zero-cgu',assets=zero_assets,goodwill=0),dict(cash=100,original_equity=-100))
step(c,'cgu.reverse',dict(recoverable=0,changed_estimates=True,passage_only=False))
c=case('individual-zero-reversal','individual',dict(asset_id='individual1',carrying=0,no_impairment=80),dict(cash=100,original_equity=-100))
step(c,'individual.reverse',dict(recoverable=120,changed_estimates=True,cost_model=True),dict(ppe=80,other_gains=-80),dict(carrying=80))

rights=[dict(right_id='A',rou=90,liability=100,rate=F(1,10),last_measurement_date='2024-01-01'),
    dict(right_id='B',rou=30,liability=50,rate=F(1,10),last_measurement_date='2024-01-01')]
c=case('heterogeneous-rights','lease',dict(lease_id='lease1',rights=rights),dict(cash=200,rou=120,lease_liability=-150,original_equity=-170))
p=dict(allocation_basis='traced_right_amounts',standalone_allocation_supported=True,annual_end_payments=True,
    rights=[dict(right_id='A',removed_rou=0,removed_liability=0,full_termination=False,new_rate=F(1,10),payments=[121]),
            dict(right_id='B',removed_rou=30,removed_liability=50,full_termination=True,new_rate=F(1,10),payments=[])])
r1=[{**rights[0],'rou':100,'liability':110},{**rights[1],'rou':0,'liability':0}]
step(c,'lease.reduce',p,dict(rou=-20,lease_liability=40,other_gains=-20),dict(rights=r1),when='2024-01-01')
p2=deepcopy(p);p2['rights'][0].update(removed_rou=10,removed_liability=11,payments=[99]);p2['rights'][1].update(removed_rou=0,removed_liability=0)
r2=[{**r1[0],'rou':81,'liability':90},r1[1]]
step(c,'lease.reduce',p2,dict(rou=-19,lease_liability=20,other_gains=-1),dict(rights=r2),when='2024-01-01')
r3=[{**r2[0],'liability':0,'last_measurement_date':'2025-01-01'},r2[1]]
step(c,'lease.pay',dict(right_id='A',amount=99,one_year_elapsed=True,no_intervening_accrual_or_modification=True),
    dict(cash=-99,finance_expense=9,lease_liability=90),dict(rights=r3),when='2025-01-01',cash=dict(operating=-9,financing=-90))
step(c,'lease.depreciate',dict(right_id='A',amount=81,systematic_allocation_supported=True),dict(rou=-81,depreciation=81),
    dict(rights=[{**r3[0],'rou':0},r3[1]]),when='2025-01-01')

cost_state=dict(contract_id='service-contract',lot_id='fulfilment1',kind='fulfilment',asset=0,no_impairment=0,remaining_units=5,cgu_review_pending=False)
incur=dict(amount=100,kind='fulfilment',nature='fulfilment',other_standard='none',incremental=False,directly_related=True,future_resources=True,recoverable=True)
c=case('fulfilment-cost-life','cost',cost_state,dict(cash=300,original_equity=-300))
step(c,'cost.incur',{**incur,'amount':5,'nature':'waste'},dict(cost_expense=5,cash=-5),cash={'operating':-5})
step(c,'cost.incur',incur,dict(contract_cost=100,cash=-100),dict(asset=100,no_impairment=100),cash={'operating':-100})
step(c,'cost.amortize',dict(delivered_units=1,equal_unit_pattern_supported=True),dict(contract_cost=-20,amortization=20),dict(asset=80,no_impairment=80,remaining_units=4))
step(c,'cost.impair',dict(credit_adjusted_consideration=70,remaining_direct_cost=20,other_impairments_done=True),
    dict(contract_cost=-30,impairment_expense=30),dict(asset=50,cgu_review_pending=True))
step(c,'cost.amortize',dict(delivered_units=1,equal_unit_pattern_supported=True),dict(contract_cost=F(-25,2),amortization=F(25,2)),
    dict(asset=F(75,2),no_impairment=60,remaining_units=3))
step(c,'cost.reverse',dict(credit_adjusted_consideration=100,remaining_direct_cost=10,other_impairments_done=True,changed_circumstances=True),
    dict(contract_cost=F(45,2),impairment_expense=F(-45,2)),dict(asset=60))
step(c,'cost.amortize',dict(delivered_units=3,equal_unit_pattern_supported=True),dict(contract_cost=-60,amortization=60),dict(asset=0,no_impairment=0,remaining_units=0))
c=case('acquisition-cost-life','cost',{**cost_state,'lot_id':'acquisition1','kind':'acquisition','remaining_units':3},dict(cash=200,original_equity=-200))
step(c,'cost.incur',{**incur,'kind':'acquisition','amount':30,'nature':'incremental','incremental':True},dict(contract_cost=30,cash=-30),dict(asset=30,no_impairment=30),cash={'operating':-30})
step(c,'cost.incur',{**incur,'kind':'acquisition','amount':40,'nature':'incremental','incremental':False},dict(cost_expense=40,cash=-40),cash={'operating':-40})
step(c,'cost.amortize',dict(delivered_units=3,equal_unit_pattern_supported=True),dict(contract_cost=-30,amortization=30),dict(asset=0,no_impairment=0,remaining_units=0))

c=case('successive-distinct','distinct',dict(contract_id='distinct1',remaining_units=8,remaining_consideration=80,revenue=20,unbilled=20,revision=0),
    dict(cash=100,contract_asset=20,revenue=-20,original_equity=-100))
mp=dict(added_units=4,added_consideration=60,remaining_distinct=True,added_distinct=True,priced_at_ssp=False)
step(c,'distinct.modify',mp,change=dict(remaining_units=12,remaining_consideration=140,revision=1))
step(c,'distinct.perform',dict(units=3),dict(contract_asset=35,revenue=-35),dict(remaining_units=9,remaining_consideration=105,revenue=55,unbilled=55))
step(c,'distinct.modify',{**mp,'added_units':3,'added_consideration':30},change=dict(remaining_units=12,remaining_consideration=135,revision=2))
step(c,'distinct.perform',dict(units=12),dict(contract_asset=135,revenue=-135),dict(remaining_units=0,remaining_consideration=0,revenue=190,unbilled=190))
c=case('successive-integrated','integrated',dict(contract_id='integrated1',total_consideration=200,progress=F(1,4),revenue=50,unbilled=50,revision=0),
    dict(cash=100,contract_asset=50,revenue=-50,original_equity=-100))
step(c,'integrated.modify',dict(new_total=260,new_progress=F(1,5),integrated_obligation=True,progress_supported=True),
    dict(contract_asset=2,revenue=-2),dict(total_consideration=260,progress=F(1,5),revenue=52,unbilled=52,revision=1))
step(c,'integrated.perform',dict(new_progress=F(1,2),progress_supported=True),dict(contract_asset=78,revenue=-78),dict(progress=F(1,2),revenue=130,unbilled=130))
step(c,'integrated.modify',dict(new_total=300,new_progress=F(2,5),integrated_obligation=True,progress_supported=True),
    dict(contract_asset=-10,revenue=10),dict(total_consideration=300,progress=F(2,5),revenue=120,unbilled=120,revision=2))
step(c,'integrated.perform',dict(new_progress=1,progress_supported=True),dict(contract_asset=180,revenue=-180),dict(progress=1,revenue=300,unbilled=300))

acq=dict(acquisition_id='acq1',acquisition_date='2024-01-01',measurement_end_inclusive='2024-12-31',dta=0,goodwill=5,
    retrospective_adjustment=0,profit_adjustment=0,oci_adjustment=0,equity_adjustment=0)
recognize=dict(additional_difference=100,rate=F(1,5),rate_enacted=True,recoverable=True,benefit_owner='acquiree',
    new_acquisition_date_information=True,measurement_period_open=True,underlying_origin='profit')
c=case('acquired-tax-measurement','acqdta',acq,dict(cash=100,goodwill=5,original_equity=-105))
step(c,'acqdta.recognize',recognize,dict(dta=20,goodwill=-5,tax_expense=-15),dict(dta=20,goodwill=0,retrospective_adjustment=20,profit_adjustment=15))
step(c,'acqdta.recognize',{**recognize,'additional_difference':50,'rate':F(3,10),'measurement_period_open':False,'underlying_origin':'oci'},
    dict(dta=15,tax_oci=-15),dict(dta=35,oci_adjustment=15),when='2025-03-01',oci={'tax':15})
c=case('acquirer-own-benefit','acqdta',acq,dict(cash=100,goodwill=5,original_equity=-105))
step(c,'acqdta.recognize',{**recognize,'benefit_owner':'acquirer','new_acquisition_date_information':None},dict(dta=20,tax_expense=-20),dict(dta=20,profit_adjustment=20))
c=case('acquirer-own-oci-origin','acqdta',acq,dict(cash=100,goodwill=5,original_equity=-105))
step(c,'acqdta.recognize',{**recognize,'benefit_owner':'acquirer','new_acquisition_date_information':None,'underlying_origin':'oci'},
    dict(dta=20,tax_oci=-20),dict(dta=20,oci_adjustment=20),oci={'tax':20})
c=case('new-post-acquisition-facts','acqdta',acq,dict(cash=100,goodwill=5,original_equity=-105))
step(c,'acqdta.recognize',{**recognize,'new_acquisition_date_information':False},dict(dta=20,tax_expense=-20),dict(dta=20,profit_adjustment=20))
c=case('closed-measurement-equity-origin','acqdta',acq,dict(cash=100,goodwill=5,original_equity=-105))
step(c,'acqdta.recognize',{**recognize,'measurement_period_open':False,'underlying_origin':'equity'},dict(dta=20,tax_equity=-20),dict(dta=20,equity_adjustment=20),equity={'tax':20})

lots=[dict(lot_id='p',entity_id='Taxpayer1',authority_id='Authority1',origin='profit',difference=100,rate=F(1,5),fraction=1,amount=20),
      dict(lot_id='o',entity_id='Taxpayer1',authority_id='Authority1',origin='oci',difference=-80,rate=F(1,4),fraction=1,amount=-20),
      dict(lot_id='e',entity_id='Taxpayer1',authority_id='Authority1',origin='equity',difference=40,rate=F(1,4),fraction=1,amount=10)]
tax_inputs=[dict(lot_id='p',difference=120,rate=F(1,4),fraction=F(1,2),rate_enacted=True,recognition_supported=True,eligible_difference=True),
    dict(lot_id='o',difference=-100,rate=F(3,10),fraction=1,rate_enacted=True,recognition_supported=True,eligible_difference=True),
    dict(lot_id='e',difference=20,rate=F(1,5),fraction=1,rate_enacted=True,recognition_supported=True,eligible_difference=True)]
c=case('mixed-tax-origin-rate','taxlots',dict(lots=lots,present_net=False),dict(cash=100,dta=30,dtl=-20,original_equity=-110))
newlots=[{**lots[0],'difference':120,'rate':F(1,4),'fraction':F(1,2),'amount':15},
    {**lots[1],'difference':-100,'rate':F(3,10),'amount':-30},{**lots[2],'difference':20,'rate':F(1,5),'amount':4}]
step(c,'taxlots.remeasure',dict(lots=tax_inputs),dict(dta=-11,dtl=-10,tax_expense=5,tax_oci=10,tax_equity=6),dict(lots=newlots),oci={'tax':-10},equity={'tax':-6})
step(c,'taxlots.present',dict(request_offset=False,enforceable_current_setoff_right=None))
step(c,'taxlots.present',dict(request_offset=True,enforceable_current_setoff_right=True),change={'present_net':True})
c=case('different-authority-tax-gross','taxlots',dict(lots=[lots[0],{**lots[1],'authority_id':'Authority2'},lots[2]],present_net=False),dict(cash=100,dta=30,dtl=-20,original_equity=-110))
step(c,'taxlots.present',dict(request_offset=False,enforceable_current_setoff_right=None))
