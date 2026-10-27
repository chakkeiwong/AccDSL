# P16 bounded result: overlapping events and projection

Completed the reviewed MA03a/MA04b supplement under approved plan
b635f1c0b530d60ff391254b7bfa4f722580ccd597546b22c5f8d2a02b23158c.
P16 remains partial. Product implementation is disabled; human acceptance is
pending. Scope is MC12/G15 with MC08, MC10, MC14, MC18 and MC25 interactions.
All original P16 criteria and MC01–MC35/G1–G18 remain active.

The supplement defines concrete family-linked and self-contained requests,
owned/external event definitions, exact dependencies, identity translations and
expected receipts. MA03a preserves overlapping events A={a,b}, B={b,c}; their
probabilities are 5/6 and 1/2, intersection 1/3 and union 1. Summing the first
two probabilities yields 4/3 by double-counting b. MA04b uses a separate model:
(region A, rate 1) and (region B, rate 1), each mass 1/2. Projection has mass
one at rate=1 and retains both elementary identities and the lost region
coordinate. Its many-to-one display map is distinct from the bijective binding.

Both receipts are specified EVALUATED, attached_assumption,
empirical_justification=not_established, capability_status=specified_only_no_runtime.
Family/view remain unchanged; MA04b retains PROJECTION_COLLISION_RETAINED.
Scalar probability stays null for the structured observations. Full field
correspondence, support ownership and synchronization duties appear in
`docs/design/proposal/architecture/uncertainty-event-comparison-v1.md`.

The claimed target and computed quantity agree for these authored finite
examples: the diagnostic derives each arm's event probabilities independently
using Fraction and then checks their receipt observations. All 277 checks pass,
covering pins, dependency availability, coordinate/assignment correspondence,
bijective maps, selectors, nonnegative unit masses, projection preimages and
separate receipt fields. Previous MA02a and prerequisite input hashes match;
those earlier diagnostics were not rerun. The report preserves the actual
command, input hashes, observations, failures and limits:
`docs/design/proposal/architecture/uncertainty-event-verification-v1.json`.

| Decision | Primary criterion | Veto diagnostics | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain both finite representations | Exact correspondence passes for MA03a/MA04b | No authored-fixture mismatch found | Broader rejection/operation behavior untested | Write the rejection comparison | Architecture preference or general equivalence |
| Keep P16 partial | Whole-product contract inventory incomplete | Six required contracts absent | Profile, integrated acceptance and dependency order unresolved | Continue bounded specification work | Product or phase readiness |

The registered structural command is
`PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_accounting_proposal.py --phase P16 --check`.
Fresh stdout and exit status are preserved separately in
`docs/design/proposal/architecture/uncertainty-event-structural-v1.json` and
`docs/design/proposal/architecture/uncertainty-event-structural-execution-v1.json`.
The whole-contract inventory remains incomplete; individual contract/profile
assessment cannot be inferred from this check. Structural evidence is not
substantive acceptance.

Changed deliverables are architecture.json, result.md and progress.md. New
architecture-directory files share the uncertainty-event prefix: comparison-v1.md,
fixtures-v1.json, diagnostic-v1.py, verification-v1.json, prior-result-v1.md,
structural-v1.json and structural-execution-v1.json. The preceding result note
was copied exactly before replacement. The saved MA02a and all earlier evidence
remain unchanged. No product module, controller or test suite changed.

Post-run red-team assessment: author-selected finite examples and common source
inputs can agree while both inherit a broader design error. Independent sums
and explicit field/identity checks reduce local transcription risk, but do not
resolve malformed inputs, stale dependencies or other probability spaces. A
counterexample to the binding or incomplete projection preimage would overturn
this bounded correspondence finding. No empirical, accounting, performance,
persistence/recovery or human validity was established.

Next: stale available dependencies, malformed inputs and partition/projection
rejection receipts. Then conditioning, duplicate-evidence protection, likelihood
updates and conditional outcomes. Six contracts, initial-profile selection,
integrated acceptance/dependency order and fourteen decisions remain unresolved.
E05 source limitations and P17 authority/research/real-company obligations remain;
full independent P16 review and human acceptance are pending. This work supplies
examples for the governing proposal; it does not approve architecture or close
the wider mission.
