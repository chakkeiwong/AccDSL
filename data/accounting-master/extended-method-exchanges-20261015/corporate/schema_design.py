"""Closed documentary types; no execution or accounting runtime."""
from copy import deepcopy
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
PREFIX = 'accdsl.corporate-components.'

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
ASSETS = 'cash wip finished_goods ppe goodwill rou dta pension_asset receivable'.split()
LIABILITIES = 'payable lease_liability pension_liability provision dtl contract_liability'.split()
PROFIT = 'income expense finance_expense tax_expense'.split()
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

def remap(v):
    if isinstance(v, str): return v.replace('accdsl.corporate.', PREFIX)
    if isinstance(v, dict): return {k: remap(x) for k, x in v.items()}
    if isinstance(v, list): return [remap(x) for x in v]
    return v

def schemas():
    base = json.loads((ROOT / 'data/accounting-master/corporate-portable-20261015/record-schemas.json').read_text())['$defs']
    s = {k: remap(deepcopy(base[k])) for k in ['SchemaLock', 'OperationSignature', 'Environment', 'Decoder',
         'Submission', 'OperationResult', 'TransportObservation']}
    s['Profile'] = obj({'profile_id': {'const': 'CorporateComponents/1'}, 'schema_lock_ref': ref('SchemaLock'),
        'operations': arr(ID, 1), 'book_mode': {'const': 'synthetic'}, 'execution_mode': {'const': 'specification_example'},
        'interest_cash_policy': {'const': 'historical_IAS7_operating_election'}})
    s['Context'] = obj({'entity_id': ID, 'book_id': ID, 'branch_key': ID, 'currency': {'const': 'USD'},
        'basis': enum('historical_EU_IFRS_conditional'), 'calendar': {'const': 'relative_synthetic'}})
    s['SourceSupport'] = obj({'source_pdf': BLOB, 'method_text': BLOB, 'inspection_note': BLOB,
        'anchors': arr(TXT, 1), 'authority_scope': {'const': 'historical_not_current_admission'}})
    s['Authority'] = obj({'source_ref': ref('SourceSupport'), 'context_ref': ref('Context'),
        'start_inclusive': INT, 'end_exclusive': INT, 'evidence_class': {'const': 'synthetic_conditional_admission'}})
    s['View'] = obj({'source_refs': arr(ref('SourceSupport'), 1), 'revision': INT,
        'supersedes_ref': maybe(ref('View')), 'information_mode': enum('archival_synthetic', 'historical_investor')})
    s['MethodDefinition'] = obj({'method_id': enum(*EVENTS), 'component_kind': enum(*COMPONENTS),
        'source_ref': ref('SourceSupport'), 'contract_blob': BLOB, 'profile_ref': ref('Profile')})
    s['ComponentState'] = {'oneOf': [obj({'tag': {'const': k}, 'value': v}) for k, v in COMPONENTS.items()]}
    s['EconomicEvent'] = {'oneOf': [obj({'method_id': {'const': k}, 'context_ref': ref('Context'),
        'instant': INT, 'parameters': v}) for k, (_, v) in EVENTS.items()]}
    s['CompanyState'] = obj({'context_ref': ref('Context'), 'view_ref': ref('View'), 'sequence': INT,
        'instant': INT, 'component_ref': ref('ComponentState'), 'balances': obj({k: Q for k in ACCOUNTS}),
        'cash_movements': obj({k: Q for k in CASH}), 'tax_status': enum('uncomputed', 'computed_origin_only'),
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
