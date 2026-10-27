# Matched authoring for the declared company program

Question: can users author the same multi-period company sequence as readable
text and as a typed data record, with exact program and execution equivalence?
MC13–18/23–26/28/32/34/35; S2–S5 bounded reference. Comparator is the checked
DeclaredCompanyProgram/1 record and engine, not a second accounting implementation.

Inspect the existing shared-book and annual-program lexical rules first. Specify
an exact finite grammar with separate company opening, named registry/methods,
statement mapping, typed event inputs, report cutoffs and explicit carry policies.
Use hash-checked imports for large reusable schema/method/opening declarations
where the existing frontend uses them; never claim those imported definitions
were authored in text. Keep the dependency manifest and unresolved source facts.

Primary criterion: text parse/render/compile round-trip equality plus exact engine
results for the same two charts and multi-period commands. Veto: invented defaults,
forward future-state hashes, unchecked imports, silently ignored fields, unknown
values converted to zero, different failure prefix, hidden Python callbacks or
raw serialized JSON passing as a full language design. Parse errors retain offsets;
structural errors precede execution; runtime refusals match the engine. Counts and
runtime are explanatory. No DSL superiority or accounting completeness claim.

Before coding, write the full grammar, import boundary and default audit. Include
negative cases for duplicate declarations, unknown keys, altered digests, malformed
numbers/dates, missing policies, reordered commands, unknown findings and stopped
programs. Preserve earlier languages and frozen evidence. After recording, integrate
and refresh coverage; select the next substantive corporate method/note gap using
the phase catalog and requirements rather than returning to forecasting.
