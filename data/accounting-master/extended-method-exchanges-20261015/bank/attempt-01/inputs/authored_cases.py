"""Authored bank examples; no imports from the builder or derivation.

Patches and journals are explicit expected answers. Helpers only copy them.
All probabilities, judgments, dates and measurements are synthetic premises.
"""
from copy import deepcopy
from fractions import Fraction as F

CASES=[]
def case(name,tag,opening,balances=None):
    ca=dict(id=name,tag=tag,currency='USD',source_family='AU_AASB',
        opening_component=deepcopy(opening),opening_balances=balances or {'cash':200,'deposits':-180,'capital':-20},steps=[])
    CASES.append(ca);return ca,deepcopy(opening)
def step(ca,c,method,date,p,patch=None,journal=None,cash=None):
    c.update(deepcopy(patch or {}))
    ca['steps'].append(dict(method=method,event_date=date,parameters=p,after=deepcopy(c),journal=journal or {},
        cash_change=cash or {},oci_change={},equity_change={}))
def hist():
    return dict(original_risk_id='risk-original',original_risk_date='2023-01-01',current_risk_id='risk-original',
        information_id='info-opening',law_id='law-opening',measurement_vintage='vintage-opening')
def measurement(label='current'):
    return dict(current_risk_id='risk-'+label,information_id='info-'+label,law_id='law-'+label,
        measurement_vintage='vintage-'+label,measurement_available=True,horizon_supported=True,horizon_evidence='horizon-supported')
def mh(label):return {k:v for k,v in measurement(label).items() if k in ['current_risk_id','information_id','law_id','measurement_vintage']}
def loan():
    return dict(contract_id='loan-A',measurement_basis='amortised_cost_non_POCI',**hist(),principal=100,terminal=121,
        gross=0,allowance=0,legal_unpaid=0,written_off=0,recovered=0,deposits=180,pending_transfer=0,
        factor=F(11,10),grid=['2024-01-01','2025-01-01','2026-01-01','2027-01-01'],clock=0,due_index=2,
        originated=False,sicr=False,credit_impaired=False,net_from_index=0,modified=False,cure_evidence=None,last_cash_evidence=None)
def scenario(name,weight,default,receipt,index=2,cost=0):
    return dict(scenario_id=name,weight=weight,default_index=default,receipts=[dict(index=index,gross=receipt,cost=cost)])
def law(label,scenarios,sicr=False,impaired=False):
    return dict(**measurement(label),sicr=sicr,credit_impaired=impaired,credit_finding_supported=True,
        mutually_exclusive_exhaustive=True,law_kind='disjoint_scenarios',scenarios=scenarios)
def initial_law():
    return [scenario('first',F(1,10),1,F(121,2)),scenario('later',F(1,10),2,F(121,2)),scenario('pay',F(4,5),None,121)]

# Same loan, with external cash or an internal deposit credit followed by transfer.
for mode in ['external','deposit_credit']:
    ca,c=case('loan-'+mode,'loan',loan())
    step(ca,c,'loan.originate','2024-01-01',dict(mode=mode,amount=100,classification_admitted=True,cash_evidence='advance'),
        dict(gross=100,legal_unpaid=121,originated=True,**({'deposits':280,'pending_transfer':100} if mode=='deposit_credit' else {})),
        {'gross_loan':100,'deposits':-100} if mode=='deposit_credit' else {'gross_loan':100,'cash':-100},
        {} if mode=='deposit_credit' else {'operating':-100})
    if mode=='deposit_credit':
        step(ca,c,'loan.external_transfer','2024-01-01',dict(amount=100,cash_evidence='outbound'),
            dict(deposits=180,pending_transfer=0),{'deposits':100,'cash':-100},{'operating':-100})
    step(ca,c,'loan.measure','2024-01-01',law('initial',initial_law()),dict(**mh('initial'),allowance=5),
        {'impairment_expense':5,'allowance':-5})
    step(ca,c,'loan.accrue','2025-01-01',dict(index=1),dict(gross=110,clock=1),{'gross_loan':10,'interest_income':-10})
    ss=[scenario('later',F(1,5),2,F(121,2)),scenario('pay',F(4,5),None,121)]
    step(ca,c,'loan.measure','2025-01-01',law('sicr',ss,True),dict(**mh('sicr'),sicr=True,allowance=11),
        {'impairment_expense':6,'allowance':-6})
    step(ca,c,'loan.measure','2025-01-01',law('impaired',[scenario('default',1,1,F(121,2))],True,True),
        dict(**mh('impaired'),credit_impaired=True,net_from_index=2,allowance=55),{'impairment_expense':44,'allowance':-44})
    step(ca,c,'loan.accrue','2026-01-01',dict(index=2),dict(gross=121,allowance=F(121,2),clock=2),
        {'gross_loan':11,'interest_income':F(-11,2),'allowance':F(-11,2)})
    step(ca,c,'loan.collect','2026-01-01',dict(amount=F(121,2),interest_component=None,cash_evidence='recovery-cash',full_contractual_settlement=False),
        dict(gross=F(121,2),legal_unpaid=F(121,2),last_cash_evidence='recovery-cash'),{'cash':F(121,2),'gross_loan':F(-121,2)},{'operating':F(121,2)})
    step(ca,c,'loan.writeoff','2026-01-01',dict(amount=F(121,2),no_reasonable_recovery=True,finding_evidence='finding-no-recovery',legal_waiver=False),
        dict(gross=0,allowance=0,written_off=F(121,2)),{'gross_loan':F(-121,2),'allowance':F(121,2)})
    step(ca,c,'loan.recovery','2026-02-01',dict(amount=5,cash_evidence='later-recovery'),
        dict(legal_unpaid=F(111,2),recovered=5,last_cash_evidence='later-recovery'),{'cash':5,'recovery_income':-5},{'operating':5})

ca,c=case('deposits','loan',loan())
step(ca,c,'loan.deposit','2024-01-01',dict(amount=50,cash_evidence='depositor-cash'),dict(deposits=230),{'cash':50,'deposits':-50},{'operating':50})
step(ca,c,'loan.deposit_interest','2024-01-02',dict(amount=2,contractual_accrual_supported=True),dict(deposits=232),{'deposit_interest_expense':2,'deposits':-2})

# Cure has a separately evidenced date; equal terminal equity cannot check interest classification.
for cured in [False,True]:
    op=loan();op.update(gross=110,allowance=55,legal_unpaid=121,originated=True,sicr=True,credit_impaired=True,
        net_from_index=1,clock=1,grid=['2023-01-01','2024-01-01','2025-01-01','2026-01-01'])
    ca,c=case('modification-'+str(cured).lower(),'loan',op,{'cash':100,'gross_loan':110,'allowance':-55,'deposits':-180,'capital':-20,'retained':45})
    step(ca,c,'loan.modify','2024-01-01',dict(new_terminal=110,new_due_index=2,non_derecognition_supported=True,fees=0,costs=0),
        dict(gross=100,terminal=110,legal_unpaid=110,modified=True),{'gross_loan':-10,'modification_expense':10})
    step(ca,c,'loan.measure','2024-01-01',law('modification',[scenario('default',1,1,88)],True,True),
        dict(**mh('modification'),allowance=20),{'allowance':35,'impairment_expense':-35})
    step(ca,c,'loan.measure','2024-01-01',law('improvement',[scenario('default',1,1,99)],True,True),
        dict(**mh('improvement'),allowance=10),{'allowance':10,'impairment_expense':-10})
    if cured:
        step(ca,c,'loan.cure','2024-01-01',dict(objective_improvement=True,subsequent_event=True,evidence='objective-cure',sicr_remains=True),
            dict(credit_impaired=False,cure_evidence='objective-cure'))
    step(ca,c,'loan.accrue','2025-01-01',dict(index=2),dict(gross=110,clock=2,allowance=10 if cured else 11),
        {'gross_loan':10,'interest_income':-10} if cured else {'gross_loan':10,'interest_income':-9,'allowance':-1})
    if cured:
        step(ca,c,'loan.measure','2025-01-01',law('cured',[scenario('pay-short',1,3,F(1089,10),index=3)],True),
            dict(**mh('cured'),allowance=11),{'allowance':-1,'impairment_expense':1})
    step(ca,c,'loan.collect','2025-01-01',dict(amount=110,interest_component=10,cash_evidence='contractual-full',full_contractual_settlement=True),
        dict(gross=0,legal_unpaid=0,allowance=0,last_cash_evidence='contractual-full'),{'cash':110,'gross_loan':-110,'allowance':11,'impairment_expense':-11},{'operating':110})

# Half-year original rate: delayed recovery unwinds after maturity without new contractual gross interest.
op=loan();op.update(grid=['2024-01-01','2024-07-01','2025-01-01','2025-07-01'])
ca,c=case('collateral-delay','loan',op)
step(ca,c,'loan.originate','2024-01-01',dict(mode='external',amount=100,classification_admitted=True,cash_evidence='advance'),
    dict(gross=100,legal_unpaid=121,originated=True),{'cash':-100,'gross_loan':100},{'operating':-100})
ss=[scenario('pay',F(3,5),None,121),scenario('high',F(1,10),1,121,3),scenario('middle',F(1,5),1,F(1331,20),3),scenario('low',F(1,10),1,F(121,10),3)]
step(ca,c,'loan.measure','2024-01-01',law('collateral',ss),dict(**mh('collateral'),allowance=20),{'impairment_expense':20,'allowance':-20})
step(ca,c,'loan.accrue','2024-07-01',dict(index=1),dict(gross=110,clock=1),{'gross_loan':10,'interest_income':-10})
ss=deepcopy(ss)
for s in ss:
    if s['default_index'] is not None:s['default_index']=2
step(ca,c,'loan.measure','2024-07-01',law('collateral-current',ss),dict(**mh('collateral-current'),allowance=22),{'impairment_expense':2,'allowance':-2})
ss=[scenario('high',F(1,4),1,121,3),scenario('middle',F(1,2),1,F(7986,100),3,F(1331,100)),scenario('low',F(1,4),1,F(121,10),3)]
step(ca,c,'loan.measure','2024-07-01',law('collateral-impaired',ss,True,True),
    dict(**mh('collateral-impaired'),sicr=True,credit_impaired=True,net_from_index=2,allowance=55),{'impairment_expense':33,'allowance':-33})
step(ca,c,'loan.accrue','2025-01-01',dict(index=2),dict(gross=121,clock=2,allowance=F(121,2)),{'gross_loan':11,'interest_income':F(-11,2),'allowance':F(-11,2)})
step(ca,c,'loan.accrue','2025-07-01',dict(index=3),dict(clock=3,allowance=F(1089,20)),{'interest_income':F(-121,20),'allowance':F(121,20)})
step(ca,c,'loan.collect','2025-07-01',dict(amount=F(1331,20),interest_component=None,cash_evidence='net-collateral-remittance',full_contractual_settlement=False),
    dict(gross=F(1089,20),legal_unpaid=F(1089,20),last_cash_evidence='net-collateral-remittance'),{'cash':F(1331,20),'gross_loan':F(-1331,20)},{'operating':F(1331,20)})
step(ca,c,'loan.writeoff','2025-07-01',dict(amount=F(1089,20),no_reasonable_recovery=True,finding_evidence='finding-no-recovery',legal_waiver=False),
    dict(gross=0,allowance=0,written_off=F(1089,20)),{'gross_loan':F(-1089,20),'allowance':F(1089,20)})

def commitment(revolving=False):
    return dict(facility_id='facility-A',**hist(),measurement_date='2024-01-01',maturity_date='2026-01-01',limit=100,capacity=100,
        gross=0,allowance=0,provision=0,deposits=180,pending_transfer=0,draw_probability=F(1,2),default_first=F(1,10),
        default_later=F(1,10),terminal=121,recovery=F(1089,10),factor=F(11,10),horizon_kind='contractual',
        horizon_evidence='horizon-supported',lifetime=False,revolving=revolving,inseparable=False,lapsed=False,fully_drawn=False)
for mode in ['external','deposit_credit','lapse']:
    ca,c=case('commitment-'+mode,'commitment',commitment())
    p=dict(**measurement('initial'),draw_probability=F(1,2),default_first=F(1,10),default_later=F(1,10),lifetime=False,sicr_supported=True)
    step(ca,c,'commitment.reserve_full','2024-01-01',p,dict(**mh('initial'),provision=F(1,2)),{'commitment_provision':F(-1,2),'impairment_expense':F(1,2)})
    p=dict(**measurement('sicr'),draw_probability=F(1,2),default_first=F(1,5),default_later=F(1,5),lifetime=True,sicr_supported=True)
    step(ca,c,'commitment.reserve_full','2024-01-01',p,dict(**mh('sicr'),provision=2,default_first=F(1,5),default_later=F(1,5),lifetime=True),
        {'commitment_provision':F(-3,2),'impairment_expense':F(3,2)})
    if mode=='lapse':
        step(ca,c,'commitment.lapse','2024-02-01',dict(rights_expired=True,evidence='facility-expired'),dict(capacity=0,provision=0,lapsed=True),
            {'commitment_provision':2,'impairment_expense':-2})
    else:
        j={'gross_loan':100,'allowance':-4,'commitment_provision':2,'impairment_expense':2}
        j.update({'cash':-100} if mode=='external' else {'deposits':-100})
        step(ca,c,'commitment.draw_full','2024-01-01',dict(mode=mode,amount=100,classification_admitted=True,cash_evidence='draw-cash'),
            dict(gross=100,capacity=0,fully_drawn=True,draw_probability=1,allowance=4,provision=0,
                **({'deposits':280,'pending_transfer':100} if mode=='deposit_credit' else {})),j,{'operating':-100} if mode=='external' else {})
        if mode=='deposit_credit':
            step(ca,c,'commitment.external_transfer','2024-01-01',dict(amount=100,cash_evidence='outbound'),dict(deposits=180,pending_transfer=0),
                {'cash':-100,'deposits':100},{'operating':-100})
op=commitment(True);op.update(provision=2,horizon_kind='behavioural_exception')
ca,c=case('revolving','commitment',op,{'cash':200,'deposits':-180,'capital':-20,'commitment_provision':-2,'impairment_expense':2})
step(ca,c,'commitment.revolving_draw','2024-01-01',dict(**measurement('draw1'),amount=40,funded_ecl=3,undrawn_ecl=F(3,2),cash_evidence='draw1'),
    dict(**mh('draw1'),gross=40,capacity=60,allowance=3,provision=F(3,2)),{'cash':-40,'gross_loan':40,'allowance':-3,'commitment_provision':F(1,2),'impairment_expense':F(5,2)},{'operating':-40})
step(ca,c,'commitment.revolving_repay','2024-02-01',dict(**measurement('repay'),amount=10,funded_ecl=F(12,5),undrawn_ecl=F(9,5),replenishment_supported=True,cash_evidence='repay'),
    dict(**mh('repay'),gross=30,capacity=70,allowance=F(12,5),provision=F(9,5)),{'cash':10,'gross_loan':-10,'allowance':F(3,5),'commitment_provision':F(-3,10),'impairment_expense':F(-3,10)},{'operating':10})
step(ca,c,'commitment.revolving_draw','2024-03-01',dict(**measurement('draw2'),amount=20,funded_ecl=4,undrawn_ecl=F(6,5),cash_evidence='draw2'),
    dict(**mh('draw2'),gross=50,capacity=50,allowance=4,provision=F(6,5)),{'cash':-20,'gross_loan':20,'allowance':F(-8,5),'commitment_provision':F(3,5),'impairment_expense':1},{'operating':-20})
op=commitment(True);op.update(gross=4,capacity=96)
ca,c=case('inseparable','commitment',op,{'cash':196,'gross_loan':4,'deposits':-180,'capital':-20})
step(ca,c,'commitment.combined','2024-01-01',dict(**measurement('combined'),combined_ecl=6,cannot_separate_supported=True),
    dict(**mh('combined'),allowance=4,provision=2,inseparable=True),{'allowance':-4,'commitment_provision':-2,'impairment_expense':6})

def fee(purpose='probable_specific_loan'):
    return dict(arrangement_id='fee-A',purpose=purpose,fee=2,liability=0,principal=100,terminal=F(539,5),gross=0,factor=F(11,10),
        interest_recognised=0,received=False,originated=False,expired=False,settled=False,zero_ecl_isolation_supported=True,
        service_elapsed=0,service_dates=['2024-06-30','2024-12-31'] if purpose=='equal_stand_ready' else [],
        origination_date='2024-01-01',maturity_date='2025-01-01')
for route in ['originate','expire','service']:
    ca,c=case('fee-'+route,'fee',fee('equal_stand_ready' if route=='service' else 'probable_specific_loan'))
    step(ca,c,'fee.receive','2024-01-01',dict(amount=2,purpose_supported=True,cash_evidence='fee-cash'),dict(received=True,liability=2),
        {'cash':2,'fee_liability':-2},{'operating':2})
    if route=='originate':
        step(ca,c,'fee.originate','2024-01-01',dict(amount=100,specific_loan_probable=True,classification_admitted=True,cash_evidence='advance'),
            dict(originated=True,gross=98,liability=0),{'cash':-100,'gross_loan':98,'fee_liability':2},{'operating':-100})
        step(ca,c,'fee.accrue','2025-01-01',dict(zero_ecl_isolation_supported=True),dict(gross=F(539,5),interest_recognised=F(49,5)),
            {'gross_loan':F(49,5),'interest_income':F(-49,5)})
        step(ca,c,'fee.collect','2025-01-01',dict(amount=F(539,5),interest_component=F(39,5),cash_evidence='loan-full'),
            dict(gross=0,settled=True),{'cash':F(539,5),'gross_loan':F(-539,5)},{'operating':F(539,5)})
    elif route=='expire':
        step(ca,c,'fee.expire','2024-12-31',dict(rights_expired=True,evidence='fee-expiry'),dict(liability=0,expired=True),{'fee_liability':2,'fee_income':-2})
    else:
        step(ca,c,'fee.service','2024-06-30',dict(elapsed=1,equal_service_performed=True,revenue_method_admitted=True),
            dict(liability=1,service_elapsed=1),{'fee_liability':1,'fee_income':-1})
        step(ca,c,'fee.service','2024-12-31',dict(elapsed=2,equal_service_performed=True,revenue_method_admitted=True),
            dict(liability=0,service_elapsed=2),{'fee_liability':1,'fee_income':-1})

def liquidity():
    return dict(funding_id='funding-A',cash=20,securities=50,gross=80,allowance=10,deposits=120,funding=0,limit=10,
        eligible_lot=10,haircut=F(1,5),capacity=0,requested=0,actual_received=0,unpaid_deposits=0,request_status='none',
        receipt_status='none',control_breach=False,receipt_evidence=None,settlement_ids=[],withdrawal_ids=[])
for received,requested in [(8,True),(6,True),(0,True),(10,True),(6,False)]:
    ca,c=case('funding-'+str(received)+'-'+str(requested).lower(),'liquidity',liquidity(),
        {'cash':20,'securities':50,'gross_loan':80,'allowance':-10,'deposits':-120,'capital':-20})
    step(ca,c,'liquidity.capacity','2024-01-01',dict(eligibility_supported=True,haircut_supported=True),dict(capacity=8))
    if requested:
        step(ca,c,'liquidity.request','2024-01-01',dict(amount=8,request_evidence='request-record'),dict(requested=8,request_status='pending'))
    step(ca,c,'liquidity.settle','2024-01-02',dict(amount=received,evidence_kind='confirmed_cash' if received else 'verified_no_receipt',settlement_id='settle1',cash_evidence='verified-settlement'),
        dict(cash=20+received,funding=received,actual_received=received,request_status='settled',receipt_status='verified_zero' if not received else 'confirmed' if requested and received==8 else 'partial',
            control_breach=not requested or received>8,receipt_evidence='verified-settlement',settlement_ids=['settle1']),
        {'cash':received,'funding':-received} if received else {},{'financing':received})
    paid=20+received
    step(ca,c,'liquidity.withdraw','2024-01-03',dict(requested=30,withdrawal_id='withdraw1',actual_payment_evidence='paid-amount'),
        dict(cash=0,deposits=120-paid,unpaid_deposits=30-paid,withdrawal_ids=['withdraw1']),{'cash':-paid,'deposits':paid},{'operating':-paid})
