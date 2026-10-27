# Selected requirements linked to a retained native request

## Inspected gap and reuse decision

MethodInputBinding/2 pins exact input bytes, field schemas, roles, types and
requirement versions. It does not identify an OperationRequest. Conversely,
the retained CorporateJointHistory/1 MethodDefinition names preconditions as
strings and has no requirement-manifest or input-binding reference. Its purchase
method cannot be treated as a definition of bank.regulatory.assess@1. No
universal MethodDefinition-to-operation mapping is established by either record.

This diagnostic therefore proposes a bounded NativeRequirementLink/1 record.
It links selected date requirements to the actual BankAssessment/1 regulatory
request. Existing MethodInputBinding/2 and MethodRequirements/1–3 perform all
selection, typing and predicate evaluation. Existing requirement text rendering
and lowering supply matched authored forms. No new evaluator or dispatcher.

## Field mapping

| Link field | Exact native origin | Check and remaining meaning |
|---|---|---|
| request_ref | retained exchange | Full kind/schema/digest and salted native record identity |
| submission_ref | retained exchange | Submitted raw bytes equal the complete canonical request record |
| profile_ref/signature_ref | request body | Match the selected profile and exact regulatory signature |
| basis_ref | request arguments.value.basis_ref | Kind/schema/native digest; no other method can be substituted |
| context_ref | basis.context_ref | Full native context bound into selected date types; caller role remains explicit |
| input_sources | basis and its state_ref | Canonical full record bytes get separate raw SHA256 identities |
| manifest_digest/binding_plan_digest | existing binder | Match the exact selected definition and input mapping |
| assessment_date, period_start, period_end | basis body date paths | State-role scalars in the complete native context |
| state_date | basis.state_ref -> body.as_of_date | Same context identity as basis; state-role scalar |

Native record digests are salted by schema; raw input digests hash canonical
record bytes. They are different identities and cannot be substituted. Original
submission bytes are read from the pinned blob file. Basis/state bytes are
explicit canonical serializations of retained records, not original filing bytes.

Selected requirements are only start < end, start <= assessment_date < end,
and assessment_date = state_date. They do not establish the native last-day
condition, scenario window, evidence availability/ingestion, average assets,
applicability, eligibility, current view/head, environment, budget or replay
semantics. A linked result includes the original requirement assessment and
these residual obligations. All execution/admission/eligibility flags stay false.

## Unknowns, failures and evidence limits

Missing registered bytes/records/capabilities remain unsupported. Bad digests,
cross-operation substitutions, mismatched full context or source mappings refuse
the link. Missing declared scalar paths remain unresolved in the binder, while
native record validity is a separate residual: unknown is not a legal native
request field. Derived mutations are labelled as mutations, never as retained
native evidence. Failed native admission cannot be hidden by satisfied selected
requirements. Replay and unknown acknowledgement remain original observations.

The diagnostic compares all retained regulatory exchanges with the original
native auditor. It checks requirement text/typed equivalence for versions 1–3,
independent Python date expectations, malformed links and binder failures. This
is a finite design probe. Arbitrary method authoring, general compilation,
cross-profile context conversion and a complete eligibility system remain open.
