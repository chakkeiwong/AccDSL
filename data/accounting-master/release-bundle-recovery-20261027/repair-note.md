# Attempt 01 harness repair

All three positive and eight schema-valid negative semantic checks passed in
the relocated directory. The corruption preflight fixture then failed while
creating the already existing root parent of README.md. This is a harness path
construction defect, not evidence against Core 0 semantics. Add exist_ok=True
to that exact parent creation and run a fresh attempt-02. Attempt-01 outputs,
its copied verifier and original error are preserved. No source evidence or
validator changed; no successful historical writer is rerun.
