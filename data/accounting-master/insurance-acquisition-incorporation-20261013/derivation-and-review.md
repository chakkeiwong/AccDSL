# Acquisition-asset incorporation — derivation and source review

13 October 2026. Audited plan:
`docs/plans/accounting-insurance-acquisition-incorporation-20261013.md`.
MC08/10/11/13/16/19/22/28/30/32–35; G4/G6/G7/G15/G16; E07/P17/P18.
Historical source SHA256:
`153e720cc1eaf7eea47d50463003391ea0433271694dd83a44c54a0e92deaec3`.
The compilation applies to annual periods beginning 1 January 2023 to before
1 July 2026. No current edition or actual insurer interpretation follows.

## Source support

Five selected text pages and images were inspected: 9 (recognition), 12
(initial CSM including derecognised acquisition assets), 20 (service revenue),
53 (premium receipt exclusion and B123A exception) and 54 (acquisition revenue/
expense allocation). Page9's paragraph26 continues on page10, already inspected
in the prior acquisition unit. Carried same-source support:28C–28F and28 from
that page10;32–35 from11;B35B–B35D from38;47 from the earlier transition
unit's14. The carried extracts and original source hashes are bound in checks.

| Anchor | Requirement | Application |
| --- | --- | --- |
| 25–28, pp. 9–10 | Earliest coverage/premium-due/onerous trigger; admit only qualifying contracts | Recognition at shared coverage start and premium due, no earlier trigger; all contracts admitted together |
| 28C–28D, B35C, pp. 10/38 | Derecognise related acquisition assets when included in group measurement | Transfer the remaining carrying assets once; no stale separate balance |
| 32, 38(a)–(c)(i), pp. 11–12 | FCF plus CSM; initial CSM prevents income/expense including acquisition-asset derecognition, subject to exceptions | Under stated positive-margin facts derive C=−F−A, L=−A before premium receipt |
| 47, p. 14; B123A, p. 53 | Onerous and other-cash-flow-asset exceptions | No onerous excess, no other pre-recognised cash-flow assets; do not universalise no-income statement |
| 40–41, p. 12; 83–85, p. 20 | Remaining coverage components and service-based revenue | No service at the instant of receipt, so no service release |
| B123(a)(i), p. 53 | Premium-cash changes excluded from revenue-producing liability reductions | Receipt exchanges a group cash-flow balance for cash, not immediate revenue |
| B125, p. 54 | Acquisition recovery revenue allocated over time with equal service expense | No elapsed service/time means no such allocation in this instantaneous bridge |

## Conditional derivation

Carry Version2.56's post-reversal acquisition assets35/15, cash40 and equity90.
There are no other assets or liabilities in this slice. Suppose coverage and
the first premium due date now begin for both correctly admitted groups,
without an earlier recognition trigger. All contemplated contracts are added
together. No service has elapsed, no claims are incurred, and no other cost,
asset, cash, tax, reinsurance or assumption movement occurs between the shown
instants. Use general measurement and preserve the prior group net inflows45/30.

Supply additional conditional measurement inputs consistent with those net
amounts: premium100/60 due immediately, present-value future claims/expenses50/25,
and nonfinancial risk adjustment5/5. Premium is received immediately after the
initial group measurement. Thus F1=50+5−100=−45 and F2=25+5−60=−30.
The present-value inputs do not imply zero discounting; their valuation remains
an external input. Previously paid acquisition costs are not paid again.

Let A be the remaining acquisition-asset carrying amount and take positive L
as liability. Derecognising A removes an asset. To avoid income/expense under
38 in this nononerous case, the group's new net asset must replace A, so
L=F+C=−A and C=−F−A. G1 C=45−35=10, L=−35; G2 C=30−15=15, L=−15.
Both CSMs are positive, so47's exception is not triggered. No other prepaid
cash-flow assets trigger B123A. Do not call L=−35 a negative CSM: C is10.

Illustrative recognition entry: debit group assets35/15; credit acquisition
assets35/15. Cash stays40, acquisition assets become0, group assets total50,
equity stays90. This transfers the *carrying* assets after impairment/reversal,
not the original costs40/20; history remains traceable separately.

Premium entry: debit cash160; credit group carrying balances100/60. FCF becomes
55/30 because the premium is no longer a future inflow. CSM stays10/15 and
the groups now carry liabilities65/45, total110. Cash200−liabilities110=equity90.
This distinguishes cash, FCF, CSM and revenue; no revenue or expense arises in
these two instants. Later service has its own CSM/RA/acquisition allocation.

Rejected paths: ignoring the derecognised assets gives CSM45/30 rather than
10/15, overstating total CSM by50. Retaining separate acquisition assets after
the correct transfer overstates assets/equity by50. Combining both mistakes
can still balance cash200+acquisition50−liability160=equity90; the balance-sheet
identity alone cannot detect incorrect CSM, asset and group measurement.
Boundary A=0 gives C=−F, initial group net balance0 and no asset transfer.
The general rule must still handle onerous groups and other exceptions, which
are outside this positive-margin bridge.

## Skeptical audit and reader reconstruction

The source-derived bridge is supported within its assumptions. It preserves
the prior net inflows and carrying assets, checks the two exceptions, and
separates valuation inputs from postprocessing. No financial performance or
accounting-compliance claim follows from the exact checks. Changed grouping,
recognition facts, expenses or valuation assumptions require recomputation.

Reader already understands the preceding impairment/reversal example.
Start from its actual ending balances, introduce why the paid cost affects
CSM at recognition, derive the replacement asset, then show premium receipt
and the invariant equity. Use a small three-stage balance table to compare
states after the prose has explained each transition. Close with the balanced
but wrong counterexample and the zero-cost boundary. Preserve all previous
prose/math/citations; human comprehension and domain acceptance remain pending.
