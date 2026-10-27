# Matched annual inventory authoring — 25 October 2026

1,089 checks across 53 cases pass, with 15 focused and 26 regression methods.
AnnualInventoryAuthoring/1 compiles optional inventory sales and all existing
annual operations to exact AnnualInventoryProgram/1 requests. Text and typed
execution results match the direct evaluator, including refused operations and
retained prefixes. Raw source hashes and line spans distinguish alternate text;
semantic digests and request data remain exact. Compilation executes no finance.

The first smoke rejected an implementation that confused inventory's text
provenance with tax's structured provenance. attempt-01 preserves that source
and the failure. The optional validator now follows its own frozen event schema;
old-operation validation remains delegated unchanged. This was an implementation
failure, repaired before recording, not evidence against matched authoring.

| Decision | Primary criterion | Veto status | Main uncertainty | Next action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain optional compiler | Exact lowering, pure compilation and full result equality pass | No remaining conformance veto; original schema failure preserved | Finite profile, missing named-family composition and broader language | Check explicit annual inventory family adapter, then integrate both | General DSL completion, real policy admission or forecast accuracy |

Engineering correctness is supported for the tested bounded profile. Exact
rational arithmetic and prior annual invariants are preserved; no stochastic
comparison or statistical ranking is involved. Synthetic controls do not show
real-company completeness. The strongest remaining alternative is an untested
syntax or size boundary; malformed-input and legacy regression controls reduce,
but do not eliminate, that uncertainty. A mismatch against a valid direct
request would overturn the interface conclusion. Independent/domain/human
acceptance remains pending. S1–S5 partial; S6 held; S7 deferred.
