# Ordered bounded claim expansion

26 October 2026. Evidence contract: accounting-ordered-assessment-expansion-20261026.md.
Skeptical audit passes only with explicit order identity. Native assessment
loops over the current Python claim map; canonical JSON digests ignore object
order. The proposed call therefore includes an explicit ordered list of keys
and its digest. The list must cover every actual claim exactly once. Reordered
keys produce different operation lists and construction identity even if the
resulting state is financially equal. No order is inferred from a canonical hash.

OrderedMethodExpansion/1 stores a complete checked scalar base template, a map
pointer, declared row-field types, explicit row-output templates and an ordered
suffix-operation list. The base template must have an empty operations list;
the expander fills it once before the scalar constructor validates the complete
method. No arbitrary destination patch is exposed. Map pointer resolves against
the actual book memory. Declared row fields must exactly cover each row; row
leaf types must match the book memory types, including escaped keys. Empty maps
are checked against the supplied typed map definition, not skipped as vacuous.

Each expression is a closed node: typed literal, row field, current key, event
metadata id/date, typed known event input, typed if, date_lt/date_le or the
deterministic operation_id primitive. Objects and arrays explicitly construct
operation data. Conditionals validate both branches before evaluating; no
unreachable bad branch is ignored. Comparisons require two date values; if
branches have the same exact scalar type. There is no general arithmetic,
string interpolation, callback, recursive function or source evaluation.

Operation ids use an explicitly supplied prefix and offset. For row ordinal i
and row-template ordinal j, id=prefix+decimal(i*m+j), where m is the declared
row-template count. Prefix is literal, index is supplied by the bounded expander.
The suffix list follows all row writes and has authored fixed ids. Final typed
memory validation rejects duplicate ids or invalid writes. A fixed map key is
data, not a pointer fragment; the retained pointer compiler escapes it.

The conformance template reproduces four writes per claim: assessed=true,
assessment_date=event date, assessed_remaining=row remaining, overdue=row
remaining only if due<event date, otherwise exact zero. A final cursor write
uses end_exclusive. Native checks for cursor/window/end/date eligibility remain
explicit outside this constructor. This is the retained state-only convention,
not an impairment measurement or a new accounting rule.

Call binds template, state, full event and explicit order digests. Returned
construction includes all of these plus the resolved operations and scalar
constructor evidence. Scope limits are inherited 4096 nodes/48 depth/one MB and
native operation limits; they are finite reference limits, not scalability
evidence. Unknown event inputs return unresolved and produce no request.

Primary criteria are complete native request/result equality, hand-checked
strict/inclusive boundary consequences, exact order binding and full malformed
coverage controls. Count/runtime is explanatory. Hidden source dependency,
different complete request, lost unknown, malformed unreachable branch or
reordered call reusing old identity vetoes and triggers repair. Native-disabled
construction demonstrates that the comparator is not called by the constructor.
No source/accounting admission, portable eligibility contract, product release
or E3 inference follows.
