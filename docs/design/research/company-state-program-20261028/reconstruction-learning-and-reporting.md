# Reconstructing a company when its reports are incomplete

A company can publish the same balance sheet after buying different machinery,
holding different inventory lots, or refinancing debts on different dates. The
accounts constrain these possibilities, but a scenario asks a further question:
which differences still matter after prices, demand or funding conditions change?
Answering it requires both an inverse accounting problem and a model of the
company's subsequent operations. A journal reconstruction supplies part of that
model. It does not automatically supply production capabilities, contractual
rights or information available to decision makers.

Several literatures supply different parts of this argument. Arya, Fellingham,
Glover, Schroeder and Strang (2000) characterize information lost when transactions
are aggregated into accounts. Bayesian filtering describes sequential inference
within a specified model. Duffie and Lando (2001) connect incomplete accounting
information to credit valuation. Nissim and Penman (2001) connect accounting
forecasts to cash flows and equity value. Research on accrual quality asks how
estimates and reporting choices alter what statements reveal. These contributions
fit together only after their different assumptions are explicit.

## What can be recovered from accounts?

Let $y$ contain amounts for a fixed collection of transaction types, let $A$
record their signed effects on accounts, and let $x$ contain observed changes
in balances. The accounting relation is $Ay=x$. It presumes that the columns
of $A$ contain the relevant transaction types and that observations use the
same account definitions and period.

Arya et al. (2000, sections 2–3, printed pages 370–377) use an incidence matrix
with one debit and one credit in each column. Their connected example has six
accounts and seven transaction types. Its rank is five, leaving two independent
directions of transactions invisible in the accounts. If $y_p$ is one solution,
every unrestricted solution has the form

$$
y=y_p+N^{\mathsf T}k,\qquad AN^{\mathsf T}=0,
$$

where the rows of $N$ span the nullspace. Multiplication by $A$ removes the second
term; conversely, the difference between any two solutions lies in that nullspace.
This describes a whole family without drawing one tree branch for every point.

The seven amounts are inventory purchases, plant acquisitions, cash expenses,
cash sales, cost of goods sold, product-cost depreciation and period-cost
depreciation. Two nonnegative vectors consistent with the same reports are

$$
y^{(1)}=(9,6,3,10,5,0,0)^{\mathsf T},\qquad
y^{(2)}=(8,7,3,10,5,1,0)^{\mathsf T}.
$$

Both yield $x=(-8,4,6,-10,5,3)^{\mathsf T}$. The second company acquires more
plant and charges more depreciation to production while purchasing less
inventory for cash. Suppose a new service contract charges one tenth of the
plant acquired in this period. That stipulated rule produces costs of 0.6 and
0.7. The service rule is our additional economic assumption; the paper's static
equations do not imply it. Reconstructing accounts and specifying future behavior
are different tasks.

Nonnegative amounts, contractual restrictions, event ordering and recognition
rules further restrict the affine family. Some possible patterns require columns
absent from $A$. Solving the system establishes consistency within the declared
model, not coverage of every possible company history.

### A best estimate does not eliminate the family

Arya et al. introduce a normally distributed prior with mean $\mu$ and identity
covariance, and use quadratic estimation loss. Their Proposition 1 gives

$$
\widehat y=A^+x+(I-A^+A)\mu,
$$

where $A^+$ is the Moore–Penrose inverse. The first term is identified by the
accounts; the second preserves the prior mean in unobserved directions. Their
proof uses Gaussianity and identity covariance to make row-space and nullspace
projections independent. This statistical assumption, in addition to accounting
geometry, makes the nullspace component unchanged.

For the prior mean $(7,9,1,10,5,1,2)^{\mathsf T}$ the paper obtains

$$
\widehat y=(7.625,9.25,1.125,10,5,1.375,1.875)^{\mathsf T}.
$$

Disclosing total depreciation of four changes the estimate to

$$
\widehat y_{\mathrm{additional}}=(7.25,10,0.75,10,5,1.75,2.25)^{\mathsf T}
$$

and reduces nullspace dimension from two to one. Exact rational reproduction verifies the
matrix, both loops, both estimates, account consistency and pseudoinverse
identities. The original posterior covariance has rank two: an optimal point
estimate is not a unique reconstructed history.

Endnotes 4 and 13 discuss nonidentity covariance. With positive-definite prior
covariance $\Sigma$, noiseless observations and $x-A\mu$ in the supported range,
the Gaussian conditional mean is

$$
E[y\mid Ay=x]=\mu+\Sigma A^{\mathsf T}
(A\Sigma A^{\mathsf T})^+(x-A\mu).
$$

To derive it, subtract this linear predictor from $y$. The residual has zero
covariance with $Ay$; joint Gaussianity makes it independent of $Ay$, so its
conditional mean remains zero. Singular observation covariance is natural
because balanced accounts are dependent. The generalized inverse operates on
its supported range; a redundant account is not independent new evidence.

For example, observe $y_1=1$ with zero prior means, unit variances and covariance
$1/2$. The conditional mean is $(1,1/2)^{\mathsf T}$. The unmeasured $y_2$
updates through assumed correlation. This is not additional accounting
identification. Industry relationships or sales ratios can sharpen forecasts
while leaving observational information unchanged. Their provenance and
sensitivity must remain visible.

The Gaussian model permits signed amounts and does not enforce all economic
constraints. It is a transparent baseline. A nonnegative, contract-constrained
family needs its corresponding conditional distribution or set analysis;
clipping the Gaussian mean is a different calculation. The paper's section-4
classification results concern a two-type Gaussian decision problem, not
preservation of every subsequent operational or financing decision.

## Defining state before choosing an estimator

A company must remember enough to support future operations and questions
about its past. Physical and contractual memory includes inventory lots,
unpaid claims, production capacity and debt maturities. Accounting memory
includes cost bases, depreciation, allowances, tax losses and prior recognition.
Historical-query memory retains transactions or sufficient accumulators for
period reports. None is generally recoverable from closing totals.

Construction should start from operations. A FIFO sale reads lot order, units,
costs and write-down allocation. Debt service reads legal obligor, dates,
currency, resets, accrued interest and settlement status. Refinancing also
reads covenants, collateral, issuance terms and information used by lenders.
Guards and refusal outcomes matter as much as successful journals: two states
can post identical entries when funded while only one can obtain funding.

Following these dependencies produces the required resources, contracts,
memory and observations. Population structure remains explicit. Inventory
balances can constrain many lot configurations; debt notes several maturity
schedules; reserves claims of different ages. An unknown number of contracts
cannot silently become one representative contract. A bounded constructor
must state its templates and population limits and retain unknown coverage.

Sector and reporting basis change these dependencies. Insurers need claims and
coverage groups; banks counterparty, collateral and impairment information;
manufacturers production and capacity. Basis conversion may preserve contracts
while changing measurement memory. It can also change taxes, covenants,
regulatory constraints or management choices. Those feedbacks need economic
rules; renaming accounts does not supply them.

A common core can hold identity, ownership, dates, units, source relationships
and event semantics, with extensions for operation-specific memory. Sufficiency
remains relative to operations, queries, information and horizon. A new shock
can require refinement even when the old simulation was internally consistent.

## Learning over time, and learning about the past

Filtering updates a distribution over a specified state as observations arrive.
Särkkä (2013, Theorem 4.1 and proof, pages 54–56) derives prediction and updating
from the Markov property and conditional independence of observations given
state. These assumptions matter: annual revenue depends on an interval of
activity, so an endpoint-only likelihood needs an accumulator or path information.

Filtering asks what could be inferred by the decision date. Smoothing asks what
can now be inferred about an earlier date using later evidence (Särkkä, Theorem
8.1 and proof, pages 134–135). A later inventory correction changes present
inference about last year. It does not give last year's lender the correction.

Several dates matter: the economic date or reporting interval, publication,
system acquisition and each actor's receipt. An archive can contain all records
while a historical policy receives only a restricted selection. Giving the
manager the complete audit record would reveal future corrections even if its
numerical estimate used an earlier cutoff.

The new reference returns a separate policy-facing projection containing only
selected assertions. Full records, other actors' receipts and eligibility reasons
remain audit information. Proposed receipt metadata in a synthetic example
does not establish an actual person's knowledge. A correction must identify its
parent and preserve quantity, economic period, context and lineage. Original
and latest-available queries then have distinct meanings. Independent conflicting
reports remain conflicting; later arrival alone does not establish a correction.

In the retained example, a proposed report of six is corrected to five. Before
publication the public view selects six. Afterward the latest view selects five
while the original view retains six. System and actor views change only when
their availability conditions permit. Both reconstruct complete histories from
the supplied opening. Completed cash transfers stay fixed.

If a correction was published between days 219 and 221, a day-220 query cannot
assume it was known. The reference retains definitely and possibly selected
assertions and returns an unresolved result when that distinction matters. It
assigns no probabilities to dates. Its conservative summary does not assert that
every combination is jointly feasible: revision order and common documents can
restrict the possibilities.


Joint timing requires more than a list of possibly available records. For example,
a correction cannot be received through a public retrieval before it was released.
A shared document may establish several dates together. The existing exact
chronology reference represents these dependencies with rational-time constraints,
including strict boundaries, and retains every feasible information view with its
proof support. Missing evidence remains unknown even when other constraints
restrict its possible time. If the computation stops early, the unexamined domain
remains unresolved.

The new composition test connects these certified views to complete accounting
histories through an explicit proposed interpretation of each selected source.
A correction available before the decision can produce one reconstruction; an
unavailable correction leaves the earlier reconstruction. Both survive when time
is unresolved. Identical measured amounts under two source histories retain both
sources. Retractions and conflicting heads remain unresolved rather than acquiring
an invented measurement. A source label alone does not determine accounting
meaning: the present comparison uses a declared synthetic interpretation between
two different reference cases. A common issuer, quantity definition and supported
source interpretation are still needed for a real-company application. Its full
proof record is audit information and is not supplied to a decision policy.

Unknown parameters are another issue. Särkkä (section 12.1, equations 12.1–12.8)
forms a joint model of parameters, states and observations, integrating states
out to obtain parameter likelihoods. Parameter estimation differs from discovering
an omitted contract type or an inadequate inventory representation. A precise
filter inside an incomplete model remains incomplete. Structural evidence should
trigger explicit state refinement and recomputation of affected results.

## What credit valuation adds

Duffie and Lando (2001) give informed equity owners an asset process and a
liquidation choice, while bond investors observe imperfect reports and survival.
Section 2.2, equations 14–19, conditions on both. The absence of default is
informative because some underlying paths would already have caused liquidation.

For a finite illustration, let two latent conditions have equal prior probability.
Suppose survival probabilities are $9/10$ in the stronger condition and $1/5$
in the weaker one. Survival changes the stronger-condition probability to
$9/11$; ignoring it leaves $1/2$. These are illustrative assumptions, not
estimates from the paper.

Section 2.4, equation 29 prices repayment conditional on survival and recovery
conditional on default. The basic model assumes risk-neutral agents, a fixed
rate, consol debt and an equity-owner liquidation choice. It does not supply
a general issuance model for arbitrary maturity ladders and funding gaps.
Its transferable lesson is to specify information, default behavior and claim
pricing together. Different information can produce different conditional values
for the same economic history.

A source issue matters for implementation. Printed page 655 says that serially
independent report noise makes the report sequence autoregressive of order one.
Read literally for the stated noisy Brownian log-asset model, that sentence is
wrong. Consider the sampled special case $Z_0=0$, $Z_t=Z_{t-1}+\eta_t$ and
$Y_t=Z_t+U_t$, with independent Gaussian innovations of variance $q>0$ and
independent report noise of variance $r>0$. Then
$\operatorname{Cov}(Y_1,Y_3)=q$,
$\operatorname{Cov}(Y_1,Y_2)=q$,
$\operatorname{Cov}(Y_2,Y_3)=2q$ and
$\operatorname{Var}(Y_2)=2q+r$. Gaussian conditioning gives

$$
\operatorname{Cov}(Y_1,Y_3\mid Y_2)
=q-\frac{2q^2}{2q+r}=\frac{qr}{2q+r}>0.
$$

A first-order Gaussian Markov sequence would have zero conditional covariance.
Earlier reports still help infer latent assets. The covariance vanishes when
report noise is zero. This finding concerns the shortcut, not the entire credit
model: equation 33 retains full report history in its predictive density. Keep
that history or a justified sufficient filtering distribution. The source sentence
was checked visually and the counterexample with exact arithmetic. A bounded
metadata search found no correction notice; it was not exhaustive. Appendix A's
intensity argument and Appendix B's conditions were inspected, but the continuous-
time theorem and numerical spreads have not been independently reproduced here.

## Accounting forecasts, cash flows and forensic alternatives

Nissim and Penman (2001, section 2.5, pages 122–123, equations 11–15) connect
operating and financing forecasts. Using their definitions, operating income
$OI_t$, net operating assets $NOA_t$, net financial expense $NFE_t$, net financial
obligations $NFO_t$ and net shareholder distributions $d_t$ satisfy

$$
FCF_t=OI_t-\Delta NOA_t,\qquad
d_t=FCF_t-NFE_t+\Delta NFO_t.
$$

Distributions include dividends and repurchases less share issues. Income can
remain invested in operations instead of becoming free cash flow. Financing and
its cost connect that cash flow to distributions. The source equations were
checked visually. They are identities under consistent classification and
comprehensive-income articulation, not laws determining investment or issuance.

A valuation simulation therefore needs the state determining margins,
reinvestment, settlement and financing. Residual-income valuation reorganizes
forecasts under consistent accounting and terminal assumptions; it does not
remove the state problem. Enterprise, debt, equity and a particular shareholder
also have different claim boundaries. Issuance can fund a company while diluting
existing holders. Financing proceeds are accompanied by claims. Physical
probabilities alone do not determine market prices: a pricing operator or
discount-factor relationship is required. The Penman–Sougiannis and
Lundholm–O'Keefe debate still needs both primary texts; the identities alone
cannot settle empirical forecasting comparisons.

Forensic accounting adds the process that generates reports. An unexplained
accrual may reflect omitted operations, an inaccurate estimate, a permissible
choice, incorrect recognition or deliberate misstatement. These explanations
imply different future cash flows and observation laws. A nonexistent sale and
a genuine sale on unusually long credit can report the same revenue and
receivables today.

Dechow and Schrand (2004, chapter 5, pages 45–47) discuss how residual accrual
measures depend on the benchmark for normal operations, including growth.
Their methodological argument supports interpreting scores as evidence rather
than observations of fraud or intent. The empirical estimates they summarize
have not been reproduced here.

Dichev's retained *Accrual duration* working paper, dated 15 December 2016,
connects estimates to the time between accrual recognition and associated cash
flows (sections 2–4 and Appendix A). Its receivable example records income
$(300,0,-100,20)$ and collects $(0,100,0,120)$: both total 220, with different
timing. Later cash realization helps evaluate an earlier estimate but does not
establish what management knew then. The paper discusses this ex-ante versus
ex-post difficulty. A 2024 article with the same title is a separate version
whose changes remain unchecked.

The working paper also explains that unchanged net receivables can conceal
collection of old claims and origination of equally large new claims of different
quality. This directly connects earnings quality to cohort state. Net balances
lose composition needed for forecasting collections and evaluating accruals.
Its classification of contemporaneous accruals as nondiscretionary assumes the
transaction's accounting treatment. A cash payment does not establish whether
its cost should be capitalized; the paper explicitly sets the initial recognition
question outside its scope. AccDSL must keep that question open when evidence
is missing.

A reconstruction should distinguish contractual or physical state, books
computed under declared valid rules, the company's reported books and extraction
of those reports. Evidence of delivery concerns recognition; collection concerns
credit and settlement; a restatement concerns a prior report; an anomaly score
concerns a fitted statistical relation. These are not interchangeable hard
constraints on true state.

The current reference accepts proposed hard assertions and refuses to turn soft
or noisy evidence into certainty. It preserves common-source dependence without
estimating reliability. Probabilistic inference requires a joint model of sources
and reporting choices; set-valued inference can preserve competing interpretations.
Some distinctions may remain unresolved indefinitely. The simulation must retain
their consequences or state the approximation used to reduce them.

## References and reading boundaries

Arya, A., J. C. Fellingham, J. C. Glover, D. A. Schroeder and G. Strang (2000).
“Inferring Transactions from Financial Statements.” *Contemporary Accounting
Research* 17(3), 365–385. DOI: 10.1506/L0LW-NX5L-4WUR-9JKL. Sections 2–4,
proofs, appendix and relevant endnotes inspected. The PDF begins at page 365;
deposited metadata reports a different first page.

Särkkä, S. (2013). *Bayesian Filtering and Smoothing*. Cambridge University Press.
Author-hosted version of 11 November 2013; Theorems 4.1 and 8.1 with proofs and
section 12.1 inspected. No empirical algorithm ranking is adopted.

Duffie, D., and D. Lando (2001). “Term Structures of Credit Spreads with
Incomplete Accounting Information.” *Econometrica* 69(3), 633–664.
DOI: 10.1111/1468-0262.00208. Sections 2.1–2.4, 3.1–3.2 and Appendices A–B
inspected within the stated scope. The page-655 observation-process shortcut
is excluded from technical support.

Nissim, D., and S. H. Penman (2001). “Ratio Analysis and Equity Valuation:
From Research to Practice.” *Review of Accounting Studies* 6, 109–154.
Selected accounting identities inspected; empirical comparisons remain open.

Dechow, P. M., and C. M. Schrand (2004). *Earnings Quality*. Research Foundation
of CFA Institute. Selected methodological passages inspected; cited primary
empirical methods require separate review.

Dichev, I. D. (2016). *Accrual duration*, working paper dated 15 December 2016,
retained from the Harvard Business School 2017 conference site. Sections 2–4
and Appendix A inspected. The 2024 article, DOI: 10.1007/s11142-024-09826-8,
is a separate version lead. No current standards conclusion or empirical
superiority is inferred from the working paper.


Penman, S. H., and T. Sougiannis (1998). “A Comparison of Dividend, Cash Flow,
and Earnings Approaches to Equity Valuation.” Primary-text review remains open;
this work is identified as a required comparison, not used here to support a
performance conclusion.

Lundholm, R., and T. O'Keefe (2001). “Reconciling Value Estimates from the
Discounted Cash Flow Model and the Residual Income Model.” *Contemporary
Accounting Research* 18(2), 311–335. DOI: 10.1506/W13B-K4BT-455N-TTR2.
Publication metadata retained; primary technical text remains unread.
