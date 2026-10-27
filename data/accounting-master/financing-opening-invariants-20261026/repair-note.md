# Opening-versus-snapshot test repair

26 October 2026. Attempt-01 preserved, not rerun.

The first conformance attempt failed at alpha.early.imported.1. The verifier
wrongly expected an intermediate financed state dated 29 June to qualify as a
new fiscal opening. The preserved report engine correctly requires opening
date equal to fiscal start, no opening cash-flow records and zero temporary
balances. Its refusal was opening_report:opening_at_period_start.

This invalidates that verifier expectation, not the E01 oracle or financing
relations. Attempt-02 requires retained intermediate/final states to satisfy
snapshot and supplied-history checks while still refusing fiscal-opening
admission. Only the original fiscal openings are accepted. History assessment
is exposed separately so a history-erasure discriminator is actually tested
at its intended boundary rather than masked by the earlier opening refusal.
No fiscal engine, frozen result, economic relation or accounting assumption
was changed. General carry/import remains a later task.
