# Versioned insurer request-identity adoption

26 October 2026. MC17/20/24/25/33/34; G2/G18, S2/S4 and interaction I04.
Work directory: data/accounting-master/insurance-identity-adoption-20261026/.

Question: can the retained InsuranceComponents financial publication semantics
adopt an unambiguous request-pair identity while preserving complete owner
states, journals, output/receipt identities and recovery behavior? The candidate
is an explicit successor profile plus a lossless, conditional documentary
conversion. This is a design/conformance unit, not a live store migration.

## Skeptical audit before implementation

The existing metadata repair is insufficient as a financial posting test. Its
455 checks prove neither native adoption nor absence of duplicate postings.
The bank successor is also the wrong financial comparator: bank queries publish
results while this profile can mutate four owners and journals. Inspect the
actual InsuranceComponents builder, independent verifier, schemas, exact request
bytes, retained before/after worlds and source locks. Record a design audit
before implementing. A changed request/profile digest necessarily changes some
record identities; declare an exact reversible mapping and compare whole records
after that mapping rather than pretending byte equality across versions.

Do not infer state compatibility with InsuranceAssessment from matching currency.
Do not fabricate a receiving receipt adapter. A missing retained decision may be
irrecoverable, and migration success is conditional on a complete supplied
history. Confirm this limitation explicitly. Refuse ambiguous/conflicting
histories. Frozen evidence and original sources must retain their hashes.

## Intent and evidence contract

| Item | Required treatment |
|---|---|
| Exact comparator | Pinned native InsuranceComponents/1 builder and independent financial auditor; saved complete portable exchanges |
| Mechanism | Explicit versioned profile/schema boundary, canonical pair key, exact-byte conflict/replay, conditional conversion of retained identities |
| Expected failure | Schema-valid (a/b,c) and (a,b/c) collide under legacy concatenation; ensure native full requests expose the defect |
| Primary pass criterion | Mapped complete ordinary financial results and owner worlds equal native results; distinct colliding pairs execute independently when individually eligible; original retries recover the same publication without a second financial effect |
| Promotion veto | Lost/mutated source, changed financial calculation, inconsistent reference closure, partial owner publication, ambiguous migration, replay identity drift or unknown erased history presented as complete |
| Continuation veto | Invalid comparator/artifact or unsupported native state/authority assumption; repair the harness before interpreting results |
| Repair trigger | Identity/refusal mismatch in an otherwise valid candidate; preserve failure and repair the successor |
| Explanatory only | Case counts, parse success and runtime; none approves accounting or product readiness |
| Nonconclusions | Actual IFRS compliance, complete real insurer facts, production durability, common state interoperability, forecasts or whole requirement completion |
| Durable evidence | design.md, semantic-contract.md, source-lock.json, checked full packages, checks.json, result.md and run-manifest.json in the work directory |

## Assumptions to check early

Canonical JSON pair encoding comes from the isolated helper. It is a reviewed
identity mechanism within its string domain, not permission to post. Confirm
schema ID domains and pair round trips. Native numerical rules remain the
baseline; detect drift with the independent financial auditor and full journals.
Complete supplied decision history is an explicit migration assumption; reject
known omissions/conflicts and never claim recovery of erased records. Profile
and schema names are engineering choices; validate every lock and reference.
Deterministic finite cases are conformance evidence only, with no ranking.

## Execution

1. Inspect native financial ownership, transactions, replay and record closure;
   write the audit and exact successor design. Determine feasibility from those
   sources before coding. Preserve the 53/6/46 mission inventory.
2. Build the smallest explicit successor and conversion with pinned native
   arithmetic, immutable source locks and no frozen-file mutation.
3. Check ordinary complete publications, collision requests, conflicts, stale
   requests, loss of acknowledgement in both worlds, and corrupt migrations.
   Validate saved packages independently of the builder's expected labels.
4. Record findings, decision and limitations; integrate a substantive result
   into the preserved governing manuscript and refresh the next phase.

Use bounded CPU-only commands with CUDA_VISIBLE_DEVICES=-1. No installations,
subagents, commits, GPU work, professional outreach, fees or E3 execution.
Native source inspection is ready work; human acceptance remains pending.

## Native inspection decision

The native request contains a financial profile reference and exact-byte
submission. Receipts and journals retain the original request reference. A
blanket financial-profile rewrite would create fresh requests and could repeat
already-posted events. Revise the successor boundary to a versioned execution
identity policy, InsuranceComponentsIdentity/1, bound to the unchanged exact
InsuranceComponents/1 financial profile and schemas. Requests keep their original
bytes. The successor world adds an explicit policy reference and converts only
decision keys to canonical pairs. Migration changes no accounting head, journal,
published financial record or decision reference. Policy records have their own
schema and immutable contract lock. An unbound/legacy world cannot enter the new
executor. This avoids requiring an invented accounting state adapter.

The primary comparator is now exact equality of financial records and worlds
after the declared key/envelope conversion, not re-identification of requests.
The execution policy is deliberately distinct from financial-profile admission.
Use the isolated migration helper for its checked identity/history conditions;
add whole-world validation and complete native request execution/recovery tests.
