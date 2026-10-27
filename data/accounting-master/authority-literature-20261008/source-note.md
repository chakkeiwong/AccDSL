# What the 2017 ASBE 22 text establishes for the loan example

The retained Ministry of Finance text supports the example's distinction
between a default-event horizon and the dates of the resulting cash shortfalls.
It also supports separate decisions about credit impairment, interest and
write-off. These are conclusions about selected provisions of the dated 2017
standard. They do not establish its applicability to a particular entity and
reporting period or validate the assumed credit forecasts.

The source is the official page entitled 企业会计准则第22号——金融工具确认和计量
（财会〔2017〕7号）, with page-publication metadata 8 September 2017. The original
HTML and response headers remain in `sources/asbe22-trusted.*`.
`source-extract.json` binds the SHA256, preserves article text, distinguishes
extraction from inspection, and records fifteen exact Chinese quotations and
their English interpretations. Translation and the deductions below are ours.

## The default window does not truncate the cash shortfall

Article 47 defines credit loss as the present value of all contractual cash
flows less expected receipts, discounted at the original effective interest
rate, with a stated exception for purchased or originated credit-impaired
assets. It expressly includes a loss caused by late receipt even if the full
nominal amount is ultimately collected. Article 48 defines twelve-month ECL by
defaults possible in the next twelve months, or the remaining expected life if
shorter. It does not limit the associated shortfalls to that period.

For the existing authored loan, advance 100 at time zero and receive contractual
payment 121 at time two. An original EIR of 10% gives 121/1.1² = 100. The
three disjoint origination scenarios have probabilities 0.1 for first-year
default, 0.1 for second-year default and 0.8 for no default. Either default
scenario has terminal receipt 60.5. The initial twelve-month allowance is
0.1 × (121 − 60.5)/1.1² = 5; lifetime ECL is 10. A cash-flow-only cutoff at
year one would return zero because nothing is due then. That is wrong relative
to the Article 48 quantity. As a separate timing check, receiving the full
121 at time three instead of time two gives a time-zero shortfall PV of
100 − 121/1.1³ = 100/11, despite no nominal loss.

The bullet structure needs a qualitative default definition before maturity:
no instalment has yet been missed. Article 52 requires a definition consistent
with the entity's credit-risk management and consideration of qualitative
indicators. Financial distress is an explanatory assumed event here; no real
borrower's facts or default policy have been admitted.

## Staging, measurement and interest answer different questions

At year one, gross balance is 110. Survival alone changes the remaining
default probability to 0.1/0.9 = 1/9. The separate forecast update to 0.2 is an
assumption, not Bayesian conditioning on survival alone. Expected receipt is
0.8 × 121 + 0.2 × 60.5 = 108.9; its one-year PV is 99 and the allowance is
110 − 99 = 11. Exactly one year remains, so both general-method horizons
produce 11. This number does not establish SICR. Article 52 asks about a
change in default risk; Articles 53–55 supply additional assessment provisions.
No universal PD-ratio trigger or unconditional overdue-day trigger is inferred.

A later, distinct credit-impairment event changes expected terminal receipt to
60.5. Article 59(5) supports allowance 110 − 60.5/1.1 = 55 for this non-POCI
impaired asset. Articles 38 and 39(2) then give net amortised cost 55 and
subsequent-year interest 5.5. Gross accrual 11 decomposes into interest revenue
5.5 and allowance unwind 5.5. This decomposition is a checked local journal
realisation, not a journal layout prescribed verbatim by the standard.

The separate non-derecognising modification illustration also has dated
support: Article 42 requires gross remeasurement and a resulting gain/loss;
Article 56 requires credit-risk reassessment comparing modified current terms
with original terms at origination. The asset decision does not inherit the
issuer-liability ten-percent test. Full classification, derecognition and
modification practice remain broader obligations.

## A forecast mean does not settle the write-off date

Article 43 states: “企业不再合理预期金融资产合同现金流量能够全部或部分收回的，应当直接减记该金融资产的账面余额。”
The relevant gross write-off is required when there is no reasonable
expectation of recovering all or part of contractual cash flows.

The earlier sentence that impairment establishes that “only 60.5 will be
collected” is wrong as a justification for retaining a definitely unrecoverable
residual until maturity. Version 2.4 instead states an expected receipt of
60.5 and an explicit assumption that reasonable prospects of fuller recovery
remain until the separate maturity settlement finding. An earlier write-off
finding would require earlier action. The arithmetic stays the same; the
underlying information assumption is now explicit.

For logical clarity, a conditional distribution with receipts 0, 60.5 and 121
and weights 1/4, 1/2 and 1/4 has mean 60.5 while allowing full recovery. The
calculation file checks this counterexample only; it is not a fitted recovery
law or a new default for bank simulations. The realised branch collects 60.5
and writes off the residual when the distinct no-recovery finding is made.
Cash 160.5 and deposits 180 then leave equity −19.5. Total interest 15.5 less
impairment expense 55 gives loss 39.5, equal to cash advanced less cash received.
Negative equity is retained rather than repaired with an invented funding event.

## Applicability remains a separate source task

Article 84 states 1 January 2018. Articles 72–73 establish transition rules,
including opening-balance adjustments and conditions for comparative changes;
Article 83 addresses initial credit-risk information and the specified
transition exception. These do not substitute for the issuance notice's
entity-group schedule or subsequent amendments. The official search identifies
the notice at `kjs.mof.gov.cn/zhengcefabu/201704/t20170406_2575699.htm`.
Both its HTTPS and indexed HTTP routes returned 502. No adoption-group dates
have been inferred from a snippet or outside memory.

The current official search also exposes Interpretations 19 and 20 and later
financial-instrument FAQs. These are discovery leads, not inspected amendment
support. Their applicability, the notice, any relevant later changes, the
target bank's adoption disclosures and actual contract/credit evidence remain
on the internal queue. The preserved 2017 page supports a dated comparison;
it is not a demonstrated consolidated standard as of October 2026.

## Caiani source attempt and literature decisions

The saved metadata identifies journal DOI `10.1016/j.jedc.2016.06.001` and
working-paper DOI `10.2139/ssrn.2664125`. A trusted Kingston retrieval failed
DNS; an alternate Insubria handle returned HTTP 500, “Cannot Connect to Server.”
No verified full text was acquired. The older purported download is a wireless
sensor-network paper by Nardelli and co-authors. Its extracted arXiv identifier
is 1508.02253v2 while the old request ledger says 1508.02248. The discrepancy is
preserved; neither identifier is guessed to be a correct Caiani source.

Consequently the two substantive literature questions remain unanswered:
the specific model contribution and its difference from disclosure
reconstruction cannot be supported from inspected Caiani text. Its equations,
matrices, event sequence, evaluation, appendices, official code and current
correction/version history remain uninspected. This is a source-access result,
not evidence against stock-flow modelling. McCarthy, Imielinski/Lipski and
Tamer remain blocked as before.

`source-claim-supplement.json` retains separate source, claim, metadata,
backward, forward and omission records. The six existing forward results now
have task-specific title/metadata dispositions, including the calibration
paper and JMAB 2.0 as future technical/code leads. No new forward query or
backward full-text review is claimed. The old OpenAlex retraction flag and
citation count are dated metadata, not a clean correction-history finding.

## Decision and skeptical review

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Admit selected dated ASBE provisions | Official identity and exact article inspection pass | No quote or source mismatch found | Entity applicability and subsequent amendments | Add bounded article-supported explanation to separate candidate | Current compliance or full E07 closure |
| Retain numerical example with repaired assumptions | Independent rational PV and journal reconciliation pass | Staging and write-off assumptions are now explicit | Actual credit/default/recovery findings are authored | Require those facts before real admission | Arithmetic validates credit judgment |
| Keep Caiani blocked | Verified primary content absent | Two-route access cap reached for this unit | Technical content, version, corrections and code | Preserve failures; use a new justified route in a later unit | Source failure rejects the method or closes E08 |

The strongest alternative explanation for apparent agreement is that the
synthetic loan was constructed to satisfy a narrow general-method case. An
applicable exception, a different recovery date, a POCI asset or an earlier
write-off finding would change the conclusion. The weakest evidence is
entity-specific applicability, not the rational arithmetic. Source identity,
engineering calculation and accounting interpretation therefore retain
separate verdicts. There is no stochastic-method ranking, empirical forecast
evidence or default-policy promotion in this unit.
