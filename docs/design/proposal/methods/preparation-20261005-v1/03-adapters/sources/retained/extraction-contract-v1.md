# Filing extraction and review contract v1

This proposed adapter contract connects acquired filings to the evidence and
time contracts. It adopts the useful eight-stage organization of Claude's
extraction draft and replaces its identity, truncation and admission rules.
It addresses MC01–MC07, MC25, MC27, MC28 and MC33, especially G11–G13/G17–G18.
The examples in extraction-fixtures-v1.json specify behavior; no extraction
engine, model or review UI is implemented here. The governing evidence rules
are evidence-contract-v3.md E1–E4 and time-contract-v2.md T1–T6.

## Request and returned records

`prepare_filing(request, source_snapshot, prior_review_snapshot)` consumes a
declared package, immutable sources and existing decisions. The request gives:

* `package_id`, requested issuer/legal entities, declared filing roots and
  reporting intervals, expected statement/note indexes and scope decisions;
* pinned `source_snapshot`, adapter/version/configuration and any model and
  taxonomy versions; languages and OCR choices are explicit;
* reference-work budget, stable work-order rule and a resume receipt, if any;
* the desired raw, proposed-reading or accepted-reading layer and explicit time
  admission/selection parameters when the operation asks a historical question.

An unavailable acquisition is an inventory record with a reason, not invented
source bytes. Each available `SourceVersion` binds the original bytes/hash,
media type, origin, acquisition receipt and derivative lineage. A model's
configuration, score and prompt never constitute source evidence. Identical
original content can share storage while every occurrence retains its own
document, location and financial context.

`ExtractionPreparation` returns the exact request/input versions, new source
occurrences, proposed readings, concept-mapping candidates, reference edges,
coverage populations, review tasks, typed issues and a resume receipt. Accepted
readings appear only with qualifying review decisions; adapter confidence cannot
advance that layer. Raw content is preserved even if its proposed reading fails.
Preparing a filing neither posts journals nor assigns probabilities to histories.

Every issue contains code, affected IDs/source locators, dependent queries,
attempted operation, retained state and the next possible repair. Results
distinguish `complete_within_declared_scope`, `partial`, `unsupported_adapter`,
`unresolved_context` and `invalid_request`. Completion of extraction means the
requested adapter work is accounted for; it is not package or semantic closure.
Uncertainty about an issue's relevance leaves the affected dependency unresolved.

## The eight stages and their interfaces

| Stage | Input and output | Required behavior |
| --- | --- | --- |
| Acquisition and inventory | Roots, scope and acquisition receipts → immutable sources, declared/discovered units and missing targets | Preserve originals, record access failures and unknown inventory extent; reconcile contents and indexes against actual units. Reuse the acquired 192-report panel. |
| Layout and text | SourceVersion plus adapter/config → located text/image/table candidates | Preserve physical PDF page and coordinate frame, HTML element/byte lineage and transformation records. OCR is a derived reading; retain ambiguity, original image and unparsed areas. |
| Tables | Located candidates → cell/header/span/footnote structures | Preserve merged cells, multi-page continuation and alternatives. Blank cells, indentation or alignment alone do not establish zero, hierarchy or arithmetic. |
| Financial context and mapping | Table/narrative occurrences, versioned taxonomy and context → proposed contextual readings and mapping alternatives | Retain entity/perimeter, basis, dates, units, precision and unknowns. Equivalent/component/broader/reclassified/transformed relationships need distinct conditions. Similar labels cannot convert accounting standards. |
| References | Declared roots, discovered references and budget → edge dispositions and retained frontier | Account for every discovered reference and unresolved target; preserve cycle-closing edges and budget exhaustion. A resource limit never means all content was visited. |
| Observations | Occurrences, proposed readings and mappings → immutable candidate records with validation findings | Validate location and faithful support separately. Keep literal source, extraction, interpretation, derivation and assumption layers distinct. Invalid candidates remain inspectable; they do not become accepted source facts. |
| Review | Candidates and located context → append-only scoped decisions and affected dependencies | Show source alongside the reading and alternatives. Accept, reject, alternative, supersede and defer are separate events; changing a reading creates a new version. Preserve earlier views and invalidate affected current derivations. |
| Reconciliation | Admitted compatible observations and explicit bridges → scoped arithmetic/completeness diagnostics | Check identities only for compatible bases, periods, perimeters, units and disjoint components. Distinguish missing operands, source conflict, rounding ambiguity, model assumptions and arithmetic failure. |

None of the stages may silently discard policies or qualitative notes. A unit
can remain unread, unstructured or unresolved with its location and reason.
Its unknown assertion count is not zero. Materiality guides work priority or a
reviewed scope decision; it cannot erase an acquired unit from the inventory.

## Identity, corrections and duplicate information

The immutable occurrence key is `(source_version, locator, occurrence_id)`.
This is different from a content-body hash or a contextual assertion identity.
Financial context includes legal entity, perimeter/version, concept/mapping
version, dimensions, calendar/version, reporting interval/instant, currency,
unit/scale, sign convention, measurement basis, source vintage and reported
precision/rounding support. The definitive portable encoding remains an IR and
persistence obligation; these components are the semantic requirements.

Context equality is necessary but not sufficient for merging assertions. An
explicit alias/equivalence decision must also establish the same assertion and
compatible source/reading lineage. Source occurrences stay distinct after such
a decision. Overlapping rounding intervals, equal displayed numbers, common
labels or a matching period never independently establish equivalence.
Source restatement and extraction correction remain different change kinds.
A corrected entity, unit or period can create a new reading even when the number
does not change. The new reading names the superseded version, supporting source
and reason; it does not modify original bytes or automatically resolve an issuer
conflict. Duplicate evidence must not later become independent likelihood input.

In fixture X01, a parent-only historical-cost reading and a consolidated
fair-value reading both display 100 for the same concept/year/currency. They
remain two assertions with separate occurrences. X02 links two faithful
occurrences of one supported assertion without creating two independent facts.
X03 corrects the period while retaining the value 100; the original reading
remains retrievable. These outcomes follow from identity, not a numeric tolerance.

## Time and information eligibility

Publication, actual availability, ingestion and review timestamps each retain
precision and evidence. Unknown publication is preserved as unknown. The adapter
does not substitute an acquisition date, period end or today's date. A timestamp
is not required merely to archive a source; the requested historical claim
determines admission under T2.

X04 archives a source with unknown publication and an evidenced ingestion
receipt. Its raw content is available for archival exploration, and a qualifying
system-as-of query can establish possession. It is unresolved for an investor
cutoff without public-availability and byte-vintage support. Later annotations
cannot add later information to a historical scenario's admitted dependencies.
An analyst may inspect later excluded records as audit evidence, but they must
not enter the forecast's information set.

There is no universal rule that publication must follow every date mentioned
in a filing: a disclosure may discuss future maturities or forecasts. Validate
the kind of date and claimed time relationship rather than reject it by position.

## Reference traversal, budget and resume

The request names its roots; do not infer roots from a field absent from the
manifest. The work queue starts with those unexpanded roots. An expansion
requires retained readable source and consumes one unit of the explicitly
supplied `max_expansions` budget. Extract each encountered reference before
scheduling its target. Record source location, target description, candidate
targets and resolution evidence. Preserve unavailable, missing or ambiguous
targets with the existing E2 dispositions.

Expanded identities include source version and unit location. Revisiting an
expanded target closes the traversal cycle or duplicate edge without deleting
that edge. Use `cycle_closed` only when a recorded return path establishes a
cycle; reconvergent references without a cycle use `duplicate_verified` after
target identity is established. Deterministic queue ordering makes resumes reproducible; it never
settles a semantic conflict. On budget exhaustion, retain all scheduled but
unexpanded targets and their incoming edges as the frontier. A known located
target can still have uninspected content: target resolution and expansion status
are separate fields. An edge to that target receives the E2 traversal disposition
`resource_exhausted`, with its located target retained. Do not call it unavailable.

The resume receipt binds sources, adapter/configuration, work order, expanded
identities, original roots, edge dispositions, frontier and used budget. Resume
starts from the saved frontier while retaining the original roots and all prior
edges. The new receipt updates an incoming `resource_exhausted` edge when its
target is expanded; the old receipt remains immutable. Resume may increase
the total budget with an explicit new request. Changed source/configuration
produces a new preparation/version and invalidates dependent cached readings;
it cannot append to a receipt while pretending the inputs are unchanged.

X05 uses R→N→E→X with two permitted expansions. It expands R and N and retains
E as frontier through N→E. E's outgoing references have not been inspected;
the result reports unknown remaining extent and makes no claim that its two
discovered edges are the whole package. X06 resumes with two further expansions
on the same sources and reaches E/X. X07 records the closing edge of R→N→R
and terminates with no frontier. X12 distinguishes two acyclic references to
the same target from a cycle. A missing root is reported as missing inventory,
not as an empty successfully processed package.

## Admission, review and failure

A source locator has at least two separate checks: it resolves to retained
content, and that content supports the proposed reading in its context. X08 has
a valid locator beside a proposal of 120 where the source says 100. It preserves
the proposal and rejects that reading with `SOURCE_READING_MISMATCH`; it does
not admit 120 because the URL or page exists. No tolerated fabrication rate
authorizes an accepted fact. Statistical error estimates describe the extraction
process; they do not waive a detected mismatch.

An accepted reading says what the source asserts; it neither proves economic
truth nor authorizes an accounting rule, narrative constraint or probability.
Interpretation/assumption admission follows E2/E4. Review actions reference their
exact input version and scope; source updates or a changed reading require a
new action. The repeated identical action returns its original receipt; changed
payload under the same identity is a conflict. Exactly-once storage mechanics
and concurrent-writer semantics remain obligations of the persistence contract.

An adapter outage returns preserved sources and a scoped unsupported/failed work
item. A single unreadable page does not erase unrelated successful readings.
An integrity mismatch rejects use of the affected source. A schema/context
failure blocks the affected admission and retains the candidate. Solver
infeasibility triggers investigation of extraction, source conflicts, mappings,
model scope and assumptions. X09 preserves those alternatives; it does not
automatically rewrite source values to make the equations balance.

## Coverage and evaluation

Use E2's separate acquired-unit, reviewed-assertion and query-exposure populations.
For each ratio retain the population definition, counting unit, eligible set,
numerator, denominator and exclusions. When inventory extent is unknown, report
the known population and unresolved frontier alongside it; a percentage of known
units is not a completeness percentage. Parent/child source spans cannot both
inflate a nonoverlapping leaf-span count.

Plan annotation on the existing nine-issuer, eight-year corpus with strata for
accounting basis, sector, language, format, statement/note, revisions and time
availability. Choose representative development cases within that corpus and
record their IDs. A small annotated subset is a pilot, not replacement coverage.
Related issuer histories and repeated filings must remain in compatible data
partitions. Establish the annotator instructions, agreement/adjudication process,
unit of sampling, contamination/exposure audit and evaluation cutoffs before
claiming extraction accuracy or model ranking.

Measure numeric transcription, context, mapping, table structure, location
support, unresolved content and false admissions separately. GriTS/table metrics
and question-answering results may explain components; they do not certify note
coverage or historical eligibility. Confidence calibration, abstention and error
consequences determine candidate thresholds. FinBERT, Docling and Arelle remain
candidate adapters requiring pinned interface/license and target-task checks;
no unmeasured baseline score or detector threshold is adopted here. No statistical
ranking follows from these deterministic examples.

## Alternatives and remaining integration

A one-step “extract and accept” path is convenient but hides provenance and
judgment. Proposed readings plus distinct admission make corrections and
alternatives observable. Aggressive numeric deduplication saves records but loses
context and source-vintage meaning; shared content storage with explicit aliases
preserves both. Exhaustive traversal without a budget risks unbounded work;
budgeted traversal with a retained frontier exposes the cost and incompleteness.

This specification supplies the extraction part of the interfaces/accounting
preparation design. P16 still owes the complete language/interface and persistence
contracts and integrated initial scope. P17 owes adapter inspection and selected
domain interpretation rules. P18 must explain this process in the governing
manuscript, and P19 must check its integration and limitations. No existing
contract's source or human acceptance status is promoted by this addition.
