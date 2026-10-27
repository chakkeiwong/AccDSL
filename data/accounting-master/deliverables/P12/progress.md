# P12 repair checkpoint

2026-10-03, repair attempt 2: completed the two structured review repairs for
MC28/MC33/MC35 within G5/G10. Independent result acceptance remains pending.

Checked findings: malformed top-level JSON and nested metrics/result/coverage
values now become failed scheduled repetitions. The CLI regression preserves
four malformed replies plus 11 successful later repetitions in both outputs;
a separate null-metrics regression retains all 15 failures. Unsupported replies
must retain unknown total/unresolved counts, zero completed/feasible/infeasible
counts, no cells and no completeness claim. Mutation tests match bytes and
metrics, so unrelated checks cannot mask false coverage. Missing explicit
unknown measurements also fail.

The phase plan records the skeptical repair audit before rerunning. Reference
answers, denominators, protocols, budgets and mathematical comparators remain
unchanged. No timing-based promotion or scientific-direction rejection follows.
Preparation revision 2 freezes new code/test/plan hashes. The previous benchmark,
report and four changed source texts are preserved verbatim with hashes under
benchmark.json/prior_evidence; the earlier run is labelled superseded because of
the harness defects, without rewriting its original content.

Executed commands:
- CUDA_VISIBLE_DEVICES=-1 python3 -B -m unittest discover -s tests -p
  'test_accounting_p12.py' (initial repaired suite: 36 passed).
- CUDA_VISIBLE_DEVICES=-1 python3 -B scripts/check_accounting_p12.py --prepare
  --repair-archive /tmp/accdsl-p12-before-repair-2.json (passed).
- CUDA_VISIBLE_DEVICES=-1 python3 -B scripts/check_accounting_p12.py --evaluate
  (passed: final P12 37, P04 21 and P06 27 tests; chronology 12/12;
  workload 5/5 cells and 15/15 scheduled repetitions).

Final verification recomputed all scores, checked every current preparation pin
(16 files), confirmed exact rendered-report equality, verified the prior archive
against its captured bytes and confirmed unchanged reference/protocol hashes.
Only the four declared code/test/plan pins differ from the prior preparation.
The structured final verification is retained in benchmark.json.

Changed files: scripts/accounting_benchmark_v1.py;
scripts/check_accounting_p12.py; tests/test_accounting_p12.py;
docs/plans/accounting-p12-benchmark-plan.md;
data/accounting-master/deliverables/P12/benchmark.json;
data/accounting-master/deliverables/P12/result.md; this checkpoint.
No controller, corpus, prerequisite engine or fixture was edited.

No required P12 repair deliverable remains unfinished. Next: independent result
review. Wider internal work remains: provisional source annotation, semantic
duplicates, unidentified debt/swap allocation and realistic workload scaling.
The purposive nine-family/eight-year panel is dependent and exposed. Accounting
validity, forecast validity, production capacity, statistical ranking, clean
heldout status, human acceptance and wider gap closure remain unestablished.
