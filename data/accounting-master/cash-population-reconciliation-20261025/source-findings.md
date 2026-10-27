# Cash captions and restricted escrow

25 October 2026. Source audit for MC01, MC04, MC06, MC09, MC20, MC28 and MC35.

The two cash captions cannot be assigned to one opening balance. In the retained
2024 annual filing, the 2023 comparative balance sheet reports cash and cash
equivalents of USD29,965 million, while the cash-flow statement starts from
USD30,737 million. The latter caption explicitly includes restricted cash and
restricted cash equivalents. The displayed difference is USD772 million.
The 2023 annual filing independently displays those same amounts, with its
own cash-flow caption, dates and source identity retained. Agreement is a
cross-edition consistency check, not permission to merge the editions.

At 28 September 2024, both cash captions display USD29,943 million. This does
not establish equal membership. Note4 on PDF40, printed37, says cash and cash
equivalents include USD2.6 billion of restricted escrow. Note7 on PDF42,
printed39, independently specifies the balance-sheet classification: the
USD15.8 billion escrow comprises USD2.6 billion classified as cash and cash
equivalents and USD13.2 billion as current marketable securities. Consequently,
adding all restricted cash to the balance-sheet cash caption would double
count the disclosed cash portion. Restricted marketable securities cannot be
silently reclassified as cash either.

## Exact source anchors

The replayable source-ledger.json binds four retained files and all six archive
members by SHA256. It preserves 41 occurrences of four selected XBRL concepts,
grouped into 35 identical representations; duplicates remain occurrences, not
additional balances. Selected anchors in the 2024 instance are:

| Meaning | Occurrence IDs | Context | Literal USD | Decimals |
|---|---|---|---:|---:|
| 2023 balance-sheet cash | f-148, f-606 | c-22 | 29965000000 | -6 |
| 2023 cash-flow population | f-262, f-344 | c-22 | 30737000000 | -6 |
| 2024 balance-sheet cash | f-147, f-510 | c-21 | 29943000000 | -6 |
| 2024 cash-flow population | f-343 | c-21 | 29943000000 | -6 |
| Restricted cash for State Aid | f-610, f-692 | c-89 | 2600000000 | -8 |

c-21 and c-22 are consolidated issuer instants on 2024-09-28 and 2023-09-30.
c-89 retains the LossContingenciesByNatureOfContingencyAxis and the issuer's
UnfavorableInvestigationOutcomeEUStateAidRulesMember. Its dimension cannot be
dropped merely because the amount is used in a comparison. The source note,
not a numeric coincidence, supports its inclusion in balance-sheet cash.
Precision and unit representations are retained. Nearest-rounding intervals,
when used below, will be explicit modeling premises, not inferred exact values.

Read at normal resolution: 2023 PDF33/35/39/45 (printed30/32/36/42); 2024
PDF36/40 in the predecessor and PDF42 in this continuation. The source ledger
also records bounded text extraction from additional pages; extraction is not
a claim that those pages were visually reviewed.

## What remains unknown

The full extracted text of the two annual PDFs was searched for restricted,
reconcil and the isolated number772. The cash/escrow passages were inspected.
The selected instance has no exact numeric772-million fact. Its three
restricted-cash calculation arcs concern the cash-flow period change, not a
stock reconciliation to balance-sheet cash. No source-backed classification
of the 2023 difference was located in this bounded inspection. This is not an
exhaustive claim about every filing, taxonomy relationship or underlying book.

The algebraic difference is not an observed account, transaction, restriction,
or exact unrounded quantity. Conditional reasoning may assume a common
additive valuation and particular membership relations. Those assumptions
must remain separate from the reported facts. A witness then establishes
compatibility with that conditional system only.

## Reuse decision and next work

Existing context_chronology_v1.check_partition handles explicitly identified
finite members and rejects unknown residuals and overlapping classifications.
The partial-claim population adapter preserves unknown membership but concerns
receivable contracts. Neither is evidence that these cash populations are
fully enumerated. The existing joint_measurement_constraints_v1 engine already
solves exact conditional linear measurement systems. Reuse it for aggregate
intersection amounts; do not add another solver or pretend those amounts are
bank accounts. Add the smallest transparent lowering and adversarial examples
needed to preserve overlap, context and uncertainty.

| Decision | Primary criterion | Veto | Main uncertainty | Next action | Not concluded |
|---|---|---|---|---|---|
| Preserve distinct cash populations | Exact labels, amounts, contexts retained | No invented residual or duplicate balance | 2023 difference composition | Conditional aggregate overlap representation | Full reconciliation or actual opening history |
| Reuse existing linear engine | General equations already supported | Unknown membership cannot become complete partition | Source-to-population interpretation | Hand-solvable cases and exact replay | Accounting admission or whole-company completion |
