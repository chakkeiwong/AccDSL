# Accounting and state-transition contract (proposed v1)

This document specifies one bounded handoff for the proposed whole-product
architecture. It is a design contract, not an accounting engine or a claim of
standards compliance. The handoff keeps source eligibility, treatment choice,
journal construction and state mutation distinct so that a balanced journal
cannot conceal an unsupported treatment.

## 1. Evidence and scope

The contract consumes an `EconomicEvent` only when the event has a stable
business identity, an entity/book perimeter, an economic interval, a declared
currency/unit/scale, an expected opening-state digest, and links to the
evidence, authority, method and assumption versions used to assess it. The
evidence link must identify the source bytes and the reviewed assertion or an
explicit unresolved reason. A source label or account name never supplies a
classification by itself. The illustrative fixtures bind to A01–A03 in
`standards-fixtures-v1.json` and to the inspected S9 paragraphs recorded in
`standards-source-register-v1.json`; their scope is a for-profit entity with an
annual period beginning 2024-01-01 under the retained 2022 compilations.

The proposed handoff is:

```text
EconomicEvent
  -> TreatmentAssessment
  -> JournalProposal
  -> StateTransitionReceipt
```

`TreatmentAssessment` answers whether the event is eligible under the declared
authority and method. It may be `eligible`, `unresolved`, `ineligible`, or
`outside_scope`. It must preserve the known facts and the reason for any
unresolved or rejected treatment. It does not mutate a book.

`JournalProposal` is produced only for an eligible assessment. It contains
typed lines with account, entity, concept, dimensions, currency, unit, basis,
debit/credit amount and rounding metadata, plus the independently computed
state delta. The line set and delta are checked together before commitment.

`StateTransitionReceipt` records the request identity, parent opening digest,
assessment and proposal digests, committed journal/state digests, status and
audit lineage. A rejected or unresolved receipt has no committed journal or
state delta and retains its reason and submitted evidence references.

## 2. Inputs and outputs

Required inputs are versioned `event`, `opening_state`, `authority`, `method`,
`evidence`, `time`, `identity`, and `cutoff` records. `opening_state` includes
the book version and all balances needed by the method; `cutoff` fixes which
source versions and publication times are admissible. `identity` binds the
business event, entity/book and event version. The method records recognition,
measurement, posting and rounding assumptions; it must not silently import an
unrecorded rate, classification or later source.

An eligible output contains `assessment.status=eligible`, a balanced journal,
an account/state delta, closing-state digest, and `receipt.status=committed`.
An unresolved output contains `assessment.status=unresolved`,
`receipt.status=rejected`, `mathematical_status=unresolved`,
`computation_status=not_computed`, `commit=false`, and `state_delta=null`.
Invalid identity, stale opening state, conflicting event payload, unsupported
authority or out-of-scope facts have distinct rejection codes. The common
status envelope does not turn a rejected request into a computed result.

## 3. Invariants and atomicity

1. Every committed line retains compatible context and exact source/method
   lineage. Labels do not perform standards conversion.
2. Debit and credit totals agree after the declared rounding rule, and the
   account roll-forward equals the independently calculated state delta.
3. A treatment is not eligible merely because its journal balances. Missing
   authority or required evidence is an eligibility veto.
4. Journal, state and committed receipt are one atomic transition. Any failed
   check writes none of them; a rejection receipt may be stored as an audit
   record with `commit=false`.
5. Replaying an identical `(book, business_event_id, event_version, payload,
   method/evidence/assumption versions)` returns the original receipt without a
   second posting. A different payload for the same identity is
   `EVENT_ID_CONFLICT`.
6. A new event whose expected opening digest differs from the current book is
   `STALE_OPENING_STATE`; it cannot overwrite or merge state implicitly.
7. Unresolved and invalid treatments preserve known facts and produce no
   domain write. A correction or alternative treatment requires a new explicit
   event/version and lineage.

## 4. Failure and interaction rules

The evidence contract supplies immutable bytes, reviewed assertions and
conflicts. The time contract supplies admissible source/review versions and
cutoffs. History families supply a branch-specific opening state and treatment
context; accounting must retain the branch identity in the receipt. The future
language/IR contract must carry these typed records without erasing status or
lineage. Persistence must make the identity lookup, opening digest and atomic
write durable; interfaces and failure semantics remain unfinished P16 work.

`MISSING_EVIDENCE`, `UNSUPPORTED_AUTHORITY`, `TREATMENT_UNRESOLVED`,
`CONTEXT_MISMATCH`, `ROUNDING_MISMATCH`, `UNBALANCED_JOURNAL`,
`EVENT_ID_CONFLICT`, and `STALE_OPENING_STATE` are separate outcomes. No
failure is converted to a zero amount, a guessed classification, or a sampled
future result. A failed transition is safe to retry only after receipt lookup
has established whether a prior commit exists.

## 5. Alternatives and provisional choice

Direct balanced posting is compact but entangles eligibility, arithmetic and
mutation; it is retained as a comparison baseline. Event-sourced projection
preserves history and replay but still needs a typed treatment boundary and
can leave projection timing ambiguous. The provisional choice is a typed
shared-IR adapter with the four explicit stages above: it makes method/source
identity portable, permits branch-specific state, and gives persistence a
single atomic receipt boundary. This choice is provisional until language,
persistence and interface contracts are specified and compared on the same
fixtures. No technology, database, solver or authoring syntax is selected.

## 6. Fixture interpretation and limits

Fixture A01 is an eligible FVTPL acquisition at price/fair value 100 with fee 2:
asset debit 100, expense debit 2, cash credit 102. A02 is the matched
amortised-cost case: asset debit 102 and cash credit 102, assuming that category
has been separately justified. A03 has price 100, fair value 105 and missing
evidence for the relevant observable-valuation condition; it remains
`TREATMENT_UNRESOLVED` with no journal or state write. Replay and stale-state
cases exercise identity and atomicity using A01's committed receipt.

These examples check the contract's distinctions and arithmetic only. They do
not cover leases, tax, pensions, impairment, groups/FX, banks, insurers,
IFRS/US GAAP/ASBE applicability, forecasting or complete disclosure packages.
Those later-domain obligations remain visible in the P16 profile and P17 plan.
