# Check the existing source-bound policy caller before integrating repair

28 October2026. C04/T03;MC03/11/25/33. The bare finite solver accepts
an incomplete table; the new bound-request adapter rejects altered requests.
Inspection finds an existing stronger boundary in observation-map-binding:
prepare reconstructs rows from protected Evidence and externally bound
family/declaration, and verify_previous reconstructs prior rows/kernel.
Do not replace this machinery with the small new adapter or assume the
bare-entrypoint defect affects the bound caller.

Question: does the existing bound caller reject the missing-row path and
recompute the complete policy set from protected inputs? Baseline is the
retained baseline family/declaration and saved expected result from its
attempt01, plus existing independent expected-row construction. Compare full
rows and full policy sets; counts alone do not pass. Drop a prior row or a
kernel row while supplying both original and recomputed outer identities;
structural verification must still refuse. Remove a family support or a
required declaration map/key; exact binding must reject. Inputs must remain
unchanged. The common CompanyNativeRequest dispatcher has only state,
policy-effect and report capabilities, and refuses actor operations; do not
invent a policy-solver integration there.

Audit passes: existing code and externally pinned source locks are primary;
no protected code mutation or new model assumptions. Exact selected caller
checks only. If direct source locks fail, record invalid evidence and repair
the audit, not the frozen source. Passing establishes this bounded caller's
transport/support protection, not source truth, actual actor knowledge or
all repository callers. Save result and source hashes in a new exclusive
caller-attempt01 under future-demand-failures. Continue original failures
and source work after recording the precise residual.

