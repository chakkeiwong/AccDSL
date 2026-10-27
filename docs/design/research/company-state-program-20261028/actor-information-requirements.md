# Actor information and native operation requirements

A company's economic state, its accounting records and an actor's information
are different inputs to a decision. An operation may read a financial balance
without authorizing every actor to observe it. A source may be public before
the system receives it, or may be in the system without evidence that a manager
received it. The common request therefore preserves the actor, the requested
observation or action, economic time, decision cutoff, system cutoff and
separate receipt and authority references. Unknown access remains a request
obligation. Supplied reference strings confer no admission.

## Exact native information responsibilities

The current company-path inspection and policy-effect operators accept an
archival audit view. CompanyNativeRequest/1 explicitly refuses actor uses.
Its date-time validation checks syntax only; it performs no actor-time
projection, rounding or chronology inference. A later admitted mapping must
retain the precision and uncertainty rules of its native information owner.

BankAssessment/1 already supplies a conditional information mechanism. Its
Auditor.information(root, view_ref) follows the entire semantic dependency
closure, including superseded vintages, to each Evidence record. For every
record it checks membership in View.evidence_refs, available_at no later than
View.decision_at, ingested_at no later than View.system_asof, and
measurement_asof no later than the decision's UTC day. A later model vintage
does not automatically alter the earlier published result. These are declared
query rules, not proof that the View corresponds to an actual human actor.

The BankAssessmentExactTime/1 successor separately specifies exact instants
with known UTC offsets and at most18 fractional digits. Its envelope/schema
locks and receipts differ from the older profile. The successor inherits the
reviewed financial calculations while adapting exact clock comparisons and
two UTC-day projections. Do not send new envelopes through old replay keys or
silently narrow timestamp precision. Its retained result documents33 complete
positive publications,30 timing cases,42 replays and28 refusal/replay controls.
Those synthetic tests remain scoped to that successor.

| Common requirement | Native binding that must agree | Unresolved meaning |
| --- | --- | --- |
| Requested observation | Exact OperationRequest operation/tag, signature, typed arguments and payload kind | No arbitrary observation projection is defined |
| Selected information | OperationRequest.view_ref and the input's view_ref; View evidence closure and cutoffs | A View identifier is not an authenticated actor identity |
| Economic and accounting context | Input context, measurement dates, expected accounting head and owner | Actual issuer/population and legal facts require separate admission |
| Decision/system cutoffs | View.decision_at and View.system_asof using the selected version's time rules | Supplied cutoffs do not prove receipt chronology |
| Receipt requirements | Evidence membership and available_at/ingested_at checks; exact query publication receipt | Query publication receipt is not proof of human receipt |
| Authority requirements | Only a declared read signature is supported by these assessment operations | No trading, distribution or posting permission is inferred |
| Action semantics | bank.policy.describe@1 returns the supplied policy specification | No selected action, optimization or feasibility verdict |

The three bank operations are bank.regulatory.assess@1, bank.loss.query@1 and
bank.policy.describe@1. Each has its own input and expected result kind. A
capital or loss query publishes a read result and changes no accounting book.
A policy description preserves objective, limits, settlement constraints, tie
handling and failure behavior; it does not execute or choose an action.

Historical query dependencies include identity and replay. In the older
native request validator, exact immutable submission/decoder checks precede
the identity lookup. Exact retry returns the recorded result before current
view/head freshness checks. Changed bytes under the same workspace/request
identity are refused. The exact-time successor first validates its own
profile/schema/signature and then delegates to that native sequence. A common
wrapper must not change this ordering or recompute a historical answer using
new information. Partial, unresolved and lost-acknowledgement records retain
their native meanings; an unknown acknowledgement is not rollback.

## Requirements for any future actor adapter

An adapter must bind an actor requirement to one exact native View and
operation, supported context and population, declared evidence closure,
receipt/authority interpretation and output projection. Each supported
observation field must name its original owner. Each proposed action must
name its preconditions, read set, effect owner and refusal behavior. Missing
bindings remain unresolved or unsupported under the chosen native contract;
an audit trace is never a substitute for the permitted observation. An actor's
belief update is a separate modeled operation, with its prior, likelihood or
set interpretation supplied explicitly.

No general actor adapter is introduced here. This definition identifies its
required meanings and preserves the scoped native mechanism already present.
Actual source availability, principal identity, authority and receipt belong
to T03/C01. Industry-specific operation/composition implementation belongs
to T05; endogenous decision/information mechanisms remain in T07 and its
research dependencies. These assignments retain T01's definition criterion
without making it wait for its own downstream implementation.

Authorities inspected: extended-method-exchanges-20261015/bank-assessment/
semantic-contract.md and verify_exchanges.py, and
exact-bank-profile-adoption-20261026/semantic-contract.md, successor.py and
result.md, all under data/accounting-master. The separate review manifest
records exact source bytes.
