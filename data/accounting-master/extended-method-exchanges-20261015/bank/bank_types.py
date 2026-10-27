"""Closed BankComponents/1 types; documentary finite examples only."""
def obj(fields): return {'type':'object','properties':fields,'required':list(fields),'additionalProperties':False}
def arr(item,n=0): return {'type':'array','items':item,'minItems':n}
def enum(*v): return {'enum':list(v)}
def maybe(v): return {'anyOf':[v,{'type':'null'}]}
ID={'type':'string','pattern':'^[A-Za-z0-9_.:@/-]+$'}
DATE={'type':'string','format':'date'}
BOOL={'type':'boolean'}
INT={'type':'integer','minimum':0}
Q=obj({'n':{'type':'string','pattern':'^(0|-?[1-9][0-9]*)$'},'d':{'type':'string','pattern':'^[1-9][0-9]*$'}})
def qs(*names): return {k:Q for k in names}
ASSETS=['cash','securities','gross_loan','allowance']
LIABILITIES=['deposits','funding','commitment_provision','fee_liability']
PROFIT=['interest_income','fee_income','recovery_income','other_gains','impairment_expense','modification_expense','deposit_interest_expense']
OCI=['fair_value_reserve']
EQUITY=['capital','retained']
ACCOUNTS=ASSETS+LIABILITIES+PROFIT+OCI+EQUITY
CASH=['operating','investing','financing','unclassified']
OCI_MOVEMENTS=['fair_value']
EQUITY_MOVEMENTS=['issue']
HISTORY={'original_risk_id':ID,'original_risk_date':DATE,'current_risk_id':ID,
         'information_id':ID,'law_id':ID,'measurement_vintage':ID}
FLOW=obj({'index':INT,'gross':Q,'cost':Q})
SCENARIO=obj({'scenario_id':ID,'weight':Q,'default_index':maybe(INT),'receipts':arr(FLOW,1)})
MEASUREMENT={**{k:ID for k in ['current_risk_id','information_id','law_id','measurement_vintage']},
             'measurement_available':BOOL,'horizon_supported':BOOL,'horizon_evidence':maybe(ID)}
COMPONENTS={
 'loan':obj({'contract_id':ID,'measurement_basis':{'const':'amortised_cost_non_POCI'},**HISTORY,
   **qs('principal','terminal','gross','allowance','legal_unpaid','written_off','recovered','deposits','pending_transfer','factor'),
   'grid':arr(DATE,2),'clock':INT,'due_index':INT,'originated':BOOL,'sicr':BOOL,'credit_impaired':BOOL,
   'net_from_index':INT,'modified':BOOL,'cure_evidence':maybe(ID),'last_cash_evidence':maybe(ID)}),
 'commitment':obj({'facility_id':ID,**HISTORY,'measurement_date':DATE,'maturity_date':DATE,**qs('limit','capacity','gross','allowance','provision','deposits',
   'pending_transfer','draw_probability','default_first','default_later','terminal','recovery','factor'),
   'horizon_kind':enum('contractual','behavioural_exception'),'horizon_evidence':maybe(ID),
   'lifetime':BOOL,'revolving':BOOL,'inseparable':BOOL,'lapsed':BOOL,'fully_drawn':BOOL}),
 'fee':obj({'arrangement_id':ID,'purpose':enum('probable_specific_loan','equal_stand_ready'),
   **qs('fee','liability','principal','terminal','gross','factor','interest_recognised'),
   'received':BOOL,'originated':BOOL,'expired':BOOL,'settled':BOOL,'zero_ecl_isolation_supported':BOOL,
   'service_elapsed':INT,'service_dates':arr(DATE),'origination_date':DATE,'maturity_date':DATE}),
 'liquidity':obj({'funding_id':ID,**qs('cash','securities','gross','allowance','deposits','funding',
   'limit','eligible_lot','haircut','capacity','requested','actual_received','unpaid_deposits'),
   'request_status':enum('none','pending','settled'),'receipt_status':enum('none','confirmed','partial','verified_zero'),
   'control_breach':BOOL,'receipt_evidence':maybe(ID),'settlement_ids':arr(ID),'withdrawal_ids':arr(ID)}),
}
EVENTS={
 'loan.originate':('loan',obj({'mode':enum('external','deposit_credit'),'amount':Q,'classification_admitted':BOOL,'cash_evidence':maybe(ID)})),
 'loan.external_transfer':('loan',obj({'amount':Q,'cash_evidence':maybe(ID)})),
 'loan.deposit':('loan',obj({'amount':Q,'cash_evidence':maybe(ID)})),
 'loan.deposit_interest':('loan',obj({'amount':Q,'contractual_accrual_supported':BOOL})),
 'loan.accrue':('loan',obj({'index':INT})),
 'loan.measure':('loan',obj({**MEASUREMENT,'sicr':BOOL,'credit_impaired':BOOL,'credit_finding_supported':BOOL,
   'mutually_exclusive_exhaustive':BOOL,'law_kind':enum('disjoint_scenarios','unweighted_set'),'scenarios':arr(SCENARIO,1)})),
 'loan.modify':('loan',obj({'new_terminal':Q,'new_due_index':INT,'non_derecognition_supported':BOOL,'fees':Q,'costs':Q})),
 'loan.cure':('loan',obj({'objective_improvement':BOOL,'subsequent_event':BOOL,'evidence':maybe(ID),'sicr_remains':BOOL})),
 'loan.collect':('loan',obj({'amount':Q,'interest_component':maybe(Q),'cash_evidence':maybe(ID),'full_contractual_settlement':BOOL})),
 'loan.writeoff':('loan',obj({'amount':Q,'no_reasonable_recovery':BOOL,'finding_evidence':maybe(ID),'legal_waiver':BOOL})),
 'loan.recovery':('loan',obj({'amount':Q,'cash_evidence':maybe(ID)})),
 'commitment.reserve_full':('commitment',obj({**MEASUREMENT,'draw_probability':Q,'default_first':Q,'default_later':Q,'lifetime':BOOL,'sicr_supported':BOOL})),
 'commitment.draw_full':('commitment',obj({'mode':enum('external','deposit_credit'),'amount':Q,'classification_admitted':BOOL,'cash_evidence':maybe(ID)})),
 'commitment.external_transfer':('commitment',obj({'amount':Q,'cash_evidence':maybe(ID)})),
 'commitment.lapse':('commitment',obj({'rights_expired':BOOL,'evidence':maybe(ID)})),
 'commitment.revolving_draw':('commitment',obj({**MEASUREMENT,'amount':Q,'funded_ecl':maybe(Q),'undrawn_ecl':maybe(Q),'cash_evidence':maybe(ID)})),
 'commitment.revolving_repay':('commitment',obj({**MEASUREMENT,'amount':Q,'funded_ecl':maybe(Q),'undrawn_ecl':maybe(Q),'replenishment_supported':BOOL,'cash_evidence':maybe(ID)})),
 'commitment.combined':('commitment',obj({**MEASUREMENT,'combined_ecl':maybe(Q),'cannot_separate_supported':BOOL})),
 'fee.receive':('fee',obj({'amount':Q,'purpose_supported':BOOL,'cash_evidence':maybe(ID)})),
 'fee.originate':('fee',obj({'amount':Q,'specific_loan_probable':BOOL,'classification_admitted':BOOL,'cash_evidence':maybe(ID)})),
 'fee.accrue':('fee',obj({'zero_ecl_isolation_supported':BOOL})),
 'fee.collect':('fee',obj({'amount':Q,'interest_component':maybe(Q),'cash_evidence':maybe(ID)})),
 'fee.expire':('fee',obj({'rights_expired':BOOL,'evidence':maybe(ID)})),
 'fee.service':('fee',obj({'elapsed':INT,'equal_service_performed':BOOL,'revenue_method_admitted':BOOL})),
 'liquidity.capacity':('liquidity',obj({'eligibility_supported':BOOL,'haircut_supported':BOOL})),
 'liquidity.request':('liquidity',obj({'amount':Q,'request_evidence':maybe(ID)})),
 'liquidity.settle':('liquidity',obj({'amount':maybe(Q),'evidence_kind':enum('confirmed_cash','verified_no_receipt','timeout'),'settlement_id':ID,'cash_evidence':maybe(ID)})),
 'liquidity.withdraw':('liquidity',obj({'requested':Q,'withdrawal_id':ID,'actual_payment_evidence':maybe(ID)})),
}
