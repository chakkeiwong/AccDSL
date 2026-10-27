"""Closed InsuranceComponents/1 wire schema, distinct from all old profiles."""
PREFIX='accdsl.insurance-components.'
ROLES=('issued','replacement','held','accounts')
OPS=('insurance.components.commit@1','insurance.components.report@1')
def sid(k): return PREFIX+k.lower()+'.v1'
def obj(p): return dict(type='object',properties=p,required=list(p),additionalProperties=False)
def arr(s,n=0): return dict(type='array',items=s,minItems=n)
def enum(*v): return dict(enum=list(v))
def const(v): return dict(const=v)
def maybe(v): return dict(anyOf=[v,dict(type='null')])
ID=dict(type='string',pattern='^[A-Za-z0-9_.:@/-]+$')
DATE=dict(type='string',format='date')
STAMP=dict(type='string',format='date-time')
INT=dict(type='integer',minimum=0)
BOOL=dict(type='boolean')
DIGEST=dict(type='string',pattern='^[0-9a-f]{64}$')
Q=obj(dict(n=dict(type='string',pattern='^(0|-?[1-9][0-9]*)$'),d=dict(type='string',pattern='^[1-9][0-9]*$')))
BLOB=obj(dict(kind=const('blob'),algorithm=const('sha256'),digest=DIGEST,byte_length=INT))
def ref(k): return obj(dict(kind=const(k),schema=const(sid(k)),digest=DIGEST))
HEADS=obj({r:ref('OwnerState') for r in ROLES})
ISSUED=obj(dict(model=enum('none','GMM','PAA','VFA'),**{k:Q for k in 'fcf ra csm loss acquisition_asset acquisition_gross lrc lic remaining_units investment allocation_carrying allocated_oci paa_cost_remaining unearned_premium'.split()}))
HELD=obj({k:Q for k in 'fcf_asset cost_csm loss_recovery'.split()})
ACCOUNTS=obj({k:Q for k in 'cash underlying derivative equity profit oci revenue service_expense finance held_result'.split()})
def inputs():
    v={}; add=lambda name,p:v.update({name+'@1':p})
    member=obj(dict(contract_id=ID,portfolio_id=ID,cohort=ID,profitability=enum('onerous','no_significant_risk','other'),contract_role=enum('issued','held')))
    add('grouping.assess',dict(group_id=ID,portfolio_id=ID,cohort=ID,profitability=enum('onerous','no_significant_risk','other'),contract_role=enum('issued','held'),membership=enum('admitted','unknown'),contracts=arr(member,1)))
    add('acquisition.allocate',dict(paid=Q,target_group=ID,allocations=arr(obj(dict(allocation_id=ID,group_id=ID,amount=Q)),1)))
    add('acquisition.recoverability',dict(recoverable=Q))
    add('gmm.recognize',dict(premium=Q,claims=Q,ra=Q,units=Q))
    add('gmm.future',dict(fcf_change=Q))
    add('gmm.service',dict(owner=enum('issued','replacement'),units=Q,expected_claims=Q,ra_release=Q,actual_claims=Q))
    add('reinsurance.recognize',dict(entry_date=DATE,recognition_date=DATE,coverage_start=DATE,underlying_recognition=DATE,share=Q,covered_loss=Q,covered_claims=Q,premium=Q,transferred_ra=Q,covered_group=ID,issued_group=ID,coverage_mapping=enum('admitted','unknown'),allocations=arr(obj(dict(contract_id=ID,covered=BOOL,premium=Q,claims=Q,ra=Q)),1)))
    add('reinsurance.change',dict(cause=enum('covered_claim_estimate','financial','new_terms'),issued_csm_treatment=enum('loss_reversal','csm'),old_covered_claims=Q,new_covered_claims=Q,new_covered_loss=Q,share=Q))
    add('reinsurance.nonperformance',dict(loss=Q))
    add('reinsurance.settle',dict(claims=Q,recovery=Q,transferred_ra=Q))
    removed=dict(removed_fcf=Q,removed_ra=Q,removed_units=Q)
    add('modification.replace',dict(**removed,equivalent_premium=maybe(Q),actual_extra=Q,new_fcf=Q,new_ra=Q,new_units=Q,modification_test=enum('derecognize','estimate_change','unknown'),existing_right=BOOL))
    add('contract.transfer',dict(**removed,third_party_premium=Q))
    add('paa.recognize',dict(premium=Q,acquisition_paid=Q,coverage_years=Q,eligibility=enum('admitted','unknown'),expense_election=BOOL,units=Q))
    add('paa.service',dict(units=Q))
    add('paa.onerous',dict(remaining_fcf=Q,facts_indicate_onerous=BOOL))
    rate=dict(rate_origin=enum('claim_incurrence','inception'),rate_date=DATE,claim_date=DATE)
    add('paa.claim',dict(**rate,payment=Q,years=Q,incurrence_rate=Q,ra=Q))
    add('paa.finance',dict(**rate,payment=Q,incurrence_rate=Q,current_rate=Q,remaining_years=Q,ra_release=Q))
    add('paa.settle',dict(payment=Q))
    add('vfa.recognize',dict(premium=Q,pool=Q,policyholder_share=Q,claims=Q,ra=Q,units=Q,participation=enum('admitted','unknown'),insurance=enum('admitted','unknown'),role=enum('issued','held')))
    add('vfa.pool',dict(new_pool=Q,policyholder_share=Q,holding=enum('held','not_held'),finance_policy=enum('all_profit','held_matching_oci')))
    add('vfa.service',dict(units=Q,claims=Q,ra_release=Q))
    add('vfa.guarantee',dict(change=Q,derivative_gain=Q,change_kind=enum('financial_guarantee','nonfinancial'),mitigation=BOOL,strategy=enum('none','prior_documented','later_documented'),economic_offset=enum('admitted','unknown'),credit_not_dominant=enum('admitted','unknown')))
    add('vfa.settle',dict(investment_payment=Q))
    add('finance.variable',dict(payment=Q,allocation_rate=Q,current_rate=Q,remaining_years=Q,elapsed_years=Q,allocation_basis=enum('prospective_revised','initial_fixed')))
    return v
DETAILS={
 'grouping.assess':'member_count', 'acquisition.allocate':'allocated unallocated',
 'acquisition.recoverability':'asset impairment_expense','gmm.recognize':'transferred_acquisition initial_loss csm',
 'gmm.future':'loss_change profit_change csm','gmm.service':'revenue csm_release claims_expense',
 'reinsurance.recognize':'expected_recovery initial_loss_recovery held_asset',
 'reinsurance.change':'issued_loss_reversal held_expense recovery_cap',
 'reinsurance.nonperformance':'collectability_expense csm_change',
 'reinsurance.settle':'issued_profit held_result issued_revenue',
 'modification.replace':'deemed_or_transfer actual_cash_change old_csm loss',
 'contract.transfer':'deemed_or_transfer actual_cash_change old_csm loss',
 'paa.recognize':'lrc acquisition_expense cash_change','paa.service':'revenue acquisition_expense lrc',
 'paa.onerous':'additional_loss lrc','paa.claim':'claim_pv lic incurrence_rate',
 'paa.finance':'profit_finance_expense oci_income current_finance_expense ra_release lic',
 'paa.settle':'cash_paid revenue','vfa.recognize':'investment_component fcf csm',
 'vfa.pool':'asset_gain liability_finance_expense fee_to_csm investment_component',
 'vfa.service':'service_revenue csm_release profit investment_revenue',
 'vfa.guarantee':'csm loss derivative_gain profit_change',
 'vfa.settle':'investment_paid investment_revenue investment_expense',
 'finance.variable':'profit_finance_expense oci_income current_liability allocation_carrying'}
METHODS=tuple(inputs())
def schemas():
    s={}
    s['Context']=obj(dict(entity_id=ID,branch_id=ID,currency=const('USD'),unit=const('illustrative_million'),authority=const('historical_EU2023_IFRS17_scenario'),tax=const('uncomputed'),fx=const('none_supplied')))
    s['Evidence']=obj(dict(evidence_id=ID,context_ref=ref('Context'),available_at=STAMP,ingested_at=STAMP,content_blob=BLOB,provenance=const('synthetic_supplied')))
    s['View']=obj(dict(context_ref=ref('Context'),evidence_refs=arr(ref('Evidence'),1),decision_at=STAMP,system_asof=STAMP,revision=INT))
    s['SourceSupport']=obj(dict(source_id=const('EU2023-1803-IFRS17'),raw_blob=BLOB,text_blob=BLOB,method_blobs=arr(BLOB,1),anchors=arr(ID,1)))
    s['SchemaLock']=obj(dict(profile_id=const('InsuranceComponents/1'),schema_blob=BLOB,semantic_contract_blob=BLOB))
    s['Profile']=obj(dict(profile_id=const('InsuranceComponents/1'),schema_lock_ref=ref('SchemaLock'),operations=arr(enum(*OPS),2),execution_mode=const('specification_example')))
    s['OwnerState']={'oneOf':[obj(dict(context_ref=ref('Context'),role=const(r),owner_id=ID,group_id=ID,generation=INT,last_result_ref=maybe(ref('ComponentResult')),balances=t)) for r,t in zip(ROLES,(ISSUED,ISSUED,HELD,ACCOUNTS))]}
    s['MethodInput']={'oneOf':[obj(dict(method_id=const(m),**p)) for m,p in inputs().items()]}
    s['MethodBasis']=obj(dict(context_ref=ref('Context'),view_ref=ref('View'),source_ref=ref('SourceSupport'),input_ref=ref('MethodInput'),evidence_ref=ref('Evidence'),opening_heads=HEADS,method_anchor=ID,measurement_date=DATE))
    closing=obj(dict(issued=ISSUED,replacement=ISSUED,held=HELD,accounts=ACCOUNTS))
    lines=arr(obj(dict(account=enum('cash','underlying_asset','derivative_asset','issued_acquisition_asset','replacement_acquisition_asset','issued_liability','replacement_liability','held_asset','insurance_service_result','insurance_finance_result','reinsurance_result','oci'),signed_debit=Q)))
    variants=[]
    for name,fields in DETAILS.items():
        detail={k:Q for k in fields.split()}
        if name=='grouping.assess': detail.update(group_id=ID,contract_role=enum('issued','held'))
        for status in ('resolved','unresolved'):
            variants.append(obj(dict(basis_ref=ref('MethodBasis'),method_id=const(name+'@1'),status=const(status),diagnostics=arr(ID),closing=closing,detail=obj(detail if status=='resolved' else {}),journal=lines)))
    s['ComponentResult']={'oneOf':variants}
    s['Authorization']=obj(dict(basis_ref=ref('MethodBasis'),opening_heads=HEADS,authority=const('authored_documentary_admission')))
    s['Proposal']=obj(dict(basis_ref=ref('MethodBasis'),result_ref=ref('ComponentResult'),authorization_ref=ref('Authorization'),before_heads=HEADS,after_heads=HEADS))
    args={'oneOf':[obj(dict(proposal_ref=ref('Proposal'))),obj(dict(state_refs=HEADS))]}
    s['OperationRequest']=obj(dict(profile_ref=ref('Profile'),context_ref=ref('Context'),view_ref=ref('View'),client_id=ID,request_id=ID,operation=enum(*OPS),arguments=args,expected_heads=HEADS,require_current=BOOL))
    s['Submission']=obj(dict(request_ref=ref('OperationRequest'),wire_blob=BLOB,decoder=const('canonical_JSON_exact_rationals_v1')))
    s['ComponentReport']=obj(dict(context_ref=ref('Context'),state_refs=HEADS,scope=const('component_states_not_whole_company_statements'),tax_status=const('uncomputed')))
    s['Receipt']=obj(dict(request_ref=ref('OperationRequest'),output_ref={'oneOf':[ref('ComponentResult'),ref('ComponentReport')]},before_heads=HEADS,after_heads=HEADS,written_roles=arr(enum(*ROLES)),status=enum('committed','unresolved_published','report_published')))
    s['OperationResult']=obj(dict(request_ref=ref('OperationRequest'),submission_ref=ref('Submission'),disposition=enum('completed','partial','replayed','rejected'),diagnostics=arr(ID),output_ref=maybe({'oneOf':[ref('ComponentResult'),ref('ComponentReport')]}),receipt_ref=maybe(ref('Receipt')),published_digests=arr(DIGEST),additional_commit=BOOL))
    s['TransportObservation']=obj(dict(submission_ref=ref('Submission'),outcome=const('acknowledgement_lost'),commit_knowledge=const('unknown')))
    return dict(schema_version='InsuranceComponents/1',schema_ids={k:sid(k) for k in s},**{'$schema':'https://json-schema.org/draft/2020-12/schema','$defs':s})
