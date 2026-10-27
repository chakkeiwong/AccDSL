# Commitment loss before and after funding

P17-06/P18; MC02/04/05/08/11/13–17/19–21/28/30/32–35. This method connects
the existing commitment population and funded-loan methods using selected
AASB9 compilation5 and AASB7 compilation7 provisions. Both retained covers admit
the synthetic Australian for-profit calendar2024 annual start. Real current
IFRS/US/ASBE scope, credit forecasts and market values require separate evidence.

CommitmentState retains contract/borrower/currency, irrevocable date, limit,
available/used/cancelled amount, notice/expiry, fixed/revolving nature, net-settlement
and below-market flags, fees, original credit baseline, current information and
credit assessment, draw/default/recovery joint law, funded EIR estimate and
provision. A DrawEvent links funded LoanState to that original commitment and
its credit history. The monetary transition has one atomic commit group for
funding and provision/allowance remeasurement. A later external withdrawal from
the borrower's deposit is a distinct economic event. Documentary journal lines
below decompose one draw event; they are not permission to publish a partially
funded state missing its impairment transition.

AASB9.2.1(g)/2.3 and4.2.1(d) distinguish ordinary commitments from net-settled,
FVTPL or below-market cases. This example is irrevocable during its immediate
decision window, fixed/non-revolving, full draw100 or lapse, not designated
FVTPL, not below-market and not originated for immediate sale. No fee or other
noncontingent commitment liability is assumed. A drawn loan meets hold-to-collect
and SPPI conditions under4.1.2. Initial fair value100 is an independently
admitted hypothetical measurement, equal to cash price100; it is not computed
from the physical credit law. Missing valuation or other2.3 conditions leaves
this method ineligible or unresolved rather than silently forcing par100.

Start with bank cash200/deposits180/equity20. At an initial ordered snapshot on
1January2024, probability of immediate full draw is1/2. Conditional on drawing,
default probabilities are0.1 in year1,0.1 in year2 and0.8 no default. Only one
default can occur. The loan contract pays121 at two years, original EIR10%;
either default leads to108.9 recovery at that same maturity. No collateral,
fees, tax or currency interaction enters this slice. Loss per default is
(121−108.9)/1.1²=10. First-year default shortfalls mature in year2 and still
enter12-month ECL. Initial provision0.5×0.1×10=0.5: D impairment0.5/C provision0.5.
No gross loan or cash outflow arises merely because the commitment exists.

A subsequent same-date information event supplies a supported SICR finding
and revised conditional default weights0.2/0.2/0.6. Draw probability remains1/2.
The numerical doubling is not itself a universal SICR rule; the borrower is
not credit-impaired and the asset is not POCI. Lifetime provision becomes
0.5×(0.2+0.2)×10=2. D impairment1.5/C provision1.5. Joint probabilities before
funding are no-draw0.5,draw/early-default0.1,draw/late-default0.1,draw/no-default0.3.
They are authored assumptions under5.5.17, not estimated or calibrated data.

An actual full draw is now observed, before interest accrues. The funded asset
continues the commitment's impairment history under5.5.6/B5.5.47; a new loan
identifier must not reset its original credit comparison. Conditioning the joint
law on the observed draw yields0.2/0.2/0.6 and lifetime ECL4. Keeping the prior
draw weight1/2 computes expected loss before funding, not on the now-funded
asset. Resetting stage1 uses first-year-only loss2, also wrong under the admitted
SICR finding. The same wrong answer2 has two different possible causes.

For direct external disbursement, D gross loan100/C cash100; D provision2,
D impairment2/C loan allowance4. The provision reclassification has no profit
effect; the incremental2 reflects actual funding information. There is no
undrawn capacity after this full draw and thus no remaining commitment provision.
Final cash100+gross100−allowance4=net assets196; deposits180 and equity16.
Cumulative impairment4 explains the equity change. AASB7.B8E supplies separate
provision/asset-allowance presentation, with35H–I/B8D explaining movements.

If the bank credits the borrower's account instead, D gross loan100/C deposits100,
with the same provision/allowance transition. Before external transfer cash200,
gross100,allowance4,deposits280,equity16 balance. Actual transfer to another bank
then D deposits100/C cash100, reaching the direct-disbursement closing state.
The deposit-credit event itself consumes no settlement cash. An external
payment would still need actual funds and authorization under the existing
liquidity method. Expected draw probability cannot authorize a cash payment.

Alternatively the holder lets the legally binding window expire undrawn.
D provision2/C impairment2; cash200,deposits180,equity20 remain and no loan
exists. This is lapse, not an assumed cancellation right. A partial/revolving
draw needs residual commitment and funded component measurements; B8E requires
combined presentation only if component losses cannot be separately identified,
with excess over gross asset recognized as provision. The full-draw case does
not establish that inseparability or the5.5.20 revolving-period exception.

The loss roll-forward is initial0.5+SICR increment1.5+actual-draw increment2=4,
with2 transferred from provision into asset allowance. On lapse it is0.5+1.5−2=0.
Keeping both provision2 and funded allowance4 double-counts exposure and leaves
equity14; using funded allowance2 leaves equity18. All can balance. A method
needs the original risk date, updated law, observed draw and remaining capacity
to distinguish them. Unknown probabilities yield conditional losses/sets but
not an unbiased weighted ECL; unknown risk history gives stage_unresolved;
unknown par/classification gives initial_measurement_unresolved.

No future default was sampled or observed. The exact check derives expectations
over a stipulated law; it neither validates that law nor ranks credit models.
No prudential ratio follows from accounting equity16: jurisdiction, perimeter,
capital eligibility/deductions and funded/undrawn exposure rules are still needed.
The current US cancellation illustration in the earlier chapter is separately
sourced and cannot be imported into this historical AASB method by label.
