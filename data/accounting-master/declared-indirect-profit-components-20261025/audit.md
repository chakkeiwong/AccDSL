# Nonoperating profit-component repair audit

25 October 2026. The pre-run contract is
docs/plans/accounting-indirect-profit-components-20261025.md. The v1 source,
tests, examples and passing 12-test log are preserved in baseline-v1/ under
the preceding indirect-cash directory. Its unsupported disposal is a candidate
limitation; it triggers this planned repair, not rejection of the direction.

The first discriminators now yield gain 2 with adjustment -2 and loss -2 with
adjustment +2; each has operating cash zero. Under the explicitly financing
interest convention, profit 44/5, working-capital adjustment -8 and interest
exclusion 31/5 give operating cash 7. The original financial report and cash
classifications remain unchanged. No residual is accepted as an adjustment.

Eleven focused tests pass in 33.414 seconds. They include exact gross profit
coverage even when postings net to zero, altered/rehashed result refusal,
gain misclassification, complete import populations, dependency and prefix
preservation, and a counterexample to classification uniqueness. Policy bounds
now run before expensive program replay, with a test proving that recursive
policy data never reaches replay. The baseline v1 implementation is unchanged.

The finite contract assigns one interpretation per account within each method.
It does not yet split one account's postings across categories or establish
actual accounting policy. Working-capital versus noncash labeling can remain
algebraically indistinguishable; classification_admission is always false.
Ordinary gain/loss adjustments here are local algebra on explicit synthetic
events, not externally sourced standards guidance.

Full record/replay is split into per-case files, with bounded progress logs.
Original v1 supported cases are compared on their common numerical and report
fields. Under financing interest, the successor moves 31/5 from the earlier
noncash category to the explicit nonoperating-profit adjustment; their sum
and operating cash remain equal. This is an intentional explanation change,
not an assertion that the category fields are byte-identical.

The source-lock includes all imported project modules, fixture files, tests,
plans and protected v1 bytes. No installation, downloaded code, GPU execution,
publication, professional engagement or forecast is involved.
