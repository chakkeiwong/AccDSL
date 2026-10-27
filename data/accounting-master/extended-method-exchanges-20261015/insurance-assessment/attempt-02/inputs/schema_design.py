"""Closed query-only InsuranceAssessment/1 schemas; no accounting commit API."""
PREFIX = 'accdsl.insurance-assessment.'
OP = 'insurance.assessment.publish@1'
def sid(k): return PREFIX + k.lower() + '.v1'
def obj(p): return dict(type='object', properties=p, required=list(p), additionalProperties=False)
def arr(s, n=0): return dict(type='array', items=s, minItems=n)
def enum(*v): return dict(enum=list(v))
def const(v): return dict(const=v)
def maybe(s): return dict(anyOf=[s, dict(type='null')])
ID = dict(type='string', pattern='^[A-Za-z0-9_.:@/-]+$')
DATE = dict(type='string', format='date')
STAMP = dict(type='string', format='date-time')
INT = dict(type='integer', minimum=0)
BOOL = dict(type='boolean')
DIGEST = dict(type='string', pattern='^[0-9a-f]{64}$')
Q = obj(dict(n=dict(type='string', pattern='^(0|-?[1-9][0-9]*)$'), d=dict(type='string', pattern='^[1-9][0-9]*$')))
BLOB = obj(dict(kind=const('blob'), algorithm=const('sha256'), digest=DIGEST, byte_length=INT))
def ref(k): return obj(dict(kind=const(k), schema=const(sid(k)), digest=DIGEST))

def variants():
    return {
        'transition.route@1': dict(initial_application=DATE, adjusted_comparatives=arr(DATE, 1), object_type=enum('issued_group', 'acquisition_asset'), requested=enum('full', 'modified', 'fair'), impracticable=enum('yes', 'no', 'unknown'), reasonable_effort=enum('documented', 'not_documented'), historical_evidence=enum('contemporaneous', 'permitted_transition', 'hindsight', 'unknown'), modified_information=enum('available', 'unavailable', 'unknown'), direct_participation=BOOL, prospective_mitigation=BOOL, mitigation_used_before_transition=BOOL),
        'transition.recovery@1': dict(underlying_recognition=DATE, treaty_entry=DATE, transition_date=DATE, mode=enum('transition', 'ordinary_initial'), remaining_coverage=BOOL, recognition_admission=enum('admitted', 'unknown'), covered_group=ID, coverage_allocation=enum('admitted', 'unknown'), group_loss=Q, covered_loss=Q, expected_share=Q, measured_held_asset=maybe(Q)),
        'transition.opening@1': dict(transition_date=DATE, groups=arr(obj(dict(group_id=ID, fcf=Q, fair_value=Q, old_liability=Q)), 1), other_assets=Q, old_held_asset=Q, new_held_asset=Q, embedded_recovery=Q, tax=const('uncomputed'), fx=const('absent'), accumulated_oci=const('excluded')),
        'triangle.inspect@1': dict(triangle_id=ID, valuation_date=DATE, origins=dict(**arr(INT, 3), maxItems=3), cumulative=dict(**arr(dict(**arr(maybe(Q), 3), maxItems=3), 3), maxItems=3), structural_missing=dict(**arr(dict(**arr(BOOL, 3), maxItems=3), 3), maxItems=3), development_unit=const('year'), tail_factor=Q, observation_model=const('volume_chainladder_no_tail')),
        'estimation.predict@1': dict(triangle_id=ID, process_law_id=ID, conditioning=enum('full_triangle', 'latest_diagonal'), horizon=const('lifetime_payments'), fit_dependence=const('shared'), failure_policy=const('retain_all_attempts'), threshold=Q, draws=arr(obj(dict(draw_id=ID, fit_id=ID, probability=Q, mean_per_cell=Q, failure=maybe(enum('FIT_DENOMINATOR_ZERO', 'MODEL_SUPPORT_FAILURE', 'PROCESS_FAILURE')), outcomes=arr(obj(dict(probability=Q, cells=arr(Q, 1)))))), 1)),
        'backward.condition@1': dict(triangle_id=ID, backward_law_id=ID, observed_y=Q, prior=maybe(arr(obj(dict(x=Q, probability=Q)), 1)), forward=arr(obj(dict(x=Q, outcomes=arr(obj(dict(y=Q, probability=Q)), 1))), 1)),
        'reserve.error@1': dict(triangle_id=ID, conditioning=enum('full_triangle', 'latest_diagonal'), center_conditioning=enum('full_triangle', 'latest_diagonal'), paid=arr(Q, 1), simulated_ultimate=arr(Q, 1), fitted_ultimate=arr(Q, 1), center_kind=enum('reserve', 'ultimate')),
        'cdr.one-year@1': dict(triangle_id=ID, opening_date=DATE, closing_date=DATE, opening_reserve=Q, payments=Q, closing_reestimated_reserve=Q, horizon=const('one_year_reestimation')),
        'dependence.stoploss@1': dict(triangle_id=ID, family_id=ID, parameter_min=Q, parameter_max=Q, selected_parameter=maybe(Q), claim_high=Q, attachment=Q, marginal_high_probability=Q, law_uncertainty=const('unweighted_set')),
    }

DETAILS = {
    'transition.route@1': dict(transition_date=DATE, permitted_routes=arr(enum('full', 'modified', 'fair')), selected_route=maybe(enum('full', 'modified', 'fair')), measurements_performed=const(False)),
    'transition.recovery@1': dict(loss_recovery=maybe(Q), measured_held_asset=maybe(Q), held_asset_derived=const(False), timing_exception=BOOL),
    'transition.opening@1': dict(groups=arr(obj(dict(group_id=ID, csm=Q, loss_component=Q, liability=Q)), 1), old_equity=Q, new_equity=Q, opening_equity_change=Q, liability=Q, cash_change=Q, current_profit=Q, held_asset=Q),
    'triangle.inspect@1': dict(factors=arr(Q), point_reserve=Q, observed_cells=INT, parameter_count=INT, residual_degrees=INT, raw_dispersion=Q, predictive_status=enum('dispersion_unresolved', 'law_not_evaluated'), triangle_sha256=DIGEST, risk_adjustment=const(None)),
    'estimation.predict@1': dict(attempted_draws=INT, failed_draw_ids=arr(ID), known_mass=Q, unresolved_mass=Q, known_mean_contribution=Q, mean=maybe(Q), variance=maybe(Q), tail_probability=maybe(Q), full_distribution=arr(obj(dict(amount=Q, probability=Q))), calibration=const('not_evaluated')),
    'backward.condition@1': dict(condition_mass=maybe(Q), posterior=arr(obj(dict(x=Q, probability=Q))), mean=maybe(Q), variance=maybe(Q), backward_law_status=enum('derived_from_joint', 'unidentified', 'zero_condition_mass')),
    'reserve.error@1': dict(simulated_reserve=Q, fitted_reserve=Q, reserve_error=Q),
    'cdr.one-year@1': dict(cdr=Q, opening_reserve=Q, paid=Q, closing_reserve=Q, calibration=const('not_evaluated')),
    'dependence.stoploss@1': dict(expectation_min=Q, expectation_max=Q, selected_expectation=maybe(Q), independent_expectation=Q, selected_joint_masses=arr(Q), second_high_after_high=maybe(Q), second_high_after_zero=maybe(Q), distribution_over_parameters=const(None)),
}
METHODS = tuple(variants())

def schemas():
    s = {}
    s['Context'] = obj(dict(entity_id=ID, book_id=ID, currency=const('USD'), unit=const('illustrative_million'), authority=const('historical_EU2023_IFRS17'), actual_entity_admission=const('not_established')))
    s['SourceSupport'] = obj(dict(raw_blob=BLOB, text_blob=BLOB, method_blobs=arr(BLOB, 1), anchors=arr(ID, 1), temporal_status=const('retained_historical')))
    s['SchemaLock'] = obj(dict(schema_blob=BLOB, semantic_contract_blob=BLOB))
    s['Profile'] = obj(dict(profile_id=const('InsuranceAssessment/1'), operation=const(OP), methods=arr(enum(*METHODS), 1), schema_lock_ref=ref('SchemaLock'), accounting_effect=const('none')))
    s['Evidence'] = obj(dict(context_ref=ref('Context'), available_at=STAMP, ingested_at=STAMP, facts_blob=BLOB))
    s['View'] = obj(dict(context_ref=ref('Context'), decision_at=STAMP, system_asof=STAMP, evidence_refs=arr(ref('Evidence'), 1)))
    s['AccountingHead'] = obj(dict(context_ref=ref('Context'), owner_id=ID, generation=INT, balances_sha256=DIGEST))
    s['ModelIdentity'] = obj(dict(group_id=ID, triangle_id=ID, process_law_id=ID, backward_law_id=ID, conditioning=enum('not_applicable', 'full_triangle', 'latest_diagonal'), horizon=enum('not_applicable', 'lifetime_payments', 'one_year_reestimation'), calibration_status=const('not_evaluated')))
    s['AssessmentInput'] = dict(oneOf=[obj(dict(method_id=const(k), **v)) for k, v in variants().items()])
    s['AssessmentBasis'] = obj(dict(context_ref=ref('Context'), view_ref=ref('View'), evidence_ref=ref('Evidence'), source_ref=ref('SourceSupport'), model_ref=ref('ModelIdentity'), input_ref=ref('AssessmentInput'), expected_head=ref('AccountingHead'), method_anchor=ID, prior_assessment_refs=arr(ref('AssessmentResult'))))
    s['AssessmentResult'] = dict(oneOf=[obj(dict(method_id=const(k), basis_ref=ref('AssessmentBasis'), status=enum('resolved', 'unresolved'), diagnostics=arr(ID), detail=obj(v), accounting_effect=const('none'))) for k, v in DETAILS.items()])
    s['OperationRequest'] = obj(dict(profile_ref=ref('Profile'), client_id=ID, request_id=ID, operation=const(OP), context_ref=ref('Context'), view_ref=ref('View'), require_current=BOOL, expected_head=ref('AccountingHead'), basis_ref=ref('AssessmentBasis')))
    s['Submission'] = obj(dict(request_ref=ref('OperationRequest'), wire_blob=BLOB))
    s['PublicationReceipt'] = obj(dict(request_ref=ref('OperationRequest'), output_ref=ref('AssessmentResult'), status=const('query_published'), accounting_head=ref('AccountingHead'), accounting_effect=const('none')))
    s['OperationResult'] = obj(dict(request_ref=ref('OperationRequest'), submission_ref=ref('Submission'), disposition=enum('completed', 'partial', 'replayed', 'rejected'), output_ref=maybe(ref('AssessmentResult')), receipt_ref=maybe(ref('PublicationReceipt')), diagnostics=arr(ID), published_digests=arr(DIGEST), additional_commit=BOOL, accounting_effect=const('none')))
    s['TransportObservation'] = obj(dict(submission_ref=ref('Submission'), status=const('acknowledgement_lost'), commit_knowledge=const('unknown')))
    return dict(**{'$schema': 'https://json-schema.org/draft/2020-12/schema', '$defs': s}, schema_ids={k: sid(k) for k in s})
