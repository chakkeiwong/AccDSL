# Apple accounting-pronouncement transitions and disclosure timing

10 October 2026. Continuous authorised internal proposal preparation,
E01/C03/E07/C08; MC01–05/07/15–16/19/28/30/32–35 and G5/G7/G11/G13/G18.
Overall readiness remains `not_ready`. This is a bounded documentary unit;
freezing its result is a checkpoint before the next feasible unit.

## Evidence contract

Question: what do Apple's retained FY2024 annual and FY2025 Q1 interim
Recent Accounting Pronouncements and critical-estimate passages establish about
future disclosure changes, transition bases and historical-query limits?
Comparator: frozen 157-page Version 2.16 at
`docs/design/proposal/manuscript-legal-20261010/`, with manifest
`data/accounting-master/apple-legal-20261010/run-manifest.json` and completion
record. Dependencies include the completed segment, tax, Note 1 and legal units.

Primary criterion: complete source-bound spans for annual Income Taxes and
Segment Reporting, interim Disaggregation of Income Statement Expenses,
Income Taxes and Segment Reporting, and both critical-estimate assertions;
preserve issuance/event dates, stated adoption quarter, transition method,
affected disclosure population and what the text does not supply. Explain why
disclosure granularity and retrospective/prospective transition affect
cross-period queries without manufacturing historical expense splits.

Promotion vetoes: treating an issuer adoption plan as operative standard
authority, treating a planned quarter as observed adoption, converting a
disclosure requirement into a recognition or measurement rule, inferring
historical expense components absent from the filing, or erasing the interim
January 2025 clarification because the period ended in December 2024. A source
hash failure, incomplete span partition, altered V2.16 files or unresolved
render defect stops dependent interpretation. No numerical calculation is
required; no standard text is independently adjudicated here.

Explanatory diagnostics are source/page counts, clean build, citation checks
and a date table. They cannot certify GAAP compliance, transition correctness,
semantic completeness or readiness. The result must state the quantity actually
computed and what remains unproved. No stochastic comparison applies.

## Skeptical plan/default audit — passed before execution

| Choice/provenance | Status and justification | Failure mode / early diagnostic |
| --- | --- | --- |
| Annual PDF and interim HTML retained in the Apple continuation | Fixed documentary baseline | Verify exact hashes and original page/HTML text |
| Complete pronouncement-to-critical-estimate spans | Bounded source population chosen by next frontier | Verify ordered headings, no skipped body text and original meaning |
| Adoption quarters and transition methods | Issuer-reported plans | Keep event/report/availability dates and plan versus outcome separate |
| Annual segment sentence | Already read in V2.14 | Preserve as dependency; do not count a repeated sentence as new evidence |
| Tax/Note 1 references | Existing completed dependencies | Link query consequences without repeating closed calculations |
| No ASU legal/technical conclusion | Operative authority not inspected in this unit | Do not state applicability, amendment hierarchy or compliance |
| At most three local builds, 240 seconds each | Resource budget inherited from adjacent unit | Diagnose a failed build before expanding |

Pre-mortem: a neat adoption table could be mistaken for a standard matrix; a
retrospective label could be read as proof that historical figures are known;
the expense-disaggregation text could be turned into invented inventory,
payroll or depreciation splits. The cheapest checks are exact quoted wording,
event dates relative to the December 28 period-end, and explicit unknowns for
amounts, thresholds, definitions and affected historical periods.

## Reader argument and cold-reader questions

Reader: accounting modeller/implementer after the legal-proceedings section.
They need to know why a future disclosure change alters the evidence schema
without changing an older statement by assumption. Argument: reported future
requirements -> affected disclosure populations -> transition basis and dates ->
critical-estimate boundary -> query consequences and unresolved source facts.
Add roughly two pages to the real-company chapter, preserve prior displays and
bibliography, and use no new equation.

Cold-reader questions fixed before drafting:

1. Which pronouncement affects which disclosure population?
2. What quarter and transition method does Apple report for each plan?
3. Why does retrospective adoption change a historical query without proving
   that the underlying economic transactions changed?
4. Why is the January 2025 clarification an event after the interim period end?
5. What do the critical-estimate passages establish, and what do they leave
   unknown about carrying values and tax reserves?
6. Which authority and data would be required before treating these plans as
   operative accounting rules or reconstructing missing expense components?

## Source boundaries and execution

Annual source: `docs/design/cases/apple/annual-2024.txt`, exact retained PDF
`docs/design/cases/apple/annual-2024.pdf`, source span begins at
“Recent Accounting Pronouncements” at Unicode offset 128403 and ends before
Item 7A after Legal and Other Contingencies. Interim source:
`docs/design/cases/apple/interim-2025q1.txt` and retained HTML, span begins at
“Recent Accounting Pronouncements” at Unicode offset 48678 and ends before Item 3 after
Critical Accounting Estimates. Exact offsets and hashes are written before
interpretation. Original annual PDF page 29 (printed 26) and interim printed page 17
are rendered separately; interim reflow remains a derived view.

Use `CUDA_VISIBLE_DEVICES=-1 python3`, preserve the V2.16 manifest/completion
and all four live records before editing, then capture sources, run deterministic
checks, copy the authoring tree, draft, build, render and read changed/adjacent
pages in ordered slices of at most six pages. Run a surface audit and freeze a
manifest with a decision table, inference-status table, result, review and next
frontier. Update requirements/checkpoint/next-plan only after the result is
complete. No network, install, GPU, worker, controller restart, outreach, paid
review or publication is needed.

Stop only for source/hash corruption, an unrepaired substantive or rendering
error, a real authorization boundary, or an explicit pause. Missing ASU text,
historical detail or actual adoption blocks only the affected claim/query;
continue other feasible internal work.

## Resume execution note — 10 October 2026

The skeptical resume audit confirmed the source/PDF baseline and boundaries but
found a stale full-checker hash in the initial source report. No source/PDF veto
fired. Preserve the failed reports and perform fresh source validation in new
subdirectories rather than overwriting earlier evidence. The fresh 38 checks
reproduce all nine units/four spans/seven queries after normalising only the
retained-span relocation paths; 20 actual candidate/preservation checks pass.
This corrects the handoff's anticipated count of 35. All four live records now
point to Version 2.17 and annual general-litigation risk as the next action.
Freeze, verify manifest/completion, then continue immediately.
