# ModuleInvocation/1 reference

This finite caller gives four retained modules one request envelope while
preserving their different meanings. A successful return from the caller says
that a module answered; the separate native status says whether it proposed a
transition, refused one, returned a report, or assessed measurements.

| module_id | Capability | Operation | Original input |
| --- | --- | --- | --- |
| typed_return | transition_proposal | propose | state_text, state_raw_sha256, event_text, event_raw_sha256 |
| shared_lease | transition_proposal | propose | state, event |
| henkel_measurements | measurement | assess | request, budget |
| sector_report | report | report | request |

ModuleInvocation/1 is a closed object with profile, module_id, operation,
registry_sha256, descriptor_sha256, payload_sha256, and payload. The registry
is code-owned and finite. Its identity binds the caller source, native code,
schema authorities and the fixed dependency-lock file. Digests use UTF-8 JSON
with sorted keys and compact separators. Strings, integers, booleans, null,
arrays and string-key objects are portable input values. Floats and callables
are rejected. Requests are limited to 2 MB, 100,000 nodes and depth 64.
Typed-return raw text retains its independent UTF-8 byte digest and duplicate
JSON-key rejection. No path or callback in a request selects executable code.

ModuleResult/1 has status returned, unsupported, or invalid. Returned results
contain capability, operation, request/descriptor/bundle identity, native_status,
the complete native_result and its digest. The wrapper derives no amounts.
A known module with the wrong operation is unsupported before native invocation.
Malformed closed fields or stale digests are invalid. Native refusal results
remain inside returned and keep their original status and reason.

All results set executed, committed, physical_durability, source_admission,
accounting_admission, method_eligible and shared_book_composition_established
false. Here executed refers to applying a transition to a caller's state; a
native calculation is of course performed. Apply and commit are unsupported.
The original input is copied where necessary and never mutated.

Verification recomputes the wrapper and compares every fixed field. Native
transition and report results must match completely. Henkel measurements use
the existing native verifier, which checks a valid alternative solver witness
and permits different measured solver time. Rehashing a forged journal,
memory, flow, status or witness does not make it valid.

The trusted local Python import environment is assumed. Disk hashes detect
accidental dependency changes; this is not a sandbox for hostile code or an
atomic filesystem snapshot. Native return accepts structurally valid changed
owner/source labels. Those calls remain proposed with admission false; no
issuer evidence is invented. Lease scope changes retain their native refusal.

This reference solves invocation. Shared balances, account meanings, periods,
tax/report policies, event ordering, memory, ownership, conflict handling and
durability require separate compatibility and transition designs. A union of
the return and lease dictionaries would violate both closed native schemas.
