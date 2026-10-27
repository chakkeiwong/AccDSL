# P11 repair checkpoint

Scope: MC23, MC25, MC31; bounded G2/G9 evidence. Recovery verified actual deliverables, all nine fixtures, structured prior records, source hashes and the shared-runtime call chain. No prior worker log was read. The approved evidence contract/default audit and recovery rationale are preserved in result.md.

Completed repair: failed ledger probes can no longer become an Unavailable family when selection is null; failures preserve candidate reasons. Adapter validation now rejects mismatched valuation dates, Arelle loader errors and partial/failed Docling conversion even when expected numerical/table values match. Two meaningful regression tests were added and existing valuation negative cases expanded.

Fresh check: PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES=-1 python3 -B scripts/check_accounting_p11.py --output-dir data/accounting-master/deliverables/P11 exited 0. It ran 21 P11 tests and 11 P03 prerequisite tests, all passing. Six textual/typed executions match semantic IR, results and independent arithmetic oracles. Complete subprocess outputs, commands, conventions, inputs and hashes are retained in integrations.json. Source hashes match executed files; protected package/compiler/controller hashes match phase entry.

Actual discovery: Arelle, ACTUS, QuantLib, Docling, Beancount, Ledger and hledger are absent in the captured interpreter/PATH and declared local ACTUS paths. Ledger selection is null. Zero external integrations completed; no installation or download was attempted. GPU devices were intentionally hidden.

Changed this attempt: scripts/accounting_integrations_v1.py, tests/test_accounting_p11.py, and integrations.json, result.md, progress.md in this directory. Full phase contributions (four source/test files and nine fixtures) and hashes are listed in integrations.json. Protected supervisor files, frozen sources and snapshots were not edited.

Next justified step: independent result review of the bounded implementation. Remaining work: actual pinned upstream exchanges after a known availability change; ACTUS/CLI wire translators; inline-XBRL scale and PDF page/table locations. General frontend equivalence, accounting validity, forecast validity, human usability/acceptance and MC01–MC35/G1–G18 closure remain unestablished. No active check process remains.
