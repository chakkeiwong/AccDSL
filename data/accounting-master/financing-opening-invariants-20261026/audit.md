# W05 audit before implementation and conformance

26 October 2026. Plan: docs/plans/accounting-financing-opening-invariants-20261026.md.

E01's independent table covers four programs, two charts, 16 event transitions
and four final reports. Its deliberately omitted missed_amount and new_shares
writes still complete in DeclaredCompanyProgram/2. The independent state oracle
rejects both. Local cash/nonnegative-claim postconditions are therefore an
insufficient baseline for the requested history checks.

Reuse CompanyBook/1 structural/schema/leaf-type validation and the existing
MethodRequirements/3 typed, guarded scalar evaluator. The receivable-specific
CompleteClaimsOpening profile cannot be relabelled as financing admission: it
assumes a claim collection, receivable sum and a different memory definition.
The current requirement evaluator already expresses the scalar relations here.
A small explicit binding/composition adapter is needed; no new arithmetic,
financial callback, language parser or duplicate general program engine is
justified. Use the existing clocked transition and report engines directly.

Snapshot checks cover nonnegative face/claim/arrears/shares, claim bounds,
pre-maturity face versus carrying value, maturity carrying/claim equality,
missed-amount/arrears consistency, and their dates. They cannot prove that an
otherwise consistent late-paid opening retained its history. A separately
supplied opening-history premise must bind the exact book and all debt-term
fields; completeness/provenance remains a supplied premise, not source truth.
Missing/partial history refuses as unresolved. Changed premises must never be
silently generated from the candidate by the evaluator.

Transition checks bind before, event and after values into explicit per-method
declarations. They preserve original face, due date and old shares and every
unchanged debt-term field; issuance increments new shares; observation records
the unpaid claim once; late payment decreases arrears/claim while preserving
missed and missed_amount. A snapshot-valid rewrite of historic missed_amount
after payment must be rejected by the transition relation. Money and share
dimensions remain distinct. Original zero-coupon/no-fee/no-tax/no-penalty scope
is retained; missed is not a legal-default flag.

The selected contract pins exact schemas, leaf types, role/account classes,
method registry and reporting map. Altering a method under an old selection
refuses; omission controls also inspect their actual candidate transition
against the unchanged declared relation, so selection rejection is not mistaken
for demonstrated semantic detection. Reports change only observation date and
must satisfy the same snapshot checks. Carry and new rights-changing events
remain outside this unit and require separate declarations.

Primary criteria: all frozen independent full states/journals/flows and final
reports match; state/transition controls reject with no accepted changed state;
partial or missing opening history is unresolved. Diagnostic counts are not
promotion evidence. Hash drift, baseline mismatch or unhandled malformed input
invalidates the harness and triggers repair. A failed declared condition calls
for repair, not rejection of financing simulation. Broader source/accounting
and E03 default/remedy integration remain open.

Defaults are explicitly inherited fixture hypotheses, not general policies.
No stochastic experiment, performance ranking or production default changes.
Bounded deterministic evidence is written once per numbered attempt with
protected dependencies, command/environment, elapsed time and non-claims.

Attempt-01 exposed a verifier error: an intermediate snapshot was expected to
qualify as a fiscal opening. The preserved runtime rightly refuses it. See
repair-note.md. Attempt-02 checks snapshot/history satisfaction separately;
opening admission retains the fiscal start, empty-flow and temporary-balance
conditions. This is a harness repair, not a scientific or direction rejection.
