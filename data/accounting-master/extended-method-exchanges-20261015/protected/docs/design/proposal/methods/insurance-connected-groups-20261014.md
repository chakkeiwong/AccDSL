# Connected insurance groups and held-reinsurance procedure

14 October 2026; P17-07/P18. Governing plan:
docs/plans/accounting-insurance-connected-groups-20261014.md.
Historical scope: Australian private-sector calendar 2024–2025, general
measurement. Retained AASB 17 F2023C00382, paragraphs 14–28, 32–44, 47–52,
60–68, 78–88, B72 and B119–B125. This is a specification supplement.

## Inputs, ownership and procedure

Each issued group owns its identity, recognition time, contract membership,
claim schedule, current/inception curves, risk adjustment, service units,
CSM, remaining coverage, incurred claims and loss component. Held R separately
owns treaty-entry/recognition/coverage times, covered-contract mapping,
premium/recovery schedules, non-performance adjustment, transferred risk,
cost CSM, remaining coverage, incurred recoveries and loss-recovery component.
Common entity/currency does not merge those groups. All numerical inputs in
group-cases.json are explicit synthetic hypotheses.

1. Resolve portfolio/profitability/cohort admission and earliest recognition.
   Reject cross-group CSM netting; keep unknown membership/timing unresolved.
2. Measure issued claim PV and risk adjustment. Hold unearned gain in CSM;
   recognise net outflow as loss, with CSM zero. Receipt changes cash and
   carrying balance, not service revenue.
3. Measure treaty PV, transferred risk adjustment and base cost separately.
   Evaluate B119C before recognising recovery of the initial underlying loss.
   Eligible recovery increases cost CSM and the asset; its component is within
   that asset. The late treaty is a valid changed-fact history, without recovery
   of the original loss under 66A. Do not erase this alternative as an error.
4. Accrete cash-flow PV at current rates and CSM at inception rates; both are
   10% here. All finance enters profit or loss; all RA release enters service.
5. Allocate B's LC finance and service movements using the declared 3/13 ratio.
   The unchanged fully covered treaty tracks half that component. Reconcile
   components inside group totals; they cannot create duplicate assets/income.
6. Allocate CSM after accretion to current/remaining equal service units.
   B's LC release is loss reversal, excluded from issued revenue. R's asset
   release is split between premium allocation and loss-recovery reversal,
   never deducted from issued revenue. A 66(bb) reversal not already represented
   by FCF is a separate case; do not duplicate the scheduled release here.
7. Recognise gross incurred claims and held recoveries separately, then settle.
   Commit each event's journal and component changes together, bound to group
   versions and replay identity. Do not expose partially committed events.
8. Reconcile group totals/components, journal balances, separate service/finance
   and entity cash/equity at each event. Recheck grouping and treaty timing even
   if terminal cash agrees. Zero remaining coverage does not itself prove zero
   LIC in cases with later settlement; this example settles every claim.

## Exact consequences and adverse cases

The case and calculated-schedules.json preserve every journal and fraction.
Timely R: cash 250, liabilities 120/130, asset 85, equity 85 initially; cash
173, liabilities 65.5/71, asset 46.5, equity 83 at year one; cash/equity 88.3
and no components at year two. Period profit after initial net loss 15 is
-2 and 5.3. Gross and held service/finance remain separately identified.

B's LC moves 30 + 36/13 - 213/13 = 213/13 in year one, then +99/65 -1164/65
to zero in year two. R's component is half at matching dates. R's total
asset 85→46.5→0 includes PV/RA/cost-CSM; it is not valued from the component.

Late R has cost CSM 5 and asset 70, with equity 70→74.75→88.3. Wrong pooling
has equity 100→91.25→88.3. Common terminal cash neither permits wrong pooling
nor authorises original-loss recovery by the late treaty. Ignoring LC finance
exhausts it early; adding the recovery component again overstates equity 15.

## Remaining boundaries

Unknown expected cash flows, RA, discount basis, service units, covered-contract
mapping or non-performance keep measurement unresolved. These supplied case
values fill no actual insurer's unknowns. Partial coverage, new estimates,
guarantees, acquisition-cost/treaty interaction, rate changes and OCI need their
stated extensions. Actuarial validation and human comprehension retain separate
pending status. Missing actual facts do not halt other internal methods.
