# A raw PDF token is not a visible report-year assertion

12 October 2026. E14/E01/C07/P18; MC01–05/25/27/30–35,
G2/G5/G9/G11/G13/G17/G18. The bounded cover discrepancy is reproduced and
integrated into a separate **Version 2.38, 175 pages**. All **136 documentary,
preservation, schema, citation, render-binding and build checks pass**.

The selected HSBC 2023 annual PDF visibly reads Accounts 2023, while both
installed text extractors also return 2024. The selected drawing records show
earlier Accounts 2024 text covered by an opaque rectangle, followed by Accounts
2023. Raw output remains intact. A schema-valid example distinguishes the raw
extraction, proposed visible reading and rejection of 2024 as a visible report
year. Six proposed query outcomes cover search, identity review, historical
admission and correction. They are specification examples, not engine results.

The manuscript adds this case to the adapter discussion at final PDF 143–144.
All prior prose is preserved outside the insertion and title-version change;
48 displays and 75 bibliography entries remain, with one cover citation added.
Seven final pages were visually inspected. A lone paragraph-opening line was
repaired. The final TeX and bibliography logs have no serious warnings.

Final PDF:
`docs/design/proposal/manuscript-visible-text-20261012/accounting-product-proposal.pdf`

SHA256: `f77a019fcfb7af70faadc4a5f98aee31cf969713e0d1e898b7ac6a7a65749815`.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain the observed visibility case | Exact source, raw outputs, drawing records, inspected render and reproducible annotation | No source/page/hash mismatch | One-page scope and independent adjudication | Use the example in adapter review design | Parser accuracy ranking, malicious intent or an issuer accounting conflict |
| Retain Version 2.38 as the next provisional candidate | Narrow addition, preserved baseline, successful build and matching inspected pages | No equation, citation or source-preservation failure | Wider source/method gaps and human acceptance | Continue P17 preparation and integrate material findings through P18 | Whole-proposal readiness or an implemented adapter |
| Keep historical admission unresolved | No selected-byte availability proof obtained | A report year cannot substitute for availability evidence | Public vintage of this exact annual PDF | Preserve the frozen 56 verified / 136 unverified assessment | Admission on the Form 20-F event date |

The diagnostic used installed PyMuPDF 1.27.2.2 and Poppler on CPU, without GPU,
installation or model inference. `diagnostic-run.json`, `build-run.json` and
`render-run.json` record commands, environment and timings. Source evidence and
four review ledgers remain distinct; no stochastic comparison was conducted.

The result invalidates an automatic visible-year interpretation of the hidden
2024 token, not the retained report, the broader research direction or the
source corpus. It triggers preservation and review behavior. The strongest
alternative explanation and limitations are recorded in `author-review.md`.
Full readiness remains **not_ready**; runtime and paid review remain held.

Next independent work: inspect JPMorgan 2025 Note 26, restricted cash and
intercompany funds transfers, together with its stated regulatory dependency.
Do not equate consolidated restricted cash, a dated dividend-capacity figure
or reported parent cash with unrestricted funds available at future payment
dates. The existing Note 33 example and its unresolved factual inputs remain.
