# Pricing the guarantee and retaining separate insurance groups

15 October 2026. Historical AU for-profit calendar2024/25 illustration under
retained AASB17 F2023C00382. The plan is
docs/plans/accounting-insurance-priced-guarantee-20261015.md.

## A financial price with an explicit market

Let a traded, non-dividend-paying underlying cost S0=100. At the next financial
observation it is Su=120 or Sd=80, then remains at that value until settlement.
The cash account has accumulation R=1. Trading is frictionless with borrowing
and shorting, no counterparty failure, and exactly these two financial states.
The observation precedes the provision of any coverage unit in this discrete
example; the service period and mortality outcome follow. Real elapsed service,
different dates, additional states or trading restrictions require a new model.

For any two payoffs Xu,Xd, a holding delta in the underlying and b in cash
satisfies delta Su+bR=Xu and delta Sd+bR=Xd. Subtraction gives
delta=(Xu-Xd)/(Su-Sd), b=(Su Xd-Sd Xu)/((Su-Sd)R).
The current price is delta S0+b. Equivalently it is
[q Xu+(1-q)Xd]/R, where q=(R S0-Sd)/(Su-Sd).
Positive state prices require Sd<R S0<Su, with R>0 and Su>Sd.
The example gives q=1/2. This is a project derivation of replication in the
specified market; AASB17.B44–48 supports using a matching replicating portfolio
for the relevant fulfilment cash flows, not the choice of the toy market.

The contract returns max(0.9 S,90) at settlement, plus an insured mortality
benefit20 if D=1. The return can be written 0.9 S+(90-0.9 S)+.
The top-up pays0 in the up state and18 in the down state. Its replicating
portfolio is -0.45 units plus54 cash, costing9. The whole investment benefit
is replicated by0.45 units plus54 cash, costing99. Both state equations must
hold; a single expected value does not establish replication.

For forecasting only, assume P(up)=3/4 and P(D=1)=1/10 independently.
The four physical weights are27/40,3/40,9/40,1/40 for up/alive,
up/death,down/alive,down/death. The physical expected top-up is4.5,
which differs from its market-consistent price9. Mortality has expected
cost2 under the supplied physical law; it is not traded in this market.
RA1 is separately supplied compensation for that nonfinancial risk under.37,
with its entire release in service under.81. Neither1 nor the mortality law
is an actuarial calibration. Unknown dependence invalidates the product weights.

## Recognition and all four conditional statements

Assume the significant-insurance-risk, component-separation and VFA admission
findings have been supplied under.3/.10–13 and B17–23/B31–32/B101–108.
The illustrative rights are mutually terminating: the policyholder cannot
retain either component after the other matures, supporting the specified
B32(b) interrelationship. Separately exercisable rights would require a
different separation assessment.
They are conditional judgments, not conclusions from q or the90% share.
The identified underlying pool and enforceable linkage persist. The investment
return is payable whether the insured lives or dies; there are no surrender,
lapse, tax or fee cash flows. It is not distinct from the insurance component
under the supplied finding. Under.85 it is excluded from service revenue and
expense. The insurer buys one unit of the underlying at FVTPL; its valuation
portfolio is a calculation, not an assertion that it holds the replicating hedge.
No B115 risk-mitigation election is made.

Opening owner capital/cash50 provides liquidity. Premium110 gives fulfilment
cash flows before premium of99+2+1-110=-8 and CSM8. After receipt LRC110
contains financial benefit99, mortality2, RA1 and CSM8. Investing100 leaves
cash60 and underlying100 against LRC110 and equity50.

At the pre-service observation, the variable-fee change is
0.1(S-S0) minus the change in the top-up value, under.45/B111–114.
For up, it is2-(0-9)=11: CSM rises8→19. The fulfilment liability becomes
108+2+1=111, and total LRC130. Underlying gain20 and insurance finance
expense20 offset. For down, it is-2-(18-9)=-11: CSM8 is exhausted,
loss3 is recognised, fulfilment liability/LRC is90+2+1=93, and loss
component3 is tracked within93. Underlying loss20 and insurance finance
income20 offset; the separate service loss reduces equity to47.
Reclassification as non-VFA solely because the floor now binds would violate
the inception-assessment rule B102.

One complete service interval then releases the remaining mortality estimate2
and RA1, together with any CSM. Up-state revenue is2+1+19=22.
In the down state all3 of the service-related release is allocated to the
loss component, giving loss reversal3 and revenue0; the investment repayment
does not enter this allocation. Actual mortality expense is0 or20, with a
separate incurred-claim liability and payment. The insurer sells the underlying
and pays the investment component108 or90. Final liabilities/components are0.

| Physical world | Weight | Cumulative profit | Final cash/equity | Operating cash | Investing cash |
|---|---:|---:|---:|---:|---:|
| Up, alive |27/40|22|72|2|20|
| Up, death |3/40|2|52|-18|20|
| Down, alive |9/40|0|50|20|-20|
| Down, death |1/40|-20|30|0|-20|

Operating cash is premium110 minus the investment-component payment and
mortality payment; investing cash is sale proceeds minus100. These are the
specified nontrading-investment classifications under retained AASB107.14–16;
FVTPL alone does not establish dealing/trading. Profit, zero OCI and owner
capital reconcile equity in every world. Physical expected profit14.5 is
descriptive arithmetic under the authored law, not a forecast performance result.
Replacing all four worlds by the mean loses the down/death shortfall.

## Acquisition cost enters measurement once

A separate GMM group uses capital50. Before its contracts are recognised,
acquisition cash10 is allocated wholly to that future group, with no renewal
allocation. At the prior assessment, expected premium100, claims80 and RA5
give expected net inflow15; the asset10 is recoverable under B35D. Cash40
plus asset10 equals equity50. Actual claims and their expected cash timing
are revised at recognition: expected claims100, RA5, premium100, rate0.
There was no intervening unrecorded onerous reporting interval.

Under.28C/.38(c)(i)/.47, remove the acquisition asset10 and measure the
new group. Its pre-premium FCF is5; total initial loss is5+10=15 and
CSM0. The combined entry debits loss15, credits acquisition asset10 and
LRC5. Premium receipt then gives cash140, LRC105 and equity35.
Loss component15 is inside105; it is not an additional liability.
The acquisition cash was already paid; including it again as a future payment
would overstate measurement.

Held reinsurance covers50% of all claims of this group, costs55 at inception,
and has no commissions, limits, disputes or non-performance adjustment in
this conditional example. Transferred-risk RA2.5 is supplied independently,
not inferred as a universal half-RA rule. Expected recovery50 plus RA2.5
gives fulfilment asset52.5 after paying premium; ordinary cost CSM2.5 makes
the measured asset55. The held group has its own identity and service units
and is not itself VFA (B109).

If the treaty was entered into at or before recognition of the onerous group,
.66A/B119C–D adds loss-recovery income15×50%=7.5, increasing cost CSM
to10 and the measured asset to62.5. This is the source formula using the
loss and expected claims-recovery percentage; it is not a claim that the
treaty separately pays half the acquisition invoice. Its loss-recovery
component7.5 is within62.5. Cash after the55 premium is85; assets147.5,
issued liability105 and equity42.5 reconcile.

At service completion, allocate the issued release105 between revenue90
and loss reversal15 (ratio15/105=1/7 for expected claims and RA).
B125 additionally presents acquisition-recovery revenue10 and the same
service expense10. This is a presentation gross-up with no new cash or
acquisition asset. Gross revenue100, claims expense100, acquisition expense10
and loss reversal15 give service-period profit5. With initial loss15,
the issued group's lifetime loss is10.

The held coverage asset62.5 releases as premium allocation55 plus reversal
of loss recovery7.5, with separate incurred recovery50 and cash collection50.
Service-period held result is-12.5; together with initial recovery7.5 its
lifetime result is-5. The whole entity finishes at cash/equity35, no group
balances, and cumulative loss15. Operating cash is-15 from premium100,
acquisition10, treaty premium55, claims100 and recovery50.

If otherwise identical reinsurance is entered into only after the issued
group's recognition, B119C prevents the original-loss recovery. Initial held
asset55 and cost CSM2.5 leave entity equity35; subsequent combined service
result0 leaves final cash/equity35. Equal terminal cash does not validate
premature recovery or netting issued and held groups.

## Records, algorithms and failure behavior

FinancialValuation binds contract/group, valuation time, currency, source view,
payoff and underlying identities, exact S0/Su/Sd/R, trading assumptions,
replication coefficients, state prices, method version and result provenance.
PhysicalJointLaw separately binds the ordered market/mortality worlds,
probabilities, conditioning information and dependence assumption. RiskAdjustment
binds group, risk type, compensation/method/evidence, measurement date and
release allocation. No probability field is shared implicitly between these
records. Conditional inputs retain their assumption IDs.

GroupMeasurement binds current components, recognition/coverage dates, eligibility,
underlying ownership, service units, loss component and finance policy. Each
event binds exact prior version, contract/group identity, source-view availability,
event time, ordered journal and component changes, and replay identity. A
valuation alone cannot post. Commit/replay follows the existing common
atomic contract; no new runtime or exception to it is introduced.

PriceTwoState validates finite exact values, positive growth and distinct
positive state prices; checks the stated market admission; constructs payoffs;
solves the two equations; independently reconciles the state-price value;
returns the guarantee and total financial-benefit prices with both laws
kept distinct. Additional states, unhedgeable guarantee terms or unsupported
trading conditions produce valuation_model_unresolved, not the toy price.

RevalueVFA checks admission and pre-service timing, changes FCF and variable
fee, applies the CSM/loss ordering, and reconciles total liability against the
underlying finance movement. ReleaseService separately allocates expected
claims, RA, CSM and loss component, excludes investment components, recognizes
actual claims and settles owned balances. Unknown service history or a missing
RA record yields measurement_unresolved. Changed laws invalidate dependent
measurements, not previously published evidence.

TransferAcquisition checks allocation/recoverability history and an unconsumed
asset version, includes it in initial group measurement and derecognises it once.
MeasureHeld independently values the treaty, tests entry/recognition times and
covered-contract mapping, and bounds the recovery component by recoverable
issued loss. Missing treaty timing, partial coverage without allocation, unknown
non-performance or an unsupported RA yields a specific unresolved measurement.
Exact replay changes nothing; a different payload under the same event ID
is a conflict. These are documentary operation obligations.

Required adverse cases include physical weights substituted for pricing;
missing nonfinancial RA; automatic VFA eligibility; a financial move after
service treated as entirely future service; whole underlying gain put into CSM;
guarantee omitted; loss component added twice; investment benefits counted as
revenue; retained/doubled acquisition asset; omitted B125 presentation; untimely
loss recovery; component added to held asset twice; and unsupported probability
independence. The exact reference cases are under
data/accounting-master/finite-method-decisions-20261015/insurance/.

This supplies a finite valuation method and group interaction. Continuous
financial markets, calibrated guarantees, actual insurer RA/dependence/terms,
partial/changing treaty coverage and actual transition histories retain their
specific methods and validation obligations. R05 must design the target-specific
financial and actuarial validation before any future empirical campaign.
