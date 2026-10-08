# Apple inventory, fixed assets and cash-flow reconstruction

8 October 2026. Direct E01/C03/C08 continuation; MC01–05/07–12/15–16/28/30/
32–35 and G1/G4/G5/G11/G13/G15/G16. Baseline: the closed 137-page Version 2.8
and its commitments result. Proposal readiness remains `not_ready`; product
implementation and the historical controller remain held.

## Question and evidence contract

What do the retained annual/interim inventory, PP&E and cash-flow disclosures
identify about asset movements, and what histories remain unresolved? Extend
A09/I06 by reading complete annual Note 5 and interim Note 5, the FIFO and
straight-line policy paragraphs, fiscal/basis context, corresponding balance-
sheet rows and cash-flow reconciliation/capital-payment rows. Use annual
Note 8's already inspected noncash/ROU classification only as a linked dependency.
This declared population does not cover every cash-flow transaction or note.

The exact comparator is Version 2.8 plus the explicit shortcuts: inventory
cash-flow adjustment equals minus balance change; capital payments equal gross
asset additions; accumulated-depreciation change equals depreciation; total
depreciation/amortisation equals PP&E depreciation. Test their implications
against the reported scopes and a stated asset-book identity, not against a
forecast score. No tuned-method or stochastic ranking is involved.

Primary pass criterion: faithful source/context mapping for the whole declared
note population; checked row/component and cross-statement consequences;
explicit identification of which shortcut or conjunction fails; feasible
conditional repair histories without inventing actual asset cohorts. Invalid
source/sign/scale/date, invented residual cause, negative retired carrying
amount under the chosen nonnegative-cost model, or unlabelled assumptions veto
the dependent claim. A failed shortcut triggers the planned repair, not a stop
to the research direction. Corrupt evidence or invalid identities stop dependent
work until repaired. Counts and PDF build success are explanatory only.

Artifacts: `data/accounting-master/apple-assets-20261008/` and separate candidate
`docs/design/proposal/manuscript-assets-20261008/`. No actual purchase/cash
reconstruction, full ASC authority, all-history completeness, calibrated
forecast, probability law, full filing semantics or independent acceptance
will be claimed. No network or paid referral is planned.

## Skeptical audit and intent ledger

Source screening confirms that quarterly inventories move from 7,286 to 6,911
million while the indirect cash-flow adjustment is +215. These have different
targets, not an established source conflict. Annual PP&E-specific depreciation
is reported as 8.2 billion, whereas cash-flow depreciation/amortisation is
11,445 million. Neither the broad line nor the change in accumulated
depreciation can silently replace the asset-specific expense.

For the annual illustration define gross cost G, accumulated depreciation B
as a positive contra balance, additions A, cost retired R, depreciation d and
accumulated depreciation removed S. With no other movements, G1=G0+A−R and
B1=B0+d−S. Nonnegative retired carrying amount requires 0<=S<=R. First test
the conjunction A=capital payments, d=displayed PP&E expense, and no other
movements. If it fails, do not infer which omitted movement actually occurred.
Then allow unpaid additions and construct two feasible books with different
retirement amounts but the same selected source endpoints/expense/cash. This
tests non-identification within a declared model, not actual Apple histories.

The plan passes after separating all four measurement shortcuts, retaining
rounding as an assumption, and requiring an asset-book feasibility check before
prose. Expected shortcut rejection is a repair trigger. The decisive artifact
is the source-bound calculation with explicit counterexamples, not a larger
table count. Missing actual contract/cohort facts limit promotion but do not
veto this bounded documentary continuation.

## Default and assumption audit

| Choice / provenance | Status and reason | Failure mode / earliest diagnostic |
| --- | --- | --- |
| Existing annual PDF/interim HTML, A09/I06 | Pinned case evidence, not representative sampling | Mismatched periods/columns: original tables and repeated September comparative checks |
| Complete two Note 5 spans plus named dependencies | Bounded source population | A stock-only reading misses cash/expense distinctions: inspect cash-flow headings and note-specific depreciation |
| USD millions; annual depreciation 8.2bn converted to 8,200 | Reported scale plus explicit conversion | False precision: point illustration and optional conditional nearest-rounding envelope |
| Nearest rounding to displayed unit, if used | Sensitivity hypothesis; issuer policy unverified | Claiming exact unrounded bounds: label outer enclosure and leave tie rule open |
| No FX/reclassifications/impairment or other movements in asset witness | Authored minimal model to test identifiability | Misstated issuer history: source populations and omissions stated before equations; do not fit all statements by a plug |
| Unpaid additions, zero disposal proceeds, full-year expense 8,200 | Authored repair assumptions, not findings | Unsupported causal attribution: show two books and state that neither is identified |
| Retired gross costs 6,000 and 7,000, if feasible | Convenience witnesses above required removed depreciation, not estimates or priors | Negative carrying amount: check 0<=S<=R and all journal/statement effects |
| Existing CPU Python, HTML/PDF tools and LuaLaTeX | Convenience environment, no installs | Extraction/render mismatch: inspect retained originals and candidate; GPU intentionally hidden in helpers |

## Execution and reader integration

1. Save four live pointers and hash the prior closed unit/candidate, original
   sources and relevant prior dependency. Verify prior manifest using saved
   pointer paths; preserve existing dirty work and Git state.
2. Partition the two full notes; capture exact dependency spans/table locators
   and dates/scales. Inspect annual PDF and retained interim HTML, including
   a clearly labelled derived print view if useful. Record unknowns and query
   consequences independently of extraction coverage.
3. Check sums, net/gross/contra relations, duplicate comparatives and cash-flow
   signs. Compute inventory residuals without assigning their cause. Test the
   minimal annual asset book; when it fails, validate two repair histories,
   nonnegative retirement carrying amounts, debits/credits and statement effects.
4. Integrate Version 2.9 where the reader already knows inventory and fixed-
   asset methods: a new included section in Chapter 9 before lease/tax
   integration, with a short cross-reference from source admission in Chapter 3.
   Preserve the entire earlier Apple chapter and all prior math/citations.
5. Build with `latexmk -lualatex -interaction=nonstopmode -halt-on-error
   accounting-product-proposal.tex`. Inspect title/contents, the new/adjacent
   Chapter 9 pages and the changed Chapter 3 transition. Check preservation and
   surface diagnostics; preserve superseded build evidence if repair is needed.
6. Record result, decision/uncertainty, author review, manifest and next action.
   Update four live records, retaining all five E workstreams, MC/G requirements,
   forty exhibit targets and 136 unverified publication dates. Stop this unit
   at checked integration; broader proposal acceptance remains pending.

Use `CUDA_VISIBLE_DEVICES=-1 python3` for helpers. No seeds or GPU/ML settings
apply. Run manifest includes actual commands, source versions, Git commit,
environment, elapsed interval and output hashes. A source/calculation defect
gets a focused repair; no unrelated test or controller campaign is planned.

The intended reader is an accounting-system designer who understands the
preceding lot and depreciation examples. The new section asks why those
methods cannot be populated from reported totals alone. The narrative moves
from inventory balance versus indirect cash adjustment, to three dated asset
measurements, to the failed cash-equals-additions book and feasible repairs.
This fills a missing bridge in Chapter 9 rather than extending the opening
case chapter indefinitely. Baseline pages 27 and 68–69 are the relevant entry
and exit transitions; the final bounded page set is determined after build.

Cold-reader questions: What does +215 measure? Why is the 375 change different?
Which depreciation figure belongs to PP&E, and what precision does it have?
Which assumptions jointly force an impossible retirement? What do unpaid
additions repair, and why are they not a finding about Apple? What lot/cohort,
payment and accounting facts remain needed for a future query?

Pre-mortem: the run could pass while assigning the residual to FX without
evidence, borrowing a later quarter as part of the preceding fiscal year,
using rounded depreciation as exact, or treating two constructed books as all
histories. Check those distinctions before drafting. Author answers and clean
rendering cannot establish independent/human comprehension; that remains pending.
