# Native measurement binding result — 28 October 2026

All 65 checks pass in attempt-01. The new inventory and insurance definitions
execute through unchanged TemporalMeasurementConstraints/1 and its rational
solver. Sixteen loaded native source files retain their hashes. The complete
requests, results, lowering, independent witnesses and refusals are retained.

Inventory lowers to opening - cost - closing = 0 with exact civil-date roles.
The expected witness is (1000,300,700); a cost of700 with closing700 is
conditionally infeasible and its conflict is rechecked. Missing identity
premises remain unresolved and a wrong closing date remains invalid.

The finite insurance diagnostic gives H-r+n=5 with H=6, 0<=r<=3 and 0<=n<=2.
Both complete witnesses (H,r,n)=(6,1,0) and (6,3,2) pass the native exact
witness checker. Adding n=2 gives r=3 in that restricted problem. The finite
bounds are explicit diagnostic hypotheses, not actuarial bounds and not a
replacement for the larger ray proved in the research note. A solver-selected
witness never establishes a unique or actual state.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Reuse native measurement interface for these relations | Complete lowering and independently checked witnesses agree | No source drift or numeric veto | General history construction and mapping are absent | Bind explicit history/state dependencies and information views | A new production adapter or complete reconstruction |
| Preserve unresolved and unknown | Missing premise and zero-cell budget return native statuses | No false infeasibility | Resources and premises can limit other cases | Keep status distinctions through future composition | Feasibility under missing evidence |
| Preserve source/opening boundary | No execution/source admission; direct opening call refuses | Admission flags remain false | Full history, mappings and obligations still required | Construct the missing typed history before an opening | Actual issuer state or historical cutoff approval |

The declared command ran on repository Python with the installed z3 package;
the manifest records its version, CPU-only scope, wall time, HEAD and outputs.
No dependency installation, product-source edits, stochastic comparison or GPU
work occurred. The numerical checks are not evidence of predictive accuracy.

Post-run red team: the selected linear examples fit the native domain by
construction. Nonlinear accounting measurements, changing populations, source
truth and the completeness of latent histories remain outside the result.
The separate publication/ingestion diagnostic is not implemented by the native
temporal interface; current native opening provenance still explicitly says
investor_information_cutoff_checked=false.
