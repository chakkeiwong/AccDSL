"""Closed documentary US assessment profile; no endpoint implementation."""
from copy import deepcopy
from pathlib import Path
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
PREFIX='accdsl.bank-assessment.'
OPS=('bank.regulatory.assess@1','bank.loss.query@1','bank.policy.describe@1')
ACCOUNTS=('cash','loans','goodwill','allowance','deposits','borrowing','stock',
          'retained','interest_income','deposit_expense','loss_expense')
AMOUNTS=('book_equity','gross_loans','allowance','goodwill','cap_base','cap',
         'admitted_allowance','excess_allowance','rwa','cet1','tier1','tier2',
         'total_capital','leverage_denominator')
RATIOS=('cet1_ratio','tier1_ratio','total_ratio','leverage_ratio')
EXCLUSIONS=('subsidiaries','advanced_approaches','category_iii','market_risk',
 'cblr','supervisory_adjustment','cecl_transition','aoci','own_capital',
 'financial_institution_capital','deferred_taxes','other_intangibles',
 'pension_asset','securitization','atrr','off_balance_credit')
ELIGIBILITY=tuple('condition_'+str(i) for i in range(1,14))
EVENTS=('loan.originate','loan.external','income.receive','deposits.interest',
        'allowance.measure','income.close','funding.draw','deposits.runoff')
def sid(k):return PREFIX+k.lower()+'.v1'
def obj(p):return dict(type='object',properties=p,required=list(p),additionalProperties=False)
def arr(s,n=0):return dict(type='array',items=s,minItems=n)
def enum(*v):return dict(enum=list(v))
def const(v):return dict(const=v)
def maybe(s):return dict(anyOf=[s,dict(type='null')])
ID=dict(type='string',pattern='^[A-Za-z0-9_.:@/-]+$')
TXT=dict(type='string',minLength=1)
DATE=dict(type='string',format='date')
STAMP=dict(type='string',format='date-time')
INT=dict(type='integer',minimum=0)
BOOL=dict(type='boolean')
DIGEST=dict(type='string',pattern='^[0-9a-f]{64}$')
Q=obj(dict(n=dict(type='string',pattern='^(0|-?[1-9][0-9]*)$'),d=dict(type='string',pattern='^[1-9][0-9]*$')))
BLOB=obj(dict(kind=const('blob'),algorithm=const('sha256'),digest=DIGEST,byte_length=INT))
def ref(k=None):return obj(dict(kind=const(k) if k else ID,schema=const(sid(k)) if k else ID,digest=DIGEST))
def refs(*names):return {k:ref(v) for k,v in names}
def remap(v):
 if isinstance(v,str):return v.replace('accdsl.corporate.',PREFIX).replace('accdsl.operation.request.v1',sid('OperationRequest')).replace('accdsl.operation.result.v1',sid('OperationResult'))
 if isinstance(v,dict):return {k:remap(x) for k,x in v.items()}
 if isinstance(v,list):return [remap(x) for x in v]
 return v
def schemas():
 base=json.loads((ROOT/'data/accounting-master/corporate-portable-20261015/record-schemas.json').read_text())['$defs']
 s={k:remap(deepcopy(base[k])) for k in ('SchemaLock','OperationSignature','Environment','Decoder','Submission','OperationResult','TransportObservation')}
 s['Profile']=obj(dict(profile_id=const('BankAssessment/1'),schema_lock_ref=ref('SchemaLock'),operations=arr(enum(*OPS),3),execution_mode=const('specification_example'),accounting_effect=const('none')))
 s['Context']=obj(dict(bank_id=ID,book_id=ID,perimeter_id=ID,currency=const('USD'),unit=const('million'),accounting_basis=const('US_GAAP_CECL_supplied'),jurisdiction=const('US_national_bank')))
 s['Evidence']=obj(dict(evidence_id=ID,available_at=STAMP,ingested_at=STAMP,measurement_asof=DATE,content_blob=BLOB,provenance=enum('synthetic_supplied','historical_source')))
 s['View']=obj(dict(evidence_refs=arr(ref('Evidence'),1),decision_at=STAMP,system_asof=STAMP,mode=const('historical_information'),revision=INT,supersedes_ref=maybe(ref('View'))))
 s['SourceSupport']=obj(dict(raw_blob=BLOB,text_blob=maybe(BLOB),method_blob=BLOB,anchors=arr(TXT,1),source_role=enum('historical_rule','older_ordering_crosscheck','method_semantics'),snapshot=maybe(DATE)))
 s['RulePackage']=obj(dict(source_refs=arr(ref('SourceSupport'),1),snapshot=const('2026-01-01'),law_mode=const('scenario_frozen_not_actual_applicability'),method_version=const('US_restricted_ordinary_bank_v1')))
 s['Applicability']=obj(dict(context_ref=ref('Context'),evidence_ref=ref('Evidence'),institution=const('ordinary_national_bank'),exclusions=obj({k:enum('absent','present','unknown') for k in EXCLUSIONS})))
 s['StockEligibility']=obj(dict(context_ref=ref('Context'),evidence_ref=ref('Evidence'),conditions=obj({k:enum('satisfied','failed','unknown') for k in ELIGIBILITY})))
 s['ExposureClassification']=obj(dict(context_ref=ref('Context'),evidence_ref=ref('Evidence'),reserve_venue=enum('federal_reserve','commercial_bank','unknown'),loan_class=enum('ordinary_performing_nonPCD_corporate','PCD','nonaccrual','unknown')))
 s['AllowanceAdmission']=obj(dict(context_ref=ref('Context'),evidence_ref=ref('Evidence'),all_eligible_aacl=enum('yes','no','unknown'),measurement=const('supplied_not_estimated')))
 s['DeductionAdmission']=obj(dict(context_ref=ref('Context'),evidence_ref=ref('Evidence'),goodwill_without_dtl=enum('yes','no','unknown')))
 s['AverageAssets']=obj(dict(context_ref=ref('Context'),evidence_ref=ref('Evidence'),period_start=DATE,period_end_exclusive=DATE,measure_kind=enum('regulatory_average_total_assets','period_end_total_assets'),amount=Q))
 s['FundingFacility']=obj(dict(context_ref=ref('Context'),evidence_ref=ref('Evidence'),limit=Q,availability=const('supplied_available_not_estimated')))
 s['AccountingEvent']={'oneOf':[obj(dict(method_id=const(k),amount=Q,event_date=DATE)) for k in EVENTS]}
 s['AccountingState']=obj(dict(context_ref=ref('Context'),evidence_ref=ref('Evidence'),facility_ref=ref('FundingFacility'),opening_asof_date=DATE,as_of_date=DATE,sequence=INT,opening_balances=obj({k:Q for k in ACCOUNTS}),event_refs=arr(ref('AccountingEvent')),posted_journals=arr(obj(dict(event_ref=ref('AccountingEvent'),lines=arr(obj(dict(account=enum(*ACCOUNTS),signed_amount=Q)))))),balances=obj({k:Q for k in ACCOUNTS}),unpaid_withdrawal=Q,frozen_head_id=ID))
 s['AssessmentBasis']=obj(dict(context_ref=ref('Context'),state_ref=ref('AccountingState'),view_ref=ref('View'),rule_ref=ref('RulePackage'),applicability_ref=ref('Applicability'),eligibility_ref=ref('StockEligibility'),exposure_ref=ref('ExposureClassification'),allowance_ref=ref('AllowanceAdmission'),deduction_ref=ref('DeductionAdmission'),average_ref=maybe(ref('AverageAssets')),assessment_date=DATE,period_start=DATE,period_end_exclusive=DATE))
 metric=obj(dict(status=enum('resolved','unresolved','undefined'),value=maybe(Q),diagnostics=arr(ID),dependency_refs=arr(ref(),1)))
 ratio=obj(dict(status=enum('resolved','unresolved','undefined'),numerator=maybe(Q),denominator=maybe(Q),value=maybe(Q),diagnostics=arr(ID),dependency_refs=arr(ref(),1)))
 s['RegulatoryAssessment']=obj(dict(basis_ref=ref('AssessmentBasis'),amounts=obj({k:metric for k in AMOUNTS}),ratios=obj({k:ratio for k in RATIOS}),distribution_permission=const('unresolved_not_assessed'),minimum_ratio_verdict=const('not_assessed'),accounting_effect=const('none')))
 s['Vintage']=obj(dict(evidence_ref=ref('Evidence'),vintage_id=ID,as_of_date=DATE,supersedes_ref=maybe(ref('Vintage'))))
 cell=obj(dict(cell_id=ID,default_date=maybe(DATE),ead=Q,lgd=Q,cash_shortfall=Q,discount_factor=Q))
 s['JointLaw']=obj(dict(context_ref=ref('Context'),evidence_ref=ref('Evidence'),vintage_ref=ref('Vintage'),origin_date=DATE,horizon_end_exclusive=DATE,cells=arr(cell,1),support_status=const('complete_finite_synthetic'),dependence=const('joint_cells_no_factorization'),target=const('economic_discounted_cash_shortfall_not_accounting_allowance')))
 candidate=obj(dict(law_id=ID,weights=arr(Q,1)))
 s['Measure']=obj(dict(law_ref=ref('JointLaw'),mode=enum('point_law','law_family','unweighted_histories'),candidates=arr(candidate),family_status=const('complete_declared_finite_family')))
 s['Condition']=obj(dict(kind=enum('all','survived_through'),survived_through=maybe(DATE),evidence_ref=maybe(ref('Evidence'))))
 s['LossQuery']=obj(dict(context_ref=ref('Context'),view_ref=ref('View'),measure_ref=ref('Measure'),condition_ref=ref('Condition'),origin_date=DATE,default_window_start=DATE,default_window_end_exclusive=DATE))
 law_value=obj(dict(law_id=ID,status=enum('resolved','unresolved'),conditioning_mass=Q,conditional_weights=arr(Q),expected_loss=maybe(Q),diagnostic=maybe(ID)))
 s['LossQueryResult']=obj(dict(query_ref=ref('LossQuery'),law_results=arr(law_value),possible_losses=arr(Q),expectation_status=enum('resolved','set_valued','unresolved'),expectation_values=arr(Q),lower=maybe(Q),upper=maybe(Q),bounds_target=enum('expectation_over_candidate_laws','possible_history_losses','undefined'),diagnostics=arr(ID),accounting_allowance_claim=const(False),dependency_refs=arr(ref(),1)))
 s['PolicySpecification']=obj(dict(context_ref=ref('Context'),view_ref=ref('View'),evidence_ref=ref('Evidence'),loss_result_ref=ref('LossQueryResult'),objective=const('maximize_cash_after_contractual_settlement'),actions=arr(obj(dict(action_id=ID,kind=enum('fixed_book','contractual_runoff','secured_draw'),limit=Q)),1),constraints=obj(dict(actual_settlements_only=const(True),no_fabricated_investor=const(True),respect_facility_limit=const(True),distribution_permission=enum('unknown','supplied_separately'))),tie_break=const('lexicographic_action_id'),failure_behavior=const('record_policy_failure_or_legal_default'),calibration_status=const('not_calibrated')))
 s['PolicyQueryResult']=obj(dict(policy_ref=ref('PolicySpecification'),objective=const('maximize_cash_after_contractual_settlement'),action_ids=arr(ID,1),tie_break=const('lexicographic_action_id'),selected_action=const(None),feasibility_status=const('not_evaluated'),distribution_permission=const('unresolved_not_assessed'),diagnostics=arr(ID,1),accounting_effect=const('none')))
 s['QueryPublicationReceipt']=obj(dict(request_ref=ref('OperationRequest'),output_ref=ref(),status=const('query_published'),accounting_effect=const('none')))
 s['Domain']=obj(dict(request_ref=ref('OperationRequest'),meaning=const('singleton_request_decision')))
 s['Region']=obj(dict(domain_ref=ref('Domain'),predicate=const('this_request')))
 s['Obligation']=obj(dict(code=ID,required_input=TXT,query_ref=ref()))
 args={OPS[0]:obj(dict(basis_ref=ref('AssessmentBasis'),require_current=BOOL)),OPS[1]:obj(dict(query_ref=ref('LossQuery'),require_current=BOOL)),OPS[2]:obj(dict(policy_ref=ref('PolicySpecification'),require_current=BOOL))}
 s['OperationRequest']=remap(deepcopy(base['OperationRequest']))
 s['OperationRequest']['properties']['operation']=enum(*OPS)
 s['OperationRequest']['properties']['expected_head']=maybe(obj(dict(owner_key=ID,state_ref=ref('AccountingState'),generation=INT)))
 s['OperationRequest']['properties']['arguments']={'oneOf':[obj(dict(tag=const(k),value=v)) for k,v in args.items()]}
 for k,v in args.items():s['Arguments.'+k]=v
 return dict(**{'$schema':'https://json-schema.org/draft/2020-12/schema','$defs':s},schema_ids={k:sid(k) for k in s})
