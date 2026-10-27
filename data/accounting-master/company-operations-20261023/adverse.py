"""Mutation witnesses distinguish accounting equivalence from timing failures."""
from copy import deepcopy
from fractions import Fraction as Q
from operations import execute
from fixtures import split_operations


def inspect(body,source,baseline,base_report,check,case,witnesses,reporting):
    def op(inp,kind):return next(o for o in inp['operations'] if o['kind']==kind)
    def mutated(name,kind,changes):
        inp=deepcopy(body);op(inp,kind)['payload'].update(changes)
        return case(name,inp)
    run,report=mutated('price_change','delivery',{'unit_price':'11/1'})
    # Explicit collection stays280; revenue +30 raises tax6 and AR30.
    check('explicit_settlement_not_automatic_fraction',run['income']['revenue']-baseline['income']['revenue']==30 and run['statements']['profit']-baseline['statements']['profit']==24 and run['statements']['cash']-baseline['statements']['cash']==-6 and run['closing_balances']['receivables']-baseline['closing_balances']['receivables']==30)
    run,report=mutated('unknown_late_payroll','payroll',{'amount':'unknown'})
    check('late_unknown_retains_seven_events',run['status']=='unresolved' and len(run['applied'])==7 and run['balances']['payroll']==0 and run['facility_drawn']==0)
    check('late_unknown_report_is_dated_prefix',report['status']=='partial' and report['prefix_snapshot']['last_event']=='facility_repayment-1' and report['lines']['cash']['status']=='unresolved' and not report['annual_complete'])
    for val,expected in [('unknown','unresolved'),(False,'unsupported')]:
        run,_=mutated('delivery_control_'+str(val),'delivery',{'control_transferred':val})
        check('control_'+str(val)+':no_sale',run['status']==expected and len(run['applied'])==1 and run['balances']['revenue']==0)
    run,_=mutated('insufficient_stock','delivery',{'units':'39/1'})
    check('stock_shortfall_atomic',run['status']=='economic_failure' and run['shortfall']==1 and run['inventory_units']==38 and run['balances']['revenue']==0)
    run,_=mutated('zero_life','plant_addition',{'life':'0/1'})
    check('invalid_asset_no_posting',run['status']=='invalid' and run['reason']=='asset_life' and run['balances']['plant_cost']==122)
    run,_=mutated('midyear_service','plant_addition',{'in_service':'2025-07-01'})
    check('service_before_acquisition_rejected',run['status']=='invalid' and run['reason']=='service_before_acquisition')
    inp=deepcopy(body);op(inp,'plant_addition').update(at='2025-07-01T09:00:00Z');op(inp,'plant_addition')['payload']['in_service']='2025-07-01';inp['operations'].sort(key=lambda o:o['at'])
    run,_=case('valid_acquisition_unsupported_fraction',inp)
    check('midyear_fraction_not_guessed',run['status']=='unsupported' and run['reason']=='midyear_service_fraction')
    run,_=mutated('unreduced_units','purchase',{'units':'68/2'})
    check('noncanonical_rational_rejected',run['status']=='invalid' and run['reason']=='operation_rational')
    run,_=mutated('negative_units','purchase',{'units':'-1/1'})
    check('negative_purchase_not_disposal',run['status']=='invalid' and run['reason']=='operation_rational')
    inp=deepcopy(body);op(inp,'purchase')['payload']['extra']='ignored'
    run,_=case('extra_payload_field',inp)
    check('closed_payload_schema',run['status']=='invalid' and run['reason']=='schema')
    inp=deepcopy(body);op(inp,'delivery')['id']=op(inp,'purchase')['id']
    run,_=case('duplicate_operation',inp)
    check('duplicate_operation_rejected',run['status']=='invalid' and run['reason']=='duplicate_operation_id')
    inp=deepcopy(body);clone=deepcopy(op(inp,'tax'));clone['id']='tax-again';inp['operations'].insert(-1,clone)
    run,_=case('duplicate_tax',inp)
    check('tax_cannot_repeat',run['status']=='invalid' and run['reason']=='single_operation_count')
    inp=deepcopy(body);op(inp,'delivery')['payload']['claim_id']='opening-ar'
    run,_=case('claim_identity_reused',inp)
    check('duplicate_recognition_rejected',run['status']=='invalid' and run['reason']=='duplicate_claim' and run['balances']['revenue']==0)
    inp=split_operations(body);second=next(o for o in inp['operations'] if o['id']=='plant_addition-1-b');second['payload']['asset_id']='capex-2025-a'
    run,_=case('split_asset_identity_reused',inp)
    check('duplicate_asset_retains_first_only',run['status']=='invalid' and run['reason']=='duplicate_asset' and run['balances']['plant_cost']==132)
    inp=deepcopy(body);op(inp,'collection')['payload']['allocations']=[{'claim_id':'sales-ar','amount':'10/1'},{'claim_id':'sales-ar','amount':'10/1'}]
    run,_=case('duplicate_settlement_allocation',inp)
    check('duplicate_allocation_rejected',run['status']=='invalid' and run['reason']=='duplicate_allocation' and run['claims']['sales-ar']['settled']==0)
    inp=deepcopy(body);op(inp,'collection')['payload']['allocations']=[{'claim_id':'opening-ar','amount':'10/1'},{'claim_id':'sales-ar','amount':'301/1'}]
    run,_=case('second_allocation_overpayment',inp)
    check('failed_allocation_list_atomic',run['status']=='invalid' and run['reason']=='over_settlement' and run['claims']['opening-ar']['settled']==0 and run['claims']['sales-ar']['settled']==0)
    inp=deepcopy(body);op(inp,'collection')['payload']['allocations']=[{'claim_id':'purchase-ap','amount':'1/1'}]
    run,_=case('wrong_claim_ledger',inp)
    check('receivable_payment_ledger_enforced',run['status']=='invalid' and run['reason']=='wrong_claim_ledger')
    inp=deepcopy(body);op(inp,'collection')['at']='2025-01-02T10:00:00Z';inp['operations'].sort(key=lambda o:o['at'])
    run,_=case('collection_before_recognition',inp)
    check('future_claim_not_spendable',run['status']=='invalid' and run['reason']=='unrecognised_claim' and run['claims']['opening-ar']['settled']==0)
    inp=split_operations(body);op(inp,'supplier_payment')['at']='2025-01-04T10:00:00Z';inp['operations'].sort(key=lambda o:o['at'])
    run,report=case('first_payment_before_draw',inp)
    check('failed_payment_keeps_both_supplier_claims',run['status']=='funding_failure' and run['shortfall']==Q(27,5) and run['claims']['purchase-ap-a']['settled']==0 and run['claims']['purchase-ap-b']['settled']==0 and run['facility_drawn']==0)
    inp=split_operations(body);second=next(o for o in inp['operations'] if o['id']=='collection-1-b');second['at']='2025-01-08T09:00:00Z';inp['operations'].sort(key=lambda o:o['at'])
    run,_=case('late_partial_receipt',inp)
    check('half_receipt_still_funds_payroll',run['status']=='complete_conditional' and run['closing_balances']==baseline['closing_balances'])
    inp=split_operations(body,Q(2,5));second=next(o for o in inp['operations'] if o['id']=='collection-1-b');second['at']='2025-01-08T09:00:00Z';inp['operations'].sort(key=lambda o:o['at'])
    run,_=case('smaller_partial_receipt_failure',inp)
    bridge=Q(427,5)*Q(1,20)*Q(2,365)
    check('smaller_receipt_causes_payroll_failure',run['status']=='funding_failure' and run['event']=='payroll-1-b' and run['shortfall']==Q(117,5)+bridge and run['claims']['sales-ar-a']['settled']==Q(216,5) and run['claims']['sales-ar-b']['settled']==Q(324,5) and run['balances']['payroll']==20)
    inp=deepcopy(body);op(inp,'collection')['at']='2025-01-04T12:00:00Z';op(inp,'facility_draw')['at']='2025-01-04T12:00:00Z';inp['loan']['principal']='0/1'
    inp['operations'].sort(key=lambda o:o['at'])
    # Equal-instant list order currently places draw,payment,collection.
    run,_=case('equal_instant_payment_before_collection',inp)
    check('same_instant_does_not_net_future_cash',run['status']=='funding_failure' and run['event']=='supplier_payment-1')
    payment=op(inp,'supplier_payment');collection=op(inp,'collection');i=inp['operations'].index(payment);j=inp['operations'].index(collection);inp['operations'][i],inp['operations'][j]=collection,payment
    run,_=case('equal_instant_collection_before_payment',inp)
    check('explicit_precedence_enables_payment',run['status']=='complete_conditional')
    inp=deepcopy(body);op(inp,'collection')['at']='unknown'
    run,report=case('unknown_instant',inp)
    check('unknown_global_order_has_no_prefix',run['status']=='unresolved' and 'applied' not in run and 'prefix_snapshot' not in report)
    inp=deepcopy(body);inp['name']='unknown';run,_=case('literal_unknown_name',inp)
    check('unknown_token_only_for_supported_fields',run['status']=='complete_conditional')
    inp=deepcopy(body);inp['inventory']['method']='fifo';run,_=case('unsupported_costing',inp)
    check('unsupported_method_no_fallback',run['status']=='unsupported' and run['reason']=='method')
    inp=deepcopy(body);inp['facility']['eligible']='unknown';run,_=case('unknown_facility',inp)
    check('unknown_global_facility_not_approval',run['status']=='unresolved' and 'applied' not in run)
    inp=deepcopy(body);inp['facility']['limit']='80/1';run,_=case('facility_capacity',inp)
    check('facility_draw_not_cash_plug',run['status']=='funding_failure' and run['reason']=='facility_headroom' and run['facility_drawn']==0)
    changed=deepcopy(body);op(changed,'delivery')['payload']['unit_price']='11/1'
    check('report_input_mismatch_rejected',reporting.build_report(changed,baseline,source)['status']=='invalid')
    check('report_result_digest_present',base_report['run_sha256'] and base_report['input_sha256']==baseline['input_sha256'])
