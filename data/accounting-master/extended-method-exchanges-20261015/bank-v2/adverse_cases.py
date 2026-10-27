"""Independently authored refusal expectations, not imported by the verifier."""
from fractions import Fraction as F

# method -> (changed parameters, exact diagnostic, disposition)
METHOD_REFUSALS={
 'transfer.partial':({'finding_supported':None},'transfer_finding_required','partial'),
 'transfer.retain_risks':({'fees':1},'unsupported_transfer_extras','unsupported'),
 'transfer.asset_income':({'original_eir_supported':False},'asset_eir_not_supported','rejected'),
 'transfer.liability_expense':({'separate_eir_supported':False},'liability_eir_not_supported','rejected'),
 'transfer.repay':({'interest_component':None},'cash_interest_allocation_required','partial'),
 'guarantee.start':({'measurement_available':False},'measurement_required','partial'),
 'guarantee.service':({'service_evidence':None},'service_evidence_required','partial'),
 'guarantee.measure_loss':({'expected_loss':None},'expected_loss_required','partial'),
 'guarantee.expire':({'no_claim_supported':False},'no_claim_expiry_not_supported','rejected'),
 'option.start':({'continuing_involvement_supported':False},'continuing_involvement_not_supported','rejected'),
 'option.remeasure':({'measurement_available':False},'measurement_required','partial'),
 'option.expire':({'rights_expired':False},'option_expiry_not_supported','rejected'),
 'option.exercise':({'physical_settlement_supported':False},'cash_settlement_not_in_scope','unsupported'),
 'ac_option.start':({'zero_allowance_isolation_supported':False},'zero_allowance_isolation_required','partial'),
 'ac_option.accrue_asset':({'original_eir_supported':False},'asset_eir_not_supported','rejected'),
 'ac_option.accrue_liability':({'separate_eir_supported':False},'liability_eir_not_supported','rejected'),
 'ac_option.exercise':({'amount':101},'exercise_amount_mismatch','rejected'),
 'asset.classify':({'assessment_evidence':None},'classification_finding_required','partial'),
 'asset.acquire':({'nontrading_investment':False},'cash_classification_finding_required','partial'),
 'asset.remeasure':({'measurement_available':False},'measurement_required','partial'),
 'asset.impair':({'expected_loss':None},'expected_loss_required','partial'),
 'asset.dispose':({'rights_transferred':False},'asset_disposal_not_supported','rejected'),
 'asset.transfer_reserve':({'within_equity_elected':False},'within_equity_transfer_not_elected','rejected'),
 'asset.time_value_probe':({'matched_benchmark_supported':False},'benchmark_evidence_required','partial'),
}

# label, case, method, parameter patch, component patch, date, code, status
BOUNDARIES=[]
def boundary(label,case,method,parameters,code,status='rejected',component=None,date=None):
    BOUNDARIES.append((label,case,method,parameters,component,date,code,status))

boundary('ineligible-part','partial-relative-values','transfer.partial',{'eligible_part':False},'partial_derecognition_not_supported')
boundary('missing-transfer-finding','partial-relative-values','transfer.partial',{'finding_evidence':None},'transfer_finding_required','partial')
boundary('failed-transfer-finding','partial-relative-values','transfer.partial',{'finding_supported':False},'transfer_finding_failed')
boundary('partial-prior-OCI','partial-relative-values','transfer.partial',{'prior_oci':1},'unsupported_transfer_extras','unsupported')
boundary('partial-no-cash-evidence','partial-relative-values','transfer.partial',{'cash_evidence':None},'cash_evidence_required','partial')
boundary('zero-relative-value','partial-relative-values','transfer.partial',{'retained_fv':0},'invalid_relative_values')
boundary('no-funding','retained-risk-borrowing','transfer.retain_risks',{'proceeds':0},'invalid_funding_amount')
boundary('early-asset-accrual','retained-risk-borrowing','transfer.asset_income',{},'accrual_anniversary_mismatch',date='2024-12-31')
boundary('duplicate-asset-accrual','retained-risk-borrowing','transfer.asset_income',{},'asset_accrual_state',component={'asset_accrued':True})
boundary('undischarged-borrowing','retained-risk-borrowing','transfer.repay',{'discharge_supported':False},'discharge_not_supported')
boundary('wrong-repayment','retained-risk-borrowing','transfer.repay',{'amount':50},'repayment_amount_mismatch')
boundary('invented-cash-interest','retained-risk-borrowing','transfer.repay',{'interest_component':1},'cash_interest_allocation_mismatch')
boundary('unsupported-cash-interest','retained-risk-borrowing','transfer.repay',{'contractual_interest_allocation_supported':False},'cash_interest_allocation_required','partial')
boundary('guarantee-wrong-proceeds','guarantee-no-claim','guarantee.start',{'proceeds':100},'isolated_guarantee_proceeds_mismatch')
boundary('guarantee-zero-cap','guarantee-no-claim','guarantee.start',{'cap':0},'invalid_guarantee_values')
boundary('guarantee-admission','guarantee-no-claim','guarantee.start',{'continuing_involvement_supported':False},'continuing_involvement_not_supported')
boundary('unperformed-service','guarantee-no-claim','guarantee.service',{'equal_service_performed':False},'service_pattern_not_supported')
boundary('service-fraction-outside-unit','guarantee-no-claim','guarantee.service',{'cumulative_fraction':F(4,3)},'service_fraction_order')
boundary('guarantee-loss-exceeds-exposure','guarantee-no-claim','guarantee.measure_loss',{'expected_loss':21},'invalid_expected_loss')
boundary('guarantee-early-expiry','guarantee-no-claim','guarantee.expire',{},'guarantee_expiry_date',date='2024-12-30')
boundary('guarantee-unverified-expiry','guarantee-no-claim','guarantee.expire',{'expiry_evidence':None},'expiry_evidence_required','partial')
boundary('option-day-one-gain','fv-call','option.start',{'zero_day_one_gain_supported':False},'day_one_gain_not_in_scope','unsupported')
boundary('option-proceeds','fv-call','option.start',{'proceeds':76},'isolated_option_proceeds_mismatch')
boundary('call-unused-put','fv-call','option.remeasure',{'put_time':1},'unused_option_time_value')
boundary('put-unused-call','fv-put','option.remeasure',{'call_time':1},'unused_option_time_value')
boundary('negative-option-value','fv-call','option.remeasure',{'call_time':-1},'invalid_option_value')
boundary('collar-inverted-strikes','fv-collar-lower','option.remeasure',{},'invalid_option_strikes',component={'put_strike':130})
boundary('nonzero-expiry-time','fv-call','option.expire',{'call_time':1},'expiry_time_value_nonzero')
boundary('wrong-exercise-side','fv-call','option.exercise',{'side':'put'},'option_exercise_side')
boundary('wrong-physical-price','fv-call','option.exercise',{'amount':94},'exercise_amount_mismatch')
boundary('AC-shared-EIR','ac-option-separate-rates','ac_option.start',{},'liability_eir_terminal_mismatch',component={'liability_rate':F(1,49)})
boundary('AC-nonzero-allowance-scope','ac-option-separate-rates','ac_option.start',{},'zero_allowance_isolation_required','partial',component={'zero_allowance_isolation':False})
boundary('AC-separate-liability-rate','ac-option-separate-rates','ac_option.accrue_liability',{'separate_eir_supported':False},'liability_eir_not_supported')
boundary('AC-cash-settlement','ac-option-separate-rates','ac_option.exercise',{'physical_settlement_supported':False},'cash_settlement_not_in_scope','unsupported')
boundary('missing-business-model','investment-AC','asset.classify',{'business_model':'unknown'},'classification_finding_required','partial')
boundary('missing-SPPI','investment-AC','asset.classify',{'sppi':'unknown'},'classification_finding_required','partial')
boundary('debt-equity-election','investment-AC','asset.classify',{'equity_election':True},'debt_equity_election_invalid')
boundary('late-equity-election','investment-equity_FVOCI','asset.classify',{'initial_recognition':False},'initial_election_date_required')
boundary('trading-equity-election','investment-equity_FVOCI','asset.classify',{'held_for_trading':True},'trading_equity_election_invalid')
boundary('missing-mismatch-finding','investment-mismatch_FVTPL','asset.classify',{'mismatch_eligible':None},'mismatch_finding_required','partial')
boundary('ineligible-mismatch','investment-mismatch_FVTPL','asset.classify',{'mismatch_eligible':False},'mismatch_designation_not_eligible')
boundary('investment-fees','investment-AC','asset.acquire',{'fees':1},'investment_costs_not_in_scope','unsupported')
boundary('negative-FV','investment-debt_FVOCI','asset.remeasure',{'fair_value':-1},'invalid_fair_value')
boundary('FV-missing-measurement-evidence','investment-debt_FVOCI','asset.remeasure',{'measurement_evidence':None},'measurement_required','partial')
boundary('ECL-exceeds-asset','investment-AC','asset.impair',{'expected_loss':101},'invalid_expected_loss')
boundary('equity-separate-ECL','investment-debt_FVOCI','asset.impair',{},'separate_ECL_not_applicable',component={'classification':'equity_FVOCI','instrument':'equity'})
boundary('AC-fair-value-remeasurement','investment-debt_FVOCI','asset.remeasure',{},'AC_does_not_remeasure_to_FV',component={'classification':'AC'})
boundary('debt-FV-sale-not-current','investment-debt_FVOCI','asset.dispose',{'proceeds':99},'dispose_fv_current_required')
boundary('equity-FV-sale-not-current','investment-equity_FVOCI','asset.dispose',{'proceeds':99},'dispose_fv_current_required')
boundary('probe-no-scenario','modified-time-value-probe','asset.time_value_probe',{'scenario_evidence':None},'benchmark_evidence_required','partial')
boundary('probe-zero-principal','modified-time-value-probe','asset.time_value_probe',{'principal':0},'invalid_probe_inputs')
boundary('probe-period-too-long','modified-time-value-probe','asset.time_value_probe',{'months':13},'invalid_probe_inputs')
