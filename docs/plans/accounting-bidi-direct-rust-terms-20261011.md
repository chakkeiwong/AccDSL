# Direct Rust terms for the inspected `python-bidi` candidate

11 October 2026. E14/C07; MC23/30/31/34/35. Follow the exact
`python-bidi` 0.6.11 source inspection without installing or executing it.

## Question and evidence contract

The bundled third-party notice gives stale versions for its two direct Rust
dependencies: `pyo3` 0.22.1 and `unicode-bidi` 0.3.15, whereas the same
archive's `Cargo.toml` and `Cargo.lock` resolve 0.29.0 and 0.3.18. Do the
authoritative exact crate releases carry licence terms consistent with the
notice's broad MIT/Apache labels? The comparator is the verified archive,
not an installed dependency graph.

Primary pass: retain official crates.io exact-version metadata and crate
archives, verify each archive against the matching `Cargo.lock` checksum,
read package metadata and licence files, and record the direct-dependency
verdict separately for each. Metadata licence labels alone are explanatory;
source licence bodies decide whether the advertised grant has inspectable
support. Wrong package/version/hash, absent body or inaccessible source is a
promotion veto for that crate. Missing deeper transitive crates limits this
unit but is not a continuation veto. No legal clearance, install readiness,
distribution approval or OCR behavior follows.

Output under `data/accounting-master/bidi-direct-rust-terms-20261011/`:
exact bytes, bounded receipts, checks, result, manifest and next source
frontier. Stop unchanged-route retries after one sandbox and one trusted
attempt per URL; do not convert network failure into a licence conclusion.

## Skeptical default and assumption audit

The locked versions are inherited from the verified candidate sdist, not
chosen as universal defaults. A build might update lock resolution or select
platform-specific features; these are source-inspection hypotheses. The
bundled notice might be stale in version only, with unchanged licence terms;
direct archive inspection discriminates that from a terms change. A crate
tarball can be wrong or corrupted; compare exact lockfile digest before
interpreting terms. A two-crate check cannot complete the 15 external locked
dependencies or final conveyed wheel contents. This plan passes because it
uses the correct baseline, predeclares digest/source vetoes, and narrows the
conclusion to two direct editions.
