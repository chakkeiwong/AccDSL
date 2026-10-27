"""Authored existing benefit/tax examples; independent arithmetic is elsewhere."""
from copy import deepcopy

def populate_benefit_tax(case,step):
    c=case('pension-ceiling-amendment','benefit_ceiling',{'plan_id':'ceiling-plan','dbo':'100','plan_assets':'130',
        'economic_benefit':'10','ceiling':'20','recognized_asset':'10','no_minimum_funding_adjustment':True,'phase':'opening'},
        {'cash':'100','pension_asset':'10','capital':'-110'})
    step(c,'ceiling.amend',{'dbo_reduction':'20','new_economic_benefit':'15','current_measurements':True,'no_earlier_trigger':True},
        {'dbo':'80','economic_benefit':'15','ceiling':'35','recognized_asset':'15','phase':'amended'},
        {'pension_asset':'5','income':'-20','oci_pension':'15'})
    for key,right,asset,ceiling,refund in [('refund-availability',True,'25','5','25'),('contribution-availability',False,'10','20','0')]:
        c=case(key,'benefit_availability',{'plan_id':'availability-plan','dbo':'100','plan_assets':'130',
            'recognized_asset':asset,'ceiling':ceiling,'prepayment':'7','unconditional_refund_right':right,'refund_cost':'5' if right else None,
            'minimum_future_funding':True,'future_periods':[{'employer_service':'20','required_funding_without_prepayment':'12'},
                {'employer_service':'20','required_funding_without_prepayment':'25'}],
            'plan_life_periods':2,'entity_life_periods':2,'zero_discount_assumption':True,'mutually_exclusive_routes':True,
            'funding_assumptions_admitted':True,'refund_benefit':None,'contribution_benefit':None,'economic_benefit':asset,'assessed':False},
            {'cash':'100','pension_asset':asset,'capital':'-125' if right else '-110'})
        step(c,'availability.assess',{'rights_and_assumptions_current':True},
            {'refund_benefit':refund,'contribution_benefit':'10','assessed':True},{})

    c=case('multi-employer-deficit','multi_employer',{'plan_id':'multi-plan','common_control':False,'defined_benefit_terms':True,
        'reliable_allocation':False,'information_condition_admitted':True,'accounting_route':'unclassified','disclosures_required':[],
        'deficit_contract_admitted':True,'deficit_due':'121','rate':'1/10','recognized_deficit':'0','paid':'0','remaining_years':2,
        'phase':'opening'}, {'cash':'200','capital':'-200'})
    step(c,'multiemployer.classify',{'terms_and_relationships_current':True},
        {'accounting_route':'dc_information_fallback','disclosures_required':['IAS19.148'],'phase':'classified'},{})
    step(c,'multiemployer.recognize_deficit',{'contract_effective':True},
        {'recognized_deficit':'100','disclosures_required':['IAS19.148','IAS19.37'],'phase':'recognized'},
        {'pension_liability':'-100','expense':'100'})
    step(c,'multiemployer.accrue',{'full_year_elapsed':True},{'recognized_deficit':'110','remaining_years':1},
        {'pension_liability':'-10','finance_expense':'10'})
    step(c,'multiemployer.accrue',{'full_year_elapsed':True},{'recognized_deficit':'121','remaining_years':0},
        {'pension_liability':'-11','finance_expense':'11'})
    step(c,'multiemployer.pay',{'cash':'121'},{'recognized_deficit':'0','paid':'121','phase':'settled'},
        {'cash':'-121','pension_liability':'121'},{'operating':'-121'})

    variants=[('accepted',True,'accepted_filing',[('100','4/5'),('20','1/5')],'100','0','0','20'),
        ('most-likely',False,'most_likely',[('100','1/5'),('20','4/5')],'20','80','20','0'),
        ('expected-value',False,'expected_value',[('100','1/5'),('40','3/10'),('20','1/2')],'42','58','29/2','11/2')]
    for key,accepted,measure,distribution,deduction,base,current,dtl in variants:
        c=case('uncertain-tax-'+key,'uncertain_tax',{'treatment_id':'equipment-deduction','grouping_admitted':True,
            'full_information_examination':True,'rate_enacted':True,'predictive_choice_admitted':True,
            'asset_cost':'100','carrying':'80','revenue_before_deduction':'100','filing_deduction':'100','rate':'1/4',
            'current_assessed':'0','current_paid':'0','dtl':'0','outcomes':[{'deduction':d,'probability':p} for d,p in distribution],
            'tax_base':None,'selected_deduction':None,'measure':'not_measured','phase':'opening'},
            {'cash':'500','ppe':'80','capital':'-500','product_revenue':'-100','expense':'20'},tax='computed_origin_only')
        step(c,'uncertaintax.measure',{'acceptance_probable':accepted,'measure':measure},
            {'tax_base':base,'selected_deduction':deduction,'measure':measure,'current_assessed':current,'dtl':dtl,'phase':'measured'},
            {'current_tax_payable':'-'+current,'dtl':'-'+dtl,'tax_expense':'20'})
        if key=='expected-value':
            step(c,'uncertaintax.resolve',{'deduction':'40','new_evidence_admitted':True,'no_intervening_changes':True},
                {'tax_base':'60','selected_deduction':'40','measure':'resolved','current_assessed':'15','dtl':'5','phase':'resolved'},
                {'current_tax_payable':'-1/2','dtl':'1/2'})
            step(c,'uncertaintax.pay',{'cash':'15','classification':'operating','activity_identification_admitted':True},{'current_paid':'15','phase':'paid'},
                {'current_tax_payable':'15','cash':'-15'},{'operating':'-15'})

    c=case('acquisition-tax-origin','acquisition_tax',{'acquisition_id':'full-acquisition','consideration':'150','fair_value':'150',
        'tax_base':'100','rate':'1/4','recognized_asset':'0','dtl':'0','goodwill':'0','rate_enacted':True,
        'full_acquisition':True,'no_acquired_cash':True,'scope_admitted':True,'phase':'opening'},
        {'cash':'200','capital':'-200'},tax='computed_origin_only')
    c['book_id']='Consolidated'
    step(c,'acquisitiontax.recognize',{'acquisition_date_measurements_current':True},
        {'recognized_asset':'150','dtl':'25/2','goodwill':'25/2','phase':'acquired'},
        {'cash':'-150','ppe':'150','dtl':'-25/2','goodwill':'25/2'},{'investing':'-150'})

    variants=[('exception','taxable',True,True,False,True,'0','0'),
        ('liability','taxable',False,True,False,True,'12','0'),
        ('expected-distribution','taxable',True,False,True,True,'12','0'),
        ('deductible-viable','deductible',True,False,True,True,'0','12'),
        ('deductible-no-reversal','deductible',True,True,False,True,'0','0'),
        ('deductible-no-profit','deductible',True,False,True,False,'0','0')]
    for key,kind,control,no_reverse,reverse,profit,dtl,dta in variants:
        c=case('investment-tax-'+key,'investment_tax',{'investment_id':'outside-basis-slice','difference_kind':kind,
            'difference':'60','rate':'1/5','dtl':'0','dta':'0','rate_enacted':True,'reversal_control':control,
            'foreseeable_reversal_probable':reverse,'foreseeable_nonreversal_probable':no_reverse,
            'taxable_profit_available':profit,'recovery_manner_admitted':True,'assessed':False},
            {'cash':'100','capital':'-100'},tax='computed_origin_only')
        j={} if dtl==dta=='0' else {'dtl':'-'+dtl,'dta':dta,'tax_expense':'12' if dtl=='12' else '-12'}
        step(c,'investmenttax.assess',{'findings_current':True},{'dtl':dtl,'dta':dta,'assessed':True},j)

    state={'asset_id':'revalued-tax-asset','carrying':'140','tax_base':'100','rate':'1/4','dtl':'10','dta':'0',
        'gross_surplus':'40','prior_profit_loss':'0','no_impairment_carrying':'140','tax_profit_to_date':'0','tax_oci_to_date':'0',
        'rate_enacted':True,'recovery_probable':True}
    balances={'cash':'100','ppe':'140','dtl':'-10','capital':'-200','oci_revaluation':'-30'}
    c=case('tax-origin-reversal','tax_revaluation',deepcopy(state),deepcopy(balances),tax='computed_origin_only')
    step(c,'taxorigin.impair',{'recoverable':'90','no_time_or_base_change':True},
        {'carrying':'90','dtl':'0','dta':'5/2','gross_surplus':'0','prior_profit_loss':'10','tax_profit_to_date':'-5/2','tax_oci_to_date':'-10'},
        {'ppe':'-50','expense':'10','oci_revaluation':'30','dtl':'10','dta':'5/2','tax_expense':'-5/2'})
    step(c,'taxorigin.reverse',{'recoverable':'130','no_time_or_base_change':True,'changed_estimates_admitted':True},
        {'carrying':'130','dtl':'15/2','dta':'0','gross_surplus':'30','prior_profit_loss':'0','tax_profit_to_date':'0','tax_oci_to_date':'-5/2'},
        {'ppe':'40','income':'-10','oci_revaluation':'-45/2','dtl':'-15/2','dta':'-5/2','tax_expense':'5/2'})
    c=case('tax-origin-rate','tax_revaluation',deepcopy(state),deepcopy(balances),tax='computed_origin_only')
    step(c,'taxorigin.rate',{'new_rate':'3/10','new_rate_enacted':True,'recovery_manner_unchanged':True},
        {'rate':'3/10','dtl':'12','tax_oci_to_date':'2'},{'dtl':'-2','oci_revaluation':'2'})

    state={'jurisdiction_id':'SyntheticJurisdiction','legislation_enacted':True,'legislation_effective':True,'scope_admitted':True,
        'current_assessed':'0','paid':'0','hypothetical_temporary_difference':'40','dtl':'0','dta':'0',
        'exception_applied':False,'exception_disclosed':False,'current_separately_disclosed':False,
        'exposure_known':None,'exposure_lower':None,'exposure_upper':None,'unavailable_explanation':None,
        'assessment_progress':None,'phase':'opening'}
    c=case('pillar-current','pillar_two',deepcopy(state),{'cash':'100','capital':'-100'},tax='computed_origin_only')
    c['calendar_dates']=True
    step(c,'pillar.recognize',{'current_tax':'7','current_amount_admitted':True},
        {'current_assessed':'7','exception_applied':True,'exception_disclosed':True,'current_separately_disclosed':True,'phase':'recognized'},
        {'pillar_tax_payable':'-7','pillar_tax_expense':'7'})
    step(c,'pillar.pay',{'cash':'7','classification':'operating','activity_identification_admitted':True},
        {'paid':'7','phase':'paid'},{'pillar_tax_payable':'7','cash':'-7'},{'operating':'-7'})
    for s in c['steps']:s['event_date']='2024-12-31'
    state['legislation_effective']=False
    c=case('pillar-exposure-unknown','pillar_two',deepcopy(state),{'cash':'100','capital':'-100'},tax='computed_origin_only')
    c['calendar_dates']=True
    explanation='Illustrative premise: covered-tax inputs are not yet available.'
    progress='Illustrative premise: jurisdiction mapping is complete; covered-tax reconciliation is pending.'
    step(c,'pillar.exposure',{'known_or_estimable':False,'lower':None,'upper':None,
        'unavailable_explanation':explanation,'assessment_progress':progress},
        {'exception_applied':True,'exception_disclosed':True,'exposure_known':False,'unavailable_explanation':explanation,
         'assessment_progress':progress,'phase':'exposure_disclosed'}, {})
    c['steps'][0]['event_date']='2024-12-31'
