# Bounded dependency review

The source identity is supported by the PyPI JSON, declared distribution
digest and locally recomputed SHA256. I read the archive's `pyproject.toml`,
`bidi/__init__.py`, `bidi/wrapper.py`, README, `Cargo.toml`, the opening and
scope of `COPYING`/`COPYING.LESSER`, and the relevant third-party notice rows.
I compared the bundled third-party notice against `Cargo.lock` and found
13 unmatched name/version rows. The notice is not an exact lock-level terms
inventory.
The EasyOCR comparator is the already pinned 1.7.2 requirement and import.

The material default risk is the unbounded dependency. The latest inspected
release is only a candidate; no resolver, wheel, Python environment, OCR
sample or model asset was run. The top-level Rust path may change text
behavior relative to the older Python implementation. A one-argument static
signature match is narrower than runtime compatibility. Licence text is
source evidence, not a legal conclusion about any actual distribution. The
notice/lock mismatch is a concrete reason to withhold transitive clearance.

The source record can inform the E14 dependency and terms decision. It does
not promote OCR to an executable or distributable feature. Independent
domain/human and legal acceptance remain separate.
