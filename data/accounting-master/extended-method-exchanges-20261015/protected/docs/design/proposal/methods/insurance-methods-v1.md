# Insurance groups, service, claims and reinsurance

An insurance group retains obligations for future service, claims already
incurred, financial risks and compensation for non-financial risk. Its assets
and reinsurance are separate from gross insurance obligations. This method
addresses MC11–MC14, MC16, MC19–MC22 and MC25–MC29. The retained official AASB17
text supports the cited incorporated IFRS17 provisions for its stated version.
The synthetic inputs below do not establish actuarial calibration or an entity's
risk adjustment. EU cohort endorsement exceptions are not imported into an
Australian/IASB group definition.

## I1. Group state and general measurement

Contract records retain insured risks, premiums/benefits, service and settlement
dates, options/guarantees, cancellation/repricing rights and acquisition costs.
Group admission evaluates portfolio/similar-risk management, onerous status and
required issuance cohorts under AASB17.14–24, recognition under25–28 and boundary
under34. Cash outside the boundary belongs to future contracts, not this group's
profit. GroupState retains expected dated cash flows, current discount curves,
inception rates, explicit risk adjustment, CSM, loss component, LRC/LIC,
coverage units, service experience and assumption vintages. Same premium totals
are not sufficient state for merging different guarantees or claim tails.

General measurement follows32–38: fulfilment cash flows are probability-weighted
future net outflows, adjusted for timing/financial risk without double counting,
plus explicit non-financial risk adjustment. CSM removes initial unearned gain
under its conditions; an initial net loss is recognized under47, not negative
CSM. Paragraphs40–44 separate remaining coverage and incurred claims. For a
nonparticipating group, accrete CSM at the specified locked-in rate, apply future
service changes at their required rate to CSM up to its available amount, record
any excess loss and allocate current service over current plus future coverage
units under B119. B96–B97 distinguish future service from incurred-claim changes,
financial changes and current experience; not every revision is a CSM adjustment.

A MeasurementInput must resolve cash-flow/law, discount, risk-adjustment method,
service grouping and coverage-unit evidence. Missing probabilities or RA support
permit conditional sensitivity cases but block a source-supported measurement.
Risk adjustment is the compensation the entity requires under37; a standard
deviation, confidence quantile or arbitrary percentage is only a candidate method
until justified for that entity. Disclosures and the confidence-level equivalent,
where applicable, are separate obligations. Market-consistent financial inputs
and entity risk compensation must not be conflated.

## I2. Complete two-year general-measurement case

Take a two-year nonparticipating group with one premium120 received at inception,
claims expected/actually incurred and paid40 each year, zero discount rate,
RA10 initially released5 with each equal service year, no acquisition costs,
investment component, lapses, taxes, finance changes or reinsurance. Coverage
units are1 in each year because equal benefits and coverage are assumed.
Before premium payment, expected net cash outflow is80−120=−40, RA10, FCF−30
and CSM30, with net initial carrying amount zero. After the premium debit cash120/
credit LRC120. Its components are remaining expected claims80, RA10 and CSM30.

Each year releases expected service claims40, RA5 and CSM15: debit LRC60/
credit insurance revenue60. Incur claims40: debit service expense40/credit LIC40;
payment debits LIC40/credits cash40. End of year one: cash80, LRC60 (claims40,
RA5, CSM15), LIC0 and equity/profit20. End year two: cash40, liabilities0,
cumulative equity/profit40. Revenue120 and claims80 reconcile to premium120 less
claims cash80. No investment component has been mistaken for revenue.

At year-one close, a separate pre-next-service change increases the remaining
claim estimate from40 to60, RA unchanged. FCF rises20; consume remaining CSM15
and recognize service loss5. LRC rises from60 to65, comprising FCF65, CSM0 and
loss component5 as a tracked portion, not an added liability on top. Debit
service loss5/credit LRC5 with component transfer CSM→FCF15. A decrease of8 in
the revised future claim estimate, before any additional service/finance
movement, first reverses loss5 and restores CSM3. FCF57 plus CSM3 gives LRC60.
Credit loss reversal5/debit LRC5. This tests48–52 ordering. Later systematic
allocation of loss component to releases/finance must reduce it to zero by
coverage end; it cannot be amortized as revenue a second time.

In a separate case, an already-incurred unpaid claim estimate rises40 to48.
Debit service expense8/credit LIC8; do not consume future-service CSM. A
discount-rate change is financial under B97; its profit/OCI route follows the
selected permitted finance policy. The zero-rate base case does not remove the
need for separate current and locked-in rate calculations in a real group.

For the unreversed onerous alternative, carry the loss component through the
remaining service year. Opening LRC65 comprises future claims60 and RA5, with
CSM0 and loss component5 within that LRC. A declared proportional allocation
assigns 5/65 of each expected claim/RA release to the loss component, consistent
with paragraphs49–52 and B124's revenue exclusions. The expected claim release
allocates60/13 to loss reversal and the RA release5/13; the total is5, leaving
loss component0. Debit LRC65, credit revenue60 and credit loss reversal5.
Separately incur and pay claims60 through LIC. Period profit is60−60+5=5;
combined with first-year profit20 and the earlier onerous loss5, lifetime profit
is20. Closing cash20 equals equity20 and all liabilities are zero. Treating
all65 as revenue while also reversing loss5 overstates profit by5.

## I2a. Nonzero discount and service allocation

A second complete case keeps premium120, two equal coverage units and RA10,
but expected and realized claims are44 after one year and48.4 after two years.
Both the inception and current discount curves remain a flat10% throughout;
there are no new estimates, options, fees, taxes, investments or OCI election.
This RA schedule is an authored measurement input, not an actuarial calibration:
it declines by5 per year, with its entire change in the service result under81.
All other insurance finance effects go to profit or loss. The retained source
supports the mechanics in44,80–88,B119 and B123–B124.

At inception claim PV is44/1.1+48.4/1.1²=80. FCF before premium is80+10−120=−30,
CSM30, and after premium LRC120. In year one the claim PV accretes8; CSM accretes3
at the locked-in rate. Allocate the resulting CSM33 across the two current/future
units, releasing16.5. Revenue is expected claims44 plus RA5 plus CSM16.5=65.5.
Service expense44 and finance expense11 leave profit10.5. After paying44,
cash76 and LRC65.5 (claim PV44, RA5, CSM16.5) reconcile to equity10.5.

In year two claim PV accretes4.4 and CSM accretes1.65. Release all remaining
CSM18.15, RA5 and expected claims48.4, giving revenue71.55. Service expense48.4
and finance expense6.05 leave profit17.1. Final cash/equity27.6 equals premium120
minus claims92.4; all group liabilities are zero. Total revenue137.05 less
finance expense17.05 equals premium120. Setting revenue equal to cash premium
each year or releasing15 of CSM each year would ignore the specified financing.
These are separate component calculations followed by debit finance expense/
credit LRC for accretion, debit LRC/credit revenue for service and the stated
LIC recognition/settlement entries. Cash is deliberately assumed uninvested.

## I3. PAA, reinsurance and valuation methods

The retained sectors.json PAA gross/reinsurance case remains a bounded reference,
with its separately stated treaty eligibility and recognition timing. PAA under
53–59 requires the one-year coverage or nonmaterial-difference condition; a
short payment lag is not the eligibility test. LRC starts with received premium
and applicable acquisition adjustments, then releases insurance revenue under
the prescribed service pattern. LIC still measures incurred obligations using
the applicable fulfilment-cash-flow rules; the allowed short-settlement discount
simplification needs its own conditions. Emerging onerous facts require a loss
assessment; a premium balance cannot be presumed sufficient.

Reinsurance has its own group, boundary, recognition time, counterparty risk,
cash-flow, CSM/cost and possibly loss-recovery component under60–70A. Do not
multiply every gross insurance liability by a quota share: excluded claims,
limits, deductibles, timing, reinstatements and counterparty non-performance
matter. Claim100 with an eligible50% recovery but expected90% collectability
gives conditional expected recovery45, not50; altering transferred insurance
risk and reinsurer non-performance are different inputs. This simple calculation
does not establish treaty recognition or RA by itself. Gross liability100 remains;
reinsurance recovery is a separate asset/measurement with its own authority.

For direct participation, test B101's conditions using the actual underlying
items, substantial-share and variation judgments. Retain underlying fair values,
entity fee share and guarantee/risk-mitigation choices; .45 and B101–B118 specify
the variable-fee adjustments to CSM, with onerous and mitigation exceptions.
A local component illustration of a qualifying share: underlying-value increase20
and entity's fixed10% share gives candidate variable-fee change2; eligibility,
guarantees and other FCF changes must be evaluated before posting. The full
option/guarantee valuation and transition calculations are further supported
profiles, with source and numerical obligations, not an assumed linear fee model.

Claims development is an estimation input, not accounting recognition. For a
strictly positive cumulative triangle, volume-weighted chain-ladder factors are
f_k=Σ_i C_i,k+1 / Σ_i C_i,k over observed matched cells; project each incomplete
row multiplicatively and subtract latest cumulative claims to get the reserve.
Mack1993 equations(1)–(3) and Theorems1–3 require conditional development means,
variance scaling and independent accident years for its error formulas. Tail,
calendar inflation, zero/negative cells and dependence need explicit treatment;
the point estimate alone is neither a predictive distribution nor IFRS17 RA.
For rows (100,150,180), (120,180), (140), factors1.5 and1.2 give ultimates180,
216,252 and total outstanding36+112=148. Only one observation estimates the
second factor here, so a final development variance/error estimate is not
identified from these data without a separately justified tail assumption.
Return variance_unresolved instead of a fabricated zero standard error.

## I4. Interfaces, exclusions and acceptance cases

Insurance events are group_recognize, premium_settle, service_release,
claim_incur, claim_settle, assumption_change, onerous_change and treaty_change,
each bound through M1–M4 to the exact group/version, evidence and information
view. Journals and component roll-forwards must reconcile independently; a
component reallocation is not always a net liability change. Invalid grouping,
missing rate/law, unsupported option valuation, ambiguous contract boundary or
unknown service units produces the corresponding unresolved/outside-scope result.
Failed numerical paths retain their coverage/mass, without successful-only
normalization. Modified contracts need the applicable derecognition analysis;
no new ID can erase unfavorable old-group obligations.

Initial transition requires an actual method choice and eligibility for full
retrospective, modified-retrospective or fair-value transition under Appendix C,
with acquisition, grouping, past service and historical-rate records. This
collection does not claim an executed transition or a general VFA valuation.
The nonzero-rate general case and onerous allocation through expiry above are
finite specification examples. Required later acceptance still includes a priced
guarantee, acquisition/reinsurance interaction,
transition and actuarial backtesting. These retained obligations prevent the
two-year illustration from being described as full insurance-domain readiness.
