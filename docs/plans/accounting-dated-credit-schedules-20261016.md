# B1 — dated effective-interest schedules and earlier write-offs

16 October 2026. MC02/04/05/11/13/15–17/19/21/24–28/30/32–35;
G2/G4/G7/G12/G13/G17/G18. Documentary reference calculations only.
Evidence: data/accounting-master/dated-credit-schedules-20261016/.
Baseline: Version3.32, POCIAnnualTerminal/1, the integral-fee example, and the
existing fixed-rate debt schedules. Runtime, installations and empirical work
remain held.

## Skeptical audit and intent

The question is how dated receipts, integral acquisition costs, revised credit
expectations and earlier full/partial write-offs affect net interest, gross
carrying, allowance and cash. The annual terminal-only oracle is insufficient.
Blindly inserting fractional years into exact rational arithmetic is also
wrong: most annual-rate fractional powers are irrational. Rounded rates must
not be presented as exact roots, and a cash-balanced book must not hide an
incorrect discount convention or delayed write-off.

Use a deliberately declared ACT/365F elapsed-day convention with annual compound
effective rate. This is a supplied contract/model convention, not an IFRS
mandated day-count. Retain exact rational rates and cash amounts; enclose each
fractional-year discount factor by rational bounds proven with integer powers.
The lower/upper endpoints, computation scale and resulting interval widths
remain visible. No binary floating-point approximation is called exact.
Rate r must exceed−1, including zero and negative rates. Rate solving is a
separate bounded monotone PV calculation for positive dated cash flows.
The financial profiles require a certified exact initial PV identity (zero
initial tolerance). A root bracket is not silently rounded to an admitted rate;
propagating rate uncertainty through a general financial schedule remains open.

Two profiles prevent accounting shortcuts. PerformingEIRSchedule/1 covers an
amortised-cost asset with a separately supplied zero-credit-loss assessment,
fees/costs, expected contractual receipts and a B5.4.6 non-credit prepayment
estimate revision. POCIDatedSchedule/1 covers a supplied POCI classification,
original credit-adjusted rate, complete expected credit receipts, successive
cash, revisions and financial write-offs. It never turns a high-risk asset
into POCI merely because a discount fits. General modifications, stage changes,
FX, portfolios and statutory tax remain separate methods.

## Sources and target definitions

Retained EU2023/1803 original IFRS9.5.4.1(a),5.4.4,5.5.13–14;
AppendixA amortised cost/credit-adjusted EIR/EIR definitions;
B5.4.1–4,6–9 and B5.5.44–45. Technical text inspected before this plan.
5.4.4/B5.4.9 requires immediate gross reduction when no reasonable recovery
expectation exists for the identified part; positive remaining receipts do not
permit postponement. Write-off does not assert legal forgiveness. POCI only
recognizes changes in lifetime losses since initial recognition; favorable
changes can give a signed negative allowance.

Let F(s,t)=(1+r)^((t−s).days/365). At a reporting date t, net POCI carrying is
the PV of complete remaining expected receipts at original r. Between events,
accrete G and signed L by F; interest is (G−L)*(F−1). Credit revisions set
L=G−PV(expected) and recognize the change in net carrying as impairment.
Collections reduce gross and cash receivable; expected receipts must match the
known dated cash. Partial financial write-off W reduces G and L equally after
the credit assessment, leaving N unchanged; the supplied unrecoverable portion
must carry no expected cash. A full write-off first recognizes any remaining
net impairment, then removes G and L atomically. Terminal collection clears
G and signed L against the confirmed net receipt without another gain.

While the asset remains recognized, the independent gross identity is initial
carrying compounded to t, minus each actual collection and gross write-off
compounded from its own date, plus non-credit catch-up adjustments compounded
from their own dates. Terminal derecognition additionally removes the residual
signed allowance from gross after cash; it is not another gain or loss.
The independent net identity is direct original-rate PV. Thus neither
implementation recurrence supplies its own sole oracle.

## Authored examples and evidence contract

Primary POCI: acquire on2025-01-01 for98 with integral transaction cost2, net
carrying100, cash/capital300. Contract receipts66 on2026-01-01 and72.6 on
2027-01-01; initial expected55/60.5; original CAEIR10%. Initial expected PV100
and embedded credit shortfall PV20; initial subsequent-change allowance0.
The cash98 and cost2 are separate cash origins.

At2025-07-01 (181 days), f=(11/10)^(181/365). Before revision G=N=100f.
Revise expected receipts to44/48.4: N=80f,L=20f, impairment loss20f.
An admitted20% proportional whole-claim no-recovery finding then writes off
G amount20f and the same L, leaving G=N=80f,L0. Record the removed contractual
receipts13.2/14.52; do not call them another impairment loss.
At2026-01-01 G88, collect44, leaving44. Improve expected terminal recovery to55,
within the surviving contractual58.08: net50, allowance−6, impairment gain6.
Next-year interest5, G48.4, L−6.6, net55. Terminal collection55 closes both.
Final cash is300−98−2+44+55=299; cumulative profit is−1. The exact totals and
all intermediate origins must be independently authored before implementation.

Comparators: no credit revision/write-off; adverse expectations without an
early no-recovery finding; full earlier write-off; zero and valid negative
rates; irregular report dates including a leap-day interval; fee omitted from
rate fitting; positive remaining cash with a required earlier partial write-off.
Preserve prospective conditions and unknown findings explicitly.

Performing comparator: advance102 and receive integral fee2, carrying100;
receipts55/60.5 at the same annual dates give EIR10%. A permitted prepayment
estimate at the July date changes all future receipts to105 on2026-01-01.
New G=(1050/11)f; catch-up=(−50/11)f. Accrete to105, collect and close. Net
cash profit5 equals fee2−advance102+receipt105. A coupon label cannot override
the rate that discounts the full net initial amount and schedule.

Primary criteria: independent PV enclosures contain each authored target;
rate-root brackets have validated endpoint signs and specified width; gross,
allowance, interest, impairment, fee, write-off and cash origins reconcile;
adverse requests return no partial result. Veto source changes, ambiguous
convention, missing cash, future information, inappropriate delayed write-off,
nonpositive discount base, initial PV mismatch beyond the explicit acceptance
interval, and missing numerical bounds. Build/check counts are explanatory.
No statistical superiority, credit forecasting, production-ready solver,
actual issuer classification or current-law claim follows.

## Default/assumption audit and stopping rules

| Choice/provenance | Justification | Failure mode / earliest check | Status |
|---|---|---|---|
| ACT/365F annual compounding, supplied | Explicit irregular-date meaning | Leap-year annual mismatch; actual elapsed-day fixture | Model hypothesis |
| Fraction bounds at declared decimal grid | Integer-powered inequalities prove containment | False exactness or accumulated width; endpoint proof and width report | Engineering choice |
| Positive dated receipts | Makes PV monotone for root bracketing | Multiple roots from sign-changing cash; refuse outside profile | Restricted numerical scope |
| Net acquisition includes integral costs | Source-defined EIR amount | Fee expensed or counted twice; separate cash and PV identity | Source-supported conditional terms |
| Proportional whole-claim financial write-off | Keeps allocation and lost cash explicit | Wrong amount/continued accrual on removed part; no-recovery and direct-origin checks | Finite local method |
| Supplied credit expectations | Isolates accounting from forecasting | Expectations treated as calibrated probabilities; no forecast claim | Conditional input |

The audit already repaired one expectation exceeding the surviving contract and
a cash-sign error in tentative arithmetic. Freeze clean independent expectations
only after the source/formula audit; preserve this explanation. Pre-mortem:
an apparently smooth schedule could be wrong because of day-count, fee or
write-off timing, even if final cash agrees. Boundary/date/origin checks must
detect each. If the enclosures cannot meet their stated width or a write-off
allocation lacks support, do not promote the result; repair or continue an
independent ready unit. Missing actual inputs blocks only their application.

Use existing CPU standard-library Python; no installation. First implement and
check the bounded factor/PV utility and independent authored targets, then the
two profiles. Preserve numbered attempts and actual manifests. Integrate the
completed unit with132 protected Version3.32 sources. Refresh B1 residuals and
I1 service/finance-origin plan before continuing. Human/domain acceptance stays
pending; no global continuation veto has fired.
