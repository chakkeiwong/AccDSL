# Reusable pure functions for company policy expressions

25 October 2026. S2–S4; MC13/14/23/24/25/26/28/32/34/35.

## Question and evidence contract

Can explicitly typed, finite pure function declarations reuse the checked
expression semantics without silently introducing behavioral solving, host-code
execution or different unknown/type rules? Comparator: the frozen
CompanyExpressionsDraft/1 evaluator and its manually expanded policy example.
Primary criterion: expanded graph and full policy/path/accounting consequences
agree with the baseline, including selected/unselected failures and unknowns.
Veto: wrong units/context, missing or duplicate names, recursion/cycles, unsafe
expansion, altered predecessor bytes, or implicit conversion of an unknown.
Check counts are explanatory only. Passing establishes this bounded language
extension, not a general simulator, empirical policy validity or forecasting.

## Skeptical audit and defaults

The current expression engine already rejects cycles and checks both conditional
arms. Reimplementing arithmetic would create an unnecessary baseline mismatch;
lower calls to its existing graph instead. Functions are monomorphic, pure and
lexically scoped. Every definition, including unused definitions, receives
static checks. Calls use demand-driven expression evaluation, matching inlined
expressions; an unused argument need not be evaluated. Declared call arguments
remain separately inspectable from dependencies that reach the result.

Explicit bounds on functions, depth and expanded nodes are convenience safety
limits, not performance evidence. Boundary cases must check each limit and
reject before uncontrolled expansion. Exact fractions, Boolean/unknown rules
and entity/currency contexts inherit the reviewed expression contract. The
extension must pin and verify the predecessor implementation hash before use.
No imported callable, recursion, date function, behavioral equation system,
automatic event scheduling or financing rule is admitted. Those remain gaps.

## Execution

1. Preserve the source-recovery findings and complete coverage before changing
   the active phase. Keep all 53 obligations, six interactions and 46 operations.
2. Specify function signatures, lexical names, expansion/source maps, dependency
   reporting, refusal conditions and exact baseline comparisons.
3. Implement an optional compiler/reference interface and focused adverse tests.
   Verify nested calls, repeated uses, capture refusal, return/argument types,
   unknown branches, recursion, resource bounds and unchanged financial outputs.
4. Record the run and review. If checks pass, integrate only checked conclusions
   into a protected manuscript successor and refresh complete master coverage.
5. Select the next substantive dependency across the full remaining program.

Research intent: candidate is reusable pure functions; expected failures are
scope capture, lost dependencies or exponential expansion. Promotion is exact
semantic correspondence; continuation veto is an invalid baseline or unavailable
required source. A candidate failure triggers local repair, not abandonment of
the simulator. No forecasting or product implementation starts from this plan.
