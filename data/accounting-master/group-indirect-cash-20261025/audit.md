# Group bridge implementation audit

25 October2026. The governing pre-run contract is
docs/plans/accounting-group-indirect-cash-20261025.md. This is deterministic
conformance of a supplied two-book example, not an accounting-policy claim.

The original group examples have no asymmetric operating-flow removal, so a
zero correction alone would be an inadequate comparator. Two extra category
combinations require +30 and −30 corrections respectively. The original books
have literal flow IDs; executed flows use event/local-ID hashes. The plan
records the exact translation and one added empty input schema before testing.
All other book fields and full adapted requests/reports must match exactly.

The first small probe failed with requirements because its constructed method
had an empty postcondition list. The frozen engine correctly requires a nonempty
requirement population. The fixture now checks nonnegative closing cash instead
of weakening that engine. Initial log: /tmp/accdsl-group-indirect-probe.log.
This is a fixture implementation failure, not evidence against group cash-flow
composition. No failed candidate has been accepted or frozen.

The wrapper recomputes both the group report and each legal indirect bridge,
binds exact selected opening/closing and complete report requests/results, and
retains raw legal sums plus per-pair corrections. The current group method does
not alter profit; this restriction is checked explicitly. Supplied full ownership,
pair population and accounting classifications remain unadmitted.

The repaired discriminators pass: raw operating−10 plus30 gives20; raw50
minus30 gives20. Fourteen focused tests then pass in5.341 seconds. They cover
two charts/four category combinations, unchanged complete adapted reports,
unrelated valid traces, swapped owners, forged rehashed results, stale/reused
pairs, exact owner population, gross zero-net pairs and dependency changes.
An omitted pair remains explicitly incomplete rather than being inferred:
the explanation matches the supplied group report and leaves completeness false.

Record/replay now runs those14 focused tests and the existing group-period,
compatible-composition, company-report and legal-indirect test files. Cases
are stored separately; replay requires exact complete objects and source hashes.
This regression extends checks only across the directly used dependencies.
