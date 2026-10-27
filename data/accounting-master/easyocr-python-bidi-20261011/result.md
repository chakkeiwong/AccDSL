# `python-bidi` 0.6.11: bounded dependency-source result

11 October 2026. E14/C07; MC23/30/31/34/35. The inspected EasyOCR 1.7.2
source lists `python-bidi` without a version bound and imports
`bidi.get_display` unconditionally. PyPI's current non-yanked stable release
was 0.6.11 at inspection. This is a **candidate release**, not a resolved
EasyOCR lock or project default.

The retained PyPI JSON names `python_bidi-0.6.11.tar.gz`, uploaded
30 June 2026, requiring Python 3.9 or later. The 57,647-byte archive's SHA256
`034090c597af250d699299d7e7f1e83eb016f9e47b3b707bd89ab2bdec77bce0`
matches PyPI's declared digest. Its `pyproject.toml` classifies the package
under the GNU Library/Lesser GPL. Its `bidi/__init__.py` says the package is
under GNU LGPL **version 3 or later**; the archive includes `COPYING.LESSER`
for LGPLv3 and the incorporated GPLv3 `COPYING` text. The PyPI `license` and
`license_expression` metadata fields are null, so neither field supplies an
independent exact grant. These source files, rather than an old issue comment,
support the stated edition-specific licence finding.

This candidate's top-level `bidi.get_display` imports `bidi.wrapper`, which
calls a compiled Rust extension. The README explicitly distinguishes that
top-level Rust path from the older Python implementation at
`bidi.algorithm.get_display`. EasyOCR's inspected import selects the top-level
path, and its call uses one text argument supported by the wrapper signature.
That static match does not establish installed-wheel compatibility, identical
Unicode behavior, OCR output or platform availability. `Cargo.toml` lists
`pyo3` and `unicode-bidi`. The archive's `LICENSE-THIRD-PARTY.yml` is **not
synchronized with its own `Cargo.lock`**: it lists PyO3 0.22.1 versus locked
0.29.0 and `unicode-bidi` 0.3.15 versus locked 0.3.18. Thirteen of its 19
name/version rows do not match the bundled lock (some names are absent);
the lock also contains the root package, which is appropriately outside the
third-party notice. The notice therefore cannot establish exact transitive
terms for this candidate. Actual build resolution and distribution
obligations remain open.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain 0.6.11 as a source-inspection candidate | Exact PyPI digest, source version, LGPL header/text and import path checked | No source-identity veto | Actual resolver choice and wheel/platform support | Build a justified dependency lock in later implementation preparation | Adopt 0.6.11 as default |
| Flag distribution terms for exact-use review | LGPLv3-or-later source header and included licence bodies | Bundled third-party notice/lock mismatch and missing actual distribution context veto blanket clearance | Selected wheel, linking, modification, notices, conveyance and model terms | Reconcile exact build dependency terms and specify intended distribution | Automatically incompatible with EasyOCR's Apache licence or legally cleared |
| Keep OCR validation open | Static one-argument API match; top-level Rust path identified | No static import-path veto | Unicode behavior and accounting-document tests | Later pinned install and downstream OCR checks under a separate evidence contract | Runtime compatibility, accuracy or product readiness |

No stochastic comparison or ranking occurred. The strongest alternative
explanation is that a future resolver selects a different `python-bidi`
release, or another version has different licence/API/build behavior. This
result applies to the exact inspected archive only. Version 2.31's manuscript
and all frozen source records remain unchanged; full readiness is `not_ready`.
