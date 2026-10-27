# Common requests to native state owners

CompanyNativeRequest/1 provides a typed caller for three reviewed capabilities.
It does not merge their financial states. CompanyStateInspectionRequest/1
selects annual reports, event prefixes and claim/asset histories;
CompanyPolicyEffectRequest/1 generates supplied inputs, checks equalities or
compares targets; CompanyBookReport/1 reports a supplied recorded period.
Native schemas and guards continue to decide financial admissibility.

The executable closed schema, pinned registry and dispatcher live under
data/accounting-master/company-state-common-request-20261028/. The signature
is dispatch(request, resources). resources maps a declared resource ID to
bytes; it contains exactly source for company-path capabilities and is empty
for a book report. The caller does not load code or files named by the request.

| Required field | Exact meaning |
| --- | --- |
| profile | CompanyNativeRequest/1 |
| capability, operation | Fixed reviewed pair: state_inspection/inspect, policy_effect/inspect, book_report/report |
| implementation_sha256 | Expected bytes of the fixed entrypoint, agreeing with the retained registry and current implementation |
| payload, payload_sha256 | Closed outer payload with request, and path for company-path capabilities; exact sorted-key compact UTF-8 JSON digest |
| resources | Exact IDs, SHA-256 and byte lengths; raw bytes are not canonicalized |
| population | scope=supplied_native_input, actual_company_coverage=unknown |
| information | Explicit audit request or a complete unsupported actor requirement |
| joins | Empty for supported calls; any named join is unsupported |

Transport checks precede the native call: schema, capability/operation,
implementation identity, payload identity, resource identity, joins and
information use. Their order is explicit and does not replace the native
validation order after dispatch. The three capabilities retain the exact
native query selection, operation roles, refusal order, full historical
prefixes and unresolved obligations. The common caller never supplies
defaults for missing native economic fields.

CompanyNativeResponse/1 uses dispatch_status, not a new universal financial
status. returned includes the complete unchanged native_result, even when
that result is invalid, partial or unresolved. invalid means the transport
requirements failed. unsupported means no reviewed capability, operation,
join or actor operator is available. native_exception preserves the
exception type, module and message; it does not pretend a native financial
refusal was returned. Inputs are not mutated.

An audit call requires use=audit_only and view=archival_exogenous_stress.
An actor request instead declares use=actor_observation or actor_action,
actor_id, economic_time, decision_cutoff, system_cutoff,
observation_or_action, receipt_evidence_refs and authority_evidence_refs.
Times use timezone-qualified date-time syntax and evidence lists are nonempty.
These fields record what an actor mapping would need; no reference is accepted
as true because it is supplied. Well-formed actor requirements remain
unsupported by these audit capabilities. Malformed requirements are invalid.
The native BankAssessment information rules require their own exact binding,
described separately from this caller.

Population identity is local to each exact native owner and context. Claim
and asset queries preserve original IDs and complete executed histories;
year-qualified operation IDs distinguish repeated local names. A settled
claim or fully depreciated asset remains queryable when its native history
retains it. The report caller uses supplied books and account partition; it
does not convert accounts into a claim population. Cross-owner transfer,
split, merge, contract lifecycle and population joins have no operator here.

The first retained conformance set has 304 checks over39 cases, including
seven complete native interim reports. It supplies exact return comparisons
and selected independent amounts, not proof of native accounting correctness.
The manifest locks the transitive local files inspected in this run; runtime
pins identify entrypoints and do not certify every possible dependency
environment. No shared state, real source admission, authority, completeness
or release acceptance follows from this common interface.
