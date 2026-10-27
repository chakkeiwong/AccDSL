# P08 authority and corporate methods result

The bounded P08 implementation covers an Australian for-profit Tier 1 issuer
compound convertible bond under the retained 31 December 2022 AASB
compilations. It recognises the issue, separates the liability and residual
conversion equity, accrues effective interest, pays two annual coupons, and
settles at maturity by either cash redemption or fixed-share conversion. Exact
`Fraction` arithmetic, atomic state transitions, journal balancing, and note
roll-forwards are implemented in [corporate_financing_v1.py](../../../../scripts/corporate_financing_v1.py).

## Supported operation

The supported contract is synthetic and deliberately narrow. The issuer is a
party to the contract at issue; proceeds equal whole-instrument fair value; the
conversion right exchanges a fixed number of ordinary shares for a fixed cash
amount; the instrument is non-puttable and convertible only at maturity; the
functional and presentation currencies are AUD; and the ordinary liability is
measured at amortised cost. Issue dates are 1 January, coupons are 31 December,
and all rates and amounts are exact rational inputs. Fees, taxes, derivatives,
options, early repurchase, modification, default, foreign currency, and
consolidation are rejected before state mutation.

At issue, the engine debits cash for proceeds, credits the liability for the
present value of coupons and principal at the supplied comparable
non-convertible yield, and credits residual conversion equity. Each period
credits the liability and debits interest expense at the opening carrying amount
times the exact effective yield, then debits the liability and credits cash for
the coupon. Cash redemption debits the liability and credits cash. Maturity
conversion debits the liability and credits share equity for principal, increases
the issued-share count, and leaves the original conversion equity within equity.
The sign convention is `postings_debit_positive`; every journal and total state
must sum to zero. Selected carrying-amount and effective-interest note rows link
to `note_carrying`, `measurement`, `note_interest`, and `interest` in the
authority register. They are not a complete financial-instrument disclosure.

The default two-period case has principal and proceeds 100, coupon 5, and
comparable yield 10%. The independent present-value calculation gives initial
liability `11050/121` and residual conversion equity `1050/121`. Total effective
interest is `2260/121`. After coupons, redemption leaves cash 10; conversion
leaves cash 110 and issues ten shares. A second case with principal 240,
proceeds 245, coupon 12, yield `2/25`, and 24 shares is also parameterised and
reconciled. The full dated journals, state snapshots, notes, and formulas are in
[authority-and-methods.json](authority-and-methods.json).

## Authority and jurisdiction limits

[authority-and-methods.json](authority-and-methods.json) links every claimed
paragraph to retained bytes and a SHA-256 hash in
`docs/design/research/p08-v1/authority-register.json`. The inspected sources
are AASB 132 paragraphs 22, 22A, 25–27, 28–32, 35, and AG30–AG35; AASB 9
paragraphs 3.1.1, 3.3.1–3.3.3, 4.2.1, 5.1.1, and the Appendix A definitions
of amortised cost and effective interest; and AASB 7 paragraphs 7, 8(g), and
20(b). Their common compilation applies to annual periods beginning on or after
2023-01-01 and before 2026-07-01. The register records the jurisdiction,
for-profit entity scope, Tier 1 basis, retrieval paths, inspected page anchors,
quotes, and transition limits. The source register is the authority boundary;
the implementation does not turn Australian adoption into universal IFRS
authority.

The official FASB storage route returned ASU 2020-06 on 3 October 2026.
The retained amendment notice reproduces ASC 470-20-25-12/13: a convertible
instrument is a single liability unless embedded-derivative separation or the
substantial-premium rule applies. That conditional classification differs from
the AASB residual-equity split. PDF page 40 was visually checked because its
plain text combines deleted and inserted words. ASC 815-40-65-1(a) gives
mandatory adoption after 15 December 2021 for specified SEC filers and after
15 December 2023 for other entities; paragraph (b) gives the transition choices.
Selected ASC 815-15-25-15 language describes the conventional-convertible
exception but cross-references provisions that are not reproduced in full.

The ASU expressly says it is not itself authoritative: it communicates changes
to the authoritative Codification. Complete applicable ASC eligibility, general
debt measurement and extinguishment, and subsequent amendment applicability
remain uninspected. The source preparation record names those dependencies.
Consequently the complete US lifecycle comparison remains unresolved. The two
Ministry of Finance routes returned 502 errors; earlier EUR-Lex requests returned empty 202 responses. The original EU regulation
and four amendment texts were subsequently retained. Later v4–v5 inspections recovered the amendment/corrigendum texts. The last Portuguese scope correction is now retained in `docs/design/research/p08-v6`; its wording affects recitals 7/9 and Article 2, not Article 4. A reviewed current applicability profile and actual EU lifecycle implementation remain necessary. Historical requests
remain preserved alongside the new sources.

Comparison hashes now derive from common economic facts, including funding,
entity scope, currency and both settlement outcomes. The AASB row contains both
fully replayable lifecycles. Other rows retain null results; the conditional
FASB classification finding does not establish a full numerical comparison.
No company practice substitutes for missing primary authority.

The retained ACTUS technical specification was inspected only for dated events,
state variables, and payoff functions. Integration is deferred; no ACTUS
algorithm, official code equivalence, behavioural parameter, or forecast claim
is adopted.

This engineering result does not establish professional accounting validity,
empirical forecast validity, or human acceptance.

## Decision table

| Decision | Primary criterion | Veto diagnostics | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Implement the bounded AASB issuer slice; leave the cross-standard comparison criterion incomplete | Inspected source anchors plus independent PV, cash-flow, journal, state, note, rejection, and matched-fact checks | Source hash/anchor failure, period or jurisdiction mismatch, unsupported term, chronology error, imbalance, negative funding, or note roll-forward mismatch | Synthetic eligibility, comparable yield, exact annual timing, and incomplete comparator eligibility and lifecycle authority | Obtain legitimate primary ASC/ASBE/EU text or keep those cells unresolved; extend the six queued methods with their own authority and cases | Professional accounting validity, empirical forecast validity, production readiness, human acceptance, superiority, and whole MC01–MC35/G1–G18 closure |

## Inference status

| Evidence class | Status | Interpretation |
| --- | --- | --- |
| Hard veto screen | Pass for the declared AASB engineering slice | The focused unit tests and deterministic checker exercise source admission, invariants, failure atomicity, exact cases, and unresolved comparison handling. |
| Statistically supported ranking | Not applicable | This is not a stochastic comparison or forecast experiment. |
| Descriptive-only differences | None claimed | No second inspected standard supports a numerical difference or equivalence. |
| Default readiness | Not ready | Synthetic assumptions and a single inspected jurisdiction cannot establish a production accounting default. |
| Next evidence needed | Primary US GAAP, ASBE, and EU-endorsed texts; real contract eligibility and market-yield evidence; independent human review | These are required before extending or promoting the method. |

## Remaining corporate-method queue

Revenue, tax, leases, FX, and complex groups remain specific follow-up entries
with an operation boundary, missing authority, unresolved interpretation, exact
next case, and MC/G links in the deliverable. The bond queue covers early
repurchase, inducement, modification, default, embedded terms, and complete
disclosures. No professional engagement, paid data, outreach, or publication
was used.

## Verification and manifest

Current repair: the reproducible builder regenerated and validated the canonical JSON before atomic publication, archiving the prior bytes under `docs/design/research/p08-v6/build-history/`. The standalone checker passed 51 tests with no findings; criterion 3 remains incomplete. The current check is `docs/design/research/p08-v6/final-check.json`. Exact source/code/test pins live in the rebuilt JSON. The full cases and comparisons objects equal `docs/design/research/p08-v6/applicability-baseline.json` byte-for-byte as parsed JSON; EU admission remains false.

The earlier recovery checks on 3 October 2026 executed:

- `CUDA_VISIBLE_DEVICES=-1 python3 -B scripts/check_accounting_p08.py --check`: **six engineering check groups and 51 unit-test methods passed**, zero failures/errors/skips, 101.268319 seconds measured command wall time. Its separate phase-acceptance result is false because criterion 3 is incomplete. The JSON report is retained at `docs/design/research/p08-v6/final-check.json`.

The historical JSON bytes and measurements remain in the research archive and original run records. The current JSON contains executed cases, inspection records and input hashes; the separately saved checker report records commands, timing and environment. The immediately preceding repair process timed out before this coherent rebuild; that stale-bundle failure is repaired here.
This execution independently reran both commands; its 27-test results supersede
the earlier 24-test measurements, which remain in the JSON verification history.
The checker reconstructs every stored Contract and replays complete journals,
final states and notes. It compares authority records and access histories with
their retained records, checks source bytes and independently recalculates
present values, annual interest and cash reconciliation. Mutation tests reject
altered amounts, postings, notes, claim text, missing claims, stale hashes,
fabricated common hashes, changed comparator economics, falsified access status
and unsupported adoption of deferred research. Further tests remove authority
after issuance and verify that failed accrual, coupon and either settlement
preserve the previously committed history.

This attempt also reproduced and repaired a manifest consistency defect:
changing the recorded AASB 7 or FASB PDF hash previously produced no finding.
The checker now checks every manifest hash against retained bytes, requires all
supporting primary sources, text extractions, access records and research inputs,
and rejects missing files and unsafe paths. Both AASB 132 input pins are now
included. Three new regression tests exercise stale pins, missing authority
inputs and invalid additional paths. Source bytes and the authority register
were preserved. These repairs strengthen provenance and reproducibility; they
do not supply the missing comparator authority.

The actual interpreter is Python 3.11.15 at
`/home/chakwong/miniconda3/envs/tfgpu/bin/python3`, in the existing `tfgpu`
environment. Only the standard library was used; no packages were changed.
GPU devices were intentionally hidden with `CUDA_VISIBLE_DEVICES=-1`; no
accelerator framework was imported. Read-only Git inspection returned this
repository as its root and HEAD `8e3b2628df8c89f7315119170b82624d536bc3e5`;
content hashes identify the current implementation. No Git setup or commit was
performed. All six protected controller/plan hashes match the current packet;
the execution-2 pre-edit inventory covers 434 files. The checker, test file and
three declared P08 deliverables are the only files changed in this attempt;
429 other inventoried files remain unchanged. No retained source or protected
snapshot was changed.

| Original criterion | Status | Evidence or remaining dependency |
| --- | --- | --- |
| 1: Applicable primary anchors | Complete for admitted AASB slice | Three checked compilations; 12 mandatory source-linked claims; unavailable texts excluded |
| 2: Operation and exact multi-period cases | Complete for admitted AASB slice | Preconditions, recognition, measurement, event/posting links, notes, both settlements and second parameter set |
| 3: Supported same-fact cross-standard comparison | Incomplete | FASB conditional classification is prepared; full eligible US lifecycle, ASBE and EU authority remain incomplete |
| 4: Specific follow-up work | Complete for this slice | Six method queues, ACTUS defer decision and exact source dependencies |

Passing engineering checks does not pass criterion 3. Phase acceptance is
incomplete. Professional accounting validity, empirical forecast validity,
production readiness, human acceptance and whole-gap closure remain unestablished.
The strongest alternative explanation for a balanced lifecycle is incorrect
synthetic eligibility or market yield. An applicable conflicting paragraph or
independent accounting reconstruction would overturn treatment admission; the
weakest evidence is the incomplete comparator authority. Internal source and
method preparation remains the next action; no paid review or outreach is needed.


## Historical EU preparation repair, 3 October 2026

The following records the earlier v3 state. Its uninspected-source counts are historical; the current v6 preparation and bounded applicability disposition below supersede that inventory.

The original Regulation 2023/1803 and Regulation 1606/2002 Article 4 support
preparation for a hypothetical Member State issuer whose securities trade on a
regulated EU market and which prepares consolidated accounts. This is an
alternative reporting context, with unchanged instrument economics. The original
regulation's printed August date is corrected to 13 September 2023 by the retained
OJ L239/39 corrigendum. Article 5 gives entry into force on 16 October 2023.

The new p08-v3 authority register preserves 26 inspected paragraph anchors,
source hashes, event-date applicability rows and four annex decisions. IAS 32.22,
.28–32 and AG31–AG32 support the fixed-share split and maturity conversion in the
original text; IFRS 9.3.1.1, .3.3.1–3, .4.2.1, .5.1.1 and Appendix A support
recognition, amortised cost and settlement. The original wording implies the
same arithmetic as AASB under the stated assumptions. Applicable agreement is
not established until the amendment and corrigendum chain is resolved.

The inspected 2023/2822 annex, IAS 1.69(c) and .76B, makes the outstanding debt
current after the 2024 coupon; separately recognised equity conversion does not
change that classification. IAS 1.139U/139W apply retrospectively from 2024.
The 2023/2468 IAS 12 amendments concern tax, which remains outside this pretax
journal. The 2023/2579 IFRS 16 amendments concern sale-and-leaseback transactions,
absent here. The 2024/1317 amendments concern supplier finance; no provider pays
suppliers in this case. These findings neither establish a complete tax treatment
nor complete IFRS 7 liquidity disclosures.

Seven 2024–2025 amendment documents and four further corrigenda remain
uninspected. Four later amendments are also recorded for subsequent applicability
review; their dates alone do not establish absence of retrospective effects.
Reporting-scope amendments and remaining instrument cross-references also need
inspection. The new module checks retained bytes, independent EU claim names,
note/event links and the unresolved period matrix. EU admission fails with its
specific source dependencies before any journal mutation. Both comparison cells
remain null, and criterion 3 remains incomplete.

Independent arithmetic for the unchanged facts gives L0 = 5/(11/10) +
105/(11/10)^2 = 11050/121 and equity = 1050/121. Year-one interest is 1105/121,
leaving 1050/11 after coupon 5. Year-two interest is 105/11, leaving principal
100 after coupon 5. Redemption leaves cash 10; conversion leaves cash 110 and
issues ten shares with share equity 100. These are checked AASB outcomes and
conditional EU calculations, not admitted EU accounting results.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Preserve AASB execution | Existing exact lifecycles retained | No new AASB validity failure identified | Synthetic eligibility and yield | Review current deterministic checks | Real-contract accounting validity |
| Keep EU unadmitted | Applicable second lifecycle incomplete | Missing amendment/corrigendum authority | Applicable 2024–2025 edition and eligibility | Inspect named missing texts after a legitimate new source opportunity | Cross-standard acceptance or whole-gap closure |

The access limit fired only for source acquisition. It does not invalidate the
arithmetic or existing AASB implementation. Internal source preparation continued;
no professional engagement, paid data, permission escalation or model worker was
used. The strongest alternative to the provisional agreement is a relevant
correction or eligibility provision changing the treatment. Complete applicable
primary evidence could overturn the current admission veto. professional
accounting validity, empirical forecast validity and human acceptance remain
unestablished. All six wider method queues and ACTUS deferral are preserved.

## Current v6 preparation

The source-disposition draft is now validated and integrated with the canonical builder and checker. Exact RDF subjects and typed predicates distinguish citations, amendments and corrections; the six EEA incorporation decisions remain citations of Regulation 2023/1803. The validator verifies retained source bytes, anchors, required claims, inspections, operation/note links and explicit pending dependencies. Mutation tests reject stale/unsafe pins, wrong subjects, citation-as-amendment changes, omitted corrections, contradictory reporting assumptions and attempted admission.

Historical inspection rows are explicitly named as historical and cannot assign current amendment status. This integrity result does not decide claim-specific applicability or transition questions. Those decisions remain admission vetoes, and no EU lifecycle is enabled. The complete validation record is `docs/design/research/p08-v6/validation-report.json`; independent review of this exact preparation is pending.


## Bounded scope and eligibility disposition

The separate `docs/design/research/p08-v6/applicability-disposition.json` records
15 conditional decisions using the retained primary provisions. Regulation
2023/1803 Article 1 adopts the Annex and Article 5 gives entry into force on
16 October 2023. Regulation 1606/2002 Article 4 supplies the conditional
consolidated-reporting scope. The hypothetical issuer is assumed to satisfy its
Member State-law and regulated-market conditions at both balance sheet dates.
The 2008 amendment changes adoption procedures, the Polish correction confirms
“any Member State”, and the Portuguese correction changes recitals 7/9 and
Article 2, without changing Article 4.

IAS 32.16, .22, .22A, .25–27 and AG29 support conditional eligibility analysis of
the fixed-share option under the stated ordinary-share, currency and group-term
assumptions. The whole bond has contractual cash obligations; these decisions do
not classify it wholly as equity. IFRS 9.2.1(d) conditionally excludes qualifying
issuer equity, not the bond liability. Compound classification and measurement,
settlement and notes, and remaining amendment/transition decisions are pending.
Of 26 original anchors, seven have conditional decisions awaiting review, one
has eligibility analysis with compound classification still pending, and 18 are
assigned to later groups. The six EEA documents remain citations.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Submit scope/eligibility as PARTIAL | Claim-specific provisions, assumptions, dates and operation dependencies recorded | Independent review and unfinished transition/operation groups prevent EU admission | Synthetic eligibility and applicable amended wording | Independently review these 15 decisions, then classification/issuance | Completed criterion 3, wider MC19, EU lifecycle or professional accounting validity |

Mechanical checks verify provenance, coverage and mutation rejection; they do
not prove legal reasoning. The evidence/default audit, exact commands, timings,
changed-file inventory and checks are retained in
`docs/design/research/p08-v6/applicability-check-report.json`. The builder now
accepts an explicit history directory so prior canonical bytes can be preserved
under research without writing protected supervisor files. The final checker
must follow rebuilding so the canonical manifest pins the actual validator,
fixture and tests. Unchanged AASB cases and the entire comparison are compared
with `applicability-baseline.json`. EU admission remains false.

The strongest alternative explanation is an omitted or differently applicable
amendment or contract term. Such evidence would require revising eligibility;
passing hash and mutation checks would not defeat it. US GAAP/ASBE authority,
revenue, tax, leases, FX, complex groups and broader bond methods remain queued.
Empirical forecast validity and human acceptance remain unestablished; this
bounded task does not close MC01–MC35 or G1–G18.


## Coherent-bundle repair record

The approved repair rebuilt `authority-and-methods.json` with the explicit
research history directory and retained the prior canonical bytes by hash. The
rebuilt manifest now pins the applicability disposition and validator together
with the fixture, builder, checker and test inputs. The exact parsed `cases`
and `comparisons` objects equal `docs/design/research/p08-v6/applicability-baseline.json`.
The checker reports six passing groups, 51 tests, zero failures, zero errors and
zero skips. `admission_allowed` remains false, `criterion_3` remains
`incomplete`, and `phase_criteria_complete` remains false.

This is a bounded engineering repair. It does not independently validate the
15 applicability decisions, admit an EU lifecycle, establish a second
same-fact treatment, or establish professional accounting validity, forecast
validity or human acceptance. The exact report, stderr capture, archive path,
changed-artifact inventory and next task are in
`docs/design/research/p08-v6/applicability-check-report.json`. No source, code or
test file was changed in this repair; the existing validator, builder, checker
and tests are evidence inputs.
