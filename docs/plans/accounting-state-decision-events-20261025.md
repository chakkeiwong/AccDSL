# Generate economic events from the current annual book

25 October 2026. S2–S4; MC13/14/15/18/23/24/25/26/28/32/34/35.

## Question and research intent

Can an explicit decision rule read the current company state, propose a dated
event, and retain exactly the existing accounting consequences? The candidate
is a bounded single-lot sale policy: sell the lesser of declared demand and
stock above a declared reserve. Demand, price and reserve are authored scenario
inputs, not estimates or defaults. The rule generates a proposal, not a claim
that a real sale occurred. Its execution uses the existing conditional sale
method and all of that method's explicit findings.

The comparator is the unchanged AnnualInventoryProgram/1 transition applied to
the same manually authored sale. Primary criteria are exact event, journal,
full period-book and statement equality; an independently calculated repeated
decision case must respond to the remaining inventory. No-action, unknown
decision, invalid policy and refused accounting treatment stay distinct.
Static/type/time violations, stale state and changed protected baselines veto
the candidate. Counts, runtime and balanced journals alone are explanatory.
No behavior validity, forecasting accuracy, complete simulator, source admission
or accounting compliance is concluded.

## Skeptical audit and assumptions

Existing collection policies revise already supplied future operations. Pure
functions by themselves do not read current execution state or emit events.
The annual inventory transition already supplies the relevant conditional
accounting method; duplicating it would risk a wrong comparator. Use that exact
transition after the new decision stage and retain failed proposals separately.

The minimal experiment uses a selected existing lot and explicit decision dates
inside the current fiscal period. Dates and sequence are authored; they are not
endogenously discovered. The closed authored scenario means no omitted event
between its last state and the next declared decision. This premise must be
named, and cannot establish historical information completeness. A snapshot
hash binds each proposal to the complete book it read. Applying to a changed
book must refuse, including a rehashed altered proposal.

Numeric inputs retain exact units and a declared context. Only named projections
of lot quantity and cash may read state; all other inputs need explicit scenario
records. Future or undated availability cannot expose a value to the rule.
An unknown may be unused by a false decision guard, so it must not automatically
turn no-action into rejection. Evaluate the guard first, then event quantities
only when true; compile the entire policy statically in either case. Model
availability is distinct from input availability and must also be explicit.
Accounting findings remain the native method's responsibility.

Convenience limits bound inputs, policy graph and decision sequence; they are
not throughput claims. The stock rule and selected exact fractions are test
hypotheses with no empirical promotion. Cases at zero stock, reserve above
stock, unknown demand/price, future information and repeated calls provide cheap
diagnostics. An expired or false accounting premise blocks the event; it does
not erase earlier successful events or reject company simulation as a direction.

## Execution and evidence

1. Finish complete 53/6/46 coverage after Version4.01.
2. Write a decision/proposal contract with types, clocks, state binding, guard
   semantics, native transition dispatch, no-action and refusal results.
3. Implement a bounded optional reference and focused tests. Compare manual
   events and all statements; check repeated state-dependent decisions, stale
   snapshots, tampering, withheld information and unchanged inputs.
4. Preserve exact requests/results, tests, source locks and a run manifest.
   Separate engineering correctness from actual economic behavior evidence.
5. Integrate checked conclusions into the governing manuscript and refresh the
   full program. General schedules, financing, groups/FX, sectors, actual
   histories, scaling/migration and whole-document acceptance remain queued.

Repair trigger: candidate or fixture fails a stated check. Continuation veto:
invalid baseline, unavailable necessary source, or a choice crossing a human
decision boundary that local evidence cannot resolve. No global blocker is
currently known. Forecasting remains deferred.
