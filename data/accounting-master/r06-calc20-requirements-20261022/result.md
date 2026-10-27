# Calculations 2.0 requirements: broader relations still need company premises

Completed 23 October 2026. Plan:
`docs/plans/accounting-r06-calc20-requirements-20261022.md`.
P16/P17/P19; MC01/02/04/05/07/24–26/29/30/32–35.

The official 6 February 2019 requirements describe dimensional aggregation,
instant/duration roll-forwards, consecutive periods and inferred intermediate
subtotals. They also recognise the central completeness problem: an available
cash balance at an earlier instant does not supply the other components needed
to infer total current assets. These are useful design requirements for
reporting relations. They supply no complete algorithm for reconstructing a
company's economic history.

The retained product index lists only supporting draft requirements, and the
requirements history labels the edition **Supports Public Working Draft**
(anchors status-index/status-history/title/history-first). The product heading
and description do not establish Recommendation status or an implemented
processor. The later Calculations 1.1 requirements explicitly exclude new
cross-period and cross-dimensional functionality (prior-11-exclusion). The
broader earlier proposal therefore cannot be imported as functionality of 1.1.

All three official documents were read, including the full technical text,
tables, 20 actual image examples and Appendices A–B. All 23 requests returned
HTTP 200. Original responses, headers, errors, commands, UTC times, request
metrics, image derivatives and their separate provenance are retained.
`source-ledger.json` binds 36 exact quotations; `reading-ledger.json` records
the actual inspections. These counts describe coverage, not technical validity.
The copied illustrations were read; their underlying filings and workbooks
were not acquired or independently checked.

## What the proposed relationships cover

Concept rollups retain equal non-concept aspects and allow contributions of
+1 or -1. The text excludes mixed period types, non-numeric concepts, specified
mixed base datatypes and float/double concepts. An absent typed dimension and
a typed dimension carrying nil remain different (3.1.1). Dimensional aggregation
requires a specified domain and concept-sensitive permission; alternative
hierarchies stay separate (3.1.2). EPS can aggregate across continuing and
discontinued operations within a share class without supporting aggregation
across share classes. A range's minimum and maximum are not additive components.

Typed dimensions may be non-aggregating or aggregate to a fact where the
dimension is absent; totals expressed through nil typed values are excluded
(3.1.3/5.4). Roll-forwards combine opening and closing instants for one concept
with duration movements, including consecutive shorter durations (3.1.4).
Combined relation types may use an intermediate subtotal that was not reported
(3.2/3.4). Taxonomy reuse is an aim, with recreation also permitted (3.5).

The proposal asks preparers to associate fact sets with calculation-complete
sections (3.3.3). It treats a nil fact value as unknown, with an attempted
calculation producing an error (3.3.4). This nil fact rule is distinct from the
typed-dimension nil distinction. Filing indicators are excluded as a solution
to fact-set completeness because they concern taxonomy-defined tables rather
than specific facts (5.5). Balance-attribute checks may be explicitly disabled
per calculation; that exception does not settle the substantive accounting
signs (3.6.1).

## What company-history use would additionally require

`scope-prerequisites.json` gives ten separate mappings, with source passages,
missing premises, failure modes and dispositions. Concept matching requires
compatible units, basis, perimeter and revisions. A dimensional subtotal
requires an evidenced partition, with overlaps, eliminations and unallocated
amounts handled explicitly. Consecutive periods require exact boundary
semantics and a distinction between standalone and cumulative disclosures.
An opening-to-closing bridge also needs the applicable complete movement
model, including FX, acquisitions, disposals or reclassifications where relevant.
Subtracting two balances cannot by itself name the intervening economic events.

An inferred subtotal must retain its derivation and common underlying facts.
Its appearance in several equations cannot create independent copies of the
same uncertain quantity or turn it into a reported assertion. Completeness
and context compatibility must be established for each dependency, alongside
the joint-history constraints already required by AccDSL. These are local
design deductions, not additional requirements attributed to the source.

Cross-entity and cross-unit calculations are outside the proposed requirements
(5.1). The weighted-member examples are redirected toward separate concepts
(5.3); they do not provide a general consolidation, currency conversion or
weighted-average method. Formula capability and possible translation are
statements made by this requirements document (4/5.6). Formula's technical
specification was not independently inspected in this unit.

The 2019 duplicate proposal uses the most precise consistent value (3.3.1).
Final Calculations 1.1 uses the intersection of all duplicate fact-value
intervals (prior-11-intersection). The predecessor inquiry already retains an
exact witness distinguishing those rules; no arithmetic campaign was repeated.
The 2019 requirements cannot resolve the corrected Recommendation's outstanding
5.1/5.4 interpretation questions or select a rounding policy. Interval checking
and a report-level rounding method are proposed in 3.3.2, but the exact linked
Duplicates Working Group Note was not acquired here.

Figure 10's caption says Equity breakdown while its displayed table is a PP&E/
assets example. Both are preserved. Figures 5–6 present differently scaled
cost figures; the underlying filing's unit convention is unverified, so this
unit asserts no original-filing inconsistency. The IBM component/total rounding
example is the source's illustration, without a new numerical validation claim.

## Decision and evidence limits

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | What is not concluded |
| --- | --- | --- | --- | --- | --- |
| Complete the bounded source inquiry | Full text, 20 figures, 36 anchors and ten premise mappings recorded | No source/status or preservation veto; integrity checks must pass before recording | Requirements do not specify an adopted algorithm | Preserve and bind the result, then continue ready internal preparation | No standard adoption, runtime or whole-company reconstruction |
| Retain the existing reported/derived/history distinction | Source comparison is compatible with that design | No confirmed manuscript defect identified | Actual-company context, completeness and movements unestablished | Keep claims conditional and preserve unresolved premises | No manuscript repair or whole-row closure |
| Keep rounding and duplicates policy unselected | Early proposal differs from final Recommendation | An unqualified transfer of the early rule is vetoed | Linked note and 1.1 source ambiguities remain | Inspect a specific unresolved dependency under a new bounded plan if useful | No correction of 1.1 or default-policy change |

This is deterministic documentary evidence. No stochastic methods or candidates
were compared; no ranking, uncertainty interval or default-readiness inference
is available. There is no inference-status table for a stochastic comparison
because no such comparison occurred.

The strongest alternative reading is that the proposal's broad language already
authorises all needed aggregation. Its explicit concept/aspect constraints,
incomplete-fact example and out-of-scope sections defeat that reading. A later
normative algorithm with checked semantics could change the implementation
assessment, but would not retrospectively validate a company's missing facts.
The weakest evidence is the reproduced examples' unverified filing context.

This result invalidates neither the research question nor the existing design.
It identifies the boundary of one source and the premises required before its
proposed relations can be used. No global continuation veto fired. Version
3.48 remains frozen at 401 pages and not_ready. All 53 obligations, six
interactions and 46 operation rows remain; zero whole rows close. The 192
vintages remain unadmitted and E3 choices unselected. Independent reader,
implementability, domain and human acceptance remain pending. Runtime,
installations, empirical campaigns, acquired-code execution, commits, outreach,
publication and fees remain held.
