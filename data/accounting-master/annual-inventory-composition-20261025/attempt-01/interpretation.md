# Refusal-order diagnostic corrected

The original stale-measurement fixture attempted measurement immediately after
new inventory activity. The protected evaluator first requires a new current
assessment,so it correctly returned unresolved/current_assessment_required
before inspecting the old state digest. Expecting invalid at that point was
wrong relative to the preserved prerequisite order.

Retain that case as measurement_without_reassessment with unresolved status.
Add a separate case that performs fresh current reassessment,updates only the
measurement date and retains the obsolete state digest. That case reaches the
staleness check and must be invalid. No implementation change is warranted.
