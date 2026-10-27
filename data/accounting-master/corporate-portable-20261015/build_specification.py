"""Author finite corporate records and expected exchanges; no product runtime."""
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import hashlib,json

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
REG,ALIASES,BLOBS,EXCHANGES={},{},{},[]
P='accdsl.corporate.'
def enc(x): return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def sid(k): return {'OperationRequest':'accdsl.operation.request.v1','OperationResult':'accdsl.operation.result.v1'}.get(k,P+k.lower()+'.v1')
def rat(v):
 q=Q(v);return {'n':str(q.numerator),'d':str(q.denominator)}
def affine(a,b=0):return {'constant':rat(a),'coefficient_x':rat(b)}
def obj(p):return {'type':'object','properties':p,'required':list(p),'additionalProperties':False}
def arr(x,n=0):return {'type':'array','items':x,'minItems':n}
def maybe(x):return {'anyOf':[x,{'type':'null'}]}
TEXT={'type':'string','minLength':1}
ID={'type':'string','pattern':'^[A-Za-z0-9_.:@/-]+$'}
INT={'type':'integer','minimum':0}
BOOL={'type':'boolean'}
DATE={'type':'string','format':'date'}
STAMP={'type':'string','format':'date-time'}
RAT=obj({'n':{'type':'string','pattern':'^(0|-?[1-9][0-9]*)$'},'d':{'type':'string','pattern':'^[1-9][0-9]*$'}})
AFF=obj({'constant':RAT,'coefficient_x':RAT})
BLOB=obj({'kind':{'const':'blob'},'algorithm':{'const':'sha256'},'digest':{'type':'string','pattern':'^[0-9a-f]{64}$'},'byte_length':INT})
def ref(k=None):return obj({'kind':{'const':k} if k else ID,'schema':{'const':sid(k)} if k else ID,'digest':{'type':'string','pattern':'^[0-9a-f]{64}$'}})
UNKNOWN=obj({'tag':{'const':'unknown'},'reason':TEXT,'obligation_refs':arr(ref('Obligation'),1)})
def uncertain(t):return {'oneOf':[t,UNKNOWN]}
def unknown(reason,obligations):return {'tag':'unknown','reason':reason,'obligation_refs':obligations}
def links(x):
 if isinstance(x,dict):
  if set(x)=={'kind','schema','digest'}:yield x
  else:
   for v in x.values():yield from links(v)
 elif isinstance(x,list):
  for v in x:yield from links(v)
def add(k,key,b):
 if k=='View':b={'conditional_refs':[],**b}
 if k=='Reading':b={'admission_ref':None,**b}
 deps={enc(r):r for r in links(b)}
 r={'kind':k,'schema':sid(k),'key':key,'revision':0,'body':b,'dependencies':[deps[x] for x in sorted(deps)]}
 d=hashlib.sha256(('accdsl.portable.v1/'+sid(k)).encode()+b'\0'+enc(r)).hexdigest()
 REG[d]=r;v={'kind':k,'schema':sid(k),'digest':d};ALIASES[key]=v;return v
def body(r):return REG[r['digest']]['body']
def blob(path):
 p=ROOT/path if isinstance(path,str) else path
 data=p.read_bytes();d=hashlib.sha256(data).hexdigest()
 BLOBS[d]={'path':str(p.relative_to(ROOT)),'byte_length':len(data)}
 return {'kind':'blob','algorithm':'sha256','digest':d,'byte_length':len(data)}
def bytes_blob(name,data):
 p=OUT/'bytes'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);return blob(p)

ACCOUNTS=['cash','receivables','inventory','plant_cost','accum_depreciation','tax_prepaid','payables','debt','capital','retained','revenue','cost_of_sales','payroll','depreciation','interest','tax']
BAL=obj({k:RAT for k in ACCOUNTS})
LINE=obj({'account':{'enum':ACCOUNTS},'signed_amount':RAT})
REPORT_KEYS=['cash','receivables','inventory','plant_net','tax_prepaid','assets','payables','debt','capital','retained','equity','revenue','cost_of_sales','payroll','depreciation','interest','profit_before_tax','tax','profit','oci','comprehensive_income','operating_cash','investing_cash','financing_cash','cash_change','opening_cash','opening_equity','dividends','plant_additions']
FACT_KEYS=['years','purchase_units','delivery_units','sales_consideration','collections','supplier_payment','payroll','capex','capex_life','interest_rate','tax_rate','tax_payment','dividend']
DRIVERS=['years','demand_units','price','target_inventory_units','collection_fraction','legacy_collections','supplier_payment','payroll','capex','capex_life','tax_rate','dividend','fixed_rate','floating_rate']
IDENTITY=obj({k:ID for k in ['entity_id','book_id','branch_key','business_event_id']})
HEAD=obj({'owner_key':ID,'state_ref':ref(),'generation':INT})
ISSUE=obj({'code':ID,'affected_fields':arr(ID,1),'support_refs':arr(ref()),'reason':TEXT})
STATUS=obj({'structural_validity':{'enum':['valid','invalid']},'mathematical_status':{'enum':['defined','unresolved','undefined','infeasible','not_applicable']},
 'computation_status':{'enum':['complete','partial','not_computed','cancelled']},
 'empirical_justification':{'const':'not_established'},'capability_status':{'const':'specified_only_no_runtime'},
 'accounting_validity':{'const':'not_assessed'},'forecast_validity':{'const':'not_assessed'},'product_readiness':{'const':'not_implemented'},'human_acceptance':{'const':'pending'}})
DIAG=obj({'code':ID,'stage':TEXT,'record_ref':maybe(ref()),'source_locator':maybe(TEXT),'field_path':TEXT,
 'affected_query_branch_ids':arr(ID),'dependency_path':arr(ref()),'observed':TEXT,'expected_rule':TEXT,
 'retry_advice':TEXT,'blocking_diagnostic_ids':arr(ID)})
S={}
S['SchemaLock']=obj({'schema_blob':BLOB,'semantic_contract_blob':BLOB,'format':{'const':'jsonschema2020-12'}})
S['Profile']=obj({'profile_id':{'const':'CorporateJointHistory/1'},'schema_lock_ref':ref('SchemaLock'),'operations':arr(ID,1),'book_mode':{'const':'synthetic'},'execution_mode':{'const':'specification_example'}})
S['OperationSignature']=obj({'operation':ID,'profile_ref':ref('Profile'),'arguments_definition':ID,'payload_kinds':arr(ID,1),'effects':{'enum':['read','candidate','review_transaction','accounting_transaction','migration_transaction','import_transaction','candidate_or_checkpoint_transaction','checkpoint_transaction']}})
S['Context']=obj({'entity':{'const':'Northstar'},'book':{'const':'DemoCorporate'},'perimeter':{'const':'single-entity'},'currency':{'const':'USD'},'unit':{'const':'one_currency_unit'},'basis':{'const':'DemoCorporate/1'},'calendar':{'const':'Gregorian'},'period_start':DATE,'period_end_exclusive':DATE,'dimensions':arr(obj({'axis':ID,'member':ID}))})
S['SourceUnit']=obj({'source_blob':BLOB,'unit_key':ID,'kind':{'enum':['statement','note','policy','cross_reference']},'public_date':maybe(DATE),'publication_timezone':{'const':'UTC'},'public_bytes_verified':BOOL,'ingested_at':maybe(STAMP),'ingestion_verified':BOOL,'reviewed_at':maybe(STAMP),'revision_group':ID,'supersedes_refs':arr(ref('SourceUnit')),'fact_status':{'const':'authored_synthetic'}})
S['Reading']=obj({'source_ref':ref('SourceUnit'),'context_ref':ref('Context'),'concept':ID,'value':maybe(RAT),'literal':TEXT,'target_layer':{'enum':['reported_assertion','authored_fact']},'status':{'enum':['candidate','accepted_literal']}})
S['Obligation']=obj({'code':ID,'source_ref':maybe(ref('SourceUnit')),'affected_targets':arr(ID,1),'reason':TEXT})
S['Package']=obj({'unit_refs':arr(ref('SourceUnit'),1),'reading_refs':arr(ref('Reading')),'obligation_refs':arr(ref('Obligation')),'coverage':arr(obj({'unit_key':ID,'disposition':{'enum':['structured','literal_only','unresolved','duplicate','cross_reference_resolved']},'target_ref':maybe(ref())}),1),'recursive_closure':BOOL})
S['ReviewProposal']=obj({'target_ref':ref(),'layer':{'enum':['extraction','interpretation','assumption']},'decision':{'enum':['accept','reject','retain_alternative','supersede']},'evidence_refs':arr(ref(),1),'actor':ID,'rationale':TEXT,'replacement_ref':maybe(ref())})
S['ReviewDecision']=obj({'proposal_ref':ref('ReviewProposal'),'prior_view_ref':ref('View'),'accepted':BOOL,'decided_at':STAMP,'scope':TEXT})
S['View']=obj({'view_id':ID,'parent_ref':maybe(ref('View')),'source_refs':arr(ref('SourceUnit')),'reading_refs':arr(ref('Reading')),'decision_refs':arr(ref('ReviewDecision')),'candidate_membership_revision':INT,'mode':{'enum':['archival_exploration','investor_information','system_as_of']}})
S['Assumptions']=obj({'source_blob':BLOB,'inventory_unit_cost':RAT,'tax_rule':{'const':'positive_profit_times_rate_no_deferred_tax'},'capex_service':{'const':'next_period'},'oci':{'const':'zero'},'intraperiod':{'const':'aggregate_feasible_order_not_recovered_invoices'},'scope_exclusions':arr(TEXT,1)})
S['Facts']=obj({'source_blob':BLOB,'opening':BAL,'periods':arr(obj({'id':ID,'start':DATE,'end_exclusive':DATE,**{k:RAT for k in FACT_KEYS}}),2),
 'assets':arr(obj({'id':ID,'cost':RAT,'life_years':RAT,'in_service':DATE,'accumulated':RAT}),1),
 'contract':obj({'principal':RAT,'fixed_rate':RAT,'historical_floating_rate':RAT,'maturity':DATE}),
 'forecast':obj({'start':DATE,'end_exclusive':DATE,**{k:RAT for k in DRIVERS}})})
S['Symbol']=obj({'name':{'const':'x'},'type':{'const':'dimensionless_floating_fraction'},'lower':RAT,'upper':RAT,'lower_included':BOOL,'upper_included':BOOL,'uncertainty_category':{'const':'historical_fact_unknown'},'support_refs':arr(ref(),1)})
S['Constraint']=obj({'name':ID,'relation':{'enum':['eq','ge','le']},'expression':AFF,'rhs':RAT,'support_refs':arr(ref(),1)})
S['Template']=obj({'event_kind':ID,'parameter_names':arr(ID),'preconditions':arr(ID),'method_contract':BLOB,'cash_class':maybe({'enum':['operating','investing','financing']}),'source_refs':arr(ref(),1)})
S['DebtFormula']=obj({'principal':RAT,'fixed_rate':RAT,'floating_rate':RAT,'year_fraction':RAT,'fraction_symbol_ref':ref('Symbol'),'formula':{'const':'principal*((1-x)*fixed_rate+x*floating_rate)*year_fraction'},'result':AFF,'context_ref':ref('Context')})
S['Module']=obj({'context_refs':arr(ref('Context'),1),'source_refs':arr(ref('SourceUnit')),'reading_refs':arr(ref('Reading')),'assumption_refs':arr(ref('Assumptions'),1),'symbol_refs':arr(ref('Symbol'),1),'constraint_refs':arr(ref('Constraint'),1),'derived_expression_refs':arr(ref('DebtFormula'),1),'template_refs':arr(ref('Template')),'facts_ref':ref('Facts'),'profile_ref':ref('Profile'),'view_ref':ref('View'),'scope':{'enum':['debt_fragment','corporate_full']},'source_kind':{'enum':['matched_semantics','typed_full']}})
S['HistoryFamily']=obj({'module_ref':ref('Module'),'view_ref':ref('View'),'symbol_ref':ref('Symbol'),'constraint_refs':arr(ref('Constraint'),1),'opening_ref':ref('CompanyState'),'reconstruction_ref':ref('HistoricalReconstruction'),'target_layer':{'const':'conditional_accounting_history'},'scope':{'const':'Northstar_declared_aggregate_model'},'formulation_complete':BOOL,'obligation_refs':arr(ref('Obligation')),'measure_ref':{'type':'null'}})
S['Scenario']=obj({'context_ref':ref('Context'),'family_ref':ref('HistoryFamily'),'mode':{'const':'exogenous_stress'},'information_mode':{'enum':['archival_exploration','investor_information']},'decision_at':STAMP,'information_cutoff':maybe(STAMP),'driver_values':obj({k:uncertain(RAT) for k in DRIVERS}),'driver_origin':{'enum':['imposed_assumption','future_realization']},'realized_at':maybe(STAMP),'future_realizations_permitted':{'const':False},'tax_method_supported':BOOL})
S['EconomicEvent']=obj({'business_event_id':ID,'context_ref':ref('Context'),'period':ID,'date':DATE,'sequence':INT,'event_kind':ID,'parameters':obj({'amount':maybe(RAT),'units':maybe(RAT),'consideration':maybe(RAT)}),'source_ref':ref('Facts')})
S['JournalProposal']=obj({'basis_ref':ref('AccountingEventBasis'),'authorization_ref':ref('PostingAuthorization'),'lines':arr(LINE,1),'cash_class':maybe({'enum':['operating','investing','financing']})})
S['CompanyState']=obj({'context_ref':ref('Context'),'view_ref':ref('View'),'sequence':INT,'balances':BAL,'inventory_units':RAT,'source_ref':ref('Facts')})
S['AccountingEventBasis']=obj({'identity':IDENTITY,'event_ref':ref('EconomicEvent'),'opening_ref':ref('CompanyState'),'context_ref':ref('Context'),'branch_ref':ref('Branch'),'time_ref':ref('Time'),'chart_ref':ref('Chart'),'authority_refs':arr(ref('SyntheticAuthority'),1),'method_ref':ref('MethodDefinition'),'evidence_refs':arr(ref('Facts'),1),'admission_refs':arr(ref('Admission'),1),'assumptions_ref':ref('Assumptions'),'view_ref':ref('View')})
S['Branch']=obj({'branch_key':ID,'book_mode':{'const':'synthetic'},'context_ref':ref('Context'),'view_ref':ref('View')})
S['Time']=obj({'economic_date':DATE,'reporting_start':DATE,'reporting_end_exclusive':DATE,'view_ref':ref('View')})
S['Chart']=obj({'context_ref':ref('Context'),'account_ids':arr({'enum':ACCOUNTS},len(ACCOUNTS)),'sign_convention':{'const':'debit_positive'}})
S['SyntheticAuthority']=obj({'assumptions_ref':ref('Assumptions'),'scope':{'const':'Northstar_authored_teaching_only'}})
S['MethodDefinition']=obj({'method_id':{'const':'northstar.purchase@1'},'semantic_contract_blob':BLOB,'parameter_units':obj({'amount':{'const':'USD'},'units':{'const':'goods_count'}}),'preconditions':arr(ID,1),'effects':arr(ID,1),'unsupported':arr(ID,1)})
S['Admission']=obj({'view_ref':ref('View'),'facts_ref':ref('Facts'),'status':{'const':'synthetic_only'}})
S['PostingAuthorization']=obj({'basis_ref':ref('AccountingEventBasis'),'posting_profile_ref':ref('Profile'),'method_ref':ref('MethodDefinition'),'authority_refs':arr(ref('SyntheticAuthority'),1),'status':{'enum':['eligible','unresolved','ineligible']},'findings':arr(obj({'name':ID,'status':{'enum':['satisfied','failed','unknown']},'support':TEXT}),1),'posting_permitted':BOOL,'evidence_level':{'const':'authored-synthetic'},'view_ref':ref('View')})
S['EconomicDelta']=obj({'basis_ref':ref('AccountingEventBasis'),'authorization_ref':ref('PostingAuthorization'),'account_changes':BAL,'inventory_units_before':RAT,'inventory_units_after':RAT})
S['StateTransitionReceipt']=obj({'request_ref':ref('OperationRequest'),'identity':IDENTITY,'basis_ref':ref('AccountingEventBasis'),'authorization_ref':ref('PostingAuthorization'),'journal_ref':ref('JournalProposal'),'delta_ref':ref('EconomicDelta'),'opening_ref':ref('CompanyState'),'closing_ref':ref('CompanyState'),'generation':INT,'status':{'const':'committed'}})
S['Projection']=obj({'family_ref':ref('HistoryFamily'),'scenario_ref':ref('Scenario'),'context_ref':ref('Context'),'view_ref':ref('View'),'opening_ref':ref('CompanyState'),'assumptions_ref':ref('Assumptions'),'lines':obj({k:uncertain(AFF) for k in REPORT_KEYS}),'obligation_refs':arr(ref('Obligation')),'event_plan':arr(obj({'event_kind':ID,'amount':uncertain(AFF),'cash_class':maybe({'enum':['operating','investing','financing']})}),1),
 'proposed_journals':arr(obj({'event_kind':ID,'template_ref':ref('Template'),'treatment_status':{'const':'conditional_on_synthetic_assumptions'},'posting_permission':{'const':False},'lines':arr(obj({'account':{'enum':ACCOUNTS},'signed_amount':AFF}),1)})),
 'closing_balances':obj({k:uncertain(AFF) for k in ACCOUNTS}),
 'historical_investor_claim':{'const':False}})
S['ReportMap']=obj({'context_ref':ref('Context'),'financial_statements':arr({'enum':['balance_sheet','income_oci','cash_flow','equity','debt','plant']},6),'joint_axis':{'const':'same_family_x'},'population_policy':{'enum':['partition','sum_product_and_geography']}})
S['Report']=obj({'projection_ref':ref('Projection'),'map_ref':ref('ReportMap'),'lines':obj({k:uncertain(AFF) for k in REPORT_KEYS}),'obligation_refs':arr(ref('Obligation')),'reconciliation':{'enum':['complete','affected_lines_unresolved']}})
S['TimeSelection']=obj({'selected_refs':arr(ref('Reading')),'excluded':arr(obj({'reading_ref':ref('Reading'),'reason':ID})),'unresolved':arr(obj({'reading_ref':ref('Reading'),'reason':ID})),'value':maybe(RAT),'claim':{'enum':['supported_within_synthetic_dates','unresolved','archival_only']}})
S['Preparation']=obj({'package_ref':ref('Package'),'candidate_reading_refs':arr(ref('Reading')),'obligation_refs':arr(ref('Obligation')),'semantic_admission':{'const':False}})
S['CompileResult']=obj({'module_ref':ref('Module'),'authored_blob':BLOB,'source_kind':{'enum':['text','typed']},'source_map':arr(obj({'declaration':ID,'locator':TEXT}),1),'execution_admitted':BOOL,'capability':{'const':'rational_affine_finite_choices'},'posting_permitted':{'const':False}})
S['HistoryAnswer']=obj({'family_ref':ref('HistoryFamily'),'query':{'enum':['working_capital_bridges','interest_bounds','unweighted','require_probability','nonlinear_bounds','approximate_bounds']},'values':arr(obj({'name':ID,'value':RAT})),'lower':maybe(RAT),'upper':maybe(RAT),'lower_attained':maybe(BOOL),'upper_attained':maybe(BOOL),'measure_ref':{'type':'null'},'guarantee':{'enum':['exact_algebra_within_complete_scope','unweighted_family','unsupported']}})
S['FamilyRefinement']=obj({'parent_ref':ref('HistoryFamily'),'constraint_ref':ref('Constraint'),'relation':{'enum':['subset','empty','replaces_constraint']},'lower':maybe(RAT),'upper':maybe(RAT)})
S['Domain']=obj({'request_ref':ref('OperationRequest'),'family_ref':maybe(ref('HistoryFamily')),'meaning':{'enum':['singleton_request_decision','continuous_family_x']}})
S['Region']=obj({'domain_ref':ref('Domain'),'lower':maybe(RAT),'upper':maybe(RAT),'lower_included':BOOL,'upper_included':BOOL,'predicate':{'enum':['this_request','0_le_x_le_half','half_lt_x_le_1','0_le_x_le_1']}})
S['Checkpoint']=obj({'family_ref':ref('HistoryFamily'),'view_ref':ref('View'),'semantic_manifest_ref':ref('Module'),'partition_refs':arr(ref('Region'),2),'completed_refs':arr(ref('Region')),'unresolved_refs':arr(ref('Region')),'next_index':INT,'used_operation_count':INT})
S['WorkState']=obj({'owner_key':ID,'checkpoint_ref':maybe(ref('Checkpoint')),'generation':INT})
S['WorkReceipt']=obj({'request_ref':ref('OperationRequest'),'opening_ref':ref('WorkState'),'closing_ref':ref('WorkState'),'checkpoint_ref':ref('Checkpoint'),'generation':INT})
S['Explanation']=obj({'output_ref':ref(),'frozen_view_ref':ref('View'),'dependency_refs':arr(ref()),'truncated':BOOL,'current_use':{'enum':['valid','superseded','frozen_only']}})
S['ReviewReceipt']=obj({'request_ref':ref('OperationRequest'),'decision_ref':ref('ReviewDecision'),'old_view_ref':ref('View'),'new_view_ref':ref('View'),'generation':INT,'invalidated_refs':arr(ref())})
S['MigrationComparison']=obj({'original_ref':ref('HistoryFamily'),'candidate_ref':ref('FamilyRefinement'),'relation':{'const':'claimed_representation_only'},'equal_values':BOOL,'equal_domain':BOOL,'accepted':BOOL})
S['ExportManifest']=obj({'root_refs':arr(ref(),1),'record_refs':arr(ref(),1),'required_blobs':arr(BLOB),'complete':BOOL,'financial_admission':{'const':False}})
S['ImportState']=obj({'namespace':ID,'manifest_refs':arr(ref('ExportManifest')),'generation':INT})
S['ImportReceipt']=obj({'request_ref':ref('OperationRequest'),'manifest_ref':ref('ExportManifest'),'opening_ref':ref('ImportState'),'closing_ref':ref('ImportState'),'original_to_local':arr(obj({'original_ref':ref(),'local_ref':ref()}),1),'financial_admission':{'const':False}})
S['PeriodDifference']=obj({'annual_ref':ref('Reading'),'interim_ref':ref('Reading'),'amount':maybe(RAT),'revision_compatible':BOOL,'result_start':DATE,'result_end_exclusive':DATE})
S['Interpretation']=obj({'reading_ref':ref('Reading'),'proposed_meaning':{'enum':['qualitative_majority_unquantified','all_customers','invented_90_percent','nearest_integer_assumption','rounding_unknown']},'constraint_ref':maybe(ref('AssumedInterval')),'admitted':BOOL,'assumption_status':{'enum':['not_supplied','explicit_synthetic_condition']}})
S['AssumedInterval']=obj({'reading_ref':ref('Reading'),'quantity':{'enum':['prompt_payer_fraction','disclosed_principal']},'lower':RAT,'upper':RAT,'lower_included':BOOL,'upper_included':BOOL,'origin':{'const':'explicit_analyst_assumption'},'source_entails_constraint':{'const':False}})
S['ConditionalAdmission']=obj({'decision_ref':ref('ReviewDecision'),'interpretation_ref':ref('Interpretation'),'view_ref':ref('View'),'constraint_ref':ref('AssumedInterval'),'use':{'const':'conditional_only_no_source_fact'}})
S['HistoricalStep']=obj({'opening_ref':ref('CompanyState'),'closing_ref':ref('CompanyState'),'template_ref':ref('Template'),'facts_ref':ref('Facts'),'period':ID,'date':DATE,'event_kind':ID,'lines':arr(LINE,1),'cash_class':maybe({'enum':['operating','investing','financing']}),'status':{'const':'synthetic_reconstruction_not_committed'}})
S['HistoricalReconstruction']=obj({'facts_ref':ref('Facts'),'assumptions_ref':ref('Assumptions'),'opening_ref':ref('CompanyState'),'step_refs':arr(ref('HistoricalStep'),1),'closing_ref':ref('CompanyState'),'period_reports':arr(obj({'period':ID,'context_ref':ref('Context'),'closing_ref':ref('CompanyState'),'lines':obj({k:RAT for k in REPORT_KEYS})}),3),'resolution':{'const':'half_year_aggregate_feasible_order'}})
S['LiteralAdmission']=obj({'source_ref':ref('SourceUnit'),'context_ref':ref('Context'),'concept':ID,'value':RAT,'accepted_at':STAMP,'actor':ID,'scope':{'const':'synthetic_literal_only_no_posting'}})
S['Reading']['properties']['admission_ref']=maybe(ref('LiteralAdmission'));S['Reading']['required'].append('admission_ref')
S['DerivedUse']=obj({'input_refs':arr(ref(),1),'view_ref':ref('View'),'purpose':ID,'value':RAT})
S['View']['properties']['conditional_refs']=arr(ref('Interpretation'));S['View']['required'].append('conditional_refs')
S['SourceUnit']['properties']['locator']=TEXT;S['SourceUnit']['required'].append('locator')
S['SourceUnit']['properties']['reference_targets']=arr(ID);S['SourceUnit']['required'].append('reference_targets')
ARGS_EXTRA={}
S['Environment']=obj({'purpose':{'const':'documentary_fixture'},'numerics':{'const':'exact_rational'},'runtime_executed':{'const':False}})
S['Decoder']=obj({'media_type':{'const':'application/json'},'canonical_encoding':{'const':'accdsl.portable.v1'}})
S['Submission']=obj({'blob_ref':BLOB,'media_type':{'const':'application/json'},'transport':{'const':'authored_fixture'},'decoder_ref':ref('Decoder')})
S['TransportObservation']=obj({'submission_ref':ref('Submission'),'request_ref':ref('OperationRequest'),'observation':{'const':'acknowledgement_timeout'},'commit_observation':{'const':'unknown'},'receipt_ref':{'type':'null'},'next_action':{'const':'resubmit_exact_original_request'}})

ARGS={
 'source.prepare@1':obj({'package_ref':ref('Package'),'source_snapshot_ref':ref('View'),'profile_ref':ref('Profile'),'prior_review_ref':ref('View'),'traversal_budget':INT,'continuation_ref':maybe(ref('Checkpoint'))}),
 'review.propose@1':S['ReviewProposal'],
 'review.commit@1':obj({'proposal_ref':ref('ReviewProposal')}),
 'time.select@1':obj({'package_ref':ref('Package'),'view_ref':ref('View'),'admission_mode':{'enum':['investor_information','system_as_of','archival_exploration']},'selection':{'enum':['original','latest_available']},'information_cutoff':maybe(STAMP),'system_as_of':maybe(STAMP),'requested_layer':{'enum':['raw','accepted']},'concept':ID}),
 'model.compile@1':obj({'source_kind':{'enum':['text','typed']},'source_blob':BLOB,'module_ref':ref('Module'),'schema_lock_ref':ref('SchemaLock'),'view_ref':ref('View'),'target':{'const':'rational_affine'}}),
 'history.construct@1':obj({'module_ref':ref('Module'),'opening_ref':ref('CompanyState'),'view_ref':ref('View'),'query':{'const':'corporate_2025'},'horizon_end':DATE,'cell_budget':INT}),
 'history.refine@1':obj({'family_ref':ref('HistoryFamily'),'constraint_ref':ref('Constraint'),'view_ref':ref('View'),'mode':{'enum':['intersect','replace']}}),
 'history.query@1':obj({'family_ref':ref('HistoryFamily'),'query':deepcopy(S['HistoryAnswer']['properties']['query']),'scenario_rate':RAT,'view_ref':ref('View'),'require_current':BOOL}),
 'scenario.project@1':obj({'family_ref':ref('HistoryFamily'),'scenario_ref':ref('Scenario'),'view_ref':ref('View'),'horizon_end':DATE,'profile_ref':ref('Profile')}),
 'accounting.authorize@1':obj({'basis_ref':ref('AccountingEventBasis'),'posting_profile_ref':ref('Profile')}),
 'accounting.propose@1':obj({'authorization_ref':ref('PostingAuthorization'),'basis_ref':ref('AccountingEventBasis'),'method_ref':ref('MethodDefinition')}),
 'accounting.commit@1':obj({'basis_ref':ref('AccountingEventBasis'),'authorization_ref':ref('PostingAuthorization'),'journal_ref':ref('JournalProposal'),'delta_ref':ref('EconomicDelta')}),
 'report.build@1':obj({'projection_ref':ref('Projection'),'statement_map_ref':ref('ReportMap'),'view_ref':ref('View'),'interval_start':DATE,'interval_end_exclusive':DATE,'require_current':BOOL}),
 'record.explain@1':obj({'output_ref':ref(),'frozen_view_ref':ref('View'),'depth':INT}),
 'work.resume@1':obj({'checkpoint_ref':ref('Checkpoint'),'semantic_manifest_ref':ref('Module'),'additional_cells':INT}),
 'store.migrate@1':obj({'original_ref':ref('HistoryFamily'),'candidate_ref':ref('FamilyRefinement'),'relation':{'const':'representation_only'}}),
 'store.export@1':obj({'root_refs':arr(ref(),1),'format':{'const':'accdsl.portable.v1'},'destination':{'const':'fixture_export'}}),
 'store.import@1':obj({'manifest_ref':ref('ExportManifest'),'target_namespace':ID}),
}
# Period subtraction is a bounded history query, not a new platform endpoint.
ARGS['history.query@1']['properties']['query']['enum']+=['period_difference']
ARGS['history.query@1']['properties']['annual_ref']=maybe(ref('Reading'))
ARGS['history.query@1']['properties']['interim_ref']=maybe(ref('Reading'))
ARGS['history.query@1']['required']+=['annual_ref','interim_ref']
ARG_UNION=[]
for op,sch in ARGS.items():
 ARG_UNION.append(obj({'tag':{'const':op},'value':sch}))
S['OperationRequest']=obj({'operation':{'enum':list(ARGS)},'request_id':ID,'workspace_key':ID,'profile_ref':ref('Profile'),'signature_ref':ref('OperationSignature'),'view_ref':ref('View'),'arguments':{'oneOf':ARG_UNION},'execution':obj({'mode':{'const':'specification_example'},'budget':obj({'operation_count':INT,'elapsed_seconds':INT}),'environment_ref':ref('Environment')}),'expected_head':maybe(HEAD)})
S['OperationResult']=obj({'submission_ref':ref('Submission'),'request_ref':maybe(ref('OperationRequest')),'operation':maybe(ID),'input_view_ref':maybe(ref('View')),'disposition':{'enum':['completed','partial','rejected','unsupported','cancelled','replayed']},'statuses':STATUS,
 'payload':maybe(obj({'tag':ID,'result_refs':arr(ref()),'additional_commit':BOOL})),
 'diagnostics':arr(DIAG),'coverage':maybe(obj({'domain_ref':ref('Domain'),**{k:arr(ref('Region')) for k in ['completed','unresolved','unsupported','infeasible','cancelled']},'relation':{'const':'disjoint_exhaustive'}})),
 'unresolved':arr(ref('Obligation')),'continuation_ref':maybe(ref('Checkpoint')),'commit_observation':{'enum':['committed','not_committed','unknown']},'receipt_ref':maybe(ref()),'evidence_mode':{'const':'specification_example'}})
for op,sch in ARGS.items():S['Arguments.'+op]=sch

def default_status(disposition,validated=True):
 return {'structural_validity':'valid' if validated else 'invalid','mathematical_status':'unresolved' if disposition in ['rejected','unsupported','partial'] else 'defined',
 'computation_status':'not_computed' if disposition in ['rejected','unsupported'] else 'partial' if disposition=='partial' else 'complete',
 'empirical_justification':'not_established','capability_status':'specified_only_no_runtime','accounting_validity':'not_assessed','forecast_validity':'not_assessed','product_readiness':'not_implemented','human_acceptance':'pending'}

def main():
 schema={'$schema':'https://json-schema.org/draft/2020-12/schema','schema_ids':{k:sid(k) for k in S},'$defs':S}
 (OUT/'record-schemas.json').write_text(json.dumps(schema,indent=2)+'\n')
 contract=blob('docs/design/proposal/architecture/corporate-portable-20261015.md')
 lock=add('SchemaLock','schema-lock',{'schema_blob':blob(OUT/'record-schemas.json'),'semantic_contract_blob':contract,'format':'jsonschema2020-12'})
 profile=add('Profile','corporate-profile',{'profile_id':'CorporateJointHistory/1','schema_lock_ref':lock,'operations':list(ARGS),'book_mode':'synthetic','execution_mode':'specification_example'})
 kinds={
 'source.prepare@1':['Preparation'],'review.propose@1':['ReviewProposal'],'review.commit@1':['ReviewReceipt','ConditionalAdmission'],
 'time.select@1':['TimeSelection'],'model.compile@1':['CompileResult'],'history.construct@1':['HistoryFamily','Checkpoint','WorkReceipt'],
 'history.refine@1':['FamilyRefinement'],'history.query@1':['HistoryAnswer','PeriodDifference'],'scenario.project@1':['Projection'],
 'accounting.authorize@1':['PostingAuthorization'],'accounting.propose@1':['JournalProposal','EconomicDelta'],
 'accounting.commit@1':['StateTransitionReceipt'],'report.build@1':['Report'],'record.explain@1':['Explanation'],
 'work.resume@1':['Checkpoint','WorkReceipt'],'store.migrate@1':['MigrationComparison'],'store.export@1':['ExportManifest'],'store.import@1':['ImportReceipt']}
 signatures={}
 for op in ARGS:
  effect={'review.commit@1':'review_transaction','accounting.commit@1':'accounting_transaction','store.migrate@1':'migration_transaction','store.import@1':'import_transaction','history.construct@1':'candidate_or_checkpoint_transaction','work.resume@1':'checkpoint_transaction'}.get(op,'candidate' if op in ['source.prepare@1','review.propose@1','model.compile@1','history.refine@1','scenario.project@1','accounting.propose@1'] else 'read')
  signatures[op]=add('OperationSignature','signature.'+op,{'operation':op,'profile_ref':profile,'arguments_definition':'Arguments.'+op,'payload_kinds':kinds[op],'effects':effect})
 env=add('Environment','documentary-environment',{'purpose':'documentary_fixture','numerics':'exact_rational','runtime_executed':False})
 decoder=add('Decoder','decoder',{'media_type':'application/json','canonical_encoding':'accdsl.portable.v1'})
 contexts={}
 for k,start,end in [('historical','2024-01-01','2025-01-01'),('h1','2024-01-01','2024-07-01'),('h2','2024-07-01','2025-01-01'),('forecast','2025-01-01','2026-01-01')]:
  contexts[k]=add('Context','context.'+k,{'entity':'Northstar','book':'DemoCorporate','perimeter':'single-entity','currency':'USD','unit':'one_currency_unit','basis':'DemoCorporate/1','calendar':'Gregorian','period_start':start,'period_end_exclusive':end,'dimensions':[]})
 native=json.loads((ROOT/'docs/design/fixtures/p05-economic-inputs-v1.json').read_text())
 assumptions=add('Assumptions','assumptions',{'source_blob':blob('docs/design/fixtures/northstar.json'),'inventory_unit_cost':rat(5),'tax_rule':'positive_profit_times_rate_no_deferred_tax','capex_service':'next_period','oci':'zero','intraperiod':'aggregate_feasible_order_not_recovered_invoices','scope_exclusions':['FX','subsidiaries','leases','returns','deferred_tax','automatic_borrowing']})
 opening={k:rat(native['opening'].get(k,'0')) for k in ACCOUNTS}
 facts=add('Facts','economic-facts',{'source_blob':blob('docs/design/fixtures/p05-economic-inputs-v1.json'),'opening':opening,
 'periods':[{'id':p['id'],'start':p['start'],'end_exclusive':{'2024H1':'2024-07-01','2024H2':'2025-01-01'}[p['id']],**{k:rat(p[k]) for k in FACT_KEYS}} for p in native['periods']],
 'assets':[{k:rat(v) if k in ['cost','life_years','accumulated'] else v for k,v in a.items()} for a in native['assets']],
 'contract':{k:rat(v) if k!='maturity' else v for k,v in native['contract'].items()},
 'forecast':{'start':native['forecast']['start'],'end_exclusive':'2026-01-01',**{k:rat(native['forecast'][k]) for k in DRIVERS}}})
 source_blob=blob('docs/design/fixtures/northstar.json')
 inventory=json.loads((ROOT/'docs/design/fixtures/northstar.json').read_text())['coverage_units']
 def source(key,date,ingest,review,revision,parents=(),verified=True):
  unit=next(u for u in inventory if u['id']==key)
  return add('SourceUnit',key,{'source_blob':source_blob,'unit_key':key,'kind':unit['kind'],'locator':'/coverage_units/'+str(inventory.index(unit)),'reference_targets':[unit['target']] if 'target' in unit else [],'public_date':date,'publication_timezone':'UTC','public_bytes_verified':verified,'ingested_at':ingest,'ingestion_verified':True,'reviewed_at':review,'revision_group':revision,'supersedes_refs':list(parents),'fact_status':'authored_synthetic'})
 original=source('NS.h1.original','2024-08-01','2024-08-03T12:00:00Z','2024-08-03T13:00:00Z','v1')
 correction=source('NS.h1.correction','2025-03-02','2025-03-05T12:00:00Z','2025-03-05T13:00:00Z','v2',[original])
 annual=source('NS.fy','2025-03-02','2025-03-05T12:00:00Z','2025-03-05T13:00:00Z','v2')
 units=[original,correction,annual]+[source(u['id'],'2025-03-02','2025-03-05T12:00:00Z','2025-03-05T13:00:00Z','v2') for u in inventory if u['id'] not in ['NS.h1.original','NS.h1.correction','NS.fy']]
 reads=[]
 for key,s,c,val in [('h1.original',original,contexts['h1'],120),('h1.corrected',correction,contexts['h1'],110),('fy.corrected',annual,contexts['historical'],260)]:
  admission=add('LiteralAdmission',key+'.admission',{'source_ref':s,'context_ref':c,'concept':'revenue','value':rat(val),'accepted_at':body(s)['reviewed_at'],'actor':'synthetic-analyst','scope':'synthetic_literal_only_no_posting'})
  reads.append(add('Reading',key,{'source_ref':s,'context_ref':c,'concept':'revenue','value':rat(val),'literal':str(val),'target_layer':'reported_assertion','status':'accepted_literal','admission_ref':admission}))
 oldview=add('View','view.original',{'view_id':'original','parent_ref':None,'source_refs':[original],'reading_refs':[reads[0]],'decision_refs':[],'candidate_membership_revision':0,'mode':'archival_exploration'})
 view=add('View','view.corrected',{'view_id':'corrected','parent_ref':oldview,'source_refs':units,'reading_refs':reads,'decision_refs':[],'candidate_membership_revision':1,'mode':'archival_exploration'})
 coverage=[{'unit_key':body(s)['unit_key'],'disposition':'literal_only','target_ref':s} for s in [original,correction,annual]]
 coverage += [{'unit_key':body(s)['unit_key'],'disposition':'cross_reference_resolved' if body(s)['kind']=='cross_reference' else 'structured','target_ref':ALIASES['NS.debt'] if body(s)['kind']=='cross_reference' else facts if body(s)['kind']!='policy' else assumptions} for s in units[3:]]
 state0=add('CompanyState','opening-2024',{'context_ref':contexts['historical'],'view_ref':view,'sequence':0,'balances':opening,'inventory_units':rat(6),'source_ref':facts})
 symbol=add('Symbol','floating-share',{'name':'x','type':'dimensionless_floating_fraction','lower':rat(0),'upper':rat(1),'lower_included':True,'upper_included':True,'uncertainty_category':'historical_fact_unknown','support_refs':[facts,assumptions]})
 constraints=[add('Constraint','constraint.'+name,{'name':name,'relation':rel,'expression':affine(a,b),'rhs':rat(rhs),'support_refs':[facts,assumptions]}) for name,rel,a,b,rhs in [('nonnegative_float','ge',0,1,0),('bounded_float','le',0,1,1),('principal_total','eq',100,0,100),('historical_interest','eq',5,0,5)]]
 formula=add('DebtFormula','debt.formula',{'principal':rat(100),'fixed_rate':rat('1/20'),'floating_rate':rat('7/100'),'year_fraction':rat(1),'fraction_symbol_ref':symbol,'formula':'principal*((1-x)*fixed_rate+x*floating_rate)*year_fraction','result':affine(5,2),'context_ref':contexts['forecast']})
 templates=[]
 for kind,parameters,preconditions,cash in [('purchase',['units','amount'],['cost_times_units','nonnegative_units'],None),('delivery',['units','consideration'],['inventory_sufficient','control_transferred'],None),('collection',['amount'],['receivable_sufficient'],'operating'),('supplier_payment',['amount'],['payable_sufficient','cash_sufficient'],'operating'),('payroll',['amount'],['cash_sufficient'],'operating'),('plant_addition',['amount','life_years'],['positive_life','cash_sufficient'],'investing'),('depreciation',['year_fraction'],['asset_in_service'],None),('interest',['rate','year_fraction'],['contract_rate_admitted'],'operating'),('tax',['rate','payment'],['teaching_tax_scope'],'operating'),('dividend',['amount'],['synthetic_distribution_assumed','cash_sufficient'],'financing'),('close',[],['temporary_balances_known'],None)]:
  templates.append(add('Template','template.'+kind,{'event_kind':kind,'parameter_names':parameters,'preconditions':preconditions,'method_contract':contract,'cash_class':cash,'source_refs':[facts,assumptions]}))
 def module(key,full):
  return add('Module',key,{'context_refs':list(contexts.values()),'source_refs':units,'reading_refs':reads,'assumption_refs':[assumptions],'symbol_refs':[symbol],'constraint_refs':constraints,'derived_expression_refs':[formula],'template_refs':templates if full else [],'facts_ref':facts,'profile_ref':profile,'view_ref':view,'scope':'corporate_full' if full else 'debt_fragment','source_kind':'typed_full' if full else 'matched_semantics'})
 fullmodule=module('module.corporate',True); debtmodule=module('module.debt',False)
 history=build_history(facts,assumptions,state0,contexts)
 for item in coverage:
  if item['unit_key'] in ['NS.h1.correction','NS.fy']:item.update(disposition='structured',target_ref=history)
  elif item['unit_key']=='NS.opening':item.update(target_ref=state0)
  elif item['unit_key']=='NS.debt':item.update(target_ref=fullmodule)
 package=add('Package','source-package',{'unit_refs':units,'reading_refs':reads,'obligation_refs':[],'coverage':coverage,'recursive_closure':True})
 family=add('HistoryFamily','family.corporate',{'module_ref':fullmodule,'view_ref':view,'symbol_ref':symbol,'constraint_refs':constraints,'opening_ref':state0,'reconstruction_ref':history,'target_layer':'conditional_accounting_history','scope':'Northstar_declared_aggregate_model','formulation_complete':True,'obligation_refs':[],'measure_ref':None})
 # Requests/results retain exact bytes; expected cases never execute an endpoint.
 def request(key,op,args,v=None,head=None,budget=1000):
  if op=='history.query@1':args={'annual_ref':None,'interim_ref':None,**args}
  req=add('OperationRequest','request.'+key,{'operation':op,'request_id':key,'workspace_key':'Northstar-specification','profile_ref':profile,'signature_ref':signatures[op],'view_ref':v or view,'arguments':{'tag':op,'value':args},'execution':{'mode':'specification_example','budget':{'operation_count':budget,'elapsed_seconds':60},'environment_ref':env},'expected_head':head})
  sub=add('Submission','submission.'+key,{'blob_ref':bytes_blob(key+'.json',enc(REG[req['digest']])),'media_type':'application/json','transport':'authored_fixture','decoder_ref':decoder})
  return req,sub
 def result(key,req,sub,outputs=(),disposition='completed',code=None,validated=True,receipt=None,commit=False,continuation=None,obligations=(),coverage=None,stage=None):
  op=body(req)['operation']
  if coverage is None and validated:
   family_domain=op in ['history.construct@1','history.query@1','history.refine@1','scenario.project@1','report.build@1']
   dom=add('Domain','domain.'+key,{'request_ref':req,'family_ref':family if family_domain else None,'meaning':'continuous_family_x' if family_domain else 'singleton_request_decision'})
   region=add('Region','region.'+key,{'domain_ref':dom,'lower':rat(0) if family_domain else None,'upper':rat(1) if family_domain else None,'lower_included':family_domain,'upper_included':family_domain,'predicate':'0_le_x_le_1' if family_domain else 'this_request'})
   label='unsupported' if disposition=='unsupported' else 'unresolved' if disposition=='partial' else 'completed'
   coverage={'domain_ref':dom,**{k:[region] if k==label else [] for k in ['completed','unresolved','unsupported','infeasible','cancelled']},'relation':'disjoint_exhaustive'}
  diagnostics=[] if code is None else [{'code':code,'stage':stage or ('binding_and_admission' if not validated else 'calculation_or_transaction'),'record_ref':req if validated else None,'source_locator':None,'field_path':'arguments','affected_query_branch_ids':[key],'dependency_path':[],'observed':code,'expected_rule':'corporate-portable-20261015','retry_advice':'new_request_after_input_repair','blocking_diagnostic_ids':[]}]
  if code=='TEXT_DECLARATION_UNSUPPORTED':diagnostics[0].update(source_locator='bytes/unsupported-source.txt:1:17',field_path='arguments.value.source_blob')
  return add('OperationResult','result.'+key,{'submission_ref':sub,'request_ref':req if validated else None,'operation':op if validated else None,'input_view_ref':body(req)['view_ref'] if validated else None,'disposition':disposition,'statuses':default_status(disposition,validated),
   'payload':None if not validated else {'tag':op,'result_refs':list(outputs),'additional_commit':commit},'diagnostics':diagnostics,'coverage':coverage if validated else None,'unresolved':list(obligations),'continuation_ref':continuation,'commit_observation':'committed' if commit else 'not_committed','receipt_ref':receipt,'evidence_mode':'specification_example'})
 def exchange(key,op,args,outputs=(),**kwargs):
  req,sub=request(key,op,args,kwargs.pop('view',None),kwargs.pop('head',None),kwargs.pop('budget',1000))
  res=result(key,req,sub,outputs,**kwargs)
  EXCHANGES.append({'id':key,'request_ref':req,'submission_ref':sub,'response_ref':res,'world_before':None,'world_after':None,'evidence_mode':'specification_example'})
  return req,res
 prep=add('Preparation','prepared',{'package_ref':package,'candidate_reading_refs':reads,'obligation_refs':[],'semantic_admission':False})
 exchange('prepare','source.prepare@1',{'package_ref':package,'source_snapshot_ref':view,'profile_ref':profile,'prior_review_ref':view,'traversal_budget':20,'continuation_ref':None},[prep])
 missing=add('Obligation','missing-debt-reference',{'code':'INCORPORATED_REFERENCE_MISSING','source_ref':original,'affected_targets':['debt_rights','history_admission'],'reason':'Separate adverse package variant lacks an incorporated agreement; no rate, maturity or permission is inferred.'})
 partial_package=add('Package','package.missing',{'unit_refs':units,'reading_refs':reads,'obligation_refs':[missing],'coverage':body(package)['coverage']+[{'unit_key':'debt.agreement','disposition':'unresolved','target_ref':missing}],'recursive_closure':False})
 partialprep=add('Preparation','prepared.partial',{'package_ref':partial_package,'candidate_reading_refs':reads,'obligation_refs':[missing],'semantic_admission':False})
 exchange('prepare-missing','source.prepare@1',{'package_ref':partial_package,'source_snapshot_ref':view,'profile_ref':profile,'prior_review_ref':view,'traversal_budget':20,'continuation_ref':None},[partialprep],disposition='partial',obligations=[missing])
 # Authored original/corrected selection expectations, independently checked by time rules.
 timecases=[
 ('investor-original','investor_information','latest_available','2024-09-01T00:00:00Z',None,[0],[(1,'AFTER_INFORMATION_CUTOFF'),(2,'CONTEXT_MISMATCH')],[],120),
 ('investor-corrected-archive','investor_information','latest_available','2025-03-03T00:00:00Z',None,[1],[(0,'SUPERSEDED'),(2,'CONTEXT_MISMATCH')],[],110),
 ('system-before-correction','system_as_of','latest_available',None,'2025-03-04T00:00:00Z',[0],[(1,'AFTER_SYSTEM_CUTOFF'),(2,'CONTEXT_MISMATCH')],[],120),
 ('system-after-correction','system_as_of','latest_available',None,'2025-03-06T00:00:00Z',[1],[(0,'SUPERSEDED'),(2,'CONTEXT_MISMATCH')],[],110),
 ('publication-date-precision','investor_information','latest_available','2025-03-02T12:00:00Z',None,[0],[(2,'CONTEXT_MISMATCH')],[(1,'PUBLICATION_PRECISION_UNRESOLVED')],None),
 ('original-root','investor_information','original','2025-03-03T00:00:00Z',None,[0],[(1,'NOT_ORIGINAL_ROOT'),(2,'CONTEXT_MISMATCH')],[],120)]
 for key,mode,selection,K,T,sel,ex,un,val in timecases:
  out=add('TimeSelection',key+'.selection',{'selected_refs':[reads[i] for i in sel],'excluded':[{'reading_ref':reads[i],'reason':c} for i,c in ex],'unresolved':[{'reading_ref':reads[i],'reason':c} for i,c in un],'value':None if val is None else rat(val),'claim':'unresolved' if un else 'supported_within_synthetic_dates'})
  exchange(key,'time.select@1',{'package_ref':package,'view_ref':view,'admission_mode':mode,'selection':selection,'information_cutoff':K,'system_as_of':T,'requested_layer':'accepted','concept':'H1.revenue'},[out],disposition='partial' if un else 'completed')
 # Existing debt text is retained as source; exact matched subset input is explicit.
 debt_text=bytes_blob('debt-source.txt',b'NorthstarDebt { principal = 100; x: Rational in [0,1]; fixed_rate = 1/20; floating_rate = 7/100; interest = 100*((1-x)*fixed_rate+x*floating_rate); }\n')
 typed_debt=bytes_blob('debt-typed.json',enc(REG[debtmodule['digest']]))
 typed_full=bytes_blob('corporate-typed.json',enc(REG[fullmodule['digest']]))
 for key,kind,source,mod in [('compile-text','text',debt_text,debtmodule),('compile-typed-debt','typed',typed_debt,debtmodule),('compile-corporate','typed',typed_full,fullmodule)]:
  out=add('CompileResult',key+'.output',{'module_ref':mod,'authored_blob':source,'source_kind':kind,'source_map':[{'declaration':'x','locator':'debt-source: x' if kind=='text' else 'body.symbol_refs[0]'}],'execution_admitted':True,'capability':'rational_affine_finite_choices','posting_permitted':False})
  exchange(key,'model.compile@1',{'source_kind':kind,'source_blob':source,'module_ref':mod,'schema_lock_ref':lock,'view_ref':view,'target':'rational_affine'},[out])
 unsupported_text=bytes_blob('unsupported-source.txt',b'NorthstarDebt { payroll = 20; }\n')
 exchange('compile-unsupported-declaration','model.compile@1',{'source_kind':'text','source_blob':unsupported_text,'module_ref':debtmodule,'schema_lock_ref':lock,'view_ref':view,'target':'rational_affine'},disposition='unsupported',code='TEXT_DECLARATION_UNSUPPORTED')
 exchange('construct-family','history.construct@1',{'module_ref':fullmodule,'opening_ref':state0,'view_ref':view,'query':'corporate_2025','horizon_end':'2026-01-01','cell_budget':2},[family])
 for key,query,vals,lower,upper,guarantee in [('bridges','working_capital_bridges',[('collections',245),('purchases',155),('supplier_payments',145)],None,None,'exact_algebra_within_complete_scope'),('interest-bounds','interest_bounds',[],5,7,'exact_algebra_within_complete_scope'),('unweighted','unweighted',[],None,None,'unweighted_family'),('probability-refused','require_probability',[],None,None,'unsupported'),('nonlinear-refused','nonlinear_bounds',[],None,None,'unsupported'),('approximation-refused','approximate_bounds',[],None,None,'unsupported')]:
  answer=add('HistoryAnswer',key+'.answer',{'family_ref':family,'query':query,'values':[{'name':k,'value':rat(v)} for k,v in vals],'lower':rat(lower) if lower is not None else None,'upper':rat(upper) if upper is not None else None,'lower_attained':True if lower is not None else None,'upper_attained':True if upper is not None else None,'measure_ref':None,'guarantee':guarantee})
  exchange(key,'history.query@1',{'family_ref':family,'query':query,'scenario_rate':rat('7/100'),'view_ref':view,'require_current':True},[answer],disposition='unsupported' if guarantee=='unsupported' else 'completed',code={'require_probability':'MEASURE_REQUIRED','nonlinear_bounds':'NONLINEAR_CAPABILITY_REQUIRED','approximate_bounds':'APPROXIMATION_POLICY_REQUIRED'}.get(query))
 # Remaining connected scenarios, transaction and recovery fixtures are authored below.
 build_connections(locals())
 # Invalid submissions remain exact bytes and never enter the valid registry.
 good=ALIASES['request.compile-corporate']
 for label,code,stage,transform in [
  ('malformed-json','JSON_DECODE_FAILED','decode',None),
  ('unknown-field','UNKNOWN_FIELD','field_shape','extra'),
  ('missing-reference','REQUIRED_REFERENCE_MISSING','reference_integrity','missing'),
  ('wrong-argument-tag','ARGUMENT_SIGNATURE_MISMATCH','binding_and_admission','tag')]:
  wire=deepcopy(REG[good['digest']])
  if transform=='extra':wire['body']['unexpected']=True
  if transform=='missing':wire['body']['arguments']['value']['module_ref']['digest']='0'*64
  if transform=='tag':wire['body']['operation']='source.prepare@1'
  deps={enc(r):r for r in links(wire['body'])};wire['dependencies']=[deps[k] for k in sorted(deps)]
  submitted=b'{"kind":' if transform is None else enc(wire)
  sub=add('Submission','submission.'+label,{'blob_ref':bytes_blob(label+'.json',submitted),'media_type':'application/json','transport':'authored_fixture','decoder_ref':decoder})
  res=result(label,good,sub,disposition='rejected',validated=False,code=code,stage=stage)
  baseline=deepcopy(EXCHANGES[0]['world_before'])
  EXCHANGES.append({'id':label,'request_ref':None,'submission_ref':sub,'response_ref':res,'world_before':baseline,'world_after':deepcopy(baseline),'evidence_mode':'specification_example'})
 pins=['docs/design/fixtures/northstar.json','docs/design/fixtures/p05-economic-inputs-v1.json','docs/design/proposal/architecture/interfaces-contract-v1.md','docs/design/proposal/architecture/language-ir-contract-v1.md','docs/design/proposal/architecture/time-contract-v2.md','docs/design/proposal/architecture/initial-profile-v1.md','docs/design/proposal/manuscript-production-cost-20261015/chapters/13-reference-company.tex']
 bundle={'evidence_mode':'specification_example','product_implemented':False,'schema_lock_ref':lock,'profile_ref':profile,'record_registry':REG,'aliases':ALIASES,'blobs':BLOBS,'exchanges':EXCHANGES,'source_pins':[{'path':p,'sha256':hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for p in pins]}
 (OUT/'portable-exchanges.json').write_text(json.dumps(bundle,indent=2)+'\n')
 print(json.dumps({'records':len(REG),'blobs':len(BLOBS),'exchanges':len(EXCHANGES)}))

def build_history(facts,assumptions,state0,contexts):
 # Authored journal table, independently checked against economic drivers.
 schedules=[('2024H1','2024-06-30',[
  ('purchase',[('inventory',70),('payables',-70)],14),
  ('delivery',[('receivables',110),('revenue',-110),('cost_of_sales',75),('inventory',-75)],-15),
  ('collection',[('cash',110),('receivables',-110)],0),
  ('supplier_payment',[('payables',65),('cash',-65)],0),
  ('payroll',[('payroll',20),('cash',-20)],0),
  ('plant_addition',[('plant_cost',10),('cash',-10)],0),
  ('depreciation',[('depreciation',5),('accum_depreciation',-5)],0),
  ('interest',[('interest','2.5'),('cash','-2.5')],0),
  ('tax',[('tax','1.5'),('tax_prepaid',2),('cash','-3.5')],0),
  ('dividend',[('retained',4),('cash',-4)],0),
  ('close',[('revenue',110),('cost_of_sales',-75),('payroll',-20),('depreciation',-5),('interest','-2.5'),('tax','-1.5'),('retained',-6)],0)]),
 ('2024H2','2024-12-31',[
  ('purchase',[('inventory',85),('payables',-85)],17),
  ('delivery',[('receivables',150),('revenue',-150),('cost_of_sales',90),('inventory',-90)],-18),
  ('collection',[('cash',135),('receivables',-135)],0),
  ('supplier_payment',[('payables',80),('cash',-80)],0),
  ('payroll',[('payroll',22),('cash',-22)],0),
  ('plant_addition',[('plant_cost',12),('cash',-12)],0),
  ('depreciation',[('depreciation',6),('accum_depreciation',-6)],0),
  ('interest',[('interest','2.5'),('cash','-2.5')],0),
  ('tax',[('tax','5.9'),('tax_prepaid',-2),('cash','-3.9')],0),
  ('dividend',[('retained',5),('cash',-5)],0),
  ('close',[('revenue',150),('cost_of_sales',-90),('payroll',-22),('depreciation',-6),('interest','-2.5'),('tax','-5.9'),('retained','-23.6')],0)])]
 prior=state0;steps=[];ends={}
 for period,date,events in schedules:
  for kind,rows,units in events:
   nxt=deepcopy(body(prior));nxt['sequence']+=1
   for account,amount in rows:
    value=nxt['balances'][account];nxt['balances'][account]=rat(Q(value['n'])/Q(value['d'])+Q(amount))
   value=nxt['inventory_units'];nxt['inventory_units']=rat(Q(value['n'])/Q(value['d'])+units)
   closing=add('CompanyState',period+'.after.'+kind,nxt)
   step=add('HistoricalStep',period+'.'+kind,{'opening_ref':prior,'closing_ref':closing,'template_ref':ALIASES['template.'+kind],'facts_ref':facts,'period':period,'date':date,'event_kind':kind,'lines':[{'account':a,'signed_amount':rat(v)} for a,v in rows],'cash_class':body(ALIASES['template.'+kind])['cash_class'],'status':'synthetic_reconstruction_not_committed'})
   steps.append(step);prior=closing
  ends[period]=prior
 reports=[]
 for period,c,values in [
  ('2024H1','h1',[65,20,25,85,2,197,25,100,50,22,72,110,75,20,5,'2.5','7.5','1.5',6,0,6,19,-10,-4,5,60,70,4,10]),
  ('2024H2','h2',['74.6',35,20,91,0,'220.6',30,100,50,'40.6','90.6',150,90,22,6,'2.5','29.5','5.9','23.6',0,'23.6','26.6',-12,-5,'9.6',65,72,5,12]),
  ('2024FY','historical',['74.6',35,20,91,0,'220.6',30,100,50,'40.6','90.6',260,165,42,11,5,37,'7.4','29.6',0,'29.6','45.6',-22,-9,'14.6',60,70,9,22])]:
  assert len(values)==len(REPORT_KEYS)
  reports.append({'period':period,'context_ref':contexts[c],'closing_ref':ends['2024H2'] if period=='2024FY' else ends[period],'lines':{k:rat(v) for k,v in zip(REPORT_KEYS,values)}})
 return add('HistoricalReconstruction','historical.reconstruction',{'facts_ref':facts,'assumptions_ref':assumptions,'opening_ref':state0,'step_refs':steps,'closing_ref':prior,'period_reports':reports,'resolution':'half_year_aggregate_feasible_order'})

def build_connections(scope):
 exchange,request,result=[scope[k] for k in ['exchange','request','result']]
 family,view,oldview,facts,assumptions,contexts,profile,fullmodule,state0,reads,original,package=[scope[k] for k in ['family','view','oldview','facts','assumptions','contexts','profile','fullmodule','state0','reads','original','package']]
 # Preserve ambiguity of qualitative language and precision; no implicit constraint.
 supplemental=add('SourceUnit','NS.adverse.narrative',{**body(original),'source_blob':bytes_blob('adverse-narrative.json',enc({'collections_policy':'Substantially all customers pay promptly.','displayed_principal':'100'})),'unit_key':'NS.adverse.narrative','kind':'note','locator':'/','reference_targets':[],'supersedes_refs':[]})
 narrative=add('Reading','narrative.reading',{'source_ref':supplemental,'context_ref':contexts['h1'],'concept':'collections_policy','value':None,'literal':'Substantially all customers pay promptly.','target_layer':'reported_assertion','status':'candidate'})
 rounded=add('Reading','rounding.reading',{'source_ref':supplemental,'context_ref':contexts['h1'],'concept':'displayed_principal','value':rat(100),'literal':'100','target_layer':'reported_assertion','status':'candidate'})
 for meaning,admitted in [('qualitative_majority_unquantified',False),('all_customers',False),('invented_90_percent',False),('rounding_unknown',False),('nearest_integer_assumption',False)]:
  reading=rounded if meaning in ['rounding_unknown','nearest_integer_assumption'] else narrative
  interp=add('Interpretation','interpretation.'+meaning,{'reading_ref':reading,'proposed_meaning':meaning,'constraint_ref':None,'admitted':admitted,'assumption_status':'not_supplied'})
  proposal_args={'target_ref':interp,'layer':'interpretation','decision':'retain_alternative','evidence_refs':[reading],'actor':'synthetic-analyst','rationale':'Candidate only; qualitative wording and displayed precision imply no numerical condition.','replacement_ref':None}
  proposal=add('ReviewProposal','proposal.'+meaning,proposal_args)
  exchange('propose-'+meaning,'review.propose@1',proposal_args,[proposal])
 invented=ALIASES['proposal.invented_90_percent']
 review_head={'owner_key':'review/Northstar','state_ref':oldview,'generation':0}
 exchange('reject-invented-threshold','review.commit@1',{'proposal_ref':invented},disposition='rejected',code='UNSUPPORTED_NUMERIC_INTERPRETATION',validated=False,head=review_head)
 for label,reading,meaning,quantity,lo,hi,inclusive in [('all-payers',narrative,'all_customers','prompt_payer_fraction',1,1,True),('nearest-unit',rounded,'nearest_integer_assumption','disclosed_principal','99.5','100.5',False)]:
  condition=add('AssumedInterval','assumption.'+label,{'reading_ref':reading,'quantity':quantity,'lower':rat(lo),'upper':rat(hi),'lower_included':True,'upper_included':inclusive,'origin':'explicit_analyst_assumption','source_entails_constraint':False})
  interpretation=add('Interpretation','conditional.'+label,{'reading_ref':reading,'proposed_meaning':meaning,'constraint_ref':condition,'admitted':False,'assumption_status':'explicit_synthetic_condition'})
  prop=add('ReviewProposal','proposal.admit.'+label,{'target_ref':interpretation,'layer':'assumption','decision':'accept','evidence_refs':[reading,condition],'actor':'synthetic-analyst','rationale':'Admit a conditional analytical assumption; preserve the unquantified source alternative.','replacement_ref':None})
  dec=add('ReviewDecision','decision.'+label,{'proposal_ref':prop,'prior_view_ref':oldview,'accepted':True,'decided_at':'2025-03-05T13:00:00Z','scope':'conditional analytical use only; not asserted by the source'})
  nv=add('View','view.'+label,{'view_id':label,'parent_ref':oldview,'source_refs':[original,supplemental],'reading_refs':[reads[0],reading],'decision_refs':[dec],'conditional_refs':[interpretation],'candidate_membership_revision':1,'mode':'archival_exploration'})
  admitted=add('ConditionalAdmission','admitted.'+label,{'decision_ref':dec,'interpretation_ref':interpretation,'view_ref':nv,'constraint_ref':condition,'use':'conditional_only_no_source_fact'})
  ar,asu=request('admit-'+label,'review.commit@1',{'proposal_ref':prop},oldview,review_head)
  arec=add('ReviewReceipt','receipt.'+label,{'request_ref':ar,'decision_ref':dec,'old_view_ref':oldview,'new_view_ref':nv,'generation':1,'invalidated_refs':[]})
  arsp=result('admit-'+label,ar,asu,[arec,admitted],receipt=arec,commit=True)
  EXCHANGES.append({'id':'admit-'+label,'request_ref':ar,'submission_ref':asu,'response_ref':arsp,'world_before':{'review_head':review_head},'world_after':{'review_head':{'owner_key':'review/Northstar','state_ref':nv,'generation':1}},'evidence_mode':'specification_example'})
 # A reviewed source supersession changes only the review owner.
 proposal=add('ReviewProposal','proposal.corrected-reading',{'target_ref':reads[0],'layer':'interpretation','decision':'supersede','evidence_refs':[reads[1]],'actor':'synthetic-analyst','rationale':'Supersede current source selection using the later correction; both original and corrected literal extractions remain accepted in their own source versions.','replacement_ref':reads[1]})
 decision=add('ReviewDecision','decision.corrected-reading',{'proposal_ref':proposal,'prior_view_ref':oldview,'accepted':True,'decided_at':'2025-03-05T13:00:00Z','scope':'H1 revenue and dependent current results; no accounting permission'})
 reviewed=add('View','view.review-commit',{'view_id':'review-commit','parent_ref':oldview,'source_refs':body(view)['source_refs'],'reading_refs':reads,'decision_refs':[decision],'candidate_membership_revision':1,'mode':'archival_exploration'})
 req,sub=request('review-correction','review.commit@1',{'proposal_ref':proposal},oldview,review_head)
 old_selection=add('DerivedUse','original.selection',{'input_refs':[oldview,reads[0]],'view_ref':oldview,'purpose':'candidate_membership_selection','value':rat(120)})
 old_profit=add('DerivedUse','original.profit',{'input_refs':[old_selection,assumptions],'view_ref':oldview,'purpose':'profit_from_original_revenue','value':rat(14)})
 old_equity=add('DerivedUse','original.equity',{'input_refs':[old_profit,facts],'view_ref':oldview,'purpose':'equity_from_original_profit','value':rat(80)})
 receipt=add('ReviewReceipt','review.receipt',{'request_ref':req,'decision_ref':decision,'old_view_ref':oldview,'new_view_ref':reviewed,'generation':1,'invalidated_refs':[reads[0],old_selection,old_profit,old_equity]})
 response=result('review-correction',req,sub,[receipt],receipt=receipt,commit=True)
 EXCHANGES.append({'id':'review-correction','request_ref':req,'submission_ref':sub,'response_ref':response,'world_before':{'review_head':review_head},'world_after':{'review_head':{'owner_key':'review/Northstar','state_ref':reviewed,'generation':1}},'evidence_mode':'specification_example'})
 late=add('DerivedUse','late.original-equity',{'input_refs':[old_equity],'view_ref':oldview,'purpose':'late_descendant_of_superseded_original','value':rat(80)})
 exchange('late-descendant-rebind','record.explain@1',{'output_ref':late,'frozen_view_ref':reviewed,'depth':4},disposition='rejected',validated=False,code='FROZEN_VIEW_MISMATCH')
 for key,index,ok,value in [('compatible-YTD',1,True,150),('mixed-YTD',0,False,None)]:
  answer=add('PeriodDifference',key+'.difference',{'annual_ref':reads[2],'interim_ref':reads[index],'amount':None if value is None else rat(value),'revision_compatible':ok,'result_start':'2024-07-01','result_end_exclusive':'2025-01-01'})
  exchange(key,'history.query@1',{'family_ref':family,'query':'period_difference','scenario_rate':rat('7/100'),'view_ref':view,'require_current':True,'annual_ref':reads[2],'interim_ref':reads[index]},[answer] if ok else [],disposition='completed' if ok else 'rejected',code=None if ok else 'REVISION_CONTEXT_MISMATCH',validated=ok)
 # Affine output is independently authored, retaining all x in [0,1].
 def projection(key,rate='7/100',missing=False,tax=True,mode='archival_exploration',origin='imposed_assumption'):
  drivers=deepcopy(body(facts)['forecast']);drivers={k:drivers[k] for k in DRIVERS}
  drivers['floating_rate']=rat(rate)
  obligations=[]
  if missing:
   affected=['cash','receivables','assets','operating_cash','cash_change']
   obligations.append(add('Obligation','obligation.collection.'+key,{'code':'COLLECTION_FRACTION_UNKNOWN','source_ref':None,'affected_targets':affected+['collections','collection_fraction','settlement_feasibility'],'reason':'No collection timing supplied; delivery profit is determined, but funded settlements remain conditional.'}))
   drivers['collection_fraction']=unknown('COLLECTION_FRACTION_UNKNOWN',obligations)
  if not tax:
   affected=['tax','profit','comprehensive_income','retained','equity','cash','assets','operating_cash','cash_change','tax_prepaid']
   obligations.append(add('Obligation','obligation.tax.'+key,{'code':'TAX_METHOD_UNSUPPORTED','source_ref':None,'affected_targets':affected+['closing_balances','period_close'],'reason':'Tax and final closing entries are unsupported in this adverse request.'}))
  scenario=add('Scenario','scenario.'+key,{'context_ref':contexts['forecast'],'family_ref':family,'mode':'exogenous_stress','information_mode':mode,'decision_at':'2025-01-01T00:00:00Z','information_cutoff':'2025-01-01T00:00:00Z' if mode=='investor_information' else None,'driver_values':drivers,'driver_origin':origin,'realized_at':'2025-12-31T00:00:00Z' if origin=='future_realization' else None,'future_realizations_permitted':False,'tax_method_supported':tax})
  slope=Q(2) if rate=='7/100' else Q(4)
  pairs={'cash':('95.2',-slope*Q('4/5')),'receivables':(55,0),'inventory':(40,0),'plant_net':(98,0),'tax_prepaid':(0,0),'assets':('288.2',-slope*Q('4/5')),'payables':(40,0),'debt':(100,0),'capital':(50,0),'retained':('98.2',-slope*Q('4/5')),'equity':('148.2',-slope*Q('4/5')),'revenue':(300,0),'cost_of_sales':(150,0),'payroll':(50,0),'depreciation':(13,0),'interest':(5,slope),'profit_before_tax':(82,-slope),'tax':('16.4',-slope/5),'profit':('65.6',-slope*Q('4/5')),'oci':(0,0),'comprehensive_income':('65.6',-slope*Q('4/5')),'operating_cash':('48.6',-slope*Q('4/5')),'investing_cash':(-20,0),'financing_cash':(-8,0),'cash_change':('20.6',-slope*Q('4/5')),'opening_cash':('74.6',0),'opening_equity':('90.6',0),'dividends':(8,0),'plant_additions':(20,0)}
  lines={k:affine(*pairs[k]) for k in REPORT_KEYS}
  if missing:
   affected=['cash','receivables','assets','operating_cash','cash_change']
   for k in affected:lines[k]=unknown('COLLECTION_FRACTION_UNKNOWN',obligations)
  if not tax:
   affected=['tax','profit','comprehensive_income','retained','equity','cash','assets','operating_cash','cash_change','tax_prepaid']
   for k in affected:lines[k]=unknown('TAX_METHOD_UNSUPPORTED',obligations)
  balances={k:affine(0) for k in ACCOUNTS}
  for k in ['cash','receivables','inventory','tax_prepaid']:balances[k]=lines[k]
  balances.update(plant_cost=affine(142),accum_depreciation=affine(-44),payables=affine(-40),debt=affine(-100),capital=affine(-50),retained=unknown('TAX_METHOD_UNSUPPORTED',obligations) if not tax else affine('-98.2',slope*Q('4/5')))
  if not tax:
   for k in ['revenue','cost_of_sales','payroll','depreciation','interest','tax']:balances[k]=unknown('PERIOD_CLOSE_UNRESOLVED',obligations)
  journals=[]
  def journal(kind,rows):journals.append({'event_kind':kind,'template_ref':ALIASES['template.'+kind],'treatment_status':'conditional_on_synthetic_assumptions','posting_permission':False,'lines':[{'account':a,'signed_amount':affine(c,b)} for a,c,b in rows]})
  journal('purchase',[('inventory',170,0),('payables',-170,0)])
  journal('delivery',[('receivables',300,0),('revenue',-300,0),('cost_of_sales',150,0),('inventory',-150,0)])
  if not missing:journal('collection',[('cash',280,0),('receivables',-280,0)])
  journal('supplier_payment',[('payables',160,0),('cash',-160,0)])
  journal('payroll',[('payroll',50,0),('cash',-50,0)])
  journal('plant_addition',[('plant_cost',20,0),('cash',-20,0)])
  journal('depreciation',[('depreciation',13,0),('accum_depreciation',-13,0)])
  journal('interest',[('interest',5,slope),('cash',-5,-slope)])
  if tax:journal('tax',[('tax','16.4',-slope/5),('cash','-16.4',slope/5)])
  journal('dividend',[('retained',8,0),('cash',-8,0)])
  if tax:journal('close',[('revenue',300,0),('cost_of_sales',-150,0),('payroll',-50,0),('depreciation',-13,0),('interest',-5,-slope),('tax','-16.4',slope/5),('retained','-65.6',slope*Q('4/5'))])
  events=[{'event_kind':j['event_kind'],'amount':j['lines'][0]['signed_amount'],'cash_class':{'collection':'operating','supplier_payment':'operating','payroll':'operating','plant_addition':'investing','interest':'operating','tax':'operating','dividend':'financing'}.get(j['event_kind'])} for j in journals]
  if missing:events.insert(2,{'event_kind':'collection','amount':unknown('COLLECTION_FRACTION_UNKNOWN',obligations),'cash_class':'operating'})
  if not tax:events.append({'event_kind':'tax','amount':unknown('TAX_METHOD_UNSUPPORTED',obligations),'cash_class':'operating'})
  out=add('Projection','projection.'+key,{'family_ref':family,'scenario_ref':scenario,'context_ref':contexts['forecast'],'view_ref':view,'opening_ref':body(scope['history'])['closing_ref'],'assumptions_ref':assumptions,'lines':lines,'obligation_refs':obligations,'event_plan':events,'proposed_journals':journals,'closing_balances':balances,'historical_investor_claim':False})
  args={'family_ref':family,'scenario_ref':scenario,'view_ref':view,'horizon_end':'2026-01-01','profile_ref':profile}
  reject=mode=='investor_information' or origin=='future_realization'
  exchange(key,'scenario.project@1',args,[] if reject else [out],disposition='rejected' if reject else 'partial' if obligations else 'completed',validated=not reject,code='AFTER_INFORMATION_CUTOFF' if mode=='investor_information' else 'FUTURE_REALIZATION_FORBIDDEN' if reject else None,obligations=obligations if not reject else [])
  return out
 projections=[projection('stress7'),projection('stress9','9/100'),projection('missing-collection',missing=True),projection('unsupported-tax',tax=False)]
 projection('investor-lookahead',mode='investor_information')
 projection('policy-lookahead',origin='future_realization')
 normalmap=add('ReportMap','map.normal',{'context_ref':contexts['forecast'],'financial_statements':['balance_sheet','income_oci','cash_flow','equity','debt','plant'],'joint_axis':'same_family_x','population_policy':'partition'})
 wrongmap=add('ReportMap','map.overlap',{'context_ref':contexts['forecast'],'financial_statements':['balance_sheet','income_oci','cash_flow','equity','debt','plant'],'joint_axis':'same_family_x','population_policy':'sum_product_and_geography'})
 for n,proj in enumerate(projections):
  b=body(proj);rep=add('Report','report.'+str(n),{'projection_ref':proj,'map_ref':normalmap,'lines':b['lines'],'obligation_refs':b['obligation_refs'],'reconciliation':'affected_lines_unresolved' if b['obligation_refs'] else 'complete'})
  exchange('report-'+str(n),'report.build@1',{'projection_ref':proj,'statement_map_ref':normalmap,'view_ref':view,'interval_start':'2025-01-01','interval_end_exclusive':'2026-01-01','require_current':True},[rep],disposition='partial' if b['obligation_refs'] else 'completed',obligations=b['obligation_refs'])
 exchange('overlap-report','report.build@1',{'projection_ref':projections[0],'statement_map_ref':wrongmap,'view_ref':view,'interval_start':'2025-01-01','interval_end_exclusive':'2026-01-01','require_current':True},disposition='rejected',code='OVERLAPPING_AGGREGATION',validated=False)
 wrongcontext=add('ReportMap','map.wrong-context',{**body(normalmap),'context_ref':contexts['h1']})
 for label,mapping,start,code in [('wrong-report-period',normalmap,'2024-01-01','REPORT_PERIOD_MISMATCH'),('wrong-report-context',wrongcontext,'2025-01-01','REPORT_CONTEXT_MISMATCH')]:
  exchange(label,'report.build@1',{'projection_ref':projections[0],'statement_map_ref':mapping,'view_ref':view,'interval_start':start,'interval_end_exclusive':'2026-01-01','require_current':True},disposition='rejected',code=code,validated=False)
 # A new candidate-set revision stales current use even with unchanged selected amounts.
 nextview=add('View','view.membership-changed',{'view_id':'membership-changed','parent_ref':view,'source_refs':body(view)['source_refs']+[supplemental],'reading_refs':reads+[narrative],'decision_refs':[],'candidate_membership_revision':2,'mode':'archival_exploration'})
 exchange('stale-current-report','report.build@1',{'projection_ref':projections[0],'statement_map_ref':normalmap,'view_ref':nextview,'interval_start':'2025-01-01','interval_end_exclusive':'2026-01-01','require_current':True},view=nextview,disposition='rejected',code='DEPENDENCY_VIEW_SUPERSEDED',validated=False)
 explain=add('Explanation','explanation.frozen',{'output_ref':projections[0],'frozen_view_ref':view,'dependency_refs':REG[projections[0]['digest']]['dependencies'],'truncated':True,'current_use':'frozen_only'})
 exchange('frozen-explain','record.explain@1',{'output_ref':projections[0],'frozen_view_ref':view,'depth':1},[explain])
 # Continuous partition is preserved after a finite budget; changed semantics cannot resume.
 args={'module_ref':fullmodule,'opening_ref':state0,'view_ref':view,'query':'corporate_2025','horizon_end':'2026-01-01','cell_budget':1}
 work0=add('WorkState','work.empty',{'owner_key':'work/Northstar-search','checkpoint_ref':None,'generation':0})
 workhead={'owner_key':'work/Northstar-search','state_ref':work0,'generation':0}
 req,sub=request('partial-search','history.construct@1',args,budget=1,head=workhead)
 domain=add('Domain','search.domain',{'request_ref':req,'family_ref':family,'meaning':'continuous_family_x'})
 regions=[add('Region','search.cell.'+str(i),{'domain_ref':domain,'lower':rat(a),'upper':rat(b),'lower_included':inc,'upper_included':True,'predicate':p}) for i,(a,b,inc,p) in enumerate([(0,'1/2',True,'0_le_x_le_half'),('1/2',1,False,'half_lt_x_le_1')])]
 checkpoint=add('Checkpoint','search.checkpoint1',{'family_ref':family,'view_ref':view,'semantic_manifest_ref':fullmodule,'partition_refs':regions,'completed_refs':[regions[0]],'unresolved_refs':[regions[1]],'next_index':1,'used_operation_count':1})
 coverage={'domain_ref':domain,'completed':[regions[0]],'unresolved':[regions[1]],'unsupported':[],'infeasible':[],'cancelled':[],'relation':'disjoint_exhaustive'}
 work1=add('WorkState','work.partial',{'owner_key':workhead['owner_key'],'checkpoint_ref':checkpoint,'generation':1})
 workreceipt1=add('WorkReceipt','work.receipt1',{'request_ref':req,'opening_ref':work0,'closing_ref':work1,'checkpoint_ref':checkpoint,'generation':1})
 response=result('partial-search',req,sub,[family,checkpoint,workreceipt1],disposition='partial',continuation=checkpoint,coverage=coverage,receipt=workreceipt1,commit=True)
 head1={**workhead,'state_ref':work1,'generation':1}
 EXCHANGES.append({'id':'partial-search','request_ref':req,'submission_ref':sub,'response_ref':response,'world_before':{'work_head':workhead,'work_receipts':[]},'world_after':{'work_head':head1,'work_receipts':[workreceipt1]},'evidence_mode':'specification_example'})
 finished=add('Checkpoint','search.checkpoint2',{'family_ref':family,'view_ref':view,'semantic_manifest_ref':fullmodule,'partition_refs':regions,'completed_refs':regions,'unresolved_refs':[],'next_index':2,'used_operation_count':2})
 wr,ws=request('resume-search','work.resume@1',{'checkpoint_ref':checkpoint,'semantic_manifest_ref':fullmodule,'additional_cells':1},head=head1)
 work2=add('WorkState','work.finished',{'owner_key':workhead['owner_key'],'checkpoint_ref':finished,'generation':2})
 workreceipt2=add('WorkReceipt','work.receipt2',{'request_ref':wr,'opening_ref':work1,'closing_ref':work2,'checkpoint_ref':finished,'generation':2})
 wresponse=result('resume-search',wr,ws,[finished,workreceipt2],coverage={**coverage,'completed':regions,'unresolved':[]},receipt=workreceipt2,commit=True)
 EXCHANGES.append({'id':'resume-search','request_ref':wr,'submission_ref':ws,'response_ref':wresponse,'world_before':{'work_head':head1,'work_receipts':[workreceipt1]},'world_after':{'work_head':{**workhead,'state_ref':work2,'generation':2},'work_receipts':[workreceipt1,workreceipt2]},'evidence_mode':'specification_example'})
 exchange('changed-resume','work.resume@1',{'checkpoint_ref':checkpoint,'semantic_manifest_ref':scope['debtmodule'],'additional_cells':1},disposition='rejected',code='SEMANTIC_MANIFEST_CHANGED',validated=False,head=head1)
 EXCHANGES[-1]['world_before']={'work_head':head1,'work_receipts':[workreceipt1]};EXCHANGES[-1]['world_after']=deepcopy(EXCHANGES[-1]['world_before'])
 con=add('Constraint','constraint.x_zero',{'name':'x_zero','relation':'eq','expression':affine(0,1),'rhs':rat(0),'support_refs':[assumptions]})
 refined=add('FamilyRefinement','family.fixed-only',{'parent_ref':family,'constraint_ref':con,'relation':'subset','lower':rat(0),'upper':rat(0)})
 exchange('explicit-refinement','history.refine@1',{'family_ref':family,'constraint_ref':con,'view_ref':view,'mode':'intersect'},[refined])
 compare=add('MigrationComparison','migration.failed',{'original_ref':family,'candidate_ref':refined,'relation':'claimed_representation_only','equal_values':False,'equal_domain':False,'accepted':False})
 exchange('failed-migration','store.migrate@1',{'original_ref':family,'candidate_ref':refined,'relation':'representation_only'},[compare],disposition='unsupported',code='MIGRATION_CHANGES_FINANCIAL_DOMAIN',head={'owner_key':'model/Northstar','state_ref':family,'generation':0})
 # Atomic first purchase: independent delta contains quantity as well as money.
 branch=add('Branch','branch.historical',{'branch_key':'historical','book_mode':'synthetic','context_ref':contexts['historical'],'view_ref':view})
 tm=add('Time','time.purchase',{'economic_date':'2024-06-30','reporting_start':'2024-01-01','reporting_end_exclusive':'2024-07-01','view_ref':view})
 chart=add('Chart','chart',{'context_ref':contexts['historical'],'account_ids':ACCOUNTS,'sign_convention':'debit_positive'})
 authority=add('SyntheticAuthority','authority',{'assumptions_ref':assumptions,'scope':'Northstar_authored_teaching_only'})
 method=add('MethodDefinition','method.purchase',{'method_id':'northstar.purchase@1','semantic_contract_blob':scope['contract'],'parameter_units':{'amount':'USD','units':'goods_count'},'preconditions':['same_context','units_times_cost_equals_amount','synthetic_admission','nonnegative_units'],'effects':['inventory_and_payable_increase','cash_unchanged'],'unsupported':['real_book','foreign_currency','production_cost']})
 admission=add('Admission','admission',{'view_ref':view,'facts_ref':facts,'status':'synthetic_only'})
 event=add('EconomicEvent','event.purchase',{'business_event_id':'2024H1.purchase','context_ref':contexts['historical'],'period':'2024H1','date':'2024-06-30','sequence':1,'event_kind':'purchase','parameters':{'amount':rat(70),'units':rat(14),'consideration':None},'source_ref':facts})
 identity={'entity_id':'Northstar','book_id':'DemoCorporate','branch_key':'historical','business_event_id':'2024H1.purchase'}
 basis=add('AccountingEventBasis','basis.purchase',{'identity':identity,'event_ref':event,'opening_ref':state0,'context_ref':contexts['historical'],'branch_ref':branch,'time_ref':tm,'chart_ref':chart,'authority_refs':[authority],'method_ref':method,'evidence_refs':[facts],'admission_refs':[admission],'assumptions_ref':assumptions,'view_ref':view})
 authorization=add('PostingAuthorization','authorization.purchase',{'basis_ref':basis,'posting_profile_ref':profile,'method_ref':method,'authority_refs':[authority],'status':'eligible','findings':[{'name':'synthetic_method','status':'satisfied','support':'Authored Northstar purchase70 at cost5 for14 units.'}],'posting_permitted':True,'evidence_level':'authored-synthetic','view_ref':view})
 journal=add('JournalProposal','journal.purchase',{'basis_ref':basis,'authorization_ref':authorization,'lines':[{'account':'inventory','signed_amount':rat(70)},{'account':'payables','signed_amount':rat(-70)}],'cash_class':None})
 changes={k:rat(0) for k in ACCOUNTS};changes.update(inventory=rat(70),payables=rat(-70))
 delta=add('EconomicDelta','delta.purchase',{'basis_ref':basis,'authorization_ref':authorization,'account_changes':changes,'inventory_units_before':rat(6),'inventory_units_after':rat(20)})
 closing=deepcopy(body(state0));closing['sequence']=1;closing['balances']['inventory']=rat(100);closing['balances']['payables']=rat(-90);closing['inventory_units']=rat(20)
 state1=add('CompanyState','state.purchase',closing)
 exchange('authorize-purchase','accounting.authorize@1',{'basis_ref':basis,'posting_profile_ref':profile},[authorization])
 exchange('propose-purchase','accounting.propose@1',{'authorization_ref':authorization,'basis_ref':basis,'method_ref':method},[journal,delta])
 args={'basis_ref':basis,'authorization_ref':authorization,'journal_ref':journal,'delta_ref':delta}
 head={'owner_key':'Northstar/DemoCorporate/historical','state_ref':state0,'generation':0}
 req,sub=request('commit-purchase','accounting.commit@1',args,head=head)
 receipt=add('StateTransitionReceipt','receipt.purchase',{'request_ref':req,'identity':identity,'basis_ref':basis,'authorization_ref':authorization,'journal_ref':journal,'delta_ref':delta,'opening_ref':state0,'closing_ref':state1,'generation':1,'status':'committed'})
 committed=result('commit-purchase',req,sub,[receipt],receipt=receipt,commit=True)
 def closure(roots):
  found=set()
  def visit(r):
   if r['digest'] in found:return
   found.add(r['digest'])
   for d in REG[r['digest']]['dependencies']:visit(d)
  for r in roots:visit(r)
  return sorted(found)
 import0=add('ImportState','import.empty',{'namespace':'Northstar-import-candidate','manifest_refs':[],'generation':0})
 initial={'head':head,'events':[],'journals':[],'deltas':[],'receipts':[],'published_records':closure([state0,view,import0,work0,old_selection,old_profit,old_equity]),'review_head':{'owner_key':'review/Northstar','state_ref':view,'generation':1},'review_receipts':[],'import_head':{'owner_key':'import/Northstar-import-candidate','state_ref':import0,'generation':0},'import_receipts':[],'import_records':[],'work_head':workhead,'work_receipts':[],'model_head':{'owner_key':'model/Northstar','state_ref':family,'generation':0}}
 initial['published_records']=sorted(set(initial['published_records'])|set(closure([family])))
 after=deepcopy(initial);after.update(head={'owner_key':head['owner_key'],'state_ref':state1,'generation':1},events=[{'identity':identity,'request_ref':req,'receipt_ref':receipt}],journals=[journal],deltas=[delta],receipts=[receipt],published_records=sorted(set(initial['published_records'])|set(closure([receipt]))))
 EXCHANGES.append({'id':'commit-purchase','request_ref':req,'submission_ref':sub,'response_ref':committed,'world_before':initial,'world_after':after,'evidence_mode':'specification_example'})
 replay=result('replay-purchase',req,sub,[receipt],disposition='replayed',receipt=receipt)
 EXCHANGES.append({'id':'replay-purchase','request_ref':req,'submission_ref':sub,'response_ref':replay,'world_before':after,'world_after':after,'evidence_mode':'specification_example'})
 for key,budget,bad in [('changed-request-id',1000,False),('changed-budget',999,False),('balanced-wrong-quantity',1000,True)]:
  a=deepcopy(args)
  if bad:
   wrong=deepcopy(body(delta));wrong['inventory_units_after']=rat(21)
   a['delta_ref']=add('EconomicDelta','delta.wrong',wrong)
  nr,ns=request(key,'accounting.commit@1',a,head=head,budget=budget)
  valid=not bad
  rr=result(key,nr,ns,disposition='rejected',validated=valid,code='ECONOMIC_DELTA_MISMATCH' if bad else 'EVENT_ID_CONFLICT')
  EXCHANGES.append({'id':key,'request_ref':nr,'submission_ref':ns,'response_ref':rr,'world_before':after,'world_after':after,'evidence_mode':'specification_example'})
 # Stale head for a different economic event with individually coherent bindings.
 fresh_event=deepcopy(body(event));fresh_event['business_event_id']='2024H1.purchase.other'
 e2=add('EconomicEvent','event.other',fresh_event)
 b2=deepcopy(body(basis));b2['event_ref']=e2;b2['identity']={**identity,'business_event_id':fresh_event['business_event_id']}
 b2=add('AccountingEventBasis','basis.other',b2)
 au2=deepcopy(body(authorization));au2['basis_ref']=b2;au2=add('PostingAuthorization','authorization.other',au2)
 j2=deepcopy(body(journal));j2.update(basis_ref=b2,authorization_ref=au2);j2=add('JournalProposal','journal.other',j2)
 d2=deepcopy(body(delta));d2.update(basis_ref=b2,authorization_ref=au2);d2=add('EconomicDelta','delta.other',d2)
 nr,ns=request('stale-new-event','accounting.commit@1',{'basis_ref':b2,'authorization_ref':au2,'journal_ref':j2,'delta_ref':d2},head=head)
 rr=result('stale-new-event',nr,ns,disposition='rejected',code='STALE_OPENING_STATE')
 EXCHANGES.append({'id':'stale-new-event','request_ref':nr,'submission_ref':ns,'response_ref':rr,'world_before':after,'world_after':after,'evidence_mode':'specification_example'})
 observation=add('TransportObservation','lost-acknowledgement',{'submission_ref':sub,'request_ref':req,'observation':'acknowledgement_timeout','commit_observation':'unknown','receipt_ref':None,'next_action':'resubmit_exact_original_request'})
 for key,before,ending,response in [('retry-precommit',initial,after,committed),('retry-postcommit',after,after,replay)]:
  EXCHANGES.append({'id':key,'request_ref':req,'submission_ref':sub,'response_ref':response,'world_before':before,'world_after':ending,'prior_transport_observation_ref':observation,'received_response_before_retry':None,'evidence_mode':'specification_example'})
 # Same receipt can replay after a later head: lookup must precede freshness.
 # Explicit recovery-only extra purchase, with its complete intervening receipt.
 evnext=add('EconomicEvent','event.recovery-extra',{**body(event),'business_event_id':'recovery.extra-purchase','sequence':2})
 nextid={**identity,'business_event_id':'recovery.extra-purchase'}
 bnext=add('AccountingEventBasis','basis.recovery-extra',{**body(basis),'identity':nextid,'event_ref':evnext,'opening_ref':state1})
 anext=add('PostingAuthorization','authorization.recovery-extra',{**body(authorization),'basis_ref':bnext})
 jnext=add('JournalProposal','journal.recovery-extra',{**body(journal),'basis_ref':bnext,'authorization_ref':anext})
 dnext=add('EconomicDelta','delta.recovery-extra',{**body(delta),'basis_ref':bnext,'authorization_ref':anext,'inventory_units_before':rat(20),'inventory_units_after':rat(34)})
 stnext=deepcopy(body(state1));stnext.update(sequence=2,inventory_units=rat(34));stnext['balances'].update(inventory=rat(170),payables=rat(-160))
 state2=add('CompanyState','state.recovery-extra',stnext)
 nr,ns=request('commit-intervening-purchase','accounting.commit@1',{'basis_ref':bnext,'authorization_ref':anext,'journal_ref':jnext,'delta_ref':dnext},head=after['head'])
 nextreceipt=add('StateTransitionReceipt','receipt.recovery-extra',{'request_ref':nr,'identity':nextid,'basis_ref':bnext,'authorization_ref':anext,'journal_ref':jnext,'delta_ref':dnext,'opening_ref':state1,'closing_ref':state2,'generation':2,'status':'committed'})
 nextresult=result('commit-intervening-purchase',nr,ns,[nextreceipt],receipt=nextreceipt,commit=True)
 advanced=deepcopy(after);advanced.update(head={**head,'state_ref':state2,'generation':2},events=after['events']+[{'identity':nextid,'request_ref':nr,'receipt_ref':nextreceipt}],journals=after['journals']+[jnext],deltas=after['deltas']+[dnext],receipts=after['receipts']+[nextreceipt],published_records=sorted(set(after['published_records'])|set(closure([nextreceipt]))))
 EXCHANGES.append({'id':'commit-intervening-purchase','request_ref':nr,'submission_ref':ns,'response_ref':nextresult,'world_before':after,'world_after':advanced,'evidence_mode':'specification_example'})
 EXCHANGES.append({'id':'replay-after-head-advance','request_ref':req,'submission_ref':sub,'response_ref':replay,'world_before':advanced,'world_after':advanced,'evidence_mode':'specification_example'})
 # Read/candidate outputs leave the book immutable. Review changes only its owner.
 for ex in EXCHANGES:
  if ex['world_before'] is None:ex['world_before']=deepcopy(initial);ex['world_after']=deepcopy(initial)
  elif set(ex['world_before'])=={'review_head'}:
   before=deepcopy(initial);before['review_head']=ex['world_before']['review_head'];ending=deepcopy(before);ending['review_head']=ex['world_after']['review_head']
   rr=body(ex['response_ref'])['receipt_ref'];ending['review_receipts']=[rr];ending['published_records']=sorted(set(initial['published_records'])|set(closure(body(ex['response_ref'])['payload']['result_refs'])))
   ex['world_before']=before;ex['world_after']=ending
  elif set(ex['world_before'])=={'work_head','work_receipts'}:
   pair=[]
   for side in ['world_before','world_after']:
    w=deepcopy(initial);w.update(ex[side]);w['published_records']=sorted(set(initial['published_records'])|set(closure([w['work_head']['state_ref']]+w['work_receipts'])))
    pair.append(w)
   ex['world_before'],ex['world_after']=pair
  if ex['id'] in ['stale-current-report','frozen-explain']:
   ex['world_before']['review_head']={'owner_key':'review/Northstar','state_ref':nextview,'generation':2}
   ex['world_before']['published_records']=sorted(set(ex['world_before']['published_records'])|set(closure([nextview])))
   ex['world_after']=deepcopy(ex['world_before'])
 # Export and import are lossless documentary exchanges with exact required bytes.
 roots=[family,projections[0],receipt];digests=closure(roots)
 records=[{'kind':REG[d]['kind'],'schema':REG[d]['schema'],'digest':d} for d in digests]
 required={}
 def blobs_in(x):
  if isinstance(x,dict):
   if x.get('kind')=='blob':required[x['digest']]=x
   else:
    for child in x.values():blobs_in(child)
  elif isinstance(x,list):
   for child in x:blobs_in(child)
 for d in digests:blobs_in(REG[d])
 manifest=add('ExportManifest','export.manifest',{'root_refs':roots,'record_refs':records,'required_blobs':[required[d] for d in sorted(required)],'complete':True,'financial_admission':False})
 exchange('export-closure','store.export@1',{'root_refs':roots,'format':'accdsl.portable.v1','destination':'fixture_export'},[manifest])
 ir,isu=request('import-closure','store.import@1',{'manifest_ref':manifest,'target_namespace':'Northstar-import-candidate'},head=initial['import_head'])
 import1=add('ImportState','import.populated',{'namespace':'Northstar-import-candidate','manifest_refs':[manifest],'generation':1})
 imp=add('ImportReceipt','import.receipt',{'request_ref':ir,'manifest_ref':manifest,'opening_ref':import0,'closing_ref':import1,'original_to_local':[{'original_ref':r,'local_ref':r} for r in records],'financial_admission':False})
 imported=deepcopy(initial);imported.update(import_head={**initial['import_head'],'state_ref':import1,'generation':1},import_receipts=[imp],import_records=records,published_records=sorted(set(initial['published_records'])|set(closure([imp]))))
 irsp=result('import-closure',ir,isu,[imp],receipt=imp,commit=True)
 EXCHANGES.append({'id':'import-closure','request_ref':ir,'submission_ref':isu,'response_ref':irsp,'world_before':initial,'world_after':imported,'evidence_mode':'specification_example'})
 expected_blob=body(facts)['source_blob']
 corrupt_blob=bytes_blob('corrupted-import-input.bin',b'corrupted source bytes, retained as received\n')
 corrupt_result=result('import-corrupt-blob',ir,isu,disposition='rejected',validated=False,code='REQUIRED_BLOB_DIGEST_MISMATCH',stage='reference_integrity')
 EXCHANGES.append({'id':'import-corrupt-blob','request_ref':ir,'submission_ref':isu,'response_ref':corrupt_result,'world_before':initial,'world_after':deepcopy(initial),'supplied_blob_overrides':[{'expected_blob':expected_blob,'received_blob':corrupt_blob}],'evidence_mode':'specification_example'})
 for ex in EXCHANGES:
  if ex['world_before'] is None:ex['world_before']=deepcopy(initial);ex['world_after']=deepcopy(initial)

if __name__=='__main__':main()
