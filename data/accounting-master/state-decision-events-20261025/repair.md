# Focused candidate repair — 25 October 2026

The first eight-method run failed only on the statement scope description.
The expanded23-method run exposed a second deliberately replaced descriptive
field, unresolved. Financial statement amounts and complete native transitions
matched. The final comparison checks every other native field exactly and checks
both replacements against their declared meaning; it does not omit financial
amounts or silently claim byte equality for the whole report wrapper.

Code inspection found failure(ValueError()) could itself raise IndexError, and
an unexpected exception status could escape normalization. The handler now
retains native reasons, emits a nonempty fallback for empty exceptions and maps
unexpected statuses to invalid. Focused tests exercise both cases.

The example claimed nonnegative demand/reserve/price but did not enforce that
domain. Its constructor now rejects negative assumptions; no such premise was
added to the general typed interface. Direct requests with signed inputs remain
governed by their authored rule and the native method's quantity/proceeds checks.
Initial implementation, example and eight-method test file are in attempt-01.

These are engineering and fixture repairs. They provide no evidence of actual
company behavior, accounting compliance or predictive accuracy.

Final review also found native refusal outcomes dropped the generated proposal.
Apply now retains it under decision, separately from the native refusal status
and reason. Tests check that false and unknown findings remain inspectable.
