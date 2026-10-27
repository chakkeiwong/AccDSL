"""Closed documentary financing types. No accounting endpoint is implemented."""
from copy import deepcopy
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
PREFIX = 'accdsl.financing-residuals.'

def sid(kind):
    return {'OperationRequest':'accdsl.operation.request.v1',
            'OperationResult':'accdsl.operation.result.v1'}.get(kind, PREFIX+kind.lower()+'.v1')
def obj(fields): return {'type':'object','properties':fields,'required':list(fields),'additionalProperties':False}
def arr(item, n=0): return {'type':'array','items':item,'minItems':n}
def enum(*values): return {'enum':list(values)}
def maybe(v): return {'anyOf':[v,{'type':'null'}]}
ID = {'type':'string','pattern':'^[A-Za-z0-9_.:@/-]+$'}
TXT = {'type':'string','minLength':1}
INT = {'type':'integer','minimum':0}
BOOL = {'type':'boolean'}
DATE = {'type':'string','format':'date'}
Q = obj({'n':{'type':'string','pattern':'^(0|-?[1-9][0-9]*)$'},'d':{'type':'string','pattern':'^[1-9][0-9]*$'}})
DIGEST = {'type':'string','pattern':'^[0-9a-f]{64}$'}
BLOB = obj({'kind':{'const':'blob'},'algorithm':{'const':'sha256'},'digest':DIGEST,'byte_length':INT})
def ref(kind=None):
    return obj({'kind':{'const':kind} if kind else ID,'schema':{'const':sid(kind)} if kind else ID,'digest':DIGEST})
def quantities(*names): return {name:Q for name in names}

ASSETS = ['cash','inventory']
LIABILITIES = ['debt','bonus_payable','award_liability']
PROFIT = ['revenue','other_gains','service_expense','award_expense','inducement_expense','hedge_expense','finance_expense','cost_of_sales']
OCI = ['cf_reserve','intrinsic_reserve','cost_reserve']
EQUITY = ['capital','retained','original_equity','equity_pending','award_equity']
ACCOUNTS = ASSETS+LIABILITIES+PROFIT+OCI+EQUITY+['derivative']
CASH = ['operating','investing','financing','unclassified']
OCI_MOVEMENTS = ['cash_flow','intrinsic','cost']
EQUITY_MOVEMENTS = ['issue','award','basis_transfer']

COMPONENTS = {
 'amendment':obj({'instrument_id':ID,'consideration':enum('shares','cash_bonus'),
    **quantities('old_shares','new_shares','debt','bonus','bonus_due','equity_pending','issued'),
    'announcement_date':DATE,'binding_date':DATE,'delivery_date':DATE,
    'announced':BOOL,'bound':BOOL,'delivered':BOOL,'bonus_paid':BOOL}),
 'award':obj({'grant_id':ID,'settlement':enum('equity','cash'),
    **quantities('quantity','grant_fv','original_cost','incremental_total','incremental_cost','award_equity','liability'),
    'total_years':INT,'elapsed':INT,'modification_elapsed':maybe(INT),'incremental_end':maybe(INT),
    'modified':BOOL,'all_original_vest':BOOL,'service_dates':arr(DATE,1)}),
 'cashflow':obj({'designation_id':ID,'purpose':enum('inventory','interest'),
    **quantities('D','E','I','derivative','settled_total','reserve','inventory','interest_paid'),
    'active':BOOL,'expected':BOOL,'bought':BOOL,'basis_done':BOOL,'sold':BOOL}),
 'option':obj({'designation_id':ID,'route':enum('transaction','time_period'),
    **quantities('initial_actual','initial_aligned','intrinsic','time_value','aligned_time_value',
       'effective_intrinsic','related_cost','mismatch_profit','intrinsic_reserve','cost_reserve',
       'derivative','amortized','inventory'),
    'periods':INT,'elapsed':INT,'protection_dates':arr(DATE),'bought':BOOL,'settled':BOOL,'inventory_bought':BOOL,
    'basis_done':BOOL,'sold':BOOL,'active':BOOL,'zero_cost_collar':BOOL}),
 'rebalancing':obj({'designation_id':ID,**quantities('D','E','I','derivative','reserve','retained_fraction','layer_gain'),
    'revision':INT,'last_measurement_date':maybe(DATE),'prospective_measured':BOOL,
    'layers':arr(obj({'layer_id':ID,'quantity':Q,'reference_price':Q,'designation_date':DATE}),1)}),
 'nethedge':obj({'designation_id':ID,'sales_id':ID,'service_id':ID,
    'exposure_currency':{'const':'USD'},'functional_currency':{'const':'EUR'},
    **quantities('sales_usd','service_usd','initial_spot','execution_spot','derivative','reserve',
       'gross_revenue','gross_service','hedge_expense'),
    'sales_period':INT,'service_period':INT,'designated':BOOL,'measured':BOOL,
    'sales_done':BOOL,'service_done':BOOL,'settled':BOOL,'external_items':BOOL,
    'rolling_strategy':BOOL,'changing_net_size':BOOL,'normal_instrument_use':BOOL,'inconsistent_recognition':BOOL}),
}
EVENTS = {
 'amendment.announce':('amendment',obj({'rights_changed':BOOL})),
 'amendment.bind':('amendment',obj({'quote':maybe(Q),'quote_date':DATE,'legal_discharge':BOOL,
    'equity_qualified':BOOL,'cash_alternative':BOOL,'conditions_resolved':BOOL})),
 'amendment.deliver':('amendment',obj({'shares':Q})),
 'amendment.pay_bonus':('amendment',obj({'amount':Q})),
 'award.service':('award',obj({'elapsed':INT})),
 'award.modify':('award',obj({'kind':enum('repricing','added_instruments'),
    'before_fv':maybe(Q),'after_fv':maybe(Q),'added_quantity':Q,'incremental_end':INT,
    'original_conditions_unchanged':BOOL})),
 'award.cash_to_equity':('award',obj({'remeasured_liability':maybe(Q),'replacement_fv':maybe(Q),
    'modified_total_years':INT,'replacement_identified':BOOL})),
 'cashflow.measure':('cashflow',obj({'D':maybe(Q),'H':maybe(Q),'eligibility_known':BOOL})),
 'cashflow.settle':('cashflow',obj({'amount':Q})),
 'cashflow.purchase':('cashflow',obj({'amount':Q})),
 'cashflow.basis_transfer':('cashflow',obj({'reserve_origin':ID})),
 'cashflow.sell':('cashflow',obj({'proceeds':Q})),
 'cashflow.pay_interest':('cashflow',obj({'amount':Q})),
 'cashflow.release':('cashflow',obj({'reserve_origin':ID,'reason':enum('interest_earned','no_longer_expected')})),
 'cashflow.discontinue':('cashflow',obj({'still_expected':BOOL})),
 'option.buy':('option',obj({'premium':Q})),
 'option.measure':('option',obj({'intrinsic':maybe(Q),'time_value':maybe(Q),'aligned_time_value':maybe(Q),'H':maybe(Q)})),
 'option.settle':('option',obj({'amount':Q})),
 'option.purchase':('option',obj({'amount':Q})),
 'option.basis_transfer':('option',obj({'intrinsic_origin':ID,'cost_origin':ID})),
 'option.sell':('option',obj({'proceeds':Q})),
 'option.amortize':('option',obj({'elapsed':INT,'rational_even_allocation_admitted':BOOL})),
 'option.discontinue':('option',obj({'relationship_ended':BOOL})),
 'rebalancing.measure':('rebalancing',obj({'D':Q,'H':Q})),
 'rebalancing.change':('rebalancing',obj({'retained_fraction':Q,'objective_unchanged':BOOL,
    'documentation_updated':BOOL,'added_layer':maybe(obj({'layer_id':ID,'quantity':Q,'reference_price':Q,'designation_date':DATE}))})),
 'rebalancing.layers':('rebalancing',obj({'current_price':Q,'zero_discount_admitted':BOOL})),
 'rebalancing.prospective_measure':('rebalancing',obj({'total_D':Q,'item_change_since_rebalance':Q})),
 'nethedge.designate':('nethedge',obj({'individually_eligible':BOOL,'highly_probable':BOOL,
    'actual_net_management':BOOL,'documented_periods':BOOL,'effectiveness_admitted':BOOL})),
 'nethedge.measure':('nethedge',obj({'spot':Q,'zero_discount_forward_credit_effects':BOOL})),
 'nethedge.sale':('nethedge',obj({'spot':Q,'recognition_period':INT})),
 'nethedge.service':('nethedge',obj({'spot':Q,'recognition_period':INT})),
 'nethedge.settle':('nethedge',obj({'amount':Q})),
}

from residual_schema import extend
extend(globals())

def remap(v):
    if isinstance(v,str): return v.replace('accdsl.corporate.',PREFIX)
    if isinstance(v,dict): return {k:remap(x) for k,x in v.items()}
    if isinstance(v,list): return [remap(x) for x in v]
    return v

def schemas():
    base=json.loads((ROOT/'data/accounting-master/corporate-portable-20261015/record-schemas.json').read_text())['$defs']
    s={k:remap(deepcopy(base[k])) for k in ['SchemaLock','OperationSignature','Environment','Decoder','Submission','OperationResult','TransportObservation']}
    s['Profile']=obj({'profile_id':{'const':'FinancingComponents/2'},'schema_lock_ref':ref('SchemaLock'),
       'operations':arr(ID,1),'book_mode':{'const':'synthetic'},'execution_mode':{'const':'specification_example'},
       'interest_cash_policy':{'const':'historical_IAS7_operating_election'}})
    s['Context']=obj({'entity_id':ID,'book_id':ID,'branch_key':ID,'currency':enum('USD','EUR'),
       'basis':enum('historical_EU_IFRS_conditional','historical_AU_AASB_conditional'),
       'issuer_class':{'const':'for_profit'},'calendar':{'const':'dated_synthetic'}})
    s['SourceSupport']=obj({'source_pdf':BLOB,'source_text':BLOB,'method_text':BLOB,'inspection_note':BLOB,
       'anchors':arr(TXT,1),'authority_scope':{'const':'historical_not_current_admission'},
       'family':enum('EU_IFRS','AU_AASB'),'period_start_inclusive':maybe(DATE),'period_start_exclusive':maybe(DATE)})
    s['Authority']=obj({'source_ref':ref('SourceSupport'),'supporting_source_refs':arr(ref('SourceSupport')),
       'context_ref':ref('Context'),'start_inclusive':INT,'end_exclusive':INT,'evidence_class':{'const':'synthetic_conditional_admission'}})
    s['View']=obj({'source_refs':arr(ref('SourceSupport'),1),'revision':INT,'supersedes_ref':maybe(ref('View')),
       'information_mode':enum('archival_synthetic','historical_investor')})
    s['MethodDefinition']=obj({'method_id':enum(*EVENTS),'component_kind':enum(*COMPONENTS),
       'method_status':{'const':'specified_finite'},'source_ref':ref('SourceSupport'),
       'supporting_source_refs':arr(ref('SourceSupport')),'contract_blob':BLOB,'profile_ref':ref('Profile')})
    s['ComponentState']={'oneOf':[obj({'tag':{'const':k},'value':v}) for k,v in COMPONENTS.items()]}
    s['EconomicEvent']={'oneOf':[obj({'method_id':{'const':k},'context_ref':ref('Context'),'instant':INT,
       'event_date':DATE,'reporting_period_start':DATE,'reporting_period_end_exclusive':DATE,'parameters':v}) for k,(_,v) in EVENTS.items()]}
    s['CompanyState']=obj({'context_ref':ref('Context'),'view_ref':ref('View'),'sequence':INT,'instant':INT,'as_of_date':DATE,
       'component_ref':ref('ComponentState'),'balances':obj({k:Q for k in ACCOUNTS}),
       'cash_movements':obj({k:Q for k in CASH}),'cash_receipts':obj({k:Q for k in CASH}),'cash_payments':obj({k:Q for k in CASH}),
       'oci_movements':obj({k:Q for k in OCI_MOVEMENTS}),
       'equity_movements':obj({k:Q for k in EQUITY_MOVEMENTS}),'tax_status':{'const':'uncomputed'}})
    s['AccountingEventBasis']=obj({'identity':obj({k:ID for k in ['entity_id','book_id','branch_key','business_event_id']}),
       **{k:ref(v) for k,v in [('opening_ref','CompanyState'),('event_ref','EconomicEvent'),('method_ref','MethodDefinition'),
       ('authority_ref','Authority'),('view_ref','View'),('context_ref','Context')]}})
    s['Admission']=obj({'basis_ref':ref('AccountingEventBasis'),'source_ref':ref('SourceSupport'),'context_ref':ref('Context'),
       'instant':INT,'status':enum('eligible','unresolved','ineligible'),'fact_basis':{'const':'authored_synthetic'},
       'findings':arr(obj({'name':ID,'status':enum('satisfied','unknown','failed'),'support_ref':ref()}),1)})
    s['PostingAuthorization']=obj({'basis_ref':ref('AccountingEventBasis'),'admission_ref':ref('Admission'),'view_ref':ref('View'),'posting_permitted':BOOL})
    s['JournalProposal']=obj({'basis_ref':ref('AccountingEventBasis'),'mode':enum('monetary','state_only'),
       'currency':enum('USD','EUR'),'lines':arr(obj({'account':enum(*ACCOUNTS),'signed_amount':Q}))})
    s['EconomicDelta']=obj({'basis_ref':ref('AccountingEventBasis'),'opening_ref':ref('CompanyState'),
       'closing_ref':ref('CompanyState'),'cash_change':obj({k:Q for k in CASH})})
    s['StateTransitionReceipt']=obj({**{k:ref(v) for k,v in [('request_ref','OperationRequest'),('basis_ref','AccountingEventBasis'),
       ('authorization_ref','PostingAuthorization'),('journal_ref','JournalProposal'),('delta_ref','EconomicDelta'),
       ('opening_ref','CompanyState'),('closing_ref','CompanyState')]},'generation':INT,'status':{'const':'committed'}})
    s['Report']=obj({'opening_ref':ref('CompanyState'),'state_ref':ref('CompanyState'),'view_ref':ref('View'),
       'period_start':DATE,'period_end_exclusive':DATE,'receipt_refs':arr(ref('StateTransitionReceipt')),
       'currency':enum('USD','EUR'),'values':obj({k:Q for k in ['cash','assets','liabilities','equity','profit','oci',*CASH]}),
       'cash_receipts':obj({k:Q for k in CASH}),'cash_payments':obj({k:Q for k in CASH}),'interest_paid':Q,
       'income_statement':obj({k:Q for k in PROFIT}),'oci_components':obj({k:Q for k in OCI_MOVEMENTS}),
       'other_equity_movements':obj({k:Q for k in EQUITY_MOVEMENTS}),
       'tax_status':{'const':'uncomputed'},'complete_company_after_tax':{'const':False},
       'eps_quantity':maybe(EPS_QUANTITY)})
    s['Obligation']=obj({'code':ID,'required_input':TXT,'basis_ref':ref('AccountingEventBasis')})
    s['Domain']=obj({'request_ref':ref('OperationRequest'),'meaning':{'const':'singleton_request_decision'}})
    s['Region']=obj({'domain_ref':ref('Domain'),'predicate':{'const':'this_request'}})
    args={'accounting.authorize@1':obj({'basis_ref':ref('AccountingEventBasis')}),
       'accounting.propose@1':obj({'basis_ref':ref('AccountingEventBasis'),'authorization_ref':ref('PostingAuthorization')}),
       'accounting.commit@1':obj({k:ref(v) for k,v in [('basis_ref','AccountingEventBasis'),('authorization_ref','PostingAuthorization'),
          ('journal_ref','JournalProposal'),('delta_ref','EconomicDelta')]}),
       'report.build@1':obj({'opening_ref':ref('CompanyState'),'state_ref':ref('CompanyState'),'view_ref':ref('View'),
          'period_start':DATE,'period_end_exclusive':DATE,'receipt_refs':arr(ref('StateTransitionReceipt')),'require_current':BOOL})}
    s['OperationRequest']=remap(deepcopy(base['OperationRequest']))
    s['OperationRequest']['properties']['operation']=enum(*args)
    s['OperationRequest']['properties']['arguments']={'oneOf':[obj({'tag':{'const':k},'value':v}) for k,v in args.items()]}
    for op,spec in args.items(): s['Arguments.'+op]=spec
    return {'$schema':'https://json-schema.org/draft/2020-12/schema','schema_ids':{k:sid(k) for k in s},'$defs':s}
