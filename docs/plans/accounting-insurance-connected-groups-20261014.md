# P17-07/P18 — Connected issued groups and held reinsurance

14 October 2026. MC02/04/05/07/11/13–16/18–22/25/28/30/32–35;
E07, G4/G6/G7/G12/G15/G16. Protected baseline: Version 2.82, 246 pages,
SHA256 `411072801fa21a0e360f9e0cdbc3f0c6f116663e40069c464d97930189bb54c5`.
Evidence: `data/accounting-master/p17-completion-20261014/P17-07/connected-groups/`.
Successor: `docs/design/proposal/manuscript-insurance-connected-groups-20261014/`.

## Refresh and skeptical audit

The chapter already specifies two-year GMM, nonzero finance, onerous allocation,
PAA/LIC, VFA guarantee components, acquisition-asset recognition, actual Munich Re
movements and transition/reinsurance components. Do not call these absent. The
remaining bounded interaction is one balance sheet containing a profitable
issued group, an onerous issued group and held reinsurance through nonzero
finance, service, incurred claims and final settlement. Retained original
AASB 17 compilation F2023C00382 supports Australian private-sector calendar
2024 and 2025 periods; no current cross-jurisdiction claim follows.

Read 14–28, 32–44, 47–52, 60–68, 78–88, B72, B119–B125. Especially:
LC finance must be allocated under 51(c); reinsurance recovery components
track underlying losses under B119F and are not extra assets; 66(bb) treats
reversals not represented by FCF changes; B119C's timing requirement must not
be replaced with C20A's exceptional transition treatment. Separate groups
under 16/22/24 may share estimators but cannot share a CSM merely to suppress
losses. Final cash equality alone cannot validate intermediate components.

Audit rejects a zero-finance-only extension as insufficient for the selected
connected question. Use the already explained flat 10% example for profitable
group A, and the same currency/rate dates for onerous group B and its treaty.
The rate is an authored hypothesis, not a market quote. Use explicit current
and locked-in rates with no rate changes, all finance through profit or loss,
and a separately supplied service-only RA schedule. No actual valuation or
calibration is inferred. Neither component cap alone nor a quota alone values
the treaty. Derive its entire remaining-coverage asset and its CSM.

## Research intent and evidence contract

Question: do separate issued/held groups preserve recognition, financing,
service and cash consequences, including when terminal cash is identical?
Comparator: inspected dated AASB 17 requirements plus exact component and
journal derivations; wrong pooling and a genuinely late treaty are distinct
comparators (invalid treatment versus valid changed facts).
Primary pass criterion: all group FCF/CSM/LC/LRC/LIC and reinsurance FCF/CSM/
loss-recovery/remaining-coverage/incurred-recovery movements reconcile to
each event's journals, all three statements and the terminal cash identity.
Promotion vetoes: source/date mismatch, unsupported grouping/timing, missing
measurements, doubled components, inconsistent finance, nonzero expiry
components, wrong profit/statement presentation, broken baseline preservation.
Continuation veto: invalid case/source/harness that cannot yet be repaired;
stop the affected assertion, continue independent work. A failed wrong-treatment
arm is expected evidence, not a continuation veto. Arithmetic/check counts and
rendering diagnose integrity only. No calibrated valuation, stochastic ranking,
prudential readiness, engine conformance or completed insurance module follows.
Preserve case JSON, exact checker, source pages/hash, method, PDF/render, result
decision table and run manifest under the evidence path.

## Final admitted case and default audit

Opening cash/equity 100. All amounts use the same currency; no other assets,
taxes, acquisition costs, investment components, FX, lapses or rate changes.
On 1 January 2024 two separately classified nonparticipating groups enter
two-year coverage; no earlier recognition triggers or later additions. Each
contains same-year contracts; A is profitable, B onerous, with no paragraph 20
pricing-law exception. Expected and realised claims coincide only on this
authored path. Both have two equal service units and independently supplied
RA 10 released 5 per year, entirely in service result under 81.

A: premium 120; claims 44 after year one and 48.4 after year two; claim PV 80;
initial CSM 30. B: premium 100; claims 66 and 72.6; claim PV 120; initial CSM 0,
loss 30 and LRC after premium 130. Systematic LC allocation ratio is 30/130,
applied to expected-claim releases, RA service release and finance. It remains
constant in this no-revision case and produces zero at expiry. This is a
specified admissible allocation, not a unique universal regulatory formula.

R: treaty entered at/before B recognition; covers only all B claims at 50%,
with no caps, exclusions, delays, commissions or expected non-performance.
Independent transferred-risk measurement is 5, released 2.5 per year. The
chosen value equals half B's RA as an admitted case fact, not a general rule.
Premium 70 is paid at inception. Recovery PV 60 plus RA 5 and base cost CSM 5
would give asset 70 after payment. Eligible initial loss recovery 15 adjusts
CSM to 20 and asset to 85; loss-recovery component 15 is already within 85.
It tracks half B's loss component while cover and collectability stay fixed.
Finance and service allocations move this component inside the asset rather
than adding another asset. No separate 66(bb) CSM reversal is assumed when
the relevant reversal is already represented by the scheduled FCF release.

CSMs accrete at 10% before allocation across current/remaining equal units.
Expected claim/recovery PV accretes at the same 10%; RA changes are service.
Each year: finance, service/claim incurrence, claim/recovery settlement. Cash
is uninvested. Gross and held-reinsurance portfolios and results stay separate.

| Choice / provenance | Status and justification | Failure mode | Earliest diagnostic |
|---|---|---|---|
| A's existing nonzero case | Protected illustrative baseline | Wrong baseline silently changed | Reproduce A balances and profit independently |
| B claim timing and rate | Authored hypothesis isolating grouping and loss allocation | Artificial rate differences confuse comparison | Same dates/currency/current/locked rates as A/R |
| RA and expected cash schedules | Supplied conditional measurements, not calibrated defaults | Claiming actuarial derivation from arithmetic | Explicit measurement references and non-claims; RA service split |
| 30/130 LC allocation | Proposed systematic no-revision method | Ignore finance or double-count loss in revenue | Component ratio before/after every event, zero at expiry |
| R's coverage, collectability and RA | Synthetic admissions | Multiplying a nominal quota into a full asset | Independent premium/PV/RA/CSM computation; cap/exposure checks |
| Equal coverage units | Explicit benefits/duration assumption | Cash-based service allocation | CSM release uses remaining/current service units |
| Late treaty alternative | Different legal ordering, no elapsed finance/service | Import transition timing exception | No initial 66A recovery or component; preserve original loss |

Audit passes for this bounded historical case. Its strongest failure risk is
confusing component movements with extra recognition. Derive independent total
asset/liability and income reconciliations before writing reader conclusions.

## Execution and continuation

1. Retain inspected source passages; finish formula/presentation audit.
2. Write exact case/journal/component checker, including wrong grouping, late
   treaty and doubled-component/finance-allocation failure comparisons.
3. Draft the connected explanation in the chapter; preserve all prior equations
   and evidence. Repair the stale bank-rule claim in this successor only.
4. Build with `scripts/accounting_document_tools.py build`, render affected
   pages, inspect images and verify exact PDF/baseline/index preservation.
5. Record result and refresh six live controls. Continue the next ready P17
   unit after auditing its actual residuals. P17-07 remains open for rich
   actual-group facts, priced guarantees and actuarial validation design.

Use the linear scholarly narrative skill: readers know bookkeeping and basic
probability, not these component interactions. Teach why pooling fails, then
walk the same insurer through the years; sidecars hold exhaustive schedules.
Human comprehension remains pending while provisional drafting continues.
