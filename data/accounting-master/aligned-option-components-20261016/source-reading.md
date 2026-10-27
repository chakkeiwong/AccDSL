# Actual and hypothetical option components

Inspected retained EU2023/1803 original IFRS9.6.2.4(a) (35762–35770),
6.5.11 (36083–36146),6.5.15 (36179–36243),B6.5.5 (41957–41985),
B6.5.29–33 (42400–42520). The primary PDF/text remain under
docs/design/research/p08-v3-preparation. Historical rule support only.

B6.5.5 makes the hypothetical derivative a mathematical device for the hedged
item. It must replicate that item's terms and cannot import actual-instrument
features absent from the item. For the stated one-sided price risk, use the
hypothetical call's intrinsic value at the specified hedged price level.
The actual purchased call has its own strike and complete actual valuation.

6.5.11 places effective designated intrinsic gains in the cash-flow hedge
reserve and the remainder in profit.6.5.15(b) separately accumulates related
time-value changes in equity and transfers the transaction-related amount into
the inventory basis when the purchase occurs. Neither reserve transfer is a
new cash flow. Only the actual premium and settlement enter cash or the option
asset. The hypothetical contract is never acquired.

B6.5.32 determines aligned time value from an option with critical terms
matching the item.33(a) uses aligned changes when initial actual time value is
higher, with the actual/aligned difference in profit.33(b) uses the lower
cumulative change when actual is initially lower. This finite method uses
positive purchased-call time values whose cumulative changes are nonpositive;
the reserve is the negative of the smaller cumulative loss in33(b). It does
not extrapolate this loss calculation to opposed changes or signed collars.
Equality is admitted only for fully matched terms and equal component values.

The intrinsic identities q*max(price−strike,0), journal differences and complete
cash/basis bridge are local deductions for supplied terms/marks. They are not
a model for pricing time value or evidence that actual qualifying findings are
true. The older AASB-profile example is preserved as a comparator, not silently
relabelled as this historical-EU profile.
