# Debt, bonds and ownership interests

Financing state must separate cash received, contractual principal, amortised
carrying amount, fair value, accrued amounts, collateral, covenants, seniority
and share rights. An issuer's obligation and an investor's asset have different
method selections. This specification addresses MC11–MC20 and MC25–MC29 using
the common P16 boundary. The selected AASB 9 and AASB 132 provisions support
dated incorporated IFRS mechanisms, not universal current cross-standard rules.

## F1. Schedules and initial classification

DebtContract contains parties, currency, principal, issue/settlement dates,
payment calendar, fixed/index/spread/reset terms, compounding/day-count,
business-day adjustment, principal changes, fees, options, security, priority
and legal default/remedy terms. Each term has evidence/admission provenance.
The economic schedule emits due cash independently of the recognition method.
A market-value adapter may value that schedule but cannot choose amortised cost,
FVOCI, FVTPL or liability/equity classification.

An investor's classification evaluates business model and contractual cash-flow
features; a debt label alone cannot establish the AASB9.4.1.2/4.1.2A conditions.
At initial recognition the selected 5.1.1 rule measures fair value and qualifying
costs as appropriate. An unknown day-one observable-value condition yields
unresolved under 5.1.1A/B5.1.2A. The already inspected A01–A07 cases distinguish
FVTPL expensed fees, amortised-cost fees, original EIR and POCI credit-adjusted
EIR. No rate method inferred from market value can overwrite the contract rate.

For an issuer with a plain amortised-cost debt, net proceeds 100 and one legally
due payment 121 at the end of two annual periods, the exact EIR solves
100=121/(1+r)^2, hence r=10%. Issue debit cash100/credit debt100; year-one debit
interest10/credit debt10; year-two debit interest11/credit debt11; redemption
debit debt121/credit cash121. Outstanding contractual payment stays 121 until
settled even while carrying value is 100 or 110. Total interest21 equals cash
outflow121 minus proceeds100. An immediate transaction fee2 changes net proceeds
to98 and the EIR root; retaining 10% is wrong. The numerical root method is in
forecasting-methods-v1.md; an irrational rate is not silently an exact rational.

A fractional period uses the declared convention. Annual-effective21% over half
a year produces factor1.1 and interest10 on100; simple proration gives10.5 and
is wrong for that contract. A floating coupon resets from the admitted fixing
available at the reset date, not a later observed rate. Actual day-count and
holiday-calendar versions are immutable inputs. Unknown fixings preserve
conditional paths, rather than defaulting to the latest value.

## F2. Modification, extinguishment and default

At a modification, retain original and replacement terms, counterparty, fees,
effective date, legal-release evidence and original EIR. Determine derecognition
before measurement. AASB9.3.3.1–3.3.3 and B3.3.1–B3.3.6 govern the selected
issuer-liability cases. The quantitative ten-percent test compares the PV of
new terms, including specified borrower/lender fees, at original EIR against
remaining original PV. It is not a universal asset test, nor proof that every
change below ten percent is immaterial; changed currency, rights and other
qualitative terms need the applicable analysis. Insufficient evidence remains
unresolved. Third-party payment without legal release does not extinguish debt.

On the first anniversary above, old remaining121 has PV110. Replace with133.1
due at the original maturity date, one year after the modification, with no fees
and an explicit supported substantial-terms conclusion:
PV121 differs by exactly10%, satisfying the inclusive test. Assume separately
supported new fair value118; debit old debt110, debit extinguishment loss8,
credit new debt118. The new EIR is133.1/118−1, not automatically the old rate.
If the replacement is instead a stated non-substantial same-currency reduction
to115.5, no fees or other changes, PV105 leads to debit debt5/credit modification
gain5 under the B5.4.6 recalculation mechanism, then interest10.5 and settlement
115.5. The actual change below ten percent still needs the qualitative finding.
Repurchase of carrying amount110 for108 extinguishes the repurchased obligation:
debit debt110/credit cash108/credit gain2. Unamortised fees belong in the carrying
amount before that comparison, not a second gain adjustment.

If cash available is80 against debt121 due, record the due obligation and an
unpaid/default economic state; payment80 leaves contractual unpaid41 only when
that partial payment actually occurs. Do not cancel the remaining liability,
recognize a waiver or issue a loan unless a separately admitted event authorizes
it. Covenant acceleration, cross-default, cure periods, collateral realization
and restructuring require the actual legal terms and priority waterfall. A
scenario may explore specified alternatives with explicit assumptions; it may
not silently select the cheapest settlement as an accounting fact.

## F3. Equity and compound instruments

EquityInstrument retains class, voting/distribution/liquidation rights, issued,
treasury and outstanding counts, par/legal-capital requirements and conversion
terms. Share counts are integer quantities separate from currency balances.
Issue100 ordinary shares at2 with no fees: debit cash200/credit equity200, issued
and outstanding100. Repurchase10 at3 for treasury: debit treasury-equity30/
credit cash30; outstanding90, issued100, treasury10. Reissue5 at4: debit cash20/
credit treasury-equity15/credit other equity5; outstanding95, treasury5. There
is no trading profit under the selected AASB132.33 rule; a statutory par split
requires that jurisdiction's facts. Dividend declaration creates a liability
only at the admitted point at which the obligation exists; proposal of a
dividend is not itself payment or automatically an expense.

For a qualifying fixed-for-fixed issuer conversion option in functional currency,
AASB132.28–32 separates liability fair value and residual equity. Assume total
issue proceeds100, standalone debt fair value90, zero coupon, maturity two years
and cash redemption100 or fixed10 ordinary shares; no extra derivative, tax or
fee. Issue debit cash100/credit debt90/credit conversion-equity10. Effective
interest accretes debt90 to100. At maturity conversion under original terms
debits debt100 and credits issued-share equity100; the original equity10 stays
in equity (a permitted internal transfer is not income). Shares increase10 and
no redemption cash leaves. Redemption instead debits debt100/credit cash100;
unexercised equity is not remeasured into profit. AG32 supports no conversion
gain/loss in that stated case. Variable share count, cash alternatives, foreign
currency and changed conversion terms require classification/modification
analysis; they cannot be forced into this example.

Financial statement mappings separate interest, modification/extinguishment
results, owner transactions and cash settlement. A financing-liability note
reconciles opening carrying amount, cash proceeds/repayments, effective interest,
fees, conversions, modifications and FX. Total shares and earnings-per-share
denominators need dates and dilution conditions; outstanding shares at year end
are not a substitute for a weighted period denominator. Full option valuation,
hedge accounting, EPS and legal-capital regimes remain explicitly additional
methods; the proposed records preserve their required inputs.
