# Production-cost method and Version2.93

15 October2026 (Asia/Hong_Kong). P17-04/11 with P18 integration;
MC02/05–07/11/13–16/19/20/24–28/30/32–35. Scoped result, not_ready.

Normal-capacity allocation now connects each cost origin to unsold goods,
current expense, PPE and cash. Low output60, sales40: unit cost5.8,
unallocated overhead72, closing stock116, pretax profit66 and cash1010.
Normal output100/sales80 gives profit306/cash1250; high output150/sales120
reduces fixed allocation per unit and gives profit546/cash1450. Idle and
same-production sell-through cases are separate. These are conditional
scenarios, not observed factories or a ranking of production strategies.

218 exact checks pass, combining fixed expected results, an independent
per-resource signed ledger, per-unit allocation, clearing-account exhaustion,
cost/quantity conservation, direct/indirect cash and adverse admissions.
Balanced adverse cases show why trial balance equality is insufficient:
low actual-volume absorption defers24 idle cost; high uncapped allocation
creates90 of unincurred fixed cost, with a balancing credit leaving stock
and profit18 too high; capitalization of excluded30 defers10 in unsold stock.
Both cash reconciliation methods account for12 depreciation in closing stock.

26 source/integrity checks pass. AASB102 compilation3 is31December2021,
not its last amendment date20December2021; this was repaired in the plan
before numerical work. Relevant cost/expense/scope/appendix/compilation
material was inspected. Historical116 production depreciation and15 delivery
admission are reused within their inspected scope. No current authority claim.
The source-checker's initial literal-case mismatch for No WIP was repaired;
it was a text-check bug, not absent cost-model scope. The planning-only
normal/high arithmetic was also corrected before fixture execution, as
recorded in the method note. No old candidate is rewritten.

101 preservation/build checks pass.78 protected predecessor source files and
the2.92 PDF remain unchanged; all81 project build inputs are inside2.93.
Displays94→96, labels162→163, citations490→493; no removals; bibliography
unchanged. The100 unrelated staged entries remain preserved. Clean build
25.416seconds;274pages; SHA256
46d17f8440c325353f6a7e250897a1629e5f08b60107d7104ec7bf30c04bd17c.
PDF: docs/design/proposal/manuscript-production-cost-20261015/accounting-product-proposal.pdf.
Physical1,107–112 were visually inspected; page110 table/journals/cash
received full-page inspection. Whole-document and human acceptance are pending.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
|---|---|---|---|---|---|
| Integrate historical production-cost method | Cost-origin, capacity, stock and cash reconstruction pass | Balanced invalid allocations rejected | Actual capacity, yield, NRV, transfer and cost population | Retain explicit input admissions and larger-pool unsupported cases | Actual compliance or a universal costing algorithm |
| Keep pretax scope explicit | Pretax net-assets identity passes | After-tax request refused without tax inputs | Tax bases, enacted rates and timing uncomputed | Resolve in any full-company combination | Zero tax, after-tax equity, dividends or statutory completeness |
| Continue with finite convergence audit | Material gap filled; prior operations credited | No continuation veto | More examples do not demonstrate complete requirement coverage | Reconcile all53 obligations and dependencies against2.93 before selecting further work | P17/P18/P19 closure or human readiness |

Post-run red team: the weakest assumptions are normal capacity100 and equal
cost/yield for the good units. An actual capacity estimate, product mixture,
WIP, normal losses or changed resource cost could invalidate the formula
without invalidating102.13. Complete source populations, actual yield and
independently supported capacity would discriminate. No stochastic inference.

P18 disposition: add Section9.4.6 immediately before the original inventory/
asset discussion; retain prior lot/NRV/PPE cases. This new cost-origin bridge
does not supply the whole-company source-to-forecast chain. Latest full author
assessment remains2.72, negative. Runtime/controller, installation, outreach,
paid review, publication and commits remain held in this continuation.
