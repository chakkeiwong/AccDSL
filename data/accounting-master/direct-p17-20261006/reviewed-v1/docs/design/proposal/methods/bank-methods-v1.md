# Bank assets, deposits, credit loss and funding

A bank creates and settles claims with different counterparties, currencies,
maturities and priorities. Its accounting equity, eligible regulatory capital,
liquidity resources and economic loss distribution are different quantities.
This method specifies their connection for MC11–MC14, MC16–MC22 and MC25–MC29.
The selected credit-loss rules use the retained AASB9 compilation5, paragraphs
5.4.1–5.4.4, 5.5.1–5.5.20 and B5.5.26–B5.5.55, within its inspected scope.
The example's probabilities and credit judgments are assumptions, not estimates.

## B1. State and event order

BankState contains cash/reserves by settlement venue and currency; deposits by
customer, access rights and maturity; assets by contract, gross carrying amount,
allowance, original EIR, accrued cash flows, collateral and credit state; undrawn
commitments; funding lines and covenants; accounting equity; regulatory mappings;
and evidence/information views. LoanState separately retains origination credit
risk and current risk, SICR finding, credit-impaired/POCI status, forbearance,
modification, write-off and recovery history. Aggregating by today's loan balance
alone loses both staging evidence and later response to shocks.

Each time step first admits information known then, forms permitted credit and
liquidity forecasts, chooses behavior under that information, and schedules due
events. Accrual, actual settlement, impairment measurement and regulatory queries
have separate business identities. A deposit received from outside debits
cash/reserves and credits deposit liability. A loan credited to the borrower's
deposit debits loans and credits deposits without initially transferring reserves;
a transfer to another bank then debits deposits and credits reserves. A loan paid
directly outside instead debits loan/credits reserves. These two funding paths
cannot be treated as identical cash events. Deposit interest debits interest
expense/credits deposit or accrued payable; withdrawal requires settlement funds.

## B2. Expected credit loss

For each admitted scenario j and date t, calculate contractual due flows minus
the cash expected to be received, including supported collateral/enforcement
cash and timing; discount the shortfall under the applicable original EIR or
specified exception. With mutually exclusive exhaustive scenario weights w_j,
ECL is the sum of w_j times those present-value shortfalls. Default-time hazards
must be converted to disjoint default-time probabilities; summing cumulative PDs
over dates counts the same default repeatedly. Collateral recoveries cannot be
credited both in LGD and as a second recovery cash flow. A shorthand PD×LGD×EAD
is admissible only if its definitions and discounting reproduce the specified
cash-shortfall calculation; it is not a universal replacement.

For the general approach, twelve-month ECL considers lifetime shortfalls arising
from possible defaults during the next twelve months; it is not just unpaid
cash in those twelve months. SICR uses the change in lifetime default risk since
initial recognition, reasonable forward-looking information and the applicable
rebuttable presumptions. Do not install a two-times-PD or30-day rule as an
unconditional universal trigger. Lifetime ECL follows a supported SICR finding;
cure needs a supported reversal of that finding. Subsequently credit-impaired
assets use original EIR on amortised cost for interest in subsequent periods;
POCI has a separate credit-adjusted-rate and cumulative-change method.

The general measurement interface requires scenario_cashflows, law_ref,
information_view, horizon_admission, credit_assessment and discount_rule. An
unweighted history set can produce conditional losses or loss bounds, but cannot
produce an unbiased probability-weighted ECL by silently using equal weights.
Return measurement_unresolved for the ECL claim. Trade receivables and certain
other assets use the separately applicable simplified approach; the general
loan staging rule must not overwrite AASB9.5.5.15–16.

## B3. Full loan and allowance roll-forward

Assume a fixed-rate non-POCI amortised-cost loan originated for100, one terminal
payment121 two years later, original EIR10%, no fees, collateral, modifications,
FX or taxes. At origination the assumed lifetime scenarios are: default in the
first twelve months with probability 0.1, default during the following year
with probability 0.1, and no default with probability 0.8. Either default gives
terminal collection 60.5. The first twelve-month ECL includes lifetime loss from
the first scenario only: 0.1×(121−60.5)/1.1²=5; initial lifetime ECL would be 10.
Debit loan100/
credit cash100; debit impairment5/credit allowance5. Gross100, allowance5, net95.

At year-one accrual the loan has survived the first window and is not yet
credit-impaired: debit gross loan10/credit interest10. Survival alone would give
remaining default probability 0.1/0.9=1/9. A subsequent, separately admitted
credit forecast revises that conditional probability to 0.2; it is an authored
forecast update, not a Bayes calculation from survival alone. Its lifetime
weights are 0.8/0.2, with a
separately established SICR finding; ECL=0.2×60.5/1.1=11. Debit impairment6/
credit allowance6. Gross110, allowance11, net99. The ratio change alone is not
the defined SICR test. Immediately afterward, a distinct, ordered credit-impairment event
establishes that only60.5 will be collected at maturity. Required allowance is
110−60.5/1.1=55; debit impairment44/credit allowance44. Net55.

In the next full year interest revenue is55×10%=5.5. The gross contractual
accretion is11. One consistent decomposed posting debits gross loan11, credits
interest revenue5.5 and allowance5.5: gross121, allowance60.5, net60.5. This
reconciles gross and net-interest bases without counting the same expected loss
again. Collect60.5: debit cash/credit gross60.5. When no reasonable expectation
of remaining recovery is established, debit allowance60.5/credit gross60.5.
Both balances reach zero. A mere delinquency is not that write-off finding.
Subsequent unexpected cash recovery is recorded with its own recovery-income
method and evidence; it does not restore an old live receivable by default.

| Moment | Cash, opening200 | Gross loan | Allowance | Deposit liability | Equity, opening20 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Initial loan and allowance | 100 | 100 | 5 | 180 | 15 |
| Year-one accrual and SICR | 100 | 110 | 11 | 180 | 19 |
| Credit impairment | 100 | 110 | 55 | 180 | −25 |
| Maturity accrual | 100 | 121 | 60.5 | 180 | −19.5 |
| Collection and write-off | 160.5 | 0 | 0 | 180 | −19.5 |

Total interest15.5 less impairment55 is loss39.5, equal to100 advanced minus60.5
received. The negative equity state survives; no missing branch or capital plug
restores solvency. These five dates jointly test allowance, recognition and bank
balance-sheet arithmetic. The same loss cannot also be deducted directly from
gross before the stated write-off.

For a non-derecognized loan modification, AASB9.5.4.3 requires gross PV at original
EIR and a modification result, then allowance and SICR reassessment under5.5.12.
For example gross110 changed to a single future110 at original10% gives revised
gross100 and modification loss10 before any allowance change. This is separate
from the financing method's issuer-liability ten-percent test. A derecognition
decision requires its own asset conditions and cannot reuse that threshold.

## B4. Funding, capital and decision policies

Liquidity simulation settles the dated net payment queue by venue/currency,
respecting encumbrance, available cash, committed line terms and admissible
actions. Haircut/eligibility and transferability come from a versioned policy;
market value alone is not available liquidity. With cash20, due withdrawal30
and an admitted usable facility8, even a full draw leaves shortfall2. Record the
default/unresolved settlement according to the event's legal model. Raising
exactly2 of new equity without an investor event is an invented financing source.
Interbank contagion requires explicit counterparties and settlement priorities;
it cannot be inferred from aggregate deposits.

A RegulatoryAssessment reads an accounting view and an independent jurisdiction,
date, perimeter, eligibility, deductions and exposure-weight policy. It outputs
capital components, RWA/exposure measures, liquidity measures and reconciliations
with their distinct denominators. Illustratively, equity20 minus an assumed
regulatory deduction2 yields capital18; assumed RWA125 gives14.4%. Those inputs
are synthetic, not a Basel rule, national capital approval or default threshold.
No binding capital-policy numbers have been inspected for a target bank here.
Use the Basel/national source and actual bank facts before real admission.

Behavior under capital/liquidity constraints is a separate economic model.
Specify feasible actions, objectives, information set and ties before solving;
failure to find an action returns policy_failure or default under the stated
contract. Halaj/Behn sources can motivate candidate behavior but cannot calibrate
it for an individual bank. A forecast experiment must compare simple fixed-book,
contractual runoff and explicitly estimated policy baselines with time-safe
data, before claiming a predictive improvement. CECL and other bases retain
separate authority/method branches in standards-methods-v1.md.
