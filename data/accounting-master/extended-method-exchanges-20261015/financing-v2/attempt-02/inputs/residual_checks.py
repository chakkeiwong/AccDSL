"""Independent residual accounting derivations. No expected-fixture imports."""
from copy import deepcopy
from datetime import date, timedelta
from fractions import Fraction as F

def pv(c,rate):
    return sum(F(c['coupon'])/(1+F(rate))**i for i in range(1,int(c['periods'])+1))+F(c['redemption'])/(1+F(rate))**int(c['periods'])

def anniversary(start,years,require):
    """Contractual whole/six-month anniversaries; no actual-day approximation."""
    months=F(years)*12
    require(months.denominator==1 and months>=0,'anniversary_scope','unsupported')
    d=date.fromisoformat(start);index=d.year*12+d.month-1+int(months)
    try:return date(index//12,index%12+1,d.day).isoformat()
    except ValueError:require(False,'anniversary_calendar_method_required','unsupported')

def derive(tag,original,method,p,event_date,require):
    c=deepcopy(original); j={}
    cash={k:F(0) for k in ['operating','investing','financing','unclassified']}
    oci={k:F(0) for k in ['cash_flow','intrinsic','cost']}
    eq={k:F(0) for k in ['issue','award','basis_transfer','repurchase','reissue']}
    def line(k,v): j[k]=j.get(k,F(0))+v
    def flow(v,kind='financing'):line('cash',v);cash[kind]+=v
    def known(v,code):require(v is not None,code,'partial');return v

    if tag=='debt':
        if method=='debt.issue':
            require(not c['originated'] and event_date==c['issue_date'],'debt_issue_order')
            n=c['term_years'];require(n>0 and n.denominator==1,'integer_term_required','unsupported')
            require(c['due_date']==anniversary(c['issue_date'],n,require),'debt_contract_calendar')
            require(p['proceeds']>0 and p['rate']>=0,'debt_issue_value')
            require(p['proceeds']*(1+p['rate'])**int(n)==c['principal']+c['legal_interest'],'eir_identity')
            require(p['proceeds']==c['principal'],'issue_at_principal_scope','unsupported')
            flow(p['proceeds']);line('debt',-p['proceeds'])
            c.update(originated=True,carrying=p['proceeds'],rate=p['rate'])
        elif method=='debt.fee':
            require(c['originated'] and c['elapsed_years']==0 and c['rate_mode']=='exact' and event_date==c['issue_date'],'fee_order')
            require(p['directly_attributable'],'fee_purpose_unresolved','partial')
            net=c['carrying']-p['amount'];lo,hi=p['rate_low'],p['rate_high']
            require(0<p['amount']<c['carrying'] and 0<=lo<hi and hi-lo<=F(1,1000),'rate_bracket_width')
            n=int(c['term_years']);due=c['principal']+c['legal_interest']
            require(net*(1+lo)**n<=due<=net*(1+hi)**n,'rate_bracket_sign')
            flow(-p['amount']);line('debt',p['amount'])
            c.update(carrying=net,rate_mode='enclosure',rate=F(0),rate_low=lo,rate_high=hi)
        elif method=='debt.accrue':
            require(c['originated'],'debt_not_issued')
            require(c['rate_mode']=='exact','enclosure_not_exact_accrual','unsupported')
            t,f=p['year_fraction'],p['factor'];require(0<t<=1 and t.denominator<=2,'period_factor_scope','unsupported')
            require(f>0 and f**t.denominator==(1+c['rate'])**t.numerator,'period_factor_identity')
            require(c['elapsed_years']+t<=c['term_years'] and event_date<=c['due_date'],'accrual_beyond_maturity')
            require(event_date==anniversary(c['issue_date'],c['elapsed_years']+t,require),'debt_accrual_calendar')
            expense=c['carrying']*(f-1);line('finance_expense',expense);line('debt',-expense)
            c.update(carrying=c['carrying']+expense,elapsed_years=c['elapsed_years']+t)
        elif method=='debt.pay':
            require(c['originated'] and event_date>=c['due_date'] and c['elapsed_years']==c['term_years'],'debt_payment_order')
            require(not p['legal_release_of_unpaid'],'release_requires_separate_method','unsupported')
            a,b=p['principal'],p['interest']
            require(0<=a<=c['principal'] and 0<=b<=c['legal_interest'] and a+b>0,'legal_payment_allocation')
            require(c['carrying']==c['principal']+c['legal_interest'],'maturity_carrying_mismatch')
            line('debt',a+b);flow(-a);flow(-b,'operating')
            c.update(carrying=c['carrying']-a-b,principal=c['principal']-a,legal_interest=c['legal_interest']-b,
                defaulted=c['principal']+c['legal_interest']>a+b)
        else:require(False,'unknown_method','unsupported')
    elif tag=='modification':
        if method=='modification.change':
            require(c['phase']=='original' and event_date<c['due_date'],'modification_order')
            require(c['due_date']==anniversary(event_date,1,require),'modification_one_year_scope','unsupported')
            require(p['fee_scope_known'],'fee_scope_unresolved','partial')
            require(p['qualitative']!='unknown','qualitative_unresolved','partial')
            require(min(p['lender_fee'],p['third_party_fee'])>=0 and p['new_payment']>0,'modification_value')
            require(F(c['old_payment'])/(1+c['old_rate'])==c['carrying'],'one_year_old_cashflow_identity')
            pv_new=F(p['new_payment'])/(1+c['old_rate'])
            ratio=F(abs(pv_new+p['lender_fee']-c['carrying']))/c['carrying']
            substantial=ratio>=F(1,10) or p['qualitative']=='substantial'
            fees=p['lender_fee']+p['third_party_fee']
            if substantial:
                target=known(p['replacement_fv'],'replacement_fv_unresolved')
                require(target>0,'replacement_value')
                line('finance_expense',target-c['carrying']+fees)
            else:
                target=pv_new-fees;require(target>0,'modified_carrying_nonpositive')
                line('other_gains',pv_new-c['carrying'])
            line('debt',c['carrying']-target);flow(-fees)
            c.update(carrying=target,principal_basis=target,new_payment=p['new_payment'],new_rate=F(p['new_payment'])/target-1,
                test_ratio=ratio,outcome='substantial' if substantial else 'non_substantial',phase='modified')
        elif method=='modification.accrue':
            require(c['phase']=='modified' and event_date==c['due_date'],'modification_accrual_order')
            require(p['rate']==c['new_rate'],'replacement_rate_mismatch')
            v=c['carrying']*p['rate'];line('finance_expense',v);line('debt',-v)
            c.update(carrying=c['carrying']+v,phase='accrued')
        elif method=='modification.pay':
            require(c['phase']=='accrued' and event_date>=c['due_date'],'modified_payment_order')
            require(p['amount']==c['new_payment']==c['carrying'],'modified_payment_mismatch')
            line('debt',p['amount']);flow(-c['principal_basis']);flow(-(p['amount']-c['principal_basis']),'operating')
            c.update(carrying=F(0),phase='paid')
        else:require(False,'unknown_method','unsupported')
    elif tag=='shares':
        n,price=p['quantity'],p['price'];require(n>0 and n.denominator==1 and price>=0,'share_quantity_or_price')
        amount=n*price
        if method=='shares.issue':
            flow(amount);line('capital',-amount);eq['issue']=amount
            c.update(issued=c['issued']+n,capital=c['capital']+amount)
        elif method=='shares.buy':
            require(n<=c['issued']-c['treasury'],'buyback_exceeds_outstanding')
            flow(-amount);line('treasury',amount);eq['repurchase']=-amount
            c.update(treasury=c['treasury']+n,treasury_cost=c['treasury_cost']+amount)
        elif method=='shares.reissue':
            require(n<=c['treasury'],'reissue_exceeds_treasury')
            cost=F(c['treasury_cost'])*n/c['treasury'];surplus=amount-cost
            flow(amount);line('treasury',-cost);line('share_surplus',-surplus);eq['reissue']=amount
            c.update(treasury=c['treasury']-n,treasury_cost=c['treasury_cost']-cost,surplus=c['surplus']+surplus)
        else:require(False,'unknown_method','unsupported')
    elif tag=='compound':
        if method=='compound.issue':
            require(c['phase']=='unissued','compound_issue_order')
            require(c['due_date']==anniversary(event_date,1,require),'compound_one_year_scope','unsupported')
            require(p['fixed_for_fixed'],'compound_classification_method_required','unsupported')
            d=known(p['debt_fv'],'debt_fv_unresolved');require(0<d<=p['proceeds'],'compound_issue_value')
            require(d*(1+c['rate'])==c['redemption'],'compound_rate_identity')
            e=p['proceeds']-d;flow(p['proceeds']);line('debt',-d);line('original_equity',-e);eq['issue']=e
            c.update(debt=d,debt_cash_basis=d,original_equity=e,phase='issued')
        elif method=='compound.accrue':
            require(c['phase']=='issued' and event_date==c['due_date'],'compound_accrual_order')
            require(p['rate']==c['rate'],'compound_rate_mismatch')
            v=c['debt']*p['rate'];line('finance_expense',v);line('debt',-v);c.update(debt=c['debt']+v,phase='matured')
        elif method=='compound.end':
            require(c['phase']=='matured' and event_date>=c['due_date'],'compound_end_order')
            require(p['original_rights_unchanged'],'inducement_method_required','unsupported')
            line('debt',c['debt'])
            if p['route']=='redeem':
                require(p['amount_or_shares']==c['redemption']==c['debt'],'compound_redemption_mismatch')
                require(0<c['debt_cash_basis']<=c['debt'],'compound_cash_basis')
                flow(-c['debt_cash_basis']);flow(-(c['debt']-c['debt_cash_basis']),'operating')
            else:
                require(p['amount_or_shares']==c['fixed_shares'],'conversion_share_mismatch')
                line('capital',-c['debt']);eq['issue']=c['debt'];c['capital']+=c['debt']
            c.update(debt=F(0),phase='ended')
        elif method=='compound.repurchase':
            require(c['phase']=='issued' and event_date<c['due_date'],'repurchase_order')
            require(p['unchanged_rights'],'inducement_method_required','unsupported')
            require(p['comparable_debt_rate_known'],'comparable_debt_value_unresolved','partial')
            require(c['periods']>0 and c['periods'].denominator==1,'repurchase_schedule_scope','unsupported')
            old,new=pv(c,c['old_period_rate']),pv(c,c['current_period_rate'])
            if c['valuation_mode']=='source_rounded':old,new=F(round(old)),F(round(new))
            require(c['debt']==old and p['consideration']>=new,'repurchase_allocation_scope','unsupported')
            e=p['consideration']-new;line('debt',c['debt']);line('finance_expense',new-c['debt'])
            line('original_equity',c['original_equity']);line('retained',e-c['original_equity']);flow(-p['consideration']);eq['repurchase']=-e
            c.update(debt=F(0),retained_debit=c['retained_debit']+e-c['original_equity'],original_equity=F(0),phase='ended')
        else:require(False,'unknown_method','unsupported')
    else:
        return derive_other(tag,c,method,p,event_date,require)
    j={k:v for k,v in j.items() if v};require(sum(j.values())==0,'derived_journal_unbalanced')
    return c,j,cash,oci,eq

def derive_other(tag,c,method,p,event_date,require):
    j={};cash={k:F(0) for k in ['operating','investing','financing','unclassified']}
    oci={k:F(0) for k in ['cash_flow','intrinsic','cost']}
    eq={k:F(0) for k in ['issue','award','basis_transfer','repurchase','reissue']}
    def line(k,v):j[k]=j.get(k,F(0))+v
    def known(v,code):require(v is not None,code,'partial');return v
    def cost(target,liability=False):
        delta=target-c['cost'];line('award_expense',delta)
        if liability:line('award_liability',-(target-c['liability']));c['liability']=target
        else:line('award_equity',-delta);eq['award']=delta;c['award_equity']+=delta
        c['cost']=target
    if tag=='vesting':
        require(not c['paid'],'award_already_paid')
        if method=='vesting.service':
            require(not c['cancelled'] and p['elapsed']==c['elapsed']+1 and p['elapsed']<=c['years'],'vesting_clock')
            require(event_date>=c['service_dates'][p['elapsed']-1],'future_service')
            require(p['other_conditions_met'],'vesting_conditions_unresolved','partial')
            require(p['employees']>=0,'negative_employees')
            # Market hurdles enter grant FV, not a subsequent cost reversal.
            target=F(p['employees'])*c['awards_each']*c['grant_fv']*F(p['elapsed'],c['years'])
            cost(target);c.update(employees=p['employees'],elapsed=p['elapsed'])
        elif method=='vesting.fail':
            require(not c['cancelled'] and c['elapsed']>0,'vesting_failure_order')
            require(c['condition']!='market' and p['non_market_failure'],'market_reversal_forbidden')
            cost(F(0));c.update(employees=F(0),cancelled=True)
        elif method=='vesting.cancel':
            require(not c['cancelled'] and 0<c['elapsed']<c['years'],'cancellation_order')
            require(not p['replacement'],'replacement_award_method_required','unsupported')
            cost(F(c['employees'])*c['awards_each']*c['grant_fv']);c['cancelled']=True
        elif method=='vesting.pay':
            require(c['cancelled'],'cancellation_payment_order')
            fv=known(p['award_fv'],'cancellation_fv_unresolved');require(min(fv,p['amount'])>=0,'cancellation_value')
            equity=min(fv,p['amount']);excess=p['amount']-equity
            line('award_equity',equity);line('award_expense',excess);line('cash',-p['amount'])
            cash['financing']=-equity;cash['operating']=-excess
            eq['award']=-equity;c.update(award_equity=c['award_equity']-equity,cost=c['cost']+excess,paid=True)
        else:require(False,'unknown_method','unsupported')
    elif tag=='cashaward':
        require(not c['paid'],'award_already_paid')
        fv=known(p['fv'],'cash_award_fv_unresolved');require(fv>=0,'cash_award_value')
        if method=='cashaward.service':
            require(p['elapsed']==c['elapsed']+1 and p['elapsed']<=c['years'],'cash_award_clock')
            require(event_date>=c['service_dates'][p['elapsed']-1] and p['employees']>=0,'cash_award_service')
            target=F(p['employees'])*c['awards_each']*fv*F(p['elapsed'],c['years'])
            cost(target,True);c.update(employees=p['employees'],elapsed=p['elapsed'],last_fv=fv)
        elif method=='cashaward.settle':
            require(c['elapsed']==c['years'],'cash_award_not_vested')
            target=F(c['employees'])*c['awards_each']*fv;require(p['amount']==target,'cash_award_payment_mismatch')
            cost(target,True);line('award_liability',target);line('cash',-target);cash['operating']=-target
            c.update(liability=F(0),last_fv=fv,paid=True)
        else:require(False,'unknown_method','unsupported')
    elif tag=='choice':
        require(not c['settled'],'choice_already_settled')
        if method=='choice.grant':
            require(not c['granted'],'choice_grant_order')
            require(c['services_complete'],'choice_service_schedule_method_required','unsupported')
            sf=known(p['share_fv'],'choice_share_fv_unresolved');cf=known(p['cash_fv'],'choice_cash_fv_unresolved')
            require(min(sf,cf)>=0,'choice_value')
            if c['holder']=='counterparty':
                require(sf>=cf,'compound_choice_value_order');liability,equity=cf,sf-cf;classification='compound'
            else:
                findings=[p[k] for k in ['practice_cash','policy_cash','equity_lacks_substance']]
                require(all(v is not None for v in findings),'present_cash_obligation_unresolved','partial')
                obligation=any(findings);classification='cash' if obligation else 'equity'
                liability,equity=(cf,F(0)) if obligation else (F(0),sf)
            line('award_expense',liability+equity);line('award_liability',-liability);line('award_equity',-equity);eq['award']=equity
            c.update(classification=classification,liability=liability,equity=equity,cost=liability+equity,granted=True,
                liability_valuation_date=event_date if classification in ['compound','cash'] else None)
        elif method=='choice.remeasure':
            require(c['granted'] and c['classification'] in ['compound','cash'],'choice_liability_required','unsupported')
            fv=known(p['liability_fv'],'choice_liability_fv_unresolved');require(fv>=0,'choice_liability_value')
            delta=fv-c['liability'];line('award_expense',delta);line('award_liability',-delta)
            c.update(liability=fv,cost=c['cost']+delta,liability_valuation_date=event_date)
        elif method=='choice.settle':
            require(c['granted'],'choice_not_granted')
            sf=known(p['shares_fv'],'settlement_share_fv_unresolved')
            require(min(sf,p['cash_paid'])>=0,'choice_settlement_value')
            if c['classification'] in ['compound','cash']:
                require(c['liability_valuation_date']==event_date,'choice_settlement_remeasurement_required','partial')
                if p['route']=='cash':
                    require(p['cash_paid']==c['liability'],'remeasure_before_cash_settlement')
                    line('award_liability',c['liability']);line('cash',-p['cash_paid']);cash['operating']=-p['cash_paid']
                else:
                    require(p['cash_paid']==0 and sf>=c['liability'],'choice_share_settlement_scope','unsupported')
                    require(c['classification']=='compound' or sf==c['liability'],'cash_classified_share_method_required','unsupported')
                    line('award_liability',c['liability']);line('award_equity',-c['liability']);eq['award']=c['liability'];c['equity']+=c['liability']
                c['liability']=F(0)
            else:
                cf=known(p['cash_alternative_fv'],'settlement_cash_alternative_unresolved')
                require(cf>=0,'choice_settlement_value')
                if p['route']=='cash':
                    # Entity elects cash; any excess over the equity alternative is expense.
                    require(p['cash_paid']==cf,'cash_alternative_payment_mismatch')
                    excess=max(F(0),p['cash_paid']-sf);debit=p['cash_paid']-excess
                    line('award_equity',debit);line('award_expense',excess);line('cash',-p['cash_paid'])
                    cash['financing']=-debit;cash['operating']=-excess
                    eq['award']=-debit;c.update(equity=c['equity']-debit,cost=c['cost']+excess)
                else:
                    require(p['cash_paid']==0,'share_settlement_cash_mismatch')
                    excess=max(F(0),sf-cf)
                    line('award_expense',excess);line('award_equity',-excess);eq['award']=excess
                    c.update(equity=c['equity']+excess,cost=c['cost']+excess)
            c['settled']=True
        else:require(False,'unknown_method','unsupported')
    elif tag=='eps':
        require(not c['computed'],'eps_already_computed')
        require(c['rights_known'],'eps_rights_unresolved','partial')
        require(c['other_instruments_absent'],'eps_ordered_series_method_required','unsupported')
        require(p['full_period_rights'],'eps_changing_rights_method_required','unsupported')
        # Dates designate completed reporting days; intervals remain [start,end).
        require(date.fromisoformat(event_date)>=date.fromisoformat(c['period_end_exclusive'])-timedelta(days=1),'eps_period_not_complete')
        days=(date.fromisoformat(c['period_end_exclusive'])-date.fromisoformat(c['period_start'])).days
        require(days>0,'eps_empty_period');cursor=c['period_start'];weighted=F(0)
        for part in c['intervals']:
            require(part['start']==cursor and part['start']<part['end_exclusive']<=c['period_end_exclusive'] and part['ordinary_shares']>=0,'eps_interval_partition')
            weighted+=part['ordinary_shares']*F((date.fromisoformat(part['end_exclusive'])-date.fromisoformat(part['start'])).days,days)
            cursor=part['end_exclusive']
        require(cursor==c['period_end_exclusive'] and weighted>0,'eps_interval_partition')
        n=F(c['profit']);dn=n;dd=weighted;pe=F(0);p_eps=F(0)
        if method=='eps.participation':
            require(c['rights']=='uncapped_weighted' and c['participants']>0 and c['participation_weight']>0,'participation_rights_scope','unsupported')
            require(all(v['ordinary_shares']==weighted for v in c['intervals']),'changing_participation_method_required','unsupported')
            require(c['profit']>=c['ordinary_dividends']+c['participant_dividends'],'participating_loss_method_required','unsupported')
            undistributed=c['profit']-c['ordinary_dividends']-c['participant_dividends']
            weight=weighted+c['participants']*c['participation_weight']
            n=c['ordinary_dividends']+F(undistributed)*weighted/weight
            pe=c['participant_dividends']+F(undistributed)*c['participants']*c['participation_weight']/weight
            p_eps=F(pe)/c['participants'];dn=n
        else:
            require(c['rights']=='plain' and c['participants']==0,'plain_rights_required','unsupported')
            if method=='eps.options':
                price=known(c['average_price'],'average_price_unresolved');require(price>0 and min(c['option_quantity'],c['strike'],c['future_service'])>=0,'option_dilution_value')
                incremental=max(F(0),c['option_quantity']-F(c['option_quantity'])*(c['strike']+c['future_service'])/price)
                if c['continuing_profit']>0:dd+=incremental
            elif method=='eps.choice':
                require(c['after_tax_adjustment_known'],'eps_after_tax_adjustment_unresolved','partial')
                require(c['choice_shares']>0,'choice_shares_nonpositive')
                adjusted=c['continuing_profit']+c['choice_continuing_expense']
                if F(adjusted)/(weighted+c['choice_shares'])<F(c['continuing_profit'])/weighted:
                    dn+=c['choice_expense'];dd+=c['choice_shares']
            else:require(method=='eps.basic','unknown_method','unsupported')
        c.update(computed=True,numerator=n,denominator=weighted,diluted_numerator=dn,diluted_denominator=dd,participant_earnings=pe,participant_eps=p_eps)
    elif tag=='fvhedge':
        if method=='fvhedge.measure':
            require(c['active'] and not c['paid'],'fair_value_hedge_inactive')
            require(p['eligibility_known'],'fair_value_eligibility_unresolved','partial')
            d=known(p['derivative_gain'],'fair_value_unresolved');b=known(p['risk_debt_loss'],'fair_value_unresolved')
            line('derivative',d-c['derivative']);line('debt',-(b-c['basis']));line('hedge_expense',(b-c['basis'])-(d-c['derivative']))
            c.update(derivative=d,debt=c['debt']+b-c['basis'],basis=b,measured=True)
        elif method=='fvhedge.discontinue':
            require(c['active'] and c['measured'],'fair_value_discontinue_order')
            require(c['due_date']==anniversary(event_date,1,require),'basis_one_year_scope','unsupported')
            require(p['final_measurement_done'],'final_measurement_unresolved','partial')
            require(c['debt']*(1+p['revised_rate'])==c['principal']+c['coupon'],'basis_amortization_rate')
            c.update(active=False,revised_rate=p['revised_rate'])
        elif method=='fvhedge.accrue':
            require(not c['active'] and not c['accrued'] and event_date==c['due_date'],'basis_accrual_order')
            require(p['rate']==c['revised_rate'],'basis_rate_mismatch')
            expense=c['debt']*p['rate'];line('finance_expense',expense);line('debt',-expense)
            c.update(debt=c['debt']+expense,basis=c['basis']+expense-c['coupon'],contractual_accrual=c['coupon'],accrued=True)
            require(c['basis']==0,'basis_not_amortized')
        elif method=='fvhedge.pay':
            require(c['accrued'] and not c['paid'] and event_date>=c['due_date'],'fair_value_payment_order')
            require(p['amount']==c['debt']==c['principal']+c['coupon'],'fair_value_payment_value')
            line('debt',c['debt']);line('cash',-p['amount']);cash['financing']=-c['principal'];cash['operating']=-c['coupon']
            c.update(debt=F(0),contractual_accrual=F(0),paid=True)
        elif method=='fvhedge.settle':
            require(not c['settled'] and p['amount']==c['derivative'],'fair_value_settlement_value')
            line('derivative',-p['amount']);line('cash',p['amount']);cash['operating']=p['amount'];c.update(derivative=F(0),settled=True)
        else:require(False,'unknown_method','unsupported')
    elif tag=='reform':
        if method=='reform.assess':
            require(not c['qualified'] and event_date==c['change_date'],'reform_assessment_order')
            require(p['direct_cause'] is not None and p['economically_equivalent'] is not None,'reform_findings_unresolved','partial')
            require(p['direct_cause'] and p['economically_equivalent'],'reform_relief_failed')
            require(p['additional_changes']!='unassessed' and p['derecognition_assessed'],'reform_additional_assessment_unresolved','partial')
            require(p['additional_changes']=='none','reform_additional_method_required','unsupported')
            require(c['old_coupon']==c['new_benchmark']+c['spread'],'illustrative_coupon_mismatch')
            c['qualified']=True
        elif method=='reform.amend':
            require(c['qualified'] and not c['amended'] and c['change_date']<=event_date<=c['reporting_end'],'reform_designation_timing')
            require(p['documented'],'reform_documentation_unresolved','partial')
            require(p['same_relationship'] and c['active'],'reform_new_designation_method_required','unsupported')
            c['amended']=True
        else:require(False,'unknown_method','unsupported')
    else:require(False,'unsupported_component','unsupported')
    j={k:v for k,v in j.items() if v};require(sum(j.values())==0,'derived_journal_unbalanced')
    return c,j,cash,oci,eq

def check_component(tag,c,b):
    if tag in ['debt','modification']:
        assert -b['debt']==c['carrying']>=0
        if tag=='debt':
            assert c['principal']>=0 and c['legal_interest']>=0 and 0<=c['elapsed_years']<=c['term_years']
            assert c['rate']>=0 and c['term_years']>0 and c['issue_date']<c['due_date']
        else:assert c['old_rate']>=0 and c['old_payment']>0 and c['principal_basis']>=0
    elif tag=='shares':
        assert -b['capital']==c['capital'] and b['treasury']==c['treasury_cost'] and -b['share_surplus']==c['surplus']
        assert 0<=c['treasury']<=c['issued'] and c['treasury_cost']>=0
    elif tag=='compound':
        assert -b['debt']==c['debt'] and -b['original_equity']==c['original_equity'] and -b['capital']==c['capital']
        assert b['retained']==c['retained_debit']
        assert min(c['debt'],c['debt_cash_basis'],c['original_equity'],c['fixed_shares'],c['rate'])>=0
        assert c['debt_cash_basis']<=c['redemption'] and c['redemption']>0
        if c['phase']=='unissued':assert c['debt']==c['debt_cash_basis']==c['original_equity']==0
        elif c['phase']=='ended':assert c['debt']==0
    elif tag in ['vesting','cashaward']:
        assert 0<=c['elapsed']<=c['years'] and c['years']>0 and len(c['service_dates'])==c['years'] and c['service_dates']==sorted(set(c['service_dates']))
        assert c['employees']>=0 and c['awards_each']>=0
        assert b['award_expense']==c['cost']
        if tag=='vesting':assert -b['award_equity']==c['award_equity']
        else:assert -b['award_liability']==c['liability']
    elif tag=='choice':
        assert -b['award_liability']==c['liability'] and -b['award_equity']==c['equity'] and b['award_expense']==c['cost']
        assert c['liability']>=0 and c['cost']>=0
        if c['settled']:assert c['granted'] and c['liability']==0
    elif tag=='eps':assert c['denominator']>0 if c['computed'] else c['denominator']==0
    elif tag=='fvhedge':
        assert -b['debt']==c['debt'] and b['derivative']==c['derivative'] and b['cf_reserve']==0
        assert c['debt']==(0 if c['paid'] else c['principal']+c['contractual_accrual']+c['basis'])
    elif tag=='reform':assert -b['cf_reserve']==c['reserve'] and -b['debt']==c['principal']
    else:raise AssertionError(tag)
