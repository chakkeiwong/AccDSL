# Proposed filing-adapter evaluation

The target is faithful, located, contextual proposed readings from the retained
disclosure package, including visible unresolved content. A correct number
attached to the wrong entity or period fails that target. The proposed evaluation
therefore measures transcription, context, table structure, mapping, source
support and coverage separately; a single parsing score cannot select the adapter.
Requirements: MC01-MC07, MC25, MC27, MC31 and MC33.

No run is authorized by the existence of this protocol alone. This packet
performs source inspection and deterministic specification checks; runtime
dependency/model selection and P16 integration must precede the evaluation.

## Population, labels and exposure

Use the existing 192 accepted reports across nine issuers and 2018-2025; preserve
their original hashes and report IDs. Root packet 4 prepares Apple FY2025 Q1
inline HTML, HSBC FY2024 annual PDF, Munich Re FY2024 annual PDF and Midea FY2024
annual Chinese PDF. These four are a purposive, exposed development pilot, not
a representative sample or heldout test. Read the final packet-4 selection,
occurrence index and ambiguity log before sampling additional units.

Retain existing annotation-record.schema.json as the base exchange where it
fits. A separate occurrence sidecar links label/version to source_version_id,
full SHA256, original locator and field-level supporting occurrences. HTML
uses original ID/DOM locator and verified byte span where possible. PDF uses
physical page, printed page separately, page dimensions and bbox coordinate
frame. A table cell label includes cell/row/column/header/footnote support; a
narrative label retains modality, scope and exceptions. Record exact literal
and separate normalized value, every context field's known/unknown/conflicting
state, intended mapping relation and review status. Character offsets in
derived text are not source byte offsets.

Labels must not be copied from the evaluated extractor and called ground truth.
The first annotator locates each source unit and its contextual support; a
second reader independently reads the source without seeing the candidate's
answer; adjudication records both readings, the evidence and unresolved items.
Where only one reader is available, keep provisional status and report agreement
as unmeasured. LLM reviewer agreement does not establish human acceptance.
Economic truth and accounting compliance are outside the label's extraction
judgment.

Partition at issuer/history-family level when enough data permit; keep repeated
filings, amendments, restatements and overlapping source histories together.
If a research question instead studies within-issuer later-year transfer,
predeclare that design, make temporal cutoffs explicit and do not call it
issuer-heldout generalization. Record every report/page exposed during design,
annotation, prompting, tuning and source inspection. Training-corpus exposure
of pretrained models may remain unknown; it must be reported. The accepted
corpus was already used in project development, so clean heldout status cannot
be asserted retrospectively.

## Comparison ladder

1. Located manual labels and original-source inventory establish the bounded
   comparison target. For digital PDF, native text extraction and explicit
   geometry provide the naive baseline. For XML/inline, a transparent tag/context
   inventory on the same annotated fragments provides the naive baseline.
2. Tune the rule-based digital-PDF baseline (pdfplumber) on development units with
   a declared small configuration budget covering line/text strategies, cell
   tolerances and page cropping. Tune no setting on heldout labels. Retain all
   tried configurations, failed regions and tuning time. For structured facts,
   use the complete pinned Arelle path and explicit taxonomy package as the
   classical candidate; a tag-only inventory is not an equal full validator.
3. Run a plain Docling PDF/layout candidate with explicit backend/model hashes,
   OCR language/rotation and table settings. Compare digital and scanned strata
   separately. The Docling XBRL graph path is a loss-detection case, not a
   competing independent parser or the accepted finance representation.
4. Test proposed context/header/footnote repair logic on the same inputs and
   label units. Count correction and review cost. Enhancement must preserve
   originals and may not use heldout labels or later historical information.

All candidates receive identical documents, roots, region definitions and
disclosure scope, plus the same allowed taxonomy/context sources. Report native
capability failures as such. Do not penalize an XBRL processor for failing to OCR
a scan or credit a PDF parser for taxonomies that another candidate alone was
given. Candidate settings, model revision, language packs, hardware and resource
limits are hypotheses with provenance, not promoted defaults.

## Metrics, denominators and roles

| Diagnostic | Exact population and measurement | Role before interpretation |
| --- | --- | --- |
| Literal transcription | Matched labeled source occurrences; exact source string plus separately predeclared Unicode/whitespace-normalized comparison. Numeric tuple includes sign, digits, separator, decimal, scale and nil/blank status. Report missing and extra occurrences separately. | Primary component criterion; formatting normalization cannot excuse changed financial value. |
| Context | Per-field correctness among annotated supported fields, unresolved/unknown-state fidelity among unknown fields, and joint all-required-field exactness for eligible readings. Fields include entity, perimeter, concept, dimensions, dates/calendar, currency/unit/scale/sign, basis and precision support. | Joint faithful-reading criterion; wrong entity/date/unit is a veto for affected reading. |
| Tables | Labeled cells with row/column spans, cell text, header associations, footnote links, continuation links and bbox/page. Record merged-cell and empty-cell cases separately. Table similarity/GriTS may be added with its inspected definition and version. | Component explanatory metric and error localization; table score alone cannot promote finance extraction. |
| Mapping | Each annotated concept mapping request, including equivalent/component/broader/reclassified/transformed/unresolved alternatives; compare relation, target version and applicable conditions. Report unresolved labels separately. | Primary mapping criterion only for the mapping component; never waived by label similarity. |
| Locator validity | Every proposed occurrence; exact source hash and page/element/span resolve. For PDF, verify frame and crop then inspect actual region. Bbox overlap is diagnostic, not support truth. | Integrity veto when original source cannot be located; separate from semantic support. |
| Faithful support and false admission | Every proposed/accepted candidate in labeled units; independent source review determines whether source and context support the reading. Count contradicted, unsupported, unresolved and accepted cases separately. | Any detected false acceptance blocks that acceptance and repairs the admission path; no tolerated fabrication rate grants individual acceptance. |
| Retention and unknowns | Known acquired nonoverlapping leaf units with one disposition each; assertions reviewed among explicitly enumerated assertions; requested query dependencies with supported/resolved/unknown status. | Preservation/coverage criterion. Unknown total extent or unexpanded frontier prevents package-closure claim regardless of ratio. |
| Historical admissibility | Eligible queries with cutoffs, exact bytes and publication/ingestion/review evidence; include unknown publication, date-only boundary, unverified vintage and later revision cases. | Admission veto for affected historical query; archival extraction may continue. |
| Review effort, latency and resources | Matched complete jobs; include all failures/timeouts and attempted pages, cold model setup separately from warm conversion, CPU/GPU, memory, wall time and analyst actions. | Explanatory/resource-budget diagnostic. Never rank speed after different omissions or invalid output. |

Do not count a parent table and its child cells as disjoint coverage units in
the same denominator. Keep raw discovered counts, scope exclusions and unresolved
frontier. Do not substitute the number of successfully converted pages for the
number of retained/understood assertions. Derived grid blanks are not evidence
of source blanks, and unknown assertions are not zero assertions.

## Pass, veto and continuation decisions

Engineering conformance requires the agreed deterministic contract cases to
pass: source/occurrence preservation, scale/sign, complete units/dimensions,
date boundaries, nil/blank distinction, scoped partial failure and immutable
review/correction. Hash failure, missing required source links, or silent
acceptance of a known mismatch blocks the affected output. A structurally valid
library object alone does not satisfy this criterion.

For a larger comparison, predeclare the primary empirical quantity as the
proportion of annotated occurrences with both faithful reading and all required
supported context correct, alongside proposal/abstention coverage and all
preservation/admission veto counts. Do not choose a numerical promotion target
until the initial profile and consequences of specific errors are agreed from
the pilot. Until then the run is diagnostic, with no product/default promotion.
Any selected target must name the population, false-admission treatment,
uncertainty level and review policy before evaluating heldout results.

Paired results on the same documents should include uncertainty at the sampled
document/issuer cluster level, not pretend each cell is an independent sample.
With only four purposively chosen reports, display casewise descriptive results
and uncertainty about generalization; do not bootstrap thousands of correlated
cells into a population ranking. A later sufficiently broad predeclared sample
may support paired cluster intervals or another justified analysis. Runtime tails
need enough independent jobs and repeated timing conditions; small maxima and
q95 differences are descriptive only.

Rejecting one candidate triggers the next relevant repair or adapter alternative.
It does not end the investigation. Stop a run for changed source bytes, invalid
labels, untracked dependency/model changes, wrong input partition, accidental
network/model acquisition, corrupted output or exhaustion of its declared
resource budget. Missing publication evidence blocks investor-information
queries, not archival pilot labels. Missing human adjudication blocks final
acceptance, not continued provisional annotation.

## Execution and preserved results

Before a runtime pilot, write the exact command and environment lock under
docs/plans when imported, with source/label/split manifest hashes, inspected
licenses, adapter commit, dependency and model weight hashes, taxonomy packages,
CPU/GPU mode, seeds if applicable, wall/time/resource budget and output directory.
Do not install or choose these silently from upstream defaults. Use retained
local inputs and explicitly allowed offline resources; preserve standard output,
errors, failed-unit inventories and every configuration tried. Keep conversion
save time distinct from evidenced source ingestion/publication.

The run report must separate engineering conformance, empirical extraction
quality and historical/accounting interpretation. Its decision table records
primary criterion, veto status, uncertainty, next action and unsupported
conclusions. Its inference table records hard failures, viable candidates,
whether a ranking is statistically supported, descriptive-only differences,
default readiness and next evidence. This packet supplies no measured ranking,
latency estimate, threshold, pretrained model default or production acceptance.
