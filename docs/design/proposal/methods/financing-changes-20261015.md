# Changed financing rights and qualifying hedges

R03-A, 15 October2026. MC06/07/11/13–20/24–28/30/32–35.
Historical AU for-profit Tier1 calendar2024/25 illustrations; no optional
later amendments. The retained AASB132 and AASB9 compilations apply to annual
periods starting1January2023 through before1July2026. This is not an
October2026-current or multi-GAAP admission. All monetary examples are pretax;
tax is uncomputed, not zero. Source fields and exact spans are in the financing
sidecar under data/accounting-master/finite-method-decisions-20261015/financing/.

## Records, ownership and common admission

FinancingChange carries issuer/book/perimeter/currency, old instrument and
classification refs, signed carrying components, accrued coupon status,
original/revised legal terms, amendment/settlement times, actual exercise,
cash/share consideration, fees, share quotation and valuation time, liability
fair-value method/input/result refs, authority/applicability, approval refs and
event identity. A derivative or foreign-currency/cash-alternative feature is
classified before using a plain fixed-for-fixed compound-instrument method.
Unknown legal terms, fair value, quotation date or event timing remain unknown.
The original equity component is historical equity, not a derivative marked
to market. An event proposal and a report never grant posting permission.

HedgeDesignation carries issuer/book/perimeter, hedge kind, eligible external
instrument/item refs, designated quantity and risk component, inception time,
documented objective and strategy, designation evidence, effectiveness
assessment method, economic-relationship analysis, credit-risk conclusion,
actual ratio and imbalance assessment. Forecast-item admission separately
requires highly-probable evidence; item measurement must be reliable. Whole
instruments are used in the examples; excluded option time value, forward
points and currency basis need their own supported cost-of-hedging method.

HedgeMeasurement carries valuation time, currency, instrument cumulative gain
including settled gains, instrument carrying amount, cumulative hedged-item
PV change attributable only to the designated risk, source/model/curve refs,
discounting and numerical status. A hypothetical derivative may calculate the
item's change but may not import features unique to the actual derivative
(AASB9 B6.5.4–6). Supplied values are illustrative inputs, not a valuation
implementation. Missing values refuse measurement, never imply zero.

HedgeState stores designation revision, active/rebalanced/discontinued state,
last measurement, cumulative effective and ineffective gain, signed reserve,
cumulative earnings reclassifications and nonfinancial basis transfers,
remaining item exposure, derivative carrying amount and actual settlements.
Assessment occurs at inception and each reporting date or significant change,
whichever comes first (B6.4.12–19). Correlation alone does not establish an
economic relationship. Credit dominance is assessed against the economic
relationship; a quiet underlying period alone cannot establish dominance.

Admit source/date/profile and complete facts first; classify and test
eligibility next; calculate proposed measurement/state; derive journal and
statement effects independently; authorize and commit under the common
expected-head/event-identity/replay rules only in a later implementation.
Pure designation or a qualifying benchmark amendment can be state-only.
Unknown eligibility must not receive OCI treatment. Definite ineligibility
routes to the separately supported ordinary derivative method; it does not
erase the derivative. Reused event IDs cannot post the same reserve release
or share issue again. These records are a field specification, not yet a new
complete portable wire profile or executed endpoint.

## F4 — Repurchase, inducement and settlement alternatives

For a repurchase before maturity with original conversion rights unchanged,
AASB132 AG33–34 allocates consideration and costs consistently with initial
component separation. For zero fees, value the debt component using the
remaining contractual flows at the contemporaneous comparable nonconvertible
debt rate; allocate the residual repurchase consideration to equity. Debit the
old debt carrying amount, recognize debt allocation minus that carrying amount
as settlement expense (negative is gain), debit equity for the equity
allocation, and credit actual cash. Do not expense the equity allocation.

IE39–46 supplies face1,000, half-year coupons50, original half-year rate5.5%,
10 remaining coupons after five years and current comparable rate4%. Exact
illustrative valuation uses PV(r)=sum(k=1..10)50/(1+r)^k+1000/(1+r)^10.
The source rounds the old/new debt amounts to962/1,081; consideration1,700
then allocates619 to equity and119 to debt settlement expense. The source's
integer figures are not exact unrounded present values. Preserve both
calculations and their displayed rounding comparison. The earlier equity60
remains within total equity and may be transferred internally; the619 debit
is not limited to that original component. Tax and transaction costs are
omitted as in the source illustration.

AG35 measures an inducement loss as revised-conversion consideration fair
value minus original-conversion consideration fair value at the amendment
date. IE47–50 uses face1,000, conversion price25 changed to20, and quoted
ordinary share price40: original40 shares, revised50 shares, extra10 shares
worth400. A later share price is not the measurement date. For the explicitly
immediate, unconditional share-only conversion case with supplied carrying
debt960 and original equity60, debit debt960 and inducement expense400, credit
issued equity1,360; issue50 shares and retain the original60 in equity. The
entry is a local deduction combining derecognition, issued consideration and
the checked AG35 loss, not an assertion that the source's later example gives
that carrying debt. There is no cash flow; disclose the noncash financing event.

A delayed, contingent or cash inducement requires terms determining when and
what obligation is recognized; this immediate-entry case does not answer it.
Unknown acceptance or an expired offer gives no automatic conversion event.
Original maturity conversion remains AG32's no-gain/loss case. A net-cash
settlement alternative in a derivative requires AASB132.26–27 classification
unless every alternative is equity; a variable number of shares worth a fixed
sum is not equity merely because shares settle it (.21). These cases refuse
the fixed-for-fixed path and retain the classification/valuation obligation.
Legal-capital allocation and award accounting require their separate rules.

## F5 — Cash-flow hedge measurement and release

AASB9.6.4.1 requires eligible items/instruments, inception designation and the
economic-relationship/credit/ratio criteria. The lower-of computation does not
establish these findings. The finite arithmetic below covers a single
documented offsetting exposure with a zero-valued derivative at designation,
no excluded components, no intermediate releases, and admitted opposite-signed
cumulative changes. Same-direction or otherwise unsupported complex exposures
require a broader measurement method; they are not automatically declared
ineligible because of a sign test.

Let D be cumulative derivative gain and H cumulative change of the hedged
item attributable to the risk, in the item's signed economic-value convention.
For admitted offsetting changes, E=sign(D)*min(abs(D),abs(H)) is the signed
cumulative effective gain, and I=D-E cumulative ineffectiveness. At each
remeasurement post the derivative carrying change, deltaE to OCI/reserve and
deltaI to profit. Cumulative values, not each period's separate minimum, control
the computation (6.5.11). Retain prior E/I even when a derivative settles.
Settling a derivative debits/credits cash against its carrying amount; that
settlement alone does not release the hedge reserve.

For a forecast purchase of inventory, D12/H-10 gives effective10 and gain2.
At the next measurement D15/H-14 gives effective14 and cumulative gain1, so
the new period records derivative+3, OCI+4 and loss1. Buy inventory114, settle
the derivative for15, and remove the credit reserve14 by debiting the reserve
and crediting inventory14. Inventory basis is100. The14 basis transfer is a
direct equity-to-asset transfer, not an OCI reclassification (6.5.11(d)(i)).
Sell the inventory for130: revenue130 and cost100 give profit30. From an
opening cash/equity200, cumulative pretax profit31, OCI14 and the separate
equity basis transfer-14 reconcile final cash/equity231. Gross operating cash
is -114+15+130=31 under AASB107.16's same-position hedge classification.
Interim profit, OCI, reserve and cash are not interchangeable.

For hedged interest payments, the reserve is instead reclassified to profit
when the interest affects earnings (6.5.11(d)(ii)). Supplied D8/H-8, settlement8
and paid interest18 leave net expense10. The reserve release credits profit8
and debits the reserve8, with OCI reclassification-8; it is not another cash
receipt. The historical AASB107.31–33 operating-interest election is explicit
for this nonfinancial illustrative entity; use it consistently and separately
identify interest cash. Net operating cash is-10. New presentation regimes
and different entity elections need their own admitted method.

On discontinuation, if flows remain expected, keep the reserve until they
occur or an unrecoverable loss requires release. No-longer-highly-probable
does not imply no-longer-expected. If flows are no longer expected, reclassify
the reserve immediately to profit (6.5.12). A reserve loss expected not to be
recovered is reclassified to profit immediately for that portion
(6.5.11(d)(iii)). Later derivative changes after discontinuation follow their
ordinary method; the old designation cannot continue generating OCI.

## F6 — Fair-value hedge and remaining basis

For an admitted fair-value hedge of an amortised-cost issuer debt, recognize
the derivative gain/loss in profit and the risk-attributable debt carrying
adjustment in profit (6.5.8); this is not a cash-flow-hedge reserve. With debt100,
derivative gain8 and debt-value increase10, debit derivative8/credit gain8,
and debit loss10/credit debt10. Net loss2, derivative8 and debt110 preserve
the balance sheet. The item and derivative need separately admitted values.

After discontinuation, amortize the hedge adjustment using a recalculated EIR
no later than when the item ceases adjustment (6.5.10). If the now110 debt has
contractual principal100 and coupon21 due together one year later, revised EIR
is10%, expense11 and payment121 extinguishes it. Cash interest21 is operating
under the explicit election, while principal100 is financing. The difference
between cash interest21 and effective expense11 amortizes the10 hedge adjustment.
Retaining an old rate21% would over-accrete it.
For this finite example amortization begins at discontinuation. Missing cash
schedule or maturity leaves the EIR unresolved; the adjustment cannot disappear
merely because hedging stopped. FVOCI equities, portfolio hedges and firm
commitments retain their distinct source methods.

## F7 — Benchmark reform is a conditional exception

Record old/new benchmark, fallback/legal change, effective dates, spread/reset
changes, direct reform cause, economic-equivalence analysis, additional changes,
original derecognition conclusion, designation amendments and transition source.
A name change alone supplies none of those findings. Under5.4.5–9, the
B5.4.5 rate-update expedient applies only to necessary, economically equivalent
reform changes; additional changes then receive ordinary modification or
derecognition treatment. The arithmetic comparison of old4% versus new3.8%+
0.2% can check one coupon but does not prove equivalence of all future terms.

Under6.9.1–6 a qualifying formal designation amendment by the reporting-period
end is neither automatic discontinuation nor a new designation. Additional
changes must first be assessed for discontinuation; all unaffected qualifying
requirements continue. Cash-flow reserves follow the alternative rate under
6.9.7–8, not a new zero opening. Mixed benchmark groups need6.9.9–10 subgroup
eligibility. The24-month separately-identifiable exception is rate-specific,
requires a supported expectation and ends on adverse reassessment under
6.9.11–13. The finite profile refuses to invent that expectation or extend the
exception beyond its source conditions. Phase1 relief and its cessation remain
separately tracked under6.8 rather than reused indefinitely.

## Residual decisions

These are required financing method repairs, not optional decorations. They
supply scoped calculations and decision procedures but do not close actual
valuation, delayed/contingent inducement recognition, excluded-component option
costs, general rebalancing/group-hedge computation, legal capital or current
multi-GAAP authority. Preserve those named readiness residuals. Next supported
leads are AASB9.6.5.15–16/B6.5.29–39 for excluded components, B6.5.7–21 for
rebalancing and6.6/B6.6 for group hedges; inspect before implementing those
claims. More examples of the same base instrument cannot close those methods.
