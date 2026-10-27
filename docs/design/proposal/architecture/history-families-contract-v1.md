# History families: proposed contract, version 1

This contract specifies how one set of disclosures can support several joint
financial histories. It addresses MC08–MC11 and G1/G16, with evidence, chronology,
language and reproducibility dependencies under MC02/MC04/MC05/MC18/MC25/MC27.
It is a proposed specification. Its examples are deliberately synthetic;
independent review, accounting validity and human acceptance remain pending.
The companion `history-families-fixtures-v1.json` contains specified inputs and
expected results, not observations from an implemented engine.

## H1. Inputs and the question being answered

A reconstruction request supplies the following versioned records. References
mean immutable record versions and content hashes, not a mutable name such as
“latest”. A declared unknown differs from an omitted required field.

| Record | Required content | Admission consequence |
| --- | --- | --- |
| Evidence/time view | Source, reading, interpretation and review IDs; admission mode, selection mode, cutoffs, context-specific candidate-set revisions and unknown eligibility | Use the evidence v3 and time v2 rules. Unknown availability remains an affected-query obligation. |
| Observation | Concept, entity, perimeter version, economic instant or half-open reporting interval, calendar, basis, unit/currency, scale, sign and precision/rounding support; expression and source links | Two occurrences may refer to one quantity only through a supported context mapping. Never equate totals from different periods or bases by matching labels. |
| Interpretation and assumptions | Alternative IDs, conflict scope, admission layer, selected conditions, rationale, author and dependency versions; separate uncertainty category | Reading acceptance is not factual truth, treatment permission or a probability. An unselected assumption is not a constraint. |
| Opening state | Economic identities, rights/obligations, dated contract/lot/cohort state; accounting balances and reconciliation where supported; explicit unknown domains | Missing opening facts remain variables/obligations. Missing accounting support cannot be filled by balancing entries. |
| Model scope | Entities/perimeters, periods, candidate event/contract types, admissible domains, exclusions and reasons, template registry and mappings with versions | Finite slots or a bounded timeline are declared modeling restrictions, never evidence that excluded events did not occur. |
| Source obligations | Every in-scope observation/narrative obligation, applicability decision, dependent query and disposition | Unmapped, disputed, unsupported and not-yet-inspected content remains visible. An unexplained disposition prevents scope adequacy. |
| Query and budget | Requested layer, outputs, views/composition, scenario drivers and horizon, resolution, explicit resource ceilings, traversal policy and continuation reference | Omitted budget or view composition is a request error. Zero budget is valid; it is not an empty family. |

A template proposal must name its origin (source-supported, supplied assumption
or candidate requiring review), applicability conditions, economic state and event
effects, observation mappings, and accounting rules if it requests journals.
Each admitted constraint points to its exact support or selected assumption.
Unsupported accounting treatment is retained as an unresolved proposal with its
reason; it does not become an admissible treatment branch. Conversely, supported
reported-value arithmetic can proceed without claiming that a journal exists.

The output identifies its **target layer**. A conditional reported-value family
can be defined while the accounting-history family is unresolved. Calling both
simply “feasible” would conceal a different target. Any unresolved obligation
that can change membership in the requested family prevents an unconditional
admissibility claim, even if the currently enforced subset has a witness.

## H2. Joint trajectories, views and identity

Let h contain the chosen interpretations, dated economic states, events and,
where admitted, journals and balances. Within declared scope M and immutable
view v, define F(M,v) as the set of h satisfying all admitted opening,
transition, context-mapping and observation constraints jointly, conditional
on the listed assumptions. A missing required constraint leaves a partial
formulation; the implementation must retain the obligation and label witnesses
of the relaxed formulation as candidates, not validated members of the target.

Shared economic IDs link contracts across periods and accounts. Observation
IDs identify assertions; they are not substitute contract IDs. Two assertions
about the same balance constrain one shared variable after context alignment.
A bridge connects successive states using the same events. For example, the
synthetic opening 100 plus an event amount 20 implies closing 120. A candidate
closing 110 fails that bridge even if 110 appears elsewhere as a possible total.
This small identity assumes no omitted flows or valuation effects; actual
bridges require the accounting and domain contracts.

For the principal example, let nonnegative amounts x and y denote two components
of one reported total in synthetic USD. The disclosure condition is x+y=100.
The marginal ranges are each [0,100], but x=y=100 is impossible because its sum
is 200. Projection onto x may return [0,100], retaining the parent-family ID and
an extension obligation: any downstream use must find a y satisfying the same
family. Joining independent marginal ranges discards that obligation.

A named view is a predicate on the parent family, not another independent
history. Write A={h in F: x>=40} and B={h in F: x<=60}. Their intersection has
40<=x<=60 and y=100-x; their union is F. The overlap is not counted twice.
A request with several view IDs must say union or intersection. Views can also
leave parts of F uncovered. They provide no probability weights. Composition
across different family/view versions returns `FAMILY_CONTEXT_MISMATCH` unless
an explicit versioned alignment transformation proves the intended relation.

Family representation identity includes the full immutable semantic manifest:
view/review versions and candidate membership, scope, variables/domains,
constraints/support, selected assumptions, template/mapping versions and
resolution. Changing those fields creates a new family version. Merely changing
a search budget or traversal does not. A query has its own identity including
the family version, requested outputs, composition, layer, scenarios and horizon.

An individual witness identifies its family, complete assignments and dated
trajectory, interpretation choices and provenance. Two labels attached to the
same assignment do not create two witnesses. Different provenance manifests can
represent equal economic trajectories without sharing representation identity;
economic equivalence needs a stated comparison domain and argument. No solver
normal form or content hash proves that equivalence. A symbolic region is not
one witness and cannot be assigned one vote in a distribution.

For E05, an explicit conditional selector k in {A,B} gives
(k=A and revenue=120) or (k=B and revenue=110), with cash=40. These are assumptions
about which conflicting source to use, not evidence of a source's correctness.
The unconditioned reported-value response remains unresolved with both values;
the ratios conditional on A and B are 3 and 11/4. The target is not
revenue=120 and revenue=110. Choosing that conjunction would compute an empty
set for a different question. Missing treatment authority blocks journals in
both branches. Unknown source eligibility also propagates; constructing a
conditional branch cannot bypass time admission. E05 still lacks a qualifying
real-source conflict; this example does not repair that source gap.

## H3. Construction, search and continuation

The proposed interfaces are staged so that each decision has an accountable
input and an inspectable output. They do not select a solver or implement it.

| Operation | Input | Output and stopping rule |
| --- | --- | --- |
| ProposeCandidates | Reviewed view, opening state, scope and versioned template registry | Candidate instances, applicability reasons, exclusions and source-obligation dispositions. No arbitrary-disclosure discovery claim. |
| AdmitConstraints | Candidate instances plus category-specific evidence/assumption/treatment decisions | Supported constraints with origin IDs, rejected proposals with reasons, unresolved obligations and target-layer completeness. Stop target-dependent admission on missing authority. |
| BuildFamily | Admitted constraints, domains and full dependency manifest | Family formula/representation, shared symbol map, search partition specification, unresolved formulation obligations. Reject duplicate/conflicting IDs, missing context or undeclared symbols. |
| ValidateWitness | Family version and full candidate assignment/trajectory | Satisfied constraints with checked support, violated constraints, unsupported checks or missing fields. Valid only when every required target constraint is checked. |
| SearchFamily | Family version, explicit budget, capabilities, traversal and optional receipt | Evidence about regions, witnesses, infeasibility reasons/proofs, unresolved regions and a continuation receipt. A resource stop preserves the original formula. |
| QueryFamily | Family plus requested view/projection/scenario/resolution | Set/region or conditional results with completeness and dependency status. Bounds from explored regions are labelled explored-only. |

Source obligations use `mapped`, `not_applicable_with_reason`, `out_of_scope`,
`disputed` or `unresolved`. `Mapped` requires the actual constraint/support IDs;
several assertions can support one constraint without double-counting evidence.
`Not applicable` requires a reason and review version, not just a count.
Out-of-scope disclosures remain on the coverage report and wider mission queue.
A source count equal to a constraint count establishes none of these relations.
P17 must supply domain-specific candidate generation and applicability methods.

Search may partition a family into reproducible decision cells. Each cell
retains the original family formula AND its decision assignment/predicate.
A declared finite choice needs an explicit domain; continuous quantities remain
regions. The partition manifest states why its cells are exhaustive and
nonoverlapping. Named views are not automatically cells. If the backend cannot
establish a partition, retain the original region as unresolved instead of
inventing a finite-universe completeness claim.

For the examples, a cell key is the tuple (partition-version, decision-ID,
value-ID), or a sorted tuple of these assignments for several decisions. Decision
and value IDs come from the immutable manifest, never array positions or
traversal order. The retained key and manifest uniquely reconstruct the cell;
a digest can index them. General byte encoding belongs to language/IR. A search
receipt records the exact manifest, explicit traversal order, examined keys,
unvisited keys or a reconstructible range predicate, formulas, resource use,
backend/version and unresolved reasons. Ordinal suffixes are valid only with
the pinned ordering/domain manifest; changing order cannot reuse an old suffix.

A cell has one of three coverage dispositions: represented feasible region with
validated witness or another supported existence argument; proved infeasible
with checked contradiction/proof and scope; unresolved, retaining the region
and reason (`unvisited`, `unknown`, `unsupported`, `interrupted`, `cancelled`).
A feasible continuous region is preserved symbolically: one sample never
exhausts its points. “Every declared cell decided” means the whole family is
represented within M, not that every history was enumerated. All-cell
infeasibility proves emptiness only for the complete admitted formulation and
an exhaustive partition. Unsupported required operations or unresolved source
obligations veto that stronger conclusion.

The response therefore reports three independent fields: `existence` (witness,
proved_empty, unknown); `declared_search` (complete, partial, not_started);
`economic_scope` (supported_for_declared_scope, unresolved, explicitly_limited).
A scope may be explicitly limited even when search is complete. A partial
formulation also reports `formulation_complete=false`; its candidates do not
set target `existence=witness`. These statuses are scoped to the requested layer.
No value of these fields alone certifies whole-company coverage.

Resume requires exact semantic-manifest and partition identity. A changed
budget can continue unresolved cells. Changed evidence, assumptions, domains,
rules or partition create a new request and prevent blind continuation. Preserve
already committed partial work on cancellation; if a cell's result was not
committed, leave that whole cell unresolved. A zero-budget request returns the
entire original region unresolved and no proof of emptiness. No new solver is
required to specify this behavior.

## H4. Economic memory, grouping and refinement

A historical accounting balance does not describe all future contractual cash
flows. A principal of 100 with a fixed rate of 5% and a principal of 100 whose
floating rate was 5% can produce the same stipulated historical interest of 5.
If the next full-year rate is 7%, future interest is respectively 5 and 7. A
principal due next year and one due a year later can likewise have identical
current balances but different principal repayments within a one-year query.
The histories must retain rate/reset terms and maturity even when their
historical postings happen to agree. The example establishes arithmetic under
specified simple-interest assumptions, not a recognition or valuation method.

Required state is determined by requested scenarios, horizon and outputs plus
the applicable domain methods. It includes legal entity/perimeter, ownership and
rights, contract/lot/cohort identities, currency, principal/units, recognition
and measurement basis where applicable, rates/resets, schedules/maturities,
options/guarantees/collateral and linked dependencies whenever those affect the
query. “Unknown” is a value status requiring preservation; absence of a field
cannot silently mean no guarantee or no option. Later banks, insurance, groups,
FX, securities and cross-standard methods must extend these state requirements;
a scalar balance schema is not a whole-product substitute.

A grouping request names constituents, transformation/version, retained detail,
scenario domain, horizon, outputs, rules and exact/approximate claim. An exact
certificate must show that aggregation G commutes with every admitted transition
T for that domain, G(T(s,u))=T_group(G(s),u), and that requested outputs satisfy
O(s)=O_group(G(s)). These are proof obligations, not general facts about
financial balances. Missing proof/evaluation returns `GROUPING_UNSUPPORTED`;
it leaves detailed histories available and cannot delete them. A certificate is
part of query/resolution identity, with constituent and rule versions.

For the deliberately narrow simple-interest fixture, two principals 40 and 60
share entity, currency, a fixed 1/20 annual rate, a common day-count convention,
no intermediate principal change, and maturities after the half-year horizon.
Only total principal and interest are requested. Individual interest is
40*(1/20)*(1/2)+60*(1/20)*(1/2)=1+3/2=5/2. Grouping gives
(40+60)*(1/20)*(1/2)=5/2 by distributivity. Principal remains 100 under both
representations; any stipulated interest-payment cash transition subtracts the
same 5/2. This proves the named aggregate outputs/transitions for those
assumptions, not contract-level cash flows or other accounting measurements.
Constituent records remain linked so a later query can refine the group.

A changed output (individual contract exposure), rate/reset/maturity/guarantee
assumption, rule or horizon requires a new sufficiency decision. Reusing the old
certificate returns `RESOLUTION_REVALIDATION_REQUIRED`. Refinement produces a
new resolution version linked to its parent and constituent detail; if the
required detail was never preserved, return `DETAIL_UNAVAILABLE`, not fabricated
lots or contracts. Refinement can restore represented detail, not recover facts
that were never known.

Approximation is a distinct, optional future claim. Its record must name each
output, unit, scenario/horizon domain, absolute/relative tolerance, justification,
error argument or evaluation evidence, and exact-detail fallback. No tolerance,
empirical error bound or approximate grouping is approved by this contract.
Changing the query invalidates the approximation's applicability. Counts of
similar contracts and similarity of old postings are insufficient evidence.

## H5. Revisions, errors and layer interactions

Current eligibility depends on the candidate population as well as selected
assertions. Adding a competing source to an unchanged selection key creates a
new membership revision and invalidates affected family/query descendants.
Changed interpretation review, assumptions, template applicability, opening state
or treatment rules similarly changes the relevant semantic manifest. An old
result remains readable under its frozen view with a historical label. It must
not be relabelled current. Reuse requires a complete dependency comparison or an
explicitly supported independence argument; missing dependency information
means reuse is unestablished. An unrelated cash-only family can be reusable
while a revenue family is invalidated, subject to the same time/cutoff checks.

| Outcome | Required payload and consequence |
| --- | --- |
| `REQUEST_INVALID` / `CONTEXT_INCOMPLETE` | Missing fields, duplicate IDs or ambiguous composition with record locations; no admitted family is fabricated. |
| `CONSTRAINT_VIOLATION` | Candidate, failed original constraint and arithmetic/logic; candidate rejection is not family emptiness. |
| `PROVED_INFEASIBLE` | Complete target/formula, region, supported exhaustive scope and checked contradiction/proof; no conclusions about out-of-scope real histories. |
| `UNKNOWN` | Undecided formula and reason, even if no witness was returned. |
| `OPERATION_UNSUPPORTED` / `TREATMENT_UNSUPPORTED` | Exact operation or missing authority, affected target and retained formula/proposal; unsupported does not mean false. |
| `BUDGET_EXHAUSTED` / `CANCELLED` | Committed region results, all unresolved cells/regions and continuation receipt; partial valid witnesses survive. |
| `STALE_CONTINUATION` / `STALE_VIEW` | Expected and supplied immutable versions; require a new request or explicit frozen access, with no mutation of historical records. |
| `RESOLUTION_REVALIDATION_REQUIRED` | Changed query/rule/dependency fields and retained constituents; no use of an inapplicable certificate. |

These names specify distinctions for this contract. The later failure contract
must reconcile a common encoding with evidence/time/E05; this is not a claim
that a production exception hierarchy exists. A per-region outcome and a
request termination reason may coexist. For example, one feasible cell and
cancellation leave a partial family, not a cancelled mathematical truth.

| Neighbor | History-family input or output | Responsibility remaining outside this contract |
| --- | --- | --- |
| Evidence/time | Consume `SelectedEvidenceView`, contextual predicates, conflicts, membership revisions and unresolved eligibility; return dependency/obligation IDs | Complete source support and exact temporal admission belong to evidence v3/time v2. History construction cannot relax them. |
| Uncertainty | Consume category-labelled admission/selected assumptions; return joint family, conditional branch IDs and unresolved regions | Specify narrowing, elections, estimates, revisions and defensible joint measures. No equal weights or normalization over successful cells by default. |
| Accounting | Consume dated rule applicability, treatment constraints and opening/event bridges; return economic/history candidates plus unsupported obligations | Establish authority, recognition, measurement, journals and statements. Reported-value or economic feasibility cannot imply compliant accounting. |
| Language/IR | Supply shared identities, complete contexts, typed predicates, region/proof/status and source-location requirements | Define portable encoding, parser/typed authoring semantics, numerical capability and migration; symbolic prose is not an implemented IR. |
| Persistence | Supply immutable manifests, witness/region IDs, continuation receipts and dependency edges including membership | Define atomic commits, stale-write handling and reverse invalidation. Failed persistence cannot silently mark an unfinished cell complete. |
| Interfaces | Supply query layer, view composition, assumptions, scope/exclusions, coverage and unresolved outputs | Display those distinctions and allow conditional/frozen queries; avoid a single “complete” badge. |
| Failure semantics | Supply the outcome distinctions above with causal IDs and partial results | Harmonize names, retryability and recovery behavior without conflating mathematical and operational failures. |

## H6. Matched alternatives and proposed choices

Hold the same synthetic inputs x>=0, y>=0, x+y=100 and the same requested
outputs fixed: the joint feasible set, membership of (50,50) and (100,100),
and the A/B views from H2. A joint symbolic representation retains the line
segment, includes (50,50), rejects (100,100), and expresses overlap directly.
It is proposed because it preserves these meanings. Merely writing a formula
does not prove that construction captured all disclosures or that a backend can
solve it. An unsupported query still has to return its original region.

Explicit finite history enumeration is exact for an explicitly finite universe.
For example, if a separately justified scope limits x to {40,70}, enumerating
(40,60) and (70,30) represents that narrower family exactly. Under the original
continuous inputs, listing endpoints (0,100) and (100,0) alone misses (50,50).
An honest enumerator must report those as witnesses and leave the remainder
unresolved; it cannot change the input domain merely to report completeness.
Finite enumeration remains a suitable implementation candidate for genuinely
finite subproblems, with the same joint constraints and source obligations.

Independent account intervals [0,100] and [0,100] answer marginal questions, but
their Cartesian product admits (100,100). Using that product as the joint family
is wrong relative to the specified target. Retaining the linking equation with
the intervals repairs it, making them a presentation of the joint constraint
rather than an independent reconstruction. The proposed representation may
therefore expose intervals as summaries with their parent relation preserved.
No speed, usability or stochastic ranking is inferred from these examples.

| Choice and status | Provenance and justification | Failure mode and smallest diagnostic |
| --- | --- | --- |
| Joint constraints, proposed semantic requirement | MC08 and P15 audit; H2 proves the dependence counterexample | Independent marginal combination; HF01/HF02 reject it. |
| Region plus search evidence, proposed interface | MC09; historical P04 illustrates but does not authorize the design | Witness promoted to completeness; HF04/HF06/HF07 distinguish them. |
| Explicit scope/obligation report, proposed interface | G1/P15; supplied templates cannot discover omitted events | Complete cell count hides exclusions; HF05/HF09 preserve them. |
| Stable manifest and cell keys, proposed engineering choice | MC25 reproducibility; semantic keys survive traversal changes | Order-dependent replay; HF07/HF15 reject mismatched continuation. Byte encoding remains IR work. |
| Exact rational small examples, fixture convenience | Deliberately stipulated numbers make algebra independently checkable | Mistaken universal decimal/solver policy; HF04 preserves strict endpoints, accounting/numerics remain open. |
| Finite example decisions and cell budgets, fixture convenience | Two branches expose interruption with a tiny example | Whole-company or continuous completeness inferred from counts; H3 requires preserved regions and scope. |
| Query-dependent grouping, proposed interface | MC11/G16; H4 derives a narrow positive case and counterexamples | Same postings mistaken for same exposure; HF10–HF12 require detail/revalidation. |

Z3, Python, rational arithmetic, Boolean truth-cell expansion, slot limits,
traversal order, storage and compression are not chosen as whole-product defaults.
Historical `reconstruction-profile-v1.md` and `reconstruction_v1.py` (construction
and grouping functions) are bounded prototype evidence. P03's authored debt
lowering likewise does not establish disclosure-to-template discovery. The
current contract's arguments are the explicit set and arithmetic derivations
above; no uninspected paper or accounting authority is invoked.

## H7. Completion and remaining decisions

The companion fixtures cover joint dependence, contexts, source conflict,
continuous regions, scope, honest failure/search, economic memory, grouping,
revision invalidation and frozen access. Their algebra and file consistency can
be checked without building a product module. They do not establish semantic
completeness of this specification; that requires independent result review.

P15-E09 (partial outcomes), E11 (numerical capabilities), E12 (economic memory),
E13 (scenarios/weights), and E05 (layered review) now have concrete proposed
history-family consequences. They remain open pending counterpart contracts and
review. All fourteen P15 decisions and all MC01–MC35/G1–G18 obligations remain
active. In particular, sufficient state for every sector, source-grounded
candidate generation, dated accounting permissions, general grouping proofs,
and probability/calibration methods belong to further P16/P17 work. This slice
does not select the initial product profile or dependency order.

The stop condition is saved H1–H7, specified fixtures, architecture registration,
actual local/registered-check records, and explicit residuals. The next task is
a separately reviewed uncertainty contract. Pending E05/history-family bounded
result review and expected whole-architecture check failure do not prevent that
planning or authorised independent drafting. Full independent P16 result review
remains required before phase acceptance.
