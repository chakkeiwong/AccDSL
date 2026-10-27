# Bounded storage reuse audit

The audited plan is accounting-simulator-storage-reuse-audit-20261024.md.
Question: can existing P07 preserve newer complete records without silently
changing their types, meaning or transaction boundary? Original P07 source and
process-exit tests, plus original native propose/apply, are the comparators.
An observed generic node round-trip is engineering evidence only. It cannot
establish native execution, actual-source admission or production durability.

Inspected complete state, Store canonical/dump/node/add_node, schedule, run lock,
replay, apply, export and migration functions and focused P07 tests. Important
defaults: one writer, SQLite FULL/DELETE, strict P07 JSON, generic unknown node
kinds and old Engine coupling. These are inherited baseline choices, not newly
promoted simulator defaults. Their failure modes are altered identity/ordering,
float-metadata rejection, semantic forgery and partial multi-node publication.
The earliest probes exercise precisely those risks in fresh /tmp databases.

Evidence contract: exact retained bytes/types and original native rejection of
forged states are primary. Hash equality alone is explanatory about retention.
Record original behavior even when it rejects reuse. Separately committed nodes
may survive as a partial logical group; a surrounding transaction must be tested
before reuse. Process exits demonstrate only the observed local recovery case,
not power-loss, multiwriter, distributed or adversarial integrity. No new source
assertion, scientific comparison or model default is introduced. Preserve every
frozen input hash; mismatch stops continuation. All other applicability failures
trigger a narrower design and remain evidence for the next repair.
