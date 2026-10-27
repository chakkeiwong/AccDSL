# Closed linear monetary-history reference

24 October 2026. MC04/05/08/09/10/11/13/16/24/26/28. The preceding reuse audit
supports a new conditional profile, leaving reconstruction_v1 unchanged.

This first profile uses one book/context and a common explicit currency/scale
for all posting amounts, account balances and monetary economic-memory fields.
Nonmonetary units, rates, nonlinear valuation, arbitrary contracts/cohorts,
endogenous events and conditional method applicability are outside this scope.
That restriction is an engineering choice, not a product requirement. It avoids
silently assigning dimensions to template incidence; a later dimensional
successor must handle such conversions explicitly.

The closed input declares an opening date, strictly increasing snapshot dates,
account and monetary-memory opening intervals, fixed templates with balanced
posting incidence and monetary state incidence, supplied event slots with finite
nonnegative amount intervals, snapshot measurement linear forms with exact bounds,
named proposed premises, explicit scope/exclusions and unresolved obligations.
Every account/state/slot/measurement has a unique generated variable identity.
Opening values are shared unknowns at every later date. Same-day event array
order is retained, but this affine additive fragment does not claim event-order
precondition behavior. Posting quantum/rounding is absent; supplied domains are
exact under their proposed premises. Fractions retain strict endpoints.

Lowering uses the existing lower-level Problem/domain_formula/solve interface.
It introduces opening account/state and event-amount variables, opening
account-balance equality, and exact bounds on every snapshot measurement's
declared linear form of the shared opening plus all supplied events at or before
that date. It uses one original opening value per field; it never chooses
openings separately for each observation. No numeric after-state is accepted
from a caller. The narrower joint-measurement adapter requires every variable
to occur in a measured equation, which would force artificial tautologies for
unmeasured but declared economic state. Direct solver reuse avoids that mismatch
without weakening the frozen adapter. Exact solver infrastructure is reused;
the reference separately replays a witness with Fraction through every dated
event and checks every supplied snapshot measurement and domain.

Every opening domain, event/template and measurement premise is explicitly
proposed or absent. Absent premises prevent solving. Unresolved source/state
obligations are different: a complete declared numeric relaxation can produce
a candidate, while target existence stays unknown and formulation completeness
false. Results separately state candidate feasibility, target existence,
declared search and economic scope. Source/accounting admission and execution
remain false in every case. With no missing obligations, any witness applies
only to the declared conditional linear model, not an actual issuer or native
method. The full symbolic definition is always retained; one witness is not the
whole continuous family. No probability is attached.

Skeptical audit: balanced templates alone do not validate financial recognition,
economic state sufficiency or intermediate liquidity. Negative balances and
state values are permitted unless explicitly constrained by measurement bounds;
the result must not claim operational executability. A missing template premise
is unresolved rather than a feasible admitted event. Unused/extraneous fields,
shadowed names, invalid dates, noncanonical rationals, negative slot domains,
unbalanced incidence or a forged witness must reject. Do not lower real source
captions into this authored legal-book model.

Evidence contract: independent opening and per-event Fraction replay, exact
snapshot constraints, unchanged constant-opening comparator, shared-opening
counterexamples, two different histories with one closing report, strict bounds,
unknown premises, unresolved obligations and zero budgets. Failure of the
candidate family means its supplied assumptions conflict; it does not invalidate
the research direction. Invalid harness or witness vetoes interpretation and
triggers repair. Small CPU-only tests, no benchmark ranking or forecasts.
