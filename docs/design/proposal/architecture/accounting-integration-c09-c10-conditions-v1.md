# C09 nested reasons and C10 contextual reasons — proposal amendment v1

This bounded amendment addresses MC08, MC13, MC25, MC34 and MC35 with G4/G18 interactions. It resolves F280, F286 and F294 without rewriting the original field inventory or accepted C03/C05/C07 work. The retained integration exchanges and source packets are synthetic preservation comparators. Product implementation remains disabled.

## Question and evidence contract

Can the representation retain unknown valuation routes and contextual explanations without changing branch selection or method availability? The comparators are the retained E01/E06/E07/E08/E10/E12/E13 packets and their complete integration exchanges, together with the nine valuation pairs in the decision supplement. Passing this bounded task requires explicit predicates, candidate-derived findings, complete matched exchanges, refreshed dependencies and unchanged committed state. Changed predecessor bytes, lost facts, stale dependencies, ambiguous guards, premature lookup or changed committed domains veto completion. Counts from document checks are explanatory only. They establish neither accounting validity nor runtime conformance, forecast validity or human acceptance.

The skeptical audit supports this bounded design: comparators are retained and matched, unknown and not-applicable nulls are distinguished using the supplied controller, text cannot supply accounting facts, and validation precedes lookup. No new accounting authority, numerical method, library or performance comparison is selected. Stop after these rules, finite fixtures and fresh checks; remaining source predicates and V01–V16 repairs are separate tasks.

## Reason predicates

Both `C09/unknown_reason` and `C09/value/unknown_reason` are required properties. Each permits JSON null or a nonblank string. Missing is not null. With exact `required=true` and at least one well-typed null valuation route, both reasons must be nonblank strings, even if the other route is true and establishes branch (a). Their wording need not match: the retained E06 has separate inner and outer explanations. A known branch does not erase an unknown route.

With `required=true` and both routes known, each reason independently permits null or contextual text. For the retained equal-price context with `required=false`, null routes are not applicable and both reasons independently permit null or contextual text. This last rule does not authorize arbitrary false controllers under unequal-price source facts; wider source-context reconciliation remains deferred.

`C10/unknown_reason` is independently required and permits null or nonblank contextual text for every retained branch/method disposition. Retained E06 null and E12 text are valid comparators. An unresolved C09 branch does not make C10 text mandatory. C10 text does not establish a supported method, alter method flags or determine a valuation route.

Strings are preserved exactly. Nonblank means at least one character outside U+0009–U+000D, U+0020, U+0085, U+00A0, U+1680, U+2000–U+200A, U+2028–U+2029, U+202F, U+205F and U+3000, the explicit set inherited from the six-row reason amendment. There is no trimming, coercion or Unicode normalization.

## Diagnostic guards and outputs

Inspect presence, then type, then content at each required node. C09 and its value must be objects; its required controller is an exact Boolean and its two routes are Boolean|null. Preserve the enclosing-object, value and method-flag requirements of C10. Missing required members yield `INVALID_CONDITION_PACKET`; wrong types yield `INVALID_FIELD_TYPE`; blank strings and conditionally forbidden null reasons yield `INVALID_UNKNOWN_REPRESENTATION`.

Derive the unresolved-route obligation only when required is exactly true. A well-typed null route establishes the obligation independently of a malformed sibling route. A missing or malformed required controller suppresses that conditional obligation but does not suppress independently inspectable reason presence, type or blank-string findings. A malformed parent suppresses descendants only: an invalid C09 value does not suppress its inspectable outer reason or independent C10 packet. A reason receives at most one finding; do not duplicate a missing, type or blank-content finding with a conditional-null finding.

Every finding includes stage `shape`, path, code, expected rule and observed presence/type/value. Sort by path then code. Malformed exchanges return rejected/not_committed with additional_commit=false, no validated request or assessment, and null journal/delta/receipt/observed-state publication references. Lookup, freshness and assessment are not performed. Preserve submission bytes and all four committed domains: identity index, journals, selected state and receipts. The seven rejection statuses are structural_validity=invalid, mathematical_status=unresolved, computation_status=not_computed, empirical_justification=not_established, capability_status=specified_only_no_runtime, accounting_validity=not_assessed and human_acceptance=pending.

Valid exchanges continue through source/binding validation, identity lookup, freshness and assessment. Changed source pins, ConditionRefs, request identity, submission and response dependencies must be refreshed. Assessment facts and evidence statuses remain those of the comparator; publication remains assessed/not_committed with no additional commit. A reason edit may change identity, but cannot change economic facts or method availability.

## Alternatives and assumptions

Forced equality between inner and outer reasons would discard E06's distinct explanations. Requiring null whenever no unknown exists would discard contextual evidence, including C10 E12. Requiring C10 text whenever C09 is unresolved would reject E06 without supplying missing valuation facts. The selected rule retains evidence while leaving branch and method decisions with their typed facts.

| Choice and provenance | Status and purpose | Failure mode and earliest diagnostic |
| --- | --- | --- |
| Nullable reasons from F280/F286/F294 | Reviewed proposal refinement; distinguish missing, unknown and context | Unknown routes lose explanations; true/null with each null reason |
| Explicit Unicode set from reason-types v1 | Inherited representation rule | Host-dependent blank classification; empty and U+3000 controls |
| Retained synthetic packets/exchanges | Preservation baselines only | Wrong comparator grants eligibility; exact source and assessment comparison |
| Shape-before-lookup order from rejection contract | Reviewed inherited ordering | Stale identity masks malformed reasons; refreshed candidate dependencies |

## Completion boundary

Specification and matrix are saved first. Local controls, complete exchanges and candidate-derived diagnostics must still be supplied and checked; this text alone does not complete the reviewed task. Independent bounded review follows those checks. Remaining source/context predicates, V01–V16, four architecture groups, the initial profile, dependency order and fourteen decisions remain unfinished. All MC01–MC35/G1–G18 obligations persist.
