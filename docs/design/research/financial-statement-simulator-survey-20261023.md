# Building the financial-statement simulator

23 October 2026. Working synthesis for MC13–18, MC23–26 and MC28–35.
This note executes S1/S2 of the refreshed master. It distinguishes inspected
methods from component candidates and unresolved design questions.

A company simulator needs two kinds of explanation. Accounting determines how
an event affects recognised amounts and statements. Economic assumptions
determine which events occur, when they occur and whether the company can pay.
The methods reviewed here contribute different parts of that problem. Their
names and numerical outputs cannot be imported without checking their meaning.

## Comparison of retained methods

| Method and source | State, timing and behaviour | Contribution to AccDSL | Limits and next check |
|---|---|---|---|
| Corporate microsimulation: Shahnazarian (2004), §§2.3–2.8, selected Ch.3, §8.3 and Appendix B | Financial stocks evolve through accounting bridges; separate behavioural/optimisation relationships determine decisions. The model is developed for incorporated businesses and the source's Swedish tax-data setting. | Keep stock movements and decision rules explicit; distinguish economic from tax depreciation and tax-related reserves. Eq. (2.28), for example, separates machinery investment, disposal and economic depreciation. | The retained source review is targeted, not replication. Its data, tax law and estimated relationships do not supply modern issuer disclosures or transferable behavioural parameters. |
| Accounting/system dynamics: Pierson (2020), §§3–4 and author supplement | Cash, receivables, payables, inventory and equity are stocks; accrual and payment flows differ. Period accumulators feed held reported values. Payment of payables uses a first-order delay in the supplied model. | Require separate event dates and reporting periods; test accrual-to-cash bridges and period-end reporting. | The paper omits OCI; its financing, inventory and payment assumptions are a model scope. Reporting code expresses some annualised rates, which must be converted to amounts before comparison with statement flows. |
| Bank asset/liability optimisation: Halaj (2016), ECB WP 1896, §§3.2–3.7, §4 and §5 | Portfolio choices respond to uncertain funding, credit and securities returns under liquidity and capital constraints. | Treat funding availability and liquidity feasibility as inputs to decisions, not an automatic balancing liability. | Bank-specific objective and distributional assumptions are not company defaults. The inspected working-paper version is not asserted identical to the journal version; no numerical replication or code adoption. |
| Bank behaviour: Behn, Daminato and Salleo (2019), ECB WP 2233, §2 and §3 | Loans, deposits, wholesale funding and equity evolve under jointly binding capital/liquidity constraints; structural parameters are estimated in two steps. | A policy interface must receive the state and constraints jointly; accounting and prudential measurements must remain distinguishable. | §3 uses granular SSM supervisory data and a model-specific liquidity proxy. Public issuer data do not automatically identify those parameters or reproduce the model's regulatory ratios. |
| Agent-based/stock-flow consistency: Caiani et al. (2016), newly recovered journal paper, §§2–5 and Appendices A/B (selected passages) | Agents hold heterogeneous loans and capital vintages. An 18-step within-period event sequence links production, credit, payments, taxes and dividends; counterparties share financial claims. | Preserve contract/vintage state, causal event ordering and counterparty consistency. Separate accounting validation from behaviour/calibration. | The steady-state, initially homogeneous artificial economy is not an observed company opening state. The source's OCF subtracts principal repayments; it cannot be silently mapped to AccDSL's statement operating cash flow. Official code inspection is recorded below. |
| Contract events: retained ACTUS technical specification | Contract schedules, state transitions and payoffs are a candidate financial-instrument component. | A contract component can propose dated contractual events with explicit terms and risk inputs. | Contract payoffs alone do not select recognition, accounting measurement, operating behaviour, consolidation or statement mappings. Verify retained technical sections and actual implementation before selecting a runtime. |
| Strategic financial planning: Gentry (1974 working paper; 1979 journal version not inspected) | Management specifies EPS growth, investment growth, debt/assets, P/E and debt-cost inputs; annual balance-sheet and income variables feed required investment returns. Dividend and debt-limit decisions affect financing. | Separate management objectives, imposed investment choices and financing responses; compare an aggregate planning interface with event-level simulation. | The paper assumes independently sampled managerial distributions and an EPS objective. Neither becomes an AccDSL default. The appendix derivation is referenced but is absent from the visually inspected trailing pages of the retained scan; edition correspondence remains unchecked. No executable implementation adopted. |
| Simultaneous-equation alternative: Francis and Rowell (1978) | Publication identity verified; methods still unavailable from attempted publisher/author routes. | Preserve this concrete comparator before declaring the survey complete or ruling out an equation-model alternative. | DOI `10.2307/3664904`; Wiley and ResearchGate returned HTTP 403 on 23 October. No technical claims from abstracts or metadata. |

## A newly resolved source gap: Caiani et al.

The 13 October retrieval failed and identified a wrong arXiv reference. A new
university-hosted copy was retrieved on 23 October and verified by the title,
six authors, journal pagination 375–408, DOI and 34 PDF pages. The old failure
record remains correct about its attempts; it no longer establishes present
unavailability.

- Source: `https://faculty.sites.iastate.edu/tesfatsi/archive/tesfatsi/ABMSFCMacroModelBenchmark.CainiEtAl2016.pdf`.
- Local PDF: `docs/papers/Agent based-stock flow consistent macroeconomics Towards a benchmark model Caiani (2016).pdf`.
- SHA-256: `8575b73c39650d2ebf189034595d2c09f29e352aafa20d97118a3788914cd050`.
- Extraction: `docs/design/research/text/caiani2016-recovered-20261023.txt`.
- Prior route history: `data/accounting-master/caiani-source-recovery-20261013/result.md`.

The useful result for this design is the separation between transactions,
behaviour and accounting checks. Section 2 describes the matching transfers
between agents; §2.1 fixes the order of events. Section 3.1.3 distinguishes
profit from its cash/debt-service measure. Section 4 and Appendix A construct
consistent initial stocks under steady-state assumptions. Section 5.2 checks
the transaction matrices and aggregate balance sheet before comparing simulated
series with empirical regularities. This makes accounting consistency a
necessary diagnostic without treating it as evidence of predictive accuracy.

The source defines OCF as after-tax profit plus depreciation, less inventory
changes and loan principal repayments (§3.1.3, journal p.384/PDF p.10). Its use
in credit demand and credit assessment is consequently a debt-service concept.
AccDSL must represent that formula under its own concept identifier and require
an explicit bridge to a statement cash-flow classification. Matching the label
“operating cash flow” is insufficient. This is a source-to-target mismatch,
not a claim that the authors computed their own definition incorrectly.

The baseline's 100 simulations of 400 periods and the sensitivity repetitions
are author-reported evidence (§5), not experiments performed here. They do not
establish issuer-level forecasting or AccDSL runtime validity.

## Source paths and inspected code

Existing primary texts are retained under `docs/papers/` and extracted in
`docs/design/research/text/{shahnazarian2004,pierson2020,halaj2016,behn2019}.txt`.
Their earlier selected-section reading limits remain in
`docs/design/research/source-support.json`. New technical checks in this note
extend particular anchors; they do not turn those sources into fully replicated
models.

Pierson's retained author model is
`docs/design/research/software/pierson-accounting-model.mdl`. Directly inspected
equations include `BS Cash`, `BS Accounts Receivable`, `BS Accounts Payable`,
`Payment of Accounts Payable`, `Accumulated Reported Revenue`,
`Drained Reported Revenue`, `Reported Revenue` and `Check Reporting`. The
payables stock integrates purchases on credit less payments; the payment rule
divides that stock by average credit terms. The reporting accumulator is drained
at the reporting boundary and converted using `TIME STEP/Reporting Period`.
These are inspectable model assumptions, not a universal invoice schedule.

Caiani's paper links `S120/jmab` and `S120/benchmark`. Selected benchmark files
are retained at `docs/design/research/software/caiani-benchmark-20261023/`,
pinned to commit `3bccc645bb99ba7835d9a0040313e6715bc3e722`. Static inspection
of `ConsumptionFirm.java` covers the event switch, `computeDebtPayments`,
`computeCreditDemand`, `updateAfterTaxProfits` and `payInterests`. Lines 584–589
subtract scheduled principal from the reported internal cash-flow measure.
Lines 643–690 collect liquidity, pay scheduled debt when sufficient and invoke
bankruptcy otherwise. `FirmBankruptcyFireSales.java` was inspected only for
its opening liquidation/liquidity and creditor-allocation structure, not for
complete correctness. This is a retrieved repository revision, not a verified
paper-era executable. No downloaded code has been run or installed.

The code is useful evidence about decomposition, not ready-made AccDSL
accounting. It mutates deposits, loans and counterpart balances directly;
AccDSL requires the corresponding proposed event, independent economic change,
accounting basis and journal. The fixed-payment loan formula also divides by
`(1+iRate)^length-1`; zero-rate handling and schedule domains would need a
targeted boundary check before reuse. This is a static local observation, not
an executed defect claim about the whole JMAB program.

## Financial planning as an alternative

Gentry's University of Illinois working paper 180, dated 10 May 1974, is now
retained as `docs/papers/Simulating the Strategic Financial Planning Process
Gentry (1974 working paper).pdf` (52 scanned PDF pages; SHA-256
`f769c5dff5f53f61b511b898e3f9fec1b767b61edbb401889aa8e79b333122d6`).
It was retrieved from
`https://archive.org/download/simulatingstrate180gent/simulatingstrate180gent.pdf`;
the university contributed the scan. The title and author match the later
journal lead, but version equivalence has not been established. The 1979
journal DOI is `10.1016/0377-2217(79)90027-4`.

Inspected printed pp.1–9 and 12–13 explain its managerial objective, five main
inputs, dividend and financing adjustments, eight-year simulation and example
interpretation. Figure 1 (printed p.8/PDF p.29) was also inspected visually
because the extraction is poor. It asks what return new investments must earn
to attain an imposed EPS growth goal. That is an inverse planning question;
it does not supply a general rule predicting customer demand or payment dates.
Printed p.3 assumes the sampled variables operate independently within chosen
limits. AccDSL should allow such a model only as an explicit assumption with
its own joint-law justification.

The working paper references an appendix derivation. Visual inspection confirms
references at printed p.17/PDF p.45, followed by blank reverse pages, endpapers
and the back cover on PDF pp.46–52. No appendix was found in those pages; zero
extracted text was not treated as sufficient evidence. Figure2, its
interpretation, TableI and footnotes were inspected at PDF pp.33,35,41,43. This
supports the planning structure, not a checked reconstruction of the ROI
equation. The missing derivation and uninspected 1979 version remain gaps.
Images and hashes are retained in planning-source-continuation-20261023/review.json.

Exact DOI metadata for Francis and Rowell was retained. Crossref gives
publisher routes; OpenAlex gives the DOI location without an accessible PDF
location. An unverified ResearchGate request returned403; its response is
retained as HTML, not a paper. These records establish neither global
unavailability nor a technical conclusion about the model.

## Immediate design consequences

The initial design should keep dated economic state, behavioural decisions,
contract events, accounting transitions and statement aggregation separable.
This is a provisional architectural recommendation from the inspected
mechanisms and the mission, not a final library selection. The same typed IR
must be the comparator for textual DSL and typed-library authoring.

The next concrete work is to finish the bounded official-code check, resolve
the consequential planning-model comparison, and map each proposed simulator
interface onto existing portable records. New records are justified only where
an included operation cannot be expressed with the current design.

## ACTUS interface follow-on — 23 October 2026

The retained technical specification now has a targeted interface comparison
at actus-interface-boundary-20261023.md, with source hashes and inspected line
ranges in its JSON companion. Event/payoff/state separation supports a contract
component, but timezone handling, midnight interpretation, event ordering,
day-count/calendar and risk observation require explicit adapter conventions.
The borrower PAM formulas admit the local bridge-loan cash flows under stated
simplifications; this is an algebraic mapping, not runtime conformance. A
pinned accessible implementation and its dictionary/version correspondence
remain required before adopting a library. No new dependency was selected.

The follow-on now also inspects four exact service-code blobs. The service
requests core 1.1.0 but does not supply a resolved binary lock; its wall-clock
horizon fallback, carry-forward risk observer and double-valued event output
require explicit adapter handling. Tree/blob identities and retained bytes are
recorded. The underlying core and dictionary correspondence remain open; no
external code was executed or selected as a dependency.
