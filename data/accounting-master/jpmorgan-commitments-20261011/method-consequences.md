# Consequences for the bank specification

Maintain at least five distinct states: the contract and cancellation terms;
the dated disclosed commitment population; a future draw or acquisition
condition; the applicable allowance/guarantee measurement; and the settlement
and funding state. Each retains its entity, currency, reporting date, source,
population, measurement basis and any expected future date. A source amount
must not silently change roles when passed between these states.

| Requested result | What the inspected facts support | Inputs still needed |
| --- | --- | --- |
| Reproduce the displayed commitment total | Consumer plus wholesale and maturity buckets reconcile to 1,817,307 million | No individual contract inventory is supplied by the total |
| Reproduce the commitment allowance movement | Opening 2,101 plus provision 2,969 plus other 1 equals closing 5,071 | Meaning of the one-million other movement remains unallocated; no invented journal |
| Reproduce guarantee carrying value | 175 allowance plus 441 guarantee liability equals 616 for the selected guarantee population | Underlying instruments, valuation and operative authority for a new computation |
| Simulate customer draw | A conditional draw branch may be retained where terms permit | Contractual ability to cancel, actual cancellation policy, demand, timing and default dependence |
| Simulate funding | Settlement creates or changes funding needs under an explicit policy | On-us/off-us settlement, available liquidity, collateral and funding limits |
| Query Apple portfolio owned at year-end | Forward purchase commitment and future-close estimate remain distinct from owned loans | Actual close and acquisition accounting facts; future estimate cannot answer current ownership |
| Compare a regulatory exposure | Align gross/net participations and excluded guarantees first | Exact regulatory schedule definitions, date and perimeter |

A permitted cancellation branch and a permitted draw branch can coexist where
facts do not decide between them. Their weights remain absent. A contractual
draw may create a loan and deposit before external settlement, or require a
different settlement path; the accounting event must follow the actual
contract and payment mechanism. These are requirements for later implementation,
not executed simulations or claims that every branch is legally available.

The allowance-related policy applies before realised default and separately
from a cash draw. AccDSL should preserve the issuer's five-scenario protocol
as disclosed provenance. It should not fill missing probabilities, forecast
horizon or qualitative overlays from that protocol when modelling another
bank. None of these observations changes the existing illustrative PD/LGD
calculation into a compliant expected-credit-loss implementation.
