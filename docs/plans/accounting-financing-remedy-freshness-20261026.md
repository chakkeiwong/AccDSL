# Bind conditional remedies to the observed financial state

26 October 2026. W05/W16; MC05/13/16/17/20/24/25/28/33/34/35.
Continue the authorised master program from Version 5.15. The previous
date-only remedy adapter is rejected by its retained same-day discriminator.
Its typed E03 classification table remains useful and its evidence is frozen.

Question: can a conditional finding be reused only while its relevant economic
state, observation date and supplied evidence revision still match, without
making the adapter's own status writes invalidate the finding?

Use a new successor directory, financing-remedy-freshness-20261026. Preserve
the existing translation and runtime. Add an explicit observation stamp to the
contract memory: economic-state digest, evidence revision and clause route.
The economic projection preserves the complete book except contract-status
memory, event IDs and current observation date; those exclusions are deliberate.
Dates are checked separately, contract-status changes are the adapter's own
updates, and event IDs alone do not establish an economic change. Balances,
flows, other memory, periods, context, accounts and types remain in the digest.
An evidence revision is an explicitly supplied immutable-view identifier. It
does not prove that all outside evidence has been acquired or is current.

Primary criterion: the saved same-day payment discriminator is refused as
unresolved with no changed state; fresh findings allow the corresponding
conditional decision. Complete original trace states, journals and flows match
independent expectations after the declared schema/stamp additions. All 58
E03 classifications retain their outcomes. Additional cases cover changed
evidence revision, same-date economic changes, harmless remedy writes, stale
dates, route/category mismatches, unknown findings and false supplied existing
acceleration. Source/native-classifier callbacks remain disabled in candidate
classification runs. Preserve all predecessor hashes and evidence attempts.

Skeptical review before implementation: a date match is the wrong baseline for
freshness. A full-state digest would also be wrong because recording the finding
changes that state. The explicitly projected digest is conservative: unrelated
economic changes can require reassessment, but cannot justify a stale finding.
A digest alone cannot detect a corrected external fact with unchanged books;
the supplied evidence revision therefore participates in the binding. A caller
can still supply a false or incomplete view, so actual-source admission remains
open. Clauses that are not bankruptcy clauses must not inherit an automatic
bankruptcy acceleration route. A current selected-clause result cannot certify
that no other event exists. Tests target these distinctions, not test counts.

Promotion vetoes: stale evidence accepted, new acceleration inferred from a
different clause category, mutation of refused prefixes, changed frozen source,
or a complete-state mismatch. A comparator error triggers repair in a fresh
attempt. No stochastic ranking, legal admission, or production inference follows.
The existing deterministic CPU environment is a convenience adequate for exact
state checks; use CUDA_VISIBLE_DEVICES=-1 and PYTHONDONTWRITEBYTECODE=1.
No training, installs, agents or external actions. The reviewed plan passes
for this bounded successor repair, not for whole-financing completion.

After the check passes, integrate the coherent financing and inference
companions into a protected manuscript successor, with source-preservation,
build and rendered-page checks. Refresh the master and full gap queue with
the exact completed scope and remaining source/method dependencies. Finish
feasible internal work; human acceptance stays distinct from drafting.
