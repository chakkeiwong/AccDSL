# P16 bounded representation comparison

Definitions and the paired MA02a attachment example are saved. Both the
family-linked and self-contained encodings preserve the three semantic outcomes,
their assignments and masses 1/2, 1/3 and 1/6, the exact family/view versions,
and the same synthetic admission. Neither representation is selected. This
completes only the reviewed bounded task, not P16 or the uncertainty contract.

The comparison document defines ownership, dependency closure, immutable
mapping, field correspondence, failure obligations and interactions with
histories, time, language/IR, persistence and interfaces. The owned model has
its own complete numerical definitions; evidence, admission and family binding
remain explicit external dependencies. The fixtures contain different concrete
requests and receipts, not two links to the same request.

Author verification ran:
`PYTHONDONTWRITEBYTECODE=1 python3 docs/design/proposal/architecture/uncertainty-representation-diagnostic-v1.py docs/design/proposal/architecture/uncertainty-representation-verification-v1.json`.
It passed 205 checks: pinned source hashes and available dependencies, complete
coordinate/assignment correspondence, bijective identity mappings, nonnegative
masses with complete coverage and total exactly one, and separately checked
receipt dimensions. Both expected receipts retain ATTACHED_ASSUMPTION,
empirical_justification=not_established and specified_only_no_runtime.
The prerequisite supplement's five input hashes still match; its 266 saved
checks were inspected, not rerun. No runtime attachment was executed.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain both candidates | Definitions and one complete mapped pair saved; author checks pass | No inconsistency detected in this pair | Overlap, projection, rejection behavior and full contracts remain incomplete | Add MA03a and MA04b comparisons | Architecture selection, general equivalence, product correctness or readiness |

The exact command, input hashes, observations, failures and environment are in
uncertainty-representation-verification-v1.json. Its scope is document
consistency. The full-phase checker ran with
`PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_accounting_proposal.py --phase P16 --check`
and returned exit 1: 133/134 checks passed, with only whole architecture
contracts failing. The checker stops before individual-contract and
initial-profile assessment. Its nonempty JSON and exit status are preserved
in uncertainty-representation-structural-v1.json and structural-execution-v1.json.
The exact precheck result is preserved separately; a fresh v2 structural report
binds this final result note. These are structural checks, not acceptance.

All prior architecture references, three contract rows, six unfinished
contracts and fourteen decisions are preserved. The initial profile remains
unresolved. Product implementation is false and human acceptance is pending.
The strongest alternative explanation is that the inherited attachment
specification itself omits an important behavior: exact agreement on one
synthetic example cannot expose that. A non-bijective projection or a stale
admission mapping could invalidate a broader equivalence claim. Those cases
must be specified and independently reviewed; no broad claim is made here.

Changed files: architecture.json, result.md and progress.md in the P16 output;
under docs/design/proposal/architecture, uncertainty-representation-comparison-v1.md,
fixtures-v1.json, diagnostic-v1.py, verification-v1.json and prior-result-v1.md
(all with the uncertainty-representation- prefix). The previous result note is
preserved in that last file. No production modules, controller files or test
suite were changed. Additional saved files there are uncertainty-representation-precheck-result-v1.md,
uncertainty-representation-structural-v1.json and -v2.json, and
uncertainty-representation-structural-execution-v1.json and -v2.json. The v2
report repeats only the bounded structural check after the result-note update.

Next bounded task: extend this saved comparison with MA03a overlap, preserving
5/6 and 1/2, intersection 1/3 and union 1, and MA04b projection, retaining two
distinct elementary outcomes beneath rate=1. Then address stale available
dependencies, malformed input and partition/projection rejection receipts;
conditioning, duplicate-evidence protection, likelihood updates and conditional
outcomes remain later work. E05 source limits, wider MC01–MC35/G1–G18 obligations,
source and accounting authority, empirical validity, full independent P16 review
and human acceptance remain open. Optional partial review is not a prerequisite
to the next reviewed drafting task.
