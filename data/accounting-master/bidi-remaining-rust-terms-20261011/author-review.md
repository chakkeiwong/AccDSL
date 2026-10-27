# Bounded terms-source review

I checked exact edition metadata, registry and parent-lock checksums, package
manifests and all 26 archive rights files. The twelve MIT grant/notice bodies
are identical after whitespace normalization once attribution prefixes are
separated; exact copyright lines were preserved. I read the LLVM exception
and the Unicode data-file terms separately, together with `unicode-ident`'s
README distinction between generated and other code.

The thirteen normalized Apache sections 1–9 are identical to the already
read unicode-bidi 0.3.18 licence body; their exact original files remain
retained. This comparison supports reuse of that reading without silently
discarding the separate LLVM exception or any attribution prefix.

The 82 header hits contain local Apache-or-MIT SPDX lines, ordinary source
references and identified code adaptations. I inspected the material
`portable-atomic`, `pyo3-ffi`, `libc` and `unicode-ident` contexts. Their
upstream rights correspondence is not independently established by these
local references. No large source files were omitted by the bounded scan,
but a keyword scan is not an exhaustive human rights-chain review.

The result distinguishes package-level source declarations from actual build
resolution, selected features, wheel contents and a legal distribution
decision. It does not treat stale version metadata as proof that licence
alternatives changed or that reuse is prohibited. These are author documentary
checks; compatibility, OCR behavior and domain acceptance remain untested.
