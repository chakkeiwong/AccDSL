# Pre-implementation skeptical audit

MC13/14/23/24/25/26/28/32/34/35. The plan uses the existing expression engine
and exact accounting consequences as its baseline. It introduces no new
arithmetic, empirical calibration, automatic financing or forecast objective.
Its main risks are lexical capture, erased call dependencies, evaluating unused
arguments unexpectedly, and excessive expansion. The design resolves these
with explicit parameter nodes, fresh identities, separate declared/effective
dependencies, demand-driven semantics and bounded graph/depth checks.

The demand-driven choice inherits the expression baseline and is tested using
unused division by zero and unknown values. Monomorphic signatures and size
limits are scoped convenience choices. No source argues that these limits or
types suit every company. Their failure rejects this bounded request, not the
research direction. Protected-source hash failure is a continuation veto until
the baseline is repaired or explicitly revised.

Evidence contract: exact inlining and complete policy/path/accounting equality
are primary criteria. Static refusals and predecessor integrity are vetoes.
Check counts and runtime are explanatory. A false comparison, missing dependency
or wrong units triggers repair. No scientific ranking, causal validity,
forecasting, whole-language acceptance or production readiness is concluded.
Artifact: focused tests, verification results, immutable source lock and run
manifest in this directory. Audit passes for bounded reference implementation.
