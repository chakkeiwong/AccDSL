# Keeping possible histories without enumerating a tree

26 October 2026. Follow-up to the simulation-history and financing review.

Each possibility needs a precise meaning, but it need not occupy a separately
allocated node. AccDSL should store a joint family of possible economic
histories using variables and constraints, share common records and calculations,
and expand particular cases only when a requested calculation requires them.
A tree can display selected explanations or future observation paths. It
should not be the authoritative enumeration of everything that could happen.

This builds on the current design: the language already stores alternative
relationships in a constraint graph, partitions unknown rule guards, and
distinguishes evidence refinement from correction. The implementation design
already calls for shared immutable histories and branch-local changes [R1–R3].
The additional requirement here is that compression preserve future learning,
not just current reports or a fixed collection of forecasts.

## Separate the world from what each actor knows

Let theta contain persistent unknown facts, such as existing loan terms, and
let X_t contain the economic state at time t. A simulated loan has one set of
terms; analyst uncertainty about those terms does not mean its fixed/floating
status is randomly redrawn each period. Modifications or refinancing are
separate dated events. Future innovations evolve X_t under a stated model.

The analyst maintains either a feasible family C_t or, when a probability model
is justified, a distribution mu_t over that family. For compatible hard
evidence about the same historical scope, the update is

    C_new = {h in C_old : h is compatible with the new observation}.

For a noisy observation with a declared likelihood L(y | h), the probabilistic
update is proportional to L(y | h) mu_old(dh), with a positive finite
normalising constant. Hard conditioning on an exact continuous value instead
requires the appropriate conditional measure; an arbitrary tiny Gaussian is
not an automatic replacement. Missing or uninformative evidence may leave an
old ambiguity unchanged. Zero normalisation or an empty family is a conflict
or model problem to investigate, not permission to select a convenient case.

Forward propagation and new evidence are different operations. Extending the
horizon can introduce new uncertain events and enlarge future outcome ranges
even while evidence narrows the compatible old histories. A restatement or
rejected source creates a revised evidence view; it is not blindly conjoined
with the assertion it replaces. Previously frozen forecasts remain reproducible.

Some uncertainty may never resolve. Preserve it as uncertainty unless later
evidence distinguishes it or it ceases to matter for a particular query. A
repaid loan may become irrelevant to future cash flows while remaining relevant
to historical explanations or later inference about management behaviour.

Each decision maker also needs its own information view. Company managers may
know their loan contracts while a public-data analyst does not. Their simulated
actions can legitimately differ across those contract histories. By contrast,
a manager who does not yet know next year's sales shock cannot choose a
different action today because a simulator already sampled that shock. The
same policy must prescribe the same action distribution at indistinguishable
information histories. If policy randomness is used, its sampling convention
must be explicit; unrelated future randomness cannot become private knowledge.

In a model of future learning, branch on what an actor may observe. Update
that actor's simulated information state after the observation and choose the
next action from it. Such observations belong only to the hypothetical run.
They do not resolve the analyst's actual evidence outside the simulation.
Belief-state filtering and control in a fully specified probabilistic model
provide the formal analogue [S2]. AccDSL must also support unweighted families,
which are not ordinary probabilistic POMDP beliefs without additional choices.

## What to store

The proposed record has separate references to:

| Record | Contents |
|---|---|
| History family | Shared events/contracts, persistent variables, domains, joint constraints and source support |
| Evidence view | Available observations, cutoffs, corrections and review decisions |
| Information view | What a particular actor can know at a decision date |
| Optional measure | Prior/likelihood or other justified joint weights, with measure provenance |
| Execution state | Concrete or symbolic economic/accounting state, shared ancestors and local changes |
| Query | Outputs, scenarios, horizon, permitted policies and error requirements |
| Result | Conditional formulas, cases, bounds or estimates, with completeness and approximation status |

A constraint or expression graph shares repeated logic; a provenance graph
shares source and history records; a transition graph shares equivalent
execution. These can use related IDs, but they have different edge meanings.
The logical constraint graph need not be a probabilistic network, and its
displayed arrangement does not establish statistical independence. A directed
acyclic graph for immutable expressions or dated execution can share parents
and future states; cyclic economic dependencies still require a specified
simultaneous solver. Replacing the word tree with graph does not solve them.

A node can denote a whole feasible region. Discrete alternatives can be
mutually exclusive guards over that region; continuous uncertainty can remain
an interval, polytope or other constrained domain. Preserve the joint
constraints. Independent marginal intervals can admit combinations that no
single company history could produce.

## Control expansion before approximating

1. **Keep variables symbolic.** Twenty binary facts have 2^20 possible
   assignments, but their domains and many useful relations can be stored
   without creating a million company records. A constraint representation
   can remain small even when solving every requested query is hard.
2. **Share common work.** Reuse the same source records, common event prefixes
   and expression nodes. A changed rate clause need not copy an entire
   company. Sharing does not remove any economic alternatives.
3. **Follow the requested dependencies.** Resolve only variables needed for
   the requested outputs, event guards, actor decisions or observation model.
   Exact elimination must preserve the constraints induced on the remaining
   variables. Leaving an irrelevant factor unevaluated is not evidence that
   it is absent or independent.
4. **Split when necessary.** If all members satisfy the same posting or
   contract rule, apply it symbolically. If an unknown crosses a reset,
   covenant, liquidity or default threshold, partition by that guard only
   when needed for the answer. A piecewise expression may represent the split
   without allocating separate full states.
5. **Merge only under an adequate sufficiency argument.** Keep distinct source
   provenance even if two histories can share forward execution.
6. **Use bounded approximation where exact work remains expensive.** Choose
   the method and error statement for the query, and retain the unexplored
   family instead of silently deleting it.

Darwiche and Marquis show why the first two steps are useful and why their
limits matter: representation size and supported operations trade off, and
tractable queries on a compiled structure do not imply that compiling it is
cheap [S1]. No claim here is that every AccDSL family has a compact exact
representation or that a million distinct journals can be printed cheaply.

## A small example with continuously many possibilities

Assume debt of 100, historical annual interest of 5, and an unknown floating
fraction alpha in [0,1]. Fixed and floating parts had the same historical
rate. Assume a two-percentage-point shock passes through to every floating
part for the full next year, with no amortisation, hedge, floor or cap. Then

    next interest I(alpha) = 5 + 100 * 0.02 * alpha = 5 + 2 alpha.

The engine can return this formula and the exact interval [5,7] without
enumerating alpha. If the opening cash is 95 and interest is the only payment,
closing cash is 90 - 2 alpha. Those results remain linked: closing cash plus
interest is 95 in every history. It is wrong to independently select interest
7 and closing cash 90 as one possible company.

A later disclosure that restricts alpha to [0.2,0.4] narrows next-year interest
to [5.4,5.8] and closing cash to [89.2,89.6], while retaining the same relation.
No informative disclosure means alpha remains unresolved.

If a covenant requires closing cash of at least 89.4, the formula gives the
exact partition alpha <= 0.3 versus alpha > 0.3. After that disclosure both
regions remain possible. At this point the engine must account for different
covenant consequences if those consequences affect the requested answer. A
covenant breach is not automatically default: cure, waiver and acceleration
depend on the contract and policy. The equality belongs to the non-breach
region under this explicitly inclusive threshold.

This exact reduction does not survive every new query. Different maturities,
rate-reset calendars or caps may require individual tranches. The aggregate
alpha must then be refined from the retained underlying constraints.

## Compression must preserve learning

Equality of today's balance sheet is insufficient for merging. Equality of
future reports under one fixed scenario can also be insufficient when future
observations change later decisions. Two histories can produce the same cash
flow today but different probabilities of a revealing disclosure tomorrow.
Dropping that difference can change the inferred state and subsequent policy.

A sufficient condition for exact probabilistic aggregation is that, for each
permitted action and scenario, states with the same compressed representation
have the same feasible actions, current requested outputs and joint
distribution of next compressed state, observations and required outputs.
The initial information distribution and updates must also be mapped
consistently. Under that condition, induction over time preserves the output
and observation law for policies adapted to those observations. This is a
project sufficiency argument, not a claim that a checker already exists.

For unweighted families, the corresponding requirement is to preserve the
feasible joint successor/observation possibilities and their persistent
cross-time constraints. A union of one-step marginal possibilities is not
enough: it could permit a fixed hidden contract to change type between dates.
Retaining the latent variable in a symbolic state is often safer than
attempting a lossy merge.

Approximate grouping needs an error statement tied to actual questions. An
error of 0.1 in cash may be negligible for a revenue chart and decisive at a
covenant boundary. Before collapsing a region, test whether its uncertainty
can cross relevant guard thresholds. An unresolved crossing requires further
refinement or an explicitly unresolved result. A new output, observation model,
scenario, policy or horizon invalidates a compression approval that does not
cover the change.

## When the exact family is still too expensive

Use a budgeted query evaluator over the retained family. Budgets can limit
time, memory, solver calls and expanded regions; choose them as engineering
settings, not assertions about economic truth. The evaluator should preserve
known results and the unfinished frontier. A budget stop is incomplete
computation, not evidence of impossibility.

| Requested result | Suitable treatment | Necessary qualification |
|---|---|---|
| Best/worst feasible cash or profit | Exact optimisation where supported; otherwise certified relaxations and adaptive splitting | Feasible witnesses supply attainable examples; relaxed bounds must be labelled and cannot claim joint attainability |
| Can a covenant be breached? | Solve threshold feasibility and retain a witness or infeasibility certificate | Timeout/unknown is not safe/no breach |
| Conditional mean or probability with a justified measure | Quadrature or conditional analytic calculation when feasible; weighted simulation/particles otherwise | Sampling error, target measure and missing/failed contribution remain visible |
| Unweighted alternatives | Symbolic constraints plus optimised or targeted witnesses | No probabilities from the number of witnesses; sampled minima/maxima are not outer bounds |
| Individual explanation | Materialise a requested witness and its journal trace | One witness is not the whole feasible family |

If particle filtering is used, a particle is an approximation unit, not an
ontological claim that other histories do not exist. Resampling can remove
old genealogies and rare modes; Doucet and Johansen discuss this explicitly
[S3]. Do not make the surviving particles the only stored historical family.
Preserve structural alternatives outside the sample, keep weights correct
when allocating extra samples to a stress region, and use a targeted
feasibility calculation for important rare-event possibilities. Analytically
integrating suitable conditional submodels can reduce the sampled dimension
without asserting independence [S3, §4.6].

Selecting representative states or clustering trajectories is approximate
unless a sufficiency/error argument is supplied. Rare or small-weight states
cannot be discarded solely because expected outputs barely change if a tail
or covenant question is in scope. If bounded output Y lies in [L,U] and a
known probability mass delta < 1 is removed and the remainder renormalised, the
mean error is at most delta*(U-L): the full mean is (1-delta)*m_kept +
delta*m_removed. Without a known mass and output bound this guarantee is
unavailable; in particular, counting pruned solver branches cannot supply it.

Full robust-policy optimisation, a solver choice and general particle tuning
are separate tasks. This note recommends interfaces and safe semantics, not
an untested numerical default.

## Implementation consequence

Extend the existing shared IR with explicit links between a history family,
actor information view, optional observation/weight model and query-specific
execution. Build a lazy evaluator that returns a symbolic answer whenever
possible and refines only the unresolved guards needed by the query. Keep
exactly shared records, exactly equivalent execution and approximate
summaries visibly different.

The first acceptance case should use the alpha example to check persistence,
disclosure refinement, joint outputs and the covenant boundary. Add two cases
where current reports coincide but future resets differ, and where current
outputs coincide but later observations lead to different decisions. Also
check a source correction and a resource stop. Those tests would directly
address MC08–12, MC14 and MC18; no implementation completion is claimed here.

## Sources and existing design

- R1: [Language alternatives and updates](../chapters/06-language.tex), unknown guards and alternative readings/updates.
- R2: [Mathematical grouping and uncertainty](../chapters/05-mathematics.tex), conditional laws and which details may safely be combined.
- R3: [Implementation storage and execution](../chapters/09-implementation.tex), immutable sharing and result dimensions.
- S1: [Darwiche and Marquis, A Knowledge Compilation Map, 2002](../../papers/A%20Knowledge%20Compilation%20Map%20Darwiche%20%282002%29.pdf), Definition 2.1, §2 decomposability/determinism, §3 succinctness, §§4–5 queries/transformations.
- S2: [Kaelbling, Littman and Cassandra, Planning and Acting in Partially Observable Stochastic Domains, 1998](../../papers/Planning%20and%20Acting%20in%20Partially%20Observable%20Stochastic%20Domains%20Kaelbling%20%281998%29.pdf), retained 12 February 1998 preprint, §§3.1–3.4, pp.9–12 visually inspected.
- S3: [Doucet and Johansen, A Tutorial on Particle Filtering and Smoothing: Fifteen years later](../../papers/A%20Tutorial%20on%20Particle%20Filtering%20and%20Smoothing%20Fifteen%20years%20later%20Doucet%20%282008%20corrected%202012%29.pdf), December 2008 version with March 2012 corrections, §§2.1–2.2, 3.3–3.6, 4.6.

Primary reading is targeted to the claims above; no exhaustive survey or
independent solver-code audit is asserted. Source versions, acquisition
routes, checks and remaining limits are recorded in the
[review result](../../../data/accounting-master/uncertainty-representation-20261026/result.md).
