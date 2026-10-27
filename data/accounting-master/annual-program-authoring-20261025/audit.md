# Annual-program authoring audit — 25 October 2026

MC13/14/15/23/24/26/28/32/35; G2/G4. Compare matched text and typed authoring
against the frozen AnnualProgram/1 evaluator. Existing shared_book_authoring_v1
separates structural compilation from financial execution, retains raw and
semantic digests and has closed named declarations. Its request shape is the
older report/opening/events interface, so it cannot simply be relabeled annual.

Use a new frontend with a named program, an explicit digest-bound imported root
and ordered operation blocks. The root is supplied through a local in-memory
registry keyed by its canonical request digest; compilation never reads a path,
executes a model or infers new source facts. A raw JSON wrapper would hide the
operation/field contract; use named scalar fields, declaration-map entries and
ordered list entries instead. Nested typed records remain data-only values.

The existing strict lexical layer rejects duplicate JSON keys, floats, invalid
UTF/control characters and malformed line endings. Its 1MB/depth48 limits are
more restrictive than the evaluator's bounds; preserve and disclose them as a
frontend convenience limit rather than silently widening them. An imported root
is checked by the evaluator's portable bounds and exact digest, without putting
the entire nested historical record into source text.

First validate closed structural fields, exact rationals/dates and known/unknown
declaration types. Economic missing information, authorization truth, available
cash, lifetime ids, assessments and tax applicability remain evaluator checks.
Unknown information can compile and then return unresolved. Pure compilation
must work under a test that forbids calling the evaluator.

Primary criteria: exact lowered request, text/typed result equality, lossless
round trip, explicit source spans and semantic/raw digest separation. Negative
controls include duplicate fields and ids, invalid rationals/dates, unknown
fields/kinds/imports, stale digest, invalid UTF and financial prefix failures.
Wrong lowering, lost provenance, hidden evaluation or disagreement across
frontends veto evidence and trigger repair. Counts/runtime are explanatory.
No complete-language, actual-company or accounting-admission claim.
