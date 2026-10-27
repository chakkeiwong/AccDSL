# Guarded requirement activation

MethodRequirements/3 is a separate successor that composes the protected v2
arithmetic and v1 consequence rules. It adds guard and guard_requires to every
requirement, plus an explicit manifest-level required_known list. Body requires
and guard_requires name exact referenced inputs separately. Their union must
cover all manifest inputs together with required_known. No default guard or
implicit global known-input requirement is inserted.

The guard controls applicability of one declared requirement, not execution
permission. Structural/type/dimension validation checks guard and body even
when the guard is false. The evaluator computes both, preserving dependencies,
unknown reasons and product details; the body result is diagnostic when inactive.

| Guard | Body | Requirement consequence |
|---|---|---|
| true | true | satisfied |
| true | false | declared on_false: invalid or unsupported |
| true | unknown | unresolved |
| false | any of true/false/unknown | not_applicable |
| unknown | any of true/false/unknown | unresolved |

Unknown guard remains unresolved even when the body is true. This is a
conservative applicability rule, not classical implication or history-family
entailment. An always-required fact belongs in required_known or a separate
unconditional requirement; a false guard does not remove that obligation.
Unknown required_known inputs produce explicit unresolved findings. Literal
known text unknown is still a known value.

After retaining all findings, invalid dominates unsupported and unresolved as
before. Missing capabilities remain unsupported. If no blocking consequence
exists and at least one guard is true, status is requirements_satisfied. If all
guards are false, status is no_active_requirements, not an eligibility claim.
Every result retains method_eligible=false, source_admission=false,
accounting_admission=false and executed=false. Manifest identity binds guards
and required_known. Reauthoring a different guard changes the selected identity;
the system does not independently prove that the caller chose all necessary
conditions, and the result cannot authorize a transition.

## Lowering and exact comparators

Each guard and body becomes a separately identified protected v2 requirement.
The v3 layer interprets their truth pair through the table above and records
original identities and dependencies. required_known-only inputs receive
internal validation rows so that types are still checked; those rows are not
published as financial equalities. No dynamic callback, method import or new
arithmetic is introduced. Generated requirement IDs are deterministic and not
confused with user identities. The v2 result is explanatory input to activation,
not the v3 summary verdict.

The retained opening refund/recovery equations apply when the component is
unsettled; settled components instead require outstanding refund/recovery zero.
Deferred correspondence additionally requires the selected zero tax bases.
For this scoped comparison, selected tax and component scalars remain explicitly
required_known to match the legacy validator's separate unknown-input collection.
The comparison preserves other original method requirements as residuals.
Known-state examples, unknown settlement, unknown amounts and mixed false/unknown
cases distinguish activation from accidental bypass. Collection/sequence,
report/carry and accounting-authority obligations are not supplied by guards.

A false guard with a malformed body is invalid; a false guard with a well-typed
false body is not_applicable. This separation is essential. Test both directly.
Test all nine guard/body truth pairs, required-known-only inputs, all-inactive
results, missing capabilities, changed guards under stale hashes and immutable
input data. Every known retained comparison must state its supplied premise.

No v1/v2 hashes or semantics change. Text and record binding for successors are
the next interoperability task. All evidence is deterministic engineering
conformance. No full method, source/accounting admission, production or forecast
conclusion follows; S1–S5 partial, S6 held and S7 deferred.
