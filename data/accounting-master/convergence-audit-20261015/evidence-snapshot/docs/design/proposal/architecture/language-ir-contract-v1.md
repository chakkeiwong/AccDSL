# Portable financial records and authoring, proposed version 1

The portable representation is the meaning exchanged between extraction,
reconstruction, accounting and reporting. Text notation and typed constructors
are two ways of proposing those records. Neither authoring path can create an
accepted source reading, an accounting permission or a probability merely by
constructing a value. This contract addresses MC02–MC14 and MC23–MC27, especially
G2/G3/G12/G15/G18. `platform-contract-examples-v1.json` supplies specified examples;
the companion calculation checks finite consequences, not a compiler.

## L1. Representation and version boundary

A `Record` has exactly `kind`, `schema`, `key`, `revision`, `body`, and
`dependencies`. `kind` and `schema` name a registered, versioned record
definition; `key` is its stable, schema-scoped logical name; `revision` is a
nonnegative JSON integer (never Boolean). `body` conforms to that exact schema.
`dependencies` is a set of typed `Ref` values. A `Ref` has exactly `kind`,
`schema`, `digest`; its target digest covers the entire target record. Links
inside a body are also typed Refs and must occur in dependencies. Additional
dependencies are permitted only with a declared role in the body's schema.
The dependency graph of a submitted closure must be finite and acyclic. A new
receipt refers to its request and prior state; the prior state never refers
forward to that receipt. Stable business keys may refer to one another as names
without creating content-reference cycles.

Each schema declares required, optional and nullable fields separately, and
rejects unknown fields. Omission and null are not synonyms. Unknown scientific
or accounting content uses `Unknown {reason, obligation_refs}`; an absent required
field is an invalid record. A record with unknown content can be retained but
cannot satisfy an operation that requires that content. A `Candidate<T>` is
distinct from `Admitted<T, view_ref, decision_ref>`. Admission requires checking
the referenced decision in the requested immutable view, including ancestors;
possession of the wrapper alone is insufficient.

Quantities use reduced exact `Rational {n,d}` with signed base-ten numerator
text and positive denominator text: no leading plus or zeroes, `gcd(|n|,d)=1`,
zero `0/1`. Decimal source tokens are converted by their base-ten value, never
through binary floating point. Integer metadata and integer counts remain JSON
integers. This separates the old Core 0 phrase “all numeric values are rational”
from record revisions, ordinals and bounded counts. Approximate results instead
use `Approximation {decimal_text, method_ref, error_description, environment_ref}`;
they cannot be substituted into an exact operation without an explicit
approximation policy and its provenance.

New record digests use `SHA256(UTF8("accdsl.portable.v1/" + schema) || 0x00 ||
canonical(record))`. Canonical JSON is UTF-8, sorted ASCII object keys, no
insignificant whitespace and no floats, NaN, infinity, duplicate keys or invalid
Unicode scalar values. Strings retain their decoded code points; JSON escapes
and literal Unicode for the same code point are equivalent. Composed and
decomposed Unicode are distinct unless a named transformation explicitly maps
them. Identifiers are ASCII; financial labels and quoted source text may be
Unicode. This deliberately replaces implicit global NFC normalization in the
exploratory Core 0 proposal: source spelling must not be silently changed.
Raw source identity always hashes original bytes, outside this record encoding.

A `BlobRef` is a distinct tagged object with exactly `kind="blob"`,
`algorithm="sha256"`, `digest` (64 lowercase hexadecimal digits), and
`byte_length` (nonnegative integer, never Boolean). It resolves to exact bytes,
not to a portable record. A `Submission` record has body exactly
`{blob_ref, media_type, transport, decoder_ref}`, with decoder_ref null when
decoding is unavailable. An OperationResult.submission_ref is a typed Ref to
this record; it is not a record digest falsely assigned to raw bytes. Record
dependencies list record Refs; schema-declared BlobRefs are a separate required
byte-closure obligation checked alongside them.

Native unknowns are decoded through a named LegacyImport adapter. A nullable
value with a required explanatory reason maps to an Unknown carrying that
reason and its source/obligation Refs, while retaining the original native
packet/inner/outer reasons in the import. A non-applicable null remains an
explicit NotApplicable variant, never Unknown or zero. Under native C09,
required=true with a null route requires both nonblank inner and outer reasons;
neither replaces the other. A contextual reason on a known value is annotation,
not an unknown. Missing or malformed native fields reject before conversion.
This mapping preserves source statements without giving the converted value
admission in a new view.

Array order is meaningful except for schema-declared sets. In this version,
`dependencies`, module declarations by key, context dimensions by axis key, and
the explicit IR `all_of`/`any_of` operand sets are canonical sets; reject duplicate
keys or members before sorting by canonical UTF-8 bytes. All other arrays,
including event schedules, journal lines, source spans and diagnostic priority
sequences, retain order. Rational reduction and set sorting occur during typed
construction; a purported canonical wire record violating them is rejected.
There is no general algebraic simplification, alias folding or equivalence proof
in hashing. Hash equality supports byte identity under the chosen encoding, not
economic equivalence or source truth.

For byte-level interoperability the serializer emits literal valid non-ASCII
Unicode scalars in UTF-8. Escape only quotation mark, reverse solidus and control
characters U+0000–U+001F: use `\b`, `\t`, `\n`, `\f`, `\r` for their five named
controls and lowercase `\u00xx` for the remainder. Do not escape solidus. Integers
use minimal base-ten text, with no leading plus, zeroes or negative zero. Input
escapes are decoded before canonical output. Object keys are ASCII and ordered
by unsigned ASCII bytes. These rules, set normalization and rational reduction
fix one byte string for every valid typed record; arbitrary JSON writer defaults
are not part of the definition.

Existing `accdsl.replay.v1/*`, uncertainty fixture and Core 0 digests retain
their original encodings. `LegacyImport {format, original_bytes_ref,
original_id, decoder_ref, portable_ref, comparison_ref}` connects them to a new
record. A migration must prove the stated field/value correspondence and retain
both IDs. A two-decimal acquisition fixture is not a general two-decimal money
rule. No historical digest or receipt is rewritten to fit this proposal.

When conversion produces multiple records, portable_ref points to an
`ImportMapping` record with exactly `{outputs, field_mappings}`. Outputs is a
nonempty schema-declared set of typed Refs. Each field mapping has source_path,
target_ref, target_path and relation (`equal_decoded_value` or
`explicit_conversion`); the latter additionally requires conversion_method_ref.
The LegacyImport comparison_ref covers every output and mapping. This supports
A6's CorrectionBasis plus InvalidationReport without overloading a single Ref,
and records branch_id → branch_key as an equal-decoded-value field mapping.
No mapping authorizes source facts or accounting treatment in a new scope.

## L2. Financial types and context

The primitive types are Bool, Int, Rational, Text, Date, Timestamp, Ref<T> and
explicit tagged Unknown. Containers are Option<T>, homogeneous List<T>,
schema-declared Set<T>, records and tagged unions. Bool is not Int. Dates use
valid Gregorian days; timestamps require an offset and retain the original
precision. Timestamp comparison uses the time contract's interval interpretation.

The financial types include `Money<currency>`, `Quantity<unit>`,
`Rate<convention>`, `YearFraction<calendar, convention>`, `InstantValue<T>` and
`Flow<T, [start,end)>`. Every contextual value carries a Context Ref identifying
legal entity, book, perimeter version, basis, currency/unit, economic instant
or reporting interval, calendar and a set of dimensions. Source locators,
reported display scale and reading provenance are retained alongside the value;
they do not silently change its arithmetic magnitude.

Addition, subtraction and comparison require equal financial types and
compatible contexts. A source scale is applied once during reading, while its
original value and spelling remain available. Entity, perimeter, basis,
currency, time or dimension changes require a named transformation with input
and output contexts, method, assumptions and evidence. `sumOver` removes an
axis only under a pinned disjoint/exhaustive partition. `convert` requires a
dated rate, purpose and measurement method. No label similarity converts IFRS
into US GAAP; the standards method must supply a transformation or report that
the comparison is unresolved.

An opening and closing stock cannot be added as flows. Deriving an interim
flow by annual-minus-prior-interim requires compatible interval endpoints,
perimeter, basis and revision view. Precision does not create an error tolerance:
nearest-rounding intervals require source support or an explicit admitted
rounding assumption. A displayed 100 at unit scale may conditionally denote
`[199/2,201/2)` only under the declared tie convention; unknown convention
remains unknown, and different tie rules have different endpoint inclusion.

## L3. Expression and model records

An Expression has `key`, `type`, nullable `context_ref` and one discriminated
operator payload. Literal carries one typed value; ref names one declaration;
negate/not take one operand; add/subtract/multiply/divide/comparisons take two;
`all_of`/`any_of` take nonempty operand sets; field takes a record and field key;
call carries a pinned operation Ref and ordered arguments. Each operator's
payload excludes the other payloads. Boolean expressions remain formulas when
their shared symbols are unknown; Unknown values are never coerced to false.

Multiplication by a dimensionless scalar preserves a financial type. A rate is
not dimensionless: simple interest requires principal, annual rate and an
explicit year fraction. Division requires a nonzero denominator; inability to
establish nonzero is an unresolved precondition, while an established zero
gives undefined mathematics. Backend admission classifies the expanded formula,
not the spelling of a function call. Symbolic products are not rational-linear
merely because the surrounding function has an accounting name.

A Module contains declaration sets for contexts, sources, readings,
interpretations, assumptions, symbols/domains, constraints, choices,
contracts/events, measurements, rules, scenarios and reports, plus a package
lock. Every symbol has one uncertainty category, type, domain and admission
dependencies. Reusing its key means the same unknown in every linked expression.
Global constraints apply to every alternative; a choice-local constraint stays
inside that named choice. Alternatives are joined under the history contract's
specified union/intersection, not silently intersected or independently selected
account by account. No declaration automatically creates a probability measure.

An OperationSignature declares input/output types, context relationships,
preconditions, postconditions, failure codes, effects, capability and method/
authority dependencies. Effects are one of pure calculation, candidate
construction, source acquisition, review proposal or requested transaction.
An accounting rule proposes an assessment/journal/delta; it cannot commit.
Opaque callbacks or arbitrary host-language execution are not portable IR.
Extension packages must declare record schemas and signatures, export hashes
and the unsupported-operation response; unknown required semantics cannot be
ignored. Names are qualified by package and version; no mutable “latest”.

The portable initial exact fragment permits rational affine constraints over
real unknowns plus explicitly finite discrete choices and bounded integers.
Negative rates are permitted when the operation's economic domain permits them;
the P03 nonnegative-rate restriction is not inherited globally. Unsupported
nonlinear, unbounded discrete, distribution or calendar methods return the
requested operation and missing capability. Partial linearization is a new
assumption-labelled model, never an exact solution of the original formula.

## L4. Compilation and matched authoring

`CompileRequest` supplies source kind (text or typed construction), source bytes
or typed Module, schema/profile refs, full package lock, evidence/time view and
requested capability target. Compilation performs, in order: strict decode and
source spans; name/import resolution; dependency/cycle checks; static types and
context checks; admission-layer checks; expanded-operation capability analysis;
canonical record production. Each stage returns all independently decidable
diagnostics in stage/path/code order. Dependent checks are `not_evaluated` with
their blocking diagnostic; they are not additional guessed type errors.

`CompileResult` returns candidate IR, source map, unresolved input obligations,
capability analysis and a validation receipt bound to every input. Invalid
structure/types produce no executable IR. A well-typed module can have unresolved
financial inputs: return a retained candidate and `execution_admitted=false` for
affected targets. Compilation does not call a solver, choose a history, post a
journal or turn source acceptance into method eligibility.

The bounded text notation retains Core 0 lexical/precedence rules and its
registered declarations. Unsupported syntax is diagnosed; textual support is
advertised per declaration/signature. Typed constructors produce the same
abstract declarations; arbitrary Python objects or lambdas are not accepted.
Both frontends pass through the same typed IR admission rules. Text positions
are Unicode code-point half-open ranges in retained source bytes after a named
decode; typed positions are constructor paths. Source maps are outside model
semantic identity, but their own content hashes bind the exact authored source.
Formatting and comments may change a source-map ID without changing the model.

LX01 specifies matched text and typed declarations for debt 100, shared unknown
floating share x in [0,1] and interest `100*((1-x)*1/20+x*7/100)`. Both propose
the same financial expression and its explicitly conditional stress assumption.
Its expanded interest is `5+2x`; endpoints are 5 and 7 and x=1/2 gives 6.
The shared domain is continuous, not two equally probable cases. LX02 changes
7/100 to 9/100, so the upper endpoint becomes 9: frontend agreement alone would
miss a shared wrong constant, hence the independent arithmetic. LX03–LX08 reject
currency/context mixing, absent admission, symbolic nonlinearity at an exact
linear backend, duplicate keys and unknown imports. These are proposed expected
exchanges; the document calculation is not evidence of a completed compiler.

## L5. Alternatives and consequences

The old small text compiler and typed library are useful feasibility evidence,
but neither settles the portable representation. JSON records are proposed
because they are inspectable and already match retained evidence; a binary
encoding is permissible as a lossless transport with a specified decoder.
Embedding executable Python is rejected as the governing representation because
it leaves side effects, evaluation order and unknown handling outside a shared
contract. XBRL remains an evidence interchange, ledgers carry concrete postings,
and inference languages implement selected methods; none by itself preserves
all the required evidence, joint histories and accounting admission layers.
No authoring, performance or maintenance superiority has been measured.
