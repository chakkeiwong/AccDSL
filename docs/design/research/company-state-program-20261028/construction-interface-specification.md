# From company operations to an admitted state family

28 October 2026. Proposed common design specification for T01/T03/T05/R01.
This document assigns responsibilities to inspected existing interfaces. Its
construction procedure is a specification, not a claim that a general
constructor has been implemented.

## The construction request

A request identifies the legal entities and consolidation perimeter, economic
and reporting dates, currencies and units, accounting basis and version,
requested operations/reports, shock/intervention mode, actor information and
permitted policies. It also declares the available source population and
whether its coverage is complete, partial or unknown. Completeness is relative
to a stated population; it cannot be inferred from having one feasible history.

The request must say whether it asks for a possible history, a range over all
histories within a declared model, a weighted forecast, a feasible policy or
a value for a particular claim. These targets require different evidence.
One feasible witness establishes existence only within its supplied premises.
A robust bound requires coverage or a certified outer representation. A
posterior additionally requires a justified prior and joint likelihood.
A causal intervention needs a structural replacement rule; conditioning on
an observed management action is a different calculation.

Each requested operation carries a versioned definition of its read quantities,
preconditions, monetary effects, memory effects, refusal outcomes and report
consequences. Each quantity has a context, unit, economic owner, accounting
memory owner and source/assumption origin. The allowed expression language
and numerical fragment are explicit. A derived quantity names its parents.
An external shock names its probability or scenario interpretation.

## Construct the state by closing operation dependencies

Begin with the inputs to every requested transition, refusal and report.
Classify an input as current economic/contract state, accounting memory,
retained history, external realization, model parameter, actor information
or a derived quantity. Follow derived quantities to their parents until each
leaf has an admitted source, a declared hypothesis, an unresolved obligation
or an unsupported operation. Recursion must terminate on a finite declared
registry; a cyclic dependency is either an explicitly specified simultaneous
problem with its own solver semantics or an unsupported construction.

A report over a past interval can require historical transactions after its
closing stock has ceased to distinguish the histories. Conversely, a model
can retain a sufficient accumulator instead of all transactions if a proof
covers every permitted historical query. Such a reduction is a model choice
with a preservation argument, not a storage convenience.

For collections, retain the counterparty and enforceable claim, maturity,
currency, settlement history, credit premises and any collateral eligibility.
If the claim is impaired, gross amount and allowance remain distinct. For
FIFO sales, remaining lot order and cost are read dependencies; a sum of costs
cannot substitute. For insurance component remeasurement, retain the separate
components even if the report observes only their net. The prior exact cases
provide counterexamples to particular insufficient dependency sets.

The dependency closure produces candidate state definitions and construction
obligations. It does not discover all possible industry mechanisms. A missing
mechanism can invalidate the claimed coverage even when every declared
dependency is present. Model-scope exclusions therefore accompany the result,
and an operation outside that scope must be refused or trigger refinement.

## Evidence constrains paths and sometimes the model itself

A source assertion records exact retained bytes and span, author/issuer,
subject, context, measurement definition, interval or point, modality, precision,
publication and ingestion information, and revision identity. Extraction,
interpretation, assumed rounding and asserted economic truth are distinct.
An uncertain reading creates alternatives; it is not silently selected because
one interpretation makes the balance sheet reconcile.

Observations of balances constrain a snapshot. Observations of revenue,
expense or cash flow normally constrain an interval path or its accumulator.
Narrative statements can constrain admissible instruments, populations,
rights, transitions or reporting policies. A common source identifier retains
its dependence across those constraints. Copies and restatements cannot be
treated as fresh independent observations without a model of their relation.

For simultaneous hard interval assertions about the same quantity, intersect
the admitted model domain and all active assertion intervals. Preserve strict
endpoints. The executed successor demonstrates that this operation is
order-independent and that contradictions remain visible. It deliberately
does not decide reliability or revisions. If an assertion is considered
unreliable, add a reliability model or alternative source interpretation;
do not weaken the hard assertion invisibly.

A later correction has at least two distinct meanings: what was reported at
the earlier public cutoff, and what is now believed about the earlier economic
period. Preserve both queries. Before joining a revised assertion, specify
what it supersedes, when the supersession became available, what historical
results are invalidated and which completed real cash flows remain unchanged.
Unknown availability yields an unresolved as-of result. Public availability
does not prove any particular actor actually received the information.

## Constructing and returning alternatives

Instantiate the declared economic/event templates with domains that retain
unknown quantities, identities and relevant population structure. Link
variables shared across dates, reports, contracts and accounts. Check context
and units before lowering their joint constraints to a supported solver.
Return scope and coverage together with feasibility.

The result distinguishes malformed input, unresolved required meaning,
unsupported mathematical operation, resource-limited search, a feasible
conditional family and a certified contradiction within the supplied model.
The native status names at each interface remain authoritative; a common
description cannot replace them with an unreviewed universal enumeration.
A contradiction says that the admitted assumptions and observations cannot
all hold together. It does not identify which assertion, mapping, template
or domain is wrong.

For a finite supplied family, list retained members and excluded members with
the relevant constraints. For a symbolic family, return the shared variables,
constraints, witnesses and any certified bounds plus residual coverage.
For a weighted result, attach the additional probability model, information
cutoff and dependence assumptions. Do not silently turn set membership into
equal weights or a solver-selected witness into the actual company.

## Native responsibility map

| Inspected responsibility | What it establishes | What the construction must still supply |
| --- | --- | --- |
| NativeReturnStateStructure/1 | Pinned legal-book shape, exact scalar/context fields, lots, tax/cash-flow history and source pointers | Economic truth, complete state dependencies and broader sector support |
| MethodStateAssessment/1 | Classification of selected supplied-state requirements, including funding failure distinct from malformed state | Actual resource facts, other admission criteria and complete operation coverage |
| TypedAffineHistory/1 | Joint event/account/memory equations and complete supplied-witness replay | Template/population selection and source-derived premises |
| TemporalMeasurementConstraints/1 | Typed time/quantity relations in its declared rational fragment | Assertion meaning, publication/ingestion and actor access |
| TypedHistoryMeasurementAttachment/1 | Separate typed measurements joined to full history snapshots or movements | Validated semantic mappings and source-information obligations |
| SharedStateCompatibility/1 | Same-profile/same-state compatibility and explicit missing cross-profile evidence | Actual composition, migration and exclusive financial-effect ownership |
| InsurancePAADatedBook/1 | Selected group/calendar/component inputs through declared company events and full interim reports | Broader group domains, annual carry, actuarial uncertainty and applicability |
| BankComponents/1 and /2; BankAssessment/1 | Distinct selected banking and historical prudential responsibilities | Same-basis/perimeter joins, common memory and accounting versus prudential reconciliation |
| Scoped information-intersection successor | Conjunction of supplied hard intervals without order-dependent overwriting; preserves complete native histories | Revision selection is a separate responsibility; reliability and actual source construction remain open |
| ConditionalRevisionInformationView/1 | Native original/latest supersession, conservative integer-day availability summaries, public/system/actor views and separate selected-assertion projection | General joint chronology, authenticated receipt, source truth and justified noisy likelihoods |
| BoundTemporalPolicyFamily/1 | Verified joint rational-clock families, source/revision/access provenance, every nonempty proof support and explicit budget remainder | Supported common quantity semantics and actual actor observation/action meaning |
| CertifiedTemporalNativeHistoryJoin/1 | Exact preservation of a verified temporal family while attaching proposed typed measurements to complete native histories | Its cross-case interpretation is synthetic; common issuer/source semantics and source-backed sector construction remain open |

Equal account labels are not an equivalence or migration proof. In particular,
SharedStateCompatibility/1 explicitly refuses to infer shared-book composition
from common names. Its missing-evidence categories—account meaning, module
memory, flow ownership, tax policy, report policy and source scope—are required
inputs to any later composition specification.

### Source meaning and temporal alternatives

The executed certified join deliberately separates source selection from source
interpretation. Each selected head receives an explicit proposed interpretation
with matching quantity type, context and period. A head that adds no constraint
also receives an explicit disposition. The same head must keep the same meaning
through every temporal alternative in this bounded profile. Competing meanings
would require an explicit interpretation family; silently changing a source's
meaning with an unobserved clock branch is refused.

Every original temporal outcome and its supporting cells survive the join.
Retractions, conflicting source heads and unavailable required records remain
unresolved. Two different head histories that imply equal measurements retain
their separate evidence. A clock-budget stop retains the entire original domain
under the inherited reference; it does not return a completed prefix disguised
as the whole family. Unknown trust or timing remains recorded even if other
chronology constraints entail a selected view. No probability is inferred from
the number of supporting clock cells or source alternatives.

The two information adapters have distinct stated premises. The compact native
supersession adapter can determine a latest revision without requiring every
ancestor's availability. The certified temporal profile conservatively requires
available ancestry and separately checks authorship, publication, ingestion,
review, effective time and actor access. These are different conditional query
contracts, not interchangeable implementations of one unstated default. A
source-specific choice between them needs an explicit justification.

The complete joined result is for audit and inference. It supplies no policy
input, because the inherited financing example and native insurance example
have different decision populations. Its exploratory proposed interpretation
does not establish a common issuer or turn financing source text into an
insurance fact. Real application still requires supported source meanings and
a common actor observation/action interface. The earlier compact adapter's
selected-assertion projection is likewise a scoped conditional interface,
not proof of actual actor receipt or general production access enforcement.

Execution and adverse cases are in
data/accounting-master/unified-program-20261028/certified-join-result.md and
revisions-result.md. These clarify construction responsibilities without
claiming that the general source-to-company constructor is implemented.

## Industry extensions and changes of reporting basis

A sector adds resources/contracts, transition laws and memory by specifying
which existing operations it refines and what new operations it permits.
Its extension must account for all new reads, writes, guards and financial
effects. A company-specific override must satisfy the package's admissibility
rules; accepting an arbitrary formula is not a standards-compliant override.

A basis migration declares the source and target contexts, retained economic
identities, opening memory, transformation of comparatives and treatment of
measurement differences. Missing opening information leaves a family of
possible target memories or an unresolved migration. It does not permit
renaming a source profile. Tax, covenants, regulatory capital and management
responses require separate explicit feedback where they depend on the new
reported amounts.

A group composition similarly identifies legal owners, control dates,
transfer restrictions, reciprocal positions, consolidation adjustments and
the single owner of each cash or noncash effect. A consolidated resource
can be unavailable to the entity that owes a payment. Complete before/after
legal books and adjustment books are needed to check that the composition
neither creates a balancing plug nor posts an effect twice.

## Refinement and acceptance

New evidence can narrow an existing family. Discovering an omitted state
distinction instead changes its definition. Record the relation between old
and new states, preserve the former result under its original scope, and
recompute every affected report, policy or valuation. The exact deterministic
and finite stochastic reduction conditions govern only the operations and
information they actually preserve.

This specification closes the responsibility ambiguity between defining state,
validating supplied state and inferring state from evidence. It does not yet
close the general construction task: complete source-backed template
instantiation, industry/basis composition, general revisions and independent
implementability evidence remain required. Those are concrete T01/T03/T05/R01
deliverables, not reasons to repeat the completed finite examples.
