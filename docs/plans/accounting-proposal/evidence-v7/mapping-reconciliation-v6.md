# P15 mapping and aggregation reconciliation — v6

This audit corrects MC07 and G12 using the current manuscript and retained P06 evidence. The earlier MC25/G18 and MC34 slice received independent bounded acceptance in execution-1; full P15 remains incomplete. P06 supplies exploratory engineering evidence, not an approved architecture or accounting method. Only these two current assessments are superseded.

The retained P06 conformance record reports 27 passing P06 tests with no failures, errors or skips. All five recorded implementation/checker/test/specification/fixture hashes match current files; the supervisor execution-2 test hash also matches. The six mapping/partition test names used here occur in the retained report. These tests were inspected, not rerun. The test record and independent P06 review establish only bounded deterministic conformance.

## Mapping relationships

The manuscript distinguishes equivalent, component, broader, presentation-reclassification and measurement-transformation relationships; source concepts remain identifiable and company extensions need not equal a standard concept. Many-to-many mappings carry dates, dimensions and evidence. The later mapping section identifies entity/basis/period/dimensions, reviewer and transformation fields; the existing Core IR Mapping schema declares all five relations, a string applicability reference, optional transform/partition references and source/review references. These are existing record shapes, not an absent registry schema.

MappingRule admits equivalent, component and reclassification only, requires nonempty concept IDs and provenance, and rejects conversion. compatible_context selects one active direct edge when concept is the only context difference; optional source_context/target_context restrict entity strings, not full contextual predicates.

The retained sales-to-revenue case preserves both concept spellings, scale and precision. It asserts a compatibility witness, not source-backed equality of observed amounts or cross-company comparability. Provenance is fixture:review, not accounting authority.

Broader relations, numerical measurement transformations, full dimensional applicability predicates and a versioned company-concept registry are not established by these operations. Specify registry identity/version, relationship direction and cardinality, complete applicability predicates, evidence/reviewer dependencies, and how unsupported or ambiguous mappings remain unresolved. Supply real-source cases for differently named equal quantities and similarly named unlike measurements. Keep vocabulary alignment distinct from measurement conversion and accounting eligibility; a nonempty provenance string cannot authorize equivalence.

Support: `docs/design/chapters/02-history.tex` (lines 56-81); `scripts/context_chronology_v1.py` (lines 147-188); `scripts/context_chronology_v1.py` (lines 221-256); `tests/test_accounting_p06.py` (lines 38-71); `data/accounting-master/deliverables/P06/conformance.json` (JSON Pointer /tests/test_accounting_p06); `docs/design/chapters/02-history.tex` (lines 222-233); `docs/design/spec/core-ir.schema.json` (JSON Pointer /$defs/Mapping). Exact hashes are in the matching JSON claim.

## Composition ambiguity

The manuscript explicitly says component followed by equivalence remains component and that two measurement transforms compose only when intermediate bases and information dates agree. It also permits many-to-many mappings. These are substantive specified rules; the general admissible composition algebra and executable resolution are still incomplete.

_check_mapping_graph rejects directed cycles across all supplied rules without filtering by applicability dates. compatible_context does not traverse a chain; it selects active direct source-target edges and raises AMBIGUOUS_MAPPING for more than one before checking entity restrictions. Identical contexts return identity after graph validation.

A two-edge cycle and one expired direct rule are rejected in the retained test. General chain composition, overlapping active alternatives, and non-overlapping dated reverse edges are not independently tested by the cited methods.

Acyclicity does not implement transitivity, relation-specific composition, precedence or conflict resolution. Equivalent is represented as a directed rule and cannot be assumed to support symmetric registry edges. Decide whether supported execution permits direct edges only or composable chains. Specify composition by relation kind, evidence/dependency propagation, date/context intersection, ambiguity handling, cycle policy and invalidation, with positive and negative worked cases. Preserve competing mappings as unresolved alternatives until the proposal defines a justified selection or composition rule; do not inherit acyclicity or direct-only selection as immutable product defaults.

Support: `docs/design/chapters/02-history.tex` (lines 63-73); `scripts/context_chronology_v1.py` (lines 203-250); `tests/test_accounting_p06.py` (lines 63-71); `data/accounting-master/deliverables/P06/conformance.json` (JSON Pointer /tests/test_accounting_p06); `docs/design/chapters/02-history.tex` (lines 224-233). Exact hashes are in the matching JSON claim.

## Context gross net

The manuscript distinguishes principal, carrying amount, contractual flows and fair value, and warns that gross/net revenue and segment measures differ. Contextual addition requires compatible entity, perimeter, time, dimensions and basis. Core 0 context equality explicitly includes instant/period/calendar; this is wider than P06 Context. The manuscript also uses Apple vendor non-trade receivables as an unlike-meaning counterexample.

_context_mismatch compares entity, perimeter/version, basis, measurement, unit, currency, calendar, dimensions, gross_net, parent/group and display metadata before concept. Equivalent mappings cannot waive these mismatches. Context has no reporting-period start/end or observation amount; compatible_context is not a full dated-quantity comparison.

The retained same-concept synthetic pairs reject historical-cost/fair-value, gross/net, perimeter/version, basis, currency and calendar mismatches; scale conversion also fails. This is guarded rejection, not a method for reconciling or converting those measures. Separately, the retained Apple 2024 primary report, Note 4 printed p.38, confirms that component sales to vendors are excluded from products net sales and gains reduce products cost of sales. This supports that company-specific distinction, not a general cross-company mapping method.

Positive cross-basis, gross/net or perimeter transformations and actual reporting-period comparability are not established by the mapping API. Entity mismatch rejection also does not establish comparability between two real issuers. Turn the existing Apple source distinction and synthetic measurement/gross-net rejection examples into complete mapping records and expected outcomes. Define contextual comparability separately from numeric conversion; bind quantities to reporting periods/evidence views and preserve original/derived measures. Add a justified gross/net bridge or explicit refusal and a perimeter-change/reclassification case. Reject unsubstantiated aggregation and report the exact missing conversion or comparability evidence. Calendar equality and a query date alone cannot establish that quantities refer to the same period.

Support: `docs/design/chapters/02-history.tex` (lines 56-81); `docs/design/chapters/06-language.tex` (lines 79-85); `scripts/context_chronology_v1.py` (lines 135-144); `scripts/context_chronology_v1.py` (lines 191-256); `tests/test_accounting_p06.py` (lines 49-71); `data/accounting-master/deliverables/P06/conformance.json` (JSON Pointer /tests/test_accounting_p06); `docs/design/spec/core-contract.md` (lines 116-121); `docs/design/chapters/02-history.tex` (lines 245-252); `docs/design/cases/apple/annual-2024.txt` (lines 1992-2002); `scripts/context_chronology_v1.py` (lines 85-115). Exact hashes are in the matching JSON claim.

## Finite partitions residuals

The manuscript requires a disjoint and exhaustive population for sumOver, retains unallocated residuals instead of setting them to zero, and leaves unobserved geography-by-product cells unidentified. The Core IR Partition schema already records population, axis, members, context, disjoint/exhaustive proof references and an optional residual member.

check_partition enumerates caller-supplied finite IDs, rejects duplicates, outside members, overlap and omission, and accepts an explicit known residual exactly equal to the missing set. Unknown residuals are rejected. map_components requires one exact rational value per population ID and an exhaustive named partition; it has no residual argument, so a residual can enter that operation only as an explicitly valued ordinary member. Both component and reclassification take this same arithmetic path.

The retained tests verify finite completeness, overlap/omission/unknown-residual rejection, a known residual membership witness and the 3+5=8 component total. They do not establish the source completeness of the declared population, a measured value for a residual merely marked known, or an independently tested reclassification treatment.

Enumeration proves disjointness and exhaustiveness only relative to supplied IDs. String proof references and known=True do not prove real disclosures are complete or accounting amounts comparable. Unknown-residual feasible-set/interval propagation and non-enumerated populations are not provided by these APIs. Specify what source evidence establishes the population, measurement context and membership; define residual identity, known amount versus known membership versus missing amount, and how unresolved residuals constrain totals. Connect Core IR proof references to checkable witnesses and define supported reclassification cases and dimension-removal semantics. A valid finite partition is a reusable conformance example, not proof of disclosure coverage. Preserve partial totals and unresolved residual constraints without inventing zero or certifying an exact total.

Support: `docs/design/chapters/02-history.tex` (lines 235-243); `docs/design/spec/core-ir.schema.json` (JSON Pointer /$defs/Partition); `scripts/context_chronology_v1.py` (lines 264-319); `tests/test_accounting_p06.py` (lines 73-85); `tests/test_accounting_p06.py` (lines 269-283); `data/accounting-master/deliverables/P06/conformance.json` (JSON Pointer /tests/test_accounting_p06). Exact hashes are in the matching JSON claim.

## Alternative classifications

The manuscript already gives two classifications of the same 260: 180+80 and 200+60; adding all four to obtain 520 is forbidden. Population identity is shared and axes differ; cross-tabulation cells need additional constraints.

combine_partitions rechecks each partition and rejects any shared population member ID. It permits only disjoint populations and returns their union; it does not compare accounting contexts or sum amounts. map_components labels the output with an axis but requires otherwise matching Context records, rather than implementing general dimension removal.

The retained product partition has atoms a=3 and b=5 and total 8. A geography partition north={a,b} over the same IDs cannot be combined with it. This directly exercises the anti-double-counting rule. It is not a real product/geography filing or an independently valued pair of alternative totals.

Distinct IDs for the same economic item can evade a membership-only overlap check. Shared real populations, group eliminations, measured marginal consistency and reconstruction of joint geography-by-product cells are not established. Provide a source-backed product/geography example with canonical population identity, compatible periods/bases/perimeters, independently reconciled equal totals, explicit refusal to sum axes and preserved unknown joint cells. Specify when genuinely disjoint populations may be added and how source aliases and context changes affect that decision. Define economic population identity and a separate contextual amount check; a disjoint-ID union cannot by itself authorize financial addition. Do not convert two marginal classifications into a joint table without evidence.

Support: `docs/design/chapters/02-history.tex` (lines 235-243); `docs/design/chapters/06-language.tex` (lines 79-85); `scripts/context_chronology_v1.py` (lines 303-330); `tests/test_accounting_p06.py` (lines 269-283); `data/accounting-master/deliverables/P06/conformance.json` (JSON Pointer /tests/test_accounting_p06). Exact hashes are in the matching JSON claim.

## Company extensions over time

Company extensions retain distinct meaning, may express dated presentation changes and cannot override recognition rules. Mapping records specify applicable entity, basis, period and dimensions.

MappingRule.active uses start-inclusive/end-exclusive date windows, and a dated rule without an as-of date is ineligible. Perimeter and perimeter_version differences are rejected before concept mapping. P06Engine.add_mapping stores rules and checks cycles; it supplies no versioned extension lifecycle or source-to-period migration policy.

An expired rule is rejected; changed perimeter versions fail compatibility. The cited retained tests do not cover a positive switch between dated company extensions, window-boundary transitions, a change within a reporting period or a restated comparative under a revised perimeter.

A query-date eligibility test does not show that a rule applies throughout a reported duration. Rejecting a perimeter change is not a consolidation or reclassification method. Inactive rules still enter cycle validation; the date-window design cannot automatically admit every historically non-overlapping mapping sequence. Define extension versions, economic validity versus evidence availability, period-spanning applicability, supersession/alternatives and downstream invalidation. Supply a two-period company-extension example and a perimeter-change case retaining original and restated views, with explicit unsupported outcomes where comparability cannot be established. Keep dated comparability unresolved unless the mapping, population and reporting period all support it. The proposal must choose and justify lifecycle rules independently of P06 storage or graph convenience.

Support: `docs/design/chapters/02-history.tex` (lines 224-252); `scripts/context_chronology_v1.py` (lines 147-188); `scripts/context_chronology_v1.py` (lines 203-256); `scripts/context_chronology_v1.py` (lines 867-881); `tests/test_accounting_p06.py` (lines 49-71); `data/accounting-master/deliverables/P06/conformance.json` (JSON Pointer /tests/test_accounting_p06). Exact hashes are in the matching JSON claim.

## Assessment and next decision

Both MC07 and G12 remain **partial**. It is wrong to say mapping/partition records and finite residual handling are wholly unspecified or unexecuted. It is equally unsupported to treat direct mapping witnesses, caller-supplied partitions or contextual mismatch rejection as source-backed accounting comparability. The existing manuscript specifies two composition rules and contains an actual Apple disclosure distinction; those contributions are retained while their missing registry and application cases are made explicit.

| Decision | Primary criterion | Veto diagnostics | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Submit MC07/G12 reconciliation for bounded review | Every original G12 obligation is assigned inspected support and specific remaining work | Invalid source hash/anchor, missing retained test provenance, altered protected files or changes outside two rows prevent completion | Real-source population completeness and comparability remain unresolved | Independent bounded review, then separately reconcile MC24/G2 | Full P15 acceptance, architecture selection, accounting validity, empirical forecast validity or human acceptance |

Finite populations, Gregorian dates, exact arithmetic, same-entity direct mappings and graph acyclicity come from the historical P06 profile. They remain exploratory assumptions; no comparison establishes them as product defaults. No new scientific run or product test was performed. The main alternative explanation for the checked arithmetic is that synthetic IDs and metadata encode the desired answer; the proposal still needs source-backed worked mappings and independently inspectable applicability. This audit is complete only for the two named assessments, subject to independent review. Historical-phase completeness and initial-profile alternatives remain separate P15 tasks.
