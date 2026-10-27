# TypedHistoryMeasurementAttachment/1

The closed definition contains profile, history, measurements, bindings and
obligations. The complete TypedAffineHistory/1 and TemporalMeasurementConstraints/1
definitions remain embedded. Their variables occupy disjoint namespaces until
explicit mapping equations connect them; neither parent may be replaced by a
selected result or witness. Every original typed history constraint, including
the opening and post-event state constraints, survives variable renaming.

Each binding has kind (snapshot or movement), quantity, terms and premise.
Quantity equals the selected observation's declared quantity. Each term has
kind (account or memory), field and coefficient. Coefficient has value (exact
rational) and type. Its product with the field's complete type must equal the
observation's value type, including context, dimensions and scale. Observation
context equals history book context. Fixed conversion/valuation coefficients
are explicit authored assumptions, never guessed prices or implicit conversions.

A snapshot uses an explicitly declared snapshot date and includes all events
on that date in their preserved order. A period movement sums only event effects
in the exact half-open period, excluding opening stock. Its civil-date endpoints
follow the existing monetary attachment contract. Scalar lowering is used only
for already type-checked mapping arithmetic; the complete typed history's
build_problem supplies the actual parent constraints.

Every parent observation, interval and equation survives even if unmapped.
Unmapped observations create target obligations; supplied parent and attachment
obligations persist. Missing parent or mapping premises prevent solving;
conflicting premise identities reject. Satisfying a proposed mapping does not
admit its source interpretation or establish actual company state.

Every witness is independently replayed by the original typed history and
temporal measurement checkers. Fraction arithmetic then recomputes each mapping
from original snapshots/event effects, and all compiled constraints are checked
under the same witness. Alternative valid assignments are acceptable. Named
infeasible constraint sets are rechecked; zero/exhausted budgets remain unknown.
All admission and execution flags remain false.

Bounds retain the parent input/formula/solver policies with <=256 combined
variables and <=4096 mapping terms. Python validation and replay are bounded
by definition/formula limits but not hard-preempted by the solver deadline.
This is a deterministic reference profile, not a solver performance or default
claim. Broader method/state composition, actual source/legal facts, nonlinear
coefficients and full accounting eligibility remain separate work.

The initial test fixture incorrectly removed the history parent's mandatory
measurement declarations. It was repaired to retain broad explicit intervals.
Two test expectations were corrected to the actual parent event_id and
conditionally_feasible API. No frozen parent was changed. All 19 focused tests
now pass, including exact units/cash, state-shortage, dimensional valuation and
compensating scale conversion, same-day snapshots, unresolved mappings, unknown
memory, forged results and separately feasible but incompatible parents.
