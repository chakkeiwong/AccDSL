# Unambiguous component request identity

26 October 2026. MC25, MC34, G18; interaction I04. Parent work is
accounting-current-design-reconciliation-20261025.md.

## Question and skeptical audit

InsuranceComponents/1 says identity is client plus request ID. Its schema
allows slash in both fields, while build_exchanges.py:48 and
verify_exchanges.py:199,240 join them with a slash. Distinct admitted pairs
can therefore share a lookup key. This is a concrete representation defect,
separate from the intentional distinction between component publication and
common business-event accounting. The latter uses different owners and locks;
no automatic migration or compatibility is implied.

Primary question: can a new, isolated lookup encoding distinguish the declared
pair, preserve exact-retry decisions and detect ambiguous legacy indexes without
rewriting frozen requests or receipts? Comparator: the retained builder and
auditor expressions under their retained ID schema. A source-derived witness
must precede promotion of a repair. This audit passes for that bounded task.

Primary criterion: reversible canonical tuple encoding, unchanged-request replay,
changed-content conflict, distinct valid pairs separated, and atomic all-or-none
legacy index conversion from retained request bodies. Missing or contradictory
legacy bodies/entries veto conversion; no overwrite or fabricated record repairs
them. A failed candidate triggers another bounded encoding repair, not rejection
of the whole financial-statement design. No elapsed-time or count metric is a
promotion criterion.

Assumptions: field values retain decoded code points (portable semantics);
existing request bodies and immutable receipts are the source of identity
(legacy contract); the new index is separate metadata, not a new accounting
commit. Canonical JSON arrays are a proposed reviewed encoding, with round-trip
and adversarial checks. This work does not infer a missing historical receipt,
establish runtime durability, or authorize cross-profile financial execution.

## Execution

1. Read the actual retained schema and identity expressions; reproduce the
   smallest collision without running historical artifact writers.
2. Specify and implement a separate successor lookup/index helper and explicit
   migration refusals. Preserve all frozen source/schema/request/receipt hashes.
3. Run focused deterministic tests: permitted separators, pair round trips,
   duplicate/conflicting identities, retained references, missing bodies,
   corrupted keys and refusal atomicity. No GPU or installs are needed.
4. Record the checked conclusion, limitations and exact next design boundary;
   add it to the current reconciliation and master routing.

Artifacts: data/accounting-master/component-identity-repair-20261026/.
CPU only, no framework import. No commits, agents, installation, professional
engagement, publication or forecast experiment. General identity dispatch and
assessment publication semantics remain separate review questions.
