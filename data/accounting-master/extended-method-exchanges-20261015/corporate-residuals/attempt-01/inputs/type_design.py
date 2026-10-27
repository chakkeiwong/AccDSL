"""Closed CorporateResiduals/1 component and event types; no service implementation."""
from copy import deepcopy
import json
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[3]
PREFIX='accdsl.corporate-residuals.'
def sid(kind):return {'OperationRequest':'accdsl.operation.request.v1','OperationResult':'accdsl.operation.result.v1'}.get(kind,PREFIX+kind.lower()+'.v1')
def obj(fields):return {'type':'object','properties':fields,'required':list(fields),'additionalProperties':False}
def arr(item,n=0):return {'type':'array','items':item,'minItems':n}
def enum(*v):return {'enum':list(v)}
def maybe(v):return {'anyOf':[v,{'type':'null'}]}
ID={'type':'string','pattern':'^[A-Za-z0-9_.:@/-]+$'}
TXT={'type':'string','minLength':1}
INT={'type':'integer','minimum':0}
BOOL={'type':'boolean'}
DATE={'type':'string','format':'date'}
Q=obj({'n':{'type':'string','pattern':'^(0|-?[1-9][0-9]*)$'},'d':{'type':'string','pattern':'^[1-9][0-9]*$'}})
DIGEST={'type':'string','pattern':'^[0-9a-f]{64}$'}
BLOB=obj({'kind':{'const':'blob'},'algorithm':{'const':'sha256'},'digest':DIGEST,'byte_length':INT})
def ref(kind=None):return obj({'kind':{'const':kind} if kind else ID,'schema':{'const':sid(kind)} if kind else ID,'digest':DIGEST})
def quantities(*names):return {k:Q for k in names}
ASSETS=['cash','inventory','recovery_asset','ppe','rou','contract_cost','contract_asset','goodwill','dta']
LIABILITIES=['refund_liability','lease_liability','dtl']
PROFIT=['revenue','other_gains','cost_of_sales','cost_expense','amortization','impairment_expense','depreciation','finance_expense','tax_expense']
OCI=['tax_oci']
EQUITY=['capital','retained','original_equity','tax_equity']
ACCOUNTS=ASSETS+LIABILITIES+PROFIT+OCI+EQUITY
CASH=['operating','investing','financing','unclassified']
OCI_MOVEMENTS=['tax']
EQUITY_MOVEMENTS=['tax']
ORIGIN=enum('profit','oci','equity')
ASSET=obj({'asset_id':ID,**quantities('carrying','no_impairment','recoverable_cap')})
RIGHT=obj({'right_id':ID,**quantities('rou','liability','rate'),'last_measurement_date':DATE})
LOT=obj({'lot_id':ID,'entity_id':ID,'authority_id':ID,'origin':ORIGIN,**quantities('difference','rate','fraction','amount')})
COMPONENTS={
 'rcost':obj({'contract_id':ID,**quantities('sold_units','expected_units','unit_refund','unit_cost','estimated_handling','estimated_deterioration','refund','recovery','inventory'),'settled':BOOL}),
 'cgu':obj({'cgu_id':ID,'assets':arr(ASSET,1),'goodwill':Q}),
 'individual':obj({'asset_id':ID,**quantities('carrying','no_impairment')}),
 'lease':obj({'lease_id':ID,'rights':arr(RIGHT,1)}),
 'cost':obj({'contract_id':ID,'lot_id':ID,'kind':enum('acquisition','fulfilment'),**quantities('asset','no_impairment','remaining_units'),'cgu_review_pending':BOOL}),
 'distinct':obj({'contract_id':ID,**quantities('remaining_units','remaining_consideration','revenue','unbilled'),'revision':INT}),
 'integrated':obj({'contract_id':ID,**quantities('total_consideration','progress','revenue','unbilled'),'revision':INT}),
 'acqdta':obj({'acquisition_id':ID,'acquisition_date':DATE,'measurement_end_inclusive':DATE,**quantities('dta','goodwill','retrospective_adjustment','profit_adjustment','oci_adjustment','equity_adjustment')}),
 'taxlots':obj({'lots':arr(LOT,1),'present_net':BOOL}),
}
EVENTS={
 'rcost.settle':('rcost',obj({'actual_units':Q,'unit_handling':maybe(Q),'unit_deterioration':Q,'refund_cash':maybe(Q),'handling_cash':maybe(Q),'inventory_nrv':maybe(Q),'all_rights_closed':BOOL,'handling_is_selling_cost':maybe(BOOL)})),
 'cgu.reverse':('cgu',obj({'recoverable':Q,'changed_estimates':BOOL,'passage_only':BOOL})),
 'individual.reverse':('individual',obj({'recoverable':Q,'changed_estimates':BOOL,'cost_model':BOOL})),
 'lease.reduce':('lease',obj({'allocation_basis':enum('traced_right_amounts','unknown'),'standalone_allocation_supported':maybe(BOOL),'annual_end_payments':BOOL,'rights':arr(obj({'right_id':ID,'removed_rou':maybe(Q),'removed_liability':maybe(Q),'full_termination':BOOL,'new_rate':maybe(Q),'payments':arr(Q)}),1)})),
 'lease.pay':('lease',obj({'right_id':ID,'amount':Q,'one_year_elapsed':BOOL,'no_intervening_accrual_or_modification':BOOL})),
 'lease.depreciate':('lease',obj({'right_id':ID,'amount':Q,'systematic_allocation_supported':maybe(BOOL)})),
 'cost.incur':('cost',obj({'amount':Q,'kind':enum('acquisition','fulfilment'),'nature':enum('incremental','fulfilment','waste','past_service','admin'),'other_standard':enum('none','IAS2','IAS16','IAS38'),'incremental':maybe(BOOL),'directly_related':maybe(BOOL),'future_resources':maybe(BOOL),'recoverable':maybe(BOOL)})),
 'cost.amortize':('cost',obj({'delivered_units':Q,'equal_unit_pattern_supported':maybe(BOOL)})),
 'cost.impair':('cost',obj({'credit_adjusted_consideration':Q,'remaining_direct_cost':Q,'other_impairments_done':maybe(BOOL)})),
 'cost.reverse':('cost',obj({'credit_adjusted_consideration':Q,'remaining_direct_cost':Q,'other_impairments_done':maybe(BOOL),'changed_circumstances':BOOL})),
 'distinct.modify':('distinct',obj({'added_units':Q,'added_consideration':Q,'remaining_distinct':maybe(BOOL),'added_distinct':maybe(BOOL),'priced_at_ssp':BOOL})),
 'distinct.perform':('distinct',obj({'units':Q})),
 'integrated.modify':('integrated',obj({'new_total':Q,'new_progress':Q,'integrated_obligation':maybe(BOOL),'progress_supported':maybe(BOOL)})),
 'integrated.perform':('integrated',obj({'new_progress':Q,'progress_supported':maybe(BOOL)})),
 'acqdta.recognize':('acqdta',obj({'additional_difference':Q,'rate':maybe(Q),'rate_enacted':maybe(BOOL),'recoverable':maybe(BOOL),'benefit_owner':enum('acquiree','acquirer'),'new_acquisition_date_information':maybe(BOOL),'measurement_period_open':BOOL,'underlying_origin':maybe(ORIGIN)})),
 'taxlots.remeasure':('taxlots',obj({'lots':arr(obj({'lot_id':ID,'difference':Q,'rate':maybe(Q),'fraction':Q,'rate_enacted':maybe(BOOL),'recognition_supported':maybe(BOOL),'eligible_difference':maybe(BOOL)}),1)})),
 'taxlots.present':('taxlots',obj({'request_offset':BOOL,'enforceable_current_setoff_right':maybe(BOOL)})),
}
