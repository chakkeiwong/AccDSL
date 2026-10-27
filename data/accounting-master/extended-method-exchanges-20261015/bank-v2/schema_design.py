"""Closed documentary bank types. No accounting endpoint is implemented."""
from copy import deepcopy
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
PREFIX = 'accdsl.bank-components-v2.'

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

from bank_types import ASSETS, LIABILITIES, PROFIT, OCI, EQUITY, ACCOUNTS, CASH, OCI_MOVEMENTS, EQUITY_MOVEMENTS, COMPONENTS, EVENTS

def remap(v):
    if isinstance(v,str): return v.replace('accdsl.corporate.',PREFIX)
    if isinstance(v,dict): return {k:remap(x) for k,x in v.items()}
    if isinstance(v,list): return [remap(x) for x in v]
    return v

def schemas():
    base=json.loads((ROOT/'data/accounting-master/corporate-portable-20261015/record-schemas.json').read_text())['$defs']
    s={k:remap(deepcopy(base[k])) for k in ['SchemaLock','OperationSignature','Environment','Decoder','Submission','OperationResult','TransportObservation']}
    s['Profile']=obj({'profile_id':{'const':'BankComponents/2'},'schema_lock_ref':ref('SchemaLock'),
       'operations':arr(ID,1),'book_mode':{'const':'synthetic'},'execution_mode':{'const':'specification_example'},
       'interest_cash_policy':{'const':'contractual_interest_operating_and_complex_transfers_unclassified'}})
    s['Context']=obj({'entity_id':ID,'book_id':ID,'branch_key':ID,'currency':enum('USD'),
       'basis':enum('historical_AU_AASB_conditional'),
       'issuer_class':{'const':'for_profit'},'calendar':{'const':'dated_synthetic'}})
    s['SourceSupport']=obj({'source_pdf':BLOB,'source_text':BLOB,'method_text':BLOB,'inspection_note':BLOB,
       'anchors':arr(TXT,1),'authority_scope':{'const':'historical_not_current_admission'},
       'family':enum('AU_AASB'),'period_start_inclusive':maybe(DATE),'period_start_exclusive':maybe(DATE)})
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
       'currency':enum('USD'),'lines':arr(obj({'account':enum(*ACCOUNTS),'signed_amount':Q}))})
    s['EconomicDelta']=obj({'basis_ref':ref('AccountingEventBasis'),'opening_ref':ref('CompanyState'),
       'closing_ref':ref('CompanyState'),'cash_change':obj({k:Q for k in CASH})})
    s['StateTransitionReceipt']=obj({**{k:ref(v) for k,v in [('request_ref','OperationRequest'),('basis_ref','AccountingEventBasis'),
       ('authorization_ref','PostingAuthorization'),('journal_ref','JournalProposal'),('delta_ref','EconomicDelta'),
       ('opening_ref','CompanyState'),('closing_ref','CompanyState')]},'generation':INT,'status':{'const':'committed'}})
    s['Report']=obj({'opening_ref':ref('CompanyState'),'state_ref':ref('CompanyState'),'view_ref':ref('View'),
       'period_start':DATE,'period_end_exclusive':DATE,'receipt_refs':arr(ref('StateTransitionReceipt')),
       'currency':enum('USD'),'values':obj({k:Q for k in ['cash','assets','liabilities','equity','profit','oci',*CASH]}),
       'cash_receipts':obj({k:Q for k in CASH}),'cash_payments':obj({k:Q for k in CASH}),'interest_paid':Q,'interest_received':Q,'cash_classification':enum('complete','unresolved'),
       'income_statement':obj({k:Q for k in PROFIT}),'oci_components':obj({k:Q for k in OCI_MOVEMENTS}),
       'other_equity_movements':obj({k:Q for k in EQUITY_MOVEMENTS}),
       'tax_status':{'const':'uncomputed'},'complete_company_after_tax':{'const':False}})
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
