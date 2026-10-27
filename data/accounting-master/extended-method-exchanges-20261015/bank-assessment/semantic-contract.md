# BankAssessment/1 documentary contract

15 October2026. MC02/04-07/11/13-17/19-21/24-28/30/32-35. These are closed,
authored exchanges and deterministic conformance checks. No service is run.
All new schema IDs use accdsl.bank-assessment.; no preceding profile changes.

## Sources, accounting and prudential target

The US national-bank book uses supplied US-GAAP CECL and USD millions. The
2026-01-01 Part3 snapshot is deliberately frozen through the Jan-Mar2026
synthetic window. This does not admit actual March law. Retained FDIC2024
instructions cross-check ordering only. SourceSupport binds original bytes,
extracted text, inspected locators and the retained derivation. RulePackage
must contain the complete declared source set. Eligibility lists each of the
13 stock conditions individually. Applicability lists every restricted absence.
Present exclusions or failed stock conditions reject this restricted method;
unknown findings leave dependent outputs unresolved. No ratio decides minimum
compliance, distribution permission or supervisory admission.

Opening debits are positive. State contains the entire opening book, dated
events, authored posted journals, closing book and unpaid demand. Independent
ledger derivation checks every event and balance. A supplied funding facility
limits cumulative borrowing; unpaid withdrawals remain in deposit liabilities.
Sequence equals event count. The opening date is explicit. All events are
nondecreasing in date, no earlier than opening and no later than the state's
as-of date. Assessment state date equals assessment date,
which is the day before period_end_exclusive. Context, book, perimeter and
currency must match every admission and measurement. AverageAssets must be
regulatory_average_total_assets for exactly the assessment's period/context.
A missing average never becomes closing assets or zero.

For the restricted corporate loans G and eligible allowance A, goodwill W and
accounting equity E, B=G, cap=B/80, T=min(A,cap), X=A-T and RWA=B-X.
CET1=Tier1=E-W, Tier2=T and total=E-W+T. Leverage uses M-W, where M is a
separately supplied regulatory average. Equity includes unclosed profit when
present. The allowance expense is already in book equity and is never deducted
twice. Direct Federal Reserve balances have zero risk weight; goodwill is
deducted and excluded from RWA. Net loans, circular allowance caps, omitted
excess deductions, goodwill in RWA and double allowance deductions are wrong
relative to this target. Each metric carries its actual dependency closure.
Nonpositive denominators produce undefined ratios without a numeric value.

Unknown applicability or deduction propagates through regulatory amounts;
unknown exposure affects cap/RWA/Tier2; unknown allowance admission affects
admitted/excess allowance, RWA and Tier2; unknown stock eligibility affects
CET1/Tier1/total but leaves exposure subtotals. Missing M affects leverage only.
These partial outputs remain query publications with unresolved obligations.

## Information and conditional loss

Every referenced Evidence must belong to the selected View, have available_at
at or before decision_at, and ingested_at at or before system_asof. Compare
timestamps as instants. This includes state, facility, all capital admissions,
average input, law, vintage, condition and policy evidence. Missing membership,
future availability or later ingestion rejects the query. An evidence reference
is checked through its contents, not accepted because its identifier looks old.
Measurement dates must not exceed the decision date. Current-view requirements
are checked after exact-request replay lookup. Historical results remain
immutable when a later View or Vintage appears.

JointLaw cells form a supplied complete finite synthetic partition. Each cell
records disjoint default date, EAD, LGD, cash shortfall and discount factor.
EAD*LGD must equal the supplied shortfall; no-default cells have zero EAD/LGD/
shortfall. Loss includes discounted lifetime shortfall for defaults within the
half-open default window, not cash restricted to that window. Query windows
stay within the law horizon and begin no earlier than query origin. Discount
factors are supplied valuation premises and are not recalibrated here.

Condition all has no condition evidence/date. survived_through has both; the
date precedes or equals query origin, is no earlier than law origin, and its
observed evidence is no later than the query decision. Retain no-default cells
and defaults strictly after that date. Normalize each supplied candidate law
separately. Zero retained mass is unresolved, with no division or bounds.
Point laws have exactly one candidate; finite law families retain the set of
expectations, without mixing candidates. Unweighted histories have no weights:
they can give possible cell-loss bounds but no expectation. possible_losses
describes retained declared cells even where a particular law assigns zero
mass. No row count, factorization, mean-LGD substitution or LLM confidence
creates a law. A separately supplied later Vintage is a new forecast, not a
Bayesian consequence of survival. A superseding law's evidence must still be
available. Results are economic loss, not a CECL/AASB9 allowance or calibration.

PolicySpecification declares objective, action limits, actual-settlement
constraints, tie handling and failure behavior. Describe returns no selected
action, no feasibility verdict and no distribution permission. Description is
not optimization. Negative limits and mismatched context/view/loss evidence
reject the specification; an arbitrary profitable policy is not promoted.

## Identity, publication and recovery

Identity is the ordered pair workspace_key/request_id. Submission bytes are
canonical UTF-8 JSON for the full immutable OperationRequest record. Reduced
rationals, no floating/nonfinite values and no duplicate keys are required.
Unknown fields and older corporate/AU profiles fail closed. Request operation,
signature, argument tag, profile, selected view and expected accounting head
must agree. A positive budget is required. Every output belongs to that request.

First publication atomically adds the immutable output, QueryPublicationReceipt
and identity index entry, plus their dependency closure. An unresolved output
can be published with partial disposition and explicit obligations. A published
query changes no accounting head, journal, balance, unrelated owner or view.
The receipt says query_published and accounting_effect none. Envelope
additional_commit records new query publication only; it never means accounting
posting. Every completed/partial result has disjoint exhaustive query coverage.

Exact-byte retry returns the original output and receipt before freshness or
head checks. Its disposition is replayed and additional_commit is false;
all original statuses, diagnostics, coverage and obligations are preserved.
Changed bytes under an existing identity reject request_identity_conflict.
Lost acknowledgement reports unknown until exact retry; it never means rollback.
The two crash states are before publication (none of the three items visible)
and after atomic publication (all visible). Partial publication is invalid.
No runtime durability, concurrency, calibrated forecast, lawful payout or
whole-company acceptance follows from these documentary examples.
