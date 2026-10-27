"""Hand-authored conditional examples. No financial derivation imports.

The helper applies declared patches, never computes accounting effects.
Journals, OCI/equity changes and expected component values are authored here;
financial_checks.py reconstructs them separately from opening/event facts.
"""
from copy import deepcopy
from fractions import Fraction as F
from source_policy import SOURCES

CASES=[]

def case(name,tag,opening,balances=None,currency='USD'):
    c={'id':name,'tag':tag,'currency':currency,
       'source_family':SOURCES[tag]['family'],
       'opening_component':deepcopy(opening),'opening_balances':balances or {'cash':200,'capital':-200},'steps':[]}
    CASES.append(c)
    return c,deepcopy(opening)

def step(case,c,method,date,parameters,patch=None,journal=None,cash=None,oci=None,equity=None):
    c.update(deepcopy(patch or {}))
    case['steps'].append({'method':method,'event_date':date,'parameters':parameters,'after':deepcopy(c),
        'journal':journal or {},'cash_change':cash or {},'oci_change':oci or {},'equity_change':equity or {}})

def amendment(consideration):
    return dict(instrument_id='bond-A',consideration=consideration,old_shares=40,
        new_shares=50 if consideration=='shares' else 40,debt=960,bonus=0 if consideration=='shares' else 100,
        bonus_due=0,equity_pending=0,issued=0,announcement_date='2024-01-01',binding_date='2024-01-05',
        delivery_date='2024-01-20',announced=False,bound=False,delivered=False,bonus_paid=False)

for kind in ['shares','cash_bonus']:
    ca,c=case('amendment-'+kind,'amendment',amendment(kind),{'cash':1020,'debt':-960,'original_equity':-60})
    step(ca,c,'amendment.announce','2024-01-01',{'rights_changed':False},{'announced':True})
    if kind=='shares':
        step(ca,c,'amendment.bind','2024-01-05',dict(quote=40,quote_date='2024-01-05',legal_discharge=True,
            equity_qualified=True,cash_alternative=False,conditions_resolved=True),
            dict(debt=0,equity_pending=1360,bound=True),
            {'debt':960,'inducement_expense':400,'equity_pending':-1360},equity={'issue':1360})
        step(ca,c,'amendment.deliver','2024-01-20',{'shares':50},
            dict(issued=1360,equity_pending=0,delivered=True),{'equity_pending':1360,'capital':-1360})
    else:
        step(ca,c,'amendment.bind','2024-01-05',dict(quote=40,quote_date='2024-01-05',legal_discharge=True,
            equity_qualified=True,cash_alternative=False,conditions_resolved=True),
            dict(debt=0,bonus_due=100,equity_pending=960,bound=True),
            {'debt':960,'inducement_expense':100,'equity_pending':-960,'bonus_payable':-100},equity={'issue':960})
        step(ca,c,'amendment.deliver','2024-01-20',{'shares':40},
            dict(issued=960,equity_pending=0,delivered=True),{'equity_pending':960,'capital':-960})
        step(ca,c,'amendment.pay_bonus','2024-01-25',{'amount':100},dict(bonus_due=0,bonus_paid=True),
            {'bonus_payable':100,'cash':-100},cash={'financing':-100})

def award(settlement='equity'):
    return dict(grant_id='grant-A',settlement=settlement,quantity=100,grant_fv=3,original_cost=0,
        incremental_total=0,incremental_cost=0,award_equity=0,liability=0,total_years=3,elapsed=0,
        modification_elapsed=None,incremental_end=None,modified=False,all_original_vest=True,
        service_dates=['2023-12-31','2024-12-31','2025-12-31'])

for kind in ['repricing','added_instruments']:
    ca,c=case('award-'+kind,'award',award())
    step(ca,c,'award.service','2023-12-31',{'elapsed':1},dict(elapsed=1,original_cost=100,award_equity=100),
        {'award_expense':100,'award_equity':-100},equity={'award':100})
    inc,end=(200,3) if kind=='repricing' else (80,2)
    step(ca,c,'award.modify','2024-01-01',dict(kind=kind,before_fv=2,after_fv=4,
        added_quantity=0 if kind=='repricing' else 20,incremental_end=end,original_conditions_unchanged=True),
        dict(modified=True,incremental_total=inc,modification_elapsed=1,incremental_end=end))
    if kind=='repricing':
        step(ca,c,'award.service','2024-12-31',{'elapsed':2},dict(elapsed=2,original_cost=200,incremental_cost=100,award_equity=300),
            {'award_expense':200,'award_equity':-200},equity={'award':200})
        step(ca,c,'award.service','2025-12-31',{'elapsed':3},dict(elapsed=3,original_cost=300,incremental_cost=200,award_equity=500),
            {'award_expense':200,'award_equity':-200},equity={'award':200})
    else:
        step(ca,c,'award.service','2024-12-31',{'elapsed':2},dict(elapsed=2,original_cost=200,incremental_cost=80,award_equity=280),
            {'award_expense':180,'award_equity':-180},equity={'award':180})
        step(ca,c,'award.service','2025-12-31',{'elapsed':3},dict(elapsed=3,original_cost=300,award_equity=380),
            {'award_expense':100,'award_equity':-100},equity={'award':100})

for liability,difference in [(180,20),(220,-20)]:
    opening=award('cash');opening.update(elapsed=2,original_cost=liability,liability=liability)
    ca,c=case('cash-award-'+str(liability),'award',opening,
        {'cash':300,'capital':-300,'award_expense':liability,'award_liability':-liability})
    step(ca,c,'award.cash_to_equity','2025-01-01',dict(remeasured_liability=liability,replacement_fv=300,
        modified_total_years=3,replacement_identified=True),
        dict(liability=0,settlement='equity',modified=True,original_cost=200,grant_fv=3,award_equity=200),
        {'award_liability':liability,'award_expense':difference,'award_equity':-200},equity={'award':200})
    step(ca,c,'award.service','2025-12-31',{'elapsed':3},dict(elapsed=3,original_cost=300,award_equity=300),
        {'award_expense':100,'award_equity':-100},equity={'award':100})

def cashflow(purpose='inventory'):
    return dict(designation_id='cf-A',purpose=purpose,D=0,E=0,I=0,derivative=0,settled_total=0,
        reserve=0,inventory=0,interest_paid=0,active=True,expected=True,bought=False,basis_done=False,sold=False)

ca,c=case('cashflow-inventory','cashflow',cashflow())
step(ca,c,'cashflow.measure','2024-03-31',dict(D=12,H=-10,eligibility_known=True),
    dict(D=12,E=10,I=2,derivative=12,reserve=10),{'derivative':12,'cf_reserve':-10,'other_gains':-2},oci={'cash_flow':10})
step(ca,c,'cashflow.measure','2024-06-30',dict(D=15,H=-14,eligibility_known=True),
    dict(D=15,E=14,I=1,derivative=15,reserve=14),{'derivative':3,'cf_reserve':-4,'other_gains':1},oci={'cash_flow':4})
step(ca,c,'cashflow.purchase','2024-07-01',{'amount':114},dict(inventory=114,bought=True),
    {'inventory':114,'cash':-114},cash={'operating':-114})
step(ca,c,'cashflow.settle','2024-07-01',{'amount':15},dict(derivative=0,settled_total=15),
    {'derivative':-15,'cash':15},cash={'operating':15})
step(ca,c,'cashflow.basis_transfer','2024-07-01',{'reserve_origin':'cf-A'},dict(reserve=0,inventory=100,basis_done=True),
    {'cf_reserve':14,'inventory':-14},equity={'basis_transfer':-14})
step(ca,c,'cashflow.sell','2024-09-30',{'proceeds':130},dict(inventory=0,sold=True),
    {'cash':130,'revenue':-130,'inventory':-100,'cost_of_sales':100},cash={'operating':130})

ca,c=case('cashflow-interest','cashflow',cashflow('interest'))
step(ca,c,'cashflow.measure','2024-06-30',dict(D=8,H=-8,eligibility_known=True),
    dict(D=8,E=8,I=0,derivative=8,reserve=8),{'derivative':8,'cf_reserve':-8},oci={'cash_flow':8})
step(ca,c,'cashflow.settle','2024-12-31',{'amount':8},dict(derivative=0,settled_total=8),
    {'derivative':-8,'cash':8},cash={'operating':8})
step(ca,c,'cashflow.pay_interest','2024-12-31',{'amount':18},dict(interest_paid=18),
    {'finance_expense':18,'cash':-18},cash={'operating':-18})
step(ca,c,'cashflow.release','2024-12-31',{'reserve_origin':'cf-A','reason':'interest_earned'},dict(reserve=0),
    {'cf_reserve':8,'hedge_expense':-8},oci={'cash_flow':-8})

for expected in [True,False]:
    ca,c=case('cashflow-discontinue-'+str(expected).lower(),'cashflow',cashflow())
    step(ca,c,'cashflow.measure','2024-06-30',dict(D=8,H=-8,eligibility_known=True),
        dict(D=8,E=8,I=0,derivative=8,reserve=8),{'derivative':8,'cf_reserve':-8},oci={'cash_flow':8})
    step(ca,c,'cashflow.discontinue','2024-07-01',{'still_expected':expected},dict(active=False,expected=expected))
    if not expected:
        step(ca,c,'cashflow.release','2024-07-01',{'reserve_origin':'cf-A','reason':'no_longer_expected'},dict(reserve=0),
            {'cf_reserve':8,'hedge_expense':-8},oci={'cash_flow':-8})

def option(route='transaction',actual=6,aligned=6,collar=False):
    return dict(designation_id='opt-A',route=route,initial_actual=actual,initial_aligned=aligned,
        intrinsic=0,time_value=0,aligned_time_value=0,effective_intrinsic=0,related_cost=0,mismatch_profit=0,
        intrinsic_reserve=0,cost_reserve=0,derivative=0,amortized=0,inventory=0,periods=2 if route=='time_period' else 0,
        elapsed=0,protection_dates=['2024-12-31','2025-12-31'] if route=='time_period' else [],bought=False,
        settled=False,inventory_bought=False,basis_done=False,sold=False,active=True,zero_cost_collar=collar)

def buy(ca,c,premium,aligned):
    step(ca,c,'option.buy','2024-01-01',{'premium':premium},
        dict(bought=True,time_value=premium,aligned_time_value=aligned,derivative=premium),
        {'derivative':premium,'cash':-premium} if premium else {},cash={'operating':-premium} if premium else {})

ca,c=case('option-inventory','option',option());buy(ca,c,6,6)
step(ca,c,'option.measure','2024-06-30',dict(intrinsic=12,time_value=4,aligned_time_value=4,H=-12),
    dict(intrinsic=12,time_value=4,aligned_time_value=4,derivative=16,effective_intrinsic=12,related_cost=-2,
        intrinsic_reserve=12,cost_reserve=-2),{'derivative':10,'intrinsic_reserve':-12,'cost_reserve':2},oci={'intrinsic':12,'cost':-2})
step(ca,c,'option.measure','2024-12-31',dict(intrinsic=20,time_value=0,aligned_time_value=0,H=-20),
    dict(intrinsic=20,time_value=0,aligned_time_value=0,derivative=20,effective_intrinsic=20,related_cost=-6,
        intrinsic_reserve=20,cost_reserve=-6),{'derivative':4,'intrinsic_reserve':-8,'cost_reserve':4},oci={'intrinsic':8,'cost':-4})
step(ca,c,'option.purchase','2024-12-31',{'amount':120},dict(inventory_bought=True,inventory=120),
    {'inventory':120,'cash':-120},cash={'operating':-120})
step(ca,c,'option.settle','2024-12-31',{'amount':20},dict(derivative=0,settled=True),
    {'derivative':-20,'cash':20},cash={'operating':20})
step(ca,c,'option.basis_transfer','2024-12-31',dict(intrinsic_origin='opt-A/intrinsic',cost_origin='opt-A/cost'),
    dict(intrinsic_reserve=0,cost_reserve=0,inventory=106,basis_done=True),
    {'intrinsic_reserve':20,'cost_reserve':-6,'inventory':-14},equity={'basis_transfer':-14})
step(ca,c,'option.sell','2025-01-31',{'proceeds':130},dict(inventory=0,sold=True),
    {'cash':130,'revenue':-130,'inventory':-106,'cost_of_sales':106},cash={'operating':130})

for stopped in [False,True]:
    ca,c=case('option-time-'+str(stopped).lower(),'option',option('time_period'));buy(ca,c,6,6)
    step(ca,c,'option.measure','2024-12-31',dict(intrinsic=0,time_value=2,aligned_time_value=2,H=0),
        dict(time_value=2,aligned_time_value=2,derivative=2,related_cost=-4,cost_reserve=-4),
        {'derivative':-4,'cost_reserve':4},oci={'cost':-4})
    step(ca,c,'option.amortize','2024-12-31',dict(elapsed=1,rational_even_allocation_admitted=True),
        dict(elapsed=1,amortized=3,cost_reserve=-1),{'cost_reserve':-3,'hedge_expense':3},oci={'cost':3})
    if stopped:
        step(ca,c,'option.discontinue','2024-12-31',{'relationship_ended':True},dict(cost_reserve=0,active=False),
            {'cost_reserve':-1,'hedge_expense':1},oci={'cost':1})
    else:
        step(ca,c,'option.measure','2025-12-31',dict(intrinsic=0,time_value=0,aligned_time_value=0,H=0),
            dict(time_value=0,aligned_time_value=0,derivative=0,related_cost=-6,cost_reserve=-3),
            {'derivative':-2,'cost_reserve':2},oci={'cost':-2})
        step(ca,c,'option.amortize','2025-12-31',dict(elapsed=2,rational_even_allocation_admitted=True),
            dict(elapsed=2,amortized=6,cost_reserve=0),{'cost_reserve':-3,'hedge_expense':3},oci={'cost':3})

for label,a0,h0,a1,h1,r1,m1,r2,m2 in [
    ('above',6,4,3,3,-1,-2,-4,-2),('below',2,3,1,F('5/2'),F('-1/2'),F('-1/2'),-2,0),
    ('collar',0,0,F('6/5'),F('6/5'),F('6/5'),0,0,0)]:
    ca,c=case('option-aligned-'+label,'option',option(actual=a0,aligned=h0,collar=label=='collar'));buy(ca,c,a0,h0)
    # These two journals are declared from the retained numerical examples.
    j1={'derivative':a1-a0,'cost_reserve':-r1,'hedge_expense':-m1}
    j2={'derivative':-a1,'cost_reserve':-(r2-r1),'hedge_expense':-(m2-m1)}
    step(ca,c,'option.measure','2024-06-30',dict(intrinsic=0,time_value=a1,aligned_time_value=h1,H=0),
        dict(time_value=a1,aligned_time_value=h1,derivative=a1,related_cost=r1,mismatch_profit=m1,cost_reserve=r1),j1,oci={'cost':r1})
    step(ca,c,'option.measure','2024-12-31',dict(intrinsic=0,time_value=0,aligned_time_value=0,H=0),
        dict(time_value=0,aligned_time_value=0,derivative=0,related_cost=r2,mismatch_profit=m2,cost_reserve=r2),j2,oci={'cost':r2-r1})

opening=dict(designation_id='reb-A',D=0,E=0,I=0,derivative=0,reserve=0,retained_fraction=1,layer_gain=0,
    revision=0,last_measurement_date=None,prospective_measured=False,
    layers=[dict(layer_id='original',quantity=100,reference_price=80,designation_date='2024-01-01')])
ca,c=case('rebalancing','rebalancing',opening)
step(ca,c,'rebalancing.measure','2024-03-31',dict(D=12,H=-10),
    dict(D=12,E=10,I=2,derivative=12,reserve=10,last_measurement_date='2024-03-31'),
    {'derivative':12,'cf_reserve':-10,'other_gains':-2},oci={'cash_flow':10})
step(ca,c,'rebalancing.measure','2024-06-30',dict(D=18,H=-14),
    dict(D=18,E=14,I=4,derivative=18,reserve=14,last_measurement_date='2024-06-30'),
    {'derivative':6,'cf_reserve':-4,'other_gains':-2},oci={'cash_flow':4})
new=dict(layer_id='additional',quantity=10,reference_price=90,designation_date='2024-06-30')
step(ca,c,'rebalancing.change','2024-06-30',dict(retained_fraction=F('9/10'),objective_unchanged=True,
    documentation_updated=True,added_layer=new),dict(revision=1,retained_fraction=F('9/10'),layers=[*opening['layers'],new]))
step(ca,c,'rebalancing.layers','2024-09-30',dict(current_price=95,zero_discount_admitted=True),{'layer_gain':1550})
step(ca,c,'rebalancing.prospective_measure','2024-09-30',dict(total_D=28,item_change_since_rebalance=-9),
    dict(D=28,E=23,I=5,derivative=28,reserve=23,last_measurement_date='2024-09-30',prospective_measured=True),
    {'derivative':10,'cf_reserve':-9,'other_gains':-1},oci={'cash_flow':9})

for name,service,period in [('same',80,2024),('different',80,2025),('nil',100,2025)]:
    opening=dict(designation_id='net-A',sales_id='external-sale',service_id='external-service',exposure_currency='USD',
        functional_currency='EUR',sales_usd=100,service_usd=service,initial_spot=1,execution_spot=F('11/10'),
        derivative=0,reserve=0,gross_revenue=0,gross_service=0,hedge_expense=0,sales_period=2024,service_period=period,
        designated=False,measured=False,sales_done=False,service_done=False,settled=False,external_items=True,
        rolling_strategy=True,changing_net_size=True,normal_instrument_use=True,inconsistent_recognition=True)
    ca,c=case('nethedge-'+name,'nethedge',opening,currency='EUR')
    step(ca,c,'nethedge.designate','2024-01-01',dict(individually_eligible=True,highly_probable=True,
        actual_net_management=True,documented_periods=True,effectiveness_admitted=True),{'designated':True})
    d=0 if name=='nil' else -2
    step(ca,c,'nethedge.measure','2024-12-31',dict(spot=F('11/10'),zero_discount_forward_credit_effects=True),
        dict(derivative=d,reserve=d,measured=True),{'derivative':d,'cf_reserve':-d} if d else {},oci={'cash_flow':d})
    step(ca,c,'nethedge.sale','2024-12-31',dict(spot=F('11/10'),recognition_period=2024),
        dict(sales_done=True,gross_revenue=110,hedge_expense=10,reserve=10 if name=='nil' else 8),
        {'cash':110,'revenue':-110,'hedge_expense':10,'cf_reserve':-10},cash={'operating':110},oci={'cash_flow':10})
    cost,release=(110,10) if name=='nil' else (88,8)
    step(ca,c,'nethedge.service',str(period)+'-12-31',dict(spot=F('11/10'),recognition_period=period),
        dict(service_done=True,gross_service=cost,hedge_expense=0 if name=='nil' else 2,reserve=0),
        {'cash':-cost,'service_expense':cost,'hedge_expense':-release,'cf_reserve':release},
        cash={'operating':-cost},oci={'cash_flow':-release})
    step(ca,c,'nethedge.settle',str(period)+'-12-31',{'amount':d},dict(derivative=0,settled=True),
        {'cash':d,'derivative':-d} if d else {},cash={'operating':d})

from residual_cases import populate
populate(case,step)
