# Typed expressions for a declared collection policy

A policy author can now calculate the collection fraction and installment
shares using a finite pure expression graph. Text and typed inputs describe
the same graph. The adapter passes its known dimensionless outputs to the
existing settlement generator, which retains responsibility for fraction
domains, named claims, operation dates and accounting scope.

Values are exact reduced rationals, strict Booleans or explicit unknowns.
Numeric types carry dimensional exponents and a context identifier. Addition,
ordering and equality require compatible types; multiplication and division
combine dimensions without converting currencies or aggregating entities.
A context-free dimensionless scalar can scale a contextual quantity. A ratio
of contextual quantities retains its context and therefore cannot silently
become a context-free policy parameter.

Static analysis checks every node, including unused nodes and both conditional
arms, for arity, references, cycles, types, context and canonical values.
Evaluation resolves forward references and performs exact arithmetic. A known
Boolean guard selects one arm. A valid but undefined calculation in the
unselected arm is not evaluated. An unknown guard remains unresolved, even
if the two arms appear equivalent; symbolic equivalence is outside this scope.
Logical and/or evaluate both operands and conservatively propagate unknowns.
They do not short-circuit or implement SQL truth tables.

Every output retains both its declared input dependencies and the subset
actually evaluated. An unselected arm's dependencies remain visible. A missing
input is invalid; a declared unknown value is unresolved. Known division by
zero is invalid, including an unknown numerator divided by known zero.
No unknown is replaced with zero, false or an inferred probability.

The retained collection example computes 1 - 1/10 = 9/10 and two shares of
1/2. Selecting the other declared branch gives 4/5. On the exact protected
second-year price-revision path, invoices total 384; reducing the fraction
from 9/10 to 4/5 reduces cash by 38.4, increases receivables by 38.4 and leaves
profit unchanged. These are consequences of explicit assumptions, not an
estimate of collection behavior.

The expression program, adapter and evaluated assumptions need their own
information evidence. Existing availability declarations for the direct policy
are not inherited by the new expression program. Every branch keeps temporal,
historical-execution, behavior and forecast admission false. Source maps,
portable record wrapping, general functions, dates, richer types, endogenous
event scheduling, module imports and empirical validation remain open.
