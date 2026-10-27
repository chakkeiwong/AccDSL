# Fixed-asset cohorts in native company state

28 October 2026. T01/C04; MC08/09/13/18/19/20/28/33/35.

## Skeptical audit and intent

Question: which asset cohort fields determine depreciation and its downstream
accounting memory in the existing three-year CompanyOperationPathDraft/1?
Reuse the native executor and the new relationship inspector; add inspection
of supplied assets and executed plant additions/depreciation only.

Baseline: the complete original operation example, not the price-revised policy
parent. Every input is an authored synthetic assumption. The baseline method is
straight_line_full_year, with service eligibility at the annual opening date
and an explicit remaining-cost cap. Neither mid-year proration nor real-world
standards compliance is implied. The initial three cohorts and all six later
additions must survive, including fully depreciated or not-yet-served assets.

Primary criterion: exact per-cohort amounts and service/remaining-cost guards
reproduce all native plant journals, annual populations and carried memory.
Independent yearly totals and same-current-report/different-future-depreciation
controls test why cohort life and service timing matter. Promotion vetoes:
wrong source/parent, missing cohort, erased guard, mismatch or invented legal
facts. Continuation veto: invalid input binding or corrupted artifact stops the
affected case for repair. Counts are explanatory; no general state sufficiency
or optimal depreciation method is concluded.

Material choices: exact fractions and annual method are inherited reviewed
scope; year-qualified event identifiers prevent repeated IDs from merging.
The 10-to-5 year life change is a discriminating authored alternative, not an
empirical estimate. Equal first-year reports with divergent next-year expense
test the insufficiency of balances alone in this declared method. Zero charges
must retain service and cap reads. Missing physical location, legal title and
asset-specific source support stay unknown. No state reduction is performed.

Pre-mortem: an inspector could duplicate a native bug or compare the wrong
annual population. Independently verify baseline depreciation 13,15,16 and
net plant 98,93,87; compare all nine cohort records. Adverse duplicate identity,
zero life, service-before-acquisition and mid-year service controls must keep
native refusal rather than create a successful cohort trace.

## Execution

Add a separate adapter/checker in
data/accounting-master/company-state-asset-cohort-dependencies-20261028/.
Read-only execution of existing modules; do not change prior manifest inputs.
Save complete inspections and controls, exact comparisons, run manifest,
result decision and fresh attempt directory.

Command: python3 -B data/accounting-master/company-state-asset-cohort-dependencies-20261028/check_cohorts.py --output data/accounting-master/company-state-asset-cohort-dependencies-20261028/attempt-01
Environment: existing Python/jsonschema, CPU exact arithmetic; no accelerator
imports, seeds, stochastic comparisons or research rankings.

After the bounded criteria pass, attach evidence to T01/C04 and leave general
population, industry/basis and actual source construction open.
