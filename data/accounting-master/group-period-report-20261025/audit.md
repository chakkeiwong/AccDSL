# Period report audit — 25 October2026

Baseline is the existing legal report engine and separately checked composition
worksheet, plus four hand-specified cases (two account charts; same-activity
or investing/financing internal cash classifications). The independent expected
outcome is group cash200→220, profit20, equity200→220, external receipt20.
No economic history is inferred from snapshot balances.

The design preserves each complete legal report and all raw cash origins.
Only named full-amount pairs are removed from group presentation; a reference
binds owner, flow ID and exact bytes. Dates and currency must match; amounts
must be opposite; same-book, repeated and stale references refuse. Different
activities are removed independently, not by netting activity totals. Legal
activity classifications are supplied assumptions, not separately assessed.

Important defaults: fixed two-book, same-policy/currency, full-ownership and
stable control scope are inherited convenience hypotheses from the preceding
worksheet. Provenance is the explicitly constructed fixture, not real source
data. Wrong assumptions could produce a reconciled but economically false
summary; source/accounting/control acceptance remains false. Early diagnostics
refuse unsupported ownership/perimeter and stale legal reports. Reconciliation
is a correctness veto, not accounting promotion. Counts and runtime explain
the check only; no stochastic ranking is involved.

Missing pairs or a missing reciprocal closing elimination can still leave
cash/equity numerically balanced. The implementation therefore never calls
the result complete: it preserves unremoved flows/balances and an explicit
population-completeness uncertainty. In contrast, a changed investment/capital
elimination breaks the declared equity bridge and refuses. This distinction
prevents arithmetic reconciliation from claiming identification of all internal
transactions. A matching amount/date cannot establish the truth of its supplied
counterparty premise. Actual sources and richer methods remain required.

The snapshot API is reused without alteration. New code has no durable write,
external computation or method-admission side effect. Audit passes for this
conditional period summary. Full consolidated statements, indirect cash flows,
NCI, goodwill, tax, FX, intragroup profit and complete notes remain open.
