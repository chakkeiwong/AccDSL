# Reconcile insurer fiscal profit and cash using declared classifications

25 October2026. S2-S5; MC02/06-13/16/19-22/24-28/30/32-35.
Dependency: accepted InsuranceFiscalBook/1 and its exact replay; frozen
DeclaredIndirectCash/2 is the comparator, not a new reporting implementation.
The current fiscal record passes14 focused tests,71 regressions and8 cases;
read-only replay remains a prerequisite to executing this dependent comparison.

## Intent, assumptions and skeptical audit

Question: can the existing indirect-cash explanation consume all three fiscal
reports from the exact insurer trace without treating the loss component as
another liability, carrying previous-period profit forward or inventing a
balancing adjustment? Candidate: a finite composition record pairing the exact
fiscal trace with caller-supplied method/account classifications. Prefer a
testable composition with the existing bridge over creating another wrapper
that only repeats its calculation. No frozen engine changes are planned.

The audit passes for a conditional comparison. The existing bridge already
selects the interval following the previous carry and accepts report or carry
IDs. Its gross-posting requirement prevents silent omission of a zero reversal.
The insurer liability's finance movements and service releases need different
declared explanations even though they affect one liability account. A policy
can assign categories per method; no method in the retained trace mixes those
movements. All income/expense postings remain in the operating-profit base.

Primary fixture policy: classify liability movements in the finance methods
as noncash_profit and liability releases in service methods as working_capital.
Classify every gross income/expense posting as operating. These are explicitly
supplied illustrative explanations, not inferred accounting classifications or
default insurance presentation. Claims have no noncash balance-sheet account.
Alternative policy: classify all liability movement as noncash_profit; total
cash must agree while the explanatory split differs. This deliberately shows
that reconciliation cannot select a unique accounting classification.

For2025 expect P=W=N=R=0 and cash0. For2026 expect profit-5, working adjustment
-55, noncash adjustment+10, removed profit0 and operating cash-50. For2027
expect profit10, working adjustment-50, noncash adjustment-5 and cash-45.
The all-noncash policy instead has working0 and noncash-45,-55. Both produce
the same cash and retain the six original loss origins separately from journals.
The zero-loss case preserves zero gross reversal entries. All amounts are
exact rationals in the explicit illustrative CU/XCU units.

Primary criterion: full bridge request/result replay, matching exact fiscal
financial reports and openings, all6 event identities/gross postings, correct
period profit and signed cash under both supplied policies on both charts and
both native cases. Vetoes: lost zero posting, stale method hash after fiscal
rebasing, mixing periods, fake extra loss liability, forged/rehashed execution,
missing classification or omitted gross posting. A missing or unsupported
classification must not be filled by a residual. Runtime/counts explain only.
Alternative valid splits prevent a uniqueness or accounting-admission claim.

1. Verify accepted fiscal and indirect engine hashes before comparison.
2. Build explicit policies from named roles and reviewed native method kinds;
   require exact per-period method sets, including the empty2025 set.
3. Compare all annual statements and both classifications; test omitted zero
   reversal and liability mappings, stale pre-carry hashes and changed traces.
4. Record complete exchanges, source locks, targeted tests and exact replay.
5. Integrate the explanatory result only if it adds an actual reader decision;
   then reassess whole-company/sector gaps and stop adding redundant examples.

No current standards, default classification, actual source admission, insurer
completeness or forecast claim. No whole row closes; retain53/6/46, S1-S5
partial,S6 held,S7/E3 deferred. Unknown actual source facts are separate from
the exact comparison. No installs, workers, commits, GPU, publication or fees.
Artifacts: data/accounting-master/insurance-statement-bridge-20261025/.
