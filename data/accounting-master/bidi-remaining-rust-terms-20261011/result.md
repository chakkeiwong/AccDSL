# Candidate Rust dependency source inventory

11 October 2026. E14/C07; MC23/30/31/34/35. All 13 remaining archives
match both their crates.io metadata and the checksums in the inspected
`python-bidi` 0.6.11 Cargo lock. All 118 documentary checks pass. Together
with the preceding direct-crate unit, all **15 external packages in this
particular lock** now have retained exact source archives and package-level
terms evidence. This is not an installed, feature-resolved or complete build
dependency graph.

| Package | Locked version | Source-declared terms |
| --- | --- | --- |
| heck | 0.5.0 | MIT OR Apache-2.0 |
| libc | 0.2.155 | MIT OR Apache-2.0 |
| once_cell | 1.21.3 | MIT OR Apache-2.0 |
| portable-atomic | 1.6.0 | Apache-2.0 OR MIT |
| proc-macro2 | 1.0.86 | MIT OR Apache-2.0 |
| pyo3-build-config | 0.29.0 | MIT OR Apache-2.0 |
| pyo3-ffi | 0.29.0 | MIT OR Apache-2.0 |
| pyo3-macros | 0.29.0 | MIT OR Apache-2.0 |
| pyo3-macros-backend | 0.29.0 | MIT OR Apache-2.0 |
| quote | 1.0.45 | MIT OR Apache-2.0 |
| syn | 2.0.70 | MIT OR Apache-2.0 |
| target-lexicon | 0.13.3 | Apache-2.0 WITH LLVM-exception |
| unicode-ident | 1.0.12 | (MIT OR Apache-2.0) AND Unicode-DFS-2016 |

The exact 26 rights files are preserved beside source manifests and relevant
headers. Twelve packages contain an MIT grant with the same normalized
permission/notice/disclaimer body; attribution text remains exact and separate.
Their Apache alternative is also retained. The remaining package,
`target-lexicon`, contains Apache-2.0 with the LLVM exceptions. The first
exception concerns code embedded into object form through compilation and
specified redistribution conditions; the second concerns a particular GPLv2
combined-software situation. Neither is a blanket removal of all Apache
conditions. No exception is applied to an actual distribution in this work.

`unicode-ident` requires an additional distinction. Its README says generated
files combine Unicode Character Database material with crate code, so both
the Unicode terms and the chosen MIT/Apache alternative apply to those files.
The bundled Unicode text supplies notice, disclaimer and name-use conditions.
Flattening that expression to a single MIT label would omit source-stated
conditions. The parent Python package retains its separate LGPLv3-or-later
grant; the Rust packages do not replace it.

The 82 header-scan hits were reviewed as diagnostics, not an exhaustive rights
certificate. `portable-atomic` identifies adaptations from other projects
with local Apache-or-MIT SPDX headers. `pyo3-ffi` identifies compatibility
shims adapted from `pythoncapi-compat` and a CPython-derived branch; `libc`
links two Fuchsia/musl constants. Those references are retained in full source
context. This unit neither reconstructs every upstream derivation edition nor
establishes incompatible terms or an infringement. The actual compiled
platform/features and conveyed files remain unexamined.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain all 13 exact source records | Registry, lock and archive hashes agree; source grant files inspected; 118/0 checks | No package-identity or missing root-grant veto | Actual selected features, build tools and wheel content | Use the fixed inventory for a later justified lock and notice preparation | Installed dependency or full distribution clearance |
| Preserve compound and exception terms | LLVM exception and Unicode source provisions present | Single generic MIT/Apache summary is inadequate | Their application to actual conveyed content | Keep expressions and source conditions separate in design | Automatic incompatibility or permission to omit all notices |
| Retain embedded-code provenance questions | Adaptation/source references present in exact archives | No blanket rights-chain clearance; no demonstrated violation | Exact incorporated origins and platform branches | Inspect origins when the build/distribution scenario makes them relevant | Every source reference creates a licence defect |

No stochastic ranking or execution benchmark applies. The strongest alternative
explanation is that a later build resolves different versions or features; the
fixed candidate inventory would then need revalidation. The weak point is
actual conveyed contents and upstream derivation correspondence, not the
checked archive identities. No compiler, install, OCR, GPU or outreach ran.
Full readiness remains `not_ready`.
