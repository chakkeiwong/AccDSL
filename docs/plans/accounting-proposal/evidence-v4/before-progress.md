# P15 progress — MC25/G18 reconciliation

Review scope: bounded_partial_work. MC25/G18 have been reconciled and remain partial; independent review is pending. The earlier complete-audit claim remains retracted. The 53-row expansion exceeded the approved eight-assessment review slice and remains provisional outside the repaired scope. Product implementation is disabled; human acceptance is pending.

Checked sources: P07 code/tests match their retained manifest hashes. Seven claim groups distinguish transaction/initialization rollback, replay, conflicts, invalidation/history, canonical rational encoding, identities/order and schema 1→2 migration from wider obligations. Comparator: direct P05 execution shares the Engine, with a separate journal/statement verifier. No product tests or scientific runs were added or rerun.

Skeptical audit passed: retained P07 evidence is the baseline; counts and structural checks are diagnostics only. One writer, exact rationals, deterministic P05 inputs and a schema 1→2 conversion cannot select product defaults. Independent implementations, arbitrary commutation, assessed stochastic streams, general accounting/forecast validity and human acceptance are unestablished.

Saved: p15-p07-reconciliation-v3.json/.md; only MC25/G18 rows plus related audit metadata changed in coverage.json. Result/progress now describe this bounded task. evidence-v3 contains before-images, preservation hashes and retained P07 execution provenance. Prior v1/v2 documents/reports are preserved. The two v3 reports validate current inputs and resolve changed historical v2 inputs against before-images.

Exact checks: python3 -B docs/plans/accounting-proposal/p15-reference-validator-v3.py; python3 -B scripts/check_accounting_proposal.py --phase P15 --check. Fresh reports: p15-assessment-validation-v3.json, p15-reference-validation-v3.json and p15-registered-check-p07-reconciliation-v3.json. Process outcomes, final hashes and independent verification are saved in p15-p07-completion-v3.json. Their passed/errors fields govern success; structural success is not substantive acceptance.

Changed paths: P15 coverage.json/result.md/progress.md; evidence-v3 snapshots/capture records; reconciliation JSON/analysis; v3 reference validator and its reports; fresh checker/process captures; final completion record. The reference report/completion record enumerate every path. Product source, controller/checker, tests and frozen evidence remain unchanged.

Stop condition: both partial rows reconciled, valid source anchors/current hashes, historical bytes preserved, and both v3 reports plus registered checker passing. Next task after independent bounded review: remaining provisional assessments and gap-specific obligations, then preliminary P15 profile comparison and full substantive review. Wider MC01–MC35/G1–G18 remain open at their stated scopes; P08 needs_repair and P09/P10/P13/P14 are unexecuted.
