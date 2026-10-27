# All46 original operations after Version3.25

Original wording and hashes are preserved in `residual-ledger.json`. A finite
case does not close a whole row. Repair IDs refer to `repair-queue.md`.

| Row | Located delivery | Remaining internal work | Application dependencies |
|---|---|---|---|
| P17-04.01 Performance, invoice and collection | Performance, gross billing, collection, advance allocation and successive contract changes | C1, C2 | Contract eligibility, control, price and progress |
| P17-04.02 Unbilled customer advance | Prepaid billing including state-only allocation and duplicate rejection | C2 | Shared contract identities and opening balances |
| P17-04.03 Sale with return right | Actual return settlement, handling/NRV distinctions and group tax/cash join | C2 | Return rights, stock condition and handling classification |
| P17-04.04 Bundles, principal/agent, warranties, modifications | Distinct/integrated changes and one allocated mixed amendment, assurance/service distinction | C1 | Enforceable allocations, faithful progress and warranty facts |
| P17-04.05 Inventory and supplier payables | Production cohorts, joint/byproducts, financing payables and inventory-sale/NRV joins | C2 | Actual costing policy, yields, capacity, lots and NRV |
| P17-04.06 Payroll and benefits | Benefit changes, funding, ceiling/availability and multiemployer conditional methods | C2 | Employee law/data, actuarial values and common-control allocations |
| P17-04.07 PPE and estimate/modification | Inspection/replacement/restoration and original/restated/current annual PPE/tax example | C2 | Asset cohorts, prior information and recoverable values |
| P17-04.08 Impairment and provisions | Floor redistribution, capped reversal, corporate/NCI impairment and restoration methods | C1, S1 | Recoverable values and provision facts; zero-weight CGU rule unresolved |
| P17-04.09 Leases | Per-right lease reduction, repeated reduction, payment and depreciation | C2 | Rights attribution, discount/calendar/variable-payment terms |
| P17-04.10 Current/deferred tax | Origin-specific deferred tax, compound-tax unwind and annual comparative reconstruction | C2 | Actual rates, tax bases, recovery, offsets and applicable law |
| P17-04.11 Closing and cash-flow presentation | Shared two-entity close, gross cash, NCI, maturity conversion/redemption and tax-aware EPS | C2, J1 | Complete openings, reporting periods and cash classifications |
| P17-04.12 Currency/group interaction | Reciprocal and inventory elimination, control/FX/restatement methods and a same-currency company join | J1 | Control, functional currency, reciprocal identities and actual rates |
| P17-04.13 US GAAP and ASBE admission | Historical source profiles distinguish ASC/ASBE access from EU/AU conditional methods | S2 | Operative topic/issuer-class/edition admission |
| P17-05.01 Debt issue/EIR/accrual/settlement | Debt basis, fees, EIR, due/unpaid states and compound cash/tax schedule | B1, C2 | Actual agreements, dates, reset fixings and valuations |
| P17-05.02 Modification/default | Inclusive ten-percent and qualitative findings, fee purposes, recalc/repurchase and unpaid claims | B1 | Actual qualitative substantiality and legal remedies |
| P17-05.03 Equity/conversion | Shares, treasury equity, compound issue/repurchase and original-term maturity conversion | F1, S1 | Legal capital, actual rights/values; early-conversion measurement remains source-specific |
| P17-05.04 Awards/EPS | Service/market conditions, cash choices, simple participation and ordered multiple-series/company EPS | F1 | Senior/capped/dependent participation, actual conditions and valuation |
| P17-05.05 Benchmark/hedges | Repeated item additions, acquired derivative origins, homogeneous partial discontinuation and inventory sale/NRV | F2, J1 | Valuations, designation, effectiveness and recoverability findings |
| P17-05.06 Control/acquisition | Acquisition/control, partial goodwill, impairment and group/foreign-operation bindings | J1 | Business/control conclusions, purchase valuations and actual tax |
| P17-05.07 Ownership changes and disposal | Ownership without loss of control and foreign-operation full/retained disposals | J1 | Dated ownership, rights, valuation and disposal consideration |
| P17-05.08 Reciprocal/inventory elimination | Reciprocal allocations, inventory margin/tax elimination and later external sale release | J1 | Matched legal books, control intervals and shared lots |
| P17-05.09 Currency | Hyperinflation before translation, exchangeability purpose/date and transition origins | J1 | Actual indices, currency/rate estimations and perimeter |
| P17-05.10 Guarantees/succession/real perimeter | JPMorgan/Apple issuer and guarantee source inquiries preserve unresolved rights | S2 | Actual agreements, succession, obligor identities, ranks and perimeter |
| P17-06.01 Origination/deposit/external transfer | Origination/deposit/transfer distinctions and restricted US bank book | B1, J1 | Actual contract/currency/admission and compatible book joins |
| P17-06.02 Funded ECL and credit state | Ordinary credit/cure methods plus original-rate POCI subsequent-loss lifecycle | B1 | Calibrated credit forecasts, class/POCI/write-off findings and actual terms |
| P17-06.03 Undrawn commitments | Full and partial/revolving draws retain original risk and provision/allowance origins | B1 | Draw/cancellation dates, commitment horizons and eligibility |
| P17-06.04 Modification/default | Modification/cure, collateral, fees, transfers and guarantee/option continuing involvement | B1 | Rights/risks/control, servicing values and actual cash classification |
| P17-06.05 Funding/liquidity | Confirmed funding receipts, full/partial/pending withdrawal payments and funding interest | B1, J1 | Facility access, collateral, venues, maturity and behavior |
| P17-06.06 Regulatory capital | Restricted US eligibility, allowance cap/excess and separate leverage denominator | S2, J1 | Operative-date chain, actual regulatory perimeter, eligibility and payout facts |
| P17-06.07 Forecast/decision policy | Joint-law, cutoff, survival and unweighted-family queries plus future validation protocol | V1 | Calibration, decision objectives and future authorized empirical evidence |
| P17-07.01 GMM/service/finance | GMM future-service CSM/loss order, finite service/finance and groupwise opening | I1, J1 | Actual FCF/RA, coverage units and finance policy |
| P17-07.02 Grouping/cohorts | Closed group membership, separate openings and adverse pooling | J1 | Actual insurer portfolio, cohort and profitability membership |
| P17-07.03 Reinsurance | Covered quota changes, timing/recovery and conditional nonlinear stop-loss query | I1, I2 | Actual treaty terms, collectability and calibrated joint distribution |
| P17-07.04 Acquisition costs | Acquisition cost allocation, impairment/reversal, group transfer and route assessment | I2, J1 | Actual asset recoverability, allocated costs and expense reconciliation |
| P17-07.05 VFA/guarantees | Priced finite guarantee, VFA pool/fee/service and mitigation distinction | I1, J1, V1 | Actual underlying model, risk adjustment, eligibility and dependence |
| P17-07.06 Transition | Transition dates, route/impracticability and supplied groupwise opening/recovery | I2 | Complete histories and supported transition valuation inputs |
| P17-07.07 Actuarial estimation | Conditional/process/backward-law distinctions, reserve center, dependence and future comparator design | V1, L1 | Actual triangles/tails, calibration and independent downstream evaluation |
| P17-07.08 Shared interfaces | Closed accounting/query profiles, atomic publication/replay and both lost-acknowledgement worlds | J1, R8 | Actual durable runtime and compatible migrations remain held |
| P17-08.01 Construction/search | Finite construction/search, witnesses and joint company conditional outputs | V1, R8 | General implementation correctness requires later conformance |
| P17-08.02 Empty/unknown/certainty | Empty-family, unknown, mixed and certainty semantics remain explicit | V1, R8 | Broader solver behavior is unexecuted |
| P17-08.03 Exact/rounded/integer | Exact/rounded/integer projections, strict endpoints and rational enclosures | B1, R8 | Numerical policies must be explicit; no implicit cent grid |
| P17-08.04 Grouping/state | Query-specific grouping/state distinctions and changed-query refusal | J1, R8 | Wider transition equivalence needs proof or checked conformance |
| P17-08.05 Time/revision | Original/revised clocks and annual comparative/earliest-opening reconstruction | C2, R8 | Actual publication precision, report vintages and wider transition facts |
| P17-08.06 Uncertainty/partial execution | Joint-law attachment, unresolved mass, conditional/interventional and partial results | V1 | Identifiable calibrated laws and causal assumptions are not inferred |
| P17-08.07 Mappings/partitions | Contexts/partitions, state-only allocations and explicit finite subset migration | J1, R6 | General adapter field preservation and cross-profile admission |
| P17-08.08 Continuous forecasting | Frozen future target/vintage/comparator/budget-ladder/veto design for six tasks | V1, L1 | Target-specific tuning/sample budgets require development evidence before empirical promotion |
