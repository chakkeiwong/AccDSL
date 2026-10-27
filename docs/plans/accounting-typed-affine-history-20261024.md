# Typed affine histories with explicit constraints at every event

24 October 2026. S2–S4; MC05/08/09/10/11/13/16/24/26/28/35.

Question: can one conditional history preserve monetary balances, physical
quantities and typed event sizes jointly, while rejecting an intermediate path
that violates explicitly supplied economic constraints? The baseline is the
unchanged ConditionalMonetaryHistory/1 and its fixed-opening reconstruction
comparator. Reuse MethodRequirements/2 dimension/context/scale algebra and the
exact rational solver. This is a distinct state-semantics dependency, not another
authoring wrapper or a real-company reconstruction.

Skeptical audit passes for this restricted question: existing memory staging
preserves structured known records, and monetary derivation supports typed fixed
products, but the recent conditional family restricts all unknowns to one money
type and checks no intermediate state conditions. Both capabilities are useful
comparators rather than proofs that the missing joint family already exists.
Closed statements can hide a temporary inventory shortage. A parser alone does
not resolve that question. General nonlinear methods and candidate admission
remain larger dependencies with missing inputs; no new solver is justified yet.

Proposed profile TypedAffineHistory/1 has one monetary book, typed rational
opening memory, a type per supplied event template, typed fixed coefficients,
dated finite events, typed snapshot measurements, and optional explicit state
constraints. Each state constraint applies at the opening and after every event,
including separate same-day events in their supplied order. Its premise is
mandatory for a conditional result. Omission means that constraint is unchecked,
not that inventory or cash is automatically unrestricted in the target economy.
Preserve explicit target obligations and selected assumptions.

Before scalar lowering, check each coefficient times event/field type equals the
destination/measurement type exactly, including context and scale. Reuse the
existing type product, require one book context, and reject implicit conversions.
Monetary posting coefficients balance for each template. Units may be divisible
rationals only under the authored example; integer lots are outside this profile.
Coefficients are fixed rational assumptions, not functions of unknown state.
Products of unknowns, endogenous events, variable prices, generic contracts,
accounting authority and actual-company execution are explicitly unsupported.

Research intent and evidence contract:
- Candidate mechanism: typed affine transitions plus constraints at each state.
- Primary pass: exact independent Fraction replay, unchanged monetary comparator,
  preserved complete typed definitions, and expected infeasibility for a balanced
  closing path that sells before stock is available.
- Promotion veto: type/context/scale erasure before validation, dropped prefix
  constraints, fabricated source assumptions, changed frozen inputs, or a forged
  replay accepted. Repair these before recording a result.
- Continuation veto: corrupted required comparator or unavailable required exact
  solver. A rejected candidate triggers the next repair, not direction rejection.
- Explanatory only: counts, runtime and solver-selected witness values. No ranking,
  performance claim or completeness claim follows from them.
- Not concluded: source admission, accounting compliance, general operational
  feasibility, native method execution, nonlinear completeness or whole DSL.

Default audit: dimensions and exact scales inherit a checked local type contract;
this is a reviewed reuse for typing, not an accounting interpretation. Finite
supplied events and affine coefficients are declared restrictions. All example
numbers are synthetic authored test inputs, with provenance. Explicit inventory
nonnegativity is a conditional modeling assumption, not a universal rule. Same-day
order follows the authored list; daily measurements see all events that day.
CPU only, bounded existing solver budgets, no stochastic inference or benchmarks.
Compare fixed-price stock quantities with hand arithmetic before larger tests.

Implement a new scripts/typed_affine_history_v1.py and focused tests, retaining old
code. Document the complete record/typing/lowering/error interface and resource
limits in data/accounting-master/typed-affine-history-20261024/design.md. Keep strict
text/byte authoring on the next dependency list. Run focused unit and old-history
regressions via python3 -B; create checked cases, dependency lock, manifest, result
and replay. Record checks once after repairs. Update controls and reassess the next
ready dependency without claiming full phases closed or starting forecasting.
