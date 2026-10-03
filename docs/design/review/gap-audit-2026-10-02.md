# Product-design gap audit

Date: 2 October 2026 (Asia/Hong_Kong).
Status: completed documentary review; manuscript unchanged. Human comprehension
and independent accounting review remain pending.

## Question, baseline and skeptical audit

Assess whether the current design is sufficient to govern implementation of
the user's intended company-history representation and conditional simulation
system. Readers are accounting modellers and language/software implementers.
They should be able to reconstruct the proposed methods and implement compatible
behaviour without inventing substantive accounting or uncertainty semantics.

The protected baseline is the current manuscript and PDF whose hashes are in
`session-recovery-2026-10-02/original-verification.json`. Recovery checked those
hashes against the current files. This review does not edit the manuscript.
The PDF SHA-256 is
`0b83e17e8f7906c8ea341cb6c1ef2b3082069ca59577eb0ae7d22b50c54163f0`.

Skeptical audit: assess the declared first release and later modules separately;
do not classify lack of production code as a defect in a design document, or
mistake mentions and intended tests for complete specifications and executed
evidence. Page count, successful compilation and illustrative arithmetic are
not acceptance criteria for design completeness. Compare the DSL with the
document's own typed-library baseline. Check all chapters and companion records
before asserting an omission. Imported source claims are reviewed only as far
as the inspected local evidence supports; this is not a new exhaustive
literature review. Stop after evidence-backed findings and a prioritised repair
sequence are recorded. No experiments, benchmarks or external model workers
are needed.

## Findings

The document is an architecture and requirements draft with useful local
mathematical definitions. It does not yet specify enough common behaviour to
govern compatible independent implementations of the requested whole-company
system. The missing author-review file is an administrative symptom, not the
main substantive gap.

The fixed/floating illustration, the signed-balance conservation derivation,
and the distinction between feasible families and probability mixtures are
internally consistent under their stated assumptions. This review does not
certify every imported literature claim or a standards implementation. Its
main findings concern missing methods, contracts and evidence.

### G1. Reconstruction defines the answer more precisely than the algorithm

Evidence: [historical compatibility](/home/chakwong/python/AccDSL/docs/design/chapters/05-mathematics.tex:12)
and [reconstruction procedure](/home/chakwong/python/AccDSL/docs/design/chapters/07-execution.tex:28).

The feasible-history set is defined relative to model scope M. The procedure
says to build variables, add supported bridges and contract constraints, solve,
and retain alternatives. It leaves the critical translation from actual
disclosures to that model largely unspecified: which event and contract
templates are available, how their instances are proposed, how account/note
mappings become joint constraints, how structural alternatives are generated,
and what coverage can be asserted after bounded search. Limits on event types,
time resolution and latent contracts are acknowledged but not instantiated in
a reference scope.

Consequence: two implementations can both satisfy the prose while constructing
materially different feasible families. An omitted floating-rate structure can
remove a rate-sensitive future without violating any balance identity.

Required repair: specify one bounded reference model, its template registry,
candidate-generation procedure, constraint lowering, scope exclusions,
sufficient-state checks and partial-search semantics. Include exact examples
of an admissible history retained, an incompatible history rejected, and an
economically relevant possibility outside the declared scope. A solver witness
must remain distinct from a coverage claim.

### G2. The normative language and IR contracts remain incomplete

Evidence: [language scope](/home/chakwong/python/AccDSL/docs/design/chapters/06-language.tex:6),
[core records](/home/chakwong/python/AccDSL/docs/design/chapters/11-contracts.tex:84),
and [plugin interfaces](/home/chakwong/python/AccDSL/docs/design/chapters/09-implementation.tex:117).

The grammar covers declaration forms and Appendix A supplies selected record
sketches. There is no complete serialised expression/domain model, model-scope
record, contract/economic-state schema, narrative-assertion schema, probability
model, run configuration or payload definition for every result variant.
Methods such as schedule, transition and measure are named without complete
argument/result types. The representation names semantic hashes, capabilities
and extension points without specifying canonical encoding, their full
validation rules or required built-in function semantics.

The running program relies on DemoDebt, DebtMix, an external evidence registry,
an opening state and reporting templates that are not fully defined in the
document. It therefore cannot itself serve as a complete language conformance
fixture.

Required repair: publish the complete Core 0 schema and reference package,
precise typing/context rules and function contracts, serialisation rules and
matched source-to-IR-to-result fixtures. Implementers need reproducible outcomes
for valid and invalid programs, not just agreement on names of operations.

### G3. Ordinary disclosure uncertainty can leave the promised solver fragment

Evidence: [linear core scope](/home/chakwong/python/AccDSL/docs/design/chapters/05-mathematics.tex:247),
[debt decomposition](/home/chakwong/python/AccDSL/docs/design/chapters/06-language.tex:104),
and [rounded observations](/home/chakwong/python/AccDSL/docs/design/chapters/06-language.tex:131).

The example deliberately makes debt exactly 100. In a real rounded disclosure,
let D denote the shared unknown debt amount and alpha the unknown fixed
fraction. Its expression for fixed principal becomes alpha times D. This is
bilinear because both factors are unknown, although the supported core is
linear. Posting quantisation, symbolic applicability and simultaneous funding
relations introduce further boundaries between symbolic representation and
certified computation. Unsupported-operation diagnostics are specified, but a
complete lowering or approximation policy is not.

Required repair: enumerate supported formula classes and solver operations,
including rounding, strict bounds and attainment. Where valid, use a linear
parameterisation: fixed amount F and floating amount V, with F+V=D and F,V
nonnegative; then future interest at known rates is linear in F and V. Specify
when that rewrite is equivalent to the intended model and when additional
fraction restrictions prevent it. Unsupported cases must retain the model and
return a clearly limited answer, with declared computational budgets.

This finding does not invalidate the exact-100 illustration. It identifies
a missing route from that illustration to ordinary reported amounts.

### G4. The first corporate accounting package is an inventory of duties

Evidence: [initial corporate scope](/home/chakwong/python/AccDSL/docs/design/chapters/08-modules.tex:41)
and [report production](/home/chakwong/python/AccDSL/docs/design/chapters/07-execution.tex:209).

Sales, inventory, payroll, fixed assets and working capital are named, but
recognition, measurement and transition rules are not supplied as a coherent
reference package. There is no complete company example joining accruals,
settlements, cost of sales, depreciation, closing, cash-flow classification
and changes in equity. Consolidation, foreign-currency translation and
restatement have sound stated requirements but lack equivalent numerical
specifications. The tests for these operations mostly describe desired
properties without complete inputs and expected outputs.

Required repair: provide one deliberately bounded corporate profile with an
opening state, event schedules, journal templates and all statement mappings.
Carry it across annual and interim periods, including a correction and one
perimeter or currency case. Every supported operation needs its assumptions,
preconditions, state changes and expected reports; explicit exclusions are
acceptable. A balanced financing illustration does not specify this package.

### G5. No complete filing-to-forecast reference case tests the central workflow

Evidence: [proposed demonstrator](/home/chakwong/python/AccDSL/docs/design/chapters/01-purpose.tex:128),
[ingestion](/home/chakwong/python/AccDSL/docs/design/chapters/07-execution.tex:6),
and [example request](/home/chakwong/python/AccDSL/docs/design/chapters/11-contracts.tex:234).

The document proposes a real company and a synthetic company but does not
instantiate either as a full disclosure package. There is no named filing
set with source passages, extracted records, alternative readings, resolved
cross-references, history constraints and resulting conditional statements.
The mathematical example starts after the consequential interpretation work
has already been supplied by hand.

Required repair: add a complete synthetic fixture whose hidden history is known
and a bounded, named real annual/interim disclosure case. Show representative
notes including narrative qualifications, missing terms, a contradiction and
a revised comparative. A worked specification can be written before the
engine exists; the gap is not simply the absence of production code.

### G6. Forward economic and probability models remain interfaces

Evidence: [forward equations](/home/chakwong/python/AccDSL/docs/design/chapters/05-mathematics.tex:119),
[probability mixture](/home/chakwong/python/AccDSL/docs/design/chapters/05-mathematics.tex:170),
and [funding dependencies](/home/chakwong/python/AccDSL/docs/design/chapters/07-execution.tex:122).

The policy, event generator and measurement functions have the right
responsibilities, but there is no reference operating model specifying how
macroeconomic paths change sales, costs, collections, inventories, investment
and financing. Likewise, the optional probability mathematics is more complete
than its implementation design: no full joint likelihood/weight model,
conditioning protocol or accepted treatment of partially executable weighted
families is provided.

The document already requires joint dependence, preservation of individual
branches and explicit unknown outputs. Those intentions need concrete result
and query semantics: preserve joint statement paths; distinguish attainable
joint outputs from separate per-cell bounds; handle overlapping named
conditions without counting their weights twice; and keep unresolved branches
visible without silently renormalising the successful ones. Defaults as
economic outcomes must remain distinct from computation failures.

Required repair: specify one transparent scenario/operating baseline and its
information timing. For the optional probabilistic stage, supply a worked
joint model and an evidence-update example. Target-specific calibration is a
later empirical task, not a prerequisite for documenting those methods. P0
need not wait for a full Bayesian engine.

### G7. Standards, banks and insurance are largely deferred requirements

Evidence: [standards sources and limits](/home/chakwong/python/AccDSL/docs/design/chapters/08-modules.tex:14),
[banking](/home/chakwong/python/AccDSL/docs/design/chapters/08-modules.tex:128),
and [insurance](/home/chakwong/python/AccDSL/docs/design/chapters/08-modules.tex:170).

The design explicitly relies on IFRS overview material rather than
paragraph-level rule implementations. US GAAP and ASBE acquisition/review are
future tasks. There is no matched economic-event example showing actual
differences between the three reporting bases. Banking has an illustrative
one-horizon credit-loss calculation, but no specified allowance lifecycle or
prudential-capital computation. Insurance names groups, cash flows, risk
adjustments, service and finance effects without a complete cohort state and
roll-forward. Hybrid instruments are described but not worked through competing
supported treatments.

Deferring execution is reasonable. It means the document currently governs
requirements for those modules, not their implementation. Their claimed
influence on the core representation also needs structural fixtures now, so
the types are tested before the later engines are built.

Required repair: define operation-level scope and primary authority for the
first supported treatments. Add matched cross-standard examples and bank,
insurance and hybrid-instrument record/transition examples. Expand actuarial,
regulatory and accounting literature alongside each method specification.

### G8. Literature breadth exceeds the depth of the follow-up screening

Evidence: [stated research scope](/home/chakwong/python/AccDSL/docs/design/chapters/12-research.tex:76),
[forward ledger](/home/chakwong/python/AccDSL/docs/design/research/forward-snowball.json),
and [ledger generator](/home/chakwong/python/AccDSL/scripts/build_design_research.py:182).

The 31 archived PDFs provide a broad starting point and important access gaps
are honestly recorded. Nevertheless, 62 forward-search records contain 164
candidate records, of which 159 have the same generic disposition: outside
the core or a specialised extension, screened as metadata. The generator
assigns that disposition by default and uses a few title-string exceptions.
These records do not establish 159 individually justified relevance decisions.
For example, a provenance-in-databases survey receives the blanket disposition
although provenance is part of the proposed core. This does not establish that
the paper must be adopted; it does require a substantive exclusion rationale.

The four inaccessible sources are only one part of the gap. Accounting
measurement, actuarial methods and some direct reconstruction/uncertainty
approaches are expressly deferred. The current records therefore do not
establish a sufficiently deep survey for the entire requested implementation
scope. They do not invalidate the individually supported claims already made.

Required repair: record actual screening decisions for relevant candidates;
use an unreviewed status until a decision exists. Inspect direct competitors,
extensions, corrections and negative findings, expanding each implementation
method's supporting literature. Do not treat the mere existence of six JSON
ledgers as evidence that the literature policy has been satisfied.

### G9. Tool selection is a shortlist, without demonstrated adapter contracts

Evidence: [software survey limits](/home/chakwong/python/AccDSL/docs/design/chapters/04-architecture.tex:83)
and [software ledger](/home/chakwong/python/AccDSL/docs/design/research/tools.json).

Official descriptions, licences and selected interfaces were inspected, but
no integrations were executed and the snapshots do not select pinned working
combinations. There is no complete adapter example preserving a real Arelle
fact's context, moving an ACTUS event into the proposed contract state, or
carrying a valuation's units and numerical status into a journal rule. The
DSL-versus-typed-Python comparison is a proposed evaluation, not evidence that
the textual frontend adds value.

Required repair: specify the adapter inputs, outputs, errors and supported
subsets; demonstrate the smallest important exchanges with recorded versions.
An integration spike is an implementation-time check. The design can already
define the expected exchange and fallback without asserting performance or
superiority. Broad benchmarking is unnecessary at this stage.

### G10. Acceptance and completion are not yet determinate

Evidence: [conformance cases](/home/chakwong/python/AccDSL/docs/design/chapters/10-validation.tex:19),
[unselected release criteria](/home/chakwong/python/AccDSL/docs/design/chapters/10-validation.tex:100),
and [current checks](/home/chakwong/python/AccDSL/scripts/check_design_examples.py:1).

T01–T18 are useful requirements, but most are not fully specified fixtures.
The real-company corpus, annotation/adjudication protocol and release-specific
acceptance criteria remain to be selected. Search budgets are mentioned but
there is no reference workload or resource envelope against which to decide
that an implementation is usable. Human review is described as an interface,
without a complete record lifecycle and resolution example.

The 12 executed checks use hand-written arithmetic and do not parse or execute
the DSL. This is correctly disclosed; those checks must not substitute for
conformance. The author-review record remains missing, and the current
document verifier does not test for its existence.

Required repair: turn the central cases into canonical inputs and expected
outputs; define the initial corpus and review decisions; select justified
release criteria and workload budgets before evaluation. Universal arbitrary
accuracy cutoffs are not needed. Maintain an open-decisions register identifying
what must be settled before each stage can be accepted.

## Prioritised repair sequence

| Order | Deliverable | Reason |
| --- | --- | --- |
| 1 | One complete synthetic company and a bounded real filing case | Exposes missing contexts, accounting state and interpretations through concrete requirements |
| 2 | Reference historical scope, reconstruction procedure, core accounting/reporting package | Turns the desired result family into a method with explicit limits |
| 3 | Complete IR/schema, built-ins, temporal semantics and source/API/result fixtures | Allows compatible implementations and local conformance tests |
| 4 | Solver-fragment rules, failure/incompleteness semantics and resource budgets | Prevents routine uncertainty from silently exceeding the promised method |
| 5 | Structural bank/insurer/hybrid examples and selected cross-standard rules | Tests core extensibility before broad module development |
| 6 | Targeted literature repair and narrow adapter checks supporting those choices | Replaces generic coverage and reuse claims with decision-specific evidence |
| 7 | Release-specific corpus/criteria, author review and later independent review | Separates a completed draft, a usable implementation and scientifically valid forecasts |

P0 prototyping can proceed after its concrete types and fixtures are settled.
The optional probabilistic stage and full bank/insurance engines need not block
that foundation. The document should distinguish fixed architectural
requirements, fully specified current behaviour and future method obligations.

## Review evidence and limits

Read all twelve chapter/appendix sources, the root and contents, relevant
research records, ledger-generation logic, document checks and the current
checkpoint. Inspected rendered PDF pages 27 and 50 to confirm the presentation
of the DSL example and normative grammar. This was a focused rendered check,
not a new complete page-by-page or human readability review. The main argument
is understandable; the findings above primarily concern the work hidden behind
terms such as package, solver and plugin, rather than a need to shorten prose.

Rechecked the protected file hashes; the manuscript and recorded deliverables
were unchanged. No new source downloads, engine runs, model comparisons or
benchmarks were conducted. This audit supplies documentary evidence for the
specific gaps; it does not establish that the architecture is unworkable or
that any proposed library is unsuitable.

The strongest alternative interpretation is that this was intended only as an
architecture document with later specifications. Under that narrower purpose,
many deferrals are acceptable. Under the user's explicit request for a governing
implementation document covering the wider accounting problem, they remain
unfinished requirements. Completion of the reference cases and contracts above
would change that assessment; another successful PDF build would not.
