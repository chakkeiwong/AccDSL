# Connected-design inspection against Version 2.93

15 October 2026. Work in progress under the convergence-audit plan. These
findings distinguish inspected support from remaining specification work; they
do not replace the frozen Version 2.72 assessment or promote the candidate.

## CA01 — Corporate exchange closure is still missing

The Northstar company is already a substantive synthetic financial case. The
initial profile gives a continuous shared debt fraction, complete conditional
statements and a changed-rate control. IX01–IX06 preserve the corresponding
financial consequences, unavailable collection input, information cutoff,
overlapping classifications and unavailable insurance method. Their
`inputs`/`expected` objects are concise semantic examples, however; they are
not the required complete OperationRequest/OperationResult closures.

Inspected: `architecture/initial-profile-v1.md`, acceptance examples 1–6;
`architecture/interfaces-contract-v1.md`, I1–I5;
`architecture/language-ir-contract-v1.md`, L1–L4;
`architecture/platform-contract-examples-v1.json`, IX01–IX06;
current manuscript chapter 17 and `sections/operations-storage.tex`. Paths
are relative to `docs/design/proposal/` unless stated otherwise.

I1 closes the common envelope but I2 lists many argument/domain records by
meaning rather than defining their exact tagged wire fields. Chapter 17
repeats that descriptive registry. Core 0's schema does not define the new
portable profile. The exact state-only, reserving-adapter and insurance-atomic
schemas are scoped supplements, not a definition of Northstar's full workflow.
This is a specification gap affecting MC24/25/28, G2/G5/G9/G18 and the profile's
six acceptance cases. It cannot be deferred as runtime testing.

Repair completion requires an explicitly versioned corporate operation schema,
exact required record/byte closure, connected valid and adverse exchanges,
independent financial expectations, and integration into a protected successor.
The existing descriptive registry and historical examples must remain intact.
Do not claim every platform operation complete from one repaired subset.

## CA02 — Historical routing must not erase delivered evidence

The initial profile still describes E05's real-source conflict and Apple
preparation as pending in terms that predate later supplements. The history
contract H2 likewise says E05 lacks a qualifying real-source conflict. Current
P17-03 has a source-backed navigation conflict with review/invalidation
consequences, and P17-02 has an expanded package disposition. Preserve these
historical contracts; the successor audit and live routing must credit that
evidence while separately assessing the connected real-package requirement.

## CA03 — Financing and group connections have real delivered content

The acquisition/translation/disposal case uses the same group throughout:
EUR16 goodwill is translated to USD20.8; parent/NCI translation reserves are
10.4/2.2; full versus retained disposal gives different cash but the same
353.8 equity. The source/date/rights conditions remain explicit. The supporting
result also records the repaired event order, which prevents intermediate
negative inventory. Inspecting final equity alone would miss that error.

Trace: historical IFRS3/IFRS10/IAS21/IAS7 support and supplied rights/dates →
conditional control/perimeter → acquisition and translated joint state → full
or retained disposal event → adjustment journals and NCI/reserve removal →
cash/profit/OCI/equity. These consequences are delivered. Exact common portable
group records/recovery remain less complete than insurance's transaction
example; no schema or actual company valuation follows from the arithmetic.
Financing also has EPS timing/dilution and the later coupon/carrying-value
correction. Remaining hedge/benchmark and changed-option scope must receive a
finite method disposition, not another claim that basic financing is absent.

Evidence: P17-05/group-fx-disposal/result.md, P17-05/operation-matrix.md,
P17-05/eps-lifecycle/result.md and P17-08/sector-revision/result.md beneath
data/accounting-master/p17-completion-20261014/.

## CA04 — Bank accounting, prudential and information targets differ

Trace A: historical AASB commitment terms and supplied risk findings → original
commitment baseline → draw/lapse → provision-to-allowance transfer → funded
allowance4/equity16. The revision supplement checks unknown original risk,
later restoration, public-byte timing, system review and candidate membership.
It does not infer SICR from doubling a probability or reset risk at draw.

Trace B is a separate conditional US book, not a continuation of Trace A.
Frozen rule support plus supplied CECL/stock eligibility → same-bank monetary
events and profit2.4 → accounting equity23.6 → deductions/cap ordering →
CET1/Tier1 21.6, total capital23.1 and RWA119.1. A separate average145 supplies
leverage. Runoff40 leaves9 unpaid despite unchanged capital ratios. A capital
assessment does not post journals or authorize dividends. Missing operative
actual-date evidence blocks real compliance, not this restricted calculation.

Common time/review/reuse behavior is specified through semantic traces; most
are not complete new portable encodings. Required bank operation fields and
remaining restructuring/funding scope still need explicit disposition. Actual
calibration and runtime fault behavior are separate later evidence.

Evidence: P17-06/commitment-draw/result.md, prudential-connection/result.md,
operation-matrix.md and architecture/sector-evidence-revision-20261014.md.

## CA05 — Insurance transaction closure is the strongest reuse example

Trace: historical AASB17 method and authored terms → separately eligible A/B/R
groups → timely versus late treaty histories → information-time admission →
finance/service/incurrence/settlement events → independently bound component
and journal changes → year-one cash173/equity83 in the timely case → exact
replay, changed-payload conflict and both lost-acknowledgement worlds.

The component is not another liability. A balanced extra component entry is
rejected. Late treaty gives year-one equity74.75 even though terminal cash88.3
matches: terminal-cash grouping loses service memory. Unknown treaty order is
unresolved, not implicitly timely. The atomic specification supplies 27 exact
exchanges, 274 records and 22 blobs; runtime isolation/durability is untested.
Reserving's 18 exchanges separately preserve process-law identity, zero versus
missing and incomplete draws. Neither case supplies a priced VFA guarantee,
complete acquisition/reinsurance combination or target-specific calibration.

Evidence: P17-07/connected-groups/result.md, operation-matrix.md,
P17-10/insurance-atomic/result.md, record-schemas.json and
P17-10/reserving-adapter/result.md; architecture/query-resolution-supplement-
20261014.md and sector-evidence-revision-20261014.md.

## CA06 — Real-case completion must preserve the actual target

Apple's annual/interim statement networks and full declared package dispositions
already exist. Later comparative segment detail is a later-information source,
not automatically an accounting correction or earlier available bytes. The
coupled history transformation is conditional on a feasible company remainder;
matching all 102 displayed rows does not construct that remainder. Conversely,
the requirement does not demand uniquely known private transactions.

The missing design deliverable is one connected result whose target layer,
support, conditional alternatives, affected statements, missing constraints,
temporal limits and obligations are explicit. The result may honestly remain
partial. A partial answer can satisfy specified behavior without proving the
actual issuer history complete; the source/case acceptance remains separately
judged. JPMorgan supplies its own actual contradiction and review example. Do
not silently insert that contradiction into Apple's source history.

Evidence: P17-02/result.md and connected-package-map.json, P17-03/result.md,
current chapter13 and sections/source-admission.tex.

## Decision table

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
|---|---|---|---|---|---|
| Credit delivered cases | Located same-history financial and review consequences | No inspected basis for calling these absent | Full common-wire scope and final review | Preserve and connect them | Whole mission closure |
| Repair corporate closure first | Initial profile requires exact connected exchanges | Descriptive argument registries are insufficient | Exact record boundaries and reuse | R01 in repair-queue.md | New runtime permission |
| Retain real-case conditional limits | Target layer and unknown dependencies must agree | Absolute feasible issuer-history claim remains unsupported | Private facts and exact public-byte timing | R02's complete partial-result specification | A unique actual history |
| Continue remaining methods | Existing matrices name consequential scope gaps | Missing support vetoes the affected method only | Operative sources and facts | Finite R03 method decisions | Rejection of the overall direction |

## Inspection boundary

No claim of global schema absence is made merely from filenames. The new
ledger records evidence locations and hashes for all53 obligations. These are
documentary interaction findings, not engine execution or independent acceptance.
No engine, benchmark, external review, source acquisition or Git mutation ran.
