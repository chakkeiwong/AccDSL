# Connected insurance groups — scoped result

14 October 2026. Version 2.83, 249 pages, provisional and not_ready.
PDF: docs/design/proposal/manuscript-insurance-connected-groups-20261014/accounting-product-proposal.pdf
SHA256: 2fe73c20217962911bc8454ba391f2131296dbc3d07a00f4e91e1514248b98dd
Plan: docs/plans/accounting-insurance-connected-groups-20261014.md.

## Result and evidence

Two separately classified issued groups and a held treaty now share a complete
two-year documentary roll-forward. The timely treaty yields equity 85 at
recognition, 83 at year one and 88.3 at expiry. The late prospective treaty
instead gives 70, 74.75 and 88.3. Invalid pooling gives 100, 91.25 and 88.3.
Terminal cash therefore cannot establish correct group/timing recognition.
Gross liabilities, reinsurance assets, loss components, CSMs, service, finance,
incurred claims/recoveries and cash are reconciled separately at each event.

All 248 exact checks pass, including intermediate balances and wrong-treatment
contrasts. All 83 preservation/build checks pass. The 68 protected source files
remain unchanged in 2.82; the successor changes exactly three and adds one.
Displays 84→85, labels 152→153 and citations 440→445 preserve every prior
occurrence; bibliography is unchanged. All 71 project build inputs reside in
the successor. Build diagnostics are empty. Seven pages were visually inspected;
after repairing a forward reference, the changed page 177 was re-inspected and
the other six were carried by exact PNG equality. Human feedback remains pending.
The stale bank-rule absence claim is repaired only in this successor.

## Decision and interpretation

| Decision | Primary criterion | Veto diagnostic status | Main uncertainty | Next action | Not concluded |
|---|---|---|---|---|---|
| Accept bounded historical design supplement | Exact group, journal and statement reconciliation plus supported grouping/timing | No source-scope, calculation, preservation or rendering veto fires | RA, rate, expectations and cover/collectability are admitted synthetic inputs | Refresh/audit P17-08 using the newly delivered group interactions | Full P17-07/E07 closure, actual insurer valuation, runtime, calibration or human acceptance |

The claimed target and computed quantity are the same conditional consequences
of the supplied group and treaty measurements. They are not an estimate of an
actual insurer. No stochastic ranking is attempted; the checker is exact
fraction arithmetic. Counts and successful builds are integrity diagnostics.

## Post-run skeptical review

The strongest alternative explanation for apparently correct totals is
compensating errors in loss-component presentation. Independent group totals,
component ratios, separate finance/service, timely/late scenarios and invalid
pooling expose those errors before expiry. The weakest evidence is the supplied
actuarial/market input: calculation does not validate it. Actual contract mapping,
rate/RA support, non-performance or partial coverage could overturn admission
of this example to an insurer and would require new measurement, not a plug.

The constant proportional allocation is a specified method for unchanged facts,
not a universal unique formula. Reinsurance loss-recovery is within the complete
asset. No duplicated CSM reversal is inferred for scheduled releases already
represented by FCF; other 66(bb) changes need a separate case.

No continuation veto fired. The current candidate remains not_ready, and P17-07
retains actual-group facts, priced guarantee, acquisition/treaty interaction and
actuarial protocol obligations. Continue P17-08 cross-cutting contract audit;
P17-09/10 and eventual P17-11/P18/P19 assembly remain separately required.
