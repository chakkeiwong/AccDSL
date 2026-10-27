# Finite schedules bind decisions to the current book

StateDecisionSchedule/1 receives a complete PeriodBook/1 and a root request:
profile,id,expected_state_sha256,context,scenario,schedules. Scenario and context
retain StateDecisionEvent/1 meanings. Root snapshot identity must match exactly.
All input values are portable and bounded by the existing annual caller checker.
Its inherited limits are2,000,000 canonical serialized bytes,100,000 structure
nodes and depth64. They are defensive convenience limits. Each typed function
program remains subject to its own tighter compiler limits.

Each schedule has id,priority,calendar,template. IDs are unique nonempty text;
priority is an explicit nonnegative integer. A calendar is either explicit_dates
with a nonempty sorted unique dates array, or every_days with start,end_exclusive,
step_days. Dates are canonical ISO calendar days. Every_days uses integer calendar
days with positive step; start is included, end excluded. No month, business-day,
timezone or day-count convention is implied. All occurrences lie within the
current book's fiscal period and at/after its last event. A generated calendar
must contain1–64 occurrences; the root permits0–32 schedules and at most64 total
decisions. Equal-date occurrences need distinct priorities. An ambiguous tie is
unresolved before any economic transition. Input-array order does not break ties.

The template contains model,bindings,output_map,event. Event contains only method,
lot_id,findings. The scheduler supplies id and date. Each occurrence's decision
and event IDs use separate prefixes plus the SHA256 of root id,schedule id and
zero-based occurrence number. Identity is stable across input-array order and
calendar spelling when those occurrence dates are identical. Root request hash
separately distinguishes different schedule definitions or changed policy bytes.

Validate every calendar and template before execution. A template is checked by
StateDecisionEvent/1 prepare against the initial book at its first occurrence,
without evaluating it. That catches invalid later policies even when an earlier
decision would refuse. The runner sorts by date and explicit priority, binds a
fresh expected-state hash to each materialized request, proposes and applies the
unchanged decision runtime, and then advances. A refusal preserves the successful
and no-action prefix, exact current book, decision cursor and pending calendar.
The stop record retains the materialized request and decision outcome.

The result contains the complete scheduled calendar, schedule hash, initial-state
hash, implementation/dependency hashes, trace, stop, remaining_occurrences,
recorded_statements and fiscal_complete=false. Financial report fields equal the
existing decision sequence; scope/unresolved descriptions retain that runtime's
meaning. Admission/commit/durability flags remain false. No disk checkpoint,
restart guarantee, endogenous calendar or actual historical execution is added.
