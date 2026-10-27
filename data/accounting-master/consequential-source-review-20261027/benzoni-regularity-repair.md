# A conditional repair of the restructuring derivative

27 October 2026; MC14/18/29–31/35. Local derivation for the source-review
question in c08-source-review.md. This is not a new theorem attributed to the
paper, a numerical experiment or adoption of its model.

The shareholder restructuring value depends on the pre-issue income-to-face-
debt ratio y and the chosen post-issue ratio z. Suppress the fixed strategy a.
Write e₀(z) and P₀(z) for the continuation-region equity value per face and
debt price per face. Define s₀(z)=(e₀(z)+P₀(z))/z. Source equation(10) is

    Φ(y,z) = y[s₀(z)−β] − P₀(z).

On y≥yu, the selected target Y(y) gives E(y)=Φ(y,Y(y)) and Q(y)=P₀(Y(y)).
E and Q denote the source's extensions e and P into the restructuring region;
the different letters here prevent differentiating P₀ at the wrong argument.
Both ratios are positive. Work locally on a compact y interval lying strictly
above yu; boundary matching and the limit at infinity remain separate checks.

## What continuity alone does not provide

Let C be the continuous nondecreasing Cantor distribution function on[0,1].
Its derivative is zero Lebesgue-almost everywhere, but C(1)−C(0)=1.
For e(x)=∫₀ˣC(t)dt, e is C¹ and convex, with continuous nondecreasing e′=C.
If e′ were absolutely continuous, its endpoint difference would equal
∫₀¹C′(t)dt=0, a contradiction. The second derivative of e as a measure is the
nonzero singular Cantor measure. Thus the implication printed between(A.5)
and(A.6) is wrong as a general mathematical inference. This counterexample
does not satisfy or refute all of the paper's model-specific restrictions.

## Explicit sufficient conditions

Assume e₀ and P₀ are C² in a neighborhood of the selected interior targets,
and that each y has a unique global maximizer Y(y) in that neighborhood.
Assume additionally that the second derivative with respect to z at the
maximizer is nonzero:

    D(y) = y s₀″(Y(y)) − P₀″(Y(y)) ≠ 0.

For an interior twice-differentiable maximum this makes D(y)<0. These are
sufficient conditions, not necessary conditions for absolute continuity.
The continuation-region formulas in source(7) and(12) provide smoothness
away from zero and boundaries. The unique interior target is in
Proposition1(6). The nonzero curvature condition is an additional premise:
the inspected source does not establish it globally, and a root returned by
fsolve does not establish it.

Interior optimality gives F(y,Y(y))=0 where

    F(y,z) = y s₀′(z) − P₀′(z).

F is C¹ under the stated premises. The implicit-function theorem yields a
local C¹ maximizing branch. Uniqueness identifies overlapping local branches
with the same Y. Differentiating F along that branch gives

    s₀′(Y) + [y s₀″(Y)−P₀″(Y)]Y′ = 0,
    Y′ = −s₀′(Y)/D(y).

Now differentiate the value, keeping both dependencies on y:

    E′ = s₀(Y)−β + [y s₀′(Y)−P₀′(Y)]Y′ = s₀(Y)−β,
    E″ = s₀′(Y)Y′,
    Q′ = P₀′(Y)Y′ = y s₀′(Y)Y′ = y E″.

The middle bracket vanishes by interior optimality. Also E+Q=y[s₀(Y)−β],
so yE′=E+Q. Substituting both identities gives, exactly on this branch,

    δ − (r+ξ)E + (μ+ξ)yE′ + ½σ²y²E″
      = δ − (r−μ)E + (μ+ξ)Q + ½σ²yQ′.

This is the equality used in source(A.6)/(25) and the inspected author-code
functions. It is correct under the explicit smooth-branch conditions above.
E′ is C¹, hence absolutely continuous on each compact subinterval. A global
certificate must still cover every selected branch, any join at yu, endpoint
behavior and all admissible deviations. No finite grid proves those conditions.

## The compact-set issue can be localized

Under the source's positive issuance cost and barrier assumptions, Φ extends
continuously to z∈[yb,yu] since yb>0 and continuation values extend to the
barriers. At z=yb, e₀=P₀=0, so Φ(y,yb)=−βy<0, whereas the selected
restructuring value is positive. At z=yu, the source's value-matching and
price-continuity identities give, with Yᵤ=Y(yu),

    Φ(y,yu) = Φ(y,Yᵤ) − βy < Φ(y,Yᵤ).

The upper endpoint cannot maximize either. Consequently maximization may be
performed on the closed compact interval while retaining an interior target.
With the source's unique-target condition this supplies the compact-domain
premise for Milgrom–Segal Corollary4. It repairs the open-set wording under
these premises; it does not prove the separate nonzero-curvature condition.

## Verification without that additional smoothness

For the transformed value v=e−ê, use the source's weak measure operator:

    Ov(dy) = ½σ²y² v″(dy)
             + [(μ+ξ)y v′₋(y)−(r+ξ)v(y)]dy.

If e is convex, its distributional second derivative is a nonnegative measure.
Subtracting the affine ê does not change that measure. Write
e″=e″ac dy+νs. The singular component of Ov is ½σ²y²νs. On y>0 with σ>0,
the requirement Ov≤0 rules out a nonzero positive νs. A density-only numerical
check does not test νs and is therefore insufficient before its absence has
been proved. Retaining the full measure formulation preserves the actual
target; the stopping obstacle and boundary conditions remain necessary too.

## Disposition

The conditional derivative identity and compact-interval repair are local
deductions with explicit premises. They explain what the author code computes.
They do not close the proof under every original parameter/strategy
assumption. Remaining questions include degeneracy/regularity under the
original assumptions, the strict versus weak default threshold, the drift
scope difference and published/preprint dependency correspondence. Current C08
does not assert these unresolved theorems. Continue the other current claims;
do not turn this local promotion veto into a program-wide stop.
