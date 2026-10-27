# Explicit nested contract source

26 October 2026. The skeptical audit in the source plan passes with an explicit
order-preserving grammar. This is a bounded frontend to the frozen evaluator.

A source file begins with selected_term_state and its profile, then names each
field or nested block. The grammar has dedicated blocks for state structure,
admission stages, semantic components, projections, grouped queries, captures,
template slots, guarded requirements, collection constraints and bindings.
Every algorithm-bearing component is written inline. There is no resource
import, generic record/list escape or contract JSON literal.

Small context, exact type, expected schema and scalar data use the existing
JSON token grammar. Predicate expressions use the preserved parenthesized
expression parser. Requirements expose guard, predicate, dependencies and
failure policy as separate declarations. Maps use named entries in authored
order; sequences use explicit repeated entries. The frontend preserves that
order, including empty maps/lists. It never sorts the selected declaration.

Each directive has an absolute UTF-8 byte span and physical line number.
Only LF splits lines; CRLF is accepted without splitting Unicode line-separator
characters inside strings. Nested blocks accumulate spans over their full
body. Typed component validation wraps failures at the narrowest component
available from the frozen validator; lexical and grammar failures point to
their exact token/declaration. A located block may contain multiple declarations;
the frontend does not invent field precision for an opaque validator error.

Compilation returns the typed contract and locations. Assessment additionally
requires the explicit compilation memory definition, state, population evidence, the independently supplied reviewed
selection and the existing call binding. Compilation never derives review
authority. All accounting, source, opening and future-command flags remain
false. The preserved evaluator owns expression and financial semantics.

Implementation budget: one complete bounded conformance pass after focused
grammar/Unicode diagnostics; repair only observed defects and retain attempts.
No benchmark, stochastic experiment, network operation or product runtime is
part of this work.

Focused diagnostics found and repaired two source issues before the full pass.
Unbounded greatest queries need explicit null upper_bound. The inherited JSON
renderer sorts keys, changing 355 ordered mappings in the first alpha fixture;
this frontend uses order-preserving JSON tokens and an order-preserving
expression renderer with the unchanged parser/evaluator. It does not alter
the frozen source modules. An initially incorrect collection-validator import
was also corrected to the actual engine.validate entry point.

Compilation uses a separately supplied memory definition. A malformed snapshot
must be rejected by state assessment, rather than silently redefining the
source's compilation environment. The source wrapper therefore takes both the
compilation definition and the supplied state. State/schema mismatch remains
the preserved evaluator's responsibility. This separation will be tested with
the structural corruption fixtures.
