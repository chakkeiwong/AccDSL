# Verification repairs

The first control failure expected an empty provenance string to reach semantic
validation. The inherited lexer rejects empty string tokens first. The test now
expects that existing diagnostic; no parser behavior changed.

The next control expected a token span from the nested invariant parser. That
protected parser supplies a declaration span. The test now verifies the entire
translated declaration and its exact parent-source bytes/line/hash. A separate
nested opening-parser control checks the precise offending token, since that
parser supplies token locations. Neither error was hidden by weakening the
location bounds or by inventing a more precise location.

The repaired full run passes. No financial implementation or frozen evidence was
changed for these repairs. Current checks are deterministic source correspondence
only, and do not replace independent accounting or reader review.

The first passing run is preserved in attempt-01. Two additional controls edit
the actual opening equality and claim nonnegativity predicates while retaining
the independent reviewed selection. Both fail selection correspondence. The
final run has 32 controls and 787 assertions; the underlying implementation is
unchanged. The additional run strengthens the evidence beyond residual-text
edits and does not revise the profile's scope.
