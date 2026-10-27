# ConditionalReturnStateFamily/1

The closed request contains profile, state, event, event_domains, premise,
obligations and branch_limit. State is one complete NativeReturnBookReference/1
record. Event is the complete selected settlement/sale skeleton. A domain is
allowed only for an explicit unknown event field: actual_units, unit_handling,
unit_deterioration, inventory_nrv for settlement, or proceeds for sale. Domains
use the existing exact interval/premise/source_ref format; source_ref must match
the full skeleton's canonical digest and field pointer. Known event facts cannot
be overwritten by a domain. The common proposed premise connects fixed source
bindings; domain-specific premises remain. No premise admits actual facts.

Validate the complete opening with the original structural/native checks.
Reject duplicate event identities, settlement lot collisions, missing sale lots
and disposed lots. Dates, methods, fractions, Boolean findings and external cash
facts remain fixed known/unknown values. Unknown required state-derived monetary
inputs are unresolved. The original builder regenerates event-dated method
contexts and exact source references; no at key or other context is discarded.

The preserved original requirement template is re-instantiated with declarations
returned by the original generator and must match its complete digest. This
avoids monkeypatching the evaluator. Every selected requirement maps to a shared
monetary input or an explicit external binding. Build the full prerequisite and
piecewise monetary family, then add opening_cash + journal_cash >= 0 to every
branch. Preserve all domains, minimum arms, prerequisites and obligations. The
condition-audit.md establishes coverage of other native conditions in this
fixed-opening/identity fragment; candidate replay is additional verification.

Each feasible witness materializes only the declared unknown numeric event
fields. Run both TypedReturnTransition/1.propose and the original native
transition. Compare complete next state, journal and flows; also match the
monetary family's amounts and all compiled constraints. The resulting state is
conditional and uncommitted. Actual/source/accounting admission and method
eligibility stay false. Residual obligations keep actual target existence unknown.

All branches must be checked infeasible for conditional emptiness. A witness
under partial search establishes existence but leaves coverage incomplete.
Global branch/cell/time limits and exact conflict checks follow the unchanged
parent policies; Python preparation/replay is bounded but not hard deadline
preemption. Alternate valid witnesses are acceptable. Invalid original replay
vetoes a candidate result and is never reclassified as empty family.

An already cash-negative opening returns its original funding_failure. A valid
opening whose possible events all breach the funding condition yields an empty
conditional next-state family. This distinction preserves the concrete failure
and family feasibility questions. No balancing loan or omitted failed branch.

Seventeen focused tests pass, including complete known matches, alternative
recoverable-value states, strict quantity, low cash, event/lot ordering, original
context regeneration, missing facts/premises, dimensional input integrity,
unknown products, resource stops, forged state and alternate witness replay.
Repeated-event symbolic state propagation remains the next distinct task.
