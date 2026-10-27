"""Closed GroupComponents/1 documentary types, separate from GroupForeignOperation/1."""
from copy import deepcopy
from pathlib import Path
import json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
PREFIX='accdsl.group-components.'
OPS=('group.component.commit@1','group.component.report@1')
METHODS=('reciprocal.join@1','inventory.eliminate@1','inventory.release@1',
 'inflation.restate@1','inflation.opening_tax@1','goodwill.impair@1',
 'corporate_asset.impair@1','acquisition.tax@1','investment.taxable@1',
 'investment.deductible@1','exchangeability.assess@1','exchangeability.transition@1')
ACCOUNTS=('cash','inventory','debt','capital','goodwill','identifiable_assets',
 'investment','receivable','payable','revenue','cogs','retained','dtl','dta')
JOURNAL_ACCOUNTS=ACCOUNTS+('subsidiary_capital','monetary_loss','write_down',
 'opening_retained','impairment_expense','tax_expense','net_assets','accumulated_translation')+tuple('asset_'+str(i) for i in range(1,6))
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
YES=enum('yes','no','unknown')
def ref(k=None):return obj(dict(kind=const(k) if k else ID,schema=const(sid(k)) if k else ID,digest=DIGEST))
def remap(v):
 if isinstance(v,str):return v.replace('accdsl.group.',PREFIX).replace('accdsl.operation.request.v1',sid('OperationRequest'))
 if isinstance(v,dict):return {k:remap(x) for k,x in v.items()}
 if isinstance(v,list):return [remap(x) for x in v]
 return v
def schemas():
 base=json.loads((ROOT/'data/accounting-master/finite-method-decisions-20261015/group/record-schemas.json').read_text())['$defs']
 s={k:remap(deepcopy(base[k])) for k in ('SchemaLock','OperationSignature','Environment','Decoder','Submission','OperationResult','TransportObservation')}
 s['Profile']=obj(dict(profile_id=const('GroupComponents/1'),schema_lock_ref=ref('SchemaLock'),operations=arr(enum(*OPS),2),execution_mode=const('specification_example'),scope=const('finite_group_component_histories_not_combined_statements')))
 s['Context']=obj(dict(group_id=ID,perimeter_id=ID,branch_id=ID,functional_currency=const('LC'),presentation_currency=const('USD'),unit=const('illustrative_million'),authority=const('historical_EU_scenario_not_actual_admission')))
 s['Evidence']=obj(dict(evidence_id=ID,available_at=STAMP,ingested_at=STAMP,measurement_asof=DATE,content_blob=BLOB,provenance=const('synthetic_supplied')))
 s['View']=obj(dict(evidence_refs=arr(ref('Evidence'),1),decision_at=STAMP,system_asof=STAMP,mode=const('historical_information'),revision=INT,supersedes_ref=maybe(ref('View'))))
 s['SourceSupport']=obj(dict(source_key=ID,raw_blob=BLOB,text_blob=BLOB,method_blobs=arr(BLOB,1),anchors=arr(TXT,1),scope=const('retained_historical_not_current_law')))
 s['RulePackage']=obj(dict(source_refs=arr(ref('SourceSupport'),2),method_ids=arr(enum(*METHODS),12),law_mode=const('historical_scenario_frozen_not_actual_applicability')))
 s['LegalBook']=obj(dict(entity_id=ID,owner_key=ID,book_id=ID,revision=INT,as_of_date=DATE,currency=const('LC'),branch_id=ID,context_ref=ref('Context'),evidence_ref=ref('Evidence'),balances=obj({k:Q for k in ACCOUNTS}),frozen_head_id=ID))
 s['ReciprocalSide']=obj(dict(context_ref=ref('Context'),book_ref=ref('LegalBook'),counterparty_ref=ref('LegalBook'),economic_event_id=ID,invoice_id=ID,lot_id=ID,currency=const('LC'),cutoff=DATE,transaction_date=DATE,branch_id=ID,role=enum('receivable','payable'),amount=Q))
 s['ControlAssessment']=obj(dict(context_ref=ref('Context'),entity_refs=arr(ref('LegalBook'),1),control_start=DATE,control_end_exclusive=DATE,reporting_date=DATE,assessment=const('supplied_control'),reporting_alignment=const('same_reporting_date_and_policies_supplied')))
 s['MethodInput']={'oneOf':[obj(dict(method_id=const(m),**p)) for m,p in input_variants().items()]}
 s['MethodDefinition']=obj(dict(method_id=enum(*METHODS),source_refs=arr(ref('SourceSupport'),1),contract_blob=BLOB,scope=const('conditional_finite_supplied_facts'),legal_book_effect=const('none')))
 s['MethodBasis']=obj(dict(context_ref=ref('Context'),view_ref=ref('View'),rule_ref=ref('RulePackage'),method_ref=ref('MethodDefinition'),input_ref=ref('MethodInput'),facts_evidence_ref=ref('Evidence'),legal_book_refs=arr(ref('LegalBook'),1),control_ref=ref('ControlAssessment'),reciprocal_refs=arr(ref('ReciprocalSide')),prior_result_ref=maybe(ref('ComponentResult')),measurement_date=DATE,result_currency=enum('LC','USD'),source_status=const('synthetic_facts_historical_rules')))
 j=dict(type='object',properties={k:Q for k in JOURNAL_ACCOUNTS},additionalProperties=False)
 s['ComponentResult']={'oneOf':[obj(dict(basis_ref=ref('MethodBasis'),method_id=const(m),status=enum('resolved','unresolved'),diagnostics=arr(ID),values=obj(p),adjustment_journal=j,posting_effect=enum('none','group_only'))) for m,p in value_variants().items()]}
 s['GroupState']=obj(dict(context_ref=ref('Context'),owner_key=ID,branch_id=ID,sequence=INT,last_result_ref=maybe(ref('ComponentResult')),legal_book_refs=arr(ref('LegalBook'),1),component_scope=const('isolated_method_history')))
 s['PostingAuthorization']=obj(dict(basis_ref=ref('MethodBasis'),from_state_ref=ref('GroupState'),owner_key=ID,legal_book_effect=const('none'),authority=const('authored_documentary_admission_not_professional_review')))
 s['ComponentProposal']=obj(dict(basis_ref=ref('MethodBasis'),result_ref=ref('ComponentResult'),from_state_ref=ref('GroupState'),to_state_ref=ref('GroupState'),authorization_ref=ref('PostingAuthorization')))
 s['PublicationReceipt']=obj(dict(request_ref=ref('OperationRequest'),result_ref=ref('ComponentResult'),from_state_ref=ref('GroupState'),to_state_ref=ref('GroupState'),proposal_ref=ref('ComponentProposal'),status=enum('component_committed','unresolved_result_published'),legal_effect=const('none')))
 s['ReportReceipt']=obj(dict(request_ref=ref('OperationRequest'),report_ref=ref('ComponentReport'),state_ref=ref('GroupState'),status=const('component_report_published'),legal_effect=const('none')))
 s['ComponentReport']=obj(dict(state_ref=ref('GroupState'),result_ref=ref('ComponentResult'),basis_ref=ref('MethodBasis'),scope=const('component_only_no_combined_company_claim'),values= {'oneOf':[obj(dict(method_id=const(m),**p)) for m,p in value_variants().items()]},tax_status=enum('uncomputed_separate_obligation','supplied_conditional_tax_method')))
 s['Domain']=obj(dict(request_ref=ref('OperationRequest'),meaning=const('singleton_request_decision')))
 s['Region']=obj(dict(domain_ref=ref('Domain'),predicate=const('this_request')))
 s['Obligation']=obj(dict(code=ID,required_input=ID,basis_ref=ref('MethodBasis')))
 for op,k in zip(OPS,('proposal_ref','state_ref')):
  s['Arguments.'+op]=obj({k:ref('ComponentProposal' if k=='proposal_ref' else 'GroupState'),'require_current':BOOL})
 common=deepcopy(base['OperationRequest']);common=remap(common)
 common['properties']['operation']=enum(*OPS)
 common['properties']['arguments']={'oneOf':[obj(dict(tag=const(op),value=s['Arguments.'+op])) for op in OPS]}
 s['OperationRequest']=common
 return dict(schema_version='GroupComponents/1',schema_ids={k:sid(k) for k in s},**{'$schema':'https://json-schema.org/draft/2020-12/schema','$defs':s})
def input_variants():
 v={}
 v[METHODS[0]]=dict(left_amount=Q,right_amount=Q,allocations=arr(obj(dict(allocation_id=ID,invoice_id=ID,amount=Q))),transaction_date=DATE,cutoff=DATE,control_start=DATE,control_end_exclusive=DATE,monetary_fx_difference=Q)
 v[METHODS[1]]=dict(original_cost=Q,internal_price=Q,sold_fraction=Q,external_proceeds=Q,parent_cash=Q,subsidiary_opening_cash=Q,parent_opening_equity=Q,investment=Q,lot_id=ID,internal_event_id=ID,external_sale_id=ID)
 v[METHODS[2]]=dict(external_proceeds=Q,lot_id=ID,external_sale_id=ID,prior_external_sale_id=ID)
 v[METHODS[3]]=dict(cash=Q,inventory=Q,debt=Q,capital=Q,indices=arr(obj(dict(date=DATE,index=Q)),2),cash_income=arr(obj(dict(date=DATE,amount=Q,event_id=ID))),nrv=maybe(Q),closing_rate=Q,prior_rate=Q,prior_presentation_date=DATE,rate_date=DATE,rate_from=const('LC'),rate_to=const('USD'),rate_purpose=const('foreign_operation_presentation'),hyperinflation_finding=const('supplied_admitted'),index_basis=const('general_price_index_supplied'),comparative_policy=const('prior_nonhyperinflationary_presentation_retained'))
 v[METHODS[4]]=dict(cost=Q,tax_base=Q,tax_rate=Q,acquisition_index=Q,opening_index=Q,closing_index=Q,acquisition_date=DATE,opening_date=DATE,closing_date=DATE,tax_origin=const('profit_no_exception_supplied'),tax_base_policy=const('fixed_supplied'))
 v[METHODS[5]]=dict(identifiable_assets=Q,recognized_goodwill=Q,notional_goodwill=Q,recoverable=Q,parent_fraction=Q,notional_support=enum('admitted','unknown'),nci_measurement=const('proportionate_share'),profit_allocation=const('same_as_parent_fraction'),unit_scope=const('subsidiary_is_unit'))
 v[METHODS[6]]=dict(assets=dict(type='array',items=Q,minItems=5,maxItems=5),floors=dict(type='array',items=Q,minItems=5,maxItems=5),unit_a_recoverable=Q,unit_b_recoverable=Q,group_recoverable=Q,asset_order=const(['A1','A2','B1','B2','HQ']),hq_allocation=const('smallest_combined_group_only'),unit_goodwill=const('none'),recoverables=const('supplied_not_valued'))
 v[METHODS[7]]=dict(fair_value_assets=Q,tax_base=Q,tax_rate=Q,consideration=Q,business_finding=const('supplied_business'),control_finding=const('supplied_control'),tax_origin=const('acquisition'),goodwill_dtl_exception=const('applies_to_initial_goodwill_only'))
 for m in METHODS[8:10]:v[m]=dict(difference=Q,carrying=Q,tax_base=Q,tax_rate=Q,controls_reversal=YES,no_foreseeable_reversal=YES,probable_reversal=YES,probable_taxable_profit=YES,tax_origin=const('profit'),tax_law=const('supplied_synthetic'))
 v[METHODS[10]]=dict(amount_needed=Q,amount_obtainable=Q,enforceable=YES,normal_delay=YES,permitted=YES,significance=enum('insignificant','significant','unknown'),admitted_rate=maybe(Q),rate_objective=enum('met','not_met','unknown'),foreign_amount=Q,measurement_date=DATE,rate_date=DATE,rate_from=ID,rate_to=ID,rate_purpose=enum('dividends','imports','foreign_operation_presentation','liability_settlement'),admission_purpose=ID,other_purpose_rate=Q,subsequent_rate=Q,subsequent_date=DATE,management_intent=enum('exchange','hold'),ability_basis=const('supplied_findings_not_intent'))
 v[METHODS[11]]=dict(foreign_amount=Q,old_rate=Q,new_rate=Q,transition_kind=enum('monetary_payable','foreign_operation'),initial_date=DATE,annual_period_start=DATE,rate_date=DATE,rate_from=ID,rate_to=ID,rate_purpose=enum('foreign_operation_presentation','liability_settlement'),rate_admission=const('orderly_measurement_date_rate_supplied'),comparative_restatement=const(False),transition_destination=enum('opening_retained','accumulated_translation'))
 v[METHODS[0]].update(economic_event_id=ID,invoice_id=ID,lot_id=ID)
 v[METHODS[1]].update(internal_date=DATE,external_date=DATE)
 v[METHODS[2]].update(external_date=DATE)
 return v
def value_variants():
 qnames=lambda names:{k:Q for k in names.split()}
 v={METHODS[0]:dict(**qnames('matched unmatched balance_elimination fx_difference_retained'),performance_eligible=BOOL)}
 for m in METHODS[1:3]:v[m]=qnames('cash inventory unrealized_profit group_cogs period_profit cumulative_profit equity')
 local=qnames('cash inventory debt capital monetary_loss real_income write_down equity')
 v[METHODS[3]]=dict(**local,**qnames('cash_purchasing_power_loss restated_opening_cash restated_cash_flow nominal_cash_flow prior_presentation_cash'),translated=obj(local))
 v[METHODS[4]]=qnames('opening_asset opening_dtl restated_opening_dtl closing_asset closing_dtl period_tax_expense closing_equity')
 v[METHODS[5]]={k:maybe(Q) for k in 'test_carrying test_loss recognized_loss unrecognized_nci_loss parent_loss nci_loss closing_goodwill closing_assets reported_assets remaining_notional'.split()}
 v[METHODS[6]]=dict(unit_stage=arr(Q,5),**qnames('unit_loss group_test_carrying additional_loss total_loss closing_total'),closing_assets=arr(Q,5))
 v[METHODS[7]]=qnames('identifiable_assets dtl net_identifiable_assets goodwill group_equity legal_cash_posting')
 for m in METHODS[8:10]:v[m]=dict(deferred_tax=maybe(Q),recognition=enum('recognized','not_recognized','unresolved'),tax_origin=const('profit'))
 v[METHODS[10]]=dict(exchangeability=enum('exchangeable','not_exchangeable','unresolved'),availability_ratio=Q,admitted_rate=maybe(Q),translated_amount=maybe(Q),estimator=const('supplied_not_estimated'))
 v[METHODS[11]]=dict(**qnames('old_carrying new_carrying equity_change period_profit period_oci'),destination=enum('opening_retained','accumulated_translation'),comparative_restatement=const(False))
 return v
