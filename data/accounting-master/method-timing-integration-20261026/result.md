# Version 4.45 method and timing integration

Version 4.45 is a 541-page proposal candidate, not_ready. Appendix A.54.7
explains exact timing over the whole native evidence closure; A.54.8 explains
complete bounded method authoring, including typed claim insertion and the
consequential half-payment example. All 178 predecessor source files and their
prior mathematics remain, subject only to the explicit version/include changes.
Two source files were added. The build has no new warnings and five inherited
underfull warnings. The cover and physical pages 505–508 were inspected.

PDF: docs/design/proposal/manuscript-method-authoring-20261026/accounting-product-proposal.pdf
SHA256: 3cdfb69adfa669a75cb8902fc7ee45d25ed939a988f571b8204350cb784e576e.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
|---|---|---|---|---|---|
| Retain Version 4.45 as governing candidate | Exact allowed delta, checked evidence and rendered additions | Baseline, references and warning checks pass | Whole-candidate consistency and independent/human acceptance | Connect authored methods to a registry that explicitly selects v1/v2 semantics | Complete design, production runtime or migrated native bank profile |

The next inspected dependency is concrete: CompanyMethodRegistry/2 delegates to
the original v1 transition engine. Its entry fields do not select transition v2
or supply a memory definition. Claim-creating methods therefore cannot simply
be inserted into that frozen registry. A separate successor must preserve
original v1 behavior and explicitly dispatch typed-growth methods, with complete
state/result comparisons and refusal of stale or malformed unselected entries.
No source-data ambiguity prevents this internal design step.

MC05/20/23/24/25/32/33/34 receive scoped evidence. All 53 obligations, six
interactions and 46 operations remain represented; no whole obligation closes.
S1–S5 remain partial, S6 held and S7/E3 deferred. No continuation veto fired.
