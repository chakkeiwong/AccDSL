# Reserve-risk targets and a finite risk-measure specification

20 October 2026. Proposed method design; no runtime or accounting admission.
Source: England/Verrall/Wüthrich accepted manuscript, §§5–7 and Appendices 2–3.
The mathematical deductions below state their own assumptions. The current
3.44 manuscript correctly leaves risk compensation unresolved but does not
yet specify these finite transformations or future-information distinctions.

## Future payments and future information

Fix the contracts, terminal settlement date T, currency and information at
time 0. Let F_t be increasing information, U the square-integrable final
total payment and A_t the cumulative amount already paid, observable at t.
Remaining payments are L_t=U−A_t. Assume U is revealed by T. For this
derivation, the reserve estimate is the true conditional mean
R_t=E[U|F_t]−A_t. A fitted reserve rule need not have this property.

Put M_t=E[U|F_t]. If the payment between t−1 and t is A_t−A_(t−1), then

    CDR_t = R_(t−1) − (A_t−A_(t−1)) − R_t
          = M_(t−1) − M_t.

This is the paper's profit sign: an increase in the estimated ultimate gives
a negative CDR. A capital calculation on losses must explicitly use the
opposite sign. The paper's Table 7 uses the negative of the lower 0.5% CDR
quantile. Atomic quantiles need their own convention; a percentile reflection
must not silently change endpoint handling.

From time 0, three quantities answer different questions:

    a_t = E[sqrt(Var(L_t|F_t)) | F_0],
    b_t = sqrt(E[Var(L_t|F_t) | F_0]),
    c_t = sqrt(Var(L_t|F_0)).

The first is expected future conditional standard deviation. The second is
the root mean square of that conditional standard deviation. The third
measures remaining-payment variability using today's information. Concavity
of square root gives a_t≤b_t. Conditional total variance gives

    Var(L_t|F_0) = E[Var(L_t|F_t)|F_0]
                   + Var(E[L_t|F_t]|F_0),

so b_t≤c_t. This reconstructs Appendix 3, Lemma A3.1. It bounds expected
standard deviation, not every future state's risk. Equality in the first
inequality requires conditional variance constant given F_0 (apart from
degenerate cases); equality in the second requires the future conditional
mean of L_t constant given F_0. These are different conditions.

The reverse sum of future CDRs telescopes to M_t−U. Its conditional mean
given F_t is zero, and Var(L_t|F_t)=Var(U|F_t), because A_t is then known.
Thus b_t²=Var(sum_(k>t) CDR_k | F_0). Under these conditional-mean assumptions,
the CDR increments are martingale differences. For k<l, CDR_k is measurable
at l−1 and E[CDR_l|F_(l−1)]=0; iterated conditioning makes their covariance
given F_0 zero. Consequently

    b_t² = sum_(k>t) Var(CDR_k | F_0).

This is a local derivation of the ideal relation behind Corollary A3.2, not
a reproduction of Merz/Wüthrich's uninspected estimators. The source corollary
is written for a fixed origin; aggregate variance must retain dependence
between origins. The local derivation may use total U directly and therefore
does not assume independent origins. Estimated MSEPs are not automatically
equal to these conditional variances, and arbitrary refitting can introduce
conditional bias or nonzero covariance. For such rules, keep the full joint
CDR path and its covariance terms rather than asserting the sum-of-variances
identity. Uncorrelated increments need not be independent.

In the predeclared four-outcome example, U is 0,2,8 or14 with probability
1/4, and time 1 reveals its lower or upper pair. Conditional means are 1 and
11; conditional variances are 1 and9. Therefore a_1=2, b_1=√5 and c_1=√30.
The two CDR increments have variances 25 and5 and zero covariance. Their
dependence remains visible because the second increment's absolute size is
1 or3 according to the first increment's sign. On the upper branch the
future SD is3>√5. Neither an expected-risk upper bound nor a fitted MSEP is
a pathwise capital guarantee. The lemma establishes no quantile ordering,
discounted-value identity or current regulatory capital rule.

## A risk measure requires a complete declared law

For a bounded finite specification, let X take ordered values x_j with
strictly positive rational probabilities p_j summing to one. Equal values
may be grouped by adding their probabilities, preserving their provenance.
X is a declared discounted payment total in one currency, at one information
date and for one contract perimeter. Its law, joint cash-flow paths and
discounting assumptions must already be justified for its intended use.
An unweighted set of admissible histories does not supply those probabilities.
Incomplete computational draws cannot be renormalised into a complete law.

This finite example specifies three optional methods, without selecting any
one of them for an insurer. Write F for the CDF and m=E[X].

* VaR uses the left quantile Q_alpha=inf{x:F(x)≥alpha}, 0<alpha≤1.
  Its relative amount is Q_alpha−m. The level is an explicit input.
* Expected shortfall uses ES_alpha=(1/(1−alpha)) integral_alpha^1 Q_u du,
  0≤alpha<1. For q=Q_alpha, its numerator is
  sum_(x_j>q) p_j x_j + q(F(q)−alpha). The boundary mass is retained.
  At alpha=0 define ES_0=m directly. This precise convention supplies what
  the source's informal equal-upper-tail-weight description leaves implicit
  for a finite distribution with atoms.
* For nonnegative X, the proportional-hazards functional is
  H_rho(X)=integral_0^infinity S(u)^(1/rho) du, rho≥1. With
  S_j=1−sum_(k≤j)p_k and S_0=1, its masses are
  w_j=S_(j−1)^(1/rho)−S_j^(1/rho); H_rho=sum_j w_j x_j.
  These masses are nonnegative and telescope to one. For rho=1 they are
  p_j. A signed cash-flow law needs a separately specified extension; shifting
  or clipping losses silently would change this stated target.

The last weights follow from the transformed survival function in Appendix 2.
The retained accepted manuscript prints the subtraction in the opposite order
for j≥2 on paper page34. That formula is wrong relative to its stated integral:
for equally weighted losses 0 and4 and rho=1, the printed weights are 1/2
and−1/2, sum to zero, and give an unnormalised value −2. The integral is2.
The corrected subtraction gives weights 1/2 and1/2 and value2. This is a
source-specific formula error. It does not establish the formula in the final
journal edition or the behavior of ResQ/Igloo, the software named in the paper.

For a second exact check, losses 0,4,10 with probabilities 5/9,1/3,1/9 have
mean22/9. At rho=2 the transformed tails are1,2/3,1/3,0, giving weights1/3
each and H=14/3. Integrating survival over intervals [0,4) and [4,10) gives
4(2/3)+6(1/3)=14/3 independently. This is an illustrative specified law,
not an inferred actuarial model or a selected risk preference.

For atom handling, use losses 0,4,10 with probabilities1/2,1/4,1/4 and
alpha=3/5. The quantile is4, but expected shortfall is31/4. Conditioning on
X>4 gives10; conditioning on X≥4 gives7. Neither equals the declared
quantile-integral target. The relative ES amount is31/4−7/2=17/4.
An output of31/4 lies between support points and has no exact left-quantile
equivalent. The value4 corresponds to alpha in(1/2,3/4]. Therefore report
F(v−), F(v), the atom at v, and whether an exact quantile-equivalent set
exists. CDF coverage F(31/4)=3/4 is computable, but Q_(3/4)=4. Calling that
coverage an exactly matching quantile would be wrong. Interpolation requires
an explicit different convention. This is a mathematical output convention,
not an interpretation of an insurer's regulatory disclosure duty.

## Compensation and projected capital remain additional choices

A candidate relative risk measure is rho(X)−E[X]. If a chosen quantile makes
this negative, preserve the result and flag its incompatibility with a
nonnegative-compensation profile; silently flooring it changes the method.
The chosen functional and level express a risk preference, not something
identified solely from the claims distribution. The paper's 75%,40%,1.85,
98%,97.1%,6% and3% numbers belong to its examples and historical discussion.
They are not AccDSL defaults or current authority.

For a separate cost-of-capital convention, let K_t be a justified projected
capital amount at the start of year t, c_t its annual charge, and d(0,t+1)
the discount factor for paying that charge at year end. Then

    RM_0 = sum_t d(0,t+1) c_t K_t.

This equation specifies timing, not the capital amounts or charges. If capital
is random, the intended conditional expectation and its joint relation to
discount factors must be stated. Discounting expected capital is not generally
equal to expected discounted capital. The reserve cash-payment timing may
differ from capital-cost timing. A best-estimate runoff profile, a conditional
SD profile and a quantile profile need separate justification even when they
share the same opening capital. An observed near equality in the paper's
single illustrative dataset is descriptive, not a universal equivalence.

The proposed evaluation input therefore names the source law, information
date, payment horizon, loss sign, cash-flow perimeter, currency/unit,
discount convention, chosen functional and explicit parameter. Its output
retains the mean, total risk measure, relative amount, boundary conventions,
CDF coverage, assumptions, source/derivation identities and failure status.
Unknown probabilities, incomplete draws, mixed currencies, unsupported signed
PHT inputs or missing parameters block the affected calculation. None may be
filled from a historical paper's example. Aggregate risk uses a joint law;
contract-group allocations and reinsurance risk transfer remain separate
methods with their own authority and dependence assumptions. The paper itself
leaves allocation/diversification outside scope. This optional specification
adds no operation admission or production implementation to the frozen design.
