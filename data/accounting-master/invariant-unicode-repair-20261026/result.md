# Invariant source Unicode preservation

26 October 2026. The repaired parser preserves U+0085, U+2028 and U+2029 as
data inside quoted invariant strings. The earlier parser used Python splitlines
in both its physical-line reader and embedded guarded-rule renderer. Each of
the nine probes reproduces the earlier unterminated-string failure and then
roundtrips exactly through the repaired parser. The probes place each character
in an invariant residual, guarded-rule residual and guarded input source reference.

All eight retained programs and 54 commands reproduce every source-result field,
including both serialization-order identities. All 32 prior controls reproduce
their complete saved records. Nine Unicode cases preserve the edited typed
program and complete execution under an explicitly supplied revised test
selection. The original selection refuses those edits. LF and CRLF cases retain
correct physical lines, UTF-8 bounds and slice hashes after the separator.
The final run has 41 controls, 2,782 assertions and 584 protected files.
Most assertions are preservation/location checks, not distinct financial cases.

Four copied modules have exact recorded deltas: two line-splitting corrections
in the invariant parser, two explicit successor imports in company wrappers,
and one successor import in the reused controls. All financial evaluators and
frozen predecessors remain unchanged. Native lifecycle and operating builder
callbacks are disabled during the comparisons. Existing source profiles keep
their meanings; the corrected implementation identity is explicit.

| Decision | Primary criterion | Veto status | Main uncertainty | Next action | Not concluded |
|---|---|---|---|---|---|
| Retain the compatibility repair | Exact typed/source roundtrips, all retained full results/controls and nine reproduced defects pass | No changed frozen file, financial difference or location regression | Wider language algorithms and independent implementation remain incomplete | Correct the manuscript's Unicode scope and successor evidence pointer | General Unicode/security certification, accounting correctness or product readiness |

Run and environment are recorded in run-manifest.json. source-preservation.json
records every permitted copied-file change. Raw full results, sources and adverse
cases are retained separately. This is deterministic engineering evidence, not
a statistical ranking. No whole requirement closes; S6 held and E3 deferred.

Post-run red team: an LF-only reader might accidentally accept malformed CR
forms or silently change an old diagnostic. Existing controls and unchanged
control validation remain, while exact prior-control equality checks the latter.
The Unicode cases only establish the specified quoted-data positions; they do
not establish every possible Unicode behavior in every predecessor frontend.
