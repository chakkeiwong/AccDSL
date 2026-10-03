# Review against the AccDSL mission

Date: 2 October 2026 (Asia/Hong_Kong).
Basis: [mission control](../../../MISSION_CONTROL.md) and
[MC01–MC34 requirements](../../plans/accounting-mission-requirements.md).
Protected manuscript: the unchanged 60-page PDF and LaTeX assessed in the
[initial gap audit](gap-audit-2026-10-02.md).

## Answer and review scope

The earlier list is not an exhaustive gap inventory. G1–G10 identify major
method, language, accounting, case-study, literature, software and acceptance
gaps. Comparing the whole document with the original goals also exposes the
cross-cutting obligations below. Some are detailed refinements of those broad
findings; others become visible when two requirements have to work together.
They are not counted as independent evidence of poor quality.

The current requirement register maps every listed MC requirement to inspected
document content and remaining work. That is a coverage record for this review,
not proof that all future specification defects have been found. Real filing
cases, primary accounting sources, implementation and domain review can reveal
further gaps. A chapter mentioning a topic is not sufficient to close it.

## Goals and current coverage

| Goal | What the current document supplies | What remains |
| --- | --- | --- |
| M1 Historical record | Source/context fields, time distinctions and narrative examples | Complete disclosure-coverage procedure, concept/mapping semantics, exact temporal queries and review transitions |
| M2 Alternatives | Feasible-set definitions, shared symbols and mixture mathematics | Construction procedure, uncertainty-kind propagation, coverage and practical resolution policy |
| M3 Simulation | Event/accounting abstraction and financing arithmetic | Full economic/accounting reference package, scenario modes, joint output and incomplete-execution semantics |
| M4 Heterogeneity | Standards/sector requirements and module boundaries | Supported treatments, primary rules, cross-standard examples, bank/insurance structural and method cases |
| M5 Implementability | Grammar, selected records and named interfaces | Complete schema, built-ins, contracts, numeric fragments, identities and conformance fixtures |
| M6 Research and reuse | Archived sources, broad survey and inspected software shortlist | Source-specific screening, missing technical coverage and concrete selected adapter evidence |
| M7 Governing document | Coherent architecture exposition and a compiled manuscript | Full-case teaching and sufficient method detail to govern implementation |
| M8 Evidence and continuity | Proposed tests, limited arithmetic/build checks and implementation stages | Instantiated acceptance evidence, clear completion status and maintained mission traceability; the mission records are installed now |

## Additional explicit findings

### G11. Whole-report coverage and narrative formalisation need a procedure

Requirements: MC01, MC03. Refines G2 and G5.
Evidence: [source coverage](/home/chakwong/python/AccDSL/docs/design/chapters/02-history.tex:6)
and [narrative assertions](/home/chakwong/python/AccDSL/docs/design/chapters/02-history.tex:44).

The draft requires dispositions for source spans and separates document,
semantic and simulation coverage. It does not specify how to establish the
complete disclosure inventory, resolve incorporated cross-references, carry
qualifications from narrative into the affected figures, or verify that the
coverage process itself has not missed a note or table. Generic actor/predicate
fields are insufficient to determine the executable meaning of exclusions,
scope qualifications, contingent commitments and qualitative quantifiers.

Required evidence: one complete filing manifest, source-span disposition and
cross-reference example; typed narrative records; a mapping from disclosures
to supported constraints or explicit unresolved obligations. Preserve separate
coverage meanings and defined denominators. Do not score parsed pages as
formalised financial meaning, or turn "substantially all" into an invented
numeric threshold.

### G12. Cross-company concepts and aggregation need formal mapping semantics

Requirements: MC02, MC06, MC07, MC20, MC24. Refines G2, G4 and G7.
Evidence: [concept relationships](/home/chakwong/python/AccDSL/docs/design/chapters/02-history.tex:54)
and [contextual aggregation](/home/chakwong/python/AccDSL/docs/design/chapters/06-language.tex:69).

Equivalent, component, broader, reclassified and measurement-transformed
concepts are named, and partitions are required. Their records, applicability
conditions and allowed compositions are not fully defined. There is no worked
case showing company extensions changing over time, gross/net distinctions,
or two classifications of the same revenue that must not be summed together.

Required evidence: a mapping registry and application rules, with cases where
similar labels mean different measurements and different labels mean the same
quantity. Define what proves a partition disjoint/exhaustive, how unallocated
residuals are represented and how perimeter/context changes affect mappings.
The representation need not impose one universal chart of accounts, but it
must specify how comparability is established or left unresolved.

### G13. Multiple clocks are identified without complete historical query rules

Requirements: MC05, MC19, MC25. Refines G2, G4 and G10.
Evidence: [time and views](/home/chakwong/python/AccDSL/docs/design/chapters/02-history.tex:80)
and [EvidenceView](/home/chakwong/python/AccDSL/docs/design/chapters/11-contracts.tex:92).

Storing dates and supersession links does not specify which assertion wins a
query. The design needs precise rules for incomplete publication timestamps,
conflicting available filings, selective restatements, changed accounting
bases and calendars, and different investor-information versus system-version
queries. Prospective estimate changes and retrospective corrections are
delegated to future packages without a complete transition example.

Required evidence: a multi-date example with explicit publication, ingestion,
economic and reporting times, original and revised amounts, and the exact
records/results returned by each supported view. Show invalid year-to-date
subtractions across revisions as well as a valid one. Declare unsupported
timing assumptions rather than silently using the latest available row.

### G14. Scenario modes and permitted information need enforceable contracts

Requirements: MC14, MC18. Refines G6 and crosses modelling/execution requirements.
Evidence: [three scenario meanings](/home/chakwong/python/AccDSL/docs/design/chapters/03-literature.tex:149),
[information timing](/home/chakwong/python/AccDSL/docs/design/chapters/05-mathematics.tex:121),
and [scenario grammar](/home/chakwong/python/AccDSL/docs/design/chapters/11-contracts.tex:51).

The literature chapter promises to distinguish an imposed exogenous path,
an observational conditional forecast and an intervention. The surface example
only sets a driver. The record/API specification does not supply complete
mode-specific semantics for conditioning or replacing equations. Similarly,
behavioural and measurement plugins are told to use permissible information,
but the available-information object and its access rules are unspecified.

Required evidence: declare supported scenario kinds and represent them in the
schema. A first release can explicitly support exogenous stress only without
claiming the other operations. Show how a manager and an allowance calculation
receive current information while future simulated outcomes remain hidden.
Explain when new observed evidence updates historical weights and why merely
selecting a hypothetical stress does not do so.

### G15. Different kinds of uncertainty need different admissibility rules

Requirements: MC04, MC08, MC10, MC12, MC24. Refines G1, G2 and G6.
Evidence: [interpretation distinction](/home/chakwong/python/AccDSL/docs/design/chapters/01-purpose.tex:67)
and [alternative records](/home/chakwong/python/AccDSL/docs/design/chapters/06-language.tex:183).

An unknown fixed-rate share, two readings of a note, a permitted accounting
election, a measurement estimate and a future management decision are different
uncertainties. The text recognises this, but generic symbols/choices and
assumption provenance do not fully specify how each kind is validated,
updated or propagated. An unsupported treatment must not be accepted as an
equally legitimate interpretation merely because it produces balanced entries.

Required evidence: define these distinctions in the model and review contracts,
including links between dependent uncertainties. Show an admissible alternative,
an evidence-refuted alternative and an unsupported accounting treatment.
Preserve a possibly erroneous source assertion as evidence without silently
endorsing its treatment. This requires no new fraud-detection product.

### G16. Aggregation and history compression need a practical resolution policy

Requirements: MC11, MC22. Refines G1 and G6.
Evidence: [conditional-law equivalence](/home/chakwong/python/AccDSL/docs/design/chapters/05-mathematics.tex:222).

The definition that grouped histories must have the same relevant conditional
laws is useful. It does not supply a usable rule for choosing instrument,
lot, vintage or cohort resolution, carrying necessary accounting memory, or
reconsidering a grouping when a scenario/horizon changes. The draft correctly
avoids claiming a general equivalence-deciding compiler, but does not specify
enough supported transformations in its place.

Required evidence: define resolution metadata, state requirements and a small
set of justified transformations. Include one grouping that preserves the
requested results and another that loses a rate, maturity or guarantee
exposure. Declare the scope/error of approximate aggregation and retain its
source/detail references. Changing the query must trigger a sufficiency check.

### G17. Local evidence review needs a state machine and invalidation rules

Requirements: MC04, MC27. Refines G2, G5 and G10.
Evidence: [review actions](/home/chakwong/python/AccDSL/docs/design/chapters/09-implementation.tex:142)
and [correction proposals](/home/chakwong/python/AccDSL/docs/design/chapters/07-execution.tex:13).

The analyst can accept, reject, add an alternative or correct a proposal, but
the permissible transitions, required reasons and effects on existing models
and results are not fully specified. A future implementer must decide how
an accepted reading becomes superseded, how contradictions stay visible and
which derived runs must be recomputed after a review decision changes.

Required evidence: a simple local review-state specification and an example
from raw extraction through reviewed alternatives and revised conclusions.
Separate reviewer approval, extraction confidence and probabilities of
economic histories. Preserve previous results against their original evidence
view. Multi-user approval hierarchies are outside the current need.

### G18. Reproducibility needs identity and replay definitions, not only fields

Requirements: MC25, MC34. Refines G2, G9 and G10.
Evidence: [three identities](/home/chakwong/python/AccDSL/docs/design/chapters/06-language.tex:21),
[event replay](/home/chakwong/python/AccDSL/docs/design/chapters/07-execution.tex:115),
and [manifest](/home/chakwong/python/AccDSL/docs/design/chapters/09-implementation.tex:175).

The draft requires evidence/model/execution identifiers, idempotency and stable
random streams, but does not fully define canonical representation, event
identity, stream allocation or semantics-preserving migrations. Without these,
different implementations can assign different identities or change simulated
draws after a harmless branch reorder while claiming to follow the same design.

Required evidence: explicit canonicalisation and identity rules, version and
migration contracts, and replay examples covering formatting changes, evidence
corrections, reordered independent events, duplicate event IDs and branch order.
Specify which results must be identical and which numerical comparisons have a
justified tolerance. No new cryptographic-attestation system is implied.

## Completion consequences

The full mission requires more than appending these eight subsections. Resolve
the underlying methods and use complete cases to exercise their interactions.
A restored historic report, for example, depends on source coverage, concept
mapping, time selection and review state together; independently naming those
four mechanisms does not establish their combination.

The requirements register now provides the durable baseline for this work.
The root AGENTS.md directs future sessions to it and to the current checkpoint.
The authoring plan and design README now describe the draft as requiring
specification repair. This corrects the workflow without claiming that the
underlying manuscript has been repaired.

It remains reasonable to build a bounded core before full banks, insurance or
probabilistic inference. It is not reasonable to call the broader governing
document complete merely because those difficult methods were moved into
unspecified future packages. Deferrals need explicit structural support,
method obligations and acceptance evidence at the relevant stage.

## Evidence and limits of this pass

Re-read the original three user requests and relevant project policies. Used
the prior complete chapter review and re-inspected the source passages cited
above, the current plan/README/checkpoint, and the exact field/grammar definitions
for the additional findings. No new primary literature survey, production
execution, standards certification or independent human review occurred.

The root mission, requirement register and AGENTS.md are new local control
documents. The manuscript's source and PDF remain unchanged. This is a
requirements-based documentary assessment, with finite inspected scope; it
does not establish that the proposed product is infeasible or that no further
gaps remain.
