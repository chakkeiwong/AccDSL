# Finite mixed-book authoring contract

24 October 2026. S2–S4; MC05/11/13/16/24/26/28; G2/G4.

The source lock pins 152 dependencies, including the exact original statement
requests and results, inspected lexical helpers, their local dependencies and
the pre-execution plan. The implementation adds no evaluator, imports, include
paths, expressions, callbacks or source-admission mechanism to authored text.

## Grammar and typed representation

Each declaration occupies one line and ends with a semicolon. Blank lines and
CRLF are accepted. Values are bounded JSON; rational amounts remain exact strings.
The header is shared_book followed by the SharedBookProgram/1 profile and name.
An explicit opening declaration names SyntheticReturnLeaseBook/1. Each scalar
or memory field is declared by its native field name and complete JSON value.
Fields may appear in any order but none may be omitted or repeated.

An accounts block contains one named account declaration for every native account.
A lots block contains named lot records. A leases block contains complete lease
members. Each block has an explicit end_accounts, end_lots or end_leases marker.
The three blocks are mandatory, including empty lot and lease collections.
After end_opening, an events block contains ordered event declarations naming
the return or lease module and its full record. The report declaration contains
four strings: native report profile, source-bundle digest, opening digest and
events digest. An end_program declaration terminates the program.

The typed record contains exactly profile, name and request. The request is the
unchanged six-field native request. The from_request, render and lower functions
preserve the full typed record. compile_program and compile_text check structure
and identity. execute_program and execute_text return the native report directly,
retaining every flag, refusal, trace, gross cash origin, classification, memory
field and unresolved statement obligation.

The report request digest is the semantic identity. Program identity additionally
includes its name. Text identity covers the exact UTF-8 bytes, including whitespace
and newline style. A renamed program has the same request digest; whitespace has
the same program digest. Digests bind supplied content, not external truth.

## Structural and semantic failures

Invalid JSON, duplicate keys, missing or extra fields, malformed rationals,
unsupported modules/methods, stale digests and omitted blocks fail compilation.
Declaration failures include their line number. Whole-source encoding, size and
nesting checks precede line parsing. All original lexical limits remain active:
1,000,000 bytes, depth 48, at most 32 tokens per declaration, strings at most
4,096 characters, at most 4,096 declarations and 20,000 portable data nodes.

Balance, funding, source premises, context eligibility, date ordering and tax
completion are execution questions. Structurally valid unbalanced openings,
unknown membership and duplicate event identifiers compile, then retain the
native result. No absent balance is inserted, no false premise is made true,
and no unknown is inferred from statement balance.

All 19 original requests are retained in the comparison. Sixteen belong to this
finite grammar and must reproduce their complete saved results. The tax-module
request is intentionally outside the grammar; the stale opening digest and
caller-supplied closing field are malformed requests. Those three are classified
as compiler rejections, not silently dropped or counted as execution matches.

## Audit and evidence limits

The skeptical audit retains the complete original report as comparator. Checks
of cash or balanced statements alone cannot pass. The inherited lexical limits
are reviewed engineering bounds, not ergonomic or scalability findings. Exact
round trips, malformed declarations and original-result comparisons are the
early diagnostics. Any dropped memory or changed native result vetoes this
frontend; parser defects require repair. There is no statistical comparison.
General module composition, authoring convenience, complete annual accounting,
actual source admission and production readiness remain unestablished.
