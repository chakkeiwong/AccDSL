# Dated nominal credit components: evidence contract

27 October 2026. Plan: docs/plans/accounting-credit-claim-continuity-20261027.md.
MC03/05/08/11/13/15/16/17/19/24/25/26/28/33/34; W07/09/11/12/16/17.

Question: do all nine retained schedules admit a complete per-date rollforward
which distinguishes collections, uncollected scheduled amounts, removed
write-off portions, remaining schedules and signed noncredit replacements?
Candidate: a read-only projection of the pinned requests and results. Comparator:
independently authored endpoint amounts, an independent additive movement
calculation, and every original native stage/archive. No financial engine edit.

Pass requires complete event-ordered records and exact rational equality at each
due date and each stage, with zero entries retained. It also requires binding
the original request, result, context, event and write-off portion identities,
and unchanged source files. Summed endpoints and assertion counts are explanatory
only. Source drift, mismatched archives, lost components, or altered native
journals veto acceptance and trigger repair. Three fresh attempts, 120 seconds
each, are the continuation limit for this unit; other packages remain ready.

The independent calculation will use dated additive movements and native
schedule snapshots, rather than calling the candidate's transition routine.
Authored endpoint amounts are fixed before candidate execution. Controls include
same-total date swaps, duplicate/lost portions, erased zero entries, hidden
replacements, stale/rehashed identities, false forgiveness and admission, and
misclassifying removed nominal schedules as collections. Controls must be
rejected even if a modified record is given a fresh content hash.

Research intent: financial derecognition and nominal schedule accounting are
different questions. The expected failure is a balanced aggregate which hides
a missing dated component or implies legal forgiveness. Complete records are the
criterion; source drift and failed identities are vetoes; a later-event refusal
explains an interface limit rather than a failed nominal reconciliation. Passing
does not establish legal rights, standards admission, future recovery, host-book
posting, or an unbounded simulator.

Default audit: exact rational nominal amounts come from supplied requests;
their provenance and units are retained. No probability or discount rate is
introduced. Dates and ordering follow the retained engine, including accrual
stages without nominal changes. A zero-valued schedule entry is distinct from
absence. Prepayment replaces the modeled receipt schedule under the supplied
unchanged-terms finding; it is not reclassified as a legal amendment. Legal
forgiveness stays not_assessed. All nine endpoints happen to close financially;
the candidate does not infer a legal outcome from that closure.

Artifacts: source-lock.json, authored-endpoints.json, claim.py, verify.py,
attempt-NN/{cases,checks,controls,run-manifest}.json and result.md. Manifest records
actual command, environment, commit, CPU-only execution, timings and paths.
Successful one-shot evidence writers will not be rerun.
