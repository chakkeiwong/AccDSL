# Fair-value transition balances — result

13 October 2026. Version **2.54, 199 pages**, readiness **not_ready**.
Candidate: `docs/design/proposal/manuscript-transition-balances-20261013/accounting-product-proposal.pdf`.
SHA256: `d69f9719902989736b79fec98b1e3bb03b255c5c74eaf1bfcfb7794e6f20eec3`.

Section 12.9 now derives both signs of fair value less fulfilment cash flows,
then reconciles the component entries and opening equity. With the stated
remaining-coverage-only assumptions, CSM=max(V−F,0), loss component=max(F−V,0)
and liability=F+CSM. The loss component stays within that liability.
The two authored groups produce liabilities 110 and 120, total 230, against
old balances totalling 220. Unchanged assets 500 imply equity 280→270.
Pooling the groups before the sign calculation would incorrectly give 210.

The calculation is correct relative to this explicitly conditional target,
supported by AASB17.38/40/47/49–50/C4–C5/C20 and the local derivation.
It is not an actual insurer valuation, a full transition including reinsurance,
tax/OCI/acquisition or incurred claims, or a current-operative-edition finding.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Integrate the conditional balance example | Both signs, boundary, separate components and opening equity derived | No source/sign/double-counting failure in stated case | Actual FCF/fair value, eligibility and group facts are supplied assumptions | Extend the separate reinsurance component under C20A | Actual insurer reconstruction or accounting acceptance |
| Preserve group-level calculation | 230 differs from improperly pooled 210 | Pool-before-sign shortcut rejected | Legally appropriate grouping is a precondition | Keep admitted groups until after component calculation | Every alternative grouping is prohibited |
| Retain provisional manuscript | 45 source/arithmetic and 123 manuscript checks pass | No build, preservation or selected-render failure | Human comprehension and independent domain judgment pending | Continue internal preparation | Whole-proposal readiness or implemented runtime |

Ten extracted source pages were read and four selected source images inspected;
the earlier full Appendix C inspection remains separately attributed. Seven
final manuscript pages were visually inspected: 1, 6 and 149–153. Author
review moved the opening-equity calculation to an intact new page. The final
LuaLaTeX build has no warnings, undefined references or box diagnostics.
This is selected-page typography and author review, not a new full-document
or human review.

All 48 baseline source files remain byte-identical, all 48 previous display
blocks and all 357 citation occurrences survive. One display and three
citations to the existing AASB17 bibliography entry are added. Only the root
version and insurance section change in the separate candidate. The prior
PDF, entire bibliography, frozen corpus and controller records are preserved.

Engineering evidence is the exact arithmetic, source identity, preservation
and rendered review. Accounting support is the inspected historical provisions
and scoped derivation; independent acceptance remains pending. Scientific
forecast validity is unevaluated. No stochastic ranking, empirical default or
statistical superiority is claimed.

Post-run red team: balanced journals could also encode the wrong liability,
so the source-derived component relation is necessary. Inclusion of incurred
claims, taxes, OCI, acquisition or reinsurance would require another derivation.
The strongest remaining limitation is the conditional valuation inputs, not
an unresolved arithmetic failure. The result advances MC08/10/11/13/16/19/22/
28/30/32–35 and G4/G6/G7/G15/G16 within E07; none of those wider obligations
is closed. Next execute the reinsurance transition recovery plan.
