# Exact original debt-family failure discriminators

28 October 2026. C04; MC08/09/10/18/19/20/28/32. Targets: SIM-F005,
SIM-F007, SIM-F009 and SIM-F014 from the unchanged201-row register.

Question: does the existing declared fixed/floating debt family preserve
nonidentification and joint cash/interest constraints, and distinguish a
resource-limited query from infeasibility? Reuse core0_frontends_v1, the
existing from_p03 adapter and rational_solver_v1. Read the existing borrowing
source and independently authored borrowing expectations. No new financial
solver, empirical forecast or actual-company source is needed.

Skeptical audit: Northstar's tax/working-capital scenario has different cash
numbers, so it is not the original cash95-minus-interest discriminator. Use
the exact simple-debt fixture: principal100, initial fixed/floating rates5%,
historical interest5, cash95; later supplied floating rate7% and fixed5%.
Source syntax alone observes principal, so add the historical interest
constraint explicitly and retain it with the native family. Repeated identical
interest observations cannot become independent probabilistic evidence.
The continuous fixed/floating family must not be reduced to its two endpoints.
No accounting-method or population completeness beyond this fixture follows.

Evidence contract: compare native family outputs and feasibility to exact
rational derivations. Both endpoint histories satisfy principal100/interest5;
historical interest cannot identify composition. Under the supplied rate
change, interest plus closing cash equals95 throughout the family; the pair
interest7/cash90 must be infeasible although both marginal values occur.
Repeated pre-reset interest5 must retain both endpoints and an interior
mixture. An explicit zero-cell budget must return unknown/unresolved coverage,
never infeasible, for the same problem with retained feasible witnesses under
the regular budget. Primary criterion is all these exact predicates.

Vetoes: compiler rejection, adapter/domain mismatch, solver unknown at the
ordinary small budget, lost feasible alternative, invalid bounds or false
infeasibility. A veto triggers harness/implementation investigation and a new
retained attempt. Runtime/check count are explanatory only. No method ranking.

Defaults/assumptions: values and rate timing come from borrowing.acc and
borrowings.json; provenance is synthetic and explicit. Exact rational arithmetic
and unchanged native constraints are reviewed choices for this finite check.
Budget10 slots/10000 nodes/100 assignments/100 cells/10000ms/1000ms per solver/
1000000 rlimit reuses the bounded p03_family caller as a diagnostic budget,
not a new default. Zero max_cells is a deliberate control, not a timeout
simulation. If it cannot complete the base query, stop that result and repair.

Artifacts: company-state-original-debt-failures-20261028 under
data/accounting-master; source-locked input/IR, full native results, compact
checks, exact original rows, run manifest and decision note. Preserve all
original statuses and distinguish these four inspected discriminators from
all201 failures or full company execution. Update the current disposition
supplement and checkpoint only after successful checks.

Attempt review: attempt-01 used CompileResult.valid instead of the actual ok
property and failed before the solver. Attempt-02 exposed a harness syntax
mistake: native distinct (the Z3 encoding of !=) is unsupported in this
bounded fragment, so Unknown was a correct refusal rather than infeasibility.
Retain that unsupported control; establish equality by separately excluding
the supported strict-less and strict-greater cases. Native compiler, adapter
and solver remain unchanged. The earlier attempts and original question remain.
