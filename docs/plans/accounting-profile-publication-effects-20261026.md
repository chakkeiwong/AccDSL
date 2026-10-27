# Describe publication effects across retained component profiles

26 October 2026. S2–S4; MC20/24/25/33/34, G2/G18, I04 and P17-07.08.
Predecessor: current-design-reconciliation-20261025, all-row scoped review.

## Skeptical audit and evidence contract

Question: can a shared read-only descriptor retain the actual publication and
financial effects of four existing profile locks without equating their Boolean
fields or identity namespaces? Compare InsuranceComponents/1, GroupComponents/1,
BankAssessment/1 and InsuranceAssessment/1 against their exact retained
request/result/receipt and before/after documentary worlds. Insurance assessment
uses additional_commit=false for a query publication; bank assessment uses true.
Copying that field is therefore the wrong comparator for actual effects.

This plan passes for a bounded design/conformance helper. It does not make a
common dispatcher, rewrite old records, post a journal, install dependencies or
claim transactional durability. Existing component worlds are authored semantic
examples, not observations of a production store. The identity repair is separate
metadata evidence; use explicit tuple fields, never split an ambiguous old key.

Primary criterion: each exact exchange has a descriptor preserving request and
profile identity, disposition, original receipt, query publication, component
head changes, legal/account changes, journal additions and unchanged ownership
domains. The native Boolean and its profile-specific meaning remain visible.
Exact replay/refusal creates no new effect; unknown acknowledgement remains
unknown even when a test fixture contains a hidden before/after storage world.

Vetoes: source hash mismatch, wrong profile/schema, unrecognized world field,
lost or fabricated record, rewritten legal book, changed replay world, or
classification inferred only from an operation name/Boolean. Refuse unsupported
cases and preserve their native evidence. Counts are inventory only. Financial
measurement, actual authority and empirical validity are not promotion targets.

Assumptions and earliest checks: retained successful attempts are the baseline
(verify result/manifest identities); world maps represent complete declared
owners (check exact fields); receipts bind their request/results (check references);
no cross-profile economic equivalence is assumed. A design inconsistency triggers
a new repair, not silent edits to frozen examples or a global stop.

## Work

1. Pin accepted source packets, inspect one publication/replay/refusal and both
   acknowledgement-loss worlds per profile; fix the exact mapping in a contract.
2. Implement the read-only descriptor under a new directory. Preserve complete
   references and explicit effects without normalizing away original meanings.
3. Compare all retained exchanges in these four locks and meaningful tampering
   cases, including changed query Boolean, changed accounting head, lost receipt,
   and pretending an unknown transport observation means no commit.
4. Record result/manifest, refresh controls, then specify the next shared method
   composition boundary. Keep full manuscript integration separate and preserved.

Artifacts: data/accounting-master/profile-publication-effects-20261026/.
CPU-only standard-library diagnostics; no GPU, commits, agents, installs, fees,
outreach, publication, product rollout or forecasting. Independent/human acceptance
is pending and does not prevent this internal work.
