# Initial-state and requested-loss conditions repaired

27 October 2026. C21 / MC10–12/26/29/32/33. Prepared 5.52-R2 from protected
5.52-R1; no stable pointer has been changed by this unit. The current master
may advance concurrently and must be reconciled before selection.

The original finite-coupling argument did not explicitly require the initial
state pair to satisfy its relation with matching current output, and it
asserted loss equality without requiring that the loss use preserved records.
A literal claim for arbitrary bounded path loss is unsupported under those
written hypotheses. The intended result is correct with these conditions.

The manuscript now states the initial relation and complete initial matching,
common feasible information-based policy, and common measurable bounded loss.
Its unconditional survival recurrence also handles zero surviving probability.
It retains the original product bound and numerical example, then adds
initial mismatch delta0 and within-pair loss error rho: with
Delta = 1 - (1-delta0) product_t(1-delta_t), the expected loss difference is at
most rho + (B-rho) Delta. This follows by splitting the coupled absolute loss
difference over matching and nonmatching paths. No new source theorem is claimed.

272 exact rational checks include the two missing-hypothesis counterexamples,
zero/one mismatch limits, exhaustive finite survival hazards, a threshold atom
and sharp two-epsilon common-policy regret. These are deterministic checks,
not statistical superiority or empirical model validation.

Both volumes build: 831 main pages and 263 total simulation pages. Protected
predecessor files remain unchanged, all citation tokens and bibliography bytes
are preserved, and the intended change set is confined to the argument, version
roots and package README. The failed draft citation pattern emitted a warning;
it was repaired with explicit escaped delimiters and a nonempty-count check.
No claim relies on the earlier weaker parser.

The four baseline standalone pages and six resulting main/standalone pages were
actually viewed. Mathematical assumptions and interpretations are legible, with
no clipping or undefined references/citations. A sentence spanning a page break
is ordinary continuation and does not hide a condition. Source/build and visual
evidence are in verification.json, exact-results.json, build-manifest.json and
rendered-review.json.

| Decision | Primary criterion | Veto status | Main uncertainty | Next action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain corrected local bound and prepare integration | Proof now states initial/loss hypotheses; old examples preserved; both builds pass | Literal broader claim repaired; no source or fixture loss | General kernel-error certification and independent reading remain open | Reconcile live candidate, package and integrate; continue source/whole-document review | Release acceptance, arbitrary hidden losses, unbounded losses, or empirically estimated error coverage |

Reader comprehension, mathematics, source fidelity and engineering are separate:
this unit clarifies the conditions; checks the local derivation and examples;
preserves imported claims; and verifies builds/rendered changes. It does not
constitute the full-document or independent-reader acceptance required for release.
