# DeclaredCompanyProgram/1

MC02/06/11/13–18/23–26/28/32/34/35; S2–S5, bounded synthetic reference only.

Program fields: profile, name, opening, schemas, registry, mapping, commands.
Opening must be a valid closed-temporary-account period opening. Registry and
mapping use the checked CompanyMethodRegistry/1 and CompanyStatementMap/1.
Every registry schema must occur identically in schemas. No Python callback,
future-state hash, expected journal or future book is an authored command input.

Commands are a finite list of at most 64 records:
- event: kind, method_key, event (id/date/typed inputs).
- report: kind, id, cutoff, equity_movements, notes.
- carry: report fields plus retained_account, next_end_exclusive, memory_policies.

Validate every command shape, scalar date and method structure before executing.
Validate the registry with unknown placeholders at the valid initial date;
prerequisites are not evaluated there. Runtime validates nondecreasing dates,
period membership, unused identities, findings and current-state controls.
Unsupported clock families and unknown methods remain unsupported. Malformed
programs return invalid with no execution. Economic refusal preserves the full
successful prefix and the exact attempted command, request and underlying result.

The authored order is authoritative, including equal dates. Each report/carry
cutoff explicitly advances a cloned observation date; no event, flow or memory is
invented. Commit that provisional observation only if the whole command succeeds.
Trace both original and observed hashes and the supplied cutoff. A failed command
retains the previous current book and period opening, not the attempted cutoff.
Dates do not prove omitted events absent. All admission/completeness flags stay
false. Successful report IDs are program-local; event/close IDs also enter lifetime
book history. All command IDs share a run-local namespace, seeded with seen IDs.

Build every engine request from current at the command's turn. A report uses the
actual current-period opening. A carry recomputes its report and sets both current
and opening to next_opening. Each report supplies its own explicit period-to-date
equity explanations and unresolved notes; none are silently copied across carry.
Trace records include complete command/request/result and before/after/opening
hashes. Report/archive indexes point to their trace records by digest. Pure replay
recomputes the whole result using canonical JSON equality; it does not resume a
prefix, accept edits under an old identity, or claim a durable storage commit.

Bounds: inherited request JSON limit and 64 commands; an explicit 8 MiB trace
budget is a convenience safety bound, not a scale claim. Exceeding it stops before
adding that command and preserves the prefix; a bounded digest summary identifies
the refused oversized result. Tests must check the boundary. Failed programs do
not automatically execute later independent commands because their dates and
opening may depend on the failed carry. Repair and rerun is a separate proposal.
