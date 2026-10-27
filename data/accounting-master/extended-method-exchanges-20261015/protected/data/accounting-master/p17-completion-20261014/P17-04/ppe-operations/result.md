# PPE replacement, disposal and revaluation — scoped result

14 October 2026. P17-04/P18-01–04; MC02/04/07/11/13–16/19/20/28/30/32–35.
Version **2.78**, **237 pages**, adds exact component replacement/disposal and
asset-specific revaluation cases. The supported pretax calculations pass;
P17-04/E07 and the whole proposal remain **not_ready**.

## Findings and source limits

The first case removes a replaced component's remaining amount 10, recognizes
its eligible replacement 30, depreciates each active component, and disposes
of the remaining asset for 90. Final cash/equity is 160 from opening 200;
lifetime loss and investing outflow are both 40. Retaining the old component
would overstate PPE/equity 10 immediately despite balanced purchase entries.
Ordinary servicing expense is distinguished from an eligible replacement.

The second case revalues the entire two-machine class but preserves individual
surplus and prior-loss histories. Its 2023 opening derivation credits A's OCI
40 and expenses B's decrease 6; the net class increase 34 cannot all be OCI.
In 2024, profit is −37 and OCI −40, giving equity 127. In 2025, profit is −21
and OCI 15; immediate disposal at the admitted values produces no gain.
Direct transfer of surplus 15 to retained earnings leaves final cash/equity
121 and retained earnings −79. Recycling that transfer would overstate profit
15. Direct and indirect operating cash are zero in both comparison years.

The claimed target and actually computed objects agree for these exact
documentary cases: dated journals reconcile to separate component roll-forwards,
profit/OCI, cash, retained earnings and total equity. This does not compute
market fair values, tax consequences, private company facts or a running engine.

Retained AASB116 compilation 6, 31 December 2022, F2023C00192, and AASB107
compilation 5, 31 December 2023, F2024C00050, are separately pinned. The former
has annual-start interval [2023-01-01, 2027-01-01); the latter has
[2024-01-01, 2026-01-01) according to their retained official HTML. Cash-flow
comparisons therefore cover only calendar 2024/2025; the 2023 derivation is
opening asset/equity history. Australian for-profit scope, assumed reliable
valuations, administrative use, zero residuals, even use and separate impairment
assessment are explicit. Tax remains uncomputed. No US/ASBE transfer is made.

## Checks, repairs and decision

`check_ppe.py` passes **214 exact checks**. Complete journals, component states,
valuation histories, statement reports and twelve adverse dispositions are in
`ppe-cases.json`. Some adverse rows document eligibility/source limits rather
than executed predicates; this is not a runtime rejection test suite.

The first arithmetic pass exposed no numerical error, but author review found
that the immediate sale prices differed from the same-date assumed fair values
without supporting facts. The revised example sells at those values. Initial
plan/method/code/calculation/build artifacts are preserved in `initial-model/`;
the final calculation and build apply to the revised case. The first build's
missing section reference was also repaired. Both were local repair triggers,
not evidence against the research direction.

`verify_candidate.py` passes **78 preservation/build checks**. All 63 protected
2.77 source files remain unchanged. The successor changes only its version
and the corporate-methods input and adds one section. Displays increase 72→75,
labels 144→146 and citations 429→432, with none removed. Bibliography bytes are
unchanged; all 66 project build inputs resolve within the successor. The final
build has no recorded diagnostics. Physical pages 1 and 104–109 were inspected
directly; tables, equations and the adjoining Apple section remain readable
without clipping or overlap. Human comprehension and whole-candidate review
remain pending.

| Decision | Primary criterion | Veto diagnostics | Main uncertainty | Next justified action | Not concluded |
|---|---|---|---|---|---|
| Accept these bounded methods/cases | Source-supported operations and independently reconciled journals/state/statements | No remaining arithmetic, source-date, state or presentation mismatch in the stated scope | Actual valuations, legal tax facts and broader lifecycle cases | Retain evidence; continue the impairment-floor allocation method | Full P17-04 completion or accounting compliance |
| Integrate 2.78 provisionally | Exposition connects component/history needs to entries and all affected pretax statements | Preservation, build and seven-page inspection pass | Whole-candidate interactions and human comprehension | P18/P19 assembly after other required methods | Final proposal readiness or human acceptance |

Final PDF: `docs/design/proposal/manuscript-ppe-operations-20261014/accounting-product-proposal.pdf`.
SHA256: `7fb6e19ce905f52071239f2c2000ff389db86f2c8f1172b9d7bce723526bae77`.
The latest full all-53-row assessment remains 2.72; this is a scoped supplement.

## Red-team and continuation

The strongest alternative explanation is that plausible totals hide wrong
eligibility or misclassified value changes. Individual component exits,
per-asset OCI/profit routing, contrary balanced entries and dated source scope
address that risk for these authored facts. A different actual scope, valuation,
consumption pattern or tax result would require recalculation, not automatic
reuse. The weakest evidence is real-input admission and valuation, explicitly
assumed here. No continuation veto fired. Refresh the existing impairment method
and retained IAS36 authority to supply the missing multi-asset allocation when
a floor binds, its unresolved remainder and reversal limits. Other capital-cost,
restoration, tax, sector and full-company obligations remain open.
