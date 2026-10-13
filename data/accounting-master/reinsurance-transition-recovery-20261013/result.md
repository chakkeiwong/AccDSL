# Reinsurance transition loss recovery — result

13 October 2026. Version **2.55, 201 pages**, readiness **not_ready**.
Candidate: `docs/design/proposal/manuscript-reinsurance-recovery-20261013/accounting-product-proposal.pdf`.
SHA256: `1655ce7fbf6d266d589c0c4f448cab2bb4f700e1cfb46abf5d2613a6bd5fd789`.

Section 12.10 derives the separate loss-recovery component under C20A and
explains its express exception to B119C's ordinary timing condition. For the
authored issued group with loss component 20 and expected recovery 60%, the
transition component is 12. The issued liability remains 120. The calculation
does not identify the whole reinsurance asset, cash receipts or opening equity.

Additional, explicitly supplied total reinsurance assets of 45 before and 50
after transition allow the two-group equity bridge 325→320. Those total asset
measurements are assumptions, not outputs of 20×60%. Adding 12 again would
overstate assets/equity by 12. A separate later underlying loss component of
14 yields a B119F upper bound of 8.4, not a unique new asset or P&L result.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Integrate the C20A component example | Timing exception and R=Kq supported by inspected text | No unresolved source/sign mismatch in conditional scope | Actual treaty, grouping and expected recovery | Retain each dependency and inspect acquisition interaction next | Actual treaty eligibility or full valuation |
| Keep the asset/equity calculation conditional | Component 12 distinguished from supplied full asset 50 | Gross netting and component double counting rejected | Total asset not derived from actual cash flows | Obtain separate full measurement for any real application | C20A alone supplies equity or complete CSM |
| Interpret the later diagnostic as a cap | R≤8.4 derived from stated recoverable portion | Old R=12 violates the cap | Actual later movements and allocation absent | Require complete update facts before computing P&L | The bound selects an exact new component |
| Retain provisional candidate | 44 source/arithmetic and 123 manuscript checks pass | No final build, preservation or selected-render failure | Human/domain acceptance pending | Continue internal work | Overall proposal readiness or runtime implementation |

Six source images and seven final manuscript pages were inspected. The selected
source chain includes 60–70A, 75, 78–79, B119C–B119F and C20A; C4 support
carries forward the immediately preceding same-source inspection. The final
build has no warnings, unresolved references or box diagnostics. A page break
keeps the complete-asset assumption and equity calculation together. The
historical recognition-date assumption and a prior Munich Re pointer were
clarified. The latter replaces only “next case” with “later Munich Re case.”

The protected baseline's 48 source files, 49 displays and 360 citation
occurrences survive. One display and six citations to an existing entry are
added; the bibliography is unchanged. Only the root version and insurance
section differ in the separate candidate. No full-document reread or independent
review is claimed.

Accounting interpretation is supported only for the historical edition and
explicitly conditional facts. Engineering evidence consists of arithmetic,
identity/preservation and selected-page review. Scientific forecast validity
is unevaluated, and no stochastic ranking is attempted. Post-run red team:
an unexamined treaty quota could create false certainty about q, while a correct
component could conceal an unsupported total asset. The manuscript states
both limits before using the relevant values. Changed treaty populations or
applicable rules require re-evaluation.

MC08/10/11/13/16/19/22/28/30/32–35 and G4/G6/G7/G15/G16 gain bounded
method evidence; all five E workstreams and broader acceptance stay open.
Next: `docs/plans/accounting-insurance-acquisition-recoverability-20261013.md`.
The exact Python interpreter is recorded in the manifest; an inherited
environment-description correction is retained in `inherited-check-note.md`.
