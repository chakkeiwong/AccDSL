# P04 recovery checkpoint

Current execution: `20261002T233421-cea9e631/P04/execution-0`.
Inspected the current approved plan and issue-free review, previous structured
check/repair records, timed-out review process, checker and protection helpers,
profile and numerical tests. Before edits, all 393 current execution-inventory
hashes and all 384 historical phase-entry hashes matched actual files. Both
required deliverables exist but describe the previous run, not fresh acceptance.

Skeptical audit passed for the focused repair: the checker really uses stale
approval/inventory paths. Preserve the historical baseline separately and use the
supervisor's current `execution-0/pre-edit-files.json` for execution protection.
Independent posting enumeration and analytic bounds remain the numerical
comparators. Test counts and runtime are explanatory, never accounting or forecast
promotion criteria. No stochastic comparison or new default is proposed.
Python/Fraction/existing Z3 and explicit caller budgets retain the profile's
audited assumptions; GPU devices will intentionally be hidden.
Missing/malformed/unapproved provenance and protection failures stop execution
before deliverable writes; numerical failures trigger local repair. Current
approval, exact commands, source hashes and observed assertions answer the bounded
engineering question; wider history completeness is not inferred.

Research intent, diagnostic roles, defaults and the shared model-error pre-mortem
remain in `docs/design/spec/reconstruction-profile-v1.md`. MC08–MC12, MC18 and MC26
retain their original scope and acceptance criteria.

Implemented: explicit same-run approval/execution-inventory arguments; validated
approval structure, issue-free review and controller-compatible plan hash;
separate current and historical hashes; unchanged protection exclusions; actual
changed-file selection; failure reports without success assertions.
Changed source/code/test files: `scripts/check_accounting_p04.py`,
`tests/test_accounting_p04.py`, `docs/design/spec/reconstruction-profile-v1.md`,
`docs/design/fixtures/p04-reconstruction-cases-v1.json`. Numerical solver and
construction source are unchanged in this recovery.

Executed: `CUDA_VISIBLE_DEVICES=-1 python3 -B -m unittest discover -s tests
-p 'test_accounting_p04.py' -v` (21 passing, 1.155 seconds) and the analogous
`test_accounting_p03.py` command (11 passing, 2.579 seconds). No failures, errors
or skips. Four new recorded checker obligations use disposable-tree tests and
simulated check outcomes only for reporting behavior; the 17 existing numerical
obligations remain independently executed.

Completed regeneration and inspection of conformance.json and result.md with
`CUDA_VISIBLE_DEVICES=-1 python3 -B scripts/check_accounting_p04.py
--output-dir data/accounting-master/deliverables/P04
--execution-inventory data/accounting-master/runs/20261002T233421-cea9e631/P04/execution-0/pre-edit-files.json
--approved-plan data/accounting-master/runs/20261002T233421-cea9e631/P04/approved-plan.json`.
Checker result: PASS, 21 P04 tests, 11 P03 regressions, 21/21 obligations; no
failures, errors, skips, missing/duplicate obligations or protection failures.
Wall time 4.406002 seconds. All 394 recorded input/source/test/provenance hashes
match after execution. All 384 protected inputs remain unchanged. Current plan
hash is `85a97c5299d1ee74c369d6257d8cb8f10503ff0f5cee687e9ae09df87dc86717`.
The manifest records the four changed source/code/test files plus the three P04
output files, separately from the nine cumulative phase contributions.

No required implementation deliverable is unfinished. Independent result review
remains pending with the supervisor; the prior timed-out review is not acceptance.
Accounting validity, empirical forecast validity, arbitrary-history completeness
and human acceptance remain unestablished. All wider MC/G obligations remain open.
