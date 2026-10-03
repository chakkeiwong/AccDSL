# AccDSL product and implementation design

Read the [compiled design document](accounting-product-design.pdf). The
[LaTeX root](accounting-product-design.tex) includes ten chapters and two
appendices from [chapters](chapters/); [references.bib](references.bib) supplies
the bibliography. Version 1.0 is dated 2 October 2026.

The design governs a typed representation of company histories and conditional
scenario simulation. It preserves source evidence, reporting context, multiple
time dimensions, shared unknowns, alternative economic histories and accounting
interpretations. Events generate balanced journals and reports. Probability
weights require an explicit probability model; a feasible family alone does not
define a distribution.

The implementation sequence begins with the shared intermediate representation,
validators and Python API, then adds the bounded textual DSL. The document
compares this approach with XBRL, typed libraries, ledger tools, rule languages,
graphs, probabilistic programs and spreadsheets. Banking, insurance and detailed
standard-specific treatment have explicit later milestones and review duties.

## Reading routes

| Purpose | Chapters |
| --- | --- |
| Product scope and historical-record problems | 1–2 |
| Literature, alternatives and open-source reuse | 3–4 |
| Mathematical meaning of compatibility and simulation | 5 |
| DSL types, examples and execution | 6–7 |
| Standards, industries, bonds, equity, banks and insurance | 8 |
| Persistence, APIs, plugins, acceptance and implementation order | 9–10 |
| Grammar, core records, rule selection and traceability | Appendix A |
| Source versions, access gaps and review boundaries | Appendix B |

The [paper index](../papers/README.md) links 31 verified PDFs, with version
qualifications. The [research directory](research/) holds the catalogue, six
literature ledgers, software evidence, standards snapshots and source extracts.
Four important inaccessible sources are recorded as access gaps; no technical
claim relies on their uninspected full texts. This is a bounded design survey,
not an exhaustive review of every later sector module.

## Build and reproduce checks

From the repository root:

```bash
python3 scripts/build_design_research.py
python3 scripts/check_design_examples.py
cd docs/design
latexmk -xelatex -interaction=nonstopmode -halt-on-error accounting-product-design.tex
```

The build uses XeLaTeX, BibTeX, latexmk, Latin Modern fonts and the packages
listed in the root TeX file. It needs no shell escape. The research-generation
script updates the catalogue, bibliography, paper index and ledgers from
author-entered reading notes; it does not review sources or fetch new papers.
The claim-support ledger is maintained separately.

From the repository root, run the document/library consistency check with:

```bash
python3 scripts/verify_design_document.py
```

The arithmetic script checks the manuscript's financing and uncertainty
illustrations using exact rational arithmetic. It does not implement the DSL
or establish accounting-standard compliance. The consistency check validates
local paper hashes, references, research records and the build; it does not
certify the truth of source claims.

## Review evidence

- [Author review and remaining limits](review/author-review.md).
- [Example arithmetic](review/example-checks.json).
- [Consistency results and file hashes](review/verification.json).
- [Build log](review/build.log).
- [Plan and evidence contract](../plans/accounting-product-design.md).

Human comprehension review, independent accounting review and implementation
conformance remain pending. They are separate from author checks and successful
compilation. The workspace has no usable Git revision; checksums preserve the
reviewed document and library versions without inventing commit provenance.
