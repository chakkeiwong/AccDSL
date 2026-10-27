# State-dependent decisions on the conditional annual book

StateDecisionEvent/1 takes an existing complete PeriodBook/1 snapshot and an
explicit request. Its snapshot hash establishes which state was read; it does
not establish that the state is historically true or reachable from disclosures.
The reference supports one event kind: the existing proportional sale of a
divisible homogeneous recovered inventory lot. Native recognition, posting,
tax-history invalidation and refusal rules remain unchanged.

The request contains profile, id, expected_state_sha256, context, decision_date,
scenario, model, bindings, output_map and event. The scenario must explicitly
declare an authored_closed_path and its premise: the snapshot plus listed
decisions has no omitted intervening economic event. Decision and event occur
on the same authored calendar date, not before the snapshot or outside its
fiscal period. This day-level choice cannot resolve intraday order; a sequence
orders same-date decisions explicitly. The engine discovers no dates.

The model contains a CompanyFunctions/1 program, available_on date (or unknown)
and provenance. Program inputs must have unknown placeholder values. Every
input has one binding: state_lot_units for the selected lot, state_cash, or a
scenario value with its own available_on date (or unknown) and provenance.
Bindings have the program input's declared type. State projections have exact
quantity or currency units and a context derived from the complete book context.
They read current executed state in this authored scenario, not future inputs.
Missing, future or unknown availability replaces a scenario input with unknown
for evaluation; it does not erase the supplied record or create a false value.
All bindings are syntactically/type checked even when unused. A future or
undated model leaves the decision unresolved without evaluating its rule.

output_map names exactly three declared outputs: execute (Boolean), sold_units
(the selected lot's quantity type) and proceeds (the book's monetary type).
Compile the entire program first. Evaluate only execute initially. False gives
no_action, with no event or journal; an unknown guard gives unresolved. For a
true guard, evaluate all outputs. Unknown units/proceeds remain unresolved;
invalid arithmetic remains invalid. A known request proposes the native event
with explicit id, same-day date, method, lot_id and all six caller-supplied
findings. A proposal does not establish performance or commit a sale.

apply recomputes and compares the complete proposal against the current state
and request, then calls the unchanged native transition. A stale state, altered
request or rehashed altered result refuses. Native unresolved/unsupported/invalid
outcomes remain distinct. No-action retains the exact state; successful apply
returns a new conditional state and the full native transition. It performs no
database commit and supplies no durable exactly-once guarantee.

run_sequence accepts at most 64 explicitly dated, hash-bound requests. It keeps
the successful/no-action prefix, rejects duplicate decision identities and
backward dates, and stops on the first unresolved/refused request. The state
remains at the last successful event, while the decision cursor records later
no-actions. Remaining requests, full statements and native operation traces stay
visible. No refused branch is converted to a zero result or annual completion.
Financial statement fields equal the native statement function. Two descriptive
fields are deliberately replaced: scope describes the authored decision prefix,
and unresolved uses the current annual interface's outstanding questions rather
than the older statement helper's obsolete implementation-status text.

The authored demonstration sells min(demand,max(stock-reserve,0)) at a declared
price. It is a test hypothesis, not an empirical model or default sales policy.
The example constructor rejects negative demand, reserve or price explicitly.
The generic typed interface imposes no such economic premise: a different
authored policy may use signed inputs, and native sale restrictions still apply
to any proposed quantities and proceeds.
Two decisions must respond to the residual stock rather than reuse the original
quantity. A reserve above stock produces no action, not negative selling. The
native method's performance-complete finding remains explicit. General sales,
credit collections, financing, simultaneous decisions, event-date discovery,
historical information admission and predictive evaluation remain open.
