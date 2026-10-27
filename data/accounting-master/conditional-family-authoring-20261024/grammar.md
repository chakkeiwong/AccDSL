# ConditionalFamilyExchange/1 grammar and interface

24 October 2026. A closed authoring profile for five existing conditional record
interfaces. This does not add methods or extend their semantic scope.

## Lexical rules

Input is a Python str or bytes containing strict UTF-8, without BOM. UTF-8 encoding
must succeed without surrogate replacement. Maximum source bytes: 1,000,000.
Statements occupy individual LF-separated lines. Empty ASCII-whitespace lines
are allowed. CR is permitted only as trailing CR in a CRLF line ending. Spaces
and tabs separate tokens. No comments, continuations, expressions, interpolation,
executable code or file/URL imports are supported. Each declaration ends with one
semicolon. Extra non-whitespace characters after it reject.

Keywords are ASCII words. Quoted strings, objects, arrays, integers, booleans and
null use JSON syntax. Duplicate JSON keys reject at every depth, including escaped
aliases. All floats (including exponent notation), NaN and infinities reject;
canonical rational values remain quoted strings. Integers are bounded and valid
only where the selected semantic profile permits them. Semantic field validation
rejects control characters, and the transport additionally rejects Unicode line
separators and surrogate code points. JSON values have at most depth 48; the
whole exchange has at most 20,000 nodes and strings at most 4096 characters.
Source nesting is checked before JSON decoding. Noncanonical rational strings,
dates, types, schema fields or budget values reject under the original validators.

## Grammar

J denotes one strict JSON value, S a JSON string. Each listed declaration occupies
one line; braces here indicate repetition, not literal syntax.

    conditional_exchange "ConditionalFamilyExchange/1";
    budget J;
    { family S S;
        { profile-specific declaration }
      end_family; }
    select S S;
    end_exchange;

The first family S is a local name, the second its exact semantic profile.
The select strings are a previously completed family name and its exact canonical
definition SHA256. The budget and selection occur exactly once. Budget precedes
families; selection follows all complete families. No declaration follows end.
Family names are unique. Parent references name preceding completed families;
unknown/forward/cyclic references reject. All supplied families must be reachable
from the selected family; unused definitions reject rather than vanish silently.

JointMeasurementConstraints/1 declarations:

    observation S J;
    equation J;

TemporalMeasurementConstraints/1 declarations:

    observation S J;
    relation J;

For both profiles, ordered equation/relation lists and keyed observation maps
start empty under the grammar. Their semantic validators enforce nonempty required
collections and the exact nested record fields. Repeated keys or list IDs reject.

ConditionalMonetaryHistory/1 and TypedAffineHistory/1 require each singleton once:

    scope J;
    value_type J;
    opening_date S;
    dates J;
    balance_premise J;
    obligations J;

They also accept domain-specific collection declarations:

    account S J;
    memory S J;
    template S J;
    event J;
    measurement J;

TypedAffineHistory/1 additionally accepts state_constraint J. Collection maps and
lists start empty; zero state constraints means none supplied or checked, not a
claim that none are economically needed. Required missing semantics remain in the
explicit obligations list. Event order is declaration order and is never sorted.
Dates, type records, intervals, premises and coefficients are the complete original
profile records, so the parser cannot infer prices, conversions or support.

HistoryMeasurementAttachment/1 requires:

    use_history S;
    use_measurements S;
    obligations J;
    { binding S J; }

References embed complete definitions, never prior results, witnesses or digests
alone. The existing attachment validator requires ConditionalMonetaryHistory/1
and TemporalMeasurementConstraints/1 parents. TypedAffineHistory/1 is supported
as a standalone family; this exchange does not invent typed attachment semantics.

## IR, dispatch and errors

lower(source) returns exactly profile, definition, selected_digest, budget.
definition is byte-independent JSON-compatible data equal to the selected Python
definition, not a solver formula or witness. Local authoring names disappear only
after reachability validation and complete parent embedding. The canonical digest
is the existing sorted-key compact UTF-8 identity of the full semantic definition;
arrays, including events, retain order. No selection digest covers the budget;
the explicit budget remains part of the exchange and assessed request.

validate_exchange checks all exchange fields, exact digest and the original
profile validator, then normalizes map keys using the existing canonical JSON
encoding. This preserves semantic dictionary equality and every array order.
The old solver reports contain insertion-order-dependent variable names and
constraint order; those diagnostics are not byte-identical under equivalent map
permutations. The new exchange therefore uses one canonical order for both typed
records and text, and validates replay against that exact normalized definition.
Independent witness checks also operate on the complete original constraints;
no map permutation changes the intended family. Near-budget solver outcomes are
not claimed invariant to arbitrary historical request ordering.
assess_exchange delegates the normalized definition to the unchanged assess.
assess_source is lower followed by assess_exchange. decode_exchange accepts a
strict JSON byte/text exchange with identical validation. render(exchange) emits
deterministic declarations which lower to an equal exchange. Canonical emission
sorts map keys only, preserving every ordered collection. It expands attachment
parents into preceding named families.

Malformed syntax raises core.Invalid (a ValueError), with source line where
available. Semantic validation errors retain their original reason. Invalid UTF-8,
size/depth/node overflow, duplicate declarations, trailing content, unavailable
profile, bad selection or inconsistent definitions reject before solving. Valid
missing-premise inputs remain unresolved; explicit zero budgets remain unknown.
Source parsing never executes text or resolves source references externally.

Conformance artifacts retain authored source, exact expected exchange, semantic
status and result. Existing independent replay is used for history/attachment;
measurement witnesses are checked against full original constraints. Text/record
equivalence cannot establish accounting admission or independent implementability
of the wider DSL.
