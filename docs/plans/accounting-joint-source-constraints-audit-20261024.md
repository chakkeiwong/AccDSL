# Audit joint source measurement constraints before solver work

24 October 2026. S2–S4; MC04/08/09/10/13/16/24/26/28; G1/G2/G3/G15.

Research question: under explicit measurement-identity and rounding assumptions,
do the selected source observations admit one shared assignment satisfying all
selected relations? Candidate: a finite exact rational linear constraint layer
over preserved observation identities, using existing reconstruction capability
where its semantics match. Baseline: existing per-relation interval compatibility
and scripts/reconstruction_v1.py, plus independently solvable small systems.

Inspect the solver and its tests, strict/open interval representation, precision
and source-relation contracts, typed contexts, missing observations and existing
result categories before implementation. In particular x=0 and x=1 can each be
locally compatible with x in [0,1], yet their conjunction is infeasible. Repeated
observation identities must refer to one variable, not independent intervals.

Evidence contract: promotion means exact finite joint measurement feasibility
or infeasibility under the declared assumptions, with a checked witness or
explicit explanation of the solver guarantee. Unknown/timeout/unsupported must
remain distinct from infeasible. Open endpoints, shared variables and optional
identity assumptions are primary correctness cases. Source/context drift,
unreviewed rounding assumptions, unsafe floating approximations or unbounded
solver commands veto interpretation until repaired. Candidate failures trigger
the next repair; they do not reject reconstruction research.

Default audit: display-only remains baseline, no invented rounding rule or
literal-dash zero. Any constraint activation, exact arithmetic solver mode,
timeout or size bound must have provenance, justification, failure mode and
early diagnostic. Do not change a numerical default or select a solver solely
because it is installed. Reuse exact arithmetic and existing frozen interfaces
where possible; no callback, dynamic objective or caller-supplied executable.

Explanatory diagnostics: individual residuals, constraint counts and runtime.
These cannot replace the joint criterion. A common assignment establishes only
the selected measurement equations, not legal/accounting history, uniqueness,
probabilities, unavailable state, causal economics or an executable Apple opening.
No stochastic superiority claim is intended.

First artifact: data/accounting-master/joint-source-constraints-audit-20261024/
with source/method inventory, precise mathematical contract, skeptical decision
and audited next implementation plan. Record local source hashes and environment.
Any external technical dependency claim requires inspected primary documentation
and local evidence where it affects the decision. CPU-only deterministic work;
no forecasting or paid review. Continue the smallest justified implementation
after the audit passes. S1–S5 partial, S6 held, S7 deferred, Version 3.62 not_ready.
