# Dimension-aware products for method prerequisites

24 October 2026. S2–S4; MC02/05/10/11/13/15/17/24/26/31 and G2/G3/G10/G13/G15/G16.
Preserve MethodRequirements/1 and its recorded frontend/binder. Do not silently
change existing context meanings or hashes. Version 3.59 remains provisional.

Question: can a versioned requirement fragment express return refund and tax
allocation products without losing units, entity/book/date context, source roles
or known/unknown meaning? Baselines are exact Fraction arithmetic, independently
derived small examples and the known-operand arithmetic in Core 0. Compare
semantic types as well as numeric results. Equal numerals alone do not pass.

Skeptical audit: multiplying two currency amounts is not a currency amount;
units times currency/unit must produce currency. Rate times amount has another
valid product. Dates and scope must remain compatible. A generic product that
copies a convenient operand's unit is wrong. A context string containing an
informal unit cannot be reliably parsed into dimensions. The old profile must
be preserved with an explicit, checked mapping or an unresolved mapping gap.

Before implementation, define the finite dimensional representation, dimensionless
values, scale treatment, identity/equality and context compatibility. Separate
physical/financial dimensions from entity/book/basis/measurement time and from
source role/admission. Audit any canonicalization; do not equate incompatible
source concepts merely because units match. State how monetary scale changes
are handled, and reject unprovided currency or unit conversions.

Implement a separate versioned successor only after that definition is checked.
Use canonical exact rationals and explicit unknowns; do not add solver inference,
division, rounded accounting amounts or probabilistic meaning by convenience.
Test units*price, rate*amount, dimensional mismatch, differing currencies/books,
signed values, zero with unknown, changed registry identity and exact replay.
Compare the refund/recovery/deferred relationships under their existing guards;
the arithmetic extension alone does not resolve the guards or full method.

Primary criterion: correct dimensional inference and exact known-value products
with preserved unknown/context boundaries and old-version immutability. A wrong
unit, lost context, implicit conversion or false method admission vetoes the
candidate and triggers repair. Core 0 arithmetic is a comparator for known
values only; its symbolic/observation semantics are not transferred. Check counts
and speed are explanatory. No superiority, full compiler, accounting acceptance,
real-company feasibility or production readiness follows.

Defaults/assumptions: integer dimension exponents are a finite design hypothesis;
units and scale need explicit caller declarations and evidence. The retained
return method is a discriminating example, not universal sector coverage.
All imported method assumptions and source precision remain separately visible.

Artifacts: data/accounting-master/dimensional-requirements-20261024/.
CPU-only deterministic tests; no external research claim, numerical sweep, GPU,
forecast experiment or paid review. Record the current commit, exact command,
input locks and result. Then audit guarded predicates and collection/state
conditions as the next dependency. S1–S5 partial; S6 held; S7 deferred.
