# R06 — pinned calculation binding and duplicate-state source inquiry

20 October 2026, Asia/Shanghai. P15/P16/P17/P19; MC01–07,MC23–26,MC28–35.
Predecessor:r06-calc11-alignment-20261020.
Output:data/accounting-master/r06-calc11-processor-20261020/.

Question: what alignment mechanism does the already selected Arelle source
use, and is its inspected duplicate interval helper faithful to the retained
source contract under explicit constructed inputs? The comparator is the
corrected Calculations1.1 source plus the declared contextual OIM6.2 reading.
Processor source is implementation evidence, never an authoritative erratum.

Reuse ValidateXbrlCalcs.py and ModelInstanceObject.py at commit
01f6a4656c2c6551d2f05f31c9d74366d133ee7e. Acquire only their missing
arelle/utils/Contexts.py and arelle/utils/Units.py helpers from the same commit;
up to2MiB/45seconds each, with one trusted retry for sandbox/network failure.
Retain exact commands, headers, bytes, hashes and failures. Inspect the complete
short helpers and relevant binding/canonicalization/equality/interval branches.
Do not import, evaluate or execute acquired/upstream code.

Evidence contract: trace context and unit canonicalization into binding tuples,
set intersections and per-concept fact lookup; distinguish hash prefilter and
equality checks, collisions, validity assumptions and runtime identity. Inspect
the complete consistentFactValueInterval state transitions, rangeValue helper
and the caller. Compare independent exact authored transition witnesses with
the already checked mathematical interval/pairwise contract. Test differing
same-precision values, duplicate/excess precedence, open endpoint propagation,
nil sets and mixed nil. Preserve helper inputs and every transition.

Primary criterion: exact source anchors plus AST shape and hand-auditable
transition witnesses; conclusions state the input preconditions and whether
the computed branch differs from the declared target. A source mismatch or
uninspected dependency vetoes its dependent claim. Missing helper sources
leave that edge unresolved, not falsely closed. Protection failure or upstream
execution is a continuation veto. Explanatory counts do not certify runtime.

Skeptical audit: prior artifacts addressed separate duplicate APIs, not this
calculation helper's final overwrite. The assignment to _inConsistent after
the loop appears to discard same-precision inequality; an explicit two-fact
witness is required before classifying it. Binding uses exact keys rather than
subset search, but context hashes and canonicalization prevent claiming generic
OIM equality. No unqualified report arithmetic may follow from this code alone.
The narrower source inquiry passes after these boundaries are explicit.

| Choice | Provenance / reason | Failure / early check | Status |
| --- | --- | --- | --- |
| Existing exact commit | Prior source identity | Latest code mistaken for historical pin; verify manifests | Baseline |
| Static AST and authored traces | Upstream execution held | Trace omits a branch; bind complete helper and caller | Bounded diagnostic |
| Contextual OIM6.2 consistency | Prior explicit source ambiguity | Treat interpretation as correction; preserve source caveat | Conditional comparator |
| Equal keys as implementation fact | Inspected binding expression | Hash collision or prefilter ignored; trace helpers | Source claim only |
| Both interval modes | Separate report-wide alternatives | Silent rounding default; explicit mode inputs | Unselected alternatives |

Premortem: a real code divergence could be hidden by earlier validation or an
unreachable caller. Inspect calling modes and prerequisites; classify source
branch behavior separately from actual filing/runtime impact. Do not alter
frozen evidence or upstream code. Record source failures and continue ready
internal work. No superiority, production, accounting or full-conformance claim.

CPU-only standard library using CUDA_VISIBLE_DEVICES=-1 and
/home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B. One-time prepare, build,
check and record, then read-only replay. Preserve3.44/396/not_ready,53/6/46,
HEAD/index,empty staging,36 dirty paths. Four live controls/additiveR08 only.
No installations, empirical runs, commits, outreach, publication or fees.
