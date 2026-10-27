# Insurance request-pair collision and bounded repair

26 October 2026. MC25/MC34/G18 and I04. The retained InsuranceComponents/1
index is wrong relative to its declared pair identity: (a/b,c) and (a,b/c)
are both schema-valid but both produce a/b/c. The actual retained builder
function reproduces this collision; the independent auditor uses the same
expression. This can falsely conflict two distinct identities. The finding
does not establish that an existing retained financial example was corrupted,
and does not by itself demonstrate duplicate posting.

The separate successor helper uses a canonical JSON array key inside an
exact-profile index. Array decoding recovers both strings, so equal keys imply
equal pairs. The finite separator matrix corroborates this argument; its count
is not an exhaustive proof. Migration preserves request/result/receipt references
and refuses ambiguous or conflicting retained history rather than overwriting it.
An absent lookup result grants no permission to post.

The final CPU-only command in run-manifest.json passes 455 deterministic checks
over 85 distinct retained indexes, plus synthetic collision, missing-record,
changed-digest, binding, conflicting-history and invalid-ID cases. Every protected
input, including the 4.40 PDF, retains its hash. The earlier 450-check run passed;
five additional binding/history checks strengthened the same bounded evidence.
No legacy builder, frozen schema, request, receipt or manuscript was rewritten.

| Decision | Primary criterion status | Veto diagnostic status | Main uncertainty | Next justified action | Not concluded |
|---|---|---|---|---|---|
| Retain the isolated index successor | Pair round trips, exact replay, conflict and preserved decisions pass | Corrupt/missing/ambiguous histories refuse with unchanged inputs | Completeness of supplied retained decision history | Route any future InsuranceComponents index adoption through explicit conversion | Full component migration, production durability or common accounting compatibility |
| Keep frozen evidence and qualify its identity claim | Concrete schema-valid collision reproduced | No silent repair or overwrite | Whether any unretained historical decision was lost | Preserve originals; recover from independent records if needed | That existing financial examples are numerically wrong |

The apparent common-versus-component namespace discrepancy is not itself a
confirmed bug: GroupComponents and InsuranceComponents declare separate owners,
operations and schema locks. InsuranceAssessment and BankAssessment also explicitly
assign different meanings to additional_commit. A future shared adapter must
translate actual effects, including query publication, financial state mutation
and replay, rather than copying that Boolean. This remains design work.

Post-run red team: if a colliding entry was already lost, a supplied one-entry
history can pass migration. The helper cannot infer the erased record; success
is conditional on history completeness. The repair would be insufficient if
presented as a live runtime migration or global event index. It is only a checked
metadata successor and does not establish physical atomicity or source admission.
No research-direction rejection or continuation veto follows. Resume the full
operation and interaction reconciliation; E3 remains deferred.
