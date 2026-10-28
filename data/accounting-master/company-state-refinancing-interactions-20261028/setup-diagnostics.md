# Retained setup diagnostics

Setup01 was refused before execution: opening_report:duplicate_line_id.
The shared native book already contains tax_payable; the fixture added a second
report line with that identity. setup-01.json.gz preserves the refusal.
Repair: reuse the existing account and report mapping where the role exists.
This is a fixture wiring defect, not evidence against the interaction design.
The independent numerical comparator and all supplied premises are unchanged.

Attempt01 correctly refused an inconsistent event rename as invalid: flow_event.
The harness expected stale, but changed the seen ID without the linked cash-flow
event ID. Repair the test: retain the broken-link invalid control, and separately
rename the event and its linked flow coherently before testing stale reuse.
The validated native book invariant is stronger than the original test assumed.
Attempt01 and its exact local sources remain preserved.
