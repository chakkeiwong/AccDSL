# Preserve missing guarantee inputs without replacing native outcomes

28 October2026. C04; MC02/03/08/33/34. Supplement to the original
company-state-guarantee-failures-20261028.md evidence contract.

## Inspected result and bounded repair

Attempt01 passes244 engineering checks across46 cases. It confirms the
pre-mortem: omitted fields reject, null opening measurement is unresolved,
but null ECL/service measurements are unsupported by the hardcoded profile.
No zero imputation occurs. This rejects a claim of complete unknown-input
semantics; it does not invalidate the finite calculator or stop C04.

Add a separate read-only CompanyGuaranteeInputInspection/1 supplement,
following the existing population-inspection pattern. Keep the exact request,
missing-field/null distinction, JSON-pointer obligations and complete native
result. Pin the implementation and protected sources, and give source refusal
precedence over semantic inspection. The supplement describes incomplete
inputs; it never authorizes execution, fills values or claims to discover an
undisclosed guarantee. No native code, original status or frozen file changes.

Pass criteria: complete baseline output remains byte-equivalent after canonical
encoding; every native rejection/status survives; omitted and null values have
distinct exact pointers; known zero remains known; bad digest/implementation
or source mismatch stops inspection; repeated reads and input immutability
hold. Separate examples cover malformed shapes and unknown extra fields.
Source or identity mismatch is a continuation veto for inspection. The absent
general admissible-family mechanism remains an explicit residual for T03/C01
and C04, even if this bounded supplement passes.
