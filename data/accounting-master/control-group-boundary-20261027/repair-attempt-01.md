# First verification repair

All23 accepted scope cases passed their route/history/binding checks. The first
attempt then failed because the test expected unknown_offset; the reused
exact-time parser correctly refused it as unknown_negative_zero_offset.
The implementation and refusal behaviour were unchanged. Corrected only the
test's exact expected reason, preserving attempt-01, its source snapshots and
manifest. This is a harness expectation failure, not evidence against the scope
method. Continue the remaining refusal controls in a new bounded attempt.
