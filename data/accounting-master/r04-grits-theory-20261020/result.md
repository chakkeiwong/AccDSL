# Original GriTS: exact target, implemented scores and bounds

20 October 2026. P15/P17/P19; MC01–05/23/26/28–35. The bounded original
paper/source inquiry is complete. It preserves source statements, local
derivations and finite checks as separate evidence.

The inspected paper is arXiv2203.12555v3,23 May2023,15 pages. Sections2–4,
equations1–6, all18 references and the evaluation were read; this revision has
no appendix. Physical7–9 were rendered and read. Original-author repository
commit16d124f616109746b7785f03085100f1f6247575 was pinned from its page; both
downloaded source blobs match the recursive tree. The complete src/grits.py
was read. Caller reading covers only eval.py266–331 and394–485. Six successful
acquisitions and32 passage anchors are bound. Published-edition equality,
historical experiment identity and dependency/runtime correspondence remain
unverified.

The paper's equations3–6 define similarity through the joint optimum over
increasing row and column subsequences. Section3.5 then explicitly defines the
reported GriTS as the heuristic's feasible lower bound. These are related
quantities, not universally equal ones. If L is the score of the jointly
selected row/column substructure and Ur,Uc are the separate row and column
relaxations, then L<=OPT<=min(Ur,Uc). Every exact feasible alignment is allowed
by each relaxation, while the returned substructure is itself feasible. The
bound survives normalization by2/(|A|+|B|). This is the paper's argument,
expanded in execution-audit.md; the cited original complexity result was not
independently read.

The fixed one-character matrices A=[[a,b],[b,a]], B=[[b,a],[a,b]] demonstrate
the distinction. With the inspected diagonal-first tie rule, each relaxed
alignment chooses both corresponding rows or columns, scoring2. Their Cartesian
product matches no cells, so L=0. A one-row, two-column alignment matches2
cells; exhaustive enumeration confirms OPT=2. Dividing by4 gives reported
lower0 and exact/upper1/2. Neither current-wrapper shortcut fires. This rejects
universal tightness and any positive uniform multiplicative approximation
guarantee for this tie rule; it does not violate the stated bounds.

The complete finite domain of256 pairs of binary2x2 grids confirms the bounds
and both current-wrapper shortcuts against independent exhaustive alignments.
The original lower bound equals the optimum in230 pairs and is strictly below
it in26; the upper bound equals it inall256. These are exact counts for this
declared toy domain, not estimated error rates on tables. The shortcut proofs
in execution-audit.md apply to rewards in[0,1]; the finite checks do not validate
arbitrary callbacks, floating point or installed dependencies.

The original cell-text function is **wrong relative to its stated normalized
LCS target** for the inspected source expression and local standard library.
It uses SequenceMatcher and counts matching blocks, which need not maximize
subsequence length. The mathematical grid bounds still apply to that different
bounded reward, but they no longer establish bounds for the claimed LCS reward.

| Fixed input | Actual block-based reward | Normalized LCS target | Consequence |
|---|---:|---:|---|
| aaa / abaa | 4/7 | 6/7 | Unequal even with autojunk disabled |
| tide / diet | 1/4 | 1/2 | Suboptimal and argument-order dependent |
| diet / tide | 1/2 | 1/2 | Reversing arguments changes the first expression |
| x repeated200 / y followed by x repeated200 | 0 | 400/401 | Default autojunk removes the repeated anchor; disabling it gives200 matched characters |

The short-string LCS values have independent exhaustive subsequence checks.
The long pair contains a common subsequence of length200, attaining the
minimum-string-length upper bound. Python version and difflib source hash are
in witnesses.json. Only the standard library and local reconstruction ran;
the acquired modules and dependencies were never imported or executed.
The newer Kensho wrapper delegates to pylcs.lcs_sequence_length. That is a
different source path, not proof here of the dependency's correctness or of
published-score equivalence.

The geometry expressions also differ: original source uses Rect.include_rect;
the newer wrapper uses area1+area2-intersection. Exact Rect/bbox semantics remain
uninspected, so this unit records a dependency question rather than an unsupported
runtime verdict. Original HTML parse errors return None, which the selected
grits_from_html path sends to a len-dependent converter; no benchmark-wide
failure-denominator policy is established by that source path.

The selected original caller records lower and upper values per sample but its
summary lists mean acc_con/grits_top/grits_con/grits_loc, without upper bounds.
It passes the same supplied page-word tokens to true and predicted cell
construction. These are static facts about selected spans, not a complete audit
of execution or historical input quality. Paper Table2 compares checkpoints
from one20-epoch training sequence on PubTables-1M. Its rounded descriptive
gaps and44,381 no-spanning-cell corruption examples establish neither financial
transfer nor a statistically supported general ranking. Rounded means need not
subtract to the separately rounded reported difference.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
|---|---|---|---|---|---|
| Accept bounded objective/bound account | Checked technical text, local proof, independent finite oracle | Bounds hold;78 source/evidence assertions pass; six altered records rejected | General callback/dependency and floating behavior | Retain exact-versus-heuristic distinction | Universal tightness or arbitrary runtime correctness |
| Reject original source equality to LCS | Explicit fixed counterexamples | Equality claim fails | Historical Python/code/data identity | Preserve source-specific finding; inspect dependency scope | Published results disproved or current pylcs validated |
| Keep3.44 unchanged | Existing extraction/accounting distinction remains accurate | No confirmed manuscript defect | Independent/domain/human acceptance | Separate R08 supplement and four-control refresh | Readiness or any whole-row closure |

| Inference status | Finding |
|---|---|
| Hard veto screen | Exact-LCS equality and universal heuristic tightness are rejected by deterministic counterexamples; no claimed paper dataset is invalidated |
| Statistically supported ranking | None; no stochastic comparison was run |
| Descriptive-only differences | The paper's rounded checkpoint scores and metric-response plots remain attributed descriptive evidence |
| Default-readiness | No metric/runtime/default adoption follows |
| Next evidence needed | Exact historical evaluator/dependency/data and downstream accounting validation; original geometry/helper semantics can be inspected now |

The current source's cell-reward mismatch does not reject grid matching as a
research direction. It triggers a dependency/version-aware metric repair if
this source is ever selected for execution. No continuation veto fired.
3.44 remains396 pages/not_ready with53 obligations,six interactions,46 operations
and zero whole-row closures. All2338 predecessor protections plus the completed
metadata unit are preserved by this unit's2376-file protection set.

Run commands: CPU-only standard-library Python with CUDA_VISIBLE_DEVICES=-1
and -B for build_records.py, then verify.py --check, --record and no-flag replay.
Exact HTTPS commands/receipts are in source-ledger.json; lifecycle/environment,
elapsed time and output bindings are in run-manifest.json and completion.json.
Future replay is verify.py without flags; do not repeat completed one-time stages.
