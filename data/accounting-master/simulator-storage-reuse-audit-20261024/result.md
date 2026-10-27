# Existing storage reuse: valid primitives, explicit integration limits

24 October 2026. Twenty-five checks pass across17 bounded applicability probes
and eight protected inputs. The probe count includes a three-method original
P07 regression slice covering process kill, retry conflict and schema migration.
All databases were fresh temporary files under/tmp; no frozen code changed.

Native openings, original transition proposals and complete conditional query
requests round-trip exactly in the inspected cases, including unresolved target
obligations. A fresh subprocess recovers those records unchanged. Complete
range results contain wall_seconds as a float, which P07 correctly refuses
under its existing canonical-data contract without inserting a partial node.
A byte envelope retains the entire result including that metadata exactly.

Two additional mismatches make direct generic-node reuse unsuitable as the
new record-identity contract. P07 normalizes Unicode strings, so distinct UTF-8
payloads can receive the same node identity and retrieve the earlier spelling.
It also treats fields named constraints as sets: differently ordered lists can
share identity and retrieve the earlier order. These are P07 conventions, not
proof of corruption in its original contract. They are wrong for a proposed
new contract promising exact original-byte retention. An opaque byte envelope
avoids these aliases without changing or promoting P07 canonicalization.

Storage integrity is distinct from native correctness. A forged proposal whose
cash/equity changes still balance passes generic node retention and SQLite
integrity; the original native apply replay rejects it. No raw storage receipt
may imply semantic verification, state admission or execution.

Process-exit probes preserve one node when two independent writes are interrupted
after the first. With an explicit outer transaction, exit before commit preserves
neither node, and exit after commit preserves both. The old P07 kill/retry/migration
slice also passes. These are observed local process recovery outcomes, not
power-loss, multiwriter or distributed durability claims.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Reject direct generic-node identity for exact new payloads | Unicode/order aliases and float refusal reproduced | Promotion veto for this reuse contract; no continuation veto | Complete new record grammar and resource limits | Specify an exact-byte envelope with typed roles and explicit validation | P07 is wrong for its original contract |
| Reuse P07 transactions and immutable dependency nodes as optional reference primitives | Fresh-process retention and before/after commit probes pass | Separate writes fail a logical-group atomicity requirement; outer transaction passes tested cases | Broader failure/environment coverage | Build a bounded atomic evidence archive reference using the unchanged store | Whole-simulator execution persistence or production readiness |
| Separate archived bytes from valid simulation | Balanced forged proposal retained but original replay rejects | Hash-only semantic acceptance vetoed | Profile-specific validators and independent review | Preserve verification status separately; never infer it from storage | Source/accounting admission from a storage receipt |

The strongest limitation is the narrow local failure model. Filesystem or power
failure could violate stronger claims these probes do not test. An exact-byte
mismatch after recovery or a partial committed bundle would overturn the proposed
reference behavior and trigger repair. The findings reject an overly broad
reuse design, not the storage research direction. No global continuation veto
fired. Version3.70 remains459 pages,not_ready; S1-S5 partial,S6 held,S7 deferred.
Next: docs/plans/accounting-simulator-evidence-archive-20261024.md.
