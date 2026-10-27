# Northstar baseline and assumption audit

15 October 2026. R01a under docs/plans/accounting-corporate-portable-20261015.md.
The current Version2.93 chapter13 is the documentary comparator. The old
Northstar posting fixture and P05 economic-input/prototype files are preserved.
They are distinct evidence, not interchangeable new portable representations.

## Material findings before construction

1. The current manuscript's synthetic original publication/ingestion dates are
   1/3 August2024; corrected interim/annual dates are2/5 March2025. P05's old
   inputs instead use1/2 August and1/2 March. New records use the current
   manuscript dates and explicitly retain a mapping to the conflicting old
   values. No frozen fixture is rewritten. IX04's February dates are another
   standalone adverse case, not Northstar's correction chronology.
2. The old prototype information helper requires both publication and ingestion
   before an investor query. Current timev2 permits subsequently acquired
   archives if exact public-byte availability is established. Copying that
   helper would compute the wrong information view. Documentary expectations
   must separately check investor and system-as-of conditions.
3. Northstar's2025 stress uses a supplied true/corrected opening. The corrected
   report is published in March2025, after the January scenario origin. This
   is an exploratory conditional teaching projection, not an information-
   available January forecast. A historical-investor request using that later
   report must reject. Under exploratory mode, the opening and drivers are
   explicit synthetic conditions; policies still cannot inspect simulated
   future realizations. No as-of predictive performance can be inferred.
4. The preserved posting fixture lists the sales accrual before purchase, then
   the associated inventory expense later. It represents classified aggregate
   movements, not a safe atomic event order. The economic source already uses
   purchase then one delivery. The new schedule uses that dependency order,
   combines revenue and cost on delivery, and verifies intermediate inventory
   and cash. Final amounts must equal the preserved fixture. This is an explicit
   representation mapping, not a new assertion about recovered invoices.

## Defaults and status

| Choice | Provenance | Justification and failure risk | Earliest diagnostic | Status |
|---|---|---|---|---|
| Half-year/year accrual | Northstar assumptions | Authored teaching fractions; not actual day-count inference | Interest and cohort depreciation by period | Baseline assumption |
| Homogeneous cost5 goods | Northstar and P05 inputs | Closed synthetic pool; not general inventory accounting | Quantity/cost at every purchase/delivery | Baseline assumption |
|20% positive-profit tax | Northstar | Same declared tax model; no jurisdiction/deferred-tax claim | Expense/payment/prepayment bridges | Baseline assumption |
| Continuous floating share x | Initial profile/IX01 | Historical equal rates do not identify mix | Shared affine cash/profit/equity and changed9% control | Reviewed bounded method |
| Corrected opening in2025 stress | Current chapter13 | Conditional archival question; would leak future disclosure into investor backtest | Reject investor mode at January cutoff | Explicit scenario condition |
| P05 operation order | Economic inputs and source code | Provides a feasible aggregate order; not invoice chronology | Nonnegative inventory and funded settlements | Reuse hypothesis checked locally |
| Portable I1/L1 envelope | Current shared contracts | Preserves ownership/identity; named prose alone is insufficient | Closed schema, reference/hash/blob closure | Proposed contract |

No inherited runtime helper is executed or promoted. The finite documentary
checker derives historical and forecast finances from economic inputs and
compares them with independently authored expected values. Later runtime,
empirical forecasting, independent and human acceptance remain separate.
