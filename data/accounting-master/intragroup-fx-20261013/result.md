# Intragroup currency exposure and Version 2.52

13 October 2026. The bounded source/method and P18 integration unit is complete.
**Version 2.52, 195 pages** is the current provisional candidate; full readiness
remains **not_ready**. PDF:
`docs/design/proposal/manuscript-intragroup-fx-20261013/accounting-product-proposal.pdf`.
SHA256: `a9de309d7c4176b799f094e9a1a91380a6506ce79c284fa6c96b16959cc52a6c`.

P17/E07/P18; MC02/06/08/10–11/13/15–16/19/28/30/32–35;
G4/G7/G12/G15/G16. The addition explains the proposal's existing claim that
an intragroup loan balance can eliminate while its currency result survives.

## Checked result

The authored USD-functional parent has opening cash 56, investment 24 and a
EUR100 monetary receivable valued at 120, against equity 200. The EUR-functional
subsidiary has cash 120, payable 100 and capital 20 in EUR. At USD1.20 per EUR,
group cash/equity is 200 after elimination. This starts from established
carrying amounts and isolates exchange remeasurement; it does not prescribe
the initial fair value or interest terms of a new loan.

At USD1.30 per EUR the parent's separate gain is 10. Translating the subsidiary
gives cash 156, payable 130, historical capital 24 and translation OCI 2.
Eliminating the reciprocal loan and investment/capital leaves group cash and
equity 212. The ordinary loan produces profit 10 and OCI 2. Under separately
assumed IAS 21.15 net-investment conditions, group profit is zero and OCI is 12;
the parent's separate gain remains 10. This is a conditional presentation
difference, not an elective relabelling of a long-term loan.

Cash increases by 12 in USD value with no transaction cash flow. IAS 7.28
requires that exchange effect separately from operating/investing/financing
flows. No additional gain is added. Both treatments reconcile through the
same group balances; they differ for profit, OCI and later disposal questions.

The full retained IAS 21 (PDF 151–162), relevant IAS 7 and IFRS 10 passages,
and the regulation-date corrigendum were read. Sixteen exact paragraph anchors
and seven inspected source renders are retained. The 2023 incorporation is
historical authority, not proof of current amendment completeness. All **49
source/arithmetic checks** pass, including balanced separate/combined/group
trial balances and unchanged/falling-rate limiting cases. These are exact
authored calculations, not an empirical comparison or actual-company audit.

## Integration and decisions

Only the root version and an appended Chapter 10 section change. All 48
baseline source files, 48 earlier display blocks and 349 earlier citation
occurrences remain; the candidate adds six citations to the existing reference.
Bibliography bytes are unchanged. All **124 manuscript checks** pass. Final
LuaLaTeX output has no warnings or unresolved references, and six final pages
have inspected-image evidence. The first layout and its repaired orphan/table
placement are retained. The protected corpus/controller bytes remain unchanged.

| Decision | Primary criterion status | Veto diagnostic status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain the FX-only worked example | Exact source anchors and rational statement bridges pass | No source, balance or rate-direction failure remains | Actual settlement facts and complete non-FX measurement | Preserve conditional status and separate/group records | Complete period accounting or real-group compliance |
| Make Version 2.52 current provisionally | Exact allowed changes, clean build and rendered review pass | Initial layout problem repaired and preserved | Human comprehension and independent domain acceptance | Continue internal preparation and later bounded review | Full readiness or human acceptance |
| Refresh requirement-level priorities | Original five E obligations remain wider than the new examples | Counts cannot close original acceptance requirements | Which remaining design gaps have the greatest dependent impact | Execute the separate readiness-refresh plan | Positive P19 verdict from author self-review |

Post-run red team: the principal risk is silently extending this isolated FX
step into a claim about loan origination or a full reporting period. The source
explicitly defers carrying measurement to other standards; the example holds
those inputs fixed. A different monetary amount, currency, hedge, tax treatment,
control conclusion or settlement fact would require a different case. The
calculation establishes the stated bridge only. Human and independent domain
acceptance remain separate and pending.

E01/E05/E07/E08/E14 and MC01–MC35/G1–G18 remain controlling. No new source
acquisition, publication-date evidence, runtime, stochastic ranking, outreach
or paid engagement occurred. Continue with
`docs/plans/accounting-readiness-refresh-20261013.md`.
