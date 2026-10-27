# Final document review

26 October 2026. The final integrated PDF is the 714-page Version 5.0 candidate
with SHA-256 `6a35cd61bd087fe4b1b508a74632d0a1765325cdd76b6f6104f24b0abda7b3d1`.
Root and PDF hashes are in `build-check.json`; source hashes are in
`candidate-source-manifest.json`.

## Inspected scope

During drafting, eleven contact sheets spanning the preceding 169-page reading
edition were inspected for chapter openings, navigation, tables and layout.
Those images are an earlier layout record, not proof of continuous reading.
Normal-resolution inspection of the unchanged standalone edition covered
physical pages 35–36, 54, 61–62, 85, 92, 98, 105–106, 145–146 and 163–170.
Before the final language merge, inspection of the then 713-page integrated
draft covered pages 1, 176–178, 679–681, 706 and 713. This includes debt
pricing/recovery, the aggregation
proof, scenario-reduction bounds, company journals, refinancing, ownership,
learning, tax memory, the complete finite-debt chapter, the Part I/II join,
latest inherited authoring section, and bibliography samples.

The bibliography version note changed standalone page 169; it was rendered and
inspected again, with integrated page 706. After the 4.50 language revision was
merged, integrated physical pages 267–271 were rendered from the final PDF;
their pixels matched the retained review images, which were inspected again
during final navigation. Physical page 714 was also rendered and inspected.
These readings distinguish source constraints from behavioural policies and
imported accounting rules, then follow the transition to type and identity
semantics. No clipping or broken reference was found in this slice. The binding is recorded in
`visual/final-v450-integration-review.json`. Earlier page-refresh comparisons
remain in `visual/inspected-page-refresh.json`; all final physical pages pass
the automated page-bounds scan, which checks clipping only.

## Findings and repairs

Earlier stripped LaTeX commands were repaired, including two recovery-ratio rho
symbols, a sampling relation, ellipses and epsilon. The tax-loss update was
corrected to avoid double-counting current losses. Currency-shock language now
states a change in the domestic-currency price of foreign currency; the swap
example states a net increase in interest cost; the hedge example uses
minimax-loss terminology. Julia Fonseca's bibliography metadata and the Givan
manuscript version were corrected. Final logs contain no overfull boxes,
undefined references/citations, missing characters, duplicate labels or BibTeX
warnings. No new defect was found in the final inspected page set.

| Ledger | Verdict and practical limit |
|---|---|
| Reader comprehension | The new text teaches the joint-history, information and financing mechanisms with worked cases. Author source review and selected rendered reading were performed; independent continuous reader review and human acceptance remain pending. |
| Mathematical integrity | 169 exact example checks pass. The local finite-horizon aggregation proof, scenario expectation/regret bounds and financing convention were inspected. This does not verify every possible model or the complete simulation engine. |
| Source fidelity | All new citation keys resolve and all 26 cited sources have retained copies and inspected-use records. Source results, local deductions and remaining version/code gaps are distinguished. Exhaustive literature and correction clearance are not established. |
| Typography and navigation | Both LuaLaTeX builds resolve references; all-page geometry and selected normal-resolution inspection pass. The two editions share the same chapter files. Contact sheets are not continuous reading. |

## Red-team assessment

The strongest remaining alternative explanation for an apparently successful
case is that its admitted model excludes the decisive contract, policy or
information mechanism. More sampling and balanced journals would not expose
that omission. The manuscript therefore retains model-scope limits, actor
information, failed branches and open structural alternatives.

The weakest current evidence is broader implementation and real-company
validation. Passing synthetic arithmetic establishes the quantities stated in
those examples, not correct reconstruction of an issuer or calibrated distress
probabilities. Actual-source company cases, adversarial cross-module execution
and independent reading can overturn or refine the design. No empirical method
ranking, neural-performance result, accounting compliance or product readiness
is claimed. Existing specification obligations remain open.
