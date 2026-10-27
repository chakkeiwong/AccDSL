"""Authored expected effects; does not import independent financial checks."""
from copy import deepcopy
from fractions import Fraction as F

def populate(case,step):
    def debt(principal=100,interest=21,term=2,due='2026-01-01'):
        return dict(instrument_id='plain-A',originated=False,rate_mode='exact',principal=principal,legal_interest=interest,
          carrying=0,rate=0,rate_low=0,rate_high=0,term_years=term,elapsed_years=0,issue_date='2024-01-01',due_date=due,defaulted=False)
    for short in [False,True]:
        ca,c=case('debt-short' if short else 'debt-full','debt',debt(),{'cash':0,'debt':0})
        step(ca,c,'debt.issue','2024-01-01',dict(proceeds=100,rate=F(1,10)),dict(originated=True,carrying=100,rate=F(1,10)),{'cash':100,'debt':-100},cash={'financing':100})
        for year,carrying,expense in [(2025,110,10),(2026,121,11)]:
            step(ca,c,'debt.accrue',f'{year}-01-01',dict(year_fraction=1,factor=F(11,10)),dict(carrying=carrying,elapsed_years=year-2024),{'finance_expense':expense,'debt':-expense})
        principal=59 if short else 100
        step(ca,c,'debt.pay','2026-01-01',dict(principal=principal,interest=21,legal_release_of_unpaid=False),
          dict(carrying=41 if short else 0,principal=41 if short else 0,legal_interest=0,defaulted=short),
          {'debt':principal+21,'cash':-principal-21},cash={'financing':-principal,'operating':-21})
    ca,c=case('debt-fee-enclosure','debt',debt(),{'cash':0,'debt':0})
    step(ca,c,'debt.issue','2024-01-01',dict(proceeds=100,rate=F(1,10)),dict(originated=True,carrying=100,rate=F(1,10)),{'cash':100,'debt':-100},cash={'financing':100})
    step(ca,c,'debt.fee','2024-01-01',dict(amount=2,directly_attributable=True,rate_low=F(111,1000),rate_high=F(112,1000)),
      dict(carrying=98,rate_mode='enclosure',rate=0,rate_low=F(111,1000),rate_high=F(112,1000)),{'debt':2,'cash':-2},cash={'financing':-2})
    ca,c=case('debt-half-year','debt',debt(100,21,1,'2025-01-01'),{'cash':0,'debt':0})
    step(ca,c,'debt.issue','2024-01-01',dict(proceeds=100,rate=F(21,100)),dict(originated=True,carrying=100,rate=F(21,100)),{'cash':100,'debt':-100},cash={'financing':100})
    step(ca,c,'debt.accrue','2024-07-01',dict(year_fraction=F(1,2),factor=F(11,10)),dict(carrying=110,elapsed_years=F(1,2)),{'debt':-10,'finance_expense':10})

    for name,payment,lender_fee,third_fee,fv,substantial,target,rate,ratio in [
      ('inclusive',F(1331,10),0,0,118,True,118,F(151,1180),F(1,10)),
      ('non-substantial',F(231,2),0,0,None,False,105,F(1,10),F(1,22)),
      ('third-party-fee',F(231,2),0,2,None,False,103,F(25,206),F(1,22)),
      ('lender-fee',121,11,0,118,True,118,F(3,118),F(1,10)),
      ('qualitative',121,0,0,118,True,118,F(3,118),0),
    ]:
        opening=dict(instrument_id='mod-A',carrying=110,old_rate=F(1,10),old_payment=121,new_payment=0,new_rate=0,
          principal_basis=0,test_ratio=0,due_date='2025-01-01',phase='original',outcome='none')
        ca,c=case('mod-'+name,'modification',opening,{'cash':200,'debt':-110,'capital':-90})
        fees=lender_fee+third_fee
        journal={'debt':110-target,'cash':-fees}
        if substantial:journal['finance_expense']=target-110+fees
        else:journal['other_gains']=-5
        step(ca,c,'modification.change','2024-01-01',dict(new_payment=payment,lender_fee=lender_fee,third_party_fee=third_fee,
          fee_scope_known=True,qualitative='substantial' if name=='qualitative' else 'non_substantial',replacement_fv=fv),
          dict(carrying=target,principal_basis=target,new_payment=payment,new_rate=rate,test_ratio=ratio,
          outcome='substantial' if substantial else 'non_substantial',phase='modified'),journal,cash={'financing':-fees})
        expense=payment-target
        step(ca,c,'modification.accrue','2025-01-01',dict(rate=rate),dict(carrying=payment,phase='accrued'),{'debt':-expense,'finance_expense':expense})
        step(ca,c,'modification.pay','2025-01-01',dict(amount=payment),dict(carrying=0,phase='paid'),{'debt':payment,'cash':-payment},cash={'financing':-target,'operating':-expense})

    ca,c=case('treasury-equity','shares',dict(class_id='ordinary',issued=0,treasury=0,treasury_cost=0,capital=0,surplus=0),{'cash':0})
    step(ca,c,'shares.issue','2024-01-01',dict(quantity=100,price=2),dict(issued=100,capital=200),{'cash':200,'capital':-200},cash={'financing':200},equity={'issue':200})
    step(ca,c,'shares.buy','2024-04-01',dict(quantity=10,price=3),dict(treasury=10,treasury_cost=30),{'cash':-30,'treasury':30},cash={'financing':-30},equity={'repurchase':-30})
    step(ca,c,'shares.reissue','2024-07-01',dict(quantity=5,price=4),dict(treasury=5,treasury_cost=15,surplus=5),{'cash':20,'treasury':-15,'share_surplus':-5},cash={'financing':20},equity={'reissue':20})

    def compound():return dict(instrument_id='convertible-A',phase='unissued',debt=0,debt_cash_basis=0,original_equity=0,redemption=100,
      fixed_shares=10,rate=F(1,9),capital=0,retained_debit=0,due_date='2025-01-01',valuation_mode='exact',coupon=0,periods=1,old_period_rate=0,current_period_rate=0)
    for route in ['redeem','convert']:
        ca,c=case('original-'+route,'compound',compound(),{'cash':0})
        step(ca,c,'compound.issue','2024-01-01',dict(proceeds=100,debt_fv=90,fixed_for_fixed=True),dict(debt=90,debt_cash_basis=90,original_equity=10,phase='issued'),{'cash':100,'debt':-90,'original_equity':-10},cash={'financing':100},equity={'issue':10})
        step(ca,c,'compound.accrue','2025-01-01',dict(rate=F(1,9)),dict(debt=100,phase='matured'),{'debt':-10,'finance_expense':10})
        step(ca,c,'compound.end','2025-01-01',dict(route=route,amount_or_shares=100 if route=='redeem' else 10,original_rights_unchanged=True),
          dict(debt=0,phase='ended',capital=100 if route=='convert' else 0),
          {'debt':100,'cash':-100} if route=='redeem' else {'debt':100,'capital':-100},
          cash={'financing':-90,'operating':-10} if route=='redeem' else {},equity={'issue':100} if route=='convert' else {})
    # Explicit rational sums are authored separately from the calculator's PV function.
    old=sum(F(50)*F(200,211)**i for i in range(1,11))+F(1000)*F(200,211)**10
    new=sum(F(50)*F(25,26)**i for i in range(1,11))+F(1000)*F(25,26)**10
    for mode,carrying,valuation in [('exact',old,new),('source_rounded',F(962),F(1081))]:
        opening=compound();opening.update(phase='issued',debt=carrying,debt_cash_basis=carrying,original_equity=60,redemption=1000,coupon=50,periods=10,
          old_period_rate=F(11,200),current_period_rate=F(1,25),valuation_mode=mode,capital=2000-carrying-60,due_date='2029-01-01')
        ca,c=case('repurchase-'+mode,'compound',opening,{'cash':2000,'debt':-carrying,'original_equity':-60,'capital':-(2000-carrying-60)})
        allocation=1700-valuation
        step(ca,c,'compound.repurchase','2024-01-01',dict(consideration=1700,unchanged_rights=True,comparable_debt_rate_known=True),
          dict(debt=0,original_equity=0,retained_debit=allocation-60,phase='ended'),
          {'debt':carrying,'finance_expense':valuation-carrying,'original_equity':60,'retained':allocation-60,'cash':-1700},
          cash={'financing':-1700},equity={'repurchase':-allocation})

    populate_awards(case,step)
    populate_eps_hedges(case,step)

def populate_awards(case,step):
    dates=['2024-12-31','2025-12-31','2026-12-31']
    def vest(condition='service',employees=100,each=10):return dict(grant_id='conditional-A',condition=condition,
      employees=employees,awards_each=each,grant_fv=3,award_equity=0,cost=0,years=3,elapsed=0,service_dates=dates,cancelled=False,paid=False)
    ca,c=case('vesting-estimates','vesting',vest())
    for elapsed,employees,total,charge in [(1,90,900,900),(2,80,1600,700),(3,75,2250,650)]:
        step(ca,c,'vesting.service',dates[elapsed-1],dict(elapsed=elapsed,employees=employees,other_conditions_met=True,market_met=True),
          dict(employees=employees,elapsed=elapsed,cost=total,award_equity=total),{'award_expense':charge,'award_equity':-charge},equity={'award':charge})
    ca,c=case('non-market-reversal','vesting',vest('non_market'))
    step(ca,c,'vesting.service',dates[0],dict(elapsed=1,employees=90,other_conditions_met=True,market_met=True),dict(elapsed=1,employees=90,cost=900,award_equity=900),{'award_expense':900,'award_equity':-900},equity={'award':900})
    step(ca,c,'vesting.fail','2025-01-01',dict(non_market_failure=True),dict(employees=0,cost=0,award_equity=0,cancelled=True),{'award_expense':-900,'award_equity':900},equity={'award':-900})
    ca,c=case('failed-market-no-reversal','vesting',vest('market',100,1))
    for elapsed in [1,2,3]:
        step(ca,c,'vesting.service',dates[elapsed-1],dict(elapsed=elapsed,employees=100,other_conditions_met=True,market_met=False),
          dict(elapsed=elapsed,cost=100*elapsed,award_equity=100*elapsed),{'award_expense':100,'award_equity':-100},equity={'award':100})
    ca,c=case('cancellation-excess','vesting',vest('service',100,1),{'cash':500,'capital':-500})
    step(ca,c,'vesting.service',dates[0],dict(elapsed=1,employees=100,other_conditions_met=True,market_met=True),dict(elapsed=1,cost=100,award_equity=100),{'award_expense':100,'award_equity':-100},equity={'award':100})
    step(ca,c,'vesting.cancel','2025-01-01',dict(replacement=False),dict(cancelled=True,cost=300,award_equity=300),{'award_expense':200,'award_equity':-200},equity={'award':200})
    step(ca,c,'vesting.pay','2025-01-01',dict(amount=330,award_fv=320),dict(paid=True,cost=310,award_equity=-20),{'cash':-330,'award_equity':320,'award_expense':10},cash={'financing':-320,'operating':-10},equity={'award':-320})
    opening=dict(grant_id='cash-A',employees=100,awards_each=10,liability=0,cost=0,last_fv=0,years=3,elapsed=0,service_dates=dates,paid=False)
    ca,c=case('cash-award-remeasure','cashaward',opening,{'cash':8000,'capital':-8000})
    for elapsed,employees,fv,total,charge in [(1,90,3,900,900),(2,80,6,3200,2300),(3,75,8,6000,2800)]:
        step(ca,c,'cashaward.service',dates[elapsed-1],dict(elapsed=elapsed,employees=employees,fv=fv),dict(elapsed=elapsed,employees=employees,last_fv=fv,cost=total,liability=total),{'award_expense':charge,'award_liability':-charge})
    step(ca,c,'cashaward.settle','2027-01-01',dict(fv=9,amount=6750),dict(last_fv=9,cost=6750,liability=0,paid=True),{'award_expense':750,'award_liability':6000,'cash':-6750},cash={'operating':-6750})

    for holder,obligation,route in [('counterparty',False,'cash'),('counterparty',False,'shares'),('entity',False,'cash'),('entity',False,'shares'),('entity',False,'shares-premium'),('entity',True,'cash')]:
        name='choice-'+holder+('-obligation' if obligation else '')+'-'+route
        ca,c=case(name,'choice',dict(grant_id=name,holder=holder,classification='unassessed',liability=0,equity=0,cost=0,granted=False,settled=False,services_complete=True,liability_valuation_date=None),{'cash':500,'capital':-500})
        compound=holder=='counterparty';cash=holder=='entity' and obligation
        liability=100 if compound or cash else 0;equity=20 if compound else 0 if cash else 100
        step(ca,c,'choice.grant','2024-01-01',dict(cash_fv=100,share_fv=120 if compound else 100,practice_cash=obligation,policy_cash=False,equity_lacks_substance=False),
          dict(classification='compound' if compound else 'cash' if cash else 'equity',liability=liability,equity=equity,cost=liability+equity,granted=True,
          liability_valuation_date='2024-01-01' if compound or cash else None),
          {'award_expense':liability+equity,'award_liability':-liability,'award_equity':-equity},equity={'award':equity})
        if compound or cash:
            step(ca,c,'choice.remeasure','2024-12-31',dict(liability_fv=130),dict(liability=130,cost=liability+equity+30,liability_valuation_date='2024-12-31'),{'award_expense':30,'award_liability':-30})
            if route=='cash':
                step(ca,c,'choice.settle','2024-12-31',dict(route='cash',cash_paid=130,shares_fv=150,cash_alternative_fv=None),dict(liability=0,settled=True),{'award_liability':130,'cash':-130},cash={'operating':-130})
            else:
                step(ca,c,'choice.settle','2024-12-31',dict(route='shares',cash_paid=0,shares_fv=150,cash_alternative_fv=None),dict(liability=0,equity=150,settled=True),{'award_liability':130,'award_equity':-130},equity={'award':130})
        elif route=='cash':
            step(ca,c,'choice.settle','2024-12-31',dict(route='cash',cash_paid=130,shares_fv=120,cash_alternative_fv=130),dict(equity=-20,cost=110,settled=True),{'award_equity':120,'award_expense':10,'cash':-130},cash={'financing':-120,'operating':-10},equity={'award':-120})
        elif route=='shares-premium':
            step(ca,c,'choice.settle','2024-12-31',dict(route='shares',cash_paid=0,shares_fv=130,cash_alternative_fv=120),dict(equity=110,cost=110,settled=True),{'award_expense':10,'award_equity':-10},equity={'award':10})
        else:
            step(ca,c,'choice.settle','2024-12-31',dict(route='shares',cash_paid=0,shares_fv=120,cash_alternative_fv=130),dict(settled=True))

def populate_eps_hedges(case,step):
    def eps():return dict(period_start='2024-01-01',period_end_exclusive='2025-01-01',
      intervals=[dict(start='2024-01-01',end_exclusive='2025-01-01',ordinary_shares=100)],
      rights='plain',rights_known=True,other_instruments_absent=True,profit=100,continuing_profit=100,
      ordinary_dividends=0,participant_dividends=0,participants=0,participation_weight=0,option_quantity=0,strike=0,
      future_service=0,choice_shares=0,choice_expense=0,choice_continuing_expense=0,average_price=None,
      after_tax_adjustment_known=True,computed=False,numerator=0,denominator=0,diluted_numerator=0,diluted_denominator=0,participant_earnings=0,participant_eps=0)
    specifications=[
      ('weighted','eps.basic',dict(profit=100,continuing_profit=100,intervals=[
        dict(start='2024-01-01',end_exclusive='2024-07-01',ordinary_shares=100),
        dict(start='2024-07-01',end_exclusive='2025-01-01',ordinary_shares=90)]),100,F(17380,183),100,F(17380,183),0,0),
      ('options','eps.options',dict(option_quantity=10,strike=5,future_service=2,average_price=10),100,100,100,103,0,0),
      ('options-control-loss','eps.options',dict(profit=100,continuing_profit=-20,option_quantity=10,strike=5,future_service=2,average_price=10),100,100,100,100,0,0),
      ('choice','eps.choice',dict(profit=90,continuing_profit=90,choice_shares=20,choice_expense=10,choice_continuing_expense=10),90,100,100,120,0,0),
      ('choice-antidilutive','eps.choice',dict(profit=90,continuing_profit=-10,choice_shares=20,choice_expense=10,choice_continuing_expense=10),90,100,90,100,0,0),
      ('participating','eps.participation',dict(rights='uncapped_weighted',profit=120,continuing_profit=120,ordinary_dividends=20,participant_dividends=4,participants=10,participation_weight=2),100,100,100,100,20,2),
    ]
    for name,method,patch,n,d,dn,dd,pe,p_eps in specifications:
        opening=eps();opening.update(patch);ca,c=case('eps-'+name,'eps',opening)
        step(ca,c,method,'2024-12-31',dict(full_period_rights=True),dict(computed=True,numerator=n,denominator=d,
          diluted_numerator=dn,diluted_denominator=dd,participant_earnings=pe,participant_eps=p_eps))
    ca,c=case('fair-value-basis','fvhedge',dict(designation_id='fv-A',principal=100,coupon=21,debt=100,derivative=0,basis=0,
      revised_rate=0,contractual_accrual=0,due_date='2025-01-01',active=True,measured=False,accrued=False,paid=False,settled=False),{'cash':200,'debt':-100,'capital':-100})
    step(ca,c,'fvhedge.measure','2024-01-01',dict(derivative_gain=8,risk_debt_loss=10,eligibility_known=True),dict(debt=110,derivative=8,basis=10,measured=True),{'derivative':8,'debt':-10,'hedge_expense':2})
    step(ca,c,'fvhedge.discontinue','2024-01-01',dict(revised_rate=F(1,10),final_measurement_done=True),dict(active=False,revised_rate=F(1,10)))
    step(ca,c,'fvhedge.accrue','2025-01-01',dict(rate=F(1,10)),dict(debt=121,basis=0,contractual_accrual=21,accrued=True),{'debt':-11,'finance_expense':11})
    step(ca,c,'fvhedge.pay','2025-01-01',dict(amount=121),dict(debt=0,contractual_accrual=0,paid=True),{'debt':121,'cash':-121},cash={'financing':-100,'operating':-21})
    step(ca,c,'fvhedge.settle','2025-01-01',dict(amount=8),dict(derivative=0,settled=True),{'derivative':-8,'cash':8},cash={'operating':8})
    ca,c=case('benchmark-qualified','reform',dict(designation_id='reform-A',principal=100,old_coupon=F(1,25),new_benchmark=F(19,500),spread=F(1,500),reserve=6,
      qualified=False,amended=False,active=True,change_date='2024-07-01',reporting_end='2024-12-31'),{'cash':106,'debt':-100,'cf_reserve':-6})
    step(ca,c,'reform.assess','2024-07-01',dict(direct_cause=True,economically_equivalent=True,additional_changes='none',derecognition_assessed=True),dict(qualified=True))
    step(ca,c,'reform.amend','2024-12-31',dict(documented=True,same_relationship=True),dict(amended=True))
