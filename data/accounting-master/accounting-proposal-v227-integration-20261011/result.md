# Version 2.27 JPMorgan manuscript integration

11 October 2026. This unit integrates the checked JPMorgan source findings into
a separate reader-facing candidate while preserving Version 2.26 and its
source result. The candidate is the 168-page
`docs/design/proposal/manuscript-jpmorgan-guarantees-20261011/accounting-product-proposal.pdf`,
SHA256
`933091db38e0006a0124418150b3115b608780b777aee7dfc94ba270eb77a3f0`.
Full proposal readiness remains `not_ready`; independent-reader, domain and
human acceptance remain pending.

The bank chapter now places the reported JPMorgan parent, IHC, bank,
non-bank entities and guaranteed issuer before the existing illustrative bank
mechanics. It states that Exhibit 21 is a qualified significant-entity and
resolution-planning roster, that Exhibit 22.2 names JPMorgan Chase Financial
Company LLC as issuer and JPMorgan Chase & Co. as guarantor, and that the
reported guarantee description supplies no outstanding principal, valuation or
accounting recognition. The validation chapter now distinguishes 192 retained
report slots and eight reporting years from complete filing contents, while
preserving the four selected JPMorgan reports whose omitted Form 10-K pages
remain an explicit source boundary.

The source delta is restricted to the title/date, the two prose repairs and
four official issuer-hosted 10-K bibliography entries. The focused checker
passes **86 checks**: 48 displayed equations are byte-for-byte unchanged;
labels and literal references resolve; the bibliography grows from 67 to 71
entries; all four JPMorgan citations resolve; the 108 semantic checks and 147
Exhibit 21/22.2 checks remain passing; the rendered review-image hashes bind to
the rebuilt PDF; and the qualification sentences remain present. LuaLaTeX
builds cleanly after redirecting its font cache to `/tmp`; the only benign
package message is the existing `listings.sty` First Aid notice. The first
unredirected build stopped before typesetting because the default cache path
was not writable; it did not change the source or the candidate result.

The changed and adjacent PDF indices 114--117 and 146--149 were read in order
at normal resolution. The two remaining pages (148--149) close the acceptance
chapter and begin Appendix A with no clipping, orphaned heading or detached
qualification. The surface auditor was rerun and retained as a deterministic
diagnostic; because the document delegates content through `\input`, its
top-level counts do not certify whole-document coverage.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain Version 2.27 as the current manuscript candidate | Nonempty reader-facing delta, clean 168-page build, 86 preservation/source/render checks, and ordered page inspection | No source-drift, equation-loss, citation, build or render veto | Independent reader and domain interpretation | Continue bounded source preparation and obtain independent reading when available | Whole-proposal readiness, implemented runtime or accounting compliance |
| Accept the JPMorgan repair within its stated scope | Reported entity/guarantee/perimeter distinctions are tied to 108 semantic and 147 exhibit checks | No documentary veto in the retained source units | Ownership, balances, transfer rights, instrument terms and guarantee valuation | Inspect operative registrations/indentures and parent funding facts | Complete group graph, recognized guarantee liability or default probability |
| Keep the panel completeness claim qualified | Acquisition count and semantic closure are explicitly separated | No count-preservation veto | Historical byte availability and full package semantics | Continue publication and incorporated-document work | Complete issuer filing contents for all 192 slots |

| Inference class | Status |
| --- | --- |
| Hard veto screen | Passed source-preservation, citation, equation, build, page-count and render-image checks; accounting validity and independent interpretation remain unevaluated |
| Statistically supported ranking | N/A; this is deterministic document/source work |
| Descriptive-only differences | The candidate is descriptively clearer at the two repaired transitions; no scientific or performance ranking is claimed |
| Default-readiness | `not_ready`; no numerical, accounting or probability default changed |
| Next evidence needed | Operative guarantee/registration terms, ownership and balances, historical availability, complete package semantics and independent/domain review |

The strongest alternative explanation for an apparent guarantee or funding
change remains a disclosure-scope or wording change rather than a changed
economic obligation. The repair records that distinction and does not infer a
balance, transfer right, liability or probability. The weakest evidence is the
still-unresolved legal and historical context, not a failure of the
representation design. The next source frontier is recorded separately in
`next-source-frontier.md`.
