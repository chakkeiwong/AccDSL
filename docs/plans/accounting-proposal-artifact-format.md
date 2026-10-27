# Proposal evidence format

This is an authoring reference for P15–P19. The governing requirement is the
phase objective and MC01–MC35, not the length of this checklist. The registered
checker checks structure and retained evidence; independent review assesses
whether the analysis answers the design questions. A populated record does not
establish accounting validity or a complete proposal.

Write the phase's JSON and `result.md` in its declared deliverable directory.
Use its permitted document directory for substantive analysis and source
copies. Preserve useful earlier work and cite exact support. Use existing
immutable inputs or local snapshots of changing supervisor records; citing
live `state.json`, `next-plan.json` or a live checkpoint creates stale evidence
as soon as the supervisor advances. Do not capture a checker by redirecting
over an existing file. A disposable check can write to `/tmp`.

Every stage has `schema_version: accdsl.proposal.pXX.v1` (lowercase `p`),
`product_implemented: false`, `human_acceptance: pending`, a substantive
`limitations` string, and a nonempty `source_evidence` array. A reference is an
object with repository-relative `path`, current `sha256`, and, where helpful,
`locator` or an exact `quote`. All referenced files must exist and be nonempty.
Use locators for PDFs; quotes are checked against UTF-8 text. Record sources
actually inspected and distinguish their authority and limitations in prose.

P15's `coverage.json` contains:

- `requirements`: one row for each MC01–MC35; `gaps`: one row for each G1–G18.
  Each row has `id`, `status` (`open`, `partial`, `specified`, `checked_design`),
  `assessment`, `remaining_work`, `design_consequence`, and nonempty `evidence`
  references with at least one locator or quote. Assess design evidence, not
  product completion; do not change the required evidence to match prototypes.
- `open_decisions`: objects with `id`, `question`, `proposed_answer`,
  `alternative`, `consequence`, `next_step`, and boolean `blocks_proposal`.
  An empty list needs justification in the analysis when major choices remain.
- `candidate_initial_profile`, `profile_alternative`, `selection_question`:
  substantive strings. The first implementation scope is still proposed.
- `prior_work`: one row for each P00–P14 with `phase`, `role`
  (`source_evidence`, `exploratory_probe`, `unexecuted`), `scope`, `limitations`,
  `design_consequence`, and evidence references. Preserve partial P08 findings.
- `audit_note`: references to the actual requirements and prior-work analysis.

P16's `architecture.json` references P15's exact `coverage.json` as `coverage`.
Its `contracts` cover `evidence`, `history_families`, `uncertainty`, `accounting`,
`time`, `language_ir`, `persistence`, `interfaces`, `failure_semantics`. Each has
`id`, `inputs`, `outputs`, `invariants`, `failure_behavior`, `alternatives`,
`chosen_reason`, and reference arrays `specification` and `fixtures`. The
`initial_profile` object has `status: proposed`, `name`, `rationale`, `included`,
`excluded`, `acceptance_criteria`, `dependency_order`. Include `open_decisions`.

P17's `methods.json` references P16 as `architecture`. Its `domains` cover
`corporate`, `bonds_equity`, `groups_fx`, `banks`, `insurance`, `ifrs`, `us_gaap`,
`asbe`, `forecasting`, `literature`, `software_reuse`. Each has `id`, `scope`,
`method`, `assumptions`, `authority_limits`, `case`, `unresolved`, `interface`,
`source_status` (`inspected`, `partial`, `blocked`), and `evidence` and
`specification` reference arrays. Include `open_decisions`; source-access gaps
limit supported claims while independent feasible work continues.

P18's `manuscript.json` references P16/P17 as `architecture`/`methods`. Save the
integrated candidate under `docs/design/proposal/manuscript/`. Include `main_tex`
and `pdf` references; `source_files` references pin all candidate `.tex`, `.bib`,
`.sty` and `.cls` files and include `main_tex`. The `build` object records the
actual command, exit code, environment and log reference. Build with TeX's
`-recorder` option and include the `.fls` reference as `build.recorder`, the
repository-relative `build.working_directory`, and `build.environment_inputs`
listing the absolute nonproject INPUT paths from that recorder. Pin every
project INPUT file in `source_files`, including figures, tables and files
outside the manuscript directory. Environment-managed TeX inputs are identified
separately from project source evidence. `rendered_pages`,
`render_review`, `baseline_preservation_review` are reference arrays;
`rendered_pdf_sha256` identifies the inspected PDF. Build success cannot stand
in for actually reading the rendered pages or checking retained substance.
Also preserve `build.record`, a reference to the actual build-time JSON record
with `inputs_before` and `inputs_after` maps (the paths and SHA-256 of all
`source_files`), `exit_code`, and the resulting `pdf_sha256`. First discover
dependencies with the recorder, then capture hashes around a successful final
build. If inputs change, rebuild until stable and retain the actual record.
Editing sources and merely updating their manifest hashes cannot reuse an
earlier PDF or render review.

P19's `readiness.json` has `stage_evidence` mapping P15–P18 to their exact JSON
references, final `requirements` and `gaps`, and `open_decisions`. Coverage uses
`specified` or `checked_design` and adds a substantive `contract` locator and
`scope` (`initial_profile`, `later_profile`, `whole_product`). No proposal-blocking
decision can remain unresolved. References `initial_profile`,
`implementation_sequence`, `acceptance_fixtures`, `residual_work` preserve the
reviewable design. Set `status: candidate_for_independent_review`. This stage
does not write the supervisor's readiness record or enable product work.
