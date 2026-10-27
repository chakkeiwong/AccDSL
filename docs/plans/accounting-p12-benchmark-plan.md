# P12 bounded benchmark, protocol v1

This implementation executes the approved P12 plan for MC28 (workload evidence),
MC33 (meaningful acceptance) and MC35 (internal preparation), within G5/G10.
The structured plan review returned AGREE; recovery inspection confirmed there
were no earlier P12 deliverables. All wider MC01–MC35/G1–G18 obligations remain.

## Research intent and evidence contract (before execution)

Question: do the existing cumulative-subtraction and rational-linear components
conform to a finite, independently specified task, and what resources do these
small workloads actually consume? Source-reference preparation is a separate
activity: four Apple records are provisional, not an extraction accuracy test.

The mechanism under test is context/revision-aware subtraction and bounded
finite assignment enumeration. The exact comparators are manually derived
Fraction subtraction and a standard-library Cartesian-product enumerator on
identical domains, rational weights and thresholds. No comparative performance
claim is planned. A naive finite enumerator is sufficient for this finite
correctness question; a tuned classical performance ladder is out of scope.

Primary criterion: all 12 chronology cases and all five workload cells satisfy
their complete, predeclared admissibility rules (three repetitions per workload
cell). Denominators are 12 overall, three valid, nine invalid; workloads are five
cells / 15 scheduled repetitions. The four source records are preparation only,
with zero extraction evaluations. Every missing, duplicate, malformed, extra,
crashed, timed-out or unexpectedly abstaining answer fails. Correct rejection
passes only the designated invalid cases. No post-result exclusion is allowed.

Promotion vetoes: incorrect amount/context/period, incorrect rejection code,
lost or fabricated assignments, mismatched outputs, false completeness, missing
resource measurements, or unsupported cases presented as supported. Continuation
vetoes: changed frozen source/reference/input/code hashes, broken scorer, failed
preparation or exhausted 180-second aggregate measurement ceiling. A candidate
failure alone triggers diagnosis, not reference editing or direction rejection.

Explanatory only: wall/CPU time, peak RSS, Python allocation peak, serialized
bytes, formula size and branch counts. No timings, source pages, smoke tests or
schema checks establish production capacity, accounting validity or superiority.
No population uncertainty interval is meaningful for this purposive deterministic
census. Three fresh-process timing repetitions are descriptive, without ranking,
confidence intervals or stochastic superiority claims.

## Defaults and assumptions

| Choice / provenance | Justification and status | Failure mode / earliest check |
| --- | --- | --- |
| 12 synthetic cases / approved plan | Finite conformance baseline | Narrow coverage; explicit case inventory and no general chronology claim |
| Gregorian half-open intervals / P06 contract | Reviewed interface default within this task | Apple fiscal periods mistaken for Gregorian quarters; separate real-source record and boundary assertions |
| Exact Fraction amounts / P04/P06 contracts | Reviewed exactness default | Float/coercion drift; rational field comparison |
| Binary sizes 1, 3, 5 / approved plan | Convenience workloads, not production limits | Tiny tasks conceal scaling; report facts/constraints/branches and no capacity extrapolation |
| Rational weights and thresholds / fixture v1 | Synthetic hypothesis; covers feasible and infeasible branches | Trivial all-feasible test; require both classifications |
| Explicit seven Budget fields / solver contract | Convenience caps; 1,000 slots, 10,000 nodes, 64 assignments/cells, 3,000 ms elapsed, 1,000 ms per solver, 1,000,000 rlimit | Unexpected partial search; smallest workload smoke and coverage reconciliation |
| Partial cell: assignment cap 2 / approved plan | Deliberate graceful-failure test | False complete answer; compare visited prefix and unresolved remainder |
| Three repetitions, 10 s child / approved plan | Descriptive measurements, fresh synchronous processes | Startup dominates, platform memory units differ; retain process and kernel time separately |
| Existing Python/Z3, CPU only / worker constraint | Convenience environment, not a hardware comparison | Import/process mismatch; CPU-hidden import smoke |
| Nine proposed issuer-family roles / frozen protocol | Historical candidate split, not clean holdout | Acquisition QA, development and annotation leakage; separate exposure fields, keep every year/language/revision together |
| Four source records / approved plan | Internal provisional annotation | Circular truth; inspect original text/HTML contexts, retain unknown debt allocation and unadjudicated rounding |

## Preparation and scoring

Preparation validates schema, unique identifiers, denominators, source hashes,
exact source spans, expected outcomes, ambiguity and exposure fields. It saves
protocol, source/reference/input/code hashes and a preparation digest in
`data/accounting-master/deliverables/P12/benchmark.json`. Evaluation is a separate
invocation and verifies that digest and every pinned input before importing the
evaluated components. Reference construction never calls those components.

T3 cases: ordinary subtraction, negative residual, matched revised observations;
then instant, concept, context, calendar, start, nesting, unknown revision,
incompatible revision, and incorrectly scoped revision-exception rejections.

T5 cells: 1/3/5 binary choices with rational weighted sum constrained above;
5 choices with an insufficient assignment budget; and a nonlinear unsupported
fragment. The independent enumerator freezes every feasible assignment/output.
All explored feasible/infeasible/unresolved branches must reconcile. Unsupported
coverage must remain unknown, with no implied completeness. Source pages are
never used as workload units.

Each workload repetition runs in a fresh synchronous child, sequentially. Record
wall time, CPU time, peak RSS (platform units and normalized bytes), Python
allocation peak (not total memory), input/output bytes and complete solver reply.
Timeouts and aggregate-budget skips remain failures in the 15-run denominator.

Pre-mortem: self-consistent wrong references can pass; independent arithmetic,
original context inspection and scorer mutation tests reduce this risk without
constituting professional adjudication. Imports may dominate tiny runtimes;
record scope explicitly. A resource cap can cause partial output without
invalidating the method; the planned partial case distinguishes this from false
completeness. Repeated years and copied tables can suggest an artificial sample
size; report family dependence and exact-hash duplicate groups, leaving semantic
duplicates incomplete.

## Exact execution and retained evidence

Use `CUDA_VISIBLE_DEVICES=-1` before Python imports. No GPU detection is needed.

```
CUDA_VISIBLE_DEVICES=-1 python3 -B -m unittest discover -s tests -p 'test_accounting_p12.py'
CUDA_VISIBLE_DEVICES=-1 python3 -B -m unittest discover -s tests -p 'test_accounting_p04.py'
CUDA_VISIBLE_DEVICES=-1 python3 -B -m unittest discover -s tests -p 'test_accounting_p06.py'
CUDA_VISIBLE_DEVICES=-1 python3 -B scripts/check_accounting_p12.py --prepare
CUDA_VISIBLE_DEVICES=-1 python3 -B scripts/check_accounting_p12.py --evaluate
```

Record command results in benchmark.json; result.md includes decision and
inference tables, remaining internal work, alternative explanations and actual
manifest fields. No extra supervisor-directory outputs are created.

Skeptical plan audit passed before implementation/measurement: comparators answer
the finite correctness question, proxies cannot promote acceptance, stop limits
are explicit, environment is checked, exposed/dependent families are disclosed,
and incomplete searches remain visible. No broad accounting, forecast, production,
clean-heldout, default-readiness or human acceptance conclusion is authorized.

## Reviewed-result repair, harness revision 2 (before rerun)

The result review found harness failures, not a failure of the scientific
direction: non-object child JSON and null metrics could abort evaluation, and
unsupported responses could claim zero unresolved branches. The repair retains
the same 12 chronology cases, five workload cells, 15 repetitions, exact
comparators, source records and every resource budget. Its primary check is
that malformed replies fail their scheduled repetition while later repetitions
and both result files remain available. Unsupported coverage must have unknown
total/unresolved counts, zero completed/feasible/infeasible counts, no cells and
absent or explicitly false completeness. Mutations synchronize the reported metrics and
serialized length so incidental byte mismatches cannot hide scoring defects.

The skeptical repair audit passes: no baseline or reference answer changes,
no new proxy promotion, no discarded failed cases, and no comparison of timing
results across harness versions. Environment and stop limits remain as above.
Response structure checks reject malformed evidence without modifying valid
solver results. Regression tests cover the CLI persistence path as well as
the scorer; this exposes a report-rendering exception that a scorer-only check
would miss. Existing P04/P06 suites check that prerequisite behavior is retained.

Preserve the exact old benchmark/report and changed source texts in a hashed
archive inside benchmark.json. Mark that evidence as superseded by the harness
review, without changing its original contents. Freeze revision 2 separately,
including its new code/test/plan hashes, and require unchanged reference hashes.
The preparation command for this repair is:

```
CUDA_VISIBLE_DEVICES=-1 python3 -B scripts/check_accounting_p12.py --prepare --repair-archive /tmp/accdsl-p12-before-repair-2.json
CUDA_VISIBLE_DEVICES=-1 python3 -B scripts/check_accounting_p12.py --evaluate
```

The temporary archive is only an input to preparation; its full contents are
retained in the declared benchmark deliverable. New measurements and checks
receive a new preparation digest. The old timings support no ranking or claim
about realistic capacity. Independent result acceptance remains pending.
