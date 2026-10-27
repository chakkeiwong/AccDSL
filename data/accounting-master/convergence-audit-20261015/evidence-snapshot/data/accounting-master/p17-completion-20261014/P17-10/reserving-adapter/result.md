# P17-10 reserving adapter — scoped result

14 October 2026. Version 2.87 is a 258-page provisional candidate, not_ready.
The retained unmodified ChainLadder output is unsupported for a complete
predictive result because it removes the per-cell distinction between a valid
zero and a failed process draw. The proposed exchange preserves that distinction
and the exact requested process law. It does not implement an R adapter.

## Decision and evidence

| Decision | Primary criterion | Veto evidence | Main uncertainty | Next justified action | Not concluded |
|---|---|---|---|---|---|
| Reject native post-coercion arrays as complete predictive evidence | Two distinct pre-coercion worlds produce the same returned array | Missing original failure mask; input structural mask cannot repair it | Whether a future instrumented implementation preserves all required evidence | Pin and validate a distinct implementation in the later runtime program | No claim that all native zero payments are failures |
| Retain the proposed documentary exchange | 18 cases and 1,115 schema, identity, closure, law, coverage and arithmetic checks pass | Wrong law, unsupported native dispersion/shape, mixed fits, missing cells and invalid payments have explicit adverse results | Actual numerical generation, dependencies, terms and durable restart unexecuted | Continue connected-group atomicity/replay specification | No calibration, stochastic ranking, runtime compatibility or compliance |
| Integrate the boundary into the governing manuscript | 93 preservation/build checks pass; six physical pages inspected | No current build or preservation failure | Whole-document and human comprehension review pending | Continue P17-10/11 and P18 integration | No full P17/P18/P19 completion |

The source baseline is mages/ChainLadder commit
5cd0dd441c3bb9e1ee6d7572d5bc1475f29be728, DESCRIPTION 0.2.17 dated 2023-01-09.
Its inspected source replaces process NA with zero before returned aggregation
and supplies no original failure mask. The authored worlds (0,4,0) and
(0,4,failed) therefore return the same numeric vector and total. This is an
information-loss argument, independent of executing a stochastic generator.

The native od.pois helper uses a negative binomial with mean m and size
m/(phi−1) for phi>1 and Poisson at phi=1. It cannot satisfy a scaled-Poisson
request merely by matching mean and variance. For m=2, phi=3/2, negative-binomial
size is 4 and variance is 3; a payment of 1 is possible, whereas the
scaled-Poisson support consists of multiples of 3/2. Gamma remains a separate
positive law and is not ruled out by the helper's underdispersion limitation.
The inspected equal-row/column check limits this profile to square triangles.

## Complete expected exchanges

The schema-closed bundle contains 209 records and 33 exact blobs. It reuses the
common operation envelope with optional documentary reserving.evaluate@1.
It is pure regarding financial books and probability-law admission. It retains
the triangle, method/law, requested draw IDs, shared fit IDs, raw output bytes,
cell status, units and every required dependency.

Authored vectors (0,4,8) and (2,6,10) give totals 12 and 18 and sample mean 15.
A failed cell leaves its draw total null; completed-only mean 18 is explicitly
diagnostic. Cancellation after the first draw retains total 12 but withholds the
requested full-sample mean. Unknown termination remains unresolved; the fixture
has no checkpoint and offers no resume. Computational counts are not probability
mass over economic histories. Native seed reinitialization in both stages is
recorded without an independent-stream claim.

Adverse cases cover failed/cancelled/unknown execution, native zero coercion,
wrong law, unsupported native underdispersion, mixed fits, duplicate draws,
missing cells, wrong currency, unavailable observed values, negative and
noninteger payments, rectangle shape and zero fitted mean. Positive cases include
the explicit gamma-underdispersion and Poisson-at-one laws. Input rejection keeps
the exact submission and has null validated request/coverage. Producer rejection
after successful input validation retains the validated request.

## Integration and preservation

The new section teaches the failed-zero counterexample before the exchange,
law support and cancellation requirements. All 72 predecessor source files and
the 2.86 PDF are protected. Only the successor root and insurance input changed,
with one new section. Prior displays remain 88; labels increase 156 to 157 and
citations 460 to 463. Bibliography bytes are unchanged; all 75 project build
inputs resolve inside the successor. All 100 unrelated staged entries match
the recorded index baseline.

Candidate: docs/design/proposal/manuscript-reserving-adapter-20261014/accounting-product-proposal.pdf

SHA256: 1af3ff838342d23e23924a2d5b2fe0038fb3f07a502e81c99212a3144fd11742.
Build: 20.899 seconds, 258 pages, no recorded diagnostics. Physical pages
1, 6, 187–190 were visually inspected. The prior full author assessment remains
Version 2.72; this is a scoped supplement.

## Claim disposition and red-team note

Existing retained source/code support and the 2.85/2.86 literature decisions are
reused within their inspected scope; no new academic source, theorem claim or
literature-coverage completion is added. The strongest alternative explanation
is that a later upstream version or instrumented implementation could return a
failure mask. That would require different inspected bytes and would overturn
the native capability disposition for that version, not this retained snapshot.
The weakest evidence is runtime behavior: none was executed. The counterexample
and exact authored exchanges support the specification only. There is no
statistical comparison and no supported ranking.

The result identifies a package-output limitation, not an invalid research
direction. It triggers an evidence-preserving interface requirement and leaves
the independent connected-group atomicity/replay unit ready. No continuation
veto fired. See docs/plans/accounting-insurance-atomic-commit-20261014.md.
