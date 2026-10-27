# A first draw changes the second payment problem

26 October 2026. W03/W04/W05/W16; MC05/11/12/26/28/33/34, G16, L01/L02.

Attempt-04 passes 2,828 complete symbolic-state comparisons across 968
mode/rate/receipt cells, with 29,525 assertions and eight failure controls.
The exact reference preserves one fixed or floating coupon interpretation
and one facility right across both dates. Date 2 inherits cash, the payable,
the used-facility flag and the full journal. Six source files are protected.
The accepted writer must not be rerun.

The primary evidence is complete-state equality and equality of the accepted
payment domains, including strict boundaries, against independently authored
financial formulas. The comparator shares only the affine and region value
types. Twelve solver diagnostics and an explicit geometric argument support
this bounded two-dimensional solver; this is not an independent solver
implementation or a general nonlinear certificate.

At coupons I1=I2=6, date-1 drawing leaves cash0.25 and facility debt1. With a
date-2 operating receipt of6, repayment leaves cash5.25. The second interest
expense accrues, but paying6 refuses and retains payable6. Omitting repayment
or replenishing the once-only facility would falsely accept the payment. With
a receipt of7, cash after repayment is6.25 and paying6 leaves0.25.

Throughout the committed-facility family, a receipt of7 and the stipulated
trigger signal admit four feasible policies on reachable observation histories.
All use the same date-1 rule: pay below or at the trigger; draw above it.
At date2, ordinary payment is feasible everywhere. Two observed classes also
permit an optional new draw when the facility was not used on date1, giving
four combinations. This is feasibility, not an optimality ranking: those draws
incur a fee and leave debt beyond the horizon. Under coarse date-1 information
no robust policy exists. Keeping unavailable high-rate facilities in the
family also prevents a robust policy. A receipt of6 fails for all tested
information/facility-family combinations because some admissible rate paths
lack funds, not because the simulator fails.

Three earlier attempts were rejected for inconsistent serialized account
identifiers. The first two local repairs missed the shared cause. The third
failure invalidated the recorded claim that every journal string had been
inspected. A revised plan required a single account vocabulary and a 46-path
complete-journal/account-membership check before one additional full run.
All failed sources, diagnostics and the corrected review remain preserved.
No mathematical comparator or acceptance condition was relaxed.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain the bounded two-date financial reference | Complete symbolic states and accepted domains agree over all declared regions | Solver, source, journal, cash, memory and information checks pass after preserved repairs | Supplied contract/receipt/signals, two-dimensional exact fragment and shared geometry implementation | Connect to existing typed journal execution and add query-budget/checkpoint guarantees | Production execution, scalable compression, actual source admission or arbitrary-horizon correctness |
| Reject the receipt6 robust funding policy | One admissible high/high coupon path cannot pay date2 | Full payable and refusal prefix remain; omitted repayment/redraw controls discriminate | Whether actual future cash or contractual alternatives differ | Retain both receipt hypotheses and obtain source-supported cash/contract restrictions | Rejection of simulation, the research direction, or an actual company's solvency |

Inference status: repaired journal defects were implementation vetoes, while
receipt6 is a correctly computed financial infeasibility under supplied
premises. Statistical ranking is not applicable. Counts and30.20-second CPU
runtime are descriptive; no method-speed, empirical quality or default-change
claim follows. No probability distribution or stochastic seed is used.

Post-run red-team: the model supplies a rectangular rate family, fixed operating
receipts, immediate settlements and advance knowledge of cash-coverage signals.
A real actor may not see those signals; a real facility may permit redraw or
have different repayment timing. Those changes can alter the policy set.
The candidate and oracle also share geometric primitives, so a common solver
defect remains a possible explanation despite focused diagnostics. Larger
models need independent solver/certificate evidence and source admission.

Run manifest: attempt-04/run-manifest.json; Python3.11.15, exact Fraction
arithmetic, CPU with GPU devices intentionally hidden, git
03fea070f089821f4759e49a4466a3399b7fc078. Command and all inputs are retained.
The general common runtime, demand-driven two-date compression, budget/resume
invariants and source-version invalidation remain unimplemented here; the
one-date checks do not establish them for this continuation. No whole W04 or
MC requirement closes. Human/whole-document acceptance remains pending.
