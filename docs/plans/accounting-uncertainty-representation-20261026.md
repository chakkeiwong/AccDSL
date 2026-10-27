# Uncertainty representation and controlled expansion

Date: 26 October 2026. Follow-up to the user's question about explicit trees,
learning and an exploding number of possible histories. MC08–12, MC14,
MC18, MC24–26, MC29–30 and MC33–35.

Plan: inspect existing symbolic-family, refinement and grouping definitions;
check targeted primary treatments of compact logical representation, belief
updates and particle approximation; record an implementable recommendation
with an algebraic example and explicit limits. No runtime implementation,
long diagnostic, empirical experiment or method ranking is authorised here.

Skeptical audit passes with these restrictions: a graph does not magically
remove exponential worst cases; shared syntax is not statistical independence;
identical current reports do not justify merging future states; identical
forecasts do not automatically justify discarding information needed for later
learning. Unknown fixed facts are not redrawn each period. Hypothetical
simulated observations do not update the actual evidence view. Company
management may know more than the analyst, so decision information must be
specified actor by actor. Prior uncertainty requires no invented probabilities.

Evidence contract: compare with current chapters 5–7 and 9, not an invented
tree-only baseline. A recommendation passes if its exact versus approximate
meaning is explicit and its scope follows from a checked derivation, existing
design or inspected primary text. Unjustified factorisation, clairvoyant
decisions, lost learning dependencies or discarded unresolved alternatives
veto the affected recommendation. Example arithmetic is explanatory, not a
performance or validity claim. A source gap narrows its claim rather than
stopping independent design work.

Material choices: symbolic joint families are an existing design baseline; a
shared immutable graph is a proposed representation, with build/query cost as
its failure mode; weighted particles are optional only under an explicit
probability model, with branch extinction as a failure mode; a one-period
linear rate-reset example is a teaching model whose limits are maturity,
hedges, nonlinear clauses and different reset dates.

Deliverable: docs/design/research/uncertainty-representation-20261026.md.
Supporting sources and inspection records will be retained under
data/accounting-master/uncertainty-representation-20261026/. Update the
requirements and checkpoint additively; keep the active master plan and frozen
manuscript unchanged.

Completed: the design note distinguishes world/evidence/actor knowledge,
symbolic storage, query-driven refinement, learning-preserving compression
and approximation. Three primary sources are retained with technical anchors.
The exact affine/covenant example and local references are checked; current
source-clearance and general algorithm-selection limits remain explicit.
No engine implementation or experiment campaign is claimed.
