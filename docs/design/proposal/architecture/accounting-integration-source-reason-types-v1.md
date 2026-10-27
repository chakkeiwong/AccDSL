# Source reason types — six-row amendment v1

This proposal amendment repairs F154/C01, F169/C02, F182/C03, F194/C04,
F229/C06 and F261/C08 in the retained integration field matrix. It addresses
MC08, MC13, MC25, MC34 and MC35, with G4/G18 interactions. It is a document
specification and finite set of local examples. Product implementation remains
disabled; independent review of this repair and full P16 acceptance are pending.

## Decision and amendment precedence

The old `types: ["null"]` entries describe values observed in the preserved
integration examples. They cannot also specify the permitted types: each row's
constraint expressly allows `string|null`. For these six rows only, use the
companion amendment matrix's `observed_types` for the observations and
`allowed_types: ["null", "string"]` for the proposed type rule. This amendment
takes precedence over those six `types` declarations and clarifies their reason
string content and local diagnostic selection. The original 299-path inventory,
fact-field constraints, source packets and V01–V16/S01–S04 examples remain
preserved. Other rows' ambiguities and conditional rules are not repaired here.

Each packet must contain `unknown_reason`. JSON null is present and has type
null; an absent property is missing and is not another spelling of null.
A string must contain at least one character outside the whitespace set
defined below. A nonblank contextual explanation is permitted even when the
packet's facts are stipulated and no unresolved fact is represented. It remains
explanatory text: it supplies no missing fact, changes no Boolean or date, and
does not establish accounting eligibility. Source text is preserved exactly;
there is no trimming, Unicode normalization, string coercion or fact extraction.

For this proposal, whitespace is the following explicit set of Unicode scalar
values: U+0009–U+000D, U+0020, U+0085, U+00A0, U+1680, U+2000–U+200A,
U+2028–U+2029, U+202F, U+205F and U+3000. This finite set avoids a dependence on
a host language's changing character classification. The empty string and a
string composed entirely of these values fail the content rule. Other string
characters remain subject to inherited source-document parsing requirements.
No new source parsing or normalization policy is introduced by this local rule.

Permitting null as a JSON type does not permit it in every packet context.
Existing restrictions on null facts and the requirement for explanations of
unresolved facts still apply. This task demonstrates the two type-valid reason
variants only in E01's retained, fully stipulated packets. Whether a reason is
required by a different packet's facts is a separate conditional predicate.
C03's `contractual_date = null` when `party_to_contract = false` remains the
existing not-applicable-date rule; this amendment neither tests nor enlarges it.
It does not permit a null party-to-contract Boolean.

## Local findings and their derivation

The diagnostic path is `source/<condition_id>/unknown_reason`. The local
predicate stages below are `shape`, assuming the packet has already been
parsed and its enclosing object is available. They describe the result of these
field predicates, not the result of executing the full integration endpoint.

| Candidate property | Scoped predicate | Finding |
| --- | --- | --- |
| Missing | Required packet member | `INVALID_CONDITION_PACKET` |
| Present, neither null nor string | Permitted JSON type | `INVALID_FIELD_TYPE` |
| Present, string without a non-whitespace character | Reason content | `INVALID_UNKNOWN_REPRESENTATION` |
| Present null | Type permitted; context still applies | No local finding |
| Present nonblank string | Type and content permitted; context still applies | No local finding |

This table resolves overlap between the inherited lexical, source-packet and
unknown-representation groups at these six properties. Evaluate presence first;
evaluate type only for a present member; evaluate string content only for a
string. Thus a missing field does not also generate a type error, and an array
does not also generate a content error. A wrong-type reason is not treated as
an unresolved accounting fact. Conditional fact/reason consistency has not been
evaluated by these local examples and cannot supply another finding here.

At other independently decidable paths, retain all findings from the same shape
stage and sort by `(path, code)`, as required by the rejection contract's
“Submitted bytes and validation order” section. An example containing several
faulty reason properties demonstrates this retention without assuming that a
full request reached the shape stage. A malformed enclosing packet would need
its own container diagnostic before a leaf can be inspected; such containers
are outside this amendment's examples.

Each expected finding records `stage`, `path`, `code`, the expected field rule
and the observed presence/type/value. Missing observations have `present:false`
and no value; null observations have `present:true`, `type:"null"`, `value:null`.
The diagnostic derives these fields from the actual materialized candidate.
Mutation paths document the changed property and are not substituted for
returned diagnostic paths. Passing examples state `scoped_predicates_satisfied`;
their packet admission is explicitly `not_assessed`.

## Matched examples and alternatives

For each row the fixtures copy the corresponding complete E01 packet by pinned
file, case and condition. The retained null control and a proposed contextual
string preserve every other member. Negative candidates remove the member or
replace its value with empty/whitespace text, booleans, numbers, an array or an
object. These are design variants, not newly asserted source evidence. Retained
source bytes and their existing identities are unchanged; no candidate is
installed in a validated registry. No request identity, receipt lookup,
publication behavior or semantic accounting assessment is simulated.

Inferring an allowed type from the observed sample would reject valid future
reason text merely because every selected example used null. Allowing arbitrary
JSON values would admit false/zero as explanations. Coercing these values to
strings would alter the source and obscure the distinction between malformed
data and intentional uncertainty. Explicit permitted types plus a separate
content rule avoids these errors while leaving conditional admissibility
visible. It is a proposed finite-profile rule, not a universal accounting rule.

## Pre-execution audit and evidence contract

The engineering question is whether the six inconsistent declarations can be
amended without changing their observed inventory or admitting malformed reason
values. The exact baselines are the pinned field matrix, all seventeen corrected
integration cases and their source references, and E01's six retained packets.
The pass criterion is an explicit observed/permitted distinction for all six
rows, matched positive and negative candidates, and findings independently
derived from their actual properties. Changed predecessors, extra amended rows,
contradictory controls, non-isolated mutations or ambiguous diagnostic selection
veto completion of this bounded task. Check counts are explanatory only.

The skeptical plan audit found no remaining objection to this smaller slice:
the comparator is unchanged, no broad acceptance follows from local checks,
the stop condition is finite, and standard-library document diagnostics match
the environment. No scientific run, model comparison or accounting calculation
is involved. The source-reason-types matrix, fixtures and verification report
preserve the result. The retained source hashes and P16 reference checks detect
accidental edits and stale bindings.

| Choice | Provenance and status | Failure risk and early check |
| --- | --- | --- |
| Null/string types | Existing six row constraints; proposed clarification | Rejecting text because it was unobserved; exercise both positive variants |
| E01 comparator | Retained synthetic example; preservation baseline | Mistaking stipulated facts for authority; copy packets exactly and preserve scope/provenance |
| Nonblank Unicode reason | Inherited nonempty source-text rule, refined proposal | Empty explanations or implicit coercion; empty, Unicode whitespace and nonstring candidates |
| Presence/type/content precedence | Proposed disambiguation of existing shape groups | Duplicate or suppressed findings; derive each case and aggregate independent faults |
| Standard-library diagnostic | Document-check convenience, no runtime selection | Self-confirming metadata; recompute observations, mutations and findings from candidate values |

Stop after the six-row amendment, examples, derived findings, preservation and
registered structural checks, and reconciled P16 references are saved. The next
task completes source null/reason conditional rules and representative complete
exchanges, including C05/C07 unknowns, C09 inner/outer reasons, C10 contextual
reasons and controlling nullable leaves. Then repair the explicit V01–V16
diagnostics and stage derivations before wider predicate coverage. Four
architecture groups, the integrated profile and dependency order, and fourteen
decisions remain unresolved. Runtime enforcement, accounting validity, forecast
validity and human acceptance are not established. All wider MC01–MC35/G1–G18
obligations remain active.
