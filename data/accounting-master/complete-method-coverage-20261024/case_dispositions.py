"""Explicit disposition for every recorded adverse case in the selected boundary."""
GROUPS={}


def add(package,category,names,next_action):
    target=GROUPS.setdefault(package,{})
    for name in names.split():
        assert name not in target,name
        target[name]={'category':category,'next_action':next_action,
                      'evidence_role':'preserved_original_adverse_case',
                      'declarative_equivalence':'not_established_for_full_method'}


AUTHOR='company-return-schema-20261023'
EXEC='company-return-execution-20261024'
PROGRAM='company-composed-profile-20261024'
add(AUTHOR,'schema_scalar_and_identity',
    'missing_component extra_component_field wrong_profile integer_boolean noncanonical_rational negative_refund float_amount missing_tax_source multiline_typed_name unicode_line_separator nul_in_typed_context bad_source_pointer_digest bad_source_pointer_escape wrong_method wrong_account_role unknown_identifier',
    'Retain closed schema and exact scalar/source syntax validation; do not replace it with true findings.')
add(AUTHOR,'guarded_numeric_and_allocation',
    'bad_refund_allocation bad_recovery_allocation wrong_opening_dta wrong_tax_basis zero_units_no_phantom_lot wrong_cash_fact partial_lot_sale',
    'Add context-checked products and guarded scalar conditions before collection or execution claims.')
add(AUTHOR,'unknown_finding_and_precedence',
    'unknown_tax_rate unknown_tax_finding false_tax_finding false_handling_finding unknown_settlement known_contradiction_with_unknown false_finding_with_unknown known_contradiction_with_false_finding unknown_refund_not_invented unknown_settled_not_truthy false_sale_control',
    'Preserve false/unknown distinction and explicit guards; no authority follows from a caller Boolean.')
add(AUTHOR,'collection_time_and_reference',
    'duplicate_event_identity sale_before_settlement outside_period missing_lot_reference double_sale',
    'Specify collection uniqueness, reference/state order and temporal checks separately.')
add(EXEC,'proposal_replay_identity',
    'changed_journal_refused changed_after_state_refused changed_method_identity_refused changed_event_fact_refused stale_proposal_refused forged_proposal_before_sha256 forged_proposal_committed',
    'Preserve trusted semantic replay and proposal identity; static predicate success cannot replace it.')
add(EXEC,'state_lifetime_and_allocations',
    'second_settlement_refused disposed_lot_refused old_event_id_after_carry opening_dta_allocation extra_inventory_allocation_refused',
    'Preserve component/lot allocations and lifetime identity before any composition promotion.')
add(EXEC,'runtime_schema_and_dates',
    'all_rights_closed_0 handling_is_selling_cost_0 closed_event_extra_field missing_event_field malformed_event_date malformed_event_rational extra_state_wallet malformed_carry_date',
    'Keep structural failures distinct from unresolved facts and unsupported methods.')
add(EXEC,'runtime_caller_findings',
    'all_rights_closed_unknown all_rights_closed_False handling_is_selling_cost_unknown handling_is_selling_cost_False tax_rate_enacted_unknown tax_rate_enacted_False tax_recovery_supported_unknown tax_recovery_supported_False tax_temporary_difference_inventory_complete_unknown tax_temporary_difference_inventory_complete_False tax_outside_basis_timing_control_unknown tax_outside_basis_timing_control_False tax_outside_basis_no_foreseeable_reversal_unknown tax_outside_basis_no_foreseeable_reversal_False',
    'Retain event-specific unresolved/unsupported findings while preserving preceding successful state.')
add(EXEC,'funding_failure','cash_shortfall_is_economic_failure',
    'Preserve economic funding failure and atomicity; never convert it into an invalid-input finding or invented borrowing.')
add(EXEC,'tax_period_report_and_carry',
    'no_annual_report_before_tax no_carry_before_tax wrong_tax_start wrong_tax_cutoff unknown_tax_prefix_no_carry tax_refund_not_manufactured same_year_late_post_after_tax repeated_tax_close partial_carry_atomic_refusal',
    'Keep contiguous tax periods, selected refund scope and incomplete-year report/carry refusal explicit.')
add(PROGRAM,'program_structure_and_source_identity',
    'wrong_profile extra_wallet missing_opening changed_owner changed_currency changed_packet changed_component changed_event_pointer changed_event_digest duplicate_event omitted_event reordered_events extra_review integer_review multiline_metadata',
    'Preserve exact program/source identity, complete schedule and closed caller-finding keys.')
add(PROGRAM,'capability_selection',
    'swapped_native_route swapped_tax_route arbitrary_import changed_method_bytes wrong_report_route wrong_carry_route different_next_year',
    'Keep caller-trusted capability selection and exact report/carry route bindings outside partial predicates.')
add(PROGRAM,'program_prefix_findings',
    'unknown_tax_review false_return_review unknown_return_review false_review_precedes_unknown',
    'Retain exact successful prefix and per-event findings; do not require future tax certainty before earlier valid events.')
