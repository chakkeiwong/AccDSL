# Repair execution note and manifest guide

Date: 2 October 2026. Plan:
`docs/plans/accounting-gap-repair-2026-10-02.md`. The pre-execution skeptical
audit is `repair-plan-review-2026-10-02.md`; the substantive result and remaining
work are `gap-repair-results-2026-10-02.md`.

## Question, comparator and decision

The question was whether the expanded gaps could be turned into concrete
methods, cases, interfaces and reviewable evidence without narrowing the
mission. The comparator is the saved 60-page draft, not a production engine.
The plan's criterion was a traceable disposition for every G1–G18 finding,
with precise supported behaviour and honest residual obligations. Wrong
arithmetic, lost alternatives, unsupported sources, stale artifacts and
unreadable confirmed passages triggered repair. Page/paper/test counts were
inventory only. No stochastic comparison or forecast ranking was performed.

The local campaign delivered a revised candidate and updated mission control.
Full domain, product and human acceptance remain pending. Missing sources
qualified dependent claims; they did not stop independent design work.

## Commands actually used

The meaningful generation and verification commands, run from the repository
root unless otherwise stated, were:

```bash
python3 scripts/build_repair_fixtures.py
python3 scripts/build_real_case.py
python3 scripts/build_core_contract.py
python3 scripts/build_design_research.py
python3 scripts/check_design_examples.py
python3 scripts/check_repair_conformance.py
python3 scripts/check_core_contract.py
```

The debt schema/fixtures and contract checker were rerun after the final domain,
assumption and alternative metadata repairs. Unchanged arithmetic suites retain
their passing reports. The research generator completed after individual
screening decisions replaced its automatic generic dispositions. It now fails
before output generation if an encountered candidate lacks a decision.

From `docs/design`, the document was rebuilt after manuscript/layout edits:

```bash
latexmk -xelatex -interaction=nonstopmode -halt-on-error accounting-product-design.tex > review/repair-build.log 2>&1
```

The final page render and text extraction used:

```bash
pdftoppm -png -scale-to 1100 docs/design/accounting-product-design.pdf docs/design/review/repair-render/final/page
pdftotext -layout docs/design/accounting-product-design.pdf docs/design/review/repair-render/final/document.txt
```

Pillow generated 4-by-2 page contact sheets. All sheets were inspected, followed
by selected full page images. After later layout edits, images were regenerated
and hashed; changed pages were inspected again, while byte-identical page
images retained their prior inspection. The manifest binds the final PDF,
images and review status. The former 60-page renders remain separate.

Final consistency is checked with:

```bash
python3 scripts/verify_design_document.py
```

Additional bounded diagnostics verified all 45 protected-file hashes, compared
all 34 requirement/acceptance pairs with the protected register, counted actual
forward candidate IDs/occurrences, compared removed display math/citations and
checked companion source hashes/links. They are recorded in
`repair-verification.json`; they are not a second scientific experiment.

## Source and environment record

New retrieval outcomes are retained in `research/retrieval-attempts.json`,
`research/standards-support.json`, `research/supplemental-support.json`, the
catalogue and `cases/apple/manifest.json`. Sources used in claims have local
copies and specified inspection scope. FASB returned 403, the Ministry index
returned 502 and full ASC text required login; the bounded alternate attempts
and source qualifications are recorded. No inaccessible technical claim was
invented to make a requirement appear complete.

The environment is the existing local Python/TeX environment on CPU. No
TensorFlow/JAX/PyTorch import, GPU work, training or dependency installation was
needed. Lark and JSON Schema check syntax/structure; Z3 checks bounded rational
constraints. The final manifest records actual package versions. Random seeds
are N/A for this deterministic campaign; the stream fixture uses its explicit
synthetic key `seed1`, which is not a Monte Carlo study.

Git commit is unavailable because the workspace Git marker is not a usable
repository. No Git initialization or commit occurred. The protected snapshot
and final hashes replace missing commit provenance. Data versions are the
frozen filing/source bytes and fixture hashes in the manifests. Individual
check wall times are recorded where the checker measured them; total campaign
wall time was not recorded and is not estimated.

## Final skeptical review

The strongest remaining alternative explanation is shared author assumptions
between prose, expected values and reference checkers. Exact arithmetic,
solver counterexamples and acquired source bytes are useful independent
constraints, but they do not certify full semantics, accounting treatment or
human understanding. The next discriminating evidence is independent
implementation and domain review on the declared cases, followed by a broader
annotated real-company corpus. A failed future candidate does not by itself
invalidate the whole representation approach; identify whether the failure is
in scope, source, implementation, treatment or forecasting assumptions.

No unexplained failed local check remains. Known source and method gaps remain
visible in the result map. The decision is to deliver Version 1.1 as a design
candidate and keep the wider mission active.
