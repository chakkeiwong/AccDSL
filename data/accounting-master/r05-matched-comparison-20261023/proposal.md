# Compare two forecasts of the same operating cash flow

The primary E3 contrast remains the structural model preserving alternative
histories against the same structural model using a fixed interpretation.
Both receive the same permitted evidence and forecast the same first-release
consolidated operating cash flow, in matching units and with the same positive
as-of asset denominator. Their difference concerns how historical ambiguity
affects prediction. The earlier phrase “add predictive information” expresses
that research motivation; it must not mean that one arm gets extra observations.

For a scoped finite illustration, let D be the admitted information at an
origin and H(D) a finite collection of substantive history alternatives.
Let F_h be the predictive law for OCF produced by the common economic model
conditional on history h. These laws may retain future uncertainty even when
the historical interpretation is fixed. Let w_h(D) be nonnegative as-of weights
summing to one, supported by a declared probabilistic model or fitted procedure.
The candidate law is

    F_mix(z | D) = sum_h w_h(D) F_h(z | D).

The fixed arm uses F_(s(D)), where s is a selection procedure fixed using
development information before the affected test outcome. Its forecast is
still a law: fixing a historical interpretation does not justify removing its
future economic uncertainty. A selection made after observing Y is an oracle,
not this comparator. Neither uniform weights from branch counts nor a continuous
density mode supplies a default s or w. The finite example does not restrict
the full design to finite histories or establish any actual company's weights.

## Why component-score averaging is a different comparison

Write L(F,y) for negatively oriented CRPS. The completed target derivation
gives L(F,y)=integral (F(z)-1{y<=z})^2 dz for the finite laws used here.
For w summing to one, put M=sum_h w_h F_h and I=1{y<=z}. Expanding squares
at each z gives

    sum_h w_h(F_h-I)^2 - (M-I)^2
      = sum_h w_h F_h^2 - M^2
      = sum_h w_h(F_h-M)^2
      = (1/2) sum_(h,j) w_h w_j(F_h-F_j)^2.

The terms containing I cancel. Integrating yields

    sum_h w_h L(F_h,y) - L(F_mix,y)
      = integral sum_h w_h(F_h-M)^2 dz
      = (1/2) sum_(h,j) w_h w_j integral (F_h-F_j)^2 dz >= 0.

For finite support all integrals are finite; finite first moments are required
for the broader CRPS setting. The gap is independent of y for fixed component
laws and weights. It is a property of the mixture and score. It can explain
why a mixture outperforms a random component whose selection probabilities
are w, after averaging that selection randomness. It gives no ordering against
the particular fixed law F_(s(D)). Treating the averaged component score as the
primary fixed-interpretation comparator would answer the wrong question.

For example, take point laws at0 and2 with weights one half each, and lock the
fixed arm at0. At y=0 the mixture loss is1/2 and the fixed loss is0: the
candidate loses. At y=2 the losses are1/2 and2: the candidate wins. If the
true fictional outcome has probability p at2 and1-p at0, the expected paired
difference is

    Delta(p) = (1-p)(1/2) + p(-3/2) = 1/2 - 2p.

It is zero at p=1/4 and negative only for p>1/4. These are complete synthetic
laws for a mathematical counterexample, not estimates, priors or performance
evidence for the named companies. The mixture identity cannot establish the
true p. Dividing both losses by the same positive assets preserves the signs.

## Representation and fitting requirements

A duplicated encoding must not create extra probability. Splitting the mass
of the zero history from1/2 into1/4+1/4 leaves the mixture unchanged. Assigning
equal mass to all three encodings instead changes its substantive probabilities
to2/3 at0 and1/3 at2; its loss at2 becomes8/9 rather than1/2. That is a different
forecast law. Equal numbers of encodings are not evidence for those probabilities.
Histories with identical past journals but different future conditional laws
are also not equivalent merely because the journals match.

The proposed primary comparison should preserve the following matched inputs
and explicitly name the permitted difference:

| Quantity or procedure | Required relationship |
| --- | --- |
| Issuer, fiscal interval, cutoff, source versions, target basis and asset scale | Identical for both arms |
| Economic/behavioural mechanisms and conditional forecast kernels | Same definition; the history-conditioning or integration operation is the declared difference |
| Training labels, transformations and validation origins | Same permitted information and timing rules |
| Common nuisance fitting | Shared fitted state for a strict mechanism ablation; if fitted separately, disclose that broader procedure contrast and justify parity |
| History selector and history weights | Explicit procedures frozen before test outcomes, with provenance and development/tuning budgets |
| Output validity and service failure | Same reporting obligations; no deletion or renormalisation of failed mass or missing positive-weight cells |
| Primary test contrast | Candidate CRPS minus locked fixed-arm CRPS on paired outcomes |

The strict shared-state ablation and a separately tuned method comparison
answer different questions. The former isolates the final treatment of history
uncertainty conditional on common fitted inputs. The latter compares two full
learning procedures, whose training objectives and fits may differ. Record both
if both are studied; a gain in the broader contrast cannot be attributed solely
to the final mixture operation. Common-state construction must itself use a
predeclared, symmetric development rule rather than favouring one arm.

The existing naive, runoff and tuned-classical ladder remains necessary. A
non-history ensemble can be a later mechanism diagnostic if an improvement
could be explained by generic averaging. It requires its own matched component
and tuning design; it is not silently promoted into the primary comparator or
added as an unbudgeted empirical arm here. The diversity identity is explanatory,
not a promotion criterion for any method.

No weight estimator, fixed selector, nuisance-fitting objective or default
resource allocation has been selected by this note. These are the next concrete
fitting-design dependencies. An unjustified probability law blocks the CRPS
comparison; valid unweighted history sets remain eligible for the separate
set-valued inclusion/width/decision questions already specified in E3.

The exact reference checks below test the attribution logic. They neither
evaluate the actual economic model nor supply uncertainty for the user's future
performance claim. The frozen manuscript and all historical-vintage admissions
remain unchanged.
