# Exact supplied-input monetary derivation

MethodMonetaryEffects/1 defines numeric input declarations, an ordered list of
named calculations, an exact account registry with one cash account, signed
postings and ordered gross cash flows. Every field is closed. References resolve
only to original inputs or earlier calculations. Calculations carry their exact
result type and transitive original-input dependencies. An input cannot be
shadowed. All types and fields are validated before any value is evaluated.

The evaluator reuses frozen v1 canonical scalar and tagged known/unknown binding
validation, and v2 dimensional product rules. Its additional binary minimum
requires exactly matching types, contexts and scales. Addition and subtraction
have the same restriction. Multiplication combines declared dimensions and scales
using the existing algebra. There is no currency conversion, automatic scale
normalization, rounding, interval solver, callback or imported executable code.

Every account in this selected profile has the same money type: one explicit
currency dimension to power one. Coefficients can be negative. That preserves
signed debit-positive effects without claiming that a negative inventory amount
is financially admissible. Rational operations, journal aggregation and cash
aggregation check the coefficient bound. Size/entry/node/depth/bit limits are
implementation limits and return invalid with an explicit reason.

Unknown input dependencies propagate with their original reasons through all
arithmetic, including zero multiplication and minimum. Independent known
calculations remain visible as diagnostics. Any unresolved calculation, posting
or gross flow withholds the complete journal and flow proposal. For all-known
effects, require balance and cash-flow agreement; preserve zero flows and their
original order. Derivation leaves all admission/execution/commit flags false.

The retained examples use declared constructed projections into a shared event
measurement context. That test fixture does not establish an exact raw pointer
binding or resolve dates and accounting bases. Those obligations belong to the
next transition composition. The native comparator is recomputed from each
preceding retained state and event; its saved journal is not used as an oracle.
Negative and unknown cases distinguish arithmetic from preconditions. A purposely
wrong carrying formula remains balanced, demonstrating why exact measurement
agreement and state/domain checks cannot be replaced with journal balance.

The ten retained comparisons include settlement, sale, NRV cap/zero, zero
handling, fractional units/proceeds, zero proceeds, unknown NRV and unused unknown
tax evidence. Independent hand-derived coefficients check debit signs and the
minimum. Tests also cover currencies, dates, scales, dimensions, forward/cyclic
references, collisions, exact dependencies, malformed values, unsupported
operators, missing registries, journal balance, gross cash and finite limits.
