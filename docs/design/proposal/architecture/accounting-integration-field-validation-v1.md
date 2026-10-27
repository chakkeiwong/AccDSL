# Integration field validation — proposed supplement v1

This bounded specification addresses MC08, MC13, MC25, MC34 and MC35 with
G4/G18 interactions. Its comparator is the corrected integration-v2 fixture and
the independently accepted rejection exchanges, including retained R06 replay.
Those files remain unchanged. This supplement specifies field validation; it
does not establish accounting authority, implement an endpoint or accept P16.

## Question, evidence and stopping condition

Can every integration-added input and assessment field, including nested source
packets and dependent references, be validated without losing intentional
unknowns or disclosing a receipt for an invalid submission? Acceptance requires
an explicit inventory, required/null and type rules, located predecessor support,
and an observable disposition for each predicate. Missing rows, changed
predecessor bytes, contradictory controls, implicit coercion and premature
receipt disclosure require repair. Hash and check counts establish document
consistency only. The known whole-architecture failure does not invalidate this
subsection. Stop after the matrix, matched examples, fresh checks and P16 records.

The skeptical audit passes for this scope: facts, versions and committed-state
baselines stay matched; no proxy is a promotion criterion; there is no stochastic
comparison; standard-library checks suit the environment. Source/method-context
assessment is separate. Assumed field values cannot prove accounting eligibility.

## Validation phases and observable outcomes

Preserve the accepted order: parse, dependencies, shape, source_versions,
bindings; then identity lookup, freshness and semantic assessment. Parsing
rejects duplicate keys at any depth. Dependency validation checks availability,
exact bytes, original digest domain and reference kind. It traverses recognizable
references only; malformed reference shapes produce shape findings, never guessed
targets. Correctly shaped unresolved references produce dependency findings.
Source versions are opaque strings compared exactly after source packet shape
validation. No latest-version substitution is allowed. Binding checks compare
verified material only. Within a phase retain independently decidable findings
sorted by field path and reason code; stop before subsequent phases.

Input rejection preserves raw submission/dependency bytes, reports stage/path,
sets request, assessment, diagnostic journal/delta, receipt and observed state to
null, and sets commit_status=not_committed and additional_commit=false. Identity
index, committed journals, selected state and committed receipts stay unchanged.
No lookup or accounting assessment occurs. J01–J10 already specify these exchange
consequences and are reused rather than copied.

Output checking has a separate boundary. Shape, reference and consistency checks
precede assessment publication. A producer defect yields
ASSESSMENT_OUTPUT_INVALID, retaining the validated request but publishing no
assessment, journal, delta, receipt or observed state. It remains not_committed,
additional_commit=false, with unchanged committed domains. This is not evidence
that the acquisition is ineligible. Candidate output bytes and field diagnostics
remain diagnostic evidence. Consumers check these same predicates before
admitting received assessment records.

## Alternatives and default audit

Explicit validation distinguishes malformed fields from unresolved facts.
Deferring it until accounting inference can treat a missing Boolean as false or
retrieve an unrelated receipt. Coercion changes bytes and versions used for
identity. A future extensible schema needs a reviewed version and explicit
unknown-field identity rules. Closed records, ordered conditions and integer
record versions are inherited preservation baselines. Opaque source versions
come from the accepted typing repair. Finite enums and packet shapes are proposed
for this acquisition profile, not universal accounting defaults. Early checks
target type confusion, lost unknowns, source substitution and inconsistent
outputs. Actual-instrument classification, historical admission and lifecycle
methods remain separate obligations.

## Reading the field matrix

The companion matrix inventories 299 paths across all seventeen corrected
exchanges and their referenced C01–C10 packets. It includes containers and
inherited interaction fields so a missing nested obligation remains visible.
An asterisk means each array element, not an unconstrained property name.
Each row identifies its required/null behavior, type, shared predicates,
validation stage, observable failure and an exact retained example. The union
of immediate child paths defines a closed object's fields; the conditional
route_findings and KnownBool variants override unconditional requiredness.
Source packets remain UTF-8 documents: the ASCII restriction on record strings
must not erase their existing typographical Unicode source citations.

A well-formed unknown is distinct from a malformed field. C05's missing upstream
rationale and C07's unsubstantiated incrementality retain null values with
reasons and can yield unresolved findings. C03's null contractual date when the
entity is not party to the contract is not-applicable, not an unknown Boolean.
C09 retains both valuation routes even when one route already selects branch
(a). Its not-required equal-price case preserves null route values as
not-applicable. Source packet versions remain opaque strings; record versions
remain integers. These categories cannot be exchanged by coercion.

The fixed dossier and decision-rule pins identify this finite profile. Shape
checking of a supplied packet does not validate its accounting assertions.
C01.within_retained_window, C04 policy eligibility and C05 classification
rationale remain stipulated inputs whose authority and context need separate
assessment. This slice neither derives those claims from prose nor promotes
them because their types are valid.
