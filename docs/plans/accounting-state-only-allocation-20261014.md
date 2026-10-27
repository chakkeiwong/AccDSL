# P17-10 continuation: state-only advance allocation

14 October 2026. MC02/04/11/13/15/24–27/32–35; E14/G2/G4/G12/G17/G18.
Protected manuscript: Version 2.76. The ready input is the 2.75 advance method,
not a new runtime campaign. Preserve all native acquisition examples and the
portable L1/I1/P2/A1 contract versions.

## Question and skeptical audit

Can a compatible implementation consume prepaid credit once when the new bill
has no unpaid amount? The baseline is the current separate authored posting
path, which requires a pinned profile-specific JournalProposal/EconomicDelta
schema. The native acquisition journal explicitly requires nonempty lines and
cannot represent this event. Weakening that frozen schema would be a wrong
baseline. Treating all empty journals as no-ops would lose economic state;
inventing offsetting zero/monetary lines would conceal the operation.

The audit passes with a new explicitly synthetic, versioned advance-allocation
profile and complete portable exchanges. No generic schema is silently widened.
L1 requires full typed dependency and byte closure, including the schema/package
lock. I1 fingerprints request_id, execution and expected head; P2 looks up the
business identity before current-head freshness. A changed request_id is a
conflict for a committed event, even with unchanged economic amounts. A replay
must return the original receipt and make no new state change. A1 authorization
and prelookup binding checks apply to a state-only event exactly as to a monetary
one. A domain candidate mismatch must be detected from independent formulas,
not by hashing the author's expected answer.

## Evidence contract and assumptions

The primary criterion is a closed, independently reconstructible request,
authorization, empty-line proposal, independent economic delta, closing state,
receipt and response, plus replay/conflict/stale/adverse outcomes. Reject
unclosed or cyclic references, unsupported profile/mode, false authorization,
nonzero monetary effect hidden by empty lines, reused credit, or any partial
domain mutation. Hashes and zero journal balance are integrity diagnostics;
neither establishes accounting validity, persistence durability or runtime
compatibility. All data are declared synthetic and deterministic.

Initial state: one fixed-price 100 contract, cash advance 30, no performance
or prior bills, cash 30/contract liability 30, advance A1 unused 30. New bill
I1 has gross 30 and applies all 30. Cumulative gross G and applied K both
rise from 0 to 30; T=G+A−K remains 30. AR, CA, CL, cash and revenue have zero
changes, while invoice and allocation state change. The authority/source and
method limitations remain the historical AASB15 extension's stated scope.
These are authored facts, not issuer records or a grant of real-book permission.

Use exact portable reduced rationals, canonical sorted dependencies and full
request fingerprints. An explicit journal variant has `effect=state_only`,
empty ordered lines and zero changes for every chart account; it still names
basis and authorization. Independent delta requires a genuine nonzero
allocation update. The atomic transition publishes proposal, delta, closing
state, receipt and business-identity index and advances the branch generation
once. No database, compiler or production endpoint is implemented.

## Bounded execution and acceptance cases

1. Write a method/interface supplement and closed record schemas, pin source
   and predecessor contract files, and produce a complete portable registry
   and exact request-submission bytes. Bind schema/package definitions without
   a reference cycle. The schema lock pins a separate byte artifact.
2. Produce complete expected positive, exact replay, changed-payload conflict,
   changed-request-id conflict, absent-key stale-head and repeated-credit
   cases. Add false authorization, unsupported profile and a balanced-empty
   proposal with nonzero account delta. Distinguish invalid submitted fields
   from a producer's semantically wrong candidate.
3. Independently verify schema/reference/byte closure and derive balances,
   allocations, identity/fingerprint behavior and before/after domain views.
   Preserve all rejection states and original receipts. The checker validates
   documentary fixtures only; no live book is written.
4. Integrate the operative rules and small numerical example in a protected
   successor to 2.76; preserve equations/citations, build and inspect affected
   pages. Refresh master/checkpoint and the next operation plan. P17-10 stays
   open for other adapter/interface decisions.

Evidence: `data/accounting-master/p17-completion-20261014/P17-10/state-only/`.
A source or profile claim may remain unsupported without stopping independent
work. Repair malformed artifacts before using them. Runtime/controller remains
held; no external communication, fee, publication or dependency installation.
