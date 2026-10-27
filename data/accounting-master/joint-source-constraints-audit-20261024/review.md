# Existing exact solver fits a narrower measurement question

24 October 2026. Inspected reconstruction_v1.construct/expression/from_p03 and
rational_solver_v1.Problem, Budget, affine, solve and domain_formula, together
with tests/test_accounting_p04.py and source-relations.interval_sum/evaluate.
The installed Z3 Python version reports 4.16.0. No solver is installed or changed.

The existing lower-level Problem/solve path already handles shared real variables,
exact rational coefficients, strict/open domain endpoints, conjunctions and
explicit finite budgets. It rejects unknown-by-unknown products. A feasible
cell retains a rational witness; an infeasible cell rechecks its extracted core.
Unknown or incomplete coverage remains distinct from infeasibility. A simple
conjunction with no finite choices or disjunctions requires one cell, avoiding
the wider combinatorial partition machinery.

The reconstruction constructor additionally assumes admitted records, journal
templates, opening accounts and economic state. Those are unavailable in the
partial source-state task, so using that constructor would invent obligations
or imply a historical admission the source has not earned. Reuse the lower-level
exact solver with an explicitly limited measurement problem instead.

The solver's disclosure_domain implements half-even rounding. The retained
partial-state hypothesis instead uses nearest ties away from zero, including
different signed endpoint inclusion. Therefore preserve the already supplied
exact interval endpoints and call domain_formula directly. Do not substitute
the rounding helper or silently change the source hypothesis.

The source relation interface already combines repeated observation coefficients.
That identity must become one solver variable across all selected relations.
Each relation still needs an explicit measurement-identity premise; a displayed
zero residual is not such a premise. Missing intervals or unasserted identities
produce unresolved assessment, not infeasible history. The full context must
match within an equation; no conversion or cross-period mapping is inferred.

## Evidence contract and defaults

The next repair tests conditional joint measurement consistency only. The
baseline is local interval compatibility and hand-solvable linear systems. A
feasible result requires independent Fraction evaluation of every original bound
and equation on the solver witness. Infeasible means the exact solver found no
assignment within the explicitly selected system and rechecked its core; that
is not a source/accounting-history verdict or an independently checked proof
certificate. Unknown/timeout/resource/unsupported outcomes cannot be promoted.

Budgets remain explicit, caller-supplied nonnegative integers. For a deterministic
conformance probe, use one cell/one assignment, no slots, 10,000 formula nodes,
5 seconds total, 1 second per solver check and 1,000,000 solver resource units.
These are convenience test bounds inherited in scale from P04, not a default
runtime policy. Zero budgets test refusal. Check actual witness arithmetic and
strict endpoint examples before any larger source integration.

No optimization, integer relaxation, probability assignment or forecast is
requested. Counts, elapsed time and local residuals are explanatory only. A
wrong witness, dropped shared identity, implicit premise or source drift vetoes
the candidate and triggers repair. Invalid harness/environment stops result
interpretation until repaired. The typed effect work remains valid independent
of this question.

| Decision | Primary criterion | Veto status | Uncertainty | Next action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Reuse existing exact solver through a limited new contract | Inspected solver supports required finite rational conjunction | Rounding helper mismatch identified and excluded | Generic input/source mapping and witness checks need implementation | Build conditional joint measurement assessment, then bind retained relations | Historical reconstruction, real-company executable state or solver replacement |

External web documentation retrieval returned no usable content in this pass.
The decision rests on inspected local source and recorded tests; no new theorem
or claim about upstream solver internals is imported from an unread source.
