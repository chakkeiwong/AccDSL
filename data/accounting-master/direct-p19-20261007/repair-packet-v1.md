Read-only focused final-disposition review. No tools/edits/commands/agents.
At most 400 words, no tables. End VERDICT: AGREE or VERDICT: REVISE.
Prior translation/numerical/memory and ASBE source reviews returned AGREE with
nonblocking clarifications. Review the FINAL answer wording and the supporting
clauses below. Agreement is only on the bounded negative assessment and these
repairs, never whole-product readiness or domain validity.

Completed repairs: E02 now names propose/commit operations, accepted layer and
enforcement boundary; six real source translations remain author-proposed,
zero human admitted. Their original/extraction hashes and exact Unicode slices
were checked (six records, all pass). E03 begins No. E11 binds exact bounds to
F3; broader interval/aggregate posting and unsupported capability details remain
internal obligations before admission. E12 cites exact sections and limits the
fixture to named outputs/transition. E13 clearly excludes continuous/causal/MCMC
execution from the initial finite/stress profile. None closes E01/E05/E07/E08/E14.

Do not require editing frozen P16/P17 bytes merely to add a cross-reference.
The D3 one-unit sentence is an illustration saying it is not itself proof of
conflict; it declares no universal tolerance. Its component-dependent bound is
not used to admit any real source. Missing spaces in frozen P17 are cosmetic;
current assessment uses normal spacing. No unverified issuer rounding rule.

Final scoped answers:
[
  {
    "id": "P15-E02",
    "question": "How does a narrative reading become a constraint?",
    "proposed_answer": "Evidence E4 defines layer-specific admission; interfaces I2 review.propose@1/review.commit@1 and persistence P4 record actor, rationale, expected view and immutable decision. A constraint query requires accepted interpretation and admitted translation, with resolved predicates or explicit assumptions. The six located Apple translations are proposed; zero are human-admitted.",
    "next_step": "Complete real-package translation and actual admission under E01; retain the specified acceptance/enforcement procedure and every proposed reading separately.",
    "blocks_proposal": false
  },
  {
    "id": "P15-E03",
    "question": "May source preparation infer a half-unit interval from displayed precision when the rounding rule is unknown?",
    "proposed_answer": "No. Display scale alone cannot establish a half-unit interval. P02 nearest-rounding results are conditional assumptions; without an admitted convention or explicit assumption there is no hard interval. Closed enclosures and tie-specific endpoints remain distinct.",
    "next_step": "Preserve source-specific unknowns and admit an issuer convention only on evidence.",
    "blocks_proposal": false
  },
  {
    "id": "P15-E11",
    "question": "Which numerical operations and incomplete outcomes can the initial profile honestly admit?",
    "proposed_answer": "Capability is checked after expansion. The initial affine/finite profile retains exact, partial and unsupported outcomes. Failure F3 requires whole-domain proof/certificate or a checked exact method for exact bounds. Broader numerical methods and posting quantization require their own admitted policy; they are not silent defaults.",
    "next_step": "Execute initial conformance later; finish interval/aggregate posting policy and named unsupported capabilities before any broader numerical extension is admitted.",
    "blocks_proposal": false
  },
  {
    "id": "P15-E12",
    "question": "What entity and economic memory must survive aggregation and extension?",
    "proposed_answer": "History H4, bank B1, insurance I1 and group G1 specify query-scoped economic memory. H4 grouping requires a certificate for the named transitions and outputs; its fixture covers only principal/interest and one stipulated payment transition. DETAIL_UNAVAILABLE preserves missing constituents. No universal grouping algorithm or full domain authority is inferred.",
    "next_step": "Retain actual control/cohort/lot facts and prove each new grouping for its precise query and transition scope.",
    "blocks_proposal": false
  },
  {
    "id": "P15-E13",
    "question": "What scenario and probability claims belong in the initial profile?",
    "proposed_answer": "The initial profile admits exogenous stress and optional finite joint laws. P17 Q3\u2013Q5 specify later Gaussian conditioning, the distinction between observation and intervention, and a forecast evaluation protocol. General MCMC and continuous/causal execution are outside the initial profile and require separate target-specific admission and validation.",
    "next_step": "Gather actual calibration and heldout evidence later; no forecast or causal validity is inferred, and no general sampler becomes a default.",
    "blocks_proposal": false
  }
]

FILE docs/design/proposal/architecture/evidence-contract-v3.md
SHA256 688dab1b7f194eb89abf789c70326463892f41d7893662a8b720300cb393801f
## E4. Narrative interpretation and admission

A narrative interpretation binds subject/entity, contract or instrument set,
valid dates, quantifier, modality (`reported_fact`, `permission`,
`conditional_obligation`, `policy`), predicate, exceptions, dependent facts and
affected quantities. Missing scope is unresolved, not universal. Literal wording
is retained even when no executable predicate is available.

“May repurchase up to 50” permits an action in the specified period and currency;
it imposes neither a purchase nor a payment. A selected scenario may add an
exercise decision and resulting cash flow, separately attributed as an
assumption. “Pays if borrower defaults” preserves the condition; with default
unknown it cannot become an unconditional payable. “Substantially all” supplies
no 95% threshold. A proposed threshold must be a named modelling assumption
and cannot replace the retained qualitative claim.

The source-backed Apple example uses Note 9 of the 2024 10-K (physical page 46, printed page 43),
the fixed-rate debt table and the adjacent swap paragraph. The coupon
classification applies to notes. The paragraph says certain USD notes are
effectively converted to floating rates by swaps; it does not identify each
instrument allocation here. Preserve a combined exposure query as unresolved
pending allocation and terms. Reject a translation stating all combined
note-and-swap cash flows are fixed. The adjacent Note 4 wording “may use” is a
policy/permission description, not evidence that every instrument is hedged.
These passages are compatible qualifications, not a genuine source conflict.

Review events name target ID/version, layer, action, reviewer/time and reason.
At each layer a candidate progresses `proposed -> accepted | rejected |
unresolved`. A new alternative starts at proposed. A correction creates a new
candidate and an explicit supersession link; it does not overwrite source bytes
or retroactively change old review snapshots. Rejected/unresolved candidates
can be reconsidered only by a new recorded decision. Extraction acceptance
means faithful reading; interpretation acceptance means accepted scoped meaning;
accounting admission additionally requires applicable treatment authority,
context and rule/version. No transition automatically accepts a higher layer.

Read-only disclosed-value queries can use accepted extraction and context.
Constraint queries require an accepted interpretation, admitted translation,
resolved predicates or explicit conditional assumptions. Posting requests also
require accounting admission. Dependency corrections invalidate current use of
transitive descendants; old results remain retrievable under their old evidence
view with a current superseded warning. Unrelated descendants stay usable.
The storage transaction and identity mechanics remain a later P16 contract.



FILE docs/design/proposal/architecture/interfaces-contract-v1.md
SHA256 d305133f10e667d402d9357e9597099eb83bd065d8d18c94171f3d0ce60bbb41
## I2. Operation signatures and ownership

In this table each listed input is required unless explicitly marked optional.
Lists are explicit even when empty. Domain records retain the detailed fields
in their named contracts; the table does not replace them with untyped prose.

| Versioned operation | Arguments → payload | Effect and controlling contract |
| --- | --- | --- |
| `source.prepare@1` | package manifest, source snapshot, adapter/config lock, prior review, traversal budget and optional continuation → ExtractionPreparation | Acquires/preserves sources and constructs candidates under extraction-v1; no semantic admission |
| `review.propose@1` | target Ref, layer, decision kind, evidence Refs, actor, rationale, replacement Ref or null → ReviewProposal | Candidate construction; accepts no layer |
| `review.commit@1` | ReviewProposal, expected review view/revision → immutable ReviewDecision and new view | Review transaction under evidence E4/persistence P4; admissible action/layer required |
| `time.select@1` | package/view, investor/system/exploratory mode, cutoffs, revision and unknown-time policy → selected assertions, conflicts and temporal obligations | Pure selection under time T1–T6; no invented ingestion or publication time |
| `model.compile@1` | CompileRequest from L4 → candidate Module, source map, diagnostics and target admission/capability report | Candidate construction; no solver or posting |
| `history.construct@1` | admitted Module, opening, scope, template registry, query/horizon, resource budget → HistoryFamily, partition, witnesses and unresolved formulas | H1–H7; witnesses are examples within the family, not its definition |
| `history.refine@1` | frozen family, additional admitted constraint or refinement, dependency view, budget → child family and inclusion relation | Candidate construction; record whether correction replaces constraints instead of intersecting them |
| `history.query@1` | family, typed joint observable, bound/feasibility request, capability manifest → symbolic/partial/exact answer, coverage and endpoint attainability | Pure; unsupported expressions remain explicit |
| `uncertainty.evaluate@1` | exact native uncertainty request, law/attachment/admission and operation-specific event or observation block → native UncertaintyResult and candidate derived bundle | Native admission/attachment/chaining rules; never selects its result automatically |
| `uncertainty.admit@1` | candidate bundle, target time/evidence/purpose, actor, rationale, requested assumption scope, expected selection revision → admitted attachment and decision | Admission transaction; author-stipulated measures keep that label |
| `uncertainty.select@1` | admitted attachment/receipt, rationale and expected selection revision → new selected-view revision | Selection transaction; no probability recomputation |
| `scenario.project@1` | family, exogenous scenario, policy/method lock, horizon/calendar, explicit information policy, resource budget → conditional event/journal/state proposals by history and scenario | Candidate construction; budgets preserve unresolved regions; no historical-book commit |
| `accounting.assess@1` | native assessment request, event, opening, context/time, authority/method, evidence/assumptions and admissions → TreatmentAssessment | Pure accounting assessment; inherited `assess_only` profile cannot post |
| `accounting.authorize@1` | AccountingEventBasis and posting-profile Ref → PostingAuthorization | Pure evaluation under a separately supported posting profile; an assess-only result cannot grant posting permission |
| `accounting.propose@1` | PostingAuthorization, AccountingEventBasis and posting/rounding method → JournalProposal and independent EconomicDelta | Candidate construction; revalidate bindings; unsupported method gives no journal |
| `accounting.commit@1` | AccountingCommitArguments/v1 and envelope expected branch head/generation → StateTransitionReceipt | Single atomic transaction in P2; schema in cross-contract-amendment-v1, separate from native assess-only |
| `report.build@1` | frozen branch/family result, statement-map version, interval/view, typed requested statements and presentation policy → joint statement family, reconciliation and coverage | Pure; derive from retained state/journals, no balancing plug or hidden branch selection |
| `record.explain@1` | output Ref, its frozen view, requested lineage depth → source/method/assumption/decision paths and unresolved dependencies | Pure; depth truncation is explicit; cannot substitute today's view |
| `work.resume@1` | checkpoint Ref, original semantic manifest, scheduling budget → operation-specific resumed result | Resume the original operation; checkpoint ownership/atomicity in P3; no model change hidden as resume |
| `store.export@1` | snapshot/root Refs, format/decoder, destination → closed manifest or explicit incomplete export | Derivative publication under P3; no domain mutation |
| `store.import@1` | closed manifest, exact blobs/records, decoder and target namespace → import receipt and original-to-local mappings | Verify before metadata transaction; import alone grants no financial admission |
| `store.migrate@1` | migration request from P5 → preserved originals, new representation, comparison/mapping and receipt | Transaction only after required semantic comparisons; no changed-model-as-format claim |

Compilation and history queries may be pure with respect to committed accounting
state while producing immutable candidates in a scratch or candidate store.
Persisting those candidates requires the named owner and receipt. The effect
classification is not a promise that no bytes are written anywhere.



FILE docs/design/proposal/architecture/persistence-contract-v1.md
SHA256 30d4fb6a88821e57329ffb416ad8a76ae883b26c214e02f94e29ae9496d43de4
## P4. Review, correction and invalidation

Source and review requests have their own idempotency namespace
`(operation_kind, workspace_key, request_id)` and fingerprints. A repeated exact
request returns its immutable receipt; changed payload conflicts. A new review
uses an expected prior view and generation. It records reviewer, rationale,
accepted layer, referenced evidence and operation (propose, accept,
accept-alternative, reject or supersede). Legal state transitions follow the
evidence contract. Self-supersession and mismatched replacement scope reject
before mutation. Only review admission records can advance a reading's layer.

A new immutable view records its parent, changed decisions and dependency
selection revisions. It never mutates the old view. Invalidation follows the
reverse dependency graph transitively, including dependencies on candidate-set
membership, not only on the previously chosen members. Therefore adding a newly
eligible filing can stale a selection that formerly had one member. Newly
created descendants must check all ancestors against their requested view;
they cannot escape invalidation by being created after the invalidation scan.
Unrelated dependency closures remain usable. `explain` always uses the output's
frozen view; a current-view query explicitly reports stale dependencies.

A correction to an economic event is a new business event linked to its
predecessor and a specified correction method (reversal/replacement or a dated
adjustment, as applicable). It does not overwrite the original receipt and a
version bump alone does not post it. Corrected historical disclosure creates a
new evidence/model projection; it does not retroactively change what an investor
or the system knew. P17 supplies the accounting treatment of each correction;
missing treatment authority remains unresolved rather than a generic reversal.



FILE docs/design/proposal/architecture/failure-contract-v1.md
SHA256 7a89698262396c12781b2ce74af33734b224b606b41dfa78052c71534ff61aaf
Without an admitted law, return joint feasible regions or per-history conditional
results, never weights derived from witness/branch counts. Interval endpoints
from partial exploration are explored-only. An exact bound must identify the
full formula, proof/certificate or checked exact method, endpoint attainability
and numerical policy. A supremum of 1 for x<1 is not an attained maximum.
Approximate bounds retain method, error description and missing coverage.



FILE docs/design/proposal/architecture/initial-profile-v1.md
SHA256 7bdb16b6e5eac40c296e8fe7a4d38438d5f719853b7c078c2842a0f8fbfb7cbb
Scenario execution initially supports imposed exogenous paths with explicit
behavior and information restrictions. Joint finite rational probability is an
optional extension under the admitted-measure contract. Unweighted alternatives
remain valid initial results. Continuous inference, causal interventions,
calibration and empirically validated forecasts require P17 methods and later
execution evidence. An imposed interest-rate stress does not reweight historical
contract alternatives or become a probability forecast.


H4 exact fixture limit excerpt:


FILE docs/design/proposal/architecture/history-families-contract-v1.md
SHA256 87140fbbbbd9137d792f22ed92e92d274a0a1cf9b2c332f2e743df2d92bcc3bd
## H4. Economic memory, grouping and refinement

A historical accounting balance does not describe all future contractual cash
flows. A principal of 100 with a fixed rate of 5% and a principal of 100 whose
floating rate was 5% can produce the same stipulated historical interest of 5.
If the next full-year rate is 7%, future interest is respectively 5 and 7. A
principal due next year and one due a year later can likewise have identical
current balances but different principal repayments within a one-year query.
The histories must retain rate/reset terms and maturity even when their
historical postings happen to agree. The example establishes arithmetic under
specified simple-interest assumptions, not a recognition or valuation method.

Required state is determined by requested scenarios, horizon and outputs plus
the applicable domain methods. It includes legal entity/perimeter, ownership and
rights, contract/lot/cohort identities, currency, principal/units, recognition
and measurement basis where applicable, rates/resets, schedules/maturities,
options/guarantees/collateral and linked dependencies whenever those affect the
query. “Unknown” is a value status requiring preservation; absence of a field
cannot silently mean no guarantee or no option. Later banks, insurance, groups,
FX, securities and cross-standard methods must extend these state requirements;
a scalar balance schema is not a whole-product substitute.

A grouping request names constituents, transformation/version, retained detail,
scenario domain, horizon, outputs, rules and exact/approximate claim. An exact
certificate must show that aggregation G commutes with every admitted transition
T for that domain, G(T(s,u))=T_group(G(s),u), and that requested outputs satisfy
O(s)=O_group(G(s)). These are proof obligations, not general facts about
financial balances. Missing proof/evaluation returns `GROUPING_UNSUPPORTED`;
it leaves detailed histories available and cannot delete them. A certificate is
part of query/resolution identity, with constituent and rule versions.

For the deliberately narrow simple-interest fixture, two principals 40 and 60
share entity, currency, a fixed 1/20 annual rate, a common day-count convention,
no intermediate principal change, and maturities after the half-year horizon.
Only total principal and interest are requested. Individual interest is
40*(1/20)*(1/2)+60*(1/20)*(1/2)=1+3/2=5/2. Grouping gives
(40+60)*(1/20)*(1/2)=5/2 by distributivity. Principal remains 100 under both
representations; any stipulated interest-payment cash transition subtracts the
same 5/2. This proves the named aggregate outputs/transitions for those
assumptions, not contract-level cash flows or other accounting measurements.
Constituent records remain linked so a later query can refine the group.

A changed output (individual contract exposure), rate/reset/maturity/guarantee
assumption, rule or horizon requires a new sufficiency decision. Reusing the old
certificate returns `RESOLUTION_REVALIDATION_REQUIRED`. Refinement produces a
new resolution version linked to its parent and constituent detail; if the
required detail was never preserved, return `DETAIL_UNAVAILABLE`, not fabricated
lots or contracts. Refinement can restore represented detail, not recover facts
that were never known.

Approximation is a distinct, optional future claim. Its record must name each
output, unit, scenario/horizon domain, absolute/relative tolerance, justification,
error argument or evaluation evidence, and exact-detail fallback. No tolerance,
empirical error bound or approximate grouping is approved by this contract.
Changing the query invalidates the approximation's applicability. Counts of
similar contracts and similarity of old postings are insufficient evidence.


Source follow-up already agreed with two precision suggestions. Final changes: affiliate -> parent-or-subsidiary; the sentence now expressly carries opening adjustments on existing balances through comparative window. No new treatment or numbers. Author inspected the actual first PDF page and confirmed continuous parenthetical clause; text extraction alone caused interleaving.


FILE docs/design/proposal/readiness/asbe-tax-source-repair-v1.md
SHA256 0daf9c7ae09ee72cf6e76b749103151905eb6cddf51c982f971b85924862b387
# ASBE lease tax: recovered primary sources

7 October 2026. This supplements the frozen P17/P18 source status. Their earlier
HTTP 502 records remain true records of those attempts. The Ministry of Finance
ASBE 18 page and the Interpretation 16 issuance page now return 200, and the
issuance page's linked five-page PDF has been retained and read in full.
During session recovery the separate 2018 lease issuance notice also returned
200, together with its linked standard. The earlier failed retrievals remain
preserved alongside these later successful responses.

Exact URLs, retained-file hashes and inspected provisions are recorded in
`sources-20261007/inspection-v1.json`. The ASBE 18 original text is available at
<https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/200806/t20080618_46230.htm>;
Interpretation 16 and its operative attachment are linked from
<https://kjs.mof.gov.cn/gongzuotongzhi/202212/t20221212_3857395.htm>.

## Exact source and applicability findings

The official ASBE 18 page is titled 企业会计准则第18号——所得税 and gives a
publication date of 9 March 2006. The 2008 directory in its URL is not an
effective-date finding, and the site's template date is not the publication
date. Its original text must be read with subsequent interpretations; it is
not a consolidated statement of every amendment through 2026.

Articles 4–9 define carrying amounts, tax bases and taxable/deductible temporary
differences. Articles 11 and 13 contain the original initial-recognition
exceptions. Article 13 limits recognition of a deferred tax asset to the
probable taxable profit available for use of the deduction. Articles 16–20
specify current/deferred tax measurement, applicable rates, recovery/settlement
method, no discounting and subsequent review. Articles 21–23 address allocation
to profit/equity and separate noncurrent presentation. These provisions were
inspected in the retained Chinese text, not inferred from an IFRS comparison.

The Interpretation 16 notice is 财会〔2022〕31号, signed 30 November 2022 and
published on its webpage on 13 December 2022. Its attached PDF is the operative
interpretation text. The number and signing/publication dates are verified from
the retained issuance webpage; they are not printed in the attachment. The PDF
text extraction interleaves part of the parenthetical definition on page 1;
the original PDF preserves the continuous clause. Section I(a), physical page 1, excludes a qualifying single
transaction from ASBE 18 articles 11(2) and 13's initial-recognition exemption
when it is not a business combination, affects neither accounting profit nor
taxable income/loss initially, and creates equal taxable and deductible temporary
differences. The examples expressly include a lessee's initial lease liability
and right-of-use asset, and an asset with a decommissioning obligation.
Corresponding deferred tax liabilities and assets are recognized separately
under the applicable income-tax provisions. Equal asset/liability carrying
amounts alone are not the test, and asset recoverability is still required.

Section I(b), physical page 2, requires adjustment of qualifying transactions
between the earliest comparative opening and application. For qualifying
existing balances at that opening, cumulative effects adjust opening retained
earnings and the relevant financial-statement items. Related disclosure is
required. Early application is allowed from the year of issuance with disclosure.
Section IV, physical page 5, makes Section I effective on 1 January 2023.
Sections II and III have different effective and transition provisions; the
lease-tax date must not be copied to those other treatments.

The remaining PDF sections were read to distinguish those boundaries: Section II
concerns income tax on dividends from instruments classified as equity, and
Section III concerns modifications from cash-settled to equity-settled
share-based payments. This supplement does not introduce implementations of
either method.

## Lease adoption dates recovered during continuation

The [2018 issuance notice](https://kjs.mof.gov.cn/zhengcefabu/201812/t20181213_3092629.htm)
is 财会〔2018〕35号, signed 7 December 2018 and published on the webpage on
14 December 2018. Its URL contains 13 December; the printed publication date
controls that metadata. Paragraph I requires application from 1 January 2019
for enterprises listed both domestically and overseas, and overseas-listed
enterprises preparing financial statements under IFRS or ASBE. Other enterprises
applying ASBE must apply the revised standard from 1 January 2021.

Paragraph II permits early application for enterprises whose parent or subsidiary
is listed overseas and prepares its overseas statements under IFRS or ASBE. That
early date cannot precede their simultaneous application of the specified 2017
financial-instruments and revenue standards. Paragraph III discontinues the 2006
lease standard and its application guidance when an enterprise applies the
revision. Thus article 68's general 2019 date does not establish every entity's
mandatory adoption date.

The notice's linked `P020181213596772599039.doc` is an OOXML ZIP despite its
`.doc` suffix. The original bytes and derived paragraph text are retained.
Inspected articles 1–8, 14–18, 20–23, 25–33 and 60–68 support the lessee scope,
recognition, measurement, modification and transition findings used here.
Automatic list labels in the Word document are not reproduced by the text
extractor; the original document and the earlier official HTML remain available.
Article 61 permits retrospective transition or adjustment of opening retained
earnings without comparative restatement, subject to its detailed conditions.
Neither route may be assigned to an actual issuer without its election evidence.

For an otherwise qualifying ASBE enterprise in the second group, a 2020
reporting date alone does not establish mandatory use of the revised lease
standard; verified early adoption satisfying paragraph II's parent-or-subsidiary and
concurrent-standards conditions would be needed. The same enterprise falls
within mandatory application from 2021. This is a source-backed selection
example, not a claim that any particular company belongs to that group.

## Consequences for the existing lease case

Keep the previously reviewed synthetic assumptions: initial lease liability
and ROU asset 210, two annual payments of 121, discount rate 10%, two-year
straight-line depreciation, tax deductions allocated to the liability, zero
tax bases, tax rate 25%, and sufficient taxable profit satisfying the DTA
recognition condition. The primary sources now support the exception analysis
for a qualifying ASBE case to which Section I applies from 1 January 2023;
the tax law and entity facts remain
explicit assumptions.

At commencement, taxable ROU difference 210 gives DTL 52.5; deductible liability
difference 210 gives DTA 52.5. Recognize debit DTA 52.5 / credit DTL 52.5. At the
first annual close, liability 110 and ROU 105 give DTA 27.5 and DTL 26.25.
The DTA reduction of 25 is deferred expense and the DTL reduction of 26.25 is
deferred benefit: net benefit 1.25. Both reverse by expiry. These are the same
amounts already checked in P17 and rendered on P18 physical page 63.

These are gross recognition and measurement amounts. Whether deferred tax
assets and liabilities may be offset on an actual balance sheet requires the
applicable presentation provisions and entity/tax-authority facts. Article 23's
noncurrent classification and Section I's separate recognition do not alone
settle that offset question. The transition illustration below displays gross
amounts to expose the adjustment; it does not determine an issuer's net display.

For a separate transition illustration, assume the earliest comparative opening
has cash 500, ROU 105, lease liability 110 and equity 495, with no recognized
deferred tax. Assume the same illustrative tax bases, rate and recoverability.
Recognition adds DTA 27.5, DTL 26.25 and opening retained earnings 1.25.
Assets become 632.5; liabilities 136.25 plus equity 496.25 also equal 632.5.
This demonstrates the opening-equity route; it is not a new current-period tax
expense or a rewrite of the original disclosure. Actual adoption dates and
comparative periods must be supplied by the entity.

Section I(b) also requires adjusting the qualifying transactions within the
comparative window and carrying the opening adjustments on existing balances
through that window. In this transition illustration, if the comparative year
contains the remaining lease year, DTA 27.5 and DTL 26.25 both reverse by expiry,
giving comparative deferred tax expense 1.25. The opening adjustment alone is
therefore not a complete transition statement. Section III's instruction not to
adjust comparative information applies to its different share-payment topic and
must not be imported into Section I.

Applying the old exemption to set both deferred balances to zero in the
qualifying post-2023 example is wrong relative to Interpretation 16 Section I.
It preserves the initial net equity by accident while omitting required gross
balances and the later 1.25 deferred benefit. Conversely, automatically creating
equal deferred balances whenever a lease has equal carrying amounts is also
wrong: the temporary differences, qualifying conditions and DTA recognition
criteria have to be established. Unknown tax deductions or recoverability
produce an unresolved assessment, not assumed eligibility.

## Decision and limits

| Decision | Primary criterion | Veto status | Main uncertainty | Next action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Recover ASBE 18/Interpretation 16 and the ASBE 21 issuance schedule | Official texts, exact provisions and effective/transition rules are retained and inspected | No source/title/content mismatch; historical failed requests retained | Full later amendment census, actual tax law, entity adoption, offset eligibility and recoverability remain unverified | Review this supplement, then incorporate its dated source correction in the next manuscript revision | Whole ASBE/current-2026 compliance, complete authority coverage or E07 closure |

The strongest competing reading applies the original ASBE 18 initial exemption
without Interpretation 16. Section I expressly excludes the qualifying case
from that exemption, so that reading is rejected for the stated target period
and facts. A later applicable amendment, a nonqualifying transaction, different
tax bases, or unavailable recoverable taxable profit would change the answer.
The source retrieval narrows E07; US, ASBE sector and other authority work remain
internal. No paid review is required to identify or repair this source gap.
