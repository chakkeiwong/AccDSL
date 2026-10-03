# Results: internal preparation before professional review

Date: 2 October 2026. Authority: the user's direction to minimise expensive
human-review time. The [plan](../../plans/accounting-before-paid-review.md)
records the pre-execution skeptical audit and subsequent source findings.
Baseline: protected Version 1.1, SHA-256
`ec4edabbb0d1e9e0a41415a1c95d4fc4b38942d7a1c5a8a69c2ba5a8ae6a3382`.

## Result and decision

MC35 now makes internal preparation a standing requirement. All G1–G18 have
an internal next deliverable and a separately identified possible professional
judgment in the [work allocation](internal-before-expert.md). Missing human
feedback retains its acceptance meaning without halting authorised internal
work. The original 34 technical requirement/acceptance pairs are preserved.

Version 1.2 corrects the inventory note citation and makes the reinsurance
example's separate eligibility, recognition and recovery timing explicit.
The Core 0 supplements now include a frozen registry and a tested static
validator for the authored debt profile. Three accounting dossiers supply
proposed answers, source paragraphs, calculations and counterarguments.
The [future review brief](future-professional-review-brief.md) is unsent.
No professional has been contacted, no fee incurred or authorised, and no
packet is declared ready for paid review of an actual company.

## Defects resolved internally

| Finding | Correction | Evidence |
| --- | --- | --- |
| The IR used a Real `one` as an integer slot count despite forbidding an implicit cast | Added a separate `Int` literal and retained the Real fraction-comparison value | Initial validator returned `SlotLimitType`; the corrected fixture passes and the original misuse is retained as a negative case |
| The example's stress driver and assumed initial component rates lacked Assumption records | Added scoped reasons, origin, validity, cutoff and hypothesis status in the generator | Removing either record now yields `MissingAssumption`; whole-program compilation is still absent |
| JSON Schema alone accepts contradictory financial/context/source/time records | Added a bounded validator and frozen 17-export registry | 78 checks: 5 valid variants, 71 schema-valid semantic corruptions and 2 JSON-boundary rejections |
| A balanced opening, selected view or report binding could still describe the wrong example | Link the frozen opening, source reading, admitted facts, model/family declarations and report operations | Balanced-but-wrong opening, omitted admitted observation, wrong entity, wrong account role and wrong closing policy are rejected |
| Caterpillar inventory table cited as Note 7 | Corrected bibliography source, generated bibliography and standards ledger to Note 8 | Retained report's Note 1.C and Note 8, table on PDF p. 78 |
| Issued-contract PAA eligibility did not explicitly establish eligibility and recognition for the held treaty | State the treaty's one-year coverage, coincident recognition, uniform service and short recovery timing | Reinspection of AASB 17 paragraphs 53(b), 62–62A, 69(b), 59(b), B126–B127; revised manuscript and dossier |
| Source age could be mistaken for applicability, and the recovered summary misstated one cutoff | Record actual annual-period-start conditions from AASB 132/17 PDFs | Both compilations cover starts on/after 1 January 2023 and before 1 July 2026; this includes a calendar-2026 annual period |

The [semantic report](semantic-preparation-checks.json) records each mutation's
expected and observed error. Every semantic negative is first required to pass
the structural schema. Positive cases include record/export reordering,
equivalent timestamp offsets, the exact system-cutoff boundary and a different
documented nonnegative stress. A test initially expected a general type error
for a money-valued rate; the checker correctly rejected it at the contract-field
boundary, and the expectation was corrected to `ContractType`.

The [accounting report](accounting-dossier-checks.json) supplies 17 exact checks
and balanced journal sequences: inventory costing and reversal caps, bond
issue/accretion/redemption/conversion, and insurance with separately varied
transferred risk and non-performance. These calculations are conditional on
the dossier assumptions. Existing suites also pass: 12 original illustrations,
49 repair cases and 31 Core 0 reference checks. These counts are inventories;
overlapping arithmetic is not independent accounting evidence.

## Source and interpretation record

The [inventory](accounting-dossiers/inventory.md),
[compound-bond](accounting-dossiers/compound-bond.md) and
[insurance](accounting-dossiers/insurance.md) dossiers distinguish the source's
statement, the local deduction and the actual-fact judgment still needed.
The inspected official AASB texts have explicit edition and jurisdiction limits.
Caterpillar supplies company-policy evidence. The ASBE reproduction remains
unofficial; full primary ASC authority remains unavailable locally. Previously
blocked downloads were not repeated without a distinct lead.

The calculation targeted and computed are equal under the explicit synthetic
assumptions, as shown by exact rational values and journals. That is an
engineering/mathematical result. Equality to an actual issuer's applicable
accounting treatment, actuarial estimates or complete historical state is not
established. No stochastic comparison, forecast ranking or savings estimate
was made.

## Decision table and skeptical result review

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain the bounded checker and corrected example | Positive variants and semantically invalid inputs behave as specified | Discovered fixture inconsistencies repaired; unsupported sections/operations explicitly rejected | Other Core 0 semantics, runtime behaviour and coverage proofs remain outside this checker | Extend supported compilation/semantics using new counterexamples | Full language, historical reconstruction or accounting conformance |
| Retain conditional accounting examples and source dossiers | Exact journals/calculations reconcile and cited paragraphs were inspected | Note error and missing treaty assumptions repaired | Actual terms, dated jurisdiction authority and estimated risk inputs | Finish relevant facts/source/method work internally | Applicability to a real company or professional assurance |
| Continue internal work before commissioning review | Every G category has an internal task and conditional residual question | No question has complete actual-company preparation warranting paid referral | Which residual judgments will survive that preparation | Follow MC35 and the internal queue; commission only if later instructed | Mission completion, quantified savings or a firm engagement |

Strongest alternative explanation: author-written specifications, examples and
checks can share an error. The adversarial cases make some such errors visible
but do not remove that risk. A source paragraph contradicting the treatment,
a valid rejected program or an invalid accepted supported case reopens the
corresponding finding. The weakest evidence remains real-world applicability
and full-language execution, not the exact arithmetic. The observed failures
invalidated particular fixture choices and missing checks; they did not
invalidate the wider reconstruction project or justify stopping internal work.

## Reproduction and retained evidence

From the repository root:

```bash
python3 scripts/build_core_contract.py
python3 scripts/build_demo_registry.py
python3 scripts/check_semantic_preparation.py
python3 scripts/check_accounting_dossiers.py
python3 scripts/check_core_contract.py
python3 scripts/check_repair_conformance.py
python3 scripts/check_design_examples.py
python3 scripts/verify_design_document.py
```

The manuscript was rebuilt with XeLaTeX through latexmk, including a final
forced `latexmk -g -xelatex -interaction=nonstopmode -halt-on-error` rebuild.
The first final verifier detected a source mtime 0.886 seconds newer than the
PDF despite the corrected text being present; the forced rebuild resolves that
freshness veto. Current rendered
inspection is recorded in [author review](author-review.md) and the
[render manifest](repair-render/final/manifest.json). The
[preparation manifest](internal-preparation-manifest.json) binds current files,
environment and checks. [The protected baseline](pre-expert-preparation-2026-10-02/manifest.json)
retains its original 44 files; Version 1.1's render evidence is separately kept
under `repair-render/version-1.1/`. The older repair report/manifest describe
their historical Version 1.1 bytes, not this amended candidate.

All commands used the existing Python/document environment and ordinary CPU
utilities; no ML/GPU framework, new dependency, paid service or model worker was
used. Git revision is unavailable because the workspace marker is unusable;
content hashes preserve provenance. Random seeds are not applicable to these
deterministic checks. Test wall times and commands are recorded in their reports;
session chronology is not a measurement of professional time saved.
