# Carry a company through consecutive years and revised assumptions

23 October 2026. S3/S4; MC13–16/18/23–26/28. Extends the same Northstar
case, not a new small financing example. Forecast evaluation remains deferred.

## Skeptical audit

The present year profile has one operation of each kind and an historical
opening. Running it twice with the same opening would repeat 2025, not model
2026. Copying only closing balances would lose claims and asset service memory.
Calling a projected closing state a newly observed fact would also be wrong.
The next increment must carry all these together and retain its conditional
origin. A failed year cannot become the next year's opening. Old annual inputs,
semantics, outputs and manuscript stay protected.

Use the existing annual interpreter as the comparator and execution component.
An explicit path layer authors each year's operating terms separately, carries
claim identities/outstanding amounts, asset cohorts and facility state, and
binds each year to the previous complete conditional closing. Its adapter to the
old opening API is an internal representation, not imported historical evidence
or a newly admitted portable Facts record. The exported path carries source,
input, preceding-result and complete-result identities. No method/library
adoption or production store is implied.

Revision means a new conditional assumption branch. It does not restate a
reported historical book or certify when the inputs were publicly available.
Recompute from the original historical source; unchanged prefixes must match.
Never splice an old later year into a changed predecessor. The original branch
must remain byte-identical. Information views must name a branch and period.

## Evidence contract and intent

Question: can the authored company year compose across consecutive fiscal years
without resetting economic memory or mixing assumption branches? Candidate is
CompanyPathInputsDraft/1 with explicit annual terms and settlement allocations.
Baseline is the protected CompanyYearInputsDraft/1 result for 2025. For 2026,
independently derive purchase units, revenue, depreciation, cash/profit, retained
earnings, claims and assets from 2025 closing amounts and authored 2026 inputs.

Primary criterion: first year matches every old journal and all 29 report lines;
second year opening equals the prior closing, including economic memory;
independent two-year arithmetic and bridges agree; revised prices flow through
both years; a second-year revision preserves the first-year result identity.
All reports identify their branch and completed period. Failed or unresolved
years leave later years unexecuted, and no annual zeros replace unknowns.

Promotion vetoes: lost/duplicated claims, repeated asset service, tax/profit reset
errors, mixed predecessor identities, changed protected bytes, unsupported
annual methods silently accepted, or fabricated historical status. Repair these
before using the result. A corrupt original source or inability to define the
annual continuation faithfully is a continuation veto for this work unit.
Check count and runtime are explanatory. Passing supports this conditional
annual composition only; no financial accuracy, general language completion,
accounting compliance, prospective information admission or durable recovery.

## Material assumptions

| Choice | Provenance and purpose | Failure mode and early check | Status |
|---|---|---|---|
| Full calendar years | Existing annual profile | Midyear depreciation/coupon unsupported; reject gaps, overlap, partial years | Retained restriction |
| Explicit annual operating terms | User's authored-input objective | Hidden continuation defaults; require all annual fields | Design hypothesis |
| Carry outstanding claims, including settled records | Existing claim controls | Identity reused or lifetime cash confused with current-year cash; distinguish opening outstanding from historical settlement | Design hypothesis |
| Carry every asset cohort | Existing plant control | New 2025 capex wrongly stays unserved in 2026; independent depreciation15 check | Reviewed local consequence |
| Same homogeneous cost and synthetic tax | Existing single-year methods | Different costing/loss tax needs new method; reject instead of adapting | Synthetic restriction |
| Revisions replay from root | Pure reference interpreter | Stale suffix or changed historical branch; digest and ancestor checks | Design hypothesis |
| Annual rather than within-year multiplicity | Smallest independent state-composition question | Mistaken whole-language completion; keep repeated invoices as the next residual | Explicit scope |

## Execution and preserved evidence

Implement under data/accounting-master/company-path-20261023/. Use standard
Python exact Fraction arithmetic and the existing jsonschema environment;
CUDA_VISIBLE_DEVICES=-1. No downloaded code, GPU, fitting or stochastic run.
Store typed input/schema, reference semantics, conformance witnesses, run
manifest, decision note and additive coverage/continuation updates. The verifier
must support read-only replay; writing new evidence requires an explicit flag.

Audit verdict: proceed with this bounded deterministic design diagnostic.
Multiple invoices per year, source/method admission, general information views,
group/bank/insurance methods and manuscript integration remain subsequent work.
