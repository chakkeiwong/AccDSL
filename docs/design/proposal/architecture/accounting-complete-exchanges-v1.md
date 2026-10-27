# Accounting exchange and context reconciliation

The field controls for C09/C10 distinguish missing, malformed, unknown and
not-applicable values. This supplement carries those controls through complete
requests, dependency closure, assessments and publication. It also supplies the
remaining source/context predicates and an independently derived disposition for
V01–V16. It addresses MC08, MC13, MC25, MC27, MC34 and MC35, with G4/G18.
No accounting engine or product endpoint is implemented.

## Comparator, evidence and audit

The comparators are the seventeen corrected integration-v2 exchanges, the
accepted C03/C05/C07 supplements, the saved 260 C09/C10 field controls and
the sixteen V-series input/output mutations. Source claims and method flags
remain synthetic assumptions. The check must derive findings from supplied
fields, verify newly pinned source packets and all transitive record references,
then compare authored expected results. Matching a copied outcome alone would
not test the defect. Earlier evidence remains unchanged.

The skeptical audit passes for this finite specification task. Reject stale
pins, unintended changed facts, incorrect reference closure, disagreement between
price and route requirement, guessed Boolean controllers, premature receipt
lookup or publication of defective output. Fixable failures trigger correction
of this draft. Source-authority gaps remain P17 work; no deterministic check
promotes stipulated facts into inspected entity facts. No backend, solver,
timing or statistical comparison is attempted.

## Binding and semantic predicates

Use the native sequence parse, recognizable dependencies, shape, source_versions,
bindings, lookup, freshness, assessment, output validation. A shape-valid but
internally inconsistent source packet is a binding failure, not a legitimate
economic alternative. Unknown economic content must use the named unknown
representation. The existing 299-path field matrix governs types/presence; the
later reason and C03/C05/C07/C09/C10 amendments prevail for their exact fields.

| Conditions | Required consistency and remaining meaning |
| --- | --- |
| C01 | Annual start equals request context; `within_retained_window` equals `2023-01-01 <= annual_start < 2026-07-01` for the pinned Compilation 5. False consistently represented is outside_scope; a contradictory flag is SOURCE_CONTEXT_MISMATCH. The edition, reporting basis and actual entity applicability still need source-supported assessment. |
| C02 | Holder/instrument/exception facts remain independently admitted. A synthetic scope-exceptions string is a stated assumption, never executable proof that exceptions are absent. Unsupported feature gives outside_scope; missing required real-world assessment gives unresolved. |
| C03/C04 | Preserve the accepted C03 date/party rules. Recognition date equals the event's economic date; trade/settlement and valuation dates must be valid dates. Conditional policy eligibility does not override nonparticipation. No universal equality of contractual and recognition dates is imposed. Regular-way/policy eligibility is a distinct admitted method judgment. |
| C05 | Category agrees with the event category. Classification rationale and designation/OCI choices remain the accepted explicit conditional rules; descriptive cash-flow prose is not a completed SPPI analysis. |
| C06/C07 | Exact decimal price/fair value/fee equal the event values; valuation date equals the event's date for this immediate-acquisition profile. A different valuation date needs a named bridging method/new profile. C07 incrementality and purpose obey the saved predicates; contextual reason text never changes them. |
| C08 | Source entity/book/branch labels match the declared synthetic aliases; aliases match request identity and pinned context/branch. Currency/unit/scale equal context. Cash settlement and no separate FX/tax/other-asset treatment are profile assumptions, not universal accounting rules. |
| C09 | With valid exact source amounts, required is exactly `price != fair_value`. Under equal price the retained profile has two null, not-applicable routes and branch not_applicable. Under unequal price either true route gives branch a, both false give b, and all other valid pairs give unknown. Both route values and both reasons survive even when one true route suffices. A stored branch inconsistent with those values is SOURCE_CONTEXT_MISMATCH. |
| C10 | Method availability comes from the pinned method/profile, not a supplied true flag or reason. This retained profile has neither unequal-price posting method. A true availability flag contradicts its pinned capability and fails METHOD_CAPABILITY_MISMATCH. A different supported package requires a new method/profile Ref and full reassessment. C10 contextual reason remains nullable; unknown C09 does not itself require C10 text. |

The single KnownBool `observable_valuation` in the request's evidence record is
only the derived qualifying OR of C09. Under required=false it is unknown/not
required; with a true route it is known true; with two false routes known false;
otherwise unknown. The source's two route values are never reconstructed from
this lossy projection. A contradictory convenience field fails
SOURCE_CONTEXT_MISMATCH. Assessment preconditions retain their coarse historical
projection, while findings and valuation_routes retain the precise results.

These rules distinguish a malformed controller from an internally inconsistent
but typed packet, and both from a legitimate unresolved treatment. C01/C02/C04/
C05 actual authority, economic facts and permitted methods remain admissibility
requirements. A real input cannot acquire `synthetic_only` admission by copying
an example label. The interfaces require an explicit mapping and reviewed
applicability decision in its own scope.

## Complete exchanges and output discipline

The companion fixture imports the exact native record registries. Every changed
source packet is stored separately with its comparator and change explanation;
the changed eligibility source/ConditionRefs, request, submission, assessment and
response are rehashed. Each exchange resolves the complete record closure.
File hashes are file references, never mistaken for record digests. Imported
records retain their original digest domains.

Valid contextual-reason changes preserve all economic facts, treatment findings,
method flags and evidence statuses of their comparator. Invalid shape/context
changes return no validated request, assessment, diagnostic journal/delta,
receipt or observed-state publication reference. Lookup, freshness and assessment
are false. Every exchange has additional_commit=false and identical before/after
values for identity index, committed journals, selected state and committed
receipts. Valid assess-only exchanges can look up and assess without posting.

The sixteen retained V cases are active adverse examples, not completed runtime
tests. V01–V04 and V08/V09 fail shape; V05–V07 fail bindings; V10 fails dependency
kind. V11–V16 retain a validated request but reject a defective produced
assessment/response as ASSESSMENT_OUTPUT_INVALID. Derive these outcomes from the
candidate operation/profile/version/aliases/conditions/bindings and published
assessment content. Output checking requires one ordered finding per C01–C10,
summary consistency, correct route projection and diagnostic-example scope,
posting_permitted=false for assess-only, and no additional commit. The rejection
does not imply that the company's acquisition is ineligible.

The finite diagnostic establishes these specified distinctions and preservation
properties. It does not implement arbitrary request validation, prove the truth
of the underlying source statements, establish standards compliance or accept
P16. Integrated independent review must assess its scope with the other eight
contracts and the initial profile.
