# What a company model must remember

28 October 2026. Research draft for the governing manuscript. This develops
the existing [construction specification](../company-state-inference-20261028/state-construction.md),
not a replacement product API. Exact derivations below are local results for
the stated finite models; the source ledger distinguishes them from imported
literature.

## A balance sheet is an observation of a company

A retailer can report inventory of 100 units costing 1000 while retaining very
different purchase layers. When it sells 50 units, older units costing 6 each
produce cost of sales 300; older units costing 14 produce 700. The opening total
does not determine the next journal even when both companies use FIFO. A
borrower reporting debt 100 can likewise owe 80 next month or 20 next month.
Its cash requirement depends on the calendar, not merely the balance.

These examples show why a journal is necessary but not sufficient as the
company's internal description. A journal records recognized changes in
accounts. Contract rights, payment dates, inventory identities, unused
capacity, collateral restrictions and contingent obligations can determine
future transactions before they produce a recognized balance. Multiple
journals consistent with a statement are therefore only part of the relevant
uncertainty. Different nonjournal contractual or operational histories may
produce the same journal as well.

For a declared task, describe a company's condition as

$$
s_t=(e_t,c_t,m_t,h_t).
$$

Here e_t describes economic resources, c_t the contracts and relationships
that constrain their use, m_t accounting memory, and h_t any additional
accumulators or history required by the permitted reports. These components
need not be disjoint physical databases: a contract identifier can connect
several of them. Their responsibilities must be distinct. Model parameters,
transition laws and reporting-basis versions are declared separately; if a
parameter evolves or is learned, its role and evolution must be explicit.

The analyst's distribution over s_t is not another company asset or
liability. It represents uncertainty about the company. Management, creditors,
auditors and public investors may hold different information. An actor's
beliefs enter the behavioral model if its choices depend on those beliefs;
they do not alter inventory layers simply because the analyst revises an
estimate. The state of the analyst's estimation problem and the state of
the company are related but different quantities.

A practical construction starts with required operations and works backward
through their dependencies. A FIFO sale needs order and cost of remaining
layers. A maturity payment needs legal obligor, currency, date, priority and
amount; a refinancing decision may also need pledged collateral, covenants,
funding access and what prospective lenders know. An interim expense report
needs transactions or accumulators over its interval even if two histories
have already converged to the same forward state. Refusal conditions matter
as much as successful operations: the model must retain enough information
to say a payment cannot be made or a valuation is unsupported.

## The industry changes the required distinctions

The proposal is a composition procedure, not one universal vector of ratios.
A sector extension is justified by a mechanism and a required question.

| Operation or question | Information that totals can conceal | Consequence of dropping it |
| --- | --- | --- |
| Sell or replenish inventory | Lot order, cost, location, expiry and product substitution | Wrong cost, spoilage or feasible delivery |
| Collect and finance receivables | Debtor identity, dispute, maturity, credit state and eligibility | Wrong collection concentration or borrowing base |
| Use productive assets | Age, condition, maintenance, capacity and remaining service | Wrong depreciation, downtime or investment timing |
| Service debt | Currency, reset, maturity, covenant, collateral and priority linked by instrument | Wrong cash need, refinancing or recovery |
| Fulfil a subscription/service contract | Performance obligations, prepaid amounts, renewals and cancellation rights | Wrong revenue timing and liquidity |
| Fund a bank | Deposit counterparties, withdrawal options, loan cohorts and collateral | Wrong run exposure or credit/funding interaction |
| Measure an insurer | Contract/treaty groups, claims development, coverage and component memory | Wrong service/finance/reinsurance movements |
| Allocate cash in a group | Legal owner, transfer restrictions, control dates and reciprocal claims | Consolidated cash mistaken for spendable obligor cash |

These are candidate distinctions to test, not a claim of complete industry
coverage or current standards compliance. A standards basis specifies
recognition, measurement, presentation and memory, while business mechanisms
specify operations. The two interact through taxes, covenants, compensation,
regulatory capital and management decisions. Treating a reporting-basis change
as a label change misses both required opening memory and possible behavioral
feedback.

## Why a probability distribution can replace a growing history tree

A finite partially observed model illustrates the role of a belief. Let the
company occupy state s, let a be an action chosen using the actor's available
information, and let y be the next observation. With a known transition
T(s'|s,a), observation law O(y|s',a) and prior b(s), Bayes' rule gives

$$
b'(s')=\frac{O(y\mid s',a)\sum_s T(s'\mid s,a)b(s)}{p(y\mid b,a)},\qquad p(y\mid b,a)=\sum_v O(y\mid v,a)\sum_s T(v\mid s,a)b(s).
$$

The denominator is required to be positive. Zero probability for observed
evidence is a conflict with the admitted probabilistic model, not permission
to reset weights silently. Kaelbling, Littman and Cassandra (1998),
sections 3.1–3.4, printed 105–108, define this separation between world state,
belief and policy and derive the update. Their model presupposes the state
space and transition/observation model; it does not construct a company from
a filing.

For these assumptions, the belief summarizes the past for the stated future
control problem. That does not make its support small, identify a unique
actual state or recover a state the model omitted. Parameters unknown to the
analyst require joint inference or a declared alternative model. Correlated
reporting errors, persistent hidden management choices and observations of
interval cash flows require the appropriate memory and joint likelihood.
Treating overlapping annual and quarterly totals as independent observations
can count the same evidence twice.

A tree is one way of displaying histories and contingent policies. It need
not be the storage format for every possible world. A symbolic family can
retain constraints on unknown cost layers; a factored distribution can retain
conditional dependence; a shared-prefix graph can avoid storing common
transactions repeatedly. A belief distribution records uncertainty conditional
on information. These representations save work only when their structure is
valid; none guarantees a small exact solution for arbitrary companies.

## What an exact stochastic reduction must preserve

Matching expected balances is too weak for a payment, default or information
problem. We can state a sufficient condition for a finite controlled model
without assuming independent observations and financial outcomes.

Let K(s',y,z|s,a) be the joint probability of next state s', next available
observation y and requested financial output z. The output can include a
vector of cash flows, journals, refusals and reports. Its support and all sets
are finite here. Let rho(s) be a proposed reduced state, with equivalence
classes C. States in one class must admit the same actions, including a
consistent definition of refusal. For every shared action, observation, output
and successor class require

$$
\sum_{s'\in C}K(s',y,z\mid s,a)=\sum_{s'\in C}K(s',y,z\mid r,a)\quad\text{whenever }\rho(s)=\rho(r).\tag{1}
$$

This is equality of the joint law, not separate equality of its marginals.
Givan, Dean and Greig's retained manuscript, sections 2.2 and 3.3 and appendix
proofs of Theorems 5 and 7, establishes the corresponding reward/block-transition
argument for their fully observed MDP. Equation (1) is a local extension for
our declared joint financial-output and observation model, derived next. It
does not import a general partially observed accounting theorem from that paper.

Define the reduced kernel by the left side of (1), using any representative
s from the current class. Equation (1) makes that definition independent of
the representative. Suppose two full beliefs have the same mass in every
class. For a chosen action, the probability of (C',y,z) is

$$
\sum_C\left[\sum_{s\in C}b(s)\right]\overline K(C',y,z\mid C,a).\tag{2}
$$

To obtain (2), expand the probability as a sum over s and s', group s by its
class, and use (1) to replace its inner transition sum by Kbar. Thus the next
observable and reduced-state laws depend only on class masses. Normalizing
the sum over z gives the same next belief over classes after any positive-
probability y. If some output components are observed by the actor, include
those components in y as well; hidden outputs cannot be used to choose actions.

Now fix an initial class-mass distribution and a policy that uses only the
declared observation/action history, with the same independent policy
randomization in both models. Require that each chosen action is admissible
at every state in the current belief support; alternatively, define attempted
actions everywhere and include their refusal outcomes in the preserved law.
Equal action sets inside each class alone do not tell a partially informed
actor which action is feasible across different possible classes.
The first action law is the same. Equation (2)
gives the same first observation, output and reduced-state law. Conditioning
on each positive-probability observed history gives the same argument for
the next step. Induction proves equality of the joint finite-horizon laws
of actions, observations, outputs and reduced states. Consequently any
finite-horizon functional of those preserved outputs has the same law.
This includes discounted value only when its discount factors and cash-flow
arguments are themselves preserved in the declared output.

The conclusion applies to that common information-based policy class. It
does not justify giving an actor the hidden full state, discarding private
signals, or changing who knows what. Multiple actors require a jointly
specified signal process and each actor's information restriction. Infinite
horizons require separate convergence/integrability conditions. Continuous
state spaces, approximate kernels, equilibrium existence and industry-wide
sufficiency are outside this finite derivation.

## Three tempting reductions that fail

First, consider tomorrow's cash of 50 with certainty versus cash 0 or 100 with
equal probabilities. Both have mean 50. A due payment 40 has shortage
probability 0 in the first case and 1/2 in the second. Replacing either
distribution by its mean preserves an expectation but changes feasibility.

Second, suppose a binary cash-flow condition Y and a binary signal H each
have probability 1/2. In one model H=Y; in another H=1-Y. Their separate
marginals agree. After observing H, a manager chooses a=H and earns 1 when
a=Y. The policy succeeds with probability 1 in the first model and 0 in the
second. A reduction that preserves only the separate observation and outcome
marginals is therefore wrong for this policy. Preserving their joint law
in (1) avoids that error.

Third, let the condition be equally likely to be 0 or 1 and let the manager
receive a perfect signal either before or after choosing a. The eventual
condition and signal have the same joint distribution in both models. With
the early signal, expected payoff 1 is achievable; without it, the highest
expected payoff before the signal is 1/2. The dates at which information is
available are part of the simulation. Givan et al.'s section 3.1 likewise
explains why fixed action-sequence comparisons do not suffice for adaptive
policies.

## Learning a hidden state does not identify a causal effect

An exact counterexample separates this issue from filtering. Let an unobserved
U take values 0 and 1 with equal probability. In both candidate models the
observed action is A=U. In model M 1 the outcome equation is Y=A; in model M 2
it is Y=U. Both produce the same observational distribution: (A,Y)=(0,0)
or(1,1), each with probability 1/2. No number of independent repetitions from
that observation law distinguishes the models.

Define intervention do(A=a) to replace the equation assigning A while leaving
U's distribution and the outcome equation unchanged. Under M 1, forcing A=1
versus A=0 changes expected Y from 0 to 1. Under M 2 it leaves expected Y=1/2
in both cases. The causal effect is therefore 1 in M 1 and 0 in M 2. This is a
local structural counterexample, not an estimated effect or a claim about an
issuer. A financial interpretation is a management action selected using
private information that also predicts performance. Good prediction of
performance conditional on observed actions does not settle the effect of
forcing a different action.

Bayesian model weights do not remove this ambiguity. With equal likelihoods,
posterior odds remain prior odds. Useful causal simulation therefore needs
explicit structural assumptions, intervention definitions and, where possible,
additional discriminating evidence. The causal literature survey remains
necessary; this counterexample establishes only that observational fit alone
is insufficient.

## Value, reporting quality and the same underlying histories

A valuation is a functional of future claimant cash flows and their pricing
weights. The existing exact valuation examples show that compatible terminal
terms make dividend and residual-income calculations agree, while equal PV
can coexist with different short-term funding needs. They also show that
equal marginal payoffs have different prices when their dependence on the
stochastic discount factor differs. State reconstruction, policy simulation
and pricing must therefore preserve the dependence relevant to the chosen
claim, not only statement totals or expected earnings.

The inspected Nissim–Penman sections 1–2.3 connect accounting decomposition
to valuation and forecasting. Dechow–Schrand's printed 14–15 describes both
the finite-horizon valuation comparison and the Lundholm–O'Keefe critique
of unequal terminal assumptions. Those competing primary papers must be
read before adopting a comparative-performance conclusion. The same book's
accrual discussion directs attention to estimation errors as well as
managerial choices; its summaries are leads to primary studies, not proof
that every unusual accrual signals misconduct.

The repaired claim/evidence example makes the observation problem concrete.
Reported revenue and receivable 100 can correspond to a timely genuine sale,
a delayed genuine sale, an impaired claim or a purported sale with no service
and no enforceable claim under the stipulated rule. Their correctly stated
books need not coincide. Delivery, enforceability, payment schedule and
credit evidence discriminate different aspects of the hypotheses. Later
collection cannot be used as information available before its disclosure.
An anomaly score supplies neither those facts nor intent.

Penman–Zhang's January 2025 working paper, inspected here through section 3.1,
uses accounting co-determination to motivate asset-pricing factors. This is
a relevant connection, but its risk interpretation is not an operative
accounting standard and its empirical superiority has not been reproduced.
Its market-efficiency assumption and alternative mispricing interpretation
are material. A market price used to infer the state or discount rate also
cannot serve as an independent validation target for that fitted valuation.

## Consequences for AccDSL

The design should retain alternatives explicitly at the level of their
meaning, without requiring literal enumeration as tree nodes. Each family
needs a declared state definition, context, evidence constraints, coverage
status and supported operations. Probabilities require an additional justified
model. Exact reductions require a preservation argument for the actual
queries and policies; approximate reductions require a stated downstream
error target and reference comparison. New observations can narrow a family;
new mechanisms can require expanding it. These are different operations.

Existing typed insurance histories already retain component alternatives
through complete journals and separately typed measurements. A subsequently
inspected reference bridge also connects synthetic publication and ingestion
cutoffs to those histories. Its preparation had to remove H=6 from the
pre-observation model itself: delaying an external disclosure while retaining
the same fact as an embedded constraint would still leak future information.

The next review found a different problem. When two active reports constrained
one measurement, the bridge replaced its interval in input order. H=5 followed
by H=6 selected 6; reversing the reports selected 5. This is wrong when both
assertions are meant to hold. A separate successor now intersects the declared
model domain and every active source interval. It preserves both contradictory
assertions and returns a conditional conflict instead of selecting one. The
115 exact checks also preserve the original complete native-history replays.
The disagreement could arise from a false assertion, incorrect mapping or
wrong model domain; the contradiction alone does not determine which.

Historical information admission with revisions, uncertain clocks, source
reliability and actual actor access remains unfinished, as does broader
source-backed sector/basis construction. A candidate history remains
conditional until its premises are established. This is where the literature,
the company-state problem and the release specification must meet.


## References used in this draft

Givan, R., T. Dean and M. Greig (2003). Equivalence notions and model
minimization in Markov decision processes. Artificial Intelligence 147,
163–223. Retained author manuscript: sections 2.2–3.3 and appendix proofs
of Theorems 5 and 7.

Kaelbling, L. P., M. L. Littman and A. R. Cassandra (1998). Planning and
acting in partially observable stochastic domains. Artificial Intelligence
101, 99–134. Sections 3.1–3.4, printed 105–108.

Nissim, D., and S. H. Penman (2001). Ratio analysis and equity valuation:
from research to practice. Review of Accounting Studies 6, 109–154.
Sections 1–2.3.

Dechow, P. M., and C. M. Schrand (2004). Earnings Quality. Research Foundation
of CFA Institute. Selected sections recorded in the source ledger; printed
14–15 supplies the leads to the valuation comparison and critique.

Penman, S. H., and X.-J. Zhang (January 2025). Accounting for Asset Pricing
Factors. Retained working version, sections 2–3.1; empirical findings and
equation typography remain unreviewed here.
