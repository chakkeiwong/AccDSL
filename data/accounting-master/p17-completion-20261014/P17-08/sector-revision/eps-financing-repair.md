# EPS financing schedule repair

The frozen2.90 EPS example supplies full-year interest800 and preconversion
interest400 but leaves the contractual coupon schedule unstated. Its journal
slice has no coupon payment. If interest accrues at a constant effective rate
without intervening payment, equal92-day periods starting at9200 would accrue
different amounts. The prior exact EPS calculations are conditional on supplied
earnings, but they do not establish a consistent debt cash-flow schedule.

Use the following explicit synthetic original terms in successor2.91.
Issued1July2025; coupon400 paid1October; principal9200 plus coupon400 payable
1January2026. The supplied92-day effective rate is1/23. Thus
400/(24/23)+9600/(24/23)^2=9200 at issue. The first interest charge400 raises
the liability to9600; paying the coupon reduces it to9200. The next400 charge
again raises it to9600 immediately before the January payment. The reporting
window ends before that January settlement. Full-year interest remains800.

The actual-conversion branch pays the1October coupon first and then converts
the liability9200 into600 ordinary shares under the original fixed-share
terms. The previous9600 transfer was wrong relative to this repaired schedule
and is replaced by9200. The original conversion-equity component800 remains
in equity. No inducement or gain/loss is assumed. Classification and option
valuation remain supplied inputs, not an IAS33 result.

Recognized interest400/tax benefit100 in that branch, versus800/200 for the
unconverted branch, preserve the previous basic/diluted EPS arithmetic exactly.
The missing coupon and changed conversion amount are substantive repairs;
they are not hidden by preservation counts. The old candidate, fixture,
script and manifest remain untouched as historical evidence.

The new finite verifier checks PV, effective-interest roll-forward, actual
coupon/transfer entries and the EPS comparison. This resolves the specific
cash-flow consistency defect, not actual instrument valuation or classification.
