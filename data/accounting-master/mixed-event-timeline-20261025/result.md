# Native cash movements change the next authored decision

MixedEventTimeline/1 orders supplied native payments/sales and state-dependent
decisions by explicit date and priority. It reuses both checked runtimes and
binds each decision to the book at its actual turn. Static structures are checked
before execution; state-dependent accounting findings are checked at the action.

The discriminating case pays4 of a carried tax vintage from cash452. Payment
first reduces cash to448, enabling a1-unit sale under the authored cash<450 rule:
cash ends463,inventory70,selected-lot carrying10 and tax payable25/4. Decision
first sees cash452 and takes no action; the later payment leaves cash448,
inventory80 and selected-lot carrying20. Both preserve vintages5/4 plus5 and
unchanged historical vintages. The sale adds profit5; payment creates no expense.

Seventeen focused methods,18 scheduler regression methods and61 exact comparisons
across6 cases check manually interleaved operations/requests, complete transitions,
states and financial report fields, order effects, native unknown/false findings,
prefix retention, identity/time conflicts and actual32-native/64-total boundaries.
All quantities are exact. No implementation repair was needed in focused tests.

| Decision | Primary criterion | Veto checks | Main uncertainty | Next action | Not concluded |
|---|---|---|---|---|---|
| Retain optional mixed timeline | Exact manual interleaving and independent order-sensitive controls | Timing,shape,identity,source and refusal preservation | Authored cash threshold and closed path; only directly dated payment/sale adapters | Integrate then review full architecture and mission gaps | Economic behavior, general calendars,compliance,forecast skill or production readiness |

The strongest alternative explanation is shared accounting behavior. Independent
cash,inventory,profit and vintage arithmetic plus a reversed-order control address
composition, but cannot validate all native accounting methods. A wrong complete
transition or missing refusal would overturn the local result. The weakest
generalization is restricted operation support: assessments,deferred measurements,
period carry and nested return/lease clocks stay unsupported, with no guessed date.

Engineering correctness is scoped to these contracts and cases. No stochastic
ranking is performed. S1–S5 remain partial,S6 held,S7 deferred. No whole requirement,
source/accounting admission,complete fiscal population or durability is promoted.
