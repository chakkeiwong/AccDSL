# Text authoring for repeated-operation company paths

23 October 2026. S3/S4; MC13–16/23–26/28. The closed typed path already exists,
but the earlier text frontend covers the single-operation annual profile only.
Extend its line-oriented, semicolon-terminated convention to initial-year and
continuation blocks, repeated operations and named allocations.

## Skeptical audit and evidence contract

Question: can a reader author the existing repeated-operation path as text and
obtain exactly the same typed input and execution? Baselines are the five
portable complete/partial/revision paths and the newly materialized settlement
policy path. The parser must implement their existing schema, not introduce new
economic assumptions. A JSON dump in a text block is not the intended frontend.

Primary criterion: serialize/lower exact round-trip for every input, identical
canonical identity and trusted execution result, with ordering, unknowns,
canonical rationals, claims and asset IDs preserved. Named allocation lines
must bind an already declared collection or supplier-payment operation. Initial
opening data cannot be authored inside a continuation. All fields required by
the existing schema must be supplied; no silent defaults or missing values.

Promotion vetoes: dropped fields, duplicate declarations, duplicate identities,
unknown operation kinds, unbound allocation lines, truth/string coercion,
noncanonical money, silently changed operation order, code execution, source
file access from parsed text or round-trip mismatch. Missing protected bytes
are a continuation veto for dependent comparison. Syntax failures trigger
repair; they do not reject the DSL direction. Counts and performance are
explanatory. Passing is bounded frontend equivalence, not full financial
language design, accounting correctness, source admission or parser security
certification against resource-exhaustion attacks.

## Assumptions and smallest checks

| Choice | Provenance and rationale | Failure mode | First diagnostic | Status |
|---|---|---|---|---|
| One declaration per line, semicolon terminator | Prior annual frontend; preserves familiar authoring | Quoted spaces, semicolons or hashes lost | Escaped-name round trip and malformed-line refusal | Inherited local convention |
| Explicit initial/continuation blocks | Existing path schema | Re-authored later openings | Forbidden continuation source/context/assets | Required boundary |
| Separate allocation declarations | Existing claim-based payloads | Allocation bound to wrong event | Missing, duplicate and wrong-kind target cases | Design hypothesis |
| Same exact rational/truth syntax | Existing interpreter | Implicit numeric conversion | Reject decimals, unreduced fractions and quoted booleans with wrong value | Protected convention |
| No expression evaluation or file inclusion | Non-executable typed inputs | Text selects arbitrary code or sources | Reject unknown directives; verify parser purity | Required boundary |

Implement in data/accounting-master/company-text-20261023. Publish a complete
three-year text example and concise grammar/reference. Keep parsing separate
from source access, temporal admission and execution. The verifier uses trusted
local modules and archived sources. Save schema lock, examples, checks, code
hashes, run manifest and result; read-only replay by default. Review the text
as an author would read it. General policy syntax, conditional branches,
interim periods and broader sector methods remain explicit residuals.

Audit verdict: proceed. After this step, integrate the coherent set of exchange,
information, policy and text examples into a protected manuscript successor,
then check preservation, build and the affected rendered pages.
