# P16 bounded result: stale-model comparison

Completed the reviewed MA05c supplement and valid old-version control. P16 is
PARTIAL; product implementation remains disabled. This work addresses MC12/G15
with MC08, MC10, MC14, MC18 and MC25. All original P16 criteria and wider
MC01–MC35/G1–G18 remain active. The preceding result is preserved exactly at
`docs/design/proposal/architecture/uncertainty-stale-prior-result-v1.md`.

Both numerical model versions are available and have identical laws. Both
representations specify probability 5/6 when v1 is explicitly requested with its
v1 attachment and event. Selecting v2 while retaining those old bindings instead
specifies RETAINED_ONLY, MODEL_VERSION_STALE, invalid requested structure,
unresolved requested mathematics, not_computed and probability=null. The old
law remains normalized and attached as a synthetic assumption; empirical
justification remains not_established. No product evaluator was executed.

The owned form supplies two local immutable model definitions and versioned
family mappings. The diagnostic derives two model mismatches in each encoding
and the additional mapping mismatch in the owned encoding. It checks complete
declarations, both coordinate/outcome bijections, assignments, purposes, cutoffs,
admission, receipt correspondence and unchanged old records. Both cases declare
model:tri@1 and model:tri@2. This repairs the original MA05c transitive-dependency
omission. New receipts explicitly defer model_migration, repairing its original
future-dependency omission without rewriting the preserved comparator.

Actual command:
`PYTHONDONTWRITEBYTECODE=1 python3 docs/design/proposal/architecture/uncertainty-stale-diagnostic-v1.py --output docs/design/proposal/architecture/uncertainty-stale-verification-v1.json`

The saved nonempty JSON records 420 passing document checks, no failures, exact
input hashes, per-encoding observations, command, Python environment, elapsed
time and limitations. The pre-check recovered 67 architecture references, 11
prior event-diagnostic hashes and 149 prior checker hashes without mismatch.
Those earlier diagnostic suites were not rerun.

| Decision | Primary criterion | Veto diagnostics | Main uncertainty | Next justified action | Not concluded |
|---|---|---|---|---|---|
| Bounded examples author-complete | Same valid/stale binding decisions; control 5/6 | No pin, declaration, mapping, arithmetic or receipt failure in 420 checks | Independent semantic review pending | Review this slice; next compare malformed inputs | General equivalence or architecture preference |
| Keep P16 partial | Six of nine contracts remain unfinished | Whole architecture structural gate previously failed | Profile, integrated criteria, dependencies and fourteen decisions unresolved | Continue bounded proposal contracts | Product readiness or human acceptance |

Engineering ledger: specified document fixtures and deterministic author checks.
Numerical ledger: exact finite probability for the valid requests; independent
normalization of the preserved law, with no stale-request probability.
Scientific ledger: synthetic masses; no accounting or empirical forecast
validity, no stochastic ranking, and no performance comparison.

Post-check red team: both encodings were authored together, so shared mistaken
semantics remain possible despite checked pins and arithmetic. A counterexample
to the binding precedence or an overlooked required dependency would overturn
this slice's acceptance. Finite explicit maps do not establish general
invalidation, migration or persistence behavior. Independent review remains
required; ordinary reader or human acceptance is not established by checks.

Changed files: the three P16 deliverables architecture.json, result.md and
progress.md; under docs/design/proposal/architecture/, the new
uncertainty-stale-comparison-v1.md, uncertainty-stale-fixtures-v1.json,
uncertainty-stale-diagnostic-v1.py, uncertainty-stale-verification-v1.json and
uncertainty-stale-prior-result-v1.md. No production modules or tests were added.
Fresh structural evidence will be saved as uncertainty-stale-structural-v1.json
and uncertainty-stale-structural-execution-v1.json; its result is recorded below.

Next task: malformed-input rejection comparisons, followed by remaining
family/support/purpose and partition/projection failures. Then conditioning,
duplicate-evidence protection, likelihood updates and conditional outcomes.
Six contracts (uncertainty, accounting, language/IR, persistence, interfaces,
failure semantics), initial-profile selection, integrated acceptance/dependency
order and fourteen decisions remain unfinished. E05 source limits, P17 authority,
research and real-company obligations and independent P16 review remain active.

Registered structural result: the unchanged checker exited 1 with 165/166 checks
passing; only whole architecture contracts failed. Individual contract/profile
checks are not reached. The initial report is uncertainty-stale-structural-v1.json
with its execution record. Because this result note is itself hashed by the
checker, the final post-note recheck is saved in fresh
uncertainty-stale-structural-v2.json and uncertainty-stale-structural-execution-v2.json.
Final integrity observations are in uncertainty-stale-integrity-v1.json.
These five structural/integrity files are additional new files in the allowed
architecture directory. The prior result matches its preceding checker's exact
SHA-256. All previously checked inputs outside the three allowed deliverables
remain unchanged. Final reference checks cover 75 architecture pins, ten new
fixture-diagnostic inputs and 153 structural inputs. Independent review remains
pending; the next task is the bounded malformed-input comparison.
