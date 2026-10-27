# Annual program authoring, finite profile1

Typed program fields: profile=AnnualProgramAuthoring/1, name, root_sha256 and
operations. Name follows the established ASCII program-name convention. The
imports map binds root_sha256 to a complete PeriodVintageContinuation/1 request.
Require exact canonical digest and portable bounds. Build AnnualProgram/1 by
copying that root request and the exact ordered operations. Imports are explicit
caller data, never filesystem or network resolution.

Text grammar is one semicolon-terminated declaration per nonblank line:
annual_program followed by quoted profile and name; import_root followed by a
quoted digest; operations; zero or more operation blocks; end_operations;
end_program. An operation header has quoted kind and quoted event id. Each
operation ends with end_operation. Preserve input order.

Operation fields: native has module and native_event (event id must match the
header); allocated_tax_payment has date, amount, authorization and zero or more
payment_allocation records. current_assessment has mode, model, interval,
information entries (quoted key plus declaration), adjustment records,
loss_model, utilization_cap, loss_use records and generation. deferred_assessment
has model, measurement, finding entries, recovery_capacity and item records.
provisional_carry has model, next_period and finding entries. Map duplicates and
repeated scalar fields reject; ordered list declarations retain their order.
Every required singleton is explicit; collections may be empty structurally.

Closed structural checks validate exact operation shapes, calendar dates,
canonical rational fields and known/unknown types with provenance. They do not
test whether a known authorization is true or a payment fits cash. The semantic
evaluator retains those decisions. Repeated operation ids are rejected as
authoring identity ambiguity; imported historical-id conflicts remain semantic.

Compilation returns the typed program, lowered request, their canonical
digests, raw source SHA256 for text (null for typed), and source spans for the
program/import and each operation (start/end line plus field lines). No financial
execution occurs during compile. Execution calls the frozen evaluator with that
exact request; result equality is semantic, while raw-source hashes/spans may
differ under whitespace changes. Canonical rendering round-trips the typed
program. Unsupported syntax and unresolved imported roots remain explicit.
