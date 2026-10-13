# Reinsurance transition component — source and derivation

13 October 2026. Plan: `docs/plans/accounting-reinsurance-transition-recovery-20261013.md`.
MC08/10/11/13/16/19/22/28/30/32–35; G4/G6/G7/G15/G16; E07/P17/P18.
Source: retained AASB17 compilation 4 (31 December 2022), SHA256
`153e720cc1eaf7eea47d50463003391ea0433271694dd83a44c54a0e92deaec3`.
The source's annual-period applicability is 1 January 2023 to before
1 July 2026. No current operative edition or ASBE equivalence is established.

## Inspected support

Selected passages: 60–70A, 75, 78–79, B119C–B119F and C20A. Text from pages
16–19, 52–53 and 61 was read; page 1's edition statement carries forward the
immediately preceding source inspection. Six images were visually inspected:
16 (recognition and FCF/RA), 17 (CSM/loss recovery), 19 (issued/held presentation),
52 (timing and allocation), 53 (subsequent cap) and 61 (transition exception).
The page 16→17 continuation of paragraph 65 was read in the images; no term
is inferred solely from the incomplete first-page extract.

| Anchor | Source requirement | Local use and limit |
| --- | --- | --- |
| 61–62A, p. 16 | Separate grouping and recognition rules, including proportionate-cover timing | Assume properly recognised treaty and group; C20A is no general recognition waiver |
| 63–64, p. 16 | Consistent underlying assumptions where applicable, issuer nonperformance including collateral/disputes, and risk transferred | Expected recovery is a supported input, not automatically the stated quota |
| 65–66B, pp. 16–17 | Held-reinsurance CSM reflects net cost/gain; loss recovery has a distinct component and allocation function | Do not import issued-group unearned-profit/onerous treatment or infer full CSM from the component |
| 68, p. 17 | Held reinsurance cannot be onerous; 47–52 do not apply to it | The underlying group's loss component is not a held-reinsurance loss component |
| 69–70A, pp. 17–18 | Separate PAA eligibility and carrying-amount adjustment | Example uses general measurement; no PAA result inferred |
| 75, 78–79, p. 19 | Reinsurance purchase does not extinguish the underlying obligation; separate issued/held asset/liability portfolios | Gross issued liability remains; component is not a policyholder offset |
| B119C–B119D, p. 52 | Ordinary 66A timing restriction and loss-times-expected-recovery calculation | Distinguish ordinary income recognition from C20A transition component |
| B119E, p. 52 | Systematic rational allocation where some underlying contracts are not covered | Example assumes all B contracts covered; mixed populations require their own allocation |
| B119F, p. 53 | Component changes with underlying loss component, capped by the expected recoverable portion | A later cap is a bound, not a full-asset remeasurement or standalone P&L entry |
| C20A, p. 61 | Transition component = underlying transition loss component × expected recovery percentage, without B119C condition | Derive R=Kq; all other applicable conditions remain |

## Authored case and evidence contract

Retain Version 2.54's group B: issued liability 120, embedded loss component
K=20. Change the earlier no-reinsurance assumption explicitly: a separately
recognised, qualifying held-reinsurance group now covers all B contracts and
only B, with remaining coverage, no incurred claims, and general measurement.
Take expected claims recovery q=3/5 as an authored conditional input that
already reflects the relevant coverage/collectability assessment. It is not
a treaty fact, inferred premium ratio or estimated quota. C20A gives R=12.
The issued liability stays 120 and its own loss component stays 20.

Illustrative timing: underlying contracts recognised 1 July 2020; treaty
entered 1 October 2020; both relevant coverages still in force at transition
1 January 2022. Ordinary B119C would not support 66A recovery income at the
original underlying recognition. C20A expressly removes that condition for
the transition component. The dates do not prove the other conditions: assume
them supported in the example and retain them as actual-case dependencies.

R=12 does not determine the full asset or transition equity. To illustrate the
additional input needed, separately *assume* that a complete supported
remeasurement would give a remaining-coverage asset of 50, already including
R=12, replacing an old reinsurance asset of 45. This unit does not derive or
validate that 50 from treaty cash flows. The bridge is conditional on it.
With other assets 500 and the earlier issued liabilities 220→230, assets are
545→550 and equity 325→320. The reinsurance asset increase contributes +5 to
equity against the issued-liability contribution −10. Illustrative reinsurance
entry: debit new asset 50, credit old asset 45 and opening equity 5. Do not add
R=12 again: that would create assets 562 and equity 332, overstated by 12.
This bridge uses C4(b)–(c), inspected and retained in the preceding unit; it
does not import ordinary 66A income into transition profit.

Boundary q=0 gives R=0 and q=1 gives R=20. Neither removes the policyholder
obligation or establishes the whole asset. For a separate later diagnostic,
if the underlying loss component is 14 and the recoverable portion remains
60%, B119F gives an upper bound of 8.4. Leaving R at 12 violates that bound.
The bound does not determine a unique new component or the total asset, cash,
CSM or P&L movement; those need the actual changes and applicable allocation.

## Skeptical verdict and teaching plan

The scoped derivation passes. Claims computed: R=12; conditional equity
325→320 given the additional full-asset inputs; later R≤8.4 under stated facts.
Do not substitute any one of these targets for another. The most vulnerable
inputs are expected recovery, group matching and the independent asset values.
They remain authored assumptions, not defaults or evidence about a treaty.
An uncovered subgroup, a different source edition or inconsistent recovery
definition vetoes the corresponding calculation and triggers a source/model
repair. It does not reject the research direction. No empirical/stochastic
comparison is made.

Reader: the finance/software reader who has just followed group B's loss
component and opening equity. Open with the remaining economic question: how
much of that loss is recoverable? Establish eligibility/timing, derive R,
separate component from full asset, then extend the balance sheet and test the
later cap. Explain the added full-asset assumption before its arithmetic.
Use one equation for the component; prose carries the conditional balance
sheet and cap so they cannot be mistaken for one universal valuation formula.
The actual Munich Re disclosure follows. Preserve all existing equations,
citations and case qualifications. Human/domain acceptance remains pending.
