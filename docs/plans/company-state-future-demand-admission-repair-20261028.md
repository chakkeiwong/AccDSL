# Repair the unbound finite-policy input boundary

28 October2026. C04;MC03/11/25/26/33. The initial79-check complete-table
comparison passes. A subsequent debug probe removes only the demand0/order1
refusal, retaining order1 in another hidden world. Native observable-cell
coverage still passes and returns order1 as feasible. The full table has
no robust exact-match policy. This is a demonstrated input-boundary gap,
not a failure of the solver on complete admitted rows. The inherited native
contract relies on protected full support; the bare entrypoint cannot
establish that support by observable-cell action coverage alone.

Preserve native policy/oracle and initial result. Add a small explicit
bound-request adapter for this finite profile: canonical JSON identity covers
all rows, both action domains and revelation regime; compare it to an
externally held expected request identity before running native code. Pin
native implementation identity too. Do not accept a request's self-reported
hash as authority. Return native full policy sets unchanged once admitted.

Baseline/comparator: independently constructed complete-table hand/oracle
sets from attempt01. Tests must reject each dropped row, a missing world,
changed status/message/regime/action domain and duplicate, while preserving
the complete exact, overstock and independent outcomes. Include an honest
changed-question expected identity to show explicit new admission is a
separate request. No general discovery of absent unknown worlds is claimed;
the external expected identity itself requires independent full-source
construction and cannot be supplied by an untrusted payload.

Pass criterion: complete full sets preserved and all mutations rejected
before native execution. Wrong canonicalization or source mismatch vetoes
the adapter and triggers repair. Counts are explanatory. This is a scoped
admission guard, not authentication of real actors or source truth, a new
policy solver, or global nonanticipativity enforcement. Keep failed native
probe, scripts, inputs, manifests and repair result. No protected code changes.

