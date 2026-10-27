# Historical corpus and initial-design checkpoint

Current continuation: Version 3.53, 413 pages, not_ready. See the master checkpoint
and data/accounting-master/company-authoring-integration-20261023/result.md.
The 2 October corpus/design records below remain historical.

Current proposal execution is recorded in
[the master checkpoint](accounting-master-checkpoint.md) and
[current master program](accounting-master-current.md).
The dated actions below preserve the 2 October state; they do not supersede
the current proposal-only work or the usable Git repository.

Updated: 2 October 2026 (Asia/Hong_Kong), after multi-year source-corpus
acceptance following the expanded-audit repair. The user directed us to do all
feasible internal work before costly professional review. MC35 preserves that work order.
The wider mission remains active; human review is not the next automatic step.

## Accepted source corpus and next execution

The user's corpus-first work unit is complete at the source-acquisition layer:
**192 of 192 target reports, 2018–2025, across nine issuers and three evidenced
accounting families. All nine have eight consecutive complete years.**
`target-panel-v2.json` is active and is now the collector's explicit default.
Henkel replaces Unilever and Munich Re replaces Allianz under the reviewed
source-access repair; frozen v1 coverage and all original files remain under
`data/financial-report-benchmark/snapshots/`.

Resume from the [corpus result](accounting-benchmark-corpus-results.md),
`data/financial-report-benchmark/index.html`, `coverage.json` and
`integrity-manifest.json`. QA 6 revalidated all 244 retained original versions;
the independent hash/provenance/grid/PDF checks pass, and 20 regression tests
pass. The old 12-, 157- and 159-report counts are historical. There are 738
attempt/revalidation records, not 738 benchmark observations.

The collector checkpoints each attempt and supports `--revalidate-retained`,
`--resolved-only`, sequential `--index-plan` capture and bounded host failures.
Official HSBC and Midea archives, SAIC year pages, Ping An's published report
feed, SEC submissions and issuer-hosted US filing feeds have been resolved.
Direct SEC archive downloads returned 403; issuer-hosted copies are used with
the regulator identity and filing dates retained. Run one acquisition writer
at a time. The optional `--http-client curl` bounds total request time;
`--source-host` can select a resolved alternate without retrying known failures.
Ping An's last ASBE slot was filled by an A-share report attachment on a public
mirror; the distinct IFRS copy remains excluded from that slot. Do not reset
the ledger, initialise Git or promote source checks into accounting evidence.

The next internal work is task-specific literal/context/span annotation and
Core 0 semantic/compiler implementation using the preserved source set and
existing fixtures. `benchmark-protocol-v1.json` and
`annotation-record.schema.json` define the proposed tasks and exchange format;
issuer-family roles are provisional, with no model score or gold labels.
Resolve incorporated documents, revisions and publication timing before
historical forecasting. Publication dates are unverified for 136 of 192
accepted reports; 56 have filing-date metadata. No paid review is triggered.

## Current deliverable

`docs/design/accounting-product-design.pdf` and its LaTeX sources are Version
1.2, a 79-page design candidate with 11 chapters and two appendices. It contains
complete Northstar annual/interim/revision/forecast cases, an Apple filing
inventory and conditional financing stress, historical construction and solver
limits, corporate operations, sector examples, Core 0 contracts,
review/replay/adapter definitions and corpus/release protocols.

The 8 mission goals and MC01–MC34 retain their requirement and acceptance
wording. MC35 adds the new cost/preparation requirement. Assessments identify
evidence and residual obligations. A bounded debt semantic validator, frozen
registry and three accounting source dossiers supplement the design. Version
1.2 corrects the Caterpillar note anchor and states separate reinsurance PAA
eligibility/recognition/timing; it preserves the prior calculations.
Control files:

- `MISSION_CONTROL.md`
- `docs/plans/accounting-mission-requirements.md`
- `docs/plans/accounting-before-paid-review.md`
- `docs/design/review/internal-before-expert.md`
- `docs/design/review/internal-preparation-results.md`
- `docs/design/review/internal-preparation-manifest.json`
- `docs/plans/accounting-gap-repair-2026-10-02.md`
- `docs/design/review/repair-plan-review-2026-10-02.md`
- `docs/design/review/gap-repair-results-2026-10-02.md`
- `docs/design/review/author-review.md`
- `docs/design/review/repair-verification.json`
- `docs/design/review/repair-execution-note.md`

The preparation manifest records the earlier Version 1.2 preparation state.
Corpus-era controls and `fixtures/corpus-protocol.json` have since been updated;
their current hashes are in `data/financial-report-benchmark/release-manifest.json`.
The older repair manifest identifies historical Version 1.1; neither historical
manifest should be treated as a current hash set for changed control files.
`docs/design/README.md` gives reading routes and commands.

## Evidence preserved

The protected original 60-page draft, controls and affected scripts are under
`docs/design/review/pre-repair-2026-10-02/`, with 45 file hashes. Its PDF hash is
`0b83e17e8f7906c8ea341cb6c1ef2b3082069ca59577eb0ae7d22b50c54163f0`.
Version 1.1 also remains protected in `pre-expert-preparation-2026-10-02/`
(44 files), with its rendered evidence in `repair-render/version-1.1/`.
No old display equations or citation keys were removed; grammar/record changes
and preserved qualifications have an author disposition.

Checks: 12 original illustrations, 49 repair/reference checks and 31
core-contract/reference checks pass. The new semantic suite passes 78 checks
(5 positive, 71 schema-valid negative, 2 JSON-boundary); the new accounting
dossiers pass 17 exact/journal checks. These are bounded author evidence. The revised PDF has no serious TeX
warnings and received contact-sheet plus selected full-page inspection.
The verifier requires an author-review file and matching current-PDF render
manifest and tracks the external grammar input. The library contains 32
verified paper PDFs. There are 179 individual title/metadata decisions across
194 occurrences and 72 forward queries; missing decisions stop generation.

Fixtures, grammar, schema and contracts are in `docs/design/fixtures` and
`docs/design/spec`. The complete demo IR is author-entered, not generated by a
compiler. The new `core_semantics.py` validates the authored monetary debt
profile and its 17 frozen exports; unsupported sections/operations are rejected.
It does not prove family coverage or execute a general model. Checks evaluate
selected IR expressions and reference financial operations; they do not certify
a production engine.

Selected rule support comes from official AASB texts incorporating IAS 2,
IAS 32 and IFRS 17. Mack's chain-ladder technical method, proofs and aggregate
error discussion were inspected. Sources and limits are recorded in
`docs/design/research/standards-support.json` and
`docs/design/cases/apple/manifest.json`.

## Remaining work and next justified steps

1. Extend the checked debt-profile registry/reference/type validation and implement source-to-IR lowering
   against the positive/negative cases. Schema parsing is not complete compiler
   conformance. Preserve assumptions, context, joint symbols and branch failures.
2. Build the bounded Northstar path and transactional replay; execute small
   version-pinned Arelle/ACTUS/QuantLib/Docling/ledger exchanges as selected.
   Only Z3 has been exercised in this repair.
3. Expand and independently annotate the real corpus. Apple's 121 annual pages
   and 23 total notes are inventoried, but full semantics and incorporated
   external documents are incomplete.
4. Obtain full ASC authority and official/current ASBE verification. Extend
   bank credit/prudential, insurance measurement/transition and richer hybrids
   with primary support and complete actual fact patterns. Existing bank capital
   assumptions are illustrative, not Basel rules. Dossiers retain source-version
   limits and calculations; source acquisition remains internal work.
5. After relevant internal tasks are complete, identify any consequential
   residual questions for independent implementability/accounting review. Use
   the unsent brief with narrow questions and a user-approved scope/cost only
   if later commissioned. Ordinary comprehension feedback is separate and need
   not come from a professional firm. Acceptance stays provisional while
   internal work continues. Forecast calibration, stochastic inference and
   performance comparisons need separate evidence plans; none was run here.

G1–G18 are mapped in the result note; the wider audit is not fully closed.
A bounded complete synthetic case must not narrow the mission. No deployment,
external messaging, Git initialization or production claims were part of this
work. No subagents were used.

## Recovery history

Original saved session: `01a0f8e0-0c0b-7332-8f7e-d6b93ce32761`. It failed at
06:13:01 after repeated HTTP 502 responses from its model-provider gateway;
logged context-limit flags were false. Last saved prior work was rendered
contact-sheet inspection; its final author-review record was absent. This
campaign supplies a new author review rather than attributing one to that
interrupted session. The upstream gateway cause remains unknown.

Original evidence remains in
`docs/plans/accounting-product-design-session-recovery.md` and
`docs/design/review/session-recovery-2026-10-02/`. Do not restart the literature
collection, initial draft or investigation from scratch. Existing `.git` is not
a usable repository; do not initialise it or invent a commit.
