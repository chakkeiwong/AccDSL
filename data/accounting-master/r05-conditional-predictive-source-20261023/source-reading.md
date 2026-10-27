# What the April2003 conditional predictive-ability draft establishes

Inspected copy: Raffaella Giacomini and Halbert White, *Tests of conditional
predictive ability*, cover “This version: April2003”,38 physical/printed pages.
It came from the Munich EconWPA repository link listed in OpenAlex. The local
copy is `docs/papers/Tests of conditional predictive ability Giacomini (2003).pdf`,
SHA256 `712ea4b631759231a36a7c6680131a4ce65d1500da5ebb7135e56989d85be2df`.
Crossref identifies the matching title/authors' November2006 journal article,
DOI10.1111/j.1468-0262.2006.00718.x. That establishes bibliographic identity,
not equality between the2003 draft and the2006 publication.

All38 pages were inspected as extracted text, including the method, assumptions,
proofs, simulation design, application, algorithm appendix, references and table
notes. Actual page images11,12,14,24,33,34 were inspected for theorem notation,
draft anomalies and both figures. Image13 was generated with the bounded
11–14 batch but not inspected; generation grants no visual-reading credit.
Tables2–5 were read as text; no numerical cells were re-estimated or reproduced.

## Forecasting methods and the tested object

Section2, pp4–8, contrasts forecasts evaluated at limiting parameter values
with forecasts from the actual estimated method. Its proposed null is a
conditional expectation of the actual loss difference given information F_t,
not a claim that one method's average future loss is below a business margin.
The source includes estimation procedure, estimation window and weighting in
the forecasting method. Section2.1 permits heterogeneous short-memory data;
its footnote2 explicitly excludes unit-root nonstationarity. This is not
permission for arbitrary regime changes or unrestricted dependence.

Section3.1, pp8–10, defines W_t=(Y_t,X_t')' and its information filtration.
The forecasts are measurable functions of at most the m most recent
observations; m remains a finite maximum. Actual parameter uncertainty thus
persists as the evaluation sample n grows. The rolling scheme yields
n=T-tau-m+1 forecasts. The paper expressly says that an expanding recursive
estimation window is excluded by this asymptotic construction (p11,comment2).
It accommodates different forecast types and loss functions subject to the
theorem's conditions; it does not separately validate a corporate CRPS model.

## Null, instruments and covariance

Equation3, p10, is

    E[Delta L_(m,t+tau) | F_t] = 0, almost surely, for all t.

For tau=1 this implies a martingale-difference property. For a predeclared
F_t-measurable q-vector h_t, write Z_(m,t+1)=h_t Delta L_(m,t+1). The selected
moments E[Z]=0 are implications of the full conditional null. Testing finitely
many such moments is not equivalent to testing every conditional restriction.
The paper makes the resulting power limitation explicit on p13.

Equation4/Theorem1, p11, uses

    T = n Zbar' Omega_hat^(-1) Zbar,
    Omega_hat = n^(-1) sum_t Z_(m,t+1) Z_(m,t+1)'.

The source states a chi-square_q null limit under fixed finite m, its specified
mixing rates, uniformly bounded 2(r+delta) moments of each Z component, and
uniformly positive definite Omega_n. The literal mixing rates are retained in
the page image and exact text anchors: phi size -r/(2r-1),r>=1, or alpha size
-r/(r-1),r>1. The moment requirement is stronger than merely finite first
moments for individual CRPS values. The unlagged covariance form uses the
conditional-null martingale structure; it is not an unrestricted serial-loss
variance estimator for the selected E3 marginal mean.

Corollary2, p12, rewrites the same statistic as n times the uncentered R² from
regressing a constant on Z. Corollary3's other regression needs conditional
homoskedasticity and separate moment assumptions. It is not the same formula
without additional assumptions. See the draft cross-reference issue below.

Equation5/Theorem4 and the discussion on p13 concern alternatives whose
instrumented average expected moment stays away from zero. A chosen h may miss
important conditional alternatives. The authors explicitly distinguish the
null from the listed global alternative rather than asserting they exhaust all
possibilities. Selecting instruments after seeing favorable test results is
not justified by that discussion.

Section3.3/Theorem5, p14, treats a fixed multi-step tau>1. Under the full
conditional null, losses already realized by time t make covariances at lags
j>=tau vanish. Equation8 retains lags1 through tau-1, with weights w_(n,j)
tending to1 for each fixed j, and imposes the stated mixing, moment and
positive-variance conditions. AppendixA, pp25–27, supplies the proof's mixing
CLT, covariance-consistency and alternative arguments. Those statements do
not establish a general HAC bandwidth of horizon-minus-one under an arbitrary
marginal-mean null. A fixed Bartlett window with nonunit limiting lag weights
is not automatically the source's displayed estimator.

The E3 panel can produce a scalar g_t only after the weights, common target
index, missingness/service meaning and fitting policy are defined. Its
cross-company covariance remains inside g_t. Irregular releases, different
financial calendars, shared fitted components and delayed target observation
need a filtration/horizon construction; a fiscal label alone does not supply
the paper's equally indexed fixed-horizon environment.

## Selection rule, experiments and their limits

Section3.4, pp14–15, proposes predicting loss differences by regressing them
on h_t and selecting by the sign relative to a user-specified threshold c.
The empirical application sets c=0. This point decision rule is not a
one-sided confidence bound below a meaningful margin. The paper itself leaves
richer decision rules, multiple comparisons and heterogeneous-data bootstrap
refinements to future work on p23. None is imported as solved here.

Section4, pp15–17, constructs a special conditional null for squared-error
forecasts. Conditional on the prescribed forecasts, it generates
Y=(f+g)/2+epsilon. It uses a CPI-based sequence of length468, moving-window
mean/AR(1) forecasts, selected m and noise variances,10,000 replications and
nominal10% tests. Table1/p33 reports rejection frequencies. The serial-loss
alternative, its initialization burn-in and Figure1/p33 are a particular
power experiment. These are attributed source results, not evidence of size,
power or sufficient origins for this nine-company CRPS task.

Section5, pp17–22, compares sequential selection, diffusion indexes and
Bayesian shrinkage with autoregressive/random-walk benchmarks for eight
macroeconomic series,1/6/12-month horizons, using a146-series monthly panel.
The source transforms series, selects models and refits in a rolling sample;
AppendixB, pp27–28, gives its simplified sequential selection algorithm.
Its prior scales, BIC ranges, outlier replacement,10% CPA threshold and
1% selection-test threshold are choices of that application, not AccDSL
defaults. It describes a simulated real-time exercise, not an authenticated
first-release-vintage experiment for our firms.

Figure2/p34 plots *predicted* loss differences from the fitted selection rule.
The percentages in Tables2–5 refer to how often that rule would select a
method, as section3.4 and p21 explain. They must not be relabelled observed
win frequencies or an uncertainty bound on E3. The application itself warns
on p23 against generalising its high-parameter/limited-sample findings.

## Proof reading and unresolved draft details

AppendixA, pp24–27, was read in full. It argues variance consistency through
finite functions of mixing sequences and moment bounds, then uses an mds CLT
for one-step loss and a mixing CLT for multi-step loss. This reading identifies
the source's dependencies; it is not a fresh proof audit of White/Domowitz,
McLeish, Wooldridge/White or the cited textbook corollaries. In particular,
the joint dependence of the data and instruments must be justified in a later
application, not inferred from separate verbal mixing labels.

Three rendered draft details need resolution before using it as an executable
theorem specification:

- Corollary3/p12 refers to assumption(iv) of Theorem1, whose displayed list
  on p11 has only(i)–(iii). No missing condition is invented.
- Theorem5(ii)/p14 prints Z_(m,t+1,i), although the multi-step statistic and
  proof use t+tau. That subscript is preserved rather than silently repaired.
- Theorem1's proof/p24 calls the product tilde-lambda_i Z_(m,t+1,i)
  F_t-measurable. Read literally with its asserted zero conditional mean,
  an integrable such product would itself be zero: E[X|F_t]=X for an
  F_t-measurable X. This is incompatible with a nondegenerate claimed
  variance if asserted for all projection components. The next displayed
  expectation only needs the deterministic coefficient to be measurable.
  Thus the literal measurability sentence is wrong for that argument;
  the intended correction and final-edition wording remain unchecked.

These are findings about the retained2003 draft. They do not establish that
the2006 article contains the same issues or that all conditional forecasting
tests are invalid. No implementation/theorem adoption is made from this copy.
The source lists an author homepage but no code package was acquired or
audited. Original-author executable correspondence remains unchecked.

## Transfer to the selected E3 question

The source usefully requires the whole forecasting method, including finite
window and refitting choices, to be the object evaluated. Its main equality
null and quadratic statistic are different from a bound for
Delta_Q=E_Q[sum_i w_i d_(i,O)] below a decision-justified negative margin.
Setting h=1 does not turn a squared equality statistic into that directional
bound, or remove its variance and origin assumptions. Rejection in itself
does not establish the direction or material size of improvement.

The next protocol still needs the target period and weights, Q/regime,
admissible vintages, fitted-service definition, valid one-sided theory,
multiplicity and sample/resource design. The original192 vintage admissions
stay false. Source reading completes a named internal task; method selection,
empirical execution and all wider acceptance remain open.
