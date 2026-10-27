# Reuse audit for preserving complete simulator records

24 October 2026. S2-S4; MC04/05/10/24/25/26/28/35; G18;
P17-07.08 and P17-08.04. Production S6 stays held; S7 stays deferred.

Question: which parts of existing P07 physical persistence can preserve the
newer complete native state and conditional-family definitions without changing
meaning, and which require a distinct design? This is an applicability audit,
not another return-method wrapper or a new production storage implementation.

Skeptical audit: company_persistence_v1.py already implements physical SQLite
transactions, process-interruption tests, exact retries, evidence views and
one schema migration. A blanket statement that AccDSL has no durable storage
is wrong. Its create_run, _replay and apply_event methods are hard-bound to the
older P05 Engine. Saving a newer state as a generic node does not integrate
its transitions, grant source admission or prove semantic validity. Existing
company-composition migration examples are documentary and must remain so.

Exact baselines: original P07 Store for storage behavior; original native
propose/apply for state meaning; complete retained query requests/results for
lossless retention. Lock all inspected sources and fixtures. Do not modify any
frozen implementation, database, protected environment or release hash. Use only
fresh temporary databases under /tmp. Deliberately hide GPU devices.

Assumptions and provenance: one writer and SQLite settings inherit P07 and are
baseline hypotheses; local process-exit checks can establish only observed
transaction recovery, not power-loss behavior, network/multiwriter guarantees
or adversarial tamper resistance. Canonical rational strings, integer prefixes
and all unresolved/admission fields must retain their original types. Unsupported
float-bearing metadata must be reported, not rounded or silently discarded.
A generic record insertion does not imply an accepted simulated state.

Primary pass criterion: exact JSON round-trip for supported payloads, explicit
refusal for unsupported data, fresh-process replay and observed atomicity under
specified interruption points. Promotion vetoes: altered native quantities,
missing provenance/unknown fields, half-published logical record or representing
raw hash integrity as semantic verification. A probe mismatch triggers repair
of the proposed reuse design; it does not reject persistence as a direction.
Continuation veto: changed frozen inputs or unsafe tests outside fresh temp
storage. Counts/timing are explanatory. No statistical ranking is attempted.

Probe sequence: inspect complete store/replay/migration and existing crash tests;
check closed native opening/proposal and full conditional request round-trips;
check a complete result without filtering metadata; demonstrate whether a
hash-consistent but semantically forged proposal is accepted by generic storage
and rejected by original replay; examine dependency/cursor and evidence-view
boundaries; compare separate insertions with one explicit transaction across
fresh subprocess termination before/after commit. Retain full bounded results,
commands, environment and source hashes. Do not run broad benchmarks.

Record data/accounting-master/simulator-storage-reuse-audit-20261024/ with an
explicit reuse/defer decision matrix and exact residuals. A successful audit
nominates a design and smallest conformance reference; it cannot close durable
whole-simulator storage or migration requirements. Refresh controls, repair the
next plan using the findings, and continue the authorized design work.
