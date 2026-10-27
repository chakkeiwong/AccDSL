"""Independent benefit/tax calculations from facts, with no author imports."""
from copy import deepcopy
from fractions import Fraction as F

FAMILIES={'ceiling','availability','multiemployer','uncertaintax','acquisitiontax','investmenttax','taxorigin','pillar'}
TAGS={'benefit_ceiling','benefit_availability','multi_employer','uncertain_tax','acquisition_tax','investment_tax','tax_revaluation','pillar_two'}

def calculate_benefit_tax(original,method,p,require):
    c=deepcopy(original);j={};cash={}
    def line(a,v): j[a]=j.get(a,F(0))+v
    def pay(v):
        category='operating'
        if family in ['uncertaintax','pillar']:
            require(p['activity_identification_admitted'] and p['classification']!='unresolved','tax_cash_classification_unresolved','partial')
            category=p['classification']
        line('cash',-v);cash[category]=-v
    family,op=method.split('.')
    if family=='ceiling':
        require(c['phase']=='opening' and c['no_minimum_funding_adjustment'],'ceiling_scope_unsupported','unsupported')
        require(p['current_measurements'] and p['no_earlier_trigger'],'benefit_measurement_unresolved','partial')
        require(0<=p['dbo_reduction']<=c['dbo'] and p['new_economic_benefit']>=0,'benefit_amount_invalid')
        old_asset=c['recognized_asset'];old_ceiling=c['ceiling'];c['dbo']-=p['dbo_reduction']
        surplus=c['plan_assets']-c['dbo'];require(surplus>=0,'benefit_surplus_scope','unsupported')
        c['economic_benefit']=p['new_economic_benefit'];c['recognized_asset']=min(surplus,c['economic_benefit'])
        c['ceiling']=surplus-c['recognized_asset'];c['phase']='amended'
        line('pension_asset',c['recognized_asset']-old_asset);line('income',-p['dbo_reduction'])
        line('oci_pension',c['ceiling']-old_ceiling)
    elif family=='availability':
        require(not c['assessed'],'availability_already_assessed')
        require(p['rights_and_assumptions_current'] and c['funding_assumptions_admitted'],'availability_facts_unresolved','partial')
        require(c['unconditional_refund_right'] is not None,'refund_right_unresolved','partial')
        require(c['zero_discount_assumption'] and c['mutually_exclusive_routes'],'availability_model_unsupported','unsupported')
        require(len(c['future_periods'])==min(c['plan_life_periods'],c['entity_life_periods'])>0,'availability_horizon_mismatch')
        require(c['prepayment']>=0 and all(x['employer_service']>=0 and x['required_funding_without_prepayment']>=0 for x in c['future_periods']),
            'funding_input_invalid')
        surplus=c['plan_assets']-c['dbo'];require(surplus>=0,'benefit_surplus_scope','unsupported')
        refund=F(0)
        if c['unconditional_refund_right']:
            require(c['refund_cost'] is not None and c['refund_cost']>=0,'refund_cost_unresolved','partial')
            refund=max(F(0),surplus-c['refund_cost'])
        if c['minimum_future_funding']:
            reduction=c['prepayment']+max(F(0),sum(x['employer_service']-x['required_funding_without_prepayment'] for x in c['future_periods']))
        else:
            require(c['prepayment']==0,'prepayment_without_minimum_funding')
            reduction=sum(x['employer_service'] for x in c['future_periods'])
        benefit=max(refund,reduction);asset=min(surplus,benefit)
        line('pension_asset',asset-c['recognized_asset']);line('oci_pension',c['recognized_asset']-asset)
        c.update(refund_benefit=refund,contribution_benefit=reduction,economic_benefit=benefit,
            recognized_asset=asset,ceiling=surplus-asset,assessed=True)
    elif family=='multiemployer':
        if op=='classify':
            require(c['phase']=='opening','plan_classification_order')
            require(p['terms_and_relationships_current'] and c['common_control'] is not None and c['defined_benefit_terms'] is not None,
                'plan_terms_unresolved','partial')
            require(not c['common_control'],'common_control_plan_requires_ias19_41','unsupported')
            if not c['defined_benefit_terms']: route='defined_contribution';disclosures=[]
            else:
                require(c['reliable_allocation'] is not None,'plan_information_unresolved','partial')
                if c['reliable_allocation']: route='defined_benefit_share';disclosures=['IAS19.135-148']
                else:
                    require(c['information_condition_admitted'],'ias19_34_finding_required','partial')
                    route='dc_information_fallback';disclosures=['IAS19.148']
            c.update(accounting_route=route,disclosures_required=disclosures,phase='classified')
        elif op=='recognize_deficit':
            require(c['phase']=='classified' and c['accounting_route']=='dc_information_fallback','deficit_recognition_order')
            require(c['deficit_contract_admitted'] and p['contract_effective'],'deficit_contract_unresolved','partial')
            require(c['remaining_years']>0 and c['rate']>=0 and c['deficit_due']>=0,'deficit_measurement_invalid')
            liability=c['deficit_due']/(1+c['rate'])**c['remaining_years']
            c.update(recognized_deficit=liability,phase='recognized',disclosures_required=['IAS19.148','IAS19.37'])
            line('pension_liability',-liability);line('expense',liability)
        elif op=='accrue':
            require(c['phase']=='recognized' and c['remaining_years']>0 and p['full_year_elapsed'],'deficit_accrual_order')
            interest=c['recognized_deficit']*c['rate'];c['recognized_deficit']+=interest;c['remaining_years']-=1
            line('pension_liability',-interest);line('finance_expense',interest)
        else:
            require(c['phase']=='recognized' and c['remaining_years']==0,'deficit_payment_order')
            require(p['cash']==c['recognized_deficit']==c['deficit_due'],'deficit_payment_mismatch')
            pay(p['cash']);line('pension_liability',p['cash']);c.update(recognized_deficit=F(0),paid=p['cash'],phase='settled')
    elif family=='uncertaintax':
        require(c['grouping_admitted'] and c['full_information_examination'] and c['rate_enacted'],'uncertain_tax_admission','partial')
        require(0<=c['rate']<=1,'tax_rate_invalid')
        if op=='pay':
            require(c['phase']=='resolved' and p['cash']==c['current_assessed']-c['current_paid'],'current_tax_payment_mismatch')
            pay(p['cash']);line('current_tax_payable',p['cash']);c.update(current_paid=c['current_paid']+p['cash'],phase='paid')
        else:
            if op=='measure':
                require(c['phase']=='opening','uncertain_tax_order')
                require(p['acceptance_probable'] is not None,'acceptance_finding_unresolved','partial')
                require(c['predictive_choice_admitted'],'predictive_measure_unresolved','partial')
                outcomes=c['outcomes']
                require(all(0<=x['probability']<=1 and 0<=x['deduction']<=c['asset_cost'] for x in outcomes)
                    and sum(x['probability'] for x in outcomes)==1,'tax_outcome_mass_invalid')
                require(len({x['deduction'] for x in outcomes})==len(outcomes),'duplicate_tax_outcome')
                if p['acceptance_probable']:
                    require(p['measure']=='accepted_filing','acceptance_measure_mismatch');deduction=c['filing_deduction']
                else:
                    require(p['measure']!='accepted_filing','acceptance_measure_mismatch')
                    if p['measure']=='expected_value':deduction=sum(x['probability']*x['deduction'] for x in outcomes)
                    else:
                        peak=max(x['probability'] for x in outcomes);choices=[x['deduction'] for x in outcomes if x['probability']==peak]
                        require(len(choices)==1,'most_likely_tie_unresolved','partial');deduction=choices[0]
                c['measure']=p['measure'];c['phase']='measured'
            else:
                require(c['phase']=='measured','uncertain_tax_order')
                require(p['new_evidence_admitted'] and p['no_intervening_changes'],'tax_reassessment_facts_unresolved','partial')
                deduction=p['deduction'];c['measure']='resolved';c['phase']='resolved'
            base=c['asset_cost']-deduction;taxable=c['revenue_before_deduction']-deduction
            require(0<=deduction<=c['asset_cost'] and taxable>=0 and c['carrying']>=base,'tax_loss_or_dta_outside_slice','unsupported')
            current=taxable*c['rate'];dtl=(c['carrying']-base)*c['rate']
            line('current_tax_payable',c['current_assessed']-current);line('dtl',c['dtl']-dtl)
            line('tax_expense',current-c['current_assessed']+dtl-c['dtl'])
            c.update(selected_deduction=deduction,tax_base=base,current_assessed=current,dtl=dtl)
    elif family=='acquisitiontax':
        require(c['phase']=='opening','acquisition_already_recorded')
        require(c['rate_enacted'] and c['full_acquisition'] and c['no_acquired_cash'] and c['scope_admitted']
            and p['acquisition_date_measurements_current'],'acquisition_facts_unresolved','partial')
        require(0<=c['rate']<=1 and c['fair_value']>=c['tax_base']>=0,'acquisition_dta_scope','unsupported')
        dtl=(c['fair_value']-c['tax_base'])*c['rate'];goodwill=c['consideration']-(c['fair_value']-dtl)
        require(goodwill>=0,'bargain_purchase_requires_reassessment','partial')
        line('cash',-c['consideration']);cash['investing']=-c['consideration']
        line('ppe',c['fair_value']);line('dtl',-dtl);line('goodwill',goodwill)
        c.update(recognized_asset=c['fair_value'],dtl=dtl,goodwill=goodwill,phase='acquired')
    elif family=='investmenttax':
        require(not c['assessed'],'investment_already_assessed')
        require(p['findings_current'] and c['rate_enacted'] and c['recovery_manner_admitted'],'investment_tax_facts_unresolved','partial')
        require(c['difference']>=0 and 0<=c['rate']<=1,'investment_tax_amount_invalid')
        dtl=dta=F(0)
        if c['difference_kind']=='taxable':
            require(c['reversal_control'] is not None and c['foreseeable_nonreversal_probable'] is not None,'investment_exception_unresolved','partial')
            if not (c['reversal_control'] and c['foreseeable_nonreversal_probable']):dtl=c['difference']*c['rate']
        else:
            require(c['foreseeable_reversal_probable'] is not None and c['taxable_profit_available'] is not None,'investment_dta_unresolved','partial')
            if c['foreseeable_reversal_probable'] and c['taxable_profit_available']:dta=c['difference']*c['rate']
        line('dtl',c['dtl']-dtl);line('dta',dta-c['dta']);line('tax_expense',dtl-c['dtl']-dta+c['dta'])
        c.update(dtl=dtl,dta=dta,assessed=True)
    elif family=='taxorigin':
        require(c['rate_enacted'] and c['recovery_probable'],'tax_origin_facts_unresolved','partial')
        if op=='rate':
            require(p['new_rate_enacted'] and p['recovery_manner_unchanged'],'tax_rate_admission_unresolved','partial')
            require(0<=p['new_rate']<=1 and c['prior_profit_loss']==0 and c['dta']==0 and c['carrying']-c['tax_base']==c['gross_surplus'],
                'mixed_tax_rate_origin_requires_allocation','unsupported')
            dtl=(c['carrying']-c['tax_base'])*p['new_rate'];change=dtl-c['dtl']
            line('dtl',-change);line('oci_revaluation',change)
            c.update(rate=p['new_rate'],dtl=dtl,tax_oci_to_date=c['tax_oci_to_date']+change)
        else:
            require(p['no_time_or_base_change'],'tax_reversal_cap_update_required','partial')
            require(p['recoverable']>=0,'recoverable_amount_invalid')
            old_dtl,old_dta=c['dtl'],c['dta']
            if op=='impair':
                require(p['recoverable']<=c['carrying'],'impairment_direction_mismatch')
                change=c['carrying']-p['recoverable'];oci=min(change,c['gross_surplus']);pl=change-oci
                c['gross_surplus']-=oci;c['prior_profit_loss']+=pl;c['carrying']=p['recoverable']
                line('ppe',-change);line('oci_revaluation',oci);line('expense',pl)
            else:
                require(p['changed_estimates_admitted'],'changed_estimates_required','partial')
                new=min(p['recoverable'],c['no_impairment_carrying']);require(new>=c['carrying'],'reversal_direction_mismatch')
                change=new-c['carrying'];pl=min(change,c['prior_profit_loss']);oci=change-pl
                c['prior_profit_loss']-=pl;c['gross_surplus']+=oci;c['carrying']=new
                line('ppe',change);line('income',-pl);line('oci_revaluation',-oci)
            difference=c['carrying']-c['tax_base'];dtl=max(difference,F(0))*c['rate'];dta=max(-difference,F(0))*c['rate']
            # This slice's taxable surplus is wholly OCI and deductible deficit wholly profit.
            require(max(difference,F(0))==c['gross_surplus'],'mixed_tax_origin_outside_slice','unsupported')
            tax_oci=dtl-old_dtl;tax_pl=old_dta-dta
            line('dtl',old_dtl-dtl);line('dta',dta-old_dta);line('oci_revaluation',tax_oci);line('tax_expense',tax_pl)
            c.update(dtl=dtl,dta=dta,tax_profit_to_date=c['tax_profit_to_date']+tax_pl,tax_oci_to_date=c['tax_oci_to_date']+tax_oci)
    elif family=='pillar':
        require(c['scope_admitted'] and c['legislation_enacted'],'pillar_scope_unresolved','partial')
        require(c['dtl']==c['dta']==0,'pillar_deferred_tax_prohibited')
        if op=='recognize':
            require(c['phase']=='opening' and c['legislation_effective'],'pillar_current_order')
            require(p['current_amount_admitted'] and p['current_tax'] is not None,'pillar_current_tax_unresolved','partial')
            require(p['current_tax']>=0,'pillar_amount_invalid')
            line('pillar_tax_payable',-p['current_tax']);line('pillar_tax_expense',p['current_tax'])
            c.update(current_assessed=p['current_tax'],exception_applied=True,exception_disclosed=True,current_separately_disclosed=True,phase='recognized')
        elif op=='pay':
            require(c['phase']=='recognized' and p['cash']==c['current_assessed']-c['paid'],'pillar_payment_mismatch')
            pay(p['cash']);line('pillar_tax_payable',p['cash']);c.update(paid=c['paid']+p['cash'],phase='paid')
        else:
            require(c['phase']=='opening' and not c['legislation_effective'],'pillar_exposure_scope')
            if p['known_or_estimable']:
                require(p['lower'] is not None and p['upper'] is not None and 0<=p['lower']<=p['upper'],'pillar_exposure_interval_invalid')
            else:
                require(p['lower'] is p['upper'] is None and bool(p['unavailable_explanation']) and bool(p['assessment_progress']),
                    'pillar_exposure_disclosure_missing','partial')
            c.update(exception_applied=True,exception_disclosed=True,exposure_known=p['known_or_estimable'],
                exposure_lower=p['lower'],exposure_upper=p['upper'],unavailable_explanation=p['unavailable_explanation'],
                assessment_progress=p['assessment_progress'],phase='exposure_disclosed')
    else:raise AssertionError(method)
    return c,{k:v for k,v in j.items() if v},{k:cash.get(k,F(0)) for k in ['operating','investing','financing','unclassified']}

def check_benefit_tax(tag,c,b):
    if tag in ['benefit_ceiling','benefit_availability']:
        assert b['pension_asset']==c['recognized_asset']==min(c['plan_assets']-c['dbo'],c['economic_benefit'])
        assert c['ceiling']==c['plan_assets']-c['dbo']-c['recognized_asset']>=0
    elif tag=='multi_employer':assert -b['pension_liability']==c['recognized_deficit']
    elif tag=='uncertain_tax':
        assert -b['current_tax_payable']==c['current_assessed']-c['current_paid'] and -b['dtl']==c['dtl'] and b['ppe']==c['carrying']
    elif tag=='acquisition_tax':
        assert b['ppe']==c['recognized_asset'] and b['goodwill']==c['goodwill'] and -b['dtl']==c['dtl']
    elif tag=='investment_tax':assert b['dta']==c['dta'] and -b['dtl']==c['dtl']
    elif tag=='tax_revaluation':
        assert b['ppe']==c['carrying'] and b['dta']==c['dta'] and -b['dtl']==c['dtl']
        assert -b['oci_revaluation']==c['gross_surplus']-c['dtl']
    elif tag=='pillar_two':
        assert b['dtl']==b['dta']==c['dtl']==c['dta']==0 and -b['pillar_tax_payable']==c['current_assessed']-c['paid']
    else:raise AssertionError(tag)
