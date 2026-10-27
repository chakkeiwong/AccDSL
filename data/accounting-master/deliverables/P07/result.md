# P07 executed result

Bounded engineering conformance passed: 117 tests, exact P05 comparison,
32 reopened event boundaries, transaction faults and killed writers before/after
commit. SQLite integrity and foreign-key checks passed. The evidence file retains
actual state, ordered journals, receipts, dependency edges, migration mappings and
correction descendants. All 423 protected pre-existing
files match the supplied 430-entry inventory; permitted
P07 phase files are excluded from the protection check.

| Decision | Primary criterion | Veto diagnostics | Main uncertainty | Next action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Submit for independent review | Exact real P05/persistent/reopened equivalence passed | Rollback, retry, source hashes, stale reuse and migration checks passed | Filesystem/hardware failures beyond process interruption | Independent result review | Production durability, accounting or forecast validity |

The actual 120-to-110 correction preserves the original report and invalidates
its transitive dependents. Tests separately reject the 720 extraction against a
120 literal and retain its correction link. Accepted alternatives remain visible
as conflict sets, with explicit choice groups. Availability is selected by P06;
unknown source availability is not inferred. New descendants of stale runs are
also denied current-view reuse, including dependencies created after the review
decision directly from superseded readings. Historical replay remains available.
Self-supersession is rejected before mutation; the accepted reading and evidence
view remain usable after reopening the store.
State, journal and measurement nodes are included in the invalidation closure.
Canonical rational payloads survive persistence and reopening. Explicit phases
separate event identities; P05 events use the documented P05-period-step phase.

The schema-1 fixture contains a real executed run. Migration adds canonical
payloads transactionally, retaining original text, digests, IDs and mappings.
Injected failure and semantic changes roll back; repeated migration is idempotent.
Legacy immutable triggers are restored transactionally. Foreign-key failures and
missing execution lineage veto migration before commit. Interrupted initial store
creation rolls back the entire schema, and a subsequent open recovers normally.
Source verification follows each run's dependencies, preserving unrelated runs
when an unrelated retained source fails verification. Fault outcomes in the JSON
are observations captured from executed tests, including process exit codes,
committed cursors and before/after state hashes.
Production stochastic execution is Unsupported. Reference hash tuple checks
establish identity and domain separation only.

Strongest alternative explanation: the bounded P05 fixture omits many real-company
operations and shares its engine with the adapter. The independent journal and
statement verifier checks the economic outputs separately, but does not establish
professional treatment validity. A mismatch on another supported schedule, a
partial commit or historical payload drift would overturn acceptance. Hardware
power loss, multiple writers, general accounting, forecast validity and human
acceptance remain untested. No stochastic-method ranking is made.

Changed implementation files: scripts/company_persistence_v1.py, scripts/check_accounting_p07.py, tests/test_accounting_p07.py, docs/design/spec/review-persistence-profile-v1.md. Exact hashes, command,
environment, approved plan and input hashes are in recovery.json. No prior release
or master-control file was changed. MC01–MC35 and wider G1–G18 remain active.
Git HEAD: `8e3b2628df8c89f7315119170b82624d536bc3e5`. Content hashes identify the checked files, including uncommitted work;
HEAD alone does not identify the executed implementation.
