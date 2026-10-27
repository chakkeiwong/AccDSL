# Eder compactness and graph-law dependency

27 October 2026. C3/C5; MC13–18/29–35. This is a bounded technical
dependency review, not acceptance of a company simulation method.

## Source identity and inspected scope

Manu Eder, *Compactness in Adapted Weak Topologies*, arXiv1905.00856v1.
Local file: sources/Compactness in adapted weak topologies Eder (2019).pdf.
SHA256: db52774ea82eb95b44ad6c2cb071ef06f3c76d44dfc0eb4d54fbafe3582a48fd.
Fourteen physical/printed pages; arXiv submission2May2019, manuscript
date3May2019. Physical1–14 were inspected, including definitions, proofs and
references. Pages12–13 were rendered and visually checked after text extraction
made bars and primes ambiguous. No numerical implementation is adopted.

The retained arXiv abstract page, sources/eder-arxiv-20261027.html, was
retrieved from https://arxiv.org/abs/1905.00856 on27October2026. It lists
v1 only and no withdrawal, correction or journal-reference notice in the
inspected submission/metadata fields. This is a bounded edition/status check,
not exhaustive correction clearance. Citation counts, venue metrics and an
independently matched published edition are not available in this review.

## What the proof supplies

The base spaces are Polish, the horizon is finite and the probability laws
have the required finite pth moments. Section2 defines the measure-dependent
modulus using self-couplings with small first-coordinate displacement.
Lemmas2.4–2.9, including the Lusin argument in2.7, and Theorem2.10 show
that relative compactness within the graph-law subspace requires both ambient
relative compactness and uniform decay of that modulus. A general weak limit
of graph laws need not be a graph law. These conditions cannot be replaced by
ordinary path-law convergence alone.

Theorem3.2 and Lemmas3.3–3.6, physical9–12, supply the integration-map
compactness step used by the all-adapted-topologies paper. Lemma3.3 concerns
relative compactness of a set of laws on X × P_p(Y) and of its integrated
laws on X × Y. Its converse uses marginal compactness and compactness under
barycentric integration, not continuity of disintegration. Lemma3.6 states
the tightness-plus-pth-moment-tail criterion. Lemma3.5 constructs compact
sets of probability laws with uniformly controlled moment tails; lower
semicontinuity of the integrals over compact-set complements makes its
constraint sets closed. Thus the proof addresses relative compactness in the
stated Wasserstein spaces rather than a quantitative compression rate.

Physical13, Lemma4.2, is the source of Lemma3.10 in the all-adapted paper.
For a fixed graph law mu and epsilon, it chooses a law-dependent delta.
Couple a nearby nu back to mu by eta, compose gamma with eta, apply the
graph-law modulus to the resulting self-coupling, and use Minkowski to obtain
rho_Y(gamma) < epsilon. The argument requires both W_p(mu,nu) < delta
and rho_X(gamma) < delta. It supplies neither a common linear Lipschitz
constant nor uniform control over an arbitrary collection of graph laws.

Theorem4.1, physical13–14, then controls compatible gluing at a pair whose
second law is graph-supported. Its constructed coupling shares the appropriate
middle marginals, and Lemma4.2 bounds the remaining coordinate displacement.
Continuity is on the domain where these marginal compatibilities hold; it is
not an unrestricted continuity statement for arbitrary conditional kernels.

## Literal notation repair in the compactness proof

On physical12, Lemma3.4 sets L = (M × Nbar) union (Mbar × N).
The subsequent complement expansion and integrals drop the bar from Nbar.
For the displayed use of equation6, retain Nbar throughout that part:
L-complement is contained in (M-complement × Y) union (M × Nbar-complement).
Equation5 bounds the first integral by epsilon/4, and equation6 bounds the
second by sup_M(phi_X) times mu_Y(Nbar-complement), also epsilon/4.
The symmetric argument uses Mbar. This is a local notation repair supported
by the displayed construction; it does not invalidate Lemma3.4. No equality
of compactness and a global quantitative stability bound is imported.

## Dependency disposition

The named Eder Lemma3.3, Theorem4.1 and Lemma4.2 dependencies have now
been inspected with their local supporting proofs. Standard measure-theoretic
dependencies, including the cited Wasserstein/Prokhorov results and measurable
selection, have not all been independently rederived. The separate weak-
transport attainment dependency of all-adapted Lemma4.13 is still uninspected.
No direct citation to the all-adapted paper occurs in the current27-claim map;
the actual C18/C03 sentences still require their own source-specific checks.

| Decision | Primary criterion | Veto / uncertainty | Next justified action | Not concluded |
|---|---|---|---|---|
| Accept the bounded Eder dependency reading | Exact named statements and local proofs inspected | Standard external dependencies remain scoped; journal correspondence unavailable | Preserve assumptions in current-claim review | Complete external-proof certification |
| Retain local complement notation repair | Correct sets give both epsilon/4 estimates | Literal missing bars cannot justify the printed estimate unchanged | Keep the repair beside the source record | Compactness theorem false |
| Continue specification work | No current manuscript contradiction established | Unread weak-transport attainment limits dependent promotion | Review current sentences, then C2/C4 joins | Small sufficient state, threshold continuity or empirical accuracy |

Strongest alternative explanation for apparent printed defects is notation
rather than a substantive theorem failure; the repaired set estimate supports
that explanation. A failure of marginal compatibility or graph support would
invalidate the corresponding local use. The weakest evidence remains edition
correspondence and uninspected external dependencies, not an executed method.
