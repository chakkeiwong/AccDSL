# Integration record-version repair — proposal supplement v1

This supplement corrects the version types in the seventeen saved acquisition
assessment examples. It addresses MC08, MC13, MC25, MC34 and MC35, with G4/G18
interactions. The integration contract remains incomplete. The earlier bounded
acceptance covers the eligibility dossier and decision supplement; it does not
accept the integration, this repair or the whole P16 proposal.

## Question, comparator and stopping condition

Can the record-version defect be corrected while preserving every condition,
finding and relationship in integration-v1? The comparator is the retained
`accounting-integration-fixtures-v1.json` on exactly the same synthetic facts.
Passing this slice requires valid record-version types, exact condition-source
version resolution, closed references, reproducible digests, unchanged semantic
outcomes, and no receipt aliases. Changed source packets, lost provenance,
changed findings, changed predecessor bytes or a new posting permission veto
acceptance. Hash and check counts are explanatory, not accounting evidence.
The known whole-architecture failure does not invalidate this bounded repair.
Stop after corrected examples, finite checks, integrity evidence and checkpoint
updates. Full rejection exchanges are the next task, not part of this slice.

The skeptical audit found the expected baseline defect: all seventeen new
evidence records violate the inherited version rule despite passing the old
finite calculation. Comparing different accounting facts would obscure the
repair; relaxing that rule would instead change the specification. The matched
comparison below isolates the correction. No stochastic or performance claim
is made. The calculation uses only the standard library on CPU, without device
detection, runtime modules or a new product test suite.

## Types, ownership and identity

As specified in `accounting-records-contract-v1.md`, a record's `version` and
`sequence`, where required by its kind, are JSON nonnegative integers; booleans
are excluded. The same integer restriction applies to numeric `schema_version`
fields inside records, with the required value fixed by the applicable record
schema. Do not coerce strings, booleans, nulls or fractional numbers. The
top-level fixture format's string schema identifier and a receipt's string
`encoding_version` are format labels, not numeric record versions.

`ConditionRef.value_version` is a separate, nonempty opaque JSON string. Resolve
the pinned CaseRef, then compare it exactly with the selected condition packet's
`version`, also a string. Preserve case, whitespace and spelling; do not parse,
trim or order these strings. The condition producer owns that source label.
The evidence-record version does not replace it. Pinned source bytes, the case
identifier, condition identifier and exact source-version string jointly locate
the input. A missing or unequal source version cannot resolve by selecting a
latest packet. Typing and resolution failures must prevent acceptance before
receipt lookup; complete rejection request/response examples remain pending.

The corrected fixture maps `integration-E01` to integer 1, through
`integration-E17` to integer 17, only at evidence-record `version`. These numbers
are deterministic synthetic identifiers, not evidence of chronological
revisions. Event business identifiers and all source condition versions retain
their original strings. The old fixtures remain available as defective evidence.

The corrected file keeps the fixture format identifier, request schema version
2 and canonical record domain `accdsl.accounting.integration.v1/<kind>` plus
NUL. Content encoding remains sorted-key ASCII JSON with compact separators,
`ensure_ascii=True` and `allow_nan=False`. This is correction of content under
the existing record schema, not a new schema or migration. Recompute evidence,
admission, eligibility input, request, assessment, submission and response in
dependency order. Submission raw text must contain the corrected request bytes;
its digest consequently changes too. Unaffected records retain exact identities.
The companion map records every old/new record digest, kind and evidence-version
mapping, including unchanged rows. It is provenance for this repair, never a
receipt-alias table or permission to rewrite committed history.

## Preserved inputs and expected outputs

`accounting-integration-fixtures-v2.json` supplies the seventeen corrected
exchanges. `accounting-integration-typing-map-v1.json` supplies their exact
reference map. `accounting-integration-typing-cases-v1.json` supplies bounded
type examples: zero and positive integers pass, while a numeric string, the old
label, booleans, negative integer, fractional number, integral-valued JSON float,
null and a missing field fail. Separate cases exercise exact and mismatched
source-version strings. These examples do not constitute complete rejection
exchanges or generalized added-field validation.

All C01–C10 values, reasons, provenance, scope and source versions remain pinned.
The June contexts, source-label aliases, nine valuation pairs, combined adverse
findings, assessment outcomes and no-posting behavior remain unchanged. Repeated
assessment retains the corrected request and assessment digests without a
receipt. Exact R01–R06 CaseRefs and R06's committed replay remain unchanged.
Corrected request digests differ from both their defective predecessors and
retained committed requests: the same event identity cannot confer receipt
equivalence. All four committed domains remain identical before and after each
exchange.

## Alternatives and default audit

| Choice and provenance | Status and justification | Failure mode and early check |
| --- | --- | --- |
| Inherited integer record versions | Reviewed bounded baseline; correct the examples to match it | Accidental bool/string coercion; explicit type cases and scan of all required version fields |
| Opaque condition-source strings | Explicit clarification of retained packets | Integer conversion or normalization loses identity; exact pinned packet comparisons |
| Synthetic mapping 1–17 | Convenience choice for these fixtures | Mistaken historical ordering; declare no ordering claim and preserve source labels |
| Existing schema and digest domain | Existing contract, unchanged representation | Reusing old digests after edits; recompute closure and reject aliasing |
| Matched facts and outcomes | Experimental control for the correction | Semantics drift hidden by rehashing; inverse-map comparison of every record and exchange |

Allowing arbitrary string record versions is a credible alternative for a future
schema, but it conflicts with the rule these examples claim to follow and would
need separately reviewed consumer and ordering semantics. Keeping the defective
strings as accepted examples leaves a contradiction. Correcting the records is
the smallest change. Replacing opaque condition strings with integers is not a
repair: it changes pinned source identity without authority.

The finite calculation independently evaluates the typing predicates, resolves
source packets, checks canonical identities and complete local reference
closure, reverses the declared mapping to compare semantic content, and derives
assessment results from the unchanged input conditions. It records the expected
seventeen baseline failures separately from candidate acceptance. Its manifest
pins inputs, command, environment, plan, result and output. The separate
integrity record checks preserved files and final architecture references.

| Decision | Primary criterion | Veto status | Main uncertainty | Next action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Submit typing repair for bounded review | Actual finite report must pass the matched comparison | Any changed fact, broken reference or receipt alias blocks acceptance | Full added-field validation is not supplied | Inspect corrected examples and retained defect | Complete integration or accounting validity |
| Retain P16 partial | Four contract groups, profile and fourteen decisions remain open | Whole-architecture check remains incomplete | Source/method-context assessment and failure exchanges | Scope malformed, stale-version, binding-disagreement and digest-corruption exchanges next | Runtime, forecast validity, product readiness or human acceptance |

The strongest alternative explanation is that the examples consistently preserve
an erroneous accounting assumption. This repair checks type and representation
consistency only; the retained AASB/source and synthetic-fact limits still apply.
A changed condition, unsupported type exception or alias to a committed receipt
would overturn the repair's conclusion. All MC01–MC35/G1–G18 obligations remain.
