"""Closed documentary types; no execution or accounting runtime."""
from copy import deepcopy
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
PREFIX = 'accdsl.corporate-components-v5.'

def sid(kind):
    return {'OperationRequest': 'accdsl.operation.request.v1',
            'OperationResult': 'accdsl.operation.result.v1'}.get(kind, PREFIX + kind.lower() + '.v1')

def obj(fields):
    return {'type': 'object', 'properties': fields, 'required': list(fields), 'additionalProperties': False}

def arr(item, n=0):
    return {'type': 'array', 'items': item, 'minItems': n}

def enum(*values):
    return {'enum': list(values)}

def maybe(value):
    return {'anyOf': [value, {'type': 'null'}]}

ID = {'type': 'string', 'pattern': '^[A-Za-z0-9_.:@/-]+$'}
TXT = {'type': 'string', 'minLength': 1}
INT = {'type': 'integer', 'minimum': 0}
BOOL = {'type': 'boolean'}
Q = obj({'n': {'type': 'string', 'pattern': '^(0|-?[1-9][0-9]*)$'},
         'd': {'type': 'string', 'pattern': '^[1-9][0-9]*$'}})
DIGEST = {'type': 'string', 'pattern': '^[0-9a-f]{64}$'}
BLOB = obj({'kind': {'const': 'blob'}, 'algorithm': {'const': 'sha256'}, 'digest': DIGEST, 'byte_length': INT})

def ref(kind=None):
    return obj({'kind': {'const': kind} if kind else ID,
                'schema': {'const': sid(kind)} if kind else ID, 'digest': DIGEST})

ACCOUNTS = 'cash wip finished_goods ppe goodwill rou dta pension_asset receivable payable lease_liability pension_liability provision dtl contract_liability capital retained income expense finance_expense tax_expense oci_revaluation oci_pension'.split()
ACCOUNTS += ['inventory', 'return_recovery', 'reimbursement', 'refund_liability']
ACCOUNTS += ['product_revenue','service_revenue','commission_revenue','reimbursement_income',
    'provision_gain','cost_of_sales','service_expense','assurance_expense']
ASSETS = 'cash wip finished_goods ppe goodwill rou dta pension_asset receivable inventory return_recovery reimbursement'.split()
LIABILITIES = 'payable lease_liability pension_liability provision dtl contract_liability refund_liability'.split()
PROFIT = 'income expense finance_expense tax_expense'.split()
PROFIT += ['product_revenue','service_revenue','commission_revenue','reimbursement_income',
    'provision_gain','cost_of_sales','service_expense','assurance_expense']
OCI = 'oci_revaluation oci_pension'.split()
CASH = ['operating', 'investing', 'financing', 'unclassified']

COMPONENTS = {
 'production': obj({'stage_id': ID, 'policy': enum('fifo', 'weighted_average'),
    **{k: Q for k in ['opening_units', 'opening_material', 'opening_conversion', 'opening_fraction',
                     'started', 'current_material', 'current_conversion', 'completed', 'closing_units',
                     'closing_fraction', 'wip_cost', 'finished_cost']},
    'phase': enum('opening', 'accumulated', 'completed')}),
 'lossbatch': obj({'batch_id': ID, **{k: Q for k in ['input_units', 'normal_output', 'good_output',
    'cost_pool', 'finished_cost', 'abnormal_cost']}, 'full_effort': BOOL, 'no_salvage': BOOL,
    'no_fixed_overhead': BOOL, 'phase': enum('unallocated', 'allocated')}),
 'inspection': obj({'asset_id': ID, 'inspection_id': ID, **{k: Q for k in
    ['physical_carrying', 'inspection_carrying', 'physical_life', 'inspection_life']}, 'zero_residual': BOOL}),
 'lease': obj({'right_id': ID, **{k: Q for k in ['rou', 'liability', 'remaining_payment', 'rate', 'usage_due']},
    'periods_remaining': INT, 'homogeneous': BOOL}),
 'benefit': obj({'plan_id': ID, 'dbo': Q, 'plan_assets': Q, 'no_ceiling_required': BOOL,
    'phase': enum('opening', 'remeasured', 'curtailed', 'settled', 'service')}),
 'funding': obj({'plan_id': ID, 'dbo': Q, 'plan_assets': Q, 'unavailable_surplus': BOOL,
    'required_funding': Q, 'recognized_obligation': Q, 'paid': Q}),
 'restoration': obj({'asset_id': ID, 'liability_id': ID, 'ppe': Q, 'liability': Q, 'life': Q,
    'impairment_to_date': Q, 'original_cost_includes_liability': BOOL}),
 'impairment': obj({'cgu_id': ID, 'goodwill': Q, 'goodwill_loss': Q, 'assets': arr(obj({
    'asset_id': ID, 'carrying': Q, 'floor': maybe(Q), 'valuation_status': enum('known', 'unknown'),
    'loss_to_date': Q}), 1), 'unit_recoverable': maybe(Q), 'allocated': BOOL}),
 'tax_origin': obj({'asset_id': ID, **{k: Q for k in ['carrying', 'tax_base', 'rate', 'dtl', 'dta', 'gross_surplus']},
    'recovery_probable': BOOL, 'rate_enacted': BOOL}),
 'advance': obj({'contract_id': ID, 'bill_id': ID, 'unallocated_advance': Q,
    'nominal_bill': Q, 'bill_allocated': BOOL}),
}
for field in ['closing_units', 'closing_fraction']:
    COMPONENTS['production']['properties'][field] = maybe(Q)
COMPONENTS['lossbatch']['properties']['good_output'] = maybe(Q)

EVENTS = {
 'production.accumulate': ('production', obj({k: Q for k in ['started', 'material_cost', 'conversion_cost']})),
 'production.complete': ('production', obj({'completed': Q, 'closing_units': Q, 'closing_fraction': Q,
    'rounding': enum('exact', 'cents')})),
 'production.loss': ('lossbatch', obj({'good_output': Q, 'normal_output_admitted_before_observation': BOOL})),
 'inspection.replace': ('inspection', obj({'new_inspection_id': ID, 'new_cost': Q, 'new_life': Q,
    'qualifies': BOOL, 'old_allocation_known': BOOL, 'old_carrying_current': BOOL})),
 'inspection.consume': ('inspection', obj({'years': Q})),
 'lease.reduce': ('lease', obj({'surrendered_fraction': Q, 'new_payment': Q, 'new_rate': Q,
    'same_remaining_term': BOOL, 'no_termination_fee': BOOL})),
 'lease.usage': ('lease', obj({'units': Q, 'unit_fee': Q, 'non_index_variable': BOOL, 'capitalization_required': BOOL})),
 'lease.mature': ('lease', obj({'cash_payment': Q, 'one_period_elapsed': BOOL})),
 'benefit.remeasure': ('benefit', obj({'dbo': Q, 'plan_assets': Q})),
 'benefit.curtail': ('benefit', obj({'dbo_reduction': Q, 'no_earlier_trigger': BOOL})),
 'benefit.settle': ('benefit', obj({'dbo_discharged': Q, 'plan_assets_paid': Q, 'company_cash_paid': Q,
    'legal_discharge': BOOL})),
 'benefit.service': ('benefit', obj({'service_cost': Q, 'annual_rate': Q, 'year_fraction': Q,
    'simple_accrual': BOOL})),
 'funding.recognize': ('funding', obj({'required_amount': Q, 'past_service': BOOL, 'wholly_unavailable_after_payment': BOOL})),
 'funding.pay': ('funding', obj({'cash_paid': Q})),
 'restoration.change': ('restoration', obj({'new_liability': Q, 'recoverable_amount': maybe(Q), 'measurement_current': BOOL})),
 'restoration.pay': ('restoration', obj({'cash_paid': Q, 'classification': enum('operating', 'unresolved'),
    'classification_status': enum('provisional_supplied_interpretation', 'unresolved')})),
 'impairment.allocate': ('impairment', obj({'unit_recoverable': maybe(Q), 'perimeter_consistent': BOOL})),
 'tax.revalue_impair': ('tax_origin', obj({'recoverable': Q, 'no_time_or_base_change': BOOL})),
 'advance.allocate': ('advance', obj({'bill_id': ID, 'gross_bill': Q})),
}

COMPONENTS.update({
 'returns': obj({'cohort_id': ID, **{k: Q for k in ['units', 'price', 'cost', 'expected_remaining', 'returned',
    'refund', 'recovery', 'inventory_units']}, 'control_passed': BOOL, 'estimate_admitted': BOOL,
    'no_recovery_costs': BOOL, 'phase': enum('opening', 'sold', 'remeasured', 'settled')}),
 'assurance': obj({'population_id': ID, **{k: Q for k in ['units', 'sale_price', 'inventory_cost', 'provision',
    'reimbursement', 'reimbursement_fraction', 'paid_claims', 'received_reimbursement']},
    'outcomes': arr(obj({'cost': Q, 'probability': Q}), 1), 'classification': enum('assurance', 'service', 'unknown'),
    'population_obligation_admitted': BOOL, 'reimbursement_virtually_certain': BOOL,
    'phase': enum('opening', 'recognized', 'paid', 'remeasured', 'settled')}),
 'service_contract': obj({'contract_id': ID, **{k: Q for k in ['price', 'product_ssp', 'service_ssp', 'product_cost',
    'cash_received', 'product_allocation', 'service_allocation', 'progress', 'revenue', 'service_cost_paid']},
    'service_start': {'type':'string','format':'date'}, 'service_end_exclusive': {'type':'string','format':'date'},
    'total_service_months': INT, 'completed_service_months': INT,
    'distinct_service': BOOL, 'faithful_uniform_progress': BOOL, 'product_delivered': BOOL}),
 'distinct_contract': obj({'contract_id': ID, **{k: Q for k in ['total_units', 'delivered', 'stock_units', 'unit_cost',
    'total_price', 'received', 'recognized', 'remaining_price_per_unit']}, 'modified': BOOL}),
 'integrated_contract': obj({'contract_id': ID, **{k: Q for k in ['price', 'received', 'progress', 'revenue', 'cost_paid']},
    'customer_controls_wip': BOOL, 'modified': BOOL}),
 'mixed_contract': obj({'contract_id': ID, **{k: Q for k in ['construction_price', 'expected_cost', 'cost_incurred',
    'construction_revenue', 'visit_price', 'visits_total', 'visits_done', 'visit_revenue', 'visit_cost_paid', 'received']},
    'modified': BOOL, 'allocation_admitted': BOOL, 'faithful_cost_progress': BOOL}),
 'agency': obj({'promise_id': ID, 'role': enum('principal', 'agent', 'unknown'), 'control_finding': BOOL,
    'cash_controlled': BOOL, 'supplier_price': Q, 'customer_price': Q, 'inventory': Q, 'payable': Q,
    'phase': enum('opening', 'acquired', 'transferred', 'settled')}),
 'joint_products': obj({'batch_id': ID, 'joint_cost': Q, 'units_a': Q, 'units_b': Q, 'split_price_a': Q,
    'split_price_b': Q, 'cost_a': Q, 'cost_b': Q, 'sold_a': Q, 'sold_b': Q,
    'relative_sales_admitted': BOOL, 'phase': enum('opening', 'allocated', 'sold')}),
 'byproduct': obj({'batch_id': ID, 'production_cost': Q, 'byproduct_nrv': Q, 'main_cost': Q, 'byproduct_cost': Q,
    'immaterial_admitted': BOOL, 'phase': enum('opening', 'allocated', 'sold')}),
 'supplier_finance': obj({'creditor_id': ID, 'normal_price': Q, 'final_payment': Q, 'rate': Q,
    'carrying': Q, 'inventory_cost': Q, 'years_accrued': INT, 'ordinary_trade_supplier': BOOL,
    'not_qualifying_asset': BOOL, 'phase': enum('opening', 'purchased', 'sold', 'settled')}),
})
EVENTS.update({
 'returns.sell': ('returns', obj({'cash_received': Q})),
 'returns.remeasure': ('returns', obj({'expected_remaining': Q, 'new_evidence_admitted': BOOL})),
 'returns.settle': ('returns', obj({'units_returned': Q, 'return_rights_expired': BOOL, 'no_unresolved_claims': BOOL})),
 'assurance.recognize': ('assurance', obj({'cash_sales': Q})),
 'assurance.pay': ('assurance', obj({'claims_paid': Q, 'reimbursement_received': Q})),
 'assurance.remeasure': ('assurance', obj({'remaining_claims': Q, 'new_evidence_admitted': BOOL})),
 'service.receive': ('service_contract', obj({'cash': Q})),
 'service.deliver': ('service_contract', obj({'control_transferred': BOOL})),
 'service.progress': ('service_contract', obj({'progress': Q, 'completed_service_months': INT,
    'cash_cost': Q, 'faithful_measure_admitted': BOOL})),
 'distinct.receive': ('distinct_contract', obj({'cash': Q})),
 'distinct.deliver': ('distinct_contract', obj({'units': Q})),
 'distinct.modify': ('distinct_contract', obj({'added_units': Q, 'added_price': Q, 'cash': Q,
    'enforceable': BOOL, 'remaining_distinct': BOOL, 'separate_contract_test': BOOL})),
 'integrated.receive': ('integrated_contract', obj({'cash': Q})),
 'integrated.perform': ('integrated_contract', obj({'cumulative_progress': Q, 'cash_cost': Q, 'faithful_measure_admitted': BOOL})),
 'integrated.modify': ('integrated_contract', obj({'new_price': Q, 'new_progress': Q, 'cash': Q,
    'enforceable': BOOL, 'remaining_not_distinct': BOOL, 'faithful_measure_admitted': BOOL})),
 'mixed.receive': ('mixed_contract', obj({'cash': Q})),
 'mixed.perform': ('mixed_contract', obj({'construction_cash_cost': Q, 'visits': Q, 'visit_cash_cost': Q})),
 'mixed.modify': ('mixed_contract', obj({'new_construction_price': Q, 'new_expected_cost': Q,
    'new_visits_total': Q, 'cash': Q, 'enforceable': BOOL, 'allocations_admitted': BOOL})),
 'agency.acquire': ('agency', obj({'cost': Q})),
 'agency.transfer': ('agency', obj({'cash': Q, 'promise_satisfied': BOOL})),
 'agency.remit': ('agency', obj({'cash': Q})),
 'joint.allocate': ('joint_products', obj({'cash_cost': Q})),
 'joint.sell': ('joint_products', obj({'units_a': Q, 'units_b': Q, 'cash': Q})),
 'byproduct.allocate': ('byproduct', obj({'cash_cost': Q})),
 'byproduct.sell': ('byproduct', obj({'cash': Q})),
 'supplier.purchase': ('supplier_finance', obj({'financing_assessment_admitted': BOOL})),
 'supplier.accrue': ('supplier_finance', obj({'full_year_elapsed': BOOL})),
 'supplier.sell': ('supplier_finance', obj({'cash': Q})),
 'supplier.pay': ('supplier_finance', obj({'cash': Q})),
})

from asset_types import extend
extend(COMPONENTS, EVENTS, obj, arr, enum, maybe, Q, ID, BOOL, INT)
from benefit_tax_types import extend as extend_benefit_tax
extend_benefit_tax(COMPONENTS, EVENTS, obj, arr, enum, maybe, Q, ID, BOOL, INT, TXT)
ACCOUNTS += ['current_tax_payable','pillar_tax_payable','pillar_tax_expense']
LIABILITIES += ['current_tax_payable','pillar_tax_payable']
PROFIT += ['pillar_tax_expense']
from customer_types import extend as extend_customer
extend_customer(COMPONENTS,EVENTS,obj,arr,enum,maybe,Q,ID,BOOL,INT)
ACCOUNTS += ['contract_asset']
ASSETS += ['contract_asset']

def remap(v):
    if isinstance(v, str): return v.replace('accdsl.corporate.', PREFIX)
    if isinstance(v, dict): return {k: remap(x) for k, x in v.items()}
    if isinstance(v, list): return [remap(x) for x in v]
    return v

def schemas():
    base = json.loads((ROOT / 'data/accounting-master/corporate-portable-20261015/record-schemas.json').read_text())['$defs']
    s = {k: remap(deepcopy(base[k])) for k in ['SchemaLock', 'OperationSignature', 'Environment', 'Decoder',
         'Submission', 'OperationResult', 'TransportObservation']}
    s['Profile'] = obj({'profile_id': {'const': 'CorporateComponents/5'}, 'schema_lock_ref': ref('SchemaLock'),
        'operations': arr(ID, 1), 'book_mode': {'const': 'synthetic'}, 'execution_mode': {'const': 'specification_example'},
        'interest_cash_policy': {'const': 'historical_IAS7_operating_election'}})
    s['Context'] = obj({'entity_id': ID, 'book_id': ID, 'branch_key': ID, 'currency': {'const': 'USD'},
        'basis': enum('historical_EU_IFRS_conditional', 'historical_AU_AASB_conditional'),
        'issuer_class': {'const': 'for_profit'}, 'calendar': {'const': 'relative_synthetic'}})
    s['SourceSupport'] = obj({'source_pdf': BLOB, 'method_text': BLOB, 'inspection_note': BLOB,
        'anchors': arr(TXT, 1), 'authority_scope': {'const': 'historical_not_current_admission'},
        'family': enum('EU_IFRS', 'AU_AASB'), 'period_start_inclusive': maybe({'type': 'string', 'format': 'date'}),
        'instrument_in_force_on':maybe({'type':'string','format':'date'}),
        'period_start_exclusive': maybe({'type': 'string', 'format': 'date'})})
    s['Authority'] = obj({'source_ref': ref('SourceSupport'), 'context_ref': ref('Context'),
        'supporting_source_refs': arr(ref('SourceSupport')), 'start_inclusive': INT,
        'end_exclusive': INT, 'evidence_class': {'const': 'synthetic_conditional_admission'}})
    s['View'] = obj({'source_refs': arr(ref('SourceSupport'), 1), 'revision': INT,
        'supersedes_ref': maybe(ref('View')), 'information_mode': enum('archival_synthetic', 'historical_investor')})
    s['MethodDefinition'] = obj({'method_id': enum(*EVENTS), 'component_kind': enum(*COMPONENTS),
        'method_status':enum('specified_finite','unresolved_settlement_boundary'),
        'source_ref': ref('SourceSupport'), 'supporting_source_refs': arr(ref('SourceSupport')),
        'contract_blob': BLOB, 'profile_ref': ref('Profile')})
    s['ComponentState'] = {'oneOf': [obj({'tag': {'const': k}, 'value': v}) for k, v in COMPONENTS.items()]}
    s['EconomicEvent'] = {'oneOf': [obj({'method_id': {'const': k}, 'context_ref': ref('Context'),
        'instant': INT, 'event_date': maybe({'type': 'string', 'format': 'date'}),
        'reporting_period_start': maybe({'type': 'string', 'format': 'date'}),
        'reporting_period_end_exclusive': maybe({'type': 'string', 'format': 'date'}),
        'parameters': v}) for k, (_, v) in EVENTS.items()]}
    s['CompanyState'] = obj({'context_ref': ref('Context'), 'view_ref': ref('View'), 'sequence': INT,
        'instant': INT, 'component_ref': ref('ComponentState'), 'balances': obj({k: Q for k in ACCOUNTS}),
        'cash_movements': obj({k: Q for k in CASH}), 'revaluation_transfers': Q,
        'tax_status': enum('uncomputed', 'computed_origin_only'),
        'cash_classification_status': enum('specified_historical_policy', 'provisional_supplied_interpretation', 'unresolved')})
    s['AccountingEventBasis'] = obj({'identity': obj({k: ID for k in ['entity_id', 'book_id', 'branch_key', 'business_event_id']}),
        'opening_ref': ref('CompanyState'), 'event_ref': ref('EconomicEvent'), 'method_ref': ref('MethodDefinition'),
        'authority_ref': ref('Authority'), 'view_ref': ref('View'), 'context_ref': ref('Context')})
    s['Admission'] = obj({'basis_ref': ref('AccountingEventBasis'), 'source_ref': ref('SourceSupport'),
        'context_ref': ref('Context'), 'instant': INT, 'status': enum('eligible', 'unresolved', 'ineligible'),
        'fact_basis': {'const': 'authored_synthetic'}, 'findings': arr(obj({'name': ID,
        'status': enum('satisfied', 'unknown', 'failed'), 'support_ref': ref()}), 1)})
    s['PostingAuthorization'] = obj({'basis_ref': ref('AccountingEventBasis'), 'admission_ref': ref('Admission'),
        'view_ref': ref('View'), 'posting_permitted': BOOL})
    s['JournalProposal'] = obj({'basis_ref': ref('AccountingEventBasis'), 'mode': enum('monetary', 'state_only'),
        'currency': {'const': 'USD'}, 'lines': arr(obj({'account': enum(*ACCOUNTS), 'signed_amount': Q}))})
    s['EconomicDelta'] = obj({'basis_ref': ref('AccountingEventBasis'), 'opening_ref': ref('CompanyState'),
        'closing_ref': ref('CompanyState'), 'cash_change': obj({k: Q for k in CASH})})
    s['StateTransitionReceipt'] = obj({'request_ref': ref('OperationRequest'), 'basis_ref': ref('AccountingEventBasis'),
        'authorization_ref': ref('PostingAuthorization'), 'journal_ref': ref('JournalProposal'),
        'delta_ref': ref('EconomicDelta'), 'opening_ref': ref('CompanyState'), 'closing_ref': ref('CompanyState'),
        'generation': INT, 'status': {'const': 'committed'}})
    s['Report'] = obj({'opening_ref': ref('CompanyState'), 'state_ref': ref('CompanyState'), 'view_ref': ref('View'),
        'values': obj({k: Q for k in ['cash', 'assets', 'liabilities', 'equity', 'profit', 'oci', *CASH]}),
        'income_statement': obj({k:Q for k in ['product_revenue','service_revenue','commission_revenue',
            'reimbursement_income','other_gains','cost_of_sales','service_expense','assurance_expense',
            'other_expense','finance_expense','tax_expense']}),
        'attribution': maybe(obj({'parent_loss': Q, 'nci_loss': Q, 'unrecognized_notional_loss': Q})),
        'oci_components':obj({'revaluation':Q,'restoration_revaluation':Q,'pension':Q}),
        'tax_movements':obj({k:Q for k in ['ordinary_current_profit','deferred_profit','deferred_oci','acquisition_deferred','pillar_current_profit']}),
        'income_taxes_paid':Q,
        'pillar_disclosures':maybe(obj({'exception_applied':BOOL,'exception_disclosed':BOOL,'current_separately_disclosed':BOOL,
            'current_tax_in_period':maybe(Q),'legislation_effective':BOOL,'exposure_known':maybe(BOOL),
            'exposure_lower':maybe(Q),'exposure_upper':maybe(Q),'unavailable_explanation':maybe(TXT),'assessment_progress':maybe(TXT)})),
        'revaluation_transfer': Q,
        'tax_status': enum('uncomputed', 'computed_origin_only'), 'complete_company_after_tax': {'const': False},
        'cash_classification_complete': BOOL,
        'cash_classification_status': enum('specified_historical_policy', 'provisional_supplied_interpretation', 'unresolved')})
    s['Obligation'] = obj({'code': ID, 'required_input': TXT, 'basis_ref': ref('AccountingEventBasis')})
    s['Domain'] = obj({'request_ref': ref('OperationRequest'), 'meaning': {'const': 'singleton_request_decision'}})
    s['Region'] = obj({'domain_ref': ref('Domain'), 'predicate': {'const': 'this_request'}})
    args = {
        'accounting.authorize@1': obj({'basis_ref': ref('AccountingEventBasis')}),
        'accounting.propose@1': obj({'basis_ref': ref('AccountingEventBasis'), 'authorization_ref': ref('PostingAuthorization')}),
        'accounting.commit@1': obj({k: ref(v) for k, v in [('basis_ref', 'AccountingEventBasis'),
            ('authorization_ref', 'PostingAuthorization'), ('journal_ref', 'JournalProposal'), ('delta_ref', 'EconomicDelta')]}),
        'report.build@1': obj({'opening_ref': ref('CompanyState'), 'state_ref': ref('CompanyState'),
                             'view_ref': ref('View'), 'require_current': BOOL}),
    }
    s['OperationRequest'] = remap(deepcopy(base['OperationRequest']))
    s['OperationRequest']['properties']['operation'] = enum(*args)
    s['OperationRequest']['properties']['arguments'] = {'oneOf': [obj({'tag': {'const': k}, 'value': v}) for k, v in args.items()]}
    for op, spec in args.items(): s['Arguments.' + op] = spec
    return {'$schema': 'https://json-schema.org/draft/2020-12/schema',
        'schema_ids': {k: sid(k) for k in s}, '$defs': s}

if __name__ == '__main__':
    (OUT / 'record-schemas.json').write_text(json.dumps(schemas(), indent=2) + '\n')
    print(json.dumps({'closed_record_definitions': len(schemas()['$defs']), 'methods': len(EVENTS)}))
