# Insurance authority and the limits of premium allocation

8 October 2026. Direct continuation under C05/C08, addressing E07 and
MC11/16/19/22/28/30/32–35, with G4/G7/G8/G10/G16 implications. This bounded
unit continues the proposal; full readiness remains `not_ready`.

## Question, baseline and intended result

Does the official ASBE 25 text support the distinction already made in the
insurance method between eligibility for the premium allocation approach (PAA)
and measurement of claims already incurred? Which adoption dates and entity
conditions govern that comparison? The comparator is the retained December
2022 AASB 17 compilation, specifically recognition, PAA and incurred-claim
provisions, not an assumed universal current IFRS rule.

Baseline: `docs/design/proposal/methods/insurance-methods-v1.md`, retained
`docs/design/research/standards/aasb17.pdf` and `.txt`, and the 128-page Version
2.4 at `docs/design/proposal/manuscript-authority-20261008/`. Existing general
measurement, PAA/reinsurance, discount and onerous examples stay protected.
The official Ministry index retained in the previous unit identifies
`https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/202202/t20220224_3790240.htm`.
No ASBE 25 technical text was found in the targeted retained source search.

Produce an exact source/adoption map and one independently reconstructible
conditional PAA consequence. A possible discriminating case is one-year
coverage with a claim paid two years after it is incurred: short coverage need
not justify ignoring discounting on the claim liability. Final assumptions
must follow inspection of the operative passages. This is a deterministic
specification example, not an insurer estimate or statistical comparison.

## Skeptical audit and assumptions

The plan passes the pre-execution audit with the following limits. A Ministry
page date is not an adoption date; a standard number is not an edition; AASB
17 is a dated comparator, not proof of universal jurisdictional applicability.
PAA eligibility, premium/service financing and claim-settlement discounting
are separate questions. The source map must preserve these distinctions.
Counts, HTTP success, balanced journals and a clean PDF build are explanatory
checks, not evidence of entity applicability or whole-domain readiness.

| Material choice | Provenance and status | Risk and earliest check |
| --- | --- | --- |
| ASBE 25 official Ministry lead | Retained Ministry index; source-retrieval hypothesis | Page may contain a notice, old text or missing attachment; inspect title, document number, body and attachments before quoting |
| December 2022 AASB 17 | Existing locally retained comparator, not promoted as current worldwide law | Amendments/jurisdiction can differ; record compilation and inspected paragraphs explicitly |
| One-year coverage / longer settlement | Proposed synthetic counterexample | Coverage, premium financing and settlement tests could be conflated; independently map each to its source condition |
| Simple cash flows, flat rate and authored risk adjustment | Convenience inputs for exact arithmetic only | Could be mistaken for actuarial calibration or market evidence; label them and retain missing entity evidence |
| Internal author inspection | MC35 preparation, not human acceptance | Model review can miss a source or prose error; preserve exact anchors, arithmetic, rendered pages and pending independent acceptance |

No candidate ranking, default numerical policy, product implementation or
stochastic experiment is proposed. A result cannot establish full IFRS/ASBE
equivalence, accounting compliance, current amendments, actual entity adoption,
actuarial calibration, general VFA/transition support or full E07 closure.

## Evidence contract and stopping rules

Primary unit criterion: locally retained official provisions with exact Chinese
anchors and labelled English interpretations; adoption conditions separated
from source/publication dates; and a checked source-to-calculation-to-journal
example whose assumptions a reviewer can reconstruct. If the finding changes
or substantiates the manuscript, integrate it into a separate Version 2.5,
preserving prior mathematics, citations and qualifications.

| Diagnostic | Role and action |
| --- | --- |
| Wrong source/edition, unsupported translation or missing applicability term | Promotion veto and repair trigger; withhold the affected claim |
| Corrupt baseline, source identity mismatch or arithmetic inconsistency | Continuation veto for dependent work; repair before proceeding |
| Bounded failed source access | Stop that route and record the failure; continue independent retained-source work |
| PDF/check counts, successful retrieval or journal balance | Explanatory only; no substantive readiness conclusion |
| Missing human or independent review | Acceptance remains pending; internal preparation continues |

At most eight distinct requested URLs, two attempts per exact route, a
30-second total timeout per request and up to two justified alternative routes
for a blocked source. Run trusted retries after sandbox network failure. Stop
the unit when source disposition, consequence, necessary manuscript repair,
verification, result and next plan are recorded; do not drift into a general
insurance campaign. Newly discovered amendment/transition work becomes an
explicit next unit. The expected failure is a scope or applicability gap; it
does not invalidate the research direction.

## Execution and preservation

1. Create `data/accounting-master/insurance-authority-20261008/`, save exact
   current-pointer bytes and baseline hashes, and record the existing Git HEAD.
2. Inspect retained AASB 17 passages and acquire the official ASBE 25 page and
   identified technical attachment/issuance text with bounded `curl` requests.
   Record URL, timestamps, command, HTTP/exit status, byte hashes and failures.
3. Extract/inspect the relevant complete provisions and their definitions,
   exceptions and adoption schedule. Use Python standard-library `Fraction`
   arithmetic for the worked consequence and check source anchors and journals.
4. If warranted, copy only manuscript source inputs to
   `docs/design/proposal/manuscript-insurance-20261008/`. Edit the insurance
   explanation, needed cross-reference, bibliography and version label only.
   Use `latexmk -lualatex -interaction=nonstopmode -halt-on-error
   accounting-product-proposal.tex` in that directory; retain the build output.
5. Inspect changed and adjacent rendered pages plus title/contents and added
   bibliography entries. Record source fidelity, mathematics, presentation and
   comprehension separately. Use the scholarly surface audit as a diagnostic,
   not a readability verdict. Verify protected evidence without rewriting it.
6. Write the result/decision table and run manifest; only then advance current
   checkpoint, next plan, requirements supplement and current roadmap. Preserve
   their earlier bytes before editing, including the previously unbound roadmap.

Environment: existing Python 3, BeautifulSoup, PyMuPDF and LaTeX utilities;
ordinary CPU document/arithmetic work, no GPU/framework imports or package
installation. Save actual commands and wall time in the unit manifest.
Research data and random seed: N/A, deterministic authored case. No controller
restart, outreach, fees or publication.

## Bounded manuscript repair

Reader: accounting modellers and implementers who know the existing LRC/LIC
distinction. They should be able to explain why one-year coverage may permit
PAA while a long-tail claim still requires discounted fulfilment cash flows,
and identify the facts needed to apply the dated ASBE text. Inspect the
insurance chapter and immediate transitions in the protected PDF before
editing. Do not rebuild the frozen Version 2.4 in place.

The argument moves from coverage-versus-settlement timing to the two source
conditions, then a concrete liability and journal consequence, followed by
the remaining authority/applicability limits. Preserve previous examples;
this is a bounded insurance repair, not a whole-document readability review.
Reader questions: what does PAA simplify; which one-year tests apply to which
amounts; what cash flow and risk adjustment enter the incurred claim; what
would the undiscounted shortcut change; and what does the dated comparison
leave unestablished? Add a concrete confusion map after reading the baseline.

Pre-mortem: a clean result could mislead by attaching the right arithmetic to
the wrong legal edition, treating short coverage as short settlement, omitting
the risk adjustment, or equating a synthetic rate with market evidence. Exact
source conditions and separately stated authored inputs are the cheapest checks.
