# Units, maturity and the meaning of evaluation

28 October 2026. C04; SIM-F061–065. Attempt01 passes 194 checks across eight
native programs and four altered-carry controls. These are conditional examples
and engineering checks. No empirical forecast or probability calibration occurs.

For F061, expressing a monetary residual in millions instead of dollars changes
an unnormalized sum of squares. Its minimizer moves from 1/2 to
1/(1+10^-12), almost 1. Rescaling the monetary normalizer with the residual
restores the same objective and minimizer 1/2. Exact square completion checks
the minimizers. This tests an inconsistent two-residual approximation; it does
not imply that scaling changes the solution of every exactly satisfiable system.

For F062, the supplied schedule borrows 20 on 31 December 2027 and pays 22 on
31 January 2028. The initial probe used an opening date inconsistent with the
reporting period and was correctly refused. The repaired example uses an
explicit one-day 2027 stub. The actual-days/365 rate 73/62 is chosen solely to
produce the stipulated interest 2 over 31 days. Accrued interest is 2/31 in
the stub and 60/31 in January. Native carry preserves principal, accrued
interest and contract memory; the next program starts from that exact opening.

With initial cash 3, the short report shows cash 23 and a continuing liability;
paying interest 2 and principal 20 leaves cash 1. With initial cash 1, the short
report shows cash 21. Interest settles, but principal repayment is refused
because only 19 remains. The unpaid principal stays 20. Both account maps
replay, and balanced carry mutations that erase debt are rejected. The event
schedule supplies maturity; no maturity is inferred from a debt balance. Reports
cover the stub and the period through 31 January, not complete fiscal years.

F063 reuses the retained, hash-verified historical debt case. Three histories
all reproduce the imposed historical interest 5; their stress interest is 5,
7 and 6. Reconciliation therefore does not establish which future occurs or
constitute out-of-sample validation. No probability is inferred from these
histories, and no actual historical source availability is newly asserted.

For F064, the stipulated uniform-alpha cash law has mean 89 and probability
7/10 of cash below 89.4. Equal mass at the two endpoints preserves mean 89 but
changes breach probability to 1/2. Four midpoint nodes give 3/4. A grid with a
node at the threshold gives different strict and inclusive probabilities. These
are exact consequences of supplied laws, not empirical forecast results.

For F065, completed nonbreach mass 0.6, completed breach mass 0.1 and unresolved
mass 0.3 give a known cash contribution of 62 and an unconditional breach
interval [0.1, 0.4]. The conditional mean among successful executions is 620/7;
the unconditional mean remains unavailable. If unresolved cash is explicitly
bounded between 0 and 100, mean bounds are [62, 92]. Without that assumption,
no finite mean bound is returned. Exact possible completions attain the bounds.
Dropping and renormalizing unresolved paths produces a different conditional
law; missing mass and unknown branches assigned a cash value are refused.

| Decision | Primary criterion | Veto status | Main uncertainty | Next action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain F061 | Normalized objective invariant under currency scaling | Raw loss changes the compromise | Appropriate economic scales | Keep units and normalizers explicit | Universal optimizer behavior |
| Retain F062 | Complete carried state and payment consequences agree | Shortfall and erased liability refused | Actual terms, rates and maturity | Bind real schedules before admission | Complete fiscal reports or actual market borrowing |
| Reuse F063 evidence | Historical fit coexists with different future outputs | Reconciliation cannot select a future | Actual histories and information cutoff | Keep validation evidence separate | Empirical forecast accuracy |
| Retain F064 | Exact threshold probabilities distinguish equal means | Mean-only validation misses breach error | Admitted probability law | Evaluate the requested distributional quantity | Real-company risk estimates |
| Retain F065 | Missing mass and conditional results remain explicit | Omission, false values and unlabelled conditioning rejected | Bounds on unresolved outcomes | Refine unresolved branches | General probabilistic execution service |

| Inference status | Finding |
| --- | --- |
| Hard veto screen | Period mismatch, liquidity shortfall, erased debt and invalid mass/value records refuse |
| Statistically supported ranking | None; all comparisons are exact supplied examples |
| Descriptive-only differences | Check and case counts describe tested scope |
| Default readiness | No numerical, accounting or forecasting defaults change |
| Next evidence needed | Actual terms and laws, broader module integration and independent validation |

Post-run red team: native replay establishes consistency with the authored
methods, not their suitability for a company. The repayment schedule and
probability laws remain assumptions. The setup failure was a repaired harness
error; no research-direction or global continuation veto fired. Continue module
interaction cases, source research and ordered reading from physical page 355.

Final verification matches all 1,179 protected hashes, including 997 frozen
release files. All 21 program-validator tests pass. The 40 original tasks,
114 acceptance rows, 156 clauses, 18 packages and 201 failure rows persist.
