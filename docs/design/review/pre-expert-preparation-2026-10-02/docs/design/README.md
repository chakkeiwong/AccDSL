# AccDSL product and implementation design

Read the [compiled design](accounting-product-design.pdf): Version 1.1,
2 October 2026, 79 pages, 11 chapters and two appendices. The
[LaTeX root](accounting-product-design.tex) and [chapter sources](chapters/)
are accompanied by normative [Core 0 contracts](spec/core-contract.md),
[grammar](spec/core-0.lark), [IR schema](spec/core-ir.schema.json) and
[reference fixtures](fixtures/).

This is a repaired design candidate. It explains how disclosures constrain
jointly compatible histories and how explicit scenarios produce coherent
future journals/statements. A complete synthetic company and a named Apple
annual/interim disclosure case connect the methods to data and exact results.
Optional probabilities require a declared joint measure; unknown weights and
unresolved branches remain visible.

[Mission control](../../MISSION_CONTROL.md) and the
[34 requirements](../plans/accounting-mission-requirements.md) retain the full
scope. The [repair plan](../plans/accounting-gap-repair-2026-10-02.md),
[plan audit](review/repair-plan-review-2026-10-02.md) and
[G1–G18 results](review/gap-repair-results-2026-10-02.md) distinguish repairs
from residual work. The original gap audits are historical baselines.

## Reading routes

| Purpose | Revised PDF chapters |
| --- | --- |
| Product scope | 1 |
| Northstar history, correction, forecast and bounded Apple case | 2 |
| Evidence, notes, contexts, mappings and time | 3 |
| Literature, alternatives and reusable software | 4–5 |
| Reconstruction, solver bounds, resolution and probability | 6 |
| Language, corporate operations, scenarios and journals | 7–8 |
| Standards, inventory, bonds, consolidation, banks and insurance | 9 |
| Review, APIs, identity, storage, adapters and acceptance | 10–11 |
| Grammar/records and source-review qualifications | Appendices A–B |

The [paper index](../papers/README.md) covers 32 verified archived PDFs.
[Research records](research/) include technical anchors, version qualifications,
179 individual forward-screening decisions and software/standards evidence.
Screening is title/metadata relevance review unless a separate technical reading
record says more. Four important paper candidates remain inaccessible.

## Reproduce the design and checks

From the repository root, author-entered records generate the supporting files:

```bash
python3 scripts/build_design_research.py
python3 scripts/build_repair_fixtures.py
python3 scripts/build_real_case.py
python3 scripts/build_core_contract.py
```

The generators use retained inputs; they do not perform literature review or
establish accounting correctness. Research generation rejects candidates without
an explicit screening decision. Update authored inputs before regenerating
independently edited fixtures.

Run the deterministic reference checks from the repository root:

```bash
python3 scripts/check_design_examples.py
python3 scripts/check_repair_conformance.py
python3 scripts/check_core_contract.py
```

They use Python 3, exact rational arithmetic, Z3, Lark and jsonschema. They check
12 original illustrations, 49 repair examples and 31 contract/reference
assertions. A general DSL compiler and product runtime are not implemented.

Build from `docs/design`:

```bash
latexmk -xelatex -interaction=nonstopmode -halt-on-error accounting-product-design.tex
```

The build uses XeLaTeX, BibTeX, latexmk, Latin Modern and the packages in the
root TeX file; it needs no shell escape. After a changed PDF, render and inspect
its pages, update the review manifest, then run from the repository root:

```bash
python3 scripts/verify_design_document.py
```

The verifier checks library hashes, references, external typeset listings,
build freshness and author/current-PDF review records. It fails if an old
rendered review is attached to a new PDF.

## Review evidence and remaining scope

- [Author review](review/author-review.md) and [gap results](review/gap-repair-results-2026-10-02.md).
- [Final verification/manifest](review/repair-verification.json) and [document consistency](review/verification.json).
- [Original arithmetic](review/example-checks.json), [repair checks](review/repair-conformance.json) and [contract checks](review/core-contract-checks.json).
- [Rendered review](review/repair-render/final/manifest.json), [build log](review/repair-build.log) and [baseline comparison](review/baseline-comparison.json).
- [Execution note](review/repair-execution-note.md) and [checkpoint](../plans/accounting-product-design-checkpoint.md).

Apple's acquired files are inventoried, but all-note semantic translation and
external incorporated documents remain incomplete. Full ASC authority and
official-current ASBE verification are missing; bank/insurance and broader
hybrid methods need additional work. Full compiler/runtime/adapter conformance,
independent accounting/implementability review, human comprehension and
empirical forecast validation remain separate acceptance obligations.

The [protected original](review/pre-repair-2026-10-02/manifest.json) preserves
the 60-page baseline. The workspace has no usable Git revision; content hashes
record provenance without inventing a commit.
