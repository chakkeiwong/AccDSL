# Approximation limits: SIM-F052/053/054/055

28 October 2026. C04; MC08/09/10/11/13/18/28/33/34.

Question: can numerical support loss, proposal sampling or an error interval
be mistaken for the declared exact family, probability or funding decision?
The baseline is each original failure row and the supplied examples in
simulation/09-approximation.tex. Reuse rational_solver_v1 for boundary witnesses.
This is exact finite arithmetic and solver conformance, not a sampled method
comparison or a particle-filter implementation. No training or tuning occurs.

Skeptical audit: current weight ESS can return to the particle count after
resampling while persistent-type diversity collapses. Keep the original family
separate. Oversampling a tail changes the measure unless P/Q weights and full
target support are checked. An empty sample does not identify probability zero.
A point estimate does not classify a guard when its certified error interval
straddles the threshold. No successful command can close these source/model
assumptions or turn hypothetical weights into admitted real probabilities.

Research intent ledger: test the omitted-support/weight/threshold mechanisms.
Promotion criterion is exact agreement with a separately derived finite target
and concrete negative controls. Lost family, wrong measure, false guard decision
or missing Unknown vetoes the affected result and triggers repair. Corrupted
protected inputs or an invalid harness stops this unit pending repair. Counts,
ESS and runtime are explanatory; ESS alone neither promotes nor stops research.

F052 retains common/rare static types with supplied masses999/1000 and1/1000.
A fixed grid of100 resampling ordinates is an explicit possible systematic
resampling outcome, not a random experiment. Copies may be all common and have
uniform weights/ESS100; the rare type remains in the underlying family. A
separate deterministic support audit nominates repair. It does not implement or
validate rejuvenation, nor require every finite Monte Carlo sample to contain
every positive-mass type.

F053 uses target tail1/1000, proposal1/10 and severity1000. Enumerate the two
outcomes and several full-support proposals using Fraction arithmetic. Weighted
expectation must equal target1; unweighted proposal loss is100. A two-draw
enumeration distinguishes ordinary and self-normalized estimators, including
their finite-sample expectations. Zero proposal mass on positive target mass
is invalid. No superiority or variance ranking is requested.

F054 calculates exact no-event probability(999/1000)^100, expected loss1 and
the one-sided95% zero-event upper endpoint. Bracket that endpoint with exact
rationals by monotone bisection, verify endpoint signs, and check coverage of
the complete one-sided binomial upper-bound procedure at the declared p by
exact enumeration. The fixed n, iid Bernoulli assumption and alpha1/20 are
supplied examples; adaptive stopping, dependence and model errors remain outside
scope. A confidence bound is not a posterior probability or an exact feasible
set. No observed sample is fabricated.

F055 uses required funding100 and supplied error bound1. Test intervals fully
above, fully below, straddling and touching the threshold. The guard is c>=100:
lower=100 is safe, upper=100 with lower<100 remains unresolved. Query exact
solver feasibility for c>=100 and c<100; preserve zero-budget Unknown. A supplied
error bound is conditional evidence, not a proven surrogate calibration.

Artifact: company-state-approximation-boundaries-20261028/attempt-01 contains
all inputs, exact arithmetic, solver formulas/results, original rows, source
hashes and manifest. Run CPU-only with python3 -B and output directory specified.
Premortem: deterministic sample arithmetic may be misreported as observed
performance; finite conformance may be mistaken for production correctness.
Result notes must keep both limits explicit. Original statuses and frozen
releases stay unchanged. No global requirement or forecasting claim follows.
