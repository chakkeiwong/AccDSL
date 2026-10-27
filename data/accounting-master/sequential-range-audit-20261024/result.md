# Exact sequence range and attainment audit

24 October 2026. 118 exact checks across10 probes pass. The existing rational
solver can supply branch bounds for the inspected complete native sequence;
its output is not already a whole-sequence bound. Every attained endpoint
replays through both original native transitions, and separate exact solver
questions reject better values and check whether the endpoint itself exists.

The complete sequence has intermediate inventory in[65,80], terminal inventory
exactly60, intermediate profit in[-19,-4], and terminal profit exactly16.
These are deductions from the full restricted formulas, not extrema of selected
witnesses. Making recoverable-value endpoints5 and20 open makes both intermediate
inventory bounds unattained. Selecting inventory65 fixes its range to{65}.
Allowing sale proceeds in[0,100] gives terminal profit[-24,76]. Unfunded settlement
leaves an empty family, which has no numeric bounds. Zero cells yields unknown.

One branch alone gives intermediate inventory{80}; the other supplies the
global lower bound65. Thus even fully certified bounds on the first branch
cannot be promoted to bounds on the complete sequence. Aggregate minima/maxima
require every branch to be proved empty or supplied with certified endpoints.
Global endpoint attainment holds when at least one extremizing branch attains
that bound. The envelope alone does not establish that every interior value
is feasible when branches or observations create gaps.

Inspected rational_solver_v1.py separates feasibility, closure optimization,
no-better verification and original-domain endpoint attainment. Its generic
unbounded result relies on the optimizer's infinity indication. The current
native family has finite explicit intervals for all numeric variables and
affine outputs within each arm, so an unbounded query result would contradict
this fragment and must not be accepted by the first range interface. This
restriction avoids importing an unreviewed general infinity certificate.

| Decision | Primary criterion | Veto status | Main uncertainty | Next action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Implement finite typed sequence bounds | Complete formulas, original replay and exact endpoint tests agree | No endpoint or branch mismatch found | General unbounded/nonlinear families and interior gaps | Execute accounting-sequential-outcome-range-20261024.md | Witness ranges or convex envelope equal the feasible set |

The strongest alternative explanation is shared solver/code structure. Native
full-state replay and independent Fraction arithmetic constrain that risk;
independent implementation acceptance remains pending. Version3.69 is unchanged.
No whole requirement closes. S1–S5 partial,S6 held,S7 deferred.
