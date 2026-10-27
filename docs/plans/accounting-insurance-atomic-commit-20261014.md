# P17-10/11 — Commit connected insurance groups as one book event

14 October 2026. Continue from Version 2.87. MC02/04/11/13/18/20/22/24/25/27/28/32–35;
E07/E14 and G2/G7/G12/G16–18. This is a documentary specification and finite
reference check. Runtime implementation, installations and campaigns stay held.

## Refresh and skeptical audit

The connected-group calculation in Version 2.83 supplies separate issued groups
A/B and reinsurance held R in one synthetic insurer's book. The common
OperationRequest, AccountingEventBasis, PostingAuthorization, commit arguments
and P2 event/replay rules already exist. Reuse them; do not invent a second
receipt index keyed by group or request_id. The new profile defines the domain
payload and whole-event validation, not a replacement common API.

Audit passes for this bounded interaction. Three independently valid group
calculations do not establish one valid book transition. Equal terminal cash
does not establish correct group identity or recognition timing. One legal book
is the atomic owner here; cross-entity/book coordination is outside this profile
and must not inherit a distributed transaction guarantee. Component balances
inside LRC/ARC must not be posted a second time as independent accounts.

The existing source-supported calculation is the numerical baseline. Authored
posting permission is synthetic only. Inspect its exact event ordering and
component definitions before choosing the event fixture. Preserve the separate
source applicability and actuarial limitations. No fresh accounting theory or
statistical ranking is inferred from storage examples.

## Evidence contract and intent

Question: can a complete dated measurement event preserve independent group
identities while committing their journals, component changes and one company
head together, including replay and partial measurement failure?

Primary pass: a complete closed portable exchange with independently checked
opening/closing company and group balances, authorization/context bindings,
event identity, expected head, immutable receipt and adverse traces. Exact
replay must return the original receipt before checking today's head. Unknown
acknowledgement must preserve the original request; changed retries conflict.

Hard vetoes for the affected result are wrong group/book/view/method binding,
missing component evidence, a partial event published as complete, duplicated
component accounting, false permission, invalid closure, stale head for a new
event, or a replay that posts again. Each triggers a specification repair;
none independently rejects the broader research direction. A corrupt baseline
or conflicting writer stops dependent work until resolved. Continue unrelated
ready units. Schema counts and balanced journals alone are explanatory checks,
not evidence of accounting compliance or storage durability.

The unresolved group remains explicit. Complete diagnostic proposals for other
groups may be retained outside committed domains; their numerical values cannot
be presented as the closing book. Cover failed measurement, stale/new event,
same event with changed bytes, lost acknowledgement before/after commit,
validation before replay, and interference by another event. Preserve old
receipts and all four committed domains on rejection or replay.

## Defaults and implementation route

| Choice | Provenance/status | Risk and smallest check |
|---|---|---|
| Same insurer/book/branch A/B/R | Existing connected-group example; synthetic baseline | Accidental cross-book atomicity; reject a mismatched owner |
| Exact rational values | Existing checked schedule | Rounded fractions obscure components; reconstruct deltas independently |
| One dated event | Derived engineering choice to preserve the declared measurement dependency | Implies all insurance is one transaction; state event scope and required group set explicitly |
| Existing common envelopes/P2 lookup | Reviewed architecture baseline | Reusing convenient schema can change semantics; compare exact common fields and replay order |
| Frozen proposed domain profile | Specification-only choice | Synthetic permission mistaken for real authority; reject real-book use |

Dossier: data/accounting-master/p17-completion-20261014/P17-10/insurance-atomic/.
Read the connected-group source/case records and current interface, persistence,
cross-contract and state-only examples. Write the domain contract, full records
and positive/adverse expected exchanges. Use system Python Fraction/jsonschema
for independent finite verification. These scripts author/check examples and
never open a live accounting store.

If the interaction adds material explanatory content, protect Version 2.87,
integrate a bounded narrative into a successor, build through
scripts/accounting_document_tools.py, inspect affected physical pages and check
all prior source/display/citation preservation. Record the result and command
manifest, refresh the six controls, and continue the next audited residual.
Human comprehension and independent acceptance remain pending while drafting
continues; no new confirmation is required.

## Event boundary chosen after source-case inspection

Use the existing year-one sequence: finance, service, claims/recovery incurrence,
then cash settlement. Each is a separately identified atomic event with the
declared A/B/R dependency set. Do not combine the year into one undifferentiated
transaction or erase the intermediate incurred balances. The finance event
alone moves A/B/R coverage amounts 120/130/85 to 131/142/93, cash stays 250,
and equity falls 85 to 70. Service, incurrence and settlement then reproduce
the existing final cash 173, coverage 65.5/71/46.5 and equity 83.

This choice lets replay be checked against a genuinely later head using the
same supplied case. Lost acknowledgement is a client transport observation,
not an invented successful server response. Preserve the two possible storage
worlds and the exact request for recovery. A finite trace specifies required
behavior; it cannot establish transactional implementation or crash durability.

## Verification refresh

The first authored trace did not distinguish the global example registry from
the records actually published in each storage world. Before verification,
extend each world with retained company states, the full published dependency
closure and explicit dependency edges. Check all of them at publication and
on rejection/replay. Add different-request interference at the final recheck,
a mismatched branch and a numerically wrong completed group measurement.
These repairs make the artifacts answer the declared atomic-publication and
validation-order questions; they do not introduce a storage implementation.
