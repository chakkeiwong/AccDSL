# Separate nonoperating profit components in the indirect cash bridge

25 October 2026. S2–S5; MC02/06/08/10–13/16/19–22/24–28/30/32–35.
Baseline: DeclaredIndirectCash/1 and its twelve passing focused tests, including
sixteen cases on two charts. Those tests take about seven minutes because they
replay the unchanged declared program. Preserve the exact files and log before
creating a successor. Version 4.25 remains the governing manuscript.

## Question, audit and evidence contract

The current candidate refuses a sale of plant for 12 with carrying amount 10
and gain 2. The recorded transaction is balanced and valid within its synthetic
scope. Its investing cash is 12 and operating cash is zero. The limitation is
the bridge's absence of an explicit nonoperating profit classification, not a
failure of indirect reporting or a reason to stop the planned repair.

Let P be profit, W and N be the existing working-capital and noncash adjustments,
X the signed excluded balance-sheet movements, and R the signed income/expense
postings explicitly classified as nonoperating. The bridge is P+W+N+R. The
independent exclusion check becomes X+R+investing_cash+financing_cash=0. For the
sale, P=2, X=-10, R=-2 and investing_cash=12. Both checks then give zero operating
cash without a plug. A disposal loss instead gives a positive R. Financing
interest can also be represented by explicitly excluding its expense and
payable movements; this classification is a supplied example, not a standard.

Skeptical audit: retain the old v1 file unchanged and implement a versioned v2
profile with exact per-method classifications for every gross income/expense
account, in addition to balance-sheet classifications. Every used method and
every gross posting account must be represented even if its net is zero. No
classification is inferred from its label, amount, sign or cash residual.
Extra and missing classifications refuse. A hash binds a supplied interpretation;
it does not establish accounting validity. Distinct classifications that satisfy
the algebra may remain observationally indistinguishable, with admission false.

The plan passes: the comparator is independently stated transaction arithmetic
and the unchanged v1 results for cases it supports. Success requires disposal
gain/loss and operating/financing-interest cases on both charts, exact unchanged
v1 projections for existing cases, prefix/carry lineage, and gross-posting
counterexamples. Wrong gain classification, rehashed forged results, missing
or extra policy entries and changed dependency bytes veto acceptance. Numeric
identity alone cannot promote the policy. This is deterministic conformance,
not forecasting, statistical evidence or accounting compliance.

## Execution and preservation

1. Save v1 source/tests/examples, passing and initial failure logs, plan and
   dependency hashes under declared-indirect-cash-20261025/baseline-v1/.
   Record the known unsupported gain case; do not claim recorded full replay
   until it is actually performed.
2. Create declared_indirect_cash_v2.py and successor examples/tests. Run a small
   gain/loss discriminator first, then focused checks and relevant regressions.
   Store complete cases separately to keep payloads and memory bounded.
3. Preserve exact requests/results, policies, dependency hashes and CPU-only
   environment in declared-indirect-profit-components-20261025/. A replay
   verifies every saved result against the current source. Report disagreements
   honestly and repair before manuscript integration.
4. Integrate the explanatory algebra into the next manuscript only after the
   finite contract passes. Preserve prior sources and inspect rendered pages.

Use python3 -B, no package installation or GPU libraries. Full regression may
exceed five minutes; keep local logs, progress updates and bounded tool results.
Primary decision: exact engineering correspondence. Veto: integrity/lineage/
algebra failure. Explanatory only: runtime, case count and alternative consistent
policies. Continued failure of a candidate triggers its identified repair;
only invalid evidence or a broken stated assumption stops dependent work.
