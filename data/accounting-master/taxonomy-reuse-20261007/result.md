# Taxonomy and Arelle source preparation

8 October 2026. The bounded E14 source/manuscript unit is complete as internal
author preparation. E01 and E14 remain open; the proposal remains `not_ready`.
The separate 127-page Version 2.3 is
`docs/design/proposal/manuscript-taxonomy-20261008/accounting-product-proposal.pdf`,
SHA256 `479fd8007fab98b7ee8393a732e183010bcfbd24df027f8dea5998ce43aad030`.

The Apple FY2024 archive has six XML members and ten direct taxonomy imports.
The inspected graph now retains those imports and eleven further dependencies:
27 XML nodes, including 21 external schemas, with 3,551 recorded references
resolved and no remaining edge in that traversal. The checker tests namespace
and fragment identity and declarations for 1,127 facts, 193 contexts and seven
units. Its 10,396 assertions pass. This resolves the recorded static taxonomy
frontier; it does not run schema/XBRL validation or close the filing's other
incorporated sources and material narrative obligations.

At Arelle commit `01f6a4656c2c6551d2f05f31c9d74366d133ee7e`, inspected controller,
cache, document loading, session, options and model code establish two specific
requirements. An offline cache can return a pathname for an absent file, so
the proposed adapter checks mapped files and hashes before loading. Validation
errors affect the controller's success return only when `validationExitCode`
is enabled; the adapter also inspects structured logs and model errors. It
selects structured logging explicitly, copies occurrences while the model is
open, preserves order independently of set iteration, and closes one owned
session. Four proposed exchange/failure examples are retained. The 65 source
anchor/expression checks pass; they do not execute Arelle.

The retained terms distinguish Arelle's source licence, FASB US GAAP/SRT notices,
SEC-authored schema headers and XBRL component conditions. The unversioned
FASB pages retrieved in October 2026 display a 2027 copyright date; they do not
establish which terms applied to the 2024 filing. A candidate Software Notice
URL returned HTTP 404. Fifteen base and three build requirements are inventoried,
but no exact installed dependency or transitive licence lock is supplied.
Distribution and wider tool/model terms remain unestablished.

Version 2.3 adds this explanation to section 13.13 and four bibliography entries.
The recorded trusted LuaLaTeX build succeeded in 3.17 seconds with no final-log
warnings. Recovery found that the old render manifest preceded that build;
new before/after-bound rendering preserves the earlier record and images.
The author inspected title/contents pages 1, 5–6, body/adjacent pages 98–101,
and bibliography pages 122–127. The candidate checker passes 138 assertions,
preserves 37 displays and all 57 earlier bibliography keys, and detects only
the three intended changed source files. It rechecks 1,266 protected files,
518 upstream references and six controller records, plus the historical P19
manifest through its saved pointer copies. Independent reader/human acceptance
remains pending. The entry-point-only surface audit is not manuscript coverage.

The recovery Git probe now finds the existing worktree at commit
`8e3b2628df8c89f7315119170b82624d536bc3e5`; earlier records saying Git was unusable
describe their saved state and are preserved. No Git mutation was performed.
The current dirty worktree means that commit alone cannot identify these new
artifacts; their hashes are in the run manifest.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not established |
| --- | --- | --- | --- | --- | --- |
| Finish this static source/manuscript unit | Located dependencies, source-grounded exchanges and bounded rendered insertion supplied | Stale render binding repaired; preservation checks pass | A future validator may discover further resources or compatibility defects | Preserve this result and proceed to independent authority/literature work | Full XBRL validation or accounting admission |
| Keep E14 open | Broader interfaces and exact dependency/model/terms evidence incomplete | Missing terms veto distribution claims | Historical taxonomy terms and transitive licences | Resolve source-specific questions before later reuse decisions | Deployment, distribution clearance, tool superiority |
| Continue the proposal | E01/E05/E07/E08/E14 acceptance still unmet | No continuation veto on independent work | Full authority/literature and company coverage | Inspect operative banking/financing/insurance claims and the four blocked papers | Whole-proposal readiness or human acceptance |

Post-run red team: graph resolution could appear complete while omitting a
discovery edge; the traversal and claim are therefore explicitly static. A
later runtime mismatch would invalidate the affected proposed exchange, not
erase the retained source bytes. The candidate did not fail an accounting
experiment: no such experiment ran. Remaining source gaps trigger continued
internal preparation under MC35 rather than a paid referral.
