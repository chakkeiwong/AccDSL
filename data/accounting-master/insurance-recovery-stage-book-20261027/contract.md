# Issued/held stage ledger: audited evidence contract

27 October 2026. Plan: accounting-insurance-recovery-stage-book-20261027.md.
MC03/05/11/13/15/17/18/19/20/24/25/26/28/33/34.

Audit passes for a stage-only ledger on the two retained recovery_change
histories. It does not implement fiscal execution or supply missing group IDs.
The four computational stages are opening, estimate change, issued service,
held service. Unknown dates and issued/held group identities remain null.
The original single group context remains visible; it is not split by assertion.

Comparator: full native result; separately authored complete balance/memory
snapshots; the existing covered-claims-revised and service journal example.
Pass requires separate issued/held profit, cash and liability/asset rollforward,
memory components and origins, complete debit-positive journals and unchanged
native identity at every stage. Controls reject double expense at estimate
change, omitted later held service expense, origin loss, netted roles, unknown
date/group substitution and false admission. The distinction matters: zero
additional component expense at estimate change does not imply zero component
allocation at later held service.

All balances are exact rationals from retained inputs. No invented dates,
treaty terms, probabilities, currency conversions or cash-flow classifications.
No additional equity plug: opening equity is the supplied native result checked
independently against cash plus held assets less issued liability. Full stage
balances, not only a final total, are the criterion. Three fresh attempts of
120 seconds each; CPU only. Source drift/mismatched financial targets veto
acceptance and trigger local repair. Keep successful evidence immutable.
