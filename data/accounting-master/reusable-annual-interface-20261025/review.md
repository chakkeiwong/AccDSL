# Implementation review — 25 October 2026

The common evaluator removes the fixed old_v,current_v destructuring and the
fixed predecessor lookup from period operations. The imported root is recomputed
once; its complete result remains available. Stable liability ids survive
payments, cumulative replacement and later carries. New current assessments
append a row, while replacement updates only the same current liability.

Independent controls cover three liabilities followed by four in another
period. The same carry operation repeats twice. Current expense is3 after
replacement, payable19/4 and cash701/2. Carry closes profit-5 into retained73/4.
Next assessment2 gives payable27/4, with zero new-period cash movement; a further
carry sets retained81/4. Funding failures, paid-tax refund refusal, loss expiry,
fresh-measurement and stale-recognition rejection are checked.

The deferred arithmetic is copied from the inspected protected implementation
with only explicit period-state population/classification dependencies changed.
It does not patch global variables or pretend a fabricated predecessor was
executed. The same item, basis, recorded-balance and capacity identities apply.

Review found that imported period rights must include intermediate trace states,
not just opening and ending rights. The importer now retains that union and a
focused assertion checks it. The complete suite and conformance must be rerun
against those exact bytes before recording. A checker syntax typo was also
repaired; neither issue changed a frozen predecessor.

Main remaining weakness: the imported book and selected event/tax models are
bounded synthetic profiles. Repetition of this financial recurrence is not
evidence for source admission, actual fiscal completeness, every accounting
rule or general company authoring. Full history increases output size, so
serialization/resource behavior remains a distinct engineering obligation.
No statistical ranking is relevant to these exact deterministic controls.
