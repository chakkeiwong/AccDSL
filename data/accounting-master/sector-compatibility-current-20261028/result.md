# Sector compatibility checked — 28 October 2026

Five delivered sector profiles are now explicitly connected to the current
compatibility reference: InsurancePAADatedBook/1, BankComponents/1 and /2,
BankAssessment/1 and BankAssessmentExactTime/1. The annex names exact owners,
typed records, clocks/context, effects, native refusals and permitted connections.
It preserves the distinction between the two AU books and the separate US book.

Attempt02 passes1,059 checks with77 locked files in62.08seconds under CPU-only
Python3.11.15. It reproduces all seven full PAA results, including named/renamed
charts and the preserved equipment/equity complement, and all21 refusal controls.
Every financial report field and closing balance agrees with the independent
authored expectations. Group identities, dates, gross flows, unresolved notes
and false admission flags survive.

For the five retained US capital cases, every extracted amount and ratio is
bound to the complete native record and its existing dependencies. Independent
Fraction arithmetic derives book equity, allowance admission/excess, goodwill
deduction, risk-weighted assets, capital amounts and all defined ratios. The
missing-average-assets case keeps leverage unresolved. The native capital
assessment retains accounting_effect=none; no prudential deduction is posted
into the book. This is a check of the historical conditional example, not a
current regulatory determination. Earlier whole-bank packet replays remain
separate evidence; they were not rerun or relabelled.

Attempt01 preserved a checker representation error after the PAA work passed:
native rational objects with dependency_refs were compared directly with their
display extraction. Attempt02 checks the exact defined projection, validates
all dependency references, then calculates amounts independently. No financial
implementation, fixture or expected amount changed.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
|---|---|---|---|---|---|
| Retain PAA-to-company/interim-report connection | Complete native replay and independent full statements pass | No identity, group, date, prefix or report failure | Finite conditional synthetic scope and actual applicability | Use the existing adapter; specify broader dates/amounts/group effects separately | General insurance engine or actual group admission |
| Retain US book-to-capital connection | All five extracted results and independent rational calculations pass | Missing average assets correctly keeps leverage unresolved | Historical rule assumptions and supplied CECL measurement | Preserve same-basis input/eligibility requirements in any successor | Current regulation or a CECL estimator |
| Keep AU/US and /1-/2 migrations explicit | Distinct source contracts, schemas and operations bound | No implied cross-profile transfer is admitted | Composite state and effect ownership remain unspecified | Define one same-basis composition before implementing it | Unified bank runtime or full MC21 closure |

The strongest alternative explanation is a shared original modeling error in
the narrow source assumptions. This arithmetic/interface regression cannot
resolve that source/domain judgment. Changed assumptions, lost rights/memory
or an invalid full report would require repair of the affected connection.
No global continuation veto fired. S1–S5 remain partial; S6 held; E3 deferred;
selected5.55-R1 remains not_ready.

Plan: docs/plans/accounting-sector-compatibility-20261028.md.
Evidence: attempt-02/run-manifest.json and four compressed complete records.
