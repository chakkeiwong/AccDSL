# Repairing the expanded AccDSL design audit

Date: 2 October 2026. Authority: the user's instruction to propose, thoroughly
review and execute the repair plan. Mission: `MISSION_CONTROL.md`; requirements:
MC01–MC34. This plan supersedes the old final-review-only stage. No further
permission is needed for local design, research and conformance work.

## Intended result and reader

Produce a revised governing LaTeX/PDF design with concrete procedures, contracts,
source support and complete cases. The reader is an accounting-aware financial
modeller or software engineer who knows double-entry bookkeeping, elementary
linear algebra and probability. The reader should be able to reconstruct how a
disclosure becomes a conditional forecast, implement the declared core, and see
exactly which sector/standards operations still need specialist validation.

The wider mission remains intact. A bounded corporate reference package is an
implementable starting point; it does not replace banks, insurance, multiple
standards, complete disclosure preservation or optional probabilistic methods.
Design specification, deterministic example checking, working software,
accounting validity, forecast evidence and human comprehension have separate
statuses. This is a design repair with small executable reference calculations,
not an implementation of the production product or a forecast experiment.

## Baseline and assumptions

Before manuscript or research-generation edits, preserve source, bibliography,
PDF, control records and affected scripts with SHA-256 hashes under
`docs/design/review/pre-repair-2026-10-02/`. The workspace has no usable Git
repository; do not initialise it. Preserve original source papers.

Use a synthetic goods company with known transactions, three historical dates,
a revised comparative, working capital, plant, debt, equity and a full future
reporting period. Exact amounts are deliberately chosen for reconstructable
arithmetic; a separate rounded-disclosure case tests the solver boundary.
Select Apple FY2024 and FY2025 first-quarter public filings if accessible,
because they include multiple reporting dates, notes, fiscal calendars and
financing. An official equivalent accessible package is an acceptable retrieval
fallback, with the final selection recorded. Inventory every section and note;
formalise representative financial and contractual content and retain the
remaining content with specific unresolved dispositions. Never label a partial
translation a complete financial model.

The initial reconstruction uses finite template slots and rational linear
constraints; continuous contract exposures are amounts, avoiding the product
of an unknown fraction and an unknown total. Nonlinear extensions have explicit
interfaces, failure states and later evidence requirements. Synthetic economic
and tax assumptions are teaching choices, not recommended forecasting defaults.

## Work units and acceptance evidence

| Unit | Concrete changes and artifacts | Requirements / gaps | Required check |
| --- | --- | --- | --- |
| A. Complete companies | Add synthetic source package, full dated event/journal input, historical statements, revised view and conditional future statements. Acquire/hash a named annual/interim filing package; inventory sections/notes/cross-references; trace debt and statement observations into a bounded forecast with unsupported content explicit. | MC01–MC18, MC28; G4–G6, G11–G15 | Independently sum movements and statements; inspect actual filing pages/text; distinguish source facts from conditional assumptions. |
| B. Historical method | Define template library, slot bounds, instantiation, observation matching, joint choice constraints, conflict evidence, completeness and termination; derive rounded fixed/floating reformulation; define permitted aggregation and query invalidation. | MC08–MC12, MC26; G1, G3, G15–G16 | Known hidden history retained; incompatible history rejected; exact open/closed bounds; unsupported bilinear input gives unknown, not infeasible. |
| C. Meaning and continuity | Specify coverage denominators, narrative modality, concept/mapping composition, partitions, clocks, vintage selection, uncertainty kinds, review actions, identity, event replay, stable streams and migration. | MC01–MC07, MC10–MC11, MC24–MC27; G11–G18 | Exact positive/negative fixtures for cross-references, overlap, revisions, review invalidation, duplicate events and reordered draws. |
| D. Corporate execution | Define economic decisions and event payloads; bounded revenue/collection, purchase/payment, inventory, plant, payroll, financing, tax assumptions and closing/report mappings. Define stress/conditioning/intervention, available information, joint results and partial failure. | MC13–MC18; G4, G6, G14–G15 | Full balance sheet, income/OCI, cash-flow and equity statements agree with the same journal path; funding failure retained; missing branches keep their mass. |
| E. Language and adapters | Complete lexical/grammar and IR records; supply a complete package/evidence/opening-state/run example; specify pure built-ins, package obligations, APIs, storage and selected adapter contracts. Compare text DSL and typed-library frontend on identical IR/tasks. | MC23–MC27, MC31; G2, G9, G12, G18 | Reference fixtures parse/validate at the specified layer; exact input/output examples; unknown fields/functions rejected; document actual adapter inspection versus integration status. |
| F. Standards and sectors | Inspect accessible primary rules; give a matched cross-standard example, bond/hybrid lifecycle, dated consolidation example, bank funding/allowance/capital stress and insurer cohort/service/reinsurance roll-forward. Specify later operation-level algorithms and acceptance obligations. | MC06, MC17, MC19–MC22; G7–G8, G13, G16 | Arithmetic and internal reconciliations; paragraph/technical anchors checked; unsupported classifications preserved as unsupported; no compliance claim. |
| G. Research repair | Replace automatic generic citation dispositions with explicit per-work screening records and fail-closed generation. Inspect relevant primary follow-ups and accounting/actuarial/sector sources; archive used papers and qualify omitted sources. | MC29–MC31; G8–G9 | Every retrieved forward candidate has an individual recorded decision with scope of inspection; included technical claims have inspected anchors; regeneration preserves decisions. |
| H. Integration and review | Integrate methods where needed in the argument, with exhaustive contracts/fixtures as supporting reference. Define corpus, annotation and bounded release workloads. Rebuild, inspect rendered pages, compare baseline and update all MC/G statuses and checkpoint. | MC32–MC34; G5, G10 and interactions | Meaningful deterministic conformance checks, existing arithmetic/library checks, clean build, visual review, author-review record and honest remaining work. |

Execute A/B/C/D in a coherent reference case, then E/F/G as their source and
method dependencies become available; H is final integration. Network retrieval
can be batched, but no subagent delegation is authorised or needed.

## Detailed decisions the document must make

1. Distinguish an explicit closed synthetic model from an open real disclosure
   model. State the exact template universe, slot limits, time resolution and
   coverage result; do not claim all economic histories.
2. Supply a canonical machine-readable core contract, a full demonstration
   package and cases with expected failures. A language listing with undefined
   imports does not count as complete.
3. Keep constraints jointly linked by shared symbols, scope and choice IDs.
   Preserve strict interval endpoints and separate suprema from attained maxima.
4. Select observation views by publication/availability and ingestion cutoffs,
   then explicit selective supersession. Equal dates do not justify choosing a
   winner. A changed basis requires an explicit derived view.
5. Define scenario operations separately. Support deterministic exogenous stress
   in the core, exact finite conditioning as a specified optional method and
   structural interventions only where a declared causal model exists.
6. Define uncertainty admission and updates separately for extraction, factual
   unknowns, permitted treatment, estimates, behaviour and random innovations.
7. Resolve cash and equity from the same path as profit. Never manufacture
   financing, drop unsuccessful branches, or independently combine extrema.
8. Make sector extensions concrete enough to expose core type requirements.
   Missing primary support blocks a treatment claim, not all provisional design.

## Evidence contract and stopping conditions

The comparator is the protected 60-page draft and its expanded audit, not an
imagined finished engine. The pass criterion is a traceable repair for every
finding at the level justified by its evidence, with unresolved domain/source
or implementation requirements explicitly retained. Page count, number of
tests and number of citations are explanatory inventory only.

Hard repair triggers are inconsistent arithmetic, an undefined required input,
an unsupported source claim, a generated false screening label, silently lost
alternatives, mismatched time/basis, or an unbuildable/unreadable rendered
passage. Repair before promoting that component. Retrieval failure requires a
bounded alternate source attempt and a qualified disposition; it does not
justify inventing the content. No long numerical training/benchmark run is
part of this plan. New scientific comparisons require a separate evidence plan.

Stop dependent actions only for unavailable required evidence, a genuine
permission boundary, corrupt input or an unresolved correctness decision that
cannot be represented conditionally. Continue independent repairs. Missing
human comprehension/accounting review blocks final acceptance, not drafting.

Preserve results in `docs/design/fixtures/`, `docs/design/spec/`, research
ledgers, the revised manuscript and `docs/design/review/repair-verification.json`.
Record actual commands and findings in the execution note and author review.

## Skeptical pre-execution review

See `docs/design/review/repair-plan-review-2026-10-02.md`. Its corrections are
incorporated above. The reviewed plan is ready for local execution; this is not
an independent expert endorsement or a declaration that repairs have passed.

## Execution disposition

Executed on 2 October 2026. Version 1.1 and the reference evidence are delivered
with a finding-by-finding [result map](../design/review/gap-repair-results-2026-10-02.md),
[author review](../design/review/author-review.md), [execution note](../design/review/repair-execution-note.md)
and [final manifest](../design/review/repair-verification.json). All MC assessments
are updated; their requirement and acceptance wording is unchanged. The wider
audit remains partly open for real-company semantic closure, missing primary
authority, richer methods and independent/product/human acceptance.
