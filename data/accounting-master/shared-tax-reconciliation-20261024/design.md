# Conditional current-tax arithmetic with exact reconciliation

24 October2026. S2–S4;MC05/11/13/16/24/26/28/35;G2/G4.

The audited plan pins the unchanged information assessor and two original native
tax controls. The inspected taxlots.remeasure implementation has explicit rate,
recognition, difference, origin and fraction premises; it cannot supply current
tax or lease tax facts by reuse. This implementation therefore selects a new
uniform_rate_no_credits_v1 arithmetic assumption explicitly. It does not present
that choice as a jurisdictional rule or a replacement for the original controls.

## Request, known premises and allocation identities

A closed request contains profile, information_request, information_sha256,
model and allocations. Model contains profile and selected. Selected is a
known Boolean with assumption/source-reference provenance, or an explicit
unknown with reason. False is unsupported; unknown is unresolved. Types and
references are preserved and bounded as in the information assessor.

Each allocation contains id, account, amount and origin. IDs are unique. Account
is one of the seven pretax accounts, including the zero-balance categories.
Amounts are exact signed rational strings. A native_return origin contains only
kind and event_id; the event must be in the complete closing tax-adjustment
history inside the selected interval, with identical amount and exactly one
allocation. An assumption origin contains kind and reference; it is explicitly
additional and is not treated as a native fact. Native adjustments must never
be added again after these allocation sums have been formed.

The original event allocation to an income category is supplied, not inferred
from the event name. Its totals must equal each corresponding information
declaration. That agreement establishes arithmetic consistency, not legally
correct categorisation. Extra or missing account declarations have already
failed the information assessor. Native report, information result, model and
complete allocations stay in the result.

## Cross-field and arithmetic checks

At opening and closing, the sum of right-level asset bases equals the supplied
aggregate ROU basis, and liability bases similarly equal aggregate lease-liability
bases. Right identities include the fully terminated zero-valued B. Their bases
are supplied, not inferred from carrying amounts or termination status.

Let P be minus the sum of all seven pretax signed balances, A the sum of exact
reconciled allocation items and r the explicitly supplied nonnegative rate.
The signed taxable-profit expression is T=P+A. If T>=0 under the selected
uniform-rate/no-credit assumption, gross conditional current tax is r*T. If T<0,
the result is loss_route_required with the exact signed loss and no tax amount.
The loss_route text from information does not select an executable refund rule.

Gross conditional tax is not an incremental expense or payable: this profile
does not subtract opening accruals, apply credits or make payments. No journal,
settlement, deferred-tax reversal, loss asset or closing date is changed. All
posting,source/accounting admission,annual-close and cash-settlement flags remain
false or unresolved, even when conditional arithmetic succeeds.

## Evidence and failure interpretation

Exact fraction arithmetic with independently stated expected results, all
native adjustment identities, complete report preservation and both right/account
equalities are primary checks. Missing/duplicate origins, changed native amounts,
allocation mismatch, basis mismatch and altered identities veto a calculation.
Stopped or unknown native states retain the original assessment. An unchanged
mixed opening under the explicit retained-return adjustment produces a negative
taxable expression; that expected outcome requests a separate loss-method design.
Positive and zero controls change only clearly labelled hypothetical additional
adjustments. No legal or actual-company facts are invented or admitted.
