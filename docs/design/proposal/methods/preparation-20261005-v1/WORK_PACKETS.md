# Independent proposal preparation

These tasks can prepare P17 inputs before P16 is accepted. Their answers concern
source facts, accounting methods or evaluation design; final product interfaces
and initial-profile selection remain with P16. No product implementation,
professional engagement, new large corpus or external publication is included.

## 1. Lease and tax dossiers — recommended first

Requirements: MC16, MC17, MC20, MC23, MC29, MC35; G4/G7.
Produce one dossier per method, using the repaired AccountingMethodSpec format:
exact standard/version and target-period applicability, instrument/entity facts,
recognition and measurement, complete dated journals and balance roll-forward,
exceptions and competing treatment, and remaining questions with proposed answers.
Start with a fixed-payment lessee example and a simple temporary-difference tax
example; cover a negative/failure case and identify what each simplification omits.
Keep lease modifications and tax-rate changes as explicit subsequent cases.
Use primary retained or legitimately retrieved sources; inspect provisions before
asserting eligibility. Keep sources local. Independently check journal conservation
and closing balances. Passing arithmetic does not establish general compliance.
Deliver: lease-dossier.md, tax-dossier.md, versioned source register, exact fixtures
and one bounded arithmetic report. Final interface encoding remains provisional.

## 2. IFRS / US GAAP / ASBE authority matrix

Requirements: MC20, MC29, MC30, MC35; G7/G8.
Compare recognition, measurement and applicability for the same stated facts,
starting with an operation needed by dossier 1. Inspect the existing P08 authority
registers before reacquisition. Record exact paragraphs, effective periods,
amendments, elections and access limitations. A secondary reproduction cannot
establish official-current ASBE authority; missing ASC access is not a zero gap.
Deliver: dated authority matrix, retained texts and claim-specific open issues.
Do not choose the product accounting framework or infer equivalence from labels.

## 3. Filing adapters and evaluation design

Requirements: MC01–MC07, MC25, MC27, MC31, MC33; G5/G9/G11–G13.
Inspect pinned official Arelle/Docling interfaces and licenses against the repaired
extraction contract. Specify what source/context/location/rounding/time information
each preserves or loses. Compare credible alternatives on matching tasks. Draft
an evaluation protocol with separate transcription, context, table, mapping,
source-support and unresolved-content measures. No unmeasured model, confidence
threshold or accuracy target becomes a default. No package installation or model
training is necessary for the first source/interface audit.
Deliver: adapter capability/limit matrix, exact upstream anchors, proposed adapter
input/output cases and evaluation protocol. Final APIs wait for P16 integration.

## 4. Corpus annotation pilot design

Requirements: MC01–MC07, MC32, MC33; G5/G10/G11.
Select explicitly identified representative units from the existing 192-report
panel, with format/language/sector/basis strata. Define annotation units,
instructions, adjudication, public-time evidence, unresolved notes and referenced
material. Separate retained occurrences from assertion identity. Record selection
and contamination/exposure; keep related issuer histories in compatible partitions.
A small pilot is development evidence, not whole-corpus or population accuracy.
Deliver: selected IDs, annotation handbook, located pilot labels and ambiguity log.
Coordinate field definitions with task 3; real annotation can begin after a small
schema agreement without waiting for complete product architecture.

## Work isolation and import

Use separate task directories below this /tmp workspace or independent checkouts.
The reference-snapshot holds immutable copies of the initial seven documents,
with original path/hash mappings in manifest.json. Read additional retained
sources from the main worktree if needed, then copy and pin them before analysis.
Keep generated files outside /home/chakwong/python/AccDSL while the master runs.
A subdirectory inside that worktree is not concurrent-write isolation.

Before any substantive task, record its exact source baseline, assumptions,
pass/fail evidence and stop condition. The task passes when its proposed answer
and supporting calculation/source record can be reconstructed; source gaps block
the affected claim rather than all useful preparation. No staffing, page-count
or runtime estimate is an acceptance criterion.

After a task finishes, import under the master locks at a stopped boundary.
Preserve original bytes, review the actual files, record source and semantic
limits, and register them as candidate P17 inputs. Do not mark P17 accepted or
rewrite controller state from a side task. Independent sources may be researched
in parallel; the integrated manuscript and final profile wait for P16/P17 decisions.

Skeptical audit: all four tasks use the current mission and existing corpus as
baseline; no prototype, test count or source count is promoted to product
acceptance. Each has a concrete independently useful output and controlled
integration boundary. The master is currently stopped on controller findings;
there is no live computation to wait for until those findings are resolved.
