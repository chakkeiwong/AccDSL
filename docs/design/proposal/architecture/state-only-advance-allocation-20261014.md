# State-only advance allocation: proposed portable profile

14 October 2026. P17-10; MC02/04/11/13/15/24–27/32–35. This supplement
completes the state-only case introduced by the customer-advance method.
It defines a new authored synthetic profile and documentary exchanges, not
a runtime endpoint or a revision of the frozen acquisition journal schema.

## Scope and representation

The method covers one fixed-price contract, cash advances received before
all performance and billing, and a new gross bill wholly paid by identified
unused advance credit. It shares L1's exact rational encoding, typed references,
dependency closure and canonical digest; I1's common operation envelope and
fingerprint; A1's separate PostingAuthorization; and P2's identity, freshness
and atomic commit rules. Its complete schema bundle is retained beside the
fixtures. A SchemaLock pins the bundle's exact BlobRef. Schema names identify
definitions in that bundle; they are not unresolved record references.
The lock is not embedded in its own byte artifact, avoiding a hash cycle.

All records have the exact L1 wrapper fields. All body schemas are closed and
registered by kind/schema in the bundle. The package/profile supports only
`accounting.commit@1`, the stated method and synthetic books. Supporting
authorize/propose behavior is fully specified by the predicates below; the
fixture's caller supplies their immutable candidate records. Execution mode
is `specification_example`, capability is `specified_only_no_runtime` and
accounting validity is `not_assessed`. These exchanges do not assert that a
runtime has registered the package.

The source support remains the historical AASB15.105–108 advance distinction;
the concrete amounts, rights and pre-state are authored. SyntheticAuthority
retains that distinction explicitly and the exact source/method pins. The
branch's immutable mode is synthetic, with authored evidence and an admission
in the named view. An identical-looking real-book request is not authorized
by copying these records.

The opening CompanyState includes every chart balance and the owned economic
state: contract ID and price, earned revenue R, gross billings G, total advances
A, applied advances K, later collections C, identified advances, invoices and
allocations. Allocation is retained by advance/invoice pair; each invoice
retains its gross, applied and net amounts. The domain journal has exactly
basis_ref, authorization_ref, context_ref, chart_ref, effect and lines, with
effect=`state_only` and lines=`[]`. EconomicDelta separately carries the same
bindings, zero account changes for every chart account, and exact before/after
contract state. Nonempty lines are outside this profile, including invented
offsetting or zero-valued lines. They need a supported monetary profile.

## Admission, independent calculation and commitment

Before lookup, validate decoding, closed shapes, kind/schema/digest and blob
closure, acyclicity, all identity/context/time/view/method/profile bindings and
synthetic evidence scope. Recompute the authorization against its pinned
opening state and event, rather than trusting a caller's Boolean. The method
requires a valid unused advance, a fresh invoice identity in that opening
state, positive applied credit equal to the bill's gross amount, no new
unconditional amount, and the original contract bounds. Every finding is
retained; false permission or failed eligibility cannot be repaired by the
balanced empty journal. This historical check uses the original pinned
opening; it does not substitute today's mutable branch state on a retry.

For a newly admitted event, independent calculation gives `G'=G+g`,
`K'=K+k`, with R, A and C unchanged. For this profile `g=k>0` and the
identified advance has at least k unused. Consequently

```
T' = G' + A − K' = G + A − K = T
AR' = G' − K' − C = AR
CA' = max(R − T', 0) = CA
CL' = max(T' − R, 0) = CL
```

Cash and earned revenue are unchanged. The calculator must also reconcile
aggregate A/K/G/C against the identified advances, allocations and invoices,
and the existing monetary state against the formula. A locally balanced but
internally inconsistent opening is invalid. The proposed delta must match
the independently calculated before/after contract, including credit usage
and a genuinely new invoice/allocation; merely setting all account deltas to
zero is insufficient. This operation has a nonzero economic effect.

Only after valid binding/authorization does P2 look up the stable tuple
`(entity_id, book_id, branch_key, business_event_id)`. Equal complete request
fingerprint returns the original receipt, even though current head/generation
has advanced. A different fingerprint conflicts. For an absent key, compare
both expected state and generation before reconciling the candidate outputs.
Then atomically recheck the key and head and publish the state-only proposal,
delta, closing CompanyState, immutable receipt and identity-index entry.
Advance generation once. A zero account movement is not a zero transition.

The receipt retains the original opening and closing state, basis,
authorization, proposal, delta, full request fingerprint and stable identity.
No earlier record points forward to it. Exact replay publishes nothing and
keeps both head and registries unchanged. The outer OperationResult says
`commit_observation=not_committed`, while its typed payload identifies the
original committed event and `additional_commit=false`. First commit says
committed/true. Receipt lookup after an unknown acknowledgement reuses the
original exact request bytes; a changed request_id, budget or expected head
changes the fingerprint and cannot masquerade as a retry.

## Complete example and adverse exchanges

The synthetic opening has cash 30, contract liability 30, AR/CA/revenue zero,
contract price 100, R=G=K=C=0, A=30 and unused advance A1=30. Event E1
creates invoice I1 with gross 30, applies A1 credit 30 and leaves invoice
receivable zero. The closing state keeps the same account balances, sets
G=K=30, marks A1 fully applied, and retains the I1 allocation. Revenue and
cash-flow contribution are zero; the liability remains 30 for performance
still owed. This is not a new cash receipt or recognition event.

The companion complete registry and submission bytes specify these exchanges:

| Exchange | Distinguishing fact | Expected result and domain consequence |
|---|---|---|
| First commit | Valid E1 at original head | Commit one state-only event; all account deltas zero; allocations/head change |
| Exact replay | Same bytes after that commit | Original receipt; no new commit, allocation or head change |
| Changed invoice under E1 | Valid alternative I2 from original pre-state, same business identity | EVENT_ID_CONFLICT after lookup; never allocate A1 twice |
| Changed request_id | Same event and amounts, different complete envelope | EVENT_ID_CONFLICT; correlation field remains part of fingerprint |
| New event from stale opening | E2, valid pinned old opening, current head is E1 closing | STALE_OPENING_STATE; no commit |
| Reused credit at current opening | E2 and I2 attempt 30 after A1 is fully used | POSTING_NOT_AUTHORIZED with failed credit finding before lookup |
| False authorization | Correct event but supplied posting_permitted=false | POSTING_NOT_AUTHORIZED before lookup; no validated request reference |
| Unsupported profile | Known closed profile with no supported commit operation | UNSUPPORTED_PROFILE_OPERATION before lookup |
| Nonzero account delta | Valid event and empty journal, AR delta +1 | DELTA_MISMATCH after valid input/freshness; no publication |
| Lost allocation | Correct zero monetary delta but economic after-state omits invoice/credit use | ECONOMIC_DELTA_MISMATCH; no publication |

Inputs rejected before full validation retain Submission and diagnostic bytes,
with request_ref/payload/coverage null. Output-candidate mismatches retain the
validated request but publish no receipt or state. The exact response schema
uses all I1/F1 status dimensions. Its coverage domain describes the singleton
request decision, not all financial histories: a completed decision can report
a known rejection, and cannot be counted as accepted accounting. Unknown
acknowledgement is governed by P3 and never inferred to be rollback from a
timeout. This unit does not implement a crash/durability experiment.

## Compatibility and remaining evidence

The native acquisition journal's nonempty lines remain correct for that profile.
No frozen schema, receipt, encoding or fixture is changed. A consumer without
this new schema lock/profile returns UNSUPPORTED_PROFILE_OPERATION with no
mutation. A journal export that can represent only monetary lines must retain
the state-only event in its event/state export or explicitly report unsupported
lossless export; silently dropping the event would permit advance reuse after
recovery. Statement builders derive no revenue/cash change from this event but
future invoice eligibility must use its retained economic state.

The documentary checker validates registered record shapes, digests, dependency
and byte closure and independently derived economic and identity consequences.
That evidence does not establish general serialization conformance, runtime
transaction isolation, crash recovery, real-contract validity or wider E14
completion. Subsequent implementation must test concurrent identical/conflicting
submissions, torn writes, lookup after lost acknowledgement and full export/import
recovery of allocation state under this exact pinned profile.
