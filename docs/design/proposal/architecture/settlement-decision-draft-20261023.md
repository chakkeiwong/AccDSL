# Claims and explicitly authorised funding decisions

23 October 2026. S3/S4; MC13–18/23–26/28. This documentary extension follows
simulator-design-delta-20261023.md and the existing interfaces I2–I4. It is not
a registered operation or production implementation. The protected company
profile and Version 3.49 are unchanged by this separate design note.

## Question, comparison and skeptical review

Can the initial simulator represent the proposed settlement of an identified
payable using an explicitly chosen credit draw, while preserving unknown
funding terms and the distinction between a plan and a completed payment?
The comparator is the checked cash-only example: cash 74.6, payment 160,
cash shortage 85.4. The proposed mechanism adds one named facility and an
explicit decision. It does not infer a borrowing policy from the shortage.

Audit: a facility limit alone is insufficient. Existing drawings, reservations,
eligibility, expiry and the draw's settlement date affect usable capacity.
An authorised draw is not cash until it settles. A plan must not consume future
information or count a facility before the decision permits its use. A failed
payment cannot roll back a draw that already settled independently. Keep this
first profile to pure proposals: simulated successful event transitions are
checked separately, with no commitment or failed-settlement recovery claim.

Primary criterion: the proposed draw of 85.4 and supplier payment of 160 produce
balanced separate journal proposals, cash zero, a paid claim and increased debt,
conditional on successful draw settlement and the declared no-intervening-change
assumption. Cash-only refusal and unknown funding must preserve the input.
Vetoes are overpayment, claim/ledger disagreement, excessive draw, future
information, late funding, unbalanced proposals and input mutation. Counts and
timing are explanatory only. No empirical default probability, forecast,
accounting-compliance opinion or production readiness follows.

## Closed input and meaning

SettlementDecisionDraft/1 has a local context (entity, book and currency),
decision and payment instants, a frozen opening snapshot, one claim, funding
knowledge and an explicit policy decision. Each source or assumption identifier
must resolve in the packet's evidence map. These are documentary references;
production integration still requires admitted typed evidence and method locks.
The schema and examples are in
data/accounting-master/settlement-decision-20261023/.

Amounts are reduced rational records with integer-string numerator and positive
denominator, matching the existing portable convention. Negative amounts are
allowed only for signed claim adjustments. The claim records its recognised
amount, adjustments, settlements and outstanding amount; outstanding equals
recognised plus adjustments minus settlements. It reconciles to the payable
control account together with explicitly declared other payables. Its entity,
book and currency match the cash and facility. This bounded profile excludes
FX conversion, discounting, partial payments, early payment and netting.

The payment instant equals the claim's contractual due instant. The decision
observes only information available at or before its own instant; the snapshot
is taken at that instant. The packet explicitly assumes no intervening cash or
claim movements except the proposed draw and payment. Without that assumption,
a full event schedule and another state evaluation would be necessary.

Funding is known absent, unknown with a reason and obligations, or one specified
facility. A facility records its committed limit, drawn principal, reserved
capacity, availability start, exclusive expiry, and eligibility knowledge.
For this draft, expiry is the last draw-availability boundary, not the debt's
maturity. Interest, fees and later principal repayment are outside the local
payment decision; a complete loan schedule remains required before integrating
the new liability into a later-period projection.

The decision is either cash_only or explicit_draw with a facility ID, draw
amount, settlement instant and reference to the scenario's authorisation.
The facility itself does not choose the draw. Known headroom is limit minus
drawn principal minus reserved capacity. Known refusal of eligibility or an
unavailable draw window rejects reliance on that draw; unknown eligibility
leaves the decision unresolved. Unknown funding does not prevent cash_only
settlement when existing cash suffices. A cash_only shortage with an unknown
funding set is unresolved; with a known funding set it is infeasible under the
chosen cash_only policy, not proof of company default.

An explicit draw must refer to the named facility and settle at or after the
decision, before expiry, and no later than payment. Equal instants require an
explicit draw-before-payment dependency. The proposed amount cannot exceed
known headroom, and the full payment cannot exceed the identified outstanding
claim. Unknown eligibility or terms are never replaced with a guessed limit.

## Results and state transitions

Return invalid_input for inconsistent amounts, currency/context, reference
closure or forbidden future information; infeasible_under_policy for a known
shortfall or unavailable selected draw; unresolved_funding for an indispensable
unknown; and proposed for a valid plan. Every result retains the input unchanged.
The proposed result contains two distinct events when borrowing is selected:

1. Draw settlement: debit cash and credit the named borrowing liability;
   increase the facility's drawn principal only when this event settles.
2. Supplier settlement: debit the identified payable and credit cash; reduce
   that claim and the payable control account only when this event settles.

The pure checker also returns a conditional post-settlement snapshot for these
stipulated successful events. It must be labelled conditional, never committed.
If an actual draw settles and a later payment fails, retain the draw and unpaid
claim; the two events are not an all-or-nothing transaction. A single event's
accounting mutation remains atomic. Current documentary cases do not execute
that runtime failure/recovery path.

## Assumptions and smallest checks

| Choice and provenance | Justification/status | Failure mode | Early diagnostic |
|---|---|---|---|
| Northstar cash and payment amounts | Retained explanatory baseline | Treating synthetic numbers as issuer facts | Bind the original source and reproduce cash/claim control totals |
| One claim of 160 plus other payables of 40 | Explicit synthetic disaggregation of the 200 payable control after purchase | Pretending source documents identify an invoice | Label the allocation as an authored scenario and verify the sum |
| Full payment, one facility, no intervening movements | Bounded hypothesis for defining records | Silent cash changes or reuse as a general credit policy | Require the assumption and refuse unsupported fields/policies |
| Chosen draw 85.4, limit 100, zero reservations | Authored financing scenario, not a default policy | Invented borrowing capacity or automatic balancing debt | Cash-only refusal, headroom, authorisation and timing controls |
| Exact rational amounts | Existing portable convention | Noncanonical values or rounding masking disagreement | Reduced-rational validation and exact journal/control checks |

Run the standard-library/jsonschema documentary checker with GPU intentionally
hidden. Record input/source hashes, exact command, environment and duration.
Next after this unit: integrate the identified payable with dated sales/purchase
claim generation and debt-service scheduling; then define matched textual and
typed authoring. Do not claim this payment subprofile completes the DSL.

Execution follow-on: the complete conditional year is now checked under
docs/plans/accounting-funded-year-design-20261023.md: 18 paths and 192 checks.
It defines a separate partial-settlement lifecycle and a two-day borrowing
contract with explicit fees, interest, repayment and tax assumptions. The next
design task is portable inputs and matched authoring for that example; this
full-payment decision draft is not silently broadened into those operations.
