# Exact terms for the two direct Rust dependencies

11 October 2026. E14/C07; MC23/30/31/34/35. Both direct crate archives
match the checksums in the inspected `python-bidi` 0.6.11 `Cargo.lock`:

| Crate | Exact version | Source-declared terms | Declared minimum Rust |
| --- | --- | --- | --- |
| `pyo3` | 0.29.0 | MIT OR Apache-2.0 | 1.83 |
| `unicode-bidi` | 0.3.18 | MIT OR Apache-2.0 | 1.47.0 |

All 17 source checks pass. Exact crates.io responses, archives, package
manifests and licence files are retained in the source ledger. The two
package manifests agree with their registry metadata. Both include MIT
permission and notice text and Apache-2.0 terms. PyO3's README states the
choice explicitly; its bundled `pyo3-runtime` licence files have the same
bytes as the root copies. `unicode-bidi`'s `COPYRIGHT` and Rust source
headers also state the alternative terms.

The earlier `python-bidi` third-party notice names older versions. The
actual checked versions still declare the same broad licence alternatives.
Thus the notice is wrong as an exact version inventory, while a change in
those licence alternatives is **not supported** by this comparison. The
Python package itself separately states LGPLv3-or-later. A parent package's
licence cannot stand in for its dependencies' individual source records.

For a proposed MIT use of these crate sources, the inspected condition is
retention of the copyright and permission notices in copies or substantial
portions. The Apache alternative includes licence-copy, changed-file and
source-attribution conditions, applicable NOTICE handling, patent terms and
other conditions. No licence choice or distribution is made here. Final
wheel contents, Python-package LGPL obligations, model rights and the other
13 external packages in this particular Cargo lock still require their own
evidence. Build tools and optional/platform resolution may add other material.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain exact direct-crate terms | Lock/registry/archive identity and source licence bodies agree; 17/0 checks | No direct source-identity or licence-body veto | Final build and conveyed content | Inspect the other 13 locked packages under a bounded source plan | Whole dependency graph or wheel cleared |
| Treat the parent notice as stale in version | Parent notice versus Cargo lock differs; exact direct terms now inspected | Notice cannot replace version-specific evidence | Other listed versions and actual resolved features | Preserve discrepancy and inspect exact remaining editions | Licence change, incompatibility or legal breach |
| Continue preparation with Version 2.31 | Manuscript identity preserved | Runtime hold remains; this is source work | Compatibility and distribution use | Integrate only a useful general dependency example | Installation, model validation or product readiness |

The strongest alternative explanation is that a later build resolves
different crate versions or includes additional feature-specific code.
That does not invalidate these exact source readings but limits their use.
No stochastic comparison or statistical ranking applies. Full readiness
remains `not_ready`; no compiler, package install, OCR, GPU or outreach ran.
