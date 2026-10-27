# P07 completion checkpoint

Completed the bounded implementation recovery slice for MC04, MC25, MC27 and
MC34 within G17/G18. Independent result acceptance remains pending.
Current approved plan:
`data/accounting-master/runs/20261003T034034-eed41196/P07/approved-plan.json`.
Current supervisor inventory:
`data/accounting-master/runs/20261003T034034-eed41196/P07/execution-0/pre-edit-files.json`.
Historical inventories, process records and protected releases were preserved.

The structured recovery snapshot and actual file hashes agreed. Prior timeout
records were not treated as acceptance. Skeptical audit retained direct P05
execution and its independent journal/statement verifier as matched comparators.
Exact state, journals, receipts, replay and lineage are criteria; counts/timing
are descriptive. Partial commits, stale reuse, lost history, invalid migration
and protected changes veto acceptance. No economic or numerical defaults changed.

Repaired stale Git provenance: the checker now observes HEAD through a bounded
read-only command and records actual unavailability reasons. Tests cover SHA-1
and SHA-256 IDs, command failure, a missing executable, timeout and invalid output.
The five-second timeout is a convenience bound for local metadata lookup, not a
scientific threshold. Content hashes identify uncommitted checked files.
A final consistency inspection also found that files_checked included exempt P07
files. A focused regression failed (2 versus 1), then passed after the counter
repair. Protection exclusions and hash comparisons were not weakened.

Executed commands, with full output retained in /tmp/accdsl-p07-20261003-034034-*.log:

```text
CUDA_VISIBLE_DEVICES=-1 python3 -B -m unittest discover -s tests -p 'test_accounting_p07.py' -v
CUDA_VISIBLE_DEVICES=-1 python3 -B -m unittest discover -s tests -p 'test_accounting_p0[3-6].py' -v
CUDA_VISIBLE_DEVICES=-1 python3 -B -m unittest discover -s tests -p 'test_accounting_p07.py' -k checker_missing_obligation_and_protected_hash_veto -v
CUDA_VISIBLE_DEVICES=-1 python3 -B scripts/check_accounting_p07.py --output-dir data/accounting-master/deliverables/P07 --approved-plan data/accounting-master/runs/20261003T034034-eed41196/P07/approved-plan.json --execution-inventory data/accounting-master/runs/20261003T034034-eed41196/P07/execution-0/pre-edit-files.json
```

Separate suites passed 27 P07 tests (10.488 seconds) and 90 prerequisite tests
(4.548 seconds). The final checker reran all 117 tests after the counter repair:
no failures/skips, eight obligation groups, 20.877 seconds total. It captured six
transaction failures and two killed-writer outcomes, exact comparison across 32
event boundaries, 132 migration mappings and 133 invalidated correction
dependents. Unrelated and historical results survived; SQLite integrity and
foreign keys passed. Git HEAD is 8e3b2628df8c89f7315119170b82624d536bc3e5.

Separate final file/JSON consistency checks verified source/input/plan/inventory
hashes, Git provenance, counts, coverage, output existence and equal uninterrupted/
reopened result hashes. All 423 protected files in the 430-entry inventory match.
Only scripts/check_accounting_p07.py, tests/test_accounting_p07.py, recovery.json,
result.md and this checkpoint changed during this attempt. The prior P07 modules
scripts/company_persistence_v1.py and docs/design/spec/review-persistence-profile-v1.md
remain hash-matched; all four phase source files are recorded in recovery.json.

Both required deliverables are complete. Next check: independent result review
against all four original criteria and the current approved plan. No implementation
deliverable remains unfinished in this slice. Scope remains one local writer,
deterministic P05 operations and representation-only migration. Production
stochastic execution is Unsupported. General hardware durability, accounting and
forecast validity, source truth and human acceptance remain unestablished; wider
MC01–MC35/G1–G18 obligations remain open.
